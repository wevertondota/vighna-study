import hashlib
import json
from datetime import date, datetime

from banco import (
    definir_configuracao_texto,
    obter_configuracao_int,
    obter_configuracao_texto,
    obter_plano_acao_automatico,
    gerar_plano_acao_automatico,
    obter_resumo_foco,
    listar_topicos_pausados_ids,
)

VERSAO_JORNADA = "jornada_dia_v1"


def _data_iso(valor=None):
    if isinstance(valor, datetime):
        return valor.date().isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    texto = str(valor or "").strip()[:10]
    if texto:
        try:
            return date.fromisoformat(texto).isoformat()
        except Exception:
            pass
    return date.today().isoformat()


def _chave(concurso_id, data_ref=None):
    return f"jornada_dia_v1_{int(concurso_id)}_{_data_iso(data_ref)}"


def _texto(valor, padrao=""):
    texto = str(valor or "").strip()
    return texto or padrao


def _inteiro(valor, padrao=0):
    try:
        return int(valor)
    except Exception:
        return int(padrao)


def estimar_minutos_item(item):
    item = dict(item or {})
    if _inteiro(item.get("minutos"), 0) > 0:
        return max(5, min(240, _inteiro(item.get("minutos"))))
    questoes = max(0, _inteiro(item.get("questoes") or item.get("questoes_alvo"), 0))
    revisoes = max(0, _inteiro(item.get("quantidade_revisoes"), 0))
    tipo = _texto(item.get("tipo") or item.get("atividade")).lower()
    minutos = 0
    if questoes:
        minutos += questoes * 2
    if revisoes:
        minutos += revisoes * 15
    if minutos <= 0:
        if "simulado" in tipo:
            minutos = 60
        elif "revis" in tipo:
            minutos = 20
        elif "reten" in tipo:
            minutos = 20
        else:
            minutos = 30
    minutos = int(((minutos + 4) // 5) * 5)
    return max(5, min(240, minutos))


def _id_item(item, posicao=0):
    base = "|".join([
        _texto(item.get("origem")),
        _texto(item.get("disciplina")),
        _texto(item.get("topico")),
        _texto(item.get("tipo") or item.get("atividade")),
        str(item.get("topico_id") or ""),
        str(posicao),
    ])
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]


def _atividade_foco(item):
    tipo = _texto(item.get("atividade") or item.get("tipo"), "Estudo livre")
    validos = {
        "Treino adaptativo",
        "Teste de retenção",
        "Revisão",
        "Sessão de controle",
        "Simulado",
        "Questões",
        "Estudo livre",
        "Teoria / leitura",
        "Resumo / anotações",
        "Outro",
    }
    if tipo in validos:
        return tipo
    if _inteiro(item.get("questoes") or item.get("questoes_alvo"), 0) > 0:
        return "Questões"
    if "revis" in tipo.lower():
        return "Revisão"
    return "Estudo livre"


def _normalizar_candidato(item, origem, posicao=0):
    item = dict(item or {})
    topico_id = item.get("topico_id")
    try:
        topico_id = int(topico_id) if topico_id not in (None, "") else None
    except Exception:
        topico_id = None
    atividade = _atividade_foco(item)
    questoes = max(0, _inteiro(item.get("questoes") or item.get("questoes_alvo"), 0))
    minutos = estimar_minutos_item(item)
    disciplina = _texto(item.get("disciplina"), "Livre / sem vínculo")
    topico = _texto(item.get("topico"), "")
    titulo = _texto(item.get("titulo"))
    if not titulo:
        titulo = disciplina if not topico else f"{disciplina} — {topico}"
    motivo = _texto(
        item.get("motivo_principal")
        or item.get("motivo")
        or item.get("detalhe")
        or item.get("acao"),
        "Atividade relevante para o ciclo atual.",
    )
    candidato = {
        "id": _id_item({**item, "origem": origem}, posicao),
        "origem_item": origem,
        "titulo": titulo,
        "disciplina": disciplina,
        "topico_id": topico_id,
        "topico": topico,
        "atividade": atividade,
        "minutos": minutos,
        "questoes_alvo": questoes if topico_id is not None else 0,
        "motivo": motivo,
        "prioridade": float(item.get("score_total") or item.get("score") or item.get("prioridade") or 0.0),
        "status": "pendente",
        "duracao_efetiva": 0,
        "sessao_foco_id": None,
        "opcional": False,
    }
    if origem in {"recomendacao_v4", "recomendacao_v5"}:
        candidato["recomendacao"] = {
            "origem": item.get("origem"),
            "versao_motor": item.get("versao_motor"),
            "score_total": item.get("score_total"),
            "score_explicado": item.get("score_explicado") or [],
            "motivos": item.get("motivos") or [],
            "calibracao_aplicada": bool(item.get("calibracao_aplicada")),
            "eixos_v5": item.get("eixos_v5") or {},
            "pesos_v5": item.get("pesos_v5") or {},
        }
    return candidato


def _meta_diaria_minutos(candidatos, resumo_foco):
    horas = max(0, obter_configuracao_int("meta_foco_semanal_horas", 0))
    dias = max(0, min(7, obter_configuracao_int("meta_dias_estudo_semanal", 0)))
    if horas > 0:
        divisor = dias if dias > 0 else 5
        return max(20, int(round(horas * 60 / max(1, divisor)))), "meta_semanal"

    soma = sum(estimar_minutos_item(item) for item in candidatos[:4])
    if soma <= 0:
        soma = 90
    # Sem meta explícita, a Jornada usa a carga real disponível no plano/recomendações,
    # sem fingir que isso é uma meta definida pelo usuário.
    return max(45, min(150, soma)), "carga_operacional"


def carregar_jornada(concurso_id, data_ref=None):
    bruto = obter_configuracao_texto(_chave(concurso_id, data_ref), None)
    if not bruto:
        return None
    try:
        jornada = json.loads(bruto)
    except Exception:
        return None
    if int(jornada.get("concurso_id") or 0) != int(concurso_id):
        return None
    if _data_iso(jornada.get("data")) != _data_iso(data_ref):
        return None
    pausados = listar_topicos_pausados_ids(concurso_id)
    if pausados:
        jornada["itens"] = [
            item for item in list(jornada.get("itens") or [])
            if item.get("status") == "concluida"
            or item.get("topico_id") in (None, "")
            or int(item.get("topico_id")) not in pausados
        ]
    return atualizar_resumo_jornada(jornada)


def salvar_jornada(jornada):
    jornada = dict(jornada or {})
    concurso_id = int(jornada.get("concurso_id"))
    data_ref = _data_iso(jornada.get("data"))
    jornada["data"] = data_ref
    jornada["atualizado_em"] = datetime.now().isoformat(timespec="seconds")
    definir_configuracao_texto(
        _chave(concurso_id, data_ref),
        json.dumps(jornada, ensure_ascii=False),
    )
    return atualizar_resumo_jornada(jornada)


def atualizar_resumo_jornada(jornada):
    jornada = dict(jornada or {})
    itens = [dict(item) for item in (jornada.get("itens") or [])]
    jornada["itens"] = itens
    resumo_foco = obter_resumo_foco(jornada.get("data"))
    hoje_min = int(round(int(resumo_foco.get("hoje_segundos") or 0) / 60.0))
    meta = max(0, _inteiro(jornada.get("meta_minutos"), 0))
    pendentes = [i for i in itens if i.get("status") in {"pendente", "interrompida", "em_andamento"}]
    concluidas = [i for i in itens if i.get("status") == "concluida"]
    puladas = [i for i in itens if i.get("status") == "pulada"]
    jornada["resumo"] = {
        "foco_hoje_minutos": hoje_min,
        "meta_minutos": meta,
        "restante_minutos": max(0, meta - hoje_min),
        "meta_atingida": bool(meta > 0 and hoje_min >= meta),
        "itens": len(itens),
        "pendentes": len(pendentes),
        "concluidas": len(concluidas),
        "puladas": len(puladas),
        "estimativa_pendente_minutos": sum(_inteiro(i.get("minutos"), 0) for i in pendentes),
    }
    return jornada


def gerar_jornada(concurso_id, recomendacao=None, fila=None, plano=None, data_ref=None, preservar=None):
    concurso_id = int(concurso_id)
    data_txt = _data_iso(data_ref)
    fila = list(fila or [])
    resumo_foco = obter_resumo_foco(data_txt)

    candidatos = []
    if recomendacao:
        candidatos.append(_normalizar_candidato(recomendacao, "recomendacao_v5", 0))

    # A fila de revisões fornece alternativas concretas e executáveis por tópico.
    for pos, item in enumerate(fila[:8], 1):
        candidato = _normalizar_candidato({
            **dict(item),
            "tipo": "Revisão",
            "minutos": 20 if _inteiro(item.get("revisoes"), 0) else 25,
            "motivo": item.get("motivo"),
        }, "fila_revisoes", pos)
        candidatos.append(candidato)

    if plano is None:
        plano = obter_plano_acao_automatico(concurso_id)
    if not plano or not plano.get("itens"):
        try:
            plano = gerar_plano_acao_automatico(
                concurso_id=concurso_id,
                data_inicio=data_txt,
                carga="moderada",
                horizonte=7,
            )
        except Exception:
            plano = None

    itens_plano = list((plano or {}).get("itens") or [])
    itens_plano.sort(key=lambda x: (str(x.get("data") or ""), -float(x.get("prioridade") or 0.0)))
    hoje = [x for x in itens_plano if str(x.get("data") or "")[:10] == data_txt]
    depois = [x for x in itens_plano if str(x.get("data") or "")[:10] > data_txt]
    for pos, item in enumerate((hoje + depois)[:10], 20):
        # Ações agrupadas sem tópico não conseguem abrir uma sessão contextual.
        # Simulados e sessões gerais ainda podem ser executados como foco livre.
        if item.get("topico_id") in (None, "") and item.get("tipo") not in {"Simulado"}:
            continue
        candidatos.append(_normalizar_candidato(item, "plano_automatico", pos))

    # Remove duplicatas mantendo a recomendação V5 como primeira opção.
    pausados = listar_topicos_pausados_ids(concurso_id)
    if pausados:
        candidatos = [
            item for item in candidatos
            if item.get("topico_id") in (None, "")
            or int(item.get("topico_id")) not in pausados
        ]

    unicos = []
    vistos = set()
    for item in candidatos:
        chave = (
            item.get("topico_id"),
            _texto(item.get("atividade")).lower(),
            _texto(item.get("disciplina")).lower(),
        )
        if chave in vistos:
            continue
        vistos.add(chave)
        unicos.append(item)
    candidatos = unicos

    if not candidatos:
        candidatos = [_normalizar_candidato({
            "disciplina": "Livre / sem vínculo",
            "tipo": "Estudo livre",
            "titulo": "Sessão livre",
            "minutos": 30,
            "motivo": "Ainda não há evidência suficiente para montar uma sequência contextual.",
        }, "fallback", 99)]

    meta_minutos, meta_origem = _meta_diaria_minutos(candidatos, resumo_foco)
    foco_hoje_min = int(round(int(resumo_foco.get("hoje_segundos") or 0) / 60.0))
    restante = max(0, meta_minutos - foco_hoje_min)

    preservados = []
    if preservar:
        for item in preservar.get("itens") or []:
            if item.get("status") in {"concluida", "pulada"}:
                preservados.append(dict(item))
    chaves_preservadas = {
        (i.get("topico_id"), _texto(i.get("atividade")).lower())
        for i in preservados
    }

    selecionados = []
    acumulado = 0
    limite = restante if restante > 0 else 30
    for candidato in candidatos:
        chave = (candidato.get("topico_id"), _texto(candidato.get("atividade")).lower())
        if chave in chaves_preservadas:
            continue
        selecionados.append(candidato)
        acumulado += _inteiro(candidato.get("minutos"), 0)
        if len(selecionados) >= 5 or (acumulado >= limite and len(selecionados) >= 2):
            break
    if not selecionados and candidatos:
        extra = dict(candidatos[0])
        extra["opcional"] = True
        selecionados = [extra]

    if restante <= 0:
        for item in selecionados:
            item["opcional"] = True

    jornada = {
        "versao": VERSAO_JORNADA,
        "concurso_id": concurso_id,
        "data": data_txt,
        "status": "ativa",
        "meta_minutos": meta_minutos,
        "meta_origem": meta_origem,
        "foco_no_inicio_minutos": foco_hoje_min,
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "itens": preservados + selecionados,
    }
    if preservar:
        jornada["recalculado_em"] = datetime.now().isoformat(timespec="seconds")
    return salvar_jornada(jornada)


def proximo_item(jornada):
    for item in (jornada or {}).get("itens") or []:
        if item.get("status") in {"interrompida", "pendente"}:
            return dict(item)
    return None


def preparar_item(item, data_ref=None, concurso_id=None):
    item = dict(item or {})
    item_id = _texto(item.get("id"))
    data_txt = _data_iso(data_ref)
    topico_id = item.get("topico_id")
    questoes = max(0, _inteiro(item.get("questoes_alvo"), 0))
    atividade = _atividade_foco(item)
    return {
        "minutos": max(5, _inteiro(item.get("minutos"), 30)),
        "atividade": atividade,
        "disciplina": item.get("disciplina"),
        "topico_id": topico_id,
        "topico": item.get("topico"),
        "observacao": f"Jornada do Dia • {_texto(item.get('titulo'), 'Atividade')}",
        "questoes_alvo": questoes if topico_id not in (None, "") else 0,
        "origem": "Jornada do Dia",
        "plano_chave": (
            f"jornada|{int(concurso_id)}|{data_txt}|{item_id}"
            if concurso_id not in (None, "")
            else f"jornada|{data_txt}|{item_id}"
        ),
        "abrir_questoes_ao_iniciar": bool(
            questoes > 0
            and topico_id not in (None, "")
            and atividade in {"Questões", "Treino adaptativo", "Teste de retenção"}
        ),
    }


def marcar_item(concurso_id, item_id, status, data_ref=None, **extras):
    jornada = carregar_jornada(concurso_id, data_ref)
    if not jornada:
        return None
    encontrado = False
    for item in jornada.get("itens") or []:
        if _texto(item.get("id")) != _texto(item_id):
            continue
        item["status"] = _texto(status, "pendente")
        item["atualizado_em"] = datetime.now().isoformat(timespec="seconds")
        for chave, valor in extras.items():
            if valor is not None:
                item[chave] = valor
        encontrado = True
        break
    if not encontrado:
        return jornada
    return salvar_jornada(jornada)


def marcar_por_plano_chave(concurso_id, plano_chave, concluida, sessao_id=None, duracao_efetiva=0):
    texto = _texto(plano_chave)
    partes = texto.split("|")
    if not partes or partes[0] != "jornada":
        return None
    if len(partes) == 4:
        try:
            concurso_id = int(partes[1])
        except Exception:
            pass
        data_txt, item_id = partes[2], partes[3]
    elif len(partes) == 3:
        data_txt, item_id = partes[1], partes[2]
    else:
        return None
    return marcar_item(
        concurso_id,
        item_id,
        "concluida" if concluida else "interrompida",
        data_txt,
        sessao_foco_id=sessao_id,
        duracao_efetiva=max(0, _inteiro(duracao_efetiva, 0)),
    )


def definir_status_jornada(concurso_id, status, data_ref=None):
    jornada = carregar_jornada(concurso_id, data_ref)
    if not jornada:
        return None
    jornada["status"] = _texto(status, "ativa")
    return salvar_jornada(jornada)


def excluir_jornada(concurso_id, data_ref=None):
    definir_configuracao_texto(_chave(concurso_id, data_ref), "")
