"""Contrato do Design System — Dashboard Bloco F (Planejamento completo)."""

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
    render_qss,
    token_spec,
)
from versao import VIGHNA_BUILD, VIGHNA_SCHEMA, VIGHNA_VERSION


ROOT = Path(__file__).resolve().parent
MAIN_SOURCE = (ROOT / "main.py").read_text(encoding="utf-8")
TEMA_SOURCE = (ROOT / "tema.py").read_text(encoding="utf-8")

PREFIX = "dashboard.planning_full_"
COLOR_TOKENS = {
    token.path for token in ALL_TOKENS
    if token.path.startswith(PREFIX) and token.kind is TokenKind.COLOR
}
GRADIENT_TOKENS = {
    token.path for token in ALL_TOKENS
    if token.path.startswith(PREFIX) and token.kind is TokenKind.GRADIENT
}
BLOCK_F_TOKENS = COLOR_TOKENS | GRADIENT_TOKENS

BLOCK_E_QSS = {
    "claro": "e5570c7884119c04747ca75fbf6cd51bf000d84030fe4d44d04cdbcc4c31b2b0",
    "escuro": "f999f4384b0349810268a4d317714daf4cc9583d4727f9d09882a2c64a052722",
    "futurista": "fc2fe1b5aa5c13d30e576bd5c6f21c52423d9febffa6034ebdb83bd986ace224",
}
BLOCK_F_QSS = {
    "claro": "0b654146ad3bd7e1299ee71bb8b8169f53286db85dff490c83c2bec4b01c58a9",
    "escuro": "812b992509e94ff2b49d47ea402543a1dbb7ccaf1754994c8d5d068e2401be0c",
    "futurista": "b25a888fdc3f0551cab27d55e1dd15b3b6576950788554e37906d19ba099cf5b",
}
PROTECTED_HASHES = {
    "main.py": "d2e4ebd54ae765ec8f11eabd5e6c6e086e3dfd7bb3d441def8c03705515da4fe",
    "versao.py": "49e9d1b5c82bc10c70bd79ca5f494961e3cae3553cd4b70af1565bca661f9ac2",
    "foco.py": "8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed",
    "jogos.py": "498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286",
    "checkpoint.py": "947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38",
}

EXPECTED_COLORS = {
    "claro": {
        "dashboard.planning_full_panel_surface": "#FFFFFF",
        "dashboard.planning_full_panel_border": "#E2E8F0",
        "dashboard.planning_full_daily_progress_fill": "#3976D5",
        "dashboard.planning_full_day_today_surface": "#F2F6FF",
        "dashboard.planning_full_day_high_border": "#E8C6C1",
        "dashboard.planning_full_week_status_attention_text": "#C2410C",
        "dashboard.planning_full_metric_track": "#E5E8F0",
    },
    "escuro": {
        "dashboard.planning_full_panel_surface": "#151F2D",
        "dashboard.planning_full_panel_border": "#2D4054",
        "dashboard.planning_full_daily_progress_fill": "#4779C7",
        "dashboard.planning_full_day_today_surface": "#172944",
        "dashboard.planning_full_day_high_border": "#5E3737",
        "dashboard.planning_full_week_status_attention_text": "#FDBA74",
        "dashboard.planning_full_metric_track": "#263548",
    },
    "futurista": {
        "dashboard.planning_full_panel_surface": "#202833",
        "dashboard.planning_full_panel_border": "#445061",
        "dashboard.planning_full_daily_progress_fill": "#3B78B1",
        "dashboard.planning_full_day_today_surface": "#E1132B43",
        "dashboard.planning_full_day_high_border": "#6B3F3F",
        "dashboard.planning_full_week_status_attention_text": "#FFE2C0",
        "dashboard.planning_full_metric_track": "#18304A",
    },
}


def canonical_qss(qss: str) -> str:
    qss = re.sub(r"#[0-9A-Fa-f]{3,8}\b", lambda m: m.group(0).upper(), qss)
    return re.sub(r"\s+", " ", qss).strip()


def qss_hash(qss: str) -> str:
    return hashlib.sha256(canonical_qss(qss).encode("utf-8")).hexdigest()


