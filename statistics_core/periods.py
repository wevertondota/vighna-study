"""Periodos civis oficiais, sempre semiabertos."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .models import TIMEZONE


def statistical_timezone():
    """Timezone oficial, com fallback para instalacoes Windows sem tzdata."""
    try:
        return ZoneInfo(TIMEZONE)
    except ZoneInfoNotFoundError:
        # O Brasil nao observa horario de verao desde 2019. Os dados atuais do
        # aplicativo usam horario local UTC-03 e continuam marcados com o ID
        # normativo America/Sao_Paulo no payload.
        return timezone(timedelta(hours=-3), name=TIMEZONE)


@dataclass(frozen=True)
class StatisticalPeriod:
    identifier: str
    start: datetime | None
    end_exclusive: datetime
    timezone: str = TIMEZONE

    def previous_equivalent(self) -> StatisticalPeriod:
        if self.start is None:
            raise ValueError("all_time nao possui periodo anterior equivalente")
        duration = self.end_exclusive - self.start
        return StatisticalPeriod(
            "previous_equivalent",
            self.start - duration,
            self.start,
            self.timezone,
        )


class StatisticalPeriods:
    """Fabrica reutilizavel para os periodos definidos no contrato 1.0."""

    @staticmethod
    def _as_of(as_of: datetime | date | None = None) -> datetime:
        tz = statistical_timezone()
        if as_of is None:
            return datetime.now(tz)
        if isinstance(as_of, date) and not isinstance(as_of, datetime):
            return datetime.combine(as_of, time.min, tzinfo=tz)
        if as_of.tzinfo is None:
            return as_of.replace(tzinfo=tz)
        return as_of.astimezone(tz)

    @classmethod
    def today(cls, as_of: datetime | date | None = None) -> StatisticalPeriod:
        current = cls._as_of(as_of)
        start = datetime.combine(current.date(), time.min, tzinfo=current.tzinfo)
        return StatisticalPeriod("today", start, start + timedelta(days=1))

    @classmethod
    def last_days(
        cls,
        days: int,
        as_of: datetime | date | None = None,
    ) -> StatisticalPeriod:
        days = int(days)
        if days <= 0:
            raise ValueError("days deve ser positivo")
        today = cls.today(as_of)
        return StatisticalPeriod(
            f"last_{days}_days",
            today.start - timedelta(days=days - 1),
            today.end_exclusive,
        )

    @classmethod
    def last_7_days(cls, as_of=None) -> StatisticalPeriod:
        return cls.last_days(7, as_of)

    @classmethod
    def last_30_days(cls, as_of=None) -> StatisticalPeriod:
        return cls.last_days(30, as_of)

    @classmethod
    def all_time(cls, as_of: datetime | date | None = None) -> StatisticalPeriod:
        current = cls._as_of(as_of)
        end = datetime.combine(
            current.date() + timedelta(days=1),
            time.min,
            tzinfo=current.tzinfo,
        )
        return StatisticalPeriod("all_time", None, end)

    @classmethod
    def custom(
        cls,
        start: datetime | date,
        end_exclusive: datetime | date,
        identifier: str = "custom",
    ) -> StatisticalPeriod:
        tz = statistical_timezone()

        def normalize(value):
            if isinstance(value, date) and not isinstance(value, datetime):
                return datetime.combine(value, time.min, tzinfo=tz)
            if value.tzinfo is None:
                return value.replace(tzinfo=tz)
            return value.astimezone(tz)

        start_dt = normalize(start)
        end_dt = normalize(end_exclusive)
        if end_dt <= start_dt:
            raise ValueError("periodo deve possuir fim posterior ao inicio")
        return StatisticalPeriod(identifier, start_dt, end_dt)
