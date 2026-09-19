"""Regularidade, sequência e ritmo de estudo do VighnaStudy.

A camada é deliberadamente global: mede hábito de uso do Vighna, não domínio
acadêmico de um concurso. Um dia conta uma única vez quando existe ao menos
uma atividade válida (tentativa de questão, revisão registrada com questões ou
sessão de foco efetiva >= 5 minutos). Essas métricas nunca entram na fila.
"""

from __future__ import annotations

from contextlib import closing
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from statistics import mean
from typing import Any, Callable

from statistics_core.periods import statistical_timezone

REGULARITY_SNAPSHOT_VERSION = "regularidade_v1"
MIN_FOCUS_SECONDS_FOR_STUDY_DAY = 5 * 60
DEFAULT_CALENDAR_WEEKS = 8

WEEKDAY_LABELS = ("Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom")


@dataclass(frozen=True)
class RegularitySnapshot:
    as_of: str
    first_activity_date: str | None
    last_activity_date: str | None
    history_span_days: int
    current_streak_days: int
    current_streak_state: str
    best_streak_days: int
    active_days_7: int
    active_days_30: int
    active_days_90: int
    current_week_active_days: int
    target_days_per_week: int
    current_week_target_rate: float | None
    regularity_score: float | None
    regularity_state: str
    observed_days_for_score: int
    pace_days_per_week_4w: float | None
    previous_pace_days_per_week_4w: float | None
    pace_delta: float | None
    current_full_gap_days: int
    longest_gap_days: int
    weekday_distribution: list[dict[str, Any]]
    weeks: list[dict[str, Any]]
    activity_days: list[dict[str, Any]] = field(default_factory=list)
    source_totals: dict[str, int] = field(default_factory=dict)
    generated_at: str = ""
    version: str = REGULARITY_SNAPSHOT_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _parse_day(value: Any) -> date | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    if not text:
        return None
    if len(text) == 10:
        try:
            return date.fromisoformat(text)
        except ValueError:
            return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            return None
    tz = statistical_timezone()
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=tz)
    else:
        parsed = parsed.astimezone(tz)
    return parsed.date()


def _query_rows(connection, sql: str, params=()):
    try:
        return connection.execute(sql, params).fetchall()
    except Exception:
        return []


def _load_activity_days(connect: Callable, *, as_of: date, min_focus_seconds: int):
    day_sources: dict[date, dict[str, int]] = {}

    def touch(day: date | None, key: str, amount: int = 1):
        if day is None or day > as_of:
            return
        item = day_sources.setdefault(day, {
            "attempts": 0,
            "reviews": 0,
            "focus_seconds": 0,
            "focus_sessions": 0,
        })
        item[key] = int(item.get(key, 0) or 0) + int(amount or 0)

    with closing(connect()) as connection:
        for occurred_at, count in _query_rows(
            connection,
            """
            SELECT respondida_em, COUNT(*)
            FROM tentativas_questoes
            WHERE respondida_em IS NOT NULL
            GROUP BY respondida_em
            """,
        ):
            touch(_parse_day(occurred_at), "attempts", int(count or 0))

        review_columns = {
            str(row[1])
            for row in _query_rows(connection, "PRAGMA table_info(revisoes)")
        }
        review_date = "COALESCE(realizada_em, data)" if "realizada_em" in review_columns else "data"
        for occurred_at, count in _query_rows(
            connection,
            f"""
            SELECT {review_date}, COUNT(*)
            FROM revisoes
            WHERE COALESCE(questoes, 0) > 0
              AND {review_date} IS NOT NULL
            GROUP BY {review_date}
            """,
        ):
            touch(_parse_day(occurred_at), "reviews", int(count or 0))

        for occurred_at, seconds, sessions in _query_rows(
            connection,
            """
            SELECT inicio,
                   COALESCE(SUM(duracao_efetiva), 0),
                   COUNT(*)
            FROM sessoes_foco
            WHERE COALESCE(duracao_efetiva, 0) >= ?
            GROUP BY inicio
            """,
            (int(min_focus_seconds),),
        ):
            day = _parse_day(occurred_at)
            touch(day, "focus_seconds", int(seconds or 0))
            touch(day, "focus_sessions", int(sessions or 0))

    return day_sources


