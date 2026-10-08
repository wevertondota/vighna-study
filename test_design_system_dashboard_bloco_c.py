"""Regressões do Design System — Dashboard, Bloco C: recomendação + progresso + acessos rápidos."""
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
    render_qss,
    token_spec,
)
from versao import VIGHNA_BUILD, VIGHNA_SCHEMA, VIGHNA_VERSION

ROOT = Path(__file__).resolve().parent
TEMA_SOURCE = (ROOT / "tema.py").read_text(encoding="utf-8")
MAIN_SOURCE = (ROOT / "main.py").read_text(encoding="utf-8")

COLOR_TOKENS = {
    "dashboard.recommendation_card_border",
    "dashboard.recommendation_icon_text",
    "dashboard.recommendation_icon_border",
    "dashboard.recommendation_title_text",
    "dashboard.recommendation_subtitle_text",
    "dashboard.recommendation_help_surface",
    "dashboard.recommendation_help_text",
    "dashboard.recommendation_help_border",
    "dashboard.recommendation_help_hover_surface",
    "dashboard.recommendation_help_hover_text",
    "dashboard.recommendation_help_hover_border",
    "dashboard.recommendation_body_surface",
    "dashboard.recommendation_body_border",
    "dashboard.recommendation_ready_text",
    "dashboard.recommendation_primary_text",
    "dashboard.recommendation_primary_border",
    "dashboard.recommendation_primary_hover_border",
    "dashboard.recommendation_primary_pressed_surface",
    "dashboard.recommendation_primary_pressed_border",
    "dashboard.recommendation_secondary_text",
    "dashboard.recommendation_secondary_hover_text",
    "dashboard.progress_card_border",
    "dashboard.progress_icon_text",
    "dashboard.progress_icon_surface",
    "dashboard.progress_icon_border",
    "dashboard.progress_title_text",
    "dashboard.progress_description_text",
    "dashboard.progress_detail_text",
    "dashboard.progress_badge_surface",
    "dashboard.progress_badge_text",
    "dashboard.progress_badge_border",
    "dashboard.progress_track",
    "dashboard.progress_button_surface",
    "dashboard.progress_button_text",
    "dashboard.progress_button_border",
    "dashboard.progress_button_hover_surface",
    "dashboard.progress_button_hover_text",
    "dashboard.progress_button_hover_border",
    "dashboard.quick_border",
    "dashboard.quick_toggle_text",
    "dashboard.quick_toolbar_text",
    "dashboard.quick_toolbar_border",
    "dashboard.quick_toolbar_hover_text",
    "dashboard.quick_toolbar_hover_border",
    "dashboard.quick_pause_text",
    "dashboard.quick_pause_border",
    "dashboard.quick_pause_hover_text",
    "dashboard.quick_pause_hover_border",
}

GRADIENT_TOKENS = {
    "dashboard.recommendation_card_gradient",
    "dashboard.recommendation_icon_gradient",
    "dashboard.recommendation_primary_gradient",
    "dashboard.recommendation_primary_hover_gradient",
    "dashboard.progress_card_gradient",
    "dashboard.progress_fill_gradient",
    "dashboard.quick_access_gradient",
    "dashboard.quick_toolbar_gradient",
    "dashboard.quick_toolbar_hover_gradient",
    "dashboard.quick_pause_gradient",
    "dashboard.quick_pause_hover_gradient",
}

BLOCK_C_TOKENS = COLOR_TOKENS | GRADIENT_TOKENS

