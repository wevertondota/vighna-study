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

from PySide6.QtCore import Qt, QRectF, QPointF, QSize, QEvent
from PySide6.QtGui import (QColor, QPainter, QPainterPath, QLinearGradient,
                          QRadialGradient, QPen, QFont, QFontMetrics,
                          QPixmap, QPolygonF)
from PySide6.QtWidgets import (QWidget, QAbstractButton, QFrame, QLabel,
                               QScrollArea, QHBoxLayout, QVBoxLayout, QGridLayout,
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
        if w < 760:
            x=66
            if not self.logo.isNull():
                img=self.logo.scaled(QSize(51,51),Qt.KeepAspectRatio,Qt.SmoothTransformation)
                p.drawPixmap(9,8,img)
            p.setFont(_fonte(22,QFont.Bold))
            p.setPen(_cor('#f7faff'))
            p.drawText(QRectF(x,6,135,39),Qt.AlignLeft|Qt.AlignVCenter,'Vighna')
            p.setPen(_cor('#12cdef'))
            p.drawText(QRectF(x+109,6,110,39),Qt.AlignLeft|Qt.AlignVCenter,'Study')
            p.setFont(_fonte(13,QFont.Medium,2.0))
            p.setPen(_cor('#e5f5ff'))
            p.drawText(QRectF(x,47,max(100,w-x-10),30),
                       Qt.AlignLeft|Qt.AlignVCenter,'INICIAR ESTUDO')
            p.end()
            return
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
        self.texto_acao={
            'planejamento': 'Abrir planejamento',
            'comecar': 'Começar agora',
            'manual': 'Abrir Grade de Estudos',
            'nivel': 'Ver conquistas',
        }.get(tipo, 'Abrir')
        self._hover=False
        self.setObjectName('iniciarEstudoH36_'+tipo)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.setMinimumWidth(208)
        self.setFixedHeight(316)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(self.texto_acao + ' — ' + subtitulo)
        self.setAccessibleName(self.texto_acao + ' — ' + titulo)
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
        elif tipo=='manual':
            # Grade/seleção manual: ícone vetorial, sem novas imagens ou dependências.
            p.setPen(QPen(az,4.2,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
            p.drawRoundedRect(QRectF(-36,-34,72,68),6,6)
            p.setPen(QPen(ciano,3.2,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
            p.drawLine(QPointF(-33,-15),QPointF(33,-15))
            p.drawLine(QPointF(-8,-13),QPointF(-8,31))
            p.drawLine(QPointF(-33,8),QPointF(33,8))
            p.drawLine(QPointF(-33,29),QPointF(33,29))
            p.setPen(Qt.NoPen);p.setBrush(ciano)
            p.drawRoundedRect(QRectF(-25,-26,27,6),2,2)
            p.drawRoundedRect(QRectF(4,14,20,8),2,2)
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
        p=QPainter(self)
        p.setRenderHint(QPainter.Antialiasing,True)
        w,h=float(self.width()),float(self.height())
        principal=self.tipo=='comecar'
        foco=self.hasFocus()
        hover=self._hover and self.isEnabled()
        # Destaque primário permanente != foco do teclado != hover.
        r=QRectF(5,5,max(1,w-10),max(1,h-10))
        gradiente=_grad(0,0,w,h,[(0,'#0e4562' if principal else '#0d3048'),
                                  (.65,'#08263e'),(1,'#061c30')])
        cor_borda='#04dff2' if principal else ('#3ab8d4' if hover else '#2588ad')
        espessura=2.6 if principal else (2.0 if hover else 1.5)
        _arred(p,r,24,gradiente,cor_borda,espessura)
        luz=QRadialGradient(QPointF(w*.5,h*.10),w*.62)
        luz.setColorAt(0,QColor(0,207,249,38 if principal else (28 if hover else 13)))
        luz.setColorAt(1,QColor(0,40,70,0))
        p.setPen(Qt.NoPen)
        p.setBrush(luz)
        p.drawRoundedRect(r.adjusted(3,3,-3,-3),21,21)
        if foco:
            # Anel interno azul claro, independente do destaque principal.
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(_cor('#e5f9ff'),2,Qt.DashLine))
            p.drawRoundedRect(r.adjusted(6,6,-6,-6),18,18)
        self._icone(p,self.tipo,w*.5,h*.275,93)
        fonte_titulo=_fonte(29,QFont.Bold)
        while (fonte_titulo.pixelSize()>17 and
               QFontMetrics(fonte_titulo).horizontalAdvance(self.titulo)>w-32):
            fonte_titulo.setPixelSize(fonte_titulo.pixelSize()-1)
        p.setFont(fonte_titulo)
        p.setPen(_cor('#f7f9ff'))
        p.drawText(QRectF(9,h*.445,w-18,h*.135),Qt.AlignHCenter|Qt.AlignVCenter,self.titulo)
        # A descrição pode ocupar duas linhas, sem ficar minúscula em duas colunas.
        fonte_sub=_fonte(17 if w>=380 else 15)
        p.setFont(fonte_sub)
        p.setPen(_cor('#d0e3f0'))
        p.drawText(QRectF(22,h*.585,w-44,h*.16),
                   Qt.AlignHCenter|Qt.AlignVCenter|Qt.TextWordWrap,self.subtitulo)
        btn=QRectF(w*.13,h*.765,w*.74,h*.16)
        preenchido=principal or hover
        _arred(p,btn,11,_grad(btn.left(),btn.top(),btn.left(),btn.bottom(),
                  [(0,'#0ce6f2' if preenchido else '#073149'),
                   (1,'#0787cb' if preenchido else '#062139')]),
                  '#05e1f0' if preenchido else '#13b6d5',1.5)
        area_texto=QRectF(btn.left()+7,btn.top(),max(15,btn.width()-43),btn.height())
        fonte_acao=_fonte(18,QFont.DemiBold)
        while (fonte_acao.pixelSize()>11 and
               QFontMetrics(fonte_acao).horizontalAdvance(self.texto_acao)>area_texto.width()-7):
            fonte_acao.setPixelSize(fonte_acao.pixelSize()-1)
        p.setFont(fonte_acao)
        p.setPen(_cor('#ffffff'))
        p.drawText(area_texto,Qt.AlignHCenter|Qt.AlignVCenter,self.texto_acao)
        ax=btn.right()-26
        ay=btn.center().y()
        p.setPen(QPen(_cor('#eefbff'),2.3,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
        p.drawLine(QPointF(ax,ay-7),QPointF(ax+8,ay))
        p.drawLine(QPointF(ax+8,ay),QPointF(ax,ay+7))
        p.end()


class PaginaIniciarEstudo(QWidget):
    # Duas escolhas de estudo, em um único lugar: recomendação ou escolha manual.
    ALTURA_CARTAO=316
    ESPACAMENTO_CARTOES=18

    @staticmethod
    def colunas_para_largura(largura):
        # Dois cartões com boa largura; coluna única para DPI/janelas estreitas.
        return 2 if largura>=660 else 1

    def __init__(self,abrir_planejamento,comecar,abrir_nivel,parent=None):
        super().__init__(parent)
        self.setObjectName('iniciarEstudoH36Page')
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        main=QVBoxLayout(self)
        main.setContentsMargins(0,0,0,0)
        main.setSpacing(0)
        scroll=QScrollArea(self)
        scroll.setObjectName('iniciarEstudoH36Scroll')
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        conteudo=CenarioIniciarEstudo()
        conteudo.setMinimumHeight(620)
        col=QVBoxLayout(conteudo)
        col.setContentsMargins(28,0,28,25)
        col.setSpacing(0)
        col.addWidget(MarcaIniciarEstudo(conteudo),0)
        col.addSpacing(15)
        titulo=QWidget(conteudo)
        titulo.setFixedHeight(88)
        lt=QHBoxLayout(titulo)
        lt.setContentsMargins(1,0,0,0)
        lt.setSpacing(23)
        dourado=QFrame(titulo)
        dourado.setFixedSize(5,68)
        dourado.setStyleSheet('background:#efb336;border-radius:2px;')
        lt.addWidget(dourado,0,Qt.AlignVCenter)
        duo=QVBoxLayout()
        duo.setContentsMargins(0,0,0,0)
        duo.setSpacing(4)
        titulo_1=QLabel('Escolha seu modo de estudo')
        titulo_1.setObjectName('iniciarEstudoH36Titulo')
        titulo_1.setStyleSheet('color:#f8fbff;background:transparent;font-family:"Segoe UI";font-size:29px;font-weight:700;')
        titulo_2=QLabel('Siga a recomendação do Vighna ou escolha o conteúdo que deseja estudar.')
        titulo_2.setObjectName('iniciarEstudoH36Subtitulo')
        titulo_2.setWordWrap(True)
        titulo_2.setStyleSheet('color:#cfdfed;background:transparent;font-family:"Segoe UI";font-size:17px;')
        duo.addWidget(titulo_1)
        duo.addWidget(titulo_2)
        lt.addLayout(duo,1)
        col.addWidget(titulo,0)
        col.addSpacing(15)
        # Dois únicos cartões reais, sem faixa auxiliar ou botões duplicados.
        box=QWidget(conteudo)
        box.setObjectName('iniciarEstudoH36Cards')
        box.setAttribute(Qt.WA_TranslucentBackground, True)
        box.setStyleSheet('background:transparent;border:none;')
        grade=QGridLayout(box)
        grade.setContentsMargins(0,0,0,0)
        grade.setHorizontalSpacing(self.ESPACAMENTO_CARTOES)
        grade.setVerticalSpacing(self.ESPACAMENTO_CARTOES)
        # Mantém o mesmo callback do algoritmo de recomendação do Dashboard.
        self.cartao_automatico=CartaoIniciarEstudo(
            'Estudo Automático',
            'Siga a próxima atividade recomendada pelo algoritmo Vighna.',
            'comecar',comecar,box)
        # O instalador da Grade conecta este cartão ao fluxo original,
        # sem criar um segundo botão ou uma segunda página.
        self.cartao_manual=CartaoIniciarEstudo(
            'Estudo Manual',
            'Escolha o que estudar na Grade de Estudos e Revisões.',
            'manual',None,box)
        self.cartoes=[self.cartao_automatico,self.cartao_manual]
        self.grade_cartoes=grade
        self.cartoes_container=box
        self._ultima_colunas=None
        self._reorganizar_cartoes(1000)
        col.addWidget(box,0)
        # Parâmetros legados permanecem na assinatura para compatibilidade
        # com o main.py instalado; os outros destinos não são exibidos aqui.
        col.addStretch(1)
        scroll.setWidget(conteudo)
        main.addWidget(scroll)
        self.cenario=conteudo
        self.scroll=scroll
        self.scroll.viewport().installEventFilter(self)
        self.setStyleSheet('''
          QWidget#iniciarEstudoH36Page { background: #041829; border: none; }
          QScrollArea#iniciarEstudoH36Scroll { background: transparent; border: none; }
          QScrollBar:vertical { background:#061b2d;width:8px; }
          QScrollBar::handle:vertical { background:#1c739a; border-radius:4px;min-height:30px; }
        ''')

    def _reorganizar_cartoes(self, largura):
        colunas=self.colunas_para_largura(max(0,int(largura)))
        if colunas==self._ultima_colunas:
            return
        self._ultima_colunas=colunas
        while self.grade_cartoes.count():
            self.grade_cartoes.takeAt(0)
        for coluna in range(2):
            self.grade_cartoes.setColumnStretch(coluna,1 if coluna<colunas else 0)
        for i,cartao in enumerate(self.cartoes):
            self.grade_cartoes.addWidget(cartao,i//colunas,i%colunas)
        linhas=(len(self.cartoes)+colunas-1)//colunas
        self.cartoes_container.setFixedHeight(
            linhas*self.ALTURA_CARTAO+(linhas-1)*self.ESPACAMENTO_CARTOES
        )
        self.cartoes_container.updateGeometry()

    def eventFilter(self,obj,event):
        if obj is self.scroll.viewport() and event.type()==QEvent.Resize:
            largura=obj.width()
            self._reorganizar_cartoes(largura-56)
        return super().eventFilter(obj,event)

    def showEvent(self,event):
        super().showEvent(event)
        largura=self.scroll.viewport().width()
        self._reorganizar_cartoes(largura-56)


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
