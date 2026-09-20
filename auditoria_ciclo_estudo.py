"""Auditoria não destrutiva do ciclo principal de estudo do VighnaStudy.

O objetivo deste módulo é responder, com dados persistidos, se o caminho
recomendação -> sessão -> tentativas -> revisão -> métricas continua íntegro.
Nenhuma função daqui altera o banco.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import banco
from statistics_core.periods import statistical_timezone


NIVEL_ORDEM = {"ok": 0, "atencao": 1, "erro": 2}


def _hoje_iso() -> str:
    return datetime.now(statistical_timezone()).date().isoformat()


def _inteiro(valor, padrao=0) -> int:
    try:
        return int(valor)
    except (TypeError, ValueError):
        return int(padrao)


def _finding(nivel: str, codigo: str, titulo: str, detalhe: str, quantidade: int = 0) -> dict:
    return {
        "nivel": nivel,
        "codigo": codigo,
        "titulo": titulo,
        "detalhe": detalhe,
        "quantidade": int(quantidade or 0),
    }


def _data_iso_valida(valor: Any) -> bool:
    texto = str(valor or "").strip()
    if not texto:
        return True
    try:
        date.fromisoformat(texto[:10])
        return True
    except ValueError:
        return False


def auditar_ciclo_estudo(concurso_id: int | None = None, limite_sessoes: int = 12) -> dict:
    """Audita o ciclo acadêmico do perfil atual sem escrever no banco."""
    if concurso_id is None:
        concurso_id = int(banco.obter_concurso_ativo()[0])
    concurso_id = int(concurso_id)
    limite_sessoes = max(1, min(100, int(limite_sessoes or 12)))
    hoje = _hoje_iso()

    findings: list[dict] = []
    sessoes_recentes: list[dict] = []

    with banco.conectar() as conexao:
        concurso = conexao.execute(
            "SELECT nome FROM concursos WHERE id = ?",
            (concurso_id,),
        ).fetchone()
        concurso_nome = str(concurso[0]) if concurso else f"Perfil {concurso_id}"

        base_linhagem_row = conexao.execute(
            """
            SELECT valor FROM configuracoes
            WHERE chave = 'revisoes_linhagem_base_max_id'
            """
        ).fetchone()
        base_linhagem = _inteiro(base_linhagem_row[0] if base_linhagem_row else 0)

        # Sessões e tentativas recentes do perfil.
        linhas = conexao.execute(
            """
            SELECT
                sq.id, sq.iniciado_em, sq.encerrado_em, sq.modo,
                COALESCE(sq.objetivo, 0), COALESCE(sq.concluida, 0),
                COALESCE(sq.origem, 'legado'), COALESCE(sq.versao_motor, 'sessao_legacy'),
                (SELECT COUNT(*) FROM itens_sessao_questoes isq WHERE isq.sessao_id = sq.id) AS itens,
                (SELECT COUNT(*) FROM tentativas_questoes tq WHERE tq.sessao_id = sq.id) AS tentativas,
                (SELECT COUNT(*) FROM tentativas_questoes tq WHERE tq.sessao_id = sq.id AND tq.correta IS NOT NULL) AS respondidas,
                (SELECT COUNT(*) FROM tentativas_questoes tq WHERE tq.sessao_id = sq.id AND tq.correta = 1) AS acertos,
                (SELECT COUNT(*) FROM tentativas_questoes tq WHERE tq.sessao_id = sq.id AND tq.correta IS NOT NULL AND tq.revisao_id IS NOT NULL) AS vinculadas_revisao
            FROM sessoes_questoes sq
            WHERE sq.concurso_id = ?
            ORDER BY sq.id DESC
            LIMIT ?
            """,
            (concurso_id, limite_sessoes),
        ).fetchall()
        for linha in linhas:
            respondidas = _inteiro(linha[10])
            acertos = _inteiro(linha[11])
            sessoes_recentes.append({
                "id": _inteiro(linha[0]),
                "iniciado_em": linha[1],
                "encerrado_em": linha[2],
                "modo": str(linha[3] or ""),
                "objetivo": _inteiro(linha[4]),
                "concluida": bool(linha[5]),
                "origem": str(linha[6] or "legado"),
                "versao_motor": str(linha[7] or "sessao_legacy"),
                "itens": _inteiro(linha[8]),
                "tentativas": _inteiro(linha[9]),
                "respondidas": respondidas,
                "acertos": acertos,
                "desempenho": (100.0 * acertos / respondidas) if respondidas else None,
                "vinculadas_revisao": _inteiro(linha[12]),
            })

        # Invariantes estruturais do motor unificado.
        perfil_mismatch = _inteiro(conexao.execute(
            """
            SELECT COUNT(*)
            FROM tentativas_questoes tq
            JOIN sessoes_questoes sq ON sq.id = tq.sessao_id
            WHERE sq.concurso_id = ?
              AND tq.concurso_id IS NOT NULL
              AND tq.concurso_id <> sq.concurso_id
            """,
            (concurso_id,),
        ).fetchone()[0])
        if perfil_mismatch:
            findings.append(_finding(
                "erro", "tentativa_perfil_divergente", "Tentativas fora do perfil da sessão",
                "Há tentativas cujo concurso_id não coincide com o concurso da sessão.", perfil_mismatch,
            ))

        item_mismatch = _inteiro(conexao.execute(
            """
            SELECT COUNT(*)
            FROM tentativas_questoes tq
            JOIN sessoes_questoes sq ON sq.id = tq.sessao_id
            JOIN itens_sessao_questoes isq ON isq.id = tq.item_sessao_id
            WHERE sq.concurso_id = ?
              AND tq.sessao_id IS NOT NULL
              AND tq.item_sessao_id IS NOT NULL
              AND (isq.sessao_id <> tq.sessao_id
                   OR COALESCE(isq.questao_id_snapshot, isq.questao_id) <>
                      COALESCE(tq.questao_id_snapshot, tq.questao_id))
            """,
            (concurso_id,),
        ).fetchone()[0])
        if item_mismatch:
            findings.append(_finding(
                "erro", "tentativa_item_divergente", "Tentativas inconsistentes com a fila congelada",
                "O item apresentado e a tentativa registrada não apontam para a mesma sessão/questão.", item_mismatch,
            ))

        sessoes_concluidas_sem_fim = _inteiro(conexao.execute(
            """
            SELECT COUNT(*) FROM sessoes_questoes
            WHERE concurso_id = ? AND concluida = 1 AND encerrado_em IS NULL
            """,
            (concurso_id,),
        ).fetchone()[0])
        if sessoes_concluidas_sem_fim:
            findings.append(_finding(
                "erro", "sessao_concluida_aberta", "Sessões concluídas sem encerramento",
                "Uma sessão concluída deve possuir encerrado_em para fechar corretamente o ciclo.", sessoes_concluidas_sem_fim,
            ))

        filas_incompletas = _inteiro(conexao.execute(
            """
            SELECT COUNT(*) FROM (
                SELECT sq.id
                FROM sessoes_questoes sq
                LEFT JOIN itens_sessao_questoes isq ON isq.sessao_id = sq.id
                WHERE sq.concurso_id = ?
                  AND COALESCE(sq.versao_motor, 'sessao_legacy') <> 'sessao_legacy'
                GROUP BY sq.id
                HAVING COUNT(isq.id) <> COALESCE(sq.objetivo, 0)
            )
            """,
            (concurso_id,),
        ).fetchone()[0])
        if filas_incompletas:
            findings.append(_finding(
                "erro", "fila_nao_congelada", "Fila de sessão incompleta",
                "Sessões do motor unificado devem congelar exatamente a quantidade planejada de itens.", filas_incompletas,
            ))

        # Linhagem das revisões novas. Revisões históricas até o marco de migração
        # podem permanecer sem concurso por decisão de integridade.
        linhagem_nova_ausente = _inteiro(conexao.execute(
            """
            SELECT COUNT(*) FROM revisoes
            WHERE id > ?
              AND sessao_questoes_id IS NOT NULL
              AND concurso_id IS NULL
            """,
            (base_linhagem,),
        ).fetchone()[0])
        if linhagem_nova_ausente:
            findings.append(_finding(
                "erro", "revisao_nova_sem_linhagem", "Revisões novas sem perfil",
                "Revisões criadas após a migração e ligadas a uma sessão precisam carregar concurso_id.", linhagem_nova_ausente,
            ))

        revisao_perfil_mismatch = _inteiro(conexao.execute(
            """
            SELECT COUNT(DISTINCT r.id)
            FROM revisoes r
            JOIN tentativas_questoes tq ON tq.revisao_id = r.id
            WHERE r.concurso_id IS NOT NULL
              AND tq.concurso_id IS NOT NULL
              AND r.concurso_id <> tq.concurso_id
            """
        ).fetchone()[0])
        if revisao_perfil_mismatch:
            findings.append(_finding(
                "erro", "revisao_perfil_divergente", "Revisões com linhagem divergente",
                "Há revisão associada a tentativas de outro perfil.", revisao_perfil_mismatch,
            ))

        revisao_orfa = _inteiro(conexao.execute(
            """
            SELECT COUNT(*)
            FROM tentativas_questoes tq
            LEFT JOIN revisoes r ON r.id = tq.revisao_id
            WHERE tq.revisao_id IS NOT NULL AND r.id IS NULL
            """
        ).fetchone()[0])
        if revisao_orfa:
            findings.append(_finding(
                "erro", "tentativa_revisao_orfa", "Tentativas apontando para revisão inexistente",
                "A ligação tentativa -> revisão contém referências sem registro de revisão.", revisao_orfa,
            ))

        # Sessões novas finalizadas e elegíveis à integração automática.
        minimo_registro = max(1, banco.obter_configuracao_int("questoes_revisao_min_registro", 5))
        grupos_integraveis = conexao.execute(
            """
            SELECT
                sq.id,
                COALESCE(tq.topico_id_snapshot, q.topico_id) AS topico_id,
                SUBSTR(tq.respondida_em, 1, 10) AS dia,
                COUNT(*) AS respondidas,
                SUM(CASE WHEN tq.revisao_id IS NOT NULL THEN 1 ELSE 0 END) AS vinculadas
            FROM sessoes_questoes sq
            JOIN tentativas_questoes tq ON tq.sessao_id = sq.id
            LEFT JOIN questoes q ON q.id = tq.questao_id
            WHERE sq.concurso_id = ?
              AND sq.encerrado_em IS NOT NULL
              AND COALESCE(sq.versao_motor, 'sessao_legacy') <> 'sessao_legacy'
              AND COALESCE(sq.origem, '') NOT IN ('simulado', 'reforco_pos_bateria')
              AND tq.correta IS NOT NULL
            GROUP BY sq.id, topico_id, dia
            """,
            (concurso_id,),
        ).fetchall()
        falhas_integracao = 0
        for sessao_id, topico_id, dia, respondidas, vinculadas in grupos_integraveis:
            respondidas = _inteiro(respondidas)
            vinculadas = _inteiro(vinculadas)
            if topico_id is None or not dia or respondidas <= 0:
                continue

            controle = conexao.execute(
                "SELECT COALESCE(revisoes_iniciais, 0) FROM controle_topico WHERE topico_id = ?",
                (int(topico_id),),
            ).fetchone()
            revisoes_iniciais = _inteiro(controle[0] if controle else 0)
            revisao_anterior = _inteiro(conexao.execute(
                """
                SELECT COUNT(*) FROM revisoes
                WHERE topico_id = ? AND concurso_id = ? AND data < ?
                """,
                (int(topico_id), concurso_id, str(dia)),
            ).fetchone()[0])
            primeiro_contato = revisoes_iniciais + revisao_anterior == 0
            deveria_integrar = primeiro_contato or respondidas >= minimo_registro
            if deveria_integrar and vinculadas < respondidas:
                falhas_integracao += 1

        if falhas_integracao:
            findings.append(_finding(
                "erro", "integracao_revisao_incompleta", "Sessões finalizadas sem consolidação completa",
                "Há grupos de respostas que deveriam ter sido consolidados em revisão automática, mas ainda possuem tentativas sem revisao_id.",
                falhas_integracao,
            ))

        # Agendamentos inválidos e revisões vencidas no universo ativo do perfil.
        agendamentos = conexao.execute(
            """
            SELECT ct.topico_id, ct.proxima_revisao
            FROM controle_topico ct
            JOIN topico_concurso_importancia tc
              ON tc.topico_id = ct.topico_id AND tc.concurso_id = ?
            JOIN topicos t ON t.id = ct.topico_id
            JOIN disciplina_concurso_inclusao dc
              ON dc.disciplina_id = t.disciplina_id AND dc.concurso_id = ?
            WHERE COALESCE(tc.incluido, 0) = 1
              AND COALESCE(tc.pausado, 0) = 0
              AND COALESCE(dc.incluido, 0) = 1
              AND COALESCE(dc.pausado, 0) = 0
              AND ct.proxima_revisao IS NOT NULL
              AND TRIM(ct.proxima_revisao) <> ''
            """,
            (concurso_id, concurso_id),
        ).fetchall()
        invalidos = sum(1 for _, valor in agendamentos if not _data_iso_valida(valor))
        vencidos = sum(
            1 for _, valor in agendamentos
            if _data_iso_valida(valor) and str(valor)[:10] <= hoje
        )
        if invalidos:
            findings.append(_finding(
                "erro", "agendamento_invalido", "Datas de revisão inválidas",
                "Há proxima_revisao que não pode ser interpretada como data ISO.", invalidos,
            ))

        # Contagens brutas usadas para confrontar o núcleo estatístico.
        bruto = conexao.execute(
            """
            SELECT
                COUNT(*) AS respondidas,
                SUM(CASE WHEN correta = 1 THEN 1 ELSE 0 END) AS acertos
            FROM tentativas_questoes
            WHERE concurso_id = ? AND correta IS NOT NULL
            """,
            (concurso_id,),
        ).fetchone()
        bruto_respondidas = _inteiro(bruto[0])
        bruto_acertos = _inteiro(bruto[1])

        legado_revisoes = _inteiro(conexao.execute(
            "SELECT COUNT(*) FROM revisoes WHERE concurso_id IS NULL"
        ).fetchone()[0])
        revisoes_perfil = _inteiro(conexao.execute(
            "SELECT COUNT(*) FROM revisoes WHERE concurso_id = ?",
            (concurso_id,),
        ).fetchone()[0])

    # O núcleo estatístico é consultado fora da conexão para reutilizar sua API oficial.
    metricas = banco.obter_metricas_globais_nucleo(concurso_id).get("metrics", {})
    nucleo_respondidas = _inteiro((metricas.get("answered_attempt_count") or {}).get("value"))
    nucleo_acertos = _inteiro((metricas.get("correct_attempt_count") or {}).get("value"))
    if nucleo_respondidas != bruto_respondidas or nucleo_acertos != bruto_acertos:
        findings.append(_finding(
            "erro", "nucleo_diverge_eventos", "Núcleo estatístico diverge dos eventos brutos",
            (
                f"Eventos: {bruto_respondidas} respondidas / {bruto_acertos} acertos; "
                f"núcleo: {nucleo_respondidas} / {nucleo_acertos}."
            ),
            abs(nucleo_respondidas - bruto_respondidas) + abs(nucleo_acertos - bruto_acertos),
        ))

    if legado_revisoes:
        findings.append(_finding(
            "atencao", "revisoes_legadas_sem_perfil", "Revisões históricas sem linhagem explícita",
            (
                "Esses registros são anteriores ao marco de migração e permanecem deliberadamente "
                "fora das métricas por perfil quando a linhagem não pode ser provada."
            ),
            legado_revisoes,
        ))

    if not findings:
        findings.append(_finding(
            "ok", "ciclo_integro", "Ciclo principal íntegro",
            "Nenhuma inconsistência estrutural foi encontrada na auditoria atual.",
        ))
    elif not any(item["nivel"] == "erro" for item in findings):
        findings.insert(0, _finding(
            "ok", "ciclo_sem_erro", "Ciclo principal sem erro estrutural",
            "A auditoria encontrou apenas limitações históricas/avisos, sem falha nova do ciclo.",
        ))

    findings.sort(key=lambda item: (-NIVEL_ORDEM.get(item["nivel"], 0), item["codigo"]))
    erros = sum(1 for item in findings if item["nivel"] == "erro")
    atencoes = sum(1 for item in findings if item["nivel"] == "atencao")
    status = "erro" if erros else "atencao" if atencoes else "ok"

    return {
        "status": status,
        "concurso_id": concurso_id,
        "concurso_nome": concurso_nome,
        "data_referencia": hoje,
        "findings": findings,
        "erros": erros,
        "atencoes": atencoes,
        "metricas": {
            "respondidas_eventos": bruto_respondidas,
            "acertos_eventos": bruto_acertos,
            "respondidas_nucleo": nucleo_respondidas,
            "acertos_nucleo": nucleo_acertos,
            "revisoes_com_linhagem": revisoes_perfil,
            "revisoes_legadas_sem_linhagem": legado_revisoes,
            "revisoes_vencidas_ativas": vencidos,
        },
        "sessoes_recentes": sessoes_recentes,
        "marco_linhagem_revisoes": base_linhagem,
    }


def texto_auditoria_ciclo(dados: dict) -> str:
    rotulo_status = {
        "ok": "OK",
        "atencao": "ATENÇÃO",
        "erro": "ERRO",
    }.get(str(dados.get("status") or ""), "—")
    m = dados.get("metricas") or {}
    linhas = [
        "AUDITORIA DO CICLO DE ESTUDO",
        f"Status: {rotulo_status}",
        f"Perfil: {dados.get('concurso_nome')} (id {dados.get('concurso_id')})",
        f"Data de referência: {dados.get('data_referencia')}",
        "",
        "Cadeia auditada: recomendação/sessão -> tentativas -> revisão -> métricas -> próximo agendamento.",
        "",
        "Métricas de controle",
        f"- Respostas brutas: {m.get('respondidas_eventos', 0)}",
        f"- Acertos brutos: {m.get('acertos_eventos', 0)}",
        f"- Núcleo estatístico: {m.get('respondidas_nucleo', 0)} respostas / {m.get('acertos_nucleo', 0)} acertos",
        f"- Revisões com linhagem do perfil: {m.get('revisoes_com_linhagem', 0)}",
        f"- Revisões históricas sem linhagem: {m.get('revisoes_legadas_sem_linhagem', 0)}",
        f"- Revisões vencidas/para hoje no universo ativo: {m.get('revisoes_vencidas_ativas', 0)}",
        "",
        "Verificações",
    ]
    for item in dados.get("findings") or []:
        prefixo = {"ok": "[OK]", "atencao": "[ATENÇÃO]", "erro": "[ERRO]"}.get(item.get("nivel"), "[-]")
        quantidade = int(item.get("quantidade") or 0)
        sufixo = f" ({quantidade})" if quantidade else ""
        linhas.append(f"{prefixo} {item.get('titulo')}{sufixo}")
        linhas.append(f"    {item.get('detalhe')}")

    recentes = dados.get("sessoes_recentes") or []
    linhas += ["", "Sessões recentes"]
    if not recentes:
        linhas.append("- Nenhuma sessão de questões encontrada neste perfil.")
    else:
        for sessao in recentes:
            desempenho = sessao.get("desempenho")
            desempenho_txt = f"{desempenho:.0f}%" if desempenho is not None else "—"
            linhas.append(
                f"- #{sessao.get('id')} • {sessao.get('origem')} • {sessao.get('modo')} • "
                f"{sessao.get('respondidas')}/{sessao.get('objetivo')} respondidas • {desempenho_txt} • "
                f"revisão {sessao.get('vinculadas_revisao')}/{sessao.get('respondidas')}"
            )
    return "\n".join(linhas)


def texto_recomendacao_diagnostica(recomendacao: dict | None) -> str:
    rec = dict(recomendacao or {})
    if not rec:
        return "RECOMENDAÇÃO ATUAL\nSem recomendação disponível."
    eixos = rec.get("eixos_v5") or {}
    linhas = [
        "RECOMENDAÇÃO ATUAL — MOTOR V5",
        f"Disciplina: {rec.get('disciplina') or '—'}",
        f"Tópico: {rec.get('topico') or '—'}",
        f"Origem: {rec.get('origem') or '—'}",
        f"Score total: {float(rec.get('score_total') or 0.0):.1f}",
        (
            "Eixos: urgência " + f"{float(eixos.get('urgencia') or 0.0):.1f}" +
            " • necessidade " + f"{float(eixos.get('necessidade') or 0.0):.1f}" +
            " • momento " + f"{float(eixos.get('momento') or 0.0):.1f}"
        ),
        f"Critério: {rec.get('criterio_selecao_v5') or '—'}",
    ]
    evidencias = rec.get("evidencias_objetivas") or []
    if evidencias:
        linhas.append("Evidências principais:")
        for item in evidencias[:6]:
            linhas.append(f"- {item.get('rotulo')}: {item.get('valor')} — {item.get('detalhe')}")
    ranking = rec.get("ranking_resumo") or []
    if ranking:
        linhas.append("Ranking auditável (top 5):")
        for item in ranking[:5]:
            marca = "*" if item.get("selecionado") else " "
            linhas.append(
                f"{marca} {item.get('posicao_global') or '—'}. {item.get('disciplina') or '—'} • "
                f"{item.get('topico') or '—'} • score {float(item.get('score_total') or 0.0):.1f}"
            )
    return "\n".join(linhas)
