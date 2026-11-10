"""VighnaStudy H36 R1 — apresentação de Iniciar estudo.

O conteúdo acadêmico da antiga tela dashboard continua vivo, mas oculto,
para manter cálculos, recomendações e os vínculos já existentes. Esta camada
usa somente QPainter/QAbstractButton e callbacks do MainWindow existente.
Não altera a barra lateral, perfis, banco ou lógica de mérito.
"""
from __future__ import annotations

import base64
import math
from pathlib import Path

from PySide6.QtCore import Qt, QRectF, QPointF, QSize
from PySide6.QtGui import (QColor, QPainter, QPainterPath, QLinearGradient,
                          QRadialGradient, QPen, QFont, QFontMetrics,
                          QPixmap, QPolygonF)
from PySide6.QtWidgets import (QWidget, QAbstractButton, QFrame, QLabel,
                               QScrollArea, QHBoxLayout, QVBoxLayout,
                               QSizePolicy)


def _cor(valor):
    return QColor(valor)


def _fonte(px, peso=QFont.Normal, espaco=None):
    f = QFont('Segoe UI', max(8, int(px)))
    f.setPixelSize(int(px))
    f.setWeight(peso)
    if espaco is not None:
        f.setLetterSpacing(QFont.AbsoluteSpacing, espaco)
    return f


def _grad(x1,y1,x2,y2,cores):
    g=QLinearGradient(x1,y1,x2,y2)
    for pos, cor in cores:
        g.setColorAt(pos,_cor(cor))
    return g


def _arred(p,r,rx,grad,stroke=None,esp=1):
    p.setBrush(grad)
    p.setPen(Qt.NoPen if not stroke else QPen(_cor(stroke),esp))
    p.drawRoundedRect(r,rx,rx)


class CenarioIniciarEstudo(QWidget):
    """Fundo vetorial leve: sem GIF, timers ou superfície pesada."""
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setObjectName('iniciarEstudoH36Cenario')

    def paintEvent(self,event):
        p=QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        w,h=float(self.width()),float(self.height())
        p.fillRect(self.rect(), _grad(0,0,w,h,[(0,'#061e31'),(.48,'#041a2d'),(1,'#03182b')]))
        # Ondas sutis na barra superior.
        grad=_grad(0,0,w*.78,h*.24,[(0,'#0a314e'),(.48,'#061f35'),(1,'#05253e')])
        pt=QPainterPath();pt.moveTo(0,0);pt.lineTo(w,0);pt.lineTo(w*.63,0)
        pt.cubicTo(w*.49,30,w*.38,89,0,108);pt.closeSubpath()
        p.setPen(Qt.NoPen);p.setBrush(grad);p.drawPath(pt)
        pt2=QPainterPath();pt2.moveTo(w*.38,0);pt2.lineTo(w*.83,0)
        pt2.cubicTo(w*.72,20,w*.62,72,w*.39,93)
        p.setPen(QPen(QColor(0,209,251,155),1.5));p.setBrush(Qt.NoBrush);p.drawPath(pt2)
        # Traço inferior direito longe do conteúdo.
        area=QPainterPath();area.moveTo(w*.30,h)
        area.cubicTo(w*.48,h*.94,w*.74,h*.86,w,h*.88)
        area.lineTo(w,h);area.closeSubpath()
        p.setPen(Qt.NoPen);p.setBrush(_grad(0,h*.86,w,h,[(0,'#052038'),(1,'#063452')]));p.drawPath(area)
        linha=QPainterPath();linha.moveTo(w*.48,h)
        linha.cubicTo(w*.68,h*.84,w*.85,h*.84,w,h*.89)
        p.setPen(QPen(_cor('#069fca'),1.4));p.setBrush(Qt.NoBrush);p.drawPath(linha)
        # Regra ciano do cabeçalho.
        p.setPen(QPen(QColor(28,135,171,150),1));p.drawLine(QPointF(0,90),QPointF(w,90))
        p.end()


