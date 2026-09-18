"""Politicas puras para observacao e prontidao da fila candidata.

Este modulo nao acessa banco, nao altera a fila ativa e nunca decide a ordem
mostrada ao usuario. Ele apenas classifica telemetria sombra acumulada.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from fila_candidata import (
    ACTIVE_QUEUE_VERSION,
    SHADOW_QUEUE_VERSION,
    USED_FOR_QUEUE_ORDER,
)

SIGNIFICANT_SHADOW_EVENTS = frozenset({
    "manual_audit",
    "recommended_session_started",
    "study_now_explicit",
    "technical_snapshot",
})

DEFAULT_READINESS_THRESHOLDS = {
    "minimum_observations": 20,
    "minimum_distinct_days": 5,
    "minimum_distinct_topics": 5,
    "minimum_moderate_high_item_observations": 10,
    "maximum_unresolved_top3_divergences": 0,
    "maximum_temporal_protection_violations": 0,
    "maximum_ineligible_topic_violations": 0,
    "maximum_known_context_without_lineage": 0,
    "maximum_review_lineage_mismatches": 0,
}

SAMPLE_BLOCKERS = {
    "insufficient_observations",
    "insufficient_distinct_days",
    "insufficient_distinct_topics",
    "insufficient_moderate_high_evidence",
}


def observation_signature(
    snapshot: Mapping[str, Any],
    event_origin: str,
) -> str:
    """Assina apenas identidade/ordem/versoes para deduplicacao curta."""

    payload = {
        "contest_id": snapshot.get("concurso_id"),
        "event_origin": str(event_origin),
        "active_queue_version": snapshot.get("active_queue_version"),
        "candidate_queue_version": snapshot.get("candidate_queue_version"),
        "metric_version": snapshot.get("metric_version"),
        "active_order": [
            int(item["topico_id"])
            for item in snapshot.get("active_order", [])
        ],
        "candidate_order": [
            int(item["topico_id"])
            for item in snapshot.get("candidate_order", [])
        ],
        "eligible_candidate_order": [
            int(item["topico_id"])
            for item in snapshot.get("eligible_candidate_order", [])
        ],
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def summarize_snapshot_safety(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Centraliza divergencias inesperadas e violacoes de seguranca."""

    comparisons = list(snapshot.get("comparisons") or [])
    expected_count = 0
    unexpected_count = 0
    unexpected_top3_count = 0
    temporal_violations = 0

    for comparison in comparisons:
        differences = list(comparison.get("relevant_differences") or [])
        for difference in differences:
            if bool(difference.get("expected")):
                expected_count += 1
                continue
            unexpected_count += 1
            if min(
                int(comparison.get("active_position") or 10**9),
                int(comparison.get("candidate_position") or 10**9),
            ) <= 3:
                unexpected_top3_count += 1

        deltas = dict(comparison.get("component_deltas") or {})
        if any(
            abs(float(deltas.get(component, 0.0) or 0.0)) >= 0.1
            for component in ("atraso", "espacamento")
        ):
            temporal_violations += 1

    active_order = {
        int(item["topico_id"])
        for item in snapshot.get("active_order", [])
    }
    candidate_order = {
        int(item["topico_id"])
        for item in snapshot.get("candidate_order", [])
    }
    ineligible_violations = len(active_order.symmetric_difference(candidate_order))

    moderate_high_count = sum(
        1
        for item in comparisons
        if str(item.get("evidence_level") or "").lower()
        in {"moderate", "high"}
    )
    return {
        "expected_divergence_count": expected_count,
        "unexpected_divergence_count": unexpected_count,
        "unexpected_top3_count": unexpected_top3_count,
        "temporal_protection_violation_count": temporal_violations,
        "ineligible_topic_violation_count": ineligible_violations,
        "moderate_high_topic_count": moderate_high_count,
        "used_for_queue_order": USED_FOR_QUEUE_ORDER,
    }


