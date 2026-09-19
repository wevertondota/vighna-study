"""Analise temporal oficial e reutilizavel do VighnaStudy.

O modulo transforma eventos brutos e metricas do Nucleo Estatistico em duas
leituras diferentes: descricao cronologica de atividade e comparacao entre
periodos equivalentes. Ele nao decide prioridade de estudo e nao modifica o
banco.
"""

from __future__ import annotations

from collections import defaultdict
from contextlib import closing
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Callable, Iterable

from statistics_core import StatisticalPeriod, StatisticalPeriods, StatisticsService
from statistics_core.periods import statistical_timezone


TEMPORAL_SNAPSHOT_VERSION = "temporal_analytics_v2"
MIN_COMPARISON_ATTEMPTS = 10
MIN_COMPARISON_ACTIVE_DAYS = 2


@dataclass(frozen=True)
class TemporalAnalyticsSnapshot:
    concurso_id: int
    current_period: dict[str, Any]
    previous_period: dict[str, Any]
    current_metrics: dict[str, Any]
    previous_metrics: dict[str, Any]
    comparisons: dict[str, Any]
    daily_series: list[dict[str, Any]]
    display_series: list[dict[str, Any]]
    subjects: list[dict[str, Any]]
    topics: list[dict[str, Any]]
    official_performance_trend: dict[str, Any]
    sufficiency: dict[str, Any]
    lineage_warnings: list[str]
    global_focus: dict[str, Any]
    progress_history: list[dict[str, Any]] = field(default_factory=list)
    generated_at: str = ""
    version: str = TEMPORAL_SNAPSHOT_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_period(
    *,
    days: int | None = None,
    start: date | datetime | None = None,
    end_inclusive: date | datetime | None = None,
    as_of: date | datetime | None = None,
) -> StatisticalPeriod:
    """Cria um periodo oficial; o fim informado pela UI e inclusivo."""
    if start is not None or end_inclusive is not None:
        if start is None or end_inclusive is None:
            raise ValueError("inicio e fim inclusivo devem ser informados juntos")
        if isinstance(end_inclusive, datetime):
            end_day = end_inclusive.date()
        else:
            end_day = end_inclusive
        return StatisticalPeriods.custom(
            start,
            end_day + timedelta(days=1),
            "custom",
        )
    days = int(days or 30)
    if days not in {7, 30, 60, 90}:
        raise ValueError("periodo deve ser 7, 30, 60 ou 90 dias")
    return StatisticalPeriods.last_days(days, as_of)


def _period_dict(period: StatisticalPeriod) -> dict[str, Any]:
    duration = period.end_exclusive - period.start if period.start else None
    return {
        "id": period.identifier,
        "start": period.start.isoformat() if period.start else None,
        "end_exclusive": period.end_exclusive.isoformat(),
        "end_inclusive": (
            (period.end_exclusive - timedelta(days=1)).date().isoformat()
            if period.start is not None
            else None
        ),
        "days": duration.days if duration is not None else None,
        "timezone": period.timezone,
    }


def _local_datetime(value: str | datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value).strip().replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return None
    timezone = statistical_timezone()
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone)
    return parsed.astimezone(timezone)


def _local_day(value: str | datetime | None) -> str | None:
    parsed = _local_datetime(value)
    return parsed.date().isoformat() if parsed is not None else None


def _metric_value(scope_metrics, metric_id: str, default=None):
    return scope_metrics.value(metric_id, default)


def _attempt_days(scope_metrics) -> int:
    evidence = scope_metrics.metric("evidence_level")
    return int((evidence.parameters or {}).get("active_days", 0) or 0)


def _summary(scope_metrics) -> dict[str, Any]:
    review = scope_metrics.metric("completed_review_count")
    accuracy = scope_metrics.metric("accuracy_rate")
    return {
        "attempts": int(_metric_value(scope_metrics, "answered_attempt_count", 0) or 0),
        "correct": int(_metric_value(scope_metrics, "correct_attempt_count", 0) or 0),
        "incorrect": int(_metric_value(scope_metrics, "incorrect_attempt_count", 0) or 0),
        "accuracy_rate": accuracy.value,
        "accuracy_state": accuracy.state,
        "unique_questions": int(
            _metric_value(scope_metrics, "answered_unique_question_count", 0) or 0
        ),
        "question_sessions": int(
            _metric_value(scope_metrics, "question_session_count", 0) or 0
        ),
        "answered_sessions": int(
            _metric_value(scope_metrics, "distinct_answered_session_count", 0) or 0
        ),
        "active_days": _attempt_days(scope_metrics),
        "study_days": int(_metric_value(scope_metrics, "study_day_count", 0) or 0),
        "qualified_reviews": int(review.value or 0),
        "review_state": review.state,
        "unattributed_legacy_reviews": int(
            (review.parameters or {}).get("unattributed_review_count", 0) or 0
        ),
        "recent_performance_rate": _metric_value(
            scope_metrics, "recent_performance_rate"
        ),
    }


