"""Modelos imutáveis para gradientes utilizáveis por QSS e QPainter."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

from .palette import ColorValue


@dataclass(frozen=True, slots=True)
class GradientDirection:
    x1: float = 0.0
    y1: float = 0.0
    x2: float = 1.0
    y2: float = 0.0

    def __post_init__(self) -> None:
        coordinates = (self.x1, self.y1, self.x2, self.y2)
        if not all(math.isfinite(value) for value in coordinates):
            raise ValueError("A direção do gradiente deve conter coordenadas finitas.")
        if self.x1 == self.x2 and self.y1 == self.y2:
            raise ValueError("A direção do gradiente precisa ter extensão diferente de zero.")


@dataclass(frozen=True, slots=True)
class GradientStop:
    position: float
    color: ColorValue

    def __post_init__(self) -> None:
        if not math.isfinite(self.position) or not 0.0 <= self.position <= 1.0:
            raise ValueError("A posição do stop deve estar entre 0 e 1.")


@dataclass(frozen=True, slots=True)
class GradientSpec:
    direction: GradientDirection
    stops: tuple[GradientStop, ...]

    def __post_init__(self) -> None:
        if len(self.stops) < 2:
            raise ValueError("Um gradiente deve possuir ao menos dois stops.")
        positions = tuple(stop.position for stop in self.stops)
        if positions != tuple(sorted(positions)):
            raise ValueError("Os stops do gradiente devem estar ordenados.")
        if len(set(positions)) != len(positions):
            raise ValueError("Os stops do gradiente devem ter posições únicas.")


def gradient(
    *stops: tuple[float, str | ColorValue],
    direction: GradientDirection | None = None,
) -> GradientSpec:
    """Constrói e valida uma especificação sem importar Qt."""

    normalized: Iterable[GradientStop] = (
        GradientStop(position, color if isinstance(color, ColorValue) else ColorValue(color))
        for position, color in stops
    )
    return GradientSpec(direction or GradientDirection(), tuple(normalized))


HORIZONTAL = GradientDirection(0.0, 0.0, 1.0, 0.0)
VERTICAL = GradientDirection(0.0, 0.0, 0.0, 1.0)
DIAGONAL_DOWN = GradientDirection(0.0, 0.0, 1.0, 1.0)
