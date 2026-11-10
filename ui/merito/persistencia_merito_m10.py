"""VighnaStudy M10 — persistência durável do mérito GLOBAL (somente desenvolvimento).

Banco de mérito separado do banco acadêmico. A origem acadêmica é lida via
adaptador M09 (SQLite mode=ro), validado antes de qualquer publicação.
NÃO ligar automaticamente à instalação do usuário antes da homologação Windows.
"""
from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass, replace
from hashlib import sha256
from datetime import datetime, timezone
from pathlib import Path
import re
import sqlite3

from .adaptador_banco_merito_m09 import (LeituraMeritoM09, ler_historico_merito_sqlite)
from .contrato_historico_merito import ResultadoIntegracao
from .motor_merito_global_v2 import MARCOS, ResumoMeritoGlobal

APPLICATION_ID = 0x56474D10  # banco lateral Vighna Global Merit, schema 1
SCHEMA_VERSION = 1
MARCO_SQL = ",".join(str(m) for m in MARCOS)
PERFIL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")


class PersistenciaMeritoInvalida(RuntimeError):
    """Falha fechada: não publicar medalhas nem sobrescrever o arquivo suspeito."""


class ConflitoRevisaoMerito(PersistenciaMeritoInvalida):
    """Outra gravação ocorreu durante leitura; reiniciar apuração."""


@dataclass(frozen=True)
class ConquistaObservada:
    marco: int
    registrada_em: str  # primeira observação NO SISTEMA, não data histórica exata


@dataclass(frozen=True)
class EstadoMeritoDuravel:
    perfil_id: str
    origem_auditada: str
    recorde: int
    acertos: int
    erros: int
    pulos: int
    saldo: int
    tentativas_contabilizadas: int
    revisao: int
    atualizado_em: str
    conquistas: tuple[ConquistaObservada, ...]


@dataclass(frozen=True)
class ApuracaoPersistidaM10:
    resultado: ResultadoIntegracao  # gravacao_realizada=True SOMENTE após COMMIT
    estado: EstadoMeritoDuravel
    mudou: bool
    linhas_lidas: int


def _perfil(perfil_id: str) -> str:
    if not isinstance(perfil_id, str) or not PERFIL_RE.fullmatch(perfil_id):
        raise PersistenciaMeritoInvalida(
            "Informe ID estável explícito para o perfil (1–128 caracteres seguros)"
        )
    return perfil_id


def _caminhos(caminho_academico: str | Path, caminho_merito: str | Path) -> tuple[Path, Path]:
    origem = Path(caminho_academico).expanduser().resolve(strict=True)
    if not origem.is_file():
        raise PersistenciaMeritoInvalida("Banco acadêmico não é arquivo existente")
    destino = Path(caminho_merito).expanduser().resolve(strict=False)
    if destino == origem or (destino.exists() and origem.samefile(destino)):
        raise PersistenciaMeritoInvalida("Banco de mérito não pode ser banco acadêmico")
    if destino.is_dir():
        raise PersistenciaMeritoInvalida("Destino de mérito é diretório")
    # Arquivo separado, idealmente em pasta de dados do usuário, não no instalador.
    return origem, destino


def _verificar_sqlite(cx: sqlite3.Connection) -> None:
    try:
        appid = cx.execute("PRAGMA application_id").fetchone()[0]
        versao = cx.execute("PRAGMA user_version").fetchone()[0]
        if appid != APPLICATION_ID or versao != SCHEMA_VERSION:
            raise PersistenciaMeritoInvalida("Arquivo não é armazenamento M10 compatível")
        for table in ("perfis_merito", "conquistas_merito"):
            linha = cx.execute("SELECT type FROM sqlite_master WHERE name=?", (table,)).fetchone()
            if not linha or linha[0] != "table":
                raise PersistenciaMeritoInvalida(f"Tabela de mérito ausente: {table}")
        if cx.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise PersistenciaMeritoInvalida("Integridade SQLite do mérito não aprovada")
    except sqlite3.DatabaseError as exc:
        raise PersistenciaMeritoInvalida("Arquivo de mérito inválido ou corrompido") from exc


