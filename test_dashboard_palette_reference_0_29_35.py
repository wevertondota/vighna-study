from pathlib import Path
import unittest

class DashboardPaletteReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tema = Path('tema.py').read_text(encoding='utf-8')
        cls.versao = Path('versao.py').read_text(encoding='utf-8')

    def test_version_updated(self):
        self.assertIn('VIGHNA_VERSION = "0.29.35"', self.versao)
        self.assertIn('VIGHNA_BUILD = "dashboard-futurista-palette-reference-v1"', self.versao)

    def test_reference_palette_applied(self):
        expected = [
            '#0B111D',  # fundo geral
            '#212A35',  # campo de busca / botões escuros
            '#4447E8',  # CTA violeta-azulado
            '#14A779',  # card verde de progresso
            '#16534D',  # base escura do progresso
            '#5A402D',  # selo âmbar de atenção
        ]
        for color in expected:
            with self.subTest(color=color):
                self.assertIn(color, self.tema)

    def test_focus_button_matches_primary_cta_family(self):
        self.assertIn('QWidget#dashboardRoot QFrame#focusDashboardMainCard QPushButton#dashboardFocusPrimaryButton', self.tema)
        self.assertIn('stop:0 #4447E8, stop:1 #3B40D4', self.tema)

if __name__ == '__main__':
    unittest.main()
