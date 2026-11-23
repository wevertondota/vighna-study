"""Atualizador local do VighnaStudy: contratos, validação e instalação segura.

Formato fechado de pacote: manifest.json + arquivos Python explicitamente enumerados.
Nenhum arquivo de dados é aceito como atualização. Não faz migrações de banco.
"""
from __future__ import annotations

import ast
import errno
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
# Tamanhos máximos de SEGURANÇA (não remover). 500 MiB compactados, 2 GiB
# descompactados e 1 GiB por fonte, com limite de 512 membros e razão 200:1.
MiB = 1024 * 1024
MAX_ZIP_SIZE = 500 * MiB
MAX_UNCOMPRESSED = 2 * 1024 * MiB
MAX_FILE = 1024 * MiB
MAX_MEMBERS = 512
MAX_COMPRESSION_RATIO = 200
MAX_MANIFEST_SIZE = 2 * MiB
MAX_VERSION_SIZE = 1 * MiB
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


def _hash_zip_member(archive, filename):
    """Confere o membro por blocos; evita manter fontes grandes em memória."""
    digest = hashlib.sha256()
    with archive.open(filename, 'r') as stream:
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
        # Verificação antes de descompactar e calcular hashes; ZIPs gigantes
        # são recusados mesmo que declarem conteúdo descompactado pequeno.
        if Path(package).stat().st_size > MAX_ZIP_SIZE:
            raise UpdateError('ZIP excede o limite de 500 MiB compactados.')
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
            if total > MAX_UNCOMPRESSED:
                raise UpdateError('Pacote excede 2 GiB descompactados.')
            if any(x.file_size > MAX_FILE for x in infos):
                raise UpdateError('Arquivo individual excede 1 GiB descompactado.')
            if any(x.file_size > MAX_COMPRESSION_RATIO * max(x.compress_size, 1)
                   for x in infos):
                raise UpdateError('ZIP com razão de compressão perigosa (possível ZIP bomb).')
            manifest_info = archive.getinfo('manifest.json')
            if manifest_info.file_size > MAX_MANIFEST_SIZE:
                raise UpdateError('Manifesto excede o tamanho máximo.')
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
                if _hash_zip_member(archive, path) != expected.lower():
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
            if archive.getinfo('versao.py').file_size > MAX_VERSION_SIZE:
                raise UpdateError('Arquivo de versão excede o tamanho máximo.')
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




def package_usage(package, root):
    """Identifica um ZIP pelo SHA-256, com compatibilidade com histórico legado.

    Não registra seleção nem modifica o banco. `installed_build` indica que um
    build foi instalado antes, não necessariamente que os bytes são iguais.
    """
    package = Path(package).resolve()
    root = Path(root).resolve()
    manifest = _metadata(package)
    digest = hash_file(package)
    current_version, current_build, _ = version_from_file(root / 'versao.py')
    target = manifest['target_build']
    history = root / 'backups' / 'atualizacoes' / 'historico.jsonl'
    entries = []
    if history.is_file():
        try:
            with history.open('r', encoding='utf-8') as stream:
                for line in stream:
                    try:
                        entry = json.loads(line)
                    except (ValueError, UnicodeDecodeError):
                        continue  # linha histórica incompleta não invalida o restante
                    if isinstance(entry, dict):
                        entries.append(entry)
        except OSError as exc:
            raise UpdateError('Não foi possível consultar o histórico de atualizações.') from exc

    # Agrupa eventos por execução. `started` sem finalização NÃO é sucesso.
    runs = {}
    for entry in entries:
        run_id = entry.get('id')
        if not isinstance(run_id, str) or not run_id:
            continue
        previous = runs.setdefault(run_id, {})
        previous.update({k: v for k, v in entry.items() if v is not None})
        if entry.get('status') in ('started', 'installed', 'failed'):
            previous['status'] = entry['status']
            previous['date'] = entry.get('date', previous.get('date', ''))

    installed = [run for run in runs.values() if run.get('status') == 'installed'
                 and run.get('sha256') == digest]
    same_build = [run for run in runs.values() if run.get('status') == 'installed'
                  and run.get('to') == target]
    failed = [run for run in runs.values() if run.get('status') == 'failed'
              and run.get('sha256') == digest]
    incomplete = [run for run in runs.values() if run.get('status') == 'started'
                  and run.get('sha256') == digest]
    # Registros antigos não armazenavam SHA. Compara nome E build apenas como
    # pista de uma tentativa; nunca afirma igualdade de conteúdo do ZIP.
    legacy_attempts = [run for run in runs.values() if not run.get('sha256')
                       and run.get('to') == target and run.get('package') == package.name]

    if installed:
        state, record = 'installed_exact', installed[-1]
    elif (current_version, current_build) == (manifest['target_version'], target):
        state, record = 'installed_current', None
    elif same_build:
        state, record = 'installed_build', same_build[-1]
    elif failed:
        state, record = 'failed', failed[-1]
    elif incomplete:
        state, record = 'incomplete', incomplete[-1]
    elif legacy_attempts:
        state, record = 'legacy_attempt', legacy_attempts[-1]
    else:
        state, record = 'new', None
    return {'state': state, 'sha256': digest, 'manifest': manifest,
            'record': record, 'filename': package.name}



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



