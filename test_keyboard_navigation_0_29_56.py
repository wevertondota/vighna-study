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


class KeyboardNavigation056Tests(unittest.TestCase):
    def test_versao_build(self):
        self.assertIn('VIGHNA_VERSION = "0.29.56"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "question-keyboard-navigation-v1"', VERSAO)
        self.assertIn('VIGHNA_SCHEMA = 25', VERSAO)

    def test_setas_percorrem_sem_marcar(self):
        filtro = ast.unparse(metodo("JanelaResolverQuestoes", "eventFilter"))
        mover = ast.unparse(metodo("JanelaResolverQuestoes", "mover_foco_teclado_alternativa"))
        self.assertIn("Qt.Key_Up", filtro)
        self.assertIn("Qt.Key_Down", filtro)
        self.assertIn("Qt.Key_Left", filtro)
        self.assertIn("Qt.Key_Right", filtro)
        self.assertIn("self.mover_foco_teclado_alternativa(-1)", filtro)
        self.assertIn("self.mover_foco_teclado_alternativa(1)", filtro)
        self.assertNotIn("setChecked", mover)

    def test_espaco_tacha_alternativa_focada(self):
        filtro = ast.unparse(metodo("JanelaResolverQuestoes", "eventFilter"))
        alternar = ast.unparse(metodo("JanelaResolverQuestoes", "alternar_eliminacao_foco_teclado"))
        self.assertIn("Qt.Key_Space", filtro)
        self.assertIn("self.alternar_eliminacao_foco_teclado()", filtro)
        self.assertIn("botao.setChecked(not botao.isChecked())", alternar)

    def test_enter_seleciona_e_segundo_confirma(self):
        acionar = ast.unparse(metodo("JanelaResolverQuestoes", "acionar_enter_foco_teclado"))
        self.assertIn("self.alternativa_selecionada() != letra", acionar)
        self.assertIn("self.selecionar_alternativa_por_letra(letra)", acionar)
        self.assertIn("self.confirmar_resposta()", acionar)

    def test_foco_visual_existe_nos_tres_temas(self):
        self.assertGreaterEqual(
            TEMA.count('QFrame#questionSolverAlternative[keyboardFocus="true"][answerState="normal"]'),
            3,
        )
        carregar = ast.unparse(metodo("JanelaResolverQuestoes", "carregar_atual"))
        self.assertIn("frame.setFocusPolicy(Qt.StrongFocus)", carregar)
        self.assertIn("frame.setProperty('keyboardFocus', False)", carregar)

    def test_filtro_global_e_removido_ao_fechar(self):
        init = ast.unparse(metodo("JanelaResolverQuestoes", "__init__"))
        done = ast.unparse(metodo("JanelaResolverQuestoes", "done"))
        self.assertIn("app.installEventFilter(self)", init)
        self.assertIn("app.removeEventFilter(self)", done)


if __name__ == "__main__":
    unittest.main()
