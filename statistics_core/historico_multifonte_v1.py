"""Histórico V2 P — visão coerente de simulados/efetividade ativos e arquivados.

Consulta exclusivamente leitura. Chave de deduplicação: simulado_id ou
sessao_id. Registros ativos prevalecem; arquivo O é incluído apenas quando
sua chave já não existe na tabela ativa. Respeita datas reais de criação e
vínculo de concurso confirmado, sem somar essas respostas a tentativas.
"""
from __future__ import annotations

from datetime import date
import sqlite3

from .historico_analitico_v1 import Janela, janela_periodo, janela_anterior
from .historico_multifonte_v1_n_base import (
    EsquemaHistoricoIncompativel, _campos, _exigir, _perfil, _janela_sql,
    _metricas_revisoes, _metricas_foco_global, _revisoes_sem_perfil,
    _agrupar as _agrupar_anteriores,
)

_ARQUIVO_SIM = 'historico_v2_simulados_arquivados'
_ARQUIVO_EF = 'historico_v2_efetividade_arquivada'


def _arquivo(con: sqlite3.Connection, nome: str, campos: set[str]) -> bool:
    # Não mascarar arquivo incompleto como "sem registros": seria subcontagem.
    presentes = {str(r[1]) for r in con.execute(f'PRAGMA table_info("{nome}")')}
    if not presentes:
        return False
    if campos - presentes:
        raise EsquemaHistoricoIncompativel(
            'Arquivo incompleto '+nome+': '+', '.join(sorted(campos - presentes)))
    return True


def _fonte_simulados(con: sqlite3.Connection) -> str:
    _exigir(con,'simulados',{'id','sessao_id','concurso_id','criado_em'})
    _exigir(con,'sessoes_questoes',{'id','encerrado_em'})
    _exigir(con,'tentativas_questoes',{'sessao_id','correta'})
    # A linhagem recupera concursos apagados com SET NULL, mas só quando
    # existe prova escrita previamente pelo gatilho O.
    linhagem = _arquivo(con, 'historico_v2_linhagem_sessoes',
                       {'tipo','registro_id','concurso_id'})
    perfil = ("COALESCE(s.concurso_id,(SELECT l.concurso_id FROM "
              "historico_v2_linhagem_sessoes l WHERE l.tipo='simulado' "
              "AND l.registro_id=s.id))" if linhagem else 's.concurso_id')
    principal = f'''SELECT s.id AS registro_id, {perfil} AS concurso_id,
         s.criado_em AS criado_em,
         CASE WHEN sq.encerrado_em IS NOT NULL THEN 1 ELSE 0 END AS concluido,
         (SELECT COUNT(*) FROM tentativas_questoes t
          WHERE t.sessao_id=s.sessao_id AND t.correta IN (0,1)) AS respostas,
         (SELECT COUNT(*) FROM tentativas_questoes t
          WHERE t.sessao_id=s.sessao_id AND t.correta=1) AS acertos,
         0 AS arquivado
         FROM simulados s JOIN sessoes_questoes sq ON sq.id=s.sessao_id'''
    # Só consultar arquivo instalado pelo esquema O; em versões pré-O, ler ativos.
    if not _arquivo(con, _ARQUIVO_SIM,
                    {'simulado_id','concurso_id','criado_em','encerrado_em','respondidas','acertos'}):
        return principal
    historico = '''SELECT a.simulado_id AS registro_id, a.concurso_id,
       a.criado_em, CASE WHEN a.encerrado_em IS NOT NULL THEN 1 ELSE 0 END,
       CASE WHEN a.respondidas>=0 THEN a.respondidas ELSE 0 END,
       CASE WHEN a.respondidas>0 AND a.acertos>=0 THEN MIN(a.acertos,a.respondidas) ELSE 0 END,
       1 AS arquivado
       FROM historico_v2_simulados_arquivados a
       WHERE NOT EXISTS (SELECT 1 FROM simulados s WHERE s.id=a.simulado_id)'''
    return principal + '\nUNION ALL\n' + historico


