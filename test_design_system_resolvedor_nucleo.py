"""Caracterização da Etapa 3E-A1 do núcleo visual do Resolvedor."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest

import tema
from ui.design import (
    ALL_TOKENS,
    COMPONENT_TOKEN_COUNT,
    COMPONENT_TOKENS,
    SEMANTIC_TOKEN_COUNT,
    get_theme,
)


ROOT = Path(__file__).resolve().parent
TEMA_SOURCE = (ROOT / "tema.py").read_text(encoding="utf-8")

EXPECTED_STYLESHEET_BASELINE = {
    "claro": "139709f8c57e00f16848668f9226703c7f8ff391dd9aea2bba8b2eae20ac2c5f",
    "escuro": "ebbc21363d0035058301d060eb099fb2d33b992e8537c20f9bf1e77f8a2b4f3e",
    "futurista": "0e588bb372946b4a6f61ad406c817fd155cac8c3c4286e9f93b7a09d06dc8622",
}

THEMES = {
    "claro": tema.stylesheet_claro,
    "escuro": tema.stylesheet_escuro,
    "futurista": tema.stylesheet_futurista,
}

EXPECTED_COLORS = {
    "claro": {
        "answer.normal_surface": "#FFFFFF",
        "answer.normal_border": "#E0E6ED",
        "answer.normal_text": "#1F2937",
        "answer.hover_surface": "#F9FAFC",
        "answer.hover_border": "#BEC9D6",
        "answer.selected_surface": "#F0F2FF",
        "answer.selected_border": "#7882E8",
        "answer.keyboard_focus_border": "#5966D9",
        "answer.indicator_surface": "#FFFFFF",
        "answer.indicator_border": "#8A96A6",
        "answer.indicator_hover_border": "#6672D9",
        "answer.checked_indicator": "#5965D8",
        "answer.indicator_checked_border": "#5965D8",
        "answer.indicator_text": "#1E293B",
        "answer.correct_surface": "#EEF9F4",
        "answer.correct_border": "#64B992",
        "answer.incorrect_surface": "#FFF1F3",
        "answer.incorrect_border": "#E18491",
        "answer.struck_surface": "#E7ECF2",
        "answer.struck_border": "#8796A8",
        "answer.struck_text": "#718096",
        "answer.struck_hover_surface": "#E3E9F0",
        "answer.struck_hover_border": "#728398",
        "answer.eliminate_text": "#94A3B8",
        "answer.eliminate_hover_surface": "#F1F5F9",
        "answer.eliminate_hover_text": "#475569",
        "answer.eliminate_checked_surface": "#D8E0E9",
        "answer.eliminate_checked_text": "#334155",
        "answer.eliminate_checked_border": "#8493A6",
        "answer.disabled_text": "#CBD5E1",
        "answer.explanation_surface": "#F8FAFC",
        "answer.explanation_border": "#DBE3ED",
        "answer.explanation_title_text": "#334155",
        "answer.explanation_text": "#475569",
        "answer.editor_surface": "#FFFFFF",
        "answer.editor_border": "#CBD5E1",
        "answer.editor_text": "#334155",
        "answer.editor_selection": "#DED9FF",
    },
    "escuro": {
        "answer.normal_surface": "#151F2C",
        "answer.normal_border": "#2F3D4D",
        "answer.normal_text": "#E2E8F0",
        "answer.hover_surface": "#192534",
        "answer.hover_border": "#4A5A6E",
        "answer.selected_surface": "#1D2440",
        "answer.selected_border": "#747FE9",
        "answer.keyboard_focus_border": "#8B95FF",
        "answer.indicator_surface": "#101722",
        "answer.indicator_border": "#687789",
        "answer.indicator_hover_border": "#8791F2",
        "answer.checked_indicator": "#626DE0",
        "answer.indicator_checked_border": "#A4ABFF",
        "answer.indicator_text": "#E2E8F0",
        "answer.correct_surface": "#173127",
        "answer.correct_border": "#4EAD80",
        "answer.incorrect_surface": "#351D24",
        "answer.incorrect_border": "#D76676",
        "answer.struck_surface": "#0B121C",
        "answer.struck_border": "#526276",
        "answer.struck_text": "#627488",
        "answer.struck_hover_surface": "#0E1723",
        "answer.struck_hover_border": "#66788E",
        "answer.eliminate_text": "#64748B",
        "answer.eliminate_hover_surface": "#273449",
        "answer.eliminate_hover_text": "#CBD5E1",
        "answer.eliminate_checked_surface": "#1D2A38",
        "answer.eliminate_checked_text": "#A1B2C3",
        "answer.eliminate_checked_border": "#5A6D82",
        "answer.disabled_text": "#475569",
        "answer.explanation_surface": "#1F2937",
        "answer.explanation_border": "#334155",
        "answer.explanation_title_text": "#CBD5E1",
        "answer.explanation_text": "#CBD5E1",
        "answer.editor_surface": "#111827",
        "answer.editor_border": "#475569",
        "answer.editor_text": "#E2E8F0",
        "answer.editor_selection": "#5549AD",
    },
    "futurista": {
        "answer.normal_surface": "#111A27",
        "answer.normal_border": "#2B3747",
        "answer.normal_text": "#DFE7EF",
        "answer.hover_surface": "#162130",
        "answer.hover_border": "#46566A",
        "answer.selected_surface": "#1B213A",
        "answer.selected_border": "#757FFF",
        "answer.keyboard_focus_border": "#4BC9F2",
        "answer.indicator_surface": "#0E1622",
        "answer.indicator_border": "#687789",
        "answer.indicator_hover_border": "#8A94FA",
        "answer.checked_indicator": "#6269E8",
        "answer.indicator_checked_border": "#ADB2FF",
        "answer.indicator_text": "#EAF0F6",
        "answer.correct_surface": "#153127",
        "answer.correct_border": "#4EBA86",
        "answer.incorrect_surface": "#351C24",
        "answer.incorrect_border": "#D96777",
        "answer.struck_surface": "#07101A",
        "answer.struck_border": "#3E617A",
        "answer.struck_text": "#607A8E",
        "answer.struck_hover_surface": "#0A1622",
        "answer.struck_hover_border": "#507A97",
        "answer.eliminate_text": "#718094",
        "answer.eliminate_hover_surface": "#222C39",
        "answer.eliminate_hover_text": "#CAD4DF",
        "answer.eliminate_checked_surface": "#132C3F",
        "answer.eliminate_checked_text": "#B5D1E2",
        "answer.eliminate_checked_border": "#507A97",
        "answer.disabled_text": "#475569",
        "answer.explanation_surface": "#171F2B",
        "answer.explanation_border": "#3A4656",
        "answer.explanation_title_text": "#9FC4DD",
        "answer.explanation_text": "#CBD5E1",
        "answer.editor_surface": "#0A1725",
        "answer.editor_border": "#355F82",
        "answer.editor_text": "#E7F5FF",
        "answer.editor_selection": "#285B8D",
    },
}


def _canonical_qss(value: str) -> str:
    normalized = re.sub(
        r"#[0-9A-Fa-f]{3,8}\b",
        lambda match: match.group(0).upper(),
        value,
    )
    return re.sub(r"\s+", " ", normalized).strip()


def _constant_source(name: str, next_name: str) -> str:
    return TEMA_SOURCE.split(f"{name} =", 1)[1].split(f"{next_name} =", 1)[0]


class ResolverCoreDesignSystemTests(unittest.TestCase):
    def test_contract_includes_approved_stage_3e_a2_budget(self) -> None:
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 191)
        self.assertEqual(len(ALL_TOKENS), 293)
        self.assertEqual(
            sum(token.path.startswith("answer.") for token in COMPONENT_TOKENS),
            60,
        )

    def test_answer_colors_reproduce_final_legacy_cascade(self) -> None:
        for theme_name, expected in EXPECTED_COLORS.items():
            theme = get_theme(theme_name)
            for token, value in expected.items():
                with self.subTest(theme=theme_name, token=token):
                    self.assertEqual(theme.color(token).value, value)

    def test_answer_gradients_preserve_direction_positions_and_colors(self) -> None:
        expected = {
            "claro": {
                "answer.selected_gradient": ((0, 0, 1, 0), ((0, "#F0F2FF"), (1, "#F0F2FF"))),
                "answer.correct_gradient": ((0, 0, 1, 1), ((0, "#EEF9F4"), (1, "#EEF9F4"))),
                "answer.incorrect_gradient": ((0, 0, 1, 1), ((0, "#FFF1F3"), (1, "#FFF1F3"))),
                "answer.struck_gradient": ((0, 0, 1, 1), ((0, "#E7ECF2"), (1, "#E7ECF2"))),
            },
            "escuro": {
                "answer.selected_gradient": ((0, 0, 1, 0), ((0, "#1D2440"), (1, "#1D2440"))),
                "answer.correct_gradient": ((0, 0, 1, 1), ((0, "#173127"), (1, "#173127"))),
                "answer.incorrect_gradient": ((0, 0, 1, 1), ((0, "#351D24"), (1, "#351D24"))),
                "answer.struck_gradient": ((0, 0, 1, 1), ((0, "#0B121C"), (1, "#0B121C"))),
            },
            "futurista": {
                "answer.selected_gradient": ((0, 0, 1, 0), ((0, "#1B213A"), (1, "#18243A"))),
                "answer.correct_gradient": ((0, 0, 1, 1), ((0, "#153127"), (1, "#12271F"))),
                "answer.incorrect_gradient": ((0, 0, 1, 1), ((0, "#351C24"), (1, "#2A171D"))),
                "answer.struck_gradient": (
                    (0, 0, 1, 1),
                    ((0, "#07101A"), (0.55, "#08121D"), (1, "#060D16")),
                ),
            },
        }
        for theme_name, gradients in expected.items():
            theme = get_theme(theme_name)
            for token, (direction, stops) in gradients.items():
                with self.subTest(theme=theme_name, token=token):
                    spec = theme.gradient(token)
                    self.assertEqual(
                        (spec.direction.x1, spec.direction.y1, spec.direction.x2, spec.direction.y2),
                        direction,
                    )
                    self.assertEqual(
                        tuple((stop.position, stop.color.value) for stop in spec.stops),
                        stops,
                    )

    def test_complete_stylesheet_hashes_are_identical_to_pre_migration_baseline(self) -> None:
        for theme_name, factory in THEMES.items():
            with self.subTest(theme=theme_name):
                digest = hashlib.sha256(_canonical_qss(factory()).encode("utf-8")).hexdigest()
                self.assertEqual(digest, EXPECTED_STYLESHEET_BASELINE[theme_name])

    def test_fully_migrated_focus_and_struck_layers_have_no_visual_hex(self) -> None:
        eliminated = _constant_source(
            "ESTILO_RESOLVEDOR_ELIMINADAS_CLARO",
            "ESTILO_RESOLVEDOR_TECLADO_CLARO",
        )
        keyboard = _constant_source(
            "ESTILO_RESOLVEDOR_TECLADO_CLARO",
            "ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_CLARO",
        )
        self.assertNotRegex(eliminated, r"#[0-9A-Fa-f]{6,8}")
        self.assertNotRegex(keyboard, r"#[0-9A-Fa-f]{6,8}")
        self.assertIn("{{gradient:answer.struck_gradient}}", eliminated)
        self.assertEqual(keyboard.count("{{color:answer.keyboard_focus_border}}"), 3)

    def test_authoritative_core_selectors_use_public_answer_tokens(self) -> None:
        for marker in (
            "{{color:answer.normal_surface}}",
            "{{color:answer.hover_surface}}",
            "{{color:answer.selected_surface}}",
            "{{gradient:answer.selected_gradient}}",
            "{{gradient:answer.correct_gradient}}",
            "{{gradient:answer.incorrect_gradient}}",
            "{{color:answer.indicator_surface}}",
            "{{color:answer.checked_indicator}}",
            "{{color:answer.eliminate_text}}",
            "{{color:answer.explanation_surface}}",
            "{{color:answer.explanation_border}}",
            "{{color:answer.explanation_title_text}}",
            "{{color:answer.editor_surface}}",
            "{{color:answer.editor_text}}",
            "{{color:answer.editor_selection}}",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, TEMA_SOURCE)
        self.assertIn("from ui.design import render_qss", TEMA_SOURCE)

    def test_stage_3e_a2_editor_controls_now_use_public_tokens(self) -> None:
        editor = _constant_source(
            "ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_CLARO",
            "ESTILO_CALENDARIO_PREVISAO_CLARO",
        )
        self.assertNotRegex(editor, r"#[0-9A-Fa-f]{6,8}")
        self.assertIn("{{color:answer.edit_action_surface}}", editor)
        self.assertIn("{{color:answer.save_action_surface}}", editor)
        self.assertIn("{{color:answer.cancel_action_surface}}", editor)

    def test_qss_output_contains_no_unresolved_token_markers(self) -> None:
        for factory in THEMES.values():
            stylesheet = factory()
            self.assertNotIn("{{color:", stylesheet)
            self.assertNotIn("{{gradient:", stylesheet)


if __name__ == "__main__":
    unittest.main()
