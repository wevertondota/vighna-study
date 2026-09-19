import unittest

from estatisticas_lazy import ABAS_ESTATISTICAS, EstadoEstatisticasLazy


class EstadoEstatisticasLazyTests(unittest.TestCase):
    def test_inicia_com_todas_as_abas_sujas(self):
        estado = EstadoEstatisticasLazy()
        self.assertEqual(set(ABAS_ESTATISTICAS), estado.sujas)
        self.assertTrue(estado.resumo_sujo)

    def test_limpar_uma_aba_nao_limpa_as_demais(self):
        estado = EstadoEstatisticasLazy()
        estado.marcar_limpa("Histórico")
        self.assertFalse(estado.precisa_atualizar("Histórico"))
        self.assertTrue(estado.precisa_atualizar("Tendências"))

    def test_invalidacao_parcial(self):
        estado = EstadoEstatisticasLazy()
        for aba in ABAS_ESTATISTICAS:
            estado.marcar_limpa(aba)
        estado.marcar_resumo_limpo()
        estado.marcar_sujas(("Histórico", "Tendências"), resumo=False)
        self.assertEqual({"Histórico", "Tendências"}, estado.sujas)
        self.assertFalse(estado.resumo_sujo)

    def test_troca_de_concurso_invalida_tudo(self):
        estado = EstadoEstatisticasLazy()
        estado.trocar_concurso(1)
        for aba in ABAS_ESTATISTICAS:
            estado.marcar_limpa(aba)
        estado.marcar_resumo_limpo()
        self.assertFalse(estado.trocar_concurso(1))
        self.assertFalse(estado.sujas)
        self.assertTrue(estado.trocar_concurso(2))
        self.assertEqual(set(ABAS_ESTATISTICAS), estado.sujas)
        self.assertTrue(estado.resumo_sujo)

    def test_registra_duracao_sem_valor_negativo(self):
        estado = EstadoEstatisticasLazy()
        estado.registrar_duracao("Histórico", -3)
        self.assertEqual(0.0, estado.duracoes_ms["Histórico"])
        estado.registrar_duracao("Histórico", 12.5)
        self.assertEqual(12.5, estado.duracoes_ms["Histórico"])


if __name__ == "__main__":
    unittest.main()
