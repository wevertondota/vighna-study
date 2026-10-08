from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest
from _design_system_test_helpers import strip_cards_global_block_a_source

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
MAIN_PATH = ROOT / "main.py"
MAIN_SOURCE = MAIN_PATH.read_text(encoding="utf-8")

TOKENS = {
    "dashboard.planning_arc_track",
    "dashboard.planning_arc_fill",
    "dashboard.planning_arc_text",
    "dashboard.quality_donut_track_dark",
    "dashboard.quality_donut_track_light",
    "dashboard.quality_donut_fill",
}
EXPECTED = {
    "dashboard.planning_arc_track": "#52CFF3E1",
    "dashboard.planning_arc_fill": "#B9FFE3",
    "dashboard.planning_arc_text": "#F4FFFA",
    "dashboard.quality_donut_track_dark": "#263B4F",
    "dashboard.quality_donut_track_light": "#DCE5ED",
    "dashboard.quality_donut_fill": "#2FB4C7",
}

BASE_H_MAIN_HASH = "2a48becdca1907644dedd23b33d19299dfdee2834440815537d6479df3b827b8"
BASE_H_TEMA_HASH = "d164c3b89ca1bb6535a393e70a371d4148e1bf1d76aa03299e9eac55d4861cc7"
PROTECTED_HASHES = {
    "estudos.db": "034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef",
    "versao.py": "c201d237e622dd2269838e54914458fd775c7ec1a91f07b518775ee833caa439",
    "foco.py": "8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed",
    "jogos.py": "498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286",
    "checkpoint.py": "947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38",
}

OLD_PLANNING_TRACK = '''        trilha = QPen(QColor(207, 243, 225, 82), 8)\n        trilha.setCapStyle(Qt.RoundCap)\n        painter.setPen(trilha)\n        painter.drawArc(rect, 180 * 16, -180 * 16)\n'''
NEW_PLANNING_TRACK = '''        tema_atual = normalizar_tema(\n            getattr(self.window(), "tema_atual", "claro")\n        )\n\n        trilha = QPen(\n            qcolor(tema_atual, "dashboard.planning_arc_track"),\n            8\n        )\n        trilha.setCapStyle(Qt.RoundCap)\n        painter.setPen(trilha)\n        painter.drawArc(rect, 180 * 16, -180 * 16)\n'''
OLD_PLANNING_FILL = "            valor = QPen(QColor('#B9FFE3'), 8)\n"
NEW_PLANNING_FILL = '''            valor = QPen(\n                qcolor(tema_atual, "dashboard.planning_arc_fill"),\n                8\n            )\n'''
OLD_PLANNING_TEXT = "        painter.setPen(QColor('#F4FFFA'))\n"
NEW_PLANNING_TEXT = '''        painter.setPen(\n            qcolor(tema_atual, "dashboard.planning_arc_text")\n        )\n'''
OLD_DONUT_TRACK = '''        cor_trilha = QColor(\n            "#263B4F"\n            if cor_texto.lightness() > 150\n            else "#DCE5ED"\n        )\n'''
NEW_DONUT_TRACK = '''        tema_atual = normalizar_tema(\n            getattr(self.window(), "tema_atual", "claro")\n        )\n\n        cor_trilha = qcolor(\n            tema_atual,\n            "dashboard.quality_donut_track_dark"\n            if cor_texto.lightness() > 150\n            else "dashboard.quality_donut_track_light"\n        )\n'''
OLD_DONUT_FILL = '''        caneta_valor = QPen(\n            QColor("#2FB4C7"),\n            11\n        )\n'''
NEW_DONUT_FILL = '''        caneta_valor = QPen(\n            qcolor(tema_atual, "dashboard.quality_donut_fill"),\n            11\n        )\n'''


def class_slice(name: str, next_name: str) -> str:
    start = MAIN_SOURCE.index(f"class {name}")
    end = MAIN_SOURCE.index(f"class {next_name}", start)
    return MAIN_SOURCE[start:end]


def rollback_navigation_back_main(source: str) -> str:
    block = '''        voltar.setProperty(\n            "navigationBack",\n            True\n        )\n'''
    if source.count(block) != 6:
        raise AssertionError("marcações navigationBack inesperadas")
    return source.replace(block, "")


def rollback_navigation_tema(source: str) -> str:
    source = strip_cards_global_block_a_source(source)
    source = re.sub(
        r'# ============================================================\n'
        r'# Design System — Navegação principal — Retornos ao Dashboard\n'
        r'# Camada aditiva de alta precisão: somente os seis subtleButton\n'
        r'# marcados explicitamente com navigationBack=true\.\n'
        r'# ============================================================\n'
        r'ESTILO_NAVEGACAO_RETORNOS_DASHBOARD = r"""\n.*?\n"""\n\n',
        "", source, count=1, flags=re.S,
    )
    source = re.sub(
        r'# ============================================================\n'
        r'# Design System — Navegação principal — Busca global\n'
        r'# Camada cromática aditiva, restrita ao QDialog da command palette\.\n'
        r'# O gatilho globalSearchTrigger continua pertencendo ao Dashboard A\.\n'
        r'# ============================================================\n'
        r'ESTILO_NAVEGACAO_BUSCA_GLOBAL = r"""\n.*?\n"""\n\n',
        "", source, count=1, flags=re.S,
    )
    for theme in ("claro", "escuro", "futurista"):
        source = source.replace(
            f' + render_qss("{theme}", ESTILO_NAVEGACAO_BUSCA_GLOBAL)',
            "", 1,
        )
        source = source.replace(
            f' + render_qss("{theme}", ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)',
            "", 1,
        )
    return source


