import hashlib
import re
import unittest
from _design_system_test_helpers import strip_cards_global_block_a
from pathlib import Path

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

PASS1_TOKENS = (
    "focus_mode.panel",
    "focus_mode.panel_active",
    "focus_mode.text",
    "focus_mode.timer",
    "focus_mode.border",
    "focus_mode.secondary_text",
    "focus_mode.section_text",
    "focus_mode.meta_text",
    "focus_mode.panel_active_border",
    "focus_mode.hero_surface",
    "focus_mode.hero_border",
    "focus_mode.hero_eyebrow_text",
    "focus_mode.hero_value_text",
    "focus_mode.hero_status_text",
    "focus_mode.mini_surface",
    "focus_mode.mini_border",
    "focus_mode.mini_label_text",
    "focus_mode.mini_value_text",
)

EXPECTED = {
    "claro": {
        "focus_mode.panel": "#FFFFFF",
        "focus_mode.panel_active": "#F3F8FF",
        "focus_mode.text": "#182433",
        "focus_mode.timer": "#285F9E",
        "focus_mode.border": "#D9E2EC",
        "focus_mode.secondary_text": "#64748B",
        "focus_mode.section_text": "#243449",
        "focus_mode.meta_text": "#64748B",
        "focus_mode.panel_active_border": "#BCD4EF",
        "focus_mode.hero_surface": "#EEF6FF",
        "focus_mode.hero_border": "#CFE0F2",
        "focus_mode.hero_eyebrow_text": "#5E7B98",
        "focus_mode.hero_value_text": "#285F9E",
        "focus_mode.hero_status_text": "#203247",
        "focus_mode.mini_surface": "#FFFFFF",
        "focus_mode.mini_border": "#D8E2EE",
        "focus_mode.mini_label_text": "#6B7D90",
        "focus_mode.mini_value_text": "#244F83",
    },
    "escuro": {
        "focus_mode.panel": "#151F2D",
        "focus_mode.panel_active": "#15283C",
        "focus_mode.text": "#EEF5FB",
        "focus_mode.timer": "#A9D3FF",
        "focus_mode.border": "#33465A",
        "focus_mode.secondary_text": "#8FA2B5",
        "focus_mode.section_text": "#E8EEF5",
        "focus_mode.meta_text": "#8CA4BB",
        "focus_mode.panel_active_border": "#3B6289",
        "focus_mode.hero_surface": "#15283C",
        "focus_mode.hero_border": "#3B6289",
        "focus_mode.hero_eyebrow_text": "#8CA4BB",
        "focus_mode.hero_value_text": "#A9D3FF",
        "focus_mode.hero_status_text": "#E0EDF8",
        "focus_mode.mini_surface": "#172536",
        "focus_mode.mini_border": "#3A5877",
        "focus_mode.mini_label_text": "#90A8BF",
        "focus_mode.mini_value_text": "#D6EAFF",
    },
    "futurista": {
        "focus_mode.panel": "#101F30",
        "focus_mode.panel_active": "#10283C",
        "focus_mode.text": "#E1F7FF",
        "focus_mode.timer": "#8FD8FF",
        "focus_mode.border": "#315D79",
        "focus_mode.secondary_text": "#8EAFC3",
        "focus_mode.section_text": "#E1F7FF",
        "focus_mode.meta_text": "#82ABC5",
        "focus_mode.panel_active_border": "#3F7599",
        "focus_mode.hero_surface": "#10283C",
        "focus_mode.hero_border": "#3F7599",
        "focus_mode.hero_eyebrow_text": "#82ABC5",
        "focus_mode.hero_value_text": "#BCE7FF",
        "focus_mode.hero_status_text": "#EAF8FF",
        "focus_mode.mini_surface": "#132B40",
        "focus_mode.mini_border": "#3E7397",
        "focus_mode.mini_label_text": "#82ABC5",
        "focus_mode.mini_value_text": "#D9F4FF",
    },
}

