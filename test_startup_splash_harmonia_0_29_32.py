import ast
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / "main.py").read_text(encoding="utf-8")
SPLASH = (ROOT / "startup_splash.py").read_text(encoding="utf-8")
VERSAO = (ROOT / "versao.py").read_text(encoding="utf-8")


class StartupSplashHarmoniaTests(unittest.TestCase):
    def test_fontes_compilam_com_ast(self):
        ast.parse(MAIN)
        ast.parse(SPLASH)

    def test_versao_schema_e_build(self):
        self.assertIn('VIGHNA_VERSION = "0.29.32"', VERSAO)
        self.assertIn(
            'VIGHNA_BUILD = "startup-splash-composicao-harmonica-v1"',
            VERSAO,
        )
        self.assertIn('VIGHNA_SCHEMA = 23', VERSAO)

    def test_splash_externo_ficou_mais_compacto(self):
        self.assertIn("self.setFixedSize(620, 318)", SPLASH)
        self.assertIn("raiz.setContentsMargins(34, 20, 32, 18)", SPLASH)
        self.assertIn("raiz.addSpacing(19)", SPLASH)
        self.assertIn("raiz.addSpacing(25)", SPLASH)

    def test_eixo_do_card_coincide_com_texto_do_cabecalho(self):
        self.assertIn("logo_box.setFixedSize(54, 54)", SPLASH)
        self.assertIn("topo.setSpacing(14)", SPLASH)
        self.assertIn("painel_linha.addSpacing(68)", SPLASH)
        self.assertIn("painel_linha.addWidget(painel, 1)", SPLASH)

    def test_rodape_pertence_ao_mesmo_eixo_do_card(self):
        self.assertIn("rodape.addSpacing(68)", SPLASH)
        self.assertIn('rodape_texto = QLabel("motor de inteligência Vighna")', SPLASH)
        self.assertNotIn('linha_esq.setObjectName("startupFooterLine")', SPLASH)
        self.assertNotIn('linha_dir.setObjectName("startupFooterLine")', SPLASH)

    def test_barra_viva_foi_preservada(self):
        for trecho in (
            "class BarraProgressoViva(QWidget):",
            "self._fase_shimmer",
            "self._fase_pulso",
            "self.barra.setValue(percentual)",
            'self.percentual.setText(f"{percentual}%")',
        ):
            self.assertIn(trecho, SPLASH)

    def test_fallback_repete_a_nova_composicao(self):
        inicio = MAIN.index("class JanelaInicializacao(QDialog):")
        fim = MAIN.index("class SistemaEstudos(QMainWindow):", inicio)
        fallback = MAIN[inicio:fim]
        self.assertIn("self.setFixedSize(620, 318)", fallback)
        self.assertIn("painel_linha.addSpacing(68)", fallback)
        self.assertIn("rodape.addSpacing(68)", fallback)
        self.assertNotIn("startupFallbackFooterLine", fallback)

    def test_banco_permanece_integro(self):
        db = ROOT / "estudos.db"
        with sqlite3.connect(db) as con:
            self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(), [])


if __name__ == "__main__":
    unittest.main()
