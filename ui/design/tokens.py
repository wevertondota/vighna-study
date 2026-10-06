"""Contrato público de tokens do Design System."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Iterator, Mapping


class TokenLevel(str, Enum):
    SEMANTIC = "semantic"
    COMPONENT = "component"


class TokenKind(str, Enum):
    COLOR = "color"
    GRADIENT = "gradient"


class VisualState(str, Enum):
    NORMAL = "normal"
    HOVER = "hover"
    PRESSED = "pressed"
    SELECTED = "selected"
    FOCUSED = "focused"
    KEYBOARD_FOCUS = "keyboard_focus"
    CHECKED = "checked"
    DISABLED = "disabled"
    CORRECT = "correct"
    INCORRECT = "incorrect"
    STRUCK = "struck"


@dataclass(frozen=True, slots=True)
class TokenSpec:
    path: str
    level: TokenLevel
    kind: TokenKind = TokenKind.COLOR

    def __post_init__(self) -> None:
        parts = self.path.split(".")
        if len(parts) < 2 or any(not part or not part.isidentifier() for part in parts):
            raise ValueError(f"Caminho de token inválido: {self.path!r}")


_SEMANTIC_COLOR_PATHS = (
    "canvas.app", "canvas.dialog", "canvas.inset",
    "surface.primary", "surface.secondary", "surface.tertiary", "surface.elevated",
    "surface.inset", "surface.hover", "surface.pressed", "surface.selected", "surface.disabled",
    "text.primary", "text.secondary", "text.muted", "text.disabled", "text.inverse",
    "text.link", "text.on_action", "text.on_feedback",
    "border.default", "border.subtle", "border.strong", "border.hover", "border.active",
    "border.selected", "border.disabled", "border.focus",
    "action.primary", "action.primary_hover", "action.primary_pressed", "action.primary_disabled",
    "action.secondary", "action.secondary_hover", "action.secondary_pressed", "action.secondary_disabled",
    "action.ghost", "action.ghost_hover", "action.destructive", "action.destructive_hover",
    "feedback.success_surface", "feedback.success_text", "feedback.success_border", "feedback.success_icon",
    "feedback.warning_surface", "feedback.warning_text", "feedback.warning_border", "feedback.warning_icon",
    "feedback.danger_surface", "feedback.danger_text", "feedback.danger_border", "feedback.danger_icon",
    "feedback.info_surface", "feedback.info_text", "feedback.info_border", "feedback.info_icon",
    "focus.ring", "focus.keyboard",
    "icon.default", "icon.muted", "icon.disabled", "icon.action", "icon.highlight", "icon.configuration",
    "overlay.scrim", "overlay.light", "overlay.dark", "overlay.selection",
    "glow.primary", "glow.focus", "glow.success", "glow.danger",
)

_SEMANTIC_GRADIENT_PATHS = (
    "gradient.action_primary", "gradient.action_primary_hover", "gradient.surface_elevated",
    "gradient.hero", "gradient.progress",
)

_COMPONENT_COLOR_PATHS = (
    "answer.normal_surface", "answer.normal_border", "answer.normal_text",
    "answer.hover_surface", "answer.hover_border",
    "answer.pressed_surface", "answer.pressed_border",
    "answer.selected_surface", "answer.selected_border", "answer.selected_text",
    "answer.focused_border", "answer.keyboard_focus_border", "answer.checked_indicator",
    "answer.disabled_surface", "answer.disabled_border", "answer.disabled_text",
    "answer.correct_surface", "answer.correct_border", "answer.correct_text",
    "answer.incorrect_surface", "answer.incorrect_border", "answer.incorrect_text",
    "answer.struck_surface", "answer.struck_border", "answer.struck_text",
    "answer.explanation_surface", "answer.explanation_text",
    "answer.editor_surface", "answer.editor_border", "answer.editor_selection",
    "progress.track", "progress.fill", "progress.text", "progress.complete", "progress.warning",
    "calendar.surface", "calendar.today_surface", "calendar.today_border", "calendar.today_text",
    "calendar.selected_surface", "calendar.selected_text", "calendar.week_predicted_surface",
    "calendar.week_predicted_border", "calendar.week_predicted_text", "calendar.weekend_text",
    "calendar.outside_month_text",
    "chart.axis", "chart.grid", "chart.label", "chart.series_1", "chart.series_2", "chart.series_3",
    "chart.series_4", "chart.series_5", "chart.series_6", "chart.positive", "chart.negative",
    "focus_mode.canvas", "focus_mode.panel", "focus_mode.panel_active", "focus_mode.text",
    "focus_mode.timer", "focus_mode.border", "focus_mode.action", "focus_mode.danger",
)

_COMPONENT_GRADIENT_PATHS = (
    "answer.selected_gradient", "answer.correct_gradient", "answer.incorrect_gradient",
    "progress.fill_gradient", "focus_mode.action_gradient", "focus_mode.action_hover_gradient",
)


def _specs(paths: tuple[str, ...], level: TokenLevel, kind: TokenKind) -> tuple[TokenSpec, ...]:
    return tuple(TokenSpec(path, level, kind) for path in paths)


SEMANTIC_TOKENS = (
    *_specs(_SEMANTIC_COLOR_PATHS, TokenLevel.SEMANTIC, TokenKind.COLOR),
    *_specs(_SEMANTIC_GRADIENT_PATHS, TokenLevel.SEMANTIC, TokenKind.GRADIENT),
)
COMPONENT_TOKENS = (
    *_specs(_COMPONENT_COLOR_PATHS, TokenLevel.COMPONENT, TokenKind.COLOR),
    *_specs(_COMPONENT_GRADIENT_PATHS, TokenLevel.COMPONENT, TokenKind.GRADIENT),
)
ALL_TOKENS = (*SEMANTIC_TOKENS, *COMPONENT_TOKENS)

_TOKEN_INDEX: Mapping[str, TokenSpec] = MappingProxyType({token.path: token for token in ALL_TOKENS})
if len(_TOKEN_INDEX) != len(ALL_TOKENS):
    raise RuntimeError("O contrato contém caminhos de token duplicados.")


def token_spec(path: str) -> TokenSpec:
    try:
        return _TOKEN_INDEX[path]
    except KeyError as exc:
        raise KeyError(f"Token inexistente no contrato: {path!r}") from exc


def iter_tokens(
    *, level: TokenLevel | None = None, kind: TokenKind | None = None
) -> Iterator[TokenSpec]:
    return (
        token
        for token in ALL_TOKENS
        if (level is None or token.level is level) and (kind is None or token.kind is kind)
    )


SEMANTIC_TOKEN_COUNT = len(SEMANTIC_TOKENS)
COMPONENT_TOKEN_COUNT = len(COMPONENT_TOKENS)
