"""M15 — ponte Qt M13 com pool dedicado e encerramento não bloqueante.

M25 aceita produção apenas após validação de fonte, banco e identidade.
Na GUI: solicitar encerramento -> bloquear eventos/timer -> aguardar QThreadPool
local sem travar a interface -> emitir encerramento_pronto uma única vez.
Os resultados tardios nunca são publicados, e nenhuma tarefa é interrompida
à força após ter começado a gravar o SQLite lateral.
"""
from __future__ import annotations

from PySide6.QtCore import QThreadPool, QTimer, Signal, Slot
from .ciclo_encerramento_m15 import CicloEncerramentoM15
from .ponte_qt_merito_m13 import PonteMeritoQtM13


class PonteMeritoQtM15(PonteMeritoQtM13):
    encerramento_pronto = Signal()

    def __init__(self, controlador, escopo, *, clone_autorizado=False,
                 debounce_ms=550):
        super().__init__(controlador, escopo,
                         clone_autorizado=clone_autorizado,
                         debounce_ms=debounce_ms)
        # M13 agenda inicialmente, mas o Qt só executará seu timer após o
        # retorno à fila de eventos. Portanto, a troca ocorre antes do trabalho.
        self._pool = QThreadPool(self)
        self._pool.setMaxThreadCount(1)
        self._ciclo_m15 = CicloEncerramentoM15()
        self._monitor_m15 = QTimer(self)
        self._monitor_m15.setInterval(80)
        self._monitor_m15.timeout.connect(self._verificar_encerramento)

    @property
    def fechando(self):
        return self._ciclo_m15.fechando

    def _iniciar_trabalho(self):
        if self.fechando:
            return
        super()._iniciar_trabalho()

    def registrar_tentativa(self, tentativa_id, *, simulado_aberto, sem_impacto=False):
        if self.fechando:
            return False
        return super().registrar_tentativa(
            tentativa_id, simulado_aberto=simulado_aberto,
            sem_impacto=sem_impacto)

    def simulado_entregue(self, *, concluida, commit_ok):
        if self.fechando:
            return False
        return super().simulado_entregue(concluida=concluida, commit_ok=commit_ok)

    @Slot(object, object)
    def _ao_concluir(self, requisicao, resultado):
        if not self.fechando:
            super()._ao_concluir(requisicao, resultado)

    @Slot(object, str)
    def _ao_falhar(self, requisicao, classe_erro):
        if not self.fechando:
            super()._ao_falhar(requisicao, classe_erro)

    def _pool_concluiu(self):
        try:
            # Timeout zero: consulta apenas, NUNCA espera bloqueando a GUI.
            return self._pool.waitForDone(0) is True
        except (RuntimeError, TypeError):
            return False  # proteção conservadora

    def iniciar_encerramento(self) -> bool:
        """Devolve True só quando nenhum worker local permanece ativo.

        Para False, manter a janela principal viva e retomar a tarefa de
        fechamento quando 'encerramento_pronto' for emitido na thread GUI.
        """
        self._na_gui()
        if not self.fechando:
            self._timer.stop()
            # Bloqueia todas as publicações e oculta o snapshot temporário.
            self.revogar('Encerramento do aplicativo em andamento')
            # Somente trabalhos ainda não iniciados podem ser descartados.
            self._pool.clear()
        pronto = self._ciclo_m15.iniciar(pool_concluido=self._pool_concluiu())
        if not pronto:
            self._monitor_m15.start()
        return pronto

    @Slot()
    def _verificar_encerramento(self):
        self._na_gui()
        if not self.fechando:
            return
        if self._ciclo_m15.verificar(pool_concluido=self._pool_concluiu()):
            self._monitor_m15.stop()
            if self._ciclo_m15.consumir_sinal_pronto():
                self.encerramento_pronto.emit()
