"""Calculos oficiais e versionados do Nucleo Estatistico Central."""

from __future__ import annotations

import statistics
from collections import defaultdict
from collections.abc import Callable, Iterable
from datetime import date, datetime, timedelta
from typing import Any

from .models import METRIC_VERSION, MetricResult, ScopeMetrics
from .periods import StatisticalPeriod, StatisticalPeriods, statistical_timezone
from .repository import AttemptEvent, CatalogItem, MetricsRepository, ReviewEvent


class StatisticsService:
    """API interna estavel para metricas academicas oficiais.

    O servico e somente leitura. Todas as agregacoes sao refeitas a partir dos
    eventos brutos do escopo; percentuais e scores de filhos nunca sao
    promediados.
    """

    def __init__(self, connection_factory: Callable):
        self.repository = MetricsRepository(connection_factory)

    @staticmethod
    def _period(period: StatisticalPeriod | None) -> StatisticalPeriod:
        return period or StatisticalPeriods.all_time()

    @staticmethod
    def _now() -> str:
        return datetime.now(statistical_timezone()).isoformat(timespec="seconds")

    @staticmethod
    def _parse_datetime(value: str) -> datetime | None:
        text = str(value or "").strip().replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=statistical_timezone())
        return parsed.astimezone(statistical_timezone())

    @staticmethod
    def _accuracy(items: Iterable[AttemptEvent]) -> float | None:
        items = list(items)
        if not items:
            return None
        return 100.0 * sum(1 for item in items if item.correct) / len(items)

    @staticmethod
    def _recency_score(last_at: str | None, as_of: date) -> tuple[float, int | None]:
        if not last_at:
            return 0.0, None
        try:
            last_day = date.fromisoformat(str(last_at)[:10])
        except ValueError:
            return 0.0, None
        age = max(0, (as_of - last_day).days)
        if age <= 7:
            score = 100.0
        elif age <= 14:
            score = 90.0
        elif age <= 30:
            score = 75.0
        elif age <= 45:
            score = 60.0
        elif age <= 60:
            score = 45.0
        elif age <= 90:
            score = 25.0
        else:
            score = 10.0
        return score, age

    @staticmethod
    def _error_control(attempts: list[AttemptEvent]) -> dict[str, Any]:
        by_question: dict[int, list[AttemptEvent]] = defaultdict(list)
        for attempt in attempts:
            if attempt.question_id is not None:
                by_question[attempt.question_id].append(attempt)

        counts = {
            "critical": 0,
            "recurring": 0,
            "recovering": 0,
            "recovered": 0,
            "isolated": 0,
        }
        for history in by_question.values():
            history.sort(key=lambda item: (item.occurred_at, item.id), reverse=True)
            total_errors = sum(1 for item in history if not item.correct)
            if total_errors <= 0:
                continue
            total_correct = len(history) - total_errors
            accuracy = 100.0 * total_correct / len(history)
            leading_correct = 0
            leading_errors = 0
            for item in history:
                if item.correct:
                    if leading_errors > 0:
                        break
                    leading_correct += 1
                else:
                    if leading_correct > 0:
                        break
                    leading_errors += 1

            if leading_correct >= 3:
                counts["recovered"] += 1
            elif leading_correct in (1, 2):
                counts["recovering"] += 1
            elif leading_errors >= 3 or (total_errors >= 3 and accuracy < 50.0):
                counts["critical"] += 1
            elif leading_errors >= 2 or (total_errors >= 2 and accuracy < 70.0):
                counts["recurring"] += 1
            else:
                counts["isolated"] += 1

        active_answered = max(1, len(by_question))
        absolute = (
            18.0 * counts["critical"]
            + 10.0 * counts["recurring"]
            + 4.0 * counts["recovering"]
            + 1.5 * counts["isolated"]
        )
        proportional = min(
            35.0,
            (
                counts["critical"]
                + 0.60 * counts["recurring"]
                + 0.25 * counts["recovering"]
            )
            / active_answered
            * 35.0,
        )
        recovery_bonus = min(10.0, counts["recovered"] / active_answered * 16.0)
        score = max(0.0, min(100.0, 100.0 - absolute - proportional + recovery_bonus))
        return {"score": score, **counts}

    @classmethod
    def _stability(cls, attempts: list[AttemptEvent]) -> tuple[float, list[str], dict]:
        by_day: dict[str, list[AttemptEvent]] = defaultdict(list)
        for item in attempts:
            by_day[item.day].append(item)
        eligible = sorted(
            (values for values in by_day.values() if len(values) >= 3),
            key=lambda values: values[0].day,
            reverse=True,
        )[:6]
        if len(eligible) < 2:
            return 50.0, ["low_temporal_evidence"], {"eligible_days": len(eligible)}
        rates = [cls._accuracy(values) or 0.0 for values in eligible]
        deviation = statistics.pstdev(rates) if len(rates) > 1 else 0.0
        consistency = max(0.0, 100.0 - min(100.0, 2.0 * deviation))
        temporal_evidence = min(100.0, len(eligible) * 20.0)
        score = temporal_evidence * (0.5 + 0.5 * consistency / 100.0)
        return score, [], {
            "eligible_days": len(eligible),
            "daily_rates": rates,
            "consistency": consistency,
        }

    @staticmethod
    def _evidence(
        attempts: list[AttemptEvent],
        qualified_reviews: list[ReviewEvent],
        revision_lineage_unknown: bool,
    ) -> dict[str, Any]:
        count = len(attempts)
        unique = len({item.question_id for item in attempts if item.question_id is not None})
        sessions = len({item.session_id for item in attempts if item.session_id is not None})
        days = sorted({item.day for item in attempts})
        amplitude = 0
        if len(days) >= 2:
            amplitude = (date.fromisoformat(days[-1]) - date.fromisoformat(days[0])).days
        first_day = days[0] if days else None
        review_days = {
            review.day
            for review in qualified_reviews
            if first_day is not None and review.day > first_day
        }

        if count < 3 or unique < 2:
            code, order, label = "insufficient", 0, "Insuficiente"
        elif (
            count >= 30
            and unique >= 10
            and sessions >= 4
            and len(days) >= 5
            and amplitude >= 21
            and len(review_days) >= 2
            and not revision_lineage_unknown
        ):
            code, order, label = "high", 3, "Alta"
        elif (
            count >= 10
            and unique >= 5
            and sessions >= 2
            and len(days) >= 3
            and (amplitude >= 7 or len(review_days) >= 1)
        ):
            code, order, label = "moderate", 2, "Moderada"
        else:
            code, order, label = "low", 1, "Baixa"

        return {
            "code": code,
            "order": order,
            "label": label,
            "attempts": count,
            "unique_questions": unique,
            "sessions": sessions,
            "active_days": len(days),
            "span_days": amplitude,
            "qualified_review_days": len(review_days),
        }

    @classmethod
    def _mastery(
        cls,
        attempts: list[AttemptEvent],
        evidence: dict[str, Any],
        as_of: date,
    ) -> dict[str, Any]:
        recent_50 = attempts[:50]
        recent_15 = attempts[:15]
        base = cls._accuracy(recent_50) or 0.0
        recent = cls._accuracy(recent_15) or 0.0
        performance = 0.65 * recent + 0.35 * base if len(recent_50) > 15 else base
        errors = cls._error_control(attempts)
        stability, warnings, stability_details = cls._stability(attempts)
        recency, age = cls._recency_score(
            attempts[0].occurred_at if attempts else None,
            as_of,
        )
        doubt_window = attempts[:30]
        doubt_rate = (
            100.0 * sum(1 for item in doubt_window if item.doubt) / len(doubt_window)
            if doubt_window
            else 0.0
        )
        doubt_penalty = min(8.0, doubt_rate * 0.08)
        estimate = max(
            0.0,
            min(
                100.0,
                0.55 * performance
                + 0.25 * errors["score"]
                + 0.15 * stability
                + 0.05 * recency
                - doubt_penalty,
            ),
        )
        public_value = None if evidence["code"] == "insufficient" else estimate
        if estimate < 30.0:
            level = "Crítico"
        elif estimate < 50.0:
            level = "Frágil"
        elif estimate < 70.0:
            level = "Em desenvolvimento"
        elif estimate < 85.0:
            level = "Consolidando"
        elif estimate < 95.0:
            level = "Dominado"
        else:
            level = "Domínio forte"
        if evidence["code"] == "low":
            warnings.append("provisional_low_evidence")
        return {
            "value": public_value,
            "estimate": estimate,
            "level": level if public_value is not None else "Dados insuficientes",
            "current_performance": performance,
            "base_performance": base,
            "recent_performance": recent,
            "error_control": errors,
            "temporal_stability": stability,
            "stability_details": stability_details,
            "recency": recency,
            "last_activity_age_days": age,
            "doubt_rate": doubt_rate,
            "doubt_penalty": doubt_penalty,
            "warnings": warnings,
        }

    @classmethod
    def _recent_performance(cls, attempts: list[AttemptEvent]) -> dict[str, Any]:
        current = attempts[:15]
        previous = attempts[15:30]
        current_rate = cls._accuracy(current)
        descriptive_ok = len(current) >= 5
        combined = current + previous
        sessions = {item.session_id for item in combined if item.session_id is not None}
        days = {item.day for item in combined}
        trend_ok = (
            len(current) >= 10
            and len(previous) >= 10
            and len(days) >= 2
            and len(sessions) >= 2
        )
        if trend_ok:
            previous_rate = cls._accuracy(previous)
            delta = float(current_rate) - float(previous_rate)
            if delta >= 5.0:
                trend = "improvement"
            elif delta <= -5.0:
                trend = "decline"
            else:
                trend = "stable"
        else:
            previous_rate = cls._accuracy(previous) if previous else None
            delta = None
            trend = "insufficient_data"
        return {
            "value": current_rate if descriptive_ok else None,
            "estimate": current_rate,
            "window_size": len(current),
            "previous_window_size": len(previous),
            "previous_rate": previous_rate,
            "trend": trend,
            "trend_delta_pp": delta,
            "trend_ready": trend_ok,
            "distinct_days": len(days),
            "distinct_sessions": len(sessions),
        }

    def _result(
        self,
        metric_id: str,
        value: Any,
        state: str,
        scope: dict[str, Any],
        period: StatisticalPeriod,
        denominator: float | None = None,
        parameters: dict[str, Any] | None = None,
        warnings: Iterable[str] = (),
        missing: dict[str, int] | None = None,
    ) -> MetricResult:
        return MetricResult(
            metric_id=metric_id,
            metric_version=METRIC_VERSION,
            value=value,
            state=state,
            scope=dict(scope),
            period_start=period.start.isoformat() if period.start else None,
            period_end_exclusive=period.end_exclusive.isoformat(),
            timezone=period.timezone,
            calculated_at=self._now(),
            denominator=denominator,
            parameters=parameters or {},
            warnings=tuple(dict.fromkeys(warnings)),
            missing_requirements=missing or {},
        )

    def _compute(
        self,
        scope: dict[str, Any],
        period: StatisticalPeriod,
        attempts: list[AttemptEvent],
        catalog: list[CatalogItem],
        active_topics: list[tuple[int, int]],
        reviews: list[ReviewEvent],
        total_session_count: int | None = None,
    ) -> ScopeMetrics:
        attempts.sort(key=lambda item: (item.occurred_at, item.id), reverse=True)
        concurso_id = scope.get("concurso_id")
        unknown_reviews = [review for review in reviews if not review.lineage_known]
        if concurso_id is None:
            qualified_reviews = list(reviews)
        else:
            qualified_reviews = [
                review
                for review in reviews
                if review.qualified_profile_id == int(concurso_id)
            ]
        evidence = self._evidence(attempts, qualified_reviews, bool(unknown_reviews))
        # O fim e exclusivo e normalmente aponta para 00:00 do dia seguinte.
        # A recencia deve usar o ultimo dia civil pertencente ao periodo.
        as_of = (period.end_exclusive - timedelta(microseconds=1)).date()
        mastery = self._mastery(attempts, evidence, as_of)
        recent = self._recent_performance(attempts)

        total = len(attempts)
        correct = sum(1 for item in attempts if item.correct)
        incorrect = total - correct
        unique_questions = {
            item.question_id for item in attempts if item.question_id is not None
        }
        distinct_sessions = {
            item.session_id for item in attempts if item.session_id is not None
        }
        available_questions = {item.question_id for item in catalog}
        answered_active = unique_questions & available_questions
        active_topic_ids = {item[0] for item in active_topics}
        answered_topic_ids = {
            item.topic_id
            for item in attempts
            if item.topic_id is not None and item.topic_id in active_topic_ids
        }
        warnings = ["legacy_local_time"]

        metrics: dict[str, MetricResult] = {}
        add = metrics.__setitem__
        add("answered_attempt_count", self._result(
            "answered_attempt_count", total, "ok", scope, period
        ))
        add("correct_attempt_count", self._result(
            "correct_attempt_count", correct, "ok", scope, period
        ))
        add("incorrect_attempt_count", self._result(
            "incorrect_attempt_count", incorrect, "ok", scope, period
        ))
        add("answered_unique_question_count", self._result(
            "answered_unique_question_count", len(unique_questions), "ok", scope, period
        ))
        add("accuracy_rate", self._result(
            "accuracy_rate",
            100.0 * correct / total if total else None,
            "ok" if total else "insufficient_data",
            scope,
            period,
            denominator=total,
            warnings=warnings,
            missing={} if total else {"attempts_needed": 1},
        ))
        add("error_rate", self._result(
            "error_rate",
            100.0 * incorrect / total if total else None,
            "ok" if total else "insufficient_data",
            scope,
            period,
            denominator=total,
            warnings=warnings,
            missing={} if total else {"attempts_needed": 1},
        ))
        add("distinct_answered_session_count", self._result(
            "distinct_answered_session_count", len(distinct_sessions), "ok", scope, period,
            warnings=("legacy_sessions_may_be_missing",) if any(item.session_id is None for item in attempts) else (),
        ))
        add("question_session_count", self._result(
            "question_session_count",
            total_session_count if total_session_count is not None else len(distinct_sessions),
            "ok",
            scope,
            period,
            warnings=("academic_scope_excludes_empty_sessions",) if total_session_count is None else (),
        ))
        last_attempt = attempts[0].occurred_at if attempts else None
        last_review = qualified_reviews[0].occurred_at if qualified_reviews else None
        last_activity = max(
            (value for value in (last_attempt, last_review) if value is not None),
            default=None,
        )
        add("last_activity_at", self._result(
            "last_activity_at", last_activity,
            "ok" if last_activity else "insufficient_data", scope, period,
            warnings=warnings,
            missing={} if last_activity else {"activity_events_needed": 1},
        ))
        study_days = {item.day for item in attempts}
        study_days.update(review.day for review in qualified_reviews)
        activity_warnings = (
            ("focus_without_profile_excluded",)
            if concurso_id is not None
            else ()
        )
        add("study_day_count", self._result(
            "study_day_count", len(study_days),
            "legacy_limited" if activity_warnings else "ok",
            scope, period, warnings=activity_warnings,
        ))
        add("last_study_date", self._result(
            "last_study_date", max(study_days) if study_days else None,
            (
                "legacy_limited"
                if study_days and activity_warnings
                else "ok" if study_days else "insufficient_data"
            ),
            scope, period, warnings=activity_warnings,
            missing={} if study_days else {"study_days_needed": 1},
        ))
        review_state = "legacy_limited" if unknown_reviews and concurso_id is not None else "ok"
        add("completed_review_count", self._result(
            "completed_review_count", len(qualified_reviews), review_state, scope, period,
            warnings=("unattributed_legacy_reviews_excluded",) if review_state == "legacy_limited" else (),
            parameters={"unattributed_review_count": len(unknown_reviews)},
        ))
        add("last_review_at", self._result(
            "last_review_at", last_review,
            (review_state if last_review is not None else "insufficient_data"),
            scope, period,
            warnings=("unattributed_legacy_reviews_excluded",) if review_state == "legacy_limited" else (),
            missing={} if last_review is not None else {"qualified_reviews_needed": 1},
        ))
        add("recent_performance_rate", self._result(
            "recent_performance_rate", recent["value"],
            "ok" if recent["value"] is not None else "insufficient_data", scope, period,
            denominator=recent["window_size"], parameters=recent, warnings=warnings,
            missing={} if recent["value"] is not None else {"attempts_needed": max(0, 5 - recent["window_size"])},
        ))
        add("performance_trend", self._result(
            "performance_trend", recent["trend"],
            "ok" if recent["trend_ready"] else "insufficient_data", scope, period,
            denominator=recent["window_size"] + recent["previous_window_size"],
            parameters=recent, warnings=warnings,
            missing={} if recent["trend_ready"] else {
                "attempts_needed": max(0, 25 - total),
                "sessions_needed": max(0, 2 - recent["distinct_sessions"]),
                "days_needed": max(0, 2 - recent["distinct_days"]),
            },
        ))
        add("question_coverage_rate", self._result(
            "question_coverage_rate",
            100.0 * len(answered_active) / len(available_questions) if available_questions else None,
            "ok" if available_questions else "insufficient_data", scope, period,
            denominator=len(available_questions),
            parameters={"answered_active_questions": len(answered_active)},
            warnings=("current_catalog_snapshot",),
            missing={} if available_questions else {"active_questions_needed": 1},
        ))
        add("topic_coverage_rate", self._result(
            "topic_coverage_rate",
            100.0 * len(answered_topic_ids) / len(active_topic_ids) if active_topic_ids else None,
            "ok" if active_topic_ids else "insufficient_data", scope, period,
            denominator=len(active_topic_ids),
            parameters={"answered_active_topics": len(answered_topic_ids)},
            warnings=("current_catalog_snapshot",),
            missing={} if active_topic_ids else {"active_topics_needed": 1},
        ))
        add("evidence_level", self._result(
            "evidence_level", evidence["code"], "ok", scope, period,
            denominator=total, parameters=evidence,
            warnings=("revision_lineage_unknown",) if unknown_reviews else (),
        ))
        mastery_state = "insufficient_data" if mastery["value"] is None else "ok"
        add("mastery_score", self._result(
            "mastery_score", mastery["value"], mastery_state, scope, period,
            denominator=total,
            parameters={key: value for key, value in mastery.items() if key != "warnings"},
            warnings=tuple(mastery["warnings"]) + tuple(warnings),
            missing={} if mastery["value"] is not None else {
                "attempts_needed": max(0, 3 - total),
                "unique_questions_needed": max(0, 2 - len(unique_questions)),
            },
        ))
        error_control = mastery["error_control"]
        add("critical_open_error_count", self._result(
            "critical_open_error_count", int(error_control["critical"]),
            "ok", scope, period,
        ))

        first_study_day = min((item.day for item in attempts), default=None)
        qualified_later_reviews = {
            review.day
            for review in qualified_reviews
            if first_study_day is not None and review.day > first_study_day
        }
        consolidation_missing = (
            mastery["value"] is None
            or not recent["trend_ready"]
            or (bool(unknown_reviews) and concurso_id is not None)
        )
        consolidation_parameters = {
            "mastery_score": mastery["value"],
            "evidence_level": evidence["code"],
            "distinct_answered_session_count": len(distinct_sessions),
            "qualified_review_count_after_first_contact": len(qualified_later_reviews),
            "performance_trend": recent["trend"],
            "critical_open_error_count": int(error_control["critical"]),
            "last_activity_age_days": mastery["last_activity_age_days"],
        }
        if consolidation_missing:
            consolidation = "insufficient_data"
            consolidation_state = "insufficient_data"
        else:
            is_consolidated = (
                float(mastery["value"]) >= 85.0
                and evidence["order"] >= 2
                and len(distinct_sessions) >= 3
                and len(qualified_later_reviews) >= 1
                and recent["trend"] != "decline"
                and int(error_control["critical"]) == 0
                and mastery["last_activity_age_days"] is not None
                and int(mastery["last_activity_age_days"]) <= 30
            )
            consolidation = "consolidated" if is_consolidated else "not_consolidated"
            consolidation_state = "ok"
        add("topic_consolidation_status", self._result(
            "topic_consolidation_status", consolidation,
            consolidation_state, scope, period,
            parameters=consolidation_parameters,
            warnings=("unattributed_legacy_reviews_excluded",)
            if unknown_reviews and concurso_id is not None else (),
        ))
        return ScopeMetrics(scope=dict(scope), period_id=period.identifier, metrics=metrics)

    def get_topic_metrics(
        self,
        topic_id: int,
        concurso_id: int,
        period: StatisticalPeriod | None = None,
    ) -> ScopeMetrics:
        period = self._period(period)
        scope = {"type": "topic", "topic_id": int(topic_id), "concurso_id": int(concurso_id)}
        return self._compute(
            scope,
            period,
            self.repository.load_attempts(period, concurso_id, topic_id=topic_id),
            self.repository.load_active_catalog(concurso_id, topic_id=topic_id),
            [(int(topic_id), 0)],
            self.repository.load_reviews(period, concurso_id, topic_id=topic_id),
        )

    def get_topic_metrics_batch(
        self,
        concurso_id: int,
        topic_ids: Iterable[int] | None = None,
        period: StatisticalPeriod | None = None,
    ) -> dict[int, ScopeMetrics]:
        period = self._period(period)
        active_topics = self.repository.load_active_topics(concurso_id)
        selected = {int(item) for item in topic_ids} if topic_ids is not None else {item[0] for item in active_topics}
        attempts = self.repository.load_attempts(period, concurso_id)
        catalog = self.repository.load_active_catalog(concurso_id)
        reviews = self.repository.load_reviews(period, concurso_id)
        attempts_by: dict[int, list[AttemptEvent]] = defaultdict(list)
        catalog_by: dict[int, list[CatalogItem]] = defaultdict(list)
        reviews_by: dict[int, list[ReviewEvent]] = defaultdict(list)
        for item in attempts:
            if item.topic_id in selected:
                attempts_by[int(item.topic_id)].append(item)
        for item in catalog:
            if item.topic_id in selected:
                catalog_by[item.topic_id].append(item)
        for item in reviews:
            if item.topic_id in selected:
                reviews_by[item.topic_id].append(item)
        return {
            topic_id: self._compute(
                {"type": "topic", "topic_id": topic_id, "concurso_id": int(concurso_id)},
                period,
                attempts_by[topic_id],
                catalog_by[topic_id],
                [(topic_id, 0)],
                reviews_by[topic_id],
            )
            for topic_id in sorted(selected)
        }

    def get_subject_metrics(
        self,
        subject_id: int,
        concurso_id: int,
        period: StatisticalPeriod | None = None,
    ) -> ScopeMetrics:
        period = self._period(period)
        subject_id = int(subject_id)
        return self._compute(
            {"type": "subject", "subject_id": subject_id, "concurso_id": int(concurso_id)},
            period,
            self.repository.load_attempts(period, concurso_id, subject_id=subject_id),
            self.repository.load_active_catalog(concurso_id, subject_id=subject_id),
            self.repository.load_active_topics(concurso_id, subject_id=subject_id),
            self.repository.load_reviews(period, concurso_id, subject_id=subject_id),
        )

    def get_subject_metrics_batch(
        self,
        concurso_id: int,
        subject_ids: Iterable[int],
        period: StatisticalPeriod | None = None,
    ) -> dict[int, ScopeMetrics]:
        # Uma consulta de eventos e catalogo para todas as disciplinas evita N+1.
        period = self._period(period)
        selected = {int(item) for item in subject_ids}
        attempts = self.repository.load_attempts(period, concurso_id)
        catalog = self.repository.load_active_catalog(concurso_id)
        topics = self.repository.load_active_topics(concurso_id)
        reviews = self.repository.load_reviews(period, concurso_id)
        return {
            subject_id: self._compute(
                {"type": "subject", "subject_id": subject_id, "concurso_id": int(concurso_id)},
                period,
                [item for item in attempts if item.subject_id == subject_id],
                [item for item in catalog if item.subject_id == subject_id],
                [item for item in topics if item[1] == subject_id],
                [item for item in reviews if item.subject_id == subject_id],
            )
            for subject_id in sorted(selected)
        }

    def get_global_metrics(
        self,
        concurso_id: int | None = None,
        period: StatisticalPeriod | None = None,
    ) -> ScopeMetrics:
        period = self._period(period)
        scope = {"type": "profile" if concurso_id is not None else "global"}
        if concurso_id is not None:
            scope["concurso_id"] = int(concurso_id)
        return self._compute(
            scope,
            period,
            self.repository.load_attempts(period, concurso_id),
            self.repository.load_active_catalog(concurso_id),
            self.repository.load_active_topics(concurso_id),
            self.repository.load_reviews(period, concurso_id),
            total_session_count=self.repository.count_question_sessions(period, concurso_id),
        )

    def get_period_metrics(
        self,
        start_date: date | datetime,
        end_date_exclusive: date | datetime,
        concurso_id: int | None = None,
    ) -> ScopeMetrics:
        return self.get_global_metrics(
            concurso_id,
            StatisticalPeriods.custom(start_date, end_date_exclusive, "custom"),
        )

    def get_question_metrics(
        self,
        question_id: int,
        concurso_id: int | None = None,
        period: StatisticalPeriod | None = None,
    ) -> ScopeMetrics:
        period = self._period(period)
        attempts = self.repository.load_attempts(
            period,
            concurso_id,
            question_id=int(question_id),
        )
        scope = {"type": "question", "question_id": int(question_id)}
        if concurso_id is not None:
            scope["concurso_id"] = int(concurso_id)
        result = self._compute(scope, period, attempts, [], [], [], None)
        sequence = ["correct" if item.correct else "incorrect" for item in attempts[:10]]
        result.metrics["question_attempt_count"] = self._result(
            "question_attempt_count", len(attempts), "ok", scope, period
        )
        result.metrics["last_attempt_at"] = self._result(
            "last_attempt_at", attempts[0].occurred_at if attempts else None,
            "ok" if attempts else "insufficient_data", scope, period,
            missing={} if attempts else {"attempts_needed": 1},
        )
        result.metrics["last_attempt_result"] = self._result(
            "last_attempt_result",
            ("correct" if attempts[0].correct else "incorrect") if attempts else None,
            "ok" if attempts else "insufficient_data", scope, period,
            missing={} if attempts else {"attempts_needed": 1},
        )
        result.metrics["recent_result_sequence"] = self._result(
            "recent_result_sequence", sequence,
            "ok" if attempts else "insufficient_data", scope, period,
            denominator=len(sequence), parameters={"requested_window": 10, "actual_window": len(sequence)},
            missing={} if attempts else {"attempts_needed": 1},
        )
        return result

    def get_recent_performance(self, topic_id: int, concurso_id: int) -> MetricResult:
        return self.get_topic_metrics(topic_id, concurso_id).metric("recent_performance_rate")

    def get_mastery_score(self, topic_id: int, concurso_id: int) -> MetricResult:
        return self.get_topic_metrics(topic_id, concurso_id).metric("mastery_score")

    def get_evidence_level(self, topic_id: int, concurso_id: int) -> MetricResult:
        return self.get_topic_metrics(topic_id, concurso_id).metric("evidence_level")

    def get_coverage(self, topic_id: int, concurso_id: int) -> MetricResult:
        return self.get_topic_metrics(topic_id, concurso_id).metric("question_coverage_rate")