def _criar_sqlite(cx: sqlite3.Connection) -> None:
    cx.execute(f"PRAGMA application_id = {APPLICATION_ID}")
    cx.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    cx.execute("""
        CREATE TABLE perfis_merito (
            perfil_id TEXT PRIMARY KEY,
            origem TEXT NOT NULL,
            recorde INTEGER NOT NULL CHECK(recorde >= 0),
            acertos INTEGER NOT NULL CHECK(acertos >= 0),
            erros INTEGER NOT NULL CHECK(erros >= 0),
            pulos INTEGER NOT NULL CHECK(pulos >= 0),
            saldo INTEGER NOT NULL,
            tentativas INTEGER NOT NULL CHECK(tentativas >= 0),
            revisao INTEGER NOT NULL CHECK(revisao >= 1),
            atualizado_em TEXT NOT NULL,
            CHECK(saldo = acertos - erros),
            CHECK(tentativas = acertos + erros + pulos),
            CHECK(recorde >= saldo)
        )""")
    cx.execute(f"""
        CREATE TABLE conquistas_merito (
            perfil_id TEXT NOT NULL REFERENCES perfis_merito(perfil_id) ON DELETE CASCADE,
            marco INTEGER NOT NULL CHECK(marco IN ({MARCO_SQL})),
            registrada_em TEXT NOT NULL,
            PRIMARY KEY(perfil_id, marco)
        )
    """)


def _abrir_conexao(path: Path, *, criar: bool) -> sqlite3.Connection:
    if not criar and not path.is_file():
        raise PersistenciaMeritoInvalida("Arquivo de mérito desapareceu")
    if criar:
        path.parent.mkdir(parents=True, exist_ok=True)
    # sqlite3.connect sem modo RO apenas no arquivo de MÉRITO, nunca no acadêmico.
    mode = "rwc" if criar else "ro"
    cx = sqlite3.connect(path.as_uri() + f"?mode={mode}", uri=True, timeout=5.0)
    cx.execute("PRAGMA foreign_keys=ON")
    cx.execute("PRAGMA busy_timeout=5000")
    if criar:
        cx.execute("PRAGMA synchronous=FULL")
    else:
        cx.execute("PRAGMA query_only=ON")
    return cx


def _ler_estado_conexao(cx: sqlite3.Connection, perfil_id: str) -> EstadoMeritoDuravel | None:
    linha = cx.execute("""SELECT perfil_id, origem, recorde, acertos, erros, pulos,
                             saldo, tentativas, revisao, atualizado_em
                             FROM perfis_merito WHERE perfil_id = ?""", (perfil_id,)).fetchone()
    if linha is None:
        return None
    conquistas = cx.execute("""SELECT marco, registrada_em FROM conquistas_merito
                               WHERE perfil_id = ? ORDER BY marco""", (perfil_id,)).fetchall()
    estado = EstadoMeritoDuravel(*linha, tuple(ConquistaObservada(*r) for r in conquistas))
    esperados = tuple(m for m in MARCOS if m <= estado.recorde)
    encontrados = tuple(c.marco for c in estado.conquistas)
    if encontrados != esperados:
        raise PersistenciaMeritoInvalida("Histórico de conquistas diverge do recorde")
    if estado.recorde < 0 or estado.revisao < 1 or estado.saldo != estado.acertos - estado.erros:
        raise PersistenciaMeritoInvalida("Contadores de mérito persistidos inválidos")
    if not estado.origem_auditada or not estado.atualizado_em:
        raise PersistenciaMeritoInvalida("Identidade de origem ou data vazia")
    return estado


def ler_estado_merito(caminho_merito: str | Path, perfil_id: str) -> EstadoMeritoDuravel | None:
    """Consulta separada, em modo RO; não cria banco inexistente."""
    perfil_id = _perfil(perfil_id)
    arquivo = Path(caminho_merito).expanduser().resolve(strict=False)
    if not arquivo.exists():
        return None
    try:
        with closing(_abrir_conexao(arquivo, criar=False)) as cx:
            _verificar_sqlite(cx)
            return _ler_estado_conexao(cx, perfil_id)
    except sqlite3.DatabaseError as exc:
        raise PersistenciaMeritoInvalida("Falha ao consultar persistência") from exc


