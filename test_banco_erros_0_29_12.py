"""Testes funcionais do Banco de Erros do VighnaStudy 0.29.12."""

from __future__ import annotations

import ast
import gc
import shutil
import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import date
from pathlib import Path

import banco
from inteligencia import MotorRecomendacaoV5


ROOT = Path(__file__).resolve().parent


class TestBancoErros(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._origem_banco = banco.CAMINHO_BANCO
        cls._template_dir = tempfile.TemporaryDirectory(
            prefix="vighna_banco_erros_template_",
            ignore_cleanup_errors=True,
        )
        cls._template = Path(cls._template_dir.name) / "template.db"
        banco.CAMINHO_BANCO = cls._template
        banco.criar_banco()
        banco.CAMINHO_BANCO = cls._origem_banco

        cls.main_source = (ROOT / "main.py").read_text(encoding="utf-8")
        cls.banco_source = (ROOT / "banco.py").read_text(encoding="utf-8")
        ast.parse(cls.main_source)
        ast.parse(cls.banco_source)

    @classmethod
    def tearDownClass(cls):
        banco.CAMINHO_BANCO = cls._origem_banco
        gc.collect()
        cls._template_dir.cleanup()

    def setUp(self):
        self._temp = tempfile.TemporaryDirectory(
            prefix="vighna_banco_erros_teste_",
            ignore_cleanup_errors=True,
        )
        self.db = Path(self._temp.name) / "estudos.db"
        shutil.copy2(self._template, self.db)
        banco.CAMINHO_BANCO = self.db

        self.perfil = banco.adicionar_concurso("Perfil A")
        banco.definir_concurso_ativo(self.perfil)
        self.disciplina = banco.adicionar_disciplina("Disciplina A")
        banco.adicionar_topico("Disciplina A", "Tópico A")
        self.disciplina_b = banco.adicionar_disciplina("Disciplina B")
        banco.adicionar_topico("Disciplina B", "Tópico B")

        with banco.conectar() as conexao:
            self.topico = int(
                conexao.execute(
                    "SELECT id FROM topicos WHERE disciplina_id = ? AND nome = 'Tópico A'",
                    (self.disciplina,),
                ).fetchone()[0]
            )
            self.topico_b = int(
                conexao.execute(
                    "SELECT id FROM topicos WHERE disciplina_id = ? AND nome = 'Tópico B'",
                    (self.disciplina_b,),
                ).fetchone()[0]
            )

        self.q_multipla = banco.criar_questao(
            self.topico,
            "Questão de múltipla escolha",
            [
                {"letra": "A", "texto": "Correta", "correta": True},
                {"letra": "B", "texto": "Errada", "correta": False},
            ],
            explicacao="Explicação de teste.",
            tipo_questao="MULTIPLA_ESCOLHA",
        )
        self.q_certo_errado = banco.criar_questao(
            self.topico,
            "Questão de certo ou errado",
            [
                {"letra": "C", "texto": "Certo", "correta": True},
                {"letra": "E", "texto": "Errado", "correta": False},
            ],
            explicacao="Explicação C/E.",
            tipo_questao="CERTO_ERRADO",
        )
        self.q_disciplina_b = banco.criar_questao(
            self.topico_b,
            "Questão da segunda disciplina",
            [
                {"letra": "A", "texto": "Correta", "correta": True},
                {"letra": "B", "texto": "Errada", "correta": False},
            ],
        )

    def tearDown(self):
        banco.CAMINHO_BANCO = self._origem_banco
        gc.collect()
        self._temp.cleanup()

    def _contar(self, tabela):
        with banco.conectar() as conexao:
            return int(conexao.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0])

    def _responder(self, questao_id, correta, perfil=None, origem="manual"):
        perfil = int(perfil or self.perfil)
        questao = banco.obter_questao(questao_id)
        gabarito = next(
            item["letra"] for item in questao["alternativas"] if item["correta"]
        )
        if correta:
            marcada = gabarito
        else:
            marcada = next(
                item["letra"]
                for item in questao["alternativas"]
                if item["letra"] != gabarito
            )
        sessao = banco.iniciar_sessao_questoes(
            perfil,
            "Sessão acadêmica de teste",
            1,
            origem=origem,
        )
        banco.registrar_fila_sessao_questoes(sessao, [{"id": questao_id}])
        item = banco.marcar_item_sessao_apresentado(sessao, 1, questao_id)
        resultado = banco.registrar_tentativa_questao(
            sessao,
            questao_id,
            perfil,
            alternativa_marcada=marcada,
            item_sessao_id=item,
        )
        banco.encerrar_sessao_questoes(sessao, concluida=True)
        return resultado

    def _preparar_pendencia(self, questao_id=None):
        questao_id = int(questao_id or self.q_multipla)
        self._responder(questao_id, correta=False)
        self.assertEqual(banco.contar_banco_erros_pendentes(self.perfil), 1)
        return questao_id

    def _metricas_topico(self):
        dados = banco.obter_metricas_topico_nucleo(self.topico, self.perfil)
        return {
            chave: dados["metrics"].get(chave, {}).get("value")
            for chave in (
                "mastery_score",
                "evidence_level",
                "question_coverage_rate",
                "accuracy_rate",
                "answered_attempt_count",
            )
        }

    def test_01_erro_academico_cria_pendencia(self):
        self._responder(self.q_multipla, correta=False, origem="revisao_inteligente")
        itens = banco.listar_banco_erros_pendentes(self.perfil)
        self.assertEqual([item["id"] for item in itens], [self.q_multipla])

    def test_02_erro_repetido_nao_cria_duplicata(self):
        self._responder(self.q_multipla, correta=False)
        self._responder(self.q_multipla, correta=False, origem="simulado")
        self.assertEqual(banco.contar_banco_erros_pendentes(self.perfil), 1)

    def test_03_erro_sem_impacto_nao_cria_pendencia_adicional(self):
        self.assertIn("if self.sem_impacto_inteligencia:", self.main_source)
        self.assertIn("if self.modo_banco_erros:", self.main_source)
        self.assertIn("processar_resposta_banco_erros", self.main_source)
        self.assertNotIn(
            "registrar_tentativa_questao(\n                    self.sessao_id",
            self.main_source.split("if self.sem_impacto_inteligencia:", 1)[1].split("else:", 1)[0],
        )
        self.assertEqual(banco.contar_banco_erros_pendentes(self.perfil), 0)

    def test_04_acerto_no_banco_remove_pendencia(self):
        self._preparar_pendencia()
        resultado = banco.processar_resposta_banco_erros(
            self.perfil, self.q_multipla, True
        )
        self.assertTrue(resultado["removida"])
        self.assertEqual(banco.contar_banco_erros_pendentes(self.perfil), 0)

    def test_05_erro_no_banco_mantem_pendencia(self):
        self._preparar_pendencia()
        resultado = banco.processar_resposta_banco_erros(
            self.perfil, self.q_multipla, False
        )
        self.assertTrue(resultado["pendente"])
        self.assertEqual(banco.contar_banco_erros_pendentes(self.perfil), 1)

    def test_06_acerto_no_banco_nao_cria_tentativa(self):
        self._preparar_pendencia()
        antes = self._contar("tentativas_questoes")
        banco.processar_resposta_banco_erros(self.perfil, self.q_multipla, True)
        self.assertEqual(self._contar("tentativas_questoes"), antes)

    def test_07_erro_no_banco_nao_cria_tentativa(self):
        self._preparar_pendencia()
        antes = self._contar("tentativas_questoes")
        banco.processar_resposta_banco_erros(self.perfil, self.q_multipla, False)
        self.assertEqual(self._contar("tentativas_questoes"), antes)

    def test_08_banco_nao_altera_sessao_academica(self):
        self._preparar_pendencia()
        antes = self._contar("sessoes_questoes")
        banco.processar_resposta_banco_erros(self.perfil, self.q_multipla, True)
        self.assertEqual(self._contar("sessoes_questoes"), antes)

    def test_09_banco_nao_altera_revisao(self):
        self._preparar_pendencia()
        antes = self._contar("revisoes")
        banco.processar_resposta_banco_erros(self.perfil, self.q_multipla, True)
        self.assertEqual(self._contar("revisoes"), antes)

    def test_10_banco_nao_altera_proxima_revisao(self):
        banco.atualizar_proxima_revisao(self.topico, "2030-01-15")
        self._preparar_pendencia()
        antes = banco.obter_resumo_topico(self.topico)["proxima_revisao"]
        banco.processar_resposta_banco_erros(self.perfil, self.q_multipla, True)
        depois = banco.obter_resumo_topico(self.topico)["proxima_revisao"]
        self.assertEqual(depois, antes)

    def test_11_banco_nao_altera_dominio(self):
        self._preparar_pendencia()
        antes = banco.obter_indice_dominio_topico(self.topico, self.perfil)
        banco.processar_resposta_banco_erros(self.perfil, self.q_multipla, True)
        depois = banco.obter_indice_dominio_topico(self.topico, self.perfil)
        self.assertEqual(depois, antes)

    def test_12_banco_nao_altera_evidencia(self):
        self._preparar_pendencia()
        antes = self._metricas_topico()["evidence_level"]
        banco.processar_resposta_banco_erros(self.perfil, self.q_multipla, True)
        self.assertEqual(self._metricas_topico()["evidence_level"], antes)

    def test_13_banco_nao_altera_cobertura(self):
        self._preparar_pendencia()
        antes = self._metricas_topico()["question_coverage_rate"]
        banco.processar_resposta_banco_erros(self.perfil, self.q_multipla, True)
        self.assertEqual(self._metricas_topico()["question_coverage_rate"], antes)

    def test_14_banco_nao_altera_caderno_erros(self):
        self._preparar_pendencia()
        antes = banco.listar_caderno_erros_questoes(self.perfil)
        banco.processar_resposta_banco_erros(self.perfil, self.q_multipla, True)
        depois = banco.listar_caderno_erros_questoes(self.perfil)
        self.assertEqual(depois, antes)

    def test_15_banco_nao_altera_fila_v3(self):
        self._preparar_pendencia()
        antes = banco.obter_prioridades_sessao_adaptativa(self.perfil)
        banco.processar_resposta_banco_erros(self.perfil, self.q_multipla, True)
        depois = banco.obter_prioridades_sessao_adaptativa(self.perfil)
        self.assertEqual(depois, antes)

    def test_16_banco_nao_altera_motor_v5(self):
        self._preparar_pendencia()

        def montar():
            adaptativas = banco.obter_prioridades_sessao_adaptativa(self.perfil)
            return MotorRecomendacaoV5(
                fila=[],
                adaptativas=adaptativas,
                contexto={},
                hoje=date(2026, 9, 23),
                usar_calibracao=False,
                usar_historico_decisoes=False,
            ).montar()

        antes = montar()
        banco.processar_resposta_banco_erros(self.perfil, self.q_multipla, True)
        self.assertEqual(montar(), antes)

    def test_17_banco_nao_altera_xp(self):
        self._preparar_pendencia()
        antes = banco.obter_snapshot_gamificacao(self.perfil)
        eventos_antes = self._contar("gamificacao_eventos")
        banco.processar_resposta_banco_erros(self.perfil, self.q_multipla, True)
        depois = banco.obter_snapshot_gamificacao(self.perfil)
        self.assertEqual(depois["total_xp"], antes["total_xp"])
        self.assertEqual(depois["achievements_earned"], antes["achievements_earned"])
        self.assertEqual(self._contar("gamificacao_eventos"), eventos_antes)

    def test_18_respeita_perfil_ativo(self):
        perfil_b = banco.adicionar_concurso("Perfil B")
        with banco.conectar() as conexao:
            conexao.execute(
                "INSERT INTO disciplina_concurso_inclusao VALUES (?, ?, 1, 0)",
                (self.disciplina, perfil_b),
            )
            conexao.execute(
                "INSERT INTO topico_concurso_importancia VALUES (?, ?, 3, 1, 0)",
                (self.topico, perfil_b),
            )
        banco.adicionar_pendencia_banco_erros(self.perfil, self.q_multipla)
        banco.adicionar_pendencia_banco_erros(perfil_b, self.q_certo_errado)
        self.assertEqual(
            [item["id"] for item in banco.listar_banco_erros_pendentes(self.perfil)],
            [self.q_multipla],
        )
        self.assertEqual(
            [item["id"] for item in banco.listar_banco_erros_pendentes(perfil_b)],
            [self.q_certo_errado],
        )

    def test_19_nao_duplica_questao_por_perfil(self):
        banco.adicionar_pendencia_banco_erros(self.perfil, self.q_multipla)
        banco.adicionar_pendencia_banco_erros(self.perfil, self.q_multipla)
        with self.assertRaises(sqlite3.IntegrityError):
            with banco.conectar() as conexao:
                conexao.execute(
                    "INSERT INTO banco_erros_pendentes(concurso_id, questao_id) VALUES (?, ?)",
                    (self.perfil, self.q_multipla),
                )
        self.assertEqual(banco.contar_banco_erros_pendentes(self.perfil), 1)

    def test_20_filtro_por_disciplina(self):
        for questao in (self.q_multipla, self.q_disciplina_b):
            banco.adicionar_pendencia_banco_erros(self.perfil, questao)
        itens = banco.listar_banco_erros_pendentes(
            self.perfil, disciplina_id=self.disciplina_b
        )
        self.assertEqual([item["id"] for item in itens], [self.q_disciplina_b])

    def test_21_filtro_por_topico(self):
        for questao in (self.q_multipla, self.q_disciplina_b):
            banco.adicionar_pendencia_banco_erros(self.perfil, questao)
        itens = banco.listar_banco_erros_pendentes(
            self.perfil, topico_id=self.topico
        )
        self.assertEqual([item["id"] for item in itens], [self.q_multipla])

    def test_22_filtro_por_formato(self):
        for questao in (self.q_multipla, self.q_certo_errado):
            banco.adicionar_pendencia_banco_erros(self.perfil, questao)
        itens = banco.listar_banco_erros_pendentes(
            self.perfil, tipo_questao="CERTO_ERRADO"
        )
        self.assertEqual([item["id"] for item in itens], [self.q_certo_errado])

    def test_23_multipla_escolha_funciona(self):
        questao = banco.obter_questao(self.q_multipla)
        self.assertEqual(questao["tipo_questao"], "MULTIPLA_ESCOLHA")
        self.assertEqual(len(questao["alternativas"]), 2)
        banco.adicionar_pendencia_banco_erros(self.perfil, self.q_multipla)
        banco.processar_resposta_banco_erros(self.perfil, self.q_multipla, True)
        self.assertEqual(banco.contar_banco_erros_pendentes(self.perfil), 0)

    def test_24_certo_errado_funciona(self):
        questao = banco.obter_questao(self.q_certo_errado)
        self.assertEqual(questao["tipo_questao"], "CERTO_ERRADO")
        self.assertEqual([item["letra"] for item in questao["alternativas"]], ["C", "E"])
        banco.adicionar_pendencia_banco_erros(self.perfil, self.q_certo_errado)
        banco.processar_resposta_banco_erros(self.perfil, self.q_certo_errado, False)
        self.assertEqual(banco.contar_banco_erros_pendentes(self.perfil), 1)

    def test_25_questao_arquivada_nao_e_oferecida(self):
        banco.adicionar_pendencia_banco_erros(self.perfil, self.q_multipla)
        banco.arquivar_questao(self.q_multipla)
        self.assertEqual(banco.listar_banco_erros_pendentes(self.perfil), [])
        preservadas = banco.listar_banco_erros_pendentes(
            self.perfil, incluir_indisponiveis=True
        )
        self.assertEqual([item["id"] for item in preservadas], [self.q_multipla])

    def test_26_encerrar_preserva_nao_respondidas(self):
        for questao in (self.q_multipla, self.q_certo_errado):
            banco.adicionar_pendencia_banco_erros(self.perfil, questao)
        banco.processar_resposta_banco_erros(self.perfil, self.q_multipla, True)
        restantes = banco.listar_banco_erros_pendentes(self.perfil)
        self.assertEqual([item["id"] for item in restantes], [self.q_certo_errado])
        self.assertIn('"ainda_pendentes"', self.main_source)

    def test_27_backfill_nao_inclui_recuperadas(self):
        for _ in range(3):
            self._responder(self.q_multipla, correta=False)
        self._responder(self.q_certo_errado, correta=False)
        for _ in range(3):
            self._responder(self.q_certo_errado, correta=True)

        status = {
            item["questao_id"]: item["status"]
            for item in banco.listar_caderno_erros_questoes(self.perfil)
        }
        self.assertEqual(status[self.q_multipla], "Crítica")
        self.assertEqual(status[self.q_certo_errado], "Recuperada")

        with banco.conectar() as conexao:
            conexao.execute("DELETE FROM banco_erros_pendentes")
            conexao.execute(
                "DELETE FROM migracoes WHERE nome = 'banco_erros_pendentes_backfill_v1'"
            )
        banco.executar_backfill_banco_erros_pendentes()
        ids = {
            item["id"]
            for item in banco.listar_banco_erros_pendentes(self.perfil)
        }
        self.assertIn(self.q_multipla, ids)
        self.assertNotIn(self.q_certo_errado, ids)

    def test_28_migracao_idempotente(self):
        self._responder(self.q_multipla, correta=False)
        with banco.conectar() as conexao:
            conexao.execute("DELETE FROM banco_erros_pendentes")
            conexao.execute(
                "DELETE FROM migracoes WHERE nome = 'banco_erros_pendentes_backfill_v1'"
            )
        primeira = banco.executar_backfill_banco_erros_pendentes()
        quantidade = banco.contar_banco_erros_pendentes(self.perfil)
        segunda = banco.executar_backfill_banco_erros_pendentes()
        self.assertEqual(primeira, 1)
        self.assertEqual(segunda, 0)
        self.assertEqual(banco.contar_banco_erros_pendentes(self.perfil), quantidade)

    def test_29_novo_erro_academico_reinsere_apos_recuperacao_operacional(self):
        self._preparar_pendencia()
        banco.processar_resposta_banco_erros(self.perfil, self.q_multipla, True)
        self.assertEqual(banco.contar_banco_erros_pendentes(self.perfil), 0)
        self._responder(self.q_multipla, correta=False, origem="algoritmo_v5")
        self.assertEqual(banco.contar_banco_erros_pendentes(self.perfil), 1)

    def test_30_schema_e_interface_estao_integrados(self):
        self.assertIn("UNIQUE (concurso_id, questao_id)", self.banco_source)
        self.assertIn("class JanelaBancoErros", self.main_source)
        self.assertIn("BANCO DE ERROS • MODO SEM IMPACTO NA INTELIGÊNCIA", self.main_source)
        self.assertIn("Questão removida do Banco de Erros", self.main_source)
        self.assertIn("Questão permanece no Banco de Erros", self.main_source)

    def test_31_banco_temporario_permanece_integro(self):
        with closing(banco.conectar()) as conexao:
            self.assertEqual(
                conexao.execute("PRAGMA integrity_check").fetchone()[0],
                "ok",
            )
            self.assertEqual(
                conexao.execute("PRAGMA foreign_key_check").fetchall(),
                [],
            )

    def test_32_acerto_academico_posterior_remove_pendencia(self):
        self._preparar_pendencia()
        resultado = self._responder(
            self.q_multipla,
            correta=True,
            origem="revisao_inteligente",
        )
        self.assertTrue(resultado["correta"])
        self.assertEqual(banco.contar_banco_erros_pendentes(self.perfil), 0)

    def test_33_acerto_academico_remove_so_pendencia_do_mesmo_perfil(self):
        perfil_b = banco.adicionar_concurso("Perfil B para recuperação")
        with banco.conectar() as conexao:
            conexao.execute(
                "INSERT INTO disciplina_concurso_inclusao VALUES (?, ?, 1, 0)",
                (self.disciplina, perfil_b),
            )
            conexao.execute(
                "INSERT INTO topico_concurso_importancia VALUES (?, ?, 3, 1, 0)",
                (self.topico, perfil_b),
            )
        banco.adicionar_pendencia_banco_erros(self.perfil, self.q_multipla)
        banco.adicionar_pendencia_banco_erros(perfil_b, self.q_multipla)

        self._responder(
            self.q_multipla,
            correta=True,
            perfil=self.perfil,
            origem="revisao_inteligente",
        )

        self.assertEqual(banco.contar_banco_erros_pendentes(self.perfil), 0)
        self.assertEqual(banco.contar_banco_erros_pendentes(perfil_b), 1)

    def test_34_pulo_academico_nao_remove_pendencia(self):
        self._preparar_pendencia()
        sessao = banco.iniciar_sessao_questoes(
            self.perfil,
            "Sessão acadêmica com pulo",
            1,
            origem="revisao_inteligente",
        )
        banco.registrar_fila_sessao_questoes(sessao, [{"id": self.q_multipla}])
        item = banco.marcar_item_sessao_apresentado(sessao, 1, self.q_multipla)
        resultado = banco.registrar_tentativa_questao(
            sessao,
            self.q_multipla,
            self.perfil,
            alternativa_marcada=None,
            item_sessao_id=item,
        )
        banco.encerrar_sessao_questoes(sessao, concluida=True)
        self.assertTrue(resultado["pulada"])
        self.assertEqual(banco.contar_banco_erros_pendentes(self.perfil), 1)

    def test_35_novo_erro_academico_reinsere_apos_acerto_academico(self):
        self._preparar_pendencia()
        self._responder(
            self.q_multipla,
            correta=True,
            origem="revisao_inteligente",
        )
        self.assertEqual(banco.contar_banco_erros_pendentes(self.perfil), 0)
        self._responder(
            self.q_multipla,
            correta=False,
            origem="treino_adaptativo",
        )
        self.assertEqual(banco.contar_banco_erros_pendentes(self.perfil), 1)

    def test_36_acerto_academico_preserva_historico_de_tentativas(self):
        self._preparar_pendencia()
        antes = self._contar("tentativas_questoes")
        self._responder(
            self.q_multipla,
            correta=True,
            origem="revisao_inteligente",
        )
        self.assertEqual(self._contar("tentativas_questoes"), antes + 1)
        with banco.conectar() as conexao:
            resultados = [
                linha[0]
                for linha in conexao.execute(
                    """
                    SELECT correta
                    FROM tentativas_questoes
                    WHERE concurso_id = ?
                      AND COALESCE(questao_id_snapshot, questao_id) = ?
                    ORDER BY id
                    """,
                    (self.perfil, self.q_multipla),
                ).fetchall()
            ]
        self.assertEqual(resultados, [0, 1])
        self.assertEqual(banco.contar_banco_erros_pendentes(self.perfil), 0)

    def test_37_regra_de_limpeza_academica_esta_no_registrador_canonico(self):
        self.assertIn(
            "DELETE FROM banco_erros_pendentes",
            self.banco_source,
        )
        self.assertIn(
            "elif resultado == 1:",
            self.banco_source,
        )


if __name__ == "__main__":
    unittest.main()
