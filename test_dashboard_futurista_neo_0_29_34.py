import ast
import re
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / 'main.py').read_text(encoding='utf-8')
TEMA = (ROOT / 'tema.py').read_text(encoding='utf-8')
VERSAO = (ROOT / 'versao.py').read_text(encoding='utf-8')


class DashboardFuturistaNeoTests(unittest.TestCase):
    def test_fontes_compilam(self):
        ast.parse(MAIN)
        ast.parse(TEMA)

    def test_versao(self):
        self.assertIn('VIGHNA_VERSION = "0.29.34"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "dashboard-futurista-neo-v1"', VERSAO)
        self.assertIn('VIGHNA_SCHEMA = 23', VERSAO)

    def test_camadas_neo_e_aplicacao_final(self):
        self.assertIn('ESTILO_DASHBOARD_NEO_FUTURISTA = r"""', TEMA)
        self.assertIn('+ ESTILO_DASHBOARD_NEO_FUTURISTA', TEMA)
        for seletor in (
            'QFrame#dashboardTopBar',
            'QPushButton#globalSearchTrigger',
            'QPushButton#questionsNavButton',
            'QFrame#dashboardInsightSummary',
            'QFrame#dashboardTodayAction[simpleHero="true"]',
            'QFrame#focusQuickCard[cardRole="progress"]',
        ):
            self.assertIn(seletor, TEMA)

    def test_foco_principal_nao_foi_alvo_da_nova_camada(self):
        inicio = TEMA.index('ESTILO_DASHBOARD_NEO_FUTURISTA = r"""')
        fim = TEMA.index('ESTILO_BUSCA_GLOBAL_FUTURISTA = r"""', inicio)
        neo = TEMA[inicio:fim]
        for seletor in (
            'QFrame#dashboardFocusPanel',
            'QFrame#focusDashboardMainCard',
            'QPushButton#dashboardFocusPrimaryButton',
        ):
            self.assertNotIn(seletor, neo)

    def test_card_progresso_tem_role_exclusiva(self):
        self.assertIn('progresso_card.setProperty("cardRole", "progress")', MAIN)
        self.assertIn('QFrame#focusQuickCard[cardRole="progress"]', TEMA)

    def test_paleta_neo_tem_hierarquia_semantica(self):
        for cor in (
            '#06131D',  # fundo profundo
            '#58A7FF',  # CTA azul
            '#7DE0A8',  # sucesso
            '#FFB66E',  # atenção
        ):
            self.assertIn(cor, TEMA)

    def test_banco_permanece_integro(self):
        db = ROOT / 'estudos.db'
        with sqlite3.connect(db) as con:
            self.assertEqual(con.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(con.execute('PRAGMA foreign_key_check').fetchall(), [])


if __name__ == '__main__':
    unittest.main()