def comparison_sufficiency(current: dict[str, Any], previous: dict[str, Any]) -> dict[str, Any]:
    missing = {
        "current_attempts": max(0, MIN_COMPARISON_ATTEMPTS - int(current["attempts"])),
        "previous_attempts": max(0, MIN_COMPARISON_ATTEMPTS - int(previous["attempts"])),
        "current_active_days": max(
            0, MIN_COMPARISON_ACTIVE_DAYS - int(current["active_days"])
        ),
        "previous_active_days": max(
            0, MIN_COMPARISON_ACTIVE_DAYS - int(previous["active_days"])
        ),
    }
    ready = not any(missing.values())
    return {
        "state": "ok" if ready else "insufficient_data",
        "ready": ready,
        "label": "Base suficiente" if ready else "Dados insuficientes para comparação",
        "requirements": {
            "attempts_each_period": MIN_COMPARISON_ATTEMPTS,
            "active_days_each_period": MIN_COMPARISON_ACTIVE_DAYS,
        },
        "missing": missing,
    }


def _count_delta(current: int, previous: int) -> dict[str, Any]:
    absolute = int(current) - int(previous)
    relative = None if int(previous) == 0 else 100.0 * absolute / int(previous)
    return {
        "current": int(current),
        "previous": int(previous),
        "absolute": absolute,
        "relative_percent": relative,
        "interpretation": "activity_only",
    }


def _period_comparisons(current: dict[str, Any], previous: dict[str, Any]) -> dict[str, Any]:
    sufficiency = comparison_sufficiency(current, previous)
    accuracy_delta = None
    if sufficiency["ready"]:
        accuracy_delta = float(current["accuracy_rate"]) - float(previous["accuracy_rate"])
    return {
        "accuracy": {
            "state": sufficiency["state"],
            "label": sufficiency["label"],
            "current": current["accuracy_rate"],
            "previous": previous["accuracy_rate"],
            "delta_pp": accuracy_delta,
            "missing": dict(sufficiency["missing"]),
        },
        "attempts": _count_delta(current["attempts"], previous["attempts"]),
        "unique_questions": _count_delta(
            current["unique_questions"], previous["unique_questions"]
        ),
        "question_sessions": _count_delta(
            current["question_sessions"], previous["question_sessions"]
        ),
        "qualified_reviews": _count_delta(
            current["qualified_reviews"], previous["qualified_reviews"]
        ),
        "active_days": _count_delta(current["active_days"], previous["active_days"]),
    }


def _scope_comparison(
    identifier: int,
    name: str,
    current,
    previous,
    official_current=None,
) -> dict[str, Any]:
    current_summary = _summary(current)
    previous_summary = _summary(previous)
    comparison = _period_comparisons(current_summary, previous_summary)
    official_current = official_current or current
    trend = official_current.metric("performance_trend")
    return {
        "id": int(identifier),
        "name": str(name),
        "current": current_summary,
        "previous": previous_summary,
        "comparison": comparison,
        "comparable": comparison["accuracy"]["state"] == "ok",
        "official_trend": trend.to_dict(),
        "current_mastery": official_current.value("mastery_score"),
        "current_mastery_state": official_current.metric("mastery_score").state,
    }


def _daily_series(attempts, reviews, period: StatisticalPeriod) -> list[dict[str, Any]]:
    attempts_by_day: dict[str, list[Any]] = defaultdict(list)
    reviews_by_day: dict[str, list[Any]] = defaultdict(list)
    for item in attempts:
        day = _local_day(item.occurred_at)
        if day:
            attempts_by_day[day].append(item)
    for item in reviews:
        if not item.lineage_known:
            continue
        day = _local_day(item.occurred_at)
        if day:
            reviews_by_day[day].append(item)

    result = []
    cursor = period.start.date()
    end = period.end_exclusive.date()
    while cursor < end:
        key = cursor.isoformat()
        day_attempts = attempts_by_day.get(key, [])
        correct = sum(1 for item in day_attempts if item.correct)
        result.append({
            "date": key,
            "attempts": len(day_attempts),
            "correct": correct,
            "accuracy_rate": (
                100.0 * correct / len(day_attempts) if day_attempts else None
            ),
            "unique_questions": len({
                item.question_id for item in day_attempts if item.question_id is not None
            }),
            "sessions": len({
                item.session_id for item in day_attempts if item.session_id is not None
            }),
            "qualified_reviews": len(reviews_by_day.get(key, [])),
            "focus_seconds_global": 0,
            "focus_sessions_global": 0,
        })
        cursor += timedelta(days=1)
    return result


