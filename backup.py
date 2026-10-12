from datetime import datetime
from pathlib import Path
import shutil
import sqlite3
import os


from caminhos import CAMINHO_BANCO, PASTA_BACKUPS, PASTA_DADOS

PASTA_PROJETO = PASTA_DADOS
ARQUIVO_BANCO = CAMINHO_BANCO
MAX_BACKUPS = 30


def garantir_pasta_backups():
    PASTA_BACKUPS.mkdir(
        parents=True,
        exist_ok=True
    )


def _backups_reservados_para_restauracao():
    """Protege backups solicitados enquanto o Vighna fecha para restaurar.

    O closeEvent executa fazer_backup("fechamento"), que normalmente pode
    excluir o backup mais antigo. Um pedido offline recém-criado mantém o
    arquivo escolhido durante o encerramento (o worker aguarda até 90 s).
    Pedidos antigos não bloqueiam a política de retenção indefinidamente.
    """
    import json
    import time

    protegidos = set()
    pedidos = PASTA_BACKUPS / "restauracoes_offline"
    if not pedidos.is_dir():
        return protegidos

    agora = time.time()
    raiz = PASTA_BACKUPS.resolve()
    for pedido in pedidos.glob("pedido_*.json"):
        try:
            # 10 min cobrem o encerramento normal e o limite do worker.
            idade = agora - pedido.stat().st_mtime
            if idade < -60 or idade > 600:
                continue
            dados = json.loads(pedido.read_text(encoding="utf-8"))
            if not isinstance(dados, dict):
                continue
            if dados.get("formato") != "vighna-offline-restore-r1":
                continue
            selecionado = Path(dados.get("backup", "")).resolve()
            if selecionado.parent == raiz:
                protegidos.add(selecionado)
        except (OSError, ValueError, TypeError, KeyError):
            continue
    return protegidos


def limpar_backups_antigos():
    garantir_pasta_backups()

    backups = sorted(
        PASTA_BACKUPS.glob("estudos_*.db"),
        key=lambda caminho: caminho.stat().st_mtime,
        reverse=True
    )

    # Preserve a contagem máxima sem excluir o arquivo de um pedido offline.
    protegidos = _backups_reservados_para_restauracao()
    excesso = max(0, len(backups) - MAX_BACKUPS)
    for arquivo in reversed(backups):
        if excesso <= 0:
            break
        try:
            if arquivo.resolve() in protegidos:
                continue
            arquivo.unlink()
            excesso -= 1
        except OSError:
            pass


def verificar_integridade_banco(caminho=ARQUIVO_BANCO, completo=False):
    """Valida o SQLite sem transformar a abertura do app em auditoria completa.

    Na inicialização normal usamos ``quick_check(1)``: ele detecta corrupção
    estrutural/malformação do arquivo com custo muito menor. A verificação
    completa continua disponível para recuperação, backup e diagnóstico
    explícito por meio de ``completo=True``.
    """
    caminho = Path(caminho)

    if not caminho.exists():
        return False, "O arquivo estudos.db não existe."

    conexao = None

    try:
        uri = caminho.resolve().as_uri() + "?mode=ro"
        conexao = sqlite3.connect(
            uri,
            uri=True,
            timeout=5
        )
        pragma = "integrity_check" if completo else "quick_check(1)"
        resultado = conexao.execute(
            f"PRAGMA {pragma}"
        ).fetchone()

        if (
            resultado is None
            or str(resultado[0]).strip().lower() != "ok"
        ):
            return False, (
                f"O banco não passou no PRAGMA {pragma}: "
                + str(resultado[0] if resultado else "sem resultado")
            )

        return True, "OK"

    except sqlite3.Error as erro:
        return False, f"SQLite: {erro}"

    finally:
        if conexao is not None:
            conexao.close()


