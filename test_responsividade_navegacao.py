import ast
import unittest
from pathlib import Path

MAIN_PATH = Path(__file__).with_name("main.py")
SOURCE = MAIN_PATH.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


def method_source(name: str) -> str:
    for node in ast.walk(TREE):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.get_source_segment(SOURCE, node) or ""
    raise AssertionError(f"Método não encontrado: {name}")


class ResponsividadeNavegacaoTests(unittest.TestCase):
    def test_voltar_dashboard_navega_antes_de_atualizar(self):
        bloco = method_source("voltar_inicio")
        navegar = bloco.index("self.telas.setCurrentWidget")
        agendar = bloco.index("self._agendar_atualizacao_dashboard")
        self.assertLess(navegar, agendar)
        self.assertNotIn("self.atualizar_dashboard()", bloco)

    def test_dashboard_deferido_respeita_estado_sujo(self):
        bloco = method_source("_agendar_atualizacao_dashboard")
        self.assertIn("self._dashboard_sujo", bloco)
        self.assertIn("QTimer.singleShot(15, executar)", bloco)

    def test_evento_fora_do_dashboard_nao_forca_refresh_sincrono(self):
        bloco = method_source("_processar_atualizacao_pendente")
        self.assertIn("self.telas.currentWidget() is not self.tela_inicial", bloco)
        self.assertIn("self._agendar_atualizacao_dashboard", bloco)
        self.assertNotIn("self.atualizar_dashboard()", bloco)

    def test_central_navega_antes_de_carregar(self):
        bloco = method_source("abrir_questoes")
        navegar = bloco.index("self.telas.setCurrentWidget")
        agendar = bloco.index("self._agendar_carregamento_central_questoes")
        self.assertLess(navegar, agendar)
        self.assertNotIn("self.carregar_questoes()", bloco)

    def test_central_catalogo_faz_uma_unica_listagem_base(self):
        bloco = method_source("carregar_questoes")
        self.assertEqual(1, bloco.count("listar_questoes("))

    def test_tabela_central_suspende_sinais_e_repaint_na_montagem(self):
        bloco = method_source("filtrar_questoes")
        self.assertIn("self.tabela_questoes.setUpdatesEnabled(False)", bloco)
        self.assertIn("self.tabela_questoes.blockSignals(True)", bloco)
        self.assertIn("self.tabela_questoes.setSortingEnabled(False)", bloco)
        self.assertIn("self.tabela_questoes.setUpdatesEnabled(True)", bloco)
        self.assertIn("self.tabela_questoes.blockSignals(False)", bloco)

    def test_ctrl_h_reusa_fluxo_responsivo(self):
        bloco = method_source("configurar_atalhos_globais")
        self.assertIn('(\"Ctrl+H\", self.voltar_inicio)', bloco)


if __name__ == "__main__":
    unittest.main()
