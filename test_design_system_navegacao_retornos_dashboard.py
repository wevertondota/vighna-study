from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest
from _design_system_test_helpers import strip_cards_global_block_a_source

from ui.design import (
    ALL_TOKENS,
    COMPONENT_TOKEN_COUNT,
    SEMANTIC_TOKEN_COUNT,
    TokenKind,
    get_theme,
    qss_gradient,
    render_qss,
    token_spec,
)
from versao import VIGHNA_BUILD, VIGHNA_SCHEMA, VIGHNA_VERSION

ROOT = Path(__file__).resolve().parent
MAIN_PATH = ROOT / "main.py"
TEMA_PATH = ROOT / "tema.py"
MAIN_SOURCE = MAIN_PATH.read_text(encoding="utf-8")
TEMA_SOURCE = TEMA_PATH.read_text(encoding="utf-8")

COLOR_TOKENS = (
    "navigation.back_text",
    "navigation.back_border",
    "navigation.back_hover_text",
    "navigation.back_hover_border",
)
GRADIENT_TOKENS = (
    "navigation.back_surface_gradient",
    "navigation.back_hover_surface_gradient",
)

EXPECTED_COLORS = {
    "claro": ("#334155", "#CFD8E3", "#235F98", "#9FC7E7"),
    "escuro": ("#DCE6F0", "#33475E", "#9BD5FF", "#4D89B8"),
    "futurista": ("#E7F5FF", "#40688D", "#C8F6FF", "#56DFFF"),
}
EXPECTED_GRADIENTS = {
    "claro": (
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFFFFF, stop:1 #FFFFFF)",
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F6FBFF, stop:1 #F6FBFF)",
    ),
    "escuro": (
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #162333, stop:1 #162333)",
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1C3145, stop:1 #1C3145)",
    ),
    "futurista": (
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #162B42, stop:1 #0D1D30)",
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1A3854, stop:1 #10263D)",
    ),
}

BASE_MAIN_HASH = "98c51d9eb1bf791d96a59a8d6b4e403bd6914348d0773fe0185a9c6a22d3fa3a"
BASE_SEARCH_TEMA_HASH = "d9ea7a462661fb35dca10b87e0b89ead5f3ec23a3855f8eb8aa1412e344d6ded"
PROTECTED_HASHES = {
    "navegacao.py": "2cb3439a580cf867af9870750a82e06777718961dd84819e0705a96838c8b862",
    "estudos.db": "034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef",
    "versao.py": "c201d237e622dd2269838e54914458fd775c7ec1a91f07b518775ee833caa439",
    "foco.py": "8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed",
    "jogos.py": "498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286",
    "checkpoint.py": "947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38",
}

BACK_FUNCTIONS = {
    "criar_tela_resumo_dia": "self.voltar_inicio",
    "criar_tela_sessao_estudo": "self.pausar_sessao_estudo",
    "criar_tela_calendario": "self.voltar_inicio",
    "criar_tela_relatorios": "self.voltar_inicio",
    "criar_tela_estatisticas": "self.voltar_inicio",
    "criar_tela_disciplina": "self.voltar_inicio",
}


def function_body(name: str) -> str:
    match = re.search(
        rf"^    def {re.escape(name)}\(self\):\n(?P<body>.*?)(?=^    def |\Z)",
        MAIN_SOURCE,
        re.M | re.S,
    )
    if not match:
        raise AssertionError(f"função não encontrada: {name}")
    return match.group("body")


def layer_template() -> str:
    match = re.search(
        r'ESTILO_NAVEGACAO_RETORNOS_DASHBOARD = r"""\n(?P<body>.*?)\n"""\n\n# =+\n# Design System — Cards globais — Bloco A',
        TEMA_SOURCE,
        re.S,
    )
    if not match:
        raise AssertionError("camada de retornos não encontrada")
    return match.group("body") + "\n"


def rollback_main(source: str) -> str:
    block = '''        voltar.setProperty(\n            "navigationBack",\n            True\n        )\n'''
    if source.count(block) != 6:
        raise AssertionError("quantidade inesperada de marcações navigationBack")
    return source.replace(block, "")


def rollback_tema(source: str) -> str:
    source = strip_cards_global_block_a_source(source)
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
    for theme_name in ("claro", "escuro", "futurista"):
        source = source.replace(
            f' + render_qss("{theme_name}", ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)',
            "",
            1,
        )
    return source