def fazer_backup(motivo="manual"):
    if not ARQUIVO_BANCO.exists():
        return None

    garantir_pasta_backups()

    agora = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    destino = (
        PASTA_BACKUPS /
        f"estudos_{agora}_{motivo}.db"
    )

    origem_con = None
    destino_con = None

    try:
        origem_con = sqlite3.connect(
            ARQUIVO_BANCO,
            timeout=10
        )
        origem_con.execute(
            "PRAGMA busy_timeout = 5000"
        )
        destino_con = sqlite3.connect(
            destino,
            timeout=10
        )

        # A API de backup do SQLite inclui corretamente o estado WAL e gera
        # um snapshot consistente mesmo se houver outra conexão aberta.
        origem_con.backup(
            destino_con
        )

        integridade = destino_con.execute(
            "PRAGMA integrity_check"
        ).fetchone()

        if (
            integridade is None
            or str(integridade[0]).strip().lower() != "ok"
        ):
            raise RuntimeError(
                "O snapshot criado não passou na verificação de integridade."
            )

    except Exception:
        try:
            if destino.exists():
                destino.unlink()
        except OSError:
            pass
        raise

    finally:
        if destino_con is not None:
            destino_con.close()
        if origem_con is not None:
            origem_con.close()

    limpar_backups_antigos()

    return destino



def listar_backups():
    garantir_pasta_backups()

    arquivos = sorted(
        PASTA_BACKUPS.glob("estudos_*.db"),
        key=lambda caminho: caminho.stat().st_mtime,
        reverse=True
    )

    resultado = []

    for caminho in arquivos:
        try:
            stat = caminho.stat()

            nome = caminho.stem

            motivo = "—"

            # Formato esperado:
            # estudos_YYYY-MM-DD_HH-MM-SS_motivo.db
            partes = nome.split("_", 3)

            if len(partes) >= 4:
                motivo = partes[3].replace(
                    "_",
                    " "
                )

            resultado.append({
                "caminho": caminho,
                "nome": caminho.name,
                "data_modificacao": stat.st_mtime,
                "tamanho": stat.st_size,
                "motivo": motivo
            })

        except OSError:
            continue

    return resultado


def validar_backup(caminho):
    caminho = Path(caminho).resolve()

    if not caminho.exists():
        return False, "O arquivo de backup não existe."

    if not caminho.is_file():
        return False, "O caminho selecionado não é um arquivo."

    try:
        pasta_resolvida = PASTA_BACKUPS.resolve()

        if pasta_resolvida not in caminho.parents:
            return (
                False,
                "O arquivo selecionado não pertence à pasta de backups."
            )
    except OSError:
        return False, "Não foi possível validar o caminho do backup."

    conexao = None

    try:
        uri = caminho.as_uri() + "?mode=ro"

        conexao = sqlite3.connect(
            uri,
            uri=True,
            timeout=5
        )

        integridade = conexao.execute(
            "PRAGMA integrity_check"
        ).fetchone()

        if (
            integridade is None
            or str(integridade[0]).lower() != "ok"
        ):
            return (
                False,
                "O arquivo não passou na verificação de integridade."
            )

        tabelas = {
            linha[0]
            for linha in conexao.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()
        }

        essenciais = {
            "disciplinas",
            "topicos",
            "revisoes"
        }

        faltantes = essenciais - tabelas

        if faltantes:
            return (
                False,
                "O arquivo não possui a estrutura esperada "
                "do Sistema de Estudos."
            )

        # O integrity_check verifica estrutura, mas não detecta todas as
        # violações de relacionamentos. Rejeitar antes de agendar restauração.
        if conexao.execute("PRAGMA foreign_key_check").fetchone() is not None:
            return False, "O backup possui violação de chave estrangeira."

        return True, "OK"

    except sqlite3.Error as erro:
        return (
            False,
            f"SQLite não conseguiu abrir o backup: {erro}"
        )

    finally:
        if conexao is not None:
            conexao.close()


def restaurar_backup(caminho):
    """Bloqueio definitivo da substituição de SQLite no processo Qt ativo.

    A restauração voluntária é feita pelo worker externo após a saída do app.
    """
    raise RuntimeError(
        "Restauração durante a execução desativada por segurança. "
        "Use iniciar_restauracao_offline() pela janela de Backups."
    )