def aggregate_daily_series_weekly(
    daily_series: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Agrega blocos semanais e recalcula taxas pelas contagens brutas."""
    result = []
    for offset in range(0, len(daily_series), 7):
        chunk = daily_series[offset : offset + 7]
        attempts = sum(int(item["attempts"]) for item in chunk)
        correct = sum(int(item["correct"]) for item in chunk)
        result.append({
            "date": chunk[0]["date"],
            "end_date": chunk[-1]["date"],
            "attempts": attempts,
            "correct": correct,
            "accuracy_rate": 100.0 * correct / attempts if attempts else None,
            "unique_questions": sum(int(item["unique_questions"]) for item in chunk),
            "sessions": sum(int(item["sessions"]) for item in chunk),
            "qualified_reviews": sum(
                int(item["qualified_reviews"]) for item in chunk
            ),
            "focus_seconds_global": sum(
                int(item["focus_seconds_global"]) for item in chunk
            ),
            "focus_sessions_global": sum(
                int(item["focus_sessions_global"]) for item in chunk
            ),
            "aggregation": "weekly_explicit",
        })
    return result


def _focus_data(connection_factory: Callable, periods: Iterable[StatisticalPeriod]):
    periods = list(periods)
    start = min(period.start for period in periods if period.start is not None)
    end = max(period.end_exclusive for period in periods)
    with closing(connection_factory()) as connection:
        rows = connection.execute(
            """
            SELECT inicio, COALESCE(duracao_efetiva, 0),
                   CASE WHEN duracao_efetiva > 0 THEN 1 ELSE 0 END
            FROM sessoes_foco
            WHERE inicio >= ? AND inicio < ?
            ORDER BY inicio
            """,
            (
                start.replace(tzinfo=None).isoformat(sep=" ", timespec="seconds"),
                end.replace(tzinfo=None).isoformat(sep=" ", timespec="seconds"),
            ),
        ).fetchall()

    events = []
    for timestamp, seconds, effective in rows:
        parsed = _local_datetime(timestamp)
        if parsed is not None and effective:
            events.append((parsed, int(seconds or 0)))

    def summarize(period):
        selected = [item for item in events if period.start <= item[0] < period.end_exclusive]
        return {
            "scope": "global",
            "seconds": sum(item[1] for item in selected),
            "sessions": len(selected),
            "active_days": len({item[0].date() for item in selected}),
            "lineage": "global_without_concurso_id",
        }

    return events, [summarize(period) for period in periods]


def _catalog_names(connection_factory: Callable, concurso_id: int):
    with closing(connection_factory()) as connection:
        rows = connection.execute(
            """
            SELECT t.id, t.nome, d.id, d.nome
            FROM topicos t
            JOIN disciplinas d ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
              ON dc.disciplina_id = d.id AND dc.concurso_id = ?
             AND dc.incluido = 1 AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
              ON tc.topico_id = t.id AND tc.concurso_id = ?
             AND tc.incluido = 1 AND COALESCE(tc.pausado, 0) = 0
            ORDER BY d.nome COLLATE NOCASE, t.nome COLLATE NOCASE
            """,
            (int(concurso_id), int(concurso_id)),
        ).fetchall()
    topics = {int(row[0]): {"topic": row[1], "subject_id": int(row[2]), "subject": row[3]} for row in rows}
    subjects = {int(row[2]): str(row[3]) for row in rows}
    return topics, subjects


def _progress_history(connection_factory: Callable, concurso_id: int):
    try:
        with closing(connection_factory()) as connection:
            rows = connection.execute(
                """
                SELECT data, captured_at, metric_version, snapshot_version,
                       topic_coverage_rate, question_coverage_rate,
                       sufficient_evidence_rate, consolidated_rate,
                       global_mastery_score, global_mastery_state
                FROM progresso_snapshots_diarios
                WHERE concurso_id = ?
                ORDER BY data, captured_at
                """,
                (int(concurso_id),),
            ).fetchall()
    except Exception as exc:
        if exc.__class__.__name__ != "OperationalError":
            raise
        return []
    return [
        {
            "date": row[0],
            "captured_at": row[1],
            "metric_version": row[2],
            "snapshot_version": row[3],
            "topic_coverage_rate": row[4],
            "question_coverage_rate": row[5],
            "sufficient_evidence_rate": row[6],
            "consolidated_rate": row[7],
            "global_mastery_score": row[8],
            "global_mastery_state": row[9],
        }
        for row in rows
    ]


def build_temporal_analytics_snapshot(
    connection_factory: Callable,
    concurso_id: int,
    period: StatisticalPeriod,
    service: StatisticsService | None = None,
) -> TemporalAnalyticsSnapshot:
    """Monta uma fotografia temporal sem formulas estatisticas na UI."""
    if period.start is None:
        raise ValueError("analise temporal exige periodo com inicio definido")
    concurso_id = int(concurso_id)
    service = service or StatisticsService(connection_factory)
    previous_period = period.previous_equivalent()

    current_scope = service.get_global_metrics(concurso_id, period)
    previous_scope = service.get_global_metrics(concurso_id, previous_period)
    official_scope = service.get_global_metrics(concurso_id)
    current_summary = _summary(current_scope)
    previous_summary = _summary(previous_scope)
    comparisons = _period_comparisons(current_summary, previous_summary)
    sufficiency = comparison_sufficiency(current_summary, previous_summary)

    topic_names, subject_names = _catalog_names(connection_factory, concurso_id)
    topic_ids = sorted(topic_names)
    subject_ids = sorted(subject_names)
    current_topics = service.get_topic_metrics_batch(concurso_id, topic_ids, period)
    previous_topics = service.get_topic_metrics_batch(
        concurso_id, topic_ids, previous_period
    )
    current_subjects = service.get_subject_metrics_batch(
        concurso_id, subject_ids, period
    )
    previous_subjects = service.get_subject_metrics_batch(
        concurso_id, subject_ids, previous_period
    )
    official_topics = service.get_topic_metrics_batch(concurso_id, topic_ids)
    official_subjects = service.get_subject_metrics_batch(concurso_id, subject_ids)

    subjects = [
        _scope_comparison(
            subject_id,
            subject_names[subject_id],
            current_subjects[subject_id],
            previous_subjects[subject_id],
            official_subjects[subject_id],
        )
        for subject_id in subject_ids
    ]
    topics = []
    for topic_id in topic_ids:
        item = _scope_comparison(
            topic_id,
            topic_names[topic_id]["topic"],
            current_topics[topic_id],
            previous_topics[topic_id],
            official_topics[topic_id],
        )
        item["subject_id"] = topic_names[topic_id]["subject_id"]
        item["subject"] = topic_names[topic_id]["subject"]
        topics.append(item)

    attempts = service.repository.load_attempts(period, concurso_id)
    reviews = service.repository.load_reviews(period, concurso_id)
    daily = _daily_series(attempts, reviews, period)
    focus_events, focus_summaries = _focus_data(
        connection_factory, [period, previous_period]
    )
    daily_by_date = {item["date"]: item for item in daily}
    for timestamp, seconds in focus_events:
        day = timestamp.date().isoformat()
        if day in daily_by_date:
            daily_by_date[day]["focus_seconds_global"] += seconds
            daily_by_date[day]["focus_sessions_global"] += 1

    official_trend = official_scope.metric("performance_trend").to_dict()
    lineage_warnings = ["focus_is_global_without_concurso_lineage"]
    if (
        current_summary["unattributed_legacy_reviews"]
        or previous_summary["unattributed_legacy_reviews"]
    ):
        lineage_warnings.append("legacy_reviews_without_concurso_excluded")

    return TemporalAnalyticsSnapshot(
        concurso_id=concurso_id,
        current_period=_period_dict(period),
        previous_period=_period_dict(previous_period),
        current_metrics=current_summary,
        previous_metrics=previous_summary,
        comparisons=comparisons,
        daily_series=daily,
        display_series=(
            aggregate_daily_series_weekly(daily)
            if (period.end_exclusive - period.start).days > 30
            else daily
        ),
        subjects=subjects,
        topics=topics,
        official_performance_trend=official_trend,
        sufficiency=sufficiency,
        lineage_warnings=lineage_warnings,
        global_focus={
            "current": focus_summaries[0],
            "previous": focus_summaries[1],
            "comparison": _count_delta(
                focus_summaries[0]["seconds"], focus_summaries[1]["seconds"]
            ),
        },
        progress_history=_progress_history(connection_factory, concurso_id),
        generated_at=datetime.now(statistical_timezone()).isoformat(timespec="seconds"),
    )
