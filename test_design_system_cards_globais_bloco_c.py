from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sqlite3
import unittest

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
from _design_system_test_helpers import strip_focus_mode_resolver_integration_source

ROOT = Path(__file__).resolve().parent
TEMA_PATH = ROOT / "tema.py"
TEMA_SOURCE = TEMA_PATH.read_text(encoding="utf-8")
MAIN_SOURCE = (ROOT / "main.py").read_text(encoding="utf-8")

COLOR_TOKENS = (
    "card.evolution_stat_border",
    "card.evolution_stat_label_text",
    "card.evolution_stat_value_text",
    "card.evolution_stat_detail_text",
)
GRADIENT_TOKENS = ("card.evolution_stat_surface_gradient",)

EXPECTED_COLORS = {
    "claro": ("#D8E0EA", "#758397", "#233247", "#8995A5"),
    "escuro": ("#33475D", "#8999AC", "#E0E8F0", "#78899D"),
    "futurista": ("#2D5670", "#7794A7", "#DCECF3", "#6F8CA0"),
}
EXPECTED_GRADIENTS = {
    "claro": ((0.0, "#FFFFFF"), (1.0, "#FFFFFF")),
    "escuro": ((0.0, "#111D2B"), (1.0, "#111D2B")),
    "futurista": ((0.0, "#0D2032"), (1.0, "#091725")),
}

BASE_TEMA_HASH = "fcef8e2c41bfe508cd3ff542f52fa119eb2862c4be2b07231429af732e366661"
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
        r'ESTILO_CARDS_GLOBAIS_BLOCO_C = r"""\n(?P<body>.*?)\n"""\n\ndef stylesheet_claro\(\):',
        TEMA_SOURCE,
        re.S,
    )
    if not match:
        raise AssertionError("camada Cards globais C não encontrada")
    return match.group("body") + "\n"


def rollback_tema(source: str) -> str:
    source = strip_focus_mode_resolver_integration_source(source)
    source = re.sub(
        r'# ============================================================\n'
        r'# Design System — Cards globais — Bloco C\n'
        r'# myEvolutionStatCard compartilhado\. Somente shell e cores dos\n'
        r'# textos descendentes; a família myEvolution restante fica intacta\.\n'
        r'# ============================================================\n'
        r'ESTILO_CARDS_GLOBAIS_BLOCO_C = r"""\n.*?\n"""\n\n',
        "",
        source,
        count=1,
        flags=re.S,
    )
    for theme_name in ("claro", "escuro", "futurista"):
        source = source.replace(
            f' + render_qss("{theme_name}", ESTILO_CARDS_GLOBAIS_BLOCO_C)',
            "",
            1,
        )
    return source


class GlobalCardsBlockCTests(unittest.TestCase):
    def test_contrato_e_orcamento_final(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 928)
        self.assertEqual(len(ALL_TOKENS), 1030)
        self.assertEqual(sum(t.kind is TokenKind.COLOR for t in ALL_TOKENS), 954)
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

    def test_gradiente_preserva_superficie_historica(self):
        for theme_name, expected in EXPECTED_GRADIENTS.items():
            gradient = get_theme(theme_name).gradient(GRADIENT_TOKENS[0])
            with self.subTest(theme=theme_name):
                self.assertEqual(
                    (gradient.direction.x1, gradient.direction.y1, gradient.direction.x2, gradient.direction.y2),
                    (0.0, 0.0, 1.0, 1.0),
                )
                self.assertEqual(
                    tuple((stop.position, stop.color.value) for stop in gradient.stops),
                    expected,
                )

    def test_camada_escopa_shell_e_textos_somente_dentro_do_card(self):
        layer = layer_template()
        required = (
            "QFrame#myEvolutionStatCard {",
            "QFrame#myEvolutionStatCard QLabel#myEvolutionStatLabel {",
            "QFrame#myEvolutionStatCard QLabel#myEvolutionStatValue {",
            "QFrame#myEvolutionStatCard QLabel#myEvolutionStatDetail {",
        )
        for selector in required:
            self.assertEqual(layer.count(selector), 1, selector)
        self.assertNotRegex(layer, r'(?m)^QLabel#myEvolutionStat(?:Label|Value|Detail)\s*\{')

    def test_familia_my_evolution_fora_do_recorte_permanece_intocada(self):
        layer = layer_template()
        for forbidden in (
            "myEvolutionFilterBar", "myEvolutionPanel", "myEvolutionTitle",
            "myEvolutionSectionTitle", "myEvolutionInsight", "evidenceTone",
            "evolutionChartCard", "evolutionDisciplineCard",
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

    def test_inventario_compartilhado_permanece_no_codigo_sem_marcacao_nova(self):
        # O recorte deve funcionar apenas pela especificidade QSS; nenhum consumidor precisa ser marcado.
        self.assertGreaterEqual(len(re.findall(r'setObjectName\(\s*"myEvolutionStatCard"\s*\)', MAIN_SOURCE)), 6)
        self.assertNotIn('evolutionStatCard=', MAIN_SOURCE)

    def test_renderizacao_resolve_tokens_em_todos_os_temas(self):
        template = layer_template()
        for theme_name in ("claro", "escuro", "futurista"):
            rendered = render_qss(theme_name, template)
            self.assertNotIn("{{color:", rendered)
            self.assertNotIn("{{gradient:", rendered)
            self.assertIn("QFrame#myEvolutionStatCard", rendered)
            for value in EXPECTED_COLORS[theme_name]:
                self.assertIn(value, rendered)
            for _, value in EXPECTED_GRADIENTS[theme_name]:
                self.assertIn(value, rendered)

    def test_composicao_final_fica_depois_do_bloco_b_em_todos_os_temas(self):
        for theme_name in ("claro", "escuro", "futurista"):
            b_marker = f'render_qss("{theme_name}", ESTILO_CARDS_GLOBAIS_BLOCO_B)'
            c_marker = f'render_qss("{theme_name}", ESTILO_CARDS_GLOBAIS_BLOCO_C)'
            self.assertEqual(TEMA_SOURCE.count(c_marker), 1)
            self.assertIn(b_marker, TEMA_SOURCE)
            self.assertGreater(TEMA_SOURCE.index(c_marker), TEMA_SOURCE.index(b_marker))

    def test_rollback_e_arquivos_protegidos_banco_versao(self):
        restored = rollback_tema(TEMA_SOURCE)
        self.assertEqual(hashlib.sha256(restored.encode("utf-8")).hexdigest(), BASE_TEMA_HASH)
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
