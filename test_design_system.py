"""Testes unitários da fundação isolada do Design System."""

from __future__ import annotations

import subprocess
import sys
import unittest

from ui.design import (
    ALL_TOKENS,
    COMPONENT_TOKEN_COUNT,
    COMPONENT_TOKENS,
    PALETTE,
    SEMANTIC_TOKEN_COUNT,
    SEMANTIC_TOKENS,
    THEMES,
    ColorValue,
    GradientDirection,
    ThemeName,
    TokenKind,
    TokenNotFoundError,
    VisualState,
    get_theme,
    gradient,
    qbrush,
    qcolor,
    qlineargradient,
    qpen,
    qss_color,
    qss_gradient,
    qtawesome_color,
)


class DesignSystemContractTests(unittest.TestCase):
    def test_todos_os_temas_implementam_o_mesmo_contrato(self) -> None:
        expected_colors = {
            token.path for token in ALL_TOKENS if token.kind is TokenKind.COLOR
        }
        expected_gradients = {
            token.path for token in ALL_TOKENS if token.kind is TokenKind.GRADIENT
        }
        self.assertEqual(set(THEMES), set(ThemeName))
        for theme in THEMES.values():
            self.assertEqual(set(theme.color_references), expected_colors)
            self.assertEqual(set(theme.gradients), expected_gradients)

    def test_nenhum_token_obrigatorio_fica_ausente(self) -> None:
        self.assertEqual(SEMANTIC_TOKEN_COUNT, len(SEMANTIC_TOKENS))
        self.assertEqual(COMPONENT_TOKEN_COUNT, len(COMPONENT_TOKENS))
        self.assertEqual(len(ALL_TOKENS), len({token.path for token in ALL_TOKENS}))
        for theme in THEMES.values():
            for token in ALL_TOKENS:
                self.assertIsNotNone(theme.resolve(token))

    def test_estados_requeridos_fazem_parte_da_api(self) -> None:
        self.assertEqual(
            {state.value for state in VisualState},
            {
                "normal", "hover", "pressed", "selected", "focused",
                "keyboard_focus", "checked", "disabled", "correct",
                "incorrect", "struck",
            },
        )

    def test_cores_da_paleta_e_dos_temas_sao_validas(self) -> None:
        for color in PALETTE.values():
            self.assertIsInstance(color, ColorValue)
            self.assertTrue(color.value == "transparent" or color.value.startswith("#"))
        for theme in THEMES.values():
            for reference in theme.color_references.values():
                self.assertIn(reference, PALETTE)

        with self.assertRaises(ValueError):
            ColorValue("#12345")
        with self.assertRaises(ValueError):
            ColorValue("rgba(1, 2, 3, 1)")

    def test_gradientes_tem_stops_validos_ordenados_e_variantes(self) -> None:
        for theme in THEMES.values():
            for spec in theme.gradients.values():
                positions = [stop.position for stop in spec.stops]
                self.assertGreaterEqual(len(positions), 2)
                self.assertEqual(positions, sorted(positions))
                self.assertEqual(len(positions), len(set(positions)))
                self.assertTrue(all(0.0 <= position <= 1.0 for position in positions))

        self.assertNotEqual(
            get_theme("claro").gradient("gradient.action_primary"),
            get_theme("futurista").gradient("gradient.action_primary"),
        )
        with self.assertRaises(ValueError):
            gradient((0.8, "#FFFFFF"), (0.2, "#000000"))
        with self.assertRaises(ValueError):
            GradientDirection(0.0, 0.0, 0.0, 0.0)

    def test_acesso_inexistente_ou_com_tipo_errado_falha_explicitamente(self) -> None:
        theme = get_theme("claro")
        with self.assertRaisesRegex(TokenNotFoundError, "inexistente"):
            theme.resolve("specific.nao_publico")
        with self.assertRaisesRegex(TokenNotFoundError, "gradiente, não cor"):
            theme.color("gradient.hero")
        with self.assertRaisesRegex(TokenNotFoundError, "cor, não gradiente"):
            theme.gradient("text.primary")
        with self.assertRaises(ValueError):
            get_theme("desconhecido")


class DesignSystemAdapterTests(unittest.TestCase):
    def test_adaptadores_qss_e_qtawesome(self) -> None:
        self.assertEqual(qss_color("claro", "canvas.app"), "#F5F7FA")
        self.assertEqual(qtawesome_color("futurista", "icon.action"), "#B6D9E8")
        result = qss_gradient("futurista", "gradient.action_primary")
        self.assertEqual(
            result,
            "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #4447E8, stop:0.52 #4347E1, stop:1 #3C42D2)",
        )

    def test_adaptadores_qpainter_funcionam_sem_qapplication(self) -> None:
        from PySide6.QtWidgets import QApplication

        self.assertIsNone(QApplication.instance())
        color = qcolor("claro", "overlay.scrim")
        self.assertEqual((color.alpha(), color.red(), color.green(), color.blue()), (102, 0, 0, 0))
        self.assertEqual(qbrush("claro", "action.primary").color().name(), "#5965d8")
        pen = qpen("escuro", "border.default", 2.5)
        self.assertEqual(pen.color().name(), "#2f3d4d")
        self.assertEqual(pen.widthF(), 2.5)
        qt_gradient = qlineargradient("futurista", "gradient.action_primary")
        self.assertEqual([position for position, _color in qt_gradient.stops()], [0.0, 0.52, 1.0])
        self.assertIsNone(QApplication.instance())

    def test_qpen_rejeita_largura_negativa(self) -> None:
        with self.assertRaises(ValueError):
            qpen("claro", "border.default", -1.0)


class DesignSystemIsolationTests(unittest.TestCase):
    def test_importacao_nao_carrega_qt_widgets_legado_ou_qtawesome(self) -> None:
        script = (
            "import sys; import ui.design; "
            "blocked=('PySide6','tema','main','icones','qtawesome'); "
            "print(','.join(name for name in blocked if name in sys.modules))"
        )
        completed = subprocess.run(
            [sys.executable, "-c", script],
            cwd=".",
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.stdout.strip(), "")
        self.assertEqual(completed.stderr.strip(), "")


if __name__ == "__main__":
    unittest.main()