def rollback_main_i(source: str) -> str:
    pairs = (
        (NEW_PLANNING_TRACK, OLD_PLANNING_TRACK),
        (NEW_PLANNING_FILL, OLD_PLANNING_FILL),
        (NEW_PLANNING_TEXT, OLD_PLANNING_TEXT),
        (NEW_DONUT_TRACK, OLD_DONUT_TRACK),
        (NEW_DONUT_FILL, OLD_DONUT_FILL),
    )
    for new, old in pairs:
        if source.count(new) != 1:
            raise AssertionError("diff I esperado não foi encontrado de forma única")
        source = source.replace(new, old, 1)
    return source


class DashboardBlockIDesignSystemTests(unittest.TestCase):
    def test_orcamento_final_e_contrato_exato(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 928)
        self.assertEqual(len(ALL_TOKENS), 1030)
        self.assertEqual(len(TOKENS), 6)
        for path in TOKENS:
            self.assertIs(token_spec(path).kind, TokenKind.COLOR)

    def test_valores_qpainter_preservados_nos_tres_temas(self):
        for theme_name in ("claro", "escuro", "futurista"):
            theme = get_theme(theme_name)
            for path, expected in EXPECTED.items():
                with self.subTest(theme=theme_name, path=path):
                    self.assertEqual(theme.color(path).value, expected)
        self.assertEqual(
            get_theme("claro").color("dashboard.planning_arc_track").argb,
            (82, 207, 243, 225),
        )

    def test_consumidores_qpainter_nao_contem_cores_fisicas(self):
        planning = class_slice("DashboardPlanningArcWidget", "DashboardDonutWidget")
        donut = class_slice("DashboardDonutWidget", "JanelaInicializacao")
        for source in (planning, donut):
            self.assertIsNone(re.search(r"#[0-9A-Fa-f]{6,8}\\b", source))
            self.assertNotIn("QColor(", source)
        for path in TOKENS:
            self.assertIn(path, MAIN_SOURCE)

    def test_geometria_e_logica_visual_permanecem(self):
        planning = class_slice("DashboardPlanningArcWidget", "DashboardDonutWidget")
        donut = class_slice("DashboardDonutWidget", "JanelaInicializacao")
        for marker in (
            "self.setMinimumSize(196, 90)",
            "self.setMaximumHeight(100)",
            "largura = max(96, self.width() - 52)",
            "altura = min(self.height() - 24, 68)",
            "painter.drawArc(rect, 180 * 16, -180 * 16)",
            "int(-180 * 16 * proporcao)",
            "fonte.setPointSize(16)",
        ):
            self.assertIn(marker, planning)
        for marker in (
            "self.setMinimumSize(128, 128)",
            "self.setMaximumSize(150, 150)",
            "margem = 16",
            "cor_texto.lightness() > 150",
            "360 * 16",
            "90 * 16",
            "-360",
            "fonte.setPointSize(16)",
        ):
            self.assertIn(marker, donut)
        self.assertIn("QPen(\n            qcolor(tema_atual, \"dashboard.planning_arc_track\"),\n            8", planning)
        self.assertIn("qcolor(tema_atual, \"dashboard.quality_donut_fill\"),\n            11", donut)

    def test_main_py_possui_somente_o_diff_cromatico_autorizado(self):
        restored = rollback_main_i(rollback_navigation_back_main(MAIN_SOURCE))
        self.assertEqual(
            hashlib.sha256(restored.encode("utf-8")).hexdigest(),
            BASE_H_MAIN_HASH,
        )
        planning = class_slice("DashboardPlanningArcWidget", "DashboardDonutWidget")
        donut = class_slice("DashboardDonutWidget", "JanelaInicializacao")
        self.assertEqual(planning.count("qcolor("), 3)
        self.assertEqual(donut.count("qcolor("), 2)
        self.assertEqual(MAIN_SOURCE.count('getattr(self.window(), "tema_atual", "claro")'), 2)

    def test_tema_qss_permanece_equivalente_ao_checkpoint_h_apos_retirar_navegacao(self):
        source = (ROOT / "tema.py").read_text(encoding="utf-8")
        restored = rollback_navigation_tema(source)
        digest = hashlib.sha256(restored.encode("utf-8")).hexdigest()
        self.assertEqual(digest, BASE_H_TEMA_HASH)

    def test_arquivos_protegidos_e_metadados_permanecem_inalterados(self):
        for relative, expected in PROTECTED_HASHES.items():
            digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(digest, expected, relative)
        self.assertEqual(VIGHNA_VERSION, "0.29.59")
        self.assertEqual(VIGHNA_BUILD, "updates-center-v1")
        self.assertEqual(VIGHNA_SCHEMA, 25)

    def test_prioridade_dormente_permanece_intocada(self):
        self.assertIn("fila_painel.setVisible(False)", MAIN_SOURCE)
        planning = class_slice("DashboardPlanningArcWidget", "DashboardDonutWidget")
        donut = class_slice("DashboardDonutWidget", "JanelaInicializacao")
        self.assertNotIn("priorityQueuePanel", planning)
        self.assertNotIn("priorityQueuePanel", donut)


if __name__ == "__main__":
    unittest.main()
