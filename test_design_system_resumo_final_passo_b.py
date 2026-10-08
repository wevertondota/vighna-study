"""Contrato da Etapa 3E-C, Passo B: painéis condicionais do resumo final."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest
from _design_system_test_helpers import strip_cards_global_block_a

import tema
from ui.design import ALL_TOKENS, COMPONENT_TOKEN_COUNT, SEMANTIC_TOKEN_COUNT, TokenKind, get_theme, token_spec
from versao import VIGHNA_BUILD, VIGHNA_SCHEMA, VIGHNA_VERSION

ROOT = Path(__file__).resolve().parent
TEMA_SOURCE = (ROOT / "tema.py").read_text(encoding="utf-8")
MAIN_SOURCE = (ROOT / "main.py").read_text(encoding="utf-8")
PALETTE_SOURCE = (ROOT / "ui/design/palette.py").read_text(encoding="utf-8")

COLOR_TOKENS = {
    "summary.adaptive_surface", "summary.adaptive_border", "summary.adaptive_title_text", "summary.adaptive_text",
    "summary.effectiveness_surface", "summary.effectiveness_border", "summary.effectiveness_title_text",
    "summary.effectiveness_metric_surface", "summary.effectiveness_metric_border",
    "summary.effectiveness_metric_label_text", "summary.effectiveness_metric_value_text",
    "summary.mock_exam_section_title_text", "summary.mock_exam_notice_surface",
    "summary.mock_exam_notice_text", "summary.mock_exam_notice_border",
}
GRADIENT_TOKENS = {"summary.adaptive_gradient", "summary.effectiveness_gradient"}
PASS_B_TOKENS = COLOR_TOKENS | GRADIENT_TOKENS

EXPECTED_COLORS = {
    "claro": {
        "summary.adaptive_surface":"#F8FBFF", "summary.adaptive_border":"#BFDBFE", "summary.adaptive_title_text":"#1E3A8A", "summary.adaptive_text":"#334155",
        "summary.effectiveness_surface":"#F8FBFF", "summary.effectiveness_border":"#BFDBFE", "summary.effectiveness_title_text":"#1E3A8A",
        "summary.effectiveness_metric_surface":"#FFFFFF", "summary.effectiveness_metric_border":"#DBEAFE",
        "summary.effectiveness_metric_label_text":"#64748B", "summary.effectiveness_metric_value_text":"#111827",
        "summary.mock_exam_section_title_text":"#111827", "summary.mock_exam_notice_surface":"#F5F3FF",
        "summary.mock_exam_notice_text":"#5B21B6", "summary.mock_exam_notice_border":"#C4B5FD",
    },
    "escuro": {
        "summary.adaptive_surface":"#172033", "summary.adaptive_border":"#1E3A8A", "summary.adaptive_title_text":"#93C5FD", "summary.adaptive_text":"#CBD5E1",
        "summary.effectiveness_surface":"#172033", "summary.effectiveness_border":"#1E3A8A", "summary.effectiveness_title_text":"#93C5FD",
        "summary.effectiveness_metric_surface":"#182235", "summary.effectiveness_metric_border":"#334155",
        "summary.effectiveness_metric_label_text":"#94A3B8", "summary.effectiveness_metric_value_text":"#F8FAFC",
        "summary.mock_exam_section_title_text":"#F8FAFC", "summary.mock_exam_notice_surface":"#2E1065",
        "summary.mock_exam_notice_text":"#DDD6FE", "summary.mock_exam_notice_border":"#7C3AED",
    },
    "futurista": {
        "summary.adaptive_surface":"#12283F", "summary.adaptive_border":"#37628A", "summary.adaptive_title_text":"#AEEEFF", "summary.adaptive_text":"#CBD5E1",
        "summary.effectiveness_surface":"#12283F", "summary.effectiveness_border":"#37628A", "summary.effectiveness_title_text":"#AEEEFF",
        "summary.effectiveness_metric_surface":"#182235", "summary.effectiveness_metric_border":"#334155",
        "summary.effectiveness_metric_label_text":"#94A3B8", "summary.effectiveness_metric_value_text":"#F8FAFC",
        "summary.mock_exam_section_title_text":"#F8FAFC", "summary.mock_exam_notice_surface":"#2E1065",
        "summary.mock_exam_notice_text":"#DDD6FE", "summary.mock_exam_notice_border":"#7C3AED",
    },
}
EXPECTED_GRADIENT_STOPS = {
    "claro": ("#F8FBFF", "#F8FBFF"),
    "escuro": ("#172033", "#172033"),
    "futurista": ("#12283F", "#09192B"),
}
PASS_A_NORMALIZED = {
    "claro":"828f96d828f7dadc111451769650ef83ee5fb5b774a43ac8bc22d3cfd1f8d9f9",
    "escuro":"7479dce86b49ddc9afdbf844b9217232f40aa4ec160069af7877d2cc5cbd39fa",
    "futurista":"6862f94c1f93abf7100ddddbf13b18759fcce4acc13a1a13ba119c4d10678239",
}
CURRENT_NORMALIZED = {
    "claro":"c8975fa69de340d0fd51e2d5a1b4d91477286cadfddd1a9fe1c77e71a51ed8e3",
    "escuro":"250d6f47d8fa10e4b6aee8e9692053693094f1d25e7c92a5b1c45da96eeb46c5",
    "futurista":"c5dc8d9ad8681a5b10fae61326ceb5b795873feb6453fb66f05b9accaa600b48",
}
PASS_B_MARKERS = (
    "#adaptiveSummaryCard", "#adaptiveSummaryTitle", "#adaptiveSummaryText",
    "#effectivenessImpactCard", "#effectivenessImpactTitle", "#effectivenessImpactMetric",
    "#effectivenessImpactLabel", "#effectivenessImpactFooter", "#effectivenessImpactValue",
    "#mockExamResultSectionTitle", "#mockExamCorrectionNotice",
)
SUMMARY_RULE = re.compile(r"(?ms)^    QDialog#questionSessionSummaryDialog[^\n{]*(?:\n    QDialog#questionSessionSummaryDialog[^\n{]*)*\s*\{.*?^    \}\n?")



def strip_navigation_layer(theme_name: str, qss: str) -> str:
    qss = strip_cards_global_block_a(tema, theme_name, qss)
    if theme_name == "futurista":
        final_back = tema.render_qss("futurista", tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
        inherited_back = tema.render_qss("escuro", tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
        if qss.endswith(final_back):
            qss = qss[:-len(final_back)]
        elif final_back in qss:
            qss = qss.replace(final_back, "", 1)
        if inherited_back in qss:
            qss = qss.replace(inherited_back, "", 1)
    else:
        back_layer = tema.render_qss(theme_name, tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
        if qss.endswith(back_layer):
            qss = qss[:-len(back_layer)]
        elif back_layer in qss:
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


def strip_dashboard_block_a(theme_name, qss):
    qss = strip_navigation_layer(theme_name, qss)
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

def canonical(value: str) -> str:
    value = re.sub(r"#[0-9A-Fa-f]{3,8}\b", lambda m: m.group(0).upper(), value)
    return re.sub(r"\s+", " ", value).strip()


def strip_pass_b_rules(qss: str) -> str:
    def repl(match: re.Match[str]) -> str:
        block = match.group(0)
        return "" if any(marker in block for marker in PASS_B_MARKERS) else block
    return SUMMARY_RULE.sub(repl, qss)


class SummaryFinalPassBTests(unittest.TestCase):
    def test_exact_seventeen_pass_b_tokens_and_final_counts(self) -> None:
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 1004)
        self.assertEqual(len(ALL_TOKENS), 1106)
        paths = {t.path for t in ALL_TOKENS}
        self.assertTrue(PASS_B_TOKENS <= paths)
        self.assertEqual(len(PASS_B_TOKENS), 17)
        for path in COLOR_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.COLOR)
        for path in GRADIENT_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.GRADIENT)

    def test_values_match_characterization_in_all_themes(self) -> None:
        for theme_name, expected in EXPECTED_COLORS.items():
            theme = get_theme(theme_name)
            for path, value in expected.items():
                self.assertEqual(theme.color(path).value, value, (theme_name, path))
            for path in GRADIENT_TOKENS:
                gradient = theme.gradient(path)
                self.assertEqual((gradient.direction.x1, gradient.direction.y1, gradient.direction.x2, gradient.direction.y2), (0.0,0.0,1.0,1.0))
                self.assertEqual(tuple(stop.color.value for stop in gradient.stops), EXPECTED_GRADIENT_STOPS[theme_name])

    def test_only_missing_physical_colors_were_registered(self) -> None:
        for color in ("#F8FBFF", "#12283F", "#09192B", "#37628A", "#AEEEFF", "#5B21B6"):
            self.assertIn(f'"{color}"', PALETTE_SOURCE)

    def test_scoped_rules_preserve_solid_light_dark_and_gradient_futuristic(self) -> None:
        rules = [r for r in SUMMARY_RULE.findall(TEMA_SOURCE) if any(m in r for m in PASS_B_MARKERS)]
        self.assertEqual(len(rules), 24)  # 10 Claro + 10 Escuro + 4 Futuristas.
        joined = "\n".join(rules)
        for forbidden in ("border-radius", "padding", "font-size", "font-weight", "margin"):
            self.assertNotIn(forbidden, joined)
        self.assertEqual(joined.count("{{gradient:summary.adaptive_gradient}}"), 1)
        self.assertEqual(joined.count("{{gradient:summary.effectiveness_gradient}}"), 1)
        self.assertEqual(joined.count("{{color:summary.adaptive_surface}}"), 2)
        self.assertEqual(joined.count("{{color:summary.effectiveness_surface}}"), 2)
        self.assertEqual(joined.count("{{color:summary.adaptive_border}}"), 3)
        self.assertEqual(joined.count("{{color:summary.effectiveness_border}}"), 3)
        self.assertEqual(joined.count("{{color:summary.adaptive_title_text}}"), 3)
        self.assertEqual(joined.count("{{color:summary.effectiveness_title_text}}"), 3)
        for path in (
            "summary.adaptive_text", "summary.effectiveness_metric_surface", "summary.effectiveness_metric_border",
            "summary.effectiveness_metric_label_text", "summary.effectiveness_metric_value_text",
            "summary.mock_exam_section_title_text", "summary.mock_exam_notice_surface",
            "summary.mock_exam_notice_text", "summary.mock_exam_notice_border",
        ):
            self.assertEqual(joined.count(f"{{{{color:{path}}}}}"), 2, path)

    def test_shared_legacy_rules_and_dependencies_remain_literal(self) -> None:
        self.assertIn("QFrame#adaptiveSummaryCard {\n        background-color: #f8fbff;", TEMA_SOURCE)
        self.assertIn("QFrame#adaptiveSummaryCard {\n        background-color: #172033;", TEMA_SOURCE)
        self.assertIn("QFrame#effectivenessImpactCard {\n        background-color: #f8fbff;", TEMA_SOURCE)
        self.assertIn("QFrame#effectivenessImpactCard {\n        background-color: #172033;", TEMA_SOURCE)
        self.assertIn("QLabel#mockExamCorrectionNotice {\n        background-color: #f5f3ff;", TEMA_SOURCE)
        self.assertIn("QLabel#mockExamCorrectionNotice {\n        background-color: #2e1065;", TEMA_SOURCE)
        self.assertNotIn("QPushButton#primaryButton {\n        background-color: {{color:summary.", TEMA_SOURCE)
        self.assertNotIn("QPushButton#subtleButton {\n        background-color: {{color:summary.", TEMA_SOURCE)
        self.assertIn('self.setObjectName("questionSessionSummaryDialog")', MAIN_SOURCE)

    def test_futuristic_prefix_architecture_and_no_redundant_overrides(self) -> None:
        dark = tema.stylesheet_escuro()
        futuristic = tema.stylesheet_futurista()
        self.assertTrue(futuristic.startswith(dark))
        suffix = futuristic[len(dark):]
        self.assertIn("#adaptiveSummaryCard", suffix)
        self.assertIn("#effectivenessImpactCard", suffix)
        self.assertIn("qlineargradient", suffix)
        for marker in ("#adaptiveSummaryText", "#effectivenessImpactMetric", "#mockExamResultSectionTitle", "#mockExamCorrectionNotice"):
            self.assertNotIn(f"QDialog#questionSessionSummaryDialog QLabel{marker}", suffix)
            self.assertNotIn(f"QDialog#questionSessionSummaryDialog QFrame{marker}", suffix)

    def test_qss_diff_from_pass_a_is_only_scoped_pass_b_rules(self) -> None:
        for theme_name, expected_hash in CURRENT_NORMALIZED.items():
            qss = getattr(tema, f"stylesheet_{theme_name}")()
            qss = strip_cards_global_block_a(tema, theme_name, qss)
            self.assertNotIn("{{color:", qss)
            self.assertNotIn("{{gradient:", qss)
            self.assertEqual(hashlib.sha256(canonical(qss).encode()).hexdigest(), expected_hash)
            qss_without_dashboard = strip_dashboard_block_a(theme_name, qss)
            stripped = strip_pass_b_rules(qss_without_dashboard)
            self.assertEqual(hashlib.sha256(canonical(stripped).encode()).hexdigest(), PASS_A_NORMALIZED[theme_name])

    def test_metadata_unchanged(self) -> None:
        self.assertEqual(VIGHNA_VERSION, "0.29.59")
        self.assertEqual(VIGHNA_BUILD, "questions-center-editor-viewer-futuristic-text-v1")
        self.assertEqual(VIGHNA_SCHEMA, 25)


if __name__ == "__main__":
    unittest.main()
