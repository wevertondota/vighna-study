"""M08 — publication of certified global-merit projections, without I/O or Qt.

This module does NOT certify database data. The data-source adapter must
obtain complete records and build a verified ResultadoIntegracao (M03).
All UI consumers use the same immutable snapshot and monotone revision.
"""
from __future__ import annotations

from dataclasses import dataclass
from .contrato_historico_merito import ResultadoIntegracao
from .visao_merito_m05 import VisaoCatalogo, visao_aguardando, projetar_resultado_auditado


@dataclass(frozen=True)
class EstadoSincronizadoM08:
    revisao: int
    visao: VisaoCatalogo
    motivo_pendente: str | None = None


class CoordenadorMeritoM08:
    """In-memory, fail-closed state for one profile/academic history source.

    It never polls/opens a database or writes QSettings. A revision changes
    only on accepted data change or explicit invalidation.
    """
    def __init__(self):
        self._revisao = 0
        self._origem = None
        self._visao = visao_aguardando()
        self._motivo = "Aguardando histórico global auditado"

    def snapshot(self) -> EstadoSincronizadoM08:
        return EstadoSincronizadoM08(
            revisao=self._revisao,
            visao=self._visao,
            motivo_pendente=self._motivo if not self._visao.apurado else None,
        )

    def publicar(self, resultado: ResultadoIntegracao) -> tuple[EstadoSincronizadoM08, bool]:
        """Accept only projected M03 results; never silently switch sources.

        Same content is idempotent; a decreasing historic record would
        remove earned badges, so must be reconciled explicitly upstream.
        """
        visao = projetar_resultado_auditado(resultado)
        if self._origem is not None and visao.fonte != self._origem:
            raise ValueError("Origem do mérito mudou: invalidar e auditar nova fonte antes")
        if self._visao.apurado and visao.recorde < self._visao.recorde:
            raise ValueError("Recorde histórico regressivo: reconciliar persistência de conquistas")
        if visao == self._visao:
            return self.snapshot(), False
        self._visao = visao
        self._origem = visao.fonte
        self._motivo = None
        self._revisao += 1
        return self.snapshot(), True

    def invalidar(self, motivo: str) -> tuple[EstadoSincronizadoM08, bool]:
        """Explicitly hides global merit; no academic rows are changed."""
        if not isinstance(motivo, str) or not motivo.strip():
            raise ValueError("Informe motivo não vazio para invalidar")
        motivo = motivo.strip()[:180]
        if not self._visao.apurado and self._motivo == motivo:
            return self.snapshot(), False
        self._visao = visao_aguardando()
        self._motivo = motivo
        self._origem = None
        self._revisao += 1
        return self.snapshot(), True
