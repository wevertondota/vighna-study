# -*- coding: utf-8 -*-
"""
Retira do uso ativo as questões dos Títulos IV a VIII da Parte Geral de Direito Penal,
sem apagar os registros das questões nem os dados históricos/inteligência.

Estratégia:
- backup SQLite consistente antes da alteração;
- localiza os cinco tópicos pelas chaves estáveis, com fallback por nome;
- move as questões para a Lixeira (ativa=0, excluida=1);
- não altera alternativas, tentativas, revisões, controle_topico, importância,
  sessões, métricas ou qualquer outra tabela;
- gera manifesto com os IDs retirados, permitindo restauração futura;
- valida integridade e confirma que os cinco tópicos ficaram sem questões visíveis.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

TARGETS = [
    {
        "chave": "top_b0fe94280bf245bbbdb06c44795fecc2",
        "nome": "TÍTULO IV – DO CONCURSO DE PESSOAS",
    },
    {
        "chave": "top_dd2558b41c4040008e308ff0c8471ed0",
        "nome": "TÍTULO V – DAS PENAS",
    },
    {
        "chave": "top_4f1dccd4586d441ea859287ec43a68e3",
        "nome": "TÍTULO VI – DAS MEDIDAS DE SEGURANÇA",
    },
    {
        "chave": "top_fc7fa33f93d9438586d1d6136ea07fe5",
        "nome": "TÍTULO VII – DA AÇÃO PENAL",
    },
    {
        "chave": "top_c685c8f5b4794a569106070d1894d833",
        "nome": "TÍTULO VIII – DA EXTINÇÃO DA PUNIBILIDADE",
    },
]

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.replace("–", "-").replace("—", "-").replace(":", " ")
    return " ".join(s.upper().split())

def abrir_banco(db: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(db), timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA busy_timeout=30000")
    return con

def verificar_integridade(con: sqlite3.Connection) -> None:
    quick = con.execute("PRAGMA quick_check").fetchone()[0]
    if str(quick).lower() != "ok":
        raise RuntimeError(f"quick_check falhou: {quick}")
    fk = con.execute("PRAGMA foreign_key_check").fetchall()
    if fk:
        raise RuntimeError(f"foreign_key_check encontrou {len(fk)} problema(s).")

def backup_consistente(origem: Path, destino: Path) -> None:
    origem_con = abrir_banco(origem)
    try:
        verificar_integridade(origem_con)
        destino.parent.mkdir(parents=True, exist_ok=True)
        if destino.exists():
            destino.unlink()
        backup_con = sqlite3.connect(str(destino))
        try:
            origem_con.backup(backup_con)
            backup_con.commit()
        finally:
            backup_con.close()
    finally:
        origem_con.close()

    teste = sqlite3.connect(f"file:{destino}?mode=ro&immutable=1", uri=True)
    try:
        if teste.execute("PRAGMA quick_check").fetchone()[0].lower() != "ok":
            raise RuntimeError("O backup criado não passou no quick_check.")
    finally:
        teste.close()

def achar_topicos(con: sqlite3.Connection):
    disciplina = con.execute(
        "SELECT id, nome FROM disciplinas WHERE UPPER(TRIM(nome)) = 'DIREITO PENAL'"
    ).fetchone()
    if disciplina is None:
        raise RuntimeError("Disciplina 'Direito Penal' não foi localizada.")

    topicos = con.execute(
        "SELECT id, nome, chave_estavel FROM topicos WHERE disciplina_id=?",
        (int(disciplina["id"]),),
    ).fetchall()

    encontrados = []
    usados = set()
    for alvo in TARGETS:
        row = next(
            (r for r in topicos if str(r["chave_estavel"] or "") == alvo["chave"]),
            None,
        )
        if row is None:
            desejado = norm(alvo["nome"])
            row = next((r for r in topicos if norm(r["nome"]) == desejado), None)
        if row is None:
            raise RuntimeError(f"Tópico não localizado: {alvo['nome']}")
        if int(row["id"]) in usados:
            raise RuntimeError("A validação de tópicos encontrou IDs duplicados.")
        usados.add(int(row["id"]))
        encontrados.append(row)
    return encontrados

def rows_as_dicts(con, sql, params=()):
    return [dict(r) for r in con.execute(sql, params).fetchall()]

def snapshot_inteligencia(con, topic_ids, question_ids):
    ph_t = ",".join("?" for _ in topic_ids)
    ph_q = ",".join("?" for _ in question_ids) if question_ids else "NULL"
    return {
        "controle_topico": rows_as_dicts(
            con, f"SELECT * FROM controle_topico WHERE topico_id IN ({ph_t}) ORDER BY topico_id", topic_ids
        ),
        "revisoes": rows_as_dicts(
            con, f"SELECT * FROM revisoes WHERE topico_id IN ({ph_t}) ORDER BY id", topic_ids
        ),
        "topico_concurso_importancia": rows_as_dicts(
            con, f"SELECT * FROM topico_concurso_importancia WHERE topico_id IN ({ph_t}) ORDER BY concurso_id, topico_id",
            topic_ids,
        ),
        "tentativas_por_topico_snapshot": rows_as_dicts(
            con,
            f"SELECT * FROM tentativas_questoes WHERE topico_id_snapshot IN ({ph_t}) ORDER BY id",
            topic_ids,
        ),
        "tentativas_por_questao": rows_as_dicts(
            con,
            f"SELECT * FROM tentativas_questoes WHERE questao_id IN ({ph_q}) ORDER BY id",
            question_ids,
        ) if question_ids else [],
        "banco_erros_pendentes": rows_as_dicts(
            con,
            f"SELECT * FROM banco_erros_pendentes WHERE questao_id IN ({ph_q}) ORDER BY id",
            question_ids,
        ) if question_ids else [],
        "itens_sessao_questoes": rows_as_dicts(
            con,
            f"SELECT * FROM itens_sessao_questoes WHERE questao_id IN ({ph_q}) ORDER BY id",
            question_ids,
        ) if question_ids else [],
    }

def canon(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str, separators=(",", ":"))

def main():
    pasta = Path(__file__).resolve().parent
    db = pasta / "estudos.db"
    if not db.exists():
        print("[ERRO] estudos.db nao encontrado em:", db)
        print("Extraia este patch dentro de C:\\SistemaEstudos e execute novamente.")
        return 2

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backups = pasta / "backups"
    backup = backups / f"estudos_{timestamp}_antes_retirada_penal_titulos_IV_VIII.db"
    manifesto = backups / f"manifesto_retirada_penal_titulos_IV_VIII_{timestamp}.json"

    print("=" * 72)
    print(" VIGHNASTUDY - RETIRADA SEGURA DE QUESTOES | TITULOS IV A VIII")
    print("=" * 72)
    print("Banco:", db)
    print()
    print("Criando backup SQLite consistente...")
    backup_consistente(db, backup)
    print("[OK] Backup:", backup)

    con = abrir_banco(db)
    try:
        verificar_integridade(con)
        topicos = achar_topicos(con)
        topic_ids = [int(r["id"]) for r in topicos]

        questoes = rows_as_dicts(
            con,
            f"""
            SELECT id, topico_id, ativa, excluida
            FROM questoes
            WHERE topico_id IN ({",".join("?" for _ in topic_ids)})
            ORDER BY topico_id, id
            """,
            topic_ids,
        )
        question_ids = [int(q["id"]) for q in questoes]
        mover_ids = [int(q["id"]) for q in questoes if int(q.get("excluida") or 0) == 0]

        antes_inteligencia = snapshot_inteligencia(con, topic_ids, question_ids)

        resumo_antes = []
        print()
        print("Topicos localizados:")
        for t in topicos:
            tid = int(t["id"])
            visiveis = con.execute(
                "SELECT COUNT(*) FROM questoes WHERE topico_id=? AND COALESCE(excluida,0)=0",
                (tid,),
            ).fetchone()[0]
            ativas = con.execute(
                "SELECT COUNT(*) FROM questoes WHERE topico_id=? AND ativa=1 AND COALESCE(excluida,0)=0",
                (tid,),
            ).fetchone()[0]
            total = con.execute(
                "SELECT COUNT(*) FROM questoes WHERE topico_id=?",
                (tid,),
            ).fetchone()[0]
            resumo_antes.append({
                "topico_id": tid,
                "nome": t["nome"],
                "questoes_visiveis": int(visiveis),
                "questoes_ativas": int(ativas),
                "questoes_totais_preservadas": int(total),
            })
            print(f"  - {t['nome']}: {visiveis} questao(oes) fora da Lixeira")

        if not mover_ids:
            print()
            print("[INFO] Os cinco topicos ja estao sem questoes fora da Lixeira.")
            print("Nenhuma alteracao foi necessaria.")
            return 0

        print()
        print(f"Retirando {len(mover_ids)} questao(oes) do uso ativo, sem apagar registros...")

        con.execute("BEGIN IMMEDIATE")
        try:
            ph = ",".join("?" for _ in mover_ids)
            con.execute(
                f"""
                UPDATE questoes
                SET
                    ativa = 0,
                    excluida = 1,
                    excluida_em = datetime('now','localtime'),
                    atualizado_em = datetime('now','localtime')
                WHERE id IN ({ph})
                """,
                mover_ids,
            )

            # Validacao dentro da propria transacao.
            for t in topicos:
                resto = con.execute(
                    "SELECT COUNT(*) FROM questoes WHERE topico_id=? AND COALESCE(excluida,0)=0",
                    (int(t["id"]),),
                ).fetchone()[0]
                if int(resto) != 0:
                    raise RuntimeError(
                        f"O topico '{t['nome']}' ainda possui {resto} questao(oes) fora da Lixeira."
                    )

            depois_inteligencia = snapshot_inteligencia(con, topic_ids, question_ids)
            if canon(antes_inteligencia) != canon(depois_inteligencia):
                raise RuntimeError(
                    "A auditoria detectou alteracao em dados de inteligencia/historico. Rollback executado."
                )

            con.commit()
        except Exception:
            con.rollback()
            raise

        verificar_integridade(con)

        resumo_depois = []
        for t in topicos:
            tid = int(t["id"])
            visiveis = con.execute(
                "SELECT COUNT(*) FROM questoes WHERE topico_id=? AND COALESCE(excluida,0)=0",
                (tid,),
            ).fetchone()[0]
            lixeira = con.execute(
                "SELECT COUNT(*) FROM questoes WHERE topico_id=? AND COALESCE(excluida,0)=1",
                (tid,),
            ).fetchone()[0]
            total = con.execute(
                "SELECT COUNT(*) FROM questoes WHERE topico_id=?",
                (tid,),
            ).fetchone()[0]
            resumo_depois.append({
                "topico_id": tid,
                "nome": t["nome"],
                "questoes_visiveis": int(visiveis),
                "questoes_na_lixeira": int(lixeira),
                "questoes_totais_preservadas": int(total),
            })

        payload = {
            "operacao": "retirada_preservando_inteligencia",
            "executado_em": timestamp,
            "banco": str(db),
            "backup": str(backup),
            "topicos": resumo_depois,
            "questoes_movidas_ids": mover_ids,
            "quantidade_movida": len(mover_ids),
            "inteligencia_preservada": True,
            "tabelas_de_inteligencia_auditadas": list(antes_inteligencia.keys()),
        }
        manifesto.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        print()
        print("=" * 72)
        print(" RETIRADA CONCLUIDA COM SUCESSO")
        print("=" * 72)
        for x in resumo_depois:
            print(f"  {x['nome']}: {x['questoes_visiveis']} visiveis | {x['questoes_na_lixeira']} na Lixeira")
        print()
        print(f"Questões retiradas nesta operacao: {len(mover_ids)}")
        print("IDs e registros das questoes foram preservados.")
        print("Controle do topico, revisoes, importancia, tentativas e historico: preservados.")
        print("quick_check: ok")
        print("foreign_key_check: 0 problema(s)")
        print("Manifesto:", manifesto)
        print("Backup:", backup)
        print()
        print("IMPORTANTE: nao esvazie a Lixeira antes da substituicao pelas novas questoes.")
        return 0
    except Exception as exc:
        print()
        print("[ERRO] Operacao cancelada:", exc)
        print("Nenhuma alteracao parcial deve ser mantida.")
        print("Backup de seguranca:", backup)
        return 1
    finally:
        con.close()

if __name__ == "__main__":
    raise SystemExit(main())