def strip_navigation_layer(theme_name: str, qss: str) -> str:
    qss = strip_cards_global_block_a(tema, theme_name, qss)
    if theme_name == "futurista":
        final_back = render_qss("futurista", tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
        inherited_back = render_qss("escuro", tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
        if qss.endswith(final_back):
            qss = qss[:-len(final_back)]
        elif final_back in qss:
            qss = qss.replace(final_back, "", 1)
        if inherited_back in qss:
            qss = qss.replace(inherited_back, "", 1)
    else:
        back_layer = render_qss(theme_name, tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
        if qss.endswith(back_layer):
            qss = qss[:-len(back_layer)]
        elif back_layer in qss:
            qss = qss.replace(back_layer, "", 1)
    if theme_name == "futurista":
        final = render_qss("futurista", tema.ESTILO_NAVEGACAO_BUSCA_GLOBAL)
        inherited = render_qss("escuro", tema.ESTILO_NAVEGACAO_BUSCA_GLOBAL)
        if qss.endswith(final):
            qss = qss[:-len(final)]
        if inherited in qss:
            qss = qss.replace(inherited, "", 1)
        return qss
    layer = render_qss(theme_name, tema.ESTILO_NAVEGACAO_BUSCA_GLOBAL)
    if qss.endswith(layer):
        return qss[:-len(layer)]
    return qss.replace(layer, "", 1)


def strip_block_h(theme_name: str, qss: str) -> str:
    qss = strip_navigation_layer(theme_name, qss)
    if theme_name == "futurista":
        final = render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_H)
        inherited = render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_H)
        if not qss.endswith(final):
            raise AssertionError("camada H futurista não é a última")
        qss = qss[:-len(final)]
        if inherited not in qss:
            raise AssertionError("camada H escura herdada não encontrada no Futurista")
        return qss.replace(inherited, "", 1)
    layer = render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_H)
    if not qss.endswith(layer):
        raise AssertionError(f"camada H não é a última em {theme_name}")
    return qss[:-len(layer)]


def strip_block_g(theme_name: str, qss: str) -> str:
    qss = strip_block_h(theme_name, qss)
    if theme_name == "futurista":
        final = render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_G)
        inherited = render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_G)
        if not qss.endswith(final):
            raise AssertionError("camada G futurista não é a última")
        qss = qss[:-len(final)]
        if inherited not in qss:
            raise AssertionError("camada G escura herdada não encontrada no Futurista")
        return qss.replace(inherited, "", 1)
    layer = render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_G)
    if not qss.endswith(layer):
        raise AssertionError(f"camada G não é a última em {theme_name}")
    return qss[:-len(layer)]


def strip_block_f(theme_name: str, qss: str) -> str:
    qss = strip_block_g(theme_name, qss)
    if theme_name == "futurista":
        final = render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_F)
        inherited = render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_F)
        if not qss.endswith(final):
            raise AssertionError("camada F futurista não é a última")
        qss = qss[:-len(final)]
        if inherited not in qss:
            raise AssertionError("camada F escura herdada não encontrada no Futurista")
        return qss.replace(inherited, "", 1)
    layer = render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_F)
    if not qss.endswith(layer):
        raise AssertionError(f"camada F não é a última em {theme_name}")
    return qss[:-len(layer)]


