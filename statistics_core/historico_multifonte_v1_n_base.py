"""VighnaStudy — análise histórica multifonte V2 (etapa B, NÃO INSTALAR).

Somente leitura; estatísticas por fonte sem somar revisões, foco e simulados
às tentativas, pois representam fenômenos distintos / fontes sobrepostas.

Contrato preliminar derivado do banco.py de referência R01/P01. Antes de
integrar à interface, confrontar com banco.py/estudos.db do clone Windows.
"""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta

from .historico_analitico_v1 import Janela, janela_anterior, janela_periodo


class EsquemaHistoricoIncompativel(RuntimeError):
    """A fonte existe, mas não oferece colunas mínimas seguras para cálculo."""


def _campos(con: sqlite3.Connection, tabela: str) -> set[str]:
    # Nomes de tabelas são apenas constantes internas, nunca entrada do usuário.
    if tabela not in {
        'revisoes', 'sessoes_foco', 'simulados', 'sessoes_questoes',
        'tentativas_questoes', 'efetividade_sessoes',
        'historico_v2_revisoes_arquivadas', 'historico_v2_vinculos_excluidos',
    }:
        raise ValueError('Fonte não permitida')
    return {c[1] for c in con.execute(f'PRAGMA table_info("{tabela}")')}


def _exigir(con: sqlite3.Connection, tabela: str, campos: set[str]) -> None:
    encontrados = _campos(con, tabela)
    if not encontrados:
        raise EsquemaHistoricoIncompativel(f'Tabela {tabela} ausente')
    faltantes = campos - encontrados
    if faltantes:
        raise EsquemaHistoricoIncompativel(
            f'Tabela {tabela} incompleta: {", ".join(sorted(faltantes))}'
        )


def _perfil(concurso_id: int) -> int:
    if isinstance(concurso_id, bool) or not isinstance(concurso_id, int) or concurso_id < 1:
        raise ValueError('Identificador do perfil inválido')
    return concurso_id


def _janela_sql(coluna: str, janela: Janela) -> tuple[str, list[str]]:
    # Esta função aceita apenas expressões constantes internas.
    if coluna not in ('r.data', 'sf.inicio', 's.criado_em', 'e.criado_em'):
        raise ValueError('Expressão temporal não autorizada')
    if janela.inicio is None:
        return '', []
    return (f' AND {coluna} >= ? AND {coluna} < ?', [
        janela.inicio.isoformat(),
        (janela.fim + timedelta(days=1)).isoformat(),
    ])


def _fonte_revisoes_historicas(con: sqlite3.Connection) -> str:
    """Consulta revisões ativas + legitimamente arquivadas por exclusão administrativa.

    Compatibilidade com bases antigas: quando a tabela de arquivo não existe,
    lê somente revisões originais. O NOT EXISTS evita dupla contagem por ID.
    """
    campos = {'id','concurso_id','topico_id','data','questoes','acertos'}
    _exigir(con,'revisoes',campos)
    origem_ativa = "COALESCE(origem, 'manual')" if 'origem' in _campos(con,'revisoes') else "'manual'"
    if _campos(con,'historico_v2_vinculos_excluidos'):
        principal = ("SELECT r.id,COALESCE(r.concurso_id, "
            "(SELECT v.concurso_id FROM historico_v2_vinculos_excluidos v "
            "WHERE v.tipo='revisao' AND v.registro_id=r.id)) AS concurso_id, "
            "r.topico_id,r.data,r.questoes,r.acertos," +
            origem_ativa.replace('origem','r.origem') + " AS origem FROM revisoes r")
    else:
        principal = ("SELECT id,concurso_id,topico_id,data,questoes,acertos,"
                     + origem_ativa + " AS origem FROM revisoes")
    if not _campos(con,'historico_v2_revisoes_arquivadas'):
        return '(' + principal + ') r'
    _exigir(con,'historico_v2_revisoes_arquivadas',{
        'revisao_id','concurso_id','topico_id','data','questoes','acertos','origem'
    })
    arquivo = ("SELECT a.revisao_id, a.concurso_id, a.topico_id, a.data, "
               "a.questoes,a.acertos,COALESCE(a.origem,'manual') AS origem "
               "FROM historico_v2_revisoes_arquivadas a "
               "WHERE NOT EXISTS (SELECT 1 FROM revisoes r0 WHERE r0.id=a.revisao_id)")
    return '(' + principal + ' UNION ALL ' + arquivo + ') r'


