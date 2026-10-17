# -*- coding: utf-8 -*-
"""G6-B2 Windows Sandbox: original R1D transactional updater + actual PyInstaller.

Prepared Python base and isolated QA site-packages are mapped read-only from the
host. No dependency downloads, live VighnaStudy installation, or personal DB.
The full G6 Gate and G7 remain blocked even if G6-B2 succeeds.
"""
from __future__ import annotations
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from xml.etree import ElementTree as ET
import zipfile

import painel_g6b as b1

RC2_BUILD=b1.RC2_BUILD
MAX_SANDBOX_SECONDS=2700
SCENARIOS={
    'sucesso':('PASSOU_B2_BUILD_ORIGINAL','installed','installed'),
    'falha_compilacao':('PASSOU_B2_ROLLBACK_ORIGINAL','pre_commit_no_snapshot','failed'),
    'falha_pos_commit':('PASSOU_B2_ROLLBACK_ORIGINAL','recovered','failed'),
}

class G6B2SafetyError(b1.G6BSafetyError): pass


def checked_qa_runtime(py:Path)->tuple[Path,Path,dict]:
    """Provide only an explicitly dedicated QA venv and its Python installation."""
    py=Path(py).resolve(strict=True)
    venv=py.parent.parent
    if (venv.name!='Ambiente_Qt_Homologador' or
            venv.parent.name!='VighnaLab' or
            py.name.lower()!='python.exe' or
            not (venv/'pyvenv.cfg').is_file()):
        raise G6B2SafetyError('Somente Python do Ambiente_Qt_Homologador no VighnaLab')
    packages=venv/'Lib'/'site-packages'
    if not packages.is_dir():raise G6B2SafetyError('QA site-packages ausente')
    for module in ('PyInstaller','PySide6','qtawesome'):
        if not (packages/module).is_dir():
            raise G6B2SafetyError('Dependencia QA ausente: '+module)
    code=('import json,sys,PyInstaller,PySide6,qtawesome;'
          'print(json.dumps({"base_prefix":sys.base_prefix,'
          '"version":sys.version.split()[0],'
          '"pyinstaller":PyInstaller.__version__,"pyside6":PySide6.__version__}))')
    try:
        result=subprocess.run([str(py),'-B','-c',code],capture_output=True,
                              text=True,errors='replace',timeout=35,check=False)
        if result.returncode!=0:raise ValueError(result.stderr[-400:])
        details=json.loads(result.stdout)
    except (OSError,ValueError,subprocess.TimeoutExpired) as exc:
        raise G6B2SafetyError('QA Python base/dependencies preflight failed') from exc
    base=Path(details['base_prefix']).resolve(strict=True)
    if (base==venv or not (base/'python.exe').is_file() or not (base/'Lib').is_dir()
            or not (base/'DLLs').is_dir()):
        raise G6B2SafetyError('Base Python Windows sem DLLs/Lib; bloqueado')
    for folder in (venv,packages,base):
        if folder.is_symlink() or (hasattr(folder,'is_junction') and folder.is_junction()):
            raise G6B2SafetyError('Junction/symlink no runtime QA')
        if (folder/'estudos.db').exists() or (folder/'VighnaStudy.exe').exists():
            raise G6B2SafetyError('Pasta QA contaminada por arquivos do programa real')
    return base,packages,details


def sandbox_xml(input_dir:Path,out_dir:Path,python_base:Path,packages:Path)->str:
    root=ET.Element('Configuration')
    for tag in ('vGPU','Networking','ClipboardRedirection','PrinterRedirection',
                'AudioInput','VideoInput'):
        ET.SubElement(root,tag).text='Disable'
    maps=ET.SubElement(root,'MappedFolders')
    for host,guest in (
        (input_dir,r'C:\VighnaQA\Entrada'),(out_dir,r'C:\VighnaQA\Saida'),
        (python_base,r'C:\VighnaQA\PythonBase'),(packages,r'C:\VighnaQA\PythonPackages')):
        m=ET.SubElement(maps,'MappedFolder')
        ET.SubElement(m,'HostFolder').text=str(host)
        ET.SubElement(m,'SandboxFolder').text=guest
        ET.SubElement(m,'ReadOnly').text='false' if host==out_dir else 'true'
    ET.SubElement(ET.SubElement(root,'LogonCommand'),'Command').text=(
        r'C:\VighnaQA\Entrada\G6B2_GUEST.exe --input C:\VighnaQA\Entrada --output C:\VighnaQA\Saida')
    ET.indent(root,space='  ')
    return '<?xml version="1.0" encoding="utf-8"?>\n'+ET.tostring(root,encoding='unicode')+'\n'


