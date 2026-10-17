# -*- coding: utf-8 -*-
"""G6-B1 guest Windows Sandbox. Frozen with PyInstaller on QA host.

Runs the original transactional update engine with *real*, precompiled Windows
executables. Build callback replaces compilation only; G6-B2 must prove the
original PyInstaller build path. Never mounts or reads a personal installation.
"""
from __future__ import annotations
import argparse
import ctypes
from datetime import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sqlite3
import stat
import subprocess
import sys
import time
import traceback
import zipfile
from contextlib import closing

BASE_VERSION = ('0.29.59', 'structural-m1c-readpilot-restore-offline-r1d-v1', 25)
RC2_BUILD = 'structural-m2-int1-settings-r1d-rc2'
MAX_EXTRACT = 25_000_000


def hash_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def read_json(p: Path):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def safe_extract_sources(src: Path, destination: Path) -> None:
    """Whitelist the source ZIP; never unzip directly into a sensitive folder."""
    destination.mkdir(exist_ok=False,parents=True)
    total=0;used=set()
    with zipfile.ZipFile(src) as z:
        for info in z.infolist():
            if info.is_dir():continue
            name=info.filename
            parts=PurePosixPath(name).parts
            if (not parts or name.startswith(('/','\\')) or '\\' in name or ':' in name
                or '..' in parts or '.' in parts or info.file_size>4_000_000
                or (info.create_system==3 and stat.S_ISLNK(info.external_attr>>16))
                or name.lower().endswith(('.db','.exe','.dll','.pyd','.sqlite','.sqlite3'))
                or name.casefold() in used):
                raise ValueError('Source ZIP entry rejected: '+name)
            total+=info.file_size;used.add(name.casefold())
            if total>MAX_EXTRACT:raise ValueError('Source ZIP over quota')
            target=destination.joinpath(*parts)
            target.parent.mkdir(exist_ok=True,parents=True)
            target.write_bytes(z.read(info))


