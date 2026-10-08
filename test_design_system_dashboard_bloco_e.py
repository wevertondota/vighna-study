"""Regressões do Design System — Dashboard, Bloco E: Notificações e alertas."""
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
MAIN_SOURCE = (ROOT / "main.py").read_text(encoding="utf-8")

COLOR_TOKENS = set(['dashboard.notifications_panel_surface',
 'dashboard.notifications_panel_border',
 'dashboard.notifications_toggle_text',
 'dashboard.notifications_toggle_hover_surface',
 'dashboard.notifications_subtitle_text',
 'dashboard.attention_priority_surface',
 'dashboard.attention_priority_border',
 'dashboard.attention_priority_ok_surface',
 'dashboard.attention_priority_ok_border',
 'dashboard.attention_priority_critical_surface',
 'dashboard.attention_priority_critical_border',
 'dashboard.attention_priority_icon_surface',
 'dashboard.attention_priority_icon_text',
 'dashboard.attention_priority_icon_border',
 'dashboard.attention_priority_icon_ok_surface',
 'dashboard.attention_priority_icon_ok_text',
 'dashboard.attention_priority_icon_ok_border',
 'dashboard.attention_priority_icon_critical_surface',
 'dashboard.attention_priority_icon_critical_text',
 'dashboard.attention_priority_icon_critical_border',
 'dashboard.attention_eyebrow_text',
 'dashboard.attention_title_text',
 'dashboard.attention_description_text',
 'dashboard.attention_meta_text',
 'dashboard.attention_badge_surface',
 'dashboard.attention_badge_text',
 'dashboard.attention_badge_border',
 'dashboard.attention_badge_ok_surface',
 'dashboard.attention_badge_ok_text',
 'dashboard.attention_badge_ok_border',
 'dashboard.attention_badge_critical_surface',
 'dashboard.attention_badge_critical_text',
 'dashboard.attention_badge_critical_border',
 'dashboard.attention_action_surface',
 'dashboard.attention_action_text',
 'dashboard.attention_action_border',
 'dashboard.attention_action_hover_surface',
 'dashboard.attention_action_hover_text',
 'dashboard.attention_action_hover_border',
 'dashboard.attention_action_disabled_surface',
 'dashboard.attention_action_disabled_text',
 'dashboard.attention_action_disabled_border',
 'dashboard.attention_pace_surface',
 'dashboard.attention_pace_border',
 'dashboard.attention_pace_icon_surface',
 'dashboard.attention_pace_icon_text',
 'dashboard.attention_pace_icon_border',
 'dashboard.attention_pace_badge_surface',
 'dashboard.attention_pace_badge_text',
 'dashboard.attention_pace_badge_border',
 'dashboard.attention_forecast_action_surface',
 'dashboard.attention_forecast_action_text',
 'dashboard.attention_forecast_action_border',
 'dashboard.attention_forecast_action_hover_surface',
 'dashboard.attention_forecast_action_hover_text',
 'dashboard.attention_forecast_action_hover_border',
 'dashboard.attention_forecast_action_disabled_border',
 'dashboard.attention_footer_surface',
 'dashboard.attention_footer_border',
 'dashboard.attention_footer_item_text',
 'dashboard.attention_footer_hint_text'])
BLOCK_E_TOKENS = COLOR_TOKENS

