import unittest
from pathlib import Path

MAIN = Path(__file__).with_name('main.py').read_text(encoding='utf-8')


class VerQuestoesTopicoNavegacaoTests(unittest.TestCase):
    def test_pagina_topico_usa_central_contextual(self):
        self.assertIn('def ver_questoes_topico(self):', MAIN)
        self.assertIn('abrir_questoes_topico_contextual', MAIN)
        self.assertIn('self.accept()', MAIN)

    def test_tela_disciplina_usa_central_contextual(self):
        trecho = MAIN[MAIN.index('def ver_questoes_topico_selecionado(self):'):]
        trecho = trecho[:trecho.index('\n    def ', 10)]
        self.assertIn('self.abrir_questoes_topico_contextual(topico_id)', trecho)
        self.assertNotIn('JanelaGerenciarQuestoesTopico(', trecho)

    def test_contexto_e_aplicado_depois_da_carga_lazy(self):
        self.assertIn('_central_questoes_contexto_pendente', MAIN)
        self.assertIn('_aplicar_contexto_pendente_central_questoes', MAIN)
        self.assertIn('QTimer.singleShot(0, self._aplicar_contexto_pendente_central_questoes)', MAIN)

    def test_topico_sem_questoes_pode_receber_primeira_questao(self):
        self.assertIn('self.questoes_filtro_topico.addItem(topico)', MAIN)
        self.assertIn('_obter_topico_id_contexto_central_questoes', MAIN)

    def test_nova_e_importacao_herdam_contexto(self):
        self.assertIn('topico_id_contexto = self._obter_topico_id_contexto_central_questoes()', MAIN)
        self.assertIn('topico_id_padrao = self._obter_topico_id_contexto_central_questoes()', MAIN)


if __name__ == '__main__':
    unittest.main()
