from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sqlite3
import unittest

from _design_system_test_helpers import strip_cards_global_block_c_source
from ui.design import (
    ALL_TOKENS,
    COMPONENT_TOKEN_COUNT,
    SEMANTIC_TOKEN_COUNT,
    TokenKind,
    get_theme,
    render_qss,
    token_spec,
)
from versao import VIGHNA_BUILD, VIGHNA_SCHEMA, VIGHNA_VERSION

ROOT = Path(__file__).resolve().parent
TEMA_PATH = ROOT / "tema.py"
TEMA_SOURCE = TEMA_PATH.read_text(encoding="utf-8")

COLOR_TOKENS = (
    "card.study_action_border",
    "card.study_action_review_border",
    "card.study_action_adaptive_border",
)
GRADIENT_TOKENS = (
    "card.study_action_surface_gradient",
    "card.study_action_adaptive_surface_gradient",
)

EXPECTED_COLORS = {
    "claro": ("#CDD8E6", "#D1DEED", "#D9D2F5"),
    "escuro": ("#354A64", "#34516D", "#5B51A6"),
    "futurista": ("#2C5069", "#3CCFF0", "#736BDF"),
}
EXPECTED_GRADIENTS = {
    "claro": (
        ((0.0, "#FBFCFE"), (1.0, "#FBFCFE")),
        ((0.0, "#FAF9FF"), (1.0, "#FAF9FF")),
    ),
    "escuro": (
        ((0.0, "#152232"), (1.0, "#152232")),
        ((0.0, "#152232"), (1.0, "#152232")),
    ),
    "futurista": (
        ((0.0, "#EB0C1F2F"), (1.0, "#EB091624")),
        ((0.0, "#EB0C1F2F"), (1.0, "#EB091624")),
    ),
}

BASE_TEMA_HASH = "624acad51b5723ce368c7c6109b9e6f32b23fdf2555117b91daa4fe83da58d69"
PROTECTED_HASHES = {
    "main.py": "0e8ec1248b38d4bac3ffce756f3a35dabb0ba1a2c0f757996b53f6a2f4b7a02b",
    "navegacao.py": "2cb3439a580cf867af9870750a82e06777718961dd84819e0705a96838c8b862",
    "estudos.db": "7152284f813f16c42bb4586d4d929b53d5d97efe8cf6e290ff9b80faf11b9c26",
    "versao.py": "ae19e3d250f581849a09245b27469b2cb1b1aef48d862338e888679d58b20d67",
    "foco.py": "8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed",
    "jogos.py": "498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286",
    "checkpoint.py": "947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38",
}


def layer_template() -> str:
    match = re.search(
        r'ESTILO_CARDS_GLOBAIS_BLOCO_B = r"""\n(?P<body>.*?)\n"""\n\n# ============================================================\n# Design System — Cards globais — Bloco C',
        TEMA_SOURCE,
        re.S,
    )
    if not match:
        raise AssertionError("camada Cards globais B não encontrada")
    return match.group("body") + "\n"


def rollback_tema(source: str) -> str:
    source = strip_cards_global_block_c_source(source)
    source = re.sub(
        r'# ============================================================\n'
        r'# Design System — Cards globais — Bloco B\n'
        r'# Shell compartilhado studyActionCard\. Somente superfície e borda;\n'
        r'# textos, geometria e comportamento permanecem na cascata histórica\.\n'
        r'# ============================================================\n'
        r'ESTILO_CARDS_GLOBAIS_BLOCO_B = r"""\n.*?\n"""\n\n',
        "",
        source,
        count=1,
        flags=re.S,
    )
    for theme_name in ("claro", "escuro", "futurista"):
        source = source.replace(
            f' + render_qss("{theme_name}", ESTILO_CARDS_GLOBAIS_BLOCO_B)',
            "",
            1,
        )
    return source


