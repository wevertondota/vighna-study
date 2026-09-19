import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path

from regularidade import build_regularity_snapshot


class RegularidadeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "teste.db"
        conn = sqlite3.connect(self.db)
        conn.executescript(
            """
            CREATE TABLE tentativas_questoes (
                id INTEGER PRIMARY KEY,
                respondida_em TEXT NOT NULL
            );
            CREATE TABLE revisoes (
                id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                realizada_em TEXT,
                questoes INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE sessoes_foco (
                id INTEGER PRIMARY KEY,
                inicio TEXT NOT NULL,
                duracao_efetiva INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        self.tmp.cleanup()

    def connect(self):
        return sqlite3.connect(self.db)

    def add_attempt(self, when):
        c = self.connect()
        try:
            c.execute("INSERT INTO tentativas_questoes(respondida_em) VALUES (?)", (when,))
            c.commit()
        finally:
            c.close()

    def add_review(self, when, questions=10):
        c = self.connect()
        try:
            c.execute(
                "INSERT INTO revisoes(data, realizada_em, questoes) VALUES (?, ?, ?)",
                (when[:10], when, questions),
            )
            c.commit()
        finally:
            c.close()

    def add_focus(self, when, seconds):
        c = self.connect()
        try:
            c.execute(
                "INSERT INTO sessoes_foco(inicio, duracao_efetiva) VALUES (?, ?)",
                (when, seconds),
            )
            c.commit()
        finally:
            c.close()

    def snapshot(self, **kwargs):
        return build_regularity_snapshot(
            self.connect,
            as_of=date(2026, 9, 18),
            **kwargs,
        ).to_dict()

    def test_empty_history(self):
        snap = self.snapshot()
        self.assertEqual(snap["current_streak_days"], 0)
        self.assertEqual(snap["best_streak_days"], 0)
        self.assertEqual(snap["active_days_30"], 0)
        self.assertEqual(snap["current_streak_state"], "no_history")
        self.assertIsNone(snap["regularity_score"])

    def test_streak_remains_open_when_today_is_pending(self):
        for day in (15, 16, 17):
            self.add_attempt(f"2026-09-{day:02d} 10:00:00")
        snap = self.snapshot()
        self.assertEqual(snap["current_streak_days"], 3)
        self.assertEqual(snap["current_streak_state"], "pending_today")
        self.assertEqual(snap["best_streak_days"], 3)
        self.assertEqual(snap["active_days_7"], 3)

    def test_today_extends_streak(self):
        for day in (16, 17, 18):
            self.add_attempt(f"2026-09-{day:02d} 10:00:00")
        snap = self.snapshot()
        self.assertEqual(snap["current_streak_days"], 3)
        self.assertEqual(snap["current_streak_state"], "active_today")

    def test_broken_streak(self):
        self.add_attempt("2026-09-15 10:00:00")
        snap = self.snapshot()
        self.assertEqual(snap["current_streak_days"], 0)
        self.assertEqual(snap["current_streak_state"], "broken")

    def test_focus_under_five_minutes_does_not_count(self):
        self.add_focus("2026-09-18 08:00:00", 299)
        snap = self.snapshot()
        self.assertEqual(snap["active_days_7"], 0)
        self.add_focus("2026-09-18 09:00:00", 300)
        snap = self.snapshot()
        self.assertEqual(snap["active_days_7"], 1)
        self.assertEqual(snap["source_totals"]["focus_seconds"], 300)

    def test_review_with_questions_counts(self):
        self.add_review("2026-09-18 12:00:00", 5)
        snap = self.snapshot()
        self.assertEqual(snap["active_days_7"], 1)
        self.assertEqual(snap["source_totals"]["reviews"], 1)

    def test_review_without_questions_does_not_count(self):
        self.add_review("2026-09-18 12:00:00", 0)
        snap = self.snapshot()
        self.assertEqual(snap["active_days_7"], 0)

    def test_same_day_multiple_sources_counts_once(self):
        self.add_attempt("2026-09-18 10:00:00")
        self.add_review("2026-09-18 11:00:00", 10)
        self.add_focus("2026-09-18 12:00:00", 600)
        snap = self.snapshot()
        self.assertEqual(snap["active_days_7"], 1)
        self.assertEqual(len(snap["activity_days"]), 1)

    def test_target_disabled_does_not_invent_score(self):
        self.add_attempt("2026-09-18 10:00:00")
        snap = self.snapshot(target_days_per_week=0)
        self.assertIsNone(snap["regularity_score"])
        self.assertEqual(snap["regularity_state"], "disabled")
        self.assertIsNone(snap["current_week_target_rate"])

    def test_short_history_score_is_provisional(self):
        for day in (15, 16, 17):
            self.add_attempt(f"2026-09-{day:02d} 10:00:00")
        snap = self.snapshot(target_days_per_week=5)
        self.assertIsNotNone(snap["regularity_score"])
        self.assertEqual(snap["regularity_state"], "provisional")
        self.assertEqual(snap["current_week_active_days"], 3)
        self.assertEqual(snap["target_days_per_week"], 5)

    def test_best_streak_and_gap(self):
        for day in (1, 2, 3, 7, 8, 17):
            self.add_attempt(f"2026-09-{day:02d} 10:00:00")
        snap = self.snapshot()
        self.assertEqual(snap["best_streak_days"], 3)
        self.assertEqual(snap["longest_gap_days"], 8)

    def test_week_rows_are_ordered_and_current_last(self):
        self.add_attempt("2026-09-17 10:00:00")
        snap = self.snapshot(calendar_weeks=8)
        self.assertEqual(len(snap["weeks"]), 8)
        self.assertTrue(snap["weeks"][-1]["current"])
        self.assertEqual(len(snap["weeks"][-1]["days"]), 7)

    def test_weekday_distribution(self):
        # 2026-09-14 = segunda; 2026-09-15 = terça.
        self.add_attempt("2026-09-14 10:00:00")
        self.add_attempt("2026-09-15 10:00:00")
        snap = self.snapshot()
        dist = {item["label"]: item["active_days"] for item in snap["weekday_distribution"]}
        self.assertEqual(dist["Seg"], 1)
        self.assertEqual(dist["Ter"], 1)


if __name__ == "__main__":
    unittest.main()
