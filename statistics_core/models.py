"""Objetos de retorno estaveis do Nucleo Estatistico."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

METRIC_VERSION = "1"
TIMEZONE = "America/Sao_Paulo"


@dataclass(frozen=True)
class MetricResult:
    """Valor de uma metrica acompanhado de seu contrato e qualidade."""

    metric_id: str
    value: Any
    state: str
    scope: dict[str, Any]
    calculated_at: str
    period_start: str | None = None
    period_end_exclusive: str | None = None
    timezone: str = TIMEZONE
    metric_version: str = METRIC_VERSION
    denominator: float | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    missing_requirements: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScopeMetrics:
    """Conjunto consistente de metricas para um unico escopo."""

    scope: dict[str, Any]
    period_id: str
    metrics: dict[str, MetricResult]

    def metric(self, metric_id: str) -> MetricResult:
        return self.metrics[metric_id]

    def value(self, metric_id: str, default: Any = None) -> Any:
        result = self.metrics.get(metric_id)
        return default if result is None else result.value

    def to_dict(self) -> dict[str, Any]:
        return {
            "scope": dict(self.scope),
            "period_id": self.period_id,
            "metrics": {
                key: result.to_dict()
                for key, result in self.metrics.items()
            },
        }
