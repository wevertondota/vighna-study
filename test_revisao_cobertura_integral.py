"""Testes da rodada de cobertura integral das revisões (0.29.8)."""

from __future__ import annotations

import gc
import tempfile
import unittest
from contextlib import closing
from datetime import date
from pathlib import Path

import banco
from ciclo_estudo import integrar_sessao_questoes_com_revisoes


class RevisaoCoberturaIntegralTests(unittest.TestCase):
    def setUp(self):
        self.original = banco.CAMINHO_BANCO
        self.temp = tempfile.TemporaryDirectory(prefix="vighna_revisao_cobertura_")
        banco.CAMINHO_BANCO = Path(self.temp.name) / "estudos.db"
        banco.criar_banco()
        concurso_id = banco.adicionar_concurso("Perfil Cobertura")
        banco.definir_concurso_ativo(concurso_id)
        self.concurso_id = int(concurso_id)
        self.disciplina_id = int(banco.adicionar_disciplina("Disciplina Cobertura"))
        self.assertTrue(banco.adicionar_topico("Disciplina Cobertura", "Tópico 80"))
        with closing(banco.conectar()) as con:
            self.topico_id = int(con.execute(
                "SELECT id FROM topicos WHERE disciplina_id = ? AND nome = ?",
                (self.disciplina_id, "Tópico 80"),
            ).fetchone()[0])
        self.questoes = []
        for indice in range(80):
            qid = banco.criar_questao(
                self.topico_id,
                f"Questão cobertura {indice + 1}?",
                [
                    {"letra": "A", "texto": "Correta", "correta": True},
                    {"letra": "B", "texto": "Errada", "correta": False},
                    {"letra": "C", "texto": "Errada 2", "correta": False},
                    {"letra": "D", "texto": "Errada 3", "correta": False},
                ],
            )
            self.questoes.append(int(qid))
        with closing(banco.conectar()) as con:
            con.execute(
                "INSERT OR IGNORE INTO controle_topico (topico_id) VALUES (?)",
                (self.topico_id,),
            )
            con.execute(
                "UPDATE controle_topico SET proxima_revisao = ? WHERE topico_id = ?",
                (date.today().isoformat(), self.topico_id),
            )
            con.commit()

    def tearDown(self):
        banco.CAMINHO_BANCO = self.original
        gc.collect()
        self.temp.cleanup()

    def _resolver(self, ids, erros=None, modo="Revisão inteligente"):
        erros = set(erros or [])
        fila = [{"id": int(qid)} for qid in ids]
        sessao_id = banco.iniciar_sessao_questoes(
            self.concurso_id,
            modo,
            len(fila),
            origem="revisao_inteligente",
            contexto={"teste": "cobertura_integral"},
            versao_motor="sessao_unificado_v1",
        )
        banco.registrar_fila_sessao_questoes(sessao_id, fila)
        itens = banco.obter_itens_sessao_questoes(sessao_id)
        for item in itens:
            qid = int(item["questao_id"])
            item_id = banco.marcar_item_sessao_apresentado(
                sessao_id, int(item["ordem"]), qid
            )
            banco.registrar_tentativa_questao(
                sessao_id,
                qid,
                self.concurso_id,
                alternativa_marcada="B" if qid in erros else "A",
                tempo_segundos=10,
                item_sessao_id=item_id,
            )
        banco.encerrar_sessao_questoes(sessao_id, concluida=True)
        return sessao_id, integrar_sessao_questoes_com_revisoes(sessao_id)

    def test_primeira_metade_nao_reagenda_e_segunda_recebe_restantes(self):
        primeira = self.questoes[:40]
        sessao1, integracao1 = self._resolver(primeira, erros=primeira[:8])
        self.assertEqual(len(integracao1), 1)
        self.assertEqual(integracao1[0]["status_integracao"], "cobertura_parcial")
        self.assertFalse(integracao1[0]["revisao_registrada"])
        self.assertFalse(integracao1[0]["agendamento_atualizado"])

        estado = banco.obter_estado_cobertura_revisao(
            self.topico_id, self.concurso_id
        )
        self.assertTrue(estado["ativa"])
        self.assertEqual(estado["total"], 80)
        self.assertEqual(estado["cobertas"], 40)
        self.assertEqual(estado["restantes"], 40)

        selecao = banco.selecionar_questoes_revisao_cobertura(
            self.concurso_id,
            self.topico_id,
            quantidade=40,
        )
        ids_segunda = [int(item["id"]) for item in selecao["fila"]]
        self.assertEqual(len(ids_segunda), 40)
        self.assertTrue(set(ids_segunda).isdisjoint(set(primeira)))
        self.assertEqual(set(ids_segunda), set(self.questoes[40:]))

        sessao2, integracao2 = self._resolver(ids_segunda, erros=ids_segunda[:8])
        self.assertEqual(len(integracao2), 1)
        self.assertEqual(integracao2[0]["status_integracao"], "cobertura_completa")
        self.assertTrue(integracao2[0]["revisao_registrada"])
        self.assertTrue(integracao2[0]["agendamento_atualizado"])
        self.assertEqual(integracao2[0]["questoes"], 80)
        self.assertEqual(integracao2[0]["acertos"], 64)
        self.assertAlmostEqual(integracao2[0]["percentual"], 80.0)

        with closing(banco.conectar()) as con:
            revisoes = con.execute(
                "SELECT questoes, acertos FROM revisoes WHERE topico_id = ?",
                (self.topico_id,),
            ).fetchall()
            self.assertEqual(len(revisoes), 1)
            self.assertEqual(int(revisoes[0][0]), 80)
            self.assertEqual(int(revisoes[0][1]), 64)
            proxima = con.execute(
                "SELECT proxima_revisao FROM controle_topico WHERE topico_id = ?",
                (self.topico_id,),
            ).fetchone()[0]
            self.assertGreater(str(proxima), date.today().isoformat())
            vinculadas = int(con.execute(
                "SELECT COUNT(*) FROM tentativas_questoes WHERE revisao_id IS NOT NULL",
            ).fetchone()[0])
            self.assertEqual(vinculadas, 80)

    def test_questao_pulada_continua_pendente(self):
        # Responde 39 e deixa uma da primeira metade sem resposta efetiva.
        ids = self.questoes[:39]
        self._resolver(ids)
        estado = banco.obter_estado_cobertura_revisao(self.topico_id, self.concurso_id)
        self.assertEqual(estado["cobertas"], 39)
        self.assertEqual(estado["restantes"], 41)

    def test_reabre_revisao_recente_reagendada_prematuramente(self):
        referencia = date.today().isoformat()
        ids = self.questoes[:40]
        # Simula o comportamento antigo: 40/80 registradas como revisão e
        # agenda empurrada para o futuro antes de completar a cobertura.
        sessao_id = banco.iniciar_sessao_questoes(
            self.concurso_id,
            "Revisão inteligente",
            40,
            origem="revisao_inteligente",
            contexto={"teste": "reabrir_parcial"},
            versao_motor="sessao_unificado_v1",
        )
        banco.registrar_fila_sessao_questoes(sessao_id, [{"id": qid} for qid in ids])
        for item in banco.obter_itens_sessao_questoes(sessao_id):
            qid = int(item["questao_id"])
            item_id = banco.marcar_item_sessao_apresentado(
                sessao_id, int(item["ordem"]), qid
            )
            banco.registrar_tentativa_questao(
                sessao_id, qid, self.concurso_id, "A", 10, item_sessao_id=item_id
            )
        banco.encerrar_sessao_questoes(sessao_id, concluida=True)
        salvo = banco.salvar_revisao_automatica_questoes(
            self.topico_id,
            referencia,
            40,
            40,
            "normal",
            proxima_revisao="2099-01-01",
            sessao_questoes_id=sessao_id,
            concurso_id=self.concurso_id,
        )
        self.assertIsNotNone(salvo["revisao_id"])

        reparo = banco.reabrir_revisoes_parciais_recentes(
            self.concurso_id, dias=2
        )
        self.assertEqual(reparo["reabertas"], 1)
        with closing(banco.conectar()) as con:
            self.assertEqual(
                con.execute(
                    "SELECT COUNT(*) FROM revisoes WHERE topico_id = ?",
                    (self.topico_id,),
                ).fetchone()[0],
                0,
            )
            proxima = con.execute(
                "SELECT proxima_revisao FROM controle_topico WHERE topico_id = ?",
                (self.topico_id,),
            ).fetchone()[0]
            self.assertEqual(proxima, referencia)
            self.assertEqual(
                con.execute(
                    "SELECT COUNT(*) FROM tentativas_questoes WHERE revisao_id IS NOT NULL"
                ).fetchone()[0],
                0,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
