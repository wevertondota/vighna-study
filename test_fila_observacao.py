"""Testes do Passo 6: linhagem, telemetria e gate da fila sombra."""

from __future__ import annotations

import inspect
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

import banco
from fila_candidata import (
    CANDIDATE_MODE_ELIGIBLE,
    build_shadow_candidate,
    evidence_activation_policy,
)
from fila_observacao import evaluate_queue_activation_readiness
from inteligencia import MotorRecomendacaoV4, MotorRecomendacaoV5
from statistics_core import StatisticsService
from test_fila_candidata import active_item, official_metrics


def build_candidate(item, metrics, *, mode="exploratory"):
    return build_shadow_candidate(
        item,
        metrics,
        decline_moderate=10.0,
        decline_strong=20.0,
        candidate_mode=mode,
    )


def sufficient_summary(**updates):
    summary = {
        "observation_count": 20,
        "distinct_days": 5,
        "distinct_topics": 5,
        "moderate_high_item_observations": 10,
        "unexpected_top3_count": 0,
        "temporal_protection_violation_count": 0,
        "ineligible_topic_violation_count": 0,
        "known_context_without_lineage_count": 0,
        "fallback_component_count": 0,
        "fallbacks_by_type": {},
        "evidence_distribution": {"moderate": 10},
        "metric_version": "1",
    }
    summary.update(updates)
    return summary


class EvidencePolicyAndReadinessTests(unittest.TestCase):
    def test_policy_is_centralized_for_all_evidence_levels(self):
        expected = {
            "insufficient": False,
            "low": False,
            "moderate": True,
            "high": True,
        }
        for level, eligible in expected.items():
            with self.subTest(level=level):
                self.assertEqual(
                    evidence_activation_policy(level)["active_eligible"],
                    eligible,
                )

    def test_insufficient_uses_fallback_in_both_views(self):
        metrics = official_metrics(
            mastery=None,
            evidence="insufficient",
            evidence_order=0,
            error_control=None,
        )
        exploratory = build_candidate(active_item(), metrics)
        eligible = build_candidate(
            active_item(),
            metrics,
            mode=CANDIDATE_MODE_ELIGIBLE,
        )
        self.assertTrue(exploratory["component_details_candidate"]["dominio"]["fallback"])
        self.assertTrue(eligible["component_details_candidate"]["dominio"]["fallback"])

        contradictory = build_candidate(
            active_item(components={"dominio": 40.0}),
            official_metrics(
                mastery=90.0,
                evidence="insufficient",
                evidence_order=0,
            ),
        )
        self.assertEqual(contradictory["components_candidate"]["dominio"], 40.0)

    def test_low_is_exploratory_but_not_activation_eligible(self):
        item = active_item(components={"dominio": 40.0})
        metrics = official_metrics(mastery=80.0, evidence="low", evidence_order=1)
        exploratory = build_candidate(item, metrics)
        eligible = build_candidate(
            item,
            metrics,
            mode=CANDIDATE_MODE_ELIGIBLE,
        )
        self.assertEqual(exploratory["components_candidate"]["dominio"], 20.0)
        self.assertEqual(eligible["components_candidate"]["dominio"], 40.0)
        self.assertEqual(
            eligible["component_details_candidate"]["dominio"]["fallback"]["reason"],
            "official_mastery_low_evidence_not_activation_eligible",
        )
        self.assertFalse(exploratory["used_for_queue_order"])
        self.assertFalse(eligible["used_for_queue_order"])

    def test_moderate_and_high_are_activation_eligible(self):
        for level, order in (("moderate", 2), ("high", 3)):
            with self.subTest(level=level):
                result = build_candidate(
                    active_item(),
                    official_metrics(
                        mastery=80.0,
                        evidence=level,
                        evidence_order=order,
                    ),
                    mode=CANDIDATE_MODE_ELIGIBLE,
                )
                self.assertEqual(result["components_candidate"]["dominio"], 20.0)
                self.assertIsNone(
                    result["component_details_candidate"]["dominio"]["fallback"]
                )

    def test_gate_false_for_small_sample(self):
        gate = evaluate_queue_activation_readiness({})
        self.assertFalse(gate["ready"])
        self.assertEqual(
            gate["classification"],
            "INFRAESTRUTURA PRONTA / AMOSTRA AINDA INSUFICIENTE",
        )

    def test_gate_blocked_by_unexpected_top3_divergence(self):
        gate = evaluate_queue_activation_readiness(
            sufficient_summary(unexpected_top3_count=1)
        )
        self.assertFalse(gate["ready"])
        self.assertEqual(gate["classification"], "BLOQUEADORES TECNICOS RESTANTES")

    def test_gate_blocked_by_temporal_violation(self):
        gate = evaluate_queue_activation_readiness(
            sufficient_summary(temporal_protection_violation_count=1)
        )
        self.assertFalse(gate["ready"])
        self.assertTrue(
            any(item["code"] == "temporal_protection_violation" for item in gate["blockers"])
        )

    def test_gate_blocked_by_review_lineage_mismatch(self):
        gate = evaluate_queue_activation_readiness(
            sufficient_summary(review_lineage_mismatch_count=1)
        )
        self.assertFalse(gate["ready"])
        self.assertFalse(gate["review_lineage_integrity"])

    def test_gate_ready_in_sufficient_fixture(self):
        gate = evaluate_queue_activation_readiness(sufficient_summary())
        self.assertTrue(gate["ready"])
        self.assertEqual(
            gate["classification"],
            "PRONTO PARA PROPOR MIGRACAO CONTROLADA",
        )
        self.assertFalse(gate["used_for_queue_order"])

    def test_v4_v5_still_do_not_consume_candidate(self):
        source = inspect.getsource(MotorRecomendacaoV4) + inspect.getsource(MotorRecomendacaoV5)
        self.assertNotIn("score_candidate", source)
        self.assertNotIn("candidate_position", source)
        self.assertNotIn("eligible_candidate_score", source)