def _metricas_revisoes(con: sqlite3.Connection, concurso_id: int, janela: Janela) -> dict:
    _exigir(con, 'revisoes', {'id', 'concurso_id', 'topico_id', 'data', 'questoes', 'acertos', 'origem'})
    clause, params = _janela_sql('r.data', janela)
    c = con.execute(f'''
        SELECT COUNT(*),
               COALESCE(SUM(CASE WHEN lower(coalesce(r.origem, 'manual')) = 'manual' THEN 1 ELSE 0 END), 0),
               COALESCE(SUM(CASE WHEN lower(coalesce(r.origem, 'manual')) <> 'manual' THEN 1 ELSE 0 END), 0),
               COALESCE(SUM(CASE WHEN r.questoes >= 0 THEN r.questoes ELSE 0 END),0),
               COALESCE(SUM(CASE WHEN r.acertos >= 0 THEN r.acertos ELSE 0 END),0),
               COUNT(DISTINCT r.topico_id),
               MIN(r.data), MAX(r.data)
        FROM {_fonte_revisoes_historicas(con)} WHERE r.concurso_id = ?{clause}
    ''', [concurso_id, *params]).fetchone()
    total, manuais, automaticas, questoes, acertos, topicos, primeira, ultima = c
    # Percentual de revisões é baseado em contadores agregados próprios,
    # não em tentativas_questoes; não somar com taxa de acerto de tentativas.
    return {
        'revisoes': int(total), 'manuais': int(manuais), 'outras_origens': int(automaticas),
        'questoes_declaradas': int(questoes), 'acertos_declarados': int(acertos),
        'taxa_declarada_pct': round(100 * acertos / questoes, 2) if questoes else None,
        'topicos_distintos': int(topicos), 'primeira': primeira, 'ultima': ultima,
        'unidade': 'registros_de_revisao',
    }


def _metricas_foco_global(con: sqlite3.Connection, janela: Janela) -> dict:
    _exigir(con, 'sessoes_foco', {'id', 'inicio', 'duracao_efetiva', 'concluida'})
    clause, params = _janela_sql('sf.inicio', janela)
    linha = con.execute(f'''
        SELECT COUNT(*),
               COALESCE(SUM(CASE WHEN sf.duracao_efetiva > 0 THEN 1 ELSE 0 END),0),
               COALESCE(SUM(CASE WHEN sf.concluida = 1 THEN 1 ELSE 0 END),0),
               COALESCE(SUM(CASE WHEN sf.duracao_efetiva > 0 THEN sf.duracao_efetiva ELSE 0 END),0),
               COUNT(DISTINCT CASE WHEN sf.duracao_efetiva > 0 THEN substr(sf.inicio,1,10) END),
               MIN(sf.inicio), MAX(sf.inicio)
        FROM sessoes_foco sf WHERE 1=1{clause}
    ''', params).fetchone()
    total, com_tempo, concluidas, segundos, dias, primeira, ultima = linha
    return {
        'sessoes_registradas': int(total), 'sessoes_com_tempo': int(com_tempo),
        'sessoes_concluidas': int(concluidas), 'tempo_efetivo_segundos': int(segundos),
        'tempo_efetivo_horas': round(int(segundos) / 3600, 2),
        'dias_ativos': int(dias), 'primeira': primeira, 'ultima': ultima,
        'escopo': 'global_sem_linhagem_de_concurso',
        'aviso': 'sessoes_foco nesta versão não registra concurso_id; não atribuir ao perfil',
    }


