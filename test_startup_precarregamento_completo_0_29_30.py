import ast
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / 'main.py').read_text(encoding='utf-8')
VERSAO = (ROOT / 'versao.py').read_text(encoding='utf-8')


class StartupPrecarregamentoCompletoTests(unittest.TestCase):
    def test_main_compila_com_ast(self):
        ast.parse(MAIN)

    def test_versao_e_schema(self):
        self.assertIn('VIGHNA_VERSION = "0.29.30"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "startup-precarregamento-completo-v1"', VERSAO)
        self.assertIn('VIGHNA_SCHEMA = 23', VERSAO)

    def test_tela_de_inicializacao_existe(self):
        self.assertIn('class JanelaInicializacao(QDialog):', MAIN)
        self.assertIn('Preparando seu ambiente de estudo', MAIN)
        self.assertIn('self.progresso = QProgressBar()', MAIN)
        self.assertIn('self._timer_animacao = QTimer(self)', MAIN)

    def test_startup_usa_precarregamento_antes_de_show(self):
        pos_criacao = MAIN.rfind('janela = SistemaEstudos(pre_carregar_startup=True)')
        pos_preload = MAIN.rfind('janela.precarregar_inicializacao_completa(splash.atualizar)')
        pos_show = MAIN.rfind('janela.show()')
        self.assertGreaterEqual(pos_criacao, 0)
        self.assertGreater(pos_preload, pos_criacao)
        self.assertGreater(pos_show, pos_preload)

    def test_modulos_principais_sao_precarregados(self):
        for trecho in (
            'self.atualizar_dashboard()',
            'self._precarregar_topicos_disciplinas()',
            'self.carregar_questoes()',
            'self.atualizar_resumo_dia()',
            'self.atualizar_calendario()',
            'self._garantir_tela_sessao_estudo()',
            'self._precarregar_estatisticas_todas_abas',
            'self._precarregar_relatorios_todas_abas',
        ):
            self.assertIn(trecho, MAIN)

    def test_primeira_navegacao_reusa_dados_precarregados(self):
        self.assertIn('self._resumo_dia_precarregado', MAIN)
        self.assertIn('self._calendario_precarregado', MAIN)
        self.assertIn('self._topicos_precarregados', MAIN)
        self.assertIn('if self._dashboard_sujo:', MAIN)

    def test_banco_do_checkpoint_integro(self):
        db = ROOT / 'estudos.db'
        with sqlite3.connect(db) as con:
            self.assertEqual(con.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(con.execute('PRAGMA foreign_key_check').fetchall(), [])


if __name__ == '__main__':
    unittest.main()