class NavigationBackDesignSystemTests(unittest.TestCase):
    def test_contrato_e_orcamento_final(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 928)
        self.assertEqual(len(ALL_TOKENS), 1030)
        for path in COLOR_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.COLOR)
        for path in GRADIENT_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.GRADIENT)

    def test_valores_historicos_preservados_nos_tres_temas(self):
        for theme_name, expected in EXPECTED_COLORS.items():
            theme = get_theme(theme_name)
            for path, value in zip(COLOR_TOKENS, expected, strict=True):
                with self.subTest(theme=theme_name, token=path):
                    self.assertEqual(theme.color(path).value, value)
        for theme_name, expected in EXPECTED_GRADIENTS.items():
            for path, value in zip(GRADIENT_TOKENS, expected, strict=True):
                with self.subTest(theme=theme_name, token=path):
                    self.assertEqual(qss_gradient(theme_name, path), value)

    def test_exatamente_seis_retornos_principais_foram_marcados(self):
        self.assertEqual(MAIN_SOURCE.count('"navigationBack"'), 6)
        subtle_uses = re.findall(r'setObjectName\(\s*"subtleButton"\s*\)', MAIN_SOURCE)
        self.assertEqual(len(subtle_uses), 97)
        for function_name, callback in BACK_FUNCTIONS.items():
            body = function_body(function_name)
            self.assertEqual(body.count('"← Voltar"'), 1, function_name)
            self.assertEqual(body.count('"navigationBack"'), 1, function_name)
            self.assertIn(callback, body)

    def test_central_de_questoes_permanece_fora_do_recorte(self):
        body = function_body("criar_tela_questoes")
        self.assertEqual(body.count('"← Voltar"'), 1)
        self.assertIn('"backButton"', body)
        self.assertNotIn('"navigationBack"', body)
        self.assertIn("self.voltar_inicio", body)

    def test_camada_e_precisa_e_nao_migra_subtlebutton_global(self):
        layer = layer_template()
        normal = 'QPushButton#subtleButton[navigationBack="true"] {'
        hover = 'QPushButton#subtleButton[navigationBack="true"]:hover {'
        self.assertEqual(layer.count(normal), 1)
        self.assertEqual(layer.count(hover), 1)
        self.assertNotRegex(layer, r'(?m)^QPushButton#subtleButton\s*\{')
        for path in COLOR_TOKENS:
            self.assertEqual(layer.count(f"{{{{color:{path}}}}}"), 1, path)
        for path in GRADIENT_TOKENS:
            self.assertEqual(layer.count(f"{{{{gradient:{path}}}}}"), 1, path)

    def test_renderizacao_resolve_tokens_e_preserva_gradientes(self):
        template = layer_template()
        for theme_name in ("claro", "escuro", "futurista"):
            rendered = render_qss(theme_name, template)
            self.assertNotIn("{{color:", rendered)
            self.assertNotIn("{{gradient:", rendered)
            for value in EXPECTED_COLORS[theme_name]:
                self.assertIn(value, rendered)
            for value in EXPECTED_GRADIENTS[theme_name]:
                self.assertIn(value, rendered)

    def test_camada_final_e_composta_depois_da_busca_global(self):
        for theme_name in ("claro", "escuro", "futurista"):
            search_marker = f'render_qss("{theme_name}", ESTILO_NAVEGACAO_BUSCA_GLOBAL)'
            back_marker = f'render_qss("{theme_name}", ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)'
            self.assertIn(search_marker, TEMA_SOURCE)
            self.assertIn(back_marker, TEMA_SOURCE)
            self.assertGreater(TEMA_SOURCE.index(back_marker), TEMA_SOURCE.index(search_marker))

    def test_composicao_final_existe_uma_vez_por_tema(self):
        for theme_name in ("claro", "escuro", "futurista"):
            marker = f'render_qss("{theme_name}", ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)'
            self.assertEqual(TEMA_SOURCE.count(marker), 1)

    def test_rollback_de_main_e_tema_recupera_checkpoint_busca_global(self):
        restored_main = rollback_main(MAIN_SOURCE)
        restored_tema = rollback_tema(TEMA_SOURCE)
        self.assertEqual(hashlib.sha256(restored_main.encode("utf-8")).hexdigest(), BASE_MAIN_HASH)
        self.assertEqual(hashlib.sha256(restored_tema.encode("utf-8")).hexdigest(), BASE_SEARCH_TEMA_HASH)

    def test_arquivos_protegidos_banco_versao_build_schema(self):
        for relative, expected in PROTECTED_HASHES.items():
            digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(digest, expected, relative)
        self.assertEqual(VIGHNA_VERSION, "0.29.59")
        self.assertEqual(VIGHNA_BUILD, "updates-center-v1")
        self.assertEqual(VIGHNA_SCHEMA, 25)


if __name__ == "__main__":
    unittest.main()
