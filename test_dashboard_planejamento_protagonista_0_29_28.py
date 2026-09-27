import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / "main.py").read_text(encoding="utf-8")
VERSAO = (ROOT / "versao.py").read_text(encoding="utf-8")


class TestDashboardPlanejamentoProtagonista02928(unittest.TestCase):
    def test_main_tem_sintaxe_valida(self):
        ast.parse(MAIN)

    def test_versao_build_schema(self):
        self.assertIn('VIGHNA_VERSION = "0.29.28"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "dashboard-planejamento-protagonista-v1"', VERSAO)
        self.assertIn('VIGHNA_SCHEMA = 23', VERSAO)

    def test_primeira_linha_e_foco_mais_planejamento(self):
        self.assertIn('dashboard_planejamento_top_container', MAIN)
        self.assertIn('foco_cards.addWidget(foco_hoje, 1)', MAIN)
        self.assertIn('foco_cards.addWidget(self.dashboard_planejamento_top_container, 1)', MAIN)
        self.assertNotIn('foco_cards.addWidget(progresso_card, 1)', MAIN)

    def test_segunda_linha_e_recomendacao_mais_progresso(self):
        self.assertIn('inteligencia_linha.addWidget(self.dashboard_hoje_acao, 3)', MAIN)
        self.assertIn('inteligencia_linha.addWidget(progresso_card, 1)', MAIN)
        self.assertNotIn('inteligencia_linha.addWidget(self.dashboard_resumo_ia, 1)', MAIN)

    def test_planejamento_virou_painel_operacional(self):
        for trecho in (
            'META DE QUESTÕES',
            'REVISÕES',
            'PARA CONCLUIR O DIA',
            'SEMANA',
            'VER PLANEJAMENTO COMPLETO  →',
            'dashboard_planejamento_status_dia',
            'dashboard_planejamento_carga_valor',
            'dashboard_planejamento_semana_labels',
        ):
            self.assertIn(trecho, MAIN)

    def test_semana_tem_tres_sinais_independentes(self):
        self.assertIn('criar_status_semana_compacto("questoes", "Questões")', MAIN)
        self.assertIn('criar_status_semana_compacto("revisoes", "Revisões")', MAIN)
        self.assertIn('criar_status_semana_compacto("dias", "Dias de estudo")', MAIN)
        self.assertIn('situacao_meta_compacta', MAIN)
        self.assertIn('"texto": "Atenção", "estado": "atencao"', MAIN)

    def test_status_do_dia_considera_meta_e_revisoes(self):
        self.assertIn('status_dia = "CONCLUÍDO"', MAIN)
        self.assertIn('status_dia = "ATENÇÃO"', MAIN)
        self.assertIn('status_dia = "META CONCLUÍDA"', MAIN)
        self.assertIn('status_dia = "EM ANDAMENTO"', MAIN)


if __name__ == "__main__":
    unittest.main()
