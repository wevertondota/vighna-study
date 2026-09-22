import ast
import gc
import json
import tempfile
import unittest
from contextlib import closing
from datetime import date
from pathlib import Path

import banco


class TestCoberturaEPulo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = Path(__file__).resolve().parent
        cls.main = (cls.pasta / "main.py").read_text(encoding="utf-8")
        cls.banco = (cls.pasta / "banco.py").read_text(encoding="utf-8")
        ast.parse(cls.main)
        ast.parse(cls.banco)

    def test_interface_exibe_cobertura(self):
        self.assertIn('"Cobertura"', self.main)
        self.assertIn("Revisão em andamento:", self.main)
        self.assertIn("próxima data após concluir a cobertura", self.main)

    def test_primeiro_pulo_reagenda_para_o_fim(self):
        self.assertIn("reagendar_questao_pulada_no_fim_sessao", self.main)
        self.assertIn("self.fila.append(item_retorno)", self.main)
        self.assertIn("retorno de questão pulada", self.main)

    def test_segundo_pulo_equivale_a_erro(self):
        self.assertIn("tratar_pulo_como_erro=tratar_como_erro", self.main)
        self.assertIn('"pulo_reincidente"', self.banco)
        self.assertIn("resultado = 0 if pulo_convertido_erro else None", self.banco)

    def test_pulo_reincidente_cobre_revisao_como_erro(self):
        caminho_original = banco.CAMINHO_BANCO
        pasta = tempfile.TemporaryDirectory(prefix="vighna_pulo_reincidente_")
        try:
            banco.CAMINHO_BANCO = Path(pasta.name) / "estudos.db"
            banco.criar_banco()
            concurso_id = banco.adicionar_concurso("Perfil de teste")
            banco.definir_concurso_ativo(concurso_id)
            disciplina_id = banco.adicionar_disciplina("Disciplina de teste")
            banco.adicionar_topico("Disciplina de teste", "Tópico de teste")
            with closing(banco.conectar()) as conexao:
                topico_id = conexao.execute(
                    "SELECT id FROM topicos WHERE disciplina_id = ?",
                    (disciplina_id,),
                ).fetchone()[0]
                conexao.execute(
                    "INSERT OR IGNORE INTO controle_topico (topico_id) VALUES (?)",
                    (topico_id,),
                )
                conexao.execute(
                    "UPDATE controle_topico SET proxima_revisao = ? WHERE topico_id = ?",
                    (date.today().isoformat(), topico_id),
                )
                conexao.commit()

            questao_id = banco.criar_questao(
                topico_id,
                "Questão de teste?",
                [
                    {"letra": "A", "texto": "Correta", "correta": True},
                    {"letra": "B", "texto": "Errada", "correta": False},
                ],
            )
            sessao_id = banco.iniciar_sessao_questoes(
                concurso_id, "Revisão inteligente", 1,
            )
            banco.registrar_fila_sessao_questoes(
                sessao_id, [{"id": questao_id}],
            )
            item_id = banco.marcar_item_sessao_apresentado(
                sessao_id, 1, questao_id,
            )
            primeiro = banco.registrar_tentativa_questao(
                sessao_id, questao_id, concurso_id, item_sessao_id=item_id,
            )
            self.assertTrue(primeiro["pulada"])
            self.assertEqual(
                banco.obter_estado_cobertura_revisao(topico_id, concurso_id)["restantes"],
                1,
            )

            retorno = banco.reagendar_questao_pulada_no_fim_sessao(
                sessao_id, questao_id,
            )
            self.assertEqual(retorno["ordem"], 2)
            item_retorno_id = banco.marcar_item_sessao_apresentado(
                sessao_id, 2, questao_id,
            )
            self.assertEqual(item_retorno_id, retorno["item_id"])
            segundo = banco.registrar_tentativa_questao(
                sessao_id, questao_id, concurso_id,
                item_sessao_id=item_retorno_id,
                tratar_pulo_como_erro=True,
            )
            self.assertFalse(segundo["correta"])
            self.assertTrue(segundo["pulo_convertido_erro"])
            self.assertEqual(
                banco.obter_estado_cobertura_revisao(topico_id, concurso_id)["cobertas"],
                1,
            )

            with closing(banco.conectar()) as conexao:
                itens = conexao.execute(
                    "SELECT estado, contexto_selecao_json FROM itens_sessao_questoes "
                    "WHERE sessao_id = ? ORDER BY ordem",
                    (sessao_id,),
                ).fetchall()
                tentativas = conexao.execute(
                    "SELECT correta, alternativa_marcada, snapshot_origem "
                    "FROM tentativas_questoes WHERE sessao_id = ? ORDER BY id",
                    (sessao_id,),
                ).fetchall()
            self.assertEqual([item[0] for item in itens], ["pulada", "respondida"])
            self.assertTrue(json.loads(itens[1][1])["retorno_pulo"])
            self.assertEqual(
                tentativas,
                [(None, None, "pulo"), (0, None, "pulo_reincidente")],
            )
        finally:
            banco.CAMINHO_BANCO = caminho_original
            gc.collect()
            pasta.cleanup()


if __name__ == "__main__":
    unittest.main()
