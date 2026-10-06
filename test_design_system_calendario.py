import ast
import hashlib
import re
import unittest
from pathlib import Path

import tema
from ui.design import get_theme, qcolor


ROOT = Path(__file__).resolve().parent
MAIN_SOURCE = (ROOT / "main.py").read_text(encoding="utf-8")
TEMA_SOURCE = (ROOT / "tema.py").read_text(encoding="utf-8")
MAIN_TREE = ast.parse(MAIN_SOURCE)


def _method_source(class_name, method_name):
    for node in MAIN_TREE.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == method_name:
                    return ast.get_source_segment(MAIN_SOURCE, item) or ""
    raise AssertionError(f"Metodo {class_name}.{method_name} nao encontrado")


def _canonical_qss(value):
    normalized = re.sub(
        r"#[0-9A-Fa-f]{3,8}\b",
        lambda match: match.group(0).upper(),
        value,
    )
    return re.sub(r"\s+", " ", normalized).strip()


def _block(stylesheet, final_selector):
    matches = re.findall(re.escape(final_selector) + r"\s*\{([^}]*)\}", stylesheet, re.S)
    if not matches:
        raise AssertionError(f"Seletor nao encontrado: {final_selector}")
    return matches[-1]


def _hex_colors(stylesheet, final_selector):
    matches = re.findall(re.escape(final_selector) + r"\s*\{([^}]*)\}", stylesheet, re.S)
    colored = [tuple(re.findall(r"#[0-9a-fA-F]{6,8}", body)) for body in matches]
    colored = [colors for colors in colored if colors]
    if not colored:
        raise AssertionError(f"Seletor sem cores: {final_selector}")
    return tuple(color.lower() for color in colored[-1])


THEMES = {
    "claro": tema.stylesheet_claro,
    "escuro": tema.stylesheet_escuro,
    "futurista": tema.stylesheet_futurista,
}


MONTHLY_COLORS = {
    "claro": {
        "QFrame#calendarDayPanel": ("#ffffff", "#dbe3ed"),
        "QLabel#calendarDateTitle": ("#111827",),
        "QLabel#calendarCountBadge": ("#f1f5f9", "#475569", "#e2e8f0"),
        "QLabel#calendarLegendToday": ("#2563eb",),
        "QLabel#calendarLegendLate": ("#dc2626",),
        "QLabel#calendarLegendFuture": ("#16a34a",),
        "QCalendarWidget#reviewCalendar": ("#ffffff",),
        "QCalendarWidget#reviewCalendar QWidget#qt_calendar_navigationbar": ("#f8fafc",),
        "QCalendarWidget#reviewCalendar QToolButton": ("#1f2937",),
        "QCalendarWidget#reviewCalendar QToolButton:hover": ("#e2e8f0",),
        "QCalendarWidget#reviewCalendar QSpinBox": ("#ffffff", "#1f2937", "#cbd5e1"),
        "QCalendarWidget#reviewCalendar QAbstractItemView": (
            "#ffffff", "#1f2937", "#2563eb", "#ffffff",
        ),
    },
    "escuro": {
        "QFrame#calendarDayPanel": ("#182235", "#334155"),
        "QLabel#calendarDateTitle": ("#f8fafc",),
        "QLabel#calendarCountBadge": ("#273449", "#cbd5e1", "#334155"),
        "QLabel#calendarLegendToday": ("#93c5fd",),
        "QLabel#calendarLegendLate": ("#fca5a5",),
        "QLabel#calendarLegendFuture": ("#86efac",),
        "QCalendarWidget#reviewCalendar": ("#182235",),
        "QCalendarWidget#reviewCalendar QWidget#qt_calendar_navigationbar": ("#172033",),
        "QCalendarWidget#reviewCalendar QToolButton": ("#e5e7eb",),
        "QCalendarWidget#reviewCalendar QToolButton:hover": ("#273449",),
        "QCalendarWidget#reviewCalendar QSpinBox": ("#172033", "#e5e7eb", "#475569"),
        "QCalendarWidget#reviewCalendar QAbstractItemView": (
            "#182235", "#e5e7eb", "#2563eb", "#ffffff",
        ),
    },
}
MONTHLY_COLORS["futurista"] = MONTHLY_COLORS["escuro"]