def build_guest(py:Path,code:Path,lab:Path,imports:tuple[str,...])->Path:
    import homologador_windows as h
    dist=lab/'DIST_G6B2_GUEST';work=lab/'BUILD_G6B2_GUEST'
    spec=lab/'SPEC_G6B2_GUEST';spec.mkdir()
    log=lab/'BUILD_G6B2_GUEST.log'
    cmd=[str(py),'-B','-m','PyInstaller','--noconfirm','--clean','--onefile',
         '--console','--name','G6B2_GUEST',
         *(f'--hidden-import={x}' for x in imports),
         '--distpath',str(dist),'--workpath',str(work),'--specpath',str(spec),str(code)]
    env=h.environment_qa(lab)
    for key in ('PYTHONHOME','PYTHONPATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH'):
        env.pop(key,None)
    print('ETAPA_G6B2: congelando executor de QA...',flush=True)
    with log.open('wb') as output:
        process=subprocess.Popen(cmd,cwd=str(lab),env=env,stdout=output,stderr=subprocess.STDOUT)
        try:ret=process.wait(timeout=b1.MAX_BUILD_SECONDS)
        except subprocess.TimeoutExpired:
            process.kill();process.wait();raise G6B2SafetyError('Build guest timeout')
    exe=dist/'G6B2_GUEST.exe'
    if ret!=0 or not exe.is_file():
        raise G6B2SafetyError('PyInstaller guest G6-B2 failed; see BUILD_G6B2_GUEST.log')
    return exe


def validate_guest_report(guest:dict)->None:
    if (guest.get('component')!='vighna-g6b2-guest' or
        guest.get('version')!='3.1.19' or guest.get('target_build')!=RC2_BUILD or
        guest.get('instalacao_autorizada') is not False or
        guest.get('gate_g6_aprovado') is not False or
        guest.get('windows_sandbox_executado') is not True or
        guest.get('original_builder_in_guest') is not True or
        guest.get('status')!='PASSOU_B2_PYINSTALLER_ORIGINAL_SANDBOX'):
        raise G6B2SafetyError('Guest identity/safety/completion invalid')
    scenarios=guest.get('cenarios')
    if not isinstance(scenarios,list) or len(scenarios)!=3:
        raise G6B2SafetyError('Three complete B2 scenarios required')
    if [s.get('cenario') for s in scenarios]!=list(SCENARIOS):
        raise G6B2SafetyError('G6-B2 scenario order/identity invalid')
    for s in scenarios:
        name=s['cenario']; status,phase,history=SCENARIOS[name]
        if (s.get('status')!=status or s.get('fase_checkpoint')!=phase or
                s.get('historico_final')!=history or s.get('banco_qa_preservado') is not True or
                s.get('motor_original_invocado') is not True or
                s.get('build_original_invocado') is not True or
                not s.get('pyinstaller_log_sha256') or
                s.get('pyinstaller_log_bytes',0)<=0 or
                s.get('smoke_antes',{}).get('stable') is not True or
                s.get('smoke_depois',{}).get('stable') is not True):
            raise G6B2SafetyError('G6-B2 scenario evidence invalid: '+name)
        checks=s.get('comparacoes_sqlite',[])
        if (len(checks)<4 or any(c.get('logica_alterada') for c in checks[1:])
                or checks[1].get('fisica_alterada') is not False):
            raise G6B2SafetyError('G6-B2 database integrity evidence invalid: '+name)


