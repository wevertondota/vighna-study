from __future__ import annotations

import argparse
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path

TOPICO = "Capítulo XIX: Dos Crimes de Trânsito"
VPQ = Path(__file__).resolve().parent / "CTB_Capitulo_XIX_Crimes_de_Transito_72Q_SIMETRIA_COMPACTA_VPQ_1_1.txt"


def norm(text):
    text = unicodedata.normalize("NFKD", str(text or ""))
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    text = text.replace("–","-").replace("—","-")
    text = re.sub(r"[^a-z0-9]+"," ",text)
    return " ".join(text.split())


def parse(path: Path):
    text = path.read_text(encoding="utf-8-sig").replace("\r\n","\n")
    markers = list(re.finditer(r"(?mi)^\s*QUESTÃO\s+(\d+)\s*$", text))
    out = []
    for i,m in enumerate(markers):
        end = markers[i+1].start() if i+1 < len(markers) else len(text)
        block = text[m.end():end].strip()
        gm = re.search(r"(?mi)^\s*GABARITO\s*:\s*([A-D])\s*$", block)
        pre = block[:gm.start()].strip()
        post = block[gm.end():].strip()
        am = list(re.finditer(r"(?mi)^\s*([A-D])\)\s*", pre))
        en = pre[:am[0].start()].strip()
        alts=[]
        for j,a in enumerate(am):
            aend=am[j+1].start() if j+1<len(am) else len(pre)
            alts.append((a.group(1).upper(),pre[a.end():aend].strip()))
        em = re.match(r"(?is)^\s*(?:EXPLICAÇÃO|EXPLICACAO|JUSTIFICATIVA)\s*:\s*(.*)$",post)
        exp = em.group(1).strip()
        out.append((en,alts,gm.group(1).upper(),exp))
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--db", default=r"C:\SistemaEstudos\estudos.db")
    args=ap.parse_args()
    db=Path(args.db)
    if not db.exists():
        raise FileNotFoundError(db)

    expected=parse(VPQ)
    con=sqlite3.connect(db)
    con.execute("PRAGMA foreign_keys=ON")

    disciplines=con.execute("SELECT id,nome FROM disciplinas").fetchall()
    accepted={norm("Código de Trânsito Brasileiro"),norm("Código de Trânsito Brasileiro (CTB)"),norm("CTB")}
    ds=[r for r in disciplines if norm(r[1]) in accepted]
    if len(ds)!=1:
        raise RuntimeError(f"Disciplina CTB ambígua: {ds}")
    did=ds[0][0]
    ts=[r for r in con.execute("SELECT id,nome FROM topicos WHERE disciplina_id=?",(did,)).fetchall() if norm(r[1])==norm(TOPICO)]
    if len(ts)!=1:
        raise RuntimeError(f"Tópico não localizado: {ts}")
    tid=ts[0][0]

    rows=con.execute("""
        SELECT id,enunciado,explicacao
        FROM questoes
        WHERE topico_id=? AND ativa=1 AND COALESCE(excluida,0)=0
        ORDER BY id
    """,(tid,)).fetchall()

    current={}
    for qid,en,exp in rows:
        alts=con.execute("SELECT letra,texto,correta FROM alternativas_questoes WHERE questao_id=? ORDER BY ordem,id",(qid,)).fetchall()
        gab=next((a[0] for a in alts if int(a[2])==1),"")
        key=(en,tuple((a[0],a[1]) for a in alts),gab,exp or "")
        current[key]=qid

    expected_keys={(en,tuple(alts),gab,exp) for en,alts,gab,exp in expected}
    current_keys=set(current.keys())

    integrity=con.execute("PRAGMA integrity_check").fetchone()[0]
    fk=con.execute("PRAGMA foreign_key_check").fetchall()
    migration=con.execute(
        "SELECT executada_em FROM migracoes WHERE nome=?",
        ("ctb_crimes_transito_simetria_compacta_72q_2026_09_22_v1",)
    ).fetchone()
    con.close()

    print("=== Verificação — CTB / Crimes de Trânsito ===")
    print(f"Questões ativas no tópico: {len(rows)}")
    print(f"Questões esperadas no VPQ: {len(expected)}")
    print(f"Conteúdo exato correspondente: {'SIM' if current_keys == expected_keys else 'NÃO'}")
    print(f"Migração registrada: {'SIM' if migration else 'NÃO'}")
    print(f"integrity_check: {integrity}")
    print(f"foreign_key_check: {len(fk)} problema(s)")

    ok=(len(rows)==72 and len(expected)==72 and current_keys==expected_keys and migration and integrity=="ok" and not fk)
    if ok:
        print("\nSTATUS: OK — as 72 novas questões substituíram o conjunto anterior.")
        return 0

    print("\nSTATUS: ATENÇÃO — a substituição não está integralmente confirmada.")
    return 1


if __name__=="__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise
