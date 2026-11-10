"""Consultas readonly do histórico importado e de arquivos de sessões (etapa O).

As revisões do Excel não têm uma data individual verificável no controle_topico;
portanto são apenas um saldo acumulado GLOBAL, fora das séries mensais e dos
contadores de revisões datadas. Nenhum campo é atribuído a concurso por inferência.
"""
from __future__ import annotations

import re
import sqlite3
from datetime import date, timedelta

_ALLOWED = {'controle_topico','historico_v2_controles_legados',
            'historico_v2_simulados_arquivados','historico_v2_efetividade_arquivada',
            'simulados','efetividade_sessoes'}


def _campos(con: sqlite3.Connection, nome: str) -> set[str]:
    if nome not in _ALLOWED:
        raise ValueError('Tabela não autorizada')
    return {str(r[1]) for r in con.execute(f'PRAGMA table_info("{nome}")')}


def consultar_legado_global(con: sqlite3.Connection) -> dict:
    """Saldos legados sem data/perfil, ativos + arquivados, uma vez por tópico.

    Somar ao número de revisões DATADAS do perfil seria enganoso. A soma é
    apresentada separada como legado importado declarado, nunca como sessão.
    """
    base = {'topico_id', 'revisoes_iniciais', 'percentual_inicial'}
    if not base.issubset(_campos(con, 'controle_topico')):
        return {'status':'indisponivel','motivo':'controle_topico incompatível'}
    ativos = con.execute('''SELECT COUNT(*), COALESCE(SUM(CASE
        WHEN revisoes_iniciais>0 THEN revisoes_iniciais ELSE 0 END),0),
        COALESCE(SUM(CASE WHEN revisoes_iniciais>0 THEN 1 ELSE 0 END),0)
        FROM controle_topico''').fetchone()
    arquivados = (0,0,0)
    if base.issubset(_campos(con,'historico_v2_controles_legados')):
        arquivados = con.execute('''SELECT COUNT(*), COALESCE(SUM(CASE
          WHEN a.revisoes_iniciais>0 THEN a.revisoes_iniciais ELSE 0 END),0),
          COALESCE(SUM(CASE WHEN a.revisoes_iniciais>0 THEN 1 ELSE 0 END),0)
          FROM historico_v2_controles_legados a
          WHERE NOT EXISTS (SELECT 1 FROM controle_topico c
            WHERE c.topico_id=a.topico_id)''').fetchone()
    return {
        'status':'disponivel',
        'escopo':'global_sem_concurso_comprovado',
        'tem_datas_individuais':False,
        'serie_mensal':None,
        'topicos_com_controle_ativos':int(ativos[0]),
        'topicos_com_controle_arquivados':int(arquivados[0]),
        'topicos_com_revisoes_importadas':int(ativos[2]+arquivados[2]),
        'revisoes_importadas_declaradas':int(ativos[1]+arquivados[1]),
        'aviso':'Contadores de revisões anteriores ao programa; sem datas por revisão nem atribuição automática ao concurso. Não somar a revisões datadas como se fossem sessões.',
    }


def _validar_periodo(inicio: str | None, fim: str | None) -> tuple[str | None,str | None]:
    if inicio is None and fim is None:
        return None,None
    if not (isinstance(inicio,str) and isinstance(fim,str)):
        raise ValueError('Informe início e fim juntos')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',inicio) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',fim):
        raise ValueError('Datas inválidas')
    a,b=date.fromisoformat(inicio),date.fromisoformat(fim)
    if a>b:raise ValueError('Início maior que fim')
    return a.isoformat(),(b+timedelta(days=1)).isoformat()


def consultar_sessoes_arquivadas(con: sqlite3.Connection, *, concurso_id: int,
                                inicio: str | None=None, fim: str | None=None) -> dict:
    """Métricas exclusivas do arquivo de exclusões, sem duplicar fontes ativas.

    Não atribui resultado a um simulado sem encerramento, mesmo que tenha
    tentativas. Dados negativos/corrompidos são ignorados nas somas.
    """
    if isinstance(concurso_id,bool) or not isinstance(concurso_id,int) or concurso_id<1:
        raise ValueError('Concurso inválido')
    inicio,limite = _validar_periodo(inicio,fim)
    sig = {'simulado_id','concurso_id','criado_em','encerrado_em','respondidas','acertos'}
    eff = {'sessao_id','concurso_id','criado_em','concluida','respostas','acertos'}
    if not sig.issubset(_campos(con,'historico_v2_simulados_arquivados')) or not eff.issubset(_campos(con,'historico_v2_efetividade_arquivada')):
        return {'status':'indisponivel','motivo':'Tabelas de arquivo O não encontradas'}
    filtros = (' AND a.criado_em >= ? AND a.criado_em < ?') if inicio is not None else ''
    params = [concurso_id] + ([inicio,limite] if inicio is not None else [])
    excl_sim = ('AND NOT EXISTS (SELECT 1 FROM simulados s WHERE s.id=a.simulado_id)' if _campos(con,'simulados') else '')
    excl_eff = ('AND NOT EXISTS (SELECT 1 FROM efetividade_sessoes e WHERE e.sessao_id=a.sessao_id)' if _campos(con,'efetividade_sessoes') else '')
    sim=con.execute(f'''SELECT COUNT(*),
        COALESCE(SUM(CASE WHEN a.encerrado_em IS NOT NULL AND a.respondidas>0 THEN 1 ELSE 0 END),0),
        COALESCE(SUM(CASE WHEN a.encerrado_em IS NOT NULL AND a.respondidas>0 THEN a.respondidas ELSE 0 END),0),
        COALESCE(SUM(CASE WHEN a.encerrado_em IS NOT NULL AND a.respondidas>0 AND a.acertos>=0 THEN min(a.acertos,a.respondidas) ELSE 0 END),0)
        FROM historico_v2_simulados_arquivados a WHERE a.concurso_id=? {filtros} {excl_sim}''',params).fetchone()
    efet=con.execute(f'''SELECT COUNT(*),
        COALESCE(SUM(CASE WHEN a.concluida=1 THEN 1 ELSE 0 END),0),
        COALESCE(SUM(CASE WHEN a.respostas>=0 THEN a.respostas ELSE 0 END),0),
        COALESCE(SUM(CASE WHEN a.acertos>=0 THEN a.acertos ELSE 0 END),0)
        FROM historico_v2_efetividade_arquivada a WHERE a.concurso_id=? {filtros} {excl_eff}''',params).fetchone()
    return {'status':'disponivel','escopo':'perfil_comprovado',
        'simulados_arquivados':int(sim[0]),'simulados_concluidos':int(sim[1]),
        'simulados_respondidas':int(sim[2]),'simulados_acertos':int(sim[3]),
        'efetividade_arquivada':int(efet[0]),'efetividade_concluida':int(efet[1]),
        'efetividade_respostas':int(efet[2]),'efetividade_acertos':int(efet[3]),
        'aviso':'Contagens de arquivo separadas do painel legado. Somar apenas depois de validar a ausência de duplicações na visão unificada.'}
