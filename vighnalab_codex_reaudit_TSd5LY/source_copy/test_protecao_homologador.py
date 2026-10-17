# -*- coding: utf-8 -*-
"""Testes internos de proteção do homologador; sem importar main.py nem banco."""
import copy
import io
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import homologador_windows as h


class ContratosSegurancaHomologador(unittest.TestCase):
    def test_01_rejeita_percurso_ascendente(self):
        self.assertTrue(h.is_bad_path("../versao.py"))
        self.assertTrue(h.is_bad_path("ui/../main.py"))

    def test_02a_rejeita_nomes_ambiguos(self):
        self.assertTrue(h.is_bad_path("ui//settings.py"))
        self.assertTrue(h.is_bad_path("ui/./settings.py"))

    def test_02_rejeita_caminho_absoluto(self):
        self.assertTrue(h.is_bad_path("/etc/passwd"))
        self.assertTrue(h.is_bad_path("C:/estudos.db"))

    def test_03_rejeita_banco_e_exe(self):
        for name in ("estudos.db", "app.exe", "backup.sqlite3",
                     "estudos.db-wal", "dados.dll", "lib.pyd"):
            self.assertTrue(h.is_bad_path(name), name)

    def test_04_aceita_fontes_autorizadas(self):
        for name in ("main.py", "ui/settings_search.py", "assets/config_gear.png"):
            self.assertFalse(h.is_bad_path(name), name)

    def test_05_rejeita_symlink_em_zip(self):
        info = zipfile.ZipInfo("ui/ponte.py")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        with self.assertRaises(ValueError):
            h.verify_package_member(info, "ui/ponte.py")

    def test_06_rejeita_membro_com_nome_duplicado(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "dup.zip"
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("MAIN.py", b"alpha")
                z.writestr("main.py", b"beta")
            with self.assertRaises(ValueError):
                h.checked_archive(p)

    def test_07_rejeita_zip_slip(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "slip.zip"
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("../fora.py", b"conteudo")
            with self.assertRaises(ValueError):
                h.checked_archive(p)

    def test_08_rejeita_conteudo_executavel(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "exe.zip"
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("VighnaStudy.exe", b"MZ")
            with self.assertRaises(ValueError):
                h.checked_archive(p)

    def test_09_rejeita_hash_incorreto_do_pacote(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t)
            (p / "entrada.txt").write_text("ok")
            (p / "MANIFESTO_ENTRADAS_SHA256.json").write_text(json.dumps({
                "arquivos": {"entrada.txt": "0"*64}}))
            with patch.object(h, "KIT", p):
                with self.assertRaises(ValueError):
                    h.verify_inputs()

    def test_10_hash_real_de_entrada(self):
        meta = h.verify_inputs()
        self.assertGreaterEqual(len(meta["arquivos"]), 10)

    def test_11_candidato_m2_exatamente_rc2(self):
        b = h.checked_archive(h.KIT / "insumos" / h.BASE)
        p = h.checked_archive(h.KIT / "insumos" / h.PATCH)
        r = h.checked_archive(h.KIT / "insumos" / h.RC2, prefix="codigo/")
        self.assertEqual(h.inspect_static(b, p, r)["status"], "PASSOU")

    def test_12_rejeita_build_invalido(self):
        b = h.checked_archive(h.KIT / "insumos" / h.BASE)
        p = h.checked_archive(h.KIT / "insumos" / h.PATCH)
        r = h.checked_archive(h.KIT / "insumos" / h.RC2, prefix="codigo/")
        p["manifest.json"] = p["manifest.json"].replace(
            h.EXPECTED_TARGET.encode(), b"build-perigoso")
        with self.assertRaises(AssertionError):
            h.inspect_static(b, p, r)

    def test_13_arquivo_spec_permanece_fora_da_atualizacao(self):
        p = h.checked_archive(h.KIT / "insumos" / h.PATCH)
        self.assertNotIn("VighnaStudy.spec", p)

    def test_14_arquivos_pessoais_nao_existem_nos_insumos(self):
        for name in (h.BASE, h.PATCH, h.RC2):
            prefix = "codigo/" if name == h.RC2 else ""
            items = h.checked_archive(h.KIT / "insumos" / name, prefix=prefix)
            for rel in items:
                self.assertFalse(rel.lower().endswith(h.FORBIDDEN_SUFFIXES), rel)

    def test_15_saida_zip_com_hashs_verificaveis(self):
        with tempfile.TemporaryDirectory() as t:
            evidence = Path(t) / "evid"
            evidence.mkdir()
            (evidence / "teste.log").write_text("SEM DADOS PESSOAIS")
            target = Path(t) / "saida.zip"
            h.report_zip(evidence, target, {"decisao": "NAO_HOMOLOGADO"})
            with zipfile.ZipFile(target) as z:
                manifest = json.loads(z.read("MANIFESTO_SHA256.json"))
                for name, digest in manifest.items():
                    self.assertEqual(h.digest(z.read(name)), digest)

    def test_16a_bloqueia_pasta_do_vighna_real(self):
        with tempfile.TemporaryDirectory() as t:
            kit = Path(t) / "kit"
            kit.mkdir()
            (Path(t) / "estudos.db").write_bytes(b"PROIBIDO")
            with patch.object(h, "KIT", kit):
                with self.assertRaises(ValueError):
                    h.ensure_not_user_installation()

    def test_16b_falha_preflight_gera_zip_diagnostico(self):
        with tempfile.TemporaryDirectory(prefix="vighna_v11_diagnostico_") as tmp:
            root = Path(tmp)
            with (
                patch.object(h, "KIT", root),
                patch.object(h, "evidence_destination", return_value=root),
                patch.object(h, "preflight_selftest", side_effect=ValueError("falha QA simulada")),
                patch.object(h.sys, "platform", "win32"),
            ):
                status = h.do_run("testes")
            self.assertEqual(status, 1)
            generated = list(root.glob("RESULTADOS_HOMOLOGACAO_WINDOWS_*.zip"))
            self.assertEqual(len(generated), 1, "Falha inicial deve produzir ZIP")
            with zipfile.ZipFile(generated[0]) as z:
                self.assertIsNone(z.testzip())
                summary = json.loads(z.read("RESUMO_HOMOLOGACAO.json"))
                self.assertEqual(summary["erro"]["tipo"], "ValueError")
                self.assertFalse(summary["instalacao_autorizada"])
                self.assertIn("erro_diagnostico_sanitizado.txt", z.namelist())

    def test_16_verificacao_local_reproduzivel(self):
        self.assertEqual(h.preflight_selftest()["status"], "PASSOU")


if __name__ == "__main__":
    unittest.main()
