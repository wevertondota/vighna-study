"""Splash de inicialização independente do VighnaStudy.

O splash roda em um processo separado durante o pré-carregamento pesado. Assim,
a animação continua fluida mesmo quando a thread principal do aplicativo está
ocupada montando widgets, consultando o banco ou aquecendo caches.
"""

from __future__ import annotations

import atexit
import json
import os
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

from ui.design import fixed_qcolor, fixed_qlineargradient, fixed_qss_color


ARG_SPLASH_WORKER = "--vighna-startup-splash"


def _processo_esta_ativo(pid: int) -> bool:
    """Retorna False quando o processo pai deixou de existir."""
    if pid <= 0:
        return True

    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes

            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            STILL_ACTIVE = 259
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
            kernel32.OpenProcess.restype = wintypes.HANDLE
            kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
            kernel32.GetExitCodeProcess.restype = wintypes.BOOL
            kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
            kernel32.CloseHandle.restype = wintypes.BOOL

            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
            if not handle:
                return False
            try:
                codigo = wintypes.DWORD()
                if not kernel32.GetExitCodeProcess(handle, ctypes.byref(codigo)):
                    return False
                return codigo.value == STILL_ACTIVE
            finally:
                kernel32.CloseHandle(handle)
        except Exception:
            return True

    try:
        os.kill(int(pid), 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except Exception:
        return True
    return True


def _resolver_icone() -> Path | None:
    candidatos = [
        Path.cwd() / "vighnastudy.ico",
        Path(sys.executable).resolve().parent / "vighnastudy.ico",
        Path(__file__).resolve().parent / "vighnastudy.ico",
    ]
    for caminho in candidatos:
        try:
            if caminho.exists():
                return caminho
        except OSError:
            continue
    return None


class ControladorSplashInicializacao:
    """Controla o splash externo por meio de um pequeno arquivo de estado."""

    def __init__(self):
        nome = f"vighnastudy_startup_{os.getpid()}_{uuid.uuid4().hex}.json"
        self.caminho_estado = Path(tempfile.gettempdir()) / nome
        self.processo: subprocess.Popen | None = None
        self.disponivel = False
        self._encerrado = False
        self._ultimo_estado = {
            "texto": "Inicializando o VighnaStudy...",
            "percentual": 2,
            "detalhe": "Preparando os componentes essenciais do aplicativo.",
            "encerrar": False,
            "atualizado_em": time.time(),
        }
        atexit.register(self._encerrar_ao_sair)

    def _gravar(self, estado: dict) -> None:
        self._ultimo_estado = dict(estado)
        temporario = self.caminho_estado.with_suffix(self.caminho_estado.suffix + ".tmp")
        try:
            temporario.write_text(
                json.dumps(estado, ensure_ascii=False),
                encoding="utf-8",
            )
            os.replace(temporario, self.caminho_estado)
        except OSError:
            try:
                temporario.unlink(missing_ok=True)
            except OSError:
                pass

    def iniciar(self) -> bool:
        self._gravar(self._ultimo_estado)
        if getattr(sys, "frozen", False):
            comando = [
                sys.executable,
                ARG_SPLASH_WORKER,
                str(self.caminho_estado),
                str(os.getpid()),
            ]
        else:
            main_py = Path(__file__).resolve().with_name("main.py")
            comando = [
                sys.executable,
                str(main_py),
                ARG_SPLASH_WORKER,
                str(self.caminho_estado),
                str(os.getpid()),
            ]

        kwargs = {
            "cwd": str(Path.cwd()),
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }
        if os.name == "nt":
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        try:
            self.processo = subprocess.Popen(comando, **kwargs)
            self.disponivel = True
            return True
        except Exception:
            self.processo = None
            self.disponivel = False
            return False

    def esta_ativo(self) -> bool:
        processo = self.processo
        return bool(
            self.disponivel
            and processo is not None
            and processo.poll() is None
        )

    def atualizar(self, texto, percentual=None, detalhe=None) -> None:
        if self._encerrado:
            return
        estado = dict(self._ultimo_estado)
        estado["texto"] = str(texto)
        if percentual is not None:
            estado["percentual"] = max(0, min(100, int(percentual)))
        if detalhe is not None:
            estado["detalhe"] = str(detalhe)
        estado["encerrar"] = False
        estado["atualizado_em"] = time.time()
        self._gravar(estado)

    def finalizar(self) -> None:
        self.atualizar(
            "Tudo pronto. Abrindo o VighnaStudy...",
            100,
            "Dashboard, Central, Estatísticas e Relatórios já estão preparados.",
        )

    def close(self) -> None:
        if self._encerrado:
            return
        self._encerrado = True
        estado = dict(self._ultimo_estado)
        estado["encerrar"] = True
        estado["atualizado_em"] = time.time()
        self._gravar(estado)

        processo = self.processo
        if processo is not None:
            try:
                processo.wait(timeout=0.9)
            except subprocess.TimeoutExpired:
                try:
                    processo.terminate()
                    processo.wait(timeout=0.4)
                except Exception:
                    pass
            except Exception:
                pass

        try:
            self.caminho_estado.unlink(missing_ok=True)
        except OSError:
            pass
        self.disponivel = False

    def _encerrar_ao_sair(self) -> None:
        try:
            self.close()
        except Exception:
            pass


def executar_splash_worker_cli(argv=None) -> int:
    """Entry point usado pelo processo auxiliar do splash."""
    argumentos = list(sys.argv if argv is None else argv)
    try:
        indice = argumentos.index(ARG_SPLASH_WORKER)
        caminho_estado = Path(argumentos[indice + 1])
        pid_pai = int(argumentos[indice + 2])
    except (ValueError, IndexError, TypeError):
        return 2

    # Imports do Qt ficam deliberadamente aqui. O processo principal consegue
    # lançar o splash antes de importar o restante do aplicativo.
    from math import sin, pi

    from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
    from PySide6.QtGui import QPainter, QPainterPath, QPen, QIcon, QBrush
    from PySide6.QtWidgets import (
        QApplication,
        QDialog,
        QFrame,
        QHBoxLayout,
        QLabel,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )

    class BarraProgressoViva(QWidget):
        """Barra real de progresso com shimmer contínuo e transição amortecida."""

        def __init__(self, parent=None):
            super().__init__(parent)
            self._valor_alvo = 2.0
            self._valor_visual = 2.0
            self._fase_shimmer = -0.25
            self._fase_pulso = 0.0
            self.setFixedHeight(18)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self._timer = QTimer(self)
            self._timer.setInterval(30)
            self._timer.timeout.connect(self._animar)
            self._timer.start()

        def setValue(self, valor):
            self._valor_alvo = float(max(0, min(100, int(valor))))
            if self._valor_visual > self._valor_alvo:
                self._valor_visual = self._valor_alvo
            self.update()

        def _animar(self):
            diferenca = self._valor_alvo - self._valor_visual
            if diferenca > 0.03:
                passo = max(0.08, min(0.85, diferenca * 0.13))
                self._valor_visual = min(self._valor_alvo, self._valor_visual + passo)
            self._fase_shimmer += 0.022
            if self._fase_shimmer > 1.35:
                self._fase_shimmer = -0.35
            self._fase_pulso = (self._fase_pulso + 0.025) % 1.0
            self.update()

        def paintEvent(self, evento):
            del evento
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing, True)

            rect = QRectF(0.75, 0.75, max(1.0, self.width() - 1.5), max(1.0, self.height() - 1.5))
            raio = rect.height() / 2.0
            trilha = QPainterPath()
            trilha.addRoundedRect(rect, raio, raio)
            painter.fillPath(trilha, fixed_qcolor("system_status.progress_track"))
            painter.setPen(QPen(fixed_qcolor("system_status.progress_border"), 1.0))
            painter.drawPath(trilha)

            proporcao = max(0.0, min(1.0, self._valor_visual / 100.0))
            if proporcao <= 0.0:
                return

            largura = rect.width() * proporcao
            preenchimento_rect = QRectF(rect.left(), rect.top(), max(raio * 2.0, largura), rect.height())
            preenchimento = QPainterPath()
            preenchimento.addRoundedRect(preenchimento_rect, raio, raio)

            gradiente = fixed_qlineargradient(
                "startup.progress_gradient",
                coordinates=(preenchimento_rect.left(), 0, preenchimento_rect.right(), 0),
            )
            painter.save()
            painter.setClipPath(trilha)
            painter.fillPath(preenchimento, QBrush(gradiente))

            # Reflexo móvel: continua atravessando a área preenchida mesmo
            # quando o percentual verdadeiro não muda.
            centro = rect.left() + (rect.width() + 90.0) * self._fase_shimmer
            brilho = fixed_qlineargradient(
                "startup.shimmer_gradient",
                coordinates=(centro - 36.0, 0, centro + 36.0, 0),
            )
            painter.setClipPath(preenchimento)
            painter.fillRect(rect, QBrush(brilho))

            # Leve pulso na frente da barra; não altera o valor real.
            intensidade = int(42 + 26 * (0.5 + 0.5 * sin(self._fase_pulso * 2.0 * pi)))
            x_frente = min(rect.right() - raio, rect.left() + largura)
            painter.setPen(Qt.NoPen)
            cor_pulso = fixed_qcolor("startup.progress_pulse")
            cor_pulso.setAlpha(intensidade)
            painter.setBrush(cor_pulso)
            painter.drawEllipse(QPointF(x_frente, rect.center().y()), 4.0, 4.0)
            painter.restore()

    class JanelaSplash(QDialog):
        def __init__(self):
            super().__init__(None)
            self.setWindowTitle("VighnaStudy")
            self.setModal(False)
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint)
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.setFixedSize(620, 318)

            tela = QApplication.primaryScreen()
            if tela is not None:
                area = tela.availableGeometry()
                self.move(
                    area.center().x() - self.width() // 2,
                    area.center().y() - self.height() // 2,
                )

            self._estado_anterior = None
            self._status_base = "Inicializando o VighnaStudy"
            self._pontos = 0
            self._ticks_pai = 0

            base = QFrame(self)
            base.setObjectName("startupShell")
            base.setGeometry(self.rect())

            raiz = QVBoxLayout(base)
            raiz.setContentsMargins(34, 20, 32, 18)
            raiz.setSpacing(0)
            # O splash passa a ser organizado por um único contêiner central.
            # Cabeçalho, painel e assinatura compartilham o mesmo centro
            # visual, evitando a diagonal entre logo, card e rodapé.
            raiz.addStretch(1)

            conteudo_wrap = QHBoxLayout()
            conteudo_wrap.setContentsMargins(0, 0, 0, 0)
            conteudo_wrap.setSpacing(0)
            conteudo_wrap.addStretch(1)

            conteudo = QWidget()
            conteudo.setObjectName("startupContent")
            conteudo.setFixedWidth(470)
            conteudo_layout = QVBoxLayout(conteudo)
            conteudo_layout.setContentsMargins(0, 0, 0, 0)
            conteudo_layout.setSpacing(0)

            topo = QHBoxLayout()
            topo.setContentsMargins(0, 0, 0, 0)
            topo.setSpacing(14)

            logo_box = QFrame()
            logo_box.setObjectName("startupLogoBox")
            logo_box.setFixedSize(54, 54)
            logo_layout = QVBoxLayout(logo_box)
            logo_layout.setContentsMargins(5, 5, 5, 5)
            self.logo = QLabel()
            self.logo.setAlignment(Qt.AlignCenter)
            caminho_icone = _resolver_icone()
            if caminho_icone is not None:
                pixmap = QIcon(str(caminho_icone)).pixmap(42, 42)
                self.logo.setPixmap(pixmap)
            else:
                self.logo.setText("V")
                self.logo.setStyleSheet(
                    "font-size: 25px; font-weight: 800; "
                    f"color: {fixed_qss_color('startup.logo_fallback')};"
                )
            logo_layout.addWidget(self.logo)
            topo.addWidget(logo_box, 0, Qt.AlignVCenter)

            textos_topo = QVBoxLayout()
            textos_topo.setSpacing(1)
            titulo = QLabel("VighnaStudy")
            titulo.setObjectName("startupTitle")
            subtitulo = QLabel("Preparando seu ambiente de estudo")
            subtitulo.setObjectName("startupSubtitle")
            textos_topo.addWidget(titulo)
            textos_topo.addWidget(subtitulo)
            topo.addLayout(textos_topo, 1)
            conteudo_layout.addLayout(topo)

            conteudo_layout.addSpacing(20)

            painel = QFrame()
            painel.setObjectName("startupPanel")
            painel_layout = QVBoxLayout(painel)
            painel_layout.setContentsMargins(18, 14, 18, 14)
            painel_layout.setSpacing(6)

            linha_status = QHBoxLayout()
            linha_status.setSpacing(12)
            self.status = QLabel("Inicializando o VighnaStudy...")
            self.status.setObjectName("startupStatus")
            self.status.setWordWrap(False)
            self.percentual = QLabel("2%")
            self.percentual.setObjectName("startupPercent")
            self.percentual.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.percentual.setFixedWidth(56)
            linha_status.addWidget(self.status, 1)
            linha_status.addWidget(self.percentual, 0)
            painel_layout.addLayout(linha_status)

            self.detalhe = QLabel("Preparando os componentes essenciais do aplicativo.")
            self.detalhe.setObjectName("startupDetail")
            self.detalhe.setWordWrap(True)
            painel_layout.addWidget(self.detalhe)
            painel_layout.addSpacing(4)

            self.barra = BarraProgressoViva()
            painel_layout.addWidget(self.barra)

            conteudo_layout.addWidget(painel)

            conteudo_layout.addSpacing(24)

            rodape = QHBoxLayout()
            rodape.setContentsMargins(0, 0, 0, 0)
            rodape.setSpacing(0)
            rodape.addStretch(1)
            rodape_texto = QLabel("motor de inteligência Vighna")
            rodape_texto.setObjectName("startupFooter")
            rodape.addWidget(rodape_texto, 0, Qt.AlignCenter)
            rodape.addStretch(1)
            conteudo_layout.addLayout(rodape)

            conteudo_wrap.addWidget(conteudo, 0, Qt.AlignHCenter)
            conteudo_wrap.addStretch(1)
            raiz.addLayout(conteudo_wrap)
            raiz.addStretch(1)

            self.setStyleSheet(
                "QFrame#startupShell {"
                f" background: {fixed_qss_color('system_status.canvas')};"
                f" border: 1px solid {fixed_qss_color('system_status.border')}; border-radius: 17px;"
                "}"
                "QFrame#startupLogoBox {"
                f" background: {fixed_qss_color('startup.logo_surface')};"
                f" border: 1px solid {fixed_qss_color('startup.logo_border')}; border-radius: 13px;"
                "}"
                "QLabel#startupTitle {"
                f" color: {fixed_qss_color('system_status.text_primary')};"
                " font-family: 'Segoe UI'; font-size: 23px; font-weight: 800;"
                "}"
                "QLabel#startupSubtitle {"
                f" color: {fixed_qss_color('startup.subtitle_text')};"
                " font-family: 'Segoe UI'; font-size: 12px;"
                "}"
                "QFrame#startupPanel {"
                f" background: {fixed_qss_color('system_status.surface')};"
                f" border: 1px solid {fixed_qss_color('system_status.surface_border')}; border-radius: 13px;"
                "}"
                "QLabel#startupStatus {"
                f" color: {fixed_qss_color('system_status.text_status')};"
                " font-family: 'Segoe UI'; font-size: 13px; font-weight: 650;"
                "}"
                "QLabel#startupPercent {"
                f" color: {fixed_qss_color('system_status.text_accent')};"
                " font-family: 'Segoe UI'; font-size: 13px; font-weight: 800;"
                "}"
                "QLabel#startupDetail {"
                f" color: {fixed_qss_color('system_status.text_secondary')};"
                " font-family: 'Segoe UI'; font-size: 11px;"
                "}"
                "QLabel#startupFooter {"
                f" color: {fixed_qss_color('startup.footer_text')};"
                " font-family: 'Segoe UI'; font-size: 9px; letter-spacing: 0.35px;"
                "}"
            )

            self._timer_estado = QTimer(self)
            self._timer_estado.setInterval(80)
            self._timer_estado.timeout.connect(self._ler_estado)
            self._timer_estado.start()

            self._timer_texto = QTimer(self)
            self._timer_texto.setInterval(320)
            self._timer_texto.timeout.connect(self._animar_texto)
            self._timer_texto.start()

        def _animar_texto(self):
            self._pontos = (self._pontos + 1) % 4
            pontos = "." * self._pontos
            self.status.setText(self._status_base + pontos)

        def _ler_estado(self):
            self._ticks_pai += 1
            if self._ticks_pai >= 12:
                self._ticks_pai = 0
                if not _processo_esta_ativo(pid_pai):
                    self.close()
                    return

            try:
                conteudo = caminho_estado.read_text(encoding="utf-8")
                estado = json.loads(conteudo)
            except (OSError, json.JSONDecodeError):
                return

            if estado == self._estado_anterior:
                return
            self._estado_anterior = estado

            if estado.get("encerrar"):
                self.close()
                return

            texto = str(estado.get("texto") or "Inicializando o VighnaStudy")
            self._status_base = texto.rstrip(". …")
            self._pontos = 3
            self.status.setText(self._status_base + "...")

            percentual = max(0, min(100, int(estado.get("percentual") or 0)))
            self.percentual.setText(f"{percentual}%")
            self.barra.setValue(percentual)
            self.detalhe.setText(str(estado.get("detalhe") or ""))

    app = QApplication([argumentos[0]])
    caminho_icone = _resolver_icone()
    if caminho_icone is not None:
        app.setWindowIcon(QIcon(str(caminho_icone)))

    janela = JanelaSplash()
    janela.show()
    janela.raise_()
    janela.activateWindow()
    return app.exec()