def _validar_leitura(leitura: LeituraMeritoM09, antigo: EstadoMeritoDuravel | None) -> None:
    if not isinstance(leitura, LeituraMeritoM09):
        raise PersistenciaMeritoInvalida("Somente leitura auditada M09 é aceita")
    d, resultado = leitura.diagnostico, leitura.resultado
    if d.esquema_validado is not True or d.consulta_somente_leitura is not True:
        raise PersistenciaMeritoInvalida("Esquema ou leitura somente-leitura não certificados")
    if resultado.origem_auditada != d.origem_fonte or not d.origem_fonte.startswith("sqlite-ro-m09:"):
        raise PersistenciaMeritoInvalida("Origem SQLite auditada divergente")
    r = resultado.resumo
    if not isinstance(r, ResumoMeritoGlobal) or resultado.gravacao_realizada is not False:
        raise PersistenciaMeritoInvalida("Resultado M09 incorreto ou já marcado como persistido")
    if type(resultado.linhas_auditadas) is not int or resultado.linhas_auditadas != d.linhas_totais:
        raise PersistenciaMeritoInvalida("Contagem de linhas auditadas divergente")
    if r.saldo != r.acertos - r.erros or r.recorde < r.saldo:
        raise PersistenciaMeritoInvalida("Resumo inconsistente")
    maximo_valido = max(antigo.recorde if antigo else 0, r.acertos)
    if r.recorde > maximo_valido:
        raise PersistenciaMeritoInvalida("Recorde supera histórico ou recorde anterior verificado")
    if antigo is not None:
        if resultado.origem_auditada != antigo.origem_auditada:
            raise PersistenciaMeritoInvalida("Origem acadêmica mudou; requer migração auditada")
        if r.recorde < antigo.recorde:
            raise PersistenciaMeritoInvalida("Recorde regressivo não pode ser gravado")


def _gravar_estado(cx: sqlite3.Connection, perfil_id: str, leitura: LeituraMeritoM09,
                  antigo: EstadoMeritoDuravel | None) -> bool:
    r = leitura.resultado.resumo
    desejado = (r.recorde, r.acertos, r.erros, r.pulos, r.saldo, r.tentativas_contabilizadas)
    anterior = ((antigo.recorde, antigo.acertos, antigo.erros, antigo.pulos,
                antigo.saldo, antigo.tentativas_contabilizadas) if antigo else None)
    if anterior == desejado:
        return False
    instante = datetime.now(timezone.utc).isoformat(timespec="seconds")
    revisao = (antigo.revisao + 1) if antigo else 1
    cx.execute("""INSERT INTO perfis_merito
      (perfil_id, origem, recorde, acertos, erros, pulos, saldo, tentativas, revisao, atualizado_em)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT(perfil_id) DO UPDATE SET
         recorde=excluded.recorde, acertos=excluded.acertos, erros=excluded.erros,
         pulos=excluded.pulos, saldo=excluded.saldo,
         tentativas=excluded.tentativas, revisao=excluded.revisao,
         atualizado_em=excluded.atualizado_em""",
      (perfil_id, leitura.resultado.origem_auditada, *desejado, revisao, instante))
    ja = {c.marco for c in antigo.conquistas} if antigo else set()
    for marco in MARCOS:
        if marco <= r.recorde and marco not in ja:
            cx.execute("INSERT INTO conquistas_merito(perfil_id,marco,registrada_em) VALUES(?,?,?)",
                       (perfil_id, marco, instante))
    return True


