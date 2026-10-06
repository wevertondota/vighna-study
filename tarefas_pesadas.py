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
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
)
from ui.design import fixed_qss_color


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


class IndicadorTarefa(QFrame):
    """Indicador reutilizável para tarefas curtas/longas dentro do Vighna.

    - tarefas normais aparecem após pequeno atraso para evitar flicker;
    - tarefas bloqueantes (ex.: fechamento) aparecem imediatamente;
    - o progresso é real por etapas, sem porcentagens artificiais.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # O indicador é deliberadamente um widget-filho da janela principal,
        # não uma janela nativa. Isso elimina de forma estrutural o flicker de
        # captions/mini-janelas no Windows: não há HWND auxiliar para o sistema
        # operacional criar, decorar ou animar durante tarefas rápidas.
        self.setObjectName("taskIndicatorRoot")
        self.setFixedSize(520, 176)
        self.hide()

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
            f"QFrame#taskIndicatorRoot {{ background: {fixed_qss_color('system_status.canvas')};"
            f" border: 1px solid {fixed_qss_color('system_status.border')}; border-radius: 16px; }}"
            f"QLabel#taskIndicatorMark {{ background: {fixed_qss_color('task_indicator.mark_surface')};"
            f" border: 1px solid {fixed_qss_color('task_indicator.mark_border')}; "
            f"border-radius: 10px; color: {fixed_qss_color('task_indicator.mark_text')};"
            " font-size: 19px; font-weight: 900; }"
            f"QLabel#taskIndicatorTitle {{ color: {fixed_qss_color('system_status.text_primary')};"
            " font-size: 15px; font-weight: 800; }"
            f"QLabel#taskIndicatorDetail {{ color: {fixed_qss_color('system_status.text_secondary')};"
            " font-size: 10px; }"
            f"QFrame#taskIndicatorPanel {{ background: {fixed_qss_color('system_status.surface')};"
            f" border: 1px solid {fixed_qss_color('system_status.surface_border')}; border-radius: 10px; }}"
            f"QLabel#taskIndicatorStatus {{ color: {fixed_qss_color('system_status.text_status')};"
            " font-size: 11px; font-weight: 650; }"
            f"QLabel#taskIndicatorPercent {{ color: {fixed_qss_color('system_status.text_accent')};"
            " font-size: 11px; font-weight: 800; }"
            f"QProgressBar {{ border: 1px solid {fixed_qss_color('system_status.progress_border')};"
            f" border-radius: 6px; background: {fixed_qss_color('system_status.progress_track')}; }}"
            f"QProgressBar::chunk {{ border-radius: 5px;"
            f" background: {fixed_qss_color('system_status.progress_fill')}; }}"
        )

        self._timer_animacao = QTimer(self)
        self._timer_animacao.setInterval(320)
        self._timer_animacao.timeout.connect(self._animar)
        self._timer_animacao.start()

        self._timer_exibir = QTimer(self)
        self._timer_exibir.setSingleShot(True)
        self._timer_exibir.timeout.connect(self._exibir_agora)

        # Tarefas muito rápidas não devem criar uma janela transitória. O
        # atraso anterior (280 ms) ainda permitia um flash em operações que
        # terminavam logo depois de o indicador aparecer.
        self._atraso_minimo_nao_bloqueante_ms = 850

    def _animar(self):
        if not self.isVisible():
            return
        self._frame = (self._frame + 1) % 4
        self.status.setText(self._titulo_base + ("." * self._frame))

    def _reposicionar(self):
        parent = self.parentWidget()
        if parent is None:
            return

        # Coordenadas de widget-filho são relativas ao conteúdo do parent.
        # Nunca usamos frameGeometry()/coordenadas globais aqui, pois isso
        # faria o indicador saltar para posições incorretas em múltiplos
        # monitores ou quando a janela principal é movida.
        area = parent.rect()
        if self._bloqueante:
            x = area.center().x() - self.width() // 2
            y = area.center().y() - self.height() // 2
        else:
            x = area.right() - self.width() - 24
            y = area.bottom() - self.height() - 42

        x = max(12, min(x, max(12, area.width() - self.width() - 12)))
        y = max(12, min(y, max(12, area.height() - self.height() - 12)))
        self.move(x, y)

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
        self._timer_exibir.stop()
        if self._bloqueante or int(atraso_ms) <= 0:
            self._exibir_agora()
        else:
            atraso = max(
                self._atraso_minimo_nao_bloqueante_ms,
                int(atraso_ms),
            )
            self._timer_exibir.start(atraso)

    def _exibir_agora(self):
        if not self._pendente_exibicao:
            return

        # Um indicador de trabalho em segundo plano não agrega informação
        # enquanto o usuário já está dentro de um diálogo modal. Exibi-lo
        # atrás do diálogo era justamente o cenário em que o Windows podia
        # mostrar por um frame uma pequena janela "Vighna...". Adiamos a
        # exibição até o modal/popup desaparecer; se a tarefa terminar antes,
        # finalizar() cancela o timer e nada chega a ser mostrado.
        if not self._bloqueante:
            modal = QApplication.activeModalWidget()
            popup = QApplication.activePopupWidget()
            if modal is not None or popup is not None:
                self._timer_exibir.start(250)
                return

        self._reposicionar()
        self.show()
        # Como agora é um widget-filho, raise_() apenas o traz acima dos demais
        # widgets da própria janela principal. Não existe ativação de janela,
        # caption transitório nem item auxiliar na barra de tarefas.
        self.raise_()

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
        if self.isVisible():
            self._reposicionar()

    def exigir_espera(self, detalhe=None):
        """Promove uma tarefa em curso para espera visual sem recriar a janela nativa."""
        if detalhe is not None:
            self.detalhe.setText(str(detalhe))
        self._bloqueante = True
        self._pendente_exibicao = True
        self._timer_exibir.stop()
        if self.isVisible():
            self._reposicionar()
            self.raise_()
        else:
            self._exibir_agora()

    def finalizar(self):
        self._pendente_exibicao = False
        self._timer_exibir.stop()
        if self.isVisible():
            self.hide()
        self._bloqueante = False

    def closeEvent(self, event):
        # Não há janela nativa a fechar. Se algum código chamar close(),
        # mantemos o componente reutilizável e apenas o ocultamos.
        event.ignore()
        self.hide()
