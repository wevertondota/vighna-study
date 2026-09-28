import unittest
from pathlib import Path

MAIN = Path("main.py").read_text(encoding="utf-8")
VERSAO = Path("versao.py").read_text(encoding="utf-8")


class TestNavegacaoEstatisticasFastPath(unittest.TestCase):
    def test_fast_path_existe(self):
        self.assertIn(
            "def _estatisticas_visivel_precisa_atualizacao(self, forcar=False):",
            MAIN,
        )
        self.assertIn(
            "if not self._estatisticas_visivel_precisa_atualizacao(forcar=forcar):\n            return",
            MAIN,
        )

    def test_troca_de_aba_so_agenda_se_precisar(self):
        trecho = MAIN[MAIN.index("def _ao_mudar_aba_estatisticas"):]
        trecho = trecho[:trecho.index("def _receber_alteracao_dados")]
        self.assertIn("and self._estatisticas_visivel_precisa_atualizacao()", trecho)
        self.assertIn("self._agendar_atualizacao_estatisticas()", trecho)

    def test_callback_revalida_estado(self):
        trecho = MAIN[MAIN.index("def _agendar_atualizacao_estatisticas"):]
        trecho = trecho[:trecho.index("def _ao_mudar_aba_estatisticas")]
        self.assertGreaterEqual(
            trecho.count("_estatisticas_visivel_precisa_atualizacao"),
            2,
        )

    def test_perfil_invalida_snapshots(self):
        trecho = MAIN[MAIN.index("def alterar_concurso_ativo"):]
        trecho = trecho[:trecho.index("def abrir_disciplinas")]
        self.assertIn('self.invalidar_estatisticas("all", atualizar_se_visivel=True)', trecho)
        self.assertIn("self.invalidar_relatorios(atualizar_se_visivel=True)", trecho)
        self.assertIn("self._marcar_central_questoes_suja()", trecho)

    def test_versao(self):
        self.assertIn('VIGHNA_VERSION = "0.29.40"', VERSAO)
        self.assertIn(
            'VIGHNA_BUILD = "navegacao-estatisticas-fast-path-v1"',
            VERSAO,
        )


if __name__ == "__main__":
    unittest.main()
