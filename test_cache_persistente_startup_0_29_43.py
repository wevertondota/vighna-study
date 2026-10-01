import sqlite3
import tempfile
import time
import unittest
from contextlib import closing
from pathlib import Path

import cache_persistente as cp
from inteligencia import CacheAnalitico


class CachePersistenteStartupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "cache.db"
        self._factory = lambda: sqlite3.connect(self.db)
        with closing(self._factory()) as con, con:
            con.execute("CREATE TABLE questoes (id INTEGER PRIMARY KEY, enunciado TEXT)")
            cp.garantir_schema_cache_persistente(con)
        cp.invalidar_memoria()

    def tearDown(self):
        cp.invalidar_memoria()
        self.tmp.cleanup()

    def test_roundtrip_preserva_tipos_relevantes(self):
        esperado = {
            7: ("a", 2),
            "datas": {"hoje": None},
            "conjunto": {1, 2, 3},
        }
        chamadas = {"n": 0}

        def carregar():
            chamadas["n"] += 1
            return esperado

        primeira = cp.obter_ou_calcular(
            self._factory, "tipos", carregar, concurso_id=1, dominios=("catalogo",)
        )
        cp.invalidar_memoria()
        segunda = cp.obter_ou_calcular(
            self._factory, "tipos", carregar, concurso_id=1, dominios=("catalogo",)
        )
        self.assertEqual(primeira, esperado)
        self.assertEqual(segunda, esperado)
        self.assertIsInstance(segunda[7], tuple)
        self.assertIsInstance(segunda["conjunto"], set)
        self.assertEqual(chamadas["n"], 1)

    def test_mutacao_da_fonte_invalida_cache(self):
        chamadas = {"n": 0}

        def carregar():
            chamadas["n"] += 1
            with closing(self._factory()) as con, con:
                return con.execute("SELECT COUNT(*) FROM questoes").fetchone()[0]

        self.assertEqual(
            cp.obter_ou_calcular(
                self._factory, "contagem", carregar,
                concurso_id=1, dominios=("catalogo",)
            ),
            0,
        )
        cp.invalidar_memoria()
        self.assertEqual(
            cp.obter_ou_calcular(
                self._factory, "contagem", carregar,
                concurso_id=1, dominios=("catalogo",)
            ),
            0,
        )
        self.assertEqual(chamadas["n"], 1)

        with closing(self._factory()) as con, con:
            con.execute("INSERT INTO questoes (enunciado) VALUES ('nova')")
        cp.invalidar_memoria()
        self.assertEqual(
            cp.obter_ou_calcular(
                self._factory, "contagem", carregar,
                concurso_id=1, dominios=("catalogo",)
            ),
            1,
        )
        self.assertEqual(chamadas["n"], 2)

    def test_suspensao_preserva_revisao_durante_migracao_idempotente(self):
        with closing(self._factory()) as con, con:
            antes = dict(cp.obter_revisoes(con, ("catalogo",)))
            cp.suspender_revisoes_cache(con, True)
            con.execute("INSERT INTO questoes (id, enunciado) VALUES (1, 'x')")
            con.execute("UPDATE questoes SET enunciado='x' WHERE id=1")
            cp.suspender_revisoes_cache(con, False)
            depois = dict(cp.obter_revisoes(con, ("catalogo",)))
        self.assertEqual(antes, depois)

    def test_fase_estavel_ignora_ttl_mas_respeita_invalidacao(self):
        cache = CacheAnalitico(ttl_padrao=0.0)
        chamadas = {"n": 0}

        def carregar():
            chamadas["n"] += 1
            return chamadas["n"]

        cache.iniciar_fase_estavel()
        try:
            self.assertEqual(cache.obter("x", carregar), 1)
            time.sleep(0.002)
            self.assertEqual(cache.obter("x", carregar), 1)
            cache.invalidar("x")
            self.assertEqual(cache.obter("x", carregar), 2)
        finally:
            cache.finalizar_fase_estavel()
        self.assertEqual(chamadas["n"], 2)

    def test_versao_da_otimizacao(self):
        versao = (Path(__file__).resolve().parent / "versao.py").read_text(encoding="utf-8")
        self.assertIn('VIGHNA_VERSION = "0.29.43"', versao)
        self.assertIn('VIGHNA_BUILD = "startup-warm-cache-v1"', versao)
        self.assertIn('VIGHNA_SCHEMA = 25', versao)


if __name__ == "__main__":
    unittest.main()
