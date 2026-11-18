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
        p.setPen(QPen(QColor(0,163,204,85),1.0));p.setBrush(Qt.NoBrush);p.drawPath(pt2)
        # Traço inferior direito longe do conteúdo.
        area=QPainterPath();area.moveTo(w*.30,h)
        area.cubicTo(w*.48,h*.94,w*.74,h*.86,w,h*.88)
        area.lineTo(w,h);area.closeSubpath()
        p.setPen(Qt.NoPen);p.setBrush(_grad(0,h*.86,w,h,[(0,'#052038'),(1,'#063452')]));p.drawPath(area)
        linha=QPainterPath();linha.moveTo(w*.48,h)
        linha.cubicTo(w*.68,h*.84,w*.85,h*.84,w,h*.89)
        p.setPen(QPen(QColor(6,159,202,110),1.0));p.setBrush(Qt.NoBrush);p.drawPath(linha)
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
            'simulados': 'Configurar simulado',
            'erros': 'Abrir Banco de Erros',
            'nivel': 'Ver conquistas',
        }.get(tipo, 'Abrir')
        self._hover=False
        self.setObjectName('iniciarEstudoH36_'+tipo)
        # Cartão único: sem pseudo-botão interno nem tooltip redundante.
        # Mesmo acabamento e densidade visual da Home profissional R2.
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.setMinimumWidth(208)
        self.setFixedHeight(148)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.setAccessibleName(titulo)
        self.setAccessibleDescription(self.texto_acao + ' — ' + subtitulo)
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
        elif tipo=='simulados':
            # Configuração de provas: usa o controlador original de simulado.
            p.setPen(QPen(az,4.5,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(QRectF(-30,-36,60,73),6,6)
            p.drawRoundedRect(QRectF(-14,-43,28,13),4,4)
            for y in (-14,8,27):
                p.setPen(QPen(ciano,4,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
                p.drawLine(QPointF(-19,y),QPointF(-14,y+4))
                p.drawLine(QPointF(-14,y+4),QPointF(-7,y-4))
                p.setPen(QPen(az,3,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
                p.drawLine(QPointF(3,y),QPointF(19,y))
        elif tipo=='erros':
            # Banco de erros: pilha de registros e indicador de correção.
            p.setPen(QPen(az,4,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
            p.drawEllipse(QRectF(-34,-34,61,17))
            p.drawLine(QPointF(-34,-25.5),QPointF(-34,19))
            p.drawLine(QPointF(27,-25.5),QPointF(27,4))
            p.drawArc(QRectF(-34,-14,61,17),180*16,180*16)
            p.drawArc(QRectF(-34,5,61,17),180*16,180*16)
            p.drawArc(QRectF(-34,12,61,17),180*16,180*16)
            p.setPen(QPen(ciano,4,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
            p.drawEllipse(QRectF(8,6,37,37))
            p.drawLine(QPointF(18,16),QPointF(35,33))
            p.drawLine(QPointF(35,16),QPointF(18,33))
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
        """Cartão horizontal: ícone, informação e sinal discreto de navegação.

        Mantém toda a área clicável e o destaque cromático da Home R2.
        Não desenha ações internas, métricas ou novos controles Qt.
        """
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        w, h = float(self.width()), float(self.height())
        principal = self.tipo == 'comecar'
        foco = self.hasFocus()
        realce = self._hover and self.isEnabled()
        if not self.isEnabled():
            p.setOpacity(.53)
        ret = QRectF(2.3, 2.3, max(1.0, w - 4.6), max(1.0, h - 4.6))

        fundo = QLinearGradient(0, 0, w, h)
        if principal:
            fundo.setColorAt(0, _cor('#12364c' if realce else '#103147'))
            fundo.setColorAt(1, _cor('#082337'))
        else:
            fundo.setColorAt(0, _cor('#103047' if realce else '#0d283c'))
            fundo.setColorAt(1, _cor('#091e31'))
        p.setPen(Qt.NoPen)
        p.setBrush(fundo)
        p.drawRoundedRect(ret, 18, 18)

        if foco:
            borda, espessura = '#75dfed', 2.0
        elif realce:
            borda, espessura = '#47c5d9', 1.6
        elif principal:
            borda, espessura = '#1bb4d2', 1.45
        else:
            borda, espessura = '#365b72', 1.1
        p.setPen(QPen(_cor(borda), espessura))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(ret, 18, 18)

        # Placa do ícone ocupa uma área fixa à esquerda, sem competir com o título.
        placa_lado = 74.0 if w >= 370 else 58.0
        placa_x = 24.0 if w >= 370 else 14.0
        placa_y = (h - placa_lado) / 2
        p.setPen(Qt.NoPen)
        p.setBrush(_cor('#10445a' if principal else '#143247'))
        p.drawRoundedRect(QRectF(placa_x, placa_y, placa_lado, placa_lado), 13, 13)
        self._icone(p, self.tipo, placa_x + placa_lado / 2,
                    h / 2, 55 if w >= 370 else 46)

        # Um único alinhamento de texto: duas linhas úteis, sem CTA repetido.
        texto_x = placa_x + placa_lado + (21 if w >= 370 else 13)
        seta_reserva = 39 if w >= 370 else 22
        texto_largura = max(75.0, w - texto_x - seta_reserva)
        titulo_f = _fonte(22 if w >= 440 else 20, QFont.DemiBold)
        metrica = QFontMetrics(titulo_f)
        while titulo_f.pixelSize() > 16 and metrica.horizontalAdvance(self.titulo) > texto_largura:
            titulo_f.setPixelSize(titulo_f.pixelSize() - 1)
            metrica = QFontMetrics(titulo_f)
        p.setPen(_cor('#f3f8fc'))
        p.setFont(titulo_f)
        p.drawText(QRectF(texto_x, h * .20, texto_largura, h * .32),
                   Qt.AlignLeft | Qt.AlignVCenter | Qt.TextWordWrap,
                   self.titulo)

        subt_f = _fonte(15 if w >= 440 else 14)
        p.setFont(subt_f)
        p.setPen(_cor('#adc4d3'))
        p.drawText(QRectF(texto_x, h * .52, texto_largura, h * .34),
                   Qt.AlignLeft | Qt.AlignVCenter | Qt.TextWordWrap,
                   self.subtitulo)

        # Chevron de acesso: orienta a navegação sem virar outro botão.
        if w >= 340:
            px, py = w - 23.0, h / 2
            p.setPen(QPen(_cor('#79c2d3' if principal else '#6a91a6'),
                          2.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawLine(QPointF(px - 5, py - 7), QPointF(px + 2, py))
            p.drawLine(QPointF(px + 2, py), QPointF(px - 5, py + 7))
        p.end()


class PaginaIniciarEstudo(QWidget):
    # Quatro acessos de preparação: automático, manual, simulado e banco de erros.
    ALTURA_CARTAO=148
    ESPACAMENTO_CARTOES=18

    @staticmethod
    def colunas_para_largura(largura):
        # Duas colunas no desktop e uma em janelas estreitas.
        # A largura recebida já desconta as margens do conteúdo.
        return 2 if largura >= 760 else 1

    def __init__(self,abrir_planejamento,comecar,abrir_nivel,parent=None,
                 abrir_simulados=None,abrir_erros=None):
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
        conteudo.setMinimumHeight(590)
        col=QVBoxLayout(conteudo)
        col.setContentsMargins(52,0,52,28)
        col.setSpacing(0)
        # A marca já está presente na Home: não a repete dentro da área de trabalho.
        # Hierarquia enxuta: título da seção, subtítulo e ações de estudo.
        col.addSpacing(34)
        cabecalho=QWidget(conteudo)
        cabecalho.setObjectName('iniciarEstudoR1Cabecalho')
        cabecalho.setFixedHeight(84)
        cabecalho.setStyleSheet('background:transparent;border:none;')
        cabecalho_layout=QVBoxLayout(cabecalho)
        cabecalho_layout.setContentsMargins(0,0,0,0)
        cabecalho_layout.setSpacing(7)
        titulo_1=QLabel('Iniciar Estudo',cabecalho)
        titulo_1.setObjectName('iniciarEstudoH36Titulo')
        titulo_1.setStyleSheet('color:#f5f9fc;background:transparent;font-family:"Segoe UI";font-size:30px;font-weight:700;')
        titulo_2=QLabel('Escolha como deseja estudar, praticar ou revisar.',cabecalho)
        titulo_2.setObjectName('iniciarEstudoH36Subtitulo')
        titulo_2.setWordWrap(True)
        titulo_2.setStyleSheet('color:#b8ccdd;background:transparent;font-family:"Segoe UI";font-size:16px;')
        cabecalho_layout.addWidget(titulo_1)
        cabecalho_layout.addWidget(titulo_2)
        col.addWidget(cabecalho,0)
        col.addStretch(1)
        # Quatro cartões horizontais, agrupados por função em duas linhas:
        # estudo (automático/manual) e avaliação/correção (simulados/erros).
        box=QWidget(conteudo)
        box.setObjectName('iniciarEstudoH36Cards')
        box.setAttribute(Qt.WA_NoSystemBackground, True)
        box.setAttribute(Qt.WA_TranslucentBackground, True)
        box.setStyleSheet('background:transparent;border:none;')
        grade=QGridLayout(box)
        grade.setContentsMargins(0,0,0,0)
        grade.setHorizontalSpacing(self.ESPACAMENTO_CARTOES)
        grade.setVerticalSpacing(self.ESPACAMENTO_CARTOES)
        # Mantém o mesmo callback do algoritmo de recomendação do Dashboard.
        self.cartao_automatico=CartaoIniciarEstudo(
            'Estudo Automático',
            'Continue pela próxima atividade recomendada.',
            'comecar',comecar,box)
        # O instalador da Grade conecta este cartão ao fluxo original,
        # sem criar um segundo botão ou uma segunda página.
        self.cartao_manual=CartaoIniciarEstudo(
            'Estudo Manual',
            'Escolha disciplinas e revisões na Grade.',
            'manual',None,box)
        self.cartao_simulados=CartaoIniciarEstudo(
            'Simulados',
            'Configure uma prova e avalie seu desempenho.',
            'simulados',abrir_simulados,box)
        self.cartao_erros=CartaoIniciarEstudo(
            'Banco de Erros',
            'Revise questões respondidas incorretamente.',
            'erros',abrir_erros,box)
        self.cartoes=[self.cartao_automatico,self.cartao_manual,
                      self.cartao_simulados,self.cartao_erros]
        self.grade_cartoes=grade
        self.cartoes_container=box
        self._ultima_colunas=None
        self._reorganizar_cartoes(1000)
        col.addWidget(box,0)
        # Parâmetros legados permanecem na assinatura para compatibilidade
        # com o main.py instalado; os outros destinos não são exibidos aqui.
        col.addStretch(2)
        scroll.setWidget(conteudo)
        main.addWidget(scroll)
        self.cenario=conteudo
        self.scroll=scroll
        self.scroll.viewport().installEventFilter(self)
        self.setStyleSheet('''
          QWidget#iniciarEstudoH36Page { background: #041829; border: none; }
          QScrollArea#iniciarEstudoH36Scroll { background: transparent; border: none; }
          QWidget#iniciarEstudoH36Cards { background: transparent; border: none; }
          QAbstractButton#iniciarEstudoH36_comecar,
          QAbstractButton#iniciarEstudoH36_manual,
          QAbstractButton#iniciarEstudoH36_simulados,
          QAbstractButton#iniciarEstudoH36_erros { background: transparent; border: none; }
          QScrollBar:vertical { background:#061b2d;width:8px; }
          QScrollBar::handle:vertical { background:#1c739a; border-radius:4px;min-height:30px; }
        ''')

    def _reorganizar_cartoes(self, largura):
        colunas=self.colunas_para_largura(max(0,int(largura)))
        if colunas == self._ultima_colunas:
            return
        self._ultima_colunas = colunas
        altura = self.ALTURA_CARTAO if colunas == 2 else 150
        for cartao in self.cartoes:
            cartao.setFixedHeight(altura)
        while self.grade_cartoes.count():
            self.grade_cartoes.takeAt(0)
        for coluna in range(4):
            self.grade_cartoes.setColumnStretch(coluna, 1 if coluna < colunas else 0)
        for i,cartao in enumerate(self.cartoes):
            self.grade_cartoes.addWidget(cartao,i//colunas,i%colunas)
        linhas=(len(self.cartoes)+colunas-1)//colunas
        self.cartoes_container.setFixedHeight(
            linhas*altura+(linhas-1)*self.ESPACAMENTO_CARTOES
        )
        self.cartoes_container.updateGeometry()

    def eventFilter(self,obj,event):
        if obj is self.scroll.viewport() and event.type()==QEvent.Resize:
            largura=obj.width()
            self._reorganizar_cartoes(largura-104)
        return super().eventFilter(obj,event)

    def showEvent(self,event):
        super().showEvent(event)
        largura=self.scroll.viewport().width()
        self._reorganizar_cartoes(largura-104)


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
                               janela.abrir_perfil_candidato,pagina,
                               abrir_simulados=janela.abrir_portal_treinos,
                               abrir_erros=janela.abrir_banco_erros)
    layout.addWidget(painel,1)
    scroll.hide()
    pagina._h36_painel=painel
    return painel