def verify_input(folder:Path) -> dict:
    manifest=read_json(folder/'MANIFESTO_G6B1.json')
    if (manifest.get('component')!='vighna-g6b1-input' or
        manifest.get('target_build')!=RC2_BUILD or
        manifest.get('instalacao_autorizada') is not False):
        raise ValueError('Input identity mismatch')
    expected=manifest['sha256_files']
    if not isinstance(expected,dict) or len(expected)<10 or len(expected)>1200:
        raise ValueError('Input manifest size incorrect')
    actual={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
    if actual != set(expected)|{'MANIFESTO_G6B1.json'}:
        raise ValueError('Unexpected/missing input files')
    for rel,digest in expected.items():
        if not isinstance(digest,str) or len(digest)!=64 or hash_file(folder/rel)!=digest:
            raise ValueError('SHA-256 mismatch: '+rel)
    return manifest


def load_engine(file:Path, suffix:str):
    spec=importlib.util.spec_from_file_location('g6b1_engine_'+suffix,file)
    if spec is None or spec.loader is None:raise ValueError('Engine unavailable')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SQLiteDivergence(RuntimeError):
    def __init__(self, message:str, divergence:dict):
        super().__init__(message)
        self.divergence=divergence


class ScenarioFailure(RuntimeError):
    def __init__(self, message:str, diagnostic:dict):
        super().__init__(message)
        self.diagnostic=diagnostic


def _quoted_identifier(value:str)->str:
    return '"'+value.replace('"','""')+'"'


def _sqlite_value(value):
    if isinstance(value,bytes):
        return {'tipo':'blob','tamanho':len(value),
                'sha256':hashlib.sha256(value).hexdigest()}
    if isinstance(value,float):
        return {'tipo':'float','valor':repr(value)}
    return {'tipo':type(value).__name__,'valor':value}


def _canonical_hash(value)->str:
    data=json.dumps(value,sort_keys=True,separators=(',',':'),
                    ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def sqlite_snapshot(db:Path, moment:str)->dict:
    """Record physical files and a deterministic logical SQLite fingerprint."""
    db=Path(db)
    snapshot={'momento':moment,'caminho_relativo':db.name}
    if not db.is_file():
        snapshot.update({'integridade':[],'chaves_estrangeiras':[],
                         'schema':[],'tabelas':{},'marcador_qa':[],
                         'pragmas':{},'arquivos_fisicos':{},
                         'fingerprint_logico':None})
        return snapshot
    uri=db.resolve().as_uri()+'?mode=ro'
    with closing(sqlite3.connect(uri,uri=True,timeout=12)) as con:
        integrity=[row[0] for row in con.execute('PRAGMA integrity_check').fetchall()]
        foreign_keys=[list(row) for row in con.execute('PRAGMA foreign_key_check').fetchall()]
        pragmas={name:con.execute('PRAGMA '+name).fetchone()[0]
                 for name in ('application_id','user_version','schema_version',
                              'page_size','page_count','freelist_count','journal_mode')}
        schema_rows=con.execute(
            "SELECT type,name,tbl_name,COALESCE(sql,'') FROM sqlite_master "
            "ORDER BY type,name,tbl_name,sql"
        ).fetchall()
        schema=[{'tipo':row[0],'nome':row[1],'tabela':row[2],
                 'sql':row[3],'sql_sha256':hashlib.sha256(row[3].encode('utf-8')).hexdigest()}
                for row in schema_rows]
        tables={};internal_tables={}
        for table_name, in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
            quoted=_quoted_identifier(table_name)
            columns=[row[1] for row in con.execute('PRAGMA table_info('+quoted+')').fetchall()]
            row_hashes=[]
            for row in con.execute('SELECT * FROM '+quoted):
                row_hashes.append(_canonical_hash([_sqlite_value(value) for value in row]))
            row_hashes.sort()
            summary={'colunas':columns,'registros':len(row_hashes),
                     'registros_sha256':_canonical_hash(row_hashes)}
            if table_name.startswith('sqlite_'):
                raw_rows=con.execute('SELECT * FROM '+quoted).fetchmany(100)
                summary['amostra']=[[_sqlite_value(value) for value in row]
                                   for row in raw_rows]
                internal_tables[table_name]=summary
            else:
                tables[table_name]=summary
        marker=[]
        if 'g6b_marker' in tables:
            marker=[list(row) for row in con.execute(
                'SELECT id,data FROM g6b_marker ORDER BY id').fetchall()]
    physical={}
    for suffix in ('','-wal','-shm','-journal'):
        item=Path(str(db)+suffix)
        label='estudos.db'+suffix
        physical[label]={'existe':item.is_file()}
        if item.is_file():
            physical[label].update({'tamanho':item.stat().st_size,
                                    'sha256':hash_file(item)})
    logical={'integridade':integrity,'chaves_estrangeiras':foreign_keys,
             'pragmas':pragmas,'schema':schema,'tabelas':tables,
             'marcador_qa':marker}
    snapshot.update(logical)
    snapshot['tabelas_internas_sqlite']=internal_tables
    snapshot['arquivos_fisicos']=physical
    logical_identity=dict(logical)
    logical_identity['pragmas']={key:pragmas[key]
                                 for key in ('application_id','user_version')}
    snapshot['fingerprint_logico']=_canonical_hash(logical_identity)
    return snapshot


def first_sqlite_divergence(expected:dict, actual:dict, *, physical:bool)->dict|None:
    """Return the first stable, human-readable difference between snapshots."""
    base={'esperado':expected.get('momento'),'encontrado':actual.get('momento')}
    if actual.get('integridade')!=['ok']:
        return {**base,'categoria':'integridade','item':'PRAGMA integrity_check',
                'valor_esperado':['ok'],'valor_encontrado':actual.get('integridade')}
    if actual.get('chaves_estrangeiras'):
        return {**base,'categoria':'integridade','item':'PRAGMA foreign_key_check',
                'valor_esperado':[],'valor_encontrado':actual.get('chaves_estrangeiras')[:1]}
    for key in ('application_id','user_version'):
        left=expected.get('pragmas',{}).get(key); right=actual.get('pragmas',{}).get(key)
        if left!=right:
            return {**base,'categoria':'pragma','item':key,
                    'valor_esperado':left,'valor_encontrado':right}
    expected_schema=expected.get('schema',[]); actual_schema=actual.get('schema',[])
    if expected_schema!=actual_schema:
        limit=max(len(expected_schema),len(actual_schema))
        for index in range(limit):
            left=expected_schema[index] if index<len(expected_schema) else None
            right=actual_schema[index] if index<len(actual_schema) else None
            if left!=right:
                return {**base,'categoria':'schema','item':index,
                        'valor_esperado':left,'valor_encontrado':right}
    expected_tables=expected.get('tabelas',{}); actual_tables=actual.get('tabelas',{})
    for name in sorted(set(expected_tables)|set(actual_tables)):
        left=expected_tables.get(name); right=actual_tables.get(name)
        if left!=right:
            field=next((k for k in ('colunas','registros','registros_sha256')
                        if (left or {}).get(k)!=(right or {}).get(k)),'tabela')
            return {**base,'categoria':'registros','item':name+'.'+field,
                    'valor_esperado':(left or {}).get(field),
                    'valor_encontrado':(right or {}).get(field)}
    if expected.get('marcador_qa')!=actual.get('marcador_qa'):
        return {**base,'categoria':'marcador_qa','item':'g6b_marker',
                'valor_esperado':expected.get('marcador_qa'),
                'valor_encontrado':actual.get('marcador_qa')}
    if physical:
        expected_internal=expected.get('tabelas_internas_sqlite',{})
        actual_internal=actual.get('tabelas_internas_sqlite',{})
        for name in sorted(set(expected_internal)|set(actual_internal)):
            if expected_internal.get(name)!=actual_internal.get(name):
                return {**base,'categoria':'metadado_fisico_sqlite','item':name,
                        'valor_esperado':expected_internal.get(name),
                        'valor_encontrado':actual_internal.get(name)}
        for key in ('schema_version','page_size','page_count','freelist_count','journal_mode'):
            left=expected.get('pragmas',{}).get(key); right=actual.get('pragmas',{}).get(key)
            if left!=right:
                return {**base,'categoria':'pragma_fisico','item':key,
                        'valor_esperado':left,'valor_encontrado':right}
        expected_files=expected.get('arquivos_fisicos',{})
        actual_files=actual.get('arquivos_fisicos',{})
        for name in ('estudos.db','estudos.db-wal','estudos.db-shm','estudos.db-journal'):
            if expected_files.get(name)!=actual_files.get(name):
                return {**base,'categoria':'arquivo_fisico','item':name,
                        'valor_esperado':expected_files.get(name),
                        'valor_encontrado':actual_files.get(name)}
    return None


def sqlite_comparison(expected:dict, actual:dict)->dict:
    logical=first_sqlite_divergence(expected,actual,physical=False)
    complete=first_sqlite_divergence(expected,actual,physical=True)
    physical_changed=(
        expected.get('tabelas_internas_sqlite',{})!=actual.get('tabelas_internas_sqlite',{})
        or any(expected.get('pragmas',{}).get(key)!=actual.get('pragmas',{}).get(key)
            for key in ('schema_version','page_size','page_count','freelist_count','journal_mode'))
        or expected.get('arquivos_fisicos',{})!=actual.get('arquivos_fisicos',{}))
    return {'de':expected.get('momento'),'para':actual.get('momento'),
            'logica_alterada':logical is not None,
            'fisica_alterada':physical_changed,
            'primeira_divergencia':complete}


def require_sqlite_preserved(expected:dict, actual:dict, *, physical:bool)->dict:
    comparison=sqlite_comparison(expected,actual)
    divergence=first_sqlite_divergence(expected,actual,physical=physical)
    if divergence is not None:
        scope='fisica/logica' if physical else 'logica'
        raise SQLiteDivergence('SQLite sintetico divergiu na preservacao '+scope,
                               divergence)
    return comparison


def require_valid_synthetic(snapshot:dict)->None:
    if snapshot.get('integridade')!=['ok']:
        raise SQLiteDivergence('SQLite sintetico sem integridade',
            {'esperado':['ok'],'encontrado':snapshot.get('integridade'),
             'categoria':'integridade','item':'PRAGMA integrity_check'})
    if snapshot.get('chaves_estrangeiras'):
        raise SQLiteDivergence('SQLite sintetico com violacao de chave estrangeira',
            {'esperado':[],'encontrado':snapshot.get('chaves_estrangeiras')[:1],
             'categoria':'integridade','item':'PRAGMA foreign_key_check'})
    if snapshot.get('marcador_qa')!=[[39,'SOMENTE_QA_G6B1']]:
        raise SQLiteDivergence('Marcador do SQLite sintetico divergiu',
            {'esperado':[[39,'SOMENTE_QA_G6B1']],
             'encontrado':snapshot.get('marcador_qa'),
             'categoria':'marcador_qa','item':'g6b_marker'})


def window_present(pid:int):
    if sys.platform!='win32':return False
    user=ctypes.windll.user32
    found=[]
    CALLBACK=ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)
    def cb(hwnd,lparam):
        target=ctypes.c_ulong()
        user.GetWindowThreadProcessId(hwnd,ctypes.byref(target))
        if target.value==pid and user.IsWindowVisible(hwnd) and user.GetWindowTextLengthW(hwnd)>0:
            found.append(True);return False
        return True
    func=CALLBACK(cb)
    user.EnumWindows(func,0)
    return bool(found)


def smoke(folder:Path, scenario_root:Path, label:str) ->dict:
    exe=folder/'VighnaStudy.exe'
    if not exe.is_file():raise RuntimeError('Real EXE absent for '+label)
    profile=scenario_root/('Perfil_'+label)
    for item in ('Home','Roaming','Local','Temp'):(profile/item).mkdir(parents=True,exist_ok=True)
    env=os.environ.copy()
    env.update({'USERPROFILE':str(profile/'Home'),'APPDATA':str(profile/'Roaming'),
                'LOCALAPPDATA':str(profile/'Local'),'TEMP':str(profile/'Temp'),
                'TMP':str(profile/'Temp'),'QT_QPA_PLATFORM':'windows',
                'PYTHONDONTWRITEBYTECODE':'1'})
    for key in ('PYTHONPATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH'):
        env.pop(key,None)
    flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
    p=subprocess.Popen([str(exe)],cwd=str(folder),env=env,creationflags=flags)
    try:
        window=False
        for _ in range(100):
            if p.poll() is not None:break
            time.sleep(.4)
            if window_present(p.pid):window=True;break
        if window:
            time.sleep(3)
        survived=p.poll() is None
        return {'label':label,'exe_sha256':hash_file(exe),'process_started':True,
                'window_observed':window,'stable':bool(window and survived),
                'exit_code_if_early':p.poll() if not survived else None}
    finally:
        if p.poll() is None:
            p.terminate()
            try:p.wait(timeout=8)
            except subprocess.TimeoutExpired:
                p.kill();p.wait(timeout=5)


def scenario(parent:Path,inp:Path,name:str)->dict:
    result={'cenario':name,'status':'EM_EXECUCAO','operacao_atual':'preparar_cenario',
            'etapas_sqlite':[],'comparacoes_sqlite':[],
            'motor_original_invocado':False,'banco_qa_preservado':False}
    try:
        root=parent/name
        root.mkdir(parents=True,exist_ok=False)
        source=root/'codigo'
        safe_extract_sources(inp/'BASE_R1D_SOMENTE_FONTES_QA.zip',source)
        e=load_engine(source/'vighna_update_engine.py',name)
        if e.version_from_file(source/'versao.py')!=BASE_VERSION:
            raise RuntimeError('Unexpected R1D base')
        db=source/'estudos.db'
        result['operacao_atual']='criar_sqlite_sintetico'
        with closing(sqlite3.connect(db)) as con:
            with con:
                con.execute('CREATE TABLE g6b_marker(id INTEGER PRIMARY KEY, data TEXT)')
                con.execute('INSERT INTO g6b_marker VALUES (39,?)',('SOMENTE_QA_G6B1',))
        created=sqlite_snapshot(db,'apos_criar_sqlite_sintetico')
        result['etapas_sqlite'].append(created);require_valid_synthetic(created)

        active=source/'dist'/'SistemaEstudos'
        shutil.copytree(inp/'R1D',active)
        old_exe_hash=hash_file(active/'VighnaStudy.exe')
        result['exe_r1d_sha256']=old_exe_hash
        patch=inp/'CANDIDATO_QA_R1D_PARA_M2_RC2_NAO_INSTALAR.zip'
        if e.inspect_package(patch,source)['target_build']!=RC2_BUILD:
            raise RuntimeError('Target differs from RC2')
        initial_version=(source/'versao.py').read_bytes()
        initial_main=hash_file(source/'main.py')

        result['operacao_atual']='iniciar_executavel_r1d'
        before_smoke=smoke(active,root,'r1d')
        result['smoke_antes']=before_smoke
        if not before_smoke.get('stable'):
            raise RuntimeError('Actual R1D executable smoke failed')
        initialized=sqlite_snapshot(db,'apos_iniciar_executavel_r1d')
        result['etapas_sqlite'].append(initialized);require_valid_synthetic(initialized)
        initialization_change=sqlite_comparison(created,initialized)
        initialization_change['classificacao']='INICIALIZACAO_R1D_OBSERVADA'
        result['comparacoes_sqlite'].append(initialization_change)

        progress=[]
        def runner(work, output, report):
            if name=='falha_compilacao':raise RuntimeError('FALHA_QA_G6B1_BUILD')
            shutil.copytree(inp/'RC2',output,dirs_exist_ok=False)
            if hash_file(output/'VighnaStudy.exe')!=hash_file(inp/'RC2'/'VighnaStudy.exe'):
                raise RuntimeError('RC2 real EXE SHA mismatch')
        if name=='falha_pos_commit':
            real_check=e.check_database
            def check(path):
                if Path(path)==db and e.version_from_file(source/'versao.py')[1]==RC2_BUILD:
                    raise e.UpdateError('FALHA_QA_G6B1_POST_COMMIT')
                return real_check(path)
            e.check_database=check
        result['operacao_atual']='transacao_motor_original_'+name
        result['motor_original_invocado']=True
        try:
            try:
                e.install_package(patch,source,python_exe='G6B_PREBUILT',runner=runner,
                                  report=lambda n,msg:progress.append(n))
                if name!='sucesso':raise RuntimeError('Injected failure did not occur')
            except e.UpdateError as exc:
                if name=='sucesso' or 'FALHA_QA_G6B1' not in str(exc):raise
        finally:
            if name=='falha_pos_commit':e.check_database=real_check
        result['progresso']=progress

        result['operacao_atual']='verificar_sqlite_apos_transacao'
        after_transaction=sqlite_snapshot(db,'apos_transacao_'+name)
        result['etapas_sqlite'].append(after_transaction);require_valid_synthetic(after_transaction)
        transaction_comparison=require_sqlite_preserved(
            initialized,after_transaction,physical=True)
        transaction_comparison['classificacao']='PRESERVACAO_TRANSACIONAL_EXATA'
        result['comparacoes_sqlite'].append(transaction_comparison)

        history=source/'backups'/'atualizacoes'/'historico.jsonl'
        events=[json.loads(x) for x in history.read_text(encoding='utf8').splitlines()]
        if not events:raise RuntimeError('Update history missing')
        backup_root=source/'backups'/'atualizacoes'
        checkpoints=list(backup_root.glob('*/state.json'))
        saved_dirs=[folder for folder in backup_root.iterdir() if folder.is_dir()]
        if len(saved_dirs)!=1 or not (saved_dirs[0]/'estudos.db').is_file():
            raise RuntimeError('Synthetic database backup absent')
        backup_snapshot=sqlite_snapshot(saved_dirs[0]/'estudos.db','backup_permanente_motor_original')
        require_valid_synthetic(backup_snapshot)
        result['backup_sqlite']=backup_snapshot
        backup_comparison=require_sqlite_preserved(initialized,backup_snapshot,physical=False)
        backup_comparison['classificacao']='BACKUP_LOGICAMENTE_EQUIVALENTE'
        result['comparacoes_sqlite'].append(backup_comparison)
        # Original engine creates state.json only immediately before commit.
        # A pre-commit PyInstaller failure MUST NOT create such a checkpoint.
        if name=='falha_compilacao':
            if checkpoints:raise RuntimeError('Pre-commit failure unexpectedly created a commit checkpoint')
            ck={'phase':'pre_commit_no_snapshot'}
        else:
            if len(checkpoints)!=1:raise RuntimeError('Commit checkpoint is absent')
            ck=json.loads(checkpoints[0].read_text())
        old_saved=saved_dirs[0]/'anterior_executavel'/'VighnaStudy.exe'
        if name=='sucesso':
            if (e.version_from_file(source/'versao.py')[1]!=RC2_BUILD or
                hash_file(active/'VighnaStudy.exe')!=hash_file(inp/'RC2'/'VighnaStudy.exe') or
                hash_file(old_saved)!=old_exe_hash or ck['phase']!='installed' or
                events[-1]['status']!='installed'):
                raise RuntimeError('Real RC2 deployment/backup verification failed')
            final_label='rc2';final_moment='apos_iniciar_executavel_rc2'
            status='PASSOU_B1_TRANSACAO_REAL'
        else:
            if (e.version_from_file(source/'versao.py')!=BASE_VERSION or
                (source/'versao.py').read_bytes()!=initial_version or
                hash_file(source/'main.py')!=initial_main or
                hash_file(active/'VighnaStudy.exe')!=old_exe_hash or
                events[-1]['status']!='failed' or events[-1].get('rollback_errors')):
                raise RuntimeError('Real executable rollback failed')
            if name=='falha_pos_commit' and ck['phase']!='recovered':
                raise RuntimeError('Post commit recovery phase missing')
            final_label='r1d_restaurado';final_moment='apos_iniciar_r1d_restaurado'
            status='PASSOU_B1_ROLLBACK_REAL'

        result['operacao_atual']='iniciar_executavel_'+final_label
        after_smoke=smoke(active,root,final_label)
        result['smoke_depois']=after_smoke
        if not after_smoke.get('stable'):
            raise RuntimeError('Actual final executable smoke failed: '+final_label)
        result['operacao_atual']='verificar_sqlite_apos_iniciar_'+final_label
        after_final=sqlite_snapshot(db,final_moment)
        result['etapas_sqlite'].append(after_final);require_valid_synthetic(after_final)
        final_comparison=require_sqlite_preserved(after_transaction,after_final,physical=False)
        final_comparison['classificacao']='PRESERVACAO_LOGICA_APOS_EXECUTAVEL'
        result['comparacoes_sqlite'].append(final_comparison)

        result.update({'status':status,'operacao_atual':'concluido',
            'exe_final_sha256':hash_file(active/'VighnaStudy.exe'),
            'banco_qa_preservado':True,'fase_checkpoint':ck['phase'],
            'historico_final':events[-1]['status']})
        return result
    except Exception as exc:
        result['status']='FALHOU_OU_BLOQUEADO'
        result['operacao_falhou']=result.get('operacao_atual')
        result['erro_tipo']=type(exc).__name__
        result['erro']=str(exc)[:600]
        if isinstance(exc,SQLiteDivergence):
            result['primeira_divergencia']=exc.divergence
        raise ScenarioFailure(str(exc),result) from exc


def guest_workspace_dir(temp_root: Path, timestamp: str) -> Path:
    """Construct a path without treating Path as a string (WinError regression)."""
    return temp_root / ('VighnaG6B1_' + timestamp)


def run(input_dir:Path, output_dir:Path)->int:
    info={'component':'vighna-g6b1-guest','version':'3.1.16','target_build':RC2_BUILD,
          'status':'BLOQUEADO','windows_sandbox_executado':sys.platform=='win32',
          'executaveis_reais':True,'engine_original_qa':False,
          'build_original_dentro_sandbox':False,'instalacao_autorizada':False,
          'gate_g6_aprovado':False,'cenarios':[]}
    output_dir.mkdir(parents=True,exist_ok=True)
    try:
        if sys.platform!='win32':raise RuntimeError('Windows only')
        verify_input(input_dir)
        workspace=guest_workspace_dir(
            Path(os.environ.get('TEMP',r'C:\Windows\Temp')),
            datetime.now().strftime('%Y%m%d%H%M%S_%f'))
        if workspace.exists():raise RuntimeError('Collision in guest QA workspace')
        workspace.mkdir(parents=True,exist_ok=False)
        try:
            for key in ('sucesso','falha_compilacao','falha_pos_commit'):
                try:
                    info['cenarios'].append(scenario(workspace,input_dir,key))
                    info['engine_original_qa']=True
                except ScenarioFailure as exc:
                    info['cenarios'].append(exc.diagnostic)
                    if exc.diagnostic.get('motor_original_invocado'):
                        info['engine_original_qa']=True
                    raise
            info['status']='PASSOU_B1_EXECUTAVEIS_REAIS'
        finally:
            shutil.rmtree(workspace,ignore_errors=True)
    except Exception as exc:
        info['status']='FALHOU_OU_BLOQUEADO'
        info['erro_tipo']=type(exc).__name__
        info['erro']=str(exc)[:600]
        # Only sanitized diagnostic excerpts; never archive synthetic DB or EXEs.
        info['traceback_final']=traceback.format_exc()[-2500:]
    finally:
        data=json.dumps(info,indent=2,ensure_ascii=False).encode('utf-8')
        path=output_dir/'RESULTADO_G6B1.json'
        path.write_bytes(data)
        diagnostic=json.dumps({'component':'vighna-g6b1-sqlite-diagnostic',
            'version':'3.1.16','status':info['status'],
            'cenarios':info['cenarios']},indent=2,ensure_ascii=False).encode('utf-8')
        diagnostic_path=output_dir/'DIAGNOSTICO_SQLITE_G6B1.json'
        diagnostic_path.write_bytes(diagnostic)
        (output_dir/'MANIFESTO_G6B1_SHA256.json').write_text(
            json.dumps({'RESULTADO_G6B1.json':hashlib.sha256(data).hexdigest(),
                        'DIAGNOSTICO_SQLITE_G6B1.json':hashlib.sha256(diagnostic).hexdigest()},
                       indent=2),encoding='utf-8')
    return 0 if info['status']=='PASSOU_B1_EXECUTAVEIS_REAIS' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--input')
    parser.add_argument('--output')
    parser.add_argument('--probe-engine')
    opts=parser.parse_args()
    if opts.probe_engine:
        if opts.input or opts.output:
            parser.error('Probe mode does not accept input or output')
        try:
            engine=load_engine(Path(opts.probe_engine),'qa_probe')
            required=('version_from_file','inspect_package','install_package','check_database')
            if not all(callable(getattr(engine,n,None)) for n in required):
                raise RuntimeError('Motor original com API QA incompleta')
            print('G6B1_ENGINE_IMPORT_OK',flush=True)
        except Exception:
            traceback.print_exc()
            sys.exit(1)
        sys.exit(0)
    if not opts.input or not opts.output:
        parser.error('--input and --output required outside probe')
    sys.exit(run(Path(opts.input),Path(opts.output)) )
