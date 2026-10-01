"""Aquecimento de snapshots derivados após alterações acadêmicas.

Este módulo não importa Qt. Ele pode rodar em worker e usa apenas funções que
abrem suas próprias conexões SQLite, preservando a regra de uma conexão por
thread.
"""

from __future__ import annotations

from datetime import date
from typing import Callable


def aquecer_dados_derivados(
    concurso_id: int,
    *,
    hoje: str | None = None,
    tendencias_inicio: str | None = None,
    tendencias_fim: str | None = None,
    relatorio_inicio: str | None = None,
    relatorio_fim: str | None = None,
    reportar: Callable[[str, str, int], None] | None = None,
) -> dict:
    """Recalcula/persiste os snapshots caros que mudam após uma resposta.

    Se a base sofrer nova alteração enquanto o cálculo está em curso, o cache
    persistente já impede a gravação do snapshot obsoleto. O chamador deve
    aglutinar outra rodada quando isso acontecer.
    """

    import banco
    from evolucao import obter_evolucao_historica

    concurso_id = int(concurso_id)
    hoje = str(hoje or date.today().isoformat())[:10]

    def etapa(titulo, detalhe, percentual):
        if callable(reportar):
            reportar(str(titulo), str(detalhe), int(percentual))

    resultado: dict = {
        "concurso_id": concurso_id,
        "hoje": hoje,
    }

    etapa(
        "Atualizando progresso",
        "Consolidando domínio, cobertura e evidência dos tópicos.",
        8,
    )
    progresso = banco.obter_snapshot_progresso_edital(
        concurso_id,
        capturar=False,
    )
    resultado["progresso"] = progresso

    etapa(
        "Atualizando métricas",
        "Recalculando o resumo global do perfil.",
        24,
    )
    resultado["metricas_globais"] = banco.obter_metricas_globais_nucleo(
        concurso_id
    )
    resultado["estatisticas_disciplinas"] = banco.obter_estatisticas_disciplinas(
        hoje,
        concurso_id,
    )

    etapa(
        "Atualizando regularidade",
        "Consolidando sequência, dias ativos e ritmo de estudo.",
        36,
    )
    regularidade = banco.obter_snapshot_regularidade(hoje)
    resultado["regularidade"] = regularidade

    etapa(
        "Atualizando histórico",
        "Recalculando a análise temporal compartilhada.",
        50,
    )
    temporal_30 = banco.obter_analise_temporal(concurso_id, dias=30)
    resultado["temporal_30"] = temporal_30
    resultado["historico_30"] = obter_evolucao_historica(concurso_id, 30)

    if tendencias_inicio and tendencias_fim:
        inicio = str(tendencias_inicio)[:10]
        fim = str(tendencias_fim)[:10]
        etapa(
            "Atualizando tendências",
            "Preparando o período exibido nas Estatísticas.",
            62,
        )
        resultado["tendencias_periodo"] = banco.obter_analise_temporal(
            concurso_id,
            data_inicio=inicio,
            data_fim_inclusivo=fim,
        )
        resultado["tendencias_inicio"] = inicio
        resultado["tendencias_fim"] = fim

    etapa(
        "Atualizando recomendações",
        "Recalculando a fila inteligente e prioridades do estudo.",
        72,
    )
    resultado["adaptativas"] = banco.obter_prioridades_sessao_adaptativa(
        concurso_id
    )

    etapa(
        "Atualizando conquistas",
        "Preparando XP e marcos com os snapshots já consolidados.",
        82,
    )
    resultado["gamificacao"] = banco.obter_snapshot_gamificacao(
        concurso_id,
        hoje,
        progresso_snapshot=progresso,
        regularidade_snapshot=regularidade,
        sincronizar=True,
    )

    etapa(
        "Atualizando histórico de erros",
        "Consolidando erros abertos e recuperação recente.",
        89,
    )
    resultado["caderno_erros"] = banco.listar_caderno_erros_questoes(
        concurso_id
    )

    if relatorio_inicio and relatorio_fim:
        inicio = str(relatorio_inicio)[:10]
        fim = str(relatorio_fim)[:10]
        etapa(
            "Atualizando relatório estratégico",
            "Preparando o período padrão de Relatórios.",
            94,
        )
        resultado["relatorio_estrategico"] = banco.obter_relatorio_estrategico(
            inicio,
            fim,
            concurso_id,
        )
        resultado["relatorio_inicio"] = inicio
        resultado["relatorio_fim"] = fim

    etapa(
        "Consolidando cache",
        "Os dados atualizados estão prontos para a interface.",
        100,
    )
    return resultado
