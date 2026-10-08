from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sqlite3
import unittest

from _design_system_test_helpers import strip_cards_global_block_b_source
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
    "card.dialog_surface",
    "card.dialog_border",
    "card.metric_surface",
    "card.metric_border",
    "card.mini_stat_surface",
    "card.mini_stat_border",
    "card.metric_label_text",
    "card.metric_value_text",
)

EXPECTED = {
    "claro": (
        "#FFFFFF",
        "#DBE3ED",
        "#FFFFFF",
        "#E2E8F0",
        "#FBFDFF",
        "#D9E5F0",
        "#64748B",
        "#111827",
    ),
    "escuro": (
        "#182235",
        "#334155",
        "#182235",
        "#334155",
        "#182235",
        "#334155",
        "#94A3B8",
        "#F8FAFC",
    ),
    "futurista": (
        "#182235",
        "#334155",
        "#182235",
        "#334155",
        "#182235",
        "#334155",
        "#94A3B8",
        "#F8FAFC",
    ),
}

BASE_TEMA_HASH = "4435545f9f7304d521581b4d3c14c167d853cb477962d810f56e0af268589fbe"
PROTECTED_HASHES = {
    "main.py": "bdb0815e71387bd87d40498bf535ef839d19a1a9086d55e0582ea50946713b45",
    "navegacao.py": "2cb3439a580cf867af9870750a82e06777718961dd84819e0705a96838c8b862",
    "estudos.db": "034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef",
    "versao.py": "c201d237e622dd2269838e54914458fd775c7ec1a91f07b518775ee833caa439",
    "foco.py": "8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed",
    "jogos.py": "498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286",
    "checkpoint.py": "947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38",
}


def layer_template() -> str:
    match = re.search(
        r'ESTILO_CARDS_GLOBAIS_BLOCO_A = r"""\n(?P<body>.*?)\n"""\n\n# ============================================================\n# Design System — Cards globais — Bloco B',
        TEMA_SOURCE,
        re.S,
    )
    if not match:
        raise AssertionError("camada Cards globais A não encontrada")
    return match.group("body") + "\n"


def rollback_tema(source: str) -> str:
    source = strip_cards_global_block_b_source(source)
    source = re.sub(
        r'# ============================================================\n'
        r'# Design System — Cards globais — Bloco A\n'
        r'# Superfícies básicas e métricas\. Camada cromática aditiva,\n'
        r'# escopada aos shells genéricos e aos textos internos dos cards\.\n'
        r'# ============================================================\n'
        r'ESTILO_CARDS_GLOBAIS_BLOCO_A = r"""\n.*?\n"""\n\n',
        "",
        source,
        count=1,
        flags=re.S,
    )
    for theme_name in ("claro", "escuro", "futurista"):
        source = source.replace(
            f' + render_qss("{theme_name}", ESTILO_CARDS_GLOBAIS_BLOCO_A)',
            "",
            1,
        )
    return source


class GlobalCardsBlockATests(unittest.TestCase):
    def test_contrato_e_orcamento_final(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 928)
        self.assertEqual(len(ALL_TOKENS), 1030)
        for path in COLOR_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.COLOR)

    def test_valores_historicos_preservados_nos_tres_temas(self):
        for theme_name, expected_values in EXPECTED.items():
            theme = get_theme(theme_name)
            for path, expected in zip(COLOR_TOKENS, expected_values, strict=True):
                with self.subTest(theme=theme_name, token=path):
                    self.assertEqual(theme.color(path).value, expected)

    def test_futurista_preserva_paridade_deliberada_com_escuro(self):
        dark = get_theme("escuro")
        futuristic = get_theme("futurista")
        for path in COLOR_TOKENS:
            with self.subTest(token=path):
                self.assertEqual(futuristic.color(path).value, dark.color(path).value)

    def test_camada_escopa_shells_e_textos_internos_sem_vazamento_global(self):
        layer = layer_template()
        required_selectors = (
            "QFrame#dialogCard {",
            "QFrame#metricCard {",
            "QFrame#metricCard QLabel#metricLabel {",
            "QFrame#metricCard QLabel#metricValue {",
            "QFrame#miniStat {",
            "QFrame#miniStat QLabel#miniStatLabel {",
            "QFrame#miniStat QLabel#miniStatValue {",
        )
        for selector in required_selectors:
            self.assertEqual(layer.count(selector), 1, selector)
        self.assertNotRegex(layer, r'(?m)^QLabel#metricLabel\s*\{')
        self.assertNotRegex(layer, r'(?m)^QLabel#miniStatLabel\s*\{')
        self.assertNotRegex(layer, r'(?m)^QLabel#miniStatValue\s*\{')

    def test_camada_consome_os_oito_tokens_e_nao_tem_cor_fisica(self):
        layer = layer_template()
        for path in COLOR_TOKENS:
            expected_count = 2 if path in ("card.metric_label_text", "card.metric_value_text") else 1
            self.assertEqual(layer.count(f"{{{{color:{path}}}}}"), expected_count, path)
        self.assertNotRegex(layer, r"#[0-9A-Fa-f]{6,8}")
        self.assertNotIn("{{gradient:", layer)

    def test_renderizacao_resolve_todos_os_tokens(self):
        template = layer_template()
        for theme_name in ("claro", "escuro", "futurista"):
            rendered = render_qss(theme_name, template)
            self.assertNotIn("{{color:", rendered)
            self.assertNotIn("{{gradient:", rendered)
            for value in set(EXPECTED[theme_name]):
                self.assertIn(value, rendered)

    def test_geometria_tipografia_e_regras_historicas_ficam_fora_da_nova_camada(self):
        layer = layer_template()
        for forbidden in ("border-radius", "padding", "margin", "font-size", "font-weight", "min-height", "max-height"):
            self.assertNotIn(forbidden, layer)
        self.assertIn("QFrame#dialogCard {", TEMA_SOURCE)
        self.assertIn("QFrame#metricCard {", TEMA_SOURCE)
        self.assertIn("QFrame#miniStat {", TEMA_SOURCE)

    def test_composicao_final_e_posterior_a_navegacao_em_todos_os_temas(self):
        for theme_name in ("claro", "escuro", "futurista"):
            nav_marker = f'render_qss("{theme_name}", ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)'
            card_marker = f'render_qss("{theme_name}", ESTILO_CARDS_GLOBAIS_BLOCO_A)'
            self.assertEqual(TEMA_SOURCE.count(card_marker), 1)
            self.assertIn(nav_marker, TEMA_SOURCE)
            self.assertGreater(TEMA_SOURCE.index(card_marker), TEMA_SOURCE.index(nav_marker))

    def test_rollback_de_tema_recupera_checkpoint_anterior(self):
        restored = rollback_tema(TEMA_SOURCE)
        self.assertEqual(hashlib.sha256(restored.encode("utf-8")).hexdigest(), BASE_TEMA_HASH)

    def test_arquivos_protegidos_banco_versao_build_schema(self):
        for relative, expected in PROTECTED_HASHES.items():
            digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(digest, expected, relative)
        self.assertEqual(VIGHNA_VERSION, "0.29.59")
        self.assertEqual(VIGHNA_BUILD, "updates-center-v1")
        self.assertEqual(VIGHNA_SCHEMA, 25)
        con = sqlite3.connect(ROOT / "estudos.db")
        try:
            self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(), [])
        finally:
            con.close()


if __name__ == "__main__":
    unittest.main()
