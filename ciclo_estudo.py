"""Núcleo puro do ciclo acadêmico do VighnaStudy.

Este módulo concentra a etapa sessão de questões -> revisão automática para
que a regra possa ser testada sem carregar a interface Qt. A interface apenas
delega para esta função.
"""

from __future__ import annotations

import json
from datetime import date, timedelta

from banco import (
    obter_configuracao_bool,
    obter_configuracao_int,
    obter_configuracao_texto,
    obter_contextos_revisao_automatica_sessao,
    obter_resultado_cobertura_revisao,
    salvar_revisao_automatica_questoes,
)
from espacamento import (
    calcular_sugestao_espacamento,
    obter_configuracao_queda_padrao,
    obter_tabela_padrao,
    normalizar_tabela_espacamento,
)


def _formatar_data(data_iso: str | None) -> str:
    if not data_iso:
        return "—"
    try:
        return date.fromisoformat(str(data_iso)[:10]).strftime("%d/%m/%Y")
    except ValueError:
        return str(data_iso)


def carregar_configuracao_espacamento_ciclo() -> dict:
    """Carrega a configuração do espaçamento sem depender da UI."""
    tabela = obter_tabela_padrao()
    texto_matriz = obter_configuracao_texto("matriz_espacamento_json", None)

    if texto_matriz:
        try:
            tabela = normalizar_tabela_espacamento(json.loads(texto_matriz))
        except (ValueError, TypeError, json.JSONDecodeError):
            tabela = obter_tabela_padrao()

    padrao = obter_configuracao_queda_padrao()
    limite_moderada = obter_configuracao_int(
        "queda_limite_moderada", padrao["limite_moderada"]
    )
    limite_forte = obter_configuracao_int(
        "queda_limite_forte", padrao["limite_forte"]
    )
    penalizacao_moderada = obter_configuracao_int(
        "queda_penalizacao_moderada", padrao["penalizacao_moderada"]
    )
    penalizacao_forte = obter_configuracao_int(
        "queda_penalizacao_forte", padrao["penalizacao_forte"]
    )

    if limite_forte <= limite_moderada:
        limite_moderada = padrao["limite_moderada"]
        limite_forte = padrao["limite_forte"]

    return {
        "tabela": tabela,
        "limite_moderada": limite_moderada,
        "limite_forte": limite_forte,
        "penalizacao_moderada": max(0, min(90, penalizacao_moderada)),
        "penalizacao_forte": max(0, min(90, penalizacao_forte)),
    }


