"""Snapshot de apresentação do Progresso do Edital V2.

Este módulo não consulta nem persiste dados. Ele transforma métricas oficiais
do Núcleo Estatístico em uma visão única para Dashboard e aba Progresso, sem
misturar cobertura, evidência, domínio e consolidação.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any

EVIDENCE_LABELS = {
    "insufficient": "Insuficiente",
    "low": "Baixa",
    "moderate": "Moderada",
    "high": "Alta",
}
EVIDENCE_ORDER = {
    "insufficient": 0,
    "low": 1,
    "moderate": 2,
    "high": 3,
}

PRESENTATION_CONSOLIDATING_RULE_VERSION = "presentation_consolidating_v1"
PRESENTATION_CONSOLIDATING_RULE = (
    "Tópico iniciado, com evidência moderada/alta, domínio oficial >= 70 "
    "e consolidação oficial ainda não atingida. É estado visual, não métrica."
)

MIN_FORECAST_EVENTS = 4
MIN_FORECAST_DISTINCT_DAYS = 3
MIN_FORECAST_SPAN_DAYS = 7


@dataclass(frozen=True)
class SyllabusProgressSnapshot:
    concurso_id: int
    total_topics: int
    started_topics: int
    topic_coverage_rate: float | None
    question_coverage_rate: float | None
    insufficient_evidence_topics: int
    low_evidence_topics: int
    moderate_evidence_topics: int
    high_evidence_topics: int
    sufficient_evidence_topics: int
    sufficient_evidence_rate: float | None
    consolidated_topics: int
    consolidated_rate: float | None
    global_mastery_score: float | None
    global_mastery_state: str
    disciplinas: list[dict[str, Any]] = field(default_factory=list)
    topicos: list[dict[str, Any]] = field(default_factory=list)
    gaps: dict[str, int] = field(default_factory=dict)
    generated_at: str = ""
    snapshot_version: str = "syllabus_progress_v2"
    consolidating_rule_version: str = PRESENTATION_CONSOLIDATING_RULE_VERSION
    consolidating_rule: str = PRESENTATION_CONSOLIDATING_RULE

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _metric(scope_metrics, metric_id: str):
    return scope_metrics.metric(metric_id)


def _value(scope_metrics, metric_id: str, default=None):
    return scope_metrics.value(metric_id, default)


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return 100.0 * numerator / denominator


def _presentation_state(attempts, consolidation, evidence, mastery):
    if int(attempts or 0) <= 0:
        return "Não iniciado", 0
    if consolidation == "consolidated":
        return "Consolidado", 3
    if (
        consolidation == "not_consolidated"
        and EVIDENCE_ORDER.get(str(evidence), 0) >= 2
        and mastery is not None
        and float(mastery) >= 70.0
    ):
        return "Em consolidação", 2
    return "Em andamento", 1


def _topic_item(catalog: dict[str, Any], metrics) -> dict[str, Any]:
    evidence_metric = _metric(metrics, "evidence_level")
    mastery_metric = _metric(metrics, "mastery_score")
    coverage_metric = _metric(metrics, "question_coverage_rate")
    consolidation_metric = _metric(metrics, "topic_consolidation_status")
    review_metric = _metric(metrics, "completed_review_count")

    evidence = str(evidence_metric.value or "insufficient")
    mastery = mastery_metric.value
    consolidation = consolidation_metric.value
    attempts = int(_value(metrics, "answered_attempt_count", 0) or 0)
    state, state_order = _presentation_state(
        attempts,
        consolidation,
        evidence,
        mastery,
    )

    mastery_parameters = dict(mastery_metric.parameters or {})
    error_control = dict(mastery_parameters.get("error_control") or {})
    last_review = _value(metrics, "last_review_at")
    next_review = catalog.get("proxima_revisao")
    today = datetime.now(timezone.utc).date().isoformat()
    overdue = bool(next_review and str(next_review)[:10] < today)

    gaps = []
    if attempts <= 0:
        gaps.append("not_started")
    elif evidence == "insufficient":
        gaps.append("started_insufficient_evidence")
    elif evidence == "low":
        gaps.append("low_evidence")
    if evidence in {"moderate", "high"} and consolidation == "not_consolidated":
        gaps.append("sufficient_evidence_not_consolidated")
    if overdue:
        gaps.append("overdue_review")

    return {
        "topico_id": int(catalog["topico_id"]),
        "disciplina_id": int(catalog["disciplina_id"]),
        "disciplina": str(catalog["disciplina"]),
        "topico": str(catalog["topico"]),
        "importancia": int(catalog.get("importancia") or 3),
        "estado": state,
        "ordem_estado": state_order,
        "estado_regra": (
            PRESENTATION_CONSOLIDATING_RULE_VERSION
            if state == "Em consolidação"
            else None
        ),
        "tentativas": attempts,
        "questoes_unicas": int(
            _value(metrics, "answered_unique_question_count", 0) or 0
        ),
        "percentual": _value(metrics, "accuracy_rate"),
        "desempenho_recente": _value(metrics, "recent_performance_rate"),
        "tendencia_desempenho": _value(metrics, "performance_trend"),
        "cobertura_questoes": coverage_metric.value,
        "questoes_ativas": int(coverage_metric.denominator or 0),
        "questoes_respondidas": int(
            coverage_metric.parameters.get("answered_active_questions", 0) or 0
        ),
        "evidencia": evidence,
        "evidencia_rotulo": EVIDENCE_LABELS.get(evidence, "Insuficiente"),
        "evidencia_ordem": EVIDENCE_ORDER.get(evidence, 0),
        "evidencia_suficiente": evidence in {"moderate", "high"},
        "dominio_score": mastery,
        "dominio_estado": mastery_metric.state,
        "dominio_nivel": mastery_parameters.get(
            "level",
            "Dados insuficientes" if mastery is None else "—",
        ),
        "dominio_provisorio": evidence == "low" and mastery is not None,
        "consolidacao": consolidation,
        "consolidacao_estado": consolidation_metric.state,
        "consolidacao_certificada": consolidation == "consolidated",
        "revisoes": int(review_metric.value or 0),
        "estado_revisoes": review_metric.state,
        "ultima": str(last_review)[:10] if last_review else None,
        "ultima_atividade": _value(metrics, "last_activity_at"),
        "proxima": next_review,
        "revisao_vencida": overdue,
        "lacunas": gaps,
        # Compatibilidade de leitura para componentes que ainda usam o bloco
        # explicativo detalhado; todos os valores continuam vindo do núcleo.
        "dominio": {
            "score": mastery,
            "score_estimado": mastery_parameters.get("estimate"),
            "nivel": mastery_parameters.get("level", "Dados insuficientes"),
            "qualidade_evidencia": EVIDENCE_LABELS.get(evidence, "Insuficiente"),
            "evidence_level": evidence,
            "desempenho": mastery_parameters.get("current_performance"),
            "desempenho_recente": _value(metrics, "recent_performance_rate"),
            "tendencia": _value(metrics, "performance_trend"),
            "cobertura": coverage_metric.value,
            "estabilidade": mastery_parameters.get("temporal_stability"),
            "recencia": mastery_parameters.get("recency"),
            "controle_erros": error_control.get("score"),
            "tentativas": attempts,
            "tentativas_historicas": attempts,
            "questoes_unicas": int(
                _value(metrics, "answered_unique_question_count", 0) or 0
            ),
            "dias_ativos_historicos": int(
                evidence_metric.parameters.get("active_days", 0) or 0
            ),
            "taxa_duvida": mastery_parameters.get("doubt_rate"),
            "recorrentes": int(error_control.get("recurring", 0) or 0),
            "criticas": int(error_control.get("critical", 0) or 0),
            "recuperadas": int(error_control.get("recovered", 0) or 0),
        },
    }


def build_syllabus_progress_snapshot(
    concurso_id: int,
    catalog_topics: list[dict[str, Any]],
    topic_metrics: dict[int, Any],
    subject_metrics: dict[int, Any],
    global_metrics: Any,
    generated_at: str | None = None,
) -> SyllabusProgressSnapshot:
    """Monta o snapshot sem médias de percentuais e sem consultas adicionais."""
    topics = [
        _topic_item(item, topic_metrics[int(item["topico_id"])])
        for item in catalog_topics
    ]
    topics.sort(
        key=lambda item: (
            item["disciplina"].casefold(),
            item["topico"].casefold(),
        )
    )

    evidence_counts = {
        code: sum(1 for item in topics if item["evidencia"] == code)
        for code in EVIDENCE_ORDER
    }
    sufficient = evidence_counts["moderate"] + evidence_counts["high"]
    consolidated = sum(1 for item in topics if item["consolidacao"] == "consolidated")
    started = sum(1 for item in topics if item["tentativas"] > 0)

    catalog_subjects = {}
    for item in catalog_topics:
        catalog_subjects[int(item["disciplina_id"])] = str(item["disciplina"])

    subjects = []
    for subject_id, subject_name in sorted(
        catalog_subjects.items(),
        key=lambda pair: pair[1].casefold(),
    ):
        metrics = subject_metrics[subject_id]
        subject_topics = [
            item for item in topics if item["disciplina_id"] == subject_id
        ]
        subject_sufficient = sum(
            1 for item in subject_topics if item["evidencia_suficiente"]
        )
        subject_consolidated = sum(
            1 for item in subject_topics if item["consolidacao"] == "consolidated"
        )
        subject_evidence = str(
            _value(metrics, "evidence_level", "insufficient") or "insufficient"
        )
        subjects.append({
            "disciplina_id": subject_id,
            "disciplina": subject_name,
            "total_topicos": len(subject_topics),
            "cobertura_topicos": _value(metrics, "topic_coverage_rate"),
            "cobertura_questoes": _value(metrics, "question_coverage_rate"),
            "evidencia": subject_evidence,
            "evidencia_rotulo": EVIDENCE_LABELS.get(
                subject_evidence, "Insuficiente"
            ),
            "evidencia_suficiente": subject_evidence in {"moderate", "high"},
            "evidencia_suficiente_topicos": subject_sufficient,
            "evidencia_suficiente_taxa": _rate(
                subject_sufficient,
                len(subject_topics),
            ),
            "consolidados": subject_consolidated,
            "consolidacao_taxa": _rate(subject_consolidated, len(subject_topics)),
            "dominio": _value(metrics, "mastery_score"),
            "dominio_estado": _metric(metrics, "mastery_score").state,
            "revisoes": int(_value(metrics, "completed_review_count", 0) or 0),
            "ultima_atividade": _value(metrics, "last_activity_at"),
        })

    gaps = {
        code: sum(1 for item in topics if code in item["lacunas"])
        for code in (
            "not_started",
            "started_insufficient_evidence",
            "low_evidence",
            "sufficient_evidence_not_consolidated",
            "overdue_review",
        )
    }
    total = len(topics)
    return SyllabusProgressSnapshot(
        concurso_id=int(concurso_id),
        total_topics=total,
        started_topics=started,
        topic_coverage_rate=_value(global_metrics, "topic_coverage_rate"),
        question_coverage_rate=_value(global_metrics, "question_coverage_rate"),
        insufficient_evidence_topics=evidence_counts["insufficient"],
        low_evidence_topics=evidence_counts["low"],
        moderate_evidence_topics=evidence_counts["moderate"],
        high_evidence_topics=evidence_counts["high"],
        sufficient_evidence_topics=sufficient,
        sufficient_evidence_rate=_rate(sufficient, total),
        consolidated_topics=consolidated,
        consolidated_rate=_rate(consolidated, total),
        global_mastery_score=_value(global_metrics, "mastery_score"),
        global_mastery_state=_metric(global_metrics, "mastery_score").state,
        disciplinas=subjects,
        topicos=topics,
        gaps=gaps,
        generated_at=generated_at or datetime.now().astimezone().isoformat(timespec="seconds"),
    )


def _forecast_basis(dates: list[date], weeks: int) -> dict[str, Any]:
    unique = sorted(set(dates))
    span = (unique[-1] - unique[0]).days if len(unique) >= 2 else 0
    sufficient = (
        len(dates) >= MIN_FORECAST_EVENTS
        and len(unique) >= MIN_FORECAST_DISTINCT_DAYS
        and span >= MIN_FORECAST_SPAN_DAYS
    )
    return {
        "event_count": len(dates),
        "distinct_days": len(unique),
        "span_days": span,
        "window_weeks": weeks,
        "sufficient": sufficient,
        "label": "Base suficiente" if sufficient else "Dados insuficientes para previsão",
    }


def _project(remaining: int, event_count: int, weeks: int, today: date):
    if remaining <= 0:
        return {"achieved": True, "date": None, "weeks": 0}
    rate = event_count / float(weeks)
    if rate <= 0:
        return None
    projected_weeks = remaining / rate
    projected_days = max(1, int(projected_weeks * 7.0 + 0.999999))
    return {
        "achieved": False,
        "date": (today + timedelta(days=projected_days)).isoformat(),
        "weeks": int(projected_weeks + 0.999999),
    }


def build_syllabus_forecast(
    snapshot: dict[str, Any] | SyllabusProgressSnapshot,
    events: list[dict[str, Any]],
    weeks: int = 4,
    today: date | None = None,
) -> dict[str, Any]:
    """Produz extrapolação somente quando a base temporal mínima é atendida."""
    data = snapshot.to_dict() if isinstance(snapshot, SyllabusProgressSnapshot) else snapshot
    weeks = max(1, int(weeks))
    today = today or datetime.now(timezone.utc).date()
    start = today - timedelta(days=weeks * 7 - 1)

    def collect(field):
        result = []
        for event in events:
            raw = event.get(field)
            if not raw:
                continue
            try:
                day = date.fromisoformat(str(raw)[:10])
            except ValueError:
                continue
            if start <= day <= today:
                result.append(day)
        return result

    start_dates = collect("data_inicio")
    consolidation_dates = collect("data_consolidacao")
    start_basis = _forecast_basis(start_dates, weeks)
    consolidation_basis = _forecast_basis(consolidation_dates, weeks)
    total = int(data.get("total_topics") or 0)
    started = int(data.get("started_topics") or 0)
    consolidated = int(data.get("consolidated_topics") or 0)
    target_80 = int(total * 0.8 + 0.999999) if total else 0

    coverage = (
        _project(total - started, len(start_dates), weeks, today)
        if start_basis["sufficient"] or total == started
        else None
    )
    consolidation_80 = (
        _project(max(0, target_80 - consolidated), len(consolidation_dates), weeks, today)
        if consolidation_basis["sufficient"] or consolidated >= target_80
        else None
    )
    consolidation_100 = (
        _project(total - consolidated, len(consolidation_dates), weeks, today)
        if consolidation_basis["sufficient"] or total == consolidated
        else None
    )
    scenarios = []
    for name, factor in (
        ("Conservador", 0.70),
        ("Ritmo atual", 1.00),
        ("Acelerado", 1.30),
    ):
        scenarios.append({
            "name": name,
            "factor": factor,
            "coverage_rate_per_week": len(start_dates) / float(weeks) * factor,
            "consolidation_rate_per_week": (
                len(consolidation_dates) / float(weeks) * factor
            ),
            "coverage_forecast": (
                _project(total - started, len(start_dates) * factor, weeks, today)
                if start_basis["sufficient"] or total == started
                else None
            ),
            "consolidation_80_forecast": (
                _project(
                    max(0, target_80 - consolidated),
                    len(consolidation_dates) * factor,
                    weeks,
                    today,
                )
                if consolidation_basis["sufficient"] or consolidated >= target_80
                else None
            ),
            "consolidation_100_forecast": (
                _project(
                    total - consolidated,
                    len(consolidation_dates) * factor,
                    weeks,
                    today,
                )
                if consolidation_basis["sufficient"] or total == consolidated
                else None
            ),
        })
    return {
        "window_start": start.isoformat(),
        "window_end": today.isoformat(),
        "window_weeks": weeks,
        "coverage_basis": start_basis,
        "consolidation_basis": consolidation_basis,
        "coverage_forecast": coverage,
        "consolidation_80_forecast": consolidation_80,
        "consolidation_100_forecast": consolidation_100,
        "coverage_rate_per_week": len(start_dates) / float(weeks),
        "consolidation_rate_per_week": len(consolidation_dates) / float(weeks),
        "scenarios": scenarios,
        "is_extrapolation": True,
    }