def load_valid_activity_days(
    connect: Callable,
    *,
    as_of: date | datetime | None = None,
    min_focus_seconds: int = MIN_FOCUS_SECONDS_FOR_STUDY_DAY,
) -> dict[date, dict[str, int]]:
    """Fonte pública única dos dias que contam como estudo válido.

    Gamificação e Regularidade compartilham esta regra para evitar que um clique,
    um foco muito curto ou uma simples abertura do programa conte como estudo.
    """
    if as_of is None:
        ref = datetime.now(statistical_timezone()).date()
    elif isinstance(as_of, datetime):
        ref = as_of.astimezone(statistical_timezone()).date() if as_of.tzinfo else as_of.date()
    else:
        ref = as_of
    return _load_activity_days(
        connect,
        as_of=ref,
        min_focus_seconds=max(1, int(min_focus_seconds or 1)),
    )


def _run_length(active: set[date], end_day: date) -> int:
    total = 0
    cursor = end_day
    while cursor in active:
        total += 1
        cursor -= timedelta(days=1)
    return total


def _best_streak(sorted_days: list[date]) -> int:
    if not sorted_days:
        return 0
    best = current = 1
    previous = sorted_days[0]
    for day in sorted_days[1:]:
        if day == previous + timedelta(days=1):
            current += 1
        else:
            current = 1
        best = max(best, current)
        previous = day
    return best


def _count_in_days(active: set[date], as_of: date, window_days: int) -> int:
    start = as_of - timedelta(days=max(1, int(window_days)) - 1)
    return sum(1 for day in active if start <= day <= as_of)


def _pace(active: set[date], as_of: date, start: date, end: date) -> float | None:
    if end < start:
        return None
    span = (end - start).days + 1
    if span < 7:
        return None
    count = sum(1 for day in active if start <= day <= end)
    return round(count * 7.0 / span, 2)


def _weeks(active: set[date], as_of: date, first_day: date | None, target: int, count: int):
    current_monday = as_of - timedelta(days=as_of.weekday())
    rows = []
    for offset in range(max(1, int(count)) - 1, -1, -1):
        start = current_monday - timedelta(days=7 * offset)
        end = start + timedelta(days=6)
        days = [start + timedelta(days=i) for i in range(7)]
        active_flags = [day in active for day in days]
        active_count = sum(active_flags)
        observed = first_day is not None and end >= first_day
        rows.append({
            "start": start.isoformat(),
            "end": end.isoformat(),
            "current": start <= as_of <= end,
            "observed": observed,
            "days": [
                {
                    "date": day.isoformat(),
                    "label": WEEKDAY_LABELS[i],
                    "active": bool(active_flags[i]),
                    "future": day > as_of,
                }
                for i, day in enumerate(days)
            ],
            "active_days": active_count,
            "target": target,
            "target_met": (active_count >= target) if target > 0 and observed else None,
        })
    return rows