EXPECTED_COLORS = {
    "claro": {
        'dashboard.recommendation_card_border': '#E2E8F0', 'dashboard.recommendation_icon_text': '#477FAE',
        'dashboard.recommendation_icon_border': '#D4E3F0', 'dashboard.recommendation_title_text': '#1A202C',
        'dashboard.recommendation_subtitle_text': '#718096', 'dashboard.recommendation_help_surface': '#FBFDFF',
        'dashboard.recommendation_help_text': '#315B87', 'dashboard.recommendation_help_border': '#D2DFEC',
        'dashboard.recommendation_help_hover_surface': '#F0F6FD', 'dashboard.recommendation_help_hover_text': '#315B87',
        'dashboard.recommendation_help_hover_border': '#B7CFE7', 'dashboard.recommendation_body_surface': '#F8FBFF',
        'dashboard.recommendation_body_border': '#E1EAF4', 'dashboard.recommendation_ready_text': '#1A202C',
        'dashboard.recommendation_primary_text': '#FFFFFF', 'dashboard.recommendation_primary_border': '#4277B8',
        'dashboard.recommendation_primary_hover_border': '#3B6DA9', 'dashboard.recommendation_primary_pressed_surface': '#3B6DA9',
        'dashboard.recommendation_primary_pressed_border': '#35629A', 'dashboard.recommendation_secondary_text': '#557FA9',
        'dashboard.recommendation_secondary_hover_text': '#164D86', 'dashboard.progress_card_border': '#E2E8F0',
        'dashboard.progress_icon_text': '#3295A7', 'dashboard.progress_icon_surface': '#EFFAFD',
        'dashboard.progress_icon_border': '#CDE8EE', 'dashboard.progress_title_text': '#1A202C',
        'dashboard.progress_description_text': '#718096', 'dashboard.progress_detail_text': '#718096',
        'dashboard.progress_badge_surface': '#0F3989', 'dashboard.progress_badge_text': '#FFFFFF',
        'dashboard.progress_badge_border': 'transparent', 'dashboard.progress_track': '#E2E8F0',
        'dashboard.progress_button_surface': '#FFFFFF', 'dashboard.progress_button_text': '#2D3748',
        'dashboard.progress_button_border': '#A0AEC0', 'dashboard.progress_button_hover_surface': '#EDF2F7',
        'dashboard.progress_button_hover_text': '#1A202C', 'dashboard.progress_button_hover_border': '#A0AEC0',
        'dashboard.quick_border': '#C8D9EC', 'dashboard.quick_toggle_text': '#294866',
        'dashboard.quick_toolbar_text': '#334155', 'dashboard.quick_toolbar_border': '#CFD8E3',
        'dashboard.quick_toolbar_hover_text': '#235F98', 'dashboard.quick_toolbar_hover_border': '#9FC7E7',
        'dashboard.quick_pause_text': '#286D70', 'dashboard.quick_pause_border': '#B9DCDD',
        'dashboard.quick_pause_hover_text': '#205D60', 'dashboard.quick_pause_hover_border': '#8FC9CB',
    },
    "escuro": {
        'dashboard.recommendation_card_border': '#304157', 'dashboard.recommendation_icon_text': '#A9D3FF',
        'dashboard.recommendation_icon_border': '#365E83', 'dashboard.recommendation_title_text': '#F3F6FB',
        'dashboard.recommendation_subtitle_text': '#94A4B9', 'dashboard.recommendation_help_surface': '#132131',
        'dashboard.recommendation_help_text': '#A8C7E5', 'dashboard.recommendation_help_border': '#354A61',
        'dashboard.recommendation_help_hover_surface': '#192B40', 'dashboard.recommendation_help_hover_text': '#A8C7E5',
        'dashboard.recommendation_help_hover_border': '#4C6682', 'dashboard.recommendation_body_surface': '#162333',
        'dashboard.recommendation_body_border': '#354B62', 'dashboard.recommendation_ready_text': '#9CC9F3',
        'dashboard.recommendation_primary_text': '#FFFFFF', 'dashboard.recommendation_primary_border': '#78A7EE',
        'dashboard.recommendation_primary_hover_border': '#A3C6FF', 'dashboard.recommendation_primary_pressed_surface': '#294F91',
        'dashboard.recommendation_primary_pressed_border': '#6F9CDE', 'dashboard.recommendation_secondary_text': '#9EC7EE',
        'dashboard.recommendation_secondary_hover_text': '#D7EAFF', 'dashboard.progress_card_border': '#355461',
        'dashboard.progress_icon_text': '#8ED4D9', 'dashboard.progress_icon_surface': '#173438',
        'dashboard.progress_icon_border': '#3E6A6F', 'dashboard.progress_title_text': '#EDF3F8',
        'dashboard.progress_description_text': '#9BABBC', 'dashboard.progress_detail_text': '#8FA2B5',
        'dashboard.progress_badge_surface': 'transparent', 'dashboard.progress_badge_text': '#E9EDF5',
        'dashboard.progress_badge_border': 'transparent', 'dashboard.progress_track': '#263B50',
        'dashboard.progress_button_surface': '#162333', 'dashboard.progress_button_text': '#DCE6F0',
        'dashboard.progress_button_border': '#33475E', 'dashboard.progress_button_hover_surface': '#1C3145',
        'dashboard.progress_button_hover_text': '#9BD5FF', 'dashboard.progress_button_hover_border': '#4D89B8',
        'dashboard.quick_border': '#35516D', 'dashboard.quick_toggle_text': '#C8DBED',
        'dashboard.quick_toolbar_text': '#DCE6F0', 'dashboard.quick_toolbar_border': '#33475E',
        'dashboard.quick_toolbar_hover_text': '#9BD5FF', 'dashboard.quick_toolbar_hover_border': '#4D89B8',
        'dashboard.quick_pause_text': '#9DE0DF', 'dashboard.quick_pause_border': '#376B70',
        'dashboard.quick_pause_hover_text': '#C4F1EF', 'dashboard.quick_pause_hover_border': '#4F8E91',
    },
    "futurista": {
        'dashboard.recommendation_card_border': '#475364', 'dashboard.recommendation_icon_text': '#E5ECF3',
        'dashboard.recommendation_icon_border': '#697587', 'dashboard.recommendation_title_text': '#F3F7FB',
        'dashboard.recommendation_subtitle_text': '#B4BEC9', 'dashboard.recommendation_help_surface': '#252E3A',
        'dashboard.recommendation_help_text': '#D1D9E2', 'dashboard.recommendation_help_border': '#5E6A7C',
        'dashboard.recommendation_help_hover_surface': '#2F3947', 'dashboard.recommendation_help_hover_text': '#FFFFFF',
        'dashboard.recommendation_help_hover_border': '#7E899A', 'dashboard.recommendation_body_surface': '#202833',
        'dashboard.recommendation_body_border': '#465263', 'dashboard.recommendation_ready_text': '#C4CDD8',
        'dashboard.recommendation_primary_text': '#FFFFFF', 'dashboard.recommendation_primary_border': '#7C83FF',
        'dashboard.recommendation_primary_hover_border': '#B1B7FF', 'dashboard.recommendation_primary_pressed_surface': '#363BB8',
        'dashboard.recommendation_primary_pressed_border': '#6C73F4', 'dashboard.recommendation_secondary_text': '#CBD3DE',
        'dashboard.recommendation_secondary_hover_text': '#F4F7FB', 'dashboard.progress_card_border': '#39C39A',
        'dashboard.progress_icon_text': '#E8FFF8', 'dashboard.progress_icon_surface': '#1FFFFFFF',
        'dashboard.progress_icon_border': '#59E8FFF8', 'dashboard.progress_title_text': '#F6FFFC',
        'dashboard.progress_description_text': '#D7FFF3', 'dashboard.progress_detail_text': '#D7FFF3',
        'dashboard.progress_badge_surface': '#24FFFFFF', 'dashboard.progress_badge_text': '#F7FFFC',
        'dashboard.progress_badge_border': '#47FFFFFF', 'dashboard.progress_track': '#730C2B25',
        'dashboard.progress_button_surface': '#202833', 'dashboard.progress_button_text': '#F1F7FB',
        'dashboard.progress_button_border': '#2EFFFFFF', 'dashboard.progress_button_hover_surface': '#293341',
        'dashboard.progress_button_hover_text': '#FFFFFF', 'dashboard.progress_button_hover_border': '#52FFFFFF',
        'dashboard.quick_border': '#475364', 'dashboard.quick_toggle_text': '#A9DCF4',
        'dashboard.quick_toolbar_text': '#E7F5FF', 'dashboard.quick_toolbar_border': '#40688D',
        'dashboard.quick_toolbar_hover_text': '#C8F6FF', 'dashboard.quick_toolbar_hover_border': '#56DFFF',
        'dashboard.quick_pause_text': '#AAF7F2', 'dashboard.quick_pause_border': '#4BC2C5',
        'dashboard.quick_pause_hover_text': '#E2FFFF', 'dashboard.quick_pause_hover_border': '#72E4E5',
    },
}

