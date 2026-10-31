"""Home Neural V3: imagem animada nativa + 4 áreas de clique independentes.

Lote escopado: não altera Dashboard nem os motores de Simulados e Recursos.
GIF Neural V3 original (160 quadros; 1300x715), sem reprocessar ou alterar seus bytes.
"""
from __future__ import annotations
import os

from PySide6.QtCore import Qt, QRect, QRectF, QBuffer, QByteArray, QIODevice, QSettings
from PySide6.QtGui import QColor, QMovie, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import QPushButton, QWidget, QScrollArea, QLabel

from ui.home_r4h_asset import bytes_home_r4h

ART_W, ART_H = 1300.0, 715.0
# Coordenadas na imagem ORIGINAL, não na janela incluindo barra lateral/título.
AREAS = (
    ("Simulados",  (281, 231, 182, 155)),
    ("Dashboard",  (524, 164, 209, 181)),
    ("Meu Edital", (794, 231, 169, 155)),
    ("Recursos",   (182, 388, 137, 132)),
)


class _AcessoInvisivel(QPushButton):
    def __init__(self, nome, acao, pai):
        super().__init__(pai)
        self.setObjectName("homeR4HAcesso" + nome.replace(" ", ""))
        self.setText("")
        self.setStyleSheet("""
            QPushButton {background:transparent; border:0; margin:0; padding:0;}
            QPushButton:focus {border:1px solid rgba(115,222,245,150);border-radius:14px;}
        """)
        self.setCursor(Qt.PointingHandCursor)
        self.setAccessibleName("Abrir " + nome)
        self.setToolTip("Abrir " + nome)
        self.setFocusPolicy(Qt.StrongFocus)
        if callable(acao):
            self.clicked.connect(acao)
        else:
            self.setEnabled(False)

    def enterEvent(self, event):
        self.parent().indicar_hover(self, True)
        return super().enterEvent(event)

    def leaveEvent(self, event):
        self.parent().indicar_hover(self, False)
        return super().leaveEvent(event)


