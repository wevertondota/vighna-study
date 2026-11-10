"""VighnaStudy M09 — leitura global somente leitura, alinhada a banco.py.

DESENVOLVIMENTO OFFLINE — NÃO conectar automaticamente à instalação atual.
Fonte de auditoria: banco.py extraído de arquivo do projeto datado de 2026-10-18.
Uma validação em clone com o banco e a versão efetivamente instalados ainda é
necessária antes de habilitar a publicação na interface do VighnaStudy.

`mode=ro` + `PRAGMA query_only` + transação de leitura; nenhuma tabela é criada.
"""
from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Final
import sqlite3

from .contrato_historico_merito import (
    CertidaoDeCompletude,
    MapeamentoHistorico,
    ResultadoIntegracao,
    conferir_e_calcular,
)

ORIGEM_EXCLUIDA: Final[str] = "__concurso_origem_excluido__"
REQUISITOS: Final[dict[str, frozenset[str]]] = {
    "concursos": frozenset({"id"}),
    "tentativas_questoes": frozenset({"id", "sessao_id", "concurso_id", "respondida_em", "correta"}),
    "sessoes_questoes": frozenset({"id", "origem", "modo", "encerrado_em", "concluida"}),
    "simulados": frozenset({"sessao_id"}),
}
MAPEAMENTO: Final[MapeamentoHistorico] = MapeamentoHistorico(
    tentativa_id="tentativa_id", status="status", data="respondida_em",
    concurso_id="concurso_id", academica="academica", publicada="publicada",
)


class FonteMeritoInvalida(ValueError):
    """O histórico não pode ser certificado; manter insígnia oculta."""


@dataclass(frozen=True)
class DiagnosticoLeituraM09:
    linhas_totais: int
    tentativas_publicadas: int
    tentativas_retidas_simulado: int
    registros_concurso_excluido: int
    origem_fonte: str
    esquema_validado: bool
    consulta_somente_leitura: bool = True


@dataclass(frozen=True)
class LeituraMeritoM09:
    resultado: ResultadoIntegracao
    diagnostico: DiagnosticoLeituraM09


def _validar_esquema(conexao: sqlite3.Connection) -> None:
    for tabela, colunas in REQUISITOS.items():
        linha = conexao.execute(
            "SELECT type FROM sqlite_master WHERE name=?", (tabela,)
        ).fetchone()
        if linha is None or linha[0] != "table":
            raise FonteMeritoInvalida(f"Tabela real ausente ou não é tabela: {tabela}")
        metadados = conexao.execute(f"PRAGMA table_info({tabela})").fetchall()
        presentes = {linha[1] for linha in metadados}
        ausentes = colunas - presentes
        if ausentes:
            raise FonteMeritoInvalida(f"Esquema incompatível em {tabela}: {sorted(ausentes)}")
    pk = conexao.execute("PRAGMA table_info(tentativas_questoes)").fetchall()
    if next((x[5] for x in pk if x[1] == "id"), 0) != 1:
        raise FonteMeritoInvalida("Identificador da tentativa não é chave primária")


def _id_inteiro(valor, campo: str, *, nulo=False) -> int | None:
    if valor is None and nulo:
        return None
    if type(valor) is not int or valor < 1:
        raise FonteMeritoInvalida(f"{campo} precisa ser inteiro positivo estável")
    return valor


def _status(valor) -> str:
    if valor is None:
        return "Pulada"
    if type(valor) is not int or valor not in (0, 1):
        raise FonteMeritoInvalida(f"Flag 'correta' inválida: {valor!r}")
    return "Correta" if valor == 1 else "Errada"


def _simulado(origem, modo, tem_registro: bool) -> bool:
    return (tem_registro
            or str(origem or "").strip().casefold().startswith("simulad")
            or "simulad" in str(modo or "").casefold())


