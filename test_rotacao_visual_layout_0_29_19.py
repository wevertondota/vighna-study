from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parent


class RotacaoVisualLayoutScrollSourceTests(unittest.TestCase):
    def test_area_rolavel_protege_altura_do_minijogo(self):
        fonte = (ROOT / "jogos.py").read_text(encoding="utf-8")
        self.assertIn("QScrollArea,", fonte)
        self.assertIn('self.scroll_area.setObjectName("rotationScrollArea")', fonte)
        self.assertIn("self.scroll_area.setWidgetResizable(True)", fonte)
        self.assertIn("self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)", fonte)
        self.assertIn("self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)", fonte)
        self.assertIn("conteudo_scroll.setMinimumHeight(520)", fonte)

    def test_grade_tem_container_proprio_e_duas_linhas_inteiras(self):
        fonte = (ROOT / "jogos.py").read_text(encoding="utf-8")
        self.assertIn('self.opcoes_container.setObjectName("rotationOptionsContainer")', fonte)
        self.assertIn("altura_opcao = 112", fonte)
        self.assertIn("(altura_opcao * 2)", fonte)
        self.assertIn("self.opcoes_layout.setRowMinimumHeight(linha, altura_opcao)", fonte)
        self.assertIn("botao.setMinimumSize(150, altura_opcao)", fonte)
        self.assertIn("desenho.setMinimumSize(110, 88)", fonte)
        self.assertIn("painel_layout.addWidget(self.opcoes_container, 0)", fonte)

    def test_forma_original_preserva_area_central(self):
        fonte = (ROOT / "jogos.py").read_text(encoding="utf-8")
        self.assertIn("topo.addLayout(original_bloco, 1)", fonte)
        self.assertIn("topo.addWidget(self.pergunta, 2)", fonte)
        self.assertIn("self.preview_original.setMinimumSize(180, 96)", fonte)
        self.assertIn("self.preview_original.setMaximumHeight(116)", fonte)

    def test_canvas_continua_escalando_sem_extrapolar(self):
        fonte = (ROOT / "jogos.py").read_text(encoding="utf-8")
        self.assertNotIn("lado = max(5.0, lado)", fonte)
        self.assertIn("margem = min(10.0, max(4.0, menor_dimensao * 0.08))", fonte)
        self.assertIn("lado = min(largura / colunas, altura / linhas)", fonte)

    def test_tres_temas_respeitam_altura_e_scroll_transparente(self):
        tema = (ROOT / "tema.py").read_text(encoding="utf-8")
        altura = re.compile(
            r"QPushButton#rotationOptionButton\s*\{\s*"
            r"min-height:\s*112px;\s*padding:\s*0px;",
            re.MULTILINE,
        )
        self.assertEqual(len(altura.findall(tema)), 3)
        self.assertEqual(tema.count("QScrollArea#rotationScrollArea"), 3)
        self.assertEqual(tema.count("QWidget#rotationOptionsContainer"), 3)

    def test_versao_avancada_sem_migracao(self):
        versao = (ROOT / "versao.py").read_text(encoding="utf-8")
        self.assertIn('VIGHNA_VERSION = "0.29.19"', versao)
        self.assertIn('VIGHNA_BUILD = "pausa-rotacao-visual-scroll-v3"', versao)
        self.assertIn("VIGHNA_SCHEMA = 22", versao)


if __name__ == "__main__":
    unittest.main()
