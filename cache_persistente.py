"""Cache persistente revisionado para cálculos caros do VighnaStudy.

O cache é derivado e descartável. A validade não depende de TTL: depende de
revisões incrementadas automaticamente por triggers nas tabelas-fonte.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import closing
from datetime import date, datetime
from typing import Any, Callable, Iterable

CACHE_SCHEMA_VERSION = 3
TRIGGER_SCHEMA_VERSION = 3

DOMINIOS_PADRAO = ("academico", "catalogo", "configuracao", "foco")

# Cache de processo: evita até a desserialização JSON quando o mesmo snapshot é
# solicitado repetidamente na mesma abertura.
_MEMORIA: dict[tuple[str, int | None], tuple[tuple[tuple[str, int], ...], Any]] = {}
_LOCK = threading.RLock()
_SCHEMA_READY: set[str] = set()


def _identificador_banco(conexao) -> str:
    try:
        linhas = conexao.execute("PRAGMA database_list").fetchall()
        principal = next((linha for linha in linhas if str(linha[1]) == "main"), None)
        caminho = str(principal[2] if principal else "")
        if caminho:
            return caminho
    except Exception:
        pass
    return f"memory:{id(conexao)}"


def _tabela_existe(conexao, tabela: str) -> bool:
    return (
        conexao.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            (str(tabela),),
        ).fetchone()
        is not None
    )


def _nome_trigger(tabela: str, evento: str, dominio: str) -> str:
    seguro = "".join(ch if ch.isalnum() else "_" for ch in tabela)
    return f"trg_cache_rev_{dominio}_{seguro}_{evento.lower()}"


def garantir_schema_cache_persistente(conexao) -> None:
    """Cria o cache derivado e os gatilhos de revisão.

    Os gatilhos são versionados e recriados apenas quando sua definição muda.
    Um sinal de suspensão permite que ``criar_banco()`` execute migrações
    idempotentes sem invalidar o warm cache a cada abertura.
    """
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS cache_revisoes (
            dominio TEXT PRIMARY KEY,
            revisao INTEGER NOT NULL DEFAULT 0,
            atualizado_em TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
        """
    )
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS cache_controle (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            suspenso INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conexao.execute(
        "INSERT OR IGNORE INTO cache_controle (id, suspenso) VALUES (1, 0)"
    )
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS cache_meta (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        )
        """
    )
    for dominio in DOMINIOS_PADRAO:
        conexao.execute(
            "INSERT OR IGNORE INTO cache_revisoes (dominio, revisao) VALUES (?, 0)",
            (dominio,),
        )

    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS cache_persistente (
            chave TEXT NOT NULL,
            concurso_id INTEGER,
            schema_cache INTEGER NOT NULL,
            revisoes_json TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            gerado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            PRIMARY KEY (chave, concurso_id)
        )
        """
    )
    conexao.execute(
        "CREATE INDEX IF NOT EXISTS idx_cache_persistente_gerado ON cache_persistente(gerado_em)"
    )

    grupos = {
        "academico": (
            "tentativas_questoes",
            "revisoes",
            "sessoes_questoes",
            "tentativa_microtemas",
            "microtema_estado",
            "banco_erros_pendentes",
            "efetividade_sessoes",
            "efetividade_topicos_sessao",
            "simulados",
        ),
        "catalogo": (
            "questoes",
            "alternativas_questoes",
            "disciplinas",
            "topicos",
            "disciplina_concurso_inclusao",
            "topico_concurso_importancia",
            "controle_topico",
            "capitulos_topico",
            "capitulo_concurso_config",
            "microtemas",
            "questao_microtemas",
            "alternativa_microtemas",
            "questao_versoes",
            "questao_versao_microtemas",
        ),
        "configuracao": (
            "configuracoes",
            "concursos",
        ),
        "foco": (
            "sessoes_foco",
            "foco_questoes",
        ),
    }

    versao_linha = conexao.execute(
        "SELECT valor FROM cache_meta WHERE chave = 'trigger_schema_version'"
    ).fetchone()
    versao_atual = int(versao_linha[0]) if versao_linha else 0
    if versao_atual != TRIGGER_SCHEMA_VERSION:
        for dominio, tabelas in grupos.items():
            for tabela in tabelas:
                if not _tabela_existe(conexao, tabela):
                    continue
                for evento in ("INSERT", "UPDATE", "DELETE"):
                    trigger = _nome_trigger(tabela, evento, dominio)
                    conexao.execute(f"DROP TRIGGER IF EXISTS {trigger}")
                    conexao.execute(
                        f"""
                        CREATE TRIGGER {trigger}
                        AFTER {evento} ON {tabela}
                        WHEN COALESCE(
                            (SELECT suspenso FROM cache_controle WHERE id = 1),
                            0
                        ) = 0
                        BEGIN
                            UPDATE cache_revisoes
                            SET revisao = revisao + 1,
                                atualizado_em = datetime('now','localtime')
                            WHERE dominio = '{dominio}';
                        END
                        """
                    )
        conexao.execute(
            """
            INSERT INTO cache_meta (chave, valor)
            VALUES ('trigger_schema_version', ?)
            ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor
            """,
            (str(TRIGGER_SCHEMA_VERSION),),
        )
    _SCHEMA_READY.add(_identificador_banco(conexao))


