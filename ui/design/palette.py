"""Paleta física do Design System, sem qualquer integração com a UI legada."""

from __future__ import annotations

from dataclasses import dataclass
import re
from types import MappingProxyType
from typing import Iterable, Iterator, Mapping


_COLOR_RE = re.compile(r"^#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$")


@dataclass(frozen=True, slots=True)
class ColorValue:
    """Cor física canônica aceita por Qt e QSS.

    O formato de oito dígitos segue a convenção do Qt: ``#AARRGGBB``.
    """

    value: str

    def __post_init__(self) -> None:
        if self.value.lower() == "transparent":
            object.__setattr__(self, "value", "transparent")
            return
        if not _COLOR_RE.fullmatch(self.value):
            raise ValueError(
                f"Cor inválida: {self.value!r}. Use #RRGGBB, #AARRGGBB ou transparent."
            )
        object.__setattr__(self, "value", self.value.upper())

    @property
    def argb(self) -> tuple[int, int, int, int]:
        """Retorna ``(alpha, red, green, blue)`` sem depender do Qt."""

        if self.value == "transparent":
            return (0, 0, 0, 0)
        digits = self.value[1:]
        if len(digits) == 6:
            return (255, int(digits[0:2], 16), int(digits[2:4], 16), int(digits[4:6], 16))
        return (
            int(digits[0:2], 16),
            int(digits[2:4], 16),
            int(digits[4:6], 16),
            int(digits[6:8], 16),
        )

    def __str__(self) -> str:
        return self.value


def physical_name(value: str | ColorValue) -> str:
    """Gera um identificador deliberadamente físico, sem atribuir semântica."""

    color = value if isinstance(value, ColorValue) else ColorValue(value)
    return "transparent" if color.value == "transparent" else f"hex_{color.value[1:].lower()}"


class PhysicalPalette(Mapping[str, ColorValue]):
    """Mapa imutável de identificadores físicos para cores."""

    def __init__(self, values: Iterable[str]) -> None:
        colors = {physical_name(value): ColorValue(value) for value in values}
        self._colors: Mapping[str, ColorValue] = MappingProxyType(colors)

    def __getitem__(self, key: str) -> ColorValue:
        try:
            return self._colors[key]
        except KeyError as exc:
            raise KeyError(f"Cor física inexistente: {key!r}") from exc

    def __iter__(self) -> Iterator[str]:
        return iter(self._colors)

    def __len__(self) -> int:
        return len(self._colors)

    def reference(self, value: str | ColorValue) -> str:
        key = physical_name(value)
        if key not in self._colors:
            raise KeyError(f"Cor física não registrada: {value!s}")
        return key


# Recorte representativo e literal da paleta existente. A lista não pretende
# absorver as 3.310 cores inventariadas antes da migração dos componentes.
_CURRENT_PHYSICAL_VALUES = (
    "transparent",
    "#000000",
    "#FFFFFF",
    "#F8FAFC",
    "#F5F7FA",
    "#F1F5F9",
    "#EEF2F7",
    "#E8EDF3",
    "#E2E8F0",
    "#E0E6ED",
    "#DCE4ED",
    "#CBD5E1",
    "#BEC9D6",
    "#94A3B8",
    "#8490A1",
    "#7C899B",
    "#64748B",
    "#596579",
    "#475569",
    "#334155",
    "#2F3D4D",
    "#273449",
    "#1F2937",
    "#182230",
    "#172033",
    "#151F2C",
    "#111A27",
    "#111827",
    "#101722",
    "#0B111D",
    "#07111E",
    "#EAF7FF",
    "#D9F4FF",
    "#BCE7FF",
    "#B6D9E8",
    "#9FB1C3",
    "#8EAFC3",
    "#82ABC5",
    "#55768B",
    "#46566A",
    "#3F7599",
    "#3E7397",
    "#315D79",
    "#2E5C78",
    "#2B3747",
    "#183850",
    "#17334E",
    "#173046",
    "#162130",
    "#14283B",
    "#132B40",
    "#10283C",
    "#101F30",
    "#0D1D2D",
    "#0C1A29",
    "#4B50DF",
    "#586DE3",
    "#595EE8",
    "#6579EC",
    "#5965D8",
    "#7882E8",
    "#747FE9",
    "#4447E8",
    "#4347E1",
    "#3C42D2",
    "#5355F2",
    "#4F54EB",
    "#464DDE",
    "#757FFF",
    "#F0F2FF",
    "#F9FAFC",
    "#EEF9F4",
    "#64B992",
    "#173127",
    "#4EAD80",
    "#153127",
    "#12271F",
    "#4EBA86",
    "#FFF1F3",
    "#E18491",
    "#351D24",
    "#D76676",
    "#351C24",
    "#2A171D",
    "#D96777",
    "#FFF8E8",
    "#F0DEB4",
    "#9A6614",
    "#EEF6FF",
    "#D2E6FA",
    "#28679E",
    "#E5E7EB",
    "#4A5A6E",
    "#192534",
    "#1D2440",
    "#1B213A",
    "#18243A",
    "#4C7FD1",
    "#55A7D5",
    "#8FD8FF",
    "#8D554D",
    "#402827",
    "#FFD0C9",
    "#B51F31",
    "#D62B3D",
    "#F04458",
    "#CE293B",
    "#E83B4C",
    "#FF596B",
    "#981827",
    "#FF7382",
    "#FFABB3",
    "#355F9F",
    "#4C7EE0",
    "#7DADFF",
    "#B9D7FF",
    "#80FFFFFF",
    "#66000000",
    "#33000000",
    "#335965D8",
)


PALETTE = PhysicalPalette(_CURRENT_PHYSICAL_VALUES)


def palette_color(reference: str) -> ColorValue:
    """Resolve uma referência física; falhas nunca usam fallback silencioso."""

    return PALETTE[reference]
