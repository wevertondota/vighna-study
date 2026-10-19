"""Gerenciador visual de pausas da bateria; sem acesso ao banco de dados.

A janela de aviso é top-level (não pertencente à janela do resolvedor), para
continuar visível quando a bateria estiver minimizada e outro app estiver ativo.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QCursor
from ui.pausa_relogio import RelogioPausa, texto_contagem

from PySide6.QtWidgets import (
    QApplication, QCheckBox, QDialog, QFrame, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QVBoxLayout, QWidget,
)


class ConfiguracaoPausa(QDialog):
    def __init__(self, minutos=10, minimizar=False, som=True, simulado=False, parent=None):
        super().__init__(parent)
        self.setObjectName("questionSessionPauseSetup")
        self.setWindowTitle("Programar pausa")
        self.setMinimumWidth(395)
        self.setWindowModality(Qt.WindowModal)
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(22, 20, 22, 20)
        raiz.setSpacing(14)
        cabecalho = QLabel("Defina o tempo de descanso")
        cabecalho.setObjectName("questionSessionPauseHeading")
        cabecalho.setStyleSheet("font-size: 17px; font-weight: 650;")
        raiz.addWidget(cabecalho)
        dica = QLabel("Ao terminar, o Vighna abrirá um aviso centralizado sobre outras janelas comuns.")
        dica.setWordWrap(True)
        raiz.addWidget(dica)
        presets = QHBoxLayout()
        presets.setSpacing(6)
        self.duracao = QSpinBox(self)
        self.duracao.setRange(1, 240)
        self.duracao.setSuffix(" min")
        self.duracao.setValue(minutos)
        for valor in (5, 10, 15, 30):
            botao = QPushButton(f"{valor} min")
            botao.clicked.connect(lambda _=False, n=valor: self.duracao.setValue(n))
            presets.addWidget(botao)
        raiz.addLayout(presets)
        linha = QHBoxLayout()
        linha.addWidget(QLabel("Duração personalizada:"))
        linha.addStretch()
        linha.addWidget(self.duracao)
        raiz.addLayout(linha)
        self.minimizar = QCheckBox("Minimizar a bateria ao iniciar")
        self.minimizar.setChecked(bool(minimizar))
        raiz.addWidget(self.minimizar)
        self.som = QCheckBox("Emitir aviso sonoro ao terminar")
        self.som.setChecked(bool(som))
        raiz.addWidget(self.som)
        if simulado:
            alerta = QLabel("Atenção: no simulado, o cronômetro oficial continuará correndo durante a pausa.")
            alerta.setWordWrap(True)
            alerta.setObjectName("questionSessionPauseExamWarning")
            raiz.addWidget(alerta)
        botoes = QHBoxLayout()
        botoes.addStretch()
        cancelar = QPushButton("Cancelar")
        iniciar = QPushButton("Iniciar pausa")
        iniciar.setObjectName("primaryButton")
        cancelar.clicked.connect(self.reject)
        iniciar.clicked.connect(self.accept)
        botoes.addWidget(cancelar)
        botoes.addWidget(iniciar)
        raiz.addLayout(botoes)


class GerenciarPausa(QDialog):
    """Controles acessíveis no botão superior enquanto o descanso está ativo."""
    def __init__(self, restantes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pausa em andamento")
        self.setMinimumWidth(350)
        self.escolha = None
        raiz = QVBoxLayout(self)
        texto = QLabel(f"Faltam {texto_contagem(restantes)} para o aviso.")
        texto.setStyleSheet("font-size: 16px; font-weight: 600;")
        raiz.addWidget(texto)
        botoes = QHBoxLayout()
        for descricao, acao in (
            ("Retomar agora", "retomar"),
            ("+ 5 minutos", "adiar"),
            ("Voltar", None),
        ):
            botao = QPushButton(descricao)
            botao.clicked.connect(lambda _=False, a=acao: self._escolher(a))
            botoes.addWidget(botao)
        raiz.addLayout(botoes)

    def _escolher(self, acao):
        self.escolha = acao
        self.accept()


def mostrar_alerta_primeiro_plano(janela):
    """Pede prioridade TOPMOST sem depender de a bateria estar restaurada.

    O Windows pode bloquear SetForegroundWindow em algumas situações. Nesse
    caso, a janela segue no topo e o ícone do programa solicita atenção.
    """
    janela.show()
    janela.raise_()
    janela.activateWindow()
    if __import__('sys').platform == 'win32':
        try:
            import ctypes
            hwnd = int(janela.winId())
            # HWND_TOPMOST = -1, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW.
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0040)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        except (OSError, ValueError, AttributeError):
            pass
    QApplication.alert(janela, 0)


class AvisoPausaFinalizada(QDialog):
    retornar = Signal()
    adiar = Signal()

    def __init__(self, parent=None):
        # Sem Qt parent: janela independente, visível mesmo com a bateria minimizada.
        super().__init__(None)
        self.setObjectName("questionSessionPauseAlert")
        self.setWindowTitle("VighnaStudy — pausa encerrada")
        self.setWindowFlags(
            Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint
            | Qt.WindowStaysOnTopHint
        )
        self.setWindowModality(Qt.NonModal)
        self.setFixedSize(465, 265)
        coluna = QVBoxLayout(self)
        coluna.setContentsMargins(26, 22, 26, 22)
        coluna.setSpacing(12)
        titulo = QLabel("Sua pausa terminou!")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 23px; font-weight: 700;")
        coluna.addWidget(titulo)
        subtitulo = QLabel("O período de descanso chegou ao fim.\nSua bateria de questões está aguardando.")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setWordWrap(True)
        coluna.addWidget(subtitulo)
        coluna.addStretch()
        retornar = QPushButton("Retornar à bateria")
        retornar.setObjectName("primaryButton")
        retornar.setMinimumHeight(43)
        retornar.clicked.connect(self.retornar.emit)
        adiar = QPushButton("Adiar por mais 5 minutos")
        adiar.setMinimumHeight(36)
        adiar.clicked.connect(self.adiar.emit)
        coluna.addWidget(retornar)
        coluna.addWidget(adiar)
        self._centralizar_na_tela_atual()

    def _centralizar_na_tela_atual(self):
        tela = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        if tela is not None:
            area = tela.availableGeometry()
            self.move(area.center().x() - self.width() // 2,
                      area.center().y() - self.height() // 2)

    def exibir_prioritario(self):
        self._centralizar_na_tela_atual()
        mostrar_alerta_primeiro_plano(self)
        # Segunda tentativa, após o Windows concluir o mapeamento da janela.
        QTimer.singleShot(160, lambda: mostrar_alerta_primeiro_plano(self) if self.isVisible() else None)

    def reject(self):
        # Esc não descarta um alerta de fim de pausa silenciosamente.
        pass

    def closeEvent(self, evento):
        evento.ignore()
