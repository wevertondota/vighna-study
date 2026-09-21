import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent
MAIN = (BASE / 'main.py').read_text(encoding='utf-8')
TEMA = (BASE / 'tema.py').read_text(encoding='utf-8')


class TopicosDisciplinaVisualTests(unittest.TestCase):
    def test_tabela_tem_identidade_visual_propria(self):
        self.assertIn('self.tabela_topicos.setObjectName("disciplineTopicsTable")', MAIN)
        self.assertIn('alternate-background-color: #f8fbff;', TEMA)
        self.assertIn('selection-background-color: #dbeafe;', TEMA)

    def test_topico_com_capitulos_nao_desenha_texto_duas_vezes(self):
        inicio = MAIN.index('def renderizar_topicos(self, dados):')
        fim = MAIN.index('def _reaplicar_filtros_topicos_preservando_scroll', inicio)
        trecho = MAIN[inicio:fim]
        self.assertIn('tem_capitulos = topico_possui_capitulos(topico_id)', trecho)
        self.assertIn('"" if tem_capitulos else nome_exibicao', trecho)
        self.assertIn('texto_topico = QLabel(nome_exibicao)', trecho)

    def test_celula_de_topico_com_capitulos_e_transparente(self):
        self.assertIn('celula_topico.setObjectName("disciplineTopicCell")', MAIN)
        self.assertIn('celula_topico.setProperty("inactive", pausado)', MAIN)
        self.assertIn('texto_topico.setObjectName("disciplineTopicCellLabel")', MAIN)
        self.assertIn('QWidget#disciplineTopicCell,', TEMA)
        self.assertIn('background: transparent;', TEMA)

    def test_inativos_nao_recebem_fundo_de_linha(self):
        inicio = MAIN.index('def renderizar_topicos(self, dados):')
        fim = MAIN.index('def _reaplicar_filtros_topicos_preservando_scroll', inicio)
        trecho = MAIN[inicio:fim]
        self.assertIn('"inativo",\n                            False', trecho)
        self.assertNotIn('"inativo",\n                            True', trecho)

        inicio_cap = MAIN.index('def renderizar_capitulo_inline', fim)
        fim_cap = MAIN.index('def alterar_dificuldade_capitulo_inline', inicio_cap)
        trecho_cap = MAIN[inicio_cap:fim_cap]
        self.assertIn('"inativo",\n                    False', trecho_cap)
        self.assertNotIn('"inativo",\n                    True', trecho_cap)

    def test_estado_ativo_usa_somente_cor_de_texto(self):
        self.assertGreaterEqual(MAIN.count('"sucesso",\n                    False'), 2)

    def test_todos_os_temas_possuem_estilo_da_tabela(self):
        self.assertIn('ESTILO_TOPICOS_DISCIPLINA_CLARO', TEMA)
        self.assertIn('ESTILO_TOPICOS_DISCIPLINA_ESCURO', TEMA)
        self.assertIn('ESTILO_TOPICOS_DISCIPLINA_FUTURISTA', TEMA)
        self.assertIn('+ ESTILO_TOPICOS_DISCIPLINA_CLARO', TEMA)
        self.assertIn('+ ESTILO_TOPICOS_DISCIPLINA_ESCURO', TEMA)
        self.assertIn('+ ESTILO_TOPICOS_DISCIPLINA_FUTURISTA', TEMA)


if __name__ == '__main__':
    unittest.main()
