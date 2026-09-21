"""Auditoria simples do banco realmente utilizado pelo VighnaStudy.

Pode ser executado fora da interface para confirmar caminho, integridade e
contagens sem depender de PySide6.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from caminhos import CAMINHO_BANCO, PASTA_DADOS


def main() -> int:
    banco = Path(CAMINHO_BANCO).resolve()
    print("=" * 64)
    print("VighnaStudy - auditoria do banco ativo")
    print("=" * 64)
    print(f"Pasta de dados : {Path(PASTA_DADOS).resolve()}")
    print(f"Banco ativo    : {banco}")
    if not banco.is_file():
        print("ERRO: o banco ativo não existe.")
        return 2

    with sqlite3.connect(f"file:{banco}?mode=ro", uri=True) as con:
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        fk = con.execute("PRAGMA foreign_key_check").fetchall()
        total = int(con.execute("SELECT COUNT(*) FROM questoes").fetchone()[0] or 0)
        ativas = int(con.execute(
            "SELECT COUNT(*) FROM questoes WHERE ativa=1 AND COALESCE(excluida,0)=0"
        ).fetchone()[0] or 0)
        excluidas = int(con.execute(
            "SELECT COUNT(*) FROM questoes WHERE COALESCE(excluida,0)=1"
        ).fetchone()[0] or 0)
        dignidade = int(con.execute(
            """
            SELECT COUNT(*)
            FROM questoes q
            JOIN topicos t ON t.id=q.topico_id
            WHERE q.ativa=1 AND COALESCE(q.excluida,0)=0
              AND UPPER(t.nome) LIKE '%DIGNIDADE SEXUAL%'
            """
        ).fetchone()[0] or 0)
        penal = int(con.execute(
            """
            SELECT COUNT(*)
            FROM questoes q
            JOIN topicos t ON t.id=q.topico_id
            JOIN disciplinas d ON d.id=t.disciplina_id
            WHERE q.ativa=1 AND COALESCE(q.excluida,0)=0
              AND d.nome='Direito Penal'
            """
        ).fetchone()[0] or 0)

    print(f"Integridade     : {integrity}")
    print(f"Foreign keys    : {len(fk)} problema(s)")
    print(f"Registros       : {total}")
    print(f"Questões ativas : {ativas}")
    print(f"Na lixeira      : {excluidas}")
    print(f"Direito Penal   : {penal}")
    print(f"Dignidade Sexual: {dignidade}")

    legado = Path(PASTA_DADOS) / "dist" / "SistemaEstudos" / "estudos.db"
    if legado.is_file() and legado.resolve() != banco:
        print("")
        print("AVISO: há um banco legado em dist\\SistemaEstudos.")
        print(f"       {legado.resolve()}")
        print("       Ele não deve ser usado como banco ativo.")

    esperado = (ativas == 2551 and dignidade == 54)
    print("")
    if esperado and integrity == "ok" and not fk:
        print("STATUS: RECUPERAÇÃO 2026-09-20 CONFIRMADA.")
        return 0
    print("STATUS: contagens diferentes da base recuperada esperada (2551 / 54).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