class MarcaIniciarEstudo(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setFixedHeight(90)
        self.logo=QPixmap()
        # Usa símbolo já embutido no módulo da Home instalada H35 R3.
        # Não depende de arquivo externo ou busca de caminhos do Windows.
        try:
            from ui.portal_inicio_maduro import _SYMBOL_B64
            self.logo.loadFromData(base64.b64decode(_SYMBOL_B64))
        except (ImportError, AttributeError, ValueError):
            pass

    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing,True)
        w=float(self.width())
        x=8
        if not self.logo.isNull():
            img=self.logo.scaled(QSize(69,69),Qt.KeepAspectRatio,Qt.SmoothTransformation)
            p.drawPixmap(10,11,img)
            x=80
        p.setFont(_fonte(27,QFont.Bold));p.setPen(_cor('#f7faff'))
        p.drawText(QRectF(x,18,136,49),Qt.AlignLeft|Qt.AlignVCenter,'Vighna')
        p.setPen(_cor('#12cdef'))
        p.drawText(QRectF(x+132,18,111,49),Qt.AlignLeft|Qt.AlignVCenter,'Study')
        p.setPen(QPen(_cor('#a2d0e7'),1.4))
        p.drawLine(QPointF(x+260,20),QPointF(x+260,64))
        p.setFont(_fonte(17,QFont.Medium,4.2));p.setPen(_cor('#ebf5ff'))
        p.drawText(QRectF(x+292,19,max(200,w-x-315),49),Qt.AlignLeft|Qt.AlignVCenter,'INICIAR ESTUDO')
        p.end()


