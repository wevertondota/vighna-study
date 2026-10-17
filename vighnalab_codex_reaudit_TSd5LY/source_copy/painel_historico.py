# -*- coding: utf-8 -*-
"""Histórico V2-B — isolado da instalação principal do VighnaStudy.

SQLite próprio: índice de evidências importadas pelo usuário; ZIPs preservados
em cofre próprio sob LOCALAPPDATA. Nunca executa/extrai conteúdo dos ZIPs.
"""
from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import tempfile
import zipfile

APPDIR_NAME = 'VighnaStudy_Homologador_V2B'
SCHEMA = 1
MAX_ARCHIVE_BYTES = 250 * 1024 * 1024
MAX_SUMMARY_BYTES = 1024 * 1024
MAX_MANIFEST_BYTES = 2 * 1024 * 1024
MAX_MEMBERS = 1200


class HistoryError(ValueError):
    pass


def storage_root() -> Path:
    """Pasta EXCLUSIVA do painel, jamais a do VighnaStudy principal."""
    local = os.environ.get('LOCALAPPDATA')
    if local:
        return Path(local) / APPDIR_NAME
    return Path.home() / '.local' / 'share' / APPDIR_NAME


def sha_file(file: Path) -> str:
    h = hashlib.sha256()
    with file.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def category_for(key: str) -> str:
    if key.startswith('qt_windows_') or key.startswith('qt_'):
        return 'Qt'
    if key == 'pyinstaller' or 'build' in key:
        return 'PyInstaller'
    if 'atualizacao' in key or 'sqlite' in key or 'rollback' in key:
        return 'SQLite / Atualização'
    if 'seguranca' in key or 'guardas' in key:
        return 'Segurança'
    if 'preflight' in key:
        return 'Integridade'
    return 'Outros'


def _safe_json(z: zipfile.ZipFile, path: str, limit: int):
    info = z.getinfo(path)
    if info.file_size > limit:
        raise HistoryError('Metadados grandes demais: ' + path)
    try:
        return json.loads(z.read(info).decode('utf-8-sig'))
    except (ValueError, UnicodeError) as exc:
        raise HistoryError('Metadados JSON inválidos: ' + path) from exc


def _parse_log_count(z: zipfile.ZipFile, name: str) -> tuple[int | None, int | None]:
    if name not in z.namelist() or z.getinfo(name).file_size > 1_500_000:
        return None, None
    text = z.read(name).decode('utf-8', 'replace')
    matches = re.findall(r'Ran\s+(\d+)\s+tests?\s+in\s+', text)
    count = int(matches[-1]) if matches else None
    failures = 0
    m = re.search(r'FAILED\s*\(([^)]*)\)', text)
    if m:
        failures = sum(int(x) for x in re.findall(r'(?:failures|errors)=(\d+)', m.group(1)))
    elif count is None:
        failures = None
    return count, failures