WEEKLY_COLORS = {
    "claro": {
        "QPushButton#calendarViewToggle": ("#ffffff", "#64748b", "#d7e0ea"),
        "QPushButton#calendarViewToggle:hover": ("#f8fafc", "#334155", "#cbd5e1"),
        "QPushButton#calendarViewToggle:checked": ("#e8f1ff", "#1d4ed8", "#93c5fd"),
        "QLabel#calendarForecastDayDate": ("#64748b",),
        "QFrame#calendarForecastPanel": ("#ffffff", "#dbe3ed"),
        "QLabel#calendarForecastTitle": ("#111827",),
        "QLabel#calendarForecastNotice": ("#475569", "#f8fafc", "#e2e8f0"),
        "QFrame#calendarForecastDay": ("#f8fafc", "#e2e8f0"),
        'QFrame#calendarForecastDay[dayState="today"]': ("#f0f7ff", "#93c5fd"),
        'QFrame#calendarForecastDay[dayState="past"]': ("#f8fafc", "#e2e8f0"),
        "QLabel#calendarForecastDayName": ("#0f172a",),
        "QLabel#calendarForecastDayCount": ("#e2e8f0", "#475569"),
        "QFrame#calendarForecastCard": ("#ffffff", "#dbe3ed", "#64748b"),
        'QFrame#calendarForecastCard[forecastKind="revisao"]': ("#2563eb",),
        'QFrame#calendarForecastCard[forecastKind="realizado"]': ("#16a34a",),
        'QFrame#calendarForecastCard[forecastKind="recomendacao"]': ("#7c3aed",),
        'QFrame#calendarForecastCard[forecastKind="simulado"]': ("#d97706",),
        "QLabel#calendarForecastDiscipline": ("#475569",),
        "QLabel#calendarForecastCardTitle": ("#111827",),
        "QLabel#calendarForecastLoad": ("#f1f5f9", "#475569", "#e2e8f0"),
        "QToolButton#calendarForecastOpen": ("#64748b",),
        "QToolButton#calendarForecastOpen:hover": ("#e8f1ff", "#1d4ed8", "#bfdbfe"),
        "QLabel#calendarForecastEmpty": ("#94a3b8",),
    },
    "escuro": {
        "QPushButton#calendarViewToggle": ("#172033", "#94a3b8", "#334155"),
        "QPushButton#calendarViewToggle:hover": ("#273449", "#e2e8f0", "#475569"),
        "QPushButton#calendarViewToggle:checked": ("#172554", "#93c5fd", "#1e40af"),
        "QLabel#calendarForecastDayDate": ("#94a3b8",),
        "QFrame#calendarForecastPanel": ("#182235", "#334155"),
        "QLabel#calendarForecastTitle": ("#f8fafc",),
        "QLabel#calendarForecastNotice": ("#cbd5e1", "#172033", "#334155"),
        "QFrame#calendarForecastDay": ("#172033", "#334155"),
        'QFrame#calendarForecastDay[dayState="today"]': ("#172554", "#1e40af"),
        'QFrame#calendarForecastDay[dayState="past"]': ("#151e2e", "#2b394b"),
        "QLabel#calendarForecastDayName": ("#f8fafc",),
        "QLabel#calendarForecastDayCount": ("#273449", "#cbd5e1"),
        "QFrame#calendarForecastCard": ("#1d293d", "#334155", "#64748b"),
        'QFrame#calendarForecastCard[forecastKind="revisao"]': ("#60a5fa",),
        'QFrame#calendarForecastCard[forecastKind="realizado"]': ("#4ade80",),
        'QFrame#calendarForecastCard[forecastKind="recomendacao"]': ("#a78bfa",),
        'QFrame#calendarForecastCard[forecastKind="simulado"]': ("#f59e0b",),
        "QLabel#calendarForecastDiscipline": ("#94a3b8",),
        "QLabel#calendarForecastCardTitle": ("#f1f5f9",),
        "QLabel#calendarForecastLoad": ("#273449", "#cbd5e1", "#3b4a61"),
        "QToolButton#calendarForecastOpen": ("#94a3b8",),
        "QToolButton#calendarForecastOpen:hover": ("#273449", "#93c5fd", "#475569"),
        "QLabel#calendarForecastEmpty": ("#64748b",),
    },
    "futurista": {
        "QPushButton#calendarViewToggle": ("#0D1D2D", "#84A9BD", "#294B63"),
        "QPushButton#calendarViewToggle:hover": ("#123049", "#D7F3FF", "#39789A"),
        "QPushButton#calendarViewToggle:checked": ("#143A55", "#BDF7FF", "#45BCE8"),
        "QLabel#calendarForecastDayDate": ("#7FA2B5",),
        "QFrame#calendarForecastPanel": ("#0B1A27", "#294B63"),
        "QLabel#calendarForecastTitle": ("#E7F7FF",),
        "QLabel#calendarForecastNotice": ("#9FC4D6", "#0D1D2D", "#294B63"),
        "QFrame#calendarForecastDay": ("#0D1D2D", "#294B63"),
        'QFrame#calendarForecastDay[dayState="today"]': ("#10304A", "#3D9BC5"),
        'QFrame#calendarForecastDay[dayState="past"]': ("#0B1824", "#223D50"),
        "QLabel#calendarForecastDayName": ("#E9F8FF",),
        "QLabel#calendarForecastDayCount": ("#153149", "#A8D9EE"),
        "QFrame#calendarForecastCard": ("#102334", "#294B63", "#5F8296"),
        'QFrame#calendarForecastCard[forecastKind="revisao"]': ("#4BC9F2",),
        'QFrame#calendarForecastCard[forecastKind="realizado"]': ("#74F1C5",),
        'QFrame#calendarForecastCard[forecastKind="recomendacao"]': ("#8D7CFF",),
        'QFrame#calendarForecastCard[forecastKind="simulado"]': ("#E7B14B",),
        "QLabel#calendarForecastDiscipline": ("#82ABC0",),
        "QLabel#calendarForecastCardTitle": ("#E7F5FF",),
        "QLabel#calendarForecastLoad": ("#153149", "#A8D9EE", "#315B75"),
        "QToolButton#calendarForecastOpen": ("#82ABC0",),
        "QToolButton#calendarForecastOpen:hover": ("#153149", "#BDF7FF", "#39789A"),
        "QLabel#calendarForecastEmpty": ("#638397",),
    },
}


