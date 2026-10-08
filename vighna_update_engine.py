"""Atualizador local do VighnaStudy: contratos, validação e instalação segura.

Formato fechado de pacote: manifest.json + arquivos Python explicitamente enumerados.
Nenhum arquivo de dados é aceito como atualização. Não faz migrações de banco.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import uuid
import zipfile
from datetime import datetime
from contextlib import closing
from pathlib import Path, PurePosixPath

FORMAT = 'vighna-source-update-v1'
MAX_UNCOMPRESSED = 100 * 1024 * 1024
MAX_FILE = 15 * 1024 * 1024
MAX_MEMBERS = 80
EXCLUDED_NAMES = {'estudos.db', 'VighnaStudy.exe', 'VighnaUpdater.exe'}
ROOT_MODULES = {"main.py", "versao.py", "tema.py", "foco.py", "icones.py", "caminhos.py",
                "backup.py", "checkpoint.py", "startup_splash.py", "navegacao.py",
                "banco.py", "importador_pdf.py", "importador_txt.py", "relatorios_lazy.py",
                "estatisticas_lazy.py", "inteligencia.py", "fila_candidata.py",
                "ciclo_estudo.py", "microtemas.py", "mapa_dominio.py", "progresso_edital.py",
                "vighna_update_engine.py", "vighna_updater.py", "gerar_pacote_atualizacao.py", "vighna_update_ui.py", "vighna_recuperar_atualizacao.py"}
SOURCE_DIRS = {'ui', 'statistics_core'}


class UpdateError(RuntimeError):
    pass


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def hash_file(file):
    digest = hashlib.sha256()
    with open(file, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def valid_source_path(path):
    if not isinstance(path, str) or not path or '\\' in path or ':' in path:
        return False
    pure = PurePosixPath(path)
    if (pure.is_absolute() or path != pure.as_posix()
            or any(p in ('', '.', '..') or p.startswith('.') for p in pure.parts)):
        return False
    if len(pure.parts) == 1:
        return pure.name in ROOT_MODULES
    directories = pure.parts[1:-1]
    return (
        pure.parts[0] in SOURCE_DIRS
        and pure.suffix == '.py'
        and pure.stem.isidentifier()
        and len(pure.parts) <= 8
        and all(part.isidentifier() for part in directories)
    )


def _metadata(package):
    try:
        with zipfile.ZipFile(package) as archive:
            infos = archive.infolist()
            if len(infos) > MAX_MEMBERS + 1:
                raise UpdateError('Pacote contém arquivos demais.')
            if any(x.is_dir() for x in infos):
                raise UpdateError('O pacote deve conter somente arquivos, sem diretórios explícitos.')
            paths = [info.filename for info in infos]
            if len({p.casefold() for p in paths}) != len(paths):
                raise UpdateError('Nomes duplicados ou conflitantes no ZIP.')
            if 'manifest.json' not in paths:
                raise UpdateError('Manifesto do pacote ausente.')
            total = sum(x.file_size for x in infos)
            if total > MAX_UNCOMPRESSED or any(x.file_size > MAX_FILE for x in infos):
                raise UpdateError('Limites de tamanho do pacote excedidos.')
            for info in infos:
                if info.flag_bits & 0x1:
                    raise UpdateError('ZIP criptografado não é aceito.')
                if ((info.external_attr >> 16) & 0o170000) == 0o120000:
                    raise UpdateError('Links simbólicos não são aceitos.')
                if info.filename != 'manifest.json' and not valid_source_path(info.filename):
                    raise UpdateError(f'Arquivo não autorizado no pacote: {info.filename}')
            try:
                manifest = json.loads(archive.read('manifest.json'))
            except (ValueError, UnicodeDecodeError, KeyError) as err:
                raise UpdateError('Manifesto inválido.') from err
            if not isinstance(manifest, dict) or manifest.get('format') != FORMAT:
                raise UpdateError('Formato de atualização não reconhecido.')
            files = manifest.get('files')
            if not isinstance(files, dict) or not files or len(files) > MAX_MEMBERS:
                raise UpdateError('Relação de arquivos inválida.')
            if set(files) != set(paths) - {'manifest.json'}:
                raise UpdateError('O conteúdo do ZIP diverge do manifesto.')
            for path, expected in files.items():
                if not valid_source_path(path) or not isinstance(expected, str) or len(expected) != 64:
                    raise UpdateError(f'Entrada inválida no manifesto: {path}')
                if sha256_bytes(archive.read(path)) != expected.lower():
                    raise UpdateError(f'Hash incorreto: {path}')
            required = ('base_version', 'base_build', 'target_version', 'target_build', 'schema')
            if any(not isinstance(manifest.get(k), str) or not manifest[k].strip() for k in required[:4]):
                raise UpdateError('Versões/base/build não informados corretamente.')
            if not isinstance(manifest.get('schema'), int):
                raise UpdateError('Schema não informado corretamente.')
            if not isinstance(manifest.get('description', ''), str):
                raise UpdateError('Descrição da atualização inválida.')
            if 'versao.py' not in files:
                raise UpdateError('O pacote deve declarar sua versão em versao.py.')
            version_tree = ast.parse(archive.read('versao.py'), filename='versao.py')
            declarations = {}
            for statement in version_tree.body:
                if isinstance(statement, ast.Assign):
                    for target in statement.targets:
                        if isinstance(target, ast.Name) and target.id in ('VIGHNA_VERSION','VIGHNA_BUILD','VIGHNA_SCHEMA'):
                            declarations[target.id] = ast.literal_eval(statement.value)
            if (declarations.get('VIGHNA_VERSION') != manifest['target_version'] or
                    declarations.get('VIGHNA_BUILD') != manifest['target_build'] or
                    declarations.get('VIGHNA_SCHEMA') != manifest['schema']):
                raise UpdateError('versao.py não corresponde ao manifesto.')
            return manifest
    except (OSError, zipfile.BadZipFile, SyntaxError, ValueError) as err:
        raise UpdateError(f'Falha ao examinar o ZIP: {err}') from err


def inspect_package(package, root, *, base=None):
    root = Path(root).resolve()
    manifest = _metadata(package)
    if base is None:
        base = version_from_file(root / 'versao.py')
    if manifest['base_version'] != base[0] or manifest['base_build'] != base[1]:
        raise UpdateError('O pacote não corresponde à versão/build instalada.')
    if manifest['schema'] != base[2]:
        raise UpdateError('Atualizações com mudança de schema exigem uma migração própria, não são aceitas aqui.')
    if (manifest['target_version'], manifest['target_build']) == (base[0], base[1]):
        raise UpdateError('O pacote não declara uma versão/build nova.')
    if not (root / 'estudos.db').is_file():
        raise UpdateError('Banco principal ausente; atualização bloqueada.')
    if not (root / 'VighnaStudy.spec').is_file():
        raise UpdateError('Arquivo de compilação ausente.')
    return manifest


def version_from_file(file):
    vals = {}
    node = ast.parse(Path(file).read_text(encoding='utf-8'), filename=str(file))
    for statement in node.body:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name) and target.id in ('VIGHNA_VERSION','VIGHNA_BUILD','VIGHNA_SCHEMA'):
                    vals[target.id] = ast.literal_eval(statement.value)
    return vals['VIGHNA_VERSION'], vals['VIGHNA_BUILD'], vals['VIGHNA_SCHEMA']


def check_database(path):
    if not Path(path).is_file():
        raise UpdateError('Banco de estudos não encontrado.')
    con = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True, timeout=12)
    try:
        value = con.execute('PRAGMA integrity_check').fetchone()
        fk = con.execute('PRAGMA foreign_key_check').fetchone()
        if value != ('ok',) or fk is not None:
            raise UpdateError('Banco de estudos não passou nas verificações de integridade.')
    finally:
        con.close()


def backup_database(source, destination):
    source, destination = Path(source), Path(destination)
    if destination.exists():
        raise UpdateError('Cópia de segurança já existe; operação interrompida.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(source.resolve().as_uri() + '?mode=ro', uri=True, timeout=15)) as src:
        with closing(sqlite3.connect(destination)) as dst:
            src.backup(dst, pages=1024, sleep=0.01)
            dst.commit()
    check_database(destination)
    return destination


def _source_files(root):
    for entry in root.iterdir():
        if entry.is_file() and entry.suffix == '.py' and not entry.name.startswith(('test_', 'benchmark_', 'main_backup', 'banco_backup', '_')):
            yield entry, Path(entry.name)
    for folder in SOURCE_DIRS:
        if (root / folder).is_dir():
            for entry in (root / folder).rglob('*.py'):
                if '__pycache__' not in entry.parts and not entry.name.startswith('test_'):
                    yield entry, entry.relative_to(root)


def _log(history, entry):
    history.parent.mkdir(parents=True, exist_ok=True)
    with history.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(entry, ensure_ascii=False) + '\n')




def _write_atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(temporary, path)


def _restore_from_saved(root, saved, state):
    """Recuperação conservadora após falha ou interrupção na troca de arquivos."""
    root = Path(root)
    saved = Path(saved)
    active = root / 'dist' / 'SistemaEstudos'
    previous = saved / 'anterior_executavel'
    if previous.is_dir():
        if active.exists():
            shutil.rmtree(active)
        previous.rename(active)
    elif not (active / 'VighnaStudy.exe').is_file():
        raise UpdateError('Nem a versão anterior nem um executável ativo foram encontrados.')
    for relative, existed in state['sources'].items():
        if not valid_source_path(relative) or not isinstance(existed, bool):
            raise UpdateError('Registro de recuperação contém caminho inválido.')
        target = root / relative
        original = saved / 'sources' / relative
        if existed:
            if not original.is_file():
                raise UpdateError(f'Fonte anterior ausente do backup: {relative}')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original, target)
        elif target.is_file():
            target.unlink()
    state['phase'] = 'recovered'
    _write_atomic_json(saved / 'state.json', state)


def recover_incomplete_updates(root):
    """Reverte instalações abandonadas ao iniciar um novo processo atualizador.

    Requer que todas as instâncias do aplicativo estejam fechadas.
    """
    root = Path(root).resolve()
    history_root = root / 'backups' / 'atualizacoes'
    recovered = []
    if not history_root.is_dir():
        return recovered
    for file in sorted(history_root.glob('*/state.json')):
        try:
            state = json.loads(file.read_text(encoding='utf-8'))
        except (ValueError, OSError) as error:
            raise UpdateError(f'Estado de recuperação ilegível: {file}') from error
        if state.get('phase') != 'committing':
            continue
        if not isinstance(state.get('sources'), dict):
            raise UpdateError('Registro de recuperação incompleto.')
        _restore_from_saved(root, file.parent, state)
        recovered.append(file.parent.name)
    return recovered

def install_package(package, root, *, python_exe, report=lambda progress, status: None,
                    runner=None, keep_work=False):
    """Realiza build em staging e troca com rollback. Deve executar após fechar o app.

    runner: injeção para testes; recebe comando, cwd, report e deve lançar exceção
    em caso de falha. A versão de produção usa subprocess sem shell.
    """
    root = Path(root).resolve()
    package = Path(package).resolve()
    manifest = inspect_package(package, root)
    source_db = root / 'estudos.db'
    backup_root = root / 'backups' / 'atualizacoes'
    run_id = datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:8]
    saved = backup_root / run_id
    history = backup_root / 'historico.jsonl'
    staging = root / '_vighna_update_staging' / run_id
    work = staging / 'source'
    build_output = staging / 'dist' / 'VighnaStudy'
    active_exe_dir = root / 'dist' / 'SistemaEstudos'
    original_dist = saved / 'anterior_executavel'
    state = None
    dist_moved = False
    deployed_dist = False
    try:
        report(5, 'Validando pacote e banco atual...')
        check_database(source_db)
        if not active_exe_dir.is_dir() or not (active_exe_dir / 'VighnaStudy.exe').is_file():
            raise UpdateError('Instalação anterior não encontrada em dist/SistemaEstudos.')
        report(14, 'Criando backup permanente e verificando integridade...')
        saved.mkdir(parents=True, exist_ok=False)
        backup_database(source_db, saved / 'estudos.db')
        _log(history, {'date': datetime.now().isoformat(), 'id':run_id, 'status':'started',
                       'package':package.name,'from':manifest['base_build'],'to':manifest['target_build']})
        work.mkdir(parents=True)
        report(25, 'Preparando os arquivos de código, sem copiar dados de estudo...')
        for src, rel in _source_files(root):
            dest = work / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        shutil.copy2(root / 'VighnaStudy.spec', work / 'VighnaStudy.spec')
        icon = root / 'vighnastudy.ico'
        if icon.is_file():
            shutil.copy2(icon, work / 'vighnastudy.ico')
        with zipfile.ZipFile(package) as archive:
            for filename in manifest['files']:
                target = work / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(filename))
        if version_from_file(work / 'versao.py') != (manifest['target_version'], manifest['target_build'], manifest['schema']):
            raise UpdateError('Versão divergente na área de compilação.')
        for file in work.rglob('*.py'):
            compile(file.read_bytes(), str(file), 'exec')
        report(38, 'Compilando a nova versão em pasta isolada...')
        if runner is None:
            cmd = [str(python_exe), '-m', 'PyInstaller', '--noconfirm', '--clean',
                   '--distpath', str(staging / 'dist'), '--workpath', str(staging / 'build'),
                   str(work / 'VighnaStudy.spec')]
            creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            proc = subprocess.Popen(cmd, cwd=work, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, errors='replace', creationflags=creationflags)
            tail = []
            with (saved / 'build.log').open('w', encoding='utf-8') as log:
                for line in proc.stdout:
                    log.write(line)
                    tail.append(line.strip())
                    tail = tail[-18:]
                if proc.wait() != 0:
                    raise UpdateError('Compilação falhou: ' + ' | '.join(tail[-3:]))
        else:
            runner(work, build_output, report)
        if not (build_output / 'VighnaStudy.exe').is_file():
            raise UpdateError('Compilação não produziu VighnaStudy.exe.')
        report(73, 'Validando saída e preservando executável anterior...')
        check_database(source_db)
        # Snapshot integral ANTES do primeiro arquivo de produção ser alterado.
        previous_files = {}
        for filename in manifest['files']:
            target = root / filename
            previous_files[filename] = target.is_file()
            if target.is_file():
                original = saved / 'sources' / filename
                original.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, original)
        state = {'phase':'committing', 'sources':previous_files,
                 'created_at':datetime.now().isoformat(), 'target_build':manifest['target_build']}
        _write_atomic_json(saved / 'state.json', state)
        for filename in manifest['files']:
            source_target = root / filename
            new_source = work / filename
            source_target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(new_source, source_target)
        report(82, 'Instalando novo executável com possibilidade de retorno...')
        # Mantém a versão anterior no diretório de recuperação. Rollback em erro.
        original_dist.parent.mkdir(parents=True, exist_ok=True)
        active_exe_dir.rename(original_dist)
        dist_moved = True
        build_output.rename(active_exe_dir)
        deployed_dist = True
        report(93, 'Conferindo banco e arquivos instalados...')
        check_database(source_db)
        if not (active_exe_dir / 'VighnaStudy.exe').is_file():
            raise UpdateError('Executável atualizado não encontrado.')
        if version_from_file(root / 'versao.py') != (manifest['target_version'], manifest['target_build'], manifest['schema']):
            raise UpdateError('Versão instalada divergente.')
        state['phase'] = 'installed'
        _write_atomic_json(saved / 'state.json', state)
        _log(history, {'date':datetime.now().isoformat(),'id':run_id,'status':'installed',
                       'to':manifest['target_build'],'backup':str(saved)})
        report(100, 'Atualização concluída. Seu histórico de estudos foi preservado.')
        return {'backup':str(saved), 'executable':str(active_exe_dir / 'VighnaStudy.exe'), 'manifest':manifest}
    except Exception as err:
        report(95, 'Falha detectada; restaurando arquivos anteriores...')
        rollback_errors = []
        if state is not None:
            try:
                # Se a falha foi depois do commit do executável, reverte também.
                _restore_from_saved(root, saved, state)
            except Exception as rollback_error:
                rollback_errors.append(str(rollback_error))
        try:
            _log(history, {'date':datetime.now().isoformat(), 'id':run_id, 'status':'failed',
                           'error':str(err), 'rollback_errors':rollback_errors})
        except OSError:
            pass
        suffix = (' Reversão incompleta: ' + '; '.join(rollback_errors)) if rollback_errors else ''
        raise UpdateError(str(err) + suffix) from err
    finally:
        if not keep_work and staging.exists():
            try:
                shutil.rmtree(staging)
            except OSError:
                pass
