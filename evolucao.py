"""Métricas de evolução histórica do VighnaStudy.

Este módulo mantém a leitura histórica separada da interface. Ele combina
questões, revisões, sessões reais do Modo Foco e observações de domínio que
já existem no banco, sem inventar dados quando não há evidência suficiente.
"""

from collections import defaultdict
from datetime import date, datetime, timedelta

import banco


def _como_data(valor):
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        return date.fromisoformat(str(valor or "")[:10])
    except Exception:
        return None


def _variacao_percentual(atual, anterior):
    atual = float(atual or 0)
    anterior = float(anterior or 0)
    if anterior <= 0:
        return None
    return 100.0 * (atual - anterior) / anterior


def _resumir_foco(rows):
    segundos = sum(int(row[1] or 0) for row in rows)
    sessoes = sum(int(row[2] or 0) for row in rows)
    concluidas = sum(int(row[3] or 0) for row in rows)
    dias_ativos = sum(1 for row in rows if int(row[1] or 0) > 0)
    return {
        "segundos": segundos,
        "sessoes": sessoes,
        "concluidas": concluidas,
        "dias_ativos": dias_ativos,
        "media_sessao": int(round(segundos / sessoes)) if sessoes else 0,
    }


def _resumo_tentativas(items):
    total = len(items)
    acertos = sum(1 for item in items if item["correta"])
    return {
        "questoes": total,
        "acertos": acertos,
        "desempenho": (100.0 * acertos / total) if total else None,
        "dias_ativos": len({item["data"] for item in items}),
    }


