"""Fila candidata baseada no Nucleo Estatistico, exclusivamente em modo sombra.

Este modulo e deliberadamente puro: nao consulta banco, nao persiste telemetria
e nao escolhe o que o usuario estudara. Ele recebe a Fila Inteligente V3 ja
calculada e os DTOs oficiais carregados em lote, produzindo apenas comparacao.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

ACTIVE_QUEUE_VERSION = "fila_inteligente_v3"
SHADOW_QUEUE_VERSION = "fila_candidate_shadow_v1"
USED_FOR_QUEUE_ORDER = False

ACADEMIC_COMPONENTS = {
    "dominio",
    "erros_recentes",
    "queda",
    "cobertura",
    "revisoes",
}
OPERATIONAL_COMPONENTS = {"atraso", "espacamento"}
USER_CONFIGURATION_COMPONENTS = {"importancia"}

COMPONENT_LABELS = {
    "atraso": "atraso da revisao",
    "dominio": "dominio baixo",
    "erros_recentes": "erros recentes",
    "queda": "queda acentuada",
    "importancia": "importancia",
    "cobertura": "cobertura insuficiente",
    "revisoes": "poucas revisoes",
    "espacamento": "espacamento",
}

DIVERGENCE_CLASSIFICATION = {
    "dominio": ("formula_change", True),
    "erros_recentes": ("unexpected_requires_investigation", False),
    "queda": ("temporal_window_and_formula_change", True),
    "cobertura": ("unexpected_population_difference", False),
    "revisoes": ("review_lineage_difference", True),
    "atraso": ("unexpected_operational_difference", False),
    "importancia": ("unexpected_user_configuration_difference", False),
    "espacamento": ("unexpected_operational_difference", False),
}


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def _metric(metrics: Any, metric_id: str) -> Any | None:
    if metrics is None:
        return None
    try:
        return metrics.metric(metric_id)
    except (AttributeError, KeyError):
        return None


def _review_score(review_count: int) -> float:
    count = max(0, int(review_count))
    return {0: 100.0, 1: 78.0, 2: 58.0, 3: 40.0, 4: 24.0}.get(
        count,
        12.0,
    )


def _decline_score(delta_pp: float, moderate: float, strong: float) -> float:
    decline = max(0.0, -float(delta_pp))
    moderate = float(moderate)
    strong = float(strong)
    if decline < 5.0:
        score = 0.0
    elif decline < moderate:
        score = 40.0 * (decline - 5.0) / max(1.0, moderate - 5.0)
    elif decline < strong:
        score = 40.0 + 60.0 * (decline - moderate) / max(
            1.0,
            strong - moderate,
        )
    else:
        score = 100.0
    return _clamp(score)


def _level(score: float) -> str:
    if score >= 80.0:
        return "MUITO ALTA"
    if score >= 60.0:
        return "ALTA"
    if score >= 40.0:
        return "MÉDIA"
    return "BAIXA"


def _active_component(active_item: Mapping[str, Any], component: str) -> float:
    components = dict(active_item.get("componentes_fila") or {})
    value = components.get(component)
    return _clamp(0.0 if value is None else float(value))


def _component_record(
    *,
    raw_value: Any,
    normalized_score: float,
    weight: float,
    source: str,
    state: str = "ok",
    metric_version: str | None = None,
    fallback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    score = _clamp(normalized_score)
    contribution = score * float(weight) / 100.0
    return {
        "raw_value": raw_value,
        "normalized_score": round(score, 1),
        "weight": float(weight),
        "contribution": round(contribution, 2),
        "source": source,
        "state": state,
        "metric_version": metric_version,
        "fallback": fallback,
    }


def build_shadow_candidate(
    active_item: Mapping[str, Any],
    official_metrics: Any,
    *,
    decline_moderate: float,
    decline_strong: float,
) -> dict[str, Any]:
    """Calcula um candidato sem modificar nem reinterpretar a fila ativa."""

    active_item = dict(active_item or {})
    weights = {
        key: float(value)
        for key, value in dict(active_item.get("pesos_fila") or {}).items()
    }
    fallbacks: list[dict[str, Any]] = []
    warnings: list[str] = []
    components: dict[str, dict[str, Any]] = {}

    def active_record(component: str, source: str) -> dict[str, Any]:
        value = _active_component(active_item, component)
        return _component_record(
            raw_value=value,
            normalized_score=value,
            weight=weights[component],
            source=source,
        )

    # Estados operacionais e configuracao permanecem identicos a V3.
    components["atraso"] = active_record("atraso", "operational_schedule_v3")
    components["espacamento"] = active_record(
        "espacamento",
        "operational_spacing_v3",
    )
    components["importancia"] = active_record(
        "importancia",
        "user_importance_configuration",
    )

    mastery = _metric(official_metrics, "mastery_score")
    evidence = _metric(official_metrics, "evidence_level")
    coverage = _metric(official_metrics, "question_coverage_rate")
    trend = _metric(official_metrics, "performance_trend")
    reviews = _metric(official_metrics, "completed_review_count")

    evidence_level = evidence.value if evidence is not None else "unavailable"
    evidence_order = (
        int(evidence.parameters.get("order", 0) or 0)
        if evidence is not None
        else 0
    )

    if mastery is not None and mastery.value is not None:
        mastery_value = _clamp(float(mastery.value))
        components["dominio"] = _component_record(
            raw_value=mastery_value,
            normalized_score=100.0 - mastery_value,
            weight=weights["dominio"],
            source="statistics_core.mastery_score",
            state=mastery.state,
            metric_version=mastery.metric_version,
        )
        if evidence_level == "low":
            warnings.append("provisional_mastery_low_evidence")
    else:
        legacy_value = active_item.get("dominio")
        if mastery is None:
            reason = "official_mastery_unavailable"
        elif mastery.state == "insufficient_data":
            reason = "official_mastery_insufficient_evidence"
        else:
            reason = "official_mastery_missing_value"
        fallback = {
            "reason": reason,
            "source": "legacy_domain_v2",
            "value": legacy_value,
        }
        fallbacks.append({"component": "dominio", **fallback})
        components["dominio"] = _component_record(
            raw_value=None,
            normalized_score=_active_component(active_item, "dominio"),
            weight=weights["dominio"],
            source="fallback.legacy_domain_v2",
            state=mastery.state if mastery is not None else "unavailable",
            metric_version=mastery.metric_version if mastery is not None else None,
            fallback=fallback,
        )

    error_control = (
        dict(mastery.parameters.get("error_control") or {})
        if mastery is not None
        else {}
    )
    if "score" in error_control:
        control = _clamp(float(error_control["score"]))
        critical = int(error_control.get("critical", 0) or 0)
        recurring = int(error_control.get("recurring", 0) or 0)
        recovering = int(error_control.get("recovering", 0) or 0)
        error_score = max(
            100.0 - control,
            min(100.0, critical * 45.0 + recurring * 28.0 + recovering * 12.0),
        )
        components["erros_recentes"] = _component_record(
            raw_value={
                "error_control": control,
                "critical": critical,
                "recurring": recurring,
                "recovering": recovering,
                "recovered": int(error_control.get("recovered", 0) or 0),
            },
            normalized_score=error_score,
            weight=weights["erros_recentes"],
            source="statistics_core.mastery_score.error_control",
            state=mastery.state,
            metric_version=mastery.metric_version,
        )
    else:
        if mastery is None:
            reason = "official_error_control_unavailable"
        elif mastery.state == "insufficient_data":
            reason = "official_error_control_insufficient_evidence"
        else:
            reason = "official_error_control_missing_parameters"
        fallback = {
            "reason": reason,
            "source": "fila_inteligente_v3",
            "value": _active_component(active_item, "erros_recentes"),
        }
        fallbacks.append({"component": "erros_recentes", **fallback})
        components["erros_recentes"] = _component_record(
            raw_value=None,
            normalized_score=fallback["value"],
            weight=weights["erros_recentes"],
            source="fallback.fila_inteligente_v3",
            state="unavailable",
            fallback=fallback,
        )

    trend_parameters = dict(trend.parameters or {}) if trend is not None else {}
    trend_delta = trend_parameters.get("trend_delta_pp")
    if trend is not None and trend.state == "ok" and trend_delta is not None:
        components["queda"] = _component_record(
            raw_value=float(trend_delta),
            normalized_score=_decline_score(
                float(trend_delta),
                decline_moderate,
                decline_strong,
            ),
            weight=weights["queda"],
            source="statistics_core.performance_trend",
            state=trend.state,
            metric_version=trend.metric_version,
        )
    else:
        if trend is None:
            reason = "official_trend_unavailable"
        elif trend.state == "insufficient_data":
            reason = "official_trend_insufficient_window"
        else:
            reason = "official_trend_missing_delta"
        fallback = {
            "reason": reason,
            "source": "fila_inteligente_v3.legacy_decline",
            "value": _active_component(active_item, "queda"),
        }
        fallbacks.append({"component": "queda", **fallback})
        components["queda"] = _component_record(
            raw_value=None,
            normalized_score=fallback["value"],
            weight=weights["queda"],
            source="fallback.fila_inteligente_v3.legacy_decline",
            state=trend.state if trend is not None else "unavailable",
            metric_version=trend.metric_version if trend is not None else None,
            fallback=fallback,
        )

    if coverage is not None and coverage.value is not None:
        coverage_value = _clamp(float(coverage.value))
        components["cobertura"] = _component_record(
            raw_value=coverage_value,
            normalized_score=100.0 - coverage_value,
            weight=weights["cobertura"],
            source="statistics_core.question_coverage_rate",
            state=coverage.state,
            metric_version=coverage.metric_version,
        )
    else:
        if coverage is None:
            reason = "official_coverage_unavailable"
        elif coverage.state == "insufficient_data":
            reason = "official_coverage_insufficient_data"
        else:
            reason = "official_coverage_missing_value"
        fallback = {
            "reason": reason,
            "source": "fila_inteligente_v3.legacy_coverage",
            "value": _active_component(active_item, "cobertura"),
        }
        fallbacks.append({"component": "cobertura", **fallback})
        components["cobertura"] = _component_record(
            raw_value=None,
            normalized_score=fallback["value"],
            weight=weights["cobertura"],
            source="fallback.fila_inteligente_v3.legacy_coverage",
            state=coverage.state if coverage is not None else "unavailable",
            metric_version=coverage.metric_version if coverage is not None else None,
            fallback=fallback,
        )

    active_review_count = int(active_item.get("revisoes_totais") or 0)
    official_review_count = (
        int(reviews.value)
        if reviews is not None and reviews.value is not None
        else None
    )
    reviews_certified = (
        reviews is not None
        and reviews.state == "ok"
        and official_review_count == active_review_count
    )
    if reviews_certified:
        components["revisoes"] = _component_record(
            raw_value=official_review_count,
            normalized_score=_review_score(official_review_count),
            weight=weights["revisoes"],
            source="statistics_core.completed_review_count",
            state=reviews.state,
            metric_version=reviews.metric_version,
        )
    else:
        reason = (
            "review_lineage_legacy_limited"
            if reviews is not None and reviews.state == "legacy_limited"
            else "legacy_initial_or_unqualified_review_count"
        )
        fallback = {
            "reason": reason,
            "source": "fila_inteligente_v3.legacy_review_count",
            "value": active_review_count,
            "official_value": official_review_count,
        }
        fallbacks.append({"component": "revisoes", **fallback})
        components["revisoes"] = _component_record(
            raw_value=official_review_count,
            normalized_score=_active_component(active_item, "revisoes"),
            weight=weights["revisoes"],
            source="fallback.fila_inteligente_v3.legacy_review_count",
            state=reviews.state if reviews is not None else "unavailable",
            metric_version=reviews.metric_version if reviews is not None else None,
            fallback=fallback,
        )

    contributions = {
        key: float(record["contribution"])
        for key, record in components.items()
    }
    score = round(
        _clamp(
            sum(
                float(record["normalized_score"])
                * float(record["weight"])
                / 100.0
                for record in components.values()
            )
        ),
        1,
    )
    principal = max(
        components,
        key=lambda key: (
            contributions[key],
            float(components[key]["weight"]),
        ),
    )
    official_snapshot = {}
    for metric_id in (
        "mastery_score",
        "evidence_level",
        "question_coverage_rate",
        "performance_trend",
        "completed_review_count",
        "recent_performance_rate",
        "critical_open_error_count",
    ):
        result = _metric(official_metrics, metric_id)
        official_snapshot[metric_id] = (
            {
                "value": result.value,
                "state": result.state,
                "metric_version": result.metric_version,
                "warnings": list(result.warnings),
            }
            if result is not None
            else {
                "value": None,
                "state": "unavailable",
                "metric_version": None,
                "warnings": [],
            }
        )

    return {
        "topico_id": int(active_item["topico_id"]),
        "disciplina": active_item.get("disciplina"),
        "topico": active_item.get("topico"),
        "importancia": int(active_item.get("importancia") or 3),
        "active_queue_version": ACTIVE_QUEUE_VERSION,
        "candidate_queue_version": SHADOW_QUEUE_VERSION,
        "score_candidate": score,
        "level_candidate": _level(score),
        "main_reason_key_candidate": principal,
        "main_reason_candidate": COMPONENT_LABELS[principal],
        "components_candidate": {
            key: float(record["normalized_score"])
            for key, record in components.items()
        },
        "component_details_candidate": components,
        "contributions_candidate": contributions,
        "weights_candidate": weights,
        "official_metrics": official_snapshot,
        "evidence_level": evidence_level,
        "evidence_order": evidence_order,
        "fallbacks": fallbacks,
        "warnings": warnings,
        "used_for_queue_order": USED_FOR_QUEUE_ORDER,
    }


def compare_shadow_queue(
    active_items: Iterable[Mapping[str, Any]],
    metrics_by_topic: Mapping[int, Any],
    *,
    decline_moderate: float,
    decline_strong: float,
) -> dict[str, Any]:
    """Compara ordens sem permitir que a ordem candidata escape ao consumidor."""

    active = [dict(item) for item in active_items]
    candidates = [
        build_shadow_candidate(
            item,
            metrics_by_topic.get(int(item["topico_id"])),
            decline_moderate=decline_moderate,
            decline_strong=decline_strong,
        )
        for item in active
    ]
    candidates.sort(
        key=lambda item: (
            -float(item["score_candidate"]),
            -int(item["importancia"]),
            str(item.get("disciplina") or "").lower(),
            str(item.get("topico") or "").lower(),
        )
    )

    active_positions = {
        int(item["topico_id"]): position
        for position, item in enumerate(active, 1)
    }
    candidate_positions = {
        int(item["topico_id"]): position
        for position, item in enumerate(candidates, 1)
    }
    candidate_by_topic = {
        int(item["topico_id"]): item
        for item in candidates
    }
    active_by_topic = {
        int(item["topico_id"]): item
        for item in active
    }

    comparisons = []
    for item in active:
        topic_id = int(item["topico_id"])
        candidate = candidate_by_topic[topic_id]
        active_components = dict(item.get("componentes_fila") or {})
        component_deltas = {
            key: round(
                float(candidate["components_candidate"].get(key, 0.0))
                - float(active_components.get(key, 0.0)),
                1,
            )
            for key in candidate["components_candidate"]
        }
        relevant = []
        for key, delta in component_deltas.items():
            if abs(delta) < 0.1:
                continue
            classification, expected = DIVERGENCE_CLASSIFICATION[key]
            relevant.append(
                {
                    "component": key,
                    "delta": delta,
                    "classification": classification,
                    "expected": expected,
                }
            )
        comparisons.append({
            "topico_id": topic_id,
            "disciplina": item.get("disciplina"),
            "topico": item.get("topico"),
            "active_position": active_positions[topic_id],
            "active_score": float(item.get("score_fila") or 0.0),
            "candidate_position": candidate_positions[topic_id],
            "candidate_score": float(candidate["score_candidate"]),
            "position_delta": active_positions[topic_id] - candidate_positions[topic_id],
            "score_delta": round(
                float(candidate["score_candidate"])
                - float(item.get("score_fila") or 0.0),
                1,
            ),
            "active_components": active_components,
            "candidate_components": candidate["components_candidate"],
            "candidate_component_details": candidate["component_details_candidate"],
            "component_deltas": component_deltas,
            "active_main_reason": item.get("motivo_fila"),
            "candidate_main_reason": candidate["main_reason_candidate"],
            "official_metrics": candidate["official_metrics"],
            "evidence_level": candidate["evidence_level"],
            "fallbacks": candidate["fallbacks"],
            "warnings": candidate["warnings"],
            "relevant_differences": relevant,
            "active_queue_version": ACTIVE_QUEUE_VERSION,
            "candidate_queue_version": SHADOW_QUEUE_VERSION,
            "used_for_queue_order": USED_FOR_QUEUE_ORDER,
        })

    total = len(active)
    position_deltas = [abs(item["position_delta"]) for item in comparisons]
    same_position = sum(1 for item in comparisons if item["position_delta"] == 0)

    def top_intersection(limit: int) -> dict[str, Any]:
        effective = min(limit, total)
        active_ids = [int(item["topico_id"]) for item in active[:effective]]
        candidate_ids = [
            int(item["topico_id"])
            for item in candidates[:effective]
        ]
        intersection = len(set(active_ids) & set(candidate_ids))
        return {
            "requested_n": limit,
            "effective_n": effective,
            "active": active_ids,
            "candidate": candidate_ids,
            "intersection_count": intersection,
            "intersection_rate": (
                round(100.0 * intersection / effective, 1)
                if effective
                else None
            ),
        }

    rises = sorted(comparisons, key=lambda item: item["position_delta"], reverse=True)
    falls = sorted(comparisons, key=lambda item: item["position_delta"])
    return {
        "active_queue_version": ACTIVE_QUEUE_VERSION,
        "candidate_queue_version": SHADOW_QUEUE_VERSION,
        "used_for_queue_order": USED_FOR_QUEUE_ORDER,
        "active_order": [int(item["topico_id"]) for item in active],
        "candidate_order": [int(item["topico_id"]) for item in candidates],
        "comparisons": comparisons,
        "summary": {
            "topics_evaluated": total,
            "same_position_count": same_position,
            "same_position_rate": round(100.0 * same_position / total, 1) if total else None,
            "mean_absolute_position_delta": (
                round(sum(position_deltas) / total, 3)
                if total
                else None
            ),
            "largest_rise": rises[0] if rises else None,
            "largest_fall": falls[0] if falls else None,
            "top_1": top_intersection(1),
            "top_3": top_intersection(3),
            "top_5": top_intersection(5),
            "top_10": top_intersection(10),
            "fallback_topic_count": sum(
                1
                for item in comparisons
                if item["fallbacks"]
            ),
            "fallback_component_count": sum(
                len(item["fallbacks"])
                for item in comparisons
            ),
        },
        "candidates_by_topic": candidate_by_topic,
        "active_by_topic": active_by_topic,
    }
