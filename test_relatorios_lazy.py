import unittest

from relatorios_lazy import ABAS_RELATORIOS, EstadoRelatoriosLazy


class EstadoRelatoriosLazyTests(unittest.TestCase):
    def test_inicia_com_resumo_e_todas_abas_sujas(self):
        estado = EstadoRelatoriosLazy()
        self.assertTrue(estado.resumo_sujo)
        self.assertEqual(set(ABAS_RELATORIOS), estado.sujas)

    def test_limpa_apenas_aba_carregada(self):
        estado = EstadoRelatoriosLazy()
        estado.marcar_limpa("Estratégico")
        self.assertFalse(estado.precisa_atualizar("Estratégico"))
        self.assertTrue(estado.precisa_atualizar("Por tópico"))

    def test_contexto_igual_nao_invalida_novamente(self):
        estado = EstadoRelatoriosLazy()
        self.assertTrue(estado.trocar_contexto(40, "2026-08-20", "2026-09-18"))
        for aba in ABAS_RELATORIOS:
            estado.marcar_limpa(aba)
        estado.marcar_resumo_limpo()
        self.assertFalse(estado.trocar_contexto(40, "2026-08-20", "2026-09-18"))
        self.assertFalse(estado.resumo_sujo)
        self.assertEqual(set(), estado.sujas)

    def test_mudanca_de_periodo_invalida_tudo(self):
        estado = EstadoRelatoriosLazy()
        estado.trocar_contexto(40, "2026-08-20", "2026-09-18")
        for aba in ABAS_RELATORIOS:
            estado.marcar_limpa(aba)
        estado.marcar_resumo_limpo()
        self.assertTrue(estado.trocar_contexto(40, "2026-09-12", "2026-09-18"))
        self.assertTrue(estado.resumo_sujo)
        self.assertEqual(set(ABAS_RELATORIOS), estado.sujas)

    def test_diagnostico_registra_duracao(self):
        estado = EstadoRelatoriosLazy()
        estado.registrar_duracao("Estratégico", 12.5)
        self.assertEqual(12.5, estado.diagnostico()["duracoes_ms"]["Estratégico"])


if __name__ == "__main__":
    unittest.main()
