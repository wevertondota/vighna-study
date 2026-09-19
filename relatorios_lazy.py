"""Estado leve para carregamento preguiçoso da área de Relatórios.

O módulo não depende do Qt. Ele controla contexto, invalidação por aba e
telemetria básica de duração para que a navegação não precise recalcular todos
os relatórios a cada clique.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


ABAS_RELATORIOS = (
    "Estratégico",
    "Por disciplina",
    "Por tópico",
    "Por dia",
)


@dataclass
class EstadoRelatoriosLazy:
    abas: tuple[str, ...] = ABAS_RELATORIOS
    sujas: set[str] = field(default_factory=set)
    resumo_sujo: bool = True
    contexto: tuple[int | None, str, str] | None = None
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

    def trocar_contexto(self, concurso_id: int | None, inicio: str, fim: str) -> bool:
        novo = (
            None if concurso_id is None else int(concurso_id),
            str(inicio),
            str(fim),
        )
        if self.contexto == novo:
            return False
        self.contexto = novo
        self.marcar_sujas()
        return True

    def registrar_duracao(self, chave: str, duracao_ms: float) -> None:
        self.duracoes_ms[str(chave)] = max(0.0, float(duracao_ms))

    def diagnostico(self) -> dict:
        return {
            "contexto": self.contexto,
            "abas_sujas": sorted(self.sujas),
            "resumo_sujo": bool(self.resumo_sujo),
            "duracoes_ms": dict(self.duracoes_ms),
        }