def suspender_revisoes_cache(conexao, suspender: bool) -> bool:
    """Suspende apenas os contadores durante migrações idempotentes."""
    try:
        conexao.execute(
            "UPDATE cache_controle SET suspenso = ? WHERE id = 1",
            (1 if suspender else 0,),
        )
        return True
    except sqlite3.OperationalError:
        return False


def _garantir_schema_rapido(conexao) -> None:
    identificador = _identificador_banco(conexao)
    if identificador in _SCHEMA_READY:
        return
    garantir_schema_cache_persistente(conexao)


def obter_revisoes(conexao, dominios: Iterable[str]) -> tuple[tuple[str, int], ...]:
    dominios = tuple(dict.fromkeys(str(d) for d in dominios))
    if not dominios:
        return ()
    marcadores = ",".join("?" for _ in dominios)
    linhas = conexao.execute(
        f"SELECT dominio, revisao FROM cache_revisoes WHERE dominio IN ({marcadores})",
        dominios,
    ).fetchall()
    mapa = {str(d): int(r or 0) for d, r in linhas}
    return tuple((d, mapa.get(d, 0)) for d in dominios)


_TIPO = "__vighna_cache_type__"


def _empacotar(valor: Any) -> Any:
    if isinstance(valor, dict):
        if all(isinstance(chave, str) and chave != _TIPO for chave in valor):
            return {chave: _empacotar(item) for chave, item in valor.items()}
        return {
            _TIPO: "dict",
            "items": [[_empacotar(chave), _empacotar(item)] for chave, item in valor.items()],
        }
    if isinstance(valor, tuple):
        return {_TIPO: "tuple", "items": [_empacotar(item) for item in valor]}
    if isinstance(valor, set):
        return {_TIPO: "set", "items": [_empacotar(item) for item in valor]}
    if isinstance(valor, datetime):
        return {_TIPO: "datetime", "value": valor.isoformat()}
    if isinstance(valor, date):
        return {_TIPO: "date", "value": valor.isoformat()}
    if isinstance(valor, list):
        return [_empacotar(item) for item in valor]
    if valor is None or isinstance(valor, (str, int, float, bool)):
        return valor
    raise TypeError(f"tipo não serializável no cache: {type(valor).__name__}")


def _desempacotar(valor: Any) -> Any:
    if isinstance(valor, list):
        return [_desempacotar(item) for item in valor]
    if not isinstance(valor, dict):
        return valor
    tipo = valor.get(_TIPO)
    if tipo == "dict":
        return {
            _desempacotar(chave): _desempacotar(item)
            for chave, item in valor.get("items", [])
        }
    if tipo == "tuple":
        return tuple(_desempacotar(item) for item in valor.get("items", []))
    if tipo == "set":
        return set(_desempacotar(item) for item in valor.get("items", []))
    if tipo == "datetime":
        return datetime.fromisoformat(str(valor.get("value") or ""))
    if tipo == "date":
        return date.fromisoformat(str(valor.get("value") or ""))
    return {chave: _desempacotar(item) for chave, item in valor.items()}


