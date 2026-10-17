# -*- coding: utf-8 -*-
"""Regressão da interface portátil sem abrir Tkinter nem usar VighnaStudy real."""
from __future__ import annotations
from pathlib import Path
import json
import os
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

import painel_core as core


class PainelCoreTests(unittest.TestCase):
    def test_01_parseia_zip_de_evidencias(self):
        text = r"ZIP DE EVIDENCIAS CRIADO: C:\Temp\RESULTADOS_HOMOLOGACAO_WINDOWS_1.zip"
        self.assertEqual(str(core.parse_result_path(text)),
                         r"C:\Temp\RESULTADOS_HOMOLOGACAO_WINDOWS_1.zip")

    def test_02_parseia_zip_de_diagnostico(self):
        p = core.parse_result_path(r"ZIP DE DIAGNOSTICO CRIADO: C:\Temp\falha.zip")
        self.assertEqual(str(p),r"C:\Temp\falha.zip")

    def test_03_nao_inventa_caminho(self):
        self.assertIsNone(core.parse_result_path("ETAPA_HOMOLOGADOR: Qt 100%"))

    def test_04_config_salva_reutiliza(self):
        with tempfile.TemporaryDirectory() as t:
            config = Path(t) / "config.json"
            with patch.object(core, "CONFIG", config):
                core.save_python_path(" C:/qtvenv/Scripts/python.exe ")
                self.assertEqual(core.load_config()["python_qt"], "C:/qtvenv/Scripts/python.exe")

    def test_05_config_invalida_ignorada(self):
        with tempfile.TemporaryDirectory() as t:
            config = Path(t) / "config.json"
            config.write_text("{invalido")
            with patch.object(core, "CONFIG", config):
                self.assertEqual(core.load_config(), {})

    def test_06_buscador_encontra_arquivo_recente(self):
        with tempfile.TemporaryDirectory() as t:
            folder = Path(t)
            old = folder / "RESULTADOS_HOMOLOGACAO_WINDOWS_antigo.zip"
            new = folder / "RESULTADOS_HOMOLOGACAO_WINDOWS_novo.zip"
            old.write_bytes(b"old")
            new.write_bytes(b"new")
            # Não depender da resolução do relógio do filesystem.
            os.utime(old, ns=(1_600_000_000_000_000_000,)*2)
            os.utime(new, ns=(1_600_000_100_000_000_000,)*2)
            with patch.object(core, "candidate_result_dirs", return_value=[folder]):
                result = core.latest_result(start_timestamp=0)
            self.assertIsNotNone(result)
            self.assertEqual(result.name, "RESULTADOS_HOMOLOGACAO_WINDOWS_novo.zip")

    def test_06a_desempate_de_timestamps_iguais(self):
        with tempfile.TemporaryDirectory() as t:
            folder=Path(t)
            old=folder/'RESULTADOS_HOMOLOGACAO_WINDOWS_antigo.zip'
            new=folder/'RESULTADOS_HOMOLOGACAO_WINDOWS_novo.zip'
            old.write_bytes(b'antigo')
            new.write_bytes(b'novo')
            instant=1_600_000_000_000_000_000
            os.utime(old, ns=(instant, instant))
            os.utime(new, ns=(instant, instant))
            with patch.object(core,'candidate_result_dirs',return_value=[folder]):
                first=core.latest_result()
                second=core.latest_result()
            self.assertEqual(first, second)
            self.assertEqual(first.name,'RESULTADOS_HOMOLOGACAO_WINDOWS_novo.zip')

    def test_07_nao_considera_zip_antigo(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "RESULTADOS_HOMOLOGACAO_WINDOWS_antigo.zip"
            p.write_bytes(b"antigo")
            with patch.object(core,"candidate_result_dirs",return_value=[Path(t)]):
                self.assertIsNone(core.latest_result(start_timestamp=10**11))

    def test_08_ler_resultado_aprovado(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "r.zip"
            obj = {"modo":"testes","resultados":{"falhas":0,"bloqueados":0},
                   "testes":{("qt_windows_"+k):{"status":"PASSOU"}
                             for k in ("100","125","150")}}
            with ZipFile(p,"w") as z:
                z.writestr("RESUMO_HOMOLOGACAO.json",json.dumps(obj))
            result=core.inspect_result(p)
            self.assertTrue(result["qt_aprovado"])
            self.assertEqual(result["status_instalacao"],"NAO AUTORIZADA")

    def test_09_bloqueio_nao_aprovado(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "r.zip"
            obj = {"modo":"testes","resultados":{"falhas":0,"bloqueados":1},
                   "testes":{"qt_windows":{"status":"BLOQUEADO"}}}
            with ZipFile(p,"w") as z:
                z.writestr("RESUMO_HOMOLOGACAO.json",json.dumps(obj))
            result = core.inspect_result(p)
            self.assertEqual(result["bloqueados"], 1)
            self.assertFalse(result["qt_aprovado"])

    def test_10_gera_diagnostico_de_falha(self):
        with tempfile.TemporaryDirectory() as t:
            with patch.object(core, "diagnostics_folder", return_value=Path(t)):
                file = core.emergency_report("falha sintética",["linha 1","linha 2"])
            with ZipFile(file) as z:
                self.assertIn("MANIFESTO_SHA256.json",z.namelist())
                self.assertEqual(z.testzip(),None)
                self.assertIn("falha sintética",z.read("ERRO_PAINEL.txt").decode())

    def test_11_sanitiza_caminho_de_perfil_no_diagnostico(self):
        home = str(Path.home())
        with tempfile.TemporaryDirectory() as t:
            with patch.object(core,"diagnostics_folder",return_value=Path(t)):
                file=core.emergency_report("erro: "+home,["log: "+home])
            with ZipFile(file) as z:
                self.assertNotIn(home,z.read("ERRO_PAINEL.txt").decode())
                self.assertNotIn(home,z.read("SAIDA_PROCESSO.txt").decode())

    def test_12_sugere_ambiente_qt_conhecido_quando_existir(self):
        with tempfile.TemporaryDirectory() as t:
            home = Path(t)
            py = (home / "Downloads" / "rascunho" / "Nova pasta"
                  / "homologacao_M2_INT1_RC1_20261012_024047" /
                  "qtvenv" / "Scripts" / "python.exe")
            py.parent.mkdir(parents=True)
            py.write_bytes(b"ARQUIVO_SIMULADO")
            with patch.object(core.Path, "home", return_value=home):
                self.assertEqual(core.suggested_python_path(), str(py))

    def test_13_zip_sem_resumo_e_rejeitado(self):
        with tempfile.TemporaryDirectory() as t:
            file=Path(t)/"r.zip"
            with ZipFile(file,"w") as z:z.writestr("outro.txt","oi")
            with self.assertRaises(ValueError):
                core.inspect_result(file)


if __name__=="__main__":
    unittest.main(verbosity=2)
