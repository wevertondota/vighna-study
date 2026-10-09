"""Caracterização da Etapa 3E-B2a: estrutura e leitura do Resolvedor."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest
from _design_system_test_helpers import strip_cards_global_block_a

import tema

# 3E-B2c: o hash Futurista muda apenas pela separação autorizada da cor
# normal das flags; equivalência integral com B2b2 validada no teste de flags.
from ui.design import ALL_TOKENS, COMPONENT_TOKEN_COUNT, SEMANTIC_TOKEN_COUNT, get_theme


ROOT = Path(__file__).resolve().parent
TEMA_SOURCE = (ROOT / "tema.py").read_text(encoding="utf-8")

EXPECTED_STYLESHEET_BASELINE = {
    "claro": "71c6c022b5fb4a3798f5bb9f837fc55fc9fa3bf4d558832688dd7fb25d8c7cdb",
    "escuro": "25dd9d735b8aa542020a05bbc3318cc91aba79f0b2f89995cea0a272d8bc1056",
    "futurista": "0e1011b5790c7a6f775d70ef4a59dd60a4c1587de412e9533bed2e39b1cba14f",
}

EXPECTED_COLORS = {
    "claro": {
        "session.title_text": "#172033",
        "session.subtitle_text": "#718096",
        "session.panel_surface": "#FFFFFF",
        "session.overview_border": "#DDE4EC",
        "session.eyebrow_text": "#7B8797",
        "progress.session_text": "#202B3C",
        "session.cycle_text": "#657286",
        "progress.session_track": "#E8EDF3",
        "session.metric_surface": "#F7F9FC",
        "session.metric_border": "#E3E8EF",
        "session.metric_label_text": "#7A8798",
        "session.metric_value_text": "#1F2937",
        "session.metric_success_text": "#17815D",
        "session.metric_danger_text": "#C44758",
        "session.metric_warning_text": "#B16A18",
        "session.discipline_text": "#5866C8",
        "session.meta_text": "#5D697A",
        "session.question_index_text": "#606BC9",
    },
    "escuro": {
        "session.title_text": "#F3F6FA",
        "session.subtitle_text": "#96A3B3",
        "session.panel_surface": "#182230",
        "session.overview_border": "#344154",
        "session.eyebrow_text": "#8392A5",
        "progress.session_text": "#EDF2F7",
        "session.cycle_text": "#A1ADBB",
        "progress.session_track": "#2C3745",
        "session.metric_surface": "#141D29",
        "session.metric_border": "#2D3949",
        "session.metric_label_text": "#8D9BAD",
        "session.metric_value_text": "#F2F5F8",
        "session.metric_success_text": "#79D6AA",
        "session.metric_danger_text": "#F08A98",
        "session.metric_warning_text": "#E5B16B",
        "session.discipline_text": "#96A0FF",
        "session.meta_text": "#A8B4C2",
        "session.question_index_text": "#9BA4FF",
    },
    "futurista": {
        "session.title_text": "#F5F7FB",
        "session.subtitle_text": "#AAB5C2",
        "session.panel_surface": "#202733",
        "session.overview_border": "#475364",
        "session.eyebrow_text": "#AAB4C0",
        "progress.session_text": "#F5F7FB",
        "session.cycle_text": "#B8C1CD",
        "progress.session_track": "#3B424F",
        "session.metric_surface": "#171F2B",
        "session.metric_border": "#344050",
        "session.metric_label_text": "#98A5B4",
        "session.metric_value_text": "#F8FAFC",
        "session.metric_success_text": "#82DBB4",
        "session.metric_danger_text": "#F28B99",
        "session.metric_warning_text": "#E9B66E",
        "session.discipline_text": "#969FFF",
        "session.meta_text": "#B6C0CB",
        "session.question_index_text": "#9BA4FF",
    },
}

AUTHORIZED_SELECTORS = (
    "QDialog#questionSolverDialog",
    "QDialog#questionSolverDialog QLabel#pageTitle",
    "QDialog#questionSolverDialog QLabel#pageSubtitle",
    "QDialog#questionSolverDialog QFrame#questionSessionOverviewCard",
    "QDialog#questionSolverDialog QLabel#questionSessionEyebrow",
    "QDialog#questionSolverDialog QLabel#questionSessionProgressText",
    "QDialog#questionSolverDialog QLabel#questionSessionCycleText",
    "QDialog#questionSolverDialog QProgressBar#questionSessionProgress",
    "QDialog#questionSolverDialog QProgressBar#questionSessionProgress::chunk",
    "QDialog#questionSolverDialog QFrame#questionSessionMiniStat",
    "QDialog#questionSolverDialog QLabel#questionSessionMiniLabel",
    "QDialog#questionSolverDialog QLabel#questionSessionMiniValue",
    'QDialog#questionSolverDialog QLabel#questionSessionMiniValue[metricRole="success"]',
    'QDialog#questionSolverDialog QLabel#questionSessionMiniValue[metricRole="danger"]',
    'QDialog#questionSolverDialog QLabel#questionSessionMiniValue[metricRole="warning"]',
    "QDialog#questionSolverDialog QLabel#questionSolverDiscipline",
    "QDialog#questionSolverDialog QLabel#questionSolverMeta",
    "QDialog#questionSolverDialog QLabel#questionSolverQuestionIndex",
)


def _canonical_qss(value: str) -> str:
    normalized = re.sub(
        r"#[0-9A-Fa-f]{3,8}\b",
        lambda match: match.group(0).upper(),
        value,
    )
    return re.sub(r"\s+", " ", normalized).strip()


def _constant_source(name: str, next_name: str) -> str:
    return TEMA_SOURCE.split(f"{name} =", 1)[1].split(f"{next_name} =", 1)[0]


def _selector_block(source: str, selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{.*?\}}", source, re.DOTALL)
    if match is None:
        raise AssertionError(f"Seletor não encontrado: {selector}")
    return match.group(0)



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

class ResolverStructureReadingDesignSystemTests(unittest.TestCase):
    def test_contract_grows_by_exactly_the_approved_nineteen_tokens(self) -> None:
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 1148)
        self.assertEqual(len(ALL_TOKENS), 1250)
        added = {
            "progress.session_text",
            "progress.session_track",
            "session.overview_gradient",
            *(token for token in EXPECTED_COLORS["claro"] if token.startswith("session.")),
        }
        self.assertEqual(len(added), 19)
        self.assertTrue(added <= {token.path for token in ALL_TOKENS})

    def test_colors_reproduce_the_characterized_final_cascade(self) -> None:
        for theme_name, expected in EXPECTED_COLORS.items():
            theme = get_theme(theme_name)
            self.assertEqual(theme.color("canvas.app").value, {
                "claro": "#F5F7FA",
                "escuro": "#101722",
                "futurista": "#0B111D",
            }[theme_name])
            for token, value in expected.items():
                with self.subTest(theme=theme_name, token=token):
                    self.assertEqual(theme.color(token).value, value)

    def test_session_gradients_preserve_direction_stops_and_alpha(self) -> None:
        progress = {
            "claro": ((0.0, "#4F5FE8"), (1.0, "#6B86F2")),
            "escuro": ((0.0, "#5964E8"), (1.0, "#6E8BEF")),
            "futurista": ((0.0, "#5358EA"), (0.52, "#5B64EE"), (1.0, "#718BF5")),
        }
        overview = {
            "claro": ((0.0, "#FFFFFF"), (1.0, "#FFFFFF")),
            "escuro": ((0.0, "#182230"), (1.0, "#182230")),
            "futurista": ((0.0, "#202733"), (0.55, "#222A36"), (1.0, "#1D2430")),
        }
        for theme_name in progress:
            theme = get_theme(theme_name)
            for token, direction, expected in (
                ("progress.fill_gradient", (0.0, 0.0, 1.0, 0.0), progress[theme_name]),
                ("session.overview_gradient", (0.0, 0.0, 1.0, 1.0), overview[theme_name]),
            ):
                with self.subTest(theme=theme_name, token=token):
                    spec = theme.gradient(token)
                    self.assertEqual(
                        (spec.direction.x1, spec.direction.y1, spec.direction.x2, spec.direction.y2),
                        direction,
                    )
                    self.assertEqual(
                        tuple((stop.position, stop.color.value) for stop in spec.stops),
                        expected,
                    )
                    self.assertTrue(all(len(stop.color.value) == 7 for stop in spec.stops))

    def test_only_the_authorized_sixty_six_hex_occurrences_were_removed(self) -> None:
        constants = (
            _constant_source("ESTILO_RESOLVEDOR_CLARO", "ESTILO_RESOLVEDOR_ESCURO"),
            _constant_source("ESTILO_RESOLVEDOR_ESCURO", "ESTILO_RESOLVEDOR_FUTURISTA"),
            _constant_source("ESTILO_RESOLVEDOR_FUTURISTA", "ESTILO_TOPICO_DETALHES_CLARO"),
        )
        for source, remaining in zip(constants, (3, 3, 3)):
            for selector in AUTHORIZED_SELECTORS:
                with self.subTest(selector=selector, remaining=remaining):
                    self.assertNotRegex(_selector_block(source, selector), r"#[0-9A-Fa-f]{6,8}\b")
            self.assertEqual(len(re.findall(r"#[0-9A-Fa-f]{6,8}\b", source)), remaining)

    def test_authorized_consumers_use_the_characterized_tokens(self) -> None:
        markers = (
            "{{color:canvas.app}}",
            "{{color:session.title_text}}",
            "{{color:session.subtitle_text}}",
            "{{color:session.panel_surface}}",
            "{{color:session.overview_border}}",
            "{{gradient:session.overview_gradient}}",
            "{{color:session.eyebrow_text}}",
            "{{color:progress.session_text}}",
            "{{color:session.cycle_text}}",
            "{{color:progress.session_track}}",
            "{{gradient:progress.fill_gradient}}",
            "{{color:session.metric_surface}}",
            "{{color:session.metric_border}}",
            "{{color:session.metric_label_text}}",
            "{{color:session.metric_value_text}}",
            "{{color:session.metric_success_text}}",
            "{{color:session.metric_danger_text}}",
            "{{color:session.metric_warning_text}}",
            "{{color:session.discipline_text}}",
            "{{color:session.meta_text}}",
            "{{color:session.question_index_text}}",
        )
        for marker in markers:
            with self.subTest(marker=marker):
                self.assertIn(marker, TEMA_SOURCE)
        self.assertEqual(TEMA_SOURCE.count("{{gradient:progress.fill_gradient}}"), 3)
        self.assertEqual(TEMA_SOURCE.count("{{gradient:session.overview_gradient}}"), 1)
        self.assertNotIn("progress.session_gradient", TEMA_SOURCE)
        self.assertNotIn("focus_mode.canvas}}", TEMA_SOURCE)

    def test_non_authorized_chrome_and_content_remain_literal(self) -> None:
        for marker in (
            "#F7F9FC", "#151E2A", "#151D28",  # Modo Foco
            # Enunciado migrado e validado pela 3E-B2f.
            # Flags migradas e validadas pela 3E-B2c.
            # Painel/Pular/Encerrar migrados e validados pela 3E-B2b2.
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, TEMA_SOURCE)

    def test_existing_generic_progress_tokens_were_not_recharacterized(self) -> None:
        expected = {
            "claro": ("#E8EDF3", "#5965D8", "#475569", "#D5DCE8"),
            "escuro": ("#111827", "#5965D8", "#CBD5E1", "#314357"),
            "futurista": ("#102235", "#4AA5D3", "#EAF7FF", "#315A7A"),
        }
        for theme_name, values in expected.items():
            theme = get_theme(theme_name)
            self.assertEqual(
                tuple(theme.color(token).value for token in (
                    "progress.track", "progress.fill", "progress.text", "progress.border"
                )),
                values,
            )

    def test_complete_stylesheet_hashes_remain_identical(self) -> None:
        for theme_name, expected in EXPECTED_STYLESHEET_BASELINE.items():
            stylesheet = getattr(tema, f"stylesheet_{theme_name}")()
            baseline_qss = strip_navigation_search_layer(theme_name, stylesheet)
            digest = hashlib.sha256(_canonical_qss(baseline_qss).encode("utf-8")).hexdigest()
            self.assertEqual(digest, expected)
            self.assertNotIn("{{color:", stylesheet)
            self.assertNotIn("{{gradient:", stylesheet)
        self.assertIn("return stylesheet_escuro() + render_qss", TEMA_SOURCE)


if __name__ == "__main__":
    unittest.main()
