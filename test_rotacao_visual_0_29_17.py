import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

import banco
import jogos


class RotacaoVisualLogicaTests(unittest.TestCase):
    def test_rotacoes_e_espelhamentos_sao_deterministicos(self):
        forma = (
            (1, 0, 0),
            (1, 1, 1),
        )
        self.assertEqual(
            jogos._aplicar_operacao_forma(forma, "rot90"),
            (
                (1, 1),
                (1, 0),
                (1, 0),
            ),
        )
        self.assertEqual(
            jogos._aplicar_operacao_forma(forma, "mirror_h"),
            (
                (0, 0, 1),
                (1, 1, 1),
            ),
        )
        self.assertEqual(
            jogos._aplicar_operacao_forma(forma, "mirror_v"),
            (
                (1, 1, 1),
                (1, 0, 0),
            ),
        )

    def test_gerador_produz_formas_com_oito_orientacoes_distintas(self):
        for tamanho in (4, 5):
            for _ in range(12):
                forma = jogos._gerar_forma_assimetrica(tamanho)
                self.assertEqual(len(jogos._variantes_dihedrais(forma)), 8)

    def test_banco_aceita_id_do_novo_jogo(self):
        self.assertIn("rotacao_visual", banco._JOGOS_VALIDOS)


class RotacaoVisualInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def tearDown(self):
        self.app.processEvents()

    def test_partida_cria_seis_alternativas_unicas_e_uma_correta(self):
        jogo = jogos.JogoRotacaoVisual()
        try:
            jogo.iniciar_partida()
            formas = list(jogo.formas_opcoes)
            self.assertEqual(len(formas), 6)
            self.assertEqual(len(set(formas)), 6)
            self.assertIn(jogo.resposta_correta, formas)
            self.assertTrue(jogo.timer_questao.isActive())
            self.assertTrue(all(botao.isEnabled() for botao, _ in jogo.opcoes))
        finally:
            jogo.timer_questao.stop()
            jogo.ativo = False
            jogo.deleteLater()

    def test_acerto_incrementa_pontos_e_acertos(self):
        jogo = jogos.JogoRotacaoVisual()
        try:
            jogo.iniciar_partida()
            indice = jogo.formas_opcoes.index(jogo.resposta_correta)
            with patch.object(jogos.time, "monotonic", return_value=(jogo.fim_questao or 0) - 5.0):
                jogo.responder(indice)
            self.assertEqual(jogo.acertos, 1)
            self.assertGreater(jogo.pontuacao, 0)
            self.assertTrue(jogo.ativo)
            self.assertTrue(jogo.bloqueado)
            # Invalida qualquer singleShot ainda pendente deste teste.
            jogo.token_rodada += 1
        finally:
            jogo.timer_questao.stop()
            jogo.ativo = False
            jogo.deleteLater()

    def test_pausa_expoe_aba_e_cartao_de_recorde(self):
        vazio = {
            chave: {
                "partidas": 0,
                "melhor_pontuacao": None,
                "melhor_nivel": None,
                "melhor_tempo": None,
                "melhor_movimentos": None,
                "ultimo_resultado": None,
            }
            for chave in banco._JOGOS_VALIDOS
        }
        with patch.object(jogos, "obter_recordes_jogos", return_value=vazio):
            janela = jogos.JanelaPausaDesafios()
        try:
            abas = [janela.tabs.tabText(i) for i in range(janela.tabs.count())]
            self.assertIn("Rotação visual", abas)
            self.assertIn("rotacao_visual", janela.recorde_labels)
            self.assertEqual(janela.recorde_labels["rotacao_visual"].text(), "Sem recorde")
        finally:
            janela.close()
            janela.deleteLater()


if __name__ == "__main__":
    unittest.main()