def evaluate_queue_activation_readiness(
    observation_summary: Mapping[str, Any],
    *,
    thresholds: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    """Avalia prontidao sem ativar, ordenar ou recomendar qualquer topico."""

    criteria = dict(DEFAULT_READINESS_THRESHOLDS)
    criteria.update({
        key: int(value)
        for key, value in dict(thresholds or {}).items()
        if key in criteria
    })
    summary = dict(observation_summary or {})
    blockers: list[dict[str, Any]] = []

    def require_minimum(code: str, key: str, criterion: str) -> None:
        actual = int(summary.get(key, 0) or 0)
        required = int(criteria[criterion])
        if actual < required:
            blockers.append({
                "code": code,
                "actual": actual,
                "required": required,
            })

    def require_maximum(code: str, key: str, criterion: str) -> None:
        actual = int(summary.get(key, 0) or 0)
        maximum = int(criteria[criterion])
        if actual > maximum:
            blockers.append({
                "code": code,
                "actual": actual,
                "maximum": maximum,
            })

    require_minimum(
        "insufficient_observations",
        "observation_count",
        "minimum_observations",
    )
    require_minimum(
        "insufficient_distinct_days",
        "distinct_days",
        "minimum_distinct_days",
    )
    require_minimum(
        "insufficient_distinct_topics",
        "distinct_topics",
        "minimum_distinct_topics",
    )
    require_minimum(
        "insufficient_moderate_high_evidence",
        "moderate_high_item_observations",
        "minimum_moderate_high_item_observations",
    )
    require_maximum(
        "unresolved_unexpected_top3_divergence",
        "unexpected_top3_count",
        "maximum_unresolved_top3_divergences",
    )
    require_maximum(
        "temporal_protection_violation",
        "temporal_protection_violation_count",
        "maximum_temporal_protection_violations",
    )
    require_maximum(
        "ineligible_topic_violation",
        "ineligible_topic_violation_count",
        "maximum_ineligible_topic_violations",
    )
    require_maximum(
        "known_review_context_without_lineage",
        "known_context_without_lineage_count",
        "maximum_known_context_without_lineage",
    )
    require_maximum(
        "review_lineage_profile_mismatch",
        "review_lineage_mismatch_count",
        "maximum_review_lineage_mismatches",
    )

    warnings = []
    if int(summary.get("fallback_component_count", 0) or 0) > 0:
        warnings.append("fallbacks_still_observed")
    evidence = dict(summary.get("evidence_distribution") or {})
    if int(evidence.get("low", 0) or 0) > 0:
        warnings.append("provisional_low_evidence_observed")
    if int(evidence.get("insufficient", 0) or 0) > 0:
        warnings.append("insufficient_evidence_observed")

    ready = not blockers
    technical_blockers = [
        item for item in blockers
        if item["code"] not in SAMPLE_BLOCKERS
    ]
    if ready:
        classification = "PRONTO PARA PROPOR MIGRACAO CONTROLADA"
    elif technical_blockers:
        classification = "BLOQUEADORES TECNICOS RESTANTES"
    else:
        classification = "INFRAESTRUTURA PRONTA / AMOSTRA AINDA INSUFICIENTE"

    return {
        "ready": ready,
        "classification": classification,
        "blockers": blockers,
        "warnings": warnings,
        "observation_count": int(summary.get("observation_count", 0) or 0),
        "distinct_days": int(summary.get("distinct_days", 0) or 0),
        "distinct_topics": int(summary.get("distinct_topics", 0) or 0),
        "moderate_high_item_observations": int(
            summary.get("moderate_high_item_observations", 0) or 0
        ),
        "unexpected_top3_count": int(
            summary.get("unexpected_top3_count", 0) or 0
        ),
        "fallbacks_by_type": dict(summary.get("fallbacks_by_type") or {}),
        "review_lineage_integrity": not any(
            item["code"] in {
                "known_review_context_without_lineage",
                "review_lineage_profile_mismatch",
            }
            for item in blockers
        ),
        "active_queue_version": ACTIVE_QUEUE_VERSION,
        "candidate_queue_version": SHADOW_QUEUE_VERSION,
        "metric_version": str(summary.get("metric_version") or "1"),
        "thresholds": criteria,
        "used_for_queue_order": USED_FOR_QUEUE_ORDER,
    }
