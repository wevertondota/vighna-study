"""Caracterização da Etapa 3E-A2: ações e feedback do Resolvedor."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest

import tema
from ui.design import ALL_TOKENS, COMPONENT_TOKEN_COUNT, get_theme


ROOT = Path(__file__).resolve().parent
TEMA_SOURCE = (ROOT / "tema.py").read_text(encoding="utf-8")

EXPECTED_STYLESHEET_BASELINE = {
    "claro": "139709f8c57e00f16848668f9226703c7f8ff391dd9aea2bba8b2eae20ac2c5f",
    "escuro": "ebbc21363d0035058301d060eb099fb2d33b992e8537c20f9bf1e77f8a2b4f3e",
    "futurista": "0e588bb372946b4a6f61ad406c817fd155cac8c3c4286e9f93b7a09d06dc8622",
}

EXPECTED_COLORS = {
    "claro": {
        "answer.edit_action_surface": "#FFFFFF",
        "answer.edit_action_hover_surface": "#EEF2FF",
        "answer.edit_action_hover_text": "#4338CA",
        "answer.edit_action_hover_border": "#A5B4FC",
        "answer.save_action_surface": "#4F46E5",
        "answer.save_action_text": "#FFFFFF",
        "answer.save_action_border": "#4338CA",
        "answer.cancel_action_surface": "#FFFFFF",
        "answer.primary_action_border": "#7885F0",
        "answer.primary_action_hover_border": "#98A2F7",
        "feedback.success_surface": "#F0FDF4",
        "feedback.success_border": "#86EFAC",
        "feedback.danger_surface": "#FEF2F2",
        "feedback.danger_border": "#FCA5A5",
        "text.on_feedback": "#111827",
    },
    "escuro": {
        "answer.edit_action_surface": "#182235",
        "answer.edit_action_hover_surface": "#273449",
        "answer.edit_action_hover_text": "#FFFFFF",
        "answer.edit_action_hover_border": "#8B95FF",
        "answer.save_action_surface": "#6366F1",
        "answer.save_action_text": "#FFFFFF",
        "answer.save_action_border": "#818CF8",
        "answer.cancel_action_surface": "#1F2937",
        "answer.primary_action_border": "#7885F0",
        "answer.primary_action_hover_border": "#A2AAFF",
        "feedback.success_surface": "#163523",
        "feedback.success_border": "#22C55E",
        "feedback.danger_surface": "#3F1218",
        "feedback.danger_border": "#EF4444",
        "text.on_feedback": "#F8FAFC",
    },
    "futurista": {
        "answer.edit_action_surface": "#0D1D2D",
        "answer.edit_action_hover_surface": "#15324A",
        "answer.edit_action_hover_text": "#F2FBFF",
        "answer.edit_action_hover_border": "#4BC9F2",
        "answer.save_action_surface": "#19527A",
        "answer.save_action_text": "#F1FAFF",
        "answer.save_action_border": "#4BC9F2",
        "answer.cancel_action_surface": "#0D1D2D",
        "answer.primary_action_border": "#7C83FF",
        "answer.primary_action_hover_border": "#B1B7FF",
        "feedback.success_surface": "#171F2B",
        "feedback.success_border": "#3A4656",
        "feedback.danger_surface": "#171F2B",
        "feedback.danger_border": "#3A4656",
        "text.on_feedback": "#F8FAFC",
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


def _selector_blocks(selector: str) -> list[str]:
    return re.findall(rf"{re.escape(selector)}\s*\{{.*?\}}", TEMA_SOURCE, re.DOTALL)


class ResolverActionsFeedbackDesignSystemTests(unittest.TestCase):
    def test_contract_growth_stays_inside_stage_budget(self) -> None:
        self.assertEqual(COMPONENT_TOKEN_COUNT, 172)
        self.assertEqual(len(ALL_TOKENS), 274)
        self.assertEqual(
            sum(token.path.startswith("answer.") for token in ALL_TOKENS),
            60,
        )

    def test_action_and_feedback_tokens_reproduce_characterized_cascade(self) -> None:
        for theme_name, expected in EXPECTED_COLORS.items():
            theme = get_theme(theme_name)
            for token, value in expected.items():
                with self.subTest(theme=theme_name, token=token):
                    self.assertEqual(theme.color(token).value, value)

    def test_primary_gradients_preserve_direction_positions_colors_and_alpha(self) -> None:
        expected = {
            "claro": (
                ((0, "#4B50DF"), (1, "#586DE3")),
                ((0, "#595EE8"), (1, "#6579EC")),
            ),
            "escuro": (
                ((0, "#4B50DF"), (1, "#586DE3")),
                ((0, "#595EE8"), (1, "#6579EC")),
            ),
            "futurista": (
                ((0, "#4447E8"), (0.52, "#4347E1"), (1, "#3C42D2")),
                ((0, "#5355F2"), (0.52, "#4F54EB"), (1, "#464DDE")),
            ),
        }
        for theme_name, variants in expected.items():
            theme = get_theme(theme_name)
            for token, stops in zip(
                ("gradient.action_primary", "gradient.action_primary_hover"),
                variants,
            ):
                with self.subTest(theme=theme_name, token=token):
                    spec = theme.gradient(token)
                    self.assertEqual(
                        (spec.direction.x1, spec.direction.y1, spec.direction.x2, spec.direction.y2),
                        (0, 0, 1, 0),
                    )
                    self.assertEqual(
                        tuple((stop.position, stop.color.value) for stop in spec.stops),
                        stops,
                    )
                    self.assertTrue(all(len(stop.color.value) == 7 for stop in spec.stops))

    def test_editor_actions_have_only_the_effective_legacy_states(self) -> None:
        editor = _constant_source(
            "ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_CLARO",
            "ESTILO_CALENDARIO_PREVISAO_CLARO",
        )
        self.assertEqual(editor.count("questionSolverExplanationEditButton:hover"), 3)
        for object_name in (
            "questionSolverExplanationEditButton",
            "questionSolverExplanationSaveButton",
            "questionSolverExplanationCancelButton",
        ):
            self.assertNotIn(f"{object_name}:pressed", editor)
            self.assertNotIn(f"{object_name}:disabled", editor)
        self.assertNotIn("questionSolverExplanationSaveButton:hover", editor)
        self.assertNotIn("questionSolverExplanationCancelButton:hover", editor)

    def test_confirm_and_next_share_the_same_primary_button_cascade(self) -> None:
        for constant, next_constant in (
            ("ESTILO_RESOLVEDOR_CLARO", "ESTILO_RESOLVEDOR_ESCURO"),
            ("ESTILO_RESOLVEDOR_ESCURO", "ESTILO_RESOLVEDOR_FUTURISTA"),
            ("ESTILO_RESOLVEDOR_FUTURISTA", "ESTILO_TOPICO_DETALHES_CLARO"),
        ):
            source = _constant_source(constant, next_constant)
            self.assertIn("{{gradient:gradient.action_primary}}", source)
            self.assertIn("{{gradient:gradient.action_primary_hover}}", source)
            self.assertIn("{{color:text.on_action}}", source)
            self.assertNotIn("QPushButton#primaryButton:pressed", source)
            self.assertNotIn("QPushButton#primaryButton:disabled", source)

    def test_feedback_uses_semantic_tokens_without_crossing_answer_boundary(self) -> None:
        for marker in (
            "{{color:feedback.success_surface}}",
            "{{color:feedback.success_border}}",
            "{{color:feedback.danger_surface}}",
            "{{color:feedback.danger_border}}",
            "{{color:text.on_feedback}}",
        ):
            self.assertIn(marker, TEMA_SOURCE)
        self.assertNotEqual(
            get_theme("claro").color("feedback.success_surface"),
            get_theme("claro").color("answer.correct_surface"),
        )
        self.assertNotEqual(
            get_theme("futurista").color("feedback.danger_border"),
            get_theme("futurista").color("answer.incorrect_border"),
        )

    def test_futuristic_feedback_preserves_later_more_specific_neutral_override(self) -> None:
        inherited_state = TEMA_SOURCE.index(
            'QFrame#questionSolverFeedback[resultState="correta"]'
        )
        futuristic_base = TEMA_SOURCE.index(
            "QDialog#questionSolverDialog QFrame#questionSolverFeedback"
        )
        self.assertLess(futuristic_base, inherited_state)
        # Na composição em runtime, todo stylesheet Escuro vem antes do bloco
        # Futurista; o seletor Futurista ainda tem um ID adicional.
        self.assertIn("return stylesheet_escuro() + render_qss", TEMA_SOURCE)
        self.assertEqual(
            get_theme("futurista").color("feedback.success_surface").value,
            get_theme("futurista").color("answer.explanation_surface").value,
        )
        self.assertEqual(
            get_theme("futurista").color("feedback.danger_border").value,
            get_theme("futurista").color("answer.explanation_border").value,
        )

    def test_all_69_scoped_visual_hex_occurrences_were_removed(self) -> None:
        editor = _constant_source(
            "ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_CLARO",
            "ESTILO_CALENDARIO_PREVISAO_CLARO",
        )
        self.assertNotRegex(editor, r"#[0-9A-Fa-f]{6,8}")
        for selector, expected_count in (
            ("QDialog#questionSolverDialog QPushButton#primaryButton", 3),
            ("QDialog#questionSolverDialog QPushButton#primaryButton:hover", 3),
            ('QFrame#questionSolverFeedback[resultState="correta"]', 2),
            ('QFrame#questionSolverFeedback[resultState="errada"]', 2),
            ("QLabel#questionSolverFeedbackTitle", 2),
        ):
            blocks = _selector_blocks(selector)
            self.assertEqual(len(blocks), expected_count)
            self.assertFalse(any(re.search(r"#[0-9A-Fa-f]{6,8}", block) for block in blocks))
        for stylesheet in (
            tema.stylesheet_claro(),
            tema.stylesheet_escuro(),
            tema.stylesheet_futurista(),
        ):
            self.assertNotIn("{{color:", stylesheet)
            self.assertNotIn("{{gradient:", stylesheet)

    def test_complete_stylesheet_hashes_remain_identical(self) -> None:
        for theme_name in EXPECTED_STYLESHEET_BASELINE:
            factory = getattr(tema, f"stylesheet_{theme_name}")
            digest = hashlib.sha256(_canonical_qss(factory()).encode("utf-8")).hexdigest()
            self.assertEqual(digest, EXPECTED_STYLESHEET_BASELINE[theme_name])


if __name__ == "__main__":
    unittest.main()
