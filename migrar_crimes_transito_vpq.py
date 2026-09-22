from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import sqlite3
import sys
import unicodedata
from pathlib import Path

MIGRACAO = "ctb_crimes_transito_simetria_compacta_72q_2026_09_22_v1"
DISCIPLINA_CANONICA = "Código de Trânsito Brasileiro (CTB)"
TOPICO_CANONICO = "Capítulo XIX: Dos Crimes de Trânsito"
EXPECTED_QUESTIONS = 72
EXPECTED_ALTERNATIVES = 4

BASE = Path(__file__).resolve().parent
DEFAULT_VPQ = BASE / "CTB_Capitulo_XIX_Crimes_de_Transito_72Q_SIMETRIA_COMPACTA_VPQ_1_1.txt"
MANIFEST = BASE / "manifest_crimes_transito.json"


def norm(text: str | None) -> str:
    text = unicodedata.normalize("NFKD", str(text or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch)).lower()
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def sha_norm(text: str | None) -> str:
    return hashlib.sha256(norm(text).encode("utf-8")).hexdigest()


def table_exists(con: sqlite3.Connection, table: str) -> bool:
    return con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone() is not None


def table_columns(con: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in con.execute(f'PRAGMA table_info("{table}")')}


def scalar(con: sqlite3.Connection, sql: str, params=()) -> int:
    return int(con.execute(sql, params).fetchone()[0] or 0)


def parse_vpq(path: Path) -> dict:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    lines = text.splitlines()
    first = next((x.strip() for x in lines if x.strip()), "")
    if first != "VIGHNA PDF — VPQ 1.1":
        raise RuntimeError("O TXT não possui cabeçalho VPQ 1.1 válido.")

    first_q = re.search(r"(?mi)^\s*QUESTÃO\s+\d+\s*$", text)
    if not first_q:
        raise RuntimeError("Nenhuma questão localizada no TXT.")

    meta = {}
    for line in text[:first_q.start()].splitlines():
        m = re.match(r"^\s*([^:]+?)\s*:\s*(.*?)\s*$", line)
        if m:
            meta[norm(m.group(1))] = m.group(2).strip()

    if norm(meta.get("capitulo", "")) != norm(TOPICO_CANONICO):
        raise RuntimeError(
            f"CAPÍTULO inesperado: {meta.get('capitulo')!r}. Esperado: {TOPICO_CANONICO!r}"
        )
    if int(meta.get("quantidade", "0") or 0) != EXPECTED_QUESTIONS:
        raise RuntimeError("O TXT deve declarar exatamente 72 questões.")
    if norm(meta.get("alternativas", "")) != norm("A-D"):
        raise RuntimeError("O TXT deve usar alternativas A-D.")

    markers = list(re.finditer(r"(?mi)^\s*QUESTÃO\s+(\d+)\s*$", text))
    questions = []
    for i, marker in enumerate(markers):
        end = markers[i + 1].start() if i + 1 < len(markers) else len(text)
        block = text[marker.end():end].strip()

        gm = re.search(r"(?mi)^\s*GABARITO\s*:\s*([A-D])\s*$", block)
        if not gm:
            raise RuntimeError(f"Questão {marker.group(1)} sem GABARITO válido.")

        pre = block[:gm.start()].strip()
        post = block[gm.end():].strip()
        am = list(re.finditer(r"(?mi)^\s*([A-D])\)\s*", pre))
        letters = [x.group(1).upper() for x in am]
        if letters != list("ABCD"):
            raise RuntimeError(f"Questão {marker.group(1)} não possui A-D em sequência.")

        enunciado = pre[:am[0].start()].strip()
        if not enunciado:
            raise RuntimeError(f"Questão {marker.group(1)} sem enunciado.")

        alternatives = []
        for j, a in enumerate(am):
            aend = am[j + 1].start() if j + 1 < len(am) else len(pre)
            alternatives.append((a.group(1).upper(), pre[a.end():aend].strip()))

        em = re.match(
            r"(?is)^\s*(?:EXPLICAÇÃO|EXPLICACAO|JUSTIFICATIVA)\s*:\s*(.*)$",
            post,
        )
        if not em:
            raise RuntimeError(f"Questão {marker.group(1)} sem EXPLICAÇÃO/JUSTIFICATIVA.")
        explanation = em.group(1).strip()

        questions.append({
            "numero": int(marker.group(1)),
            "enunciado": enunciado,
            "alternativas": alternatives,
            "gabarito": gm.group(1).upper(),
            "explicacao": explanation,
        })

    if len(questions) != EXPECTED_QUESTIONS:
        raise RuntimeError(f"Foram localizadas {len(questions)} questões; esperado: 72.")
    if [q["numero"] for q in questions] != list(range(1, EXPECTED_QUESTIONS + 1)):
        raise RuntimeError("A numeração das questões deve ser sequencial de 1 a 72.")
    return {"fonte": meta.get("fonte", ""), "questoes": questions}