def _revisoes_json(revisoes: tuple[tuple[str, int], ...]) -> str:
    return json.dumps(dict(revisoes), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _mem_key(chave: str, concurso_id: int | None) -> tuple[str, int | None]:
    return str(chave), (None if concurso_id is None else int(concurso_id))


def invalidar_memoria(prefixo: str | None = None) -> None:
    with _LOCK:
        if prefixo is None:
            _MEMORIA.clear()
            return
        prefixo = str(prefixo)
        for chave in list(_MEMORIA):
            if chave[0].startswith(prefixo):
                _MEMORIA.pop(chave, None)


def obter_ou_calcular(
    connection_factory: Callable,
    chave: str,
    carregador: Callable[[], Any],
    *,
    concurso_id: int | None = None,
    dominios: Iterable[str] = ("academico", "catalogo", "configuracao"),
    persistir: bool = True,
) -> Any:
    """Retorna cache válido ou calcula/persiste o payload.

    A leitura das revisões custa apenas algumas linhas e torna o cache seguro
    mesmo quando os dados mudam por caminhos diferentes da interface.
    """
    chave = str(chave)
    cid = None if concurso_id is None else int(concurso_id)
    with closing(connection_factory()) as conexao:
        _garantir_schema_rapido(conexao)
        revisoes = obter_revisoes(conexao, dominios)

        mk = _mem_key(chave, cid)
        with _LOCK:
            memoria = _MEMORIA.get(mk)
            if memoria is not None and memoria[0] == revisoes:
                return memoria[1]

        if persistir:
            linha = conexao.execute(
                """
                SELECT schema_cache, revisoes_json, payload_json
                FROM cache_persistente
                WHERE chave = ? AND concurso_id IS ?
                """,
                (chave, cid),
            ).fetchone()
            if linha is not None:
                schema_cache, revisoes_salvas, payload_json = linha
                if (
                    int(schema_cache or 0) == CACHE_SCHEMA_VERSION
                    and str(revisoes_salvas or "") == _revisoes_json(revisoes)
                ):
                    try:
                        valor = _desempacotar(json.loads(payload_json))
                    except (TypeError, ValueError, json.JSONDecodeError):
                        valor = None
                    else:
                        with _LOCK:
                            _MEMORIA[mk] = (revisoes, valor)
                        return valor

    valor = carregador()

    # Só cacheamos objetos serializáveis. Uma falha de serialização nunca pode
    # impedir o cálculo normal.
    try:
        payload_json = json.dumps(
            _empacotar(valor),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError):
        return valor

    with closing(connection_factory()) as conexao, conexao:
        _garantir_schema_rapido(conexao)
        revisoes_depois = obter_revisoes(conexao, dominios)
        # Se a base mudou enquanto o cálculo ocorria, não persista um snapshot
        # potencialmente obsoleto. O valor ainda serve para a chamada atual.
        if revisoes_depois == revisoes:
            if persistir:
                conexao.execute(
                    """
                    INSERT INTO cache_persistente (
                        chave, concurso_id, schema_cache, revisoes_json,
                        payload_json, gerado_em
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(chave, concurso_id) DO UPDATE SET
                        schema_cache = excluded.schema_cache,
                        revisoes_json = excluded.revisoes_json,
                        payload_json = excluded.payload_json,
                        gerado_em = excluded.gerado_em
                    """,
                    (
                        chave,
                        cid,
                        CACHE_SCHEMA_VERSION,
                        _revisoes_json(revisoes_depois),
                        payload_json,
                        datetime.now().isoformat(timespec="seconds"),
                    ),
                )
            with _LOCK:
                _MEMORIA[_mem_key(chave, cid)] = (revisoes_depois, valor)
    return valor


def estatisticas_cache(connection_factory: Callable) -> dict[str, Any]:
    with closing(connection_factory()) as conexao:
        _garantir_schema_rapido(conexao)
        total = int(conexao.execute("SELECT COUNT(*) FROM cache_persistente").fetchone()[0])
        revisoes = dict(obter_revisoes(conexao, DOMINIOS_PADRAO))
    with _LOCK:
        memoria = len(_MEMORIA)
    return {"persistentes": total, "memoria": memoria, "revisoes": revisoes}
