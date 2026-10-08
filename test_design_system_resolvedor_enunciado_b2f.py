"""Contratos da Etapa 3E-B2f: card e texto do enunciado."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest
from unittest.mock import patch

import tema
from ui.design import (
    ALL_TOKENS,
    COMPONENT_TOKEN_COUNT,
    TokenKind,
    get_theme,
    token_spec,
)

ROOT = Path(__file__).resolve().parent

CARD = "QDialog#questionSolverDialog QFrame#questionSolverStatementCard"
TEXT = "QDialog#questionSolverDialog QLabel#questionSolverStatement"

BASELINE = {
    "claro": "41163c96428ebacd62c25f5038021f51532f1c8ec41253c26dfe4fbd83e93a8a",
    "escuro": "3b313cb0085c5f2d06fbb981f5b2660ba585d36e2595b4ab7ac8ad4bc19d7ec5",
    "futurista": "01450cc14995f4c252243555dfac88536d8a0961b99a6bc235cab5f43e99b9b4",
}

COLORS = {
    "claro": {
        "session.statement_surface": "#FFFFFF",
        "session.statement_border": "#DCE3EB",
        "session.statement_text": "#172033",
    },
    "escuro": {
        "session.statement_surface": "#182230",
        "session.statement_border": "#344154",
        "session.statement_text": "#F2F6FA",
    },
    "futurista": {
        "session.statement_surface": "#171F2B",
        "session.statement_border": "#3C4858",
        "session.statement_text": "#F2F6FA",
    },
}

GRADIENTS = {
    "claro": ((0.0, "#FFFFFF"), (1.0, "#FFFFFF")),
    "escuro": ((0.0, "#182230"), (1.0, "#182230")),
    "futurista": ((0.0, "#171F2B"), (1.0, "#141C27")),
}


def canonical(value: str) -> str:
    value = re.sub(
        r"#[0-9A-Fa-f]{3,8}\b",
        lambda m: m[0].upper(),
        value,
    )
    return re.sub(r"\s+", " ", value).strip()


def raw(name: str) -> str:
    with patch.object(tema, "render_qss", side_effect=lambda name, source: source):
        if name == "futurista":
            with patch.object(tema, "stylesheet_escuro", return_value=""):
                return tema.stylesheet_futurista()
        return getattr(tema, "stylesheet_" + name)()


def block(source: str, selector: str) -> str:
    # Marcadores do design system terminam em ``}}``; uma regex não gulosa
    # encerrava a regra no primeiro ``}`` do token, antes do ponto e vírgula.
    match = re.search(
        rf"{re.escape(selector)}\s*\{{(?P<body>(?:\{{\{{.*?\}}\}}|[^}}])*)\}}",
        source,
        re.S,
    )
    if match is None:
        raise AssertionError(f"Seletor não encontrado: {selector}")
    return match.group(0)


class StatementB2FTests(unittest.TestCase):
    def test_exact_four_new_tokens(self):
        expected = {
            "session.statement_surface",
            "session.statement_gradient",
            "session.statement_border",
            "session.statement_text",
        }
        actual = {
            token.path
            for token in ALL_TOKENS
            if token.path.startswith("session.statement_")
        }
        self.assertEqual(actual, expected)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 1004)
        self.assertEqual(len(ALL_TOKENS), 1106)

        self.assertIs(
            token_spec("session.statement_gradient").kind,
            TokenKind.GRADIENT,
        )
        for name in expected - {"session.statement_gradient"}:
            self.assertIs(token_spec(name).kind, TokenKind.COLOR)

    def test_color_values(self):
        for theme_name, expected in COLORS.items():
            theme = get_theme(theme_name)
            for token, value in expected.items():
                with self.subTest(theme=theme_name, token=token):
                    self.assertEqual(theme.color(token).value, value)

    def test_gradient_values_direction_and_stops(self):
        for theme_name, expected in GRADIENTS.items():
            spec = get_theme(theme_name).gradient("session.statement_gradient")
            self.assertEqual(
                (
                    spec.direction.x1,
                    spec.direction.y1,
                    spec.direction.x2,
                    spec.direction.y2,
                ),
                (0.0, 0.0, 1.0, 1.0),
            )
            self.assertEqual(
                tuple((stop.position, stop.color.value) for stop in spec.stops),
                expected,
            )

    def test_claro_consumers(self):
        source = raw("claro")
        card = block(source, CARD)
        text = block(source, TEXT)

        self.assertIn(
            "background-color: {{color:session.statement_surface}};",
            card,
        )
        self.assertIn(
            "border: 1px solid {{color:session.statement_border}};",
            card,
        )
        self.assertIn("border-radius: 12px;", card)
        self.assertNotIn("{{gradient:session.statement_gradient}}", card)

        self.assertIn("color: {{color:session.statement_text}};", text)
        self.assertIn("font-size: 10.8pt;", text)

    def test_escuro_consumers(self):
        source = raw("escuro")
        card = block(source, CARD)
        text = block(source, TEXT)

        self.assertIn(
            "background-color: {{color:session.statement_surface}};",
            card,
        )
        self.assertIn(
            "border: 1px solid {{color:session.statement_border}};",
            card,
        )
        self.assertIn("border-radius: 12px;", card)
        self.assertNotIn("{{gradient:session.statement_gradient}}", card)

        self.assertIn("color: {{color:session.statement_text}};", text)
        self.assertIn("font-size: 10.8pt;", text)

    def test_futurista_consumers(self):
        source = raw("futurista")
        card = block(source, CARD)
        text = block(source, TEXT)

        self.assertIn(
            "background: {{gradient:session.statement_gradient}};",
            card,
        )
        self.assertNotIn(
            "background-color: {{color:session.statement_surface}};",
            card,
        )
        self.assertIn(
            "border: 1px solid {{color:session.statement_border}};",
            card,
        )
        self.assertIn("border-radius: 13px;", card)

        self.assertIn("color: {{color:session.statement_text}};", text)
        self.assertIn("font-size: 10.9pt;", text)

    def test_no_new_visual_states(self):
        for name in ("claro", "escuro", "futurista"):
            source = raw(name)
            for suffix in (":hover", ":focus", ":disabled"):
                self.assertNotIn(CARD + suffix, source)
                self.assertNotIn(TEXT + suffix, source)

    def test_identification_contracts_remain_present(self):
        source = Path(ROOT / "tema.py").read_text(encoding="utf-8")
        for marker in (
            "{{color:session.discipline_text}}",
            "{{color:session.meta_text}}",
            "{{color:session.question_index_text}}",
        ):
            self.assertIn(marker, source)

    def test_main_py_remains_b2c_byte_identical(self):
        main = ROOT / "main.py"
        self.assertTrue(main.exists())
        digest = hashlib.sha256(main.read_bytes()).hexdigest()
        self.assertEqual(
            digest,
            "0e8ec1248b38d4bac3ffce756f3a35dabb0ba1a2c0f757996b53f6a2f4b7a02b",
        )

    def test_resolved_qss_hashes_remain_identical(self):
        for theme_name, expected in BASELINE.items():
            stylesheet = getattr(tema, "stylesheet_" + theme_name)()
            digest = hashlib.sha256(
                canonical(stylesheet).encode("utf-8")
            ).hexdigest()
            self.assertEqual(digest, expected)
            self.assertNotIn("{{color:", stylesheet)
            self.assertNotIn("{{gradient:", stylesheet)


if __name__ == "__main__":
    unittest.main()