def find_ctb_discipline(con: sqlite3.Connection) -> tuple[int, str]:
    rows = con.execute("SELECT id,nome FROM disciplinas ORDER BY id").fetchall()
    accepted = {
        norm("Código de Trânsito Brasileiro (CTB)"),
        norm("Código de Trânsito Brasileiro"),
        norm("CTB"),
    }
    matches = [(int(r[0]), str(r[1])) for r in rows if norm(r[1]) in accepted]
    if len(matches) != 1:
        raise RuntimeError(
            f"Disciplina CTB não localizada de forma única. Encontradas: {matches}"
        )
    return matches[0]


def find_topic(con: sqlite3.Connection, disciplina_id: int) -> tuple[int, str]:
    rows = con.execute(
        "SELECT id,nome FROM topicos WHERE disciplina_id=? ORDER BY id",
        (disciplina_id,),
    ).fetchall()
    matches = [(int(r[0]), str(r[1])) for r in rows if norm(r[1]) == norm(TOPICO_CANONICO)]
    if len(matches) != 1:
        raise RuntimeError(
            f"Tópico {TOPICO_CANONICO!r} não localizado de forma única. Encontrados: {matches}"
        )
    return matches[0]


def ensure_history_tables(con: sqlite3.Connection) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS historico_questoes_substituidas (
            migracao TEXT NOT NULL,
            questao_id_original INTEGER NOT NULL,
            disciplina TEXT NOT NULL,
            topico_id INTEGER,
            topico_nome TEXT,
            capitulo_id INTEGER,
            capitulo_nome TEXT,
            enunciado TEXT NOT NULL,
            explicacao TEXT,
            banca TEXT,
            ano INTEGER,
            fonte TEXT,
            dificuldade TEXT,
            ativa INTEGER,
            excluida INTEGER,
            criado_em TEXT,
            atualizado_em TEXT,
            arquivada_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            PRIMARY KEY (migracao, questao_id_original)
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS historico_alternativas_substituidas (
            migracao TEXT NOT NULL,
            questao_id_original INTEGER NOT NULL,
            letra TEXT NOT NULL,
            texto TEXT NOT NULL,
            correta INTEGER NOT NULL,
            ordem INTEGER NOT NULL,
            PRIMARY KEY (migracao, questao_id_original, letra)
        )
        """
    )


def serialize_alternatives(con: sqlite3.Connection, qid: int) -> tuple[str, str]:
    rows = con.execute(
        "SELECT letra,texto,correta,ordem FROM alternativas_questoes WHERE questao_id=? ORDER BY ordem,id",
        (qid,),
    ).fetchall()
    data = [
        {"letra": r[0], "texto": r[1], "correta": bool(r[2]), "ordem": int(r[3])}
        for r in rows
    ]
    gab = next((r[0] for r in rows if int(r[2]) == 1), "")
    return json.dumps(data, ensure_ascii=False), gab


def freeze_snapshots(con: sqlite3.Connection, qids: list[int], disciplina_id: int, disciplina_nome: str, topico_id: int, topico_nome: str) -> tuple[int, int]:
    qmap = {}
    for qid in qids:
        r = con.execute(
            """
            SELECT q.id,q.enunciado,q.explicacao,q.banca,q.ano,q.fonte,q.dificuldade,q.capitulo_id,
                   COALESCE(c.nome,'')
            FROM questoes q
            LEFT JOIN capitulos_topico c ON c.id=q.capitulo_id
            WHERE q.id=?
            """,
            (qid,),
        ).fetchone()
        qmap[qid] = r

    tentativas_atualizadas = 0
    if table_exists(con, "tentativas_questoes"):
        cols = table_columns(con, "tentativas_questoes")
        required = {
            "questao_id_snapshot","topico_id_snapshot","disciplina_id_snapshot",
            "disciplina_snapshot","topico_snapshot","enunciado_snapshot",
            "alternativas_snapshot","gabarito_snapshot","explicacao_snapshot",
            "banca_snapshot","ano_snapshot","fonte_snapshot","dificuldade_snapshot",
            "snapshot_origem"
        }
        if not required.issubset(cols):
            raise RuntimeError(
                "O banco possui tabela de tentativas sem as colunas de snapshot necessárias."
            )

        for qid in qids:
            q = qmap[qid]
            alts_json, gab = serialize_alternatives(con, qid)
            ids = con.execute(
                "SELECT id FROM tentativas_questoes WHERE questao_id=?",
                (qid,),
            ).fetchall()
            for (tid,) in ids:
                con.execute(
                    """
                    UPDATE tentativas_questoes SET
                        questao_id_snapshot=COALESCE(questao_id_snapshot,?),
                        topico_id_snapshot=COALESCE(topico_id_snapshot,?),
                        disciplina_id_snapshot=COALESCE(disciplina_id_snapshot,?),
                        disciplina_snapshot=COALESCE(disciplina_snapshot,?),
                        topico_snapshot=COALESCE(topico_snapshot,?),
                        enunciado_snapshot=COALESCE(enunciado_snapshot,?),
                        alternativas_snapshot=COALESCE(alternativas_snapshot,?),
                        gabarito_snapshot=COALESCE(gabarito_snapshot,?),
                        explicacao_snapshot=COALESCE(explicacao_snapshot,?),
                        banca_snapshot=COALESCE(banca_snapshot,?),
                        ano_snapshot=COALESCE(ano_snapshot,?),
                        fonte_snapshot=COALESCE(fonte_snapshot,?),
                        dificuldade_snapshot=COALESCE(dificuldade_snapshot,?),
                        snapshot_origem=COALESCE(NULLIF(snapshot_origem,''),'migracao_ctb_crimes_transito')
                    WHERE id=?
                    """,
                    (
                        qid, topico_id, disciplina_id, disciplina_nome, topico_nome,
                        q[1], alts_json, gab, q[2] or "", q[3] or "", q[4],
                        q[5] or "", q[6] or "Não informada", tid
                    ),
                )
                tentativas_atualizadas += 1

    itens_atualizados = 0
    if table_exists(con, "itens_sessao_questoes"):
        cols = table_columns(con, "itens_sessao_questoes")
        required = {
            "questao_id_snapshot","topico_id_snapshot","capitulo_id_snapshot",
            "disciplina_id_snapshot","disciplina_snapshot","topico_snapshot",
            "capitulo_snapshot","enunciado_snapshot","alternativas_snapshot",
            "gabarito_snapshot","explicacao_snapshot","banca_snapshot",
            "ano_snapshot","fonte_snapshot","dificuldade_snapshot"
        }
        if required.issubset(cols):
            for qid in qids:
                q = qmap[qid]
                alts_json, gab = serialize_alternatives(con, qid)
                ids = con.execute(
                    "SELECT id FROM itens_sessao_questoes WHERE questao_id=?",
                    (qid,),
                ).fetchall()
                for (iid,) in ids:
                    con.execute(
                        """
                        UPDATE itens_sessao_questoes SET
                            questao_id_snapshot=COALESCE(questao_id_snapshot,?),
                            topico_id_snapshot=COALESCE(topico_id_snapshot,?),
                            capitulo_id_snapshot=COALESCE(capitulo_id_snapshot,?),
                            disciplina_id_snapshot=COALESCE(disciplina_id_snapshot,?),
                            disciplina_snapshot=COALESCE(disciplina_snapshot,?),
                            topico_snapshot=COALESCE(topico_snapshot,?),
                            capitulo_snapshot=COALESCE(capitulo_snapshot,?),
                            enunciado_snapshot=COALESCE(enunciado_snapshot,?),
                            alternativas_snapshot=COALESCE(alternativas_snapshot,?),
                            gabarito_snapshot=COALESCE(gabarito_snapshot,?),
                            explicacao_snapshot=COALESCE(explicacao_snapshot,?),
                            banca_snapshot=COALESCE(banca_snapshot,?),
                            ano_snapshot=COALESCE(ano_snapshot,?),
                            fonte_snapshot=COALESCE(fonte_snapshot,?),
                            dificuldade_snapshot=COALESCE(dificuldade_snapshot,?)
                        WHERE id=?
                        """,
                        (
                            qid, topico_id, q[7], disciplina_id, disciplina_nome, topico_nome,
                            q[8] or "", q[1], alts_json, gab, q[2] or "", q[3] or "",
                            q[4], q[5] or "", q[6] or "Não informada", iid
                        ),
                    )
                    itens_atualizados += 1

    return tentativas_atualizadas, itens_atualizados


def archive_current(con: sqlite3.Connection, qids: list[int], disciplina_nome: str, topico_id: int, topico_nome: str) -> None:
    for qid in qids:
        r = con.execute(
            """
            SELECT q.id,q.capitulo_id,c.nome,q.enunciado,q.explicacao,q.banca,q.ano,
                   q.fonte,q.dificuldade,q.ativa,COALESCE(q.excluida,0),
                   q.criado_em,q.atualizado_em
            FROM questoes q
            LEFT JOIN capitulos_topico c ON c.id=q.capitulo_id
            WHERE q.id=?
            """,
            (qid,),
        ).fetchone()
        con.execute(
            """
            INSERT OR REPLACE INTO historico_questoes_substituidas(
                migracao,questao_id_original,disciplina,topico_id,topico_nome,
                capitulo_id,capitulo_nome,enunciado,explicacao,banca,ano,fonte,
                dificuldade,ativa,excluida,criado_em,atualizado_em
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                MIGRACAO, int(r[0]), disciplina_nome, topico_id, topico_nome,
                r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8],
                r[9], r[10], r[11], r[12]
            ),
        )
        for a in con.execute(
            "SELECT letra,texto,correta,ordem FROM alternativas_questoes WHERE questao_id=? ORDER BY ordem,id",
            (qid,),
        ).fetchall():
            con.execute(
                """
                INSERT OR REPLACE INTO historico_alternativas_substituidas(
                    migracao,questao_id_original,letra,texto,correta,ordem
                ) VALUES(?,?,?,?,?,?)
                """,
                (MIGRACAO, qid, a[0], a[1], int(a[2]), int(a[3])),
            )