def _metricas_simulados(con: sqlite3.Connection, concurso_id: int, janela: Janela) -> dict:
    _exigir(con, 'simulados', {'id','sessao_id','concurso_id','criado_em'})
    _exigir(con, 'sessoes_questoes', {'id','encerrado_em'})
    _exigir(con, 'tentativas_questoes', {'sessao_id','correta'})
    clause, params = _janela_sql('s.criado_em', janela)
    # Contar um simulado por sessão, independentemente de quantas tentativas.
    # LEFT JOIN mantém simulados sem respostas na contagem de cadastrados.
    rows = con.execute(f'''
        SELECT s.id, s.criado_em,
               CASE WHEN sq.encerrado_em IS NOT NULL THEN 1 ELSE 0 END encerrado,
               COALESCE(SUM(CASE WHEN tq.correta IN (0,1) THEN 1 ELSE 0 END),0) respondidas,
               COALESCE(SUM(CASE WHEN tq.correta = 1 THEN 1 ELSE 0 END),0) acertos
        FROM simulados s
        JOIN sessoes_questoes sq ON sq.id = s.sessao_id
        LEFT JOIN tentativas_questoes tq ON tq.sessao_id = s.sessao_id
        WHERE s.concurso_id = ?{clause}
        GROUP BY s.id, s.criado_em, sq.encerrado_em
    ''', [concurso_id, *params]).fetchall()
    concluidos = [(a, b, d, e) for a,b,c,d,e in rows if c and d > 0]
    respondidas = sum(r[2] for r in concluidos)
    acertos = sum(r[3] for r in concluidos)
    percentuais = [round(100 * r[3] / r[2], 2) for r in concluidos]
    ultimo = max(concluidos, key=lambda r:(r[1],r[0])) if concluidos else None
    return {
        'simulados_cadastrados': len(rows),
        'simulados_concluidos_com_resposta': len(concluidos),
        'respondidas_em_simulados': respondidas,
        'acertos_em_simulados': acertos,
        'desempenho_ponderado_pct': round(100 * acertos / respondidas, 2) if respondidas else None,
        'media_taxa_por_simulado_pct': round(sum(percentuais)/len(percentuais),2) if percentuais else None,
        'melhor_pct': max(percentuais) if percentuais else None,
        'ultimo_pct': round(100*ultimo[3]/ultimo[2],2) if ultimo else None,
        'ultimo_em': ultimo[1] if ultimo else None,
        'unidade': 'sessoes_de_simulado',
        'nao_somar_a_tentativas': True,
    }


def _metricas_efetividade(con: sqlite3.Connection, concurso_id: int, janela: Janela) -> dict:
    _exigir(con, 'efetividade_sessoes', {
        'sessao_id','concurso_id','criado_em','concluida','respostas','acertos',
        'dominio_medio_antes','dominio_medio_depois',
        'cobertura_media_antes','cobertura_media_depois',
    })
    clause, params = _janela_sql('e.criado_em', janela)
    # Médias de pares completos: não transformar NULL em zero.
    row = con.execute(f'''
        SELECT COUNT(*),
               COALESCE(SUM(CASE WHEN e.concluida = 1 THEN 1 ELSE 0 END),0),
               COALESCE(SUM(CASE WHEN e.respostas >= 0 THEN e.respostas ELSE 0 END),0),
               COALESCE(SUM(CASE WHEN e.acertos >= 0 THEN e.acertos ELSE 0 END),0),
               COUNT(CASE WHEN e.dominio_medio_antes IS NOT NULL THEN 1 END)
        FROM efetividade_sessoes e WHERE e.concurso_id = ?{clause}
    ''', [concurso_id,*params]).fetchone()
    total, concluidas, respostas, acertos, _ = row
    deltas = con.execute(f'''
        SELECT AVG(CASE WHEN e.dominio_medio_antes IS NOT NULL AND e.dominio_medio_depois IS NOT NULL
                     THEN e.dominio_medio_depois - e.dominio_medio_antes END),
               COUNT(CASE WHEN e.dominio_medio_antes IS NOT NULL AND e.dominio_medio_depois IS NOT NULL THEN 1 END),
               AVG(CASE WHEN e.cobertura_media_antes IS NOT NULL AND e.cobertura_media_depois IS NOT NULL
                     THEN e.cobertura_media_depois - e.cobertura_media_antes END),
               COUNT(CASE WHEN e.cobertura_media_antes IS NOT NULL AND e.cobertura_media_depois IS NOT NULL THEN 1 END)
        FROM efetividade_sessoes e WHERE e.concurso_id = ?{clause}
    ''', [concurso_id,*params]).fetchone()
    dominio, n_dom, cobertura, n_cob = deltas
    return {
        'sessoes_medidas': int(total), 'concluidas': int(concluidas),
        'respostas_reportadas': int(respostas), 'acertos_reportados': int(acertos),
        'delta_dominio_medio': round(dominio, 3) if dominio is not None else None,
        'pares_dominio': int(n_dom),
        'delta_cobertura_media': round(cobertura, 3) if cobertura is not None else None,
        'pares_cobertura': int(n_cob),
        'unidade': 'medicoes_por_sessao',
        'nao_somar_a_tentativas': True,
        'aviso': 'Medições disponíveis apenas a partir da implementação do recurso',
    }


