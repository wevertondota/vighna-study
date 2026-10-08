"""Contrato da Etapa 3E-C, Passo A: núcleo do resumo final da sessão."""

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
    token_spec,
)
from versao import VIGHNA_BUILD, VIGHNA_SCHEMA, VIGHNA_VERSION


ROOT = Path(__file__).resolve().parent
TEMA_SOURCE = (ROOT / "tema.py").read_text(encoding="utf-8")
MAIN_SOURCE = (ROOT / "main.py").read_text(encoding="utf-8")

SUMMARY_TOKENS = {
    "summary.canvas",
    "summary.title_text",
    "summary.subtitle_text",
    "summary.metric_surface",
    "summary.metric_border",
    "summary.metric_label_text",
    "summary.metric_value_text",
    "summary.detail_surface",
    "summary.detail_text",
    "summary.detail_border",
    "summary.table_surface",
    "summary.table_border",
    "summary.review_surface",
    "summary.review_border",
    "summary.review_title_text",
    "summary.review_text",
}

EXPECTED = {
    "claro": {
        "summary.canvas": "#F4F6FA", "summary.title_text": "#151C2A",
        "summary.subtitle_text": "#69778C", "summary.metric_surface": "#FFFFFF",
        "summary.metric_border": "#DBE3ED", "summary.metric_label_text": "#64748B",
        "summary.metric_value_text": "#111827", "summary.detail_surface": "#EFF6FF",
        "summary.detail_text": "#1E3A8A", "summary.detail_border": "#BFDBFE",
        "summary.table_surface": "#FFFFFF", "summary.table_border": "#DBE3ED",
        "summary.review_surface": "#F0FDF4", "summary.review_border": "#BBF7D0",
        "summary.review_title_text": "#166534", "summary.review_text": "#166534",
    },
    "escuro": {
        "summary.canvas": "#0D1624", "summary.title_text": "#EEF3F8",
        "summary.subtitle_text": "#8F9CAF", "summary.metric_surface": "#182235",
        "summary.metric_border": "#334155", "summary.metric_label_text": "#94A3B8",
        "summary.metric_value_text": "#F8FAFC", "summary.detail_surface": "#172554",
        "summary.detail_text": "#BFDBFE", "summary.detail_border": "#1D4ED8",
        "summary.table_surface": "#182235", "summary.table_border": "#334155",
        "summary.review_surface": "#163523", "summary.review_border": "#166534",
        "summary.review_title_text": "#BBF7D0", "summary.review_text": "#86EFAC",
    },
    "futurista": {
        "summary.canvas": "#07111E", "summary.title_text": "#E7F5FB",
        "summary.subtitle_text": "#7F9FB4", "summary.metric_surface": "#182235",
        "summary.metric_border": "#334155", "summary.metric_label_text": "#94A3B8",
        "summary.metric_value_text": "#F8FAFC", "summary.detail_surface": "#172554",
        "summary.detail_text": "#BFDBFE", "summary.detail_border": "#1D4ED8",
        "summary.table_surface": "#182235", "summary.table_border": "#334155",
        "summary.review_surface": "#163523", "summary.review_border": "#166534",
        "summary.review_title_text": "#BBF7D0", "summary.review_text": "#86EFAC",
    },
}

CURRENT_HASHES = {
    "claro": "377b349f9564f3ca4f00c05a3e58b942290c60db08f3ce902886b0bf855dc8ed",
    "escuro": "60471c1750c25666a3a07fb7be7392ca42e71023e8cc273a0bd1535cf20ecb35",
    "futurista": "c00e04362fcdb449bc79d3337faa1f7bb83143b829128aad465204a7762ceb94",
}
B2G_HASHES = {
    "claro": "ce4accdafcfabc2d431feafe3f3ab7009a66ecfd8c2717157036bcab4cb0020f",
    "escuro": "fd26fc88cde100bb19e6eb3ea7c6fa51eb5cf734d12f2320eb1301421d3129ba",
    "futurista": "5e6c0dc38f94712b067551cba0a2266f207f6d5f7f6da2a0b7f9f16a92a79bb6",
}
PROTECTED = {
    "banco.py": "c263a502f0761d1f9fb7f910b35474cbda18b529a5244978614cc27342b32c94",
    "foco.py": "8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed",
    "checkpoint.py": "947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38",
    "versao.py": "c201d237e622dd2269838e54914458fd775c7ec1a91f07b518775ee833caa439",
    "estudos.db": "034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef",
}

SUMMARY_RULE = re.compile(
    r"(?ms)^    QDialog#questionSessionSummaryDialog[^\n{]*(?:\n    QDialog#questionSessionSummaryDialog[^\n{]*)*\s*\{.*?^    \}\n?"
)



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