EXPECTED_GRADIENTS = {
    "claro": {
        "dashboard.recommendation_card_gradient": ((0, 0, 1, 1), ((0.0, '#FFFFFF'), (1.0, '#FFFFFF'))),
        "dashboard.recommendation_icon_gradient": ((0, 0, 1, 1), ((0.0, '#F1F6FC'), (1.0, '#F1F6FC'))),
        "dashboard.recommendation_primary_gradient": ((0, 0, 1, 0), ((0.0, '#4B83C9'), (1.0, '#4B83C9'))),
        "dashboard.recommendation_primary_hover_gradient": ((0, 0, 1, 0), ((0.0, '#4278BA'), (1.0, '#4278BA'))),
        "dashboard.progress_card_gradient": ((0, 0, 1, 1), ((0.0, '#FFFFFF'), (1.0, '#FFFFFF'))),
        "dashboard.progress_fill_gradient": ((0, 0, 1, 0), ((0.0, '#0F3989'), (1.0, '#0F3989'))),
        "dashboard.quick_access_gradient": ((0, 0, 1, 0), ((0.0, '#F8FBFF'), (0.5, '#FFFFFF'), (1.0, '#F8FBFF'))),
        "dashboard.quick_toolbar_gradient": ((0, 0, 1, 1), ((0.0, '#FFFFFF'), (1.0, '#FFFFFF'))),
        "dashboard.quick_toolbar_hover_gradient": ((0, 0, 1, 1), ((0.0, '#F6FBFF'), (1.0, '#F6FBFF'))),
        "dashboard.quick_pause_gradient": ((0, 0, 1, 0), ((0.0, '#EEF8F8'), (1.0, '#EEF8F8'))),
        "dashboard.quick_pause_hover_gradient": ((0, 0, 1, 0), ((0.0, '#E0F2F2'), (1.0, '#E0F2F2'))),
    },
    "escuro": {
        "dashboard.recommendation_card_gradient": ((0, 0, 1, 1), ((0.0, '#101B29'), (1.0, '#101B29'))),
        "dashboard.recommendation_icon_gradient": ((0, 0, 1, 1), ((0.0, '#17304B'), (1.0, '#17304B'))),
        "dashboard.recommendation_primary_gradient": ((0, 0, 1, 0), ((0.0, '#315FAE'), (0.52, '#3F72C8'), (1.0, '#5488DE'))),
        "dashboard.recommendation_primary_hover_gradient": ((0, 0, 1, 0), ((0.0, '#3C6CBC'), (0.52, '#4C80D4'), (1.0, '#6297E9'))),
        "dashboard.progress_card_gradient": ((0, 0, 1, 1), ((0.0, '#172534'), (0.7, '#152432'), (1.0, '#142732'))),
        "dashboard.progress_fill_gradient": ((0, 0, 1, 0), ((0.0, '#4D83C5'), (1.0, '#4D83C5'))),
        "dashboard.quick_access_gradient": ((0, 0, 1, 0), ((0.0, '#132235'), (0.5, '#151F2D'), (1.0, '#132235'))),
        "dashboard.quick_toolbar_gradient": ((0, 0, 1, 1), ((0.0, '#162333'), (1.0, '#162333'))),
        "dashboard.quick_toolbar_hover_gradient": ((0, 0, 1, 1), ((0.0, '#1C3145'), (1.0, '#1C3145'))),
        "dashboard.quick_pause_gradient": ((0, 0, 1, 0), ((0.0, '#18333A'), (1.0, '#18333A'))),
        "dashboard.quick_pause_hover_gradient": ((0, 0, 1, 0), ((0.0, '#20454C'), (1.0, '#20454C'))),
    },
    "futurista": {
        "dashboard.recommendation_card_gradient": ((0, 0, 1, 1), ((0.0, '#202733'), (0.52, '#222A36'), (1.0, '#1D2430'))),
        "dashboard.recommendation_icon_gradient": ((0, 0, 1, 1), ((0.0, '#404957'), (1.0, '#2F3744'))),
        "dashboard.recommendation_primary_gradient": ((0, 0, 1, 0), ((0.0, '#4447E8'), (0.52, '#4347E1'), (1.0, '#3C42D2'))),
        "dashboard.recommendation_primary_hover_gradient": ((0, 0, 1, 0), ((0.0, '#5355F2'), (0.52, '#4F54EB'), (1.0, '#464DDE'))),
        "dashboard.progress_card_gradient": ((0, 0, 1, 1), ((0.0, '#14A779'), (0.55, '#13835F'), (1.0, '#16534D'))),
        "dashboard.progress_fill_gradient": ((0, 0, 1, 0), ((0.0, '#B7FFE6'), (1.0, '#F0FFF9'))),
        "dashboard.quick_access_gradient": ((0, 0, 1, 0), ((0.0, '#1F2733'), (0.5, '#212A36'), (1.0, '#1E2531'))),
        "dashboard.quick_toolbar_gradient": ((0, 0, 1, 1), ((0.0, '#162B42'), (1.0, '#0D1D30'))),
        "dashboard.quick_toolbar_hover_gradient": ((0, 0, 1, 1), ((0.0, '#1A3854'), (1.0, '#10263D'))),
        "dashboard.quick_pause_gradient": ((0, 0, 1, 0), ((0.0, '#143B43'), (1.0, '#17374F'))),
        "dashboard.quick_pause_hover_gradient": ((0, 0, 1, 0), ((0.0, '#19505A'), (1.0, '#1F4A67'))),
    },
}