# M1c-R1 - A restauração de backup é uma operação offline. Nunca fazer
# os.replace(estudos.db) no processo que ainda mantém conexões SQLite abertas.

def _sha256_arquivo(caminho):
    import hashlib
    resumo = hashlib.sha256()
    with Path(caminho).open('rb') as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b''):
            resumo.update(bloco)
    return resumo.hexdigest()


def _gravar_json_atomico(caminho, conteudo):
    import json
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_name(caminho.name + '.tmp')
    tmp.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, caminho)


def _pasta_pedidos_offline():
    destino = PASTA_BACKUPS / 'restauracoes_offline'
    destino.mkdir(parents=True, exist_ok=True)
    return destino


def _comando_worker_offline(plano):
    """Reutiliza o processo Vighna sem depender de `.venv` externo.

    No PyInstaller, o EXE é invocado novamente em modo CLI. Em modo fonte,
    Python executa main.py, cuja primeira ação reconhece esse argumento
    antes de importar splash e PySide6.
    """
    import sys
    if getattr(sys, 'frozen', False):
        executavel = Path(sys.executable)
        if not executavel.is_file():
            raise RuntimeError('Executável do Vighna não encontrado.')
        return [str(executavel), '--vighna-restore-offline', str(plano)]
    main = PASTA_DADOS / 'main.py'
    if not main.is_file():
        raise RuntimeError('main.py indisponível para o worker offline.')
    return [sys.executable, str(main), '--vighna-restore-offline', str(plano)]


def iniciar_restauracao_offline(caminho):
    """Solicita restauração externa; a GUI deve sair IMEDIATAMENTE após lançar."""
    import subprocess
    import sys
    import uuid

    selecionado = Path(caminho).resolve()
    valido, motivo = validar_backup(selecionado)
    if not valido:
        raise ValueError(motivo)
    raiz = PASTA_DADOS.resolve()
    # Descobrir o lançador antes de registrar qualquer pedido.
    _comando_worker_offline('pedido_a_validar')

    token = uuid.uuid4().hex
    diretorio = _pasta_pedidos_offline()
    plano = diretorio / ('pedido_' + token + '.json')
    log = diretorio / ('pedido_' + token + '.log')
    _gravar_json_atomico(plano, {
        'formato': 'vighna-offline-restore-r1',
        'id': token,
        'backup': str(selecionado),
        'sha256_backup': _sha256_arquivo(selecionado),
        'banco': str(ARQUIVO_BANCO.resolve()),
        'pid_aplicativo': os.getpid(),
        'criado': datetime.now().isoformat(timespec='seconds'),
    })
    # Uma falha de spawn cancela o pedido: não fecha o aplicativo.
    try:
        flags = 0x08000000 if sys.platform == 'win32' else 0  # CREATE_NO_WINDOW
        with log.open('ab') as saida:
            subprocess.Popen(
                _comando_worker_offline(plano),
                cwd=str(raiz), stdout=saida, stderr=subprocess.STDOUT,
                close_fds=True, creationflags=flags,
                start_new_session=(sys.platform != 'win32'),
            )
    except Exception:
        plano.unlink(missing_ok=True)
        raise
    return plano, log


def _esperar_pid_encerrar(pid, limite=90):
    """A confirmação de encerramento impede o worker de alterar o DB ativo."""
    import sys
    import time
    if pid <= 0 or pid == os.getpid():
        raise RuntimeError('PID de origem inválido para restauração offline.')
    if sys.platform == 'win32':
        import ctypes
        k32 = ctypes.WinDLL('kernel32', use_last_error=True)
        k32.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
        k32.OpenProcess.restype = ctypes.c_void_p
        k32.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        k32.WaitForSingleObject.restype = ctypes.c_ulong
        k32.CloseHandle.argtypes = [ctypes.c_void_p]
        handle = k32.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE
        if not handle:
            if ctypes.get_last_error() == 87:  # ERROR_INVALID_PARAMETER = PID encerrou
                return
            raise RuntimeError('Não foi possível verificar o encerramento do Vighna.')
        try:
            codigo = k32.WaitForSingleObject(handle, limite * 1000)
            if codigo != 0:  # WAIT_OBJECT_0
                raise RuntimeError('Vighna não encerrou dentro do prazo; nenhuma restauração efetuada.')
        finally:
            k32.CloseHandle(handle)
        return
    inicio = time.monotonic()
    while time.monotonic() - inicio < limite:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        except PermissionError as exc:
            raise RuntimeError('Sem permissão para verificar o processo original.') from exc
        time.sleep(0.2)
    raise RuntimeError('O aplicativo não encerrou dentro do prazo; restauração cancelada.')


