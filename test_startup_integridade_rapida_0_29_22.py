import sqlite3
import tempfile
import unittest
from pathlib import Path

from backup import verificar_integridade_banco


class StartupIntegridadeRapidaTests(unittest.TestCase):
    def test_quick_check_aceita_banco_integro(self):
        with tempfile.TemporaryDirectory() as pasta:
            db = Path(pasta) / "teste.db"
            with sqlite3.connect(db) as con:
                con.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, valor TEXT)")
                con.execute("INSERT INTO t(valor) VALUES ('ok')")
            ok, msg = verificar_integridade_banco(db)
            self.assertTrue(ok, msg)

    def test_integrity_check_completo_permanece_disponivel(self):
        with tempfile.TemporaryDirectory() as pasta:
            db = Path(pasta) / "teste.db"
            with sqlite3.connect(db) as con:
                con.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, valor TEXT)")
                con.execute("INSERT INTO t(valor) VALUES ('ok')")
            ok, msg = verificar_integridade_banco(db, completo=True)
            self.assertTrue(ok, msg)

    def test_banco_truncado_e_bloqueado(self):
        with tempfile.TemporaryDirectory() as pasta:
            db = Path(pasta) / "quebrado.db"
            db.write_bytes(b"SQLite format 3\\x00" + b"x" * 100)
            ok, _ = verificar_integridade_banco(db)
            self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
