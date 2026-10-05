import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / "main.py").read_text(encoding="utf-8")
BANCO = (ROOT / "banco.py").read_text(encoding="utf-8")
TEMA = (ROOT / "tema.py").read_text(encoding="utf-8")
VERSAO = (ROOT / "versao.py").read_text(encoding="utf-8")
TREE = ast.parse(MAIN)
BANCO_TREE = ast.parse(BANCO)


def metodo(tree, classe, nome):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == classe:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == nome:
                    return item
    raise AssertionError(f"Método {classe}.{nome} não encontrado")


def funcao(tree, nome):
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == nome:
            return node
    raise AssertionError(f"Função {nome} não encontrada")


class InlineExplanationEditor058Tests(unittest.TestCase):
    def test_versao_build_schema(self):
        self.assertIn('VIGHNA_VERSION = "0.29.58"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "inline-explanation-editor-v1"', VERSAO)
        self.assertIn('VIGHNA_SCHEMA = 25', VERSAO)

    def test_interface_tem_icone_editor_salvar_cancelar(self):
        init = ast.unparse(metodo(TREE, "JanelaResolverQuestoes", "__init__"))
        self.assertIn("questionSolverExplanationEditButton", init)
        self.assertIn("self.feedback_explicacao_editar.setText('✎')", init)
        self.assertIn("QTextEdit(self.feedback)", init)
        self.assertIn("questionSolverExplanationEditor", init)
        self.assertIn("self.feedback_explicacao_salvar", init)
        self.assertIn("self.feedback_explicacao_cancelar", init)

    def test_icone_so_aparece_no_feedback_confirmado(self):
        confirmar = ast.unparse(metodo(TREE, "JanelaResolverQuestoes", "confirmar_resposta"))
        carregar = ast.unparse(metodo(TREE, "JanelaResolverQuestoes", "carregar_atual"))
        self.assertIn("self.feedback_explicacao_editar.setVisible(True)", confirmar)
        self.assertIn("self.feedback_explicacao_editar.setVisible(False)", carregar)
        self.assertIn("self.resposta_confirmada = False", carregar)

    def test_edicao_inline_bloqueia_avanco_ate_salvar_ou_cancelar(self):
        iniciar = ast.unparse(metodo(TREE, "JanelaResolverQuestoes", "iniciar_edicao_explicacao"))
        finalizar = ast.unparse(metodo(TREE, "JanelaResolverQuestoes", "finalizar_edicao_explicacao"))
        self.assertIn("self._editando_explicacao = True", iniciar)
        self.assertIn("self.botao_proxima.setEnabled(False)", iniciar)
        self.assertIn("self._editando_explicacao = False", finalizar)
        self.assertIn("self.botao_proxima.setEnabled(True)", finalizar)

    def test_salvar_persiste_e_atualiza_feedback_atual(self):
        salvar = ast.unparse(metodo(TREE, "JanelaResolverQuestoes", "salvar_edicao_explicacao"))
        self.assertIn("atualizar_explicacao_questao", salvar)
        self.assertIn("self.questao_atual['explicacao'] = nova_explicacao", salvar)
        self.assertIn("self.atualizar_texto_feedback_explicacao()", salvar)
        self.assertIn("self.finalizar_edicao_explicacao()", salvar)

    def test_banco_atualiza_apenas_explicacao_sem_schema_novo(self):
        atualizar = ast.unparse(funcao(BANCO_TREE, "atualizar_explicacao_questao"))
        self.assertIn("UPDATE questoes", atualizar)
        self.assertIn("explicacao = ?", atualizar)
        self.assertIn("atualizado_em", atualizar)
        self.assertNotIn("ALTER TABLE", atualizar)

    def test_teclado_da_bateria_nao_interfere_no_editor(self):
        filtro = ast.unparse(metodo(TREE, "JanelaResolverQuestoes", "eventFilter"))
        self.assertIn("if self._editando_explicacao", filtro)
        self.assertIn("return super().eventFilter(objeto, evento)", filtro)
        # Fluxo anterior continua presente fora do editor.
        self.assertIn("self.proxima()", filtro)
        self.assertIn("Qt.Key_Return", filtro)
        self.assertIn("Qt.Key_Enter", filtro)

    def test_estilo_existe_nos_tres_temas(self):
        self.assertIn("ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_CLARO", TEMA)
        self.assertIn("ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_ESCURO", TEMA)
        self.assertIn("ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_FUTURISTA", TEMA)
        self.assertGreaterEqual(TEMA.count("questionSolverExplanationEditButton"), 6)
        self.assertGreaterEqual(TEMA.count("questionSolverExplanationEditor"), 3)


if __name__ == "__main__":
    unittest.main()
