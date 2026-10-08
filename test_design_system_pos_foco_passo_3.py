import hashlib
import re
import unittest
from _design_system_test_helpers import strip_cards_global_block_a
from pathlib import Path

import tema
from ui.design import ALL_TOKENS, COMPONENT_TOKEN_COUNT, SEMANTIC_TOKEN_COUNT, TokenKind, get_theme, token_spec

ROOT = Path(__file__).resolve().parent
TEMA_SOURCE = (ROOT / "tema.py").read_text(encoding="utf-8")
FOCO_SOURCE = (ROOT / "foco.py").read_text(encoding="utf-8")

POST_FOCUS_COLOR_TOKENS = ('post_focus.dialog_title_text',
 'post_focus.dialog_subtitle_text',
 'post_focus.hero_surface',
 'post_focus.hero_border',
 'post_focus.eyebrow_text',
 'post_focus.time_text',
 'post_focus.meta_text',
 'post_focus.mini_surface',
 'post_focus.mini_border',
 'post_focus.mini_label_text',
 'post_focus.mini_value_text',
 'post_focus.content_surface',
 'post_focus.content_border',
 'post_focus.strong_text',
 'post_focus.result_surface',
 'post_focus.result_border',
 'post_focus.result_value_text',
 'post_focus.continue_surface',
 'post_focus.continue_text',
 'post_focus.continue_border',
 'post_focus.continue_hover_surface',
 'post_focus.continue_hover_border',
 'post_focus.primary_surface',
 'post_focus.primary_border',
 'post_focus.primary_hover_surface',
 'post_focus.primary_hover_border',
 'post_focus.secondary_surface',
 'post_focus.secondary_text',
 'post_focus.secondary_border',
 'post_focus.secondary_hover_surface',
 'post_focus.secondary_hover_border',
 'post_focus.secondary_disabled_text',
 'post_focus.secondary_disabled_surface',
 'post_focus.secondary_disabled_border',
 'post_focus.ghost_text',
 'post_focus.ghost_border',
 'post_focus.ghost_hover_surface',
 'post_focus.ghost_hover_text')

