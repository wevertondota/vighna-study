from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / "main.py").read_text(encoding="utf-8")


class ImportacaoTxtIntegracaoTests(unittest.TestCase):
    def test_central_expoe_txt(self):
        self.assertIn('"Arquivo TXT"', MAIN)
        self.assertIn('"Selecionar TXT"', MAIN)
        self.assertIn('"txt"', MAIN)

    def test_dispatcher_encaminha_txt(self):
        self.assertIn('elif origem == "txt":', MAIN)
        self.assertIn('self.importar_questoes_txt()', MAIN)

    def test_txt_reutiliza_analisador_e_revisao_comum(self):
        self.assertIn('dados_txt = ler_arquivo_txt_questoes(caminho)', MAIN)
        self.assertIn('analisar_texto_questoes_pdf(', MAIN)
        self.assertIn('origem_tipo="txt"', MAIN)

    def test_backup_especifico_antes_da_gravacao(self):
        self.assertIn('"txt": "antes_importar_questoes_txt"', MAIN)


if __name__ == "__main__":
    unittest.main()