class CartaoIniciarEstudo(QAbstractButton):
    """Botão inteiro clicável (mouse, Enter e Espaço); QSS externo não o comprime."""
    def __init__(self,titulo,subtitulo,tipo,callback,parent=None):
        super().__init__(parent)
        self.titulo,self.subtitulo,self.tipo=titulo,subtitulo,tipo
        self._hover=False
        self.setObjectName('iniciarEstudoH36_'+tipo)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.setMinimumWidth(208)
        self.setFixedHeight(278)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip('Acessar '+titulo)
        self.setAccessibleName(titulo+' — '+subtitulo)
        if callable(callback):self.clicked.connect(callback)
        else:self.setEnabled(False)

    def enterEvent(self,e):self._hover=True;self.update();super().enterEvent(e)
    def leaveEvent(self,e):self._hover=False;self.update();super().leaveEvent(e)
    def focusInEvent(self,e):super().focusInEvent(e);self.update()
    def focusOutEvent(self,e):super().focusOutEvent(e);self.update()

    @staticmethod
    def _icone(p,tipo,cx,cy,escala):
        p.save();p.translate(cx,cy);p.scale(escala/90,escala/90)
        az=_cor('#99e9ff');ciano=_cor('#15d9f1');gold=_cor('#f5bd45')
        p.setBrush(Qt.NoBrush)
        if tipo=='planejamento':
            p.setPen(QPen(az,5,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
            p.drawRoundedRect(QRectF(-35,-32,70,65),7,7)
            p.drawLine(QPointF(-35,-13),QPointF(35,-13))
            p.drawLine(QPointF(-17,-42),QPointF(-17,-22))
            p.drawLine(QPointF(17,-42),QPointF(17,-22))
            p.setPen(Qt.NoPen);p.setBrush(ciano)
            for r in (0,1,2):
                for c in (0,1,2):p.drawRoundedRect(QRectF(-22+c*20,-2+r*13,10,8),2,2)
        elif tipo=='comecar':
            p.setPen(QPen(ciano,5));p.setBrush(Qt.NoBrush)
            p.drawEllipse(QRectF(-38,-38,76,76))
            tri=QPolygonF([QPointF(-8,-19),QPointF(21,0),QPointF(-8,19)])
            p.setPen(QPen(az,4,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin));p.drawPolygon(tri)
        else:
            # Brasão vetorial dourado, ícone do destino do perfil, não novo nível.
            esc=QPainterPath();esc.moveTo(0,-39);esc.lineTo(32,-27)
            esc.lineTo(30,5);esc.cubicTo(27,21,11,32,0,39)
            esc.cubicTo(-11,32,-27,21,-30,5);esc.lineTo(-32,-27);esc.closeSubpath()
            p.setPen(QPen(gold,3.4,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
            p.setBrush(_grad(-29,-35,29,33,[(0,'#123c54'),(1,'#081d32')]))
            p.drawPath(esc)
            pontos=QPolygonF()
            for i in range(10):
                a=-math.pi/2+i*math.pi/5
                radius=17 if i%2==0 else 7
                pontos.append(QPointF(math.cos(a)*radius,math.sin(a)*radius))
            p.setPen(Qt.NoPen);p.setBrush(gold);p.drawPolygon(pontos)
            p.setPen(QPen(gold,2.8,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
            for side in (-1,1):
                arco=QPainterPath();arco.moveTo(side*38,-24)
                arco.cubicTo(side*57,0,side*47,19,side*31,33)
                p.drawPath(arco)
        p.restore()

    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing,True)
        w,h=float(self.width()),float(self.height())
        ativo=self.tipo=='comecar' or self._hover or self.hasFocus()
        r=QRectF(4,4,w-8,h-8)
        _arred(p,r,24,_grad(0,0,w,h,[(0,'#0d405c' if ativo else '#0d3048'),(.65,'#08263e'),(1,'#061c30')]),
               '#06dff5' if ativo else '#2588ad',3.2 if ativo else 1.7)
        luz=QRadialGradient(QPointF(w*.5,h*.11),w*.61)
        luz.setColorAt(0,QColor(0,207,249,37 if ativo else 15))
        luz.setColorAt(1,QColor(0,40,70,0))
        p.setPen(Qt.NoPen);p.setBrush(luz);p.drawRoundedRect(r.adjusted(3,3,-3,-3),21,21)
        self._icone(p,self.tipo,w*.5,h*.275,83)
        font=_fonte(29,QFont.Bold)
        while font.pixelSize()>19 and QFontMetrics(font).horizontalAdvance(self.titulo)>w-30:
            font.setPixelSize(font.pixelSize()-1)
        p.setFont(font);p.setPen(_cor('#f7f9ff'))
        p.drawText(QRectF(8,h*.45,w-16,h*.135),Qt.AlignHCenter|Qt.AlignVCenter,self.titulo)
        subt=_fonte(18)
        while subt.pixelSize()>12 and QFontMetrics(subt).horizontalAdvance(self.subtitulo)>w-21:
            subt.setPixelSize(subt.pixelSize()-1)
        p.setFont(subt);p.setPen(_cor('#d0e3f0'))
        p.drawText(QRectF(8,h*.60,w-16,h*.09),Qt.AlignHCenter|Qt.AlignVCenter,self.subtitulo)
        btn=QRectF(w*.115,h*.755,w*.77,h*.165)
        _arred(p,btn,12,_grad(btn.left(),btn.top(),btn.left(),btn.bottom(),
                                 [(0,'#0ce6f2' if ativo else '#073149'),(1,'#0787cb' if ativo else '#062139')]),
               '#05e1f0',1.6)
        p.setFont(_fonte(19,QFont.DemiBold));p.setPen(_cor('#ffffff'))
        p.drawText(btn.adjusted(-14,0,-4,0),Qt.AlignHCenter|Qt.AlignVCenter,'Acessar')
        ax=w*.66;ay=h*.835
        p.setPen(QPen(_cor('#eefbff'),2.6,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
        p.drawLine(QPointF(ax,ay-8),QPointF(ax+9,ay));p.drawLine(QPointF(ax+9,ay),QPointF(ax,ay+8))
        p.end()


class PaginaIniciarEstudo(QWidget):
    def __init__(self,abrir_planejamento,comecar,abrir_nivel,parent=None):
        super().__init__(parent)
        self.setObjectName('iniciarEstudoH36Page')
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        main=QVBoxLayout(self);main.setContentsMargins(0,0,0,0);main.setSpacing(0)
        scroll=QScrollArea(self);scroll.setObjectName('iniciarEstudoH36Scroll')
        scroll.setFrameShape(QFrame.NoFrame);scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        conteudo=CenarioIniciarEstudo();conteudo.setMinimumSize(765,625)
        col=QVBoxLayout(conteudo);col.setContentsMargins(36,0,36,25);col.setSpacing(0)
        col.addWidget(MarcaIniciarEstudo(conteudo),0)
        col.addSpacing(24)
        titulo=QWidget(conteudo);titulo.setFixedHeight(101)
        lt=QHBoxLayout(titulo);lt.setContentsMargins(1,0,0,0);lt.setSpacing(23)
        dourado=QFrame(titulo);dourado.setFixedSize(5,70)
        dourado.setStyleSheet('background:#efb336;border-radius:2px;')
        lt.addWidget(dourado,0,Qt.AlignVCenter)
        duo=QVBoxLayout();duo.setContentsMargins(0,0,0,0);duo.setSpacing(6)
        titulo_1=QLabel('Seu espaço de estudo')
        titulo_1.setStyleSheet('color:#f8fbff;background:transparent;font-family:"Segoe UI";font-size:32px;font-weight:700;')
        titulo_2=QLabel('Organize sua jornada e concentre-se no próximo passo.')
        titulo_2.setStyleSheet('color:#cfdfed;background:transparent;font-family:"Segoe UI";font-size:18px;')
        duo.addWidget(titulo_1);duo.addWidget(titulo_2);lt.addLayout(duo,1)
        col.addWidget(titulo,0)
        col.addSpacing(19)
        box=QWidget(conteudo);box.setFixedHeight(278)
        grade=QHBoxLayout(box);grade.setContentsMargins(0,0,0,0);grade.setSpacing(18)
        specs=(('Planejamento','Organize suas atividades.','planejamento',abrir_planejamento),
               ('Começar agora','Retome sua jornada.','comecar',comecar),
               ('Nível e Conquistas','Evolução, méritos e recompensas.','nivel',abrir_nivel))
        self.cartoes=[]
        for label,desc,tipo,cb in specs:
            b=CartaoIniciarEstudo(label,desc,tipo,cb,box)
            grade.addWidget(b,1);self.cartoes.append(b)
        col.addWidget(box,0);col.addStretch(1)
        scroll.setWidget(conteudo);main.addWidget(scroll)
        self.cenario=conteudo
        # Estilo só local: a coluna lateral, outros portais e QSS global intocados.
        self.setStyleSheet('''
          QWidget#iniciarEstudoH36Page { background: #041829; border: none; }
          QScrollArea#iniciarEstudoH36Scroll { background: transparent; border: none; }
          QScrollBar:vertical { background:#061b2d;width:7px; }
          QScrollBar::handle:vertical { background:#1c739a; border-radius:3px;min-height:30px; }
        ''')


def instalar_no_dashboard_existente(janela):
    """Não troca o atributo tela_inicial nem seu controller: só substitui a vista.

    O Dashboard antigo continua no QStackedWidget, com mesma identidade e mesmo
    QScrollArea (oculto) para que timers, cálculos, links legados e rollback não
    percam referências. Sidebar mantém integralmente os seus próprios comandos.
    """
    pagina=getattr(janela,'tela_inicial',None)
    scroll=getattr(janela,'dashboard_scroll',None)
    if pagina is None or scroll is None:raise RuntimeError('H36: Dashboard original não encontrado')
    if getattr(pagina,'_h36_painel',None) is not None:
        return pagina._h36_painel
    layout=pagina.layout()
    if layout is None:raise RuntimeError('H36: layout do Dashboard não encontrado')
    painel=PaginaIniciarEstudo(janela.abrir_calendario,
                               janela.iniciar_estudo_um_clique,
                               janela.abrir_perfil_candidato,pagina)
    layout.addWidget(painel,1)
    scroll.hide()
    pagina._h36_painel=painel
    return painel
