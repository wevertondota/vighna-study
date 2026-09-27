import unittest
from pathlib import Path

MAIN = Path('main.py').read_text(encoding='utf-8')
VERSAO = Path('versao.py').read_text(encoding='utf-8')


class TestDashboardPlanejamentoCompacto(unittest.TestCase):
    def test_card_compactado(self):
        self.assertIn('self.dashboard_resumo_ia.setMinimumHeight(160)', MAIN)
        self.assertIn('resumo_ia_layout.setContentsMargins(12, 5, 12, 6)', MAIN)
        self.assertIn('resumo_ia_icone.setFixedSize(30, 30)', MAIN)
        self.assertIn('self.dashboard_planejamento_resumo_botao.setFixedHeight(34)', MAIN)

    def test_gauge_compactado(self):
        self.assertIn('self.setMinimumSize(196, 90)', MAIN)
        self.assertIn('self.setMaximumHeight(100)', MAIN)
        self.assertIn('trilha = QPen(QColor(207, 243, 225, 82), 8)', MAIN)
        self.assertIn("valor = QPen(QColor('#B9FFE3'), 8)", MAIN)
        self.assertIn('fonte.setPointSize(16)', MAIN)

    def test_versao_atualizada(self):
        self.assertIn('VIGHNA_VERSION = "0.29.39"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "dashboard-planejamento-compacto-v1"', VERSAO)


if __name__ == '__main__':
    unittest.main()
