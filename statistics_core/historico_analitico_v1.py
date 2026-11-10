"""VighnaStudy - núcleo experimental de histórico de tentativas, somente leitura.

Checkpoint de desenvolvimento; NÃO é instalável por si só.

O serviço não cria, atualiza ou exclui registros. Mantém em separado:
- janela selecionada (7/30/90/180/365 dias, personalizado, completo);
- acumulado de todos os anos disponíveis no banco;
- comparação com janela imediatamente anterior de duração igual;
- agrupamentos por mês e disciplina, preservando perfis distintos.

Fonte da verdade: tentativas_questoes, não o estado atual do enunciado.
É um componente analítico adicional, não substitui as métricas de domínio
ou efetividade calculadas por outros serviços do VighnaStudy.
"""
from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

PERIODOS = (7, 30, 90, 180, 365)


@dataclass(frozen=True)
class Janela:
    nome: str
    inicio: Optional[date]
    fim: Optional[date]

    @property
    def duracao(self) -> Optional[int]:
        if self.inicio is None or self.fim is None:
            return None
        return (self.fim - self.inicio).days + 1


def janela_periodo(periodo: int | str = 30, *, hoje: Optional[date] = None,
                   inicio: Optional[str | date] = None,
                   fim: Optional[str | date] = None) -> Janela:
    """Períodos fechados no fuso local fornecido pelo aplicativo."""
    if hoje is None:
        hoje = datetime.now().astimezone().date()
    if not isinstance(hoje, date):
        raise TypeError('hoje precisa ser date')
    if periodo == 'completo':
        return Janela('completo', None, None)
    if periodo == 'personalizado':
        def _date(valor: Optional[str | date]) -> date:
            if isinstance(valor, datetime):
                raise TypeError('Use uma data sem hora')
            if isinstance(valor, date):
                return valor
            if not isinstance(valor, str):
                raise ValueError('Data inicial e final são obrigatórias')
            return date.fromisoformat(valor)
        a, b = _date(inicio), _date(fim)
        if a > b:
            raise ValueError('Data inicial após a data final')
        if b > hoje:
            raise ValueError('Período futuro não é permitido na análise histórica')
        return Janela('personalizado', a, b)
    if isinstance(periodo, bool):
        raise ValueError('Período inválido')
    try:
        dias = int(periodo)
    except (ValueError, TypeError) as exc:
        raise ValueError('Período inválido') from exc
    if dias not in PERIODOS:
        raise ValueError('Período deve ser 7, 30, 90, 180, 365 ou completo')
    return Janela(f'{dias} dias', hoje - timedelta(days=dias - 1), hoje)


def janela_anterior(janela: Janela) -> Optional[Janela]:
    """A comparação não se aplica a todo o histórico."""
    if janela.duracao is None:
        return None
    fim_anterior = janela.inicio - timedelta(days=1)
    inicio_anterior = fim_anterior - timedelta(days=janela.duracao - 1)
    return Janela('anterior', inicio_anterior, fim_anterior)


def _colunas(con: sqlite3.Connection, tabela: str) -> set[str]:
    assert tabela in {'tentativas_questoes', 'questoes', 'topicos'}
    return {item[1] for item in con.execute(f'PRAGMA table_info({tabela})')}


def _filtro_base(con: sqlite3.Connection, concurso_id: int,
                 disciplina_id: Optional[int], topico_id: Optional[int]):
    if not isinstance(concurso_id, int) or isinstance(concurso_id, bool) or concurso_id < 1:
        raise ValueError('Perfil do concurso inválido')
    cols = _colunas(con, 'tentativas_questoes')
    if not {'concurso_id', 'respondida_em', 'correta', 'questao_id'} <= cols:
        raise RuntimeError('Schema de tentativas incompatível com histórico analítico')

    # LEFT JOIN preserva respostas antigas mesmo se a questão foi removida.
    qcols = _colunas(con, 'questoes')
    tcols = _colunas(con, 'topicos')
    joins = ''
    if {'id', 'topico_id'} <= qcols:
        joins += ' LEFT JOIN questoes q ON q.id = tq.questao_id '
        if {'id', 'disciplina_id'} <= tcols:
            joins += ' LEFT JOIN topicos t ON t.id = q.topico_id '
    topico_partes = []
    disciplina_partes = []
    if 'topico_id_snapshot' in cols:
        topico_partes.append('tq.topico_id_snapshot')
    if ' q ' in joins:
        topico_partes.append('q.topico_id')
    if 'disciplina_id_snapshot' in cols:
        disciplina_partes.append('tq.disciplina_id_snapshot')
    if ' t ' in joins:
        disciplina_partes.append('t.disciplina_id')

    conditions = ['tq.concurso_id = ?']
    params = [concurso_id]
    if disciplina_id is not None:
        if not disciplina_partes:
            raise RuntimeError('Dados de disciplina indisponíveis nesse esquema')
        conditions.append(f"COALESCE({', '.join(disciplina_partes)}) = ?" if len(disciplina_partes) > 1 else disciplina_partes[0] + ' = ?')
        params.append(int(disciplina_id))
    if topico_id is not None:
        if not topico_partes:
            raise RuntimeError('Dados de tópico indisponíveis nesse esquema')
        conditions.append(f"COALESCE({', '.join(topico_partes)}) = ?" if len(topico_partes) > 1 else topico_partes[0] + ' = ?')
        params.append(int(topico_id))
    return joins, conditions, params, cols, disciplina_partes


