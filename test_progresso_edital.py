"""Testes do Passo 7: Progresso do Edital V2."""

from __future__ import annotations

import inspect
import unittest
from datetime import date
from pathlib import Path

import banco
from progresso_edital import (
    PRESENTATION_CONSOLIDATING_RULE_VERSION,
    build_syllabus_forecast,
    build_syllabus_progress_snapshot,
)


class FakeMetric:
    def __init__(self, value, *, state="ok", denominator=None, parameters=None):
        self.value = value
        self.state = state
        self.denominator = denominator
        self.parameters = parameters or {}


class FakeScope:
    def __init__(self, metrics):
        self.metrics = metrics

    def metric(self, metric_id):
        return self.metrics[metric_id]

    def value(self, metric_id, default=None):
        metric = self.metrics.get(metric_id)
        return default if metric is None else metric.value


def topic_scope(
    *,
    attempts=0,
    evidence="insufficient",
    mastery=None,
    consolidation="insufficient_data",
    question_coverage=None,
    active_questions=0,
    answered_questions=0,
    reviews=0,
):
    mastery_state = "insufficient_data" if mastery is None else "ok"
    consolidation_state = (
        "insufficient_data" if consolidation == "insufficient_data" else "ok"
    )
    return FakeScope({
        "answered_attempt_count": FakeMetric(attempts),
        "answered_unique_question_count": FakeMetric(answered_questions),
        "accuracy_rate": FakeMetric(None if attempts == 0 else 80.0),
        "question_coverage_rate": FakeMetric(
            question_coverage,
            state="ok" if active_questions else "insufficient_data",
            denominator=active_questions,
            parameters={"answered_active_questions": answered_questions},
        ),
        "evidence_level": FakeMetric(
            evidence,
            parameters={
                "label": evidence.title(),
                "order": {"insufficient": 0, "low": 1, "moderate": 2, "high": 3}[evidence],
                "active_days": 1 if attempts else 0,
            },
        ),
        "mastery_score": FakeMetric(
            mastery,
            state=mastery_state,
            parameters={
                "level": "Dados insuficientes" if mastery is None else "Consolidando",
                "estimate": mastery,
                "current_performance": 80.0 if attempts else None,
                "error_control": {"score": 100.0},
            },
        ),
        "topic_consolidation_status": FakeMetric(
            consolidation,
            state=consolidation_state,
        ),
        "completed_review_count": FakeMetric(reviews),
        "last_review_at": FakeMetric(None, state="insufficient_data"),
        "last_activity_at": FakeMetric(None if attempts == 0 else "2026-09-01"),
        "recent_performance_rate": FakeMetric(None, state="insufficient_data"),
        "performance_trend": FakeMetric(None, state="insufficient_data"),
    })


def aggregate_scope(*, topic_coverage=0.0, question_coverage=None, mastery=None):
    return FakeScope({
        "topic_coverage_rate": FakeMetric(topic_coverage),
        "question_coverage_rate": FakeMetric(
            question_coverage,
            state="insufficient_data" if question_coverage is None else "ok",
        ),
        "mastery_score": FakeMetric(
            mastery,
            state="insufficient_data" if mastery is None else "ok",
        ),
    })


def make_snapshot(topic_specs, *, global_topic=0.0, global_question=None, global_mastery=None,
                  subject_mastery=None):
    catalog = []
    metrics = {}
    for index, spec in enumerate(topic_specs, 1):
        subject_id = int(spec.pop("subject_id", 1))
        catalog.append({
            "topico_id": index,
            "disciplina_id": subject_id,
            "disciplina": f"Disciplina {subject_id}",
            "topico": f"Tópico {index}",
            "importancia": 3,
            "proxima_revisao": None,
        })
        metrics[index] = topic_scope(**spec)
    subjects = {
        subject_id: aggregate_scope(
            topic_coverage=global_topic,
            question_coverage=global_question,
            mastery=subject_mastery,
        )
        for subject_id in {item["disciplina_id"] for item in catalog}
    }
    return build_syllabus_progress_snapshot(
        1,
        catalog,
        metrics,
        subjects,
        aggregate_scope(
            topic_coverage=global_topic,
            question_coverage=global_question,
            mastery=global_mastery,
        ),
        generated_at="2026-09-18T12:00:00-03:00",
    ).to_dict()


