import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / "main.py").read_text(encoding="utf-8")
FOCO = (ROOT / "foco.py").read_text(encoding="utf-8")
VERSAO = (ROOT / "versao.py").read_text(encoding="utf-8")
TREE = ast.parse(MAIN)


def metodo(classe, nome):
    for node in TREE.body:
        if isinstance(node, ast.ClassDef) and node.name == classe:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == nome:
                    return item
    raise AssertionError(f"Método {classe}.{nome} não encontrado")


class JanelasOperacionais045Tests(unittest.TestCase):
    def test_versao_build(self):
        self.assertIn('VIGHNA_VERSION = "0.29.45"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "janelas-operacionais-independentes-v1"', VERSAO)

    def test_resolvedor_e_top_level_real_nao_modal(self):
        init = ast.unparse(metodo("JanelaResolverQuestoes", "__init__"))
        self.assertIn("super().__init__(None)", init)
        self.assertIn("Qt.Window", init)
        self.assertIn("Qt.WindowMinMaxButtonsHint", init)
        self.assertIn("self.setModal(False)", init)
        self.assertIn("Qt.NonModal", init)
        self.assertNotIn("super().__init__(parent)", init)

    def test_resolvedor_tem_retorno_ao_dashboard_sem_encerrar(self):
        init = ast.unparse(metodo("JanelaResolverQuestoes", "__init__"))
        ir = ast.unparse(metodo("JanelaResolverQuestoes", "ir_ao_dashboard"))
        self.assertIn("QPushButton('Dashboard')", init)
        self.assertIn("self.showMinimized()", ir)
        self.assertIn("principal.voltar_inicio()", ir)
        self.assertNotIn("self.reject()", ir)
        self.assertNotIn("self.accept()", ir)

    def test_minimizar_pausa_tempo_da_questao_comum(self):
        mudanca = ast.unparse(metodo("JanelaResolverQuestoes", "changeEvent"))
        tempo = ast.unparse(metodo("JanelaResolverQuestoes", "tempo_atual_segundos"))
        pausar = ast.unparse(metodo("JanelaResolverQuestoes", "pausar_cronometro_questao"))
        self.assertIn("QEvent.WindowStateChange", mudanca)
        self.assertIn("self.isMinimized()", mudanca)
        self.assertIn("self.pausar_cronometro_questao()", mudanca)
        self.assertIn("self.retomar_cronometro_questao()", mudanca)
        self.assertIn("self.modo_simulado", pausar)
        self.assertIn("_questao_tempo_pausado", tempo)
        self.assertIn("_questao_pausa_iniciada", tempo)

    def test_principal_restaura_bateria_por_botao_e_atalho(self):
        init = ast.unparse(metodo("SistemaEstudos", "__init__"))
        atalhos = ast.unparse(metodo("SistemaEstudos", "configurar_atalhos_globais"))
        trazer = ast.unparse(metodo("SistemaEstudos", "abrir_ou_trazer_resolvedor_questoes"))
        dashboard = ast.unparse(metodo("SistemaEstudos", "criar_tela_inicial"))
        self.assertIn("_janela_resolvedor_questoes", init)
        self.assertIn("Ctrl+Shift+Q", atalhos)
        self.assertIn("Retomar bateria", dashboard)
        self.assertIn("janela.showNormal()", trazer)
        self.assertIn("janela.raise_()", trazer)
        self.assertIn("janela.activateWindow()", trazer)

    def test_fechamento_principal_fecha_resolvedor_top_level(self):
        fechamento = ast.unparse(metodo("SistemaEstudos", "closeEvent"))
        self.assertIn("JanelaResolverQuestoes", fechamento)
        self.assertIn("janela_resolvedor.close()", fechamento)
        self.assertIn("evento.ignore()", fechamento)

    def test_reforco_pos_bateria_tambem_nao_usa_exec_modal(self):
        corpo = ast.unparse(metodo("JanelaResumoResolucaoQuestoes", "refazer_questoes_erradas"))
        self.assertIn("JanelaResolverQuestoes", corpo)
        self.assertIn("exec_nao_modal", corpo)
        self.assertNotIn("janela.exec()", corpo)

    def test_modo_foco_permanece_top_level_com_restauracao(self):
        self.assertIn("super().__init__(None)", FOCO)
        self.assertIn("Qt.WindowMinMaxButtonsHint", FOCO)
        self.assertIn("def trazer_janela_foco_para_frente", FOCO)
        self.assertIn("janela.showNormal()", FOCO)
        self.assertIn("janela.activateWindow()", FOCO)


if __name__ == "__main__":
    unittest.main()
