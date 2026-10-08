"""Regressões do Design System — Dashboard, Bloco D: Visão geral."""
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

COLOR_TOKENS = {
    'dashboard.overview_card_border','dashboard.overview_title_text','dashboard.overview_info_text',
    'dashboard.overview_divider','dashboard.overview_vertical_divider','dashboard.rhythm_main_text',
    'dashboard.rhythm_caption_text','dashboard.rhythm_line_label_text','dashboard.rhythm_today_dot_text',
    'dashboard.rhythm_late_dot_text','dashboard.rhythm_today_value_text','dashboard.rhythm_late_value_text',
    'dashboard.rhythm_status_ok_text','dashboard.rhythm_status_attention_text','dashboard.rhythm_summary_text',
    'dashboard.quality_eyebrow_text','dashboard.quality_caption_text','dashboard.quality_trend_surface',
    'dashboard.quality_trend_border','dashboard.quality_trend_text','dashboard.quality_trend_positive_text',
    'dashboard.quality_trend_negative_text','dashboard.quality_trend_stable_text','dashboard.quality_trend_label_text',
    'dashboard.quality_footer_text','dashboard.projection_title_text','dashboard.projection_caption_text',
    'dashboard.projection_detail_text','dashboard.projection_percent_text','dashboard.projection_bar_track',
    'dashboard.projection_bar_border','dashboard.projection_bar_fill','dashboard.projection_metric_surface',
    'dashboard.projection_metric_border','dashboard.projection_metric_label_text','dashboard.projection_metric_value_text',
    'dashboard.projection_metric_consolidating_text','dashboard.projection_metric_consolidated_text',
    'dashboard.projection_metric_domain_text','dashboard.projection_action_text','dashboard.projection_action_border',
    'dashboard.projection_action_hover_border',
}
GRADIENT_TOKENS = {
    'dashboard.overview_card_gradient','dashboard.projection_action_gradient','dashboard.projection_action_hover_gradient'
}
BLOCK_D_TOKENS = COLOR_TOKENS | GRADIENT_TOKENS