def inspect_evidence(path: Path) -> dict:
    """Valida hashes completos antes de extrair metadados; não extrai arquivos."""
    path = Path(path)
    if not path.is_file() or path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise HistoryError('Arquivo ausente ou maior que o limite de 250 MB')
    try:
        with zipfile.ZipFile(path) as z:
            infos = z.infolist()
            if len(infos) > MAX_MEMBERS or sum(x.file_size for x in infos) > 350 * 1024 * 1024:
                raise HistoryError('ZIP excede limites seguros de arquivos ou tamanho descompactado')
            names = [x.filename for x in infos if not x.is_dir()]
            if len(names) != len(set(names)):
                raise HistoryError('ZIP contém entradas duplicadas')
            if z.testzip() is not None:
                raise HistoryError('CRC de ZIP inválido')
            if 'RESUMO_HOMOLOGACAO.json' not in names:
                raise HistoryError('ZIP não é resultado do homologador (resumo ausente)')
            summary = _safe_json(z, 'RESUMO_HOMOLOGACAO.json', MAX_SUMMARY_BYTES)
            if not isinstance(summary, dict) or not isinstance(summary.get('testes'), dict):
                raise HistoryError('Resumo sem estrutura reconhecida')
            if 'MANIFESTO_SHA256.json' not in names:
                raise HistoryError('Manifesto SHA-256 interno ausente')
            hashes = _safe_json(z, 'MANIFESTO_SHA256.json', MAX_MANIFEST_BYTES)
            if not isinstance(hashes, dict) or set(hashes) != set(names) - {'MANIFESTO_SHA256.json'}:
                raise HistoryError('Manifesto não cobre todos os arquivos do ZIP')
            for member, digest in hashes.items():
                if not isinstance(digest, str) or len(digest) != 64:
                    raise HistoryError('SHA-256 malformado')
                if hashlib.sha256(z.read(member)).hexdigest() != digest.lower():
                    raise HistoryError('SHA-256 divergente: ' + member)
            steps = []
            for key, state in sorted(summary['testes'].items()):
                if not isinstance(key, str) or not isinstance(state, dict):
                    continue
                status = str(state.get('status', 'INDEFINIDO'))
                if status not in {'PASSOU', 'FALHOU', 'BLOQUEADO', 'INDEFINIDO'}:
                    status = 'INDEFINIDO'
                count = None
                errors = None
                if key.startswith('qt_windows_'):
                    label = key.removeprefix('qt_windows_')
                    filename = f'qt_windows_{label}/qt_gate_resultados.json'
                    if filename in names:
                        obj = _safe_json(z, filename, MAX_SUMMARY_BYTES)
                        if isinstance(obj, dict):
                            count = obj.get('testes') if isinstance(obj.get('testes'), int) else None
                            passed = obj.get('aprovados')
                            if isinstance(passed, int) and count is not None:
                                errors = max(count - passed, 0)
                elif 'log' in state and isinstance(state['log'], str):
                    logname = state['log']
                    if key.startswith('qt_windows_'):
                        logname = f'{key}/{logname}'
                    count, errors = _parse_log_count(z, logname)
                steps.append({'key': key, 'category': category_for(key), 'status': status,
                              'checks': count, 'errors': errors})
            result = summary.get('resultados', {})
            if not isinstance(result, dict):
                result = {}
            return {
                'filename': path.name,
                'sha256': sha_file(path),
                'bytes': path.stat().st_size,
                'modo': str(summary.get('modo', 'desconhecido'))[:30],
                'ambiente': str(summary.get('ambiente', 'desconhecido'))[:30],
                'python': str(summary.get('python', ''))[:40],
                'homologador': str(summary.get('homologador', ''))[:40],
                'base_build': 'structural-m1c-readpilot-restore-offline-r1d-v1',
                'target_build': 'structural-m2-int1-settings-r1d-rc2',
                'falhas': sum(s['status'] == 'FALHOU' for s in steps),
                'bloqueados': sum(s['status'] == 'BLOQUEADO' for s in steps),
                'aprovados': sum(s['status'] == 'PASSOU' for s in steps),
                'steps': steps,
                'nota': 'Sem autorização de instalação; contagens por etapa, não por teste individual.',
            }
    except (zipfile.BadZipFile, RuntimeError, KeyError, OSError) as exc:
        raise HistoryError('Não foi possível validar ZIP: ' + str(exc)) from exc


