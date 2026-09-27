"""Testes do ciclo persistente de questões por tópico (0.29.23)."""

from __future__ import annotations

import ast
import gc
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

import banco


class CicloQuestoesPersistenteTests(unittest.TestCase):
    def setUp(self):
        self.original = banco.CAMINHO_BANCO
        self.temp = tempfile.TemporaryDirectory(prefix="vighna_ciclo_questoes_")
        banco.CAMINHO_BANCO = Path(self.temp.name) / "estudos.db"
        banco.criar_banco()
        self.concurso_id = int(banco.adicionar_concurso("Perfil ciclo"))
        banco.definir_concurso_ativo(self.concurso_id)
        self.disciplina_id = int(banco.adicionar_disciplina("Disciplina ciclo"))
        banco.adicionar_topico("Disciplina ciclo", "Tópico ciclo")
        with closing(banco.conectar()) as con:
            self.topico_id = int(con.execute(
                "SELECT id FROM topicos WHERE disciplina_id = ?",
                (self.disciplina_id,),
            ).fetchone()[0])
            con.execute(
                "INSERT OR IGNORE INTO disciplina_concurso_inclusao "
                "(disciplina_id, concurso_id, incluido, pausado) VALUES (?, ?, 1, 0)",
                (self.disciplina_id, self.concurso_id),
            )
            con.execute(
                "INSERT OR IGNORE INTO topico_concurso_importancia "
                "(topico_id, concurso_id, importancia, incluido, pausado) "
                "VALUES (?, ?, 3, 1, 0)",
                (self.topico_id, self.concurso_id),
            )
            con.commit()

        self.questoes = [
            int(banco.criar_questao(
                self.topico_id,
                f"Questão {indice}?",
                [
                    {"letra": "A", "texto": "Correta", "correta": True},
                    {"letra": "B", "texto": "Errada", "correta": False},
                ],
            ))
            for indice in range(1, 7)
        ]

    def tearDown(self):
        banco.CAMINHO_BANCO = self.original
        gc.collect()
        self.temp.cleanup()

    def test_snapshot_nao_recebe_questao_nova(self):
        ciclo = banco.criar_ciclo_questoes(
            self.concurso_id,
            self.topico_id,
            self.questoes,
            filtros={"estado": "todas"},
        )
        nova = int(banco.criar_questao(
            self.topico_id,
            "Questão importada depois?",
            [
                {"letra": "A", "texto": "Correta", "correta": True},
                {"letra": "B", "texto": "Errada", "correta": False},
            ],
        ))
        estado = banco.obter_estado_ciclo_questoes(ciclo["id"])
        self.assertEqual(estado["total"], 6)
        self.assertNotIn(nova, estado["ids_pendentes"])

    def test_continuidade_e_conclusao(self):
        ciclo = banco.criar_ciclo_questoes(
            self.concurso_id,
            self.topico_id,
            self.questoes,
        )
        for questao_id in self.questoes[:2]:
            banco.marcar_questao_ciclo_respondida(ciclo["id"], questao_id)

        estado = banco.obter_ciclo_questoes_ativo(
            self.concurso_id,
            self.topico_id,
        )
        self.assertEqual(estado["respondidas"], 2)
        self.assertEqual(estado["pendentes"], 4)
        self.assertEqual(set(estado["ids_pendentes"]), set(self.questoes[2:]))

        for questao_id in self.questoes[2:]:
            banco.marcar_questao_ciclo_respondida(ciclo["id"], questao_id)

        final = banco.obter_estado_ciclo_questoes(ciclo["id"])
        self.assertEqual(final["status"], "concluido")
        self.assertEqual(final["respondidas"], 6)
        self.assertEqual(final["pendentes"], 0)
        self.assertIsNone(banco.obter_ciclo_questoes_ativo(
            self.concurso_id,
            self.topico_id,
        ))

    def test_um_ciclo_ativo_por_perfil_e_topico(self):
        banco.criar_ciclo_questoes(
            self.concurso_id,
            self.topico_id,
            self.questoes,
        )
        with self.assertRaises(ValueError):
            banco.criar_ciclo_questoes(
                self.concurso_id,
                self.topico_id,
                self.questoes[:3],
            )

    def test_encerramento_manual_preserva_itens(self):
        ciclo = banco.criar_ciclo_questoes(
            self.concurso_id,
            self.topico_id,
            self.questoes,
        )
        encerrado = banco.encerrar_ciclo_questoes(ciclo["id"])
        self.assertEqual(encerrado["status"], "cancelado")
        self.assertEqual(encerrado["total"], 6)
        self.assertEqual(encerrado["pendentes"], 6)

    def test_interface_e_pulos_respeitam_ciclo(self):
        pasta = Path(__file__).resolve().parent
        main = (pasta / "main.py").read_text(encoding="utf-8")
        ast.parse(main)
        self.assertIn("Ciclo de questões", main)
        self.assertIn("Continuar ciclo atual", main)
        self.assertIn("Iniciar novo ciclo com o conjunto filtrado", main)
        self.assertIn("ciclo_questoes_id", main)
        self.assertIn('bool(resultado_pulo.get("pulo_convertido_erro"))', main)
        self.assertIn("Questões novas importadas depois do início ficam para o próximo ciclo.", main)


if __name__ == "__main__":
    unittest.main(verbosity=2)
