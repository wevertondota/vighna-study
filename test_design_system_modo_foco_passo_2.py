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

NEW_COLOR_TOKENS = (
    "focus_mode.secondary_action_surface",
    "focus_mode.secondary_action_text",
    "focus_mode.secondary_action_border",
    "focus_mode.secondary_action_hover_surface",
    "focus_mode.secondary_action_hover_text",
    "focus_mode.secondary_action_hover_border",
    "focus_mode.action_border",
    "focus_mode.action_hover_border",
    "focus_mode.action_pressed_border",
    "focus_mode.danger_text",
    "focus_mode.danger_border",
    "focus_mode.danger_hover_surface",
    "focus_mode.danger_hover_border",
    "focus_mode.progress_track",
    "focus_mode.progress_fill",
    "focus_mode.progress_border",
    "focus_mode.optional_surface",
    "focus_mode.optional_border",
    "focus_mode.notice_surface",
    "focus_mode.notice_text",
    "focus_mode.notice_border",
)

RECHARACTERIZED_COLOR_TOKENS = (
    "focus_mode.action",
    "focus_mode.danger",
)

EXPECTED_COLORS = {
    "claro": {
        "focus_mode.secondary_action_surface": "#FFFFFF",
        "focus_mode.secondary_action_text": "#32679F",
        "focus_mode.secondary_action_border": "#B9CEE4",
        "focus_mode.secondary_action_hover_surface": "#EEF6FF",
        "focus_mode.secondary_action_hover_text": "#245889",
        "focus_mode.secondary_action_hover_border": "#8DB7E4",
        "focus_mode.action": "#A91520",
        "focus_mode.action_border": "#A91520",
        "focus_mode.action_hover_border": "#8F111A",
        "focus_mode.action_pressed_border": "#7F1018",
        "focus_mode.danger": "#FFF7F5",
        "focus_mode.danger_text": "#A84A3F",
        "focus_mode.danger_border": "#E4B6B0",
        "focus_mode.danger_hover_surface": "#FFEBE8",
        "focus_mode.danger_hover_border": "#D8948B",
        "focus_mode.progress_track": "#E4EDF7",
        "focus_mode.progress_fill": "#3B82D0",
        "focus_mode.progress_border": "transparent",
        "focus_mode.optional_surface": "#F8FBFF",
        "focus_mode.optional_border": "#C9D8E8",
        "focus_mode.notice_surface": "#EEF6FF",
        "focus_mode.notice_text": "#245889",
        "focus_mode.notice_border": "#B9D3EE",
    },
    "escuro": {
        "focus_mode.secondary_action_surface": "#172536",
        "focus_mode.secondary_action_text": "#B9D8F7",
        "focus_mode.secondary_action_border": "#3A5877",
        "focus_mode.secondary_action_hover_surface": "#20374F",
        "focus_mode.secondary_action_hover_text": "#E0F0FF",
        "focus_mode.secondary_action_hover_border": "#527BA5",
        "focus_mode.action": "#9F1723",
        "focus_mode.action_border": "#FF6973",
        "focus_mode.action_hover_border": "#FF9298",
        "focus_mode.action_pressed_border": "#FF5964",
        "focus_mode.danger": "#392322",
        "focus_mode.danger_text": "#F0B6AE",
        "focus_mode.danger_border": "#70433E",
        "focus_mode.danger_hover_surface": "#4B2B28",
        "focus_mode.danger_hover_border": "#945950",
        "focus_mode.progress_track": "#27384A",
        "focus_mode.progress_fill": "#4F83C5",
        "focus_mode.progress_border": "transparent",
        "focus_mode.optional_surface": "transparent",
        "focus_mode.optional_border": "transparent",
        "focus_mode.notice_surface": "transparent",
        "focus_mode.notice_text": "transparent",
        "focus_mode.notice_border": "transparent",
    },
    "futurista": {
        "focus_mode.secondary_action_surface": "#132B40",
        "focus_mode.secondary_action_text": "#BCE7FF",
        "focus_mode.secondary_action_border": "#3E7397",
        "focus_mode.secondary_action_hover_surface": "#183850",
        "focus_mode.secondary_action_hover_text": "#EDFBFF",
        "focus_mode.secondary_action_hover_border": "#65B9DF",
        "focus_mode.action": "#981827",
        "focus_mode.action_border": "#FF7382",
        "focus_mode.action_hover_border": "#FFABB3",
        "focus_mode.action_pressed_border": "#FF596B",
        "focus_mode.danger": "#402827",
        "focus_mode.danger_text": "#FFD0C9",
        "focus_mode.danger_border": "#8D554D",
        "focus_mode.danger_hover_surface": "#4B2B28",
        "focus_mode.danger_hover_border": "#945950",
        "focus_mode.progress_track": "#173046",
        "focus_mode.progress_fill": "#55A7D5",
        "focus_mode.progress_border": "#2E5C78",
        "focus_mode.optional_surface": "transparent",
        "focus_mode.optional_border": "transparent",
        "focus_mode.notice_surface": "transparent",
        "focus_mode.notice_text": "transparent",
        "focus_mode.notice_border": "transparent",
    },
}

EXPECTED_GRADIENTS = {
    "claro": {
        "focus_mode.action_gradient": ((0.0, "#C91F2B"), (0.52, "#DC2626"), (1.0, "#EF4444")),
        "focus_mode.action_hover_gradient": ((0.0, "#B81924"), (0.52, "#CF202B"), (1.0, "#E43742")),
    },
    "escuro": {
        "focus_mode.action_gradient": ((0.0, "#B91C2A"), (0.52, "#D92D3A"), (1.0, "#F04451")),
        "focus_mode.action_hover_gradient": ((0.0, "#CF2634"), (0.52, "#E63B47"), (1.0, "#FF5964")),
    },
    "futurista": {
        "focus_mode.action_gradient": ((0.0, "#B51F31"), (0.52, "#D62B3D"), (1.0, "#F04458")),
        "focus_mode.action_hover_gradient": ((0.0, "#CE293B"), (0.52, "#E83B4C"), (1.0, "#FF596B")),
    },
}