class _TelaAnimadaR4H(QWidget):
    def __init__(self, acoes, parent=None):
        super().__init__(parent)
        self.setObjectName("portalInicioR4HAnimado")
        self.setMinimumSize(1, 1)
        self._buffer = QBuffer(self)
        self._buffer.setData(QByteArray(bytes_home_r4h()))
        self._buffer.open(QIODevice.ReadOnly)
        self._movie = QMovie(self._buffer, b"gif", self)
        if not self._movie.isValid():
            raise ValueError("QMovie não reconheceu o GIF da Home Neural V3")
        self._movie.setCacheMode(QMovie.CacheNone)
        self._movie.frameChanged.connect(lambda _indice: self.update())
        self._movie.jumpToFrame(0)
        self._hover = None
        self._botoes = []
        for nome, rect in AREAS:
            botao = _AcessoInvisivel(nome, acoes.get(nome), self)
            self._botoes.append((botao, rect))
        self._header = None
        self._movimento_reduzido = False
        self._ajustar_botoes()

    def frame_rect(self):
        escala = min(self.width()/ART_W, self.height()/ART_H)
        w, h = ART_W*escala, ART_H*escala
        return QRectF((self.width()-w)/2.0, (self.height()-h)/2.0, w, h)

    def _ajustar_botoes(self):
        canvas = self.frame_rect()
        sx, sy = canvas.width()/ART_W, canvas.height()/ART_H
        for botao, (x,y,w,h) in self._botoes:
            botao.setGeometry(QRect(round(canvas.x()+x*sx),round(canvas.y()+y*sy),
                                   max(1, round(w*sx)), max(1,round(h*sy))))

    def indicar_hover(self, botao, ativo):
        self._hover = botao if ativo else (None if self._hover is botao else self._hover)
        self.update()

    def attach_header(self, widget):
        self._header = widget
        self._ajustar_header()

    def _ajustar_header(self):
        if self._header is not None:
            canvas = self.frame_rect()
            self._header.setGeometry(round(canvas.x()), round(canvas.y()),
                                     round(canvas.width()), max(82, round(82*canvas.height()/ART_H)))
            self._header.raise_()

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self._ajustar_botoes()
        self._ajustar_header()

    def paintEvent(self,event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.fillRect(self.rect(),QColor(3,13,28))
        current = self._movie.currentPixmap()
        if not current.isNull():
            painter.setRenderHint(QPainter.SmoothPixmapTransform,True)
            painter.drawPixmap(self.frame_rect(),current,QRectF(current.rect()))
        if self._hover is not None:
            for btn, (x,y,w,h) in self._botoes:
                if btn is self._hover:
                    canvas = self.frame_rect()
                    sx,sy=canvas.width()/ART_W,canvas.height()/ART_H
                    cx=canvas.x()+(x+w/2)*sx
                    cy=canvas.y()+(y+h/2)*sy
                    r=min(w*sx,h*sy)*0.47
                    gradient=QRadialGradient(cx,cy,r*1.34)
                    gradient.setColorAt(0,QColor(32,158,215,4))
                    gradient.setColorAt(.72,QColor(50,187,239,8))
                    gradient.setColorAt(.92,QColor(222,182,93,27))
                    gradient.setColorAt(1,QColor(222,182,93,0))
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(gradient)
                    painter.drawEllipse(QRectF(cx-r*1.34,cy-r*1.34,r*2.68,r*2.68))
                    break
        painter.end()

    def set_reduced_motion(self, reduced):
        self._movimento_reduzido=bool(reduced)
        self._sync_movie()

    def _sync_movie(self):
        if not self.isVisible() or self._movimento_reduzido or self.window().isMinimized():
            if self._movie.state() == QMovie.Running:
                self._movie.setPaused(True)
        else:
            if self._movie.state() == QMovie.NotRunning:
                self._movie.start()
            elif self._movie.state() == QMovie.Paused:
                self._movie.setPaused(False)

    def showEvent(self,e):
        super().showEvent(e)
        self._sync_movie()

    def hideEvent(self,e):
        super().hideEvent(e)
        self._sync_movie()


class IntegracaoHomeR4H:
    def __init__(self, pagina, header, acoes):
        self.pagina=pagina
        self.header=header
        self.scroll=pagina.findChild(QScrollArea,"portalInicioScroll")
        self.header_scroll=pagina.findChild(QScrollArea,"portalInicioHeaderScroll")
        self.canvas=_TelaAnimadaR4H(acoes,pagina)
        pagina.layout().addWidget(self.canvas)
        self.canvas.hide()
        self.ativo=False
        self.brand=None
        self.brand_widgets=[]
        # A rotina existente de Configurações chama o fundo antigo. Fazer
        # a preferência alcançar também o GIF R4H sem tocar em main.py.
        fundo_antigo = (self.scroll.widget() if self.scroll is not None else None)
        metodo_antigo = getattr(fundo_antigo, "definir_reducao_movimento", None)
        if callable(metodo_antigo):
            def propagar_reducao_movimento(reduzir):
                metodo_antigo(reduzir)
                self.canvas.set_reduced_motion(reduzir)
            fundo_antigo.definir_reducao_movimento = propagar_reducao_movimento
        if header is not None:
            for nome in ("premiumHeaderLogo","premiumHeaderBrandName","premiumHeaderSubtitle","premiumHeaderDivider"):
                widget=header.findChild(QWidget,nome)
                if widget is not None:
                    self.brand_widgets.append(widget)

    def _ativar(self):
        if self.ativo:
            return
        self.ativo=True
        if self.scroll is not None:
            self.scroll.hide()
        if self.header is not None and self.header_scroll is not None:
            cabeca=getattr(self.pagina,"portal_cabeca_holografica",None)
            if cabeca is not None:
                cabeca.hide()
            # Sem duplicar seletor de perfil nem sinais: move o MESMO header Qt.
            self.header_scroll.takeWidget()
            self.header.setParent(self.canvas)
            for item in self.brand_widgets:
                item.hide()  # Marca já está no GIF, não a desenhar duas vezes.
            self.header.setStyleSheet("""
                QFrame#dashboardTopBar {background:transparent;border:0;}
                QFrame#topProfileBar {background-color:rgba(3,20,42,190);border:1px solid rgba(65,170,220,120);border-radius:10px;}
                QFrame#premiumHeaderSearchShell {background-color:rgba(3,20,42,190);border:1px solid rgba(65,170,220,120);border-radius:10px;}
            """)
            self.canvas.attach_header(self.header)
            self.header.show()
        self.canvas.show()
        self.canvas.raise_()
        if self.header is not None:
            self.header.raise_()
        self.canvas._sync_movie()

    def _desativar(self):
        if not self.ativo:
            return
        self.ativo=False
        self.canvas.hide()
        if self.header is not None and self.header_scroll is not None:
            self.header.setStyleSheet("")
            for item in self.brand_widgets:
                item.show()
            self.header_scroll.setWidget(self.header)
        if self.scroll is not None:
            self.scroll.show()

    def definir_tema(self, tema):
        if tema=="futurista":
            self._ativar()
        else:
            self._desativar()
        env = os.environ.get("VIGHNA_HOME_REDUZIR_MOVIMENTO","").strip().lower() in ("1","true","sim","yes","on")
        reduced = env or QSettings("VighnaStudy","Home").value("acessibilidade/reduzir_movimento",False,type=bool)
        self.canvas.set_reduced_motion(reduced)
