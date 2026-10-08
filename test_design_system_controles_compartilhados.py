"""Caracterização da migração dos controles visuais compartilhados."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest
from _design_system_test_helpers import strip_cards_global_block_a

import tema

# 3E-B2c: o hash Futurista muda apenas pela separação autorizada da cor
# normal das flags; equivalência integral com B2b2 validada no teste de flags.
from ui.design import get_theme


ROOT = Path(__file__).resolve().parent
TEMA_SOURCE = (ROOT / "tema.py").read_text(encoding="utf-8")

EXPECTED_STYLESHEET_BASELINE = {
    "claro": "cef0365e8cdd703fc73df505529d0e97672e5c49f036c0cba3b7ee50d42f23fe",
    "escuro": "5e365d9be91deb9d29532b8954c4cc8d66acf8142f019d3706aafba0a3e548cb",
    "futurista": "edc56b82ac5c720c06dac89700ec039d4d62536a31709d881ff1078960605dce",
}


def _normalize_hex_case(stylesheet: str) -> str:
    normalized = re.sub(
        r"#[0-9A-Fa-f]{3,8}\b",
        lambda match: match.group(0).upper(),
        stylesheet,
    )
    return re.sub(r"\s+", " ", normalized).strip()



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

class SharedControlsBaselineTests(unittest.TestCase):
    def test_stylesheets_completos_preservam_linha_de_base(self) -> None:
        stylesheets = {
            "claro": tema.stylesheet_claro(),
            "escuro": tema.stylesheet_escuro(),
            "futurista": tema.stylesheet_futurista(),
        }
        for theme, stylesheet in stylesheets.items():
            with self.subTest(theme=theme):
                stylesheet = strip_navigation_search_layer(theme, stylesheet)
                normalized = _normalize_hex_case(stylesheet)
                self.assertEqual(
                    hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
                    EXPECTED_STYLESHEET_BASELINE[theme],
                )

    def test_estados_globais_relevantes_estao_caracterizados(self) -> None:
        light = tema.stylesheet_claro()
        dark = tema.stylesheet_escuro()
        futuristic = tema.stylesheet_futurista()

        for stylesheet in (light, dark, futuristic):
            self.assertIn("QPushButton:hover", stylesheet)
            self.assertIn("QPushButton:pressed", stylesheet)
            self.assertIn("QPushButton:disabled", stylesheet)
            self.assertIn("QLineEdit:focus", stylesheet)
            self.assertIn("QTableWidget", stylesheet)
            self.assertIn("QHeaderView::section", stylesheet)
            self.assertIn("QTabBar::tab:selected", stylesheet)
            self.assertIn("QScrollBar::handle:vertical:hover", stylesheet)
            self.assertIn("QToolTip", stylesheet)

        light = light.lower()
        dark = dark.lower()
        futuristic = futuristic.lower()
        self.assertIn("background-color: #ffffff;\n        color: #1f2937;", light)
        self.assertIn("background-color: #1f2937;\n        color: #e5e7eb;", dark)
        self.assertIn("background-color: #11253a;\n        color: #d8eeff;", futuristic)
        self.assertIn("selection-background-color: #ded9ff;", light)
        self.assertIn("selection-background-color: #5549ad;", dark)
        self.assertIn("stop:0 #10253a", futuristic)
        self.assertIn("stop:1 #0a1829", futuristic)
        self.assertIn("background-color: #4aa5d3;", futuristic)

    def test_cascata_futurista_permanece_sobre_escuro(self) -> None:
        self.assertIn("return stylesheet_escuro() +", TEMA_SOURCE)

    def test_fonte_dos_blocos_migrados_usa_renderizador_publico(self) -> None:
        self.assertIn("from ui.design import render_qss", TEMA_SOURCE)
        self.assertGreaterEqual(TEMA_SOURCE.count("{{color:"), 146)
        # 4 controles compartilhados + 4 estados do núcleo do Resolvedor
        # + 6 ações primárias normal/hover da 3E-A2
        # + 3 progressos e 1 overview da 3E-B2a
        # + 1 painel inferior Futurista da 3E-B2b2
        # + 6 consumidores dos gradientes do Modo Foco (normal/hover × 3 temas)
        # + 1 consumidor do gradiente primário do Pós-Foco Futurista.
        # + 11 gradientes tokenizados do Dashboard Bloco C.
        # + 3 gradientes tokenizados do Dashboard Bloco D.
        # + 2 gradientes do shell compartilhado studyActionCard (Cards globais B).
        # + 1 gradiente do shell compartilhado myEvolutionStatCard (Cards globais C).
        self.assertEqual(TEMA_SOURCE.count("{{gradient:"), 91)

    def test_tokens_de_controles_reproduzem_valores_legados(self) -> None:
        expected = {
            "claro": {
                "action.secondary": "#FFFFFF",
                "text.control": "#182033",
                "border.default": "#CBD3DF",
                "focus.ring": "#7667E8",
                "surface.selected": "#EEEAFF",
            },
            "escuro": {
                "action.secondary": "#1F2937",
                "text.control": "#EDF1F7",
                "border.default": "#40536A",
                "focus.ring": "#8879F3",
                "surface.selected": "#39336E",
            },
            "futurista": {
                "action.secondary": "#11253A",
                "text.control": "#EEF9FF",
                "border.default": "#40668B",
                "focus.ring": "#59E3FF",
                "surface.selected": "#234766",
                "progress.fill": "#4AA5D3",
            },
        }
        for theme_name, values in expected.items():
            theme = get_theme(theme_name)
            for token, value in values.items():
                with self.subTest(theme=theme_name, token=token):
                    self.assertEqual(theme.color(token).value, value)

    def test_gradientes_genericos_futuristas_preservam_direcao_e_stops(self) -> None:
        theme = get_theme("futurista")
        expected = {
            "gradient.control_input": ((0.0, 0.0, 1.0, 1.0), ("#10253A", "#0A1829")),
            "gradient.control_header": ((0.0, 0.0, 1.0, 0.0), ("#132C45", "#0C1D31")),
            "gradient.control_tab": ((0.0, 0.0, 1.0, 0.0), ("#132B42", "#0C1D30")),
            "gradient.control_selected": ((0.0, 0.0, 1.0, 0.0), ("#0E6677", "#323E8E")),
        }
        for token, (direction, colors) in expected.items():
            with self.subTest(token=token):
                spec = theme.gradient(token)
                self.assertEqual(
                    (spec.direction.x1, spec.direction.y1, spec.direction.x2, spec.direction.y2),
                    direction,
                )
                self.assertEqual(tuple(stop.position for stop in spec.stops), (0.0, 1.0))
                self.assertEqual(tuple(stop.color.value for stop in spec.stops), colors)

    def test_tokens_de_chart_e_foco_preservam_contratos_explicitos(self) -> None:
        expected = {
            "claro": {
                "chart.grid": "#E2E8F0",
                "focus_mode.panel": "#FFFFFF",
            },
            "escuro": {
                "chart.grid": "#273449",
                "focus_mode.panel": "#151F2D",
            },
            "futurista": {
                "chart.grid": "#2E5C78",
                "focus_mode.panel": "#101F30",
            },
        }
        for theme_name, values in expected.items():
            theme = get_theme(theme_name)
            for token, value in values.items():
                with self.subTest(theme=theme_name, token=token):
                    self.assertEqual(theme.color(token).value, value)

    def test_qss_entregue_nao_expoe_marcadores_internos(self) -> None:
        for stylesheet in (
            tema.stylesheet_claro(),
            tema.stylesheet_escuro(),
            tema.stylesheet_futurista(),
        ):
            self.assertNotIn("{{color:", stylesheet)
            self.assertNotIn("{{gradient:", stylesheet)


if __name__ == "__main__":
    unittest.main()
