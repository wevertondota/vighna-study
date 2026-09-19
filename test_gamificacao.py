import sqlite3
import tempfile
import unittest
from pathlib import Path

from gamificacao import build_gamification_snapshot, ensure_gamification_schema


class GamificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "test.db"
        con = sqlite3.connect(self.db)
        con.executescript(
            """
            CREATE TABLE tentativas_questoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                questao_id INTEGER,
                concurso_id INTEGER,
                respondida_em TEXT NOT NULL,
                correta INTEGER
            );
            CREATE TABLE revisoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topico_id INTEGER,
                concurso_id INTEGER,
                data TEXT NOT NULL,
                realizada_em TEXT,
                questoes INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE sessoes_foco (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inicio TEXT NOT NULL,
                duracao_efetiva INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        ensure_gamification_schema(con)
        con.commit()
        con.close()

    def tearDown(self):
        self.tmp.cleanup()

    def connect(self):
        return sqlite3.connect(self.db)

    def regularity(self, current=0, best=0):
        return {"current_streak_days": current, "best_streak_days": best}

    def progress(self, coverage=0.0, consolidated=0):
        topics = [
            {
                "topico_id": i + 1,
                "disciplina": "D",
                "topico": f"T{i+1}",
                "consolidacao_certificada": True,
            }
            for i in range(consolidated)
        ]
        return {
            "question_coverage_rate": coverage,
            "consolidated_topics": consolidated,
            "topicos": topics,
        }

    def snapshot(self, progress=None, regularity=None):
        return build_gamification_snapshot(
            self.connect,
            1,
            progress or self.progress(),
            regularity or self.regularity(),
            synchronize=True,
        ).to_dict()

    def test_acertos_isolados_nao_geram_xp_por_acerto(self):
        con = self.connect()
        for qid in range(1, 11):
            con.execute(
                "INSERT INTO tentativas_questoes (questao_id, concurso_id, respondida_em, correta) VALUES (?, 1, ?, 1)",
                (qid, "2026-09-18T10:00:00"),
            )
        con.commit(); con.close()
        snap = self.snapshot()
        self.assertEqual(snap["total_xp"], 20)
        self.assertEqual(snap["breakdown"]["Dias de estudo"], 20)
        self.assertEqual(snap["breakdown"]["Recuperações"], 0)

    def test_sincronizacao_e_idempotente(self):
        con = self.connect()
        con.execute(
            "INSERT INTO tentativas_questoes (questao_id, concurso_id, respondida_em, correta) VALUES (1,1,'2026-09-18T10:00:00',1)"
        )
        con.commit(); con.close()
        first = self.snapshot()
        second = self.snapshot()
        self.assertEqual(first["total_xp"], second["total_xp"])
        self.assertEqual(first["events_count"], second["events_count"])

    def test_erro_recuperado_pontua_uma_unica_vez(self):
        con = self.connect()
        con.execute(
            "INSERT INTO tentativas_questoes (questao_id, concurso_id, respondida_em, correta) VALUES (7,1,'2026-09-17T10:00:00',0)"
        )
        con.execute(
            "INSERT INTO tentativas_questoes (questao_id, concurso_id, respondida_em, correta) VALUES (7,1,'2026-09-18T10:00:00',1)"
        )
        con.execute(
            "INSERT INTO tentativas_questoes (questao_id, concurso_id, respondida_em, correta) VALUES (7,1,'2026-09-18T11:00:00',1)"
        )
        con.commit(); con.close()
        snap = self.snapshot()
        self.assertEqual(snap["recovered_questions"], 1)
        self.assertEqual(snap["breakdown"]["Recuperações"], 30)

    def test_revisao_qualificada_e_marco(self):
        con = self.connect()
        con.execute(
            "INSERT INTO revisoes (topico_id, concurso_id, data, realizada_em, questoes) VALUES (1,1,'2026-09-18','2026-09-18T12:00:00',10)"
        )
        con.commit(); con.close()
        snap = self.snapshot()
        self.assertEqual(snap["qualified_reviews"], 1)
        self.assertEqual(snap["breakdown"]["Revisões"], 15)
        self.assertTrue(any(a["key"] == "achievement:revisions:1" and a["earned"] for a in snap["achievements"]))

    def test_marco_de_cobertura_nao_e_perdido_quando_catalogo_cresce(self):
        first = self.snapshot(progress=self.progress(coverage=27.0))
        self.assertTrue(any(a["key"].endswith(":25") and a["earned"] for a in first["achievements"] if a["category"] == "Cobertura"))
        xp = first["total_xp"]
        second = self.snapshot(progress=self.progress(coverage=5.0))
        self.assertEqual(second["total_xp"], xp)
        self.assertTrue(any(a["key"].endswith(":25") and a["earned"] for a in second["achievements"] if a["category"] == "Cobertura"))

    def test_consolidacao_pontua_sem_afetar_metricas_academicas(self):
        snap = self.snapshot(progress=self.progress(consolidated=1))
        self.assertEqual(snap["consolidated_topics"], 1)
        self.assertEqual(snap["breakdown"]["Consolidações"], 80)
        self.assertTrue(any(a["category"] == "Consolidação" and a["target"] == 1 and a["earned"] for a in snap["achievements"]))

    def test_foco_curto_nao_cria_dia_de_estudo(self):
        con = self.connect()
        con.execute("INSERT INTO sessoes_foco (inicio, duracao_efetiva) VALUES ('2026-09-18T10:00:00', 299)")
        con.commit(); con.close()
        snap = self.snapshot()
        self.assertEqual(snap["active_study_days"], 0)
        self.assertEqual(snap["total_xp"], 0)

    def test_foco_valido_cria_um_dia_de_estudo(self):
        con = self.connect()
        con.execute("INSERT INTO sessoes_foco (inicio, duracao_efetiva) VALUES ('2026-09-18T10:00:00', 300)")
        con.commit(); con.close()
        snap = self.snapshot()
        self.assertEqual(snap["active_study_days"], 1)
        self.assertEqual(snap["breakdown"]["Dias de estudo"], 20)

    def test_nivel_usa_faixa_transparente_de_250_xp(self):
        con = self.connect()
        ensure_gamification_schema(con)
        con.execute(
            "INSERT INTO gamificacao_eventos (chave,tipo,pontos,titulo,detalhe,ocorrido_em,versao) VALUES ('manual','test',500,'x','','2026-09-18T10:00:00','gamificacao_v1')"
        )
        con.commit(); con.close()
        snap = self.snapshot()
        self.assertEqual(snap["level"], 3)
        self.assertEqual(snap["level_progress_xp"], 0)


if __name__ == "__main__":
    unittest.main()
