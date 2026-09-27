import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / 'main.py').read_text(encoding='utf-8')
THEME = (ROOT / 'tema.py').read_text(encoding='utf-8')
VERSAO = (ROOT / 'versao.py').read_text(encoding='utf-8')


class TestDashboardPlanejamentoMetaProtagonista02929(unittest.TestCase):
    def test_main_tem_sintaxe_valida(self):
        ast.parse(MAIN)

    def test_versao_build_schema(self):
        self.assertIn('VIGHNA_VERSION = "0.29.29"', VERSAO)
        self.assertIn(
            'VIGHNA_BUILD = "dashboard-planejamento-meta-protagonista-v1"',
            VERSAO,
        )
        self.assertIn('VIGHNA_SCHEMA = 23', VERSAO)

    def test_meta_diaria_e_protagonista_visual(self):
        self.assertIn('dashboardPlanningHeroTitle', MAIN)
        self.assertIn('dashboardPlanningHeroValue', MAIN)
        self.assertIn('dashboardPlanningHeroDetail', MAIN)
        self.assertIn('self.dashboard_resumo_meta_barra.setFixedHeight(8)', MAIN)
        self.assertIn('f"{questoes_hoje} / {meta}"', MAIN)
        self.assertIn('% concluído • faltam', MAIN)

    def test_revisoes_e_carga_usam_um_unico_bloco_operacional(self):
        self.assertIn('dashboardPlanningOperational', MAIN)
        self.assertIn('dashboardPlanningDivider', MAIN)
        self.assertIn('REVISÕES PENDENTES', MAIN)
        self.assertIn('PARA CONCLUIR O DIA', MAIN)
        self.assertNotIn('revisoes_box = QFrame()', MAIN)
        self.assertNotIn('carga_box_resumo = QFrame()', MAIN)

    def test_semana_virou_faixa_unica(self):
        self.assertIn('def adicionar_status_semana(chave, titulo):', MAIN)
        self.assertIn('adicionar_status_semana("questoes", "Questões")', MAIN)
        self.assertIn('adicionar_status_semana("revisoes", "Revisões")', MAIN)
        self.assertIn('adicionar_status_semana("dias", "Dias")', MAIN)
        self.assertNotIn('def criar_status_semana_compacto', MAIN)
        self.assertNotIn('semana_grade = QHBoxLayout()', MAIN)

    def test_estilos_do_hero_presentes_nos_tres_temas(self):
        self.assertEqual(THEME.count('QLabel#dashboardPlanningHeroValue'), 3)
        self.assertEqual(THEME.count('QFrame#dashboardPlanningOperational'), 3)
        self.assertEqual(THEME.count('QLabel#dashboardPlanningWeekLabel'), 3)
        self.assertIn('font-size: 24pt;', THEME)


if __name__ == '__main__':
    unittest.main()
