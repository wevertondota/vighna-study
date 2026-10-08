from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sys
import types
import unittest
from _design_system_test_helpers import strip_cards_global_block_a

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
    qss_color,
    render_qss,
    token_spec,
)
from versao import VIGHNA_BUILD, VIGHNA_SCHEMA, VIGHNA_VERSION


ROOT = Path(__file__).resolve().parent
MAIN_SOURCE = (ROOT / "main.py").read_text(encoding="utf-8")
TEMA_SOURCE = (ROOT / "tema.py").read_text(encoding="utf-8")

PREFIX = "dashboard.disciplines_"
COLOR_TOKENS = {
    token.path for token in ALL_TOKENS
    if token.path.startswith(PREFIX) and token.kind is TokenKind.COLOR
}
GRADIENT_TOKENS = {
    token.path for token in ALL_TOKENS
    if token.path.startswith(PREFIX) and token.kind is TokenKind.GRADIENT
}

BLOCK_G_QSS = {
    "claro": "37b0603c454be85eaa6aafa1cb14dde5e27ecd6ff608598496d912bc540969cd",
    "escuro": "89cfe454b1e2ebaaf02a0cc93127b29da282fb2917f72667cf88710a43797ba5",
    "futurista": "3dbbe4e418e1a95c4dde44a932378352d714635472e9467d5a24ae87447a62fd",
}
BLOCK_H_QSS = {
    "claro": "71c6c022b5fb4a3798f5bb9f837fc55fc9fa3bf4d558832688dd7fb25d8c7cdb",
    "escuro": "25dd9d735b8aa542020a05bbc3318cc91aba79f0b2f89995cea0a272d8bc1056",
    "futurista": "d4176c63eae7f8b0349fce4eb50ada9b5186473a8d0aba884ad7aa4e41f5b448",
}
BASE_MAIN_HASH = "9395a7b754347b2028e4b52aebb04a2a036b67dee7625f915482c3ec8accdc7d"
PROTECTED_HASHES = {
    "estudos.db": "7152284f813f16c42bb4586d4d929b53d5d97efe8cf6e290ff9b80faf11b9c26",
    "versao.py": "ae19e3d250f581849a09245b27469b2cb1b1aef48d862338e888679d58b20d67",
    "foco.py": "8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed",
    "jogos.py": "498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286",
    "checkpoint.py": "947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38",
}

EXPECTED = {
    "claro": {
        "header_surface": "#FFFFFF",
        "header_border": "#D9E3EF",
        "toggle_text": "#243B5A",
        "toggle_hover_surface": "#F1EFFF",
        "edit_surface": "#EAF2FF",
        "edit_hover_surface": "#DBEAFE",
        "edit_pressed_surface": "#BFDBFE",
        "button_surface": "#FFFFFF",
        "button_text": "#1F2937",
        "button_hover_surface": "#EFF6FF",
        "button_hover_text": "#1F2937",
        "disabled_surface": "#E2E8F0",
        "disabled_text": "#64748B",
        "disabled_border": "#CBD5E1",
    },
    "escuro": {
        "header_surface": "#151F2D",
        "header_border": "#2D4054",
        "toggle_text": "#D7E4F2",
        "toggle_hover_surface": "#201E43",
        "edit_surface": "#172554",
        "edit_hover_surface": "#1E3A8A",
        "edit_pressed_surface": "#1E40AF",
        "button_surface": "#1F2937",
        "button_text": "#E5E7EB",
        "button_hover_surface": "#172554",
        "button_hover_text": "#E5E7EB",
        "disabled_surface": "#28313D",
        "disabled_text": "#94A3B8",
        "disabled_border": "#475569",
    },
    "futurista": {
        "header_surface": "#202833",
        "header_border": "#445061",
        "toggle_text": "#D7E4F2",
        "toggle_hover_surface": "#201E43",
        "edit_surface": "#172554",
        "edit_hover_surface": "#1E3A8A",
        "edit_pressed_surface": "#1E40AF",
        "button_surface": "#1F2937",
        "button_text": "#D8EEFF",
        "button_hover_surface": "#172554",
        "button_hover_text": "#F4FBFF",
        "disabled_surface": "#173244",
        "disabled_text": "#8FA8B8",
        "disabled_border": "#466477",
    },
}

