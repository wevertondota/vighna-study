from __future__ import annotations
import sqlite3
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Uso: copiar_banco_consistente.py ORIGEM DESTINO")
    origem = Path(sys.argv[1]).resolve()
    destino = Path(sys.argv[2]).resolve()
    if not origem.exists():
        raise SystemExit(f"Banco de origem não encontrado: {origem}")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.unlink(missing_ok=True)
    src = sqlite3.connect(origem, timeout=10)
    dst = sqlite3.connect(destino, timeout=10)
    try:
        src.execute("PRAGMA busy_timeout = 5000")
        src.backup(dst)
        resultado = dst.execute("PRAGMA integrity_check").fetchone()
        if not resultado or str(resultado[0]).strip().lower() != "ok":
            raise RuntimeError("A cópia do banco não passou no integrity_check.")
    finally:
        dst.close()
        src.close()


if __name__ == "__main__":
    main()