def _confirmar_arquivos_livres_windows(banco):
    """Falha se outro processo ainda tem o DB ou WAL aberto no Windows."""
    import sys
    if sys.platform != 'win32':
        return
    import ctypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_ulong,
                                  ctypes.c_ulong, ctypes.c_void_p, ctypes.c_ulong,
                                  ctypes.c_ulong, ctypes.c_void_p]
    kernel.CreateFileW.restype = ctypes.c_void_p
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    invalido = ctypes.c_void_p(-1).value
    for arquivo in (banco, Path(str(banco) + '-wal'), Path(str(banco) + '-shm')):
        if not arquivo.exists():
            continue
        handle = kernel.CreateFileW(str(arquivo), 0x80000000, 0, None, 3, 0x80, None)
        if handle == invalido or not handle:
            raise RuntimeError(
                f'O banco ainda está aberto por outro processo: {arquivo.name}. '
                'Feche todas as instâncias antes de restaurar.'
            )
        kernel.CloseHandle(handle)


def _validar_integridade_arquivo(caminho):
    conexao = None
    try:
        uri = Path(caminho).resolve().as_uri() + '?mode=ro'
        conexao = sqlite3.connect(uri, uri=True, timeout=5)
        integridade = conexao.execute('PRAGMA integrity_check').fetchone()
        if integridade != ('ok',):
            raise RuntimeError(f'Falha no integrity_check: {integridade!r}')
        # Não inventar schema: a validação existente é preservada.
        essenciais = {'disciplinas', 'topicos', 'revisoes'}
        tabelas = {linha[0] for linha in conexao.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        if not essenciais.issubset(tabelas):
            raise RuntimeError('Banco sem tabelas essenciais.')
    finally:
        if conexao is not None:
            conexao.close()


def _verificar_relacoes_arquivo(caminho):
    """Exige FKs válidas em bancos candidatos, nunca no snapshot de segurança."""
    conexao = None
    try:
        uri = Path(caminho).resolve().as_uri() + '?mode=ro'
        conexao = sqlite3.connect(uri, uri=True, timeout=5)
        if conexao.execute('PRAGMA foreign_key_check').fetchone() is not None:
            raise RuntimeError('O backup possui violação de chave estrangeira.')
    finally:
        if conexao is not None:
            conexao.close()


def _executar_restauracao_offline(plano):
    import json
    plano = Path(plano).resolve()
    diretorio = _pasta_pedidos_offline().resolve()
    if plano.parent != diretorio or not plano.name.startswith('pedido_'):
        raise RuntimeError('Pedido fora da pasta autorizada.')
    dados = json.loads(plano.read_text(encoding='utf-8'))
    if dados.get('formato') != 'vighna-offline-restore-r1':
        raise RuntimeError('Formato de pedido não reconhecido.')
    token = str(dados.get('id', ''))
    if len(token) != 32 or any(c not in '0123456789abcdef' for c in token):
        raise RuntimeError('Identificador inválido.')
    if plano.name != 'pedido_' + token + '.json':
        raise RuntimeError('Pedido inconsistente.')
    backup = Path(dados['backup']).resolve()
    banco = ARQUIVO_BANCO.resolve()
    if Path(dados['banco']).resolve() != banco:
        raise RuntimeError('O banco atual não corresponde ao pedido.')
    if not backup.is_file() or _sha256_arquivo(backup) != dados.get('sha256_backup'):
        raise RuntimeError('O backup mudou desde a confirmação; restauração recusada.')
    valido, motivo = validar_backup(backup)
    if not valido:
        raise RuntimeError('Backup não válido: ' + motivo)

    _esperar_pid_encerrar(int(dados['pid_aplicativo']))
    _confirmar_arquivos_livres_windows(banco)

    # O estado atual completo é copiado ANTES de tocar no banco ativo.
    salvaguarda = diretorio / ('salvaguarda_' + token)
    salvaguarda.mkdir(parents=True, exist_ok=False)
    for nome in (banco.name, banco.name + '-wal', banco.name + '-shm'):
        origem = banco.parent / nome
        if origem.is_file():
            shutil.copy2(origem, salvaguarda / nome)

    anterior = salvaguarda / 'estado_anterior_consistente.db'
    conn_src, conn_dst = None, None
    try:
        conn_src = sqlite3.connect(banco, timeout=5)
        conn_dst = sqlite3.connect(anterior, timeout=5)
        conn_src.backup(conn_dst)
        _validar_integridade_arquivo(anterior)
    finally:
        if conn_dst is not None:
            conn_dst.close()
        if conn_src is not None:
            conn_src.close()

    candidato = banco.with_name(banco.name + '.' + token + '.restaurar.tmp')
    shutil.copy2(backup, candidato)
    _validar_integridade_arquivo(candidato)
    _verificar_relacoes_arquivo(candidato)
    if _sha256_arquivo(candidato) != dados['sha256_backup']:
        raise RuntimeError('Arquivo temporário diverge do backup escolhido.')

    # WAL checkpointado ANTES de retirar os sidecars; nenhuma transação atual perdida.
    _confirmar_arquivos_livres_windows(banco)
    from contextlib import closing
    with closing(sqlite3.connect(banco, timeout=5)) as conn:
        with conn:
            resultado = conn.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone()
            if resultado and resultado[0] != 0:
                raise RuntimeError('WAL ocupado: cancelada a restauração.')

    trocou = False
    try:
        _confirmar_arquivos_livres_windows(banco)
        # Após checkpoint, o WAL pode ser descartado com segurança offline.
        for sufixo in ('-wal', '-shm'):
            Path(str(banco) + sufixo).unlink(missing_ok=True)
        os.replace(candidato, banco)
        trocou = True
        if _sha256_arquivo(banco) != dados['sha256_backup']:
            raise RuntimeError('O banco substituído não corresponde ao backup escolhido.')
        _validar_integridade_arquivo(banco)
        _verificar_relacoes_arquivo(banco)
        # WAL/SHM pré-existentes foram removidos antes da substituição.
        # SQLite pode criar sidecars NOVOS e legítimos durante a validação
        # (especialmente se o backup estiver configurado em journal_mode=WAL).
        return {'situacao': 'concluida', 'backup': str(backup),
                'salvaguarda': str(salvaguarda), 'id': token}
    except Exception:
        # Falha após substituir: retorno para snapshot SQL consistente anterior.
        if trocou:
            _confirmar_arquivos_livres_windows(banco)
            for sufixo in ('-wal', '-shm'):
                Path(str(banco) + sufixo).unlink(missing_ok=True)
            os.replace(anterior, banco)
            _validar_integridade_arquivo(banco)
        raise
    finally:
        candidato.unlink(missing_ok=True)


def _cli_restauracao_offline(argv=None):
    import sys
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 2 or argv[0] != '--restaurar-offline':
        print('Uso exclusivo: backup.py --restaurar-offline ARQUIVO_PEDIDO', file=sys.stderr)
        return 2
    plano = Path(argv[1])
    ultima = _pasta_pedidos_offline() / 'ultimo_resultado.json'
    try:
        resultado = _executar_restauracao_offline(plano)
        _gravar_json_atomico(ultima, resultado)
        print('RESTAURACAO OFFLINE CONCLUIDA:', resultado['backup'], flush=True)
        return 0
    except Exception as erro:
        import traceback
        resultado = {'situacao': 'falha', 'erro': str(erro),
                     'pedido': str(plano),
                     'data': datetime.now().isoformat(timespec='seconds')}
        _gravar_json_atomico(ultima, resultado)
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    raise SystemExit(_cli_restauracao_offline())
