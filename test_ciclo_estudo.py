"""Testes de integração do ciclo principal: sessão -> respostas -> revisão -> métricas."""

from __future__ import annotations

import gc
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from datetime import datetime, timedelta

import banco
from ciclo_estudo import integrar_sessao_questoes_com_revisoes
from auditoria_ciclo_estudo import auditar_ciclo_estudo
from inteligencia import montar_preparacao_foco
from statistics_core.periods import statistical_timezone


class CicloEstudoTests(unittest.TestCase):
    def setUp(self):
        self.original = banco.CAMINHO_BANCO
        self.temp = tempfile.TemporaryDirectory(prefix="vighna_ciclo_")
        banco.CAMINHO_BANCO = Path(self.temp.name) / "estudos.db"
        banco.criar_banco()

        concurso_id = banco.adicionar_concurso("Perfil Ciclo")
        self.assertIsNotNone(concurso_id)
        banco.definir_concurso_ativo(concurso_id)
        self.concurso_id = int(concurso_id)

        self.disciplina_id = int(banco.adicionar_disciplina("Disciplina Ciclo"))
        self.assertTrue(banco.adicionar_topico("Disciplina Ciclo", "Tópico Ciclo"))
        with closing(banco.conectar()) as con:
            self.topico_id = int(con.execute(
                "SELECT id FROM topicos WHERE disciplina_id = ? AND nome = ?",
                (self.disciplina_id, "Tópico Ciclo"),
            ).fetchone()[0])

        self.questoes = []
        for indice in range(10):
            qid = banco.criar_questao(
                self.topico_id,
                f"Questão de ciclo {indice + 1}?",
                [
                    {"letra": "A", "texto": "Correta", "correta": True},
                    {"letra": "B", "texto": "Distrator", "correta": False},
                    {"letra": "C", "texto": "Distrator 2", "correta": False},
                    {"letra": "D", "texto": "Distrator 3", "correta": False},
                ],
            )
            self.questoes.append(int(qid))

    def tearDown(self):
        banco.CAMINHO_BANCO = self.original
        gc.collect()
        self.temp.cleanup()

    def _resolver_bateria(self, quantidade=10, origem="algoritmo_v5", dia=None):
        fila = [{"id": qid} for qid in self.questoes[:quantidade]]
        sessao_id = banco.iniciar_sessao_questoes(
            self.concurso_id,
            "Treino inteligente • Motor V5",
            len(fila),
            origem=origem,
            contexto={"teste": "ciclo"},
            versao_motor="sessao_unificado_v1",
        )
        banco.registrar_fila_sessao_questoes(sessao_id, fila)
        itens = banco.obter_itens_sessao_questoes(sessao_id)
        for indice, item in enumerate(itens):
            item_id = banco.marcar_item_sessao_apresentado(
                sessao_id,
                int(item["ordem"]),
                int(item["questao_id"]),
            )
            banco.registrar_tentativa_questao(
                sessao_id,
                int(item["questao_id"]),
                self.concurso_id,
                alternativa_marcada="B" if indice in (2, 7) else "A",
                tempo_segundos=15,
                item_sessao_id=item_id,
            )
        if dia is None:
            dia = datetime.now(statistical_timezone()).date()
        carimbo = f"{dia.isoformat()} 12:00:00"
        with closing(banco.conectar()) as con:
            con.execute(
                "UPDATE tentativas_questoes SET respondida_em = ? WHERE sessao_id = ?",
                (carimbo, sessao_id),
            )
            con.commit()
        banco.encerrar_sessao_questoes(sessao_id, concluida=True)
        integracao = integrar_sessao_questoes_com_revisoes(sessao_id)
        return sessao_id, integracao

    def test_bateria_recomendada_fecha_ciclo_academico(self):
        sessao_id, integracao = self._resolver_bateria(10)
        self.assertEqual(len(integracao), 1)
        self.assertTrue(integracao[0]["revisao_registrada"])
        self.assertTrue(integracao[0]["agendamento_atualizado"])
        self.assertEqual(integracao[0]["confianca"], "normal")

        with closing(banco.conectar()) as con:
            revisao = con.execute(
                """
                SELECT id, concurso_id, questoes, acertos, sessao_questoes_id
                FROM revisoes WHERE topico_id = ? ORDER BY id DESC LIMIT 1
                """,
                (self.topico_id,),
            ).fetchone()
            self.assertIsNotNone(revisao)
            self.assertEqual(int(revisao[1]), self.concurso_id)
            self.assertEqual(int(revisao[2]), 10)
            self.assertEqual(int(revisao[3]), 8)
            self.assertEqual(int(revisao[4]), int(sessao_id))
            vinculadas = int(con.execute(
                "SELECT COUNT(*) FROM tentativas_questoes WHERE sessao_id = ? AND revisao_id = ?",
                (sessao_id, int(revisao[0])),
            ).fetchone()[0])
            self.assertEqual(vinculadas, 10)
            proxima = con.execute(
                "SELECT proxima_revisao FROM controle_topico WHERE topico_id = ?",
                (self.topico_id,),
            ).fetchone()[0]
            self.assertTrue(proxima)

        metricas = banco.obter_metricas_globais_nucleo(self.concurso_id)["metrics"]
        self.assertEqual(metricas["answered_attempt_count"]["value"], 10)
        self.assertEqual(metricas["correct_attempt_count"]["value"], 8)
        self.assertAlmostEqual(metricas["accuracy_rate"]["value"], 80.0)

        auditoria = auditar_ciclo_estudo(self.concurso_id)
        codigos_erro = {
            item["codigo"] for item in auditoria["findings"] if item["nivel"] == "erro"
        }
        self.assertEqual(codigos_erro, set())

    def test_bateria_curta_em_topico_conhecido_nao_forca_nova_revisao(self):
        hoje = datetime.now(statistical_timezone()).date()
        self._resolver_bateria(10, dia=hoje - timedelta(days=1))
        sessao_id, integracao = self._resolver_bateria(3, origem="topico", dia=hoje)
        self.assertEqual(len(integracao), 1)
        self.assertEqual(integracao[0]["status_integracao"], "atividade")
        with closing(banco.conectar()) as con:
            vinculadas = int(con.execute(
                "SELECT COUNT(*) FROM tentativas_questoes WHERE sessao_id = ? AND revisao_id IS NOT NULL",
                (sessao_id,),
            ).fetchone()[0])
        self.assertEqual(vinculadas, 0)
        auditoria = auditar_ciclo_estudo(self.concurso_id)
        self.assertFalse(any(
            item["codigo"] == "integracao_revisao_incompleta" and item["nivel"] == "erro"
            for item in auditoria["findings"]
        ))

    def test_preparacao_foco_preserva_origem_do_motor_v5(self):
        preparacao = montar_preparacao_foco({
            "versao_motor": 5,
            "minutos": 30,
            "atividade": "Questões",
            "questoes_alvo": 10,
            "disciplina": "Disciplina Ciclo",
            "topico_id": self.topico_id,
            "topico": "Tópico Ciclo",
            "origem_texto": "Estudar agora V5 • prioridade estratégica",
        })
        self.assertEqual(preparacao["origem_sessao"], "algoritmo_v5")
        self.assertTrue(preparacao["abrir_questoes_ao_iniciar"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
