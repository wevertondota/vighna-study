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


class CalendarWeekForecast059Tests(unittest.TestCase):
    def test_versao_build_schema(self):
        self.assertIn('VIGHNA_VERSION = "0.29.59"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "calendar-week-forecast-v1"', VERSAO)
        self.assertIn('VIGHNA_SCHEMA = 25', VERSAO)

    def test_calendario_tem_duas_visualizacoes(self):
        criar = ast.unparse(metodo("SistemaEstudos", "criar_tela_calendario"))
        self.assertIn("Calendário de Estudos", criar)
        self.assertIn("calendarViewToggle", criar)
        self.assertIn("Semana prevista", criar)
        self.assertIn("QStackedWidget", criar)
        self.assertIn("self.calendario_pagina_semana", criar)

    def test_previsao_e_lazy_e_nao_pesa_no_preload_mensal(self):
        alternar = ast.unparse(metodo("SistemaEstudos", "alternar_visualizacao_calendario"))
        atualizar = ast.unparse(metodo("SistemaEstudos", "atualizar_calendario"))
        self.assertIn("self.atualizar_previsao_semana_calendario()", alternar)
        self.assertIn("self.calendario_paginas.currentIndex() == 1", atualizar)

    def test_motor_reutiliza_plano_automatico_por_sete_dias(self):
        montar = ast.unparse(metodo("SistemaEstudos", "_montar_itens_previsao_calendario"))
        self.assertIn("gerar_plano_acao_automatico", montar)
        self.assertIn("segunda = hoje.addDays(1 - hoje.dayOfWeek())", montar)
        self.assertIn("domingo = segunda.addDays(6)", montar)
        self.assertIn("horizonte = max(3, hoje.daysTo(domingo) + 1)", montar)
        self.assertIn("variacao=0", montar)
        self.assertIn("obter_plano_acao_automatico", montar)

    def test_dias_passados_exibem_estudo_real_registrado(self):
        montar = ast.unparse(metodo("SistemaEstudos", "_montar_itens_previsao_calendario"))
        self.assertIn("obter_relatorio_topicos_periodo", montar)
        self.assertIn("'Estudado'", montar)
        self.assertIn("'Estudado hoje'", montar)
        self.assertIn("'realizado': True", montar)

    def test_revisoes_sao_exibidas_por_topico_e_nao_em_bloco_generico(self):
        montar = ast.unparse(metodo("SistemaEstudos", "_montar_itens_previsao_calendario"))
        self.assertIn("listar_pendencias", montar)
        self.assertIn("listar_revisoes_agendadas_periodo", montar)
        self.assertIn("item.get('origem') == 'agenda_revisoes'", montar)
        self.assertIn("continue", montar)
        self.assertIn("chave = (data_txt, int(topico_id))", montar)

    def test_quadro_tem_sete_colunas_cards_e_estado_vazio(self):
        atualizar = ast.unparse(metodo("SistemaEstudos", "atualizar_previsao_semana_calendario"))
        self.assertIn("for deslocamento in range(7)", atualizar)
        self.assertIn("segunda = hoje.addDays(1 - hoje.dayOfWeek())", atualizar)
        self.assertIn("calendarForecastDay", atualizar)
        self.assertIn("Sem atividade prevista", atualizar)
        self.assertIn("Sem estudo registrado", atualizar)
        self.assertIn("Atualizado", atualizar)

    def test_cards_explicam_motivo_e_abrem_topico(self):
        card = ast.unparse(metodo("SistemaEstudos", "_criar_card_previsao_calendario"))
        self.assertIn("Por que isso está aqui?", card)
        self.assertIn("calendarForecastReason", card)
        self.assertIn("abrir_topico_previsao_calendario", card)

    def test_previsao_e_invalidada_quando_estado_de_estudo_muda(self):
        notificar = ast.unparse(metodo("SistemaEstudos", "notificar_dados_alterados"))
        self.assertIn("self._previsao_semana_suja = True", notificar)
        self.assertIn("'foco'", notificar)
        self.assertIn("'revisoes'", notificar)
        self.assertIn("'tentativas'", notificar)

    def test_estilo_existe_nos_tres_temas(self):
        self.assertIn("ESTILO_CALENDARIO_PREVISAO_CLARO", TEMA)
        self.assertIn("ESTILO_CALENDARIO_PREVISAO_ESCURO", TEMA)
        self.assertIn("ESTILO_CALENDARIO_PREVISAO_FUTURISTA", TEMA)
        self.assertGreaterEqual(TEMA.count("calendarForecastCard"), 9)
        self.assertGreaterEqual(TEMA.count("calendarViewToggle"), 9)


if __name__ == "__main__":
    unittest.main()