class DashboardBlockFDesignSystemTests(unittest.TestCase):
    def test_orcamento_final_e_contrato_exato(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 1148)
        self.assertEqual(len(ALL_TOKENS), 1250)
        self.assertEqual(len(COLOR_TOKENS), 82)
        self.assertEqual(len(GRADIENT_TOKENS), 17)
        self.assertEqual(len(BLOCK_F_TOKENS), 99)
        for path in COLOR_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.COLOR)
        for path in GRADIENT_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.GRADIENT)

    def test_valores_representativos_preservam_caracterizacao(self):
        for theme_name, expected in EXPECTED_COLORS.items():
            theme = get_theme(theme_name)
            for path, value in expected.items():
                with self.subTest(theme=theme_name, path=path):
                    self.assertEqual(theme.color(path).value, value)
        future_primary = get_theme("futurista").gradient(
            "dashboard.planning_full_primary_action_gradient"
        )
        self.assertEqual(
            tuple((stop.position, stop.color.value) for stop in future_primary.stops),
            ((0.0, "#355F9F"), (1.0, "#4C7EE0")),
        )
        future_metric = get_theme("futurista").gradient(
            "dashboard.planning_full_metric_progress_gradient"
        )
        self.assertEqual(
            tuple((stop.position, stop.color.value) for stop in future_metric.stops),
            ((0.0, "#4DE7FF"), (0.5, "#7279FF"), (1.0, "#62EFBD")),
        )

    def test_camada_f_e_tokenizada_e_estritamente_escopada(self):
        source = tema.ESTILO_DASHBOARD_BLOCO_F
        self.assertIsNone(re.search(r"#[0-9A-Fa-f]{6,8}\b", source))
        self.assertNotIn("QPainter", source)
        self.assertIn("#planningPanel", source)
        for selector in re.findall(r"([^{}]+)\{", source):
            if selector.strip().startswith("Q"):
                self.assertIn("#dashboardRoot", selector)
                self.assertIn("#planningPanel", selector)
        self.assertNotIn("weeklyGoalSetupButton", source)
        self.assertNotIn("weeklyGoalEmptyDescription", source)

    def test_estados_e_consumidores_ativos_permanecem_no_main(self):
        for marker in (
            '"planningPanel"',
            '"planningGoalButton"',
            '"planningJourneyButton"',
            '"planningAutoPlanButton"',
            '"planningRedistributeButton"',
            '"weeklyGoalStatus"',
            '"weeklyGoalProgress"',
            '"dashboard_secao_planejamento_expandida"',
            '"goalState"',
            '"weekState"',
            '"loadLevel"',
            '"today"',
            '"hasPlan"',
            '"hasSuggestion"',
            '"journeyState"',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, MAIN_SOURCE)

    def test_objetos_compartilhados_ficam_limitados_ao_planejamento_completo(self):
        source = tema.ESTILO_DASHBOARD_BLOCO_F
        for object_name in ("weeklyGoalStatus", "planningSummaryButton"):
            selectors = [
                selector.strip()
                for selector in re.findall(r"([^{}]+)\{", source)
                if f"#{object_name}" in selector
            ]
            self.assertGreater(len(selectors), 0)
            for selector in selectors:
                self.assertIn("#planningPanel", selector)
        self.assertGreaterEqual(MAIN_SOURCE.count('"weeklyGoalStatus"'), 2)
        self.assertGreaterEqual(MAIN_SOURCE.count('"planningSummaryButton"'), 2)

    def test_qss_renderiza_sem_tokens_pendentes_e_com_hash_final(self):
        for theme_name in ("claro", "escuro", "futurista"):
            qss = getattr(tema, f"stylesheet_{theme_name}")()
            with self.subTest(theme=theme_name):
                self.assertNotIn("{{color:", qss)
                self.assertNotIn("{{gradient:", qss)
                self.assertEqual(qss_hash(strip_block_g(theme_name, qss)), BLOCK_F_QSS[theme_name])

    def test_rollback_da_camada_f_recupera_exatamente_checkpoint_e(self):
        for theme_name in ("claro", "escuro", "futurista"):
            qss = getattr(tema, f"stylesheet_{theme_name}")()
            with self.subTest(theme=theme_name):
                self.assertEqual(qss_hash(strip_block_f(theme_name, qss)), BLOCK_E_QSS[theme_name])

    def test_arquivos_protegidos_e_metadados_permanecem_inalterados(self):
        for relative, expected in PROTECTED_HASHES.items():
            digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(digest, expected, relative)
        self.assertEqual(VIGHNA_VERSION, "0.29.59")
        self.assertEqual(VIGHNA_BUILD, "statistics-my-evolution-tokens-v1")
        self.assertEqual(VIGHNA_SCHEMA, 25)

    def test_camada_f_foi_acrescentada_apos_e_nos_tres_temas(self):
        self.assertEqual(TEMA_SOURCE.count('render_qss("claro", ESTILO_DASHBOARD_BLOCO_F)'), 1)
        self.assertEqual(TEMA_SOURCE.count('render_qss("escuro", ESTILO_DASHBOARD_BLOCO_F)'), 1)
        self.assertEqual(TEMA_SOURCE.count('render_qss("futurista", ESTILO_DASHBOARD_BLOCO_F)'), 1)
        for theme_name in ("claro", "escuro", "futurista"):
            line = next(
                line for line in TEMA_SOURCE.splitlines()
                if f'render_qss("{theme_name}", ESTILO_DASHBOARD_BLOCO_F)' in line
            )
            self.assertLess(
                line.index(f'render_qss("{theme_name}", ESTILO_DASHBOARD_BLOCO_E)'),
                line.index(f'render_qss("{theme_name}", ESTILO_DASHBOARD_BLOCO_F)'),
            )
            self.assertLess(
                line.index(f'render_qss("{theme_name}", ESTILO_DASHBOARD_BLOCO_F)'),
                line.index(f'render_qss("{theme_name}", ESTILO_DASHBOARD_BLOCO_G)'),
            )
            self.assertLess(
                line.index(f'render_qss("{theme_name}", ESTILO_DASHBOARD_BLOCO_G)'),
                line.index(f'render_qss("{theme_name}", ESTILO_DASHBOARD_BLOCO_H)'),
            )


if __name__ == "__main__":
    unittest.main()
