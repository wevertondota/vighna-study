"""Testes da Fila Candidata do Passo 5, exclusivamente em modo sombra."""

from __future__ import annotations

import copy
import inspect
import sqlite3
import tempfile
import time
import unittest
from contextlib import closing
from pathlib import Path

import banco
from fila_candidata import (
    ACTIVE_QUEUE_VERSION,
    SHADOW_QUEUE_VERSION,
    build_shadow_candidate,
    compare_shadow_queue,
)
from inteligencia import MotorRecomendacaoV4, MotorRecomendacaoV5
from statistics_core.models import MetricResult, ScopeMetrics

WEIGHTS = {
    "atraso": 18.0,
    "dominio": 18.0,
    "erros_recentes": 15.0,
    "queda": 12.0,
    "importancia": 12.0,
    "cobertura": 9.0,
    "revisoes": 7.0,
    "espacamento": 9.0,
}


def metric(metric_id, value, *, state="ok", parameters=None, warnings=()):
    return MetricResult(
        metric_id=metric_id,
        value=value,
        state=state,
        scope={"kind": "topic", "topic_id": 1, "contest_id": 1},
        calculated_at="2026-09-18T12:00:00-03:00",
        metric_version="1",
        parameters=dict(parameters or {}),
        warnings=tuple(warnings),
    )


def official_metrics(
    *,
    mastery=60.0,
    evidence="high",
    evidence_order=3,
    coverage=70.0,
    trend_delta=0.0,
    trend_state="ok",
    reviews=2,
    review_state="ok",
    error_control=80.0,
    critical=0,
    recurring=0,
    recovering=0,
    recovered=0,
):
    error_parameters = {}
    if error_control is not None:
        error_parameters["error_control"] = {
            "score": error_control,
            "critical": critical,
            "recurring": recurring,
            "recovering": recovering,
            "recovered": recovered,
        }
    return ScopeMetrics(
        scope={"kind": "topic", "topic_id": 1, "contest_id": 1},
        period_id="all_time",
        metrics={
            "mastery_score": metric(
                "mastery_score",
                mastery,
                state="ok" if mastery is not None else "insufficient_data",
                parameters=error_parameters,
            ),
            "evidence_level": metric(
                "evidence_level",
                evidence,
                parameters={"order": evidence_order},
            ),
            "question_coverage_rate": metric(
                "question_coverage_rate",
                coverage,
                state="ok" if coverage is not None else "insufficient_data",
            ),
            "performance_trend": metric(
                "performance_trend",
                "stable" if trend_delta == 0 else "changing",
                state=trend_state,
                parameters={"trend_delta_pp": trend_delta}
                if trend_delta is not None
                else {},
            ),
            "completed_review_count": metric(
                "completed_review_count",
                reviews,
                state=review_state,
            ),
            "recent_performance_rate": metric(
                "recent_performance_rate",
                mastery,
                state="ok" if mastery is not None else "insufficient_data",
            ),
            "critical_open_error_count": metric(
                "critical_open_error_count",
                critical,
            ),
        },
    )


def active_item(
    topic_id=1,
    *,
    name=None,
    subject="Disciplina",
    importance=3,
    reviews=2,
    components=None,
):
    values = {
        "atraso": 0.0,
        "dominio": 40.0,
        "erros_recentes": 20.0,
        "queda": 0.0,
        "importancia": (importance - 1) * 25.0,
        "cobertura": 30.0,
        "revisoes": 58.0,
        "espacamento": 50.0,
    }
    values.update(components or {})
    contributions = {
        key: values[key] * WEIGHTS[key] / 100.0
        for key in WEIGHTS
    }
    principal = max(
        contributions,
        key=lambda key: (contributions[key], WEIGHTS[key]),
    )
    return {
        "topico_id": int(topic_id),
        "disciplina": subject,
        "topico": name or f"Topico {topic_id:02d}",
        "importancia": int(importance),
        "revisoes_totais": int(reviews),
        "dominio": 100.0 - values["dominio"],
        "versao_fila": ACTIVE_QUEUE_VERSION,
        "score_fila": round(sum(contributions.values()), 1),
        "motivo_fila": principal,
        "motivo_fila_chave": principal,
        "componentes_fila": values,
        "contribuicoes_fila": contributions,
        "pesos_fila": dict(WEIGHTS),
    }