OLD_IMPORT = "from ui.design import fixed_qss_color, qcolor\n"
NEW_IMPORT = "from ui.design import fixed_qss_color, qcolor, qss_color\n"
OLD_BRANCH = '''                if tema_atual == "futurista":\n                    botao.setStyleSheet(\n                        "background-color:#173244; color:#8FA8B8; "\n                        "border:1px solid #466477; text-align:left; padding-left:14px;"\n                    )\n                elif tema_atual == "escuro":\n                    botao.setStyleSheet(\n                        "background-color:#28313d; color:#94A3B8; "\n                        "border:1px solid #475569; text-align:left; padding-left:14px;"\n                    )\n                else:\n                    botao.setStyleSheet(\n                        "background-color:#E2E8F0; color:#64748B; "\n                        "border:1px solid #CBD5E1; text-align:left; padding-left:14px;"\n                    )\n'''
NEW_BRANCH = '''                if tema_atual == "futurista":\n                    botao.setStyleSheet(\n                        f"background-color:{qss_color('futurista', 'dashboard.disciplines_disabled_surface')}; "\n                        f"color:{qss_color('futurista', 'dashboard.disciplines_disabled_text')}; "\n                        f"border:1px solid {qss_color('futurista', 'dashboard.disciplines_disabled_border')}; "\n                        "text-align:left; padding-left:14px;"\n                    )\n                elif tema_atual == "escuro":\n                    botao.setStyleSheet(\n                        f"background-color:{qss_color('escuro', 'dashboard.disciplines_disabled_surface')}; "\n                        f"color:{qss_color('escuro', 'dashboard.disciplines_disabled_text')}; "\n                        f"border:1px solid {qss_color('escuro', 'dashboard.disciplines_disabled_border')}; "\n                        "text-align:left; padding-left:14px;"\n                    )\n                else:\n                    botao.setStyleSheet(\n                        f"background-color:{qss_color('claro', 'dashboard.disciplines_disabled_surface')}; "\n                        f"color:{qss_color('claro', 'dashboard.disciplines_disabled_text')}; "\n                        f"border:1px solid {qss_color('claro', 'dashboard.disciplines_disabled_border')}; "\n                        "text-align:left; padding-left:14px;"\n                    )\n'''


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



def rollback_navigation_back_main(source: str) -> str:
    block = '''        voltar.setProperty(\n            "navigationBack",\n            True\n        )\n'''
    if source.count(block) != 6:
        raise AssertionError("marcações navigationBack inesperadas")
    return source.replace(block, "")


def rollback_later_qpainter_i(source: str) -> str:
    pairs = (
        ('        tema_atual = normalizar_tema(\n            getattr(self.window(), "tema_atual", "claro")\n        )\n\n        trilha = QPen(\n            qcolor(tema_atual, "dashboard.planning_arc_track"),\n            8\n        )\n        trilha.setCapStyle(Qt.RoundCap)\n        painter.setPen(trilha)\n        painter.drawArc(rect, 180 * 16, -180 * 16)\n', '        trilha = QPen(QColor(207, 243, 225, 82), 8)\n        trilha.setCapStyle(Qt.RoundCap)\n        painter.setPen(trilha)\n        painter.drawArc(rect, 180 * 16, -180 * 16)\n'),
        ('            valor = QPen(\n                qcolor(tema_atual, "dashboard.planning_arc_fill"),\n                8\n            )\n', "            valor = QPen(QColor('#B9FFE3'), 8)\n"),
        ('        painter.setPen(\n            qcolor(tema_atual, "dashboard.planning_arc_text")\n        )\n', "        painter.setPen(QColor('#F4FFFA'))\n"),
        ('        tema_atual = normalizar_tema(\n            getattr(self.window(), "tema_atual", "claro")\n        )\n\n        cor_trilha = qcolor(\n            tema_atual,\n            "dashboard.quality_donut_track_dark"\n            if cor_texto.lightness() > 150\n            else "dashboard.quality_donut_track_light"\n        )\n', '        cor_trilha = QColor(\n            "#263B4F"\n            if cor_texto.lightness() > 150\n            else "#DCE5ED"\n        )\n'),
        ('        caneta_valor = QPen(\n            qcolor(tema_atual, "dashboard.quality_donut_fill"),\n            11\n        )\n', '        caneta_valor = QPen(\n            QColor("#2FB4C7"),\n            11\n        )\n'),
    )
    for new, old in pairs:
        if new in source:
            source = source.replace(new, old, 1)
    return source

def rollback_main_h(source: str) -> str:
    if source.count(NEW_IMPORT) != 1 or source.count(NEW_BRANCH) != 1:
        raise AssertionError("diff H esperado de main.py não foi encontrado de forma única")
    return source.replace(NEW_IMPORT, OLD_IMPORT, 1).replace(NEW_BRANCH, OLD_BRANCH, 1)


