"""Testes do Passo 8: tendencias e comparacoes temporais V2."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
import gc
import warnings
from contextlib import closing
from datetime import date, datetime, timezone
from pathlib import Path

import banco
from analise_temporal import (
    build_period,
    build_temporal_analytics_snapshot,
)
from fila_candidata import ACTIVE_QUEUE_VERSION, USED_FOR_QUEUE_ORDER
from statistics_core import StatisticalPeriods, StatisticsService


class TemporalAnalyticsTests(unittest.TestCase):
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
                    id INTEGER PRIMARY KEY, disciplina_id INTEGER, nome TEXT
                );
                CREATE TABLE concursos (id INTEGER PRIMARY KEY, nome TEXT);
                CREATE TABLE disciplina_concurso_inclusao (
                    disciplina_id INTEGER, concurso_id INTEGER,
                    incluido INTEGER, pausado INTEGER
                );
                CREATE TABLE topico_concurso_importancia (
                    topico_id INTEGER, concurso_id INTEGER,
                    incluido INTEGER, pausado INTEGER, importancia INTEGER
                );
                CREATE TABLE questoes (
                    id INTEGER PRIMARY KEY, topico_id INTEGER,
                    ativa INTEGER, excluida INTEGER
                );
                CREATE TABLE sessoes_questoes (
                    id INTEGER PRIMARY KEY, concurso_id INTEGER,
                    iniciado_em TEXT, encerrado_em TEXT, concluida INTEGER
                );
                CREATE TABLE tentativas_questoes (
                    id INTEGER PRIMARY KEY, sessao_id INTEGER,
                    questao_id INTEGER, concurso_id INTEGER,
                    respondida_em TEXT, correta INTEGER,
                    marcada_duvida INTEGER DEFAULT 0, revisao_id INTEGER,
                    questao_id_snapshot INTEGER, topico_id_snapshot INTEGER,
                    disciplina_id_snapshot INTEGER
                );
                CREATE TABLE revisoes (
                    id INTEGER PRIMARY KEY, topico_id INTEGER,
                    concurso_id INTEGER, data TEXT, realizada_em TEXT,
                    questoes INTEGER, acertos INTEGER
                );
                CREATE TABLE sessoes_foco (
                    id INTEGER PRIMARY KEY, inicio TEXT,
                    duracao_efetiva INTEGER, concluida INTEGER
                );
                CREATE TABLE progresso_snapshots_diarios (
                    id INTEGER PRIMARY KEY, concurso_id INTEGER, data TEXT,
                    captured_at TEXT, metric_version TEXT, snapshot_version TEXT,
                    topic_coverage_rate REAL, question_coverage_rate REAL,
                    sufficient_evidence_rate REAL, consolidated_rate REAL,
                    global_mastery_score REAL, global_mastery_state TEXT
                );
                """
            )
            con.executemany(
                "INSERT INTO concursos VALUES (?, ?)",
                [(1, "Perfil A"), (2, "Perfil B")],
            )
            con.executemany(
                "INSERT INTO disciplinas VALUES (?, ?)",
                [(1, "Disciplina A"), (2, "Disciplina B")],
            )
            con.executemany(
                "INSERT INTO topicos VALUES (?, ?, ?)",
                [(1, 1, "Topico A"), (2, 2, "Topico B")],
            )
            con.executemany(
                "INSERT INTO disciplina_concurso_inclusao VALUES (?, 1, 1, 0)",
                [(1,), (2,)],
            )
            con.executemany(
                "INSERT INTO topico_concurso_importancia VALUES (?, 1, 1, 0, 3)",
                [(1,), (2,)],
            )
            con.executemany(
                "INSERT INTO questoes VALUES (?, ?, 1, 0)",
                [(item, 1 if item <= 100 else 2) for item in range(1, 201)],
            )
            con.commit()
        self.service = StatisticsService(connect)
        self.next_attempt = 0
        self.next_session = 0
        self.next_review = 0
        self.period = StatisticalPeriods.custom(
            date(2026, 9, 8), date(2026, 9, 18), "test_current"
        )

    def tearDown(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            gc.collect()
        self.db_path.unlink(missing_ok=True)

    def add_attempt(
        self,
        when,
        correct,
        *,
        topic_id=1,
        subject_id=1,
        concurso_id=1,
        question_id=None,
        session_id=None,
    ):
        self.next_attempt += 1
        if question_id is None:
            question_id = self.next_attempt if topic_id == 1 else 100 + self.next_attempt
        if session_id is None:
            self.next_session += 1
            session_id = self.next_session
        with closing(self.connect()) as con:
            con.execute(
                "INSERT OR IGNORE INTO sessoes_questoes VALUES (?, ?, ?, NULL, 1)",
                (session_id, concurso_id, str(when)),
            )
            con.execute(
                """INSERT INTO tentativas_questoes VALUES
                   (?, ?, ?, ?, ?, ?, 0, NULL, ?, ?, ?)""",
                (
                    self.next_attempt,
                    session_id,
                    question_id,
                    concurso_id,
                    str(when),
                    int(bool(correct)),
                    question_id,
                    topic_id,
                    subject_id,
                ),
            )
            con.commit()

    def add_review(self, when, concurso_id, topic_id=1):
        self.next_review += 1
        with closing(self.connect()) as con:
            con.execute(
                "INSERT INTO revisoes VALUES (?, ?, ?, ?, ?, 5, 4)",
                (self.next_review, topic_id, concurso_id, str(when)[:10], str(when)),
            )
            con.commit()

    def snapshot(self, period=None):
        return build_temporal_analytics_snapshot(
            self.connect, 1, period or self.period, self.service
        ).to_dict()

    def add_period_sample(self, current, *, attempts=10, correct=7, topic_id=1):
        dates = ("2026-09-10 10:00:00", "2026-09-11 10:00:00") if current else (
            "2026-09-01 10:00:00",
            "2026-09-02 10:00:00",
        )
        for index in range(attempts):
            self.add_attempt(
                dates[index % 2],
                index < correct,
                topic_id=topic_id,
                subject_id=topic_id,
            )

    def test_a_current_period_without_data(self):
        data = self.snapshot()
        self.assertEqual(data["current_metrics"]["attempts"], 0)
        self.assertIsNone(data["current_metrics"]["accuracy_rate"])

    def test_b_previous_period_without_data(self):
        self.add_period_sample(True)
        data = self.snapshot()
        self.assertEqual(data["previous_metrics"]["attempts"], 0)
        self.assertEqual(data["sufficiency"]["state"], "insufficient_data")

    def test_c_current_counts_with_previous_zero(self):
        self.add_period_sample(True)
        delta = self.snapshot()["comparisons"]["attempts"]
        self.assertEqual(delta["absolute"], 10)
        self.assertIsNone(delta["relative_percent"])

    def test_d_current_rate_with_fewer_than_ten_attempts(self):
        self.add_period_sample(True, attempts=9)
        self.add_period_sample(False)
        self.assertFalse(self.snapshot()["sufficiency"]["ready"])

    def test_e_previous_rate_with_fewer_than_ten_attempts(self):
        self.add_period_sample(True)
        self.add_period_sample(False, attempts=9)
        self.assertFalse(self.snapshot()["sufficiency"]["ready"])

    def test_f_both_periods_sufficient(self):
        self.add_period_sample(True)
        self.add_period_sample(False)
        self.assertTrue(self.snapshot()["sufficiency"]["ready"])

    def test_g_accuracy_delta_is_percentage_points(self):
        self.add_period_sample(True, correct=8)
        self.add_period_sample(False, correct=5)
        comparison = self.snapshot()["comparisons"]["accuracy"]
        self.assertEqual(comparison["delta_pp"], 30.0)

    def test_h_official_trend_differs_from_period_comparison(self):
        self.add_period_sample(False, correct=5)
        for index in range(10):
            self.add_attempt("2026-09-10 10:00:00", True, session_id=100)
        for index in range(10):
            self.add_attempt("2026-09-11 10:00:00", False, session_id=101)
        data = self.snapshot()
        self.assertEqual(data["comparisons"]["accuracy"]["delta_pp"], 0.0)
        self.assertEqual(data["official_performance_trend"]["value"], "decline")

    def test_i_day_without_answers_has_none_accuracy(self):
        self.add_attempt("2026-09-10 10:00:00", True)
        days = {item["date"]: item for item in self.snapshot()["daily_series"]}
        self.assertIsNone(days["2026-09-09"]["accuracy_rate"])
        self.assertEqual(days["2026-09-09"]["attempts"], 0)

    def test_j_review_from_other_contest_is_excluded(self):
        self.add_review("2026-09-10 12:00:00", 2)
        data = self.snapshot()
        self.assertEqual(data["current_metrics"]["qualified_reviews"], 0)

    def test_k_null_review_remains_legacy_limited(self):
        self.add_review("2026-09-10 12:00:00", None)
        data = self.snapshot()
        self.assertEqual(data["current_metrics"]["review_state"], "legacy_limited")
        self.assertIn("legacy_reviews_without_concurso_excluded", data["lineage_warnings"])

    def test_l_focus_without_contest_is_global(self):
        with closing(self.connect()) as con:
            con.execute(
                "INSERT INTO sessoes_foco VALUES (1, '2026-09-10 08:00:00', 1800, 1)"
            )
            con.commit()
        focus = self.snapshot()["global_focus"]["current"]
        self.assertEqual(focus["scope"], "global")
        self.assertEqual(focus["seconds"], 1800)

    def test_m_legacy_domain_is_not_official_history(self):
        day = self.snapshot()["daily_series"][0]
        self.assertNotIn("dominio_observado", day)
        self.assertNotIn("mastery_score", day)

    def test_r_subjects_with_different_volumes_use_raw_events(self):
        self.add_period_sample(True, attempts=10, correct=8, topic_id=1)
        self.add_period_sample(True, attempts=20, correct=10, topic_id=2)
        subjects = {item["id"]: item for item in self.snapshot()["subjects"]}
        self.assertEqual(subjects[1]["current"]["attempts"], 10)
        self.assertEqual(subjects[2]["current"]["attempts"], 20)

    def test_s_noncomparable_topic_never_becomes_decline(self):
        self.add_attempt("2026-09-10 10:00:00", False)
        topic = self.snapshot()["topics"][0]
        self.assertFalse(topic["comparable"])
        self.assertIsNone(topic["comparison"]["accuracy"]["delta_pp"])

    def test_t_custom_period_has_previous_equal_duration(self):
        period = build_period(
            start=date(2026, 9, 3), end_inclusive=date(2026, 9, 12)
        )
        data = self.snapshot(period)
        self.assertEqual(data["current_period"]["days"], 10)
        self.assertEqual(data["previous_period"]["days"], 10)
        self.assertEqual(data["previous_period"]["end_exclusive"][:10], "2026-09-03")

    def test_u_america_sao_paulo_civil_day(self):
        # 01:30 UTC ainda pertence ao dia civil anterior em Sao Paulo.
        self.add_attempt("2026-09-10T01:30:00+00:00", True)
        period = build_period(
            start=date(2026, 9, 9), end_inclusive=date(2026, 9, 9)
        )
        data = self.snapshot(period)
        self.assertEqual(data["current_metrics"]["attempts"], 1)
        self.assertEqual(data["daily_series"][0]["date"], "2026-09-09")

    def test_v_select_count_is_constant_not_n_plus_one(self):
        self.select_count = 0
        self.snapshot()
        baseline = self.select_count
        with closing(self.connect()) as con:
            for item in range(3, 23):
                con.execute("INSERT INTO topicos VALUES (?, 1, ?)", (item, f"Topico {item}"))
                con.execute(
                    "INSERT INTO topico_concurso_importancia VALUES (?, 1, 1, 0, 3)",
                    (item,),
                )
                con.execute(
                    "INSERT INTO questoes VALUES (?, ?, 1, 0)", (1000 + item, item)
                )
            con.commit()
        self.select_count = 0
        self.snapshot()
        self.assertEqual(self.select_count, baseline)

    def test_w_queue_v3_remains_the_only_decision_queue(self):
        self.assertEqual(ACTIVE_QUEUE_VERSION, "fila_inteligente_v3")
        self.assertFalse(USED_FOR_QUEUE_ORDER)


class ProgressSnapshotPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.original_path = banco.CAMINHO_BANCO
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
            self.db_path = Path(handle.name)
        banco.CAMINHO_BANCO = self.db_path
        banco.criar_banco()
        self.concurso_id = banco.obter_concurso_ativo()[0]

    def tearDown(self):
        banco.CAMINHO_BANCO = self.original_path
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            gc.collect()
        self.db_path.unlink(missing_ok=True)

    def progress(self, **updates):
        result = {
            "concurso_id": self.concurso_id,
            "snapshot_version": "syllabus_progress_v2",
            "total_topics": 10,
            "started_topics": 2,
            "topic_coverage_rate": 20.0,
            "question_coverage_rate": 30.0,
            "insufficient_evidence_topics": 8,
            "low_evidence_topics": 2,
            "moderate_evidence_topics": 0,
            "high_evidence_topics": 0,
            "sufficient_evidence_rate": 0.0,
            "consolidated_topics": 0,
            "consolidated_rate": 0.0,
            "global_mastery_score": None,
            "global_mastery_state": "insufficient_data",
        }
        result.update(updates)
        return result

    def count(self):
        with banco.conectar() as con:
            return con.execute(
                "SELECT COUNT(*) FROM progresso_snapshots_diarios"
            ).fetchone()[0]

    def test_n_first_snapshot_has_no_backfill(self):
        banco.capturar_snapshot_progresso_diario(
            snapshot=self.progress(), captured_at="2026-09-18T10:00:00-03:00"
        )
        self.assertEqual(self.count(), 1)
        with banco.conectar() as con:
            self.assertEqual(
                con.execute("SELECT MIN(data) FROM progresso_snapshots_diarios").fetchone()[0],
                "2026-09-18",
            )

    def test_o_same_daily_snapshot_is_not_rewritten(self):
        first = banco.capturar_snapshot_progresso_diario(
            snapshot=self.progress(), captured_at="2026-09-18T10:00:00-03:00"
        )
        second = banco.capturar_snapshot_progresso_diario(
            snapshot=self.progress(), captured_at="2026-09-18T14:00:00-03:00"
        )
        self.assertTrue(first["created"])
        self.assertFalse(second["created"] or second["updated"])
        self.assertEqual(self.count(), 1)

    def test_p_two_real_days_produce_two_snapshots(self):
        banco.capturar_snapshot_progresso_diario(
            snapshot=self.progress(), captured_at="2026-09-18T10:00:00-03:00"
        )
        banco.capturar_snapshot_progresso_diario(
            snapshot=self.progress(started_topics=3),
            captured_at="2026-09-19T10:00:00-03:00",
        )
        self.assertEqual(self.count(), 2)

    def test_q_catalog_change_updates_same_day_snapshot(self):
        banco.capturar_snapshot_progresso_diario(
            snapshot=self.progress(), captured_at="2026-09-18T10:00:00-03:00"
        )
        result = banco.capturar_snapshot_progresso_diario(
            snapshot=self.progress(question_coverage_rate=25.0),
            captured_at="2026-09-18T11:00:00-03:00",
        )
        self.assertTrue(result["updated"])
        self.assertEqual(self.count(), 1)
        with banco.conectar() as con:
            value = con.execute(
                "SELECT question_coverage_rate FROM progresso_snapshots_diarios"
            ).fetchone()[0]
        self.assertEqual(value, 25.0)


if __name__ == "__main__":
    unittest.main()
