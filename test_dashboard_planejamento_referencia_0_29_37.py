import unittest
from pathlib import Path

MAIN = Path('main.py').read_text(encoding='utf-8')
TEMA = Path('tema.py').read_text(encoding='utf-8')
VERSAO = Path('versao.py').read_text(encoding='utf-8')


class TestDashboardPlanejamentoReferencia(unittest.TestCase):
    def test_widget_arco_planejamento_existe(self):
        self.assertIn('class DashboardPlanningArcWidget(QWidget):', MAIN)
        self.assertIn('self.dashboard_planejamento_meta_gauge = DashboardPlanningArcWidget()', MAIN)
        self.assertIn('self.dashboard_planejamento_meta_gauge.setProgress(', MAIN)

    def test_estilos_planejamento_verde(self):
        self.assertIn('QFrame#dashboardInsightSummary {', TEMA)
        self.assertIn('stop:0 #15B67E', TEMA)
        self.assertIn('stop:1 #0B5E4E', TEMA)
        self.assertIn('QPushButton#planningSummaryButton {', TEMA)
        self.assertIn('background-color: rgba(12, 49, 43, 0.48);', TEMA)

    def test_versao_atualizada(self):
        self.assertIn('VIGHNA_VERSION = "0.29.37"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "dashboard-planejamento-referencia-v1"', VERSAO)


if __name__ == '__main__':
    unittest.main()
