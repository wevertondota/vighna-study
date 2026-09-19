"""Adaptador da aba Historico para a camada temporal central.

Historico descreve atividade cronologica. Comparacoes inferenciais, tendencia
oficial e evolucao por escopo pertencem a aba Tendencias.
"""

from __future__ import annotations

from datetime import date

import banco


def obter_evolucao_historica(concurso_id=None, dias=30):
    if concurso_id is None:
        concurso_id = banco.obter_concurso_ativo()[0]
    concurso_id = int(concurso_id)
    temporal = banco.obter_analise_temporal(concurso_id, dias=dias)
    atual = temporal["current_metrics"]
    anterior = temporal["previous_metrics"]
    foco = temporal["global_focus"]

    serie = [
        {
            "data": item["date"],
            "questoes": item["attempts"],
            "acertos": item["correct"],
            "desempenho": item["accuracy_rate"],
            "questoes_unicas": item["unique_questions"],
            "sessoes": item["sessions"],
            "revisoes": item["qualified_reviews"],
            "foco_segundos": item["focus_seconds_global"],
            "foco_minutos": round(item["focus_seconds_global"] / 60.0, 1),
        }
        for item in temporal["daily_series"]
    ]

    resumo = {
        "questoes": atual["attempts"],
        "acertos": atual["correct"],
        "erros": atual["incorrect"],
        "desempenho": atual["accuracy_rate"],
        "dias_ativos": atual["active_days"],
        "questoes_unicas": atual["unique_questions"],
        "sessoes": atual["question_sessions"],
    }
    resumo_anterior = {
        "questoes": anterior["attempts"],
        "acertos": anterior["correct"],
        "erros": anterior["incorrect"],
        "desempenho": anterior["accuracy_rate"],
        "dias_ativos": anterior["active_days"],
        "questoes_unicas": anterior["unique_questions"],
        "sessoes": anterior["question_sessions"],
    }

    foco_atual = dict(foco["current"])
    foco_anterior = dict(foco["previous"])
    for item in (foco_atual, foco_anterior):
        item["segundos"] = item["seconds"]
        item["sessoes"] = item["sessions"]
        item["dias_ativos"] = item["active_days"]
    foco_atual["concluidas"] = foco_atual["sessions"]
    foco_atual["media_sessao"] = (
        round(foco_atual["seconds"] / foco_atual["sessions"])
        if foco_atual["sessions"]
        else 0
    )
    foco_anterior["concluidas"] = foco_anterior["sessions"]
    foco_anterior["media_sessao"] = (
        round(foco_anterior["seconds"] / foco_anterior["sessions"])
        if foco_anterior["sessions"]
        else 0
    )

    fim = date.fromisoformat(temporal["current_period"]["end_inclusive"])
    return {
        "dias": temporal["current_period"]["days"],
        "data_inicio": temporal["current_period"]["start"][:10],
        "data_fim": temporal["current_period"]["end_inclusive"],
        "resumo": resumo,
        "resumo_anterior": resumo_anterior,
        "serie": serie,
        "foco": foco_atual,
        "foco_anterior": foco_anterior,
        "foco_escopo": "global",
        "consistencia_percentual": (
            100.0 * foco_atual["active_days"] / temporal["current_period"]["days"]
        ),
        "consistencia_anterior": (
            100.0
            * foco_anterior["active_days"]
            / temporal["previous_period"]["days"]
        ),
        "revisoes_periodo": atual["qualified_reviews"],
        "revisoes_anterior": anterior["qualified_reviews"],
        "revisoes_estado": atual["review_state"],
        "revisoes_legacy_excluidas": atual["unattributed_legacy_reviews"],
        "prazos_revisao": banco.obter_estatisticas_prazos_revisoes(
            concurso_id, int(dias), fim.isoformat()
        ),
        "temporal_snapshot": temporal,
        # Campos mantidos apenas para compatibilidade de widgets ocultos.
        "variacao_desempenho": temporal["comparisons"]["accuracy"]["delta_pp"],
        "dominio_medio": None,
        "delta_dominio_observado": None,
        "topicos_com_evidencia": 0,
        "total_topicos": len(temporal["topics"]),
        "consolidados": 0,
        "disciplinas": [],
        "topicos_tendencia": [],
        "maior_evolucao": None,
        "maior_queda": None,
        "maior_evolucao_topico": None,
        "maior_queda_topico": None,
        "menor_dominio": None,
        "recuperadas": 0,
        "erros_recorrentes": 0,
    }