def analytics_snapshot(con: sqlite3.Connection, topico_id: int, qids: list[int]) -> dict:
    placeholders = ",".join("?" for _ in qids)
    attempts = []
    if table_exists(con, "tentativas_questoes") and qids:
        attempts = [
            tuple(r) for r in con.execute(
                f"""
                SELECT id,sessao_id,questao_id,concurso_id,respondida_em,
                       alternativa_marcada,correta,marcada_duvida,tempo_segundos,
                       revisao_id,item_sessao_id
                FROM tentativas_questoes
                WHERE questao_id IN ({placeholders})
                ORDER BY id
                """,
                qids,
            ).fetchall()
        ]

    revisions = []
    if table_exists(con, "revisoes"):
        revisions = [
            tuple(r) for r in con.execute(
                "SELECT * FROM revisoes WHERE topico_id=? ORDER BY id",
                (topico_id,),
            ).fetchall()
        ]

    control = []
    if table_exists(con, "controle_topico"):
        control = [
            tuple(r) for r in con.execute(
                "SELECT * FROM controle_topico WHERE topico_id=?",
                (topico_id,),
            ).fetchall()
        ]

    return {"attempts": attempts, "revisions": revisions, "control": control}


def migrate(db_path: Path, vpq_path: Path, manifest_path: Path) -> dict:
    if not db_path.exists():
        raise FileNotFoundError(f"Banco não encontrado: {db_path}")

    pack = parse_vpq(vpq_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    by_old_hash = {m["old_enunciado_sha256"]: m for m in manifest}
    by_number = {q["numero"]: q for q in pack["questoes"]}

    if len(by_old_hash) != EXPECTED_QUESTIONS or len(by_number) != EXPECTED_QUESTIONS:
        raise RuntimeError("Manifesto ou VPQ com quantidade inconsistente.")

    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"estudos_antes_substituicao_ctb_crimes_transito_{timestamp}.db"
    shutil.copy2(db_path, backup_path)

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    try:
        if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("integrity_check falhou antes da migração.")
        if con.execute("PRAGMA foreign_key_check").fetchall():
            raise RuntimeError("foreign_key_check encontrou problemas antes da migração.")
        if not table_exists(con, "migracoes"):
            raise RuntimeError("Banco incompatível: tabela 'migracoes' ausente.")
        if con.execute("SELECT 1 FROM migracoes WHERE nome=?", (MIGRACAO,)).fetchone():
            return {"already_done": True, "backup": str(backup_path)}

        disciplina_id, disciplina_nome = find_ctb_discipline(con)
        topico_id, topico_nome = find_topic(con, disciplina_id)

        rows = con.execute(
            """
            SELECT id,enunciado
            FROM questoes
            WHERE topico_id=? AND ativa=1 AND COALESCE(excluida,0)=0
            ORDER BY id
            """,
            (topico_id,),
        ).fetchall()

        if len(rows) != EXPECTED_QUESTIONS:
            raise RuntimeError(
                f"O tópico possui {len(rows)} questões ativas; esperado: 72. "
                "Nada foi alterado. Envie o banco atual para reconciliação."
            )

        mapping = []
        seen_numbers = set()
        for row in rows:
            qid = int(row[0])
            h = sha_norm(row[1])
            m = by_old_hash.get(h)
            if m is None:
                raise RuntimeError(
                    f"A questão ID {qid} não corresponde ao conjunto antigo esperado. "
                    "Nada foi alterado."
                )

            alts = con.execute(
                "SELECT letra,texto,correta,ordem FROM alternativas_questoes WHERE questao_id=? ORDER BY ordem,id",
                (qid,),
            ).fetchall()
            if [a[0] for a in alts] != list("ABCD"):
                raise RuntimeError(f"Questão ID {qid} não possui A-D em sequência.")
            gab = [a[0] for a in alts if int(a[2]) == 1]
            if len(gab) != 1 or gab[0] != m["old_gabarito"]:
                raise RuntimeError(
                    f"Gabarito atual da questão ID {qid} diverge do conjunto esperado."
                )

            numero = int(m["numero"])
            if numero in seen_numbers:
                raise RuntimeError("Mapeamento duplicado detectado.")
            seen_numbers.add(numero)
            mapping.append((qid, numero))

        if seen_numbers != set(range(1, EXPECTED_QUESTIONS + 1)):
            raise RuntimeError("Não foi possível mapear as 72 questões antigas de forma integral.")

        con.execute("BEGIN IMMEDIATE")
        ensure_history_tables(con)
        qids = [qid for qid, _ in mapping]

        frozen_attempts, frozen_items = freeze_snapshots(
            con, qids, disciplina_id, disciplina_nome, topico_id, topico_nome
        )
        analytics_before = analytics_snapshot(con, topico_id, qids)
        archive_current(con, qids, disciplina_nome, topico_id, topico_nome)

        # Atualização IN PLACE: preserva IDs das questões e das alternativas,
        # mantendo cobertura, tentativas e demais vínculos da inteligência.
        changed_questions = 0
        changed_alternatives = 0

        for qid, numero in mapping:
            nq = by_number[numero]
            old = con.execute(
                "SELECT enunciado,explicacao,fonte FROM questoes WHERE id=?",
                (qid,),
            ).fetchone()

            if (
                old[0] != nq["enunciado"]
                or (old[1] or "") != nq["explicacao"]
                or (pack["fonte"] and (old[2] or "") != pack["fonte"])
            ):
                changed_questions += 1

            con.execute(
                """
                UPDATE questoes
                SET enunciado=?, explicacao=?, fonte=?,
                    atualizado_em=datetime('now','localtime')
                WHERE id=?
                """,
                (
                    nq["enunciado"],
                    nq["explicacao"],
                    pack["fonte"] or old[2],
                    qid,
                ),
            )

            existing = con.execute(
                "SELECT id,letra,texto,correta,ordem FROM alternativas_questoes WHERE questao_id=? ORDER BY ordem,id",
                (qid,),
            ).fetchall()
            existing_by_letter = {r[1]: r for r in existing}

            for ordem, (letra, texto) in enumerate(nq["alternativas"], start=1):
                row = existing_by_letter[letra]
                correta = 1 if letra == nq["gabarito"] else 0
                if row[2] != texto or int(row[3]) != correta or int(row[4]) != ordem:
                    changed_alternatives += 1
                con.execute(
                    """
                    UPDATE alternativas_questoes
                    SET texto=?, correta=?, ordem=?
                    WHERE id=?
                    """,
                    (texto, correta, ordem, int(row[0])),
                )

        analytics_after = analytics_snapshot(con, topico_id, qids)
        if analytics_before != analytics_after:
            raise RuntimeError(
                "Dados de desempenho/revisão foram alterados durante a substituição."
            )

        # Verificação exata do novo conteúdo.
        for qid, numero in mapping:
            nq = by_number[numero]
            r = con.execute(
                "SELECT enunciado,explicacao,fonte FROM questoes WHERE id=?",
                (qid,),
            ).fetchone()
            if r[0] != nq["enunciado"] or (r[1] or "") != nq["explicacao"]:
                raise RuntimeError(f"Falha de validação na questão {numero} / ID {qid}.")
            alts = con.execute(
                "SELECT letra,texto,correta FROM alternativas_questoes WHERE questao_id=? ORDER BY ordem,id",
                (qid,),
            ).fetchall()
            expected = [
                (letter, text, 1 if letter == nq["gabarito"] else 0)
                for letter, text in nq["alternativas"]
            ]
            if [tuple(x) for x in alts] != expected:
                raise RuntimeError(f"Falha de validação das alternativas na questão {numero}.")

        if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("integrity_check falhou após a substituição.")
        fk = con.execute("PRAGMA foreign_key_check").fetchall()
        if fk:
            raise RuntimeError(f"foreign_key_check encontrou {len(fk)} problema(s).")

        con.execute(
            "INSERT INTO migracoes(nome,executada_em) VALUES(?,datetime('now','localtime'))",
            (MIGRACAO,),
        )
        con.commit()

        return {
            "already_done": False,
            "backup": str(backup_path),
            "topico_id": topico_id,
            "questoes": len(mapping),
            "changed_questions": changed_questions,
            "changed_alternatives": changed_alternatives,
            "frozen_attempts": frozen_attempts,
            "frozen_items": frozen_items,
            "tentativas": len(analytics_after["attempts"]),
            "revisoes": len(analytics_after["revisions"]),
        }
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Substitui, em lugar, as 72 questões de Crimes de Trânsito pelos novos VPQ 1.1, preservando IDs e inteligência."
    )
    parser.add_argument("--db", default=r"C:\SistemaEstudos\estudos.db")
    parser.add_argument("--vpq", default=str(DEFAULT_VPQ))
    parser.add_argument("--manifest", default=str(MANIFEST))
    args = parser.parse_args()

    print("=== VighnaStudy — Substituição CTB / Crimes de Trânsito ===")
    print(f"Banco: {args.db}")
    print(f"VPQ  : {args.vpq}")
    result = migrate(Path(args.db), Path(args.vpq), Path(args.manifest))

    if result.get("already_done"):
        print("\nEsta substituição já está registrada no banco.")
        return 0

    print("\nSUBSTITUIÇÃO CONCLUÍDA COM SUCESSO")
    print(f"Backup: {result['backup']}")
    print(f"Questões atualizadas no mesmo ID: {result['questoes']}")
    print(f"Questões com texto/explicação alterados: {result['changed_questions']}")
    print(f"Alternativas alteradas: {result['changed_alternatives']}")
    print(f"Tentativas históricas preservadas: {result['tentativas']}")
    print(f"Revisões do tópico preservadas: {result['revisoes']}")
    print(f"Snapshots de tentativas completados: {result['frozen_attempts']}")
    print(f"Snapshots de itens completados: {result['frozen_items']}")
    print("integrity_check: ok")
    print("foreign_key_check: 0 problemas")
    print("\nOs IDs das 72 questões e de suas alternativas foram preservados.")
    print("Cobertura, tentativas, revisões e vínculos da inteligência permanecem associados às mesmas questões.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"\nERRO: {exc}", file=sys.stderr)
        print("A transação foi revertida. O banco não ficou parcialmente alterado.", file=sys.stderr)
        raise
