"""Identidade visual nativa do VighnaStudy: contrato Futurista exclusivo.

Fronteira incremental U2A. Consumidores legados seguem compatíveis até U3-U5.
Não há seleção de tema nesta API e nem importações de widgets Qt.
"""
from __future__ import annotations

from .themes import FUTURISTIC_THEME
from .adapters import qss_color, qss_gradient, qss_rgba, render_qss

NATIVE_THEME = FUTURISTIC_THEME


def native_color(token: str):
    """Resolve uma cor a partir da identidade visual oficial."""
    return NATIVE_THEME.color(token)


def native_gradient(token: str):
    """Resolve um gradiente a partir da identidade visual oficial."""
    return NATIVE_THEME.gradient(token)


def native_qss_color(token: str) -> str:
    return qss_color(NATIVE_THEME, token)


def native_qss_gradient(token: str) -> str:
    return qss_gradient(NATIVE_THEME, token)


def native_qss_rgba(token: str) -> str:
    return qss_rgba(NATIVE_THEME, token)


def render_native_qss(template: str) -> str:
    """Aplica somente a identidade nativa, sem dispatcher de nomes de temas."""
    return render_qss(NATIVE_THEME, template)
