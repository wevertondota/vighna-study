"""Infraestrutura central para tarefas pesadas sem bloquear a interface.

O coordenador executa trabalhos serialmente em QThreadPool. O indicador visual
mantém o event loop do Qt livre, de modo que animações, repaint e navegação
continuem responsivos enquanto SQLite/estatísticas trabalham em outra thread.
"""

from __future__ import annotations

import itertools
import traceback
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
)


class _SinaisWorker(QObject):
    iniciado = Signal(str, str, str, bool)
    progresso = Signal(str, str, str, int)
    concluido = Signal(str, object)
    falhou = Signal(str, str)


class _Worker(QRunnable):
    def __init__(
        self,
        chave: str,
        titulo: str,
        detalhe: str,
        bloqueante: bool,
        funcao: Callable[[Callable[[str, str, int], None]], Any],
    ):
        super().__init__()
        self.chave = str(chave)
        self.titulo = str(titulo)
        self.detalhe = str(detalhe)
        self.bloqueante = bool(bloqueante)
        self.funcao = funcao
        self.sinais = _SinaisWorker()
        self.setAutoDelete(True)

    def run(self):
        self.sinais.iniciado.emit(
            self.chave,
            self.titulo,
            self.detalhe,
            self.bloqueante,
        )

        def reportar(titulo=None, detalhe=None, percentual=None):
            titulo_local = self.titulo if titulo is None else str(titulo)
            detalhe_local = self.detalhe if detalhe is None else str(detalhe)
            try:
                pct = -1 if percentual is None else max(0, min(100, int(percentual)))
            except (TypeError, ValueError):
                pct = -1
            self.sinais.progresso.emit(
                self.chave,
                titulo_local,
                detalhe_local,
                pct,
            )

        try:
            resultado = self.funcao(reportar)
        except Exception:
            self.sinais.falhou.emit(self.chave, traceback.format_exc())
            return
        self.sinais.concluido.emit(self.chave, resultado)


class CoordenadorTarefas(QObject):
    """Fila serial de trabalhos pesados com sinais centralizados.

    Uma única thread de trabalho é proposital: evita duas reconstruções
    estatísticas concorrentes disputando o mesmo banco SQLite e simplifica a
    coerência do warm cache. Novas alterações acadêmicas podem ser aglutinadas
    pelo chamador enquanto a tarefa atual ainda está em execução.
    """

    iniciada = Signal(str, str, str, bool)
    progresso = Signal(str, str, str, int)
    concluida = Signal(str, object)
    falhou = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pool = QThreadPool(self)
        self.pool.setMaxThreadCount(1)
        self._ativos: dict[str, _Worker] = {}
        self._contador = itertools.count(1)

    def ha_tarefa(self, chave: str | None = None) -> bool:
        if chave is None:
            return bool(self._ativos)
        return str(chave) in self._ativos

    def executar(
        self,
        chave: str,
        titulo: str,
        detalhe: str,
        funcao: Callable[[Callable[[str, str, int], None]], Any],
        *,
        bloqueante: bool = False,
    ) -> bool:
        chave = str(chave)
        if chave in self._ativos:
            return False

        worker = _Worker(chave, titulo, detalhe, bloqueante, funcao)
        # Referência forte até o sinal terminal. O QThreadPool é dono do ciclo
        # nativo do QRunnable, mas os sinais Python precisam permanecer vivos.
        self._ativos[chave] = worker
        worker.sinais.iniciado.connect(self.iniciada.emit)
        worker.sinais.progresso.connect(self.progresso.emit)
        worker.sinais.concluido.connect(self._concluir)
        worker.sinais.falhou.connect(self._falhar)
        self.pool.start(worker)
        return True

    def _concluir(self, chave: str, resultado: object):
        self._ativos.pop(str(chave), None)
        self.concluida.emit(str(chave), resultado)

    def _falhar(self, chave: str, erro: str):
        self._ativos.pop(str(chave), None)
        self.falhou.emit(str(chave), str(erro))


