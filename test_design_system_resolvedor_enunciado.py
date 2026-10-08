"""Contrato da Etapa 3E-B2f: card e texto principal do enunciado."""

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


ROOT = Path(__file__).resolve().parent
TEMA_SOURCE = (ROOT / "tema.py").read_text(encoding="utf-8")

EXPECTED_COLORS = {
    "claro": ("#FFFFFF", "#DCE3EB", "#172033"),
    "escuro": ("#182230", "#344154", "#F2F6FA"),
    "futurista": ("#171F2B", "#3C4858", "#F2F6FA"),
}
EXPECTED_GRADIENTS = {
    "claro": ((0.0, "#FFFFFF"), (1.0, "#FFFFFF")),
    "escuro": ((0.0, "#182230"), (1.0, "#182230")),
    "futurista": ((0.0, "#171F2B"), (1.0, "#141C27")),
}
EXPECTED_NORMALIZED_HASHES = {
    "claro": "71c6c022b5fb4a3798f5bb9f837fc55fc9fa3bf4d558832688dd7fb25d8c7cdb",
    "escuro": "25dd9d735b8aa542020a05bbc3318cc91aba79f0b2f89995cea0a272d8bc1056",
    "futurista": "d4176c63eae7f8b0349fce4eb50ada9b5186473a8d0aba884ad7aa4e41f5b448",
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



def strip_navigation_search_layer(theme_name: str, qss: str) -> str:
    qss = strip_cards_global_block_a(tema, theme_name, qss)
    """Remove apenas a camada aditiva da Busca global para snapshots históricos."""
    # Remove primeiro a camada posterior de Retornos ao Dashboard, quando presente.
    if hasattr(tema, "ESTILO_NAVEGACAO_RETORNOS_DASHBOARD"):
        if theme_name == "futurista":
            final_back = tema.render_qss("futurista", tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
            inherited_back = tema.render_qss("escuro", tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
            if qss.endswith(final_back):
                qss = qss[:-len(final_back)]
            if inherited_back in qss:
                qss = qss.replace(inherited_back, "", 1)
        else:
            back_layer = tema.render_qss(theme_name, tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
            if qss.endswith(back_layer):
                qss = qss[:-len(back_layer)]
            else:
                qss = qss.replace(back_layer, "", 1)
    if theme_name == "futurista":
        final = tema.render_qss("futurista", tema.ESTILO_NAVEGACAO_BUSCA_GLOBAL)
        inherited = tema.render_qss("escuro", tema.ESTILO_NAVEGACAO_BUSCA_GLOBAL)
        if qss.endswith(final):
            qss = qss[:-len(final)]
        if inherited in qss:
            qss = qss.replace(inherited, "", 1)
        return qss
    layer = tema.render_qss(theme_name, tema.ESTILO_NAVEGACAO_BUSCA_GLOBAL)
    if qss.endswith(layer):
        return qss[:-len(layer)]
    return qss.replace(layer, "", 1)

class ResolverStatementDesignSystemTests(unittest.TestCase):
    def test_contract_adds_exactly_four_component_tokens(self) -> None:
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 1004)
        self.assertEqual(len(ALL_TOKENS), 1106)
        expected = {
            "session.statement_surface": TokenKind.COLOR,
            "session.statement_border": TokenKind.COLOR,
            "session.statement_text": TokenKind.COLOR,
            "session.statement_gradient": TokenKind.GRADIENT,
        }
        for path, kind in expected.items():
            with self.subTest(path=path):
                self.assertEqual(token_spec(path).kind, kind)

    def test_statement_colors_match_characterization(self) -> None:
        for theme_name, values in EXPECTED_COLORS.items():
            theme = get_theme(theme_name)
            actual = tuple(
                theme.color(path).value
                for path in (
                    "session.statement_surface",
                    "session.statement_border",
                    "session.statement_text",
                )
            )
            self.assertEqual(actual, values)

    def test_statement_gradient_preserves_direction_and_stops(self) -> None:
        for theme_name, expected in EXPECTED_GRADIENTS.items():
            spec = get_theme(theme_name).gradient("session.statement_gradient")
            self.assertEqual(
                (spec.direction.x1, spec.direction.y1, spec.direction.x2, spec.direction.y2),
                (0.0, 0.0, 1.0, 1.0),
            )
            self.assertEqual(
                tuple((stop.position, stop.color.value) for stop in spec.stops),
                expected,
            )

    def test_only_effective_statement_consumers_are_tokenized(self) -> None:
        clear = _constant_source("ESTILO_RESOLVEDOR_CLARO", "ESTILO_RESOLVEDOR_ESCURO")
        dark = _constant_source("ESTILO_RESOLVEDOR_ESCURO", "ESTILO_RESOLVEDOR_FUTURISTA")
        future = _constant_source("ESTILO_RESOLVEDOR_FUTURISTA", "ESTILO_TOPICO_DETALHES_CLARO")
        card = "QDialog#questionSolverDialog QFrame#questionSolverStatementCard"
        statement = "QDialog#questionSolverDialog QLabel#questionSolverStatement"

        for source in (clear, dark):
            card_block = _selector_block(source, card)
            statement_block = _selector_block(source, statement)
            self.assertIn("background-color: {{color:session.statement_surface}};", card_block)
            self.assertIn("border: 1px solid {{color:session.statement_border}};", card_block)
            self.assertIn("color: {{color:session.statement_text}};", statement_block)

        future_card = _selector_block(future, card)
        future_statement = _selector_block(future, statement)
        self.assertIn("background: {{gradient:session.statement_gradient}};", future_card)
        self.assertIn("border: 1px solid {{color:session.statement_border}};", future_card)
        self.assertIn("color: {{color:session.statement_text}};", future_statement)

        self.assertEqual(TEMA_SOURCE.count("{{color:session.statement_surface}}"), 2)
        self.assertEqual(TEMA_SOURCE.count("{{gradient:session.statement_gradient}}"), 1)
        self.assertEqual(TEMA_SOURCE.count("{{color:session.statement_border}}"), 3)
        self.assertEqual(TEMA_SOURCE.count("{{color:session.statement_text}}"), 3)

    def test_geometry_and_typography_remain_literal(self) -> None:
        clear = _constant_source("ESTILO_RESOLVEDOR_CLARO", "ESTILO_RESOLVEDOR_ESCURO")
        dark = _constant_source("ESTILO_RESOLVEDOR_ESCURO", "ESTILO_RESOLVEDOR_FUTURISTA")
        future = _constant_source("ESTILO_RESOLVEDOR_FUTURISTA", "ESTILO_TOPICO_DETALHES_CLARO")
        card = "QDialog#questionSolverDialog QFrame#questionSolverStatementCard"
        statement = "QDialog#questionSolverDialog QLabel#questionSolverStatement"
        for source, radius, size in (
            (clear, "12px", "10.8pt"),
            (dark, "12px", "10.8pt"),
            (future, "13px", "10.9pt"),
        ):
            self.assertIn(f"border-radius: {radius};", _selector_block(source, card))
            self.assertIn(f"font-size: {size};", _selector_block(source, statement))

    def test_rendered_stylesheets_preserve_characterized_visual_contract(self) -> None:
        for theme_name, expected in EXPECTED_NORMALIZED_HASHES.items():
            qss = getattr(tema, f"stylesheet_{theme_name}")()
            baseline_qss = strip_navigation_search_layer(theme_name, qss)
            digest = hashlib.sha256(_canonical_qss(baseline_qss).encode("utf-8")).hexdigest()
            self.assertEqual(digest, expected)
            self.assertNotIn("{{color:", qss)
            self.assertNotIn("{{gradient:", qss)
        self.assertIn("return stylesheet_escuro() + render_qss", TEMA_SOURCE)


if __name__ == "__main__":
    unittest.main()
