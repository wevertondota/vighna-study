from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest
from _design_system_test_helpers import strip_cards_global_block_a_source

from ui.design import (
    ALL_TOKENS,
    COMPONENT_TOKEN_COUNT,
    PALETTE,
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

TOKENS = (
    "navigation.command_canvas",
    "navigation.command_title_text",
    "navigation.command_meta_text",
    "navigation.command_shortcut_surface",
    "navigation.command_shortcut_text",
    "navigation.command_shortcut_border",
    "navigation.command_input_surface",
    "navigation.command_input_text",
    "navigation.command_input_border",
    "navigation.command_input_selection",
    "navigation.command_input_focus_border",
    "navigation.command_results_surface",
    "navigation.command_results_text",
    "navigation.command_results_border",
    "navigation.command_results_selection_surface",
    "navigation.command_results_selection_text",
    "navigation.command_results_divider",
    "navigation.command_header_surface",
    "navigation.command_header_text",
    "navigation.command_header_border",
)

EXPECTED = {
    "claro": (
        "#F5F8FC", "#10233F", "#718096", "#EDF3FA", "#49637F", "#D1DEEB",
        "#FFFFFF", "#16263D", "#BFD1E5", "#CFE2FB", "#4B88CF", "#FFFFFF",
        "#203149", "#D8E3EF", "#E7F1FF", "#174F8A", "#EDF2F7", "#F4F7FB",
        "#617187", "#DBE5EF",
    ),
    "escuro": (
        "#0F1722", "#F2F6FB", "#8FA1B5", "#172334", "#A9BDD2", "#34495F",
        "#111C2A", "#EDF4FB", "#3D5873", "#315F91", "#6AA3DF", "#111C2A",
        "#DBE6F1", "#30465E", "#203D5D", "#EAF5FF", "#203044", "#142131",
        "#90A4B8", "#30445A",
    ),
    "futurista": (
        "#0F1520", "#F3F7FB", "#AEB7C4", "#232C38", "#D3DBE5", "#5D6774",
        "#202833", "#F3F7FB", "#4C5563", "#555AF0", "#8086FF", "#1D2430",
        "#DDE5EE", "#465162", "#343C8A", "#F8FAFC", "#2E3644", "#232C38",
        "#C2CAD4", "#465162",
    ),
}

PROTECTED_HASHES = {
    "main.py": "bdb0815e71387bd87d40498bf535ef839d19a1a9086d55e0582ea50946713b45",
    "navegacao.py": "2cb3439a580cf867af9870750a82e06777718961dd84819e0705a96838c8b862",
    "estudos.db": "034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef",
    "versao.py": "c201d237e622dd2269838e54914458fd775c7ec1a91f07b518775ee833caa439",
    "foco.py": "8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed",
    "jogos.py": "498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286",
    "checkpoint.py": "947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38",
}
BASE_I_TEMA_HASH = "d164c3b89ca1bb6535a393e70a371d4148e1bf1d76aa03299e9eac55d4861cc7"


def layer_template() -> str:
    match = re.search(
        r'ESTILO_NAVEGACAO_BUSCA_GLOBAL = r"""\n(?P<body>.*?)\n"""\n\n# =+\n# Design System — Navegação principal — Retornos ao Dashboard',
        TEMA_SOURCE,
        re.S,
    )
    if not match:
        raise AssertionError("camada de Busca global não encontrada")
    return match.group("body") + "\n"


def rollback_tema(source: str) -> str:
    source = strip_cards_global_block_a_source(source)
    source = re.sub(
        r'# ============================================================\n'
        r'# Design System — Navegação principal — Busca global\n'
        r'# Camada cromática aditiva, restrita ao QDialog da command palette\.\n'
        r'# O gatilho globalSearchTrigger continua pertencendo ao Dashboard A\.\n'
        r'# ============================================================\n'
        r'ESTILO_NAVEGACAO_BUSCA_GLOBAL = r"""\n.*?\n"""\n\n',
        "",
        source,
        count=1,
        flags=re.S,
    )
    source = re.sub(
        r'# ============================================================\n'
        r'# Design System — Navegação principal — Retornos ao Dashboard\n'
        r'# Camada aditiva de alta precisão: somente os seis subtleButton\n'
        r'# marcados explicitamente com navigationBack=true\.\n'
        r'# ============================================================\n'
        r'ESTILO_NAVEGACAO_RETORNOS_DASHBOARD = r"""\n.*?\n"""\n\n',
        "",
        source,
        count=1,
        flags=re.S,
    )
    for theme in ("claro", "escuro", "futurista"):
        source = source.replace(
            f' + render_qss("{theme}", ESTILO_NAVEGACAO_BUSCA_GLOBAL)',
            "",
            1,
        )
        source = source.replace(
            f' + render_qss("{theme}", ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)',
            "",
            1,
        )
    return source


class NavigationCommandPaletteDesignSystemTests(unittest.TestCase):
    def test_orcamento_final_e_contrato(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 928)
        self.assertEqual(len(ALL_TOKENS), 1030)
        self.assertEqual(len(TOKENS), 20)
        for path in TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.COLOR)

    def test_valores_historicos_preservados_nos_tres_temas(self):
        for theme_name, values in EXPECTED.items():
            theme = get_theme(theme_name)
            for path, expected in zip(TOKENS, values, strict=True):
                with self.subTest(theme=theme_name, token=path):
                    self.assertEqual(theme.color(path).value, expected)
                    self.assertEqual(PALETTE[PALETTE.reference(expected)].value, expected)

    def test_camada_e_estritamente_escopada_ao_dialogo(self):
        layer = layer_template()
        self.assertNotIn("globalSearchTrigger", layer)
        self.assertNotIn("globalSearchCloseButton", layer)
        self.assertNotRegex(layer, r"(?m)^Q(?:Label|LineEdit|TableWidget|HeaderView)(?:[#:\s,{])")
        rendered = render_qss("claro", layer)
        selectors = [part.strip() for part in re.findall(r"([^{}]+)\{", rendered)]
        self.assertGreaterEqual(len(selectors), 8)
        for selector_group in selectors:
            for selector in selector_group.split(","):
                selector = selector.strip()
                if selector:
                    self.assertTrue(
                        selector.startswith("QDialog#globalSearchDialog"),
                        selector,
                    )

    def test_estados_materiais_estao_cobertos(self):
        layer = layer_template()
        required = (
            "QDialog#globalSearchDialog {",
            "QLabel#globalSearchTitle",
            "QLabel#globalSearchShortcut",
            "QLineEdit#globalSearchInput {",
            "QLineEdit#globalSearchInput:focus",
            "selection-background-color",
            "QTableWidget#globalSearchResults {",
            "selection-background-color",
            "selection-color",
            "QTableWidget#globalSearchResults::item",
            "QHeaderView::section",
        )
        for marker in required:
            self.assertIn(marker, layer)
        for path in TOKENS:
            self.assertEqual(layer.count(f"{{{{color:{path}}}}}"), 1, path)

    def test_renderizacao_da_camada_resolve_todos_os_tokens(self):
        template = layer_template()
        for theme_name, values in EXPECTED.items():
            rendered = render_qss(theme_name, template)
            self.assertNotIn("{{color:", rendered)
            self.assertNotIn("{{gradient:", rendered)
            for value in set(values):
                self.assertIn(value, rendered)

    def test_composicao_final_existe_nos_tres_temas(self):
        for theme_name in ("claro", "escuro", "futurista"):
            marker = f'render_qss("{theme_name}", ESTILO_NAVEGACAO_BUSCA_GLOBAL)'
            self.assertEqual(TEMA_SOURCE.count(marker), 1)

    def test_rollback_de_tema_recupera_checkpoint_i(self):
        restored = rollback_tema(TEMA_SOURCE)
        self.assertEqual(
            hashlib.sha256(restored.encode("utf-8")).hexdigest(),
            BASE_I_TEMA_HASH,
        )

    def test_arquivos_funcionais_e_banco_permanecem_inalterados(self):
        for relative, expected in PROTECTED_HASHES.items():
            digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(digest, expected, relative)
        self.assertEqual(VIGHNA_VERSION, "0.29.59")
        self.assertEqual(VIGHNA_BUILD, "updates-center-v1")
        self.assertEqual(VIGHNA_SCHEMA, 25)

    def test_dialogo_mantem_objectnames_e_comportamento_no_navegacao(self):
        source = (ROOT / "navegacao.py").read_text(encoding="utf-8")
        for object_name in (
            "globalSearchDialog", "globalSearchTitle", "globalSearchSubtitle",
            "globalSearchShortcut", "globalSearchInput", "globalSearchResults",
            "globalSearchStatus", "globalSearchHint", "globalSearchCloseButton",
        ):
            self.assertIn(object_name, source)
        self.assertIn("setVisible(False)", source)


if __name__ == "__main__":
    unittest.main()
