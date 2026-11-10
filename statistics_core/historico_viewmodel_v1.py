"""Adaptador puro (sem Qt) dos dados históricos para Relatórios/Estatísticas V2.

Apenas prepara um contrato para a futura interface. Não altera arquivos,
não acessa o banco, não cria gráficos e não substitui serviços de domínio.
"""
from __future__ import annotations


def _fonte(multifonte: dict, chave: str, escopo: str) -> dict | None:
    bloco = multifonte.get('fontes', {}).get(chave)
    if not isinstance(bloco, dict) or bloco.get('status') != 'disponivel':
        return None
    return bloco.get(escopo)


def montar_modelo_relatorio(tentativas: dict, multifonte: dict, mensal_tentativas: list[dict], *, legado_global: dict | None = None) -> dict:
    """Monta DTO para interface; evita a falsa soma de fontes sobrepostas.

    Fonte 'foco_global' não é atribuído a perfil de concurso, porque na
    referência atual sessoes_foco não contém coluna concurso_id.
    """
    id_a=tentativas.get('filtros',{}).get('concurso_id')
    id_b=multifonte.get('concurso_id')
    if id_a is None or id_a != id_b:
        raise ValueError('Perfis históricos incompatíveis')
    jan_a=tentativas.get('janela',{})
    jan_b=multifonte.get('periodo',{})
    if (jan_a.get('inicio'),jan_a.get('fim')) != (jan_b.get('inicio'),jan_b.get('fim')):
        raise ValueError('Janelas de análise incompatíveis')
    t_atual=tentativas['atual']
    t_acum=tentativas['acumulado']
    rev=_fonte(multifonte,'revisoes','atual')
    sim=_fonte(multifonte,'simulados','atual')
    foco=_fonte(multifonte,'foco_global','atual')
    eff=_fonte(multifonte,'efetividade','atual')
    nao_ligadas=_fonte(multifonte,'revisoes_sem_perfil','acumulado')

    alertas=[
        'Os valores do período são diferentes do acumulado desde o início.',
        'Questões contabilizadas em revisões/simulados também podem existir em tentativas; nunca somá-las diretamente.',
        'Sessões de foco são globais nesta versão: sem vinculação segura a concurso.',
        'A ausência de medições antigas de efetividade não significa desempenho zero.',
        'Simulados e medições arquivados já estão incluídos nos totais de suas fontes; não somar outra vez.',
    ]
    for codigo,bloco in multifonte.get('fontes',{}).items():
        if bloco.get('status') == 'indisponivel':
            alertas.append('Fonte indisponível: '+codigo+' — '+str(bloco.get('motivo','desconhecido')))
    if nao_ligadas and nao_ligadas['sem_linhagem']:
        alertas.append(f"{nao_ligadas['sem_linhagem']} revisões históricas não vinculadas a um perfil (sem atribuição automática).")

    return {
        'perfil': id_a,
        'periodo': dict(jan_a),
        'indicadores_do_perfil': {
            'tentativas': {
                'periodo': t_atual['respondidas'],
                'acumulado': t_acum['respondidas'],
                'acertos_periodo': t_atual['acertos'],
                'taxa_periodo_pct': t_atual['desempenho'],
                'taxa_acumulada_pct': t_acum['desempenho'],
                'variacao_pp': tentativas['delta_pontos_percentuais'],
            },
            'revisoes': {
                'periodo': rev['revisoes'] if rev else None,
                'acumulado': (_fonte(multifonte,'revisoes','acumulado') or {}).get('revisoes'),
                'taxa_declarada_periodo_pct': rev['taxa_declarada_pct'] if rev else None,
            },
            'simulados': {
                'periodo': sim['simulados_concluidos_com_resposta'] if sim else None,
                'acumulado': (_fonte(multifonte,'simulados','acumulado') or {}).get('simulados_concluidos_com_resposta'),
                'taxa_periodo_pct': sim['desempenho_ponderado_pct'] if sim else None,
                'arquivados_no_periodo': sim['arquivados_concluidos_com_resposta'] if sim else None,
                'arquivados_no_acumulado': (_fonte(multifonte,'simulados','acumulado') or {}).get('arquivados_concluidos_com_resposta'),
            },
            'efetividade': {
                'periodo': eff['sessoes_medidas'] if eff else None,
                'acumulado': (_fonte(multifonte,'efetividade','acumulado') or {}).get('sessoes_medidas'),
                'delta_dominio_medio': eff['delta_dominio_medio'] if eff else None,
                'pares_medidos': eff['pares_dominio'] if eff else None,
                'arquivadas_no_periodo': eff['arquivadas'] if eff else None,
                'arquivadas_no_acumulado': (_fonte(multifonte,'efetividade','acumulado') or {}).get('arquivadas'),
            },
        },
        'indicadores_globais_nao_atribuiveis': {
            'foco': {
                'tempo_periodo_segundos': foco['tempo_efetivo_segundos'] if foco else None,
                'tempo_acumulado_segundos': (_fonte(multifonte,'foco_global','acumulado') or {}).get('tempo_efetivo_segundos'),
                'status': 'global_sem_perfil' if foco else 'indisponivel',
            },
            'revisoes_sem_perfil': nao_ligadas['sem_linhagem'] if nao_ligadas else None,
            'revisoes_importadas_excel': legado_global if legado_global and legado_global.get('status') == 'disponivel' else None,
        },
        'series_mensais_separadas': {
            'tentativas': mensal_tentativas,
            'revisoes': (multifonte.get('fontes',{}).get('revisoes') or {}).get('mensal_completo'),
            'simulados': (multifonte.get('fontes',{}).get('simulados') or {}).get('mensal_completo'),
            'foco_global': (multifonte.get('fontes',{}).get('foco_global') or {}).get('mensal_completo'),
            'efetividade': (multifonte.get('fontes',{}).get('efetividade') or {}).get('mensal_completo'),
        },
        'avisos':alertas,
        'pronto_para_integração_visual':False,
    }