EXPECTED_COLORS = {
    'claro': {
        'dashboard.overview_card_border':'#E2E8F0','dashboard.overview_title_text':'#1F2D3D','dashboard.overview_info_text':'#9AA6B5',
        'dashboard.overview_divider':'#E6EBF2','dashboard.overview_vertical_divider':'#E6EBF2','dashboard.rhythm_main_text':'#1F2D3D',
        'dashboard.rhythm_caption_text':'#7C8A9D','dashboard.rhythm_line_label_text':'#556579','dashboard.rhythm_today_dot_text':'#4D9278',
        'dashboard.rhythm_late_dot_text':'#9A7330','dashboard.rhythm_today_value_text':'#4D9278','dashboard.rhythm_late_value_text':'#9A7330',
        'dashboard.rhythm_status_ok_text':'#4D9278','dashboard.rhythm_status_attention_text':'#9A7330','dashboard.rhythm_summary_text':'#53708C',
        'dashboard.quality_eyebrow_text':'#7C8A9D','dashboard.quality_caption_text':'#7C8A9D','dashboard.quality_trend_surface':'#F7FAFD',
        'dashboard.quality_trend_border':'#E2E9F1','dashboard.quality_trend_text':'#536176','dashboard.quality_trend_positive_text':'#488D73',
        'dashboard.quality_trend_negative_text':'#B46A6A','dashboard.quality_trend_stable_text':'#233247','dashboard.quality_trend_label_text':'#8A96A6',
        'dashboard.quality_footer_text':'#7C8A9D','dashboard.projection_title_text':'#243B5A','dashboard.projection_caption_text':'#7C8A9D',
        'dashboard.projection_detail_text':'#556579','dashboard.projection_percent_text':'#233247','dashboard.projection_bar_track':'#E7EDF3',
        'dashboard.projection_bar_border':'transparent','dashboard.projection_bar_fill':'#2FB4C7','dashboard.projection_metric_surface':'#F8FBFD',
        'dashboard.projection_metric_border':'#E1E8F0','dashboard.projection_metric_label_text':'#7C8A9D','dashboard.projection_metric_value_text':'#556579',
        'dashboard.projection_metric_consolidating_text':'#6D7FD6','dashboard.projection_metric_consolidated_text':'#4B9677',
        'dashboard.projection_metric_domain_text':'#356FCF','dashboard.projection_action_text':'#FFFFFF',
        'dashboard.projection_action_border':'#326FD3','dashboard.projection_action_hover_border':'#285FB5',
    },
    'escuro': {
        'dashboard.overview_card_border':'#2D4054','dashboard.overview_title_text':'#E7EDF4','dashboard.overview_info_text':'#718398',
        'dashboard.overview_divider':'#2F4155','dashboard.overview_vertical_divider':'#2E4053','dashboard.rhythm_main_text':'#E4EBF3',
        'dashboard.rhythm_caption_text':'#8B9AAB','dashboard.rhythm_line_label_text':'#93A2B4','dashboard.rhythm_today_dot_text':'#68BF91',
        'dashboard.rhythm_late_dot_text':'#D0A458','dashboard.rhythm_today_value_text':'#82C9A1','dashboard.rhythm_late_value_text':'#D1AA66',
        'dashboard.rhythm_status_ok_text':'#81C39D','dashboard.rhythm_status_attention_text':'#D0AA67','dashboard.rhythm_summary_text':'#8CA4BB',
        'dashboard.quality_eyebrow_text':'#788A9F','dashboard.quality_caption_text':'#C6D1DD','dashboard.quality_trend_surface':'#142131',
        'dashboard.quality_trend_border':'#2D4054','dashboard.quality_trend_text':'#A6B5C6','dashboard.quality_trend_positive_text':'#79C79D',
        'dashboard.quality_trend_negative_text':'#D28585','dashboard.quality_trend_stable_text':'#A2AFBF','dashboard.quality_trend_label_text':'#77899E',
        'dashboard.quality_footer_text':'#65778B','dashboard.projection_title_text':'#D7E4F2','dashboard.projection_caption_text':'#8797A9',
        'dashboard.projection_detail_text':'#BAC6D2','dashboard.projection_percent_text':'#E3EBF3','dashboard.projection_bar_track':'#263443',
        'dashboard.projection_bar_border':'transparent','dashboard.projection_bar_fill':'#35BCB4','dashboard.projection_metric_surface':'#152333',
        'dashboard.projection_metric_border':'#2E4054','dashboard.projection_metric_label_text':'#8797AA','dashboard.projection_metric_value_text':'#DAE3EC',
        'dashboard.projection_metric_consolidating_text':'#AB94D6','dashboard.projection_metric_consolidated_text':'#80C59C',
        'dashboard.projection_metric_domain_text':'#8EBBD4','dashboard.projection_action_text':'#FFFFFF',
        'dashboard.projection_action_border':'#4C7BCF','dashboard.projection_action_hover_border':'#426EC4',
    },
    'futurista': {
        'dashboard.overview_card_border':'#445061','dashboard.overview_title_text':'#D8EBF4','dashboard.overview_info_text':'#65879C',
        'dashboard.overview_divider':'#284A60','dashboard.overview_vertical_divider':'#28485D','dashboard.rhythm_main_text':'#DDECF4',
        'dashboard.rhythm_caption_text':'#7E9AAC','dashboard.rhythm_line_label_text':'#839FAF','dashboard.rhythm_today_dot_text':'#6BC39A',
        'dashboard.rhythm_late_dot_text':'#C9A15A','dashboard.rhythm_today_value_text':'#7EC7A0','dashboard.rhythm_late_value_text':'#CAA461',
        'dashboard.rhythm_status_ok_text':'#78BD98','dashboard.rhythm_status_attention_text':'#C5A05F','dashboard.rhythm_summary_text':'#82ABC5',
        'dashboard.quality_eyebrow_text':'#718DA0','dashboard.quality_caption_text':'#C0D4DF','dashboard.quality_trend_surface':'#DC091D2C',
        'dashboard.quality_trend_border':'#29495E','dashboard.quality_trend_text':'#9EB8C7','dashboard.quality_trend_positive_text':'#75C29A',
        'dashboard.quality_trend_negative_text':'#CE8080','dashboard.quality_trend_stable_text':'#9AAFBD','dashboard.quality_trend_label_text':'#6F8B9C',
        'dashboard.quality_footer_text':'#5F7C8E','dashboard.projection_title_text':'#D7E4F2','dashboard.projection_caption_text':'#7895A7',
        'dashboard.projection_detail_text':'#ABC1CD','dashboard.projection_percent_text':'#DEEFF7','dashboard.projection_bar_track':'#1A3041',
        'dashboard.projection_bar_border':'#294B60','dashboard.projection_bar_fill':'#3BBEB8','dashboard.projection_metric_surface':'#DC0C1F2F',
        'dashboard.projection_metric_border':'#294B61','dashboard.projection_metric_label_text':'#7895A8','dashboard.projection_metric_value_text':'#D3E5ED',
        'dashboard.projection_metric_consolidating_text':'#9F91C8','dashboard.projection_metric_consolidated_text':'#76BE96',
        'dashboard.projection_metric_domain_text':'#82AFC8','dashboard.projection_action_text':'#FFFFFF',
        'dashboard.projection_action_border':'#7DADFF','dashboard.projection_action_hover_border':'#96BBFF',
    },
}
EXPECTED_GRADIENTS = {
    'claro': {
        'dashboard.overview_card_gradient': ((0,0,1,1), ((0.0,'#FFFFFF'),(1.0,'#FFFFFF'))),
        'dashboard.projection_action_gradient': ((0,0,1,0), ((0.0,'#326FD3'),(1.0,'#326FD3'))),
        'dashboard.projection_action_hover_gradient': ((0,0,1,0), ((0.0,'#285FB5'),(1.0,'#285FB5'))),
    },
    'escuro': {
        'dashboard.overview_card_gradient': ((0,0,1,1), ((0.0,'#151F2D'),(1.0,'#151F2D'))),
        'dashboard.projection_action_gradient': ((0,0,1,0), ((0.0,'#416AB7'),(1.0,'#416AB7'))),
        'dashboard.projection_action_hover_gradient': ((0,0,1,0), ((0.0,'#355BA3'),(1.0,'#355BA3'))),
    },
    'futurista': {
        'dashboard.overview_card_gradient': ((0,0,1,1), ((0.0,'#202833'),(1.0,'#202833'))),
        'dashboard.projection_action_gradient': ((0,0,1,0), ((0.0,'#355F9F'),(1.0,'#4C7EE0'))),
        'dashboard.projection_action_hover_gradient': ((0,0,1,0), ((0.0,'#2F558D'),(1.0,'#436DBE'))),
    },
}

