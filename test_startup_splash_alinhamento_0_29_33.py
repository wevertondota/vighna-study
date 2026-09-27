import ast
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / "main.py").read_text(encoding="utf-8")
SPLASH = (ROOT / "startup_splash.py").read_text(encoding="utf-8")
VERSAO = (ROOT / "versao.py").read_text(encoding="utf-8")


class StartupSplashAlinhamentoTests(unittest.TestCase):
    def test_fontes_compilam_com_ast(self):
        ast.parse(MAIN)
        ast.parse(SPLASH)

    def test_versao_schema_e_build(self):
        self.assertIn('VIGHNA_VERSION = "0.29.33"', VERSAO)
        self.assertIn(
            'VIGHNA_BUILD = "startup-splash-alinhamento-horizontal-v1"',
            VERSAO,
        )
        self.assertIn('VIGHNA_SCHEMA = 23', VERSAO)

    def test_splash_externo_usa_container_central(self):
        for trecho in (
            'conteudo = QWidget()',
            'conteudo.setObjectName("startupContent")',
            'conteudo.setFixedWidth(470)',
            'conteudo_wrap.addWidget(conteudo, 0, Qt.AlignHCenter)',
        ):
            self.assertIn(trecho, SPLASH)
        self.assertNotIn('painel_linha.addSpacing(68)', SPLASH)
        self.assertNotIn('rodape.addSpacing(68)', SPLASH)

    def test_bloco_compartilha_mesmo_eixo_visual(self):
        self.assertIn('conteudo_layout.addLayout(topo)', SPLASH)
        self.assertIn('conteudo_layout.addWidget(painel)', SPLASH)
        self.assertIn('conteudo_layout.addLayout(rodape)', SPLASH)
        self.assertIn('conteudo_layout.addSpacing(20)', SPLASH)
        self.assertIn('conteudo_layout.addSpacing(24)', SPLASH)

    def test_barra_viva_permanece(self):
        for trecho in (
            'class BarraProgressoViva(QWidget):',
            'self._fase_shimmer',
            'self._fase_pulso',
            'self.barra.setValue(percentual)',
            'self.percentual.setText(f"{percentual}%")',
        ):
            self.assertIn(trecho, SPLASH)

    def test_fallback_repete_o_mesmo_container_central(self):
        inicio = MAIN.index('class JanelaInicializacao(QDialog):')
        fim = MAIN.index('class SistemaEstudos(QMainWindow):', inicio)
        fallback = MAIN[inicio:fim]
        for trecho in (
            'conteudo = QWidget()',
            'conteudo.setObjectName("startupFallbackContent")',
            'conteudo.setFixedWidth(470)',
            'conteudo_wrap.addWidget(conteudo, 0, Qt.AlignHCenter)',
        ):
            self.assertIn(trecho, fallback)
        self.assertNotIn('painel_linha.addSpacing(68)', fallback)
        self.assertNotIn('rodape.addSpacing(68)', fallback)

    def test_banco_permanece_integro(self):
        db = ROOT / 'estudos.db'
        with sqlite3.connect(db) as con:
            self.assertEqual(con.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(con.execute('PRAGMA foreign_key_check').fetchall(), [])


if __name__ == '__main__':
    unittest.main()
