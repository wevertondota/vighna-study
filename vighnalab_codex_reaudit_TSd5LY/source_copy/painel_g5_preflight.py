# -*- coding: utf-8 -*-
"""G5-A — auditoria conservadora do caminho do banco em código RC2, SEM abrir EXE.

Um PASS nesta bateria não é homologação G5. Verificações usam apenas pasta
sintética e uma cópia de caminhos.py, não os arquivos do usuário.
"""
from __future__ import annotations
import argparse
import ast
from datetime import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'insumos'/'M2_RC2_FONTE_REFERENCIA_NAO_INSTALAR.zip'
RC2_BUILD='structural-m2-int1-settings-r1d-rc2'


def _digest(data:bytes)->str:return hashlib.sha256(data).hexdigest()


def _read_source_member(archive: zipfile.ZipFile, logical_name: str) -> bytes:
    """Read only the unique expected file, accepting either ZIP path separator.

    ZIPs generated on Windows can contain backslashes in filenames. Python's
    zipfile normalizes those filenames to '/' on Windows but not on Linux.
    Comparing normalized names and reading the selected ZipInfo works on both.
    Ambiguous entries must not be silently accepted.
    """
    canonical = logical_name.replace("\\", "/")
    matches = [entry for entry in archive.infolist()
               if not entry.is_dir() and entry.filename.replace("\\", "/") == canonical]
    if len(matches) != 1:
        reason = "ausente" if not matches else "duplicado ou ambiguo"
        raise ValueError(f"Arquivo RC2 {reason} no ZIP: {canonical}")
    return archive.read(matches[0])


def run_g5_a():
    if getattr(sys, "frozen", False):
        raise ValueError("Diagnóstico G5-A depende de python.exe externo; não executar EXE congelado como interpretador")
    results=[]
    def check(label,ok,details=''):
        results.append({'teste':label,'passou':bool(ok),'observacao':details})
    if not SRC.is_file():
        raise ValueError('Fonte RC2 não encontrada')
    with zipfile.ZipFile(SRC) as z:
        if z.testzip() is not None:
            raise ValueError('Fonte de RC2 com CRC inválido')
        raw=_read_source_member(z, 'codigo/caminhos.py')
        raw_banco=_read_source_member(z, 'codigo/banco.py')
        raw_backup=_read_source_member(z, 'codigo/backup.py')
        versao=_read_source_member(z, 'codigo/versao.py')
    tree=ast.parse(raw)
    imports=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            imports.update(a.name for a in node.names)
        if isinstance(node,ast.ImportFrom):
            imports.add(node.module)
    check('caminhos.py importa apenas biblioteca padrão', imports <= {'sys','pathlib','__future__'},str(sorted(imports)))
    check('caminhos.py não importa main/banco/backup',not imports.intersection({'main','banco','backup'}))
    text=raw.decode('utf8')
    check('pasta de dados depende de caminho identificado',
          'localizar_pasta_dados()' in text and 'CAMINHO_BANCO' in text)
    check('schema/base RC2 confirmado',RC2_BUILD.encode() in versao)
    check('banco.py utiliza CAMINHO_BANCO',b'from caminhos import CAMINHO_BANCO' in raw_banco)
    check('backup.py usa caminho de dados central',b'from caminhos import CAMINHO_BANCO' in raw_backup)
    # Executa APENAS caminhos.py, que foi verificado como stdlib-only, em cópia
    # sintética controlada: sem importar banco, sem abrir a interface e sem EXE.
    with tempfile.TemporaryDirectory(prefix='vighna_g5a_sintetico_') as td:
        work=Path(td)
        fake=work/'codigo_qa';fake.mkdir()
        (fake/'main.py').write_text('# ARQUIVO SINTETICO\n',encoding='utf8')
        (fake/'VighnaStudy.spec').write_text('# SPEC SINTETICO\n',encoding='utf8')
        (fake/'caminhos.py').write_bytes(raw)
        program=('import os,sys,runpy,json,pathlib; '
                 'sys.path.insert(0,os.getcwd()); '
                 'v=runpy.run_path("caminhos.py"); '
                 'print(json.dumps({"local_sintetico":str(v["PASTA_DADOS"])==os.getcwd(),'
                 '"banco_sintetico":str(v["CAMINHO_BANCO"])==str(pathlib.Path.cwd()/"estudos.db"),'
                 '"backups_sinteticos":str(v["PASTA_BACKUPS"])==str(pathlib.Path.cwd()/"backups")}))')
        proc=subprocess.run([sys.executable,'-S','-B','-c',program],cwd=fake,
                            capture_output=True,text=True,timeout=15,env={
                                **os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1'})
        if proc.returncode:
            check('ensaio de localização do banco sintético',False,'Falha isolada: '+proc.stderr[-250:])
        else:
            data=json.loads(proc.stdout.strip().splitlines()[-1])
            check('localizador direciona banco e backups para laboratório',all(data.values()),str(data))
            check('ensaio não cria banco nem backups',not (fake/'estudos.db').exists() and not (fake/'backups').exists())
    okay=all(x['passou'] for x in results)
    return {'format':'vighna-g5a-diagnostico-v1','etapa':'G5-A',
            'observacao':'NÃO executou EXE real. G5 permanece PENDENTE mesmo que tudo passe.',
            'g5_aprovado':False,'instalacao_autorizada':False,
            'status':'DIAGNOSTICO_APROVADO' if okay else 'FALHOU',
            'fonte_sha256':_digest(raw),'resultados':results}


def create_report():
    result=run_g5_a()
    # Mesmo formato básico do homologador; NÃO informa execução de EXE.
    test={'status':'PASSOU' if result['status']=='DIAGNOSTICO_APROVADO' else 'FALHOU',
          'observacao':'Somente isolamento sintético; NÃO cumpre G5.'}
    summary={'modo':'g5_a_diagnostico','decisao':'NAO_HOMOLOGADO_AUTOMATICAMENTE',
             'instalacao_autorizada':False,'executavel_real_iniciado':False,
             'testes':{'g5_a_localizacao':test},
             'resultados':{'aprovados':int(test['status']=='PASSOU'),
                           'falhas':int(test['status']=='FALHOU'),'bloqueados':0}}
    # Localizar pasta de resultados pelo mesmo método V1.1.
    import painel_core as core
    folder=core.diagnostics_folder()
    target=folder/('G5_A_DIAGNOSTICO_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.zip')
    files={
        'G5_A_DIAGNOSTICO.json':json.dumps(result,indent=2,ensure_ascii=False).encode('utf8'),
        'RESUMO_HOMOLOGACAO.json':json.dumps(summary,indent=2,ensure_ascii=False).encode('utf8')
    }
    files['MANIFESTO_SHA256.json']=json.dumps({k:_digest(v) for k,v in files.items()},indent=2).encode('utf8')
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for n,bytes_ in files.items():z.writestr(n,bytes_)
    return target,result


def main():
    try:
        file,result=create_report()
        print('ETAPA_G5_A:',result['status'])
        print('AVISO: EXE real não iniciado; G5 permanece pendente.')
        print('ZIP DE EVIDENCIAS CRIADO:',file)
        return 0 if result['status']=='DIAGNOSTICO_APROVADO' else 1
    except (OSError,ValueError,zipfile.BadZipFile,subprocess.TimeoutExpired) as e:
        print('ETAPA G5-A BLOQUEADA:',str(e),file=sys.stderr)
        return 77

if __name__=='__main__':raise SystemExit(main())