EXPECTED_COLORS = {
    "claro": {'dashboard.notifications_panel_surface': '#FFFFFF',
 'dashboard.notifications_panel_border': '#E2E8F0',
 'dashboard.notifications_toggle_text': '#243B5A',
 'dashboard.notifications_toggle_hover_surface': '#F1F4F8',
 'dashboard.notifications_subtitle_text': '#7C8A9D',
 'dashboard.attention_priority_surface': '#FFF9EE',
 'dashboard.attention_priority_border': '#EAD9B5',
 'dashboard.attention_priority_ok_surface': '#F5FAF7',
 'dashboard.attention_priority_ok_border': '#D4E7DB',
 'dashboard.attention_priority_critical_surface': '#FFF3F1',
 'dashboard.attention_priority_critical_border': '#E8CBC7',
 'dashboard.attention_priority_icon_surface': '#FFF1CF',
 'dashboard.attention_priority_icon_text': '#AD7B1E',
 'dashboard.attention_priority_icon_border': '#E8CF94',
 'dashboard.attention_priority_icon_ok_surface': '#E9F5ED',
 'dashboard.attention_priority_icon_ok_text': '#3F7D59',
 'dashboard.attention_priority_icon_ok_border': '#C9E1D1',
 'dashboard.attention_priority_icon_critical_surface': '#FDE9E6',
 'dashboard.attention_priority_icon_critical_text': '#B55249',
 'dashboard.attention_priority_icon_critical_border': '#E8C1BD',
 'dashboard.attention_eyebrow_text': '#768496',
 'dashboard.attention_title_text': '#27364A',
 'dashboard.attention_description_text': '#6B7787',
 'dashboard.attention_meta_text': '#7D8794',
 'dashboard.attention_badge_surface': '#FFF0C8',
 'dashboard.attention_badge_text': '#8B6724',
 'dashboard.attention_badge_border': '#E2C986',
 'dashboard.attention_badge_ok_surface': '#EAF5EE',
 'dashboard.attention_badge_ok_text': '#47785A',
 'dashboard.attention_badge_ok_border': '#C9E0D0',
 'dashboard.attention_badge_critical_surface': '#FDE9E6',
 'dashboard.attention_badge_critical_text': '#A94D45',
 'dashboard.attention_badge_critical_border': '#E8C1BD',
 'dashboard.attention_action_surface': '#D69A2E',
 'dashboard.attention_action_text': '#FFFFFF',
 'dashboard.attention_action_border': '#D69A2E',
 'dashboard.attention_action_hover_surface': '#BD8420',
 'dashboard.attention_action_hover_text': '#FFFFFF',
 'dashboard.attention_action_hover_border': '#BD8420',
 'dashboard.attention_action_disabled_surface': '#F8FAFC',
 'dashboard.attention_action_disabled_text': '#94A3B8',
 'dashboard.attention_action_disabled_border': '#E2E8F0',
 'dashboard.attention_pace_surface': '#F4F8FD',
 'dashboard.attention_pace_border': '#D4E2F0',
 'dashboard.attention_pace_icon_surface': '#EAF3FD',
 'dashboard.attention_pace_icon_text': '#3C74B5',
 'dashboard.attention_pace_icon_border': '#C7DCEF',
 'dashboard.attention_pace_badge_surface': '#E9F2FD',
 'dashboard.attention_pace_badge_text': '#3E6FA8',
 'dashboard.attention_pace_badge_border': '#C9DCED',
 'dashboard.attention_forecast_action_surface': '#FFFFFF',
 'dashboard.attention_forecast_action_text': '#326FD3',
 'dashboard.attention_forecast_action_border': '#9EC0F3',
 'dashboard.attention_forecast_action_hover_surface': '#EEF5FF',
 'dashboard.attention_forecast_action_hover_text': '#285FB5',
 'dashboard.attention_forecast_action_hover_border': '#7FA8E8',
 'dashboard.attention_forecast_action_disabled_border': '#E2E8F0',
 'dashboard.attention_footer_surface': '#FBFCFE',
 'dashboard.attention_footer_border': '#E1E7EF',
 'dashboard.attention_footer_item_text': '#536173',
 'dashboard.attention_footer_hint_text': '#8994A3'},
    "escuro": {'dashboard.notifications_panel_surface': '#151F2D',
 'dashboard.notifications_panel_border': '#2D4054',
 'dashboard.notifications_toggle_text': '#D7E4F2',
 'dashboard.notifications_toggle_hover_surface': '#172536',
 'dashboard.notifications_subtitle_text': '#8292A6',
 'dashboard.attention_priority_surface': '#2B271F',
 'dashboard.attention_priority_border': '#5C5137',
 'dashboard.attention_priority_ok_surface': '#1D2B25',
 'dashboard.attention_priority_ok_border': '#365545',
 'dashboard.attention_priority_critical_surface': '#322120',
 'dashboard.attention_priority_critical_border': '#6F4441',
 'dashboard.attention_priority_icon_surface': '#3B321F',
 'dashboard.attention_priority_icon_text': '#E1B95F',
 'dashboard.attention_priority_icon_border': '#6C5A31',
 'dashboard.attention_priority_icon_ok_surface': '#21382D',
 'dashboard.attention_priority_icon_ok_text': '#79BF93',
 'dashboard.attention_priority_icon_ok_border': '#3F6650',
 'dashboard.attention_priority_icon_critical_surface': '#432727',
 'dashboard.attention_priority_icon_critical_text': '#E38B82',
 'dashboard.attention_priority_icon_critical_border': '#754541',
 'dashboard.attention_eyebrow_text': '#8C9AAD',
 'dashboard.attention_title_text': '#DDE6F1',
 'dashboard.attention_description_text': '#A7B2C1',
 'dashboard.attention_meta_text': '#94A0AF',
 'dashboard.attention_badge_surface': '#3B321F',
 'dashboard.attention_badge_text': '#E0B968',
 'dashboard.attention_badge_border': '#66572F',
 'dashboard.attention_badge_ok_surface': '#21372D',
 'dashboard.attention_badge_ok_text': '#79BF93',
 'dashboard.attention_badge_ok_border': '#3D624E',
 'dashboard.attention_badge_critical_surface': '#432827',
 'dashboard.attention_badge_critical_text': '#E59087',
 'dashboard.attention_badge_critical_border': '#714641',
 'dashboard.attention_action_surface': '#A97523',
 'dashboard.attention_action_text': '#FFFFFF',
 'dashboard.attention_action_border': '#C6923D',
 'dashboard.attention_action_hover_surface': '#8F641C',
 'dashboard.attention_action_hover_text': '#FFFFFF',
 'dashboard.attention_action_hover_border': '#BA8C43',
 'dashboard.attention_action_disabled_surface': '#273449',
 'dashboard.attention_action_disabled_text': '#64748B',
 'dashboard.attention_action_disabled_border': '#334155',
 'dashboard.attention_pace_surface': '#1C2835',
 'dashboard.attention_pace_border': '#36516E',
 'dashboard.attention_pace_icon_surface': '#213549',
 'dashboard.attention_pace_icon_text': '#79B6DF',
 'dashboard.attention_pace_icon_border': '#416B8A',
 'dashboard.attention_pace_badge_surface': '#173552',
 'dashboard.attention_pace_badge_text': '#84B9DC',
 'dashboard.attention_pace_badge_border': '#3D6381',
 'dashboard.attention_forecast_action_surface': '#142131',
 'dashboard.attention_forecast_action_text': '#9FD0FF',
 'dashboard.attention_forecast_action_border': '#4C7BCF',
 'dashboard.attention_forecast_action_hover_surface': '#1A2D43',
 'dashboard.attention_forecast_action_hover_text': '#D8EBFF',
 'dashboard.attention_forecast_action_hover_border': '#6A99EE',
 'dashboard.attention_forecast_action_disabled_border': '#334155',
 'dashboard.attention_footer_surface': '#1D242D',
 'dashboard.attention_footer_border': '#343E4B',
 'dashboard.attention_footer_item_text': '#AEB9C7',
 'dashboard.attention_footer_hint_text': '#778393'},
    "futurista": {'dashboard.notifications_panel_surface': '#202833',
 'dashboard.notifications_panel_border': '#2D5874',
 'dashboard.notifications_toggle_text': '#D7E4F2',
 'dashboard.notifications_toggle_hover_surface': '#B4122E42',
 'dashboard.notifications_subtitle_text': '#7898AD',
 'dashboard.attention_priority_surface': '#E1312715',
 'dashboard.attention_priority_border': '#735D32',
 'dashboard.attention_priority_ok_surface': '#E1102B22',
 'dashboard.attention_priority_ok_border': '#32634F',
 'dashboard.attention_priority_critical_surface': '#E1331A1B',
 'dashboard.attention_priority_critical_border': '#774646',
 'dashboard.attention_priority_icon_surface': '#E13A2C14',
 'dashboard.attention_priority_icon_text': '#E2B85E',
 'dashboard.attention_priority_icon_border': '#816936',
 'dashboard.attention_priority_icon_ok_surface': '#E1163E2D',
 'dashboard.attention_priority_icon_ok_text': '#78D0A0',
 'dashboard.attention_priority_icon_ok_border': '#3B7759',
 'dashboard.attention_priority_icon_critical_surface': '#E6421F1F',
 'dashboard.attention_priority_icon_critical_text': '#EE8B83',
 'dashboard.attention_priority_icon_critical_border': '#824947',
 'dashboard.attention_eyebrow_text': '#7896AA',
 'dashboard.attention_title_text': '#D5EDF6',
 'dashboard.attention_description_text': '#8EAFBF',
 'dashboard.attention_meta_text': '#7F9DAB',
 'dashboard.attention_badge_surface': '#3B321F',
 'dashboard.attention_badge_text': '#E3BD69',
 'dashboard.attention_badge_border': '#7A6336',
 'dashboard.attention_badge_ok_surface': '#21372D',
 'dashboard.attention_badge_ok_text': '#7DD0A1',
 'dashboard.attention_badge_ok_border': '#3C7457',
 'dashboard.attention_badge_critical_surface': '#432827',
 'dashboard.attention_badge_critical_text': '#EE8B83',
 'dashboard.attention_badge_critical_border': '#824947',
 'dashboard.attention_action_surface': '#8F6B31',
 'dashboard.attention_action_text': '#FFFAF0',
 'dashboard.attention_action_border': '#F5C86D',
 'dashboard.attention_action_hover_surface': '#A17937',
 'dashboard.attention_action_hover_text': '#FFFFFF',
 'dashboard.attention_action_hover_border': '#FFD98C',
 'dashboard.attention_action_disabled_surface': '#273449',
 'dashboard.attention_action_disabled_text': '#64748B',
 'dashboard.attention_action_disabled_border': '#334155',
 'dashboard.attention_pace_surface': '#E60A2032',
 'dashboard.attention_pace_border': '#315976',
 'dashboard.attention_pace_icon_surface': '#E10D2C40',
 'dashboard.attention_pace_icon_text': '#7CC6E8',
 'dashboard.attention_pace_icon_border': '#3C7795',
 'dashboard.attention_pace_badge_surface': '#173552',
 'dashboard.attention_pace_badge_text': '#82C7E6',
 'dashboard.attention_pace_badge_border': '#3A718D',
 'dashboard.attention_forecast_action_surface': '#386F9E',
 'dashboard.attention_forecast_action_text': '#A3D9FF',
 'dashboard.attention_forecast_action_border': '#5F8DD8',
 'dashboard.attention_forecast_action_hover_surface': '#427CAE',
 'dashboard.attention_forecast_action_hover_text': '#E8F8FF',
 'dashboard.attention_forecast_action_hover_border': '#85B8FF',
 'dashboard.attention_forecast_action_disabled_border': '#28465D',
 'dashboard.attention_footer_surface': '#DC0B1A26',
 'dashboard.attention_footer_border': '#294354',
 'dashboard.attention_footer_item_text': '#9EB9C7',
 'dashboard.attention_footer_hint_text': '#657F8D'},
}

