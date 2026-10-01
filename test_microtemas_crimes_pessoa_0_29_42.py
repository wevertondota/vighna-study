"""Testes do piloto de microtemas e refinamento de pontos fracos (0.29.42)."""

from __future__ import annotations

import gc
import shutil
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

import banco
import microtemas


ROOT = Path(__file__).resolve().parent


class MicrotemasCrimesPessoaTests(unittest.TestCase):
    def setUp(self):
        self.original = banco.CAMINHO_BANCO
        self.temp = tempfile.TemporaryDirectory(prefix="vighna_microtemas_")
        self.db = Path(self.temp.name) / "estudos.db"
        shutil.copy2(ROOT / "estudos.db", self.db)
        banco.CAMINHO_BANCO = self.db
        banco.criar_banco()
        self.concurso_id = 40
        self.topico_id = 22

    def tearDown(self):
        banco.CAMINHO_BANCO = self.original
        gc.collect()
        self.temp.cleanup()

    def test_catalogo_cobre_todas_as_alternativas_e_preserva_ciclo(self):
        with closing(banco.conectar()) as con:
            diag = microtemas.diagnostico_piloto(con, self.topico_id)
            self.assertEqual(diag["questoes_ativas"], 353)
            self.assertEqual(diag["alternativas_ativas"], 1765)
            self.assertEqual(diag["microtemas_ativos"], 1094)
            self.assertEqual(diag["mapeamentos_alternativas"], 1765)
            self.assertEqual(diag["lacunas_mapeamento"], 0)
            self.assertEqual(con.execute(
                "SELECT COUNT(*) FROM tentativas_questoes WHERE topico_id_snapshot=22"
            ).fetchone()[0], 131)
            estados = dict(con.execute(
                "SELECT estado, COUNT(*) FROM ciclo_questoes_itens WHERE ciclo_id=5 GROUP BY estado"
            ).fetchall())
            self.assertEqual(estados.get("respondida"), 131)
            self.assertEqual(estados.get("pendente"), 222)
            self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_backfill_liga_evidencia_a_versao_historica_quando_snapshot_mudou(self):
        with closing(banco.conectar()) as con:
            historicas = con.execute(
                """
                SELECT COUNT(DISTINCT tm.questao_versao_id)
                FROM tentativa_microtemas tm
                JOIN questao_versoes qv ON qv.id=tm.questao_versao_id
                WHERE qv.atual=0 AND qv.motivo='snapshot_tentativa_historica'
                """
            ).fetchone()[0]
            self.assertGreater(historicas, 0)
            self.assertEqual(con.execute(
                "SELECT COUNT(DISTINCT tentativa_id) FROM tentativa_microtemas"
            ).fetchone()[0], 131)

    def _dados_questao(self, qid):
        with closing(banco.conectar()) as con:
            q = con.execute(
                "SELECT topico_id,capitulo_id,enunciado,explicacao,banca,ano,fonte,dificuldade,tipo_questao FROM questoes WHERE id=?",
                (qid,),
            ).fetchone()
            alts = [
                {"letra": r[0], "texto": r[1], "correta": bool(r[2])}
                for r in con.execute(
                    "SELECT letra,texto,correta FROM alternativas_questoes WHERE questao_id=? ORDER BY ordem,letra",
                    (qid,),
                ).fetchall()
            ]
        return q, alts

    def test_edicao_superficial_cria_versao_e_preserva_mapeamento(self):
        qid = 5774
        q, alts = self._dados_questao(qid)
        with closing(banco.conectar()) as con:
            antes_map = con.execute(
                "SELECT COUNT(*) FROM alternativa_microtemas WHERE questao_id=?", (qid,)
            ).fetchone()[0]
            antes_ver = con.execute(
                "SELECT COUNT(*) FROM questao_versoes WHERE questao_id=?", (qid,)
            ).fetchone()[0]
        alts[0]["texto"] = alts[0]["texto"].rstrip(". ") + "."
        self.assertTrue(banco.atualizar_questao(
            qid, q[0], q[2], alts, q[3], q[4], q[5], q[6], q[7], True, q[1], q[8]
        ))
        with closing(banco.conectar()) as con:
            depois_map = con.execute(
                "SELECT COUNT(*) FROM alternativa_microtemas WHERE questao_id=?", (qid,)
            ).fetchone()[0]
            depois_ver = con.execute(
                "SELECT COUNT(*) FROM questao_versoes WHERE questao_id=?", (qid,)
            ).fetchone()[0]
            pend = con.execute(
                "SELECT COUNT(*) FROM microtema_mapeamento_pendencias WHERE questao_id=? AND resolvida=0",
                (qid,),
            ).fetchone()[0]
        self.assertEqual(depois_map, antes_map)
        self.assertGreaterEqual(depois_ver, antes_ver)
        self.assertEqual(pend, 0)

    def test_edicao_semantica_remove_mapeamento_inseguro_e_abre_pendencia(self):
        qid = 5774
        q, alts = self._dados_questao(qid)
        letra = alts[0]["letra"]
        alts[0]["texto"] = "Conteúdo totalmente distinto, criado apenas para testar mudança semântica deliberada."
        self.assertTrue(banco.atualizar_questao(
            qid, q[0], q[2], alts, q[3], q[4], q[5], q[6], q[7], True, q[1], q[8]
        ))
        with closing(banco.conectar()) as con:
            self.assertEqual(con.execute(
                "SELECT COUNT(*) FROM alternativa_microtemas WHERE questao_id=? AND letra=?", (qid, letra)
            ).fetchone()[0], 0)
            self.assertEqual(con.execute(
                "SELECT COUNT(*) FROM microtema_mapeamento_pendencias WHERE questao_id=? AND letra=? AND resolvida=0",
                (qid, letra),
            ).fetchone()[0], 1)
            self.assertGreaterEqual(con.execute(
                "SELECT COUNT(*) FROM questao_versoes WHERE questao_id=?", (qid,)
            ).fetchone()[0], 2)

    def test_exclusao_permanente_com_historico_vira_soft_delete(self):
        qid = 5774
        self.assertTrue(banco.excluir_questao_permanentemente(qid))
        with closing(banco.conectar()) as con:
            row = con.execute("SELECT ativa,excluida FROM questoes WHERE id=?", (qid,)).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(tuple(row), (0, 1))
            self.assertGreater(con.execute(
                "SELECT COUNT(*) FROM tentativas_questoes WHERE COALESCE(questao_id_snapshot,questao_id)=?", (qid,)
            ).fetchone()[0], 0)

    def test_refinamento_so_abre_com_dominio_alto_e_prioriza_fragilidade(self):
        with closing(banco.conectar()) as con, con:
            bloqueado = microtemas.selecionar_refinamento(
                con, self.concurso_id, self.topico_id, 89.9, quantidade=5
            )
            self.assertFalse(bloqueado["elegivel"])

            mid = con.execute(
                """
                SELECT m.id FROM microtemas m
                JOIN questao_microtemas qm ON qm.microtema_id=m.id
                JOIN questoes q ON q.id=qm.questao_id
                WHERE m.topico_id=? AND q.ativa=1 AND COALESCE(q.excluida,0)=0
                ORDER BY m.id LIMIT 1
                """, (self.topico_id,)
            ).fetchone()[0]
            con.execute(
                """
                UPDATE microtema_estado
                SET fragilidade=0, proxima_revisao=date('now','+365 day'), estado='consolidado'
                WHERE concurso_id=? AND microtema_id IN (
                    SELECT id FROM microtemas WHERE topico_id=?
                )
                """,
                (self.concurso_id, self.topico_id),
            )
            con.execute(
                """
                INSERT INTO microtema_estado(
                    concurso_id,microtema_id,evidencias,peso_positivo,peso_negativo,
                    dominio_atual,fragilidade,confianca,ultima_evidencia,ultimo_erro,
                    proxima_revisao,estado
                ) VALUES(?,?,3,1,2,40,95,100,datetime('now','localtime'),datetime('now','localtime'),date('now'),'fragil')
                ON CONFLICT(concurso_id,microtema_id) DO UPDATE SET
                    fragilidade=95,confianca=100,proxima_revisao=date('now'),estado='fragil'
                """, (self.concurso_id, int(mid))
            )
            aberto = microtemas.selecionar_refinamento(
                con, self.concurso_id, self.topico_id, 95.0, quantidade=5
            )
            self.assertTrue(aberto["elegivel"])
            self.assertTrue(aberto["fila"])
            self.assertTrue(any(
                any(m["id"] == int(mid) for m in item["microtemas"])
                for item in aberto["fila"]
            ))


if __name__ == "__main__":
    unittest.main(verbosity=2)
