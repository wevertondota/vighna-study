from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sys
import types
import unittest
from _design_system_test_helpers import strip_cards_global_block_a

# O núcleo de Design System não depende de Qt. tema.py importa somente
# QApplication no topo; este stub torna a auditoria QSS executável também no
# ambiente Linux de análise quando PySide6 não está instalado.
try:
    import PySide6  # noqa: F401
except ModuleNotFoundError:
    pyside = types.ModuleType("PySide6")
    qtwidgets = types.ModuleType("PySide6.QtWidgets")
    qtwidgets.QApplication = type("QApplication", (), {})
    sys.modules.setdefault("PySide6", pyside)
    sys.modules.setdefault("PySide6.QtWidgets", qtwidgets)

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

PREFIX = "dashboard.study_questions_"
COLOR_TOKENS = {
    token.path for token in ALL_TOKENS
    if token.path.startswith(PREFIX) and token.kind is TokenKind.COLOR
}
GRADIENT_TOKENS = {
    token.path for token in ALL_TOKENS
    if token.path.startswith(PREFIX) and token.kind is TokenKind.GRADIENT
}
BLOCK_G_TOKENS = COLOR_TOKENS | GRADIENT_TOKENS

BLOCK_F_QSS = {
    "claro": "197d1f1051896765152d637943a3c2c0660b81a4514f58a01867377a3144bebd",
    "escuro": "922d7951bf5edde14ab712112aff8484510bb48702e8f5307e6bef6476c6b1f5",
    "futurista": "dd3fb829eae39970f600047328bb905878f3a152b8b40eef44f9b4fa872a214b",
}
BLOCK_G_QSS = {
    "claro": "d0e0149638447e981bdaa0a7099f57ba3d95654808992f52da98ad984b0c4de2",
    "escuro": "4df67944497bf40a3246ec85d3e863411378936bace30f582d5e28f612f8b166",
    "futurista": "1227869ce6d10ab4068e13dacd71bb37be8f009a6d22380b2218ed66382e502b",
}
PROTECTED_HASHES = {
    "main.py": "bdb0815e71387bd87d40498bf535ef839d19a1a9086d55e0582ea50946713b45",
    "estudos.db": "034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef",
    "versao.py": "c201d237e622dd2269838e54914458fd775c7ec1a91f07b518775ee833caa439",
    "foco.py": "8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed",
    "jogos.py": "498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286",
    "checkpoint.py": "947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38",
}

