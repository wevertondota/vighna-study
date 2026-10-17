
import hashlib
import io
import unittest
import zipfile

from painel_reconciliacao import (
    Conflito, combinar_main, atualizar_versao,
    _aplicar_inicio, _ler_membro,
    BUILD_ANTIGO, BUILD_NOVO
)


class TestarReconciliacao(unittest.TestCase):

    def setUp(self):
        self.base = (
            "class Exemplo:\n"
            "    def iniciar(self):\n"
            '        """\n'
            "        Prioriza os rótulos em desktops de 1366 px e oferece colapso manual.\n"
            '        """\n'
            "        self._sidebar_expandida_manual = None\n"
            "        # Em 1366 px a lateral textual tem prioridade. A versão compacta\n"
            "        # continua acessível pelo botão e é o padrão só abaixo de 1240 px.\n"
            "janela.show()\n"
            "janela.show()\n"
        )
        self.rc2 = self.base + "configuracoes = 'rc2'\n"
        self.ajuste = _aplicar_inicio(self.base)

    def test_fusao_valida(self):
        resultado = combinar_main(self.base, self.rc2, self.ajuste)
        self.assertEqual(resultado, _aplicar_inicio(self.rc2))
        self.assertIn("configuracoes = 'rc2'", resultado)

    def test_somente_segunda_janela_maximizada(self):
        resultado = combinar_main(self.base, self.rc2, self.ajuste)
        self.assertEqual(resultado.count("janela.show()"), 1)
        self.assertEqual(resultado.count("janela.showMaximized()"), 1)

    def test_lateral_inicia_false(self):
        resultado = combinar_main(self.base, self.rc2, self.ajuste)
        self.assertIn("self._sidebar_expandida_manual = False", resultado)

    def test_patch_adicional_bloqueado(self):
        with self.assertRaises(Conflito):
            combinar_main(
                self.base, self.rc2,
                self.ajuste + "efeito_indevido = True\n"
            )

    def test_primeira_janela_modificada_bloqueada(self):
        alterado = self.ajuste.replace(
            "janela.show()\n", "janela.showMaximized()\n", 1
        )
        with self.assertRaises(Conflito):
            combinar_main(self.base, self.rc2, alterado)

    def test_terceira_janela_bloqueada(self):
        with self.assertRaises(Conflito):
            combinar_main(
                self.base, self.rc2 + "janela.show()\n", self.ajuste
            )

    def test_estado_true_bloqueado(self):
        with self.assertRaises(Conflito):
            combinar_main(
                self.base,
                self.rc2.replace(
                    "_sidebar_expandida_manual = None",
                    "_sidebar_expandida_manual = True"
                ),
                self.ajuste
            )

    def test_estado_ja_false_bloqueado(self):
        with self.assertRaises(Conflito):
            combinar_main(
                self.base,
                self.rc2.replace(
                    "_sidebar_expandida_manual = None",
                    "_sidebar_expandida_manual = False"
                ),
                self.ajuste
            )

    def test_documentacao_divergente_bloqueada(self):
        with self.assertRaises(Conflito):
            combinar_main(
                self.base,
                self.rc2.replace(
                    "Prioriza os rótulos", "Outra descrição"
                ),
                self.ajuste
            )

    def test_codigo_fonte_invalido_bloqueado(self):
        with self.assertRaises((Conflito, SyntaxError)):
            combinar_main(
                self.base, self.rc2 + "\ndef falha(:\n", self.ajuste
            )

    def test_identificador_build(self):
        resultado = atualizar_versao(
            "BUILD = " + repr(BUILD_ANTIGO)
        )
        self.assertIn(BUILD_NOVO, resultado)

    def test_build_ambiguo_bloqueado(self):
        with self.assertRaises(Conflito):
            atualizar_versao(
                "A = " + repr(BUILD_ANTIGO) +
                "\nB = " + repr(BUILD_ANTIGO)
            )

    def test_main_maior_que_2mb_aceito_com_hash(self):
        conteudo = b"x" * 2032178
        h = hashlib.sha256(conteudo).hexdigest()
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("backups/main.py", b"antigo")
            z.writestr("main.py", conteudo)
        buffer.seek(0)
        with zipfile.ZipFile(buffer) as z:
            self.assertEqual(_ler_membro(z, "main.py", h), conteudo)

    def test_duplicidade_de_hash_bloqueada(self):
        conteudo = b"mesmo"
        h = hashlib.sha256(conteudo).hexdigest()
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as z:
            z.writestr("main.py", conteudo)
            z.writestr("outra/main.py", conteudo)
        buffer.seek(0)
        with zipfile.ZipFile(buffer) as z:
            with self.assertRaises(Conflito):
                _ler_membro(z, "main.py", h)

    def test_caminho_inseguro_bloqueado(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as z:
            z.writestr("../main.py", b"teste")
        buffer.seek(0)
        with zipfile.ZipFile(buffer) as z:
            with self.assertRaises(Conflito):
                _ler_membro(z, "main.py")

    def test_limite_de_3mb_preservado(self):
        conteudo = b"x" * 3000001
        h = hashlib.sha256(conteudo).hexdigest()
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("main.py", conteudo)
        buffer.seek(0)
        with zipfile.ZipFile(buffer) as z:
            with self.assertRaises(Conflito):
                _ler_membro(z, "main.py", h)


if __name__ == "__main__":
    unittest.main()
