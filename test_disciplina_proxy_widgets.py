import unittest
from pathlib import Path

MAIN = Path(__file__).with_name('main.py').read_text(encoding='utf-8')


class DisciplinaProxyWidgetsTests(unittest.TestCase):
    def test_proxies_legados_possuem_container_pai_oculto(self):
        self.assertIn('self._proxies_disciplina = QWidget(tela)', MAIN)
        self.assertIn('self._proxies_disciplina.setVisible(False)', MAIN)
        self.assertIn('"Capítulos", self._proxies_disciplina', MAIN)
        self.assertIn('"Desligar tópico", self._proxies_disciplina', MAIN)

    def test_proxy_capitulos_nunca_e_exibido(self):
        self.assertIn('self.botao_capitulos.setVisible(False)', MAIN)
        self.assertNotIn('self.botao_capitulos.setVisible(permite_capitulos)', MAIN)


if __name__ == '__main__':
    unittest.main()
