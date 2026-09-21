import ast
import unittest
from pathlib import Path


class TestPosBateriaAlgoritmo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main_path = Path(__file__).with_name("main.py")
        cls.source = cls.main_path.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_fluxo_guiado_pos_bateria_esta_presente(self):
        for texto in (
            "CONTINUAR PELO ALGORITMO",
            "Cobertura e revisão",
            "Voltar ao Dashboard",
            "Banco de questões",
            "Rever erradas",
            "A próxima sessão será recalculada com os resultados desta bateria.",
        ):
            self.assertIn(texto, self.source)

    def test_leitura_do_vighna_nao_foi_adicionada_ao_resumo(self):
        trecho_inicio = self.source.index("class JanelaResumoResolucaoQuestoes")
        trecho_fim = self.source.index("class JanelaResolverQuestoes", trecho_inicio)
        trecho = self.source[trecho_inicio:trecho_fim]
        self.assertNotIn("Leitura do Vighna", trecho)

    def test_acao_pos_bateria_propaga_ate_fluxo_do_motor(self):
        for texto in (
            'self.proxima_acao = "continuar_algoritmo"',
            'self.proxima_acao = "dashboard"',
            'self.proxima_acao = "banco_questoes"',
            '"proxima_acao": getattr(janela, "proxima_acao_final", None)',
            'origem_sessao="algoritmo_v5"',
            "def _processar_fluxo_pos_bateria_algoritmo",
            "class JanelaProximaRecomendacaoAlgoritmo",
        ):
            self.assertIn(texto, self.source)


if __name__ == "__main__":
    unittest.main()