EXPECTED_COLORS = {
    "claro": {
        "dashboard.study_questions_panel_surface": "#FFFFFF",
        "dashboard.study_questions_review_border": "#D2E2EF",
        "dashboard.study_questions_adaptive_surface": "#FFFFFF",
        "dashboard.study_questions_adaptive_action_border": "#467F5E",
        "dashboard.study_questions_simulation_action_border": "#BE8B2D",
        "dashboard.study_questions_manual_footer_surface": "#F8FAFC",
        "dashboard.study_questions_subtle_text": "#2D3748",
    },
    "escuro": {
        "dashboard.study_questions_panel_surface": "#151F2D",
        "dashboard.study_questions_review_border": "#34516D",
        "dashboard.study_questions_adaptive_surface": "#171F31",
        "dashboard.study_questions_adaptive_action_border": "#38A18E",
        "dashboard.study_questions_simulation_action_border": "#C6923D",
        "dashboard.study_questions_manual_footer_surface": "#0E1825",
        "dashboard.study_questions_subtle_text": "#DCE6F0",
    },
    "futurista": {
        "dashboard.study_questions_panel_surface": "#202833",
        "dashboard.study_questions_review_border": "#3CCFF0",
        "dashboard.study_questions_adaptive_surface": "#171F31",
        "dashboard.study_questions_adaptive_action_border": "#67D8BF",
        "dashboard.study_questions_simulation_action_border": "#F5C86D",
        "dashboard.study_questions_manual_footer_surface": "#081827",
        "dashboard.study_questions_subtle_text": "#D1D9E2",
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


class DashboardBlockGDesignSystemTests(unittest.TestCase):
    def test_orcamento_final_e_contrato_exato(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 928)
        self.assertEqual(len(ALL_TOKENS), 1030)
        self.assertEqual(len(COLOR_TOKENS), 55)
        self.assertEqual(len(GRADIENT_TOKENS), 6)
        self.assertEqual(len(BLOCK_G_TOKENS), 61)
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

        future_base = get_theme("futurista").gradient(
            "dashboard.study_questions_base_card_gradient"
        )
        self.assertEqual(
            tuple((stop.position, stop.color.value) for stop in future_base.stops),
            ((0.0, "#EB0C1F2F"), (1.0, "#EB091624")),
        )
        self.assertEqual(
            (future_base.direction.x1, future_base.direction.y1,
             future_base.direction.x2, future_base.direction.y2),
            (0.0, 0.0, 1.0, 1.0),
        )
        future_adaptive = get_theme("futurista").gradient(
            "dashboard.study_questions_adaptive_action_gradient"
        )
        self.assertEqual(
            tuple((stop.position, stop.color.value) for stop in future_adaptive.stops),
            ((0.0, "#1D6F67"), (1.0, "#2FA88F")),
        )
        future_simulation = get_theme("futurista").gradient(
            "dashboard.study_questions_simulation_action_gradient"
        )
        self.assertEqual(
            tuple((stop.position, stop.color.value) for stop in future_simulation.stops),
            ((0.0, "#A36D1E"), (1.0, "#D09A35")),
        )

    def test_camada_g_e_tokenizada_e_estritamente_escopada(self):
        source = tema.ESTILO_DASHBOARD_BLOCO_G
        self.assertIsNone(re.search(r"#[0-9A-Fa-f]{6,8}\b", source))
        self.assertIsNone(re.search(r"rgba\s*\(", source, flags=re.I))
        self.assertIn("#studyNowPanel", source)
        for group in re.findall(r"([^{}]+)\{", source):
            for selector in group.split(","):
                selector = selector.strip()
                if selector.startswith("Q"):
                    self.assertIn("#dashboardRoot", selector)
                    self.assertIn("#studyNowPanel", selector)
        self.assertNotIn("#priorityQueuePanel", source)
        self.assertNotIn("QDialog", source)

    def test_estados_e_consumidores_ativos_permanecem_no_main(self):
        for marker in (
            '"studyNowPanel"',
            '"studyActionCard"',
            '"strategyCompactCard"',
            '"questionsFoundationText"',
            '"adaptiveDashboardButton"',
            '"mockExamDashboardButton"',
            '"studyManualFooter"',
            '"dashboard_secao_estudar_expandida"',
            '"actionRole"',
            '"review"',
            '"adaptive"',
            '"simulation"',
            '"recovery"',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, MAIN_SOURCE)

    def test_object_names_compartilhados_ficam_limitados_ao_painel(self):
        source = tema.ESTILO_DASHBOARD_BLOCO_G
        shared = (
            "studyNowIcon",
            "dashboardActionSectionSubtitle",
            "studyActionCard",
            "studyActionTitle",
            "studyReviewSourceBadge",
            "adaptiveDashboardButton",
            "mockExamDashboardButton",
            "subtleButton",
        )
        for object_name in shared:
            selectors = []
            for group in re.findall(r"([^{}]+)\{", source):
                for selector in group.split(","):
                    if f"#{object_name}" in selector:
                        selectors.append(selector.strip())
            self.assertGreater(len(selectors), 0, object_name)
            for selector in selectors:
                self.assertIn("#studyNowPanel", selector, selector)
        self.assertGreaterEqual(MAIN_SOURCE.count('"studyActionCard"'), 2)
        self.assertGreaterEqual(MAIN_SOURCE.count('"adaptiveDashboardButton"'), 2)
        self.assertGreaterEqual(MAIN_SOURCE.count('"mockExamDashboardButton"'), 2)
        self.assertGreaterEqual(MAIN_SOURCE.count('"subtleButton"'), 4)

    def test_qss_renderiza_sem_tokens_pendentes_e_com_hash_final(self):
        for theme_name in ("claro", "escuro", "futurista"):
            qss = getattr(tema, f"stylesheet_{theme_name}")()
            with self.subTest(theme=theme_name):
                self.assertNotIn("{{color:", qss)
                self.assertNotIn("{{gradient:", qss)
                self.assertEqual(qss_hash(strip_block_h(theme_name, qss)), BLOCK_G_QSS[theme_name])

    def test_rollback_da_camada_g_recupera_exatamente_checkpoint_f(self):
        for theme_name in ("claro", "escuro", "futurista"):
            qss = getattr(tema, f"stylesheet_{theme_name}")()
            with self.subTest(theme=theme_name):
                self.assertEqual(
                    qss_hash(strip_block_g(theme_name, qss)),
                    BLOCK_F_QSS[theme_name],
                )

    def test_arquivos_protegidos_e_metadados_permanecem_inalterados(self):
        for relative, expected in PROTECTED_HASHES.items():
            digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(digest, expected, relative)
        self.assertEqual(VIGHNA_VERSION, "0.29.59")
        self.assertEqual(VIGHNA_BUILD, "updates-center-v1")
        self.assertEqual(VIGHNA_SCHEMA, 25)

    def test_camada_g_foi_acrescentada_apos_f_nos_tres_temas(self):
        self.assertEqual(TEMA_SOURCE.count('render_qss("claro", ESTILO_DASHBOARD_BLOCO_G)'), 1)
        self.assertEqual(TEMA_SOURCE.count('render_qss("escuro", ESTILO_DASHBOARD_BLOCO_G)'), 1)
        self.assertEqual(TEMA_SOURCE.count('render_qss("futurista", ESTILO_DASHBOARD_BLOCO_G)'), 1)
        for theme_name in ("claro", "escuro", "futurista"):
            line = next(
                line for line in TEMA_SOURCE.splitlines()
                if f'render_qss("{theme_name}", ESTILO_DASHBOARD_BLOCO_G)' in line
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
