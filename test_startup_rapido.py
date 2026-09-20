import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class StartupRapidoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main_source = (ROOT / "main.py").read_text(encoding="utf-8")
        cls.main_tree = ast.parse(cls.main_source)
        cls.pdf_tree = ast.parse((ROOT / "importador_pdf.py").read_text(encoding="utf-8"))

    def _metodo_sistema(self, nome):
        for node in self.main_tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "SistemaEstudos":
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == nome:
                        return item
        self.fail(f"Método SistemaEstudos.{nome} não encontrado")

    def test_init_constroi_apenas_dashboard(self):
        init = self._metodo_sistema("__init__")
        chamadas = {
            node.func.attr
            for node in ast.walk(init)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "self"
        }
        self.assertIn("criar_tela_inicial", chamadas)
        for nome in (
            "criar_tela_disciplina",
            "criar_tela_sessao_estudo",
            "criar_tela_resumo_dia",
            "criar_tela_calendario",
            "criar_tela_questoes",
            "criar_tela_estatisticas",
            "criar_tela_relatorios",
        ):
            self.assertNotIn(nome, chamadas)

    def test_aberturas_garantem_tela_lazy(self):
        pares = {
            "abrir_disciplina": "_garantir_tela_disciplina",
            "abrir_sessao_estudo": "_garantir_tela_sessao_estudo",
            "abrir_resumo_dia": "_garantir_tela_resumo_dia",
            "abrir_calendario": "_garantir_tela_calendario",
            "abrir_questoes": "_garantir_tela_questoes",
            "abrir_estatisticas": "_garantir_tela_estatisticas",
            "abrir_relatorios": "_garantir_tela_relatorios",
        }
        for metodo, helper in pares.items():
            node = self._metodo_sistema(metodo)
            chamadas = {
                item.func.attr
                for item in ast.walk(node)
                if isinstance(item, ast.Call)
                and isinstance(item.func, ast.Attribute)
                and isinstance(item.func.value, ast.Name)
                and item.func.value.id == "self"
            }
            self.assertIn(helper, chamadas, metodo)

    def test_pypdf_nao_e_importado_no_top_level(self):
        for node in self.pdf_tree.body:
            if isinstance(node, ast.ImportFrom) and node.module == "pypdf":
                self.fail("pypdf voltou a ser importado no top-level")
            if isinstance(node, ast.Import):
                self.assertNotIn("pypdf", {alias.name for alias in node.names})


if __name__ == "__main__":
    unittest.main()
