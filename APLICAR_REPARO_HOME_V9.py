# -*- coding: utf-8 -*-
"""Reparo externo controlado usando o motor nativo do VighnaStudy.

NAO altera o VighnaLab, nao remove validacoes nem substitui manualmente o executavel.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime

PACKAGE_NAME = "VighnaStudy_HOME_V9_HOTFIX_QIMAGE_R2_APOS_SIMULADOS_R1.zip"
EXPECTED_SHA256 = "33be0eb9e40bdb197f06ad712330ab099d86b8350caa3696b4f60c0f6767372b"


def running_vighna_study():
    if os.name != 'nt':
        raise RuntimeError('Este reparo e destinado ao Windows.')
    p = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq VighnaStudy.exe', '/NH'],
                       capture_output=True, text=True, errors='replace', timeout=12,
                       creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if p.returncode != 0:
        raise RuntimeError('Nao foi possivel verificar processos. Pare por seguranca.')
    return any(line.strip().lower().startswith('vighnastudy.exe ') for line in p.stdout.splitlines())


def main():
    root = Path(__file__).resolve().parent
    package = root / PACKAGE_NAME
    required = ['vighna_update_engine.py', 'versao.py', 'VighnaStudy.spec', 'estudos.db',
                'ui/home_r4h_canvas.py', 'dist/SistemaEstudos/VighnaStudy.exe']
    if not all((root / item).is_file() for item in required):
        raise RuntimeError('Arquivos obrigatorios ausentes. Extraia os 4 arquivos deste ZIP diretamente na raiz real do VighnaStudy (ex.: C:/SistemaEstudos). Nenhuma alteracao feita.')
    if running_vighna_study():
        raise RuntimeError('O VighnaStudy.exe ainda esta em execucao. Feche o programa e tente novamente.')
    if not package.is_file():
        raise RuntimeError('Pacote corretivo nao encontrado: ' + PACKAGE_NAME)
    actual = hashlib.sha256(package.read_bytes()).hexdigest()
    if actual != EXPECTED_SHA256:
        raise RuntimeError('Hash SHA-256 do pacote divergente. Nenhuma alteracao feita.')
    # Importa o motor ORIGINAL e aplica exatamente as suas validacoes de
    # manifesto, build, schema, banco, compilacao, backup e rollback.
    import vighna_update_engine as engine
    # Preflight somente leitura.
    info = engine.inspect_package(package, root)
    engine.check_database(root / 'estudos.db')
    if shutil.disk_usage(root).free < (2 * 1024 * 1024 * 1024):
        raise RuntimeError('Espaco livre inferior a 2 GB; compilacao e backups bloqueados por seguranca.')
    print('\nDIAGNOSTICO:')
    print('  VighnaStudy: '+info['base_version'])
    print('  Correcao: PySide6 QImage.fromData / PNG')
    print('  Alterados: ui/home_r4h_canvas.py e versao.py')
    print('  Banco de dados: preservado; backup verificado pelo atualizador')
    print('  Alvo: ' + str(root))
    print('  O VighnaLab NAO sera modificado.')
    print('\nO motor nativo compilara o executavel em staging, guardara o anterior')
    print('e fara rollback se ocorrer falha.')
    value = input('\nDigite INSTALAR para autorizar ou ENTER para cancelar: ').strip()
    if value != 'INSTALAR':
        print('Cancelado; nenhum arquivo foi alterado.')
        return 0
    recovered = engine.recover_incomplete_updates(root)
    if recovered:
        print('Instalacoes incompletas recuperadas: ' + ', '.join(recovered))
        # O build pode ter mudado com a recuperacao; checar outra vez.
        info = engine.inspect_package(package, root)
    def progress(percent, status):
        print(f'[{percent:3}%] {status}', flush=True)
    result = engine.install_package(package, root, python_exe=Path(sys.executable), report=progress)
    summary = {'instalado_em':datetime.now().isoformat(), 'pacote_sha256':actual,
               'backup':result['backup'], 'executavel':result['executable'],
               'base_build':info['base_build'], 'build_instalado':result['manifest']['target_build']}
    report = root / 'RELATORIO_REPARO_HOME_V9_R2.json'
    report.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print('\nREPARO CONCLUIDO. Relatorio: ' + str(report))
    print('Abra o VighnaStudy normalmente e teste a Home.')
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print('\nREPARO NAO CONCLUIDO: ' + str(error))
        print('Nenhum mecanismo de seguranca foi desativado.')
        sys.exit(1)
