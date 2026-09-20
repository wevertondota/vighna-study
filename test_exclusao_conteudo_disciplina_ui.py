import unittest
from pathlib import Path

MAIN = Path(__file__).with_name('main.py').read_text(encoding='utf-8')


class ExclusaoConteudoDisciplinaUITests(unittest.TestCase):
    def test_excluir_habilita_para_capitulo_ou_topico(self):
        self.assertIn('self.botao_excluir_topico.setEnabled(conteudo_id is not None)', MAIN)

    def test_fluxo_de_exclusao_trata_capitulo(self):
        trecho = MAIN[MAIN.index('def excluir_topico_selecionado(self):'):]
        trecho = trecho[:trecho.index('\n    def atualizar_revisao_topico(', 10)]
        self.assertIn('if tipo == "capitulo":', trecho)
        self.assertIn('contar_questoes_capitulo(conteudo_id)', trecho)
        self.assertIn('excluir_capitulo(conteudo_id)', trecho)
        self.assertIn('As questões NÃO serão apagadas', trecho)

    def test_fluxo_de_exclusao_preserva_exclusao_de_topico(self):
        trecho = MAIN[MAIN.index('def excluir_topico_selecionado(self):'):]
        trecho = trecho[:trecho.index('\n    def atualizar_revisao_topico(', 10)]
        self.assertIn('excluir_topico(', trecho)
        self.assertIn('"Excluir título/tópico"', trecho)


if __name__ == '__main__':
    unittest.main()
