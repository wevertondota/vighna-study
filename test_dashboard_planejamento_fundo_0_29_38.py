import unittest
from pathlib import Path

TEMA = Path('tema.py').read_text(encoding='utf-8')
VERSAO = Path('versao.py').read_text(encoding='utf-8')


class TestDashboardPlanejamentoFundo(unittest.TestCase):
    def test_card_planejamento_sem_verde(self):
        self.assertIn('QFrame#dashboardInsightSummary {', TEMA)
        self.assertIn('stop:0 #202733', TEMA)
        self.assertIn('stop:1 #1D2430', TEMA)
        self.assertNotIn('stop:0 #15B67E', TEMA)
        self.assertNotIn('stop:1 #0B5E4E', TEMA)

    def test_botao_planejamento_escuro(self):
        self.assertIn('QPushButton#planningSummaryButton {', TEMA)
        self.assertIn('background-color: #202833;', TEMA)
        self.assertIn('border: 1px solid #596474;', TEMA)

    def test_versao_atualizada(self):
        self.assertIn('VIGHNA_VERSION = "0.29.38"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "dashboard-planejamento-fundo-equalizado-v1"', VERSAO)


if __name__ == '__main__':
    unittest.main()
