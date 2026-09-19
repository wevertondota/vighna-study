import re
import unittest
from pathlib import Path


MAIN = Path(__file__).with_name("main.py").read_text(encoding="utf-8")


def bloco(nome, proximo):
    inicio = MAIN.index(f"    def {nome}")
    fim = MAIN.index(f"    def {proximo}", inicio)
    return MAIN[inicio:fim]


class ResponsividadeRelatoriosTests(unittest.TestCase):
    def test_abrir_relatorios_navega_antes_de_agendar(self):
        trecho = bloco("abrir_relatorios", "_comparar_numero")
        self.assertNotIn("self.atualizar_relatorios()", trecho)
        self.assertLess(
            trecho.index("self.telas.setCurrentWidget"),
            trecho.index("self._agendar_atualizacao_relatorios"),
        )

    def test_abas_disparam_carregamento_sob_demanda(self):
        self.assertIn(
            "self.abas_relatorios.currentChanged.connect(\n            self._ao_mudar_aba_relatorios",
            MAIN,
        )

    def test_atualizador_principal_delega_so_aba_visivel(self):
        trecho = bloco("atualizar_relatorios", "_garantir_dados_relatorio_exportacao")
        self.assertIn("self._atualizar_aba_relatorios(aba, contexto)", trecho)
        self.assertNotIn("obter_relatorio_disciplinas_periodo(", trecho)
        self.assertNotIn("obter_relatorio_topicos_periodo(", trecho)
        self.assertNotIn("obter_relatorio_diario_periodo(", trecho)
        self.assertNotIn("obter_relatorio_estrategico(", trecho)

    def test_tabelas_relatorio_suspendem_repaint(self):
        for nome, proximo in (
            ("_preencher_relatorio_disciplinas", "_preencher_relatorio_topicos"),
            ("_preencher_relatorio_topicos", "_preencher_relatorio_diario"),
            ("_preencher_relatorio_diario", "_atualizar_aba_relatorios"),
        ):
            trecho = bloco(nome, proximo)
            self.assertIn("setUpdatesEnabled(False)", trecho)
            self.assertIn("blockSignals(True)", trecho)
            self.assertIn("setUpdatesEnabled(True)", trecho)


if __name__ == "__main__":
    unittest.main()
