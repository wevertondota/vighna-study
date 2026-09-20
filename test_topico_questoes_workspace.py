import unittest
from pathlib import Path


MAIN = Path(__file__).with_name("main.py").read_text(encoding="utf-8")


class TopicoQuestoesWorkspaceTests(unittest.TestCase):
    def test_workspace_expoe_importacao_e_cadastro_manual(self):
        self.assertIn('+ Importar para este tópico', MAIN)
        self.assertIn('+ Nova manualmente', MAIN)
        self.assertIn('def importar_questoes_topico(self):', MAIN)

    def test_tabela_exibe_capitulo(self):
        self.assertIn('"", "#", "Questão", "Capítulo", "Banca", "Ano", "Dificuldade", "Gabarito", "Status"', MAIN)
        self.assertIn('str(q.get("capitulo") or "—")', MAIN)

    def test_central_importacao_aceita_topico_contextual(self):
        self.assertIn('def abrir_central_importacao_questoes(self, topico_id_padrao=None):', MAIN)
        self.assertIn('topico_id_padrao=topico_id_padrao', MAIN)
        self.assertIn('Destino inicial', MAIN)

    def test_importadores_textuais_recebem_topico_contextual(self):
        self.assertIn('def __init__(self, parent=None, topico_id_padrao=None):', MAIN)
        self.assertIn('self.topico_id_padrao_contexto', MAIN)
        self.assertIn('self.topico_id_inicial_importacao', MAIN)

    def test_csv_usa_contexto_como_fallback(self):
        self.assertIn('def importar_questoes_csv(self, topico_id_padrao=None):', MAIN)
        self.assertIn('or disciplina_padrao', MAIN)
        self.assertIn('or topico_padrao', MAIN)


if __name__ == "__main__":
    unittest.main()