def obter_evolucao_historica(concurso_id=None, dias=30):
    """Retorna a visão histórica integrada do período e do período anterior.

    Questões/revisões são filtradas pelo perfil de concurso. O Modo Foco é
    histórico global do usuário porque as versões atuais de ``sessoes_foco``
    não possuem ``concurso_id``. Isso mantém a métrica compatível com o card
    Ritmo de estudo, que também representa o foco efetivo geral.
    """

    if concurso_id is None:
        concurso_id = banco.obter_concurso_ativo()[0]
    concurso_id = int(concurso_id)
    dias = max(7, min(365, int(dias or 30)))

    hoje = date.today()
    inicio = hoje - timedelta(days=dias - 1)
    fim_anterior = inicio - timedelta(days=1)
    inicio_anterior = fim_anterior - timedelta(days=dias - 1)

    base = banco.obter_central_minha_evolucao(concurso_id, dias)

    with banco.conectar() as con:
        foco_rows = con.execute(
            """
            SELECT substr(inicio, 1, 10) AS dia,
                   COALESCE(SUM(duracao_efetiva), 0) AS segundos,
                   COUNT(*) AS sessoes,
                   COALESCE(SUM(CASE WHEN concluida = 1 THEN 1 ELSE 0 END), 0) AS concluidas
            FROM sessoes_foco
            WHERE substr(inicio, 1, 10) BETWEEN ? AND ?
              AND duracao_efetiva > 0
            GROUP BY dia
            ORDER BY dia
            """,
            (inicio.isoformat(), hoje.isoformat()),
        ).fetchall()
        foco_ant_rows = con.execute(
            """
            SELECT substr(inicio, 1, 10) AS dia,
                   COALESCE(SUM(duracao_efetiva), 0) AS segundos,
                   COUNT(*) AS sessoes,
                   COALESCE(SUM(CASE WHEN concluida = 1 THEN 1 ELSE 0 END), 0) AS concluidas
            FROM sessoes_foco
            WHERE substr(inicio, 1, 10) BETWEEN ? AND ?
              AND duracao_efetiva > 0
            GROUP BY dia
            ORDER BY dia
            """,
            (inicio_anterior.isoformat(), fim_anterior.isoformat()),
        ).fetchall()

        revisoes_rows = con.execute(
            """
            SELECT r.data, COUNT(*)
            FROM revisoes r
            JOIN topicos t ON t.id = r.topico_id
            JOIN disciplinas d ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
              ON dc.disciplina_id = d.id AND dc.concurso_id = ? AND dc.incluido = 1
              AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
              ON tc.topico_id = t.id AND tc.concurso_id = ? AND tc.incluido = 1
            WHERE r.data BETWEEN ? AND ?
            GROUP BY r.data
            ORDER BY r.data
            """,
            (concurso_id, concurso_id, inicio.isoformat(), hoje.isoformat()),
        ).fetchall()
        revisoes_ant_rows = con.execute(
            """
            SELECT r.data, COUNT(*)
            FROM revisoes r
            JOIN topicos t ON t.id = r.topico_id
            JOIN disciplinas d ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
              ON dc.disciplina_id = d.id AND dc.concurso_id = ? AND dc.incluido = 1
              AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
              ON tc.topico_id = t.id AND tc.concurso_id = ? AND tc.incluido = 1
            WHERE r.data BETWEEN ? AND ?
            GROUP BY r.data
            ORDER BY r.data
            """,
            (concurso_id, concurso_id, inicio_anterior.isoformat(), fim_anterior.isoformat()),
        ).fetchall()

        dominio_rows = con.execute(
            """
            SELECT substr(COALESCE(finalizado_em, criado_em), 1, 10) AS dia,
                   AVG(dominio_medio_depois) AS dominio
            FROM efetividade_sessoes
            WHERE concurso_id = ?
              AND dominio_medio_depois IS NOT NULL
              AND substr(COALESCE(finalizado_em, criado_em), 1, 10) BETWEEN ? AND ?
            GROUP BY dia
            ORDER BY dia
            """,
            (concurso_id, inicio.isoformat(), hoje.isoformat()),
        ).fetchall()

        tentativas_rows = con.execute(
            """
            SELECT
                substr(tq.respondida_em, 1, 10) AS dia,
                tq.correta,
                COALESCE(tq.topico_id_snapshot, q.topico_id) AS topico_id,
                COALESCE(tq.disciplina_snapshot, d.nome, '—') AS disciplina,
                COALESCE(tq.topico_snapshot, t.nome, '—') AS topico
            FROM tentativas_questoes tq
            LEFT JOIN questoes q ON q.id = tq.questao_id
            LEFT JOIN topicos t ON t.id = COALESCE(tq.topico_id_snapshot, q.topico_id)
            LEFT JOIN disciplinas d ON d.id = t.disciplina_id
            WHERE tq.concurso_id = ?
              AND tq.correta IS NOT NULL
              AND substr(tq.respondida_em, 1, 10) BETWEEN ? AND ?
            ORDER BY tq.respondida_em, tq.id
            """,
            (concurso_id, inicio_anterior.isoformat(), hoje.isoformat()),
        ).fetchall()

    foco = _resumir_foco(foco_rows)
    foco_anterior = _resumir_foco(foco_ant_rows)
    foco["variacao_percentual"] = _variacao_percentual(
        foco["segundos"], foco_anterior["segundos"]
    )

    consistencia = 100.0 * foco["dias_ativos"] / dias if dias else 0.0
    consistencia_anterior = (
        100.0 * foco_anterior["dias_ativos"] / dias if dias else 0.0
    )

    revisoes_total = sum(int(row[1] or 0) for row in revisoes_rows)
    revisoes_anterior = sum(int(row[1] or 0) for row in revisoes_ant_rows)

    dominio_map = {str(row[0]): float(row[1]) for row in dominio_rows if row[1] is not None}
    dominio_valores = [float(row[1]) for row in dominio_rows if row[1] is not None]
    dominio_inicio = dominio_valores[0] if dominio_valores else None
    dominio_fim = dominio_valores[-1] if dominio_valores else None
    delta_dominio = (
        dominio_fim - dominio_inicio
        if dominio_inicio is not None and dominio_fim is not None and len(dominio_valores) >= 2
        else None
    )

    foco_map = {str(row[0]): int(row[1] or 0) for row in foco_rows}
    revisoes_map = {str(row[0]): int(row[1] or 0) for row in revisoes_rows}
    serie = []
    base_serie = {item.get("data"): dict(item) for item in base.get("serie", [])}
    cursor = inicio
    while cursor <= hoje:
        chave = cursor.isoformat()
        item = base_serie.get(chave, {"data": chave, "questoes": 0, "desempenho": None})
        item["foco_segundos"] = foco_map.get(chave, 0)
        item["foco_minutos"] = round(item["foco_segundos"] / 60.0, 1)
        item["revisoes"] = revisoes_map.get(chave, 0)
        item["dominio_observado"] = dominio_map.get(chave)
        serie.append(item)
        cursor += timedelta(days=1)

    tentativas = []
    for row in tentativas_rows:
        dt = _como_data(row[0])
        if dt is None:
            continue
        tentativas.append({
            "data": dt,
            "correta": bool(row[1]),
            "topico_id": int(row[2]) if row[2] is not None else None,
            "disciplina": str(row[3] or "—"),
            "topico": str(row[4] or "—"),
        })

    por_topico = defaultdict(list)
    for item in tentativas:
        chave = (item["topico_id"], item["disciplina"], item["topico"])
        por_topico[chave].append(item)

    indices = banco.obter_indices_dominio_topicos(concurso_id)
    topicos = []
    for (topico_id, disciplina, topico), items in por_topico.items():
        atuais = [i for i in items if inicio <= i["data"] <= hoje]
        anteriores = [i for i in items if inicio_anterior <= i["data"] <= fim_anterior]
        if not atuais:
            continue
        ra = _resumo_tentativas(atuais)
        rp = _resumo_tentativas(anteriores)
        delta = None
        if (
            ra["desempenho"] is not None
            and rp["desempenho"] is not None
            and ra["questoes"] >= 3
            and rp["questoes"] >= 3
        ):
            delta = ra["desempenho"] - rp["desempenho"]
        dominio = None
        if topico_id is not None:
            indice = indices.get(int(topico_id))
            if indice and int(indice.get("tentativas") or 0) > 0:
                dominio = float(indice.get("score") or 0.0)
        topicos.append({
            "topico_id": topico_id,
            "disciplina": disciplina,
            "topico": topico,
            "dominio": dominio,
            "desempenho": ra["desempenho"],
            "variacao": delta,
            "questoes": ra["questoes"],
            "questoes_anteriores": rp["questoes"],
            "dias_ativos": ra["dias_ativos"],
            "ultima_atividade": max(i["data"] for i in atuais).isoformat(),
        })

    topicos.sort(
        key=lambda item: (
            item["variacao"] is None,
            -(abs(item["variacao"]) if item["variacao"] is not None else 0.0),
            item["dominio"] is None,
            item["dominio"] if item["dominio"] is not None else 999.0,
            -item["questoes"],
            item["disciplina"].lower(),
            item["topico"].lower(),
        )
    )

    comparaveis = [item for item in topicos if item["variacao"] is not None]
    maior_evolucao_topico = (
        max(comparaveis, key=lambda item: item["variacao"])
        if comparaveis else None
    )
    maior_queda_topico = (
        min(comparaveis, key=lambda item: item["variacao"])
        if comparaveis else None
    )

    prazos_revisao = banco.obter_estatisticas_prazos_revisoes(
        concurso_id, dias, hoje.isoformat()
    )

    resultado = dict(base)
    resultado.update({
        "serie": serie,
        "foco": foco,
        "foco_anterior": foco_anterior,
        "consistencia_percentual": consistencia,
        "consistencia_anterior": consistencia_anterior,
        "revisoes_periodo": revisoes_total,
        "revisoes_anterior": revisoes_anterior,
        "dominio_observado_inicio": dominio_inicio,
        "dominio_observado_fim": dominio_fim,
        "delta_dominio_observado": delta_dominio,
        "topicos_tendencia": topicos[:30],
        "maior_evolucao_topico": maior_evolucao_topico,
        "maior_queda_topico": maior_queda_topico,
        "prazos_revisao": prazos_revisao,
    })
    return resultado
