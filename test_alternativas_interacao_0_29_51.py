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


class AlternativasInteracao051Tests(unittest.TestCase):
    def test_versao_build(self):
        self.assertIn('VIGHNA_VERSION = "0.29.51"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "alternative-card-selection-v1"', VERSAO)
        self.assertIn('VIGHNA_SCHEMA = 25', VERSAO)

    def test_card_inteiro_pode_selecionar(self):
        carregar = ast.unparse(metodo("JanelaResolverQuestoes", "carregar_atual"))
        filtro = ast.unparse(metodo("JanelaResolverQuestoes", "eventFilter"))
        selecionar = ast.unparse(metodo("JanelaResolverQuestoes", "selecionar_alternativa_por_letra"))
        self.assertIn("frame.installEventFilter(self)", carregar)
        self.assertIn("texto.installEventFilter(self)", carregar)
        self.assertIn("MouseButtonRelease", filtro)
        self.assertIn("Qt.LeftButton", filtro)
        self.assertIn("self.selecionar_alternativa_por_letra(letra)", filtro)
        self.assertIn("radio.setChecked(True)", selecionar)

    def test_tesoura_fica_independente_do_clique_no_card(self):
        carregar = ast.unparse(metodo("JanelaResolverQuestoes", "carregar_atual"))
        self.assertIn("self._letra_por_widget_alternativa[frame] = letra", carregar)
        self.assertIn("self._letra_por_widget_alternativa[texto] = letra", carregar)
        self.assertNotIn("self._letra_por_widget_alternativa[eliminar]", carregar)

    def test_selecionar_alternativa_eliminada_restaura_primeiro(self):
        selecionar = ast.unparse(metodo("JanelaResolverQuestoes", "selecionar_alternativa_por_letra"))
        self.assertIn("botao.isChecked()", selecionar)
        self.assertIn("botao.setChecked(False)", selecionar)

    def test_eliminacao_apaga_card_texto_e_radio(self):
        eliminar = ast.unparse(metodo("JanelaResolverQuestoes", "alternar_eliminacao_alternativa"))
        self.assertIn("for widget in (frame, texto, radio)", eliminar)
        self.assertIn("widget.setProperty('eliminated', eliminada)", eliminar)
        self.assertIn("fonte.setStrikeOut(eliminada)", eliminar)
        self.assertIn("radio.isChecked()", eliminar)

    def test_tema_tem_estado_visual_eliminado_nos_tres_temas(self):
        self.assertGreaterEqual(
            TEMA.count('QFrame#questionSolverAlternative[eliminated="true"][answerState="normal"]'),
            3,
        )
        self.assertGreaterEqual(
            TEMA.count('QRadioButton#questionSolverRadio[eliminated="true"]'),
            3,
        )


if __name__ == "__main__":
    unittest.main()