class SyllabusProgressSnapshotTests(unittest.TestCase):
    def test_a_syllabus_without_attempts(self):
        snapshot = make_snapshot([{}])
        self.assertEqual(snapshot["started_topics"], 0)
        self.assertEqual(snapshot["topicos"][0]["estado"], "Não iniciado")
        self.assertIsNone(snapshot["global_mastery_score"])

    def test_b_one_answer_is_started_but_insufficient(self):
        snapshot = make_snapshot([{"attempts": 1, "active_questions": 4,
                                    "answered_questions": 1, "question_coverage": 25.0}],
                                 global_topic=100.0, global_question=25.0)
        topic = snapshot["topicos"][0]
        self.assertEqual(topic["estado"], "Em andamento")
        self.assertEqual(topic["evidencia"], "insufficient")
        self.assertIsNone(topic["dominio_score"])

    def test_c_low_evidence_is_provisional(self):
        topic = make_snapshot([{"attempts": 4, "evidence": "low", "mastery": 72.0,
                                "consolidation": "not_consolidated"}])["topicos"][0]
        self.assertTrue(topic["dominio_provisorio"])
        self.assertEqual(topic["estado"], "Em andamento")

    def test_d_moderate_evidence_counts_as_sufficient(self):
        snapshot = make_snapshot([{"attempts": 10, "evidence": "moderate", "mastery": 75.0,
                                    "consolidation": "not_consolidated"}])
        self.assertEqual(snapshot["sufficient_evidence_topics"], 1)
        self.assertEqual(snapshot["sufficient_evidence_rate"], 100.0)
        self.assertEqual(snapshot["topicos"][0]["estado"], "Em consolidação")
        self.assertEqual(
            snapshot["topicos"][0]["estado_regra"],
            PRESENTATION_CONSOLIDATING_RULE_VERSION,
        )

    def test_e_high_evidence_counts_as_sufficient(self):
        snapshot = make_snapshot([{"attempts": 30, "evidence": "high", "mastery": 90.0,
                                    "consolidation": "not_consolidated"}])
        self.assertEqual(snapshot["high_evidence_topics"], 1)
        self.assertEqual(snapshot["sufficient_evidence_topics"], 1)

    def test_f_official_consolidated_is_the_only_consolidated_state(self):
        snapshot = make_snapshot([{"attempts": 30, "evidence": "high", "mastery": 90.0,
                                    "consolidation": "consolidated"}])
        self.assertEqual(snapshot["consolidated_topics"], 1)
        self.assertEqual(snapshot["topicos"][0]["estado"], "Consolidado")

    def test_g_insufficient_data_does_not_become_not_consolidated(self):
        topic = make_snapshot([{"attempts": 3, "evidence": "low", "mastery": 80.0,
                                "consolidation": "insufficient_data"}])["topicos"][0]
        self.assertEqual(topic["consolidacao"], "insufficient_data")
        self.assertEqual(topic["consolidacao_estado"], "insufficient_data")
        self.assertEqual(topic["estado"], "Em andamento")

    def test_h_subject_mastery_is_official_not_simple_topic_average(self):
        snapshot = make_snapshot(
            [
                {"attempts": 3, "evidence": "low", "mastery": 10.0},
                {"attempts": 30, "evidence": "high", "mastery": 100.0},
            ],
            subject_mastery=82.0,
        )
        self.assertEqual(snapshot["disciplinas"][0]["dominio"], 82.0)
        self.assertNotEqual(snapshot["disciplinas"][0]["dominio"], 55.0)

    def test_i_topic_and_question_coverage_remain_different(self):
        snapshot = make_snapshot([{}, {}], global_topic=50.0, global_question=10.0)
        self.assertEqual(snapshot["topic_coverage_rate"], 50.0)
        self.assertEqual(snapshot["question_coverage_rate"], 10.0)

    def test_j_none_mastery_is_not_zero(self):
        snapshot = make_snapshot([{}], global_mastery=None)
        self.assertIsNone(snapshot["global_mastery_score"])
        self.assertIsNone(snapshot["topicos"][0]["dominio_score"])

    def test_k_subject_without_mastery_remains_insufficient(self):
        snapshot = make_snapshot([{}], subject_mastery=None)
        self.assertIsNone(snapshot["disciplinas"][0]["dominio"])
        self.assertEqual(snapshot["disciplinas"][0]["dominio_estado"], "insufficient_data")

    def test_l_forecast_without_minimum_basis_has_no_date(self):
        snapshot = make_snapshot([{}, {}, {}, {}, {}])
        events = [{"data_inicio": "2026-09-17"}] * 3
        result = build_syllabus_forecast(snapshot, events, 4, date(2026, 9, 18))
        self.assertFalse(result["coverage_basis"]["sufficient"])
        self.assertIsNone(result["coverage_forecast"])

    def test_m_forecast_with_controlled_basis_is_an_extrapolation(self):
        snapshot = make_snapshot([{}, {}, {}, {}, {}])
        events = [
            {"data_inicio": "2026-09-01"},
            {"data_inicio": "2026-09-05"},
            {"data_inicio": "2026-09-10"},
            {"data_inicio": "2026-09-15"},
        ]
        result = build_syllabus_forecast(snapshot, events, 4, date(2026, 9, 18))
        self.assertTrue(result["coverage_basis"]["sufficient"])
        self.assertIsNotNone(result["coverage_forecast"])
        self.assertTrue(result["is_extrapolation"])

    def test_n_topic_without_active_questions_has_insufficient_coverage(self):
        topic = make_snapshot([{"attempts": 1}])["topicos"][0]
        self.assertIsNone(topic["cobertura_questoes"])
        self.assertEqual(topic["questoes_ativas"], 0)

    def test_o_paused_or_inactive_topics_are_outside_catalog_universe(self):
        snapshot = make_snapshot([{}, {}])
        self.assertEqual(snapshot["total_topics"], 2)
        self.assertEqual([item["topico_id"] for item in snapshot["topicos"]], [1, 2])

    def test_p_dashboard_and_progress_use_same_snapshot_method(self):
        source = Path("main.py").read_text(encoding="utf-8")
        dashboard = source.split("    def atualizar_progresso_dashboard(", 1)[1].split(
            "    def abrir_progresso_edital(", 1
        )[0]
        progress = source.split("    def atualizar_progresso_edital(", 1)[1].split(
            "    def filtrar_progresso_edital(", 1
        )[0]
        self.assertIn("montar_snapshot_progresso_edital", dashboard)
        self.assertIn("montar_snapshot_progresso_edital", progress)

    def test_q_database_snapshot_uses_batch_apis_without_topic_n_plus_one(self):
        source = inspect.getsource(banco.obter_snapshot_progresso_edital)
        self.assertIn("get_topic_metrics_batch", source)
        self.assertIn("get_subject_metrics_batch", source)
        self.assertIn("get_global_metrics", source)
        self.assertNotIn("get_topic_metrics(", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
