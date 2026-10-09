"""Contratos e regressões da Etapa 3E-B2b2: painel inferior, Pular e Encerrar."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest
from _design_system_test_helpers import strip_cards_global_block_a

import tema

# 3E-B2c: o hash Futurista muda apenas pela separação autorizada da cor
# normal das flags; equivalência integral com B2b2 validada no teste de flags.
from ui.design import ALL_TOKENS, COMPONENT_TOKEN_COUNT, TokenKind, get_theme, token_spec

ROOT = Path(__file__).resolve().parent
VALUES = {'claro': {'action_panel_surface': '#FFFFFF',
           'action_panel_border': '#DDE4EC',
           'skip_surface': '#F5F7FA',
           'skip_text': '#4F5D6E',
           'skip_border': '#CCD5DF',
           'skip_hover_surface': '#EDF1F5',
           'skip_hover_text': '#4F5D6E',
           'skip_hover_border': '#AFBAC8',
           'end_surface': '#FFF7F8',
           'end_text': '#A54050',
           'end_border': '#E9BCC4',
           'end_hover_surface': '#FFF0F2',
           'end_hover_text': '#A54050',
           'end_hover_border': '#DC929E'},
 'escuro': {'action_panel_surface': '#182230',
            'action_panel_border': '#344154',
            'skip_surface': '#202B39',
            'skip_text': '#C8D1DC',
            'skip_border': '#445265',
            'skip_hover_surface': '#273444',
            'skip_hover_text': '#C8D1DC',
            'skip_hover_border': '#607086',
            'end_surface': '#2B2027',
            'end_text': '#FFB8C2',
            'end_border': '#724350',
            'end_hover_surface': '#38262D',
            'end_hover_text': '#FFB8C2',
            'end_hover_border': '#985766'},
 'futurista': {'action_panel_surface': '#171F2B',
               'action_panel_border': '#3A4656',
               'skip_surface': '#202833',
               'skip_text': '#CED6E0',
               'skip_border': '#505B69',
               'skip_hover_surface': '#293341',
               'skip_hover_text': '#FFFFFF',
               'skip_hover_border': '#707C8B',
               'end_surface': '#2A2026',
               'end_text': '#FFBAC4',
               'end_border': '#70434F',
               'end_hover_surface': '#38262E',
               'end_hover_text': '#FFD5DB',
               'end_hover_border': '#9A5968'}}
HASHES = {
    "claro": "71c6c022b5fb4a3798f5bb9f837fc55fc9fa3bf4d558832688dd7fb25d8c7cdb",
    "escuro": "25dd9d735b8aa542020a05bbc3318cc91aba79f0b2f89995cea0a272d8bc1056",
    "futurista": "0e1011b5790c7a6f775d70ef4a59dd60a4c1587de412e9533bed2e39b1cba14f",
}
SELECTORS = (
    "QDialog#questionSolverDialog QFrame#questionSessionActionPanel",
    "QDialog#questionSolverDialog QPushButton#questionSessionSkipButton",
    "QDialog#questionSolverDialog QPushButton#questionSessionSkipButton:hover",
    "QDialog#questionSolverDialog QPushButton#questionSessionEndButton",
    "QDialog#questionSolverDialog QPushButton#questionSessionEndButton:hover",
)
SOURCE_HASHES = {'checkpoint.py': '947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38',
 'foco.py': '8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed',
 'main.py': 'a8713479507a481991bf4fde56e394865823eba3d5e96ccfa08b7ad1db7e3f29'}


def canonical(qss):
    return re.sub(r"\s+", " ", re.sub(r"#[0-9A-Fa-f]{3,8}\b", lambda m: m[0].upper(), qss)).strip()


def template(name):
    return getattr(tema, "ESTILO_RESOLVEDOR_" + name.upper())


def block(qss, selector):
    matches = re.findall(re.escape(selector) + r"\s*\{(.*?)\n\}", qss, re.S)
    if len(matches) != 1:
        raise AssertionError((selector, len(matches)))
    return matches[0]



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

class SessionActionPanelTests(unittest.TestCase):
    def test_exact_fifteen_new_component_tokens_and_kinds(self):
        expected = {"session." + key for key in VALUES["claro"]} | {"session.action_panel_gradient"}
        actual = {spec.path for spec in ALL_TOKENS if spec.path.startswith(("session.action_panel_", "session.skip_", "session.end_"))}
        self.assertEqual(actual, expected)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 1148)
        self.assertEqual(len(ALL_TOKENS), 1250)
        for path in expected:
            with self.subTest(token=path):
                kind = TokenKind.GRADIENT if path.endswith("_gradient") else TokenKind.COLOR
                self.assertEqual(token_spec(path).kind, kind)

    def test_color_values_in_all_three_themes(self):
        for name, colors in VALUES.items():
            for key, value in colors.items():
                with self.subTest(theme=name, token=key):
                    self.assertEqual(get_theme(name).color("session." + key).value, value)

    def test_horizontal_gradient_contract_in_all_three_themes(self):
        for name, stops in {"claro": ("#FFFFFF", "#FFFFFF"), "escuro": ("#182230", "#182230"), "futurista": ("#171F2B", "#151D28")}.items():
            with self.subTest(theme=name):
                spec = get_theme(name).gradient("session.action_panel_gradient")
                d = spec.direction
                self.assertEqual((d.x1, d.y1, d.x2, d.y2), (0, 0, 1, 0))
                self.assertEqual(tuple((s.position, s.color.value) for s in spec.stops), tuple(zip((0, 1), stops)))

    def test_panel_preserves_solid_backgrounds_and_futuristic_gradient(self):
        for name in VALUES:
            with self.subTest(theme=name):
                panel = block(template(name), SELECTORS[0])
                expected = "background: {{gradient:session.action_panel_gradient}};" if name == "futurista" else "background-color: {{color:session.action_panel_surface}};"
                self.assertIn(expected, panel)
                self.assertIn("border: 1px solid {{color:session.action_panel_border}};", panel)
                self.assertIn("border-radius: 13px;", panel)
                self.assertEqual(panel.count(";"), 3)
                self.assertNotRegex(panel, r"#[0-9A-Fa-f]{6}\b")

    def test_buttons_consume_only_normal_and_hover_tokens(self):
        for name in VALUES:
            for prefix, offset in (("skip", 1), ("end", 3)):
                with self.subTest(theme=name, button=prefix):
                    normal = block(template(name), SELECTORS[offset])
                    hover = block(template(name), SELECTORS[offset + 1])
                    for prop, suffix in (("background-color", "surface"), ("color", "text"), ("border: 1px solid", "border")):
                        declaration = (prop + " " if prop.startswith("border:") else prop + ": ") + "{{color:session." + prefix + "_" + suffix + "}};"
                        self.assertIn(declaration, normal)
                    self.assertIn("background-color: {{color:session." + prefix + "_hover_surface}};", hover)
                    self.assertIn("border-color: {{color:session." + prefix + "_hover_border}};", hover)
                    self.assertNotRegex(normal + hover, r"#[0-9A-Fa-f]{6}\b")

    def test_hover_text_is_explicit_only_in_futuristic_theme(self):
        for name in VALUES:
            for prefix, offset in (("skip", 2), ("end", 4)):
                hover = block(template(name), SELECTORS[offset])
                text = "color: {{color:session." + prefix + "_hover_text}};"
                if name == "futurista":
                    self.assertIn(text, hover)
                else:
                    self.assertNotRegex(hover, r"(?m)^\s*color\s*:")

    def test_existing_radius_weight_and_declaration_counts_are_preserved(self):
        for name in VALUES:
            for offset in (1, 3):
                normal = block(template(name), SELECTORS[offset])
                self.assertIn("border-radius: " + ("10px;" if name == "futurista" else "9px;"), normal)
                self.assertIn("font-weight: " + ("800;" if name == "futurista" else "750;"), normal)
                self.assertEqual(normal.count(";"), 5)
                self.assertEqual(block(template(name), SELECTORS[offset + 1]).count(";"), 3 if name == "futurista" else 2)

    def test_no_specific_pressed_disabled_checked_or_extra_state(self):
        for name in VALUES:
            masked = re.sub(r"\{\{[^{}]+\}\}", "TOKEN", template(name))
            selectors = re.findall(r"([^{}]+)\{[^{}]*\}", masked)
            targets = [s.strip() for s in selectors if any(ident in s for ident in ("questionSessionActionPanel", "questionSessionSkipButton", "questionSessionEndButton"))]
            self.assertEqual(targets, list(SELECTORS))

    def test_entire_resolved_stylesheet_matches_base_including_shared_groups(self):
        # Covers every selector, value, declaration, state and rule order,
        # including global buttons, harmonized End groups, navigation and timer.
        for name, digest in HASHES.items():
            with self.subTest(theme=name):
                resolved = getattr(tema, "stylesheet_" + name)()
                resolved = strip_navigation_search_layer(name, resolved)
                self.assertEqual(hashlib.sha256(canonical(resolved).encode()).hexdigest(), digest)

    def test_futuristic_retains_dark_layer_resolved_with_dark_values(self):
        dark = tema.stylesheet_escuro()
        futuristic = tema.stylesheet_futurista()
        self.assertTrue(futuristic.startswith(dark))
        self.assertIn("background-color: #202B39;", dark)
        self.assertIn("background-color: #202833;", futuristic[len(dark):])
        self.assertNotIn("{{", futuristic)

    def test_python_layout_behavior_focus_and_checkpoint_are_byte_identical(self):
        for filename, digest in SOURCE_HASHES.items():
            with self.subTest(file=filename):
                data = (ROOT / filename).read_bytes()
                if filename == "main.py":
                    data = data.replace(
                        b"from ui.design import fixed_qss_color, qcolor, qss_color\n",
                        b"from ui.design import fixed_qss_color, qcolor\n",
                        1,
                    )
                    data = data.replace(
                        b'                if tema_atual == "futurista":\n                    botao.setStyleSheet(\n                        f"background-color:{qss_color(\'futurista\', \'dashboard.disciplines_disabled_surface\')}; "\n                        f"color:{qss_color(\'futurista\', \'dashboard.disciplines_disabled_text\')}; "\n                        f"border:1px solid {qss_color(\'futurista\', \'dashboard.disciplines_disabled_border\')}; "\n                        "text-align:left; padding-left:14px;"\n                    )\n                elif tema_atual == "escuro":\n                    botao.setStyleSheet(\n                        f"background-color:{qss_color(\'escuro\', \'dashboard.disciplines_disabled_surface\')}; "\n                        f"color:{qss_color(\'escuro\', \'dashboard.disciplines_disabled_text\')}; "\n                        f"border:1px solid {qss_color(\'escuro\', \'dashboard.disciplines_disabled_border\')}; "\n                        "text-align:left; padding-left:14px;"\n                    )\n                else:\n                    botao.setStyleSheet(\n                        f"background-color:{qss_color(\'claro\', \'dashboard.disciplines_disabled_surface\')}; "\n                        f"color:{qss_color(\'claro\', \'dashboard.disciplines_disabled_text\')}; "\n                        f"border:1px solid {qss_color(\'claro\', \'dashboard.disciplines_disabled_border\')}; "\n                        "text-align:left; padding-left:14px;"\n                    )\n',
                        b'                if tema_atual == "futurista":\n                    botao.setStyleSheet(\n                        "background-color:#173244; color:#8FA8B8; "\n                        "border:1px solid #466477; text-align:left; padding-left:14px;"\n                    )\n                elif tema_atual == "escuro":\n                    botao.setStyleSheet(\n                        "background-color:#28313d; color:#94A3B8; "\n                        "border:1px solid #475569; text-align:left; padding-left:14px;"\n                    )\n                else:\n                    botao.setStyleSheet(\n                        "background-color:#E2E8F0; color:#64748B; "\n                        "border:1px solid #CBD5E1; text-align:left; padding-left:14px;"\n                    )\n',
                        1,
                    )
                    data = data.replace(b'        self.setObjectName("questionSessionSummaryDialog")\n', b'')
                self.assertEqual(hashlib.sha256(data).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main()