def build_regularity_snapshot(
    connect: Callable,
    *,
    as_of: date | datetime | None = None,
    target_days_per_week: int = 0,
    calendar_weeks: int = DEFAULT_CALENDAR_WEEKS,
    min_focus_seconds: int = MIN_FOCUS_SECONDS_FOR_STUDY_DAY,
) -> RegularitySnapshot:
    if as_of is None:
        ref = datetime.now(statistical_timezone()).date()
    elif isinstance(as_of, datetime):
        ref = as_of.astimezone(statistical_timezone()).date() if as_of.tzinfo else as_of.date()
    else:
        ref = as_of

    target = max(0, min(7, int(target_days_per_week or 0)))
    sources = load_valid_activity_days(
        connect,
        as_of=ref,
        min_focus_seconds=max(1, int(min_focus_seconds or 1)),
    )
    active = set(sources)
    ordered = sorted(active)
    first_day = ordered[0] if ordered else None
    last_day = ordered[-1] if ordered else None
    history_span = (ref - first_day).days + 1 if first_day else 0

    if ref in active:
        current_streak = _run_length(active, ref)
        streak_state = "active_today"
    elif ref - timedelta(days=1) in active:
        current_streak = _run_length(active, ref - timedelta(days=1))
        streak_state = "pending_today"
    else:
        current_streak = 0
        streak_state = "broken" if active else "no_history"

    best = _best_streak(ordered)
    current_week_start = ref - timedelta(days=ref.weekday())
    current_week_active = sum(1 for day in active if current_week_start <= day <= ref)
    target_rate = (
        min(100.0, 100.0 * current_week_active / target)
        if target > 0
        else None
    )

    score_window_start = max(first_day, ref - timedelta(days=27)) if first_day else None
    observed_for_score = (
        (ref - score_window_start).days + 1 if score_window_start is not None else 0
    )
    regularity_score = None
    regularity_state = "disabled" if target <= 0 else "insufficient_data"
    if target > 0 and observed_for_score > 0:
        active_in_score_window = sum(
            1 for day in active if score_window_start <= day <= ref
        )
        expected = target * observed_for_score / 7.0
        regularity_score = min(100.0, 100.0 * active_in_score_window / expected) if expected > 0 else None
        regularity_state = "ok" if observed_for_score >= 14 else "provisional"

    pace_current = None
    pace_previous = None
    pace_delta = None
    if first_day is not None:
        current_start = max(first_day, ref - timedelta(days=27))
        pace_current = _pace(active, ref, current_start, ref)
        previous_end = current_start - timedelta(days=1)
        previous_start = max(first_day, previous_end - timedelta(days=27))
        pace_previous = _pace(active, ref, previous_start, previous_end)
        if pace_current is not None and pace_previous is not None:
            pace_delta = round(pace_current - pace_previous, 2)

    if last_day is None:
        current_full_gap = 0
    elif last_day == ref:
        current_full_gap = 0
    else:
        current_full_gap = max(0, (ref - last_day).days - 1)

    gaps = [
        max(0, (right - left).days - 1)
        for left, right in zip(ordered, ordered[1:])
    ]
    longest_gap = max(gaps, default=0)

    ninety_start = ref - timedelta(days=89)
    weekday_distribution = []
    for weekday, label in enumerate(WEEKDAY_LABELS):
        count = sum(
            1 for day in active
            if ninety_start <= day <= ref and day.weekday() == weekday
        )
        weekday_distribution.append({"weekday": weekday, "label": label, "active_days": count})

    activity_days = []
    for day in ordered:
        if day < ninety_start:
            continue
        item = dict(sources[day])
        item.update({"date": day.isoformat(), "weekday": WEEKDAY_LABELS[day.weekday()]})
        activity_days.append(item)

    source_totals = {
        "attempts": sum(int(item.get("attempts", 0) or 0) for item in sources.values()),
        "reviews": sum(int(item.get("reviews", 0) or 0) for item in sources.values()),
        "focus_seconds": sum(int(item.get("focus_seconds", 0) or 0) for item in sources.values()),
        "focus_sessions": sum(int(item.get("focus_sessions", 0) or 0) for item in sources.values()),
    }

    return RegularitySnapshot(
        as_of=ref.isoformat(),
        first_activity_date=first_day.isoformat() if first_day else None,
        last_activity_date=last_day.isoformat() if last_day else None,
        history_span_days=history_span,
        current_streak_days=current_streak,
        current_streak_state=streak_state,
        best_streak_days=best,
        active_days_7=_count_in_days(active, ref, 7),
        active_days_30=_count_in_days(active, ref, 30),
        active_days_90=_count_in_days(active, ref, 90),
        current_week_active_days=current_week_active,
        target_days_per_week=target,
        current_week_target_rate=target_rate,
        regularity_score=round(regularity_score, 1) if regularity_score is not None else None,
        regularity_state=regularity_state,
        observed_days_for_score=observed_for_score,
        pace_days_per_week_4w=pace_current,
        previous_pace_days_per_week_4w=pace_previous,
        pace_delta=pace_delta,
        current_full_gap_days=current_full_gap,
        longest_gap_days=longest_gap,
        weekday_distribution=weekday_distribution,
        weeks=_weeks(active, ref, first_day, target, calendar_weeks),
        activity_days=activity_days,
        source_totals=source_totals,
        generated_at=datetime.now(statistical_timezone()).isoformat(timespec="seconds"),
    )
