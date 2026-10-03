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


class EliminatedOptionEmphasis053Tests(unittest.TestCase):
    def test_versao_build(self):
        self.assertIn('VIGHNA_VERSION = "0.29.53"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "eliminated-option-emphasis-v1"', VERSAO)
        self.assertIn('VIGHNA_SCHEMA = 25', VERSAO)

    def test_tachado_funcional_permanece(self):
        eliminar = ast.unparse(metodo("JanelaResolverQuestoes", "alternar_eliminacao_alternativa"))
        self.assertIn("fonte.setStrikeOut(eliminada)", eliminar)
        self.assertIn("widget.setProperty('eliminated', eliminada)", eliminar)

    def test_estado_eliminado_tem_fundo_e_borda_diferenciados_nos_tres_temas(self):
        seletor = 'QFrame#questionSolverAlternative[eliminated="true"][answerState="normal"]'
        self.assertGreaterEqual(TEMA.count(seletor), 3)
        self.assertGreaterEqual(TEMA.count("border: 1px dashed"), 3)

    def test_texto_eliminado_tem_cor_mais_apagada_nos_tres_temas(self):
        seletor = 'QLabel#questionSolverAlternativeText[eliminated="true"]'
        self.assertGreaterEqual(TEMA.count(seletor), 3)

    def test_tesoura_marcada_tambem_tem_estado_visual(self):
        seletor = 'QToolButton#questionSolverEliminateButton:checked'
        self.assertGreaterEqual(TEMA.count(seletor), 3)

    def test_clique_no_card_continua_selecionando(self):
        filtro = ast.unparse(metodo("JanelaResolverQuestoes", "eventFilter"))
        self.assertIn("self.selecionar_alternativa_por_letra(letra)", filtro)


if __name__ == "__main__":
    unittest.main()
