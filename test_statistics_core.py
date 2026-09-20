"""Testes de referencia do Nucleo Estatistico Central.

Executavel sem dependencias externas: ``python -m unittest test_statistics_core``.
"""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path

from statistics_core import StatisticalPeriods, StatisticsService
from statistics_core.periods import statistical_timezone


class StatisticsCoreTests(unittest.TestCase):
    def setUp(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
            self.db_path = Path(handle.name)
        self.select_count = 0

        def connect():
            connection = sqlite3.connect(self.db_path)

            def trace(statement):
                if statement.lstrip().upper().startswith("SELECT"):
                    self.select_count += 1

            connection.set_trace_callback(trace)
            return connection

        self.connect = connect
        with closing(connect()) as con:
            con.executescript(
                """
                CREATE TABLE disciplinas (id INTEGER PRIMARY KEY, nome TEXT);
                CREATE TABLE topicos (
                    id INTEGER PRIMARY KEY,
                    disciplina_id INTEGER NOT NULL,
                    nome TEXT
                );
                CREATE TABLE concursos (id INTEGER PRIMARY KEY, nome TEXT);
                CREATE TABLE disciplina_concurso_inclusao (
                    disciplina_id INTEGER,
                    concurso_id INTEGER,
                    incluido INTEGER,
                    pausado INTEGER
                );
                CREATE TABLE topico_concurso_importancia (
                    topico_id INTEGER,
                    concurso_id INTEGER,
                    incluido INTEGER,
                    pausado INTEGER,
                    importancia INTEGER
                );
                CREATE TABLE questoes (
                    id INTEGER PRIMARY KEY,
                    topico_id INTEGER,
                    ativa INTEGER,
                    excluida INTEGER
                );
                CREATE TABLE sessoes_questoes (
                    id INTEGER PRIMARY KEY,
                    concurso_id INTEGER,
                    iniciado_em TEXT,
                    encerrado_em TEXT,
                    concluida INTEGER
                );
                CREATE TABLE revisoes (
                    id INTEGER PRIMARY KEY,
                    topico_id INTEGER,
                    data TEXT,
                    realizada_em TEXT,
                    questoes INTEGER,
                    acertos INTEGER
                );
                CREATE TABLE tentativas_questoes (
                    id INTEGER PRIMARY KEY,
                    sessao_id INTEGER,
                    questao_id INTEGER,
                    concurso_id INTEGER,
                    respondida_em TEXT,
                    correta INTEGER,
                    marcada_duvida INTEGER DEFAULT 0,
                    revisao_id INTEGER,
                    questao_id_snapshot INTEGER,
                    topico_id_snapshot INTEGER,
                    disciplina_id_snapshot INTEGER
                );
                """
            )
            con.executemany(
                "INSERT INTO disciplinas VALUES (?, ?)",
                [(1, "Disciplina A"), (2, "Disciplina B")],
            )
            con.executemany(
                "INSERT INTO topicos VALUES (?, ?, ?)",
                [(1, 1, "Topico A"), (2, 1, "Topico B"), (3, 2, "Topico C")],
            )
            con.execute("INSERT INTO concursos VALUES (1, 'Perfil')")
            con.executemany(
                "INSERT INTO disciplina_concurso_inclusao VALUES (?, 1, 1, 0)",
                [(1,), (2,)],
            )
            con.executemany(
                "INSERT INTO topico_concurso_importancia VALUES (?, 1, 1, 0, 3)",
                [(1,), (2,), (3,)],
            )
            questions = (
                [(item, 1, 1, 0) for item in range(1, 13)]
                + [(item, 2, 1, 0) for item in range(101, 104)]
                + [(item, 3, 1, 0) for item in range(201, 204)]
            )
            con.executemany("INSERT INTO questoes VALUES (?, ?, ?, ?)", questions)
            con.commit()

        self.service = StatisticsService(connect)
        self.attempt_id = 0

    def tearDown(self):
        self.db_path.unlink(missing_ok=True)

    def add_attempt(
        self,
        question_id,
        correct,
        *,
        days_ago=0,
        session_id=1,
        topic_id=None,
        subject_id=None,
        contest_id=1,
        doubt=0,
    ):
        self.attempt_id += 1
        if topic_id is None or subject_id is None:
            with closing(self.connect()) as con:
                row = con.execute(
                    "SELECT t.id, t.disciplina_id FROM questoes q JOIN topicos t ON t.id=q.topico_id WHERE q.id=?",
                    (question_id,),
                ).fetchone()
            topic_id = topic_id if topic_id is not None else row[0]
            subject_id = subject_id if subject_id is not None else row[1]
        timestamp = datetime.now(statistical_timezone()).replace(microsecond=0) - timedelta(days=days_ago)
        with closing(self.connect()) as con:
            con.execute(
                "INSERT OR IGNORE INTO sessoes_questoes VALUES (?, ?, ?, ?, 1)",
                (session_id, contest_id, timestamp.isoformat(sep=" "), timestamp.isoformat(sep=" ")),
            )
            con.execute(
                """
                INSERT INTO tentativas_questoes
                (id, sessao_id, questao_id, concurso_id, respondida_em, correta,
                 marcada_duvida, questao_id_snapshot, topico_id_snapshot,
                 disciplina_id_snapshot)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.attempt_id, session_id, question_id, contest_id,
                    timestamp.isoformat(sep=" "), int(bool(correct)), doubt,
                    question_id, topic_id, subject_id,
                ),
            )
            con.commit()
        return self.attempt_id

    def add_review(self, review_id, attempt_id, days_ago=0, topic_id=1):
        timestamp = datetime.now(statistical_timezone()).replace(microsecond=0) - timedelta(days=days_ago)
        with closing(self.connect()) as con:
            con.execute(
                "INSERT INTO revisoes VALUES (?, ?, ?, ?, 1, 1)",
                (review_id, topic_id, timestamp.date().isoformat(), timestamp.isoformat(sep=" ")),
            )
            con.execute(
                "UPDATE tentativas_questoes SET revisao_id=? WHERE id=?",
                (review_id, attempt_id),
            )
            con.commit()

    def topic(self, topic_id=1):
        return self.service.get_topic_metrics(topic_id, 1)

    def test_a_no_attempts(self):
        metrics = self.topic()
        self.assertEqual(metrics.value("answered_attempt_count"), 0)
        self.assertIsNone(metrics.value("accuracy_rate"))
        self.assertIsNone(metrics.value("mastery_score"))
        self.assertEqual(metrics.value("evidence_level"), "insufficient")

    def test_b_single_correct_attempt(self):
        self.add_attempt(1, True)
        metrics = self.topic()
        self.assertEqual(metrics.value("correct_attempt_count"), 1)
        self.assertEqual(metrics.value("incorrect_attempt_count"), 0)
        self.assertEqual(metrics.value("accuracy_rate"), 100.0)

    def test_c_single_incorrect_attempt(self):
        self.add_attempt(1, False)
        metrics = self.topic()
        self.assertEqual(metrics.value("correct_attempt_count"), 0)
        self.assertEqual(metrics.value("incorrect_attempt_count"), 1)
        self.assertEqual(metrics.value("accuracy_rate"), 0.0)

    def test_d_same_question_repeated(self):
        for result in (False, False, True, True):
            self.add_attempt(1, result)
        metrics = self.topic()
        self.assertEqual(metrics.value("answered_attempt_count"), 4)
        self.assertEqual(metrics.value("answered_unique_question_count"), 1)
        self.assertEqual(metrics.value("correct_attempt_count"), 2)
        self.assertEqual(metrics.value("incorrect_attempt_count"), 2)
        self.assertEqual(metrics.value("accuracy_rate"), 50.0)
        self.assertEqual(
            self.service.get_question_metrics(1, 1).value("last_attempt_result"),
            "correct",
        )
        recent = metrics.metric("recent_performance_rate")
        self.assertEqual(recent.state, "insufficient_data")
        self.assertEqual(recent.parameters["estimate"], 50.0)

    def test_e_multiple_questions_same_topic_and_coverage(self):
        for question_id in (1, 2, 3):
            self.add_attempt(question_id, True)
        metrics = self.topic()
        self.assertEqual(metrics.value("answered_unique_question_count"), 3)
        self.assertAlmostEqual(metrics.value("question_coverage_rate"), 25.0)
        self.assertIsNotNone(metrics.value("mastery_score"))
        self.assertEqual(metrics.value("evidence_level"), "low")

    def test_f_multiple_sessions(self):
        for session_id, question_id in enumerate((1, 2, 3), 1):
            self.add_attempt(question_id, True, session_id=session_id)
        metrics = self.topic()
        self.assertEqual(metrics.value("distinct_answered_session_count"), 3)
        self.assertIsNotNone(metrics.value("last_activity_at"))
        self.assertEqual(metrics.value("evidence_level"), "low")

    def test_g_perfect_accuracy_can_have_insufficient_evidence(self):
        for _ in range(8):
            self.add_attempt(1, True)
        metrics = self.topic()
        self.assertEqual(metrics.value("accuracy_rate"), 100.0)
        self.assertEqual(metrics.value("evidence_level"), "insufficient")
        self.assertIsNone(metrics.value("mastery_score"))
        self.assertGreater(
            metrics.metric("mastery_score").parameters["estimate"],
            80.0,
        )

    def test_h_high_performance_and_high_evidence(self):
        attempt_ids = []
        day_offsets = [28, 22, 15, 7, 0]
        for index in range(40):
            attempt_ids.append(self.add_attempt(
                1 + index % 10,
                index % 10 != 0,
                days_ago=day_offsets[index % 5],
                session_id=1 + index % 5,
            ))
        self.add_review(1, attempt_ids[0], days_ago=15)
        self.add_review(2, attempt_ids[1], days_ago=7)
        metrics = self.topic()
        self.assertEqual(metrics.value("evidence_level"), "high")
        self.assertIsNotNone(metrics.value("mastery_score"))
        self.assertGreater(metrics.value("accuracy_rate"), 80.0)

    def test_medium_mastery_can_have_high_evidence(self):
        attempt_ids = []
        round_offsets = (28, 15, 7, 0)
        round_results = (False, True, False, True)
        for round_index, (offset, correct) in enumerate(
            zip(round_offsets, round_results),
            1,
        ):
            for question_index in range(10):
                attempt_ids.append(self.add_attempt(
                    1 + question_index,
                    correct,
                    days_ago=22 if (round_index == 1 and question_index == 0) else offset,
                    session_id=round_index,
                ))
        self.add_review(1, attempt_ids[0], days_ago=15)
        self.add_review(2, attempt_ids[1], days_ago=7)
        metrics = self.topic()
        self.assertEqual(metrics.value("evidence_level"), "high")
        self.assertGreaterEqual(metrics.value("mastery_score"), 50.0)
        self.assertLess(metrics.value("mastery_score"), 70.0)

    def test_consolidation_uses_independent_official_requirements(self):
        attempt_ids = []
        day_offsets = [28, 22, 15, 7, 0]
        incorrect_indexes = {5, 18, 26, 37}
        for index in range(40):
            attempt_ids.append(self.add_attempt(
                1 + index % 10,
                index not in incorrect_indexes,
                days_ago=day_offsets[index % 5],
                session_id=1 + index % 5,
            ))
        self.add_review(1, attempt_ids[0], days_ago=15)
        self.add_review(2, attempt_ids[1], days_ago=7)
        metrics = self.topic()
        self.assertEqual(metrics.value("evidence_level"), "high")
        self.assertGreaterEqual(metrics.value("mastery_score"), 85.0)
        self.assertEqual(metrics.value("topic_consolidation_status"), "consolidated")

    def test_i_recent_decline(self):
        for index in range(15):
            self.add_attempt(1 + index % 10, True, days_ago=2, session_id=1)
        for index in range(15):
            self.add_attempt(1 + index % 10, False, days_ago=0, session_id=2)
        self.assertEqual(self.topic().value("performance_trend"), "decline")

    def test_j_recovery_after_errors(self):
        for result in (False, False, False, True, True, True):
            self.add_attempt(1, result)
        mastery = self.topic().metric("mastery_score")
        self.assertEqual(mastery.parameters["error_control"]["recovered"], 1)

    def test_consecutive_errors_are_classified_as_critical(self):
        for _ in range(3):
            self.add_attempt(1, False)
        mastery = self.topic().metric("mastery_score")
        self.assertEqual(mastery.parameters["error_control"]["critical"], 1)
        self.assertEqual(self.topic().value("critical_open_error_count"), 1)

    def test_k_archived_question_preserves_history(self):
        self.add_attempt(1, True)
        with closing(self.connect()) as con:
            con.execute("UPDATE questoes SET ativa=0 WHERE id=1")
            con.commit()
        metrics = self.topic()
        self.assertEqual(metrics.value("answered_attempt_count"), 1)
        self.assertEqual(metrics.value("answered_unique_question_count"), 1)
        self.assertEqual(metrics.metric("question_coverage_rate").denominator, 11)

    def test_l_trashed_question_preserves_history(self):
        self.add_attempt(1, False)
        with closing(self.connect()) as con:
            con.execute("UPDATE questoes SET ativa=0, excluida=1 WHERE id=1")
            con.commit()
        metrics = self.topic()
        self.assertEqual(metrics.value("answered_attempt_count"), 1)
        self.assertEqual(metrics.value("incorrect_attempt_count"), 1)
        self.assertEqual(metrics.metric("question_coverage_rate").denominator, 11)

    def test_m_restored_question_does_not_duplicate_history(self):
        self.add_attempt(1, True)
        with closing(self.connect()) as con:
            con.execute("UPDATE questoes SET ativa=0, excluida=1 WHERE id=1")
            con.commit()
        trashed = self.topic()
        with closing(self.connect()) as con:
            con.execute("UPDATE questoes SET ativa=1, excluida=0 WHERE id=1")
            con.commit()
        restored = self.topic()
        self.assertEqual(trashed.value("answered_attempt_count"), 1)
        self.assertEqual(restored.value("answered_attempt_count"), 1)
        self.assertEqual(restored.value("answered_unique_question_count"), 1)
        self.assertEqual(restored.metric("question_coverage_rate").denominator, 12)

    def test_permanent_deletion_preserves_snapshot_history(self):
        self.add_attempt(1, True)
        with closing(self.connect()) as con:
            con.execute("DELETE FROM questoes WHERE id=1")
            con.commit()
        self.assertEqual(self.topic().value("answered_attempt_count"), 1)

    def test_l_topics_in_same_subject_are_recalculated_from_events(self):
        self.add_attempt(1, True)
        self.add_attempt(101, False)
        subject = self.service.get_subject_metrics(1, 1)
        self.assertEqual(subject.value("answered_attempt_count"), 2)
        self.assertEqual(subject.value("accuracy_rate"), 50.0)

    def test_m_subjects_with_different_volumes_are_weighted_by_events(self):
        self.add_attempt(1, True)
        for index in range(99):
            self.add_attempt(201, index % 2 == 0, session_id=2)
        global_metrics = self.service.get_global_metrics(1)
        self.assertAlmostEqual(global_metrics.value("accuracy_rate"), 51.0)
        self.assertNotEqual(global_metrics.value("accuracy_rate"), 75.0)

    def test_n_official_7_and_30_day_periods(self):
        self.add_attempt(1, True, days_ago=2)
        self.add_attempt(2, True, days_ago=10)
        self.add_attempt(3, True, days_ago=40)
        seven = self.service.get_global_metrics(1, StatisticalPeriods.last_7_days())
        thirty = self.service.get_global_metrics(1, StatisticalPeriods.last_30_days())
        self.assertEqual(seven.value("answered_attempt_count"), 1)
        self.assertEqual(thirty.value("answered_attempt_count"), 2)
        self.assertEqual(
            StatisticalPeriods.last_7_days().previous_equivalent().identifier,
            "previous_equivalent",
        )

    def test_o_exact_period_boundaries_and_previous_equivalent(self):
        for offset in (0, 6, 7, 13, 14, 29, 30, 45):
            self.add_attempt(1, True, days_ago=offset, session_id=offset + 1)
        seven_period = StatisticalPeriods.last_7_days()
        previous = seven_period.previous_equivalent()
        seven = self.service.get_global_metrics(1, seven_period)
        previous_metrics = self.service.get_global_metrics(1, previous)
        thirty = self.service.get_global_metrics(1, StatisticalPeriods.last_30_days())
        self.assertEqual(seven.value("answered_attempt_count"), 2)
        self.assertEqual(previous_metrics.value("answered_attempt_count"), 2)
        self.assertEqual(thirty.value("answered_attempt_count"), 6)

    def test_recency_uses_last_included_day_not_exclusive_end(self):
        self.add_attempt(1, True, days_ago=7)
        mastery = self.topic().metric("mastery_score")
        self.assertEqual(mastery.parameters["last_activity_age_days"], 7)
        self.assertEqual(mastery.parameters["recency"], 100.0)

    def test_o_sparse_legacy_data_reports_missing_requirements(self):
        self.add_attempt(1, True, session_id=1)
        metrics = self.topic()
        self.assertEqual(metrics.metric("performance_trend").state, "insufficient_data")
        self.assertIn("attempts_needed", metrics.metric("performance_trend").missing_requirements)

    def test_question_api_and_consistent_metadata(self):
        self.add_attempt(1, False)
        self.add_attempt(1, True)
        metrics = self.service.get_question_metrics(1, 1)
        self.assertEqual(metrics.value("question_attempt_count"), 2)
        self.assertEqual(metrics.value("last_attempt_result"), "correct")
        result = metrics.metric("accuracy_rate")
        self.assertEqual(result.metric_version, "1")
        self.assertEqual(result.timezone, "America/Sao_Paulo")
        self.assertEqual(result.scope["question_id"], 1)

    def test_controlled_validation_matrix_for_fundamental_metrics(self):
        self.add_attempt(1, False, session_id=1)
        self.add_attempt(2, False, session_id=1)
        self.add_attempt(1, True, session_id=2)
        last_id = self.add_attempt(2, True, session_id=2)
        self.add_review(1, last_id)
        metrics = self.topic()
        produced = {
            "total_attempts": metrics.value("answered_attempt_count"),
            "correct_attempts": metrics.value("correct_attempt_count"),
            "incorrect_attempts": metrics.value("incorrect_attempt_count"),
            "unique_questions_answered": metrics.value("answered_unique_question_count"),
            "accuracy_rate": metrics.value("accuracy_rate"),
            "session_count": metrics.value("distinct_answered_session_count"),
            "review_count": metrics.value("completed_review_count"),
            "evidence_level": metrics.value("evidence_level"),
            "coverage_rate": metrics.value("question_coverage_rate"),
        }
        expected = {
            "total_attempts": 4,
            "correct_attempts": 2,
            "incorrect_attempts": 2,
            "unique_questions_answered": 2,
            "accuracy_rate": 50.0,
            "session_count": 2,
            "review_count": 1,
            "evidence_level": "low",
            "coverage_rate": 100.0 * 2 / 12,
        }
        self.assertEqual(produced, expected)
        self.assertAlmostEqual(metrics.value("mastery_score"), 60.8125)
        self.assertIsNotNone(metrics.value("last_activity_at"))

    def test_evidence_and_mastery_are_independent(self):
        ids = []
        day_offsets = [28, 22, 15, 7, 0]
        for index in range(40):
            ids.append(self.add_attempt(
                1 + index % 10,
                index % 8 == 0,
                days_ago=day_offsets[index % 5],
                session_id=1 + index % 5,
            ))
        self.add_review(1, ids[0], days_ago=15)
        self.add_review(2, ids[1], days_ago=7)
        metrics = self.topic()
        self.assertEqual(metrics.value("evidence_level"), "high")
        self.assertLess(metrics.value("mastery_score"), 50.0)

    def test_recent_performance_improvement_stability_and_insufficient(self):
        self.assertEqual(self.topic().value("performance_trend"), "insufficient_data")
        for index in range(15):
            self.add_attempt(1 + index % 10, False, days_ago=2, session_id=1)
        for index in range(15):
            self.add_attempt(1 + index % 10, True, days_ago=0, session_id=2)
        self.assertEqual(self.topic().value("performance_trend"), "improvement")

        # Um segundo tópico com taxas iguais nas duas janelas valida estabilidade.
        for index in range(15):
            self.add_attempt(101 + index % 3, index % 2 == 0, days_ago=2, session_id=3)
        for index in range(15):
            self.add_attempt(101 + index % 3, index % 2 == 0, days_ago=0, session_id=4)
        self.assertEqual(self.topic(2).value("performance_trend"), "stable")

    def test_incorrect_answer_counts_for_coverage_and_repetition_does_not_inflate(self):
        for _ in range(4):
            self.add_attempt(1, False)
        metrics = self.topic()
        self.assertEqual(metrics.value("answered_unique_question_count"), 1)
        self.assertAlmostEqual(metrics.value("question_coverage_rate"), 100.0 / 12)

    def test_topic_without_available_questions_has_insufficient_coverage(self):
        with closing(self.connect()) as con:
            con.execute("UPDATE questoes SET ativa=0 WHERE topico_id=1")
            con.commit()
        coverage = self.topic().metric("question_coverage_rate")
        self.assertIsNone(coverage.value)
        self.assertEqual(coverage.state, "insufficient_data")

    def test_batch_query_count_is_constant(self):
        self.select_count = 0
        self.service.get_topic_metrics_batch(1, [1, 2, 3])
        self.assertEqual(self.select_count, 4)

    def test_global_question_session_count_includes_empty_sessions(self):
        timestamp = datetime.now(statistical_timezone()).replace(microsecond=0)
        with closing(self.connect()) as con:
            con.execute(
                "INSERT INTO sessoes_questoes VALUES (99, 1, ?, ?, 1)",
                (timestamp.isoformat(sep=" "), timestamp.isoformat(sep=" ")),
            )
            con.commit()
        self.add_attempt(1, True, session_id=1)
        metrics = self.service.get_global_metrics(1)
        self.assertEqual(metrics.value("distinct_answered_session_count"), 1)
        self.assertEqual(metrics.value("question_session_count"), 2)

    def test_unattributed_review_is_legacy_limited(self):
        with closing(self.connect()) as con:
            con.execute(
                "INSERT INTO revisoes VALUES (1, 1, ?, NULL, 10, 8)",
                (datetime.now(statistical_timezone()).date().isoformat(),),
            )
            con.commit()
        result = self.topic().metric("completed_review_count")
        self.assertEqual(result.state, "legacy_limited")
        self.assertEqual(result.value, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
