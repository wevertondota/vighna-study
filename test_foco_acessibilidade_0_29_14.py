import ast
import os
import unittest
from pathlib import Path
from unittest.mock import patch


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QPushButton

import foco


ROOT = Path(__file__).resolve().parent
MAIN_SOURCE = (ROOT / "main.py").read_text(encoding="utf-8")
MAIN_TREE = ast.parse(MAIN_SOURCE)


def metodo(classe, nome):
    for node in MAIN_TREE.body:
        if isinstance(node, ast.ClassDef) and node.name == classe:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == nome:
                    return item
    raise AssertionError(f"Método {classe}.{nome} não encontrado")


class FocoAcessibilidadeRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.patches = [
            patch.object(foco, "listar_disciplinas", return_value=[]),
            patch.object(foco, "listar_topicos", return_value=[]),
            patch.object(foco, "listar_sessoes_foco", return_value=[]),
            patch.object(
                foco,
                "obter_resumo_foco",
                return_value={
                    "hoje_segundos": 0,
                    "semana_segundos": 0,
                    "semana_sessoes": 0,
                    "media_sessao_semana": 0,
                },
            ),
            patch.object(foco, "registrar_sessao_foco", return_value=101),
        ]
        self.mocks = [item.start() for item in self.patches]
        self.registrar_mock = self.mocks[-1]
        self.janela = foco.JanelaModoFoco(object())

    def tearDown(self):
        self.janela.sessao_ativa = False
        self.janela.close()
        self.app.processEvents()
        for item in reversed(self.patches):
            item.stop()

    def _sessao_em_execucao(self):
        self.janela.sessao_ativa = True
        self.janela.pausada = False
        self.janela.inicio_segmento = 100.0
        self.janela.acumulado = 0.0
        self.janela.duracao_planejada = 3600

    def test_janela_e_top_level_independente_e_nao_modal(self):
        self.assertIsNone(self.janela.parentWidget())
        self.assertEqual(self.janela.windowModality(), Qt.NonModal)
        self.assertTrue(bool(self.janela.windowFlags() & Qt.Window))
        self.assertFalse(bool(self.janela.windowFlags() & Qt.WindowStaysOnTopHint))

    def test_restaurar_minimizada_reutiliza_mesma_instancia(self):
        self.janela.show()
        self.janela.showMinimized()
        self.app.processEvents()
        retornada = foco.trazer_janela_foco_para_frente(self.janela)
        self.app.processEvents()
        self.assertIs(retornada, self.janela)
        self.assertFalse(self.janela.isMinimized())
        self.assertTrue(self.janela.isVisible())

    def test_pausar_e_retomar_preserva_sessao_e_ignora_tempo_pausado(self):
        self._sessao_em_execucao()
        with patch.object(foco.time, "monotonic", return_value=110.0):
            self.janela.alternar_pausa()
        self.assertTrue(self.janela.pausada)
        self.assertEqual(self.janela.acumulado, 10.0)

        with patch.object(foco.time, "monotonic", return_value=999.0):
            self.assertEqual(self.janela.tempo_decorrido(), 10.0)

        with patch.object(foco.time, "monotonic", return_value=200.0):
            self.janela.alternar_pausa()
        with patch.object(foco.time, "monotonic", return_value=207.0):
            self.assertEqual(self.janela.tempo_decorrido(), 17.0)

        self.assertFalse(self.janela.pausada)
        self.registrar_mock.assert_not_called()

    def test_estado_alterado_sincroniza_pausa_e_retomada(self):
        self._sessao_em_execucao()
        estados = []
        self.janela.estado_alterado.connect(
            lambda: estados.append((self.janela.sessao_ativa, self.janela.pausada))
        )
        with patch.object(foco.time, "monotonic", return_value=101.0):
            self.janela.alternar_pausa()
        with patch.object(foco.time, "monotonic", return_value=102.0):
            self.janela.alternar_pausa()
        self.assertEqual(estados, [(True, True), (True, False)])

    def test_atalhos_da_janela_sao_f8_e_ctrl_shift_f(self):
        self.assertEqual(self.janela.atalho_pausa.key().toString(), "F8")
        self.assertEqual(self.janela.atalho_trazer.key().toString(), "Ctrl+Shift+F")

    def test_duracoes_e_pausa_desafios_permanecem_disponiveis(self):
        for minutos in (25, 50, 90, 135, 24 * 60):
            self.janela.definir_minutos(minutos)
            self.assertEqual(
                self.janela._duracao_personalizada_minutos(),
                minutos,
            )
        textos = {botao.text() for botao in self.janela.findChildren(QPushButton)}
        self.assertIn("Pausa & Desafios", textos)

    def test_finalizar_limpa_estado_e_timer(self):
        self._sessao_em_execucao()
        self.janela.inicio_datetime = foco.datetime.now()
        self.janela.acumulado = 20.0
        self.janela.pausada = True
        self.janela.timer.start()
        resultado = self.janela.finalizar(False, mostrar_pos_foco=False)
        self.assertIsNotNone(resultado)
        self.assertFalse(self.janela.sessao_ativa)
        self.assertFalse(self.janela.pausada)
        self.assertIsNone(self.janela.inicio_segmento)
        self.assertFalse(self.janela.timer.isActive())