class IndicadorTarefa(QDialog):
    """Indicador reutilizável para tarefas curtas/longas dentro do Vighna.

    - tarefas normais aparecem após pequeno atraso para evitar flicker;
    - tarefas bloqueantes (ex.: fechamento) aparecem imediatamente;
    - o progresso é real por etapas, sem porcentagens artificiais.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("VighnaStudy")
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.Dialog
            | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.setFixedSize(520, 176)

        self._titulo_base = "Atualizando o Vighna"
        self._frame = 0
        self._bloqueante = False
        self._pendente_exibicao = False

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(18, 16, 18, 14)
        raiz.setSpacing(10)

        topo = QHBoxLayout()
        topo.setContentsMargins(0, 0, 0, 0)
        topo.setSpacing(10)
        marca = QLabel("V")
        marca.setObjectName("taskIndicatorMark")
        marca.setAlignment(Qt.AlignCenter)
        marca.setFixedSize(34, 34)
        topo.addWidget(marca, 0, Qt.AlignVCenter)

        textos = QVBoxLayout()
        textos.setSpacing(1)
        self.titulo = QLabel(self._titulo_base)
        self.titulo.setObjectName("taskIndicatorTitle")
        self.detalhe = QLabel("Preparando dados...")
        self.detalhe.setObjectName("taskIndicatorDetail")
        self.detalhe.setWordWrap(True)
        textos.addWidget(self.titulo)
        textos.addWidget(self.detalhe)
        topo.addLayout(textos, 1)
        raiz.addLayout(topo)

        painel = QFrame()
        painel.setObjectName("taskIndicatorPanel")
        painel_layout = QVBoxLayout(painel)
        painel_layout.setContentsMargins(12, 10, 12, 10)
        painel_layout.setSpacing(5)

        linha = QHBoxLayout()
        self.status = QLabel("Processando...")
        self.status.setObjectName("taskIndicatorStatus")
        self.percentual = QLabel("")
        self.percentual.setObjectName("taskIndicatorPercent")
        self.percentual.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.percentual.setFixedWidth(48)
        linha.addWidget(self.status, 1)
        linha.addWidget(self.percentual, 0)
        painel_layout.addLayout(linha)

        self.barra = QProgressBar()
        self.barra.setTextVisible(False)
        self.barra.setFixedHeight(14)
        self.barra.setRange(0, 0)
        painel_layout.addWidget(self.barra)
        raiz.addWidget(painel)

        self.setStyleSheet(
            "QDialog { background: #071522; border: 1px solid #214A64; border-radius: 16px; }"
            "QLabel#taskIndicatorMark { background: #0A2233; border: 1px solid #286483; "
            "border-radius: 10px; color: #74C7FF; font-size: 19px; font-weight: 900; }"
            "QLabel#taskIndicatorTitle { color: #F5F8FF; font-size: 15px; font-weight: 800; }"
            "QLabel#taskIndicatorDetail { color: #8FAAC0; font-size: 10px; }"
            "QFrame#taskIndicatorPanel { background: #081927; border: 1px solid #15364C; border-radius: 10px; }"
            "QLabel#taskIndicatorStatus { color: #EAF4FF; font-size: 11px; font-weight: 650; }"
            "QLabel#taskIndicatorPercent { color: #67B7FF; font-size: 11px; font-weight: 800; }"
            "QProgressBar { border: 1px solid #315B76; border-radius: 6px; background: #081A28; }"
            "QProgressBar::chunk { border-radius: 5px; background: #3A8DF1; }"
        )

        self._timer_animacao = QTimer(self)
        self._timer_animacao.setInterval(320)
        self._timer_animacao.timeout.connect(self._animar)
        self._timer_animacao.start()

        self._timer_exibir = QTimer(self)
        self._timer_exibir.setSingleShot(True)
        self._timer_exibir.timeout.connect(self._exibir_agora)

    def _animar(self):
        if not self.isVisible():
            return
        self._frame = (self._frame + 1) % 4
        self.status.setText(self._titulo_base + ("." * self._frame))

    def _reposicionar(self):
        parent = self.parentWidget()
        if parent is not None and parent.isVisible():
            geom = parent.frameGeometry()
            if self._bloqueante:
                x = geom.center().x() - self.width() // 2
                y = geom.center().y() - self.height() // 2
            else:
                x = geom.right() - self.width() - 24
                y = geom.bottom() - self.height() - 42
            self.move(max(0, x), max(0, y))
            return
        tela = QApplication.primaryScreen()
        if tela is not None:
            area = tela.availableGeometry()
            self.move(
                area.center().x() - self.width() // 2,
                area.center().y() - self.height() // 2,
            )

    def iniciar(
        self,
        titulo: str,
        detalhe: str,
        *,
        bloqueante: bool = False,
        atraso_ms: int = 280,
    ):
        self._bloqueante = bool(bloqueante)
        self._titulo_base = str(titulo or "Atualizando o Vighna")
        self.titulo.setText(self._titulo_base)
        self.detalhe.setText(str(detalhe or "Preparando dados..."))
        self.status.setText(self._titulo_base + "...")
        self.percentual.clear()
        self.barra.setRange(0, 0)
        self._frame = 3
        self._pendente_exibicao = True
        self.setWindowModality(
            Qt.ApplicationModal if self._bloqueante else Qt.NonModal
        )
        self._timer_exibir.stop()
        if self._bloqueante or int(atraso_ms) <= 0:
            self._exibir_agora()
        else:
            self._timer_exibir.start(int(atraso_ms))

    def _exibir_agora(self):
        if not self._pendente_exibicao:
            return
        self._reposicionar()
        self.show()
        self.raise_()
        self.activateWindow() if self._bloqueante else None

    def atualizar(self, titulo=None, detalhe=None, percentual=None):
        if titulo:
            self._titulo_base = str(titulo)
            self.titulo.setText(self._titulo_base)
        if detalhe is not None:
            self.detalhe.setText(str(detalhe))
        if percentual is None or int(percentual) < 0:
            self.barra.setRange(0, 0)
            self.percentual.clear()
        else:
            valor = max(0, min(100, int(percentual)))
            self.barra.setRange(0, 100)
            self.barra.setValue(valor)
            self.percentual.setText(f"{valor}%")
        self._reposicionar()

    def exigir_espera(self, detalhe=None):
        """Promove uma tarefa em curso para espera visual bloqueante."""
        if detalhe is not None:
            self.detalhe.setText(str(detalhe))
        self._bloqueante = True
        self._pendente_exibicao = True
        self._timer_exibir.stop()
        if self.isVisible():
            self.hide()
        self.setWindowModality(Qt.ApplicationModal)
        self._exibir_agora()

    def finalizar(self):
        self._pendente_exibicao = False
        self._timer_exibir.stop()
        self.hide()
        self._bloqueante = False
        self.setWindowModality(Qt.NonModal)

    def closeEvent(self, event):
        # O indicador é controlado pelo coordenador e não deve ser fechado pelo
        # usuário durante uma tarefa bloqueante.
        if self._bloqueante:
            event.ignore()
            return
        event.accept()
