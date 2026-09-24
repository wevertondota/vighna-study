import gc
import tempfile
import unittest
from pathlib import Path

import banco


class ExclusaoCapituloTests(unittest.TestCase):
    def setUp(self):
        self._caminho_original = banco.CAMINHO_BANCO
        self._tmp = tempfile.TemporaryDirectory()
        banco.CAMINHO_BANCO = Path(self._tmp.name) / "teste.db"
        banco.criar_banco()

    def tearDown(self):
        banco.CAMINHO_BANCO = self._caminho_original
        gc.collect()
        self._tmp.cleanup()

    def _criar_estrutura_generica(self):
        with banco.conectar() as conexao:
            disciplina_id = conexao.execute(
                "INSERT INTO disciplinas (nome) VALUES (?)",
                ("Direito Constitucional Teste",),
            ).lastrowid
            topico_id = conexao.execute(
                "INSERT INTO topicos (disciplina_id, nome) VALUES (?, ?)",
                (disciplina_id, "TÍTULO II — Teste"),
            ).lastrowid
            capitulo_id = conexao.execute(
                "INSERT INTO capitulos_topico (topico_id, nome, ordem) VALUES (?, ?, 1)",
                (topico_id, "CAPÍTULO II — Dos Direitos Sociais"),
            ).lastrowid
            questao_id = conexao.execute(
                "INSERT INTO questoes (topico_id, capitulo_id, enunciado) VALUES (?, ?, ?)",
                (topico_id, capitulo_id, "Questão vinculada ao capítulo"),
            ).lastrowid
        return int(topico_id), int(capitulo_id), int(questao_id)

    def test_excluir_capitulo_preserva_questao_no_titulo(self):
        topico_id, capitulo_id, questao_id = self._criar_estrutura_generica()

        self.assertEqual(banco.contar_questoes_capitulo(capitulo_id), 1)
        self.assertTrue(banco.excluir_capitulo(capitulo_id))

        with banco.conectar() as conexao:
            capitulo = conexao.execute(
                "SELECT 1 FROM capitulos_topico WHERE id = ?", (capitulo_id,)
            ).fetchone()
            questao = conexao.execute(
                "SELECT topico_id, capitulo_id FROM questoes WHERE id = ?", (questao_id,)
            ).fetchone()

        self.assertIsNone(capitulo)
        self.assertEqual(int(questao[0]), topico_id)
        self.assertIsNone(questao[1])

    def test_excluir_capitulo_inexistente_retorna_false(self):
        self.assertFalse(banco.excluir_capitulo(999999))

    def test_capitulo_padrao_excluido_nao_e_recriado(self):
        with banco.conectar() as conexao:
            penal_id = conexao.execute(
                "SELECT id FROM disciplinas WHERE nome = 'Direito Penal'"
            ).fetchone()[0]
            topicos = [
                int(linha[0])
                for linha in conexao.execute(
                    "SELECT id FROM topicos WHERE disciplina_id = ? ORDER BY id",
                    (penal_id,),
                ).fetchall()
            ]

        topico_id = None
        capitulos = []
        for candidato_id in topicos:
            candidatos = banco.listar_capitulos_topico(candidato_id)
            if candidatos:
                topico_id = candidato_id
                capitulos = candidatos
                break

        if topico_id is None:
            self.skipTest("Nenhum título penal com capítulos padrão foi materializado neste banco.")

        capitulo_id = int(capitulos[0][0])
        nome = str(capitulos[0][1])
        self.assertTrue(banco.excluir_capitulo(capitulo_id))

        nomes_depois = [item[1] for item in banco.listar_capitulos_topico(topico_id)]
        self.assertNotIn(nome, nomes_depois)


if __name__ == "__main__":
    unittest.main()
