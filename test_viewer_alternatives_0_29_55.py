import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / "main.py").read_text(encoding="utf-8")
TEMA = (ROOT / "tema.py").read_text(encoding="utf-8")
VERSAO = (ROOT / "versao.py").read_text(encoding="utf-8")
TREE = ast.parse(MAIN)


def metodo(classe, nome):
    for node in TREE.body:
        if isinstance(node, ast.ClassDef) and node.name == classe:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == nome:
                    return item
    raise AssertionError(f"Método {classe}.{nome} não encontrado")


class ViewerAlternatives055Tests(unittest.TestCase):
    def test_versao(self):
        self.assertIn('VIGHNA_VERSION = "0.29.55"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "viewer-alternatives-and-transient-guard-v2"', VERSAO)
        self.assertIn('VIGHNA_SCHEMA = 25', VERSAO)

    def test_visualizador_nao_chama_setvisible_em_label_sem_parent(self):
        init = ast.unparse(metodo("JanelaVisualizarQuestao", "__init__"))
        self.assertIn("QLabel(alternativa['texto'], card)", init)
        self.assertIn("texto.setObjectName('questionAlternativeText')", init)
        self.assertNotIn("texto.setVisible(tipo_questao != 'CERTO_ERRADO')", init)

    def test_texto_da_alternativa_tem_politica_de_tamanho_expansiva(self):
        init = ast.unparse(metodo("JanelaVisualizarQuestao", "__init__"))
        self.assertIn("texto.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)", init)
        self.assertIn("texto.setAlignment(Qt.AlignLeft | Qt.AlignTop)", init)
        self.assertIn("correto.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)", init)

    def test_guarda_transitoria_restabelece_widget_quando_reparentado(self):
        normalizar = ast.unparse(metodo("AplicacaoVighna", "_normalizar_top_level_acidental"))
        self.assertIn("receiver.parentWidget() is not None", normalizar)
        self.assertIn("receiver.setAttribute(Qt.WA_DontShowOnScreen, False)", normalizar)
        self.assertIn("receiver.show()", normalizar)
        self.assertIn("receiver.hide()", normalizar)

    def test_qss_define_texto_do_visualizador(self):
        self.assertGreaterEqual(TEMA.count("QLabel#questionAlternativeText"), 3)
        self.assertIn("color: #1f2937", TEMA)
        self.assertIn("color: #e5e7eb", TEMA)
        self.assertIn("color: #EAF7FF", TEMA)


if __name__ == "__main__":
    unittest.main()