BLOCK_B_QSS = {
    "claro": "9ba6faf327ad1fcc81bc73750b17c482bce8e2673a65aa6752b6ba41e915b987",
    "escuro": "7f77d8aa23eeb8e9d3bbacf5b2589f3617bbee2b0d3864e7b43ae91e6669d477",
    "futurista": "4869e85bff334d33d7af227e06cd951d31883d548bb8f90df041fedd605c8377",
}
BLOCK_C_QSS = {
    "claro": "64ea82086ca9575c727925b6e0ebae18bc45d0f760e94ca1d3bab679be16f273",
    "escuro": "d3011c1a6f28b7d89678129ab6462d6cb4b1b9ce19e2084dc1f3e52e5a6cda2c",
    "futurista": "69f5d9733fd68f2665f8f3a534cf7b2f88fc07890b309837302737809ebea488",
}
PROTECTED_HASHES = {
    "main.py": "bdb0815e71387bd87d40498bf535ef839d19a1a9086d55e0582ea50946713b45",
    "estudos.db": "034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef",
    "versao.py": "c201d237e622dd2269838e54914458fd775c7ec1a91f07b518775ee833caa439",
    "foco.py": "8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed",
    "jogos.py": "498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286",
    "checkpoint.py": "947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38",
}


def canonical_qss(qss: str) -> str:
    qss = re.sub(r"#[0-9A-Fa-f]{3,8}\b", lambda m: m.group(0).upper(), qss)
    return re.sub(r"\s+", " ", qss).strip()


