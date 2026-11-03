"""Observa ativacao de janela e troca de paginas para suspender GIFs invisiveis.

Sem timers periodicos. Reage apenas a eventos de Qt e agenda uma verificacao
no proximo ciclo do event loop para ler o estado final da interface.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, QEvent, QTimer, Qt
from PySide6.QtWidgets import QApplication

_EVENTOS_JANELA = frozenset((
    QEvent.Type.WindowActivate,
    QEvent.Type.WindowDeactivate,
    QEvent.Type.WindowStateChange,
    QEvent.Type.Show,
    QEvent.Type.Hide,
))
_EVENTOS_WIDGET = frozenset((
    QEvent.Type.Show,
    QEvent.Type.Hide,
    QEvent.Type.ParentChange,
))


def pode_reproduzir(widget):
    """Apenas a janela visivel e ativa pode animar (inclui alt-tab e minimizacao)."""
    app = QApplication.instance()
    if app is None or app.applicationState() != Qt.ApplicationState.ApplicationActive:
        return False
    janela = widget.window()
    return bool(widget.isVisible() and not janela.isMinimized() and
                janela.isActiveWindow())


class MonitorAtividadeGIF(QObject):
    """Monitor barato, sem poll, preservando vida util do widget observado."""

    def __init__(self, widget, sincronizar):
        super().__init__(widget)
        self._widget = widget
        self._sincronizar = sincronizar
        self._janela = None
        self._agendado = False
        widget.installEventFilter(self)
        self._acompanhar_janela()
        app = QApplication.instance()
        if app is not None:
            app.applicationStateChanged.connect(self.solicitar)
        self.solicitar()

    def _acompanhar_janela(self):
        janela = self._widget.window()
        if janela is self._janela:
            return
        if self._janela is not None:
            try:
                self._janela.removeEventFilter(self)
            except RuntimeError:
                pass
        self._janela = janela
        if janela is not self._widget:
            janela.installEventFilter(self)

    def eventFilter(self, objeto, evento):
        tipo = evento.type()
        if objeto is self._widget and tipo in _EVENTOS_WIDGET:
            self._acompanhar_janela()
            self.solicitar()
        elif objeto is self._janela and tipo in _EVENTOS_JANELA:
            self.solicitar()
        return False

    def solicitar(self, *_args):
        if self._agendado:
            return
        self._agendado = True
        QTimer.singleShot(0, self._atualizar)

    def _atualizar(self):
        self._agendado = False
        try:
            self._acompanhar_janela()
            self._sincronizar()
        except RuntimeError:
            # O Qt pode destruir janela/movie enquanto encerra o aplicativo.
            pass