def _where_janela(conditions: list[str], params: list, janela: Janela):
    if janela.inicio is not None:
        # Datas ISO; o limite superior exclusivo preserva todos os horários.
        conditions.append('tq.respondida_em >= ?')
        params.append(janela.inicio.isoformat())
        conditions.append('tq.respondida_em < ?')
        params.append((janela.fim + timedelta(days=1)).isoformat())


def _resumo(con: sqlite3.Connection, concurso_id: int, janela: Janela,
            disciplina_id: Optional[int], topico_id: Optional[int]) -> dict:
    joins, cond, params, cols, _ = _filtro_base(con, concurso_id, disciplina_id, topico_id)
    _where_janela(cond, params, janela)
    id_questao = ('COALESCE(tq.questao_id_snapshot, tq.questao_id)'
                  if 'questao_id_snapshot' in cols else 'tq.questao_id')
    duvida = 'SUM(CASE WHEN tq.marcada_duvida = 1 THEN 1 ELSE 0 END)' if 'marcada_duvida' in cols else '0'
    sql = f"""SELECT COUNT(*) AS tentativas,
             COALESCE(SUM(CASE WHEN tq.correta IN (0, 1) THEN 1 ELSE 0 END), 0) AS respondidas,
             COALESCE(SUM(CASE WHEN tq.correta = 1 THEN 1 ELSE 0 END), 0) AS acertos,
             COALESCE(SUM(CASE WHEN tq.correta = 0 THEN 1 ELSE 0 END), 0) AS erros,
             COALESCE(SUM(CASE WHEN tq.correta IS NULL THEN 1 ELSE 0 END), 0) AS puladas,
             COALESCE({duvida}, 0) AS duvidas,
             COUNT(DISTINCT CASE WHEN tq.correta IN (0, 1) THEN {id_questao} ELSE NULL END) AS questoes_unicas,
             COUNT(DISTINCT CASE WHEN tq.correta IN (0, 1) THEN substr(tq.respondida_em, 1, 10) ELSE NULL END) AS dias_ativos,
             MIN(tq.respondida_em) AS primeira_tentativa,
             MAX(tq.respondida_em) AS ultima_tentativa
             FROM tentativas_questoes tq {joins}
             WHERE {' AND '.join(cond)}"""
    row = con.execute(sql, params).fetchone()
    keys = ['tentativas','respondidas','acertos','erros','puladas','duvidas','questoes_unicas','dias_ativos','primeira_tentativa','ultima_tentativa']
    res = dict(zip(keys, row))
    res['desempenho'] = (round(100.0 * res['acertos'] / res['respondidas'], 2)
                          if res['respondidas'] else None)
    return res


def analisar_tentativas(con: sqlite3.Connection, concurso_id: int,
                       periodo: int | str = 30, *, hoje: Optional[date] = None,
                       inicio: Optional[str | date] = None,
                       fim: Optional[str | date] = None,
                       disciplina_id: Optional[int] = None,
                       topico_id: Optional[int] = None) -> dict:
    """Retorna métricas separadas, sem modificar a conexão ou o banco.

    O acumulado utiliza TODOS os registros acessíveis do perfil; alterações
    e exclusões explícitas já feitas na fonte não podem ser desfeitas aqui.
    """
    janela = janela_periodo(periodo, hoje=hoje, inicio=inicio, fim=fim)
    atual = _resumo(con, concurso_id, janela, disciplina_id, topico_id)
    acumulado = _resumo(con, concurso_id, Janela('completo', None, None), disciplina_id, topico_id)
    comparavel = janela_anterior(janela)
    anterior = (_resumo(con, concurso_id, comparavel, disciplina_id, topico_id)
                if comparavel else None)
    delta = (round(atual['desempenho'] - anterior['desempenho'], 2)
             if anterior and atual['desempenho'] is not None
             and anterior['desempenho'] is not None else None)
    return {
        'janela': {'nome': janela.nome,
                   'inicio': janela.inicio.isoformat() if janela.inicio else None,
                   'fim': janela.fim.isoformat() if janela.fim else None},
        'atual': atual,
        'acumulado': acumulado,
        'anterior': anterior,
        'delta_pontos_percentuais': delta,
        'filtros': {'concurso_id': concurso_id, 'disciplina_id': disciplina_id,
                    'topico_id': topico_id},
        'fonte': 'tentativas_questoes',
        'somente_leitura': True,
    }


def evolucao_mensal(con: sqlite3.Connection, concurso_id: int,
                   disciplina_id: Optional[int] = None,
                   topico_id: Optional[int] = None) -> list[dict]:
    """Histórico completo por mês, em ordem cronológica, sem data de corte."""
    joins, cond, params, _cols, _parts = _filtro_base(con, concurso_id, disciplina_id, topico_id)
    cond.append('tq.correta IN (0, 1)')
    cond.append("tq.respondida_em GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-*'")
    rows = con.execute(f"""SELECT substr(tq.respondida_em, 1, 7) mes,
                         COUNT(*) respondidas,
                         SUM(CASE WHEN tq.correta = 1 THEN 1 ELSE 0 END) acertos
                         FROM tentativas_questoes tq {joins}
                         WHERE {' AND '.join(cond)}
                         GROUP BY mes ORDER BY mes""", params).fetchall()
    return [{'mes': mes, 'respondidas': n, 'acertos': ac,
             'desempenho': round(100 * ac / n, 2) if n else None}
            for mes, n, ac in rows]


def abrir_banco_somente_leitura(caminho: str | Path) -> sqlite3.Connection:
    """Abre SQLite em modo read-only; útil para auditorias de segurança."""
    p = Path(caminho).expanduser().resolve(strict=True)
    return sqlite3.connect(p.as_uri() + '?mode=ro', uri=True)
