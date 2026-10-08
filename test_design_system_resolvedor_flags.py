"""Contratos e regressões da Etapa 3E-B2c: flags Dúvida e Análise posterior."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest
from _design_system_test_helpers import strip_cards_global_block_a
from unittest.mock import patch

import tema
from ui.design import ALL_TOKENS, COMPONENT_TOKEN_COUNT, TokenKind, get_theme, token_spec

ROOT = Path(__file__).resolve().parent
QUEUE_DETAIL_RULE = re.compile(r'QDialog#questionSolverDialog QLabel#questionSessionSummaryDetail\s*\{[^{}]*\}', re.S)
SUMMARY_DIALOG_RULE = re.compile(r'QDialog#questionSessionSummaryDialog(?:\s+[^\{]+)?\s*\{[^{}]*\}', re.S)
D = "QCheckBox#questionSessionDoubt"
A = "QCheckBox#questionSessionAnalysisFlag"
ANCESTOR = "QDialog#questionSolverDialog "
VALUES = {'claro': {'flag_indicator_surface': '#FFFFFF',
           'doubt_text': '#475569',
           'doubt_checked_text': '#1D4ED8',
           'doubt_indicator_border': '#64748B',
           'doubt_indicator_hover_border': '#2563EB',
           'doubt_indicator_checked_surface': '#2563EB',
           'doubt_indicator_checked_border': '#1D4ED8',
           'doubt_indicator_disabled_surface': '#E2E8F0',
           'doubt_indicator_disabled_border': '#94A3B8',
           'analysis_text': '#64748B',
           'analysis_checked_text': '#92400E',
           'analysis_indicator_border': '#94A3B8',
           'analysis_indicator_hover_border': '#D97706',
           'analysis_indicator_checked_surface': '#F59E0B',
           'analysis_indicator_checked_border': '#B45309'},
 'escuro': {'flag_indicator_surface': '#111827',
            'doubt_text': '#CBD5E1',
            'doubt_checked_text': '#93C5FD',
            'doubt_indicator_border': '#94A3B8',
            'doubt_indicator_hover_border': '#60A5FA',
            'doubt_indicator_checked_surface': '#3B82F6',
            'doubt_indicator_checked_border': '#93C5FD',
            'doubt_indicator_disabled_surface': '#1F2937',
            'doubt_indicator_disabled_border': '#475569',
            'analysis_text': '#94A3B8',
            'analysis_checked_text': '#FBBF24',
            'analysis_indicator_border': '#64748B',
            'analysis_indicator_hover_border': '#F59E0B',
            'analysis_indicator_checked_surface': '#D97706',
            'analysis_indicator_checked_border': '#FBBF24'},
 'futurista': {'flag_indicator_surface': '#111827',
               'doubt_text': '#B7C1CD',
               'doubt_checked_text': '#AEB5FF',
               'doubt_indicator_border': '#94A3B8',
               'doubt_indicator_hover_border': '#60A5FA',
               'doubt_indicator_checked_surface': '#3B82F6',
               'doubt_indicator_checked_border': '#93C5FD',
               'doubt_indicator_disabled_surface': '#1F2937',
               'doubt_indicator_disabled_border': '#475569',
               'analysis_text': '#B7C1CD',
               'analysis_checked_text': '#F0C47C',
               'analysis_indicator_border': '#64748B',
               'analysis_indicator_hover_border': '#F59E0B',
               'analysis_indicator_checked_surface': '#D97706',
               'analysis_indicator_checked_border': '#FBBF24'}}
SOURCE_HASHES = {'main.py': '2cfc317db5716638499d945c505c0936909f3cbcb31f705e80bfedbe3cf641f4', 'foco.py': '8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed', 'checkpoint.py': '947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38', 'versao.py': 'c201d237e622dd2269838e54914458fd775c7ec1a91f07b518775ee833caa439'}
BASE_HASHES = {
    "claro": "94b7d97a21118db14d1490cd97f34bfe56ef26354ce7bf9d204a4355623269b9",
    "escuro": "52298070b2d47d90e738bb3a3951f0f3e0e8bbda0ecea1126ce715bfb6810be5",
    "futurista": "1b79f426349812489f69acbd0746bfd0f2ec1286fb84f70e411478588744225d",
}



def strip_dashboard_block_a(theme_name, qss):
    # Bloco F é posterior a este contrato histórico; retire-o primeiro.
    if theme_name == "futurista":
        qss = qss.replace(tema.render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_H), "", 1)
        qss = qss.replace(tema.render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_H), "", 1)
    else:
        qss = qss.replace(tema.render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_H), "", 1)
    if theme_name == "futurista":
        qss = qss.replace(tema.render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_G), "", 1)
        qss = qss.replace(tema.render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_G), "", 1)
    else:
        qss = qss.replace(tema.render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_G), "", 1)
    if theme_name == "futurista":
        qss = qss.replace(tema.render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_F), "", 1)
        qss = qss.replace(tema.render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_F), "", 1)
    else:
        qss = qss.replace(tema.render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_F), "", 1)
    # Bloco E é posterior a este contrato histórico; retire-o em seguida.
    if theme_name == "futurista":
        qss = qss.replace(tema.render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_E), "", 1)
        qss = qss.replace(tema.render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_E), "", 1)
    else:
        qss = qss.replace(tema.render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_E), "", 1)
    # Bloco D é posterior a este contrato histórico; retire-o em seguida.
    if theme_name == "futurista":
        qss = qss.replace(tema.render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_D), "", 1)
        qss = qss.replace(tema.render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_D), "", 1)
    else:
        qss = qss.replace(tema.render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_D), "", 1)
    # Bloco C é posterior a este contrato histórico; retire-o antes dos blocos B/A.
    if theme_name == "futurista":
        qss = qss.replace(tema.render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_C), "", 1)
        qss = qss.replace(tema.render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_C), "", 1)
    else:
        qss = qss.replace(tema.render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_C), "", 1)
    # Bloco B é posterior a este contrato histórico; retire-o antes do Bloco A.
    if theme_name == "futurista":
        qss = qss.replace(
            tema.render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_B_ESCURO), "", 1
        )
        qss = qss.replace(
            tema.render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_B_FUTURISTA), "", 1
        )
    else:
        bloco_b = (
            tema.ESTILO_DASHBOARD_BLOCO_B_CLARO
            if theme_name == "claro"
            else tema.ESTILO_DASHBOARD_BLOCO_B_ESCURO
        )
        qss = qss.replace(tema.render_qss(theme_name, bloco_b), "", 1)
    if theme_name == "futurista":
        qss = qss.replace(
            tema.render_qss("escuro", tema.ESTILO_DASHBOARD_SHELL_ESCURO), "", 1
        )
        qss = qss.replace(
            tema.render_qss("futurista", tema.ESTILO_DASHBOARD_SHELL_FUTURISTA), "", 1
        )
        return qss
    constant = (
        tema.ESTILO_DASHBOARD_SHELL_CLARO
        if theme_name == "claro"
        else tema.ESTILO_DASHBOARD_SHELL_ESCURO
    )
    return qss.replace(tema.render_qss(theme_name, constant), "", 1)

def canonical(value):
    value = re.sub(r"#[0-9A-Fa-f]{3,8}\b", lambda m: m[0].upper(), value)
    return re.sub(r"\s+", " ", value).strip()


def raw(name):
    with patch.object(tema, "render_qss", side_effect=lambda name, source: source):
        if name == "futurista":
            with patch.object(tema, "stylesheet_escuro", return_value=""):
                return tema.stylesheet_futurista()
        return getattr(tema, "stylesheet_" + name)()


def rules(source):
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    placeholders = {}
    def mask(m):
        key = "PLACEHOLDER_" + str(len(placeholders))
        placeholders[key] = m[0]
        return key
    source = re.sub(r"\{\{[^{}]+\}\}", mask, source)
    out = []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", source):
        body = re.sub(r"PLACEHOLDER_\d+", lambda match: placeholders[match[0]], m[2])
        props = dict(item.strip().split(":", 1) for item in body.split(";") if item.strip())
        props = {key: value.strip() for key, value in props.items()}
        for selector in m[1].split(","):
            out.append((selector.strip(), props))
    return out


def block(source, selector):
    matches = [props for s, props in rules(source) if s == selector]
    if len(matches) != 1:
        raise AssertionError((selector, len(matches)))
    return matches[0]


def token(key):
    return "{{color:session." + key + "}}"



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

class SessionFlagsTests(unittest.TestCase):
    def test_exact_fifteen_new_component_color_tokens(self):
        expected = {"session." + key for key in VALUES["claro"]}
        actual = {s.path for s in ALL_TOKENS if s.path.startswith(("session.doubt_", "session.analysis_", "session.flag_"))}
        self.assertEqual(actual, expected)
        self.assertEqual(len(expected), 15)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 928)
        self.assertEqual(len(ALL_TOKENS), 1030)
        for name in expected:
            self.assertIs(token_spec(name).kind, TokenKind.COLOR)

    def test_values_in_each_theme(self):
        for name, values in VALUES.items():
            for key, color in values.items():
                with self.subTest(theme=name, token=key):
                    self.assertEqual(get_theme(name).color("session." + key).value, color)

    def assert_consumers(self, selector, expected):
        for name in ("claro", "escuro"):
            with self.subTest(theme=name, selector=selector):
                props = block(raw(name), selector)
                for prop, value in expected.items():
                    self.assertEqual(props[prop], value)
                self.assertNotRegex(";".join(props.values()), r"#[0-9A-Fa-f]{6}\b")

    def test_doubt_normal_uses_only_its_semantic_colors(self):
        self.assert_consumers(D, {'color': '{{color:session.doubt_text}}'})

    def test_doubt_checked_uses_only_its_semantic_colors(self):
        self.assert_consumers(D + ":checked", {'color': '{{color:session.doubt_checked_text}}'})

    def test_doubt_indicator_uses_only_its_semantic_colors(self):
        self.assert_consumers(D + "::indicator", {'background-color': '{{color:session.flag_indicator_surface}}', 'border': '2px solid {{color:session.doubt_indicator_border}}'})

    def test_doubt_hover_uses_only_its_semantic_colors(self):
        self.assert_consumers(D + "::indicator:hover", {'border-color': '{{color:session.doubt_indicator_hover_border}}'})

    def test_doubt_indicator_checked_uses_only_its_semantic_colors(self):
        self.assert_consumers(D + "::indicator:checked", {'background-color': '{{color:session.doubt_indicator_checked_surface}}', 'border-color': '{{color:session.doubt_indicator_checked_border}}'})

    def test_doubt_disabled_uses_only_its_semantic_colors(self):
        self.assert_consumers(D + "::indicator:disabled", {'background-color': '{{color:session.doubt_indicator_disabled_surface}}', 'border-color': '{{color:session.doubt_indicator_disabled_border}}'})

    def test_analysis_normal_uses_only_its_semantic_colors(self):
        self.assert_consumers(A, {'color': '{{color:session.analysis_text}}'})

    def test_analysis_checked_uses_only_its_semantic_colors(self):
        self.assert_consumers(A + ":checked", {'color': '{{color:session.analysis_checked_text}}'})

    def test_analysis_indicator_uses_only_its_semantic_colors(self):
        self.assert_consumers(A + "::indicator", {'background-color': '{{color:session.flag_indicator_surface}}', 'border': '2px solid {{color:session.analysis_indicator_border}}'})

    def test_analysis_hover_uses_only_its_semantic_colors(self):
        self.assert_consumers(A + "::indicator:hover", {'border-color': '{{color:session.analysis_indicator_hover_border}}'})

    def test_analysis_indicator_checked_uses_only_its_semantic_colors(self):
        self.assert_consumers(A + "::indicator:checked", {'background-color': '{{color:session.analysis_indicator_checked_surface}}', 'border-color': '{{color:session.analysis_indicator_checked_border}}'})

    def test_shared_surface_has_only_two_normal_consumers_per_legacy_theme(self):
        for name in ("claro", "escuro"):
            consumers = [(s, p) for s, p in rules(raw(name)) if token("flag_indicator_surface") in p.values()]
            self.assertEqual(consumers, [
                (D + "::indicator", block(raw(name), D + "::indicator")),
                (A + "::indicator", block(raw(name), A + "::indicator")),
            ])
        self.assertNotIn(token("flag_indicator_surface"), raw("futurista"))

    def test_hover_only_overrides_indicator_border(self):
        for name in ("claro", "escuro"):
            for selector in (D, A):
                self.assertEqual(set(block(raw(name), selector + "::indicator:hover")), {"border-color"})

    def test_hover_before_checked_and_doubt_disabled_after_checked(self):
        for name in ("claro", "escuro"):
            ordered = [s for s, _ in rules(raw(name))]
            for selector in (D, A):
                self.assertLess(ordered.index(selector + "::indicator:hover"), ordered.index(selector + "::indicator:checked"))
            self.assertLess(ordered.index(D + "::indicator:checked"), ordered.index(D + "::indicator:disabled"))

    def test_no_additional_flag_states_or_ancestor_on_legacy_selectors(self):
        expected = [D, D+":checked", D+"::indicator", D+"::indicator:hover", D+"::indicator:checked", D+"::indicator:disabled",
                    A, A+":checked", A+"::indicator", A+"::indicator:hover", A+"::indicator:checked"]
        for name in ("claro", "escuro"):
            actual = [s for s, _ in rules(raw(name)) if "questionSessionDoubt" in s or "questionSessionAnalysisFlag" in s]
            self.assertEqual(actual, expected)
        for name in VALUES:
            for s, _ in rules(raw(name)):
                if "questionSessionDoubt" in s or "questionSessionAnalysisFlag" in s:
                    self.assertNotRegex(s, r":(?:pressed|focus|focus-visible|unchecked|indeterminate)")
                    self.assertNotIn(":checked:hover", s)
                    if "questionSessionAnalysisFlag" in s:
                        self.assertNotIn(":disabled", s)

    def test_transparency_padding_spacing_and_weights_preserved(self):
        for name in ("claro", "escuro"):
            for selector, weight, spacing, padding in ((D,"700","9px","4px 0"), (A,"600","7px","4px 8px")):
                props = block(raw(name), selector)
                self.assertEqual({k: props[k] for k in ("background","font-weight","spacing","padding")},
                                 {"background":"transparent","font-weight":weight,"spacing":spacing,"padding":padding})
            self.assertEqual(block(raw(name), A+":checked")["font-weight"], "700")
            self.assertEqual(set(block(raw(name), D+":checked")), {"color"})

    def test_indicator_dimensions_radius_and_border_are_preserved(self):
        for name in ("claro", "escuro"):
            for selector, size, radius in ((D,"20px","5px"), (A,"16px","4px")):
                props = block(raw(name), selector+"::indicator")
                self.assertEqual((props["width"],props["height"],props["border-radius"]), (size,size,radius))
                self.assertTrue(props["border"].startswith("2px solid "))
                self.assertEqual(set(props), {"background-color","border","border-radius","width","height"})

    def test_futuristic_text_tokens_are_semantically_separate(self):
        source = raw("futurista")
        for selector, key in ((D,"doubt"),(A,"analysis")):
            normal = [p for s, p in rules(source) if s == ANCESTOR+selector]
            self.assertEqual(normal, [{"background":"transparent","font-size":"8.6pt"}, {"color":token(key+"_text")}])
            self.assertEqual(block(source, ANCESTOR+selector+":checked"), {"color":token(key+"_checked_text")})
        self.assertNotIn("text.on_action", "\n".join(str(p) for s,p in rules(source) if "questionSessionDoubt" in s or "questionSessionAnalysisFlag" in s))

    def test_futuristic_group_and_adjacent_normal_checked_order(self):
        source = raw("futurista")
        # Parsed groups emit two selector entries; no other rule is interleaved.
        selected = [(s,p) for s,p in rules(source) if s.startswith(ANCESTOR) and ("questionSessionDoubt" in s or "questionSessionAnalysisFlag" in s)]
        self.assertEqual([s for s,p in selected], [ANCESTOR+D, ANCESTOR+A, ANCESTOR+D, ANCESTOR+A, ANCESTOR+D+":checked", ANCESTOR+A+":checked"])
        self.assertEqual(selected[0][1], {"background":"transparent","font-size":"8.6pt"})
        self.assertEqual(selected[1][1], selected[0][1])

    def test_dark_prefix_is_resolved_first_with_dark_tokens(self):
        dark = tema.stylesheet_escuro()
        futuristic = tema.stylesheet_futurista()
        self.assertTrue(futuristic.startswith(dark))
        self.assertIn("color: #CBD5E1;", dark)
        self.assertIn("color: #93C5FD;", dark)
        self.assertIn("color: #B7C1CD;", futuristic[len(dark):])
        self.assertNotIn("{{", futuristic)
        source = (ROOT/"tema.py").read_text(encoding="utf-8")
        self.assertIn('return stylesheet_escuro() + render_qss("futurista",', source)

    def test_futuristic_has_no_own_flag_indicator_override(self):
        source = raw("futurista")
        self.assertFalse(any("::indicator" in s and ("questionSessionDoubt" in s or "questionSessionAnalysisFlag" in s) for s,p in rules(source)))
        dark = rules(tema.stylesheet_escuro())
        futuristic = rules(tema.stylesheet_futurista())
        for selector in (D,A):
            for suffix in ("::indicator","::indicator:hover","::indicator:checked"):
                self.assertEqual([p for s,p in futuristic if s==selector+suffix], [p for s,p in dark if s==selector+suffix])
        self.assertEqual(block(tema.stylesheet_futurista(),D+"::indicator")["background-color"], "#111827")
        self.assertEqual(block(tema.stylesheet_futurista(),A+"::indicator")["border"], "2px solid #64748B")

    def test_original_runtime_layout_focus_checkpoint_and_metadata_bytes(self):
        for filename, digest in SOURCE_HASHES.items():
            with self.subTest(file=filename):
                data = (ROOT/filename).read_bytes()
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

    def test_entire_qss_is_identical_after_reversing_only_authorized_split(self):
        # Baseline estrutural avançado no Passo 4 apenas pela separação autorizada
        # dos grupos pause/game; o teste específico do Passo 4 prova equivalência efetiva.
        for name, digest in BASE_HASHES.items():
            source = getattr(tema,"stylesheet_"+name)()
            source = strip_navigation_search_layer(name, source)
            source = strip_dashboard_block_a(name, source)
            source = QUEUE_DETAIL_RULE.sub("", source)
            source = SUMMARY_DIALOG_RULE.sub("", source)
            if name == "futurista":
                group = ANCESTOR+D+",\n"+ANCESTOR+A
                changed = group+" {\n    background: transparent;\n    font-size: 8.6pt;\n}\n"+ANCESTOR+D+" { color: #B7C1CD; }\n"+ANCESTOR+A+" { color: #B7C1CD; }"
                original = group+" {\n    color: #B7C1CD;\n    background: transparent;\n    font-size: 8.6pt;\n}"
                self.assertEqual(source.count(changed), 1)
                source = source.replace(changed,original)
            self.assertEqual(hashlib.sha256(canonical(source).encode()).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main()
