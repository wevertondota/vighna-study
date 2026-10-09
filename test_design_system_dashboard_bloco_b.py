"""Regressões do Design System — Dashboard, Bloco B: Foco + Planejamento de hoje."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest
from _design_system_test_helpers import strip_cards_global_block_a

import tema
from ui.design import ALL_TOKENS, COMPONENT_TOKEN_COUNT, SEMANTIC_TOKEN_COUNT, TokenKind, get_theme, render_qss, token_spec
from versao import VIGHNA_BUILD, VIGHNA_SCHEMA, VIGHNA_VERSION

ROOT = Path(__file__).resolve().parent
TEMA_SOURCE = (ROOT / "tema.py").read_text(encoding="utf-8")
MAIN_SOURCE = (ROOT / "main.py").read_text(encoding="utf-8")

COLOR_TOKENS = {
    'dashboard.focus_panel_surface',
    'dashboard.focus_panel_border',
    'dashboard.focus_card_border',
    'dashboard.focus_icon_text',
    'dashboard.focus_icon_surface',
    'dashboard.focus_icon_border',
    'dashboard.focus_title_text',
    'dashboard.focus_badge_text',
    'dashboard.focus_badge_surface',
    'dashboard.focus_badge_border',
    'dashboard.focus_description_text',
    'dashboard.focus_detail_text',
    'dashboard.focus_caption_text',
    'dashboard.focus_value_text',
    'dashboard.focus_goal_surface',
    'dashboard.focus_goal_border',
    'dashboard.focus_goal_title_text',
    'dashboard.focus_progress_track',
    'dashboard.focus_progress_border',
    'dashboard.focus_progress_fill',
    'dashboard.focus_action_text',
    'dashboard.focus_action_border',
    'dashboard.focus_action_hover_border',
    'dashboard.focus_action_pressed_surface',
    'dashboard.focus_action_pressed_border',
    'dashboard.planning_card_border',
    'dashboard.planning_icon_text',
    'dashboard.planning_icon_surface',
    'dashboard.planning_icon_border',
    'dashboard.planning_title_text',
    'dashboard.planning_date_text',
    'dashboard.planning_hero_title_text',
    'dashboard.planning_hero_value_text',
    'dashboard.planning_hero_detail_text',
    'dashboard.planning_progress_track',
    'dashboard.planning_operational_surface',
    'dashboard.planning_operational_border',
    'dashboard.planning_row_title_text',
    'dashboard.planning_operational_value_text',
    'dashboard.planning_row_detail_text',
    'dashboard.planning_divider',
    'dashboard.planning_week_label_text',
    'dashboard.planning_status_surface',
    'dashboard.planning_status_text',
    'dashboard.planning_status_border',
    'dashboard.planning_status_done_surface',
    'dashboard.planning_status_done_text',
    'dashboard.planning_status_done_border',
    'dashboard.planning_status_attention_surface',
    'dashboard.planning_status_attention_text',
    'dashboard.planning_status_attention_border',
    'dashboard.planning_status_active_surface',
    'dashboard.planning_status_active_text',
    'dashboard.planning_status_active_border',
    'dashboard.planning_button_surface',
    'dashboard.planning_button_text',
    'dashboard.planning_button_border',
    'dashboard.planning_button_hover_surface',
    'dashboard.planning_button_hover_text',
    'dashboard.planning_button_hover_border',
}

GRADIENT_TOKENS = {
    'dashboard.focus_card_gradient',
    'dashboard.focus_action_gradient',
    'dashboard.focus_action_hover_gradient',
    'dashboard.planning_card_gradient',
    'dashboard.planning_progress_gradient',
}

BLOCK_B_TOKENS = COLOR_TOKENS | GRADIENT_TOKENS

EXPECTED_LIGHT = {'dashboard.focus_panel_surface': '#FFFFFF',
 'dashboard.focus_panel_border': '#E2E8F0',
 'dashboard.focus_card_border': '#E2E8F0',
 'dashboard.focus_icon_text': '#347F91',
 'dashboard.focus_icon_surface': '#F1FAFB',
 'dashboard.focus_icon_border': '#CFE8EC',
 'dashboard.focus_title_text': '#1A202C',
 'dashboard.focus_badge_text': '#34798A',
 'dashboard.focus_badge_surface': '#F1FAFB',
 'dashboard.focus_badge_border': '#CFE8EC',
 'dashboard.focus_description_text': '#718096',
 'dashboard.focus_detail_text': '#718096',
 'dashboard.focus_caption_text': '#718096',
 'dashboard.focus_value_text': '#1A202C',
 'dashboard.focus_goal_surface': '#FFFFFF',
 'dashboard.focus_goal_border': '#E2E8F0',
 'dashboard.focus_goal_title_text': '#1A202C',
 'dashboard.focus_progress_track': '#E2E8F0',
 'dashboard.focus_progress_border': 'transparent',
 'dashboard.focus_progress_fill': '#0F3989',
 'dashboard.focus_action_text': '#FFFFFF',
 'dashboard.focus_action_border': '#0F3989',
 'dashboard.focus_action_hover_border': '#1A4BA8',
 'dashboard.focus_action_pressed_surface': '#0A3266',
 'dashboard.focus_action_pressed_border': '#0A3266',
 'dashboard.planning_card_border': '#DCE4ED',
 'dashboard.planning_icon_text': '#377DB4',
 'dashboard.planning_icon_surface': '#EFF7FE',
 'dashboard.planning_icon_border': '#D4E8F7',
 'dashboard.planning_title_text': '#18263A',
 'dashboard.planning_date_text': '#7C899B',
 'dashboard.planning_hero_title_text': '#4E6A86',
 'dashboard.planning_hero_value_text': '#0F3989',
 'dashboard.planning_hero_detail_text': '#66788C',
 'dashboard.planning_progress_track': '#E8EDF3',
 'dashboard.planning_operational_surface': '#FAFCFE',
 'dashboard.planning_operational_border': '#E3EAF2',
 'dashboard.planning_row_title_text': '#24344A',
 'dashboard.planning_operational_value_text': '#183A6B',
 'dashboard.planning_row_detail_text': '#8490A1',
 'dashboard.planning_divider': '#DCE4ED',
 'dashboard.planning_week_label_text': '#6F8092',
 'dashboard.planning_status_surface': '#F1F5F9',
 'dashboard.planning_status_text': '#475569',
 'dashboard.planning_status_border': '#E2E8F0',
 'dashboard.planning_status_done_surface': '#EAF6EE',
 'dashboard.planning_status_done_text': '#15803D',
 'dashboard.planning_status_done_border': '#BBF7D0',
 'dashboard.planning_status_attention_surface': '#FFF4DA',
 'dashboard.planning_status_attention_text': '#C2410C',
 'dashboard.planning_status_attention_border': '#FED7AA',
 'dashboard.planning_status_active_surface': '#F1F5F9',
 'dashboard.planning_status_active_text': '#475569',
 'dashboard.planning_status_active_border': '#E2E8F0',
 'dashboard.planning_button_surface': '#FFFFFF',
 'dashboard.planning_button_text': '#326FD3',
 'dashboard.planning_button_border': '#A9C2E8',
 'dashboard.planning_button_hover_surface': '#EEF5FF',
 'dashboard.planning_button_hover_text': '#285FB5',
 'dashboard.planning_button_hover_border': '#7FA8E8'}

EXPECTED_DARK = {'dashboard.focus_panel_surface': '#151F2D',
 'dashboard.focus_panel_border': '#304357',
 'dashboard.focus_card_border': '#66434D',
 'dashboard.focus_icon_text': '#FF9CAB',
 'dashboard.focus_icon_surface': '#37242B',
 'dashboard.focus_icon_border': '#774854',
 'dashboard.focus_title_text': '#EDF3F8',
 'dashboard.focus_badge_text': '#F0B0BA',
 'dashboard.focus_badge_surface': '#3A272E',
 'dashboard.focus_badge_border': '#714752',
 'dashboard.focus_description_text': '#9BABBC',
 'dashboard.focus_detail_text': '#8FA2B5',
 'dashboard.focus_caption_text': '#B99AA3',
 'dashboard.focus_value_text': '#FF90A1',
 'dashboard.focus_goal_surface': '#182331',
 'dashboard.focus_goal_border': '#30465A',
 'dashboard.focus_goal_title_text': '#A3B7CA',
 'dashboard.focus_progress_track': '#263B50',
 'dashboard.focus_progress_border': 'transparent',
 'dashboard.focus_progress_fill': '#4D83C5',
 'dashboard.focus_action_text': '#FFFFFF',
 'dashboard.focus_action_border': '#D35A68',
 'dashboard.focus_action_hover_border': '#E36F7A',
 'dashboard.focus_action_pressed_surface': '#BA3A4A',
 'dashboard.focus_action_pressed_border': '#E36F7A',
 'dashboard.planning_card_border': '#354B62',
 'dashboard.planning_icon_text': '#E5E7EB',
 'dashboard.planning_icon_surface': 'transparent',
 'dashboard.planning_icon_border': 'transparent',
 'dashboard.planning_title_text': '#F1F6FB',
 'dashboard.planning_date_text': '#9FB1C3',
 'dashboard.planning_hero_title_text': '#9FB1C3',
 'dashboard.planning_hero_value_text': '#F1F6FB',
 'dashboard.planning_hero_detail_text': '#9FB1C3',
 'dashboard.planning_progress_track': '#263A4D',
 'dashboard.planning_operational_surface': '#1B2C3E',
 'dashboard.planning_operational_border': '#3A536B',
 'dashboard.planning_row_title_text': '#F1F6FB',
 'dashboard.planning_operational_value_text': '#F1F6FB',
 'dashboard.planning_row_detail_text': '#9FB1C3',
 'dashboard.planning_divider': '#3A536B',
 'dashboard.planning_week_label_text': '#9FB1C3',
 'dashboard.planning_status_surface': '#202D3C',
 'dashboard.planning_status_text': '#CBD5E1',
 'dashboard.planning_status_border': '#334155',
 'dashboard.planning_status_done_surface': '#21372D',
 'dashboard.planning_status_done_text': '#86EFAC',
 'dashboard.planning_status_done_border': '#166534',
 'dashboard.planning_status_attention_surface': '#432827',
 'dashboard.planning_status_attention_text': '#FDBA74',
 'dashboard.planning_status_attention_border': '#9A3412',
 'dashboard.planning_status_active_surface': '#202D3C',
 'dashboard.planning_status_active_text': '#CBD5E1',
 'dashboard.planning_status_active_border': '#334155',
 'dashboard.planning_button_surface': '#142131',
 'dashboard.planning_button_text': '#A8CDFD',
 'dashboard.planning_button_border': '#476B9F',
 'dashboard.planning_button_hover_surface': '#1B2F47',
 'dashboard.planning_button_hover_text': '#E3F0FF',
 'dashboard.planning_button_hover_border': '#6493D4'}

EXPECTED_FUTURISTIC = {'dashboard.focus_panel_surface': '#151F2D',
 'dashboard.focus_panel_border': '#304357',
 'dashboard.focus_card_border': '#4B5667',
 'dashboard.focus_icon_text': '#F6A9B5',
 'dashboard.focus_icon_surface': '#3B2A33',
 'dashboard.focus_icon_border': '#8E6271',
 'dashboard.focus_title_text': '#F4F7FB',
 'dashboard.focus_badge_text': '#FFC5CF',
 'dashboard.focus_badge_surface': '#E454323B',
 'dashboard.focus_badge_border': '#976874',
 'dashboard.focus_description_text': '#C2CAD4',
 'dashboard.focus_detail_text': '#BAC4CF',
 'dashboard.focus_caption_text': '#D2AAB3',
 'dashboard.focus_value_text': '#F6AAB5',
 'dashboard.focus_goal_surface': '#212935',
 'dashboard.focus_goal_border': '#475365',
 'dashboard.focus_goal_title_text': '#8FC4DF',
 'dashboard.focus_progress_track': '#18364C',
 'dashboard.focus_progress_border': '#2E5C78',
 'dashboard.focus_progress_fill': '#55A7D5',
 'dashboard.focus_action_text': '#FFFFFF',
 'dashboard.focus_action_border': '#7C83FF',
 'dashboard.focus_action_hover_border': '#AAB1FF',
 'dashboard.focus_action_pressed_surface': '#363BB8',
 'dashboard.focus_action_pressed_border': '#6C73F4',
 'dashboard.planning_card_border': '#475364',
 'dashboard.planning_icon_text': '#E5ECF3',
 'dashboard.planning_icon_surface': '#39414D',
 'dashboard.planning_icon_border': '#697587',
 'dashboard.planning_title_text': '#F3F7FB',
 'dashboard.planning_date_text': '#B8C1CD',
 'dashboard.planning_hero_title_text': '#D7DEE7',
 'dashboard.planning_hero_value_text': '#F8FAFC',
 'dashboard.planning_hero_detail_text': '#C3CBD5',
 'dashboard.planning_progress_track': '#3B424F',
 'dashboard.planning_operational_surface': 'transparent',
 'dashboard.planning_operational_border': 'transparent',
 'dashboard.planning_row_title_text': '#EFF4F9',
 'dashboard.planning_operational_value_text': '#F9FBFC',
 'dashboard.planning_row_detail_text': '#C0C8D2',
 'dashboard.planning_divider': '#47BFC9D6',
 'dashboard.planning_week_label_text': '#C8D0DA',
 'dashboard.planning_status_surface': '#3E4654',
 'dashboard.planning_status_text': '#E7EDF3',
 'dashboard.planning_status_border': '#616C7A',
 'dashboard.planning_status_done_surface': '#305345',
 'dashboard.planning_status_done_text': '#D2FFE7',
 'dashboard.planning_status_done_border': '#58A07A',
 'dashboard.planning_status_attention_surface': '#5A402D',
 'dashboard.planning_status_attention_text': '#FFE2C0',
 'dashboard.planning_status_attention_border': '#D39A64',
 'dashboard.planning_status_active_surface': '#46506A',
 'dashboard.planning_status_active_text': '#E6EBFF',
 'dashboard.planning_status_active_border': '#707AA0',
 'dashboard.planning_button_surface': '#202833',
 'dashboard.planning_button_text': '#E0E7EF',
 'dashboard.planning_button_border': '#596474',
 'dashboard.planning_button_hover_surface': '#293341',
 'dashboard.planning_button_hover_text': '#FFFFFF',
 'dashboard.planning_button_hover_border': '#7B8698'}

EXPECTED_COLORS = {"claro": EXPECTED_LIGHT, "escuro": EXPECTED_DARK, "futurista": EXPECTED_FUTURISTIC}

EXPECTED_GRADIENTS = {
    "claro": {
        "dashboard.focus_card_gradient": ((0.0, 0.0, 1.0, 1.0), ((0.0, "#FFFFFF"), (1.0, "#FFFFFF"))),
        "dashboard.focus_action_gradient": ((0.0, 0.0, 1.0, 0.0), ((0.0, "#0F3989"), (1.0, "#0F3989"))),
        "dashboard.focus_action_hover_gradient": ((0.0, 0.0, 1.0, 0.0), ((0.0, "#1A4BA8"), (1.0, "#1A4BA8"))),
        "dashboard.planning_card_gradient": ((0.0, 0.0, 1.0, 1.0), ((0.0, "#FFFFFF"), (1.0, "#FFFFFF"))),
        "dashboard.planning_progress_gradient": ((0.0, 0.0, 1.0, 0.0), ((0.0, "#2F73C9"), (1.0, "#2F73C9"))),
    },
    "escuro": {
        "dashboard.focus_card_gradient": ((0.0, 0.0, 1.0, 1.0), ((0.0, "#241D25"), (0.7, "#281F26"), (1.0, "#2B2027"))),
        "dashboard.focus_action_gradient": ((0.0, 0.0, 1.0, 0.0), ((0.0, "#A92F40"), (1.0, "#C84958"))),
        "dashboard.focus_action_hover_gradient": ((0.0, 0.0, 1.0, 0.0), ((0.0, "#BA3A4A"), (1.0, "#D85866"))),
        "dashboard.planning_card_gradient": ((0.0, 0.0, 1.0, 1.0), ((0.0, "#162333"), (1.0, "#162333"))),
        "dashboard.planning_progress_gradient": ((0.0, 0.0, 1.0, 0.0), ((0.0, "#4C7FD1"), (1.0, "#4C7FD1"))),
    },
    "futurista": {
        "dashboard.focus_card_gradient": ((0.0, 0.0, 1.0, 1.0), ((0.0, "#232A36"), (0.6, "#242B37"), (1.0, "#202733"))),
        "dashboard.focus_action_gradient": ((0.0, 0.0, 1.0, 0.0), ((0.0, "#4447E8"), (1.0, "#3B40D4"))),
        "dashboard.focus_action_hover_gradient": ((0.0, 0.0, 1.0, 0.0), ((0.0, "#5254F3"), (1.0, "#484DE0"))),
        "dashboard.planning_card_gradient": ((0.0, 0.0, 1.0, 1.0), ((0.0, "#202733"), (0.52, "#222A36"), (1.0, "#1D2430"))),
        "dashboard.planning_progress_gradient": ((0.0, 0.0, 1.0, 0.0), ((0.0, "#B9FFE3"), (1.0, "#D5FFF0"))),
    },
}

BLOCK_A_QSS = {
    "claro": "f9dfec4dd2238a1955f9760f12b9df93adcf3eb32cd8ff457cb5d4a7b1cf2c14",
    "escuro": "b16a2d1643a53053b00c804fc6685a2e534836c217bee334986fdeeba016f70a",
    "futurista": "43e42f04862522996eb52351beb104570230e7283c8a8e7cbd389742fd5dee18",
}
BLOCK_B_QSS = {
    "claro": "9192b93101c8fe71a8fee1887c004a7a42bf9f7b622acfd383ef10fe94c5a51e",
    "escuro": "def70b0b7fca2306396e1740589f391fed66ddb362b373aae672617c9daa52b7",
    "futurista": "1169daa1f505ed0dcad24d0dd10ee8729536c2c4d6720f2a2cbecf929a6c4cbc",
}
PROTECTED_HASHES = {
    "main.py": "d2e4ebd54ae765ec8f11eabd5e6c6e086e3dfd7bb3d441def8c03705515da4fe",
    "versao.py": "49e9d1b5c82bc10c70bd79ca5f494961e3cae3553cd4b70af1565bca661f9ac2",
    "foco.py": "8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed",
    "jogos.py": "498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286",
    "checkpoint.py": "947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38",
}

def canonical_qss(qss: str) -> str:
    qss = re.sub(r"#[0-9A-Fa-f]{3,8}\b", lambda m: m.group(0).upper(), qss)
    return re.sub(r"\s+", " ", qss).strip()

def qss_hash(qss: str) -> str:
    return hashlib.sha256(canonical_qss(qss).encode("utf-8")).hexdigest()

def constant_source(name: str) -> str:
    match = re.search(rf'{name}\s*=\s*r"""(.*?)"""', TEMA_SOURCE, re.S)
    if not match:
        raise AssertionError(name)
    return match.group(1)


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
            raise AssertionError("camada futurista C não é a última")
        qss = qss[:-len(final)]
        return qss.replace(inherited, "", 1)
    layer = render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_C)
    if not qss.endswith(layer):
        raise AssertionError(f"camada C não é a última em {theme_name}")
    return qss[:-len(layer)]


def strip_block_b(theme_name: str, qss: str) -> str:
    qss = strip_block_c(theme_name, qss)
    if theme_name == "futurista":
        final = render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_B_FUTURISTA)
        inherited = render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_B_ESCURO)
        if not qss.endswith(final):
            raise AssertionError("camada futurista B não é a última")
        qss = qss[:-len(final)]
        return qss.replace(inherited, "", 1)
    constant = tema.ESTILO_DASHBOARD_BLOCO_B_CLARO if theme_name == "claro" else tema.ESTILO_DASHBOARD_BLOCO_B_ESCURO
    layer = render_qss(theme_name, constant)
    if not qss.endswith(layer):
        raise AssertionError(f"camada B não é a última em {theme_name}")
    return qss[:-len(layer)]

class DashboardBlockBDesignSystemTests(unittest.TestCase):
    def test_orcamento_de_tokens_exato(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 1148)
        self.assertEqual(len(ALL_TOKENS), 1250)
        self.assertEqual(len(COLOR_TOKENS), 60)
        self.assertEqual(len(GRADIENT_TOKENS), 5)
        self.assertEqual(len(BLOCK_B_TOKENS), 65)
        paths = {token.path for token in ALL_TOKENS}
        self.assertTrue(BLOCK_B_TOKENS <= paths)
        for path in COLOR_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.COLOR)
        for path in GRADIENT_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.GRADIENT)

    def test_tokens_reproduzem_caracterizacao_nos_tres_temas(self):
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

    def test_qss_do_bloco_b_e_tokenizado_escopado_e_nao_toca_qpainter(self):
        allowed_ids = {
            "dashboardRoot", "dashboardFocusPanel", "focusDashboardMainCard", "focusDashboardCardIcon",
            "focusDashboardCardTitle", "focusDashboardBadge", "focusDashboardDescription", "focusDashboardDetail",
            "focusQuickHint", "focusDashboardCaption", "dashboardTodayFocusValue", "dashboardQuickAccess",
            "dashboardQuickAccessTitle", "dashboardTodayProgress", "dashboardFocusPrimaryButton",
            "dashboardInsightSummary", "dashboardInsightSummaryIcon", "dashboardInsightSummaryTitle",
            "dashboardInsightSummaryDate", "dashboardPlanningHeroTitle", "dashboardPlanningHeroValue",
            "dashboardPlanningHeroDetail", "dashboardInsightSummaryProgress", "dashboardPlanningOperational",
            "dashboardInsightSummaryRowTitle", "dashboardPlanningOperationalValue", "dashboardInsightSummaryRowDetail",
            "dashboardPlanningDivider", "dashboardPlanningWeekLabel", "weeklyGoalStatus", "planningSummaryButton",
        }
        for constant_name in (
            "ESTILO_DASHBOARD_BLOCO_B_CLARO", "ESTILO_DASHBOARD_BLOCO_B_ESCURO", "ESTILO_DASHBOARD_BLOCO_B_FUTURISTA"
        ):
            source = constant_source(constant_name)
            with self.subTest(constant=constant_name):
                self.assertIsNone(re.search(r"#[0-9A-Fa-f]{6,8}\b", source))
                self.assertNotIn("QPainter", source)
                self.assertNotIn('focusQuickCard[cardRole="progress"]', source)
                self.assertNotIn("algorithmRecommendationBody", source)
                self.assertNotIn("dashboardOverviewCard", source)
                self.assertEqual(set(re.findall(r"#([A-Za-z_][A-Za-z0-9_]*)", source)) - allowed_ids, set())
                selectors = [line.strip() for line in source.splitlines() if line.strip().endswith("{") and line.lstrip().startswith("Q")]
                self.assertTrue(selectors)
                for selector in selectors:
                    self.assertIn("#dashboardRoot", selector)

    def test_renderizacao_tem_hash_novo_e_sem_marcadores(self):
        for theme_name in ("claro", "escuro", "futurista"):
            qss = getattr(tema, f"stylesheet_{theme_name}")()
            self.assertNotIn("{{color:", qss)
            self.assertNotIn("{{gradient:", qss)
            self.assertEqual(qss_hash(strip_block_c(theme_name, qss)), BLOCK_B_QSS[theme_name])

    def test_remocao_da_camadas_b_recupera_exatamente_o_checkpoint_a(self):
        for theme_name in ("claro", "escuro", "futurista"):
            qss = getattr(tema, f"stylesheet_{theme_name}")()
            self.assertEqual(qss_hash(strip_block_b(theme_name, qss)), BLOCK_A_QSS[theme_name])

    def test_hierarquia_e_qpainter_continuam_no_mesmo_codigo(self):
        for marker in (
            'self.dashboard_hoje_painel = QFrame()',
            '"dashboardFocusPanel"',
            'foco_hoje = QFrame()',
            '"focusDashboardMainCard"',
            'self.dashboard_resumo_ia = QFrame()',
            'self.dashboard_resumo_ia.setObjectName("dashboardInsightSummary")',
            'self.dashboard_planejamento_meta_gauge = DashboardPlanningArcWidget()',
            'foco_objetivo_box.setProperty("embedded", True)',
        ):
            self.assertIn(marker, MAIN_SOURCE)

    def test_arquivos_protegidos_permanecem_byte_a_byte(self):
        for name, expected in PROTECTED_HASHES.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected)

    def test_metadata_permanece_inalterada(self):
        self.assertEqual(VIGHNA_VERSION, "0.29.59")
        self.assertEqual(VIGHNA_BUILD, "statistics-my-evolution-tokens-v1")
        self.assertEqual(VIGHNA_SCHEMA, 25)

if __name__ == "__main__":
    unittest.main()