EXPECTED = {'claro': {'post_focus.dialog_title_text': '#203247',
           'post_focus.dialog_subtitle_text': '#64748B',
           'post_focus.hero_surface': '#F2F7FF',
           'post_focus.hero_border': '#BFD5EE',
           'post_focus.eyebrow_text': '#53708C',
           'post_focus.time_text': '#235FAE',
           'post_focus.meta_text': '#64748B',
           'post_focus.mini_surface': '#FFFFFF',
           'post_focus.mini_border': '#D9E2EC',
           'post_focus.mini_label_text': '#6B7D90',
           'post_focus.mini_value_text': '#235FAE',
           'post_focus.content_surface': '#FFFFFF',
           'post_focus.content_border': '#D9E2EC',
           'post_focus.strong_text': '#203247',
           'post_focus.result_surface': '#F6FBF7',
           'post_focus.result_border': '#BFDCC7',
           'post_focus.result_value_text': '#247344',
           'post_focus.continue_surface': '#E9F3FF',
           'post_focus.continue_text': '#235FAE',
           'post_focus.continue_border': '#AFCCEA',
           'post_focus.continue_hover_surface': '#DCECFF',
           'post_focus.continue_hover_border': '#8EB7E1',
           'post_focus.primary_surface': '#326FD3',
           'post_focus.primary_border': '#326FD3',
           'post_focus.primary_hover_surface': '#285FB5',
           'post_focus.primary_hover_border': '#285FB5',
           'post_focus.secondary_surface': '#FFFFFF',
           'post_focus.secondary_text': '#32679F',
           'post_focus.secondary_border': '#B9CEE4',
           'post_focus.secondary_hover_surface': '#EEF6FF',
           'post_focus.secondary_hover_border': '#8DB7E4',
           'post_focus.secondary_disabled_text': '#9AA9B8',
           'post_focus.secondary_disabled_surface': '#F4F6F8',
           'post_focus.secondary_disabled_border': '#DCE3EA',
           'post_focus.ghost_text': '#53708C',
           'post_focus.ghost_border': '#D1DBE6',
           'post_focus.ghost_hover_surface': '#F4F7FB',
           'post_focus.ghost_hover_text': '#2C5279'},
 'escuro': {'post_focus.dialog_title_text': '#E0EDF8',
            'post_focus.dialog_subtitle_text': '#8CA4BB',
            'post_focus.hero_surface': '#172536',
            'post_focus.hero_border': '#365574',
            'post_focus.eyebrow_text': '#8CA4BB',
            'post_focus.time_text': '#A9D3FF',
            'post_focus.meta_text': '#8CA4BB',
            'post_focus.mini_surface': '#172536',
            'post_focus.mini_border': '#365574',
            'post_focus.mini_label_text': '#8CA4BB',
            'post_focus.mini_value_text': '#D6EAFF',
            'post_focus.content_surface': '#151F2D',
            'post_focus.content_border': '#33465A',
            'post_focus.strong_text': '#E0EDF8',
            'post_focus.result_surface': '#172A24',
            'post_focus.result_border': '#365F4C',
            'post_focus.result_value_text': '#91D6AC',
            'post_focus.continue_surface': '#20374F',
            'post_focus.continue_text': '#D6EAFF',
            'post_focus.continue_border': '#527BA5',
            'post_focus.continue_hover_surface': '#294760',
            'post_focus.continue_hover_border': '#6B95BF',
            'post_focus.primary_surface': '#416AB7',
            'post_focus.primary_border': '#4C7BCF',
            'post_focus.primary_hover_surface': '#355BA3',
            'post_focus.primary_hover_border': '#426EC4',
            'post_focus.secondary_surface': '#172536',
            'post_focus.secondary_text': '#B9D8F7',
            'post_focus.secondary_border': '#3A5877',
            'post_focus.secondary_hover_surface': '#20374F',
            'post_focus.secondary_hover_border': '#527BA5',
            'post_focus.secondary_disabled_text': '#627488',
            'post_focus.secondary_disabled_surface': '#17202B',
            'post_focus.secondary_disabled_border': '#2B3949',
            'post_focus.ghost_text': '#8CA4BB',
            'post_focus.ghost_border': '#33465A',
            'post_focus.ghost_hover_surface': '#1B2A3B',
            'post_focus.ghost_hover_text': '#D2E6F8'},
 'futurista': {'post_focus.dialog_title_text': '#EAF8FF',
               'post_focus.dialog_subtitle_text': '#82ABC5',
               'post_focus.hero_surface': '#10283C',
               'post_focus.hero_border': '#3F7599',
               'post_focus.eyebrow_text': '#82ABC5',
               'post_focus.time_text': '#BCE7FF',
               'post_focus.meta_text': '#82ABC5',
               'post_focus.mini_surface': '#132B40',
               'post_focus.mini_border': '#3E7397',
               'post_focus.mini_label_text': '#82ABC5',
               'post_focus.mini_value_text': '#D9F4FF',
               'post_focus.content_surface': '#101F30',
               'post_focus.content_border': '#315D79',
               'post_focus.strong_text': '#EAF8FF',
               'post_focus.result_surface': '#102C2B',
               'post_focus.result_border': '#34756D',
               'post_focus.result_value_text': '#8DE2C2',
               'post_focus.continue_surface': '#173B55',
               'post_focus.continue_text': '#D9F4FF',
               'post_focus.continue_border': '#4F8FB7',
               'post_focus.continue_hover_surface': '#1D4967',
               'post_focus.continue_hover_border': '#70B7DF',
               'post_focus.primary_surface': 'transparent',
               'post_focus.primary_border': '#7DADFF',
               'post_focus.primary_hover_surface': 'transparent',
               'post_focus.primary_hover_border': '#B9D7FF',
               'post_focus.secondary_surface': '#132B40',
               'post_focus.secondary_text': '#BCE7FF',
               'post_focus.secondary_border': '#3E7397',
               'post_focus.secondary_hover_surface': '#183850',
               'post_focus.secondary_hover_border': '#65B9DF',
               'post_focus.secondary_disabled_text': '#55768B',
               'post_focus.secondary_disabled_surface': '#102231',
               'post_focus.secondary_disabled_border': '#29495E',
               'post_focus.ghost_text': '#82ABC5',
               'post_focus.ghost_border': '#315D79',
               'post_focus.ghost_hover_surface': '#132B40',
               'post_focus.ghost_hover_text': '#D9F4FF'}}

EXPECTED_PRIMARY_GRADIENTS = {
    "claro": ((0.0, "#326FD3"), (1.0, "#326FD3")),
    "escuro": ((0.0, "#416AB7"), (1.0, "#416AB7")),
    "futurista": ((0.0, "#355F9F"), (1.0, "#4C7EE0")),
}

BASELINE_NORMALIZED_HASHES = {
    "claro": "71c6c022b5fb4a3798f5bb9f837fc55fc9fa3bf4d558832688dd7fb25d8c7cdb",
    "escuro": "25dd9d735b8aa542020a05bbc3318cc91aba79f0b2f89995cea0a272d8bc1056",
    "futurista": "d4176c63eae7f8b0349fce4eb50ada9b5186473a8d0aba884ad7aa4e41f5b448",
}

