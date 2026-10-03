import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TAREFAS = (ROOT / "tarefas_pesadas.py").read_text(encoding="utf-8")
VERSAO = (ROOT / "versao.py").read_text(encoding="utf-8")
TREE = ast.parse(TAREFAS)


def classe(nome):
    for node in TREE.body:
        if isinstance(node, ast.ClassDef) and node.name == nome:
            return node
    raise AssertionError(f"Classe {nome} não encontrada")


def metodo(nome_classe, nome_metodo):
    node = classe(nome_classe)
    for item in node.body:
        if isinstance(item, ast.FunctionDef) and item.name == nome_metodo:
            return item
    raise AssertionError(f"Método {nome_classe}.{nome_metodo} não encontrado")


class EmbeddedTaskIndicator052Tests(unittest.TestCase):
    def test_versao_build(self):
        self.assertIn('VIGHNA_VERSION = "0.29.52"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "embedded-task-indicator-v1"', VERSAO)
        self.assertIn('VIGHNA_SCHEMA = 25', VERSAO)

    def test_indicador_deixou_de_ser_janela_nativa(self):
        node = classe("IndicadorTarefa")
        self.assertEqual(ast.unparse(node.bases[0]), "QFrame")
        init = ast.unparse(metodo("IndicadorTarefa", "__init__"))
        self.assertNotIn("setWindowFlags", init)
        self.assertNotIn("Qt.Tool", init)
        self.assertNotIn("WindowStaysOnTopHint", init)
        self.assertNotIn("setWindowModality", init)
        self.assertIn("self.setObjectName('taskIndicatorRoot')", init)
        self.assertIn("self.hide()", init)

    def test_posicionamento_e_relativo_ao_parent(self):
        repo = ast.unparse(metodo("IndicadorTarefa", "_reposicionar"))
        self.assertIn("parent.rect()", repo)
        self.assertNotIn("frameGeometry", repo)
        self.assertNotIn("primaryScreen", repo)

    def test_exibicao_nao_ativa_janela_do_windows(self):
        exibir = ast.unparse(metodo("IndicadorTarefa", "_exibir_agora"))
        self.assertIn("self.show()", exibir)
        self.assertIn("self.raise_()", exibir)
        self.assertNotIn("activateWindow", exibir)
        self.assertNotIn("setWindowFlags", exibir)

    def test_tarefas_rapidas_continuam_sem_flicker(self):
        init = ast.unparse(metodo("IndicadorTarefa", "__init__"))
        iniciar = ast.unparse(metodo("IndicadorTarefa", "iniciar"))
        self.assertIn("self._atraso_minimo_nao_bloqueante_ms = 850", init)
        self.assertIn("max(self._atraso_minimo_nao_bloqueante_ms, int(atraso_ms))", iniciar)

    def test_estilo_raiz_agora_aponta_para_qframe(self):
        self.assertIn("QFrame#taskIndicatorRoot", TAREFAS)
        self.assertNotIn('"QDialog { background: #071522;', TAREFAS)


if __name__ == "__main__":
    unittest.main()