def _revisoes_sem_perfil(con: sqlite3.Connection, janela: Janela) -> dict:
    _exigir(con, 'revisoes', {'concurso_id','data'})
    clause, params = _janela_sql('r.data', janela)
    row=con.execute(f'SELECT COUNT(*), MIN(r.data), MAX(r.data) FROM {_fonte_revisoes_historicas(con)} WHERE r.concurso_id IS NULL{clause}',params).fetchone()
    return {'sem_linhagem':int(row[0]), 'primeira':row[1], 'ultima':row[2],
            'aviso':'Não atribuídas automaticamente a nenhum concurso'}


def _agrupar(con: sqlite3.Connection, concurso_id: int, fonte: str) -> list[dict]:
    """Série mensal completa, isolada por fonte; sem inventar meses vazios."""
    spec = {
        'revisoes': (None, 'r.data', 'r.concurso_id', '1'),
        'foco_global': ('sessoes_foco sf', 'sf.inicio', None, '1'),
        'simulados': ('simulados s JOIN sessoes_questoes sq ON sq.id=s.sessao_id',
                      's.criado_em', 's.concurso_id', 'CASE WHEN sq.encerrado_em IS NOT NULL THEN 1 ELSE 0 END'),
        'efetividade': ('efetividade_sessoes e', 'e.criado_em', 'e.concurso_id', '1'),
    }
    if fonte not in spec:
        raise ValueError('Fonte inválida')
    tabela, data, perfil, cond = spec[fonte]
    if fonte == 'revisoes':
        tabela = _fonte_revisoes_historicas(con)
    where = ('WHERE '+perfil+' = ?' if perfil else '')
    params = [concurso_id] if perfil else []
    rows = con.execute(f'''
        SELECT substr({data},1,7) mes,COUNT(*) total
        FROM {tabela} {where}{' AND ' if where else ' WHERE '}{cond}
        AND substr({data},1,7) GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
        GROUP BY mes ORDER BY mes
    ''',params).fetchall()
    return [{'mes': mes,'registros':int(n)} for mes,n in rows]


def analisar_fontes_historicas(con: sqlite3.Connection, concurso_id: int,
                              periodo: int | str = 30, *, hoje: Optional[date] = None,
                              inicio: Optional[str | date] = None,
                              fim: Optional[str | date] = None) -> dict:
    """Resumo independente por fonte com janelas atual/anterior/acumulado.

    Se uma fonte estiver ausente, informar indisponibilidade em vez de zero.
    A tabela de foco é global na referência; nunca atribuí-la ao perfil.
    """
    concurso_id = _perfil(concurso_id)
    janela=janela_periodo(periodo,hoje=hoje,inicio=inicio,fim=fim)
    anterior=janela_anterior(janela)
    completo=Janela('completo',None,None)
    funcoes={
        'revisoes': lambda j:_metricas_revisoes(con,concurso_id,j),
        'foco_global': lambda j:_metricas_foco_global(con,j),
        'simulados': lambda j:_metricas_simulados(con,concurso_id,j),
        'efetividade':lambda j:_metricas_efetividade(con,concurso_id,j),
        'revisoes_sem_perfil':lambda j:_revisoes_sem_perfil(con,j),
    }
    fontes={}
    for nome,func in funcoes.items():
        try:
            atual=func(janela)
            acumulado=func(completo)
            anterior_resultado=func(anterior) if anterior else None
            serie= _agrupar(con,concurso_id,nome) if nome!='revisoes_sem_perfil' else None
            fontes[nome]={'status':'disponivel','atual':atual,
                'acumulado':acumulado,'anterior':anterior_resultado,
                'mensal_completo':serie}
        except EsquemaHistoricoIncompativel as exc:
            fontes[nome]={'status':'indisponivel','motivo':str(exc)}
    return {'concurso_id':concurso_id,'periodo':{
        'nome':janela.nome,'inicio':janela.inicio.isoformat() if janela.inicio else None,
        'fim':janela.fim.isoformat() if janela.fim else None},
        'fontes':fontes, 'somente_leitura':True,
        'politica':'Sem expiração automática no serviço analítico; não interfere na retenção das tabelas fonte',
        'escopo_foco':'global, não atribuído a concurso',
        'limite':'Dependente de registros existentes; exclusões anteriores não são recuperadas'}
