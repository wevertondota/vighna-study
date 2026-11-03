"""Home V9: reprodução quadro-a-quadro, sem perdas, e quatro acessos Qt.

Os 200 quadros do GIF enviado foram recompostos sem alterar cores,
geometria ou texto. Fundo e ações não interferem nas outras telas.
"""
from __future__ import annotations
import os

from PySide6.QtCore import Qt, QRect, QRectF, QSettings, QTimer, QByteArray
from PySide6.QtGui import QColor, QImage, QPainter, QRadialGradient
from PySide6.QtWidgets import QPushButton, QWidget, QScrollArea, QLabel

from ui.home_v9_frames import obter_png, QUADROS, DURACAO_QUADRO_MS, iniciar_preaquecimento
from ui.gif_activity_manager import MonitorAtividadeGIF, pode_reproduzir

ART_W, ART_H = 1300.0, 715.0
# Coordenadas na imagem ORIGINAL, não na janela incluindo barra lateral/título.
AREAS = (
    ("Simulados",  (354, 242, 139, 132)),
    ("Dashboard",  (567, 184, 156, 143)),
    ("Meu Edital", (841, 242, 137, 132)),
    ("Recursos",   (228, 389, 117, 113)),
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
        # O V9 original tem 113 MB, acima dos limites seguros do atualizador.
        # A codificação de quadros PNG + diferenças é VISUALMENTE sem perdas:
        # a imagem reconstruída de cada quadro coincide exatamente com o GIF.
        # Decodificamos apenas um patch a cada 100 ms, sem QMovie de 113 MB.
        self._indice_quadro = 0
        self._imagem = QImage.fromData(QByteArray(obter_png(0)), "PNG")
        if self._imagem.isNull():
            raise ValueError("Não foi possível carregar o quadro 0 da Home V9")
        self._imagem = self._imagem.convertToFormat(QImage.Format_ARGB32)
        self._quadro_inicial = self._imagem.copy()
        iniciar_preaquecimento()
        self._timer_animacao = QTimer(self)
        self._timer_animacao.setTimerType(Qt.PreciseTimer)
        self._timer_animacao.setInterval(DURACAO_QUADRO_MS)
        self._timer_animacao.timeout.connect(self._proximo_quadro)
        self._hover = None
        self._botoes = []
        for nome, rect in AREAS:
            botao = _AcessoInvisivel(nome, acoes.get(nome), self)
            self._botoes.append((botao, rect))
        self._header = None
        self._movimento_reduzido = False
        self._ajustar_botoes()
        self._monitor_gif = MonitorAtividadeGIF(self, self._sync_movie)

    def _proximo_quadro(self):
        proximo = (self._indice_quadro + 1) % QUADROS
        if proximo == 0:
            # Reinicia sem decodificar novamente um PNG completo de 1300x715.
            self._imagem = self._quadro_inicial.copy()
        else:
            delta = QImage.fromData(QByteArray(obter_png(proximo)), "PNG")
            if delta.isNull():
                self._timer_animacao.stop()
                return
            pintor = QPainter(self._imagem)
            pintor.setCompositionMode(QPainter.CompositionMode_SourceOver)
            pintor.drawImage(0, 0, delta)
            pintor.end()
        self._indice_quadro = proximo
        self.update()

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
        if not self._imagem.isNull():
            painter.setRenderHint(QPainter.SmoothPixmapTransform,True)
            painter.drawImage(self.frame_rect(), self._imagem, QRectF(self._imagem.rect()))
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
        # Nome preservado por compatibilidade com MonitorAtividadeGIF.
        # A animação pausa ao minimizar, desativar ou esconder a Home.
        if self._movimento_reduzido or not pode_reproduzir(self):
            self._timer_animacao.stop()
        elif not self._timer_animacao.isActive():
            self._timer_animacao.start()

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
