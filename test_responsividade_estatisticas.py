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


class ResponsividadeEstatisticasTests(unittest.TestCase):
    def test_open_navigates_before_scheduling_heavy_refresh(self):
        bloco = method_source("abrir_estatisticas")
        navegar = bloco.index("self.telas.setCurrentWidget")
        agendar = bloco.index("self._agendar_atualizacao_estatisticas")
        self.assertLess(navegar, agendar)
        self.assertNotIn("self.atualizar_estatisticas()", bloco)

    def test_tab_change_uses_lazy_refresh_handler(self):
        self.assertIn(
            "self.abas_estatisticas.currentChanged.connect(\n            self._ao_mudar_aba_estatisticas",
            SOURCE,
        )

    def test_refresh_updates_only_current_tab_branch(self):
        bloco = method_source("atualizar_estatisticas")
        self.assertIn("_nome_aba_estatisticas_atual", bloco)
        for nome in (
            'aba == "Histórico"',
            'aba == "Algoritmo"',
            'aba == "Disciplinas"',
            'aba == "Mapa de domínio"',
            'aba == "Pontos fracos"',
            'aba == "Revisões recentes"',
            'aba == "Tendências"',
            'aba == "Progresso"',
        ):
            self.assertIn(nome, bloco)


    def test_domain_map_is_part_of_lazy_dirty_state(self):
        lazy_source = Path(__file__).with_name("estatisticas_lazy.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('"Mapa de domínio"', lazy_source)

    def test_academic_invalidation_marks_statistics_dirty(self):
        bloco = method_source("notificar_dados_alterados")
        self.assertIn("self.invalidar_estatisticas", bloco)

    def test_deferred_refresh_gives_qt_time_to_repaint(self):
        bloco = method_source("_agendar_atualizacao_estatisticas")
        self.assertIn("QTimer.singleShot(15, executar)", bloco)


if __name__ == "__main__":
    unittest.main()