def _fonte_efetividade(con: sqlite3.Connection) -> str:
    required = {'sessao_id','concurso_id','criado_em','concluida','respostas','acertos',
        'dominio_medio_antes','dominio_medio_depois','cobertura_media_antes','cobertura_media_depois'}
    _exigir(con, 'efetividade_sessoes', required)
    linhagem = _arquivo(con,'historico_v2_linhagem_sessoes',
                       {'tipo','registro_id','concurso_id'})
    perfil = ("COALESCE(e.concurso_id,(SELECT l.concurso_id FROM "
              "historico_v2_linhagem_sessoes l WHERE l.tipo='efetividade' "
              "AND l.registro_id=e.sessao_id))" if linhagem else 'e.concurso_id')
    principal = f'''SELECT e.sessao_id AS registro_id, {perfil} AS concurso_id,
        e.criado_em, e.concluida, e.respostas, e.acertos,
        e.dominio_medio_antes, e.dominio_medio_depois,
        e.cobertura_media_antes, e.cobertura_media_depois,
        0 AS arquivado FROM efetividade_sessoes e'''
    if not _arquivo(con, _ARQUIVO_EF,required):
        return principal
    arquivo = '''SELECT a.sessao_id, a.concurso_id, a.criado_em,
        a.concluida,a.respostas,a.acertos,a.dominio_medio_antes,
        a.dominio_medio_depois,a.cobertura_media_antes,a.cobertura_media_depois,
        1 AS arquivado FROM historico_v2_efetividade_arquivada a
        WHERE NOT EXISTS (SELECT 1 FROM efetividade_sessoes e
                          WHERE e.sessao_id=a.sessao_id)'''
    return principal + '\nUNION ALL\n' + arquivo


def _metricas_simulados(con: sqlite3.Connection, concurso_id: int, janela: Janela) -> dict:
    origem = _fonte_simulados(con)
    restricao, parametros = _janela_sql('s.criado_em', janela)
    # Uma linha por simulado cadastrado, conclusão apenas com respostas.
    dados = con.execute(f'''WITH s AS ({origem})
        SELECT COUNT(*),
               COALESCE(SUM(CASE WHEN s.concluido=1 AND s.respostas>0 THEN 1 ELSE 0 END),0),
               COALESCE(SUM(CASE WHEN s.concluido=1 AND s.respostas>0 THEN s.respostas ELSE 0 END),0),
               COALESCE(SUM(CASE WHEN s.concluido=1 AND s.respostas>0 THEN s.acertos ELSE 0 END),0),
               COALESCE(SUM(CASE WHEN s.arquivado=1 THEN 1 ELSE 0 END),0),
               COALESCE(SUM(CASE WHEN s.arquivado=1 AND s.concluido=1 AND s.respostas>0 THEN 1 ELSE 0 END),0)
        FROM s WHERE s.concurso_id=?{restricao}''',[concurso_id,*parametros]).fetchone()
    total,concluidos,respostas,acertos,arquivados,concluidos_arq = map(int,dados)
    linhas = con.execute(f'''WITH s AS ({origem})
        SELECT s.registro_id,s.criado_em,s.respostas,s.acertos FROM s
        WHERE s.concurso_id=?{restricao} AND s.concluido=1 AND s.respostas>0
        ORDER BY s.criado_em DESC,s.registro_id DESC''',[concurso_id,*parametros]).fetchall()
    taxas = [100 * max(0,min(ac,resp))/resp for _,__,resp,ac in linhas]
    return {
        'simulados_cadastrados':total,
        'simulados_concluidos_com_resposta':concluidos,
        'respondidas_em_simulados':respostas,
        'acertos_em_simulados':acertos,
        'desempenho_ponderado_pct':round(100*acertos/respostas,2) if respostas else None,
        'media_taxa_por_simulado_pct':round(sum(taxas)/len(taxas),2) if taxas else None,
        'melhor_pct':round(max(taxas),2) if taxas else None,
        'ultimo_pct':round(taxas[0],2) if taxas else None,
        'ultimo_em':linhas[0][1] if linhas else None,
        'arquivados_cadastrados':arquivados,
        'arquivados_concluidos_com_resposta':concluidos_arq,
        'unidade':'sessoes_de_simulado',
        'nao_somar_a_tentativas':True,
    }


