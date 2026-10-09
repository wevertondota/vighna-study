"""Contrato da Etapa 3E-B2g: detalhe do Banco de Erros no pós-resposta."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest
from _design_system_test_helpers import strip_cards_global_block_a

import tema
from ui.design import (
    ALL_TOKENS,
    COMPONENT_TOKEN_COUNT,
    SEMANTIC_TOKEN_COUNT,
    TokenKind,
    get_theme,
    token_spec,
)
from versao import VIGHNA_BUILD, VIGHNA_SCHEMA, VIGHNA_VERSION


ROOT = Path(__file__).resolve().parent
TEMA_SOURCE = (ROOT / "tema.py").read_text(encoding="utf-8")

EXPECTED_VALUES = {
    "claro": ("#EFF6FF", "#1E3A8A", "#BFDBFE"),
    "escuro": ("#172554", "#BFDBFE", "#1D4ED8"),
    "futurista": ("#172554", "#BFDBFE", "#1D4ED8"),
}
EXPECTED_NORMALIZED_HASHES = {
    "claro": "c8975fa69de340d0fd51e2d5a1b4d91477286cadfddd1a9fe1c77e71a51ed8e3",
    "escuro": "250d6f47d8fa10e4b6aee8e9692053693094f1d25e7c92a5b1c45da96eeb46c5",
    "futurista": "8567fdd28b7856892f4802492bcc820cbe229b34ed67f7b5b0dcf2bb932f58ee",
}
BASE_FILE_HASHES = {
    "banco.py": "c263a502f0761d1f9fb7f910b35474cbda18b529a5244978614cc27342b32c94",
    "versao.py": "49e9d1b5c82bc10c70bd79ca5f494961e3cae3553cd4b70af1565bca661f9ac2",
}
EDITOR_SOURCE_HASHES = {
    "ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_CLARO": "dc7a771a73331aa16b3140897813797325fd94f31faf71a443267999d3b90cef",
    "ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_ESCURO": "dc7a771a73331aa16b3140897813797325fd94f31faf71a443267999d3b90cef",
    "ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_FUTURISTA": "90c6e54daf096dd622f1333dbcdea6b1858dffc7e99e4eb8446b602db0c8de89",
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


def _selector_block(source: str, selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{.*?^\}}", source, re.DOTALL | re.MULTILINE)
    if match is None:
        raise AssertionError(f"Seletor não encontrado: {selector}")
    return match.group(0)


class ResolverFeedbackExplanationB2gTests(unittest.TestCase):
    def test_contract_adds_exactly_three_component_color_tokens(self) -> None:
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 1148)
        self.assertEqual(len(ALL_TOKENS), 1250)
        expected = {
            "feedback.queue_detail_surface",
            "feedback.queue_detail_text",
            "feedback.queue_detail_border",
        }
        actual = {token.path for token in ALL_TOKENS if token.path.startswith("feedback.queue_detail_")}
        self.assertEqual(actual, expected)
        for path in expected:
            self.assertIs(token_spec(path).kind, TokenKind.COLOR)

    def test_queue_detail_values_match_characterization_in_all_themes(self) -> None:
        paths = (
            "feedback.queue_detail_surface",
            "feedback.queue_detail_text",
            "feedback.queue_detail_border",
        )
        for theme_name, expected in EXPECTED_VALUES.items():
            actual = tuple(get_theme(theme_name).color(path).value for path in paths)
            self.assertEqual(actual, expected)
        self.assertEqual(
            tuple(get_theme("escuro").color(path).value for path in paths),
            tuple(get_theme("futurista").color(path).value for path in paths),
        )

    def test_scoped_selector_exists_only_in_clear_and_dark_source_layers(self) -> None:
        selector = "QDialog#questionSolverDialog QLabel#questionSessionSummaryDetail"
        clear = _constant_source("ESTILO_RESOLVEDOR_CLARO", "ESTILO_RESOLVEDOR_ESCURO")
        dark = _constant_source("ESTILO_RESOLVEDOR_ESCURO", "ESTILO_RESOLVEDOR_FUTURISTA")
        future = _constant_source("ESTILO_RESOLVEDOR_FUTURISTA", "ESTILO_TOPICO_DETALHES_CLARO")
        for source in (clear, dark):
            block = _selector_block(source, selector)
            self.assertIn("background-color: {{color:feedback.queue_detail_surface}};", block)
            self.assertIn("color: {{color:feedback.queue_detail_text}};", block)
            self.assertIn("border-color: {{color:feedback.queue_detail_border}};", block)
            self.assertNotIn("feedback.info_", block)
            self.assertNotIn("border-radius", block)
            self.assertNotIn("padding", block)
            self.assertNotIn("font-weight", block)
            properties = {
                line.strip().split(":", 1)[0]
                for line in block.splitlines()[1:-1]
                if ":" in line
            }
            self.assertEqual(properties, {"background-color", "color", "border-color"})
        self.assertNotIn(selector, future)
        self.assertEqual(TEMA_SOURCE.count("{{color:feedback.queue_detail_surface}}"), 2)
        self.assertEqual(TEMA_SOURCE.count("{{color:feedback.queue_detail_text}}"), 2)
        self.assertEqual(TEMA_SOURCE.count("{{color:feedback.queue_detail_border}}"), 2)

    def test_global_summary_detail_rules_remain_literal_and_unchanged(self) -> None:
        blocks = re.findall(
            r"(?m)^    QLabel#questionSessionSummaryDetail\s*\{.*?^    \}",
            TEMA_SOURCE,
            re.DOTALL,
        )
        self.assertEqual(len(blocks), 2)
        normalized = [re.sub(r"\s+", " ", block).strip().lower() for block in blocks]
        self.assertIn(
            "qlabel#questionsessionsummarydetail { background-color: #eff6ff; color: #1e3a8a; "
            "border: 1px solid #bfdbfe; border-radius: 7px; padding: 7px 9px; font-weight: 700; }",
            normalized,
        )
        self.assertIn(
            "qlabel#questionsessionsummarydetail { background-color: #172554; color: #bfdbfe; "
            "border: 1px solid #1d4ed8; border-radius: 7px; padding: 7px 9px; font-weight: 700; }",
            normalized,
        )

    def test_feedback_state_contracts_and_futuristic_neutral_override_remain_intact(self) -> None:
        for state, surface, border in (
            ("correta", "feedback.success_surface", "feedback.success_border"),
            ("errada", "feedback.danger_surface", "feedback.danger_border"),
        ):
            selector = f'QFrame#questionSolverFeedback[resultState="{state}"]'
            blocks = re.findall(
                rf"{re.escape(selector)}\s*\{{(.*?)^    \}}",
                TEMA_SOURCE,
                re.DOTALL | re.MULTILINE,
            )
            self.assertEqual(len(blocks), 2)
            for block in blocks:
                self.assertIn(f"{{{{color:{surface}}}}}", block)
                self.assertIn(f"{{{{color:{border}}}}}", block)
        future = _constant_source("ESTILO_RESOLVEDOR_FUTURISTA", "ESTILO_TOPICO_DETALHES_CLARO")
        neutral = _selector_block(future, "QDialog#questionSolverDialog QFrame#questionSolverFeedback")
        self.assertIn("{{color:answer.explanation_surface}}", neutral)
        self.assertIn("{{color:answer.explanation_border}}", neutral)
        self.assertIn("border-radius: 11px", neutral)

    def test_explanation_editor_source_is_byte_for_byte_unchanged(self) -> None:
        pairs = (
            ("ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_CLARO", "ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_ESCURO"),
            ("ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_ESCURO", "ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_FUTURISTA"),
            ("ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_FUTURISTA", "ESTILO_CALENDARIO_PREVISAO_CLARO"),
        )
        for name, next_name in pairs:
            digest = hashlib.sha256(_constant_source(name, next_name).encode("utf-8")).hexdigest()
            self.assertEqual(digest, EDITOR_SOURCE_HASHES[name])

    def test_protected_files_version_build_schema_and_database_are_unchanged(self) -> None:
        for relative, expected in BASE_FILE_HASHES.items():
            digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(digest, expected)
        self.assertEqual(VIGHNA_VERSION, "0.29.59")
        self.assertEqual(VIGHNA_BUILD, "statistics-my-evolution-tokens-v1")
        self.assertEqual(VIGHNA_SCHEMA, 25)

    def test_rendered_qss_has_expected_new_snapshots_and_no_unresolved_markers(self) -> None:
        for theme_name, expected in EXPECTED_NORMALIZED_HASHES.items():
            qss = getattr(tema, f"stylesheet_{theme_name}")()
            qss = strip_cards_global_block_a(tema, theme_name, qss)
            digest = hashlib.sha256(_canonical_qss(qss).encode("utf-8")).hexdigest()
            self.assertEqual(digest, expected)
            self.assertNotIn("{{color:", qss)
            self.assertNotIn("{{gradient:", qss)
        self.assertIn("return stylesheet_escuro() + render_qss", TEMA_SOURCE)


if __name__ == "__main__":
    unittest.main()
