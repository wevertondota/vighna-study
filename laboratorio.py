"""Laboratório auditável do Motor V5."""

from inteligencia import MotorRecomendacaoV5, PESOS_PADRAO_V5, normalizar_pesos_v5
from banco import (
    obter_configuracao_int, obter_configuracao_bool,
    definir_configuracao_int, definir_configuracao_bool,
)


def carregar_configuracao_motor_v5():
    pesos = {
        "urgencia": obter_configuracao_int("motor_v5_peso_urgencia", 45),
        "necessidade": obter_configuracao_int("motor_v5_peso_necessidade", 40),
        "momento": obter_configuracao_int("motor_v5_peso_momento", 15),
    }
    return {
        "pesos": normalizar_pesos_v5(pesos),
        "proteger_revisoes_vencidas": obter_configuracao_bool("motor_v5_proteger_revisoes_vencidas", True),
    }


def salvar_configuracao_motor_v5(pesos, proteger_revisoes_vencidas=True):
    pesos = normalizar_pesos_v5(pesos)
    definir_configuracao_int("motor_v5_peso_urgencia", round(pesos["urgencia"]))
    definir_configuracao_int("motor_v5_peso_necessidade", round(pesos["necessidade"]))
    definir_configuracao_int("motor_v5_peso_momento", round(pesos["momento"]))
    definir_configuracao_bool("motor_v5_proteger_revisoes_vencidas", proteger_revisoes_vencidas)
    return carregar_configuracao_motor_v5()


def restaurar_padrao_motor_v5():
    return salvar_configuracao_motor_v5(PESOS_PADRAO_V5, True)


def montar_laboratorio(*, fila, adaptativas, contexto, calibracao=None, perfil_decisoes=None,
                       hoje=None, pesos=None, proteger_revisoes_vencidas=True,
                       usar_calibracao=True, usar_historico_decisoes=True):
    motor = MotorRecomendacaoV5(
        fila=fila, adaptativas=adaptativas, contexto=contexto,
        calibracao=calibracao or {}, perfil_decisoes=perfil_decisoes or {},
        hoje=hoje, pesos=pesos,
        proteger_revisoes_vencidas=proteger_revisoes_vencidas,
        usar_calibracao=usar_calibracao,
        usar_historico_decisoes=usar_historico_decisoes,
    )
    ranking = motor.analisar_candidatos()
    recomendacao = motor.montar()
    selecionado = None
    if recomendacao.get("topico_id") is not None:
        selecionado = next((x for x in ranking if x.get("topico_id") == recomendacao.get("topico_id") and x.get("origem_candidato") == recomendacao.get("origem")), None)
    if selecionado is None and ranking:
        selecionado = ranking[0]
    segundo = next((x for x in ranking if x is not selecionado), None)
    return {
        "ranking": ranking,
        "recomendacao": recomendacao,
        "selecionado": selecionado,
        "segundo": segundo,
        "comparacao": comparar_candidatos(selecionado, segundo),
        "pesos": motor.pesos_v5,
        "proteger_revisoes_vencidas": bool(proteger_revisoes_vencidas),
    }


def comparar_candidatos(primeiro, segundo):
    if not primeiro:
        return "Sem candidatos com evidência suficiente."
    if not segundo:
        return "Há apenas um candidato elegível no momento."
    difs = {
        "urgência": float(primeiro.get("urgencia") or 0) - float(segundo.get("urgencia") or 0),
        "necessidade acadêmica": float(primeiro.get("necessidade") or 0) - float(segundo.get("necessidade") or 0),
        "adequação ao momento": float(primeiro.get("momento") or 0) - float(segundo.get("momento") or 0),
    }
    eixo = max(difs, key=lambda k: abs(difs[k]))
    valor = difs[eixo]
    nome2 = f"{segundo.get('disciplina','—')} › {segundo.get('topico','—')}"
    direcao = "vantagem" if valor >= 0 else "desvantagem"
    return f"Contra {nome2}, a maior diferença está em {eixo}: {abs(valor):.1f} ponto(s) de {direcao}."


def explicar_topico(relatorio, busca):
    busca = str(busca or "").strip().lower()
    if not busca:
        return "Digite parte do nome da disciplina ou do tópico."
    ranking = list((relatorio or {}).get("ranking") or [])
    encontrados = [x for x in ranking if busca in str(x.get("disciplina") or "").lower() or busca in str(x.get("topico") or "").lower()]
    if not encontrados:
        return "Este tópico não apareceu na amostra: não há revisão pendente nem evidência adaptativa suficiente no conjunto atual."
    item = encontrados[0]
    pos = ranking.index(item) + 1
    texto = [f"#{pos} • score {float(item.get('score_total') or 0):.1f}"]
    if (relatorio or {}).get("proteger_revisoes_vencidas") and not item.get("faixa_temporal_protegida") and any(x.get("faixa_temporal_protegida") for x in ranking):
        texto.append("fora da faixa protegida porque há revisão vencida/para hoje")
    eixo = min(("urgencia","necessidade","momento"), key=lambda k: float(item.get(k) or 0))
    nomes = {"urgencia":"urgência", "necessidade":"necessidade acadêmica", "momento":"adequação ao momento"}
    texto.append(f"eixo mais fraco: {nomes[eixo]} ({float(item.get(eixo) or 0):.0f}/100)")
    return " • ".join(texto)
