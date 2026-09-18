"""Nucleo Estatistico Central do VighnaStudy.

A API publica fica concentrada em :class:`StatisticsService`. O pacote nao
escreve no banco: ele normaliza eventos existentes e calcula metricas
versionadas de forma deterministica.
"""

from .models import MetricResult, ScopeMetrics
from .periods import StatisticalPeriod, StatisticalPeriods
from .service import StatisticsService

__all__ = [
    "MetricResult",
    "ScopeMetrics",
    "StatisticalPeriod",
    "StatisticalPeriods",
    "StatisticsService",
]
