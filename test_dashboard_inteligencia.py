from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / 'main.py').read_text(encoding='utf-8')
THEME = (ROOT / 'tema.py').read_text(encoding='utf-8')


class DashboardInteligenciaTests(unittest.TestCase):
    def test_dashboard_usa_recomendacao_do_algoritmo_simplificada(self):
        self.assertIn('Recomendação do algoritmo', MAIN)
        self.assertIn(
            'Sua próxima sessão foi definida com base no motor de inteligência do Vighna.',
            MAIN,
        )
        self.assertIn('algorithmRecommendationBody', MAIN)
        self.assertNotIn('algorithmRecommendationTitle', MAIN)
        self.assertNotIn('algorithmInsightChip', MAIN)

    def test_dashboard_possui_planejamento_compacto(self):
        self.assertIn('Planejamento de hoje', MAIN)
        self.assertIn('dashboardInsightSummary', MAIN)
        self.assertIn('dashboard_planejamento_resumo_meta_diaria', MAIN)
        self.assertIn('dashboard_planejamento_resumo_pendencias', MAIN)
        self.assertNotIn('dashboard_planejamento_resumo_7d', MAIN)
        self.assertNotIn('\"Próximos 7 dias\", \"Revisões já agendadas\", \"upcoming\"', MAIN)
        self.assertIn('dashboard_planejamento_resumo_semana', MAIN)
        self.assertIn('VER PLANEJAMENTO COMPLETO  →', MAIN)
        self.assertNotIn('Seu resumo de hoje', MAIN)


    def test_recomendacao_centralizada_no_espaco_restante(self):
        self.assertNotIn('acao_layout.setAlignment(Qt.AlignTop)', MAIN)
        self.assertIn('algoritmo_titulos.setAlignment(Qt.AlignTop)', MAIN)
        self.assertIn('resumo_ia_layout.setAlignment(Qt.AlignTop)', MAIN)
        self.assertIn('acao_layout.setContentsMargins(16, 8, 16, 10)', MAIN)
        self.assertIn('resumo_ia_layout.setContentsMargins(14, 6, 14, 8)', MAIN)
        trecho = MAIN[
            MAIN.index('inteligencia_conteudo_layout.addLayout(botoes_ia)'):
            MAIN.index('# Planejamento de hoje — painel operacional da primeira dobra.')
        ]
        self.assertEqual(trecho.count('acao_layout.addStretch(1)'), 2)
        self.assertIn('acao_layout.addWidget(inteligencia_conteudo)', trecho)
        self.assertLess(
            trecho.index('acao_layout.addStretch(1)'),
            trecho.index('acao_layout.addWidget(inteligencia_conteudo)'),
        )
        self.assertLess(
            trecho.index('acao_layout.addWidget(inteligencia_conteudo)'),
            trecho.rindex('acao_layout.addStretch(1)'),
        )

    def test_fila_tecnica_nao_ocupa_dashboard(self):
        self.assertIn('fila_painel.setVisible(False)', MAIN)
        secoes = MAIN[MAIN.index('def obter_secoes_recolhiveis_dashboard'):]
        self.assertNotIn('"fila": {', secoes.split('def definir_estado_secao_dashboard', 1)[0])

    def test_acessos_rapidos_ficam_depois_da_recomendacao(self):
        recomendacao = MAIN.index('layout.addLayout(inteligencia_linha)')
        acessos = MAIN.index('layout.addWidget(atalhos_rapidos)')
        estudo_questoes = MAIN.index('# ESTUDO POR QUESTÕES — slot prioritário')
        self.assertLess(recomendacao, acessos)
        self.assertLess(acessos, estudo_questoes)
        self.assertNotIn(
            'dashboard_hoje_conteudo_layout.addWidget(atalhos_rapidos)',
            MAIN,
        )

    def test_topo_e_foco_usam_compactacao_vertical(self):
        self.assertIn('topo.setContentsMargins(14, 7, 14, 7)', MAIN)
        self.assertIn('foco_hoje.setMinimumHeight(174)', MAIN)
        self.assertIn('progresso_card.setMinimumHeight(174)', MAIN)
        self.assertIn('"▾  Acessos rápidos"', MAIN)

    def test_estilos_novos_estao_nos_tres_temas(self):
        self.assertIn('ESTILO_INTELIGENCIA_RESUMO_CLARO', THEME)
        self.assertIn('ESTILO_INTELIGENCIA_RESUMO_ESCURO', THEME)
        self.assertIn('ESTILO_INTELIGENCIA_RESUMO_FUTURISTA', THEME)
        self.assertIn('+ ESTILO_INTELIGENCIA_RESUMO_CLARO', THEME)
        self.assertIn('+ ESTILO_INTELIGENCIA_RESUMO_ESCURO', THEME)
        self.assertIn('+ ESTILO_INTELIGENCIA_RESUMO_FUTURISTA', THEME)


if __name__ == '__main__':
    unittest.main()