BASELINE_NORMALIZED_HASHES = {
    "claro": "71c6c022b5fb4a3798f5bb9f837fc55fc9fa3bf4d558832688dd7fb25d8c7cdb",
    "escuro": "25dd9d735b8aa542020a05bbc3318cc91aba79f0b2f89995cea0a272d8bc1056",
    "futurista": "d4176c63eae7f8b0349fce4eb50ada9b5186473a8d0aba884ad7aa4e41f5b448",
}


def normalized_hash(qss: str) -> str:
    qss = re.sub(r"#[0-9A-Fa-f]{3,8}\b", lambda m: m.group(0).upper(), qss)
    qss = re.sub(r"\s+", " ", qss).strip()
    return hashlib.sha256(qss.encode("utf-8")).hexdigest()



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

class DesignSystemModoFocoPasso1Tests(unittest.TestCase):
    def test_contagem_de_tokens(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 1004)
        self.assertEqual(len(ALL_TOKENS), 1106)

    def test_contratos_do_passo_1_sao_color(self):
        for path in PASS1_TOKENS:
            with self.subTest(path=path):
                self.assertEqual(token_spec(path).kind, TokenKind.COLOR)

    def test_valores_reproduzem_linha_de_base(self):
        for theme_name, values in EXPECTED.items():
            theme = get_theme(theme_name)
            for path, expected in values.items():
                with self.subTest(theme=theme_name, path=path):
                    self.assertEqual(theme.color(path).value, expected)

    def test_qss_foco_consumiu_somente_nucleo_do_passo_1(self):
        required = (
            "{{color:focus_mode.panel}}",
            "{{color:focus_mode.panel_active}}",
            "{{color:focus_mode.text}}",
            "{{color:focus_mode.timer}}",
            "{{color:focus_mode.border}}",
            "{{color:focus_mode.secondary_text}}",
            "{{color:focus_mode.section_text}}",
            "{{color:focus_mode.meta_text}}",
            "{{color:focus_mode.panel_active_border}}",
            "{{color:focus_mode.hero_surface}}",
            "{{color:focus_mode.hero_border}}",
            "{{color:focus_mode.hero_eyebrow_text}}",
            "{{color:focus_mode.hero_value_text}}",
            "{{color:focus_mode.hero_status_text}}",
            "{{color:focus_mode.mini_surface}}",
            "{{color:focus_mode.mini_border}}",
            "{{color:focus_mode.mini_label_text}}",
            "{{color:focus_mode.mini_value_text}}",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, TEMA_SOURCE)

        # Passo 2 passa a consumir ações/progresso. O canvas continua sem
        # consumidor local porque a janela usa o canvas global existente.
        self.assertNotIn("{{color:focus_mode.canvas}}", TEMA_SOURCE)

    def test_passos_posteriores_preservam_fronteiras(self):
        self.assertIn("{{gradient:focus_mode.action_gradient}}", TEMA_SOURCE)
        self.assertIn("{{color:focus_mode.progress_track}}", TEMA_SOURCE)
        self.assertIn("{{color:post_focus.hero_surface}}", TEMA_SOURCE)
        self.assertIn("{{color:pause.timer_panel_surface}}", TEMA_SOURCE)
        self.assertIn("{{color:game.board_surface}}", TEMA_SOURCE)
        self.assertIn("{{gradient:game.primary_gradient}}", TEMA_SOURCE)

    def test_qss_renderizado_permanece_normalizado_identico_ao_passo_b(self):
        styles = {
            "claro": tema.stylesheet_claro(),
            "escuro": tema.stylesheet_escuro(),
            "futurista": tema.stylesheet_futurista(),
        }
        for theme_name, qss in styles.items():
            with self.subTest(theme=theme_name):
                baseline_qss = strip_navigation_search_layer(theme_name, qss)
                self.assertEqual(normalized_hash(baseline_qss), BASELINE_NORMALIZED_HASHES[theme_name])
                self.assertNotIn("{{color:", qss)
                self.assertNotIn("{{gradient:", qss)

    def test_futurista_preserva_composicao_escuro_mais_override(self):
        self.assertIn(
            'return stylesheet_escuro() + render_qss("futurista", r"""',
            TEMA_SOURCE,
        )


if __name__ == "__main__":
    unittest.main()