class CalendarVisualBaselineTests(unittest.TestCase):
    def test_canonical_stylesheet_hashes_remain_stage_3c_baseline(self):
        expected = {
            "claro": "139709f8c57e00f16848668f9226703c7f8ff391dd9aea2bba8b2eae20ac2c5f",
            "escuro": "ebbc21363d0035058301d060eb099fb2d33b992e8537c20f9bf1e77f8a2b4f3e",
            "futurista": "0e588bb372946b4a6f61ad406c817fd155cac8c3c4286e9f93b7a09d06dc8622",
        }
        for name, factory in THEMES.items():
            digest = hashlib.sha256(_canonical_qss(factory()).encode("utf-8")).hexdigest()
            self.assertEqual(digest, expected[name], name)

    def test_monthly_qss_values_for_all_themes(self):
        for name, factory in THEMES.items():
            stylesheet = factory()
            for selector, expected in MONTHLY_COLORS[name].items():
                self.assertEqual(
                    _hex_colors(stylesheet, selector),
                    tuple(color.lower() for color in expected),
                    (name, selector),
                )

    def test_weekly_qss_values_and_states_for_all_themes(self):
        for name, factory in THEMES.items():
            stylesheet = factory()
            for selector, expected in WEEKLY_COLORS[name].items():
                self.assertEqual(
                    _hex_colors(stylesheet, selector),
                    tuple(color.lower() for color in expected),
                    (name, selector),
                )

    def test_programmatic_monthly_formats_use_exact_characterized_tokens(self):
        source = _method_source("SistemaEstudos", "atualizar_calendario_mes").lower()
        expected = {
            "claro": {
                "calendar.today_text": "#1d4ed8", "calendar.today_surface": "#dbeafe",
                "calendar.late_text": "#b91c1c", "calendar.late_surface": "#fee2e2",
                "calendar.scheduled_text": "#15803d", "calendar.scheduled_surface": "#dcfce7",
            },
            "escuro": {
                "calendar.today_text": "#93c5fd", "calendar.today_surface": "#1e3a8a",
                "calendar.late_text": "#fca5a5", "calendar.late_surface": "#4c1d24",
                "calendar.scheduled_text": "#86efac", "calendar.scheduled_surface": "#163523",
            },
            "futurista": {
                "calendar.today_text": "#bdf7ff", "calendar.today_surface": "#124e68",
                "calendar.late_text": "#ff9bac", "calendar.late_surface": "#4b1d2c",
                "calendar.scheduled_text": "#74f1c5", "calendar.scheduled_surface": "#124334",
            },
        }
        self.assertIn("qcolor(", source)
        self.assertNotRegex(source, r"#[0-9a-f]{6,8}")
        for theme_name, theme_colors in expected.items():
            design_theme = get_theme(theme_name)
            for token, color in theme_colors.items():
                self.assertIn(token, source)
                self.assertEqual(design_theme.color(token).value.lower(), color)
                self.assertEqual(qcolor(theme_name, token).name().lower(), color)

    def test_calendar_behavior_states_are_unchanged(self):
        weekly = _method_source("SistemaEstudos", "atualizar_previsao_semana_calendario")
        card = _method_source("SistemaEstudos", "_criar_card_previsao_calendario")
        for state in ('"past"', '"today"', '"future"'):
            self.assertIn(state, weekly)
        for kind in ('"revisao"', '"realizado"', '"recomendacao"', '"simulado"'):
            self.assertIn(kind, card)
        self.assertIn("Sem atividade prevista", weekly)
        self.assertIn("Sem estudo registrado", weekly)

    def test_calendar_sources_use_public_design_system_without_visual_hex(self):
        self.assertIn("from ui.design import fixed_qss_color, qcolor", MAIN_SOURCE)
        self.assertIn("from ui.design import render_qss", TEMA_SOURCE)

        for constant, next_marker in (
            ("ESTILO_CALENDARIO_PREVISAO_CLARO", "ESTILO_CALENDARIO_PREVISAO_ESCURO"),
            ("ESTILO_CALENDARIO_PREVISAO_ESCURO", "ESTILO_CALENDARIO_PREVISAO_FUTURISTA"),
            ("ESTILO_CALENDARIO_PREVISAO_FUTURISTA", "def stylesheet_claro"),
        ):
            scoped = TEMA_SOURCE.split(constant, 1)[1].split(next_marker, 1)[0]
            self.assertNotRegex(scoped, r"#[0-9A-Fa-f]{6,8}", constant)

        monthly_blocks = re.findall(
            r"QFrame#calendarPanel,\s*QFrame#calendarDayPanel\s*\{.*?"
            r"QCalendarWidget#reviewCalendar QAbstractItemView\s*\{.*?\}",
            TEMA_SOURCE,
            re.S,
        )
        self.assertEqual(len(monthly_blocks), 2)
        for block in monthly_blocks:
            self.assertNotRegex(block, r"#[0-9A-Fa-f]{6,8}")


if __name__ == "__main__":
    unittest.main()
