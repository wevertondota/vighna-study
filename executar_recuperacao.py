"""Recuperacao externa da E4 do VighnaStudy via motor de atualizacao existente.

Nao substitui o banco de estudos. Requer a .venv e o PyInstaller ja instalados.
Recusa builds diferentes da E4, arquivos fonte divergentes e processos abertos.
"""
from __future__ import annotations
import hashlib
import os
import subprocess
import sys
from pathlib import Path

EXPECTED_E4_MAIN_SHA256 = 'b79dcb8cf4b8787260e3fcd64aea616e30c309320f3c4a00246283a08393bf76'
PACKAGE_FILENAME = 'VighnaStudy_0.29.59_Foco_Premium_E4R2_Correcao_QSize.zip'


def confirm_program_closed() -> None:
    if os.name != 'nt':
        raise RuntimeError('Esta recuperacao so pode ser executada no Windows.')
    result = subprocess.run(
        ['tasklist', '/FI', 'IMAGENAME eq VighnaStudy.exe', '/NH'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, errors='replace', timeout=20,
        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
    )
    if result.returncode != 0:
        raise RuntimeError('Nao foi possivel conferir os processos. Recuperacao cancelada.')
    if any(line.strip().lower().startswith('vighnastudy.exe ') for line in result.stdout.splitlines()):
        raise RuntimeError('O VighnaStudy esta aberto. Feche o programa antes de executar a recuperacao.')


def main() -> int:
    tool_dir = Path(__file__).resolve().parent
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else tool_dir.parent
    package = tool_dir / PACKAGE_FILENAME
    print('VIGHNASTUDY — CORRECAO DE INICIALIZACAO E4R2', flush=True)
    print('Pasta selecionada:', root, flush=True)

    required = [root / 'main.py', root / 'versao.py', root / 'vighna_update_engine.py',
                root / 'estudos.db', root / 'VighnaStudy.spec',
                root / 'dist' / 'SistemaEstudos' / 'VighnaStudy.exe',
                root / '.venv' / 'Scripts' / 'python.exe', package]
    missing = [p for p in required if not p.is_file()]
    if missing:
        raise RuntimeError('Estrutura nao encontrada. O script deve estar em '
                           'uma pasta CORRECAO_FOCO_E4 dentro da raiz do VighnaStudy '
                           '(onde ficam main.py e estudos.db). Ausentes: '
                           + ', '.join(p.name for p in missing))
    if Path(sys.executable).resolve() != (root / '.venv' / 'Scripts' / 'python.exe').resolve():
        raise RuntimeError('Execucao fora da .venv da instalacao. Use RECUPERAR_FOCO_E4.cmd.')
    try:
        import PyInstaller  # noqa: F401
    except ImportError as exc:
        raise RuntimeError('PyInstaller ausente na .venv. Recuperacao cancelada.') from exc
    confirm_program_closed()
    digest = hashlib.sha256((root / 'main.py').read_bytes()).hexdigest()
    if digest != EXPECTED_E4_MAIN_SHA256:
        raise RuntimeError('main.py diferente da E4 R1 conhecida. Nada foi alterado. '
                           'Nao force a atualizacao; informe o build instalado.')

    # Importar o motor da INSTALACAO, e nao incluir outro motor desconhecido no ZIP.
    sys.path.insert(0, str(root))
    from vighna_update_engine import (
        inspect_package, check_database, recover_incomplete_updates, install_package
    )

    print('[1/4] Verificando pacote, build E4 e banco...', flush=True)
    manifest = inspect_package(package, root)
    if not manifest['target_build'].endswith('-focus-e4r2-fix-qsize-local-scope-v1'):
        raise RuntimeError('Pacote de recuperacao inesperado. Operacao cancelada.')
    check_database(root / 'estudos.db')
    print('[2/4] Verificando transacoes anteriores...', flush=True)
    # A implementacao original restaura somente transacoes com estado "committing".
    recovered = recover_incomplete_updates(root)
    if recovered:
        print('Transacoes incompletas recuperadas:', ', '.join(recovered), flush=True)
        # Se o estado mudou, conferir novamente a compatibilidade antes de agir.
        inspect_package(package, root)
    print('[3/4] Instalando por build isolado, com backup e rollback automaticos...', flush=True)
    def report(pct, message):
        print(f'   [{pct}%] {message}', flush=True)
    outcome = install_package(package, root, python_exe=sys.executable, report=report)
    print('[4/4] Corrigido. Atualizacao concluida sem substituir estudos.db.', flush=True)
    print('Backup e historico de instalacao:', outcome.get('backup', 'registrado pelo atualizador'), flush=True)
    print('Abra o VighnaStudy pelo atalho normal.', flush=True)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as error:
        print('\nRECUPERACAO NAO CONCLUIDA:', str(error), file=sys.stderr, flush=True)
        print('Se ocorreu alguma falha, nao tente forcar a substituicao de arquivos.', file=sys.stderr, flush=True)
        raise SystemExit(1)
