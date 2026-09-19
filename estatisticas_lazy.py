"""Estado leve para carregamento preguiçoso da área de Estatísticas.

O módulo não depende do Qt. Ele apenas controla quais abas precisam ser
recalculadas e registra tempos de atualização para diagnóstico local.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


ABAS_ESTATISTICAS = (
    "Histórico",
    "Regularidade",
    "Conquistas",
    "Algoritmo",
    "Disciplinas",
    "Mapa de domínio",
    "Pontos fracos",
    "Revisões recentes",
    "Tendências",
    "Progresso",
)


@dataclass
class EstadoEstatisticasLazy:
    """Controla invalidação e atualização sob demanda das abas."""

    abas: tuple[str, ...] = ABAS_ESTATISTICAS
    sujas: set[str] = field(default_factory=set)
    resumo_sujo: bool = True
    concurso_id: int | None = None
    duracoes_ms: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.sujas:
            self.sujas = set(self.abas)

    def marcar_sujas(
        self,
        abas: Iterable[str] | None = None,
        *,
        resumo: bool = True,
    ) -> None:
        if abas is None:
            self.sujas.update(self.abas)
        else:
            self.sujas.update(str(aba) for aba in abas if str(aba) in self.abas)
        if resumo:
            self.resumo_sujo = True

    def marcar_limpa(self, aba: str) -> None:
        self.sujas.discard(str(aba))

    def precisa_atualizar(self, aba: str) -> bool:
        return str(aba) in self.sujas

    def marcar_resumo_limpo(self) -> None:
        self.resumo_sujo = False

    def trocar_concurso(self, concurso_id: int | None) -> bool:
        novo = None if concurso_id is None else int(concurso_id)
        if self.concurso_id == novo:
            return False
        self.concurso_id = novo
        self.marcar_sujas()
        return True

    def registrar_duracao(self, chave: str, duracao_ms: float) -> None:
        self.duracoes_ms[str(chave)] = max(0.0, float(duracao_ms))

    def diagnostico(self) -> dict:
        return {
            "concurso_id": self.concurso_id,
            "abas_sujas": sorted(self.sujas),
            "resumo_sujo": bool(self.resumo_sujo),
            "duracoes_ms": dict(self.duracoes_ms),
        }
