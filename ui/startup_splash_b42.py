"""B42: splash em processo separado, com minimizar e controle de música.

Protocolo simples de mensagens JSON por stdin. O processo principal não cria
widgets nem espera Qt durante o pré-carregamento; mantém atualizações isoladas.
A janela pode ser minimizada sem cancelar o carregamento.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

ARG_SPLASH_WORKER_B42 = "--vighna-orbita-splash-worker-b42"


class ControladorSplashB42:
    """Cliente leve, importável antes dos módulos Qt pesados da aplicação."""
    def __init__(self):
        self._processo = None
        self._encerrado = False
        self._marcador = Path(tempfile.gettempdir()) / ("vighna_b42_min_" + uuid.uuid4().hex + ".flag")

    def iniciar(self):
        if self._processo is not None:
            return
        if getattr(sys, 'frozen', False):
            cmd = [sys.executable, ARG_SPLASH_WORKER_B42, str(self._marcador)]
        else:
            principal = str(Path(sys.argv[0]).resolve())
            cmd = [sys.executable, principal, ARG_SPLASH_WORKER_B42, str(self._marcador)]
        flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        self._processo = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, encoding='utf-8',
            creationflags=flags, bufsize=1,
        )

    def esta_ativo(self):
        return (not self._encerrado and self._processo is not None
                and self._processo.poll() is None)

    def foi_minimizado(self):
        return self._marcador.is_file()

    def _enviar(self, mensagem):
        if not self.esta_ativo():
            return False
        try:
            self._processo.stdin.write(json.dumps(mensagem, ensure_ascii=False) + '\n')
            self._processo.stdin.flush()
            return True
        except (OSError, BrokenPipeError, ValueError):
            return False

    def atualizar(self, titulo, percentual, detalhe=''):
        self._enviar({'cmd': 'progress', 'titulo': str(titulo),
                     'percentual': max(0, min(100, int(percentual))),
                     'detalhe': str(detalhe)})

    def finalizar(self):
        self._enviar({'cmd': 'progress', 'titulo': 'Preparação concluída',
                     'percentual': 100, 'detalhe': 'Abrindo sua área de estudos.'})
        # Não fecha até janela principal estar prestes a aparecer: close() faz isso.

    def close(self):
        self._enviar({'cmd': 'close'})
        self._encerrado = True
        try:
            self._marcador.unlink(missing_ok=True)
        except OSError:
            pass
        if self._processo is not None and self._processo.stdin is not None:
            try:
                self._processo.stdin.close()
            except OSError:
                pass


def executar_worker_b42():
    """Worker Qt independente. Chamado no início do main.py, antes do app real."""
    import threading
    from PySide6.QtCore import QObject, Qt, Signal, QTimer, QEvent
    from PySide6.QtWidgets import (
        QApplication, QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QPushButton, QProgressBar,
    )
    from ui.musica_ambiente_b42 import (
        ReprodutorOrbitaB42, musica_habilitada, alterar_musica_habilitada,
    )

    class Canal(QObject):
        comando = Signal(str)

    class CarregamentoB42(QDialog):
        def __init__(self):
            super().__init__(None)
            self._pode_fechar = False
            self._marcador = Path(sys.argv[sys.argv.index(ARG_SPLASH_WORKER_B42)+1]) if (
                ARG_SPLASH_WORKER_B42 in sys.argv and len(sys.argv) > sys.argv.index(ARG_SPLASH_WORKER_B42)+1
            ) else None
            self.setWindowTitle('VighnaStudy — Inicialização')
            self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint)
            self.setFixedSize(638, 318)
            self.setObjectName('b42StartupWindow')
            self._reprodutor = ReprodutorOrbitaB42(self)
            self._musica_ativa = musica_habilitada()
            root = QVBoxLayout(self)
            root.setContentsMargins(29, 23, 29, 24)
            root.setSpacing(15)

            topo = QHBoxLayout()
            marca = QLabel('VIGHNA / STUDY')
            marca.setObjectName('b42StartupBrand')
            topo.addWidget(marca)
            topo.addStretch(1)
            self.musica = QPushButton()
            self.musica.setObjectName('b42StartupMusic')
            self.musica.setFixedSize(38, 32)
            self.musica.setAccessibleName('Pausar ou reproduzir música de carregamento')
            self.musica.setFocusPolicy(Qt.StrongFocus)
            self.musica.clicked.connect(self._alternar_musica)
            topo.addWidget(self.musica)
            self.minimizar = QPushButton('—')
            self.minimizar.setObjectName('b42StartupMinimize')
            self.minimizar.setFixedSize(38, 32)
            self.minimizar.setAccessibleName('Minimizar VighnaStudy durante o carregamento')
            self.minimizar.setToolTip('Minimizar. A inicialização continua normalmente.')
            self.minimizar.clicked.connect(self._minimizar)
            topo.addWidget(self.minimizar)
            root.addLayout(topo)

            titulo = QLabel('Preparando seu ambiente de estudo')
            titulo.setObjectName('b42StartupTitle')
            root.addWidget(titulo)
            subtitulo = QLabel('Inicialização segura de componentes e dados acadêmicos')
            subtitulo.setObjectName('b42StartupSubtitle')
            root.addWidget(subtitulo)
            root.addStretch(1)
            linha = QHBoxLayout()
            self.status = QLabel('Iniciando o VighnaStudy...')
            self.status.setObjectName('b42StartupStatus')
            linha.addWidget(self.status, 1)
            self.percentual = QLabel('2%')
            self.percentual.setObjectName('b42StartupPercent')
            linha.addWidget(self.percentual)
            root.addLayout(linha)
            self.detalhe = QLabel('Preparando o núcleo da aplicação.')
            self.detalhe.setObjectName('b42StartupDetail')
            self.detalhe.setWordWrap(True)
            root.addWidget(self.detalhe)
            self.barra = QProgressBar()
            self.barra.setRange(0, 100)
            self.barra.setValue(2)
            self.barra.setTextVisible(False)
            self.barra.setFixedHeight(15)
            root.addWidget(self.barra)

            self.setStyleSheet('''
                QDialog#b42StartupWindow {background:#071b2d;color:#edf7ff;}
                QLabel#b42StartupBrand {font-size:16px; font-weight:800; color:#43d1ec; letter-spacing:2px;}
                QLabel#b42StartupTitle {font-size:21px; font-weight:750; color:#ffffff;}
                QLabel#b42StartupSubtitle {font-size:12px; color:#9fbfd0;}
                QLabel#b42StartupStatus {font-size:12px; color:#e7f7ff;}
                QLabel#b42StartupPercent {font-size:13px;font-weight:750;color:#ffd08b;}
                QLabel#b42StartupDetail {font-size:11px; color:#9db2c1;}
                QPushButton#b42StartupMusic, QPushButton#b42StartupMinimize {
                    color:#e8f9ff;background:#11334a;border:1px solid #386d85;
                    border-radius:9px;font-size:17px;font-weight:700;}
                QPushButton#b42StartupMusic:hover, QPushButton#b42StartupMinimize:hover {
                    background:#1d536a;border-color:#60d5ef;}
                QPushButton:focus {border:2px solid #f4c97d;}
                QProgressBar {border:1px solid #2b6680;border-radius:7px;background:#123347;}
                QProgressBar::chunk {background:#19cbe6;border-radius:6px;}
            ''')
            self._ajustar_icone_musica()
            if self._musica_ativa:
                QTimer.singleShot(200, self._reprodutor.iniciar)

        def _ajustar_icone_musica(self):
            self.musica.setText('Ⅱ' if self._musica_ativa else '♪')
            self.musica.setToolTip(
                'Pausar Órbita de Cristal' if self._musica_ativa
                else 'Tocar Órbita de Cristal'
            )

        def _minimizar(self):
            if self._marcador is not None:
                try:
                    self._marcador.write_text("minimized", encoding="utf8")
                except OSError:
                    pass
            self.showMinimized()

        def changeEvent(self, event):
            if event.type() == QEvent.WindowStateChange and self._marcador is not None:
                try:
                    if self.isMinimized():
                        self._marcador.write_text('minimized', encoding='utf8')
                    else:
                        self._marcador.unlink(missing_ok=True)
                except OSError:
                    pass
            super().changeEvent(event)

        def _alternar_musica(self):
            self._musica_ativa = not self._musica_ativa
            alterar_musica_habilitada(self._musica_ativa)
            self._ajustar_icone_musica()
            if self._musica_ativa:
                self._reprodutor.iniciar()
            else:
                self._reprodutor.pausar()

        def atualizar(self, msg):
            try:
                payload = json.loads(msg)
            except (ValueError, TypeError):
                return
            if payload.get('cmd') == 'close':
                self._reprodutor.fechar()
                self._pode_fechar = True
                self.close()
                return
            if payload.get('cmd') != 'progress':
                return
            numero = max(0, min(100, int(payload.get('percentual', 0))))
            self.barra.setValue(numero)
            self.percentual.setText(str(numero)+'%')
            self.status.setText(str(payload.get('titulo', 'Preparando o VighnaStudy'))[:105])
            self.detalhe.setText(str(payload.get('detalhe', ''))[:230])

        def closeEvent(self, event):
            if not self._pode_fechar:
                event.ignore()  # Evita cancelar a inicialização sem querer
            else:
                super().closeEvent(event)

    app = QApplication([sys.argv[0], ARG_SPLASH_WORKER_B42])
    app.setQuitOnLastWindowClosed(True)
    janela = CarregamentoB42()
    area = app.primaryScreen().availableGeometry() if app.primaryScreen() else None
    if area:
        janela.move(area.center().x()-janela.width()//2, area.center().y()-janela.height()//2)
    canal = Canal()
    canal.comando.connect(janela.atualizar)

    def ler_comandos():
        try:
            for linha in sys.stdin:
                canal.comando.emit(linha)
        except (OSError, UnicodeError):
            pass
        canal.comando.emit(json.dumps({'cmd':'close'}))

    threading.Thread(target=ler_comandos, daemon=True).start()
    janela.show()
    return app.exec()
