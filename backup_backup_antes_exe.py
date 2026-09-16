from datetime import datetime
from pathlib import Path
import shutil


PASTA_PROJETO = Path(__file__).resolve().parent
ARQUIVO_BANCO = PASTA_PROJETO / "estudos.db"
PASTA_BACKUPS = PASTA_PROJETO / "backups"
MAX_BACKUPS = 30


def garantir_pasta_backups():
    PASTA_BACKUPS.mkdir(
        parents=True,
        exist_ok=True
    )


def limpar_backups_antigos():
    garantir_pasta_backups()

    backups = sorted(
        PASTA_BACKUPS.glob("estudos_*.db"),
        key=lambda caminho: caminho.stat().st_mtime,
        reverse=True
    )

    for arquivo in backups[MAX_BACKUPS:]:
        try:
            arquivo.unlink()
        except OSError:
            pass


def fazer_backup(motivo="manual"):
    if not ARQUIVO_BANCO.exists():
        return None

    garantir_pasta_backups()

    agora = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    destino = (
        PASTA_BACKUPS /
        f"estudos_{agora}_{motivo}.db"
    )

    shutil.copy2(
        ARQUIVO_BANCO,
        destino
    )

    limpar_backups_antigos()

    return destino
