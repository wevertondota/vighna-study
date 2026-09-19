from pathlib import Path
import tempfile
import unittest

from importador_txt import ler_arquivo_txt_questoes


TEXTO_VPQ = """VIGHNA PDF — VPQ 1.1\nDISCIPLINA: Direito Administrativo\nTÍTULO: Conceito\nQUESTÃO 1\nEnunciado\nA) A\nB) B\nC) C\nD) D\nGABARITO: A\n"""


class ImportadorTxtTests(unittest.TestCase):
    def _arquivo(self, nome, conteudo):
        pasta = tempfile.TemporaryDirectory()
        caminho = Path(pasta.name) / nome
        caminho.write_bytes(conteudo)
        self.addCleanup(pasta.cleanup)
        return caminho

    def test_le_utf8_com_vpq(self):
        caminho = self._arquivo("questoes.txt", TEXTO_VPQ.encode("utf-8"))
        dados = ler_arquivo_txt_questoes(caminho)
        self.assertEqual(dados["arquivo"], "questoes.txt")
        self.assertEqual(dados["codificacao"], "UTF-8")
        self.assertIn("VIGHNA PDF — VPQ 1.1", dados["texto"])
        self.assertEqual(dados["faixas_paginas"], [])

    def test_le_windows_1252(self):
        texto = "QUESTÃO 1\r\nA) ação\r\nB) opção\r\nGABARITO: A"
        caminho = self._arquivo("ansi.txt", texto.encode("cp1252"))
        dados = ler_arquivo_txt_questoes(caminho)
        self.assertEqual(dados["codificacao"], "Windows-1252")
        self.assertNotIn("\r", dados["texto"])
        self.assertIn("ação", dados["texto"])

    def test_le_utf16_com_bom(self):
        caminho = self._arquivo("utf16.txt", TEXTO_VPQ.encode("utf-16"))
        dados = ler_arquivo_txt_questoes(caminho)
        self.assertEqual(dados["codificacao"], "UTF-16")
        self.assertIn("DISCIPLINA", dados["texto"])

    def test_rejeita_extensao_diferente(self):
        caminho = self._arquivo("questoes.md", b"QUESTAO 1")
        with self.assertRaises(ValueError):
            ler_arquivo_txt_questoes(caminho)

    def test_rejeita_arquivo_vazio(self):
        caminho = self._arquivo("vazio.txt", b"")
        with self.assertRaises(ValueError):
            ler_arquivo_txt_questoes(caminho)


if __name__ == "__main__":
    unittest.main()
