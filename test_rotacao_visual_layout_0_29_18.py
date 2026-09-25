from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parent


class RotacaoVisualLayoutSourceTests(unittest.TestCase):
    def test_layout_da_forma_original_ganha_espaco_horizontal(self):
        fonte = (ROOT / "jogos.py").read_text(encoding="utf-8")
        self.assertIn("topo.addLayout(original_bloco, 1)", fonte)
        self.assertIn("topo.addWidget(self.pergunta, 2)", fonte)
        self.assertIn("self.preview_original.setMinimumSize(180, 88)", fonte)

    def test_grade_reserva_altura_para_as_seis_alternativas(self):
        fonte = (ROOT / "jogos.py").read_text(encoding="utf-8")
        self.assertIn("self.opcoes_layout.setRowMinimumHeight(linha, 98)", fonte)
        self.assertIn("botao.setMinimumSize(150, 98)", fonte)
        self.assertIn("desenho.setMinimumSize(110, 78)", fonte)

    def test_canvas_nao_forca_celula_minima_que_possa_extrapolar(self):
        fonte = (ROOT / "jogos.py").read_text(encoding="utf-8")
        self.assertNotIn("lado = max(5.0, lado)", fonte)
        self.assertIn("margem = min(10.0, max(4.0, menor_dimensao * 0.08))", fonte)

    def test_tres_temas_preservam_altura_da_opcao_de_rotacao(self):
        tema = (ROOT / "tema.py").read_text(encoding="utf-8")
        padrao = re.compile(
            r"QPushButton#rotationOptionButton\s*\{\s*"
            r"min-height:\s*98px;\s*padding:\s*0px;",
            re.MULTILINE,
        )
        self.assertEqual(len(padrao.findall(tema)), 3)

    def test_versao_foi_avancada_sem_migracao_de_schema(self):
        versao = (ROOT / "versao.py").read_text(encoding="utf-8")
        self.assertIn('VIGHNA_VERSION = "0.29.18"', versao)
        self.assertIn('VIGHNA_BUILD = "pausa-rotacao-visual-layout-v2"', versao)
        self.assertIn("VIGHNA_SCHEMA = 22", versao)


if __name__ == "__main__":
    unittest.main()