BLOCK_D_QSS = {
    "claro": "67eb7f0c5eee80785bbe7595d4ca9374c9fc2985b34034ede312c06e69e49e08",
    "escuro": "1109df37ba34574f0607dd9ee3839a770c74aed8906dece461e9c2e8b81f7624",
    "futurista": "07717d507c118a34f4b8ca7c62556c60a8b0fdc874f7d30f379d19b4ed379d6c",
}
BLOCK_E_QSS = {
    "claro": "81f1c8fc6eebb10cd8dccea854795798f3871a11da372eea4baf02b5f71eb2c4",
    "escuro": "ef56315047f797aabc02a33118b97a4f6992c775e696c9b1d61509030df45186",
    "futurista": "29e36ecb0c7cbb06dfe15821c7c07b84ad6a81dc75a48f2d5fe56db70fe9079d",
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


class DashboardBlockEDesignSystemTests(unittest.TestCase):
    def test_orcamento_de_tokens_exato(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 928)
        self.assertEqual(len(ALL_TOKENS), 1030)
        self.assertEqual(len(COLOR_TOKENS), 61)
        paths = {token.path for token in ALL_TOKENS}
        self.assertTrue(BLOCK_E_TOKENS <= paths)
        for path in COLOR_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.COLOR)

    def test_tokens_reproduzem_caracterizacao(self):
        for theme_name, expected in EXPECTED_COLORS.items():
            theme = get_theme(theme_name)
            for path, value in expected.items():
                with self.subTest(theme=theme_name, path=path):
                    self.assertEqual(theme.color(path).value, value)

    def test_qss_bloco_e_e_tokenizado_e_estritamente_escopado(self):
        source = tema.ESTILO_DASHBOARD_BLOCO_E
        self.assertIsNone(re.search(r"#[0-9A-Fa-f]{6,8}\b", source))
        self.assertNotIn("QPainter", source)
        self.assertIn('dashboardNotificationsPanel', source)
        self.assertIn('attentionRole="priority"', source)
        self.assertIn('attentionRole="pace"', source)
        for state in ("monitorar", "atencao", "ok", "critico"):
            self.assertIn(f'alertState="{state}"', source)
        self.assertIn('syllabusAlertButton:disabled', source)
        self.assertIn('syllabusForecastButton:disabled', source)
        for legacy in (
            "dashboardNoticeRow", "dashboardNoticeLabel", "dashboardNoticeTitle",
            "dashboardNoticeDescription", "dashboardNoticeSummary", "dashboardNotificationsTitle",
            "dashboardNotificationsMenu", "dashboardNotificationsFooter",
        ):
            self.assertNotIn(legacy, source)
        for outside in ("planningPanel", "studyNowPanel", "dashboardOverviewCard", "focusDashboardMainCard"):
            self.assertNotIn(outside, source)
        for selector in re.findall(r"([^{}]+)\{", source):
            if selector.strip().startswith("Q"):
                self.assertIn("#dashboardRoot", selector)
                self.assertIn("#dashboardNotificationsPanel", selector)

    def test_consumidores_ativos_e_estados_dinamicos_permanecem(self):
        for marker in (
            'setObjectName(\n            "dashboardNotificationsPanel"',
            'setObjectName(\n            "dashboardAttentionCard"',
            'setObjectName(\n            "dashboardAttentionIcon"',
            'setObjectName(\n            "dashboardAttentionBadge"',
            'setObjectName(\n            "dashboardPaceBadge"',
            'setObjectName(\n            "dashboardAttentionFooter"',
            'setObjectName(\n            "dashboardAttentionFooterItem"',
        ):
            self.assertIn(marker, MAIN_SOURCE)
        self.assertRegex(MAIN_SOURCE, r'setProperty\(\s*"attentionRole",\s*"priority"\s*\)')
        self.assertRegex(MAIN_SOURCE, r'setProperty\(\s*"attentionRole",\s*"pace"\s*\)')
        self.assertRegex(MAIN_SOURCE, r'setProperty\(\s*"alertState",\s*"monitorar"\s*\)')
        self.assertRegex(MAIN_SOURCE, r'setProperty\(\s*"alertState",\s*estado\s*\)')
        for state in ("critico", "atencao", "monitorar", "ok"):
            self.assertIn(f'"{state}"', MAIN_SOURCE)
        self.assertIn('"dashboard_secao_notificacoes_expandida"', MAIN_SOURCE)

    def test_legado_de_notice_row_continua_sem_consumidor_no_main(self):
        for legacy in (
            "dashboardNoticeRow", "dashboardNoticeLabel", "dashboardNoticeTitle",
            "dashboardNoticeIcon", "dashboardNoticeDescription", "dashboardNoticeSummary",
            "dashboardNotificationsTitle", "dashboardNotificationsMenu",
        ):
            self.assertNotIn(legacy, MAIN_SOURCE)

    def test_renderizacao_tem_hash_e_e_sem_marcadores(self):
        for theme_name in ("claro", "escuro", "futurista"):
            qss = getattr(tema, f"stylesheet_{theme_name}")()
            self.assertNotIn("{{color:", qss)
            self.assertNotIn("{{gradient:", qss)
            self.assertEqual(qss_hash(strip_block_f(theme_name, qss)), BLOCK_E_QSS[theme_name])

    def test_remover_e_recupera_checkpoint_d(self):
        for theme_name in ("claro", "escuro", "futurista"):
            qss = getattr(tema, f"stylesheet_{theme_name}")()
            self.assertEqual(qss_hash(strip_block_e(theme_name, qss)), BLOCK_D_QSS[theme_name])

    def test_arquivos_protegidos_permanecem_byte_a_byte(self):
        for name, expected in PROTECTED_HASHES.items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected, name)

    def test_metadata_permanece_inalterada(self):
        self.assertEqual(VIGHNA_VERSION, "0.29.59")
        self.assertEqual(VIGHNA_BUILD, "updates-center-v1")
        self.assertEqual(VIGHNA_SCHEMA, 25)


if __name__ == "__main__":
    unittest.main()