def diagnostic_zip(out:Path,summary:dict,logs:list[Path])->Path:
    entries={'RESUMO_G6B2.json':json.dumps(summary,indent=2,ensure_ascii=False).encode()}
    for logfile in logs:
        if logfile.is_file():entries[logfile.name+'.txt']=logfile.read_bytes()[-110_000:]
    for item in ('RESULTADO_G6B2.json','MANIFESTO_G6B2_SHA256.json'):
        file=out/item
        if file.is_file():
            if file.stat().st_size>9_000_000:raise G6B2SafetyError('Oversize diagnostic: '+item)
            entries[item]=file.read_bytes()
    entries['MANIFESTO_SHA256.json']=json.dumps(
        {k:hashlib.sha256(v).hexdigest() for k,v in entries.items()},indent=2).encode()
    name=out/('G6_B2_DIAGNOSTICO_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.zip')
    with zipfile.ZipFile(name,'w',zipfile.ZIP_DEFLATED) as z:
        for k,v in entries.items():z.writestr(k,v)
    with zipfile.ZipFile(name) as z:
        if z.testzip() is not None:raise G6B2SafetyError('Diagnostic ZIP invalid')
    return name


def run(py:Path|None=None,*,launch:bool=True)->dict:
    import homologador_windows as h
    if sys.platform!='win32':raise G6B2SafetyError('Windows Sandbox required')
    h.preflight_selftest()
    b1.ensure_safe(b1.root_qa())
    win=Path(os.environ.get('WINDIR',r'C:\Windows'))/'System32'/'WindowsSandbox.exe'
    if not win.is_file():raise G6B2SafetyError('WindowsSandbox.exe missing')
    py=Path(py or sys.executable)
    base_python,packages,details=checked_qa_runtime(py)
    base=h.checked_archive(h.KIT/'insumos'/h.BASE)
    patch=h.checked_archive(h.KIT/'insumos'/h.PATCH)
    rc2=h.checked_archive(h.KIT/'insumos'/h.RC2,prefix='codigo/')
    h.inspect_static(base,patch,rc2)
    lab=b1.root_qa()/('G6B2_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    lab.parent.mkdir(parents=True,exist_ok=True)
    lab.mkdir(exist_ok=False)
    inp=lab/'ENTRADA_SOMENTE_LEITURA';inp.mkdir()
    out=lab/'SAIDA';out.mkdir()
    logs=[lab/'BUILD_R1D.log',lab/'BUILD_G6B2_GUEST.log',lab/'PROBE_G6B2_GUEST.log']
    result={'component':'vighna-g6b2-host','version':'3.1.20',
            'status':'BLOQUEADO','target_build':RC2_BUILD,
            'instalacao_autorizada':False,'gate_g6_aprovado':False,
            'user_db_or_installation_used':False,'windows_sandbox_executado':False,
            'original_builder_in_guest':False,'qa_runtime':details}
    process=None
    try:
        sources=dict(base);sources['vighnastudy.ico']=rc2['vighnastudy.ico']
        work=lab/'FONTES_R1D';h.write_sources(sources,work)
        exe=b1.build(py,work,lab,'R1D')
        shutil.copytree(exe.parent,inp/'R1D',symlinks=False)
        result['r1d_sha256']=h.digest_file(exe)
        imports=b1.engine_hidden_imports(base['vighna_update_engine.py'])
        guest=build_guest(py,h.KIT/'painel_g6b2_guest.py',lab,imports)
        # Probe executable by requesting --help (cannot access the mapped runtime on host).
        probe=subprocess.run([str(guest),'--help'],capture_output=True,timeout=60,check=False)
        logs[-1].write_bytes(probe.stdout[-2000:]+probe.stderr[-2000:])
        if probe.returncode!=0 or b'--input' not in probe.stdout:
            raise G6B2SafetyError('Frozen B2 guest launch probe failed')
        shutil.copy2(guest,inp/'G6B2_GUEST.exe')
        # The R1D QA sources intentionally omit binary assets. Its .spec, however,
        # references vighnastudy.ico by absolute path inside the staging source.
        # Provide only the independently verified RC2 reference icon, already
        # used for the host R1D build, as a manifest-hashed read-only QA input.
        icon_bytes=rc2.get('vighnastudy.ico')
        if (not isinstance(icon_bytes,bytes) or not 6 <= len(icon_bytes) <= 300_000
                or icon_bytes[:4] != b'\x00\x00\x01\x00'):
            raise G6B2SafetyError('QA icon from verified RC2 source absent or invalid')
        (inp/'vighnastudy.ico').write_bytes(icon_bytes)
        for rel in (h.BASE,h.PATCH):shutil.copy2(h.KIT/'insumos'/rel,inp/rel)
        hashes={f.relative_to(inp).as_posix():h.digest_file(f)
                for f in sorted(inp.rglob('*')) if f.is_file()}
        (inp/'MANIFESTO_G6B2.json').write_text(json.dumps({
            'component':'vighna-g6b2-input','version':'3.1.19',
            'target_build':RC2_BUILD,'sha256_files':hashes,
            'instalacao_autorizada':False,'build_original_dentro_sandbox':True},indent=2),encoding='utf8')
        conf=lab/'G6B2_SOMENTE_SANDBOX.wsb'
        conf.write_text(sandbox_xml(inp,out,base_python,packages),encoding='utf8')
        result['status']='PREPARADO_NAO_EXECUTADO'
        if launch:
            print('ETAPA_G6B2: iniciando Sandbox offline com Python QA montado somente leitura...',flush=True)
            try: sandbox_before = b1.sandbox_processes_qa()
            except (OSError, subprocess.SubprocessError, b1.G6BSafetyError): sandbox_before = None
            process=subprocess.Popen([str(win),str(conf)],cwd=str(lab))
            start=time.monotonic()
            while time.monotonic()-start<MAX_SANDBOX_SECONDS:
                report=out/'RESULTADO_G6B2.json';manifest=out/'MANIFESTO_G6B2_SHA256.json'
                if report.is_file() and manifest.is_file():
                    blob=report.read_bytes();sig=json.loads(manifest.read_text(encoding='utf8'))
                    if sig.get(report.name)!=hashlib.sha256(blob).hexdigest():
                        raise G6B2SafetyError('G6-B2 guest hash mismatch')
                    guest_data=json.loads(blob.decode('utf8'))
                    result['guest']=guest_data
                    result['windows_sandbox_executado']=guest_data.get('windows_sandbox_executado') is True
                    if guest_data.get('status')=='PASSOU_B2_PYINSTALLER_ORIGINAL_SANDBOX':
                        validate_guest_report(guest_data)
                        result['original_builder_in_guest']=True
                    result['status']=guest_data.get('status','BLOQUEADO')
                    break
                if process.poll() is not None:raise G6B2SafetyError('Sandbox closed before evidence')
                time.sleep(3)
            else:raise G6B2SafetyError('Sandbox timeout')
    except Exception as exc:
        result['status']='FALHOU_OU_BLOQUEADO';result['motivo']=str(exc)[:700]
    finally:
        try:
            result['encerramento_sandbox'] = b1.close_own_sandbox(
                process, ownership_snapshot=(locals().get('sandbox_before')
                    if locals().get('sandbox_before') is not None else {}),
                evidence_confirmed=(locals().get('sandbox_before') is not None
                    and result.get('windows_sandbox_executado') is True
                    and result.get('original_builder_in_guest') is True))
            if 'manual' in result['encerramento_sandbox']['estado']:
                print('ETAPA_G6B2: Sandbox permanece aberto; feche pela janela X quando conveniente.',flush=True)
        except Exception as exc:
            result['erro_encerramento_sandbox'] = str(exc)[:300]
        zipfile_out=diagnostic_zip(out,result,logs)
        print('ZIP DE DIAGNOSTICO CRIADO: '+str(zipfile_out),flush=True)
        print('STATUS G6-B2: '+result['status']+'; G6 / G7 NAO AUTORIZADOS.',flush=True)
    return result

if __name__=='__main__':
    try:
        output=run()
        sys.exit(0 if output['status']=='PASSOU_B2_PYINSTALLER_ORIGINAL_SANDBOX' else 1)
    except Exception as exc:
        print('G6-B2 BLOQUEADO: '+str(exc),file=sys.stderr,flush=True)
        sys.exit(1)
