# -*- coding: utf-8 -*-
"""Restaura as questões retiradas pela última operação, usando o manifesto gerado."""
from __future__ import annotations
import json, sqlite3, sys
from pathlib import Path

def main():
    pasta = Path(__file__).resolve().parent
    db = pasta / "estudos.db"
    backups = pasta / "backups"
    manifests = sorted(backups.glob("manifesto_retirada_penal_titulos_IV_VIII_*.json"), reverse=True)
    if not db.exists():
        print("[ERRO] estudos.db nao encontrado.")
        return 2
    if not manifests:
        print("[ERRO] Nenhum manifesto de retirada foi encontrado em backups.")
        return 2

    manifesto = manifests[0]
    dados = json.loads(manifesto.read_text(encoding="utf-8"))
    ids = [int(x) for x in dados.get("questoes_movidas_ids", [])]
    if not ids:
        print("[INFO] O manifesto nao contem IDs para restaurar.")
        return 0

    con = sqlite3.connect(str(db), timeout=30)
    try:
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA busy_timeout=30000")
        if con.execute("PRAGMA quick_check").fetchone()[0].lower() != "ok":
            raise RuntimeError("Banco nao passou no quick_check.")
        ph = ",".join("?" for _ in ids)
        con.execute("BEGIN IMMEDIATE")
        con.execute(
            f"""
            UPDATE questoes
            SET ativa=1, excluida=0, excluida_em=NULL,
                atualizado_em=datetime('now','localtime')
            WHERE id IN ({ph})
            """,
            ids,
        )
        con.commit()
        print(f"[OK] {len(ids)} questao(oes) restaurada(s) a partir de:")
        print(manifesto)
        return 0
    except Exception as exc:
        con.rollback()
        print("[ERRO]", exc)
        return 1
    finally:
        con.close()

if __name__ == "__main__":
    raise SystemExit(main())