def apurar_e_persistir_merito(
    caminho_banco_academico: str | Path,
    caminho_banco_merito: str | Path,
    *,
    perfil_id: str,
    tentativas_concorrentes: int = 2,
) -> ApuracaoPersistidaM10:
    """Audit M09 -> commit atômico no banco de MÉRITO -> resultado publicável.

    Se outra apuração gravar antes do commit, reaudita para não usar recorde
    defasado. Nunca altera tabelas acadêmicas ou publica ao M08 diretamente.
    Data de conquista armazena PRIMEIRA OBSERVAÇÃO, não data de prova histórica.
    """
    perfil_id = _perfil(perfil_id)
    if type(tentativas_concorrentes) is not int or not 1 <= tentativas_concorrentes <= 5:
        raise PersistenciaMeritoInvalida("Limite de reauditorias inválido")
    banco_acad, banco_estado = _caminhos(caminho_banco_academico, caminho_banco_merito)

    for _ in range(tentativas_concorrentes):
        antigo = ler_estado_merito(banco_estado, perfil_id)
        leitura = ler_historico_merito_sqlite(
            banco_acad, recorde_persistido=antigo.recorde if antigo else 0
        )
        _validar_leitura(leitura, antigo)
        arquivo_preexistia = banco_estado.exists()
        try:
            with closing(_abrir_conexao(banco_estado, criar=True)) as cx:
                # Serialize com outros escritores do mérito, sem ocupar bloqueio
                # durante a leitura potencialmente longa do banco acadêmico.
                cx.execute("BEGIN IMMEDIATE")
                if arquivo_preexistia or cx.execute("PRAGMA application_id").fetchone()[0] != 0:
                    _verificar_sqlite(cx)
                else:
                    _criar_sqlite(cx)
                atual = _ler_estado_conexao(cx, perfil_id)
                # Origin/revision changed after the snapshot was read: do not
                # write a potentially stale result; restart from current record.
                if (atual.revisao if atual else None) != (antigo.revisao if antigo else None):
                    cx.rollback()
                    continue
                _validar_leitura(leitura, atual)
                mudou = _gravar_estado(cx, perfil_id, leitura, atual)
                estado = _ler_estado_conexao(cx, perfil_id)
                if estado is None:
                    raise PersistenciaMeritoInvalida("Estado não foi gravado")
                cx.commit()
                return ApuracaoPersistidaM10(
                    resultado=replace(leitura.resultado, gravacao_realizada=True),
                    estado=estado,
                    mudou=mudou,
                    linhas_lidas=leitura.diagnostico.linhas_totais,
                )
        except sqlite3.DatabaseError as exc:
            raise PersistenciaMeritoInvalida("Falha de transação do banco lateral de mérito") from exc
    raise ConflitoRevisaoMerito("Persistência concorrente mudou durante apuração")


@dataclass(frozen=True)
class BackupMeritoM10:
    arquivo: str
    bytes: int
    sha256: str


def criar_backup_merito(
    caminho_banco_merito: str | Path, destino_backup: str | Path,
) -> BackupMeritoM10:
    """Copia transacional de um banco de mérito íntegro; nunca sobrescreve arquivo.

    Usa sqlite3.backup para gerar snapshot consistente mesmo com o banco aberto.
    Um arquivo existente (inclusive acadêmico) nunca é escrito por este método.
    Restauração deve ser conduzida em clone e aprovada, não é automática.
    """
    origem = Path(caminho_banco_merito).expanduser().resolve(strict=True)
    destino = Path(destino_backup).expanduser().resolve(strict=False)
    if origem == destino or destino.exists():
        raise PersistenciaMeritoInvalida("Destino de backup já existe ou é a própria origem")
    if not origem.is_file():
        raise PersistenciaMeritoInvalida("Arquivo de mérito inexistente")
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        with closing(_abrir_conexao(origem, criar=False)) as cx:
            _verificar_sqlite(cx)
            with closing(sqlite3.connect(destino)) as copia:
                cx.backup(copia)
        with closing(_abrir_conexao(destino, criar=False)) as validacao:
            _verificar_sqlite(validacao)
    except (sqlite3.DatabaseError, PersistenciaMeritoInvalida) as exc:
        if destino.is_file():
            destino.unlink()
        raise PersistenciaMeritoInvalida("Falha no backup transacional de mérito") from exc
    return BackupMeritoM10(
        arquivo=str(destino), bytes=destino.stat().st_size,
        sha256=sha256(destino.read_bytes()).hexdigest(),
    )