def candidate(item, metrics):
    return build_shadow_candidate(
        item,
        metrics,
        decline_moderate=10.0,
        decline_strong=20.0,
    )


class ShadowCandidateFixtureTests(unittest.TestCase):
    def test_exact_parity_when_semantics_match(self):
        active = active_item()
        result = candidate(active, official_metrics())
        self.assertEqual(result["components_candidate"], active["componentes_fila"])
        self.assertEqual(result["score_candidate"], active["score_fila"])
        self.assertEqual(result["fallbacks"], [])
        self.assertFalse(result["used_for_queue_order"])
        self.assertEqual(result["weights_candidate"], WEIGHTS)

    def test_fixtures_a_to_f_evidence_and_mastery(self):
        insufficient = official_metrics(
            mastery=None,
            evidence="insufficient",
            evidence_order=0,
            error_control=None,
        )
        for label, legacy_component in (
            ("A_never_studied", 55.0),
            ("B_single_correct", 20.0),
            ("C_single_wrong", 85.0),
            ("D_insufficient_with_100_percent", 10.0),
        ):
            with self.subTest(label=label):
                result = candidate(
                    active_item(components={"dominio": legacy_component}),
                    insufficient,
                )
                self.assertEqual(
                    result["components_candidate"]["dominio"],
                    legacy_component,
                )
                self.assertNotEqual(
                    result["components_candidate"]["dominio"],
                    100.0,
                    "mastery=None nao pode ser convertido em dominio zero",
                )
                fallback = result["component_details_candidate"]["dominio"]["fallback"]
                self.assertEqual(
                    fallback["reason"],
                    "official_mastery_insufficient_evidence",
                )

        low = candidate(active_item(), official_metrics(mastery=30.0, evidence="high"))
        high = candidate(active_item(), official_metrics(mastery=90.0, evidence="high"))
        self.assertEqual(low["components_candidate"]["dominio"], 70.0)
        self.assertEqual(high["components_candidate"]["dominio"], 10.0)

    def test_fixture_low_evidence_is_explicitly_provisional(self):
        result = candidate(
            active_item(),
            official_metrics(mastery=70.0, evidence="low", evidence_order=1),
        )
        self.assertEqual(result["evidence_level"], "low")
        self.assertIn("provisional_mastery_low_evidence", result["warnings"])

    def test_fixtures_g_to_j_preserve_operational_timing(self):
        for label, atraso, espacamento in (
            ("G_overdue", 100.0, 100.0),
            ("H_due_today", 70.0, 90.0),
            ("I_future", 0.0, 25.0),
            ("J_without_next_review", 40.0, 50.0),
        ):
            with self.subTest(label=label):
                active = active_item(
                    components={"atraso": atraso, "espacamento": espacamento},
                )
                result = candidate(active, official_metrics())
                self.assertEqual(result["components_candidate"]["atraso"], atraso)
                self.assertEqual(
                    result["components_candidate"]["espacamento"],
                    espacamento,
                )
                self.assertEqual(
                    result["component_details_candidate"]["atraso"]["source"],
                    "operational_schedule_v3",
                )

    def test_fixtures_k_to_l_preserve_user_importance(self):
        for importance, expected in ((5, 100.0), (1, 0.0)):
            with self.subTest(importance=importance):
                result = candidate(
                    active_item(importance=importance),
                    official_metrics(),
                )
                self.assertEqual(
                    result["components_candidate"]["importancia"],
                    expected,
                )
                self.assertEqual(
                    result["component_details_candidate"]["importancia"]["source"],
                    "user_importance_configuration",
                )

    def test_fixtures_m_to_o_official_trend(self):
        decline = candidate(active_item(), official_metrics(trend_delta=-20.0))
        improve = candidate(active_item(), official_metrics(trend_delta=20.0))
        stable = candidate(active_item(), official_metrics(trend_delta=0.0))
        self.assertEqual(decline["components_candidate"]["queda"], 100.0)
        self.assertEqual(improve["components_candidate"]["queda"], 0.0)
        self.assertEqual(stable["components_candidate"]["queda"], 0.0)

    def test_fixtures_p_to_q_error_states(self):
        critical = candidate(
            active_item(),
            official_metrics(error_control=80.0, critical=2),
        )
        recovered = candidate(
            active_item(),
            official_metrics(error_control=100.0, recovered=1),
        )
        self.assertEqual(critical["components_candidate"]["erros_recentes"], 90.0)
        self.assertEqual(recovered["components_candidate"]["erros_recentes"], 0.0)

    def test_fixtures_r_to_s_coverage(self):
        low = candidate(active_item(), official_metrics(coverage=5.0))
        high = candidate(active_item(), official_metrics(coverage=90.0))
        self.assertEqual(low["components_candidate"]["cobertura"], 95.0)
        self.assertEqual(high["components_candidate"]["cobertura"], 10.0)

    def test_fixture_t_many_reviews(self):
        result = candidate(
            active_item(reviews=8, components={"revisoes": 12.0}),
            official_metrics(reviews=8),
        )
        self.assertEqual(result["components_candidate"]["revisoes"], 12.0)
        self.assertIsNone(result["component_details_candidate"]["revisoes"]["fallback"])

    def test_fixture_u_legacy_limited_review(self):
        result = candidate(
            active_item(reviews=2, components={"revisoes": 58.0}),
            official_metrics(reviews=0, review_state="legacy_limited"),
        )
        detail = result["component_details_candidate"]["revisoes"]
        self.assertEqual(detail["normalized_score"], 58.0)
        self.assertEqual(detail["source"], "fallback.fila_inteligente_v3.legacy_review_count")
        self.assertEqual(detail["fallback"]["reason"], "review_lineage_legacy_limited")

    def test_valid_zero_is_not_treated_as_absence(self):
        result = candidate(
            active_item(reviews=0, components={"revisoes": 100.0}),
            official_metrics(mastery=0.0, coverage=0.0, reviews=0),
        )
        self.assertEqual(result["components_candidate"]["dominio"], 100.0)
        self.assertEqual(result["components_candidate"]["cobertura"], 100.0)
        self.assertEqual(result["components_candidate"]["revisoes"], 100.0)
        self.assertIsNone(result["component_details_candidate"]["revisoes"]["fallback"])

    def test_fixture_v_tie_break_is_stable(self):
        beta = active_item(2, name="Beta")
        alpha = active_item(1, name="Alpha")
        comparison = compare_shadow_queue(
            [beta, alpha],
            {1: official_metrics(), 2: official_metrics()},
            decline_moderate=10.0,
            decline_strong=20.0,
        )
        self.assertEqual(comparison["candidate_order"], [1, 2])

    def test_interactions_and_temporal_protection(self):
        scenarios = {
            "high_mastery_overdue": candidate(
                active_item(components={"atraso": 100.0, "espacamento": 100.0}),
                official_metrics(mastery=95.0),
            ),
            "low_mastery_future": candidate(
                active_item(components={"atraso": 0.0, "espacamento": 20.0}),
                official_metrics(mastery=20.0),
            ),
            "insufficient_high_importance": candidate(
                active_item(importance=5),
                official_metrics(mastery=None, evidence="insufficient", error_control=None),
            ),
            "decline_high_coverage": candidate(
                active_item(),
                official_metrics(trend_delta=-20.0, coverage=95.0),
            ),
            "critical_due_today": candidate(
                active_item(components={"atraso": 70.0, "espacamento": 90.0}),
                official_metrics(critical=2),
            ),
            "new_high_importance": candidate(
                active_item(importance=5),
                official_metrics(mastery=None, evidence="insufficient", error_control=None),
            ),
            "low_mastery_high_evidence_low_importance": candidate(
                active_item(importance=1),
                official_metrics(mastery=20.0, evidence="high"),
            ),
        }
        self.assertEqual(
            scenarios["high_mastery_overdue"]["components_candidate"]["atraso"],
            100.0,
        )
        self.assertEqual(
            scenarios["critical_due_today"]["components_candidate"]["atraso"],
            70.0,
        )
        self.assertEqual(
            scenarios["low_mastery_future"]["components_candidate"]["dominio"],
            80.0,
        )
        self.assertEqual(
            scenarios["insufficient_high_importance"]["components_candidate"]["importancia"],
            100.0,
        )
        self.assertEqual(
            scenarios["decline_high_coverage"]["components_candidate"]["queda"],
            100.0,
        )
        self.assertEqual(
            scenarios["low_mastery_high_evidence_low_importance"]["components_candidate"]["importancia"],
            0.0,
        )

    def test_comparison_reports_order_top_n_and_deltas(self):
        active = [active_item(index) for index in range(1, 11)]
        metrics = {
            index: official_metrics(mastery=float(index * 9), coverage=float(index * 8))
            for index in range(1, 11)
        }
        comparison = compare_shadow_queue(
            active,
            metrics,
            decline_moderate=10.0,
            decline_strong=20.0,
        )
        summary = comparison["summary"]
        self.assertEqual(summary["topics_evaluated"], 10)
        for key in ("top_1", "top_3", "top_5", "top_10"):
            self.assertIn("intersection_rate", summary[key])
        self.assertIn("mean_absolute_position_delta", summary)
        self.assertIsNotNone(summary["largest_rise"])
        self.assertIsNotNone(summary["largest_fall"])
        self.assertTrue(all(not item["used_for_queue_order"] for item in comparison["comparisons"]))

    def test_candidate_never_changes_active_order_or_input(self):
        active = [
            active_item(2, components={"atraso": 100.0}),
            active_item(1, components={"atraso": 0.0}),
        ]
        before = copy.deepcopy(active)
        comparison = compare_shadow_queue(
            active,
            {1: official_metrics(mastery=0.0), 2: official_metrics(mastery=100.0)},
            decline_moderate=10.0,
            decline_strong=20.0,
        )
        self.assertEqual(active, before)
        self.assertEqual(comparison["active_order"], [2, 1])
        self.assertFalse(comparison["used_for_queue_order"])

    def test_explainability_has_raw_normalized_weight_source_and_fallback(self):
        result = candidate(
            active_item(),
            official_metrics(mastery=None, evidence="insufficient", error_control=None),
        )
        for detail in result["component_details_candidate"].values():
            self.assertTrue(
                {"raw_value", "normalized_score", "weight", "contribution", "source", "fallback"}
                <= set(detail)
            )

    def test_v4_v5_have_no_shadow_field_consumer(self):
        source = inspect.getsource(MotorRecomendacaoV4) + inspect.getsource(MotorRecomendacaoV5)
        self.assertNotIn("comparacao_fila_sombra", source)
        self.assertNotIn("score_candidate", source)

    def test_pure_comparison_performance_fixture(self):
        active = [active_item(index) for index in range(1, 101)]
        metrics = {index: official_metrics() for index in range(1, 101)}
        started = time.perf_counter()
        result = compare_shadow_queue(
            active,
            metrics,
            decline_moderate=10.0,
            decline_strong=20.0,
        )
        elapsed = time.perf_counter() - started
        self.assertEqual(result["summary"]["topics_evaluated"], 100)
        self.assertLess(elapsed, 2.0)


