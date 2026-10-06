"""Adaptadores sem estado para consumidores QSS, QPainter e QtAwesome."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .gradients import GradientSpec
from .themes import ThemeDefinition, ThemeName, fixed_color, fixed_gradient, get_theme

if TYPE_CHECKING:
    from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPen


ThemeInput = ThemeDefinition | ThemeName | str

_QSS_TOKEN_RE = re.compile(
    r"\{\{(?P<kind>color|gradient):(?P<token>[a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)+)\}\}"
)


def _theme(theme: ThemeInput) -> ThemeDefinition:
    return theme if isinstance(theme, ThemeDefinition) else get_theme(theme)


def qss_color(theme: ThemeInput, token: str) -> str:
    """Retorna uma cor pronta para interpolação em QSS."""

    return _theme(theme).color(token).value


def _number(value: float) -> str:
    return f"{value:g}"


def gradient_to_qss(spec: GradientSpec) -> str:
    direction = spec.direction
    coordinates = (
        f"x1:{_number(direction.x1)}",
        f"y1:{_number(direction.y1)}",
        f"x2:{_number(direction.x2)}",
        f"y2:{_number(direction.y2)}",
    )
    stops = tuple(
        f"stop:{_number(stop.position)} {stop.color.value}" for stop in spec.stops
    )
    return f"qlineargradient({', '.join((*coordinates, *stops))})"


def qss_gradient(theme: ThemeInput, token: str) -> str:
    """Retorna um ``qlineargradient`` preservando direção, stops e alpha."""

    return gradient_to_qss(_theme(theme).gradient(token))


def render_qss(theme: ThemeInput, template: str) -> str:
    """Resolve marcadores de token sem transformar o QSS em f-string.

    Os formatos aceitos são ``{{color:caminho.do_token}}`` e
    ``{{gradient:caminho.do_token}}``. Um caminho inválido falha pelos mesmos
    contratos explícitos usados pelos demais adaptadores.
    """

    def resolve(match: re.Match[str]) -> str:
        token = match.group("token")
        if match.group("kind") == "color":
            return qss_color(theme, token)
        return qss_gradient(theme, token)

    rendered = _QSS_TOKEN_RE.sub(resolve, template)
    if "{{color:" in rendered or "{{gradient:" in rendered:
        raise ValueError("Marcador de token QSS inválido ou não resolvido.")
    return rendered


def fixed_qss_color(token: str) -> str:
    """Retorna uma cor de componente deliberadamente independente do tema."""

    return fixed_color(token).value


def fixed_qss_gradient(token: str) -> str:
    return gradient_to_qss(fixed_gradient(token))


def _qcolor_value(color) -> "QColor":
    from PySide6.QtGui import QColor

    alpha, red, green, blue = color.argb
    return QColor(red, green, blue, alpha)


def qcolor(theme: ThemeInput, token: str) -> "QColor":
    """Cria QColor sem exigir QApplication ou importar widgets."""

    return _qcolor_value(_theme(theme).color(token))


def fixed_qcolor(token: str) -> "QColor":
    """Cria QColor de um token fixo sem exigir QApplication."""

    return _qcolor_value(fixed_color(token))


def qbrush(theme: ThemeInput, token: str) -> "QBrush":
    from PySide6.QtGui import QBrush

    return QBrush(qcolor(theme, token))


def qpen(theme: ThemeInput, token: str, width: float = 1.0) -> "QPen":
    from PySide6.QtGui import QPen

    if width < 0:
        raise ValueError("A largura de QPen não pode ser negativa.")
    pen = QPen(qcolor(theme, token))
    pen.setWidthF(width)
    return pen


def _qlineargradient_spec(
    spec: GradientSpec,
    coordinates: tuple[float, float, float, float] | None = None,
) -> "QLinearGradient":
    from PySide6.QtGui import QLinearGradient

    if coordinates is None:
        direction = spec.direction
        coordinates = (direction.x1, direction.y1, direction.x2, direction.y2)
    result = QLinearGradient(*coordinates)
    for stop in spec.stops:
        result.setColorAt(stop.position, _qcolor_value(stop.color))
    return result


def qlineargradient(
    theme: ThemeInput,
    token: str,
    *,
    coordinates: tuple[float, float, float, float] | None = None,
) -> "QLinearGradient":
    return _qlineargradient_spec(_theme(theme).gradient(token), coordinates)


def fixed_qlineargradient(
    token: str,
    *,
    coordinates: tuple[float, float, float, float] | None = None,
) -> "QLinearGradient":
    """Cria gradiente fixo, aceitando coordenadas dinâmicas do QPainter."""

    return _qlineargradient_spec(fixed_gradient(token), coordinates)


def qtawesome_color(theme: ThemeInput, token: str) -> str:
    """Cor para o argumento ``color=`` do QtAwesome, sem importar QtAwesome."""

    return qss_color(theme, token)