def ler_historico_merito_sqlite(
    caminho_banco: str | Path, *, recorde_persistido: int = 0
) -> LeituraMeritoM09:
    """Lê TODAS as tentativas de TODOS os concursos de um snapshot SQLite.

    Não usa filtros por concurso, data, período ou LIMIT. Segura resultados de
    simulados abertos ou não concluídos. Orfandade de sessão é ambígua e falha
    fechado; orfandade de concurso, possível após exclusão, recebe marcador
    distinto e continua sendo contada. Tentativas são identificadas por ID,
    não por questão, com ordenação numérica desempate para datas iguais.

    Este leitor não cria estruturas, não persiste recorde e não publica estado.
    """
    caminho = Path(caminho_banco).expanduser().resolve(strict=True)
    if not caminho.is_file():
        raise FonteMeritoInvalida("Caminho não aponta para arquivo SQLite")
    if type(recorde_persistido) is not int or recorde_persistido < 0:
        raise FonteMeritoInvalida("Recorde persistido inválido")
    origem = "sqlite-ro-m09:" + sha256(str(caminho).encode("utf-8")).hexdigest()[:20]
    uri = caminho.as_uri() + "?mode=ro"
    # Não usar immutable=1: bancos com WAL precisam respeitar a visão transacional.
    with closing(sqlite3.connect(uri, uri=True, timeout=5.0)) as cx:
        cx.execute("PRAGMA query_only=ON")
        try:
            cx.execute("BEGIN")
            _validar_esquema(cx)
            concursos = cx.execute("SELECT id FROM concursos ORDER BY id").fetchall()
            ids_concursos: set[int] = set()
            for (valor,) in concursos:
                ids_concursos.add(_id_inteiro(valor, "concurso.id"))
            if not ids_concursos:
                raise FonteMeritoInvalida("Nenhum concurso registrado: universo não verificável")
            total = cx.execute("SELECT COUNT(*) FROM tentativas_questoes").fetchone()[0]
            if type(total) is not int or total < 0:
                raise FonteMeritoInvalida("Contagem de tentativas inválida")
            linhas = cx.execute("""
                SELECT tq.id, tq.concurso_id, tq.sessao_id,
                       tq.respondida_em, tq.correta,
                       sq.id AS sessao_encontrada,
                       sq.origem, sq.modo, sq.encerrado_em, sq.concluida,
                       si.sessao_id AS simulado_encontrado
                FROM tentativas_questoes tq
                LEFT JOIN sessoes_questoes sq ON sq.id = tq.sessao_id
                LEFT JOIN simulados si ON si.sessao_id = tq.sessao_id
                ORDER BY tq.id ASC
            """).fetchall()
            if len(linhas) != total:
                raise FonteMeritoInvalida("Snapshot incompleto: quantidade não confere")
            normalizadas = []
            orphan_concurso = retidas = publicadas = 0
            for linha in linhas:
                (ident, concurso_id, sessao_id, data, correta,
                 encontrada, origem_sessao, modo, encerrado, concluida, simulado_id) = linha
                ident = _id_inteiro(ident, "tentativa.id")
                curso = _id_inteiro(concurso_id, "tentativa.concurso_id", nulo=True)
                if curso is None:
                    curso_str = ORIGEM_EXCLUIDA
                    orphan_concurso += 1
                elif curso not in ids_concursos:
                    raise FonteMeritoInvalida("Tentativa aponta concurso inexistente: banco inconsistente")
                else:
                    curso_str = str(curso)
                # A sessão pode ter sido excluída historicamente. Não adivinhar
                # se o evento ainda pertencia a um simulado sem feedback.
                if sessao_id is None or encontrada is None:
                    raise FonteMeritoInvalida(
                        "Tentativa sem sessão comprovável; revisar migração/orfandade antes de publicar"
                    )
                _id_inteiro(sessao_id, "tentativa.sessao_id")
                _id_inteiro(encontrada, "sessao.id")
                if type(concluida) is not int or concluida not in (0, 1):
                    raise FonteMeritoInvalida("Indicador de conclusão de sessão inválido")
                if not isinstance(data, str) or not data.strip():
                    raise FonteMeritoInvalida("Tentativa sem horário válido")
                publicada = not _simulado(origem_sessao, modo, simulado_id is not None) or (
                    encerrado is not None and concluida == 1
                )
                retidas += int(not publicada)
                publicadas += int(publicada)
                normalizadas.append({
                    "tentativa_id": f"{ident:020d}",  # conserva ordem numérica no empate de segundo
                    "status": _status(correta),
                    "respondida_em": data,
                    "concurso_id": curso_str,
                    "academica": True,  # tabela acadêmica exclusiva, conforme banco.py auditado
                    "publicada": bool(publicada),
                })
            universo = {str(i) for i in ids_concursos}
            if orphan_concurso:
                universo.add(ORIGEM_EXCLUIDA)
            ids = tuple(sorted(universo))
            certidao = CertidaoDeCompletude(
                todos_concursos=True, sem_limite_de_linhas=True,
                desde_primeira_tentativa=True, identificadores_estaveis=True,
                resultados_academicos_e_publicacao_auditados=True,
                concurso_ids_esperados=ids, concurso_ids_consultados=ids,
                linhas_exportadas=total, origem_auditada=origem,
            )
            resultado = conferir_e_calcular(
                normalizadas, mapeamento=MAPEAMENTO, certidao=certidao,
                recorde_persistido=recorde_persistido,
            )
            cx.execute("ROLLBACK")
        except BaseException:
            if cx.in_transaction:
                cx.execute("ROLLBACK")
            raise
    return LeituraMeritoM09(resultado, DiagnosticoLeituraM09(
        linhas_totais=total, tentativas_publicadas=publicadas,
        tentativas_retidas_simulado=retidas,
        registros_concurso_excluido=orphan_concurso,
        origem_fonte=origem, esquema_validado=True,
    ))
