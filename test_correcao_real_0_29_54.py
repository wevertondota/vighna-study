import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / "main.py").read_text(encoding="utf-8")
TEMA = (ROOT / "tema.py").read_text(encoding="utf-8")
VERSAO = (ROOT / "versao.py").read_text(encoding="utf-8")
BAT = (ROOT / "atualizar_exe.bat").read_text(encoding="utf-8")
HASHER = (ROOT / "hash_fontes_build.py").read_text(encoding="utf-8")
TREE = ast.parse(MAIN)


def classe(nome):
    for node in TREE.body:
        if isinstance(node, ast.ClassDef) and node.name == nome:
            return node
    raise AssertionError(f"Classe {nome} não encontrada")


def metodo(nome_classe, nome_metodo):
    for item in classe(nome_classe).body:
        if isinstance(item, ast.FunctionDef) and item.name == nome_metodo:
            return item
    raise AssertionError(f"Método {nome_classe}.{nome_metodo} não encontrado")


class CorrecaoReal054Tests(unittest.TestCase):
    def test_versao_build(self):
        self.assertIn('VIGHNA_VERSION = "0.29.54"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "resolver-elimination-and-window-guard-v1"', VERSAO)
        self.assertIn('VIGHNA_SCHEMA = 25', VERSAO)

    def test_tachamento_tem_seletor_com_mesma_especificidade_do_resolvedor(self):
        seletor = 'QDialog#questionSolverDialog QFrame#questionSolverAlternative[eliminated="true"][answerState="normal"]'
        self.assertGreaterEqual(TEMA.count(seletor), 3)
        self.assertIn('ESTILO_RESOLVEDOR_ELIMINADAS_CLARO', TEMA)
        self.assertIn('ESTILO_RESOLVEDOR_ELIMINADAS_ESCURO', TEMA)
        self.assertIn('ESTILO_RESOLVEDOR_ELIMINADAS_FUTURISTA', TEMA)
        self.assertIn('border: 2px dashed #3E617A', TEMA)

    def test_tachamento_final_e_aplicado_depois_da_camada_futurista_base(self):
        retorno = TEMA[TEMA.index('def stylesheet_futurista():'):]
        self.assertIn('+ ESTILO_RESOLVEDOR_FUTURISTA', retorno)
        self.assertIn('+ ESTILO_RESOLVEDOR_ELIMINADAS_FUTURISTA', retorno)
        self.assertGreater(
            retorno.index('+ ESTILO_RESOLVEDOR_ELIMINADAS_FUTURISTA'),
            retorno.index('+ ESTILO_RESOLVEDOR_FUTURISTA'),
        )

    def test_click_card_e_tesoura_continuam_independentes(self):
        carregar = ast.unparse(metodo('JanelaResolverQuestoes', 'carregar_atual'))
        filtro = ast.unparse(metodo('JanelaResolverQuestoes', 'eventFilter'))
        self.assertIn('frame.installEventFilter(self)', carregar)
        self.assertIn('texto.installEventFilter(self)', carregar)
        self.assertNotIn('eliminar.installEventFilter(self)', carregar)
        self.assertIn('self.selecionar_alternativa_por_letra(letra)', filtro)

    def test_guardiao_bloqueia_top_level_cru_sem_afetar_dialogos(self):
        init_app = ast.unparse(classe('AplicacaoVighna'))
        self.assertIn('QEvent.Show', init_app)
        self.assertIn('Qt.WA_DontShowOnScreen', init_app)
        self.assertIn('(QMainWindow, QDialog, QMenu)', init_app)
        self.assertIn("receiver.parentWidget() is not None", init_app)
        self.assertIn('app = AplicacaoVighna(sys.argv)', MAIN)
        self.assertNotIn('app = QApplication(sys.argv)', MAIN)

    def test_build_incremental_invalida_cache_por_conteudo(self):
        self.assertIn('hash_fontes_build.py', BAT)
        self.assertIn('SOURCE_HASH', BAT)
        self.assertIn('.vighna_source_hash', BAT)
        self.assertIn('Invalidando cache do PyInstaller', BAT)
        self.assertIn('BUILD_INFO.txt', BAT)
        self.assertIn('hashlib.sha256', HASHER)


if __name__ == '__main__':
    unittest.main()
