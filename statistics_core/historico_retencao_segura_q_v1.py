"""VighnaStudy / Historico V2 - Etapa Q: migracao defensiva do esquema N+O.

DESENVOLVIMENTO: NAO EXECUTAR NO BANCO ORIGINAL ANTES DA HOMOLOGACAO WINDOWS.

Corrige uma lacuna da migracao anterior: SQLite ignora CREATE TRIGGER IF NOT
EXISTS quando ja existe objeto homonimo, mesmo que tenha SQL incorreto. Esta
camada compara o esquema REAL instalado com um exemplar limpo gerado pela
mesma versao do instalador e com as colunas reais do banco de origem.

Nenhum arquivo e aberto por esta funcao; opera somente na conexao explicitamente
fornecida, dentro de SAVEPOINT. A implantacao final deve usar backup independente.
"""
from __future__ import annotations

import re
import sqlite3
from contextlib import closing
from .historico_retencao_real_o_v1 import garantir_schema_preservacao as _instalar_o

_TABELAS_NATIVAS = (
    'concursos', 'disciplinas', 'topicos', 'revisoes', 'tentativas_questoes',
    'controle_topico', 'sessoes_questoes', 'simulados', 'efetividade_sessoes',
)
_PREFIXOS = ('historico_v2_', 'idx_hist_v2_', 'trg_hist_v2_')
_SAVEPOINT = 'vighna_historico_v2_q_integridade'


def _identificador(nome: str) -> str:
    if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', nome):
        raise RuntimeError('Identificador SQLite inesperado: migracao bloqueada')
    return '"' + nome + '"'


def _colunas(con: sqlite3.Connection, tabela: str) -> list[tuple[str, str]]:
    q = list(con.execute(f'PRAGMA table_info({_identificador(tabela)})'))
    if not q:
        raise RuntimeError('Tabela nativa ausente ou sem colunas: ' + tabela)
    return [(str(r[1]), str(r[2])) for r in q]


def _normalizado(sql: str | None) -> str:
    # Preserva tokens, nomes e literais; normaliza SOMENTE espacos entre tokens.
    # Definicoes logicamente equivalentes com outra grafia podem ser bloqueadas;
    # em casos de conflito preferimos revisao manual a um aceite falso.
    return re.sub(r'\s+', ' ', (sql or '').strip())


def _objetos_protegidos(con: sqlite3.Connection) -> dict[str, tuple[str, str]]:
    return {
        str(n): (str(tipo), _normalizado(sql))
        for tipo, n, sql in con.execute(
            "SELECT type,name,sql FROM sqlite_master "
            "WHERE type IN ('table','index','trigger') AND sql IS NOT NULL"
        )
        if str(n).startswith(_PREFIXOS)
    }


def _exemplar(con: sqlite3.Connection) -> dict[str, tuple[str, str]]:
    """Gera em memoria o esquema aprovado para as colunas REAIS de revisoes.

    N constroi gatilhos a partir das colunas disponiveis em `revisoes`;
    portanto, nao e correto fixar um hash de SQL valido so para uma revisao
    antiga do banco. O exemplar nao recebe dados nem gatilhos do usuario.
    """
    with closing(sqlite3.connect(':memory:')) as replica:
        for tabela in _TABELAS_NATIVAS:
            colunas = _colunas(con, tabela)
            # O tipo e irrelevante para montagem dos gatilhos; usar TEXT evita
            # ter de executar CREATE TABLE ou CHECK fornecido pelo banco.
            nomes = ', '.join(_identificador(c) + ' TEXT' for c, _ in colunas)
            replica.execute(f'CREATE TABLE {_identificador(tabela)} ({nomes})')
        replica.commit()
        replica.execute('PRAGMA foreign_keys=ON')
        _instalar_o(replica)
        esperado = _objetos_protegidos(replica)
        if not esperado or not any(k.startswith('trg_hist_v2_') for k in esperado):
            raise RuntimeError('Exemplar incompleto: gatilhos nao encontrados')
        return esperado


def _conferir(atual: dict[str, tuple[str, str]],
             esperado: dict[str, tuple[str, str]], *, permitir_vazio: bool) -> None:
    if not atual and permitir_vazio:
        return
    faltando = set(esperado) - set(atual)
    excedentes = set(atual) - set(esperado)
    divergentes = {n for n in set(atual) & set(esperado)
                   if atual[n] != esperado[n]}
    if faltando or excedentes or divergentes:
        detalhes = ', '.join(f'{titulo}={len(nomes)}' for titulo, nomes in (
            ('faltantes', faltando), ('inesperados', excedentes),
            ('divergentes', divergentes)) if nomes)
        raise RuntimeError('Historico V2: esquema parcial ou alterado; '
                           'nenhum gatilho sera aceito sem auditoria: ' + detalhes)


def garantir_schema_preservacao(con: sqlite3.Connection) -> dict:
    """Instala ou revalida a camada O atomicamente, sem commit/rollback externo.

    Aborta em caso de objetos faltantes, SQL divergente, versao parcial ou
    gatilhos homonimos que o SQLite ignoraria com IF NOT EXISTS.
    """
    if con.execute('PRAGMA foreign_keys').fetchone()[0] != 1:
        raise RuntimeError('Historico V2: PRAGMA foreign_keys=ON e obrigatorio')
    esperado = _exemplar(con)
    anterior = _objetos_protegidos(con)
    _conferir(anterior, esperado, permitir_vazio=True)

    con.execute('SAVEPOINT ' + _SAVEPOINT)
    try:
        resultado = _instalar_o(con)
        _conferir(_objetos_protegidos(con), esperado, permitir_vazio=False)
    except Exception:
        con.execute('ROLLBACK TO SAVEPOINT ' + _SAVEPOINT)
        con.execute('RELEASE SAVEPOINT ' + _SAVEPOINT)
        raise
    con.execute('RELEASE SAVEPOINT ' + _SAVEPOINT)
    return {
        **resultado,
        'validacao_sql_objetos': 'completa',
        'objetos_conferidos': len(esperado),
        'resultado': 'revalidado' if anterior else 'instalado',
        'esquema_idempotente': True,
    }
