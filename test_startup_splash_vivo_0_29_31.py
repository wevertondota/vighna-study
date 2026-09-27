import ast
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / "main.py").read_text(encoding="utf-8")
SPLASH = (ROOT / "startup_splash.py").read_text(encoding="utf-8")
VERSAO = (ROOT / "versao.py").read_text(encoding="utf-8")


class StartupSplashVivoTests(unittest.TestCase):
    def test_fontes_compilam_com_ast(self):
        ast.parse(MAIN)
        ast.parse(SPLASH)

    def test_versao_e_schema(self):
        self.assertIn('VIGHNA_VERSION = "0.29.31"', VERSAO)
        self.assertIn(
            'VIGHNA_BUILD = "startup-splash-vivo-processo-independente-v1"',
            VERSAO,
        )
        self.assertIn('VIGHNA_SCHEMA = 23', VERSAO)

    def test_worker_e_lancado_antes_das_importacoes_pesadas(self):
        pos_worker = MAIN.index("if ARG_SPLASH_WORKER in sys.argv:")
        pos_bootstrap = MAIN.index("ControladorSplashInicializacao()")
        pos_qt = MAIN.index("from PySide6.QtCore import")
        self.assertLess(pos_worker, pos_qt)
        self.assertLess(pos_bootstrap, pos_qt)

    def test_splash_externo_tem_barra_viva_e_progresso_real(self):
        for trecho in (
            "class BarraProgressoViva(QWidget):",
            "self._valor_alvo",
            "self._valor_visual",
            "self._fase_shimmer",
            "Reflexo móvel",
            "self.percentual.setText(f\"{percentual}%\")",
            "self.barra.setValue(percentual)",
        ):
            self.assertIn(trecho, SPLASH)

    def test_splash_externo_permanece_vivo_com_main_bloqueada(self):
        self.assertIn("subprocess.Popen", SPLASH)
        self.assertIn("self._timer_estado = QTimer(self)", SPLASH)
        self.assertIn("self._timer_texto = QTimer(self)", SPLASH)
        self.assertIn("_processo_esta_ativo(pid_pai)", SPLASH)
        self.assertIn("ARG_SPLASH_WORKER", MAIN)

    def test_hierarquia_visual_nova(self):
        for trecho in (
            "Preparando seu ambiente de estudo",
            "motor de inteligência Vighna",
            'self.percentual = QLabel("2%")',
            "startupPanel",
            "startupFooter",
        ):
            self.assertIn(trecho, SPLASH)

    def test_fallback_local_permanece_disponivel(self):
        self.assertIn("class JanelaInicializacao(QDialog):", MAIN)
        self.assertIn("self.progresso = QProgressBar()", MAIN)
        self.assertIn("self.percentual = QLabel(\"2%\")", MAIN)
        self.assertIn("motor de inteligência Vighna", MAIN)
        self.assertIn("JanelaInicializacao()", MAIN)

    def test_precarregamento_continua_antes_da_janela_principal(self):
        pos_preload = MAIN.rfind(
            "janela.precarregar_inicializacao_completa(splash.atualizar)"
        )
        pos_show = MAIN.rfind("janela.show()")
        pos_close = MAIN.rfind("splash.close()")
        self.assertGreaterEqual(pos_preload, 0)
        self.assertGreater(pos_show, pos_preload)
        self.assertGreater(pos_close, pos_show)

    def test_banco_permanece_integro(self):
        db = ROOT / "estudos.db"
        with sqlite3.connect(db) as con:
            self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(), [])


if __name__ == "__main__":
    unittest.main()
