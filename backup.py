from datetime import datetime
from pathlib import Path
import shutil
import sys
import sqlite3
import os


if getattr(sys, "frozen", False):
    PASTA_PROJETO = Path(sys.executable).resolve().parent
else:
    PASTA_PROJETO = Path(__file__).resolve().parent

ARQUIVO_BANCO = PASTA_PROJETO / "estudos.db"
PASTA_BACKUPS = PASTA_PROJETO / "backups"
MAX_BACKUPS = 30


def garantir_pasta_backups():
    PASTA_BACKUPS.mkdir(
        parents=True,
        exist_ok=True
    )


def limpar_backups_antigos():
    garantir_pasta_backups()

    backups = sorted(
        PASTA_BACKUPS.glob("estudos_*.db"),
        key=lambda caminho: caminho.stat().st_mtime,
        reverse=True
    )

    for arquivo in backups[MAX_BACKUPS:]:
        try:
            arquivo.unlink()
        except OSError:
            pass


def verificar_integridade_banco(caminho=ARQUIVO_BANCO):
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
        resultado = conexao.execute(
            "PRAGMA integrity_check"
        ).fetchone()

        if (
            resultado is None
            or str(resultado[0]).strip().lower() != "ok"
        ):
            return False, (
                "O banco não passou no PRAGMA integrity_check: "
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
    caminho = Path(caminho).resolve()

    valido, mensagem = validar_backup(
        caminho
    )

    if not valido:
        raise ValueError(mensagem)

    # Preserva o estado atual antes de qualquer substituição. Se o banco
    # atual já estiver corrompido, a API de backup pode recusar a cópia; nesse
    # caso preservamos os bytes brutos em uma pasta separada para perícia.
    try:
        backup_segurança = fazer_backup(
            "antes_restauracao"
        )
    except Exception:
        pasta_corrompidos = PASTA_BACKUPS / "corrompidos"
        pasta_corrompidos.mkdir(parents=True, exist_ok=True)
        agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_segurança = pasta_corrompidos / f"estudos_{agora}_antes_restauracao_corrompido.db"
        shutil.copy2(ARQUIVO_BANCO, backup_segurança)

    temporario = (
        ARQUIVO_BANCO.parent /
        "estudos_restauracao.tmp"
    )

    try:
        shutil.copy2(
            caminho,
            temporario
        )

        # Verifica também a cópia temporária antes de trocar o banco.
        conexao = sqlite3.connect(
            temporario
        )

        try:
            integridade = conexao.execute(
                "PRAGMA integrity_check"
            ).fetchone()

            if (
                integridade is None
                or str(integridade[0]).lower() != "ok"
            ):
                raise ValueError(
                    "A cópia temporária do backup falhou "
                    "na verificação de integridade."
                )
        finally:
            conexao.close()

        os.replace(
            temporario,
            ARQUIVO_BANCO
        )

        return backup_segurança

    except Exception:
        try:
            if temporario.exists():
                temporario.unlink()
        except OSError:
            pass

        raise