def qss_hash(qss: str) -> str:
    return hashlib.sha256(canonical_qss(qss).encode("utf-8")).hexdigest()



def strip_navigation_layer(theme_name: str, qss: str) -> str:
    qss = strip_cards_global_block_a(tema, theme_name, qss)
    if theme_name == "futurista":
        final_back = render_qss("futurista", tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
        inherited_back = render_qss("escuro", tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
        if qss.endswith(final_back):
            qss = qss[:-len(final_back)]
        elif final_back in qss:
            qss = qss.replace(final_back, "", 1)
        if inherited_back in qss:
            qss = qss.replace(inherited_back, "", 1)
    else:
        back_layer = render_qss(theme_name, tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
        if qss.endswith(back_layer):
            qss = qss[:-len(back_layer)]
        elif back_layer in qss:
            qss = qss.replace(back_layer, "", 1)
    if theme_name == "futurista":
        final = render_qss("futurista", tema.ESTILO_NAVEGACAO_BUSCA_GLOBAL)
        inherited = render_qss("escuro", tema.ESTILO_NAVEGACAO_BUSCA_GLOBAL)
        if qss.endswith(final):
            qss = qss[:-len(final)]
        if inherited in qss:
            qss = qss.replace(inherited, "", 1)
        return qss
    layer = render_qss(theme_name, tema.ESTILO_NAVEGACAO_BUSCA_GLOBAL)
    if qss.endswith(layer):
        return qss[:-len(layer)]
    return qss.replace(layer, "", 1)


def strip_block_f(theme_name: str, qss: str) -> str:
    qss = strip_navigation_layer(theme_name, qss)
    # Bloco H é posterior ao checkpoint G/F; retire-o primeiro.
    if theme_name == "futurista":
        final_h = render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_H)
        inherited_h = render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_H)
        if qss.endswith(final_h):
            qss = qss[:-len(final_h)]
        qss = qss.replace(inherited_h, "", 1)
    else:
        layer_h = render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_H)
        if qss.endswith(layer_h):
            qss = qss[:-len(layer_h)]
    # Bloco G é posterior ao checkpoint F; retire-o primeiro.
    if theme_name == "futurista":
        final_g = render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_G)
        inherited_g = render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_G)
        if qss.endswith(final_g):
            qss = qss[:-len(final_g)]
        qss = qss.replace(inherited_g, "", 1)
    else:
        layer_g = render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_G)
        if qss.endswith(layer_g):
            qss = qss[:-len(layer_g)]
    if theme_name == "futurista":
        final = render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_F)
        inherited = render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_F)
        if not qss.endswith(final):
            raise AssertionError("camada F futurista não é a última")
        qss = qss[:-len(final)]
        return qss.replace(inherited, "", 1)
    layer = render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_F)
    if not qss.endswith(layer):
        raise AssertionError(f"camada F não é a última em {theme_name}")
    return qss[:-len(layer)]