BLOCK_C_QSS = {
    'claro':'64ea82086ca9575c727925b6e0ebae18bc45d0f760e94ca1d3bab679be16f273',
    'escuro':'d3011c1a6f28b7d89678129ab6462d6cb4b1b9ce19e2084dc1f3e52e5a6cda2c',
    'futurista':'69f5d9733fd68f2665f8f3a534cf7b2f88fc07890b309837302737809ebea488',
}
BLOCK_D_QSS = {
    'claro':'67eb7f0c5eee80785bbe7595d4ca9374c9fc2985b34034ede312c06e69e49e08',
    'escuro':'1109df37ba34574f0607dd9ee3839a770c74aed8906dece461e9c2e8b81f7624',
    'futurista':'07717d507c118a34f4b8ca7c62556c60a8b0fdc874f7d30f379d19b4ed379d6c',
}
PROTECTED_HASHES = {
    'main.py':'bdb0815e71387bd87d40498bf535ef839d19a1a9086d55e0582ea50946713b45',
    'estudos.db':'034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef',
    'versao.py':'c201d237e622dd2269838e54914458fd775c7ec1a91f07b518775ee833caa439',
    'foco.py':'8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed',
    'jogos.py':'498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286',
    'checkpoint.py':'947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38',
}


def canonical_qss(qss: str) -> str:
    qss = re.sub(r"#[0-9A-Fa-f]{3,8}\b", lambda m: m.group(0).upper(), qss)
    return re.sub(r"\s+", " ", qss).strip()


def qss_hash(qss: str) -> str:
    return hashlib.sha256(canonical_qss(qss).encode('utf-8')).hexdigest()



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
    if theme_name == 'futurista':
        final = render_qss('futurista', tema.ESTILO_DASHBOARD_BLOCO_D)
        inherited = render_qss('escuro', tema.ESTILO_DASHBOARD_BLOCO_D)
        if not qss.endswith(final):
            raise AssertionError('camada D futurista não é a última')
        qss = qss[:-len(final)]
        return qss.replace(inherited, '', 1)
    layer = render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_D)
    if not qss.endswith(layer):
        raise AssertionError(f'camada D não é a última em {theme_name}')
    return qss[:-len(layer)]


