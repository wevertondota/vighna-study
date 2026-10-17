# -*- coding: utf-8 -*-
"""G6-B2 isolated Windows Sandbox executor. Original engine and PyInstaller builder.

Only QA source bundles, compiled QA R1D, and read-only mapped QA Python runtime.
No production data, no precompiled RC2 callback, no installation authorization.
"""
from __future__ import annotations
import argparse
from contextlib import closing
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sqlite3
import stat
import subprocess
import sys
import traceback

import painel_g6b_guest as q  # Reuse G6-B1 audited SQLite and GUI diagnostics.

RC2_BUILD=q.RC2_BUILD
BASE_VERSION=q.BASE_VERSION
SCENARIOS=('sucesso','falha_compilacao','falha_pos_commit')
PYTHON_BASE=Path(r'C:\VighnaQA\PythonBase')
QA_PACKAGES=Path(r'C:\VighnaQA\PythonPackages')


def verify_input(folder:Path)->dict:
    manifest=q.read_json(folder/'MANIFESTO_G6B2.json')
    if (manifest.get('component')!='vighna-g6b2-input' or
            manifest.get('target_build')!=RC2_BUILD or
            manifest.get('instalacao_autorizada') is not False or
            manifest.get('build_original_dentro_sandbox') is not True):
        raise ValueError('G6-B2 input identity mismatch')
    expected=manifest.get('sha256_files')
    if not isinstance(expected,dict) or not 5<=len(expected)<=1400:
        raise ValueError('Invalid G6-B2 input file count')
    actual={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
    if actual!=set(expected)|{'MANIFESTO_G6B2.json'}:
        raise ValueError('Unexpected G6-B2 input file')
    for name,digest in expected.items():
        parts=PurePosixPath(name).parts
        if (not parts or '\\' in name or ':' in name or name.startswith('/') or
                '..' in parts or '.' in parts or not isinstance(digest,str) or len(digest)!=64):
            raise ValueError('Invalid G6-B2 input entry')
        file=folder.joinpath(*parts)
        if file.is_symlink() or q.hash_file(file)!=digest:
            raise ValueError('G6-B2 SHA-256 mismatch: '+name)
    return manifest


def runtime_environment()->dict:
    """Host QA folders are mounted read-only. Never probe/install using host system Python."""
    if not (PYTHON_BASE/'python.exe').is_file() or not (QA_PACKAGES/'PyInstaller').is_dir():
        raise RuntimeError('Windows Sandbox QA runtime missing; no fallback to system Python')
    env=os.environ.copy()
    for key in ('PYTHONPATH','PYTHONHOME','PYTHONUSERBASE','QT_PLUGIN_PATH',
                'QT_QPA_PLATFORM_PLUGIN_PATH','PIP_TARGET','PIP_PREFIX'):
        env.pop(key,None)
    env.update({'PYTHONHOME':str(PYTHON_BASE), 'PYTHONPATH':str(QA_PACKAGES),
                'PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1',
                'PIP_NO_INDEX':'1','PIP_DISABLE_PIP_VERSION_CHECK':'1'})
    return env


def probe_guest_python(python:Path, env:dict)->dict:
    cmd=[str(python),'-B','-c',
         'import json,sys,PyInstaller,PySide6,qtawesome; '
         'print(json.dumps({"prefix":sys.prefix,"version":sys.version.split()[0],'
         '"pyinstaller":PyInstaller.__version__,"pyside6":PySide6.__version__}))']
    probe=subprocess.run(cmd,env=env,cwd=str(PYTHON_BASE),capture_output=True,
                         text=True,errors='replace',timeout=90,check=False)
    if probe.returncode!=0:
        raise RuntimeError('Sandbox PyInstaller runtime failed: '+probe.stderr[-600:])
    try: result=json.loads(probe.stdout.strip())
    except ValueError as exc: raise RuntimeError('Sandbox Python probe unreadable') from exc
    if Path(result['prefix'])!=PYTHON_BASE or not result.get('pyinstaller'):
        raise RuntimeError('Sandbox interpreter prefix/packaging differs from QA mount')
    return result


def stage_qa_icon(inp:Path,source:Path)->str:
    """Supply the icon expected by the unmodified .spec, from QA input only.

    Input files are checked by verify_input() against the host manifest before
    any scenario is run. Never search user folders or relax build requirements.
    """
    icon=inp/'vighnastudy.ico'
    if not icon.is_file() or icon.is_symlink():
        raise RuntimeError('Verified QA build icon unavailable')
    data=icon.read_bytes()
    if not 6 <= len(data) <= 300_000 or data[:4]!=b'\x00\x00\x01\x00':
        raise RuntimeError('Verified QA build icon invalid')
    target=source/'vighnastudy.ico'
    if target.exists() or target.is_symlink():
        raise RuntimeError('Unexpected icon already present in R1D QA sources')
    target.write_bytes(data)
    digest=q.hash_file(target)
    if digest!=q.hash_file(icon):
        raise RuntimeError('QA icon integrity failed after staging')
    return digest


def run_scenario(parent:Path,inp:Path,name:str,python:Path,env:dict)->dict:
    result={'cenario':name,'status':'EM_EXECUCAO','operacao_atual':'preparar_cenario',
            'etapas_sqlite':[],'comparacoes_sqlite':[],
            'motor_original_invocado':False,'build_original_invocado':False,
            'banco_qa_preservado':False}
    try:
        root=parent/name;root.mkdir(parents=True,exist_ok=False)
        source=root/'codigo'
        q.safe_extract_sources(inp/'BASE_R1D_SOMENTE_FONTES_QA.zip',source)
        # Asset is absent from the source-only R1D ZIP but required by its .spec.
        # The original production engine already copies it into its staging area.
        result['icone_qa_sha256']=stage_qa_icon(inp,source)
        engine=q.load_engine(source/'vighna_update_engine.py','b2_'+name)
        if engine.version_from_file(source/'versao.py')!=BASE_VERSION:
            raise RuntimeError('Unexpected R1D base')
        db=source/'estudos.db'
        with closing(sqlite3.connect(db)) as con:
            with con:
                con.execute('CREATE TABLE g6b_marker(id INTEGER PRIMARY KEY,data TEXT)')
                con.execute('INSERT INTO g6b_marker VALUES (39,?)',('SOMENTE_QA_G6B1',))
        created=q.sqlite_snapshot(db,'apos_criar_sqlite_sintetico')
        result['etapas_sqlite'].append(created);q.require_valid_synthetic(created)
        active=source/'dist'/'SistemaEstudos'
        shutil.copytree(inp/'R1D',active)
        old_hash=q.hash_file(active/'VighnaStudy.exe')
        result['exe_r1d_sha256']=old_hash
        patch=inp/'CANDIDATO_QA_R1D_PARA_M2_RC2_NAO_INSTALAR.zip'
        if engine.inspect_package(patch,source)['target_build']!=RC2_BUILD:
            raise RuntimeError('Target differs from RC2')
        original_version=(source/'versao.py').read_bytes()
        original_main=q.hash_file(source/'main.py')
        original_spec=(source/'VighnaStudy.spec').read_bytes()
        result['operacao_atual']='iniciar_executavel_r1d'
        before=q.smoke(active,root,'r1d');result['smoke_antes']=before
        if not before.get('stable'):raise RuntimeError('Real R1D smoke failed')
        initialized=q.sqlite_snapshot(db,'apos_iniciar_executavel_r1d')
        result['etapas_sqlite'].append(initialized);q.require_valid_synthetic(initialized)
        result['comparacoes_sqlite'].append(q.sqlite_comparison(created,initialized))
        if name=='falha_compilacao':
            # Fault injected INTO THE REAL PyInstaller spec. No runner injection.
            (source/'VighnaStudy.spec').write_text(
                "raise RuntimeError('FALHA_QA_G6B2_BUILD')\n",encoding='utf8')
        if name=='falha_pos_commit':
            real_check=engine.check_database
            def check(path):
                if Path(path)==db and engine.version_from_file(source/'versao.py')[1]==RC2_BUILD:
                    raise engine.UpdateError('FALHA_QA_G6B2_POST_COMMIT')
                return real_check(path)
            engine.check_database=check
        progress=[]
        result['operacao_atual']='motor_original_pyinstaller_'+name
        result['motor_original_invocado']=True
        result['build_original_invocado']=True
        previous_env={k:os.environ.get(k) for k in env}
        try:
            os.environ.update(env)  # inherited by engine's real subprocess.Popen
            try:
                # CRITICAL: no runner parameter; original engine runs PyInstaller itself.
                engine.install_package(patch,source,python_exe=python,
                                       report=lambda n,msg:progress.append(n))
                if name!='sucesso':raise RuntimeError('Expected controlled failure absent')
            except engine.UpdateError as exc:
                if name=='sucesso':raise
                if name=='falha_compilacao':
                    if not (source/'backups'/'atualizacoes').is_dir():raise
                elif 'FALHA_QA_G6B2_POST_COMMIT' not in str(exc):raise
            finally:
                (source/'VighnaStudy.spec').write_bytes(original_spec)
        finally:
            if name=='falha_pos_commit':engine.check_database=real_check
            for k,old in previous_env.items():
                if old is None:os.environ.pop(k,None)
                else:os.environ[k]=old
        result['progresso']=progress
        result['operacao_atual']='verificar_compilacao_real'
        history_root=source/'backups'/'atualizacoes'
        saves=[x for x in history_root.iterdir() if x.is_dir()]
        if len(saves)!=1:raise RuntimeError('Build history count invalid')
        saved=saves[0]
        log=saved/'build.log'
        if not log.is_file() or not log.stat().st_size:
            raise RuntimeError('Original PyInstaller build.log missing')
        log_text=log.read_text(encoding='utf-8',errors='replace')
        if name=='falha_compilacao' and 'FALHA_QA_G6B2_BUILD' not in log_text:
            raise RuntimeError('PyInstaller did not exercise controlled spec failure')
        result['pyinstaller_log_sha256']=q.hash_file(log)
        result['pyinstaller_log_bytes']=log.stat().st_size
        result['pyinstaller_log_final']=log_text[-1400:]
        after=q.sqlite_snapshot(db,'apos_transacao_'+name)
        result['etapas_sqlite'].append(after);q.require_valid_synthetic(after)
        result['comparacoes_sqlite'].append(q.require_sqlite_preserved(initialized,after,physical=True))
        backup=q.sqlite_snapshot(saved/'estudos.db','backup_motor_original')
        q.require_valid_synthetic(backup)
        result['comparacoes_sqlite'].append(q.require_sqlite_preserved(initialized,backup,physical=False))
        events=[json.loads(s) for s in (history_root/'historico.jsonl').read_text(encoding='utf8').splitlines()]
        checkpoints=list(history_root.glob('*/state.json'))
        if name=='falha_compilacao':
            if checkpoints:raise RuntimeError('Precommit failure should have no commit checkpoint')
            phase='pre_commit_no_snapshot'
        else:
            if len(checkpoints)!=1:raise RuntimeError('Missing transaction checkpoint')
            phase=q.read_json(checkpoints[0])['phase']
        old_saved=saved/'anterior_executavel'/'VighnaStudy.exe'
        if name=='sucesso':
            if (engine.version_from_file(source/'versao.py')[1]!=RC2_BUILD or
                    q.hash_file(active/'VighnaStudy.exe')==old_hash or
                    not old_saved.is_file() or q.hash_file(old_saved)!=old_hash or
                    phase!='installed' or events[-1]['status']!='installed'):
                raise RuntimeError('Real PyInstaller deployment or prior executable backup invalid')
            end_label='rc2';status='PASSOU_B2_BUILD_ORIGINAL'
        else:
            if (engine.version_from_file(source/'versao.py')!=BASE_VERSION or
                    (source/'versao.py').read_bytes()!=original_version or
                    q.hash_file(source/'main.py')!=original_main or
                    (source/'VighnaStudy.spec').read_bytes()!=original_spec or
                    q.hash_file(active/'VighnaStudy.exe')!=old_hash or
                    events[-1]['status']!='failed' or events[-1].get('rollback_errors')):
                raise RuntimeError('Real PyInstaller rollback verification failed')
            if name=='falha_pos_commit' and phase!='recovered':
                raise RuntimeError('Post-commit recovery checkpoint absent')
            end_label='r1d_restaurado';status='PASSOU_B2_ROLLBACK_ORIGINAL'
        result['operacao_atual']='smoke_final_'+end_label
        final=q.smoke(active,root,end_label)
        result['smoke_depois']=final
        if not final.get('stable'):raise RuntimeError('Final QA executable smoke failed')
        end=q.sqlite_snapshot(db,'apos_iniciar_'+end_label)
        result['etapas_sqlite'].append(end);q.require_valid_synthetic(end)
        result['comparacoes_sqlite'].append(q.require_sqlite_preserved(after,end,physical=False))
        result.update({'status':status,'operacao_atual':'concluido',
                       'exe_final_sha256':q.hash_file(active/'VighnaStudy.exe'),
                       'banco_qa_preservado':True,'fase_checkpoint':phase,
                       'historico_final':events[-1]['status']})
        return result
    except Exception as exc:
        result['status']='FALHOU_OU_BLOQUEADO';result['operacao_falhou']=result['operacao_atual']
        result['erro_tipo']=type(exc).__name__;result['erro']=str(exc)[:600]
        if isinstance(exc,q.SQLiteDivergence):result['primeira_divergencia']=exc.divergence
        raise q.ScenarioFailure(str(exc),result) from exc


def run(input_dir:Path,output_dir:Path)->int:
    info={'component':'vighna-g6b2-guest','version':'3.1.19',
          'target_build':RC2_BUILD,'status':'BLOQUEADO',
          'windows_sandbox_executado':sys.platform=='win32',
          'original_builder_in_guest':False,'instalacao_autorizada':False,
          'gate_g6_aprovado':False,'cenarios':[]}
    output_dir.mkdir(parents=True,exist_ok=True)
    try:
        if sys.platform!='win32':raise RuntimeError('Windows Sandbox required')
        verify_input(input_dir)
        env=runtime_environment()
        python=PYTHON_BASE/'python.exe'
        info['python_qa']=probe_guest_python(python,env)
        workspace=q.guest_workspace_dir(
            Path(os.environ.get('TEMP',r'C:\Windows\Temp')),
            datetime.now().strftime('%Y%m%d%H%M%S_%f'))
        if workspace.exists():raise RuntimeError('Workspace collision')
        workspace.mkdir(parents=True,exist_ok=False)
        try:
            for key in SCENARIOS:
                try:
                    info['cenarios'].append(run_scenario(workspace,input_dir,key,python,env))
                except q.ScenarioFailure as exc:
                    info['cenarios'].append(exc.diagnostic)
                    raise
            info['original_builder_in_guest']=True
            info['status']='PASSOU_B2_PYINSTALLER_ORIGINAL_SANDBOX'
        finally:
            shutil.rmtree(workspace,ignore_errors=True)
    except Exception as exc:
        info['status']='FALHOU_OU_BLOQUEADO';info['erro_tipo']=type(exc).__name__
        info['erro']=str(exc)[:600];info['traceback_final']=traceback.format_exc()[-2500:]
    finally:
        payload=json.dumps(info,indent=2,ensure_ascii=False).encode()
        name='RESULTADO_G6B2.json'
        tmp=output_dir/(name+'.tmp');tmp.write_bytes(payload);os.replace(tmp,output_dir/name)
        manifest={'RESULTADO_G6B2.json':hashlib.sha256(payload).hexdigest()}
        data=json.dumps(manifest,indent=2).encode()
        tmp=output_dir/'MANIFESTO_G6B2_SHA256.json.tmp';tmp.write_bytes(data)
        os.replace(tmp,output_dir/'MANIFESTO_G6B2_SHA256.json')
    return 0 if info['status']=='PASSOU_B2_PYINSTALLER_ORIGINAL_SANDBOX' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--input',required=True);p.add_argument('--output',required=True)
    args=p.parse_args();sys.exit(run(Path(args.input),Path(args.output)))