def strip_block_e(theme_name: str, qss: str) -> str:
    qss = strip_block_f(theme_name, qss)
    if theme_name == "futurista":
        final = render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_E)
        inherited = render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_E)
        if not qss.endswith(final):
            raise AssertionError("camada E futurista não é a última")
        qss = qss[:-len(final)]
        return qss.replace(inherited, "", 1)
    layer = render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_E)
    if not qss.endswith(layer):
        raise AssertionError(f"camada E não é a última em {theme_name}")
    return qss[:-len(layer)]

def strip_block_d(theme_name: str, qss: str) -> str:
    qss = strip_block_e(theme_name, qss)
    if theme_name == "futurista":
        final = render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_D)
        inherited = render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_D)
        if not qss.endswith(final):
            raise AssertionError("camada D futurista não é a última")
        qss = qss[:-len(final)]
        return qss.replace(inherited, "", 1)
    layer = render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_D)
    if not qss.endswith(layer):
        raise AssertionError(f"camada D não é a última em {theme_name}")
    return qss[:-len(layer)]


def strip_block_c(theme_name: str, qss: str) -> str:
    qss = strip_block_d(theme_name, qss)
    if theme_name == "futurista":
        final = render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_C)
        inherited = render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_C)
        if not qss.endswith(final):
            raise AssertionError("camada C futurista não é a última")
        qss = qss[:-len(final)]
        return qss.replace(inherited, "", 1)
    layer = render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_C)
    if not qss.endswith(layer):
        raise AssertionError(f"camada C não é a última em {theme_name}")
    return qss[:-len(layer)]