class FocoAcessibilidadeArquiteturaTests(unittest.TestCase):
    def test_controlador_possui_fabrica_unica(self):
        node = metodo("SistemaEstudos", "abrir_ou_trazer_modo_foco")
        criacoes = [
            item for item in ast.walk(node)
            if isinstance(item, ast.Call)
            and isinstance(item.func, ast.Name)
            and item.func.id == "JanelaModoFoco"
        ]
        self.assertEqual(len(criacoes), 1)
        self.assertIn("trazer_janela_foco_para_frente(janela)", ast.unparse(node))

    def test_resolvedor_controla_mesma_sessao_sem_criar_janela(self):
        pausa = ast.unparse(metodo("JanelaResolverQuestoes", "alternar_foco_resolvedor"))
        abrir = ast.unparse(metodo("JanelaResolverQuestoes", "abrir_foco_resolvedor"))
        self.assertIn("controlador.alternar_pausa_modo_foco()", pausa)
        self.assertIn("controlador.abrir_ou_trazer_modo_foco()", abrir)
        self.assertNotIn("JanelaModoFoco", pausa + abrir)

    def test_fechar_resolvedor_nao_encerra_foco(self):
        fechamento = ast.unparse(metodo("JanelaResolverQuestoes", "closeEvent"))
        self.assertNotIn("modo_foco", fechamento)
        self.assertNotIn("alternar_foco", fechamento)

    def test_pagina_topico_tem_execucao_nao_modal(self):
        exec_topico = ast.unparse(metodo("JanelaTopico", "exec"))
        self.assertIn("Qt.NonModal", exec_topico)
        self.assertIn("QEventLoop()", exec_topico)
        self.assertNotIn("super().exec", exec_topico)

    def test_painel_visual_reflete_estado_unico(self):
        atualizar = ast.unparse(metodo("JanelaResolverQuestoes", "atualizar_painel_foco"))
        self.assertIn("janela.pausada", atualizar)
        self.assertIn("janela.tempo_decorrido()", atualizar)
        self.assertIn("FOCO PAUSADO", atualizar)
        self.assertIn("FOCO ATIVO", atualizar)

    def test_atalhos_estao_na_principal_e_no_resolvedor(self):
        atalhos = ast.unparse(metodo("SistemaEstudos", "configurar_atalhos_globais"))
        init_resolvedor = ast.unparse(metodo("JanelaResolverQuestoes", "__init__"))
        for sequencia in ("F8", "Ctrl+Shift+F"):
            self.assertIn(sequencia, atalhos)
            self.assertIn(sequencia, init_resolvedor)

    def test_encerramento_principal_fecha_foco_top_level(self):
        fechamento = ast.unparse(metodo("SistemaEstudos", "closeEvent"))
        self.assertIn("janela_foco.close()", fechamento)
        self.assertIn("evento.ignore()", fechamento)


if __name__ == "__main__":
    unittest.main()
