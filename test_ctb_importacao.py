import gc
import tempfile
import unittest
from pathlib import Path

import banco
from importador_pdf import analisar_texto_questoes_pdf


class CTBNomenclatureTests(unittest.TestCase):
    def setUp(self):
        self.original_path = banco.CAMINHO_BANCO
        self.tempdir = tempfile.TemporaryDirectory(prefix="vighna_ctb_")
        banco.CAMINHO_BANCO = Path(self.tempdir.name) / "estudos.db"
        banco.criar_banco()

    def tearDown(self):
        banco.CAMINHO_BANCO = self.original_path
        gc.collect()
        self.tempdir.cleanup()

    def test_new_database_uses_official_ctb_name_and_sigla_alias(self):
        disciplinas = banco.listar_disciplinas(somente_incluidas=False)
        nomes = {nome for _, nome in disciplinas}
        self.assertIn(banco.CTB_NOME_OFICIAL, nomes)
        self.assertNotIn("CTB", nomes)

        oficial_id = banco.resolver_disciplina_id_estrutural(
            banco.CTB_NOME_OFICIAL
        )
        self.assertIsNotNone(oficial_id)
        self.assertEqual(
            oficial_id,
            banco.resolver_disciplina_id_estrutural("CTB"),
        )
        self.assertEqual(
            oficial_id,
            banco.resolver_disciplina_id_estrutural(
                "Código de Trânsito Brasileiro (CTB)"
            ),
        )
        self.assertTrue(banco.eh_disciplina_ctb("CTB"))
        self.assertTrue(
            banco.eh_disciplina_ctb("Código de Trânsito Brasileiro (CTB)")
        )

    def test_legacy_ctb_name_is_migrated_without_changing_identity(self):
        disciplina_id = banco.resolver_disciplina_id_estrutural("CTB")
        with banco.conectar() as conexao:
            conexao.execute(
                "UPDATE disciplinas SET nome = 'CTB' WHERE id = ?",
                (disciplina_id,),
            )
        banco.criar_banco()

        with banco.conectar() as conexao:
            linha = conexao.execute(
                "SELECT nome FROM disciplinas WHERE id = ?",
                (disciplina_id,),
            ).fetchone()
        self.assertEqual(linha[0], banco.CTB_NOME_OFICIAL)
        self.assertEqual(
            disciplina_id,
            banco.resolver_disciplina_id_estrutural("CTB"),
        )

    def test_ctb_chapter_resolves_as_structural_topic(self):
        disciplina_id = banco.resolver_disciplina_id_estrutural("CTB")
        self.assertTrue(
            banco.adicionar_topico(
                banco.CTB_NOME_OFICIAL,
                "Capítulo I: Disposições Preliminares",
            )
        )
        topico_id = banco.resolver_topico_id_estrutural(
            banco.CTB_NOME_OFICIAL,
            "Capítulo I: Disposições Preliminares",
        )
        self.assertIsNotNone(topico_id)
        self.assertEqual(
            topico_id,
            banco.resolver_topico_id_estrutural(
                "Código de Trânsito Brasileiro (CTB)",
                "CAPÍTULO I - DISPOSIÇÕES PRELIMINARES",
            ),
        )


class CTBVPQParserTests(unittest.TestCase):
    def test_ctb_vpq_does_not_require_title(self):
        texto = """VIGHNA PDF — VPQ 1.1
DISCIPLINA: Código de Trânsito Brasileiro (CTB)
CAPÍTULO: Capítulo I: Disposições Preliminares
FONTE: Código de Trânsito Brasileiro — Arts. 1º a 4º
QUANTIDADE: 1
ALTERNATIVAS: A-D

QUESTÃO 1
Para os efeitos do Código, considera-se trânsito:
A) Alternativa A.
B) Alternativa B.
C) Alternativa C.
D) Alternativa D.
GABARITO: B
EXPLICAÇÃO: Comentário.
"""
        analise = analisar_texto_questoes_pdf(texto, [])
        self.assertTrue(analise["vpq_detectado"])
        self.assertFalse(analise["vpq_bloqueia_importacao"])
        self.assertEqual(
            analise["vpq_metadados"]["disciplina"],
            "Código de Trânsito Brasileiro (CTB)",
        )
        self.assertEqual(analise["vpq_metadados"]["topico"], "")
        self.assertEqual(
            analise["vpq_metadados"]["capitulo"],
            "Capítulo I: Disposições Preliminares",
        )
        self.assertFalse(
            any(
                "Título ou capítulo não informado" in aviso
                for aviso in analise.get("vpq_avisos", [])
            )
        )

    def test_ctb_vpq_missing_chapter_uses_ctb_specific_warning(self):
        texto = """VIGHNA PDF — VPQ 1.1
DISCIPLINA: CTB
TÍTULO: Título legado que não deve substituir o capítulo no protocolo atual
FONTE: Teste
QUANTIDADE: 1
ALTERNATIVAS: A-D

QUESTÃO 1
Enunciado.
A) A
B) B
C) C
D) D
GABARITO: A
EXPLICAÇÃO: Teste.
"""
        analise = analisar_texto_questoes_pdf(texto, [])
        self.assertTrue(analise["vpq_detectado"])
        self.assertIn(
            "Capítulo não informado no cabeçalho VPQ do CTB.",
            analise.get("vpq_avisos", []),
        )
        self.assertFalse(
            any(
                "Título ou capítulo não informado" in aviso
                for aviso in analise.get("vpq_avisos", [])
            )
        )


if __name__ == "__main__":
    unittest.main()
