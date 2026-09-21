from __future__ import annotations
import argparse, json, os, sqlite3, sys, unicodedata, re
from datetime import datetime
from pathlib import Path


def norm(s: str | None) -> str:
    s = unicodedata.normalize('NFKC', s or '').strip().casefold()
    return re.sub(r'\s+', ' ', s)


def backup_sqlite(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(src) as s, sqlite3.connect(dst) as d:
        s.backup(d)
        check = d.execute('PRAGMA integrity_check').fetchone()[0]
        if check != 'ok':
            raise RuntimeError(f'Backup falhou no integrity_check: {check}')


def resolve_disc(cur, info):
    row = cur.execute('SELECT id FROM disciplinas WHERE chave_estavel=?', (info.get('chave_estavel'),)).fetchone()
    if not row:
        row = cur.execute('SELECT id FROM disciplinas WHERE nome=?', (info.get('nome'),)).fetchone()
    if not row:
        raise RuntimeError(f"Disciplina não encontrada: {info.get('nome')}")
    return int(row[0])


def resolve_topico(cur, disciplina_id, info):
    row = cur.execute('SELECT id FROM topicos WHERE chave_estavel=?', (info.get('chave_estavel'),)).fetchone()
    if not row:
        row = cur.execute('SELECT id FROM topicos WHERE disciplina_id=? AND nome=?', (disciplina_id, info.get('nome'))).fetchone()
    if not row:
        raise RuntimeError(f"Tópico não encontrado: {info.get('nome')}")
    return int(row[0])


def resolve_capitulo(cur, topico_id, info):
    if not info:
        return None
    row = cur.execute('SELECT id FROM capitulos_topico WHERE chave_estavel=?', (info.get('chave_estavel'),)).fetchone()
    if not row:
        row = cur.execute('SELECT id FROM capitulos_topico WHERE topico_id=? AND nome=?', (topico_id, info.get('nome'))).fetchone()
    if not row:
        raise RuntimeError(f"Capítulo não encontrado: {info.get('nome')}")
    return int(row[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--target', required=True)
    ap.add_argument('--data', required=True)
    ap.add_argument('--backup-dir', required=True)
    args = ap.parse_args()
    target = Path(args.target).resolve()
    data_path = Path(args.data).resolve()
    backup_dir = Path(args.backup_dir).resolve()
    if not target.exists():
        raise SystemExit(f'ERRO: banco não encontrado: {target}')
    payload = json.loads(data_path.read_text(encoding='utf-8'))
    recs = payload['questoes']
    stamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup = backup_dir / f'estudos_antes_merge_recuperacao_{stamp}.db'
    backup_sqlite(target, backup)
    print(f'Backup criado: {backup}')

    con = sqlite3.connect(target)
    con.row_factory = sqlite3.Row
    try:
        cur = con.cursor()
        check = cur.execute('PRAGMA integrity_check').fetchone()[0]
        if check != 'ok':
            raise RuntimeError(f'Banco atual inválido: {check}')
        existing = {norm(r[0]) for r in cur.execute('SELECT enunciado FROM questoes')}
        inserted = 0
        skipped = 0
        con.execute('BEGIN IMMEDIATE')
        for rec in recs:
            q = rec['questao']
            key = norm(q.get('enunciado'))
            if key in existing:
                skipped += 1
                continue
            did = resolve_disc(cur, rec['disciplina'])
            tid = resolve_topico(cur, did, rec['topico'])
            cid = resolve_capitulo(cur, tid, rec.get('capitulo'))
            cols = ['topico_id','enunciado','explicacao','banca','ano','fonte','dificuldade','ativa','criado_em','atualizado_em','excluida','excluida_em','analise_pendente','analise_solicitada_em','capitulo_id']
            vals = [tid, q.get('enunciado'), q.get('explicacao'), q.get('banca'), q.get('ano'), q.get('fonte'), q.get('dificuldade'), q.get('ativa',1), q.get('criado_em'), q.get('atualizado_em'), q.get('excluida',0), q.get('excluida_em'), q.get('analise_pendente',0), q.get('analise_solicitada_em'), cid]
            placeholders = ','.join('?' for _ in cols)
            cur.execute(f"INSERT INTO questoes ({','.join(cols)}) VALUES ({placeholders})", vals)
            new_id = cur.lastrowid
            for alt in rec['alternativas']:
                cur.execute('INSERT INTO alternativas_questoes (questao_id,letra,texto,correta,ordem) VALUES (?,?,?,?,?)',
                            (new_id, alt['letra'], alt['texto'], alt['correta'], alt['ordem']))
            existing.add(key)
            inserted += 1
        con.commit()

        # Verificações pós-merge
        integrity = cur.execute('PRAGMA integrity_check').fetchone()[0]
        fk = cur.execute('PRAGMA foreign_key_check').fetchall()
        present = 0
        db_keys = {norm(r[0]) for r in cur.execute('SELECT enunciado FROM questoes')}
        for rec in recs:
            if norm(rec['questao']['enunciado']) in db_keys:
                present += 1
        active = cur.execute('SELECT COUNT(*) FROM questoes WHERE ativa=1 AND COALESCE(excluida,0)=0').fetchone()[0]
        dignity = cur.execute("""
            SELECT COUNT(*) FROM questoes q JOIN topicos t ON t.id=q.topico_id
            WHERE q.ativa=1 AND COALESCE(q.excluida,0)=0
              AND t.nome LIKE '%DIGNIDADE SEXUAL%'
        """).fetchone()[0]
        print('')
        print('=== RESULTADO ===')
        print(f'Questões inseridas agora: {inserted}')
        print(f'Questões já presentes/ignoradas: {skipped}')
        print(f'Conjunto de recuperação presente: {present}/{len(recs)}')
        print(f'Questões ativas no banco: {active}')
        print(f'Dignidade Sexual: {dignity}')
        print(f'integrity_check: {integrity}')
        print(f'foreign_key_check: {len(fk)} problema(s)')
        if present != len(recs) or integrity != 'ok' or fk:
            raise RuntimeError('Validação final falhou. O backup original foi preservado.')
    except Exception:
        try: con.rollback()
        except Exception: pass
        raise
    finally:
        con.close()

if __name__ == '__main__':
    main()