def _metricas_efetividade(con: sqlite3.Connection, concurso_id: int, janela: Janela) -> dict:
    origem=_fonte_efetividade(con)
    restricao,parametros = _janela_sql('e.criado_em',janela)
    row = con.execute(f'''WITH e AS ({origem})
        SELECT COUNT(*),
          COALESCE(SUM(CASE WHEN e.concluida=1 THEN 1 ELSE 0 END),0),
          COALESCE(SUM(CASE WHEN e.respostas>=0 THEN e.respostas ELSE 0 END),0),
          COALESCE(SUM(CASE WHEN e.acertos>=0 THEN e.acertos ELSE 0 END),0),
          AVG(CASE WHEN e.dominio_medio_antes IS NOT NULL AND e.dominio_medio_depois IS NOT NULL
               THEN e.dominio_medio_depois-e.dominio_medio_antes END),
          COUNT(CASE WHEN e.dominio_medio_antes IS NOT NULL AND e.dominio_medio_depois IS NOT NULL THEN 1 END),
          AVG(CASE WHEN e.cobertura_media_antes IS NOT NULL AND e.cobertura_media_depois IS NOT NULL
               THEN e.cobertura_media_depois-e.cobertura_media_antes END),
          COUNT(CASE WHEN e.cobertura_media_antes IS NOT NULL AND e.cobertura_media_depois IS NOT NULL THEN 1 END),
          COALESCE(SUM(CASE WHEN e.arquivado=1 THEN 1 ELSE 0 END),0)
        FROM e WHERE e.concurso_id=?{restricao}''',[concurso_id,*parametros]).fetchone()
    total,concluidos,respostas,acertos,dominio,n_dom,cobertura,n_cob,arquivados=row
    return {
        'sessoes_medidas':int(total),'concluidas':int(concluidos),
        'respostas_reportadas':int(respostas),'acertos_reportados':int(acertos),
        'delta_dominio_medio':round(dominio,3) if dominio is not None else None,
        'pares_dominio':int(n_dom),
        'delta_cobertura_media':round(cobertura,3) if cobertura is not None else None,
        'pares_cobertura':int(n_cob),
        'arquivadas':int(arquivados),
        'unidade':'medicoes_por_sessao','nao_somar_a_tentativas':True,
        'aviso':'Medições disponíveis apenas a partir da implementação do recurso',
    }


def _agrupar(con: sqlite3.Connection, concurso_id: int, fonte: str) -> list[dict]:
    if fonte not in ('simulados','efetividade'):
        return _agrupar_anteriores(con,concurso_id,fonte)
    sql = _fonte_simulados(con) if fonte=='simulados' else _fonte_efetividade(con)
    campo='s.concluido=1 AND s.respostas>0' if fonte=='simulados' else '1=1'
    rows=con.execute(f'''WITH s AS ({sql})
        SELECT substr(s.criado_em,1,7),COUNT(*) FROM s
        WHERE s.concurso_id=? AND {campo}
          AND substr(s.criado_em,1,7) GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
        GROUP BY substr(s.criado_em,1,7) ORDER BY substr(s.criado_em,1,7)''',[concurso_id]).fetchall()
    return [{'mes':mes,'registros':int(n)} for mes,n in rows]


def analisar_fontes_historicas(con:sqlite3.Connection,concurso_id:int,
                              periodo:int|str=30,*,hoje:date|None=None,
                              inicio:str|date|None=None,fim:str|date|None=None)->dict:
    concurso_id=_perfil(concurso_id)
    janela=janela_periodo(periodo,hoje=hoje,inicio=inicio,fim=fim)
    anterior=janela_anterior(janela)
    completo=Janela('completo',None,None)
    funcoes={
        'revisoes':lambda j:_metricas_revisoes(con,concurso_id,j),
        'foco_global':lambda j:_metricas_foco_global(con,j),
        'simulados':lambda j:_metricas_simulados(con,concurso_id,j),
        'efetividade':lambda j:_metricas_efetividade(con,concurso_id,j),
        'revisoes_sem_perfil':lambda j:_revisoes_sem_perfil(con,j),
    }
    fontes={}
    for nome, func in funcoes.items():
        try:
            atual=func(janela)
            acumulado=func(completo)
            prev=func(anterior) if anterior else None
            serie=_agrupar(con,concurso_id,nome) if nome!='revisoes_sem_perfil' else None
            fontes[nome]={'status':'disponivel','atual':atual,'acumulado':acumulado,
                         'anterior':prev,'mensal_completo':serie}
        except EsquemaHistoricoIncompativel as exc:
            fontes[nome]={'status':'indisponivel','motivo':str(exc)}
    return {'concurso_id':concurso_id,'periodo':{
       'nome':janela.nome,'inicio':janela.inicio.isoformat() if janela.inicio else None,
       'fim':janela.fim.isoformat() if janela.fim else None},
       'fontes':fontes,'somente_leitura':True,
       'politica':'Sem expiração automática no serviço analítico; não interfere na retenção das tabelas fonte',
       'escopo_foco':'global, não atribuído a concurso',
       'limite':'Depende dos registros existentes; exclusões anteriores não são recuperadas'}