class Step6DatabaseTests(unittest.TestCase):
    def setUp(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
            self.db_path = Path(handle.name)
        self.original_path = banco.CAMINHO_BANCO
        self.original_connect = banco.conectar
        self.connections = []
        banco.CAMINHO_BANCO = self.db_path

        def tracked_connect():
            connection = self.original_connect()
            self.connections.append(connection)
            return connection

        banco.conectar = tracked_connect
        banco.criar_banco()
        self.contest_a = int(banco.obter_concurso_ativo()[0])
        with closing(banco.conectar()) as connection:
            self.contest_b = int(connection.execute(
                "INSERT INTO concursos (nome, e_padrao) VALUES ('Concurso B', 0)"
            ).lastrowid)
            self.subject_id = int(connection.execute(
                "INSERT INTO disciplinas (nome) VALUES ('Disciplina Step6')"
            ).lastrowid)
            self.topic_id = int(connection.execute(
                "INSERT INTO topicos (disciplina_id, nome) VALUES (?, 'Topico Step6')",
                (self.subject_id,),
            ).lastrowid)
            connection.execute(
                "INSERT INTO controle_topico (topico_id) VALUES (?)",
                (self.topic_id,),
            )
            for contest_id in (self.contest_a, self.contest_b):
                connection.execute(
                    """
                    INSERT INTO disciplina_concurso_inclusao
                    (disciplina_id, concurso_id, incluido, pausado)
                    VALUES (?, ?, 1, 0)
                    """,
                    (self.subject_id, contest_id),
                )
                connection.execute(
                    """
                    INSERT INTO topico_concurso_importancia
                    (topico_id, concurso_id, importancia, incluido, pausado)
                    VALUES (?, ?, 3, 1, 0)
                    """,
                    (self.topic_id, contest_id),
                )
            connection.execute(
                """
                INSERT INTO questoes (topico_id, enunciado, ativa, excluida)
                VALUES (?, 'Questao Step6', 1, 0)
                """,
                (self.topic_id,),
            )
            connection.commit()

    def tearDown(self):
        banco.conectar = self.original_connect
        banco.CAMINHO_BANCO = self.original_path
        for connection in self.connections:
            try:
                connection.close()
            except sqlite3.Error:
                pass
        for suffix in ("", "-wal", "-shm"):
            Path(f"{self.db_path}{suffix}").unlink(missing_ok=True)

    def review_row(self, review_id):
        with closing(banco.conectar()) as connection:
            return connection.execute(
                "SELECT concurso_id, origem, sessao_questoes_id FROM revisoes WHERE id = ?",
                (int(review_id),),
            ).fetchone()

    def create_question_session(self, contest_id):
        with closing(banco.conectar()) as connection:
            session_id = int(connection.execute(
                """
                INSERT INTO sessoes_questoes
                (concurso_id, iniciado_em, modo, objetivo, concluida)
                VALUES (?, '2026-09-18 10:00:00', 'Teste', 1, 1)
                """,
                (int(contest_id),),
            ).lastrowid)
            connection.commit()
        return session_id

    def test_new_database_has_logical_fk_and_lineage_index(self):
        with closing(banco.conectar()) as connection:
            foreign_keys = connection.execute(
                "PRAGMA foreign_key_list(revisoes)"
            ).fetchall()
            indexes = {
                row[1] for row in connection.execute("PRAGMA index_list(revisoes)")
            }
        self.assertTrue(any(row[2] == "concursos" and row[3] == "concurso_id" for row in foreign_keys))
        self.assertIn("idx_revisoes_concurso_topico_data", indexes)

    def test_legacy_database_migration_is_additive_idempotent_and_preserves_null(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
            legacy_path = Path(handle.name)
        connection = sqlite3.connect(legacy_path)
        connection.executescript(
            """
            CREATE TABLE disciplinas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE
            );
            CREATE TABLE topicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disciplina_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                UNIQUE (disciplina_id, nome)
            );
            CREATE TABLE revisoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topico_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                questoes INTEGER NOT NULL,
                acertos INTEGER NOT NULL,
                observacao TEXT,
                texto_erros TEXT,
                continuacao TEXT
            );
            INSERT INTO disciplinas(nome) VALUES ('Legada');
            INSERT INTO topicos(disciplina_id, nome) VALUES (1, 'Topico legado');
            INSERT INTO revisoes(topico_id, data, questoes, acertos)
            VALUES (1, '2025-01-01', 10, 7);
            """
        )
        connection.commit()
        connection.close()
        current_path = banco.CAMINHO_BANCO
        try:
            banco.CAMINHO_BANCO = legacy_path
            banco.criar_banco()
            banco.criar_banco()
            with closing(banco.conectar()) as migrated:
                columns = {
                    row[1] for row in migrated.execute("PRAGMA table_info(revisoes)")
                }
                row = migrated.execute(
                    "SELECT concurso_id, data, questoes, acertos FROM revisoes WHERE id = 1"
                ).fetchone()
                baseline_id = migrated.execute(
                    """
                    SELECT valor FROM configuracoes
                    WHERE chave = 'revisoes_linhagem_base_max_id'
                    """
                ).fetchone()[0]
                integrity = migrated.execute("PRAGMA integrity_check").fetchone()[0]
            self.assertIn("concurso_id", columns)
            self.assertEqual(row, (None, "2025-01-01", 10, 7))
            self.assertEqual(baseline_id, "1")
            self.assertEqual(integrity, "ok")
        finally:
            banco.CAMINHO_BANCO = current_path
            for connection in self.connections:
                try:
                    connection.close()
                except sqlite3.Error:
                    pass
            for suffix in ("", "-wal", "-shm"):
                Path(f"{legacy_path}{suffix}").unlink(missing_ok=True)

    def test_manual_review_known_contest_records_lineage(self):
        review_id = banco.registrar_revisao(
            self.topic_id,
            "2026-09-17",
            10,
            8,
            concurso_id=self.contest_a,
        )
        self.assertEqual(self.review_row(review_id)[0], self.contest_a)

    def test_review_without_unambiguous_context_remains_null(self):
        review_id = banco.registrar_revisao(
            self.topic_id,
            "2026-09-17",
            10,
            8,
        )
        self.assertIsNone(self.review_row(review_id)[0])

    def test_automatic_review_resolves_contest_from_session(self):
        session_id = self.create_question_session(self.contest_a)
        result = banco.salvar_revisao_automatica_questoes(
            self.topic_id,
            "2026-09-17",
            10,
            8,
            "normal",
            sessao_questoes_id=session_id,
        )
        self.assertEqual(result["concurso_id"], self.contest_a)
        self.assertEqual(self.review_row(result["revisao_id"])[0], self.contest_a)

    def test_consolidation_never_swaps_contest(self):
        first = banco.salvar_revisao_automatica_questoes(
            self.topic_id,
            "2026-09-17",
            10,
            8,
            "normal",
            concurso_id=self.contest_a,
        )
        second = banco.salvar_revisao_automatica_questoes(
            self.topic_id,
            "2026-09-17",
            12,
            9,
            "normal",
            concurso_id=self.contest_b,
        )
        self.assertNotEqual(first["revisao_id"], second["revisao_id"])
        self.assertEqual(self.review_row(first["revisao_id"])[0], self.contest_a)
        self.assertEqual(self.review_row(second["revisao_id"])[0], self.contest_b)

    def test_mixed_history_isolated_by_contest_and_null_stays_limited(self):
        banco.registrar_revisao(
            self.topic_id, "2026-09-15", 10, 7, concurso_id=None
        )
        banco.registrar_revisao(
            self.topic_id, "2026-09-16", 10, 8, concurso_id=self.contest_a
        )
        banco.registrar_revisao(
            self.topic_id, "2026-09-17", 10, 9, concurso_id=self.contest_b
        )
        service = StatisticsService(banco.conectar)
        metrics_a = service.get_topic_metrics(self.topic_id, self.contest_a)
        metrics_b = service.get_topic_metrics(self.topic_id, self.contest_b)
        review_a = metrics_a.metric("completed_review_count")
        review_b = metrics_b.metric("completed_review_count")
        self.assertEqual(review_a.value, 1)
        self.assertEqual(review_b.value, 1)
        self.assertEqual(review_a.state, "legacy_limited")
        self.assertEqual(review_b.state, "legacy_limited")
        self.assertEqual(review_a.parameters["unattributed_review_count"], 1)

    def test_telemetry_persists_relational_rows_and_deduplicates(self):
        snapshot = banco.obter_snapshot_paridade_fila(self.contest_a)
        first = banco.registrar_observacao_fila_sombra(
            "manual_audit",
            concurso_id=self.contest_a,
            snapshot=snapshot,
        )
        second = banco.registrar_observacao_fila_sombra(
            "manual_audit",
            concurso_id=self.contest_a,
            snapshot=snapshot,
        )
        self.assertTrue(first["gravada"])
        self.assertTrue(second["deduplicada"])
        with closing(banco.conectar()) as connection:
            executions = connection.execute(
                "SELECT COUNT(*), MAX(used_for_queue_order) FROM fila_shadow_execucoes"
            ).fetchone()
            items = connection.execute(
                "SELECT COUNT(*), MAX(used_for_queue_order) FROM fila_shadow_itens"
            ).fetchone()
        self.assertEqual(executions, (1, 0))
        self.assertEqual(items, (1, 0))

    def test_telemetry_does_not_change_academic_tables_or_metrics(self):
        academic_tables = (
            "revisoes",
            "tentativas_questoes",
            "sessoes_questoes",
            "controle_topico",
        )
        with closing(banco.conectar()) as connection:
            before = {
                table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in academic_tables
            }
        metrics_before = StatisticsService(banco.conectar).get_topic_metrics(
            self.topic_id,
            self.contest_a,
        )
        banco.registrar_observacao_fila_sombra(
            "manual_audit",
            concurso_id=self.contest_a,
        )
        with closing(banco.conectar()) as connection:
            after = {
                table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in academic_tables
            }
        metrics_after = StatisticsService(banco.conectar).get_topic_metrics(
            self.topic_id,
            self.contest_a,
        )
        self.assertEqual(before, after)
        for metric_id in ("mastery_score", "completed_review_count", "question_coverage_rate"):
            self.assertEqual(
                metrics_before.metric(metric_id).value,
                metrics_after.metric(metric_id).value,
            )

    def test_persistence_failure_never_changes_v3(self):
        before = banco.obter_prioridades_sessao_adaptativa(self.contest_a)
        original = banco.registrar_observacao_fila_sombra

        def fail(*_args, **_kwargs):
            raise sqlite3.OperationalError("falha simulada")

        banco.registrar_observacao_fila_sombra = fail
        try:
            with self.assertLogs(banco.LOGGER, level="ERROR"):
                result = banco.registrar_observacao_fila_sombra_segura(
                    "manual_audit",
                    concurso_id=self.contest_a,
                )
        finally:
            banco.registrar_observacao_fila_sombra = original
        after = banco.obter_prioridades_sessao_adaptativa(self.contest_a)
        self.assertFalse(result["gravada"])
        self.assertEqual(
            [item["topico_id"] for item in before],
            [item["topico_id"] for item in after],
        )

    def test_realistic_summary_exposes_gate_and_lineage(self):
        banco.registrar_observacao_fila_sombra(
            "manual_audit",
            concurso_id=self.contest_a,
        )
        summary = banco.obter_sumario_observacao_fila_sombra(self.contest_a)
        self.assertEqual(summary["observation_count"], 1)
        self.assertFalse(summary["readiness_gate"]["ready"])
        self.assertEqual(
            summary["readiness_gate"]["classification"],
            "INFRAESTRUTURA PRONTA / AMOSTRA AINDA INSUFICIENTE",
        )
        self.assertFalse(summary["used_for_queue_order"])


if __name__ == "__main__":
    unittest.main()
