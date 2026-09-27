import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "main.py"
VERSAO = ROOT / "versao.py"


class TestCentralSelecaoResultado02927(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = MAIN.read_text(encoding="utf-8")
        cls.versao = VERSAO.read_text(encoding="utf-8")

    def test_main_tem_sintaxe_valida(self):
        ast.parse(self.main)

    def test_versao_e_build(self):
        self.assertIn('VIGHNA_VERSION = "0.29.27"', self.versao)
        self.assertIn('VIGHNA_BUILD = "central-selecao-resultado-v1"', self.versao)
        self.assertIn('VIGHNA_SCHEMA = 23', self.versao)

    def test_checkbox_global_no_cabecalho(self):
        self.assertIn('questionsHeaderSelectAll', self.main)
        self.assertIn('self.questoes_selecionar_todas_header.clicked.connect', self.main)
        self.assertIn('Selecionar todas as questões do resultado atual.', self.main)

    def test_controle_superior_reflete_resultado(self):
        self.assertIn('Selecionar todo o resultado · 0', self.main)
        self.assertIn('f"Selecionar todo o resultado · {len(filtradas)}"', self.main)
        self.assertIn('_questoes_ids_resultado_atual', self.main)

    def test_estado_parcial_e_sincronizacao(self):
        self.assertIn('def _sincronizar_selecao_global_questoes', self.main)
        self.assertIn('Qt.PartiallyChecked', self.main)
        self.assertIn('def _reposicionar_checkbox_cabecalho_questoes', self.main)

    def test_filtro_limpa_selecao_global(self):
        self.assertIn('self.questoes_selecionar_todas_header.setCheckState(Qt.Unchecked)', self.main)
        self.assertIn('self.questoes_selecionar_todas.setChecked(False)', self.main)

    def test_ajuda_documenta_selecao_resultado(self):
        self.assertIn('• Selecionar resultado:', self.main)


if __name__ == "__main__":
    unittest.main()