# Bloqueios temporarios de arquivo/diretorio no Windows (acesso negado ou
# arquivo em uso). Nenhum processo e encerrado automaticamente.
_RENAME_ATTEMPTS = 9
_RENAME_INITIAL_DELAY = 0.35


def _retryable_rename_error(error):
    windows_code = getattr(error, 'winerror', None)
    return windows_code in (5, 32) or (
        windows_code is None
        and getattr(error, 'errno', None) in (errno.EACCES, errno.EBUSY, errno.EPERM)
    )


def _rename_directory_with_retries(source, destination, *, operation):
    """Move um diretorio sem sobrescrever destino nem encerrar processos.

    Repeticoes limitadas protegem contra antiviruses e handles transitórios.
    Se o bloqueio continuar, o caminho original permanece intocado.
    """
    source, destination = Path(source), Path(destination)
    if not source.is_dir():
        raise UpdateError(f'{operation}: pasta de origem ausente: {source}')
    if destination.exists():
        raise UpdateError(f'{operation}: destino ja existe; nenhum dado sera sobrescrito: {destination}')
    last_error = None
    for attempt in range(_RENAME_ATTEMPTS):
        try:
            source.rename(destination)
            return
        except OSError as error:
            if not _retryable_rename_error(error):
                raise
            last_error = error
            if attempt < _RENAME_ATTEMPTS - 1:
                time.sleep(min(_RENAME_INITIAL_DELAY * (attempt + 1), 1.4))
    raise UpdateError(
        f'{operation}: a pasta continuou bloqueada pelo Windows apos tentativas '
        f'limitadas ({last_error}). Feche o VighnaStudy, qualquer atualizador '
        'antigo e janelas ou ferramentas que estejam usando a pasta dist; '
        'confira eventuais bloqueios do antivirus. Nada sera forçado.'
    ) from last_error




def _leave_active_executable_directory(root, active):
    """Evita que o proprio processo atualizador bloqueie a pasta no Windows.

    Pythonw pode herdar o diretorio corrente do EXE que o iniciou. Nesse caso,
    o handle de current-directory pode impedir o rename mesmo apos sair o EXE.
    """
    current = Path.cwd().resolve()
    active = Path(active).resolve()
    if current == active or active in current.parents:
        os.chdir(Path(root).resolve())



