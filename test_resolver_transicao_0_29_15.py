from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / "main.py").read_text(encoding="utf-8")
VERSAO = (ROOT / "versao.py").read_text(encoding="utf-8")


class TestTransicaoResolverSemFlicker(unittest.TestCase):
    def test_widgets_das_alternativas_tem_parent_explicito(self):
        self.assertIn("frame = QFrame(self.alternativas_container)", MAIN)
        self.assertIn("eliminar = QToolButton(frame)", MAIN)
        self.assertRegex(
            MAIN,
            r"radio = QRadioButton\(\s*_rotulo_resposta_questao\([\s\S]*?\),\s*frame\s*\)",
        )
        self.assertRegex(
            MAIN,
            r"texto = QLabel\(\s*alternativa\[[\s\S]*?\],\s*frame\s*\)",
        )

    def test_reconstrucao_das_alternativas_e_atomica(self):
        inicio = MAIN.index("self.alternativas_container.setUpdatesEnabled(False)")
        fim = MAIN.index("self.alternativas_container.setUpdatesEnabled(True)", inicio)
        trecho = MAIN[inicio:fim]
        self.assertIn("self.limpar_alternativas()", trecho)
        self.assertIn("for alternativa in dados", trecho)
        self.assertLess(
            trecho.index("self.limpar_alternativas()"),
            trecho.index("for alternativa in dados"),
        )

    def test_widgets_antigos_sao_ocultados_antes_do_delete_later(self):
        inicio = MAIN.index("def limpar_alternativas(self):")
        fim = MAIN.index("def alternar_eliminacao_alternativa", inicio)
        trecho = MAIN[inicio:fim]
        self.assertIn("widget.hide()", trecho)
        self.assertIn("widget.deleteLater()", trecho)
        self.assertLess(trecho.index("widget.hide()"), trecho.index("widget.deleteLater()"))

    def test_schema_permanece_compativel(self):
        self.assertIn('VIGHNA_SCHEMA = 22', VERSAO)


if __name__ == "__main__":
    unittest.main()
