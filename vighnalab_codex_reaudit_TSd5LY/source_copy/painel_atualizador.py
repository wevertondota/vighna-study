# -*- coding: utf-8 -*-
"""Atualização OFFLINE e reversível somente do PAINEL de homologação.

Nunca toca no programa VighnaStudy principal, no banco pessoal ou no histórico.
Pacotes não são autenticados por SHA-256: o usuário deve reconhecer a origem.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import time
import zipfile
import threading
from queue import Queue, Empty
import subprocess

FORMAT = 'vighna-panel-update-v1'
PANEL_ID = 'vighna-panel'
BASE_VERSION = '3.0.0'
VERSION_FILE = 'PAINEL_VERSAO.json'
MAX_ZIP = 1_800_000
MAX_FILE = 500_000
MAX_TOTAL = 1_500_000
MAX_MEMBERS = 20
# Allowlist INCLUDES NOTHING FROM VIGHNASTUDY CODE OR ITS HISTORICAL TEST ENGINE.
ALLOWED = frozenset({
    'painel_homologacao.py','painel_atualizador.py','painel_g5_preflight.py',
    'painel_g5_ui.py','test_gui_v3_smoke.py','test_painel_atualizador.py','test_painel_g5.py',
    'PAINEL_VERSAO.json','ATUALIZACOES_PAINEL_LEIA.md',
    'painel_g6b.py','painel_g6b_guest.py','test_painel_g6b.py',
    'painel_g6b2.py','painel_g6b2_guest.py','test_painel_g6b2.py',
    'painel_g7.py','test_painel_g7.py',
    # Gate G7 QA: correções restritas aos módulos portáteis do painel.
    'painel_core.py','test_painel_core.py','test_painel_v3.py',
    'test_historico_v2b.py',
    'painel_reconciliacao.py',
    'test_painel_reconciliacao.py',
    'painel_historico_ui.py',
    # V3.1.44: permissao explicita para os modulos da futura Central QA.
    'painel_central_qa.py','test_painel_central_qa.py',
})

class UpdateError(ValueError):
    pass


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _unsafe_reparse(path: Path) -> bool:
    """Conservatively reject symlinks, NTFS junctions and other reparse points.

    is_symlink() alone does not detect Windows directory junctions. When the
    platform exposes st_file_attributes, reject any reparse-point attribute.
    """
    path=Path(path)
    if path.is_symlink():
        return True
    is_junction=getattr(path,'is_junction',None)
    if is_junction is not None and is_junction():
        return True
    try:
        info=path.lstat()
    except FileNotFoundError:
        return False
    # On Windows the st_file_attributes member is set by lstat. Fail closed
    # for all reparse-point types (junctions, mountpoints and exotic links).
    attrs=getattr(info,'st_file_attributes',0)
    return bool(attrs & getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0x400))


def _require_local(path: Path, description: str) -> None:
    if _unsafe_reparse(path):
        raise UpdateError('Link ou junction inseguro em '+description+'.')


def _require_local_storage(storage: Path) -> None:
    _require_local(storage,'armazenamento de atualizações')
    if storage.exists() and not storage.is_dir():
        raise UpdateError('Armazenamento de atualizações não é uma pasta local.')


def _require_local_checkpoint(checkpoint: Path) -> None:
    _require_local(checkpoint,'checkpoint')
    _require_local(checkpoint/'anteriores','backup do checkpoint')
    _require_local(checkpoint/'resultado.json','resultado do checkpoint')
    _require_local(checkpoint/'resultado.tmp','temporário do checkpoint')


def _atomic_local_write(path: Path, data: bytes, description: str) -> None:
    """Create a unique local temporary file; never open a predictable symlink for write.

    Files are replaced with os.replace rather than written through an existing
    destination symlink. Fail closed for reparse points seen before replacement.
    """
    path=Path(path)
    _require_local(path.parent,'diretório de '+description)
    _require_local(path,description)
    fd,stage=tempfile.mkstemp(prefix='painel_atomic_',suffix='.tmp',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        _require_local(path.parent,'diretório de '+description)
        _require_local(path,description)
        if _unsafe_reparse(Path(stage)):
            raise UpdateError('Arquivo temporário inseguro em '+description)
        os.replace(stage,path)
    finally:
        Path(stage).unlink(missing_ok=True)


def panel_version(root: Path) -> str:
    file = root / VERSION_FILE
    if not file.is_file():
        return BASE_VERSION
    try:
        data = json.loads(file.read_text(encoding='utf-8'))
        if set(data) != {'component','version'} or data['component'] != PANEL_ID:
            raise ValueError('Formato incorreto')
        version = data['version']
        if not isinstance(version,str) or not version.startswith('3.') or len(version)>24:
            raise ValueError('Versão inválida')
        return version
    except (OSError, ValueError, KeyError) as exc:
        raise UpdateError('Identificação local da versão inválida.') from exc


def validate_panel_root(root: Path) -> Path:
    original_root=Path(root)
    _require_local(original_root,'raiz do painel')
    root = original_root.resolve(strict=True)
    for parent in (root, root.parent, root.parent.parent):
        if (parent/'estudos.db').exists() or (parent/'VighnaStudy.exe').exists():
            raise UpdateError('Pasta próxima da instalação real: atualização bloqueada.')
        if (parent/'dist'/'VighnaStudy'/'VighnaStudy.exe').exists():
            raise UpdateError('Pasta de executável real detectada: bloqueada.')
    expected = ('painel_homologacao.py','homologador_windows.py',
                'painel_gates.py','painel_checkpoints.py')
    if not all((root/name).is_file() for name in expected):
        raise UpdateError('A pasta não contém o Painel V3 completo.')
    _require_local_storage(root/'.painel_updates')
    _require_local(root/VERSION_FILE,'identificação de versão')
    return root


def _json_unique(data: bytes) -> dict:
    def unique(pairs):
        obj={}
        for k,v in pairs:
            if k in obj:
                raise UpdateError('Manifesto com campo repetido: '+k)
            obj[k]=v
        return obj
    try:
        return json.loads(data.decode('utf-8'),object_pairs_hook=unique)
    except (ValueError,UnicodeError) as exc:
        raise UpdateError('Manifesto JSON inválido.') from exc


def read_package(file: Path) -> tuple[dict,dict[str,bytes]]:
    file = Path(file)
    if not file.is_file() or file.stat().st_size>MAX_ZIP:
        raise UpdateError('Pacote inexistente ou excessivamente grande.')
    try:
        with zipfile.ZipFile(file) as z:
            infos=z.infolist()
            if not 2<=len(infos)<=MAX_MEMBERS:
                raise UpdateError('Quantidade inesperada de arquivos no ZIP.')
            if z.testzip() is not None:
                raise UpdateError('Integridade ZIP inválida.')
            by_name={}
            total=0
            for info in infos:
                n=info.filename
                if n in by_name or n.casefold() in {x.casefold() for x in by_name}:
                    raise UpdateError('Arquivo duplicado no ZIP.')
                if info.is_dir() or (info.flag_bits & 1) or '\\' in n or '/' in n or ':' in n or n.startswith('.'):
                    raise UpdateError('Nome de arquivo inseguro: '+n)
                if info.create_system==3 and stat.S_ISLNK(info.external_attr >> 16):
                    raise UpdateError('Links simbólicos são proibidos.')
                if info.file_size>MAX_FILE:
                    raise UpdateError('Arquivo acima do limite: '+n)
                total+=info.file_size
                if total>MAX_TOTAL:
                    raise UpdateError('Pacote descompactado excede limite.')
                by_name[n]=z.read(info)
    except (OSError,zipfile.BadZipFile,RuntimeError) as exc:
        raise UpdateError('Não foi possível validar o ZIP.') from exc
    if 'manifesto.json' not in by_name:
        raise UpdateError('Manifesto ausente.')
    manifest=_json_unique(by_name.pop('manifesto.json'))
    if set(manifest)!={'format','component','from_version','to_version','description','files'}:
        raise UpdateError('Formato do manifesto desconhecido.')
    if manifest['format']!=FORMAT or manifest['component']!=PANEL_ID:
        raise UpdateError('Pacote não destinado ao Painel de Homologação.')
    if not isinstance(manifest['description'],str) or len(manifest['description'])>500:
        raise UpdateError('Descrição inválida.')
    if not isinstance(manifest['from_version'],str) or not isinstance(manifest['to_version'],str):
        raise UpdateError('Versão de origem/destino inválida.')
    if manifest['from_version']==manifest['to_version']:
        raise UpdateError('Atualização sem mudança de versão.')
    files=manifest['files']
    if not isinstance(files,dict) or not files or set(files)!=set(by_name) or not set(files)<=ALLOWED:
        raise UpdateError('Arquivos fora da lista permitida.')
    for n,item in files.items():
        if not isinstance(item,dict) or set(item)!={'old_sha256','sha256'}:
            raise UpdateError('Contrato de arquivo incompleto: '+n)
        old=item['old_sha256']; new=item['sha256']
        if old is not None and (not isinstance(old,str) or len(old)!=64):
            raise UpdateError('Hash de origem inválido: '+n)
        if not isinstance(new,str) or len(new)!=64 or sha(by_name[n])!=new:
            raise UpdateError('Hash do conteúdo divergente: '+n)
        if n.endswith('.py'):
            try: compile(by_name[n],n,'exec')
            except SyntaxError as exc: raise UpdateError('Código Python inválido: '+n) from exc
        if n==VERSION_FILE:
            data=_json_unique(by_name[n]);
            if data!={'component':PANEL_ID,'version':manifest['to_version']}:
                raise UpdateError('Versão interna não corresponde ao manifesto.')
    if VERSION_FILE not in files:
        raise UpdateError('Um pacote deve atualizar a identificação de versão.')
    return manifest,by_name


def inspect(file: Path, root: Path) -> dict:
    root=validate_panel_root(root)
    manifest,payload=read_package(file)
    version=panel_version(root)
    if version!=manifest['from_version']:
        raise UpdateError(f'Versão local {version}; pacote exige {manifest["from_version"]}.')
    store=root/'.painel_updates'
    _require_local_storage(store)
    if store.is_dir():
        for record in store.glob('atualizacao_*/resultado.json'):
            _require_local_checkpoint(record.parent)
            if _json_unique(record.read_bytes()).get('status')=='preparado':
                raise UpdateError('Atualização incompleta; recupere antes de atualizar novamente.')
    if manifest['to_version']==version:
        raise UpdateError('A versão destino já está instalada.')
    # No symlinks, directory junctions or files with unexpected source contents.
    for name,item in manifest['files'].items():
        path=root/name
        if _unsafe_reparse(path) or path.is_dir():
            raise UpdateError('Arquivo de destino inseguro: '+name)
        old=item['old_sha256']
        if old is None:
            if path.exists():
                raise UpdateError('Arquivo novo já existe: '+name)
        elif not path.is_file() or sha(path.read_bytes())!=old:
            raise UpdateError('Arquivo local divergente do esperado: '+name)
    return {'from_version':version,'to_version':manifest['to_version'],
            'description':manifest['description'],'files':sorted(payload),'root':str(root)}


def apply(file:Path,root:Path, *, failure_injection:int=-1, progress=None)->dict:
    """Operação reversível, limitada aos arquivos permitidos e validada por hash."""
    def emit(message, fraction):
        if progress is not None:
            progress(message, fraction)
    emit('Conferindo integridade, versão e arquivos...', 0.07)
    root=validate_panel_root(root)
    preview=inspect(file,root)
    manifest,payload=read_package(file)
    emit('Criando backup para reversão...', 0.24)
    storage=root/'.painel_updates'
    _require_local_storage(storage)
    storage.mkdir(exist_ok=True)
    _require_local_storage(storage)
    checkpoint=storage/('atualizacao_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    _require_local_checkpoint(checkpoint)
    checkpoint.mkdir()
    backups=checkpoint/'anteriores';backups.mkdir()
    _require_local_checkpoint(checkpoint)
    journal={'status':'preparado','versao_anterior':preview['from_version'],
             'versao_nova':preview['to_version'],'files':manifest['files'],
             'origem':'pacote selecionado manualmente','instalacao_vighnastudy_autorizada':False}
    def write_state():
        _require_local_storage(storage)
        _require_local_checkpoint(checkpoint)
        file=checkpoint/'resultado.json'
        data=json.dumps(journal,ensure_ascii=False,indent=2).encode('utf8')
        _atomic_local_write(file,data,'resultado do checkpoint')
    for name, item in manifest['files'].items():
        _require_local_storage(storage)
        _require_local_checkpoint(checkpoint)
        if item['old_sha256'] is not None:
            _require_local(backups/name,'arquivo do backup')
            shutil.copy2(root/name,backups/name)
            if sha((backups/name).read_bytes())!=item['old_sha256']:
                raise UpdateError('Falha ao verificar backup: '+name)
    write_state()
    emit('Backup verificado. Aplicando arquivos...', 0.39)
    changed=[]
    try:
        for count,name in enumerate(manifest['files']):
            emit('Atualizando arquivo %d de %d...' % (count+1, len(payload)), 0.40+0.48*count/max(1,len(payload)))
            item=manifest['files'][name]
            source=payload[name]
            fd,tmp=tempfile.mkstemp(prefix='painel_stage_',suffix='.tmp',dir=root)
            try:
                with os.fdopen(fd,'wb') as stream:
                    stream.write(source);stream.flush();os.fsync(stream.fileno())
                if sha(Path(tmp).read_bytes())!=item['sha256']:
                    raise UpdateError('Falha de integridade no staging.')
                os.replace(tmp,root/name)
            finally:
                Path(tmp).unlink(missing_ok=True)
            changed.append(name)
            if failure_injection>=0 and count==failure_injection:
                raise RuntimeError('FALHA SINTÉTICA PARA ENSAIO DE ROLLBACK')
        if any(sha((root/n).read_bytes())!=manifest['files'][n]['sha256'] for n in payload):
            raise UpdateError('Verificação após escrita falhou.')
        journal['status']='aplicado';write_state()
        _atomic_local_write(storage/'ultima_atualizacao.json',
                            json.dumps({'pasta':checkpoint.name},ensure_ascii=False).encode('utf8'),
                            'marcador de rollback')
        emit('Arquivos validados. Atualização concluída.', 1.0)
        return {'status':'APLICADO','checkpoint':str(checkpoint),'versao':preview['to_version']}
    except BaseException as exc:
        errors=[]
        for name in reversed(changed):
            try:
                item=manifest['files'][name]
                if item['old_sha256'] is None:
                    (root/name).unlink(missing_ok=True)
                else:
                    os.replace(backups/name,root/name)
            except OSError as problem:
                errors.append(f'{name}: {problem}')
        journal['status']='revertido' if not errors else 'rollback_incompleto'
        journal['erros_rollback']=errors
        write_state()
        if errors:
            raise UpdateError('ATENÇÃO: rollback incompleto; NÃO executar o painel. '+str(errors)) from exc
        raise UpdateError('Falha na atualização; arquivos restaurados.') from exc


def rollback(root:Path) -> dict:
    """Rollback manual só se os arquivos permanecerem iguais ao target instalado."""
    root=validate_panel_root(root)
    storage=root/'.painel_updates'
    _require_local_storage(storage)
    marker=storage/'ultima_atualizacao.json'
    _require_local(marker,'marcador de rollback')
    if not marker.is_file():
        raise UpdateError('Não existe atualização anterior para reverter.')
    obj=_json_unique(marker.read_bytes());folder=obj.get('pasta')
    if not isinstance(folder,str) or not folder.startswith('atualizacao_') or '/' in folder or '\\' in folder:
        raise UpdateError('Registro de rollback inválido.')
    checkpoint=storage/folder
    _require_local_checkpoint(checkpoint)
    record=_json_unique((checkpoint/'resultado.json').read_bytes())
    if record.get('status')!='aplicado' or panel_version(root)!=record.get('versao_nova'):
        raise UpdateError('A atualização não está no estado esperado.')
    files=record.get('files')
    if not isinstance(files,dict) or not files or not set(files)<=ALLOWED:
        raise UpdateError('Registro de rollback inesperado.')
    for name,item in files.items():
        p=root/name
        if _unsafe_reparse(p) or not p.is_file() or sha(p.read_bytes())!=item['sha256']:
            raise UpdateError('Arquivo alterado após atualização: '+name)
        if item['old_sha256'] is not None:
            f=checkpoint/'anteriores'/name
            _require_local(f,'arquivo de backup')
            if not f.is_file() or sha(f.read_bytes())!=item['old_sha256']:
                raise UpdateError('Backup incompleto, rollback bloqueado: '+name)
    for name,item in files.items():
        if item['old_sha256'] is None:
            (root/name).unlink()
        else:
            shutil.copy2(checkpoint/'anteriores'/name, root/name)
    record['status']='rollback_manual'
    _atomic_local_write(checkpoint/'resultado.json',json.dumps(record,indent=2).encode('utf8'),
                        'resultado do checkpoint')
    marker.unlink(missing_ok=True)
    return {'status':'REVERTIDO','versao':panel_version(root)}


def recover_incomplete(root:Path) -> dict:
    """Recupera a última operação interrompida (status preparado), sem executar código."""
    root=validate_panel_root(root)
    storage=root/'.painel_updates'
    _require_local_storage(storage)
    if not storage.is_dir():
        raise UpdateError('Armazenamento de restauração ausente ou inseguro.')
    candidates=[]
    for folder in storage.glob('atualizacao_*'):
        _require_local_checkpoint(folder)
        if not folder.is_dir():
            raise UpdateError('Caminho de recuperação inseguro.')
        record=folder/'resultado.json'
        if record.is_file():
            obj=_json_unique(record.read_bytes())
            if obj.get('status')=='preparado':candidates.append((folder,obj))
    if len(candidates)!=1:
        raise UpdateError('Esperada exatamente uma atualização incompleta para recuperar.')
    folder,obj=candidates[0]
    files=obj.get('files')
    if not isinstance(files,dict) or not files or not set(files)<=ALLOWED:
        raise UpdateError('Registro de recuperação inesperado.')
    for name,item in files.items():
        path=root/name
        if _unsafe_reparse(path) or path.is_dir():
            raise UpdateError('Destino inseguro para recuperação: '+name)
        current=sha(path.read_bytes()) if path.is_file() else None
        valid={item['sha256'],item['old_sha256']}
        if item['old_sha256'] is None:valid.add(None)
        if current not in valid:
            raise UpdateError('Arquivo alterado por terceiro; recuperação bloqueada: '+name)
        if item['old_sha256'] is not None:
            b=folder/'anteriores'/name
            _require_local(b,'arquivo de restauração')
            if not b.is_file() or sha(b.read_bytes())!=item['old_sha256']:
                raise UpdateError('Backup divergente: '+name)
    for name,item in files.items():
        if item['old_sha256'] is None:
            (root/name).unlink(missing_ok=True)
        else:
            os.replace(folder/'anteriores'/name,root/name)
    obj['status']='recuperado_apos_interrupcao'
    _atomic_local_write(folder/'resultado.json',
                        json.dumps(obj,ensure_ascii=False,indent=2).encode('utf8'),
                        'resultado do checkpoint')
    return {'status':'RECUPERADO','versao':panel_version(root)}


def _wait_for_pid(pid:int,seconds:int=40) -> None:
    if not pid:return
    if sys.platform!='win32':
        # Caller must close the GUI manually outside Windows.
        return
    import ctypes
    k=ctypes.windll.kernel32
    SYNCHRONIZE=0x00100000
    h=k.OpenProcess(SYNCHRONIZE,False,int(pid))
    if h:
        try:
            if k.WaitForSingleObject(h,seconds*1000)==0x00000102:
                raise UpdateError('O Painel ainda está aberto; atualização cancelada.')
        finally:k.CloseHandle(h)


def _save_operation_status(root: Path, status: str, detail: str) -> None:
    """Best-effort status, never write through fixed-name symlinks/junctions."""
    try:
        storage=Path(root)/'.painel_updates'
        _require_local_storage(storage)
        if storage.is_dir():
            # Old releases used this fixed scratch filename. If it exists as
            # a reparse point, refuse status persistence instead of following it.
            _require_local(storage/'ultima_execucao.tmp','temporário de status legado')
            record={'status':status,'detalhe':detail[:350]}
            data=json.dumps(record,ensure_ascii=False,indent=2).encode('utf8')
            _atomic_local_write(storage/'ultima_execucao.json',data,'status da última execução')
    except (OSError, UpdateError):
        pass


def _start_panel_after_success(root: Path, *, launcher=None) -> None:
    """Reabre somente o painel, nunca o EXE do VighnaStudy."""
    if getattr(sys, "frozen", False):
        raise UpdateError("Reabertura por script Python indisponível no executável congelado de QA")
    root=validate_panel_root(root)
    script=root/'painel_homologacao.py'
    if not script.is_file() or _unsafe_reparse(script):
        raise UpdateError('Arquivo do painel ausente para reabertura.')
    cmd=[sys.executable,'-B',str(script)]
    if launcher is None:
        launcher=subprocess.Popen
    kwargs={'cwd':str(root)}
    if sys.platform=='win32':
        kwargs['creationflags']=getattr(subprocess,'CREATE_NEW_PROCESS_GROUP',0)
    launcher(cmd,**kwargs)


def _progress_window(args) -> int:
    """Atualizador gráfico externo: opera após o processo anterior encerrar.

    Tkinter só é tocado na thread principal; operações de arquivo em worker.
    Não reabre painel após falha ou operação incompleta.
    """
    import tkinter as tk
    from tkinter import ttk
    root_path=Path(args.root)
    win=tk.Tk()
    win.title('VighnaStudy — Atualização do Painel')
    win.geometry('515x215')
    win.resizable(False,False)
    win.configure(bg='#f4f7fb')
    heading=tk.Label(win,text='Atualizando a Central de Desenvolvimento',
                    font=('Segoe UI',13,'bold'),bg='#f4f7fb',fg='#183a57')
    heading.pack(anchor='w',padx=20,pady=(20,9))
    state=tk.StringVar(value='Aguardando o painel anterior encerrar...')
    tk.Label(win,textvariable=state,justify='left',wraplength=470,
             bg='#f4f7fb',fg='#3f5870',font=('Segoe UI',10)).pack(anchor='w',padx=20,pady=(0,12))
    amount=tk.DoubleVar(value=0.0)
    bar=ttk.Progressbar(win,maximum=100,variable=amount,length=466,mode='determinate')
    bar.pack(anchor='w',padx=20)
    close_btn=ttk.Button(win,text='Fechar',command=win.destroy)
    close_btn.pack(side='bottom',anchor='e',padx=20,pady=(0,14))
    close_btn.configure(state='disabled')
    win.protocol('WM_DELETE_WINDOW',lambda:None)
    events=Queue()
    def emit(msg, fraction):
        events.put(('progress',msg,round(max(0,min(1,fraction))*100)))
    def work():
        try:
            emit('Esperando o painel anterior encerrar...',0.01)
            _wait_for_pid(args.wait_pid,seconds=40)
            emit('Verificando compatibilidade...',0.04)
            result=apply(Path(args.apply),root_path,progress=emit)
            if result['status']!='APLICADO':
                raise UpdateError('O atualizador não concluiu a aplicação.')
            _save_operation_status(root_path,'APLICADO','Versão: '+str(result['versao']))
            events.put(('success','Versão '+str(result['versao'])+' aplicada. Reabrindo painel...',100))
        except Exception as exc:
            _save_operation_status(root_path,'BLOQUEADO',str(exc))
            events.put(('error','Atualização não concluída: '+str(exc),0))
    worker=threading.Thread(target=work,daemon=True)
    worker.start()
    succeeded=[False]
    def poll():
        try:
            while True:
                typ,msg,percent=events.get_nowait()
                state.set(msg)
                if percent:
                    amount.set(percent)
                if typ=='error':
                    close_btn.configure(state='normal')
                    win.protocol('WM_DELETE_WINDOW',win.destroy)
                    return
                if typ=='success':
                    succeeded[0]=True
                    try:
                        _start_panel_after_success(root_path)
                        win.after(700,win.destroy)
                    except (OSError,ValueError) as exc:
                        state.set('Atualização aplicada, mas não foi possível reabrir: '+str(exc)+
                                  '. Abra o atalho do painel manualmente.')
                        close_btn.configure(state='normal')
                        win.protocol('WM_DELETE_WINDOW',win.destroy)
                    return
        except Empty:
            pass
        win.after(90,poll)
    win.after(90,poll)
    win.mainloop()
    # A saída do processo não representa autorização de instalação do VighnaStudy.
    return 0 if succeeded[0] else 2


def main() -> int:
    parser=argparse.ArgumentParser(description='Atualizador seguro do Painel V3 (não VighnaStudy).')
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--inspect',metavar='ZIP')
    group.add_argument('--apply',metavar='ZIP')
    group.add_argument('--rollback',action='store_true')
    group.add_argument('--recover',action='store_true')
    parser.add_argument('--root',default=str(Path(__file__).resolve().parent))
    parser.add_argument('--wait-pid',type=int,default=0)
    parser.add_argument('--gui-progress',action='store_true',help='Progresso visual e reabertura após aplicar')
    args=parser.parse_args()
    if args.gui_progress:
        if not args.apply:
            parser.error('--gui-progress exige --apply')
        return _progress_window(args)
    try:
        root=Path(args.root)
        if args.apply or args.rollback or args.recover:
            _wait_for_pid(args.wait_pid)
        if args.inspect:result=inspect(Path(args.inspect),root)
        elif args.apply:result=apply(Path(args.apply),root)
        elif args.rollback:result=rollback(root)
        else:result=recover_incomplete(root)
        print('RESULTADO:',json.dumps(result,ensure_ascii=False,indent=2))
        status={'status':result.get('status','OK'),'detalhe':'Versão: '+str(result.get('versao',result.get('to_version','')))}
        returncode=0
    except (OSError,ValueError) as exc:
        print('ATUALIZAÇÃO BLOQUEADA:',str(exc),file=sys.stderr)
        status={'status':'BLOQUEADO','detalhe':str(exc)[:350]}
        returncode=2
    # Relatório de status por gravação atômica, sem seguir links externos.
    _save_operation_status(Path(args.root),status['status'],status['detalhe'])
    return returncode

if __name__=='__main__':raise SystemExit(main())