class SummaryFinalPassATests(unittest.TestCase):
    def test_exact_sixteen_new_component_color_tokens(self) -> None:
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 928)
        self.assertEqual(len(ALL_TOKENS), 1030)
        actual = {t.path for t in ALL_TOKENS if t.path.startswith("summary.")}
        self.assertTrue(SUMMARY_TOKENS < actual)
        for path in SUMMARY_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.COLOR)

    def test_values_match_characterization_in_all_themes(self) -> None:
        for theme_name, expected in EXPECTED.items():
            theme = get_theme(theme_name)
            for path, value in expected.items():
                self.assertEqual(theme.color(path).value, value, (theme_name, path))

    def test_dialog_gets_only_the_authorized_identity(self) -> None:
        self.assertEqual(MAIN_SOURCE.count('self.setObjectName("questionSessionSummaryDialog")'), 1)
        start = MAIN_SOURCE.index("class JanelaResumoResolucaoQuestoes(QDialog):")
        end = MAIN_SOURCE.index("\nclass ", start + 1)
        block = MAIN_SOURCE[start:end]
        self.assertIn('self.setObjectName("questionSessionSummaryDialog")', block)

    def test_scoped_core_rules_use_only_summary_contracts(self) -> None:
        rules = SUMMARY_RULE.findall(TEMA_SOURCE)
        core_markers = (
            "summary.canvas", "summary.title_text", "summary.subtitle_text",
            "summary.metric_", "summary.detail_", "summary.table_", "summary.review_",
        )
        core_rules = [rule for rule in rules if any(marker in rule for marker in core_markers)]
        self.assertEqual(len(core_rules), 25)  # Passo A: 11 Claro + 11 Escuro + 3 Futuristas.
        joined = "\n".join(core_rules)
        for path in SUMMARY_TOKENS:
            expected_count = 3 if path in {"summary.canvas", "summary.title_text", "summary.subtitle_text"} else 2
            self.assertEqual(joined.count(f"{{{{color:{path}}}}}"), expected_count, path)
        for forbidden in ("border-radius", "padding", "font-size", "font-weight", "margin"):
            self.assertNotIn(forbidden, joined)
        self.assertNotIn("summary.adaptive_", joined)
        self.assertNotIn("summary.effectiveness_", joined)
        self.assertNotIn("summary.mock_exam_", joined)

    def test_shared_global_rules_remain_literal(self) -> None:
        self.assertRegex(TEMA_SOURCE, r"QLabel#questionSessionSummaryDetail\s*\{\s*background-color: #eff6ff;")
        self.assertRegex(TEMA_SOURCE, r"QLabel#questionSessionSummaryDetail\s*\{\s*background-color: #172554;")
        self.assertIn("QFrame#questionSessionConfigCard,\n    QFrame#questionSessionSummaryCard {", TEMA_SOURCE)
        self.assertIn("QFrame#questionReviewIntegrationCard {\n        background-color: #f0fdf4;", TEMA_SOURCE)
        self.assertIn("QFrame#questionReviewIntegrationCard {\n        background-color: #163523;", TEMA_SOURCE)
        self.assertNotIn("QPushButton#primaryButton {\n        background-color: {{color:summary.", TEMA_SOURCE)
        self.assertNotIn("QPushButton#subtleButton {\n        background-color: {{color:summary.", TEMA_SOURCE)

    def test_qss_diff_is_only_new_scoped_summary_rules(self) -> None:
        pass_b_markers = (
            "#adaptiveSummaryCard", "#adaptiveSummaryTitle", "#adaptiveSummaryText",
            "#effectivenessImpactCard", "#effectivenessImpactTitle", "#effectivenessImpactMetric",
            "#effectivenessImpactLabel", "#effectivenessImpactFooter", "#effectivenessImpactValue",
            "#mockExamResultSectionTitle", "#mockExamCorrectionNotice",
        )
        for theme_name, current_hash in CURRENT_HASHES.items():
            qss = getattr(tema, f"stylesheet_{theme_name}")()
            self.assertNotIn("{{color:", qss)
            self.assertNotIn("{{gradient:", qss)
            qss = strip_dashboard_block_a(theme_name, qss)
            without_b = SUMMARY_RULE.sub(
                lambda m: "" if any(marker in m.group(0) for marker in pass_b_markers) else m.group(0),
                qss,
            )
            self.assertEqual(hashlib.sha256(canonical(without_b).encode()).hexdigest(), current_hash)
            stripped = SUMMARY_RULE.sub("", without_b)
            self.assertEqual(
                hashlib.sha256(canonical(stripped).encode()).hexdigest(),
                B2G_HASHES[theme_name],
            )
        self.assertTrue(tema.stylesheet_futurista().startswith(tema.stylesheet_escuro()))

    def test_pass_b_does_not_rewrite_shared_legacy_rules(self) -> None:
        self.assertIn("QFrame#adaptiveSummaryCard {\n        background-color: #f8fbff;", TEMA_SOURCE)
        self.assertIn("QFrame#adaptiveSummaryCard {\n        background-color: #172033;", TEMA_SOURCE)
        self.assertIn("QFrame#effectivenessImpactCard {\n        background-color: #f8fbff;", TEMA_SOURCE)
        self.assertIn("QFrame#effectivenessImpactCard {\n        background-color: #172033;", TEMA_SOURCE)
        self.assertIn("QLabel#mockExamCorrectionNotice {\n        background-color: #f5f3ff;", TEMA_SOURCE)
        self.assertIn("QLabel#mockExamCorrectionNotice {\n        background-color: #2e1065;", TEMA_SOURCE)

    def test_protected_files_and_metadata_are_unchanged(self) -> None:
        for relative, expected in PROTECTED.items():
            self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), expected)
        self.assertEqual(VIGHNA_VERSION, "0.29.59")
        self.assertEqual(VIGHNA_BUILD, "updates-center-v1")
        self.assertEqual(VIGHNA_SCHEMA, 25)


if __name__ == "__main__":
    unittest.main()