class ShadowQueueDatabaseIntegrationTests(unittest.TestCase):
    def setUp(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
            self.db_path = Path(handle.name)
        self.original_path = banco.CAMINHO_BANCO
        self.original_connect = banco.conectar
        banco.CAMINHO_BANCO = self.db_path
        self.connections = []

        def tracked_connect():
            connection = self.original_connect()
            self.connections.append(connection)
            return connection

        banco.conectar = tracked_connect
        banco.criar_banco()
        self.contest_id = int(banco.obter_concurso_ativo()[0])
        with closing(banco.conectar()) as connection:
            subject_id = connection.execute(
                "INSERT INTO disciplinas (nome) VALUES ('Disciplina Fixture')"
            ).lastrowid
            connection.execute(
                """
                INSERT INTO disciplina_concurso_inclusao
                (disciplina_id, concurso_id, incluido, pausado)
                VALUES (?, ?, 1, 0)
                """,
                (subject_id, self.contest_id),
            )
            self.topic_ids = []
            for index in range(1, 7):
                topic_id = connection.execute(
                    "INSERT INTO topicos (disciplina_id, nome) VALUES (?, ?)",
                    (subject_id, f"Topico Fixture {index}"),
                ).lastrowid
                self.topic_ids.append(int(topic_id))
                paused = 1 if index == 5 else 0
                connection.execute(
                    """
                    INSERT INTO topico_concurso_importancia
                    (topico_id, concurso_id, importancia, incluido, pausado)
                    VALUES (?, ?, 3, 1, ?)
                    """,
                    (topic_id, self.contest_id, paused),
                )
                connection.execute(
                    "INSERT INTO controle_topico (topico_id) VALUES (?)",
                    (topic_id,),
                )
                if index != 6:
                    connection.execute(
                        """
                        INSERT INTO questoes (topico_id, enunciado, ativa, excluida)
                        VALUES (?, ?, 1, 0)
                        """,
                        (topic_id, f"Questao Fixture {index}"),
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

    def table_counts(self):
        with closing(banco.conectar()) as connection:
            tables = [
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            ]
            return {
                table: int(connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])
                for table in tables
            }

    def test_w_paused_and_x_without_active_questions_are_ineligible(self):
        queue = banco.obter_prioridades_sessao_adaptativa(self.contest_id)
        ids = [int(item["topico_id"]) for item in queue]
        self.assertEqual(ids, self.topic_ids[:4])
        self.assertNotIn(self.topic_ids[4], ids)
        self.assertNotIn(self.topic_ids[5], ids)

    def test_active_v3_order_and_fields_remain_authoritative(self):
        queue = banco.obter_prioridades_sessao_adaptativa(self.contest_id)
        expected = sorted(
            queue,
            key=lambda item: (
                -item["score_fila"],
                -item["importancia"],
                item["disciplina"].lower(),
                item["topico"].lower(),
            ),
        )
        self.assertEqual(
            [item["topico_id"] for item in queue],
            [item["topico_id"] for item in expected],
        )
        for position, item in enumerate(queue, 1):
            self.assertEqual(item["versao_fila"], ACTIVE_QUEUE_VERSION)
            self.assertEqual(item["posicao_fila"], position)
            self.assertFalse(item["comparacao_fila_sombra"]["used_for_queue_order"])
            self.assertEqual(
                item["comparacao_fila_sombra"]["candidate_queue_version"],
                SHADOW_QUEUE_VERSION,
            )

    def test_batch_query_count_does_not_scale_per_topic(self):
        select_count = 0

        def traced_connect():
            nonlocal select_count
            connection = self.original_connect()
            self.connections.append(connection)

            def trace(statement):
                nonlocal select_count
                if statement.lstrip().upper().startswith("SELECT"):
                    select_count += 1

            connection.set_trace_callback(trace)
            return connection

        banco.conectar = traced_connect
        banco.obter_prioridades_sessao_adaptativa(
            self.contest_id,
            topicos_ids=[self.topic_ids[0]],
        )
        one_count = select_count
        select_count = 0
        banco.obter_prioridades_sessao_adaptativa(self.contest_id)
        many_count = select_count
        self.assertLessEqual(many_count - one_count, 3)
        self.assertLessEqual(many_count, 20)

    def test_reading_queue_and_snapshot_has_no_database_side_effect(self):
        before = self.table_counts()
        snapshot = banco.obter_snapshot_paridade_fila(self.contest_id)
        after = self.table_counts()
        self.assertEqual(before, after)
        self.assertEqual(snapshot["snapshot_type"], "queue_shadow_parity")
        self.assertFalse(snapshot["used_for_queue_order"])
        self.assertEqual(snapshot["active_queue_version"], ACTIVE_QUEUE_VERSION)

    def test_snapshot_is_written_only_by_explicit_audit_call(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "snapshot.json"
            banco.obter_prioridades_sessao_adaptativa(self.contest_id)
            self.assertFalse(destination.exists())
            result = banco.salvar_snapshot_paridade_fila(
                destination,
                self.contest_id,
            )
            self.assertTrue(destination.exists())
            self.assertEqual(result["caminho"], destination)


if __name__ == "__main__":
    unittest.main()