class GlobalCardsBlockBTests(unittest.TestCase):
    def test_contrato_e_orcamento_final(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 1004)
        self.assertEqual(len(ALL_TOKENS), 1106)
        self.assertEqual(sum(t.kind is TokenKind.COLOR for t in ALL_TOKENS), 1030)
        self.assertEqual(sum(t.kind is TokenKind.GRADIENT for t in ALL_TOKENS), 76)
        for path in COLOR_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.COLOR)
        for path in GRADIENT_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.GRADIENT)

    def test_valores_historicos_de_cor_preservados_nos_tres_temas(self):
        for theme_name, expected_values in EXPECTED_COLORS.items():
            theme = get_theme(theme_name)
            for path, expected in zip(COLOR_TOKENS, expected_values, strict=True):
                with self.subTest(theme=theme_name, token=path):
                    self.assertEqual(theme.color(path).value, expected)

    def test_gradientes_preservam_superficie_normal_e_adaptativa(self):
        for theme_name, expected_gradients in EXPECTED_GRADIENTS.items():
            theme = get_theme(theme_name)
            for path, expected in zip(GRADIENT_TOKENS, expected_gradients, strict=True):
                gradient = theme.gradient(path)
                with self.subTest(theme=theme_name, token=path):
                    self.assertEqual(
                        (gradient.direction.x1, gradient.direction.y1, gradient.direction.x2, gradient.direction.y2),
                        (0.0, 0.0, 1.0, 1.0),
                    )
                    self.assertEqual(
                        tuple((stop.position, stop.color.value) for stop in gradient.stops),
                        expected,
                    )

    def test_camada_escopa_somente_shell_e_estados_study_action(self):
        layer = layer_template()
        required = (
            'QFrame#studyActionCard {',
            'QFrame#studyActionCard[actionRole="review"] {',
            'QFrame#studyActionCard[actionRole="adaptive"] {',
        )
        for selector in required:
            self.assertEqual(layer.count(selector), 1, selector)
        for forbidden in (
            "studyActionTitle", "studyActionDescription", "studyColumnTitle",
            "studyReviewSourceBadge", "QPushButton", "QLabel",
        ):
            self.assertNotIn(forbidden, layer)

    def test_camada_consome_exatamente_cinco_tokens_sem_cor_fisica(self):
        layer = layer_template()
        for path in COLOR_TOKENS:
            self.assertEqual(layer.count(f"{{{{color:{path}}}}}"), 1, path)
        for path in GRADIENT_TOKENS:
            self.assertEqual(layer.count(f"{{{{gradient:{path}}}}}"), 1, path)
        self.assertNotRegex(layer, r"#[0-9A-Fa-f]{6,8}")
        self.assertNotIn("rgba(", layer)

    def test_nova_camada_nao_mexe_em_geometria_tipografia_ou_comportamento(self):
        layer = layer_template()
        for forbidden in (
            "border-radius", "padding", "margin", "font-size", "font-weight",
            "min-height", "max-height", "setProperty", "clicked", "connect",
        ):
            self.assertNotIn(forbidden, layer)

    def test_dashboard_conserva_override_mais_especifico(self):
        self.assertIn(
            'QWidget#dashboardRoot QFrame#studyNowPanel QFrame#studyActionCard[actionRole="review"] {',
            TEMA_SOURCE,
        )
        layer = layer_template()
        self.assertNotIn("dashboardRoot", layer)
        self.assertNotIn("studyNowPanel", layer)
        self.assertIn('QFrame#studyActionCard[actionRole="review"] {', layer)

    def test_renderizacao_resolve_tokens_em_todos_os_temas(self):
        template = layer_template()
        for theme_name in ("claro", "escuro", "futurista"):
            rendered = render_qss(theme_name, template)
            self.assertNotIn("{{color:", rendered)
            self.assertNotIn("{{gradient:", rendered)
            self.assertIn("QFrame#studyActionCard", rendered)
            for value in EXPECTED_COLORS[theme_name]:
                self.assertIn(value, rendered)

    def test_composicao_final_fica_depois_do_bloco_a_em_todos_os_temas(self):
        for theme_name in ("claro", "escuro", "futurista"):
            a_marker = f'render_qss("{theme_name}", ESTILO_CARDS_GLOBAIS_BLOCO_A)'
            b_marker = f'render_qss("{theme_name}", ESTILO_CARDS_GLOBAIS_BLOCO_B)'
            self.assertEqual(TEMA_SOURCE.count(b_marker), 1)
            self.assertIn(a_marker, TEMA_SOURCE)
            self.assertGreater(TEMA_SOURCE.index(b_marker), TEMA_SOURCE.index(a_marker))

    def test_rollback_e_arquivos_protegidos_banco_versao(self):
        restored = rollback_tema(TEMA_SOURCE)
        self.assertEqual(hashlib.sha256(restored.encode("utf-8")).hexdigest(), BASE_TEMA_HASH)
        for relative, expected in PROTECTED_HASHES.items():
            digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(digest, expected, relative)
        self.assertEqual(VIGHNA_VERSION, "0.29.59")
        self.assertEqual(VIGHNA_BUILD, "questions-center-editor-viewer-futuristic-text-v1")
        self.assertEqual(VIGHNA_SCHEMA, 25)
        con = sqlite3.connect(ROOT / "estudos.db")
        try:
            self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(), [])
        finally:
            con.close()


if __name__ == "__main__":
    unittest.main()
