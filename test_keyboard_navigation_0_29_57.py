import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / "main.py").read_text(encoding="utf-8")
VERSAO = (ROOT / "versao.py").read_text(encoding="utf-8")
TREE = ast.parse(MAIN)


def metodo(classe, nome):
    for node in TREE.body:
        if isinstance(node, ast.ClassDef) and node.name == classe:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == nome:
                    return item
    raise AssertionError(f"Método {classe}.{nome} não encontrado")


class KeyboardNavigationEnterNextTests(unittest.TestCase):
    def test_versao(self):
        self.assertIn('VIGHNA_VERSION = "0.29.57"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "question-keyboard-navigation-enter-next-v2"', VERSAO)

    def test_enter_pos_confirmacao_avanca(self):
        filtro = ast.unparse(metodo("JanelaResolverQuestoes", "eventFilter"))
        self.assertIn("self.resposta_confirmada", filtro)
        self.assertIn("Qt.Key_Return", filtro)
        self.assertIn("Qt.Key_Enter", filtro)
        self.assertIn("self.proxima()", filtro)
        self.assertIn("evento.isAutoRepeat()", filtro)
        self.assertIn("evento.accept()", filtro)
        self.assertIn("return True", filtro)

    def test_fluxo_anterior_permanece(self):
        acionar = ast.unparse(metodo("JanelaResolverQuestoes", "acionar_enter_foco_teclado"))
        self.assertIn("self.alternativa_selecionada() != letra", acionar)
        self.assertIn("self.selecionar_alternativa_por_letra(letra)", acionar)
        self.assertIn("self.confirmar_resposta()", acionar)

    def test_proxima_conclui_ao_final(self):
        proxima = ast.unparse(metodo("JanelaResolverQuestoes", "proxima"))
        self.assertIn("self.indice += 1", proxima)
        self.assertIn("self.finalizar(True, 'Objetivo concluído')", proxima)
        self.assertIn("self.carregar_atual()", proxima)

    def test_confirmacao_move_foco_para_proxima(self):
        confirmar = ast.unparse(metodo("JanelaResolverQuestoes", "confirmar_resposta"))
        self.assertGreaterEqual(confirmar.count("self.botao_proxima.setFocus(Qt.OtherFocusReason)"), 2)

    def test_nova_questao_reinicia_confirmacao(self):
        carregar = ast.unparse(metodo("JanelaResolverQuestoes", "carregar_atual"))
        self.assertIn("self.resposta_confirmada = False", carregar)


if __name__ == "__main__":
    unittest.main()