# PRE-BUILD CHECK V2: examina janelas de pastas do Explorer sem fechar processos.
def _janelas_explorer_sobre_pasta(active, *, system=None, invoke=None):
    """Retorna as janelas Explorer com diretorio atual dentro de active.

    Consulta Shell.Application em PowerShell no Windows. Nao tenta enumerar
    todos os handles de todos os processos; o rename final continua protegido.
    """
    if system is None:
        system = os.name
    if system != 'nt':
        return []
    active = str(Path(active).resolve())
    powershell = r"""
$ErrorActionPreference = 'Stop'
$target = $env:VIGHNA_ACTIVE_EXE_DIR.TrimEnd('\').ToLowerInvariant()
$shell = New-Object -ComObject Shell.Application
foreach ($window in @($shell.Windows())) {
    try {
        $folder = $window.Document.Folder.Self.Path
        if ($folder) {
            $normalized = $folder.TrimEnd('\').ToLowerInvariant()
            if ($normalized -eq $target -or $normalized.StartsWith($target + '\')) {
                [Console]::Out.WriteLine($folder)
            }
        }
    } catch { }
}
"""
    env = os.environ.copy()
    env['VIGHNA_ACTIVE_EXE_DIR'] = active
    command = ['powershell.exe', '-NoProfile', '-NonInteractive',
               '-EncodedCommand', __import__('base64').b64encode(powershell.encode('utf-16le')).decode('ascii')]
    try:
        run = invoke or subprocess.run
        outcome = run(command, capture_output=True, text=True, errors='replace',
                      env=env, timeout=20,
                      creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise UpdateError('Nao foi possivel conferir as janelas do Explorador antes da compilacao; '
                          'feche as janelas de C:\\SistemaEstudos\\dist e tente de novo. '
                          f'Detalhe: {exc}') from exc
    if outcome.returncode != 0:
        raise UpdateError('Falha na consulta das janelas do Explorador; atualizacao bloqueada antes da compilacao. '
                          + (outcome.stderr or '')[-400:])
    return sorted(set(line.strip() for line in outcome.stdout.splitlines() if line.strip()))


def _verificar_bloqueio_explorer(active):
    abertas = _janelas_explorer_sobre_pasta(active)
    if abertas:
        exemplos = '; '.join(abertas[:3])
        raise UpdateError(
            'Atualizacao evitada ANTES da compilacao: existem janelas do Explorador '
            'abertas dentro da pasta do executavel. Feche essas janelas e tente novamente. '
            'Nenhuma janela sera encerrada automaticamente. Pastas: ' + exemplos
        )


def _pasta_cache_compilacao(root, python_exe):
    """Cache reutilizavel segregado por especificacao e ambiente Python.

    O PyInstaller determina quais artefatos podem ser reaproveitados. O diretório
    ativo dist nunca e usado como cache ou staging.
    """
    spec_file = Path(root) / 'VighnaStudy.spec'
    interpreter = Path(python_exe)
    environment_signature = (str(interpreter.resolve()) + '|' +
                             str(interpreter.stat().st_mtime_ns) + '|' +
                             str(interpreter.stat().st_size))
    digest = hashlib.sha256(spec_file.read_bytes() + environment_signature.encode('utf-8')).hexdigest()[:20]
    return Path(root) / '_vighna_pyinstaller_cache' / digest


def _restore_from_saved(root, saved, state):
    """Rollback conservador: nunca apaga a instalacao ativa para restaurar.

    Se uma versao nova estiver ativa e houver copia anterior, a nova fica
    isolada no backup, para possibilitar retorno mesmo durante outra falha.
    """
    root = Path(root)
    saved = Path(saved)
    active = root / 'dist' / 'SistemaEstudos'
    previous = saved / 'anterior_executavel'
    quarantine = saved / 'executavel_nao_confirmado'
    _leave_active_executable_directory(root, active)
    if previous.is_dir():
        if not (previous / 'VighnaStudy.exe').is_file():
            raise UpdateError('Backup do executavel anterior esta incompleto; rollback abortado.')
        had_active = active.exists()
        if had_active:
            _rename_directory_with_retries(active, quarantine,
                                           operation='Isolar executavel nao confirmado')
        try:
            _rename_directory_with_retries(previous, active,
                                           operation='Restaurar executavel anterior')
        except Exception as restore_error:
            # Mantem um executavel ativo sempre que o rollback for interrompido.
            if had_active and quarantine.is_dir() and not active.exists():
                try:
                    _rename_directory_with_retries(quarantine, active,
                                                   operation='Repor executavel temporario')
                except Exception as fallback_error:
                    raise UpdateError(
                        f'Restauracao do executavel anterior falhou ({restore_error}); '
                        f'reposicao da versao ativa tambem falhou ({fallback_error}). '
                        'Preserve as pastas de backup; recuperacao manual necessaria.'
                    ) from fallback_error
            raise
    elif not (active / 'VighnaStudy.exe').is_file():
        raise UpdateError('Nem a versao anterior nem um executavel ativo foram encontrados.')
    for relative, existed in state['sources'].items():
        if not valid_source_path(relative) or not isinstance(existed, bool):
            raise UpdateError('Registro de recuperacao contem caminho invalido.')
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

def _backup_vighnaknowledge_independente(root, active_exe_dir, saved):
    """Snapshot SQLite consistente, sem migrar, apagar ou alterar fonte.

    A origem canonica e C:/SistemaEstudos/VighnaKnowledge. Se uma base antiga
    ainda estiver dentro de dist, bloquear a troca para impedir ocultacao de
    registros apos a nova compilacao.
    """
    canon = Path(root) / 'VighnaKnowledge' / 'knowledge.sqlite3'
    legado = Path(active_exe_dir) / 'VighnaKnowledge' / 'knowledge.sqlite3'
    if legado.is_file() and not canon.is_file():
        raise UpdateError(
            'Existe um banco VighnaKnowledge dentro da pasta do executavel, '
            'mas ainda nao foi migrado para C:\\SistemaEstudos\\VighnaKnowledge. '
            'Faca o resgate do banco antes de atualizar; nenhum arquivo foi movido.')
    if not canon.is_file():
        return None
    destino = Path(saved) / 'VighnaKnowledge' / 'knowledge.sqlite3'
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(canon.resolve().as_uri() + '?mode=ro', uri=True, timeout=10) as origem:
            if origem.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                raise UpdateError('Banco independente VighnaKnowledge falhou na verificacao SQLite.')
            with sqlite3.connect(str(destino), timeout=10) as copia:
                origem.backup(copia)
                if copia.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                    raise UpdateError('Snapshot VighnaKnowledge nao foi validado.')
                tabelas = {linha[0] for linha in origem.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                if 'vk_microthemes' not in tabelas:
                    raise UpdateError('Base VighnaKnowledge existente nao possui catalogo reconhecivel.')
                for tabela in ('vk_microthemes', 'vk_answer_events', 'vk_first_evidence'):
                    if tabela in tabelas:
                        a = origem.execute('SELECT COUNT(*) FROM '+tabela).fetchone()[0]
                        b = copia.execute('SELECT COUNT(*) FROM '+tabela).fetchone()[0]
                        if a != b:
                            raise UpdateError('Contagem divergente no backup do VighnaKnowledge: '+tabela)
        return str(destino)
    except (sqlite3.Error, OSError) as exc:
        raise UpdateError('Nao foi possivel proteger o banco VighnaKnowledge: '+str(exc)) from exc


def install_package(package, root, *, python_exe, report=lambda progress, status: None,
                    runner=None, keep_work=False):
    """Realiza build em staging e troca com rollback. Deve executar após fechar o app.

    runner: injeção para testes; recebe comando, cwd, report e deve lançar exceção
    em caso de falha. A versão de produção usa subprocess sem shell.
    """
    callback_original = report
    tempo_inicio = time.monotonic()
    marcos = []
    def report(progresso, status):
        marcos.append({'progresso': progresso, 'segundos_desde_inicio': round(time.monotonic()-tempo_inicio, 3), 'fase': status})
        callback_original(progresso, status)

    root = Path(root).resolve()
    package = Path(package).resolve()
    manifest = inspect_package(package, root)
    package_sha256 = hash_file(package)
    source_db = root / 'estudos.db'
    # Reservar espaço para staging, backup de fontes, build e margem de erro.
    # A estimativa é deliberadamente conservadora, não uma alocação real.
    with zipfile.ZipFile(package) as archive:
        estimated_source_bytes = sum(info.file_size for info in archive.infolist())
    necessary_free = (3 * estimated_source_bytes + source_db.stat().st_size
                      + 512 * MiB)
    if shutil.disk_usage(root).free < necessary_free:
        raise UpdateError('Espaço insuficiente para atualizar com backup e rollback.')
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
        _leave_active_executable_directory(root, active_exe_dir)
        _verificar_bloqueio_explorer(active_exe_dir)
        report(14, 'Criando backup permanente e verificando integridade...')
        saved.mkdir(parents=True, exist_ok=False)
        backup_database(source_db, saved / 'estudos.db')
        _backup_vighnaknowledge_independente(root, active_exe_dir, saved)
        _log(history, {'date': datetime.now().isoformat(), 'id':run_id, 'status':'started',
                       'sha256':package_sha256, 'package':package.name,'from':manifest['base_build'],'to':manifest['target_build']})
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
                # Extração em fluxo; não materializa arquivos grandes na RAM.
                with archive.open(filename, 'r') as source, target.open('wb') as destination:
                    shutil.copyfileobj(source, destination, 1024 * 1024)
        if version_from_file(work / 'versao.py') != (manifest['target_version'], manifest['target_build'], manifest['schema']):
            raise UpdateError('Versão divergente na área de compilação.')
        for file in work.rglob('*.py'):
            compile(file.read_bytes(), str(file), 'exec')
        report(38, 'Compilando a nova versão em pasta isolada...')
        if runner is None:
            cache = _pasta_cache_compilacao(root, python_exe)
            cache.mkdir(parents=True, exist_ok=True)
            cmd = [str(python_exe), '-m', 'PyInstaller', '--noconfirm',
                   '--distpath', str(staging / 'dist'), '--workpath', str(cache),
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
        _verificar_bloqueio_explorer(active_exe_dir)
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
        report(82, 'Instalando novo executável com possibilidade de retorno...')
        # Tenta preservar a pasta anterior ANTES de alterar os fontes de producao.
        # Se o Windows bloquear a pasta, os fontes e o executavel ficam intactos.
        original_dist.parent.mkdir(parents=True, exist_ok=True)
        _leave_active_executable_directory(root, active_exe_dir)
        _rename_directory_with_retries(active_exe_dir, original_dist,
                                       operation='Preservar executavel anterior')
        dist_moved = True
        for filename in manifest['files']:
            source_target = root / filename
            new_source = work / filename
            source_target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(new_source, source_target)
        _rename_directory_with_retries(build_output, active_exe_dir,
                                       operation='Instalar executavel novo')
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
                       'sha256':package_sha256, 'package':package.name,
                       'from':manifest['base_build'], 'to':manifest['target_build'],
                       'backup':str(saved)})
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
                           'sha256':package_sha256, 'package':package.name,
                           'from':manifest['base_build'], 'to':manifest['target_build'],
                           'error':str(err), 'rollback_errors':rollback_errors})
        except OSError:
            pass
        suffix = (' Reversão incompleta: ' + '; '.join(rollback_errors)) if rollback_errors else ''
        raise UpdateError(str(err) + suffix) from err
    finally:
        # Metricas exclusivamente tecnicas, sem respostas, questoes ou dados pessoais.
        # Gravacao best effort: jamais substitui o motivo da falha original.
        if saved.is_dir():
            try:
                _write_atomic_json(saved / 'desempenho_atualizacao.json', {
                    'formato': 'vighna-update-timing-v1',
                    'tempo_total_segundos': round(time.monotonic()-tempo_inicio, 3),
                    'marcos': marcos,
                    'cache_pyinstaller': 'persistente_sem_clean',
                })
            except OSError:
                pass
        if not keep_work and staging.exists():
            try:
                shutil.rmtree(staging)
            except OSError:
                pass
