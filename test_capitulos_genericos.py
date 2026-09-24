import gc
import tempfile
import unittest
from pathlib import Path

import banco


class CapitulosGenericosTests(unittest.TestCase):
    def setUp(self):
        self.original_path = banco.CAMINHO_BANCO
        self.tempdir = tempfile.TemporaryDirectory(prefix="vighna_capitulos_")
        banco.CAMINHO_BANCO = Path(self.tempdir.name) / "estudos.db"
        banco.criar_banco()

    def tearDown(self):
        banco.CAMINHO_BANCO = self.original_path
        gc.collect()
        self.tempdir.cleanup()

    def test_disciplina_generica_pode_ter_capitulos_manuais(self):
        disciplina = "Direito Constitucional"
        titulo = "TÍTULO II — DOS DIREITOS E GARANTIAS FUNDAMENTAIS"

        self.assertTrue(banco.adicionar_topico(disciplina, titulo))
        topico_id = banco.resolver_topico_id_estrutural(disciplina, titulo)
        self.assertIsNotNone(topico_id)
        self.assertFalse(banco.topico_possui_capitulos(topico_id))

        self.assertTrue(
            banco.adicionar_capitulo(
                topico_id,
                "CAPÍTULO I — DOS DIREITOS E DEVERES INDIVIDUAIS E COLETIVOS",
            )
        )
        self.assertTrue(banco.topico_possui_capitulos(topico_id))

        self.assertTrue(
            banco.adicionar_capitulo(
                topico_id,
                "CAPÍTULO II — DOS DIREITOS SOCIAIS",
            )
        )

        capitulos = banco.listar_capitulos_topico(topico_id)
        self.assertEqual(
            [linha[1] for linha in capitulos],
            [
                "CAPÍTULO I — DOS DIREITOS E DEVERES INDIVIDUAIS E COLETIVOS",
                "CAPÍTULO II — DOS DIREITOS SOCIAIS",
            ],
        )

    def test_capitulo_duplicado_no_mesmo_topico_e_rejeitado(self):
        disciplina = "Direito Constitucional"
        titulo = "TÍTULO III — DA ORGANIZAÇÃO DO ESTADO"
        capitulo = "CAPÍTULO I — DA ORGANIZAÇÃO POLÍTICO-ADMINISTRATIVA"

        self.assertTrue(banco.adicionar_topico(disciplina, titulo))
        topico_id = banco.resolver_topico_id_estrutural(disciplina, titulo)
        self.assertTrue(banco.adicionar_capitulo(topico_id, capitulo))
        self.assertFalse(banco.adicionar_capitulo(topico_id, capitulo))

    def test_capitulos_manuais_nao_dependem_de_direito_penal(self):
        disciplina = "Direito Constitucional"
        titulo = "TÍTULO IV — DA ORGANIZAÇÃO DOS PODERES"
        self.assertTrue(banco.adicionar_topico(disciplina, titulo))
        topico_id = banco.resolver_topico_id_estrutural(disciplina, titulo)

        self.assertTrue(
            banco.adicionar_capitulo(
                topico_id,
                "CAPÍTULO I — DO PODER LEGISLATIVO",
            )
        )
        capitulos = banco.listar_capitulos_topico(topico_id)
        self.assertEqual(len(capitulos), 1)
        self.assertEqual(capitulos[0][1], "CAPÍTULO I — DO PODER LEGISLATIVO")


if __name__ == "__main__":
    unittest.main()
