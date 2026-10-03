import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / "main.py").read_text(encoding="utf-8")
TEMA = (ROOT / "tema.py").read_text(encoding="utf-8")
VERSAO = (ROOT / "versao.py").read_text(encoding="utf-8")
TREE = ast.parse(MAIN)


def metodo(classe, nome):
    for node in TREE.body:
        if isinstance(node, ast.ClassDef) and node.name == classe:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == nome:
                    return item
    raise AssertionError(f"Método {classe}.{nome} não encontrado")


class TopicDetailsRedesign048Tests(unittest.TestCase):
    def test_versao(self):
        self.assertIn('VIGHNA_VERSION = "0.29.48"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "topic-details-redesign-v1"', VERSAO)
        self.assertIn('VIGHNA_SCHEMA = 25', VERSAO)

    def test_janela_tem_hero_metricas_e_acoes(self):
        init = ast.unparse(metodo("JanelaTopico", "__init__"))
        for token in [
            "topicDetailsDialog",
            "topicHeroCard",
            "topicBreadcrumb",
            "topicMetricCard",
            "topicCompactMetric",
            "topicStudyButton",
            "topicQuestionsButton",
        ]:
            self.assertIn(token, init)

    def test_visao_geral_tem_dominio_e_proximo_passo(self):
        init = ast.unparse(metodo("JanelaTopico", "__init__"))
        for token in [
            "topicDomainCardModern",
            "topicDomainInsight",
            "topicNextStepCard",
            "Revisar agora",
            "Ver histórico",
        ]:
            self.assertIn(token, init)

    def test_evolucao_possui_estado_vazio_real(self):
        init = ast.unparse(metodo("JanelaTopico", "__init__"))
        carregar = ast.unparse(metodo("JanelaTopico", "carregar_historico"))
        self.assertIn("topicEvolutionEmpty", init)
        self.assertIn("Histórico detalhado ainda insuficiente", init)
        self.assertIn("self.grafico_evolucao.setVisible(not sem_evolucao)", carregar)
        self.assertIn("self.evolucao_vazia.setVisible(sem_evolucao)", carregar)

    def test_proximo_passo_reflete_agenda(self):
        carregar = ast.unparse(metodo("JanelaTopico", "carregar_historico"))
        self.assertIn("QDate.currentDate()", carregar)
        self.assertIn("REVISÃO EM ATRASO", carregar)
        self.assertIn("REVISÃO HOJE", carregar)
        self.assertIn("SEM REVISÃO AGENDADA", carregar)
        self.assertIn("scheduleState", carregar)

    def test_tema_tem_camada_propria_para_os_tres_temas(self):
        for constante in [
            "ESTILO_TOPICO_DETALHES_CLARO",
            "ESTILO_TOPICO_DETALHES_ESCURO",
            "ESTILO_TOPICO_DETALHES_FUTURISTA",
        ]:
            self.assertIn(constante, TEMA)
        for token in [
            "topicHeroCard",
            "topicDomainCardModern",
            "topicNextStepCard",
            "topicEvolutionEmpty",
        ]:
            self.assertIn(token, TEMA)


if __name__ == "__main__":
    unittest.main()
