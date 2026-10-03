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


class ResolvedorModerno046Tests(unittest.TestCase):
    def test_versao_e_build(self):
        self.assertIn('VIGHNA_VERSION = "0.29.46"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "resolvedor-dashboard-focus-v1"', VERSAO)
        self.assertIn('VIGHNA_SCHEMA = 25', VERSAO)

    def test_resolvedor_tem_escopo_visual_proprio(self):
        init = ast.unparse(metodo("JanelaResolverQuestoes", "__init__"))
        self.assertIn("self.setObjectName('questionSolverDialog')", init)
        self.assertIn("questionSessionOverviewCard", init)
        self.assertIn("PROGRESSO DA SESSÃO", init)
        self.assertIn("questionSessionFocusBar", init)
        self.assertIn("questionSolverDiscipline", init)
        self.assertIn("questionSolverQuestionIndex", init)

    def test_progresso_e_ciclo_foram_separados(self):
        carregar = ast.unparse(metodo("JanelaResolverQuestoes", "carregar_atual"))
        self.assertIn("self.sessao_ciclo_texto.setText", carregar)
        self.assertIn("self.sessao_ciclo_texto.setVisible", carregar)
        self.assertIn("self.questao_indice.setText", carregar)
        self.assertNotIn("+ ciclo_progresso_rotulo", carregar)

    def test_metadata_visivel_e_limpo_e_detalhe_fica_no_tooltip(self):
        carregar = ast.unparse(metodo("JanelaResolverQuestoes", "carregar_atual"))
        self.assertIn("self.questao_disciplina.setText", carregar)
        self.assertIn("self.questao_meta.setText", carregar)
        self.assertIn("chaves_metadata", carregar)
        self.assertIn("self.questao_meta.setToolTip", carregar)

    def test_alternativa_tem_estado_visual_de_selecao(self):
        init = ast.unparse(metodo("JanelaResolverQuestoes", "carregar_atual"))
        helper = ast.unparse(metodo("JanelaResolverQuestoes", "atualizar_selecao_visual_alternativas"))
        self.assertIn("selectionState", init)
        self.assertIn("radio.toggled.connect(self.atualizar_selecao_visual_alternativas)", init)
        self.assertIn("'selected' if selecionada else 'normal'", helper)

    def test_barra_de_acoes_esta_fora_do_scroll(self):
        init = ast.unparse(metodo("JanelaResolverQuestoes", "__init__"))
        pos_scroll = init.index("layout.addWidget(scroll, 1)")
        pos_footer = init.index("layout.addWidget(painel_acoes)")
        self.assertGreater(pos_footer, pos_scroll)
        self.assertIn("painel_acoes.setMinimumHeight(58)", init)

    def test_tema_futurista_herda_linguagem_do_dashboard_neo(self):
        self.assertIn("ESTILO_RESOLVEDOR_FUTURISTA", TEMA)
        self.assertIn('QDialog#questionSolverDialog QFrame#questionSessionOverviewCard', TEMA)
        self.assertIn('[selectionState="selected"][answerState="normal"]', TEMA)
        self.assertIn('stop:0 #4447E8', TEMA)
        self.assertIn('+ ESTILO_RESOLVEDOR_FUTURISTA', TEMA)


if __name__ == "__main__":
    unittest.main()