def integrar_sessao_questoes_com_revisoes(sessao_id: int) -> list[dict]:
    """Consolida as respostas de uma sessão em revisões por tópico/dia.

    Regras preservadas da implementação original:
    - 1–4 questões em tópico conhecido: só atividade; não cria revisão.
    - 5–9: revisão de baixa confiança; preserva agenda anterior.
    - 10+: revisão normal; recalcula próxima revisão.
    - primeiro contato: qualquer resolução efetiva cria a primeira revisão,
      com teto conservador de espaçamento para amostras pequenas.
    """
    minimo_registro = max(
        1, obter_configuracao_int("questoes_revisao_min_registro", 5)
    )
    minimo_agendamento = max(
        minimo_registro,
        obter_configuracao_int("questoes_revisao_min_agendamento", 10),
    )

    contextos = obter_contextos_revisao_automatica_sessao(sessao_id)
    resultados: list[dict] = []
    aplicar_penalizacao = obter_configuracao_bool("aplicar_penalizacao_queda", True)
    config = carregar_configuracao_espacamento_ciclo()

    for contexto in contextos:
        questoes = int(contexto["questoes"] or 0)
        acertos = int(contexto["acertos"] or 0)
        base = {
            "topico_id": contexto["topico_id"],
            "disciplina": contexto["disciplina"],
            "topico": contexto["topico"],
            "data": contexto["data"],
            "questoes": questoes,
            "acertos": acertos,
            "percentual": contexto["percentual"],
            "revisao_id": None,
            "revisao_registrada": False,
            "agendamento_atualizado": False,
            "proxima_revisao": None,
            "confianca": None,
        }
        primeiro_contato = bool(contexto.get("primeiro_contato", False))

        # Revisão por cobertura integral: enquanto a data prevista estiver
        # vencida/hoje, o tópico só avança na agenda depois de todas as
        # questões ativas terem recebido ao menos uma resposta efetiva na
        # rodada. O resultado final usa uma observação (a mais recente) por
        # questão, evitando que repetições pesem artificialmente no percentual.
        cobertura = obter_resultado_cobertura_revisao(
            contexto["topico_id"],
            contexto.get("concurso_id"),
        )
        if cobertura and cobertura.get("ativa"):
            total_cobertura = int(cobertura.get("total") or 0)
            restantes_cobertura = int(cobertura.get("restantes") or 0)
            cobertas_cobertura = int(cobertura.get("cobertas") or 0)
            if total_cobertura > 0 and restantes_cobertura > 0:
                resultados.append({
                    **base,
                    "questoes": cobertas_cobertura,
                    "revisao_registrada": False,
                    "agendamento_atualizado": False,
                    "confianca": "cobertura_parcial",
                    "status_integracao": "cobertura_parcial",
                    "cobertura_revisao": cobertura,
                    "descricao": (
                        f"Rodada de revisão em andamento: {cobertas_cobertura}/{total_cobertura} "
                        f"questões cobertas ({restantes_cobertura} restante(s)). "
                        "A data da próxima revisão foi preservada até a cobertura completa."
                    ),
                })
                continue

            if total_cobertura > 0 and restantes_cobertura == 0:
                questoes = int(cobertura.get("questoes") or total_cobertura)
                acertos = int(cobertura.get("acertos") or 0)
                percentual_cobertura = cobertura.get("percentual_resultado")
                contexto = dict(contexto)
                contexto["questoes"] = questoes
                contexto["acertos"] = acertos
                contexto["percentual"] = percentual_cobertura
                primeiro_contato = False
                base.update({
                    "questoes": questoes,
                    "acertos": acertos,
                    "percentual": percentual_cobertura,
                })
                confianca = "normal"
                sugestao = calcular_sugestao_espacamento(
                    numero_revisao=contexto["numero_revisao"],
                    percentual_atual=percentual_cobertura,
                    percentual_anterior=contexto["percentual_anterior"],
                    aplicar_penalizacao=aplicar_penalizacao,
                    tabela_espacamento=config["tabela"],
                    limite_queda_moderada=config["limite_moderada"],
                    limite_queda_forte=config["limite_forte"],
                    penalizacao_moderada=config["penalizacao_moderada"],
                    penalizacao_forte=config["penalizacao_forte"],
                )
                dias_aplicados = int(sugestao["dias"])
                try:
                    data_base = date.fromisoformat(str(contexto["data"])[:10])
                except ValueError:
                    data_base = None
                proxima = (
                    (data_base + timedelta(days=dias_aplicados)).isoformat()
                    if data_base is not None
                    else None
                )
                salvo = salvar_revisao_automatica_questoes(
                    contexto["topico_id"],
                    contexto["data"],
                    questoes,
                    acertos,
                    confianca,
                    proxima_revisao=proxima,
                    sessao_questoes_id=sessao_id,
                    concurso_id=contexto.get("concurso_id"),
                    tentativas_desde=cobertura.get("referencia"),
                )
                resultados.append({
                    **base,
                    "revisao_id": salvo["revisao_id"],
                    "revisao_registrada": True,
                    "agendamento_atualizado": proxima is not None,
                    "proxima_revisao": proxima,
                    "confianca": confianca,
                    "status_integracao": "cobertura_completa",
                    "cobertura_revisao": cobertura,
                    "descricao": (
                        f"Cobertura completa da revisão: {questoes}/{questoes} questões. "
                        f"Desempenho consolidado: {percentual_cobertura:.1f}%. "
                        + (
                            f"Próxima revisão agendada para {_formatar_data(proxima)}."
                            if proxima else "Revisão concluída."
                        )
                    ),
                    "dias_sugeridos": dias_aplicados,
                })
                continue

        if questoes < minimo_registro and not primeiro_contato:
            resultados.append({
                **base,
                "status_integracao": "atividade",
                "descricao": (
                    f"{questoes} questão(ões): atividade registrada. "
                    f"A revisão automática começa em {minimo_registro}."
                ),
            })
            continue

        if questoes < minimo_registro:
            confianca = "muito_baixa"
        elif questoes < minimo_agendamento:
            confianca = "baixa"
        else:
            confianca = "normal"

        proxima = None
        sugestao = None
        dias_aplicados = None
        deve_agendar = primeiro_contato or confianca == "normal"

        if deve_agendar:
            sugestao = calcular_sugestao_espacamento(
                numero_revisao=contexto["numero_revisao"],
                percentual_atual=contexto["percentual"],
                percentual_anterior=contexto["percentual_anterior"],
                aplicar_penalizacao=aplicar_penalizacao and not primeiro_contato,
                tabela_espacamento=config["tabela"],
                limite_queda_moderada=config["limite_moderada"],
                limite_queda_forte=config["limite_forte"],
                penalizacao_moderada=config["penalizacao_moderada"],
                penalizacao_forte=config["penalizacao_forte"],
            )
            dias_aplicados = int(sugestao["dias"])

            if primeiro_contato:
                if confianca == "muito_baixa":
                    dias_aplicados = min(dias_aplicados, 7)
                elif confianca == "baixa":
                    dias_aplicados = min(dias_aplicados, 14)

            try:
                data_base = date.fromisoformat(str(contexto["data"])[:10])
            except ValueError:
                data_base = None
            if data_base is not None:
                proxima = (data_base + timedelta(days=dias_aplicados)).isoformat()

        salvo = salvar_revisao_automatica_questoes(
            contexto["topico_id"],
            contexto["data"],
            questoes,
            acertos,
            confianca,
            proxima_revisao=proxima,
            sessao_questoes_id=sessao_id,
            concurso_id=contexto.get("concurso_id"),
        )

        if primeiro_contato:
            if confianca == "muito_baixa":
                rotulo = "amostra muito pequena"
            elif confianca == "baixa":
                rotulo = "baixa confiança"
            else:
                rotulo = "confiança normal"
            descricao = (
                f"Primeiro contato com o tópico: {questoes} questão(ões), {rotulo}. "
                "A primeira revisão foi registrada"
                + (
                    f" e a próxima ficou agendada para {_formatar_data(proxima)}."
                    if proxima
                    else "."
                )
            )
            status_integracao = "primeiro_contato"
        elif confianca == "baixa":
            descricao = (
                f"{questoes} questão(ões): revisão automática de baixa confiança registrada. "
                "O agendamento anterior foi preservado; "
                f"com {minimo_agendamento}+ questões a data será recalculada."
            )
            status_integracao = "baixa_confianca"
        else:
            descricao = (
                f"{questoes} questão(ões): revisão automática registrada"
                + (
                    f" e próxima revisão agendada para {_formatar_data(proxima)}."
                    if proxima
                    else "."
                )
            )
            status_integracao = "revisao_normal"

        resultados.append({
            **base,
            "revisao_id": salvo["revisao_id"],
            "revisao_registrada": True,
            "agendamento_atualizado": proxima is not None,
            "proxima_revisao": proxima,
            "confianca": confianca,
            "status_integracao": status_integracao,
            "descricao": descricao,
            "dias_sugeridos": dias_aplicados if sugestao else None,
        })

    return resultados
