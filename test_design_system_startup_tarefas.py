"""Caracterização da subpaleta fixa de startup e tarefas pesadas."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest

from PySide6.QtWidgets import QApplication

from ui.design import (
    THEMES,
    fixed_gradient,
    fixed_qcolor,
    fixed_qlineargradient,
    fixed_qss_color,
)


ROOT = Path(__file__).resolve().parent
STARTUP_SOURCE = (ROOT / "startup_splash.py").read_text(encoding="utf-8")
TASK_SOURCE = (ROOT / "tarefas_pesadas.py").read_text(encoding="utf-8")
MAIN_SOURCE = (ROOT / "main.py").read_text(encoding="utf-8")
MAIN_FALLBACK = MAIN_SOURCE[
    MAIN_SOURCE.index("class JanelaInicializacao(QDialog):"):
    MAIN_SOURCE.index("class SistemaEstudos(QMainWindow):")
]

STRUCTURAL_COLORS = {
    "canvas": "#071522",
    "border": "#214A64",
    "surface": "#081927",
    "surface_border": "#15364C",
    "text_primary": "#F5F8FF",
    "text_status": "#EAF4FF",
    "text_secondary": "#8FAAC0",
    "text_accent": "#67B7FF",
    "progress_track": "#081A28",
    "progress_border": "#315B76",
    "progress_fill": "#3A8DF1",
}

STARTUP_COLORS = {
    "logo_surface": "#091927",
    "logo_border": "#1D4058",
    "subtitle_text": "#9FB9D0",
    "footer_text": "#4E718A",
    "logo_fallback": "#6DC1FF",
    "progress_pulse": "#6FC3FF",
}

TASK_COLORS = {
    "mark_surface": "#0A2233",
    "mark_border": "#286483",
    "mark_text": "#74C7FF",
}

PROGRESS_GRADIENT = (
    (0.0, "#2E74D8"),
    (0.55, "#3A8DF1"),
    (1.0, "#4CA8FF"),
)

SHIMMER_RGBA = (
    (0.0, (125, 215, 255, 0)),
    (0.50, (175, 232, 255, 150)),
    (1.0, (125, 215, 255, 0)),
)

COLOR_TOKENS = {
    **{f"system_status.{role}": value for role, value in STRUCTURAL_COLORS.items()},
    **{f"startup.{role}": value for role, value in STARTUP_COLORS.items()},
    **{f"task_indicator.{role}": value for role, value in TASK_COLORS.items()},
}


class StartupTaskDesignSystemTests(unittest.TestCase):
    def test_cores_anteriores_sao_resolvidas_exatamente(self) -> None:
        for token, expected in COLOR_TOKENS.items():
            with self.subTest(token=token):
                self.assertEqual(fixed_qss_color(token), expected)
                for theme in THEMES.values():
                    self.assertEqual(theme.color(token).value, expected)

    def test_gradiente_de_progresso_preserva_stops_e_posicoes(self) -> None:
        spec = fixed_gradient("startup.progress_gradient")
        self.assertEqual(
            tuple((stop.position, stop.color.value) for stop in spec.stops),
            PROGRESS_GRADIENT,
        )

    def test_shimmer_preserva_rgb_alpha_e_stops(self) -> None:
        spec = fixed_gradient("startup.shimmer_gradient")
        actual = tuple(
            (
                stop.position,
                (stop.color.argb[1], stop.color.argb[2], stop.color.argb[3], stop.color.argb[0]),
            )
            for stop in spec.stops
        )
        self.assertEqual(actual, SHIMMER_RGBA)

    def test_gradientes_qpainter_preservam_coordenadas_dinamicas(self) -> None:
        self.assertIsNone(QApplication.instance())
        progress = fixed_qlineargradient(
            "startup.progress_gradient", coordinates=(12.5, 0.0, 218.75, 0.0)
        )
        self.assertEqual(
            (progress.start().x(), progress.start().y(), progress.finalStop().x(), progress.finalStop().y()),
            (12.5, 0.0, 218.75, 0.0),
        )
        self.assertEqual([position for position, _ in progress.stops()], [0.0, 0.55, 1.0])
        shimmer = fixed_qlineargradient(
            "startup.shimmer_gradient", coordinates=(20.0, 0.0, 92.0, 0.0)
        )
        self.assertEqual([position for position, _ in shimmer.stops()], [0.0, 0.5, 1.0])
        self.assertEqual([color.alpha() for _, color in shimmer.stops()], [0, 150, 0])
        self.assertIsNone(QApplication.instance())

    def test_pulso_preserva_rgb_e_alpha_dinamico(self) -> None:
        color = fixed_qcolor("startup.progress_pulse")
        self.assertEqual((color.red(), color.green(), color.blue()), (111, 195, 255))
        self.assertEqual(color.alpha(), 255)
        self.assertIn("cor_pulso.setAlpha(intensidade)", STARTUP_SOURCE)
        self.assertIn(
            "intensidade = int(42 + 26 * (0.5 + 0.5 * sin(self._fase_pulso * 2.0 * pi)))",
            STARTUP_SOURCE,
        )

    def test_consumidores_usam_api_fixa_publica(self) -> None:
        self.assertIn("from ui.design import fixed_qcolor, fixed_qlineargradient, fixed_qss_color", STARTUP_SOURCE)
        self.assertIn("from ui.design import fixed_qss_color", TASK_SOURCE)
        self.assertIn("from ui.design import fixed_qss_color", MAIN_SOURCE)
        self.assertIn('"startup.progress_gradient"', STARTUP_SOURCE)
        self.assertIn('"startup.shimmer_gradient"', STARTUP_SOURCE)
        self.assertIn("system_status.progress_fill", TASK_SOURCE)
        self.assertIn("system_status.progress_fill", MAIN_FALLBACK)

    def test_hardcodes_migrados_nao_permanecem_nos_consumidores(self) -> None:
        all_values = {
            *STRUCTURAL_COLORS.values(),
            *STARTUP_COLORS.values(),
            *TASK_COLORS.values(),
            *(value for _position, value in PROGRESS_GRADIENT),
        }
        for value in all_values:
            with self.subTest(value=value):
                self.assertNotIn(value, STARTUP_SOURCE)
                self.assertNotIn(value, TASK_SOURCE)
                self.assertNotIn(value, MAIN_FALLBACK)
        self.assertNotIn("QColor(125, 215, 255, 0)", STARTUP_SOURCE)
        self.assertNotIn("QColor(175, 232, 255, 150)", STARTUP_SOURCE)
        self.assertNotIn("QColor(111, 195, 255, intensidade)", STARTUP_SOURCE)

    def test_timing_animacao_e_comportamento_permanecem_caracterizados(self) -> None:
        for expected in (
            "self._timer.setInterval(30)",
            "self._fase_shimmer += 0.022",
            "self._timer_estado.setInterval(80)",
            "self._timer_texto.setInterval(320)",
        ):
            self.assertIn(expected, STARTUP_SOURCE)
        self.assertIn("self._timer_animacao.setInterval(320)", TASK_SOURCE)
        self.assertIn("self._atraso_minimo_nao_bloqueante_ms = 850", TASK_SOURCE)

    def test_importacao_do_controlador_continua_sem_carregar_qt(self) -> None:
        script = (
            "import sys; import startup_splash; "
            "print(','.join(name for name in sys.modules if name.startswith('PySide6')))"
        )
        completed = subprocess.run(
            [sys.executable, "-c", script],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.stdout.strip(), "")
        self.assertEqual(completed.stderr.strip(), "")


if __name__ == "__main__":
    unittest.main()