class DashboardBlockCDesignSystemTests(unittest.TestCase):
    def test_orcamento_de_tokens_exato(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 928)
        self.assertEqual(len(ALL_TOKENS), 1030)
        self.assertEqual(len(COLOR_TOKENS), 48)
        self.assertEqual(len(GRADIENT_TOKENS), 11)
        self.assertEqual(len(BLOCK_C_TOKENS), 59)
        paths = {token.path for token in ALL_TOKENS}
        self.assertTrue(BLOCK_C_TOKENS <= paths)
        for path in COLOR_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.COLOR)
        for path in GRADIENT_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.GRADIENT)

    def test_tokens_reproduzem_a_caracterizacao_nos_tres_temas(self):
        for theme_name, expected in EXPECTED_COLORS.items():
            theme = get_theme(theme_name)
            for path, value in expected.items():
                with self.subTest(theme=theme_name, path=path):
                    self.assertEqual(theme.color(path).value, value)
            for path, (direction, stops) in EXPECTED_GRADIENTS[theme_name].items():
                gradient = theme.gradient(path)
                actual_direction = (gradient.direction.x1, gradient.direction.y1, gradient.direction.x2, gradient.direction.y2)
                actual_stops = tuple((stop.position, stop.color.value) for stop in gradient.stops)
                self.assertEqual(actual_direction, direction, (theme_name, path))
                self.assertEqual(actual_stops, stops, (theme_name, path))

    def test_qss_do_bloco_c_e_tokenizado_estritamente_escopado(self):
        source = tema.ESTILO_DASHBOARD_BLOCO_C
        self.assertIsNone(re.search(r"#[0-9A-Fa-f]{6,8}\b", source))
        self.assertNotIn("QPainter", source)
        self.assertIn('focusQuickCard[cardRole="progress"]', source)
        self.assertIn('dashboardQuickAccess[embedded="false"]', source)
        self.assertNotIn('dashboardQuickAccess[embedded="true"]', source)
        self.assertIn("dashboardTodayAction", source)
        self.assertNotIn("dashboardOverviewCard", source)
        self.assertNotIn("dashboardInsightSummary", source)
        self.assertNotIn("focusDashboardMainCard", source)
        self.assertNotIn("DashboardPlanningArcWidget", source)
        self.assertNotIn("DashboardDonutWidget", source)
        allowed_ids = {
            "dashboardRoot", "dashboardTodayAction", "algorithmDashboardIcon", "algorithmDashboardTitle",
            "algorithmDashboardSubtitle", "algorithmDashboardHelp", "algorithmRecommendationBody",
            "algorithmDashboardReady", "dashboardTodayPrimaryButton", "dashboardTodayButton", "focusQuickCard",
            "focusQuickIcon", "focusDashboardCardTitle", "focusDashboardDescription", "focusDashboardDetail",
            "focusQuickHint", "dashboardProgressBadge", "dashboardTodayProgress", "subtleButton",
            "dashboardQuickAccess", "dashboardSectionToggle", "toolbarButton", "pauseNavButton",
        }
        ids = set(re.findall(r"#([A-Za-z_][A-Za-z0-9_]*)", source))
        self.assertEqual(ids - allowed_ids, set())
        for selector in re.findall(r"([^{}]+)\{", source):
            if selector.strip().startswith("Q"):
                self.assertIn("#dashboardRoot", selector)

    def test_action_role_dinamico_permanece_sem_nova_variacao_visual(self):
        source = tema.ESTILO_DASHBOARD_BLOCO_C
        self.assertNotIn('[actionRole=', source)
        self.assertIn('setProperty("actionRole", "neutral")', MAIN_SOURCE)
        self.assertIn('setProperty("actionRole", action_role)', MAIN_SOURCE)
        self.assertIn('setProperty("simpleHero", True)', MAIN_SOURCE)
        self.assertIn('setProperty("heroCentral", True)', MAIN_SOURCE)

    def test_renderizacao_tem_hash_novo_e_sem_marcadores(self):
        for theme_name in ("claro", "escuro", "futurista"):
            qss = getattr(tema, f"stylesheet_{theme_name}")()
            self.assertNotIn("{{color:", qss)
            self.assertNotIn("{{gradient:", qss)
            self.assertEqual(qss_hash(strip_block_d(theme_name, qss)), BLOCK_C_QSS[theme_name])

    def test_remover_bloco_c_recupera_exatamente_checkpoint_b(self):
        for theme_name in ("claro", "escuro", "futurista"):
            qss = getattr(tema, f"stylesheet_{theme_name}")()
            self.assertEqual(qss_hash(strip_block_c(theme_name, qss)), BLOCK_B_QSS[theme_name])

    def test_hierarquia_alvo_continua_no_mesmo_codigo(self):
        for marker in (
            'progresso_card.setObjectName("focusQuickCard")',
            'progresso_card.setProperty("cardRole", "progress")',
            'self.dashboard_progress_badge.setObjectName("dashboardProgressBadge")',
            'self.dashboard_progress_barra.setObjectName("dashboardTodayProgress")',
            'atalhos_rapidos.setObjectName("dashboardQuickAccess")',
            'atalhos_rapidos.setProperty("embedded", False)',
            'self.dashboard_botao_pausa.setObjectName("pauseNavButton")',
            'self.dashboard_hoje_acao.setObjectName("dashboardTodayAction")',
            'algoritmo_icone.setObjectName("algorithmDashboardIcon")',
            'algoritmo_titulo.setObjectName("algorithmDashboardTitle")',
            'self.dashboard_hoje_acao_ajuda.setObjectName("algorithmDashboardHelp")',
            'inteligencia_conteudo.setObjectName("algorithmRecommendationBody")',
            'self.dashboard_algoritmo_pronto.setObjectName("algorithmDashboardReady")',
            'self.dashboard_hoje_um_clique.setObjectName("dashboardTodayPrimaryButton")',
            'self.dashboard_hoje_botao.setObjectName("dashboardTodayButton")',
        ):
            self.assertIn(marker, MAIN_SOURCE)

    def test_arquivos_protegidos_permanecem_byte_a_byte(self):
        for name, expected in PROTECTED_HASHES.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected)

    def test_metadata_permanece_inalterada(self):
        self.assertEqual(VIGHNA_VERSION, "0.29.59")
        self.assertEqual(VIGHNA_BUILD, "updates-center-v1")
        self.assertEqual(VIGHNA_SCHEMA, 25)


if __name__ == "__main__":
    unittest.main()
