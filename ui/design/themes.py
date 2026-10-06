"""Definições completas dos temas no novo contrato, ainda desconectadas da UI."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from .gradients import GradientDirection, GradientSpec, gradient
from .palette import ColorValue, PALETTE
from .tokens import ALL_TOKENS, FIXED_TOKEN_PATHS, TokenKind, TokenSpec, token_spec


class ThemeName(str, Enum):
    LIGHT = "claro"
    DARK = "escuro"
    FUTURISTIC = "futurista"


class ThemeContractError(ValueError):
    """Indica que uma definição não cumpre o contrato público."""


class TokenNotFoundError(KeyError):
    """Indica acesso explícito a um token inexistente ou do tipo incorreto."""


_COLOR_PATHS = frozenset(token.path for token in ALL_TOKENS if token.kind is TokenKind.COLOR)
_GRADIENT_PATHS = frozenset(token.path for token in ALL_TOKENS if token.kind is TokenKind.GRADIENT)


@dataclass(frozen=True, slots=True)
class ThemeDefinition:
    name: ThemeName
    color_references: Mapping[str, str]
    gradients: Mapping[str, GradientSpec]

    def __post_init__(self) -> None:
        color_references = MappingProxyType(dict(self.color_references))
        gradients = MappingProxyType(dict(self.gradients))
        object.__setattr__(self, "color_references", color_references)
        object.__setattr__(self, "gradients", gradients)
        self.validate_contract()

    def validate_contract(self) -> None:
        color_paths = set(self.color_references)
        gradient_paths = set(self.gradients)
        if color_paths != _COLOR_PATHS:
            missing = sorted(_COLOR_PATHS - color_paths)
            extra = sorted(color_paths - _COLOR_PATHS)
            raise ThemeContractError(
                f"Contrato de cores incompleto em {self.name.value}: ausentes={missing}, extras={extra}"
            )
        if gradient_paths != _GRADIENT_PATHS:
            missing = sorted(_GRADIENT_PATHS - gradient_paths)
            extra = sorted(gradient_paths - _GRADIENT_PATHS)
            raise ThemeContractError(
                f"Contrato de gradientes incompleto em {self.name.value}: ausentes={missing}, extras={extra}"
            )
        unknown_references = sorted(
            reference for reference in self.color_references.values() if reference not in PALETTE
        )
        if unknown_references:
            raise ThemeContractError(
                f"Referências físicas desconhecidas em {self.name.value}: {unknown_references}"
            )

    def color(self, token: str | TokenSpec) -> ColorValue:
        path = token.path if isinstance(token, TokenSpec) else token
        try:
            reference = self.color_references[path]
        except KeyError as exc:
            if path in _GRADIENT_PATHS:
                raise TokenNotFoundError(f"{path!r} é gradiente, não cor.") from exc
            raise TokenNotFoundError(f"Token de cor inexistente: {path!r}") from exc
        return PALETTE[reference]

    def gradient(self, token: str | TokenSpec) -> GradientSpec:
        path = token.path if isinstance(token, TokenSpec) else token
        try:
            return self.gradients[path]
        except KeyError as exc:
            if path in _COLOR_PATHS:
                raise TokenNotFoundError(f"{path!r} é cor, não gradiente.") from exc
            raise TokenNotFoundError(f"Token de gradiente inexistente: {path!r}") from exc

    def resolve(self, token: str | TokenSpec) -> ColorValue | GradientSpec:
        path = token.path if isinstance(token, TokenSpec) else token
        try:
            spec = token_spec(path)
        except KeyError as exc:
            raise TokenNotFoundError(f"Token inexistente: {path!r}") from exc
        return self.color(path) if spec.kind is TokenKind.COLOR else self.gradient(path)


def _semantic_colors(c: Mapping[str, str]) -> dict[str, str]:
    return {
        "canvas.app": c["canvas_app"],
        "canvas.dialog": c["canvas_dialog"],
        "canvas.inset": c["canvas_inset"],
        "surface.primary": c["surface_primary"],
        "surface.secondary": c["surface_secondary"],
        "surface.tertiary": c["surface_tertiary"],
        "surface.elevated": c["surface_elevated"],
        "surface.inset": c["surface_inset"],
        "surface.hover": c["surface_hover"],
        "surface.pressed": c["surface_pressed"],
        "surface.selected": c["surface_selected"],
        "surface.disabled": c["surface_disabled"],
        "surface.interactive": c["surface_interactive"],
        "surface.inverse": c["surface_inverse"],
        "surface.focused": c["surface_focused"],
        "text.primary": c["text_primary"],
        "text.secondary": c["text_secondary"],
        "text.muted": c["text_muted"],
        "text.disabled": c["text_disabled"],
        "text.inverse": c["text_inverse"],
        "text.link": c["text_link"],
        "text.on_action": c["text_on_action"],
        "text.on_feedback": c["text_on_feedback"],
        "text.control": c["text_control"],
        "text.selected": c["text_selected"],
        "text.choice": c["text_choice"],
        "text.header": c["text_header"],
        "text.interactive_hover": c["text_interactive_hover"],
        "text.selection_accent": c["text_selection_accent"],
        "text.control_subtle": c["text_control_subtle"],
        "text.readonly": c["text_readonly"],
        "text.popup": c["text_popup"],
        "border.default": c["border_default"],
        "border.subtle": c["border_subtle"],
        "border.strong": c["border_strong"],
        "border.hover": c["border_hover"],
        "border.active": c["border_active"],
        "border.selected": c["border_selected"],
        "border.disabled": c["border_disabled"],
        "border.focus": c["border_focus"],
        "border.control_subtle": c["border_control_subtle"],
        "border.control_hover": c["border_control_hover"],
        "border.divider": c["border_divider"],
        "border.divider_strong": c["border_divider_strong"],
        "border.grid": c["border_grid"],
        "border.control_indicator": c["border_control_indicator"],
        "border.checked": c["border_checked"],
        "action.primary": c["action_primary"],
        "action.primary_hover": c["action_primary_hover"],
        "action.primary_pressed": c["action_primary_pressed"],
        "action.primary_disabled": c["action_primary_disabled"],
        "action.secondary": c["action_secondary"],
        "action.secondary_hover": c["action_secondary_hover"],
        "action.secondary_pressed": c["action_secondary_pressed"],
        "action.secondary_disabled": c["action_secondary_disabled"],
        "action.ghost": c["action_ghost"],
        "action.ghost_hover": c["action_ghost_hover"],
        "action.checked": c["action_checked"],
        "action.destructive": c["action_destructive"],
        "action.destructive_hover": c["action_destructive_hover"],
        "feedback.success_surface": c["feedback_success_surface"],
        "feedback.success_text": c["success_text"],
        "feedback.success_border": c["feedback_success_border"],
        "feedback.success_icon": c["success_icon"],
        "feedback.warning_surface": c["warning_surface"],
        "feedback.warning_text": c["warning_text"],
        "feedback.warning_border": c["warning_border"],
        "feedback.warning_icon": c["warning_icon"],
        "feedback.danger_surface": c["feedback_danger_surface"],
        "feedback.danger_text": c["danger_text"],
        "feedback.danger_border": c["feedback_danger_border"],
        "feedback.danger_icon": c["danger_icon"],
        "feedback.info_surface": c["info_surface"],
        "feedback.info_text": c["info_text"],
        "feedback.info_border": c["info_border"],
        "feedback.info_icon": c["info_icon"],
        "focus.ring": c["focus_ring"],
        "focus.keyboard": c["focus_keyboard"],
        "icon.default": c["icon_default"],
        "icon.muted": c["icon_muted"],
        "icon.disabled": c["icon_disabled"],
        "icon.action": c["icon_action"],
        "icon.highlight": c["icon_highlight"],
        "icon.configuration": c["icon_configuration"],
        "overlay.scrim": c["overlay_scrim"],
        "overlay.light": c["overlay_light"],
        "overlay.dark": c["overlay_dark"],
        "overlay.selection": c["overlay_selection"],
        "overlay.selection_subtle": c["overlay_selection_subtle"],
        "glow.primary": c["glow_primary"],
        "glow.focus": c["glow_focus"],
        "glow.success": c["glow_success"],
        "glow.danger": c["glow_danger"],
    }


def _component_colors(c: Mapping[str, str], overrides: Mapping[str, str]) -> dict[str, str]:
    colors = {
        "answer.normal_surface": c["surface_primary"],
        "answer.normal_border": c["border_default"],
        "answer.normal_text": c["text_primary"],
        "answer.hover_surface": c["surface_hover"],
        "answer.hover_border": c["border_hover"],
        "answer.pressed_surface": c["surface_pressed"],
        "answer.pressed_border": c["border_active"],
        "answer.selected_surface": c["surface_selected"],
        "answer.selected_border": c["border_selected"],
        "answer.selected_text": c["text_primary"],
        "answer.focused_border": c["border_focus"],
        "answer.keyboard_focus_border": c["focus_keyboard"],
        "answer.checked_indicator": c["action_primary"],
        "answer.indicator_surface": c["surface_primary"],
        "answer.indicator_border": c["border_strong"],
        "answer.indicator_hover_border": c["border_hover"],
        "answer.indicator_checked_border": c["border_selected"],
        "answer.indicator_text": c["text_choice"],
        "answer.disabled_surface": c["surface_disabled"],
        "answer.disabled_border": c["border_disabled"],
        "answer.disabled_text": c["text_disabled"],
        "answer.correct_surface": c["success_surface"],
        "answer.correct_border": c["success_border"],
        "answer.correct_text": c["success_text"],
        "answer.incorrect_surface": c["danger_surface"],
        "answer.incorrect_border": c["danger_border"],
        "answer.incorrect_text": c["danger_text"],
        "answer.struck_surface": c["surface_disabled"],
        "answer.struck_border": c["border_disabled"],
        "answer.struck_text": c["text_muted"],
        "answer.struck_hover_surface": c["surface_hover"],
        "answer.struck_hover_border": c["border_hover"],
        "answer.eliminate_text": c["icon_muted"],
        "answer.eliminate_hover_surface": c["surface_hover"],
        "answer.eliminate_hover_text": c["icon_default"],
        "answer.eliminate_checked_surface": c["surface_selected"],
        "answer.eliminate_checked_text": c["text_primary"],
        "answer.eliminate_checked_border": c["border_selected"],
        "answer.explanation_surface": c["surface_secondary"],
        "answer.explanation_border": c["border_default"],
        "answer.explanation_title_text": c["text_primary"],
        "answer.explanation_text": c["text_secondary"],
        "answer.editor_surface": c["surface_primary"],
        "answer.editor_border": c["border_focus"],
        "answer.editor_text": c["text_primary"],
        "answer.editor_selection": c["overlay_selection"],
        "answer.edit_action_surface": c["surface_primary"],
        "answer.edit_action_hover_surface": c["surface_hover"],
        "answer.edit_action_hover_text": c["text_interactive_hover"],
        "answer.edit_action_hover_border": c["border_hover"],
        "answer.save_action_surface": c["action_primary"],
        "answer.save_action_text": c["text_on_action"],
        "answer.save_action_border": c["border_active"],
        "answer.cancel_action_surface": c["action_secondary"],
        "answer.primary_action_border": c["border_active"],
        "answer.primary_action_hover_border": c["border_hover"],
        "progress.track": c["surface_inset"],
        "progress.border": c["border_subtle"],
        "progress.fill": c["action_primary"],
        "progress.text": c["text_secondary"],
        "progress.complete": c["success_icon"],
        "progress.warning": c["warning_icon"],
        "calendar.surface": c["surface_primary"],
        "calendar.today_surface": c["info_surface"],
        "calendar.today_border": c["info_border"],
        "calendar.today_text": c["info_text"],
        "calendar.selected_surface": c["surface_selected"],
        "calendar.selected_text": c["text_primary"],
        "calendar.week_predicted_surface": c["warning_surface"],
        "calendar.week_predicted_border": c["warning_border"],
        "calendar.week_predicted_text": c["warning_text"],
        "calendar.weekend_text": c["text_secondary"],
        "calendar.outside_month_text": c["text_disabled"],
        "chart.axis": c["border_strong"],
        "chart.grid": c["border_subtle"],
        "chart.label": c["text_secondary"],
        "chart.series_1": c["action_primary"],
        "chart.series_2": c["info_icon"],
        "chart.series_3": c["success_icon"],
        "chart.series_4": c["warning_icon"],
        "chart.series_5": c["danger_icon"],
        "chart.series_6": c["icon_highlight"],
        "chart.positive": c["success_icon"],
        "chart.negative": c["danger_icon"],
        "focus_mode.canvas": c["canvas_app"],
        "focus_mode.panel": c["surface_secondary"],
        "focus_mode.panel_active": c["surface_selected"],
        "focus_mode.text": c["text_primary"],
        "focus_mode.timer": c["icon_highlight"],
        "focus_mode.border": c["border_active"],
        "focus_mode.action": c["action_primary"],
        "focus_mode.danger": c["action_destructive"],
    }
    colors.update(_FIXED_COMPONENT_COLORS)
    colors.update(overrides)
    return colors


_FIXED_COMPONENT_COLORS = {
    "system_status.canvas": "#071522",
    "system_status.border": "#214A64",
    "system_status.surface": "#081927",
    "system_status.surface_border": "#15364C",
    "system_status.text_primary": "#F5F8FF",
    "system_status.text_status": "#EAF4FF",
    "system_status.text_secondary": "#8FAAC0",
    "system_status.text_accent": "#67B7FF",
    "system_status.progress_track": "#081A28",
    "system_status.progress_border": "#315B76",
    "system_status.progress_fill": "#3A8DF1",
    "startup.logo_surface": "#091927",
    "startup.logo_border": "#1D4058",
    "startup.subtitle_text": "#9FB9D0",
    "startup.footer_text": "#4E718A",
    "startup.logo_fallback": "#6DC1FF",
    "startup.progress_pulse": "#6FC3FF",
    "task_indicator.mark_surface": "#0A2233",
    "task_indicator.mark_border": "#286483",
    "task_indicator.mark_text": "#74C7FF",
}


def _refs(colors: Mapping[str, str]) -> dict[str, str]:
    return {path: PALETTE.reference(value) for path, value in colors.items()}


def _make_theme(
    name: ThemeName,
    roles: Mapping[str, str],
    component_overrides: Mapping[str, str],
    gradients: Mapping[str, GradientSpec],
) -> ThemeDefinition:
    colors = _semantic_colors(roles)
    colors.update(_component_colors(roles, component_overrides))
    return ThemeDefinition(name, _refs(colors), gradients)


def _palette_gradient(
    *stops: tuple[float, str],
    direction: GradientDirection | None = None,
) -> GradientSpec:
    """Monta stops somente com cores previamente registradas na paleta física."""

    resolved = tuple(
        (position, PALETTE[PALETTE.reference(value)]) for position, value in stops
    )
    return gradient(*resolved, direction=direction)


_LIGHT = {
    "canvas_app": "#F5F7FA", "canvas_dialog": "#FFFFFF", "canvas_inset": "#EEF2F7",
    "surface_primary": "#FFFFFF", "surface_secondary": "#FFFFFF", "surface_tertiary": "#F7F8FB",
    "surface_elevated": "#FFFFFF", "surface_inset": "#EEF1F6", "surface_hover": "#AEB7C6",
    "surface_pressed": "#EEF2F7", "surface_selected": "#EEEAFF", "surface_disabled": "#F1F5F9",
    "surface_interactive": "#C3CAD6", "surface_inverse": "#111827", "surface_focused": "#FFFFFF",
    "text_primary": "#1F2937", "text_secondary": "#20293A", "text_muted": "#68758D",
    "text_disabled": "#94A3B8", "text_inverse": "#FFFFFF", "text_link": "#5A49CF",
    "text_on_action": "#FFFFFF", "text_on_feedback": "#111827",
    "text_control": "#182033", "text_selected": "#2D246F",
    "text_choice": "#1F2937", "text_header": "#4F5B70", "text_interactive_hover": "#1F2937",
    "text_selection_accent": "#342A88",
    "text_control_subtle": "#182033", "text_readonly": "#64748B", "text_popup": "#182033",
    "border_default": "#CBD3DF", "border_subtle": "#D5DCE8", "border_strong": "#CBD5E1",
    "border_hover": "#94A3B8", "border_active": "#7882E8", "border_selected": "#7882E8",
    "border_disabled": "#E2E8F0", "border_focus": "#5965D8", "border_control_subtle": "#CBD3DF",
    "border_control_hover": "#CBD3DF", "border_divider": "#E4E8EF",
    "border_divider_strong": "#DCE2EB", "border_grid": "#EDF0F5",
    "border_control_indicator": "#CBD5E1", "border_checked": "#3B82F6",
    "action_primary": "#5965D8", "action_primary_hover": "#595EE8", "action_primary_pressed": "#4B50DF",
    "action_primary_disabled": "#94A3B8", "action_secondary": "#FFFFFF",
    "action_secondary_hover": "#F1F5F9", "action_secondary_pressed": "#E2E8F0",
    "action_secondary_disabled": "#F8FAFC", "action_ghost": "transparent", "action_ghost_hover": "#EDEAFF",
    "action_checked": "#2563EB",
    "action_destructive": "#D76676", "action_destructive_hover": "#E18491",
    "success_surface": "#EEF9F4", "success_text": "#173127", "success_border": "#64B992", "success_icon": "#4EAD80",
    "feedback_success_surface": "#F0FDF4", "feedback_success_border": "#86EFAC",
    "warning_surface": "#FFF8E8", "warning_text": "#9A6614", "warning_border": "#F0DEB4", "warning_icon": "#9A6614",
    "danger_surface": "#FFF1F3", "danger_text": "#351D24", "danger_border": "#E18491", "danger_icon": "#D76676",
    "feedback_danger_surface": "#FEF2F2", "feedback_danger_border": "#FCA5A5",
    "info_surface": "#EEF6FF", "info_text": "#28679E", "info_border": "#D2E6FA", "info_icon": "#28679E",
    "focus_ring": "#7667E8", "focus_keyboard": "#7882E8",
    "icon_default": "#475569", "icon_muted": "#64748B", "icon_disabled": "#94A3B8",
    "icon_action": "#355874", "icon_highlight": "#FFFFFF", "icon_configuration": "#0F3989",
    "overlay_scrim": "#66000000", "overlay_light": "#80FFFFFF", "overlay_dark": "#33000000", "overlay_selection": "#DED9FF",
    "overlay_selection_subtle": "#DED9FF",
    "glow_primary": "#335965D8", "glow_focus": "#335965D8", "glow_success": "#64B992", "glow_danger": "#E18491",
}

_DARK = {
    "canvas_app": "#101722", "canvas_dialog": "#182230", "canvas_inset": "#111827",
    "surface_primary": "#172434", "surface_secondary": "#121E2D", "surface_tertiary": "#182535",
    "surface_elevated": "#172434", "surface_inset": "#101A28", "surface_hover": "#586B84",
    "surface_pressed": "#151F2C", "surface_selected": "#39336E", "surface_disabled": "#172033",
    "surface_interactive": "#42536A", "surface_inverse": "#F8FAFC", "surface_focused": "#172434",
    "text_primary": "#E5E7EB", "text_secondary": "#E6EBF3", "text_muted": "#96A3B6",
    "text_disabled": "#64748B", "text_inverse": "#111827", "text_link": "#BDB3FF",
    "text_on_action": "#FFFFFF", "text_on_feedback": "#F8FAFC",
    "text_control": "#EDF1F7", "text_selected": "#FFFFFF",
    "text_choice": "#E5E7EB", "text_header": "#C8D0DD", "text_interactive_hover": "#E5E7EB",
    "text_selection_accent": "#FFFFFF",
    "text_control_subtle": "#EDF1F7", "text_readonly": "#94A3B8", "text_popup": "#EDF1F7",
    "border_default": "#40536A", "border_subtle": "#314357", "border_strong": "#475569",
    "border_hover": "#64748B", "border_active": "#7882E8", "border_selected": "#747FE9",
    "border_disabled": "#334155", "border_focus": "#7882E8", "border_control_subtle": "#40536A",
    "border_control_hover": "#40536A", "border_divider": "#2D3E52",
    "border_divider_strong": "#40536A", "border_grid": "#25364A",
    "border_control_indicator": "#475569", "border_checked": "#60A5FA",
    "action_primary": "#5965D8", "action_primary_hover": "#6579EC", "action_primary_pressed": "#4B50DF",
    "action_primary_disabled": "#475569", "action_secondary": "#1F2937",
    "action_secondary_hover": "#273449", "action_secondary_pressed": "#334155",
    "action_secondary_disabled": "#172033", "action_ghost": "transparent", "action_ghost_hover": "#3B356F",
    "action_checked": "#2563EB",
    "action_destructive": "#D76676", "action_destructive_hover": "#E18491",
    "success_surface": "#173127", "success_text": "#EEF9F4", "success_border": "#4EAD80", "success_icon": "#64B992",
    "feedback_success_surface": "#163523", "feedback_success_border": "#22C55E",
    "warning_surface": "#402827", "warning_text": "#FFF8E8", "warning_border": "#8D554D", "warning_icon": "#F0DEB4",
    "danger_surface": "#351D24", "danger_text": "#FFF1F3", "danger_border": "#D76676", "danger_icon": "#E18491",
    "feedback_danger_surface": "#3F1218", "feedback_danger_border": "#EF4444",
    "info_surface": "#17334E", "info_text": "#D9F4FF", "info_border": "#315D79", "info_icon": "#8FD8FF",
    "focus_ring": "#8879F3", "focus_keyboard": "#6579EC",
    "icon_default": "#CBD5E1", "icon_muted": "#94A3B8", "icon_disabled": "#64748B",
    "icon_action": "#BED0E1", "icon_highlight": "#FFFFFF", "icon_configuration": "#BED0E1",
    "overlay_scrim": "#66000000", "overlay_light": "#80FFFFFF", "overlay_dark": "#33000000", "overlay_selection": "#5549AD",
    "overlay_selection_subtle": "#5549AD",
    "glow_primary": "#335965D8", "glow_focus": "#7882E8", "glow_success": "#4EAD80", "glow_danger": "#D76676",
}

_FUTURISTIC = {
    "canvas_app": "#0B111D", "canvas_dialog": "#0D1D2D", "canvas_inset": "#0B1724",
    "surface_primary": "#0D1D2D", "surface_secondary": "#0A192B", "surface_tertiary": "#0C1A29",
    "surface_elevated": "#102238", "surface_inset": "#0A1726", "surface_hover": "#4D82AE",
    "surface_pressed": "#14283B", "surface_selected": "#234766", "surface_disabled": "#101F30",
    "surface_interactive": "#365F86", "surface_inverse": "#102235", "surface_focused": "#102436",
    "text_primary": "#D8EEFF", "text_secondary": "#E7F3FF", "text_muted": "#91ABC0",
    "text_disabled": "#638097", "text_inverse": "#07111E", "text_link": "#D9FCFF",
    "text_on_action": "#FFFFFF", "text_on_feedback": "#F8FAFC",
    "text_control": "#EEF9FF", "text_selected": "#FFFFFF",
    "text_choice": "#D9ECFF", "text_header": "#B7CEDE", "text_interactive_hover": "#F4FBFF",
    "text_selection_accent": "#FFFFFF",
    "text_control_subtle": "#E7F5FF", "text_readonly": "#9CB4C8", "text_popup": "#EEF8FF",
    "border_default": "#40668B", "border_subtle": "#305474", "border_strong": "#386688",
    "border_hover": "#58A6D3", "border_active": "#4B88B0", "border_selected": "#4D88B4",
    "border_disabled": "#28465D", "border_focus": "#70C6E8", "border_control_subtle": "#355F82",
    "border_control_hover": "#4F8EBD", "border_divider": "#284965",
    "border_divider_strong": "#346080", "border_grid": "#20394F",
    "border_control_indicator": "#5A8BB1", "border_checked": "#7FD5EF",
    "action_primary": "#4447E8", "action_primary_hover": "#5355F2", "action_primary_pressed": "#3C42D2",
    "action_primary_disabled": "#46566A", "action_secondary": "#11253A",
    "action_secondary_hover": "#17314B", "action_secondary_pressed": "#0F2235",
    "action_secondary_disabled": "#0D1827", "action_ghost": "transparent", "action_ghost_hover": "#27496D",
    "action_checked": "#2C6FA0",
    "action_destructive": "#D96777", "action_destructive_hover": "#E18491",
    "success_surface": "#153127", "success_text": "#EEF9F4", "success_border": "#4EBA86", "success_icon": "#64B992",
    "feedback_success_surface": "#171F2B", "feedback_success_border": "#3A4656",
    "warning_surface": "#402827", "warning_text": "#FFF8E8", "warning_border": "#8D554D", "warning_icon": "#F0DEB4",
    "danger_surface": "#351C24", "danger_text": "#FFF1F3", "danger_border": "#D96777", "danger_icon": "#E18491",
    "feedback_danger_surface": "#171F2B", "feedback_danger_border": "#3A4656",
    "info_surface": "#17334E", "info_text": "#D9F4FF", "info_border": "#3F7599", "info_icon": "#8FD8FF",
    "focus_ring": "#59E3FF", "focus_keyboard": "#8FD8FF",
    "icon_default": "#B6D9E8", "icon_muted": "#82ABC5", "icon_disabled": "#55768B",
    "icon_action": "#B6D9E8", "icon_highlight": "#FFFFFF", "icon_configuration": "#B6D9E8",
    "overlay_scrim": "#66000000", "overlay_light": "#80FFFFFF", "overlay_dark": "#33000000", "overlay_selection": "#365E9F",
    "overlay_selection_subtle": "#285B8D",
    "glow_primary": "#757FFF", "glow_focus": "#8FD8FF", "glow_success": "#4EBA86", "glow_danger": "#D96777",
}


_LIGHT_COMPONENT_OVERRIDES = {
    "answer.normal_surface": "#FFFFFF", "answer.normal_border": "#E0E6ED",
    "answer.normal_text": "#1F2937",
    "answer.hover_surface": "#F9FAFC", "answer.hover_border": "#BEC9D6",
    "answer.selected_surface": "#F0F2FF", "answer.selected_border": "#7882E8",
    "answer.selected_text": "#1F2937", "answer.keyboard_focus_border": "#5966D9",
    "answer.checked_indicator": "#5965D8",
    "answer.indicator_surface": "#FFFFFF", "answer.indicator_border": "#8A96A6",
    "answer.indicator_hover_border": "#6672D9",
    "answer.indicator_checked_border": "#5965D8", "answer.indicator_text": "#1E293B",
    "answer.disabled_text": "#CBD5E1", "answer.correct_surface": "#EEF9F4",
    "answer.correct_border": "#64B992", "answer.incorrect_surface": "#FFF1F3",
    "answer.incorrect_border": "#E18491", "answer.struck_surface": "#E7ECF2",
    "answer.struck_border": "#8796A8", "answer.struck_text": "#718096",
    "answer.struck_hover_surface": "#E3E9F0", "answer.struck_hover_border": "#728398",
    "answer.eliminate_text": "#94A3B8", "answer.eliminate_hover_surface": "#F1F5F9",
    "answer.eliminate_hover_text": "#475569",
    "answer.eliminate_checked_surface": "#D8E0E9",
    "answer.eliminate_checked_text": "#334155",
    "answer.eliminate_checked_border": "#8493A6",
    "answer.explanation_surface": "#F8FAFC", "answer.explanation_border": "#DBE3ED",
    "answer.explanation_title_text": "#334155", "answer.explanation_text": "#475569",
    "answer.editor_surface": "#FFFFFF", "answer.editor_border": "#CBD5E1",
    "answer.editor_text": "#334155", "answer.editor_selection": "#DED9FF",
    "answer.edit_action_surface": "#FFFFFF",
    "answer.edit_action_hover_surface": "#EEF2FF",
    "answer.edit_action_hover_text": "#4338CA",
    "answer.edit_action_hover_border": "#A5B4FC",
    "answer.save_action_surface": "#4F46E5", "answer.save_action_text": "#FFFFFF",
    "answer.save_action_border": "#4338CA", "answer.cancel_action_surface": "#FFFFFF",
    "answer.primary_action_border": "#7885F0",
    "answer.primary_action_hover_border": "#98A2F7",
    "progress.track": "#E8EDF3", "progress.text": "#475569",
    "calendar.surface": "#FFFFFF", "calendar.border": "#DBE3ED", "calendar.text": "#1F2937",
    "calendar.title_text": "#111827",
    "calendar.today_surface": "#DBEAFE", "calendar.today_border": "#93C5FD",
    "calendar.today_text": "#1D4ED8", "calendar.selected_surface": "#2563EB",
    "calendar.selected_text": "#FFFFFF", "calendar.week_predicted_surface": "#F8FAFC",
    "calendar.week_predicted_border": "#E2E8F0", "calendar.week_predicted_text": "#0F172A",
    "calendar.weekend_text": "#475569", "calendar.badge_surface": "#F1F5F9",
    "calendar.badge_text": "#475569", "calendar.badge_border": "#E2E8F0",
    "calendar.legend_today": "#2563EB", "calendar.legend_late": "#DC2626",
    "calendar.legend_scheduled": "#16A34A", "calendar.navigation_surface": "#F8FAFC",
    "calendar.navigation_hover_surface": "#E2E8F0", "calendar.input_surface": "#FFFFFF",
    "calendar.input_border": "#CBD5E1", "calendar.late_surface": "#FEE2E2",
    "calendar.late_text": "#B91C1C", "calendar.scheduled_surface": "#DCFCE7",
    "calendar.scheduled_text": "#15803D",
    "calendar.forecast_toggle_surface": "#FFFFFF", "calendar.forecast_toggle_text": "#64748B",
    "calendar.forecast_toggle_border": "#D7E0EA",
    "calendar.forecast_toggle_hover_surface": "#F8FAFC",
    "calendar.forecast_toggle_hover_text": "#334155",
    "calendar.forecast_toggle_hover_border": "#CBD5E1",
    "calendar.forecast_toggle_checked_surface": "#E8F1FF",
    "calendar.forecast_toggle_checked_border": "#93C5FD",
    "calendar.forecast_action_text": "#1D4ED8", "calendar.forecast_meta_text": "#64748B",
    "calendar.forecast_panel_surface": "#FFFFFF", "calendar.forecast_panel_border": "#DBE3ED",
    "calendar.forecast_title_text": "#111827", "calendar.forecast_notice_text": "#475569",
    "calendar.forecast_today_surface": "#F0F7FF", "calendar.forecast_past_surface": "#F8FAFC",
    "calendar.forecast_past_border": "#E2E8F0", "calendar.forecast_count_surface": "#E2E8F0",
    "calendar.forecast_count_text": "#475569", "calendar.forecast_badge_surface": "#F1F5F9",
    "calendar.forecast_badge_text": "#475569", "calendar.forecast_badge_border": "#E2E8F0",
    "calendar.forecast_card_surface": "#FFFFFF", "calendar.forecast_card_accent": "#64748B",
    "calendar.forecast_review": "#2563EB", "calendar.forecast_completed": "#16A34A",
    "calendar.forecast_recommendation": "#7C3AED", "calendar.forecast_simulation": "#D97706",
    "calendar.forecast_discipline_text": "#475569", "calendar.forecast_card_text": "#111827",
    "calendar.forecast_open_text": "#64748B", "calendar.forecast_open_hover_surface": "#E8F1FF",
    "calendar.forecast_open_hover_border": "#BFDBFE", "calendar.forecast_empty_text": "#94A3B8",
    "chart.grid": "#E2E8F0", "chart.label": "#475569",
    "focus_mode.panel": "#F8FAFC", "focus_mode.panel_active": "#F0F2FF",
}
_DARK_COMPONENT_OVERRIDES = {
    "answer.normal_surface": "#151F2C", "answer.normal_border": "#2F3D4D",
    "answer.normal_text": "#E2E8F0",
    "answer.hover_surface": "#192534", "answer.hover_border": "#4A5A6E",
    "answer.selected_surface": "#1D2440", "answer.selected_border": "#747FE9",
    "answer.selected_text": "#E2E8F0", "answer.keyboard_focus_border": "#8B95FF",
    "answer.checked_indicator": "#626DE0",
    "answer.indicator_surface": "#101722", "answer.indicator_border": "#687789",
    "answer.indicator_hover_border": "#8791F2",
    "answer.indicator_checked_border": "#A4ABFF", "answer.indicator_text": "#E2E8F0",
    "answer.disabled_text": "#475569",
    "answer.struck_surface": "#0B121C", "answer.struck_border": "#526276",
    "answer.struck_text": "#627488", "answer.struck_hover_surface": "#0E1723",
    "answer.struck_hover_border": "#66788E",
    "answer.eliminate_text": "#64748B", "answer.eliminate_hover_surface": "#273449",
    "answer.eliminate_hover_text": "#CBD5E1",
    "answer.eliminate_checked_surface": "#1D2A38",
    "answer.eliminate_checked_text": "#A1B2C3",
    "answer.eliminate_checked_border": "#5A6D82",
    "answer.correct_surface": "#173127", "answer.correct_border": "#4EAD80",
    "answer.incorrect_surface": "#351D24", "answer.incorrect_border": "#D76676",
    "answer.explanation_surface": "#1F2937", "answer.explanation_border": "#334155",
    "answer.explanation_title_text": "#CBD5E1", "answer.explanation_text": "#CBD5E1",
    "answer.editor_surface": "#111827", "answer.editor_border": "#475569",
    "answer.editor_text": "#E2E8F0", "answer.editor_selection": "#5549AD",
    "answer.edit_action_surface": "#182235",
    "answer.edit_action_hover_surface": "#273449",
    "answer.edit_action_hover_text": "#FFFFFF",
    "answer.edit_action_hover_border": "#8B95FF",
    "answer.save_action_surface": "#6366F1", "answer.save_action_text": "#FFFFFF",
    "answer.save_action_border": "#818CF8", "answer.cancel_action_surface": "#1F2937",
    "answer.primary_action_border": "#7885F0",
    "answer.primary_action_hover_border": "#A2AAFF",
    "progress.track": "#111827", "progress.text": "#CBD5E1",
    "calendar.surface": "#182235", "calendar.border": "#334155", "calendar.text": "#E5E7EB",
    "calendar.title_text": "#F8FAFC",
    "calendar.today_surface": "#1E3A8A", "calendar.today_border": "#1E40AF",
    "calendar.today_text": "#93C5FD", "calendar.selected_surface": "#2563EB",
    "calendar.selected_text": "#FFFFFF", "calendar.week_predicted_surface": "#172033",
    "calendar.week_predicted_border": "#334155", "calendar.week_predicted_text": "#F8FAFC",
    "calendar.weekend_text": "#CBD5E1", "calendar.badge_surface": "#273449",
    "calendar.badge_text": "#CBD5E1", "calendar.badge_border": "#334155",
    "calendar.legend_today": "#93C5FD", "calendar.legend_late": "#FCA5A5",
    "calendar.legend_scheduled": "#86EFAC", "calendar.navigation_surface": "#172033",
    "calendar.navigation_hover_surface": "#273449", "calendar.input_surface": "#172033",
    "calendar.input_border": "#475569", "calendar.late_surface": "#4C1D24",
    "calendar.late_text": "#FCA5A5", "calendar.scheduled_surface": "#163523",
    "calendar.scheduled_text": "#86EFAC",
    "calendar.forecast_toggle_surface": "#172033", "calendar.forecast_toggle_text": "#94A3B8",
    "calendar.forecast_toggle_border": "#334155",
    "calendar.forecast_toggle_hover_surface": "#273449",
    "calendar.forecast_toggle_hover_text": "#E2E8F0",
    "calendar.forecast_toggle_hover_border": "#475569",
    "calendar.forecast_toggle_checked_surface": "#172554",
    "calendar.forecast_toggle_checked_border": "#1E40AF",
    "calendar.forecast_action_text": "#93C5FD", "calendar.forecast_meta_text": "#94A3B8",
    "calendar.forecast_panel_surface": "#182235", "calendar.forecast_panel_border": "#334155",
    "calendar.forecast_title_text": "#F8FAFC", "calendar.forecast_notice_text": "#CBD5E1",
    "calendar.forecast_today_surface": "#172554", "calendar.forecast_past_surface": "#151E2E",
    "calendar.forecast_past_border": "#2B394B", "calendar.forecast_count_surface": "#273449",
    "calendar.forecast_count_text": "#CBD5E1", "calendar.forecast_badge_surface": "#273449",
    "calendar.forecast_badge_text": "#CBD5E1", "calendar.forecast_badge_border": "#3B4A61",
    "calendar.forecast_card_surface": "#1D293D", "calendar.forecast_card_accent": "#64748B",
    "calendar.forecast_review": "#60A5FA", "calendar.forecast_completed": "#4ADE80",
    "calendar.forecast_recommendation": "#A78BFA", "calendar.forecast_simulation": "#F59E0B",
    "calendar.forecast_discipline_text": "#94A3B8", "calendar.forecast_card_text": "#F1F5F9",
    "calendar.forecast_open_text": "#94A3B8", "calendar.forecast_open_hover_surface": "#273449",
    "calendar.forecast_open_hover_border": "#475569", "calendar.forecast_empty_text": "#64748B",
    "chart.grid": "#273449", "chart.label": "#CBD5E1",
    "focus_mode.panel": "#172033", "focus_mode.panel_active": "#1D2440",
    "focus_mode.text": "#F8FAFC",
}
_FUTURISTIC_COMPONENT_OVERRIDES = {
    "answer.normal_surface": "#111A27", "answer.normal_border": "#2B3747",
    "answer.normal_text": "#DFE7EF",
    "answer.hover_surface": "#162130", "answer.hover_border": "#46566A",
    "answer.selected_surface": "#1B213A", "answer.selected_border": "#757FFF",
    "answer.selected_text": "#DFE7EF", "answer.pressed_border": "#3F7599",
    "answer.focused_border": "#757FFF", "answer.keyboard_focus_border": "#4BC9F2",
    "answer.checked_indicator": "#6269E8",
    "answer.indicator_surface": "#0E1622", "answer.indicator_border": "#687789",
    "answer.indicator_hover_border": "#8A94FA",
    "answer.indicator_checked_border": "#ADB2FF", "answer.indicator_text": "#EAF0F6",
    "answer.disabled_border": "#2B3747", "answer.disabled_text": "#475569",
    "answer.struck_surface": "#07101A", "answer.struck_border": "#3E617A",
    "answer.struck_text": "#607A8E", "answer.struck_hover_surface": "#0A1622",
    "answer.struck_hover_border": "#507A97",
    "answer.eliminate_text": "#718094", "answer.eliminate_hover_surface": "#222C39",
    "answer.eliminate_hover_text": "#CAD4DF",
    "answer.eliminate_checked_surface": "#132C3F",
    "answer.eliminate_checked_text": "#B5D1E2",
    "answer.eliminate_checked_border": "#507A97",
    "answer.explanation_surface": "#171F2B", "answer.explanation_border": "#3A4656",
    "answer.explanation_title_text": "#9FC4DD", "answer.explanation_text": "#CBD5E1",
    "answer.editor_surface": "#0A1725", "answer.editor_border": "#355F82",
    "answer.editor_text": "#E7F5FF", "answer.editor_selection": "#285B8D",
    "answer.edit_action_surface": "#0D1D2D",
    "answer.edit_action_hover_surface": "#15324A",
    "answer.edit_action_hover_text": "#F2FBFF",
    "answer.edit_action_hover_border": "#4BC9F2",
    "answer.save_action_surface": "#19527A", "answer.save_action_text": "#F1FAFF",
    "answer.save_action_border": "#4BC9F2", "answer.cancel_action_surface": "#0D1D2D",
    "answer.primary_action_border": "#7C83FF",
    "answer.primary_action_hover_border": "#B1B7FF",
    "answer.correct_surface": "#153127", "answer.correct_border": "#4EBA86",
    "answer.incorrect_surface": "#351C24", "answer.incorrect_border": "#D96777",
    "progress.track": "#102235", "progress.border": "#315A7A",
    "progress.fill": "#4AA5D3", "progress.text": "#EAF7FF",
    "calendar.surface": "#182235", "calendar.border": "#334155", "calendar.text": "#E5E7EB",
    "calendar.title_text": "#F8FAFC",
    "calendar.today_surface": "#124E68", "calendar.today_border": "#3D9BC5",
    "calendar.today_text": "#BDF7FF", "calendar.selected_surface": "#2563EB",
    "calendar.selected_text": "#FFFFFF", "calendar.week_predicted_surface": "#0D1D2D",
    "calendar.week_predicted_border": "#294B63", "calendar.week_predicted_text": "#E9F8FF",
    "calendar.weekend_text": "#B6D9E8", "calendar.outside_month_text": "#55768B",
    "calendar.badge_surface": "#273449", "calendar.badge_text": "#CBD5E1",
    "calendar.badge_border": "#334155", "calendar.legend_today": "#93C5FD",
    "calendar.legend_late": "#FCA5A5", "calendar.legend_scheduled": "#86EFAC",
    "calendar.navigation_surface": "#172033", "calendar.navigation_hover_surface": "#273449",
    "calendar.input_surface": "#172033", "calendar.input_border": "#475569",
    "calendar.late_surface": "#4B1D2C", "calendar.late_text": "#FF9BAC",
    "calendar.scheduled_surface": "#124334", "calendar.scheduled_text": "#74F1C5",
    "calendar.forecast_toggle_surface": "#0D1D2D", "calendar.forecast_toggle_text": "#84A9BD",
    "calendar.forecast_toggle_border": "#294B63",
    "calendar.forecast_toggle_hover_surface": "#123049",
    "calendar.forecast_toggle_hover_text": "#D7F3FF",
    "calendar.forecast_toggle_hover_border": "#39789A",
    "calendar.forecast_toggle_checked_surface": "#143A55",
    "calendar.forecast_toggle_checked_border": "#45BCE8",
    "calendar.forecast_action_text": "#BDF7FF", "calendar.forecast_meta_text": "#7FA2B5",
    "calendar.forecast_panel_surface": "#0B1A27", "calendar.forecast_panel_border": "#294B63",
    "calendar.forecast_title_text": "#E7F7FF", "calendar.forecast_notice_text": "#9FC4D6",
    "calendar.forecast_today_surface": "#10304A", "calendar.forecast_past_surface": "#0B1824",
    "calendar.forecast_past_border": "#223D50", "calendar.forecast_count_surface": "#153149",
    "calendar.forecast_count_text": "#A8D9EE", "calendar.forecast_badge_surface": "#153149",
    "calendar.forecast_badge_text": "#A8D9EE", "calendar.forecast_badge_border": "#315B75",
    "calendar.forecast_card_surface": "#102334", "calendar.forecast_card_accent": "#5F8296",
    "calendar.forecast_review": "#4BC9F2", "calendar.forecast_completed": "#74F1C5",
    "calendar.forecast_recommendation": "#8D7CFF", "calendar.forecast_simulation": "#E7B14B",
    "calendar.forecast_discipline_text": "#82ABC0", "calendar.forecast_card_text": "#E7F5FF",
    "calendar.forecast_open_text": "#82ABC0", "calendar.forecast_open_hover_surface": "#153149",
    "calendar.forecast_open_hover_border": "#39789A", "calendar.forecast_empty_text": "#638397",
    "chart.axis": "#315D79", "chart.grid": "#2E5C78", "chart.label": "#B6D9E8",
    "focus_mode.canvas": "#0B111D", "focus_mode.panel": "#101F30",
    "focus_mode.panel_active": "#10283C", "focus_mode.text": "#EAF7FF",
    "focus_mode.timer": "#8FD8FF", "focus_mode.border": "#3F7599",
    "focus_mode.action": "#D62B3D", "focus_mode.danger": "#D96777",
}


def _theme_gradients(kind: ThemeName) -> dict[str, GradientSpec]:
    if kind is ThemeName.LIGHT:
        action = ((0.0, "#4B50DF"), (1.0, "#586DE3"))
        action_hover = ((0.0, "#595EE8"), (1.0, "#6579EC"))
        selected = ((0.0, "#F0F2FF"), (1.0, "#F0F2FF"))
        correct = ((0.0, "#EEF9F4"), (1.0, "#EEF9F4"))
        incorrect = ((0.0, "#FFF1F3"), (1.0, "#FFF1F3"))
        struck = ((0.0, "#E7ECF2"), (1.0, "#E7ECF2"))
        surface = ((0.0, "#FFFFFF"), (1.0, "#F8FAFC"))
        focus_action = action
        focus_hover = action_hover
        control_input = ((0.0, "#FFFFFF"), (1.0, "#FFFFFF"))
        control_header = ((0.0, "#F7F8FB"), (1.0, "#F7F8FB"))
        control_tab = ((0.0, "#EEF1F6"), (1.0, "#EEF1F6"))
        control_selected = ((0.0, "#FFFFFF"), (1.0, "#FFFFFF"))
    elif kind is ThemeName.DARK:
        action = ((0.0, "#4B50DF"), (1.0, "#586DE3"))
        action_hover = ((0.0, "#595EE8"), (1.0, "#6579EC"))
        selected = ((0.0, "#1D2440"), (1.0, "#1D2440"))
        correct = ((0.0, "#173127"), (1.0, "#173127"))
        incorrect = ((0.0, "#351D24"), (1.0, "#351D24"))
        struck = ((0.0, "#0B121C"), (1.0, "#0B121C"))
        surface = ((0.0, "#273449"), (1.0, "#182230"))
        focus_action = action
        focus_hover = action_hover
        control_input = ((0.0, "#172434"), (1.0, "#172434"))
        control_header = ((0.0, "#182535"), (1.0, "#182535"))
        control_tab = ((0.0, "#182535"), (1.0, "#182535"))
        control_selected = ((0.0, "#121E2D"), (1.0, "#121E2D"))
    else:
        action = ((0.0, "#4447E8"), (0.52, "#4347E1"), (1.0, "#3C42D2"))
        action_hover = ((0.0, "#5355F2"), (0.52, "#4F54EB"), (1.0, "#464DDE"))
        selected = ((0.0, "#1B213A"), (1.0, "#18243A"))
        correct = ((0.0, "#153127"), (1.0, "#12271F"))
        incorrect = ((0.0, "#351C24"), (1.0, "#2A171D"))
        struck = ((0.0, "#07101A"), (0.55, "#08121D"), (1.0, "#060D16"))
        surface = ((0.0, "#10283C"), (1.0, "#0D1D2D"))
        focus_action = ((0.0, "#B51F31"), (0.52, "#D62B3D"), (1.0, "#F04458"))
        focus_hover = ((0.0, "#CE293B"), (0.52, "#E83B4C"), (1.0, "#FF596B"))
        control_input = ((0.0, "#10253A"), (1.0, "#0A1829"))
        control_header = ((0.0, "#132C45"), (1.0, "#0C1D31"))
        control_tab = ((0.0, "#132B42"), (1.0, "#0C1D30"))
        control_selected = ((0.0, "#0E6677"), (1.0, "#323E8E"))

    return {
        "gradient.action_primary": _palette_gradient(*action),
        "gradient.action_primary_hover": _palette_gradient(*action_hover),
        "gradient.surface_elevated": _palette_gradient(
            *surface, direction=GradientDirection(0.0, 0.0, 1.0, 1.0)
        ),
        "gradient.hero": _palette_gradient(*surface),
        "gradient.progress": _palette_gradient(*action),
        "gradient.control_input": _palette_gradient(
            *control_input, direction=GradientDirection(0.0, 0.0, 1.0, 1.0)
        ),
        "gradient.control_header": _palette_gradient(*control_header),
        "gradient.control_tab": _palette_gradient(*control_tab),
        "gradient.control_selected": _palette_gradient(*control_selected),
        "answer.selected_gradient": _palette_gradient(*selected),
        "answer.correct_gradient": _palette_gradient(
            *correct, direction=GradientDirection(0.0, 0.0, 1.0, 1.0)
        ),
        "answer.incorrect_gradient": _palette_gradient(
            *incorrect, direction=GradientDirection(0.0, 0.0, 1.0, 1.0)
        ),
        "answer.struck_gradient": _palette_gradient(
            *struck, direction=GradientDirection(0.0, 0.0, 1.0, 1.0)
        ),
        "progress.fill_gradient": _palette_gradient(*action),
        "focus_mode.action_gradient": _palette_gradient(*focus_action),
        "focus_mode.action_hover_gradient": _palette_gradient(*focus_hover),
        "startup.progress_gradient": _palette_gradient(
            (0.0, "#2E74D8"),
            (0.55, "#3A8DF1"),
            (1.0, "#4CA8FF"),
        ),
        "startup.shimmer_gradient": _palette_gradient(
            (0.0, "#007DD7FF"),
            (0.5, "#96AFE8FF"),
            (1.0, "#007DD7FF"),
        ),
    }


LIGHT_THEME = _make_theme(ThemeName.LIGHT, _LIGHT, _LIGHT_COMPONENT_OVERRIDES, _theme_gradients(ThemeName.LIGHT))
DARK_THEME = _make_theme(ThemeName.DARK, _DARK, _DARK_COMPONENT_OVERRIDES, _theme_gradients(ThemeName.DARK))
FUTURISTIC_THEME = _make_theme(
    ThemeName.FUTURISTIC,
    _FUTURISTIC,
    _FUTURISTIC_COMPONENT_OVERRIDES,
    _theme_gradients(ThemeName.FUTURISTIC),
)

THEMES: Mapping[ThemeName, ThemeDefinition] = MappingProxyType(
    {
        ThemeName.LIGHT: LIGHT_THEME,
        ThemeName.DARK: DARK_THEME,
        ThemeName.FUTURISTIC: FUTURISTIC_THEME,
    }
)


def fixed_color(token: str | TokenSpec) -> ColorValue:
    """Resolve uma cor deliberadamente fixa e valida sua invariância temática."""

    path = token.path if isinstance(token, TokenSpec) else token
    if path not in FIXED_TOKEN_PATHS:
        raise TokenNotFoundError(f"Token visual fixo inexistente: {path!r}")
    colors = tuple(theme.color(path) for theme in THEMES.values())
    if len(set(colors)) != 1:
        raise ThemeContractError(f"Token fixo varia entre temas: {path!r}")
    return colors[0]


def fixed_gradient(token: str | TokenSpec) -> GradientSpec:
    """Resolve um gradiente deliberadamente fixo e valida os três contratos."""

    path = token.path if isinstance(token, TokenSpec) else token
    if path not in FIXED_TOKEN_PATHS:
        raise TokenNotFoundError(f"Token visual fixo inexistente: {path!r}")
    gradients = tuple(theme.gradient(path) for theme in THEMES.values())
    if len(set(gradients)) != 1:
        raise ThemeContractError(f"Gradiente fixo varia entre temas: {path!r}")
    return gradients[0]


for _fixed_path in FIXED_TOKEN_PATHS:
    _fixed_spec = token_spec(_fixed_path)
    if _fixed_spec.kind is TokenKind.COLOR:
        fixed_color(_fixed_spec)
    else:
        fixed_gradient(_fixed_spec)


def get_theme(theme: ThemeName | str) -> ThemeDefinition:
    if isinstance(theme, ThemeDefinition):
        return theme
    try:
        name = theme if isinstance(theme, ThemeName) else ThemeName(str(theme).strip().lower())
    except ValueError as exc:
        valid = ", ".join(item.value for item in ThemeName)
        raise ValueError(f"Tema desconhecido: {theme!r}. Valores válidos: {valid}.") from exc
    return THEMES[name]