BASELINE_NORMALIZED_HASHES = {
    "claro": "71c6c022b5fb4a3798f5bb9f837fc55fc9fa3bf4d558832688dd7fb25d8c7cdb",
    "escuro": "25dd9d735b8aa542020a05bbc3318cc91aba79f0b2f89995cea0a272d8bc1056",
    "futurista": "0e1011b5790c7a6f775d70ef4a59dd60a4c1587de412e9533bed2e39b1cba14f",
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

class DesignSystemModoFocoPasso2Tests(unittest.TestCase):
    def test_contagem_de_tokens(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 1148)
        self.assertEqual(len(ALL_TOKENS), 1250)

    def test_novos_contratos_sao_color_e_gradientes_mantem_tipo(self):
        for path in NEW_COLOR_TOKENS + RECHARACTERIZED_COLOR_TOKENS:
            with self.subTest(path=path):
                self.assertEqual(token_spec(path).kind, TokenKind.COLOR)
        for path in ("focus_mode.action_gradient", "focus_mode.action_hover_gradient"):
            with self.subTest(path=path):
                self.assertEqual(token_spec(path).kind, TokenKind.GRADIENT)

    def test_cores_reproduzem_linha_de_base(self):
        for theme_name, values in EXPECTED_COLORS.items():
            theme = get_theme(theme_name)
            for path, expected in values.items():
                with self.subTest(theme=theme_name, path=path):
                    self.assertEqual(theme.color(path).value, expected)

    def test_gradientes_reproduzem_linha_de_base(self):
        for theme_name, gradients in EXPECTED_GRADIENTS.items():
            theme = get_theme(theme_name)
            for path, expected in gradients.items():
                with self.subTest(theme=theme_name, path=path):
                    spec = theme.gradient(path)
                    self.assertEqual(
                        tuple((stop.position, stop.color.value) for stop in spec.stops),
                        expected,
                    )
                    self.assertEqual(
                        (spec.direction.x1, spec.direction.y1, spec.direction.x2, spec.direction.y2),
                        (0.0, 0.0, 1.0, 0.0),
                    )

    def test_consumidores_estao_limitados_ao_modo_foco(self):
        self.assertEqual(TEMA_SOURCE.count("{{gradient:focus_mode.action_gradient}}"), 3)
        self.assertEqual(TEMA_SOURCE.count("{{gradient:focus_mode.action_hover_gradient}}"), 3)
        self.assertEqual(TEMA_SOURCE.count("{{color:focus_mode.action}}"), 3)
        self.assertEqual(TEMA_SOURCE.count("{{color:focus_mode.progress_track}}"), 3)
        self.assertEqual(TEMA_SOURCE.count("{{color:focus_mode.progress_fill}}"), 3)
        self.assertEqual(TEMA_SOURCE.count("{{color:focus_mode.progress_border}}"), 1)
        self.assertEqual(TEMA_SOURCE.count("{{color:focus_mode.optional_surface}}"), 1)
        self.assertEqual(TEMA_SOURCE.count("{{color:focus_mode.notice_surface}}"), 1)
        self.assertNotIn("{{color:focus_mode.canvas}}", TEMA_SOURCE)
        self.assertIn("{{color:post_focus.hero_surface}}", TEMA_SOURCE)
        self.assertIn("{{color:pause.timer_panel_surface}}", TEMA_SOURCE)
        self.assertIn("{{color:game.board_surface}}", TEMA_SOURCE)
        self.assertIn("{{gradient:game.primary_gradient}}", TEMA_SOURCE)

    def test_excecoes_claro_only_permanecem_assimetricas(self):
        self.assertEqual(TEMA_SOURCE.count("QFrame#focusOptionalPanel {"), 1)
        self.assertEqual(TEMA_SOURCE.count("QLabel#focusAutoQuestionsNotice {"), 1)
        self.assertIn("border: 1px dashed {{color:focus_mode.optional_border}}", TEMA_SOURCE)
        self.assertEqual(get_theme("escuro").color("focus_mode.optional_surface").value, "transparent")
        self.assertEqual(get_theme("futurista").color("focus_mode.notice_surface").value, "transparent")

    def test_progresso_preserva_border_none_e_override_futurista(self):
        focus_progress_no_border = (
            "QProgressBar#focusProgressBar { min-height: 8px; max-height: 8px; "
            "background-color: {{color:focus_mode.progress_track}}; border: none; border-radius: 4px; }"
        )
        self.assertEqual(TEMA_SOURCE.count(focus_progress_no_border), 2)
        self.assertIn(
            "border: 1px solid {{color:focus_mode.progress_border}}; border-radius: 4px;",
            TEMA_SOURCE,
        )

    def test_qss_renderizado_permanece_normalizado_identico_ao_passo_1(self):
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

    def test_futurista_preserva_heranca_do_hover_destrutivo(self):
        # Há duas regras hover na fonte: Claro e Escuro. Futurista continua
        # herdando a regra Escuro, como antes, sem duplicação incidental.
        self.assertEqual(TEMA_SOURCE.count("QPushButton#focusDangerButton:hover"), 2)
        self.assertIn(
            'return stylesheet_escuro() + render_qss("futurista", r"""',
            TEMA_SOURCE,
        )


if __name__ == "__main__":
    unittest.main()