class HistoryStore:
    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root is not None else storage_root()
        self.evidence = self.root / 'evidencias'
        self.root.mkdir(parents=True, exist_ok=True)
        self.evidence.mkdir(parents=True, exist_ok=True)
        self.db_path = self.root / 'historico_v2b.sqlite3'
        with closing(sqlite3.connect(self.db_path, timeout=15)) as con:
            con.executescript('''
              CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS runs(
                id INTEGER PRIMARY KEY,
                hash TEXT NOT NULL UNIQUE,
                filename TEXT NOT NULL,
                imported_at TEXT NOT NULL,
                modo TEXT NOT NULL,
                ambiente TEXT NOT NULL,
                python TEXT NOT NULL,
                homologador TEXT NOT NULL,
                base_build TEXT NOT NULL,
                target_build TEXT NOT NULL,
                aprovados INTEGER NOT NULL,
                falhas INTEGER NOT NULL,
                bloqueados INTEGER NOT NULL,
                bytes INTEGER NOT NULL
              );
              CREATE TABLE IF NOT EXISTS steps(
                run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
                step_key TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL,
                checks INTEGER,
                errors INTEGER,
                PRIMARY KEY(run_id, step_key)
              );
              INSERT OR IGNORE INTO meta(k,v) VALUES('schema','1');
            ''')
            con.commit()

    def connect(self):
        con = sqlite3.connect(self.db_path, timeout=15)
        con.row_factory = sqlite3.Row
        con.execute('PRAGMA foreign_keys=ON')
        return con

    def import_zip(self, path: Path) -> tuple[int, bool]:
        parsed = inspect_evidence(Path(path))
        digest = parsed['sha256']
        with closing(self.connect()) as con:
            prev = con.execute('SELECT id FROM runs WHERE hash=?', (digest,)).fetchone()
            if prev:
                return int(prev['id']), False
            dest = self.evidence / (digest + '.zip')
            temporary = self.evidence / (digest + '.importando')
            try:
                with Path(path).open('rb') as origin, temporary.open('xb') as target:
                    shutil.copyfileobj(origin, target, length=1024*1024)
                if sha_file(temporary) != digest:
                    raise HistoryError('Arquivo mudou durante a importação')
                os.replace(temporary, dest)
                now = datetime.now(timezone.utc).isoformat(timespec='seconds')
                with con:
                    cursor = con.execute('''INSERT INTO runs
                      (hash,filename,imported_at,modo,ambiente,python,homologador,
                       base_build,target_build,aprovados,falhas,bloqueados,bytes)
                      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                      (digest,parsed['filename'],now,parsed['modo'],parsed['ambiente'],
                       parsed['python'],parsed['homologador'],parsed['base_build'],
                       parsed['target_build'],parsed['aprovados'],parsed['falhas'],
                       parsed['bloqueados'],parsed['bytes']))
                    run_id = int(cursor.lastrowid)
                    con.executemany('''INSERT INTO steps
                      (run_id,step_key,category,status,checks,errors)
                      VALUES(?,?,?,?,?,?)''',
                      [(run_id,s['key'],s['category'],s['status'],s['checks'],s['errors'])
                       for s in parsed['steps']])
                return run_id, True
            finally:
                temporary.unlink(missing_ok=True)

    def list_runs(self, *, category: str = 'Todas', status: str = 'Todos', query: str = '') -> list[dict]:
        with closing(self.connect()) as con:
            rows = con.execute('SELECT * FROM runs ORDER BY imported_at DESC,id DESC').fetchall()
            result = []
            for row in rows:
                r = dict(row)
                if query and query.casefold() not in (r['filename']+' '+r['homologador']+' '+r['modo']).casefold():
                    continue
                if status != 'Todos' and (
                    status == 'Aprovados' and (r['falhas'] or r['bloqueados']) or
                    status == 'Com falhas' and not r['falhas'] or
                    status == 'Bloqueados' and not r['bloqueados']):
                    continue
                if category != 'Todas':
                    exists = con.execute('SELECT 1 FROM steps WHERE run_id=? AND category=? LIMIT 1',
                                         (r['id'],category)).fetchone()
                    if not exists:
                        continue
                result.append(r)
            return result

    def steps_for(self, run_id: int, category: str = 'Todas') -> list[dict]:
        with closing(self.connect()) as con:
            sql = 'SELECT * FROM steps WHERE run_id=?'
            args: tuple = (run_id,)
            if category != 'Todas':
                sql += ' AND category=?'
                args += (category,)
            sql += ' ORDER BY category,step_key'
            return [dict(s) for s in con.execute(sql, args).fetchall()]

    def compare(self, old_id: int, new_id: int) -> dict:
        if int(old_id) == int(new_id):
            raise HistoryError('Selecione duas execuções diferentes')
        with closing(self.connect()) as con:
            runs = [con.execute('SELECT * FROM runs WHERE id=?', (int(n),)).fetchone()
                    for n in (old_id,new_id)]
            if not all(runs):
                raise HistoryError('Execução não encontrada')
        old = {s['step_key']: s for s in self.steps_for(old_id)}
        new = {s['step_key']: s for s in self.steps_for(new_id)}
        changed = []
        regressions = []
        improvements = []
        for key in sorted(old.keys() | new.keys()):
            a = old.get(key)
            b = new.get(key)
            previous = a['status'] if a else 'AUSENTE'
            current = b['status'] if b else 'AUSENTE'
            count_changed = bool(a and b and
                (a['checks'] != b['checks'] or a['errors'] != b['errors']))
            if previous != current or count_changed:
                before_detail = previous + (f" ({a['checks']} testes)" if a and a['checks'] is not None else '')
                after_detail = current + (f" ({b['checks']} testes)" if b and b['checks'] is not None else '')
                changed.append({'etapa': key, 'categoria': (b or a)['category'],
                                'antes': before_detail, 'depois': after_detail})
                if previous == 'PASSOU' and (current != 'PASSOU' or (a and b and
                    a['errors'] is not None and b['errors'] is not None and b['errors'] > a['errors'])):
                    regressions.append(key)
                if previous != 'PASSOU' and current == 'PASSOU':
                    improvements.append(key)
        return {'antes':dict(runs[0]), 'depois':dict(runs[1]), 'mudancas':changed,
                'regressoes':regressions,'melhorias':improvements,
                'observacao':'Comparação de etapas; não prova ausência de regressão interna.'}

    def evidence_path(self, run_id: int) -> Path:
        with closing(self.connect()) as con:
            item = con.execute('SELECT hash FROM runs WHERE id=?',(run_id,)).fetchone()
            if not item:
                raise HistoryError('Execução não encontrada')
            path = self.evidence / (item['hash']+'.zip')
            if not path.is_file() or sha_file(path) != item['hash']:
                raise HistoryError('Evidência arquivada ausente ou adulterada')
            return path

    def export_backup(self, output: Path) -> Path:
        output = Path(output)
        if output.resolve().is_relative_to(self.root.resolve()):
            raise HistoryError('Escolha uma pasta de exportação fora do cofre de histórico')
        if output.exists():
            raise HistoryError('Arquivo de exportação já existe; não será sobrescrito')
        with closing(self.connect()) as con:
            hashes = [r['hash'] for r in con.execute('SELECT hash FROM runs ORDER BY id')]
        for digest in hashes:
            path = self.evidence / (digest + '.zip')
            if not path.is_file() or sha_file(path) != digest:
                raise HistoryError('Evidência do histórico ausente/corrompida: ' + digest)
        try:
            with tempfile.TemporaryDirectory(prefix='vighna_exportar_historico_') as tmp:
                copy_db = Path(tmp) / 'historico_v2b.sqlite3'
                with closing(sqlite3.connect(copy_db)) as dst, closing(self.connect()) as src:
                    src.backup(dst)
                note = (
                    'Backup do histórico V2-B (não é instalador, não inclui banco pessoal).\n'
                    'Contém evidências importadas e índice SQLite exclusivo do painel.\n'
                    'Não extrair sobre o VighnaStudy. Envio ao ChatGPT é manual.\n'
                ).encode('utf-8')
                manifesto = {}
                with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=5) as z:
                    z.write(copy_db, arcname='historico_v2b.sqlite3')
                    manifesto['historico_v2b.sqlite3'] = sha_file(copy_db)
                    for digest in hashes:
                        path = self.evidence / (digest + '.zip')
                        name = 'evidencias/' + digest + '.zip'
                        z.write(path, arcname=name, compress_type=zipfile.ZIP_STORED)
                        manifesto[name] = digest
                    z.writestr('LEIA_PRIMEIRO.txt', note)
                    manifesto['LEIA_PRIMEIRO.txt'] = hashlib.sha256(note).hexdigest()
                    z.writestr('MANIFESTO_SHA256.json',json.dumps(manifesto,indent=2).encode('utf-8'))
            with zipfile.ZipFile(output) as z:
                if z.testzip() is not None:
                    raise HistoryError('ZIP exportado com CRC inválido')
                for key,digest in manifesto.items():
                    with z.open(key) as f:
                        h = hashlib.sha256()
                        for block in iter(lambda: f.read(1024*1024), b''):
                            h.update(block)
                        if h.hexdigest() != digest:
                            raise HistoryError('Falha no manifesto da exportação: ' + key)
            return output
        except Exception:
            output.unlink(missing_ok=True)
            raise