class DashboardBlockDDesignSystemTests(unittest.TestCase):
    def test_orcamento_de_tokens_exato(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 928)
        self.assertEqual(len(ALL_TOKENS), 1030)
        self.assertEqual(len(COLOR_TOKENS), 42)
        self.assertEqual(len(GRADIENT_TOKENS), 3)
        self.assertEqual(len(BLOCK_D_TOKENS), 45)
        paths = {token.path for token in ALL_TOKENS}
        self.assertTrue(BLOCK_D_TOKENS <= paths)
        for path in COLOR_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.COLOR)
        for path in GRADIENT_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.GRADIENT)

    def test_tokens_reproduzem_caracterizacao(self):
        for theme_name, expected in EXPECTED_COLORS.items():
            theme = get_theme(theme_name)
            for path, value in expected.items():
                self.assertEqual(theme.color(path).value, value, (theme_name, path))
            for path, (direction, stops) in EXPECTED_GRADIENTS[theme_name].items():
                gradient = theme.gradient(path)
                actual_direction = (gradient.direction.x1,gradient.direction.y1,gradient.direction.x2,gradient.direction.y2)
                actual_stops = tuple((stop.position, stop.color.value) for stop in gradient.stops)
                self.assertEqual(actual_direction, direction, (theme_name,path))
                self.assertEqual(actual_stops, stops, (theme_name,path))

    def test_qss_bloco_d_e_tokenizado_e_isolado(self):
        source = tema.ESTILO_DASHBOARD_BLOCO_D
        self.assertIsNone(re.search(r"#[0-9A-Fa-f]{6,8}\b", source))
        self.assertNotIn('QPainter', source)
        self.assertIn('dashboardOverviewCard[overviewRole="rhythm"]', source)
        self.assertIn('dashboardOverviewCard[overviewRole="quality"]', source)
        self.assertIn('dashboardOverviewCard[overviewRole="projection"]', source)
        self.assertIn('dashboardQualityTrendValue[trendRole="positive"]', source)
        self.assertIn('dashboardRhythmStatus[statusRole="attention"]', source)
        self.assertIn('dashboardProjectionMetric[metricRole="consolidated"]', source)
        self.assertNotIn('dashboardNotificationsPanel', source)
        self.assertNotIn('planningPanel', source)
        self.assertNotIn('dashboardTodayAction', source)
        self.assertNotIn('focusQuickCard', source)
        self.assertNotIn('DashboardDonutWidget', source)
        for selector in re.findall(r'([^{}]+)\{', source):
            if selector.strip().startswith('Q'):
                self.assertIn('#dashboardRoot', selector)

    def test_qpainter_do_donut_preserva_geometria_apos_bloco_i(self):
        self.assertIn('class DashboardDonutWidget(QWidget):', MAIN_SOURCE)
        donut = MAIN_SOURCE.split('class DashboardDonutWidget(QWidget):',1)[1].split('class JanelaInicializacao',1)[0]
        self.assertIn('QPainter(self)', donut)
        self.assertIn('qcolor(tema_atual, "dashboard.quality_donut_fill")', donut)
        self.assertIn('cor_texto.lightness() > 150', donut)
        self.assertIn('360 * 16', donut)
        self.assertIn('90 * 16', donut)
        self.assertNotIn('QColor(', donut)

    def test_estados_dinamicos_e_persistencia_permanecem(self):
        for role in ("rhythm", "quality", "projection"):
            self.assertRegex(
                MAIN_SOURCE,
                rf'setProperty\(\s*"overviewRole",\s*"{role}"\s*\)',
            )
        self.assertRegex(MAIN_SOURCE, r'setProperty\(\s*"metricRole",\s*role\s*\)')
        self.assertIn('"today"', MAIN_SOURCE)
        self.assertIn('"late"', MAIN_SOURCE)
        self.assertRegex(MAIN_SOURCE, r'setProperty\(\s*"trendRole",\s*"none"\s*\)')
        self.assertRegex(MAIN_SOURCE, r'setProperty\(\s*"trendRole",\s*tendencia_role\s*\)')
        self.assertIn('"dashboard_secao_resumo_expandida"', MAIN_SOURCE)
        self.assertIn('"dashboard_secao_progresso_expandida"', MAIN_SOURCE)

    def test_renderizacao_tem_hash_d_e_sem_marcadores(self):
        for theme_name in ('claro','escuro','futurista'):
            qss = getattr(tema, f'stylesheet_{theme_name}')()
            self.assertNotIn('{{color:', qss)
            self.assertNotIn('{{gradient:', qss)
            self.assertEqual(qss_hash(strip_block_e(theme_name, qss)), BLOCK_D_QSS[theme_name])

    def test_remover_d_recupera_checkpoint_c(self):
        for theme_name in ('claro','escuro','futurista'):
            qss = getattr(tema, f'stylesheet_{theme_name}')()
            self.assertEqual(qss_hash(strip_block_d(theme_name,qss)), BLOCK_C_QSS[theme_name])

    def test_arquivos_protegidos_permanecem_byte_a_byte(self):
        for name, expected in PROTECTED_HASHES.items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), expected, name)

    def test_metadata_permanece_inalterada(self):
        self.assertEqual(VIGHNA_VERSION, '0.29.59')
        self.assertEqual(VIGHNA_BUILD, 'updates-center-v1')
        self.assertEqual(VIGHNA_SCHEMA, 25)


if __name__ == '__main__':
    unittest.main()