PROTECTED_HASHES = {
    "main.py": "0e8ec1248b38d4bac3ffce756f3a35dabb0ba1a2c0f757996b53f6a2f4b7a02b",
    "foco.py": "8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed",
    "jogos.py": "498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286",
    "estudos.db": "7152284f813f16c42bb4586d4d929b53d5d97efe8cf6e290ff9b80faf11b9c26",
    "versao.py": "ae19e3d250f581849a09245b27469b2cb1b1aef48d862338e888679d58b20d67",
    "checkpoint.py": "947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38",
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

class DesignSystemPosFocoPasso3Tests(unittest.TestCase):
    def test_contagem_final_do_passo_3(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 1004)
        self.assertEqual(len(ALL_TOKENS), 1106)

    def test_exatamente_38_colors_e_um_gradiente_post_focus(self):
        self.assertEqual(len(POST_FOCUS_COLOR_TOKENS), 38)
        for path in POST_FOCUS_COLOR_TOKENS:
            with self.subTest(path=path):
                self.assertEqual(token_spec(path).kind, TokenKind.COLOR)
        self.assertEqual(token_spec("post_focus.primary_gradient").kind, TokenKind.GRADIENT)

    def test_valores_reproduzem_a_linha_de_base(self):
        for theme_name, values in EXPECTED.items():
            theme = get_theme(theme_name)
            for path, expected in values.items():
                with self.subTest(theme=theme_name, path=path):
                    self.assertEqual(theme.color(path).value, expected)

    def test_gradiente_primario_preserva_solid_light_dark_e_futurista(self):
        for theme_name, expected in EXPECTED_PRIMARY_GRADIENTS.items():
            spec = get_theme(theme_name).gradient("post_focus.primary_gradient")
            actual = tuple((stop.position, stop.color.value) for stop in spec.stops)
            self.assertEqual(actual, expected)
            self.assertEqual((spec.direction.x1, spec.direction.y1, spec.direction.x2, spec.direction.y2), (0.0, 0.0, 1.0, 0.0))

    def test_toda_a_familia_post_focus_removeu_hex_literal_do_qss_fonte(self):
        post_lines = [line for line in TEMA_SOURCE.splitlines() if "postFocus" in line]
        self.assertTrue(post_lines)
        for line in post_lines:
            with self.subTest(line=line.strip()[:80]):
                self.assertIsNone(re.search(r"#[0-9A-Fa-f]{6}\b", line))
        self.assertIn("{{gradient:post_focus.primary_gradient}}", TEMA_SOURCE)
        self.assertIn("{{color:text.on_action}}", TEMA_SOURCE)

    def test_assimetrias_do_primary_permanecem_intactas(self):
        self.assertEqual(TEMA_SOURCE.count("{{color:post_focus.primary_surface}}"), 2)
        self.assertEqual(TEMA_SOURCE.count("{{color:post_focus.primary_hover_surface}}"), 2)
        self.assertEqual(TEMA_SOURCE.count("{{gradient:post_focus.primary_gradient}}"), 1)
        self.assertEqual(TEMA_SOURCE.count("{{color:post_focus.primary_hover_border}}"), 3)
        self.assertEqual(get_theme("futurista").color("post_focus.primary_surface").value, "transparent")
        self.assertEqual(get_theme("futurista").color("post_focus.primary_hover_surface").value, "transparent")

    def test_qss_renderizado_permanece_normalizado_identico_ao_passo_2(self):
        styles = {"claro": tema.stylesheet_claro(), "escuro": tema.stylesheet_escuro(), "futurista": tema.stylesheet_futurista()}
        for theme_name, qss in styles.items():
            with self.subTest(theme=theme_name):
                baseline_qss = strip_navigation_search_layer(theme_name, qss)
                self.assertEqual(normalized_hash(baseline_qss), BASELINE_NORMALIZED_HASHES[theme_name])
                self.assertNotIn("{{color:", qss)
                self.assertNotIn("{{gradient:", qss)

    def test_codigo_de_fluxo_e_banco_permanecem_byte_a_byte(self):
        for name, expected in PROTECTED_HASHES.items():
            with self.subTest(name=name):
                actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                self.assertEqual(actual, expected)

    def test_fluxos_condicionais_do_pos_foco_continuam_presentes(self):
        self.assertIn('if resultado_questoes and int(resultado_questoes.get("respondidas") or 0) > 0:', FOCO_SOURCE)
        self.assertIn('em_jornada = str(self.dados.get("origem") or "") == "Jornada do Dia"', FOCO_SOURCE)
        self.assertIn('if em_jornada:', FOCO_SOURCE)
        self.assertIn('self.btn_revisao.setEnabled(False)', FOCO_SOURCE)
        self.assertIn('self.acao_escolhida = str(acao or "continuar")', FOCO_SOURCE)

    def test_passos_4_e_5_migram_pausa_e_jogos_sem_cruzar_contratos(self):
        self.assertIn("{{color:pause.timer_panel_surface}}", TEMA_SOURCE)
        self.assertIn("{{gradient:pause.primary_gradient}}", TEMA_SOURCE)
        self.assertIn("{{color:game.board_surface}}", TEMA_SOURCE)
        self.assertIn("{{gradient:game.primary_gradient}}", TEMA_SOURCE)

if __name__ == "__main__":
    unittest.main()