class DashboardBlockHDesignSystemTests(unittest.TestCase):
    def test_orcamento_final_e_contrato_exato(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 1004)
        self.assertEqual(len(ALL_TOKENS), 1106)
        self.assertEqual(len(COLOR_TOKENS), 21)
        self.assertEqual(len(GRADIENT_TOKENS), 0)
        for path in COLOR_TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.COLOR)

    def test_valores_preservam_caracterizacao_e_estado_desligado(self):
        for theme_name, values in EXPECTED.items():
            theme = get_theme(theme_name)
            for short, expected in values.items():
                path = PREFIX + short
                with self.subTest(theme=theme_name, path=path):
                    self.assertEqual(theme.color(path).value, expected)
        self.assertEqual(
            qss_color("futurista", PREFIX + "disabled_surface"), "#173244"
        )
        self.assertEqual(
            qss_color("escuro", PREFIX + "disabled_surface"), "#28313D"
        )
        self.assertEqual(
            qss_color("claro", PREFIX + "disabled_surface"), "#E2E8F0"
        )

    def test_camada_h_sem_hardcodes_e_escopo_restrito(self):
        source = tema.ESTILO_DASHBOARD_BLOCO_H
        self.assertIsNone(re.search(r"#[0-9A-Fa-f]{6,8}\b", source))
        self.assertIsNone(re.search(r"rgba\s*\(", source, flags=re.I))
        self.assertNotIn("qlineargradient", source.lower())
        self.assertNotIn("dashboardCollapsibleContent", source)
        self.assertNotIn("priorityQueuePanel", source)
        for group in re.findall(r"([^{}]+)\{", source):
            for selector in group.split(","):
                selector = selector.strip()
                if selector.startswith("Q"):
                    self.assertIn("#dashboardRoot", selector, selector)

    def test_consumidores_e_comportamento_protegido_permanecem(self):
        for marker in (
            '"dashboardCenterBar"',
            '"dashboardSectionToggleCentered"',
            '"sectionEditButton"',
            '"disciplineButton"',
            '"dashboard_secao_disciplinas_expandida"',
            'self.abrir_disciplinas',
            'self.abrir_disciplina(',
            '"Disciplina desligada temporariamente. Clique para abrir e gerenciar."',
            'f"{nome}  • desligada"',
            'fila_painel.setVisible(False)',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, MAIN_SOURCE)

    def test_main_py_tem_somente_o_diff_minimo_autorizado(self):
        self.assertEqual(MAIN_SOURCE.count(NEW_IMPORT), 1)
        self.assertEqual(MAIN_SOURCE.count(NEW_BRANCH), 1)
        restored = rollback_main_h(rollback_later_qpainter_i(rollback_navigation_back_main(MAIN_SOURCE)))
        self.assertEqual(
            hashlib.sha256(restored.encode("utf-8")).hexdigest(),
            BASE_MAIN_HASH,
        )
        method = MAIN_SOURCE[
            MAIN_SOURCE.index("    def carregar_botoes_disciplinas(self):"):
            MAIN_SOURCE.index("    def carregar_concursos(self):")
        ]
        paused = method[method.index("            if pausada:"):method.index("            botao.clicked.connect(")]
        self.assertIsNone(re.search(r"#[0-9A-Fa-f]{6,8}\b", paused))
        self.assertEqual(paused.count("qss_color("), 9)
        self.assertEqual(paused.count('if tema_atual == "futurista"'), 1)
        self.assertEqual(paused.count('elif tema_atual == "escuro"'), 1)
        self.assertIn('else:', paused)
        self.assertIn('text-align:left; padding-left:14px;', paused)

    def test_qss_renderiza_sem_tokens_pendentes_e_hash_final(self):
        for theme_name in ("claro", "escuro", "futurista"):
            qss = getattr(tema, f"stylesheet_{theme_name}")()
            with self.subTest(theme=theme_name):
                self.assertNotIn("{{color:", qss)
                self.assertNotIn("{{gradient:", qss)
                qss_h = strip_navigation_layer(theme_name, qss)
                self.assertEqual(qss_hash(qss_h), BLOCK_H_QSS[theme_name])

    def test_rollback_da_camada_h_recupera_exatamente_checkpoint_g(self):
        for theme_name in ("claro", "escuro", "futurista"):
            qss = getattr(tema, f"stylesheet_{theme_name}")()
            with self.subTest(theme=theme_name):
                self.assertEqual(
                    qss_hash(strip_block_h(theme_name, qss)),
                    BLOCK_G_QSS[theme_name],
                )

    def test_arquivos_protegidos_e_metadados_permanecem_inalterados(self):
        for relative, expected in PROTECTED_HASHES.items():
            digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(digest, expected, relative)
        self.assertEqual(VIGHNA_VERSION, "0.29.59")
        self.assertEqual(VIGHNA_BUILD, "questions-center-editor-viewer-futuristic-text-v1")
        self.assertEqual(VIGHNA_SCHEMA, 25)

    def test_camada_h_foi_acrescentada_apos_g_nos_tres_temas(self):
        self.assertEqual(TEMA_SOURCE.count('render_qss("claro", ESTILO_DASHBOARD_BLOCO_H)'), 1)
        self.assertEqual(TEMA_SOURCE.count('render_qss("escuro", ESTILO_DASHBOARD_BLOCO_H)'), 1)
        self.assertEqual(TEMA_SOURCE.count('render_qss("futurista", ESTILO_DASHBOARD_BLOCO_H)'), 1)
        for theme_name in ("claro", "escuro", "futurista"):
            line = next(
                line for line in TEMA_SOURCE.splitlines()
                if f'render_qss("{theme_name}", ESTILO_DASHBOARD_BLOCO_H)' in line
            )
            self.assertLess(
                line.index(f'render_qss("{theme_name}", ESTILO_DASHBOARD_BLOCO_G)'),
                line.index(f'render_qss("{theme_name}", ESTILO_DASHBOARD_BLOCO_H)'),
            )


if __name__ == "__main__":
    unittest.main()
