"""Portal nativo da Central de Simulados (sem GIF e sem painel de desempenho).

O modulo e exclusivamente visual: os destinos continuam nos controladores do
main.py. Nao abre banco de dados, nao inicia sessoes e nao cria temporizadores.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QRectF, QPointF, QSize
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QBrush, QLinearGradient, QPolygonF
from PySide6.QtWidgets import (
    QWidget, QLabel, QFrame, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QScrollArea, QSizePolicy
)


class _IconeModalidade(QWidget):
    """Pictogramas vetoriais pintados localmente, sem imagens de fundo."""
    def __init__(self, tipo: str, parent=None):
        super().__init__(parent)
        self.tipo = tipo
        self.setFixedSize(72, 68)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.translate(6, 4)
        p.setPen(QPen(QColor('#ecf6ff'), 2.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        if self.tipo == 'livro':
            l = QPainterPath(QPointF(30, 50))
            l.cubicTo(QPointF(18, 42), QPointF(12, 43), QPointF(4, 44))
            l.lineTo(4, 10)
            l.cubicTo(QPointF(14, 7), QPointF(21, 9), QPointF(30, 17))
            r = QPainterPath(QPointF(30, 50))
            r.cubicTo(QPointF(42, 42), QPointF(48, 43), QPointF(56, 44))
            r.lineTo(56, 10)
            r.cubicTo(QPointF(46, 7), QPointF(39, 9), QPointF(30, 17))
            p.drawPath(l); p.drawPath(r)
            p.drawLine(30, 17, 30, 49)
            p.setPen(QPen(QColor('#02cefb'), 1.8)); p.drawLine(1, 21, 1, 48); p.drawLine(59, 21, 59, 48)
        elif self.tipo == 'alvo':
            p.drawEllipse(QPointF(26, 30), 23, 23)
            p.drawEllipse(QPointF(26, 30), 13, 13)
            p.drawEllipse(QPointF(26, 30), 3, 3)
            p.setPen(QPen(QColor('#01d4fd'), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawLine(QPointF(26, 30), QPointF(55, 3))
            p.drawLine(QPointF(55, 3), QPointF(54, 15))
            p.drawLine(QPointF(55, 3), QPointF(44, 5))
        elif self.tipo == 'prancheta':
            p.drawRoundedRect(QRectF(15, 12, 36, 43), 3, 3)
            p.drawRoundedRect(QRectF(24, 7, 17, 9), 2, 2)
            p.setPen(QPen(QColor('#0fd8fd'), 2.3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            for y in (27, 39, 50):
                p.drawLine(QPointF(22, y), QPointF(25, y+2))
                p.drawLine(QPointF(25, y+2), QPointF(29, y-3))
                p.drawLine(QPointF(34, y), QPointF(44, y))
        elif self.tipo == 'banco':
            p.drawEllipse(QRectF(9, 8, 41, 13))
            p.drawArc(QRectF(9, 17, 41, 13), 180*16, 180*16)
            p.drawArc(QRectF(9, 26, 41, 13), 180*16, 180*16)
            p.drawLine(9, 14, 9, 37)
            p.drawLine(50, 14, 50, 37)
            p.setPen(QPen(QColor('#07d4fe'), 2.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.setBrush(QBrush(QColor('#07324a')))
            p.drawEllipse(QPointF(49, 46), 11, 11)
            p.drawLine(45, 42, 53, 50)
            p.drawLine(53, 42, 45, 50)
        p.end()


class _CartaoModalidade(QPushButton):
    def __init__(self, titulo, descricao, icone, destaque, callback, parent=None):
        super().__init__(parent)
        self.setObjectName('simuladosCardDestaque' if destaque else 'simuladosCard')
        self.setAccessibleName(titulo)
        self.setToolTip(f'{titulo}: {descricao}')
        self.setCursor(Qt.PointingHandCursor)
        # Cartoes com dimensao previsivel e sem compressao por QScrollArea,
        # estilo QSS, DPI ou widgets expansivos acima deles.
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(228)
        self.setMinimumWidth(185)
        self.clicked.connect(lambda _=False: callback())
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 17, 14, 14)
        lay.setSpacing(10)
        lay.addWidget(_IconeModalidade(icone, self), 0, Qt.AlignHCenter)
        heading = QLabel(titulo, self)
        heading.setObjectName('simuladosCardTitle')
        heading.setAlignment(Qt.AlignHCenter)
        heading.setAttribute(Qt.WA_TransparentForMouseEvents)
        heading.setWordWrap(True)
        lay.addWidget(heading)
        desc = QLabel(descricao, self)
        desc.setObjectName('simuladosCardDescription')
        desc.setAlignment(Qt.AlignHCenter)
        desc.setWordWrap(True)
        desc.setAttribute(Qt.WA_TransparentForMouseEvents)
        desc.setMinimumHeight(42)
        lay.addWidget(desc)
        lay.addStretch(1)
        linha = QFrame(self)
        linha.setObjectName('simuladosCardAccent' if destaque else 'simuladosCardAccentNeutral')
        linha.setFixedSize(63, 3)
        linha.setAttribute(Qt.WA_TransparentForMouseEvents)
        lay.addWidget(linha, 0, Qt.AlignHCenter)


class _FundoSimulados(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._claro = False
        self._cards = []
        self._colunas = 0

    def definir_claro(self, valor):
        self._claro = bool(valor)
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._redistribuir()

    def _redistribuir(self):
        if not hasattr(self, 'grade'):
            return
        width = self.width()
        colunas = 4 if width >= 940 else (2 if width >= 495 else 1)
        if self._colunas == colunas:
            return
        self._colunas = colunas
        for c in self._cards:
            self.grade.removeWidget(c)
        for i, c in enumerate(self._cards):
            self.grade.addWidget(c, i // colunas, i % colunas)
        for coluna in range(4):
            self.grade.setColumnStretch(coluna, 1 if coluna < colunas else 0)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect())
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        if self._claro:
            grad.setColorAt(0, QColor('#ebf4fc'))
            grad.setColorAt(0.55, QColor('#d7e9f8'))
            grad.setColorAt(1, QColor('#c2dff3'))
            linha = QColor(30, 103, 153, 58)
        else:
            grad.setColorAt(0, QColor('#073756'))
            grad.setColorAt(0.32, QColor('#001729'))
            grad.setColorAt(0.75, QColor('#001323'))
            grad.setColorAt(1, QColor('#005078'))
            linha = QColor(4, 146, 209, 80)
        p.fillRect(rect, grad)
        p.setPen(QPen(linha, 1.6))
        curve = QPainterPath(QPointF(-80, 180))
        curve.cubicTo(QPointF(230, 80), QPointF(210, 3), QPointF(580, -48))
        p.drawPath(curve)
        curve2 = QPainterPath(QPointF(self.width() * 0.67, self.height() + 24))
        curve2.cubicTo(QPointF(self.width() * 0.82, self.height() * 0.91), QPointF(self.width() * 0.95, self.height() * 0.91), QPointF(self.width() + 40, self.height() * 0.68))
        p.drawPath(curve2)
        p.end()


class PortalSimuladosNativo(QWidget):
    def __init__(self, *, perfil_ativo, logo, abrir_revisao, abrir_treino,
                 abrir_simulado, abrir_erros, retomar_sessao):
        super().__init__()
        self.setObjectName('centralSimuladosRoot')
        self.setMinimumSize(400, 400)
        self._retomar_sessao_callback = retomar_sessao
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea(self)
        scroll.setObjectName('centralSimuladosScroll')
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        root.addWidget(scroll)
        self.canvas = _FundoSimulados(scroll)
        self.canvas.setObjectName('centralSimuladosCanvas')
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.canvas.setMinimumHeight(560)
        # IMPORTANTE: configurar inteiramente o layout do canvas ANTES de
        # associar o widget ao QScrollArea. O Qt pode ignorar a nova geometria
        # de widgets cujo layout for instalado depois do setWidget().
        coluna = QVBoxLayout(self.canvas)
        coluna.setContentsMargins(26, 12, 26, 30)
        coluna.setSpacing(0)

        topo = QHBoxLayout()
        topo.setContentsMargins(0, 0, 0, 0)
        topo.setSpacing(10)
        # Espaco simetrico ao cartao de perfil: logotipo centralizado na tela.
        topo.addSpacing(170)
        topo.addStretch(1)
        marca = QWidget(self.canvas)
        marca_lay = QHBoxLayout(marca)
        marca_lay.setContentsMargins(0, 0, 0, 0)
        marca_lay.setSpacing(10)
        self.logo = QLabel(marca)
        self.logo.setFixedSize(51, 58)
        self.logo.setAlignment(Qt.AlignCenter)
        if logo is not None and not logo.isNull():
            self.logo.setPixmap(logo.scaled(QSize(50, 55), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        marca_lay.addWidget(self.logo)
        marca_titulos = QVBoxLayout()
        marca_titulos.setSpacing(1)
        nome = QLabel('Vighna<span style="color:#07d5ff">Study</span>', marca)
        nome.setObjectName('centralSimuladosMarca')
        nome.setTextFormat(Qt.RichText)
        marca_titulos.addWidget(nome)
        subtitulo = QLabel('S I S T E M A  D E  E S T U D O S  A V A N Ç A D O', marca)
        subtitulo.setObjectName('centralSimuladosMarcaSub')
        marca_titulos.addWidget(subtitulo)
        marca_lay.addLayout(marca_titulos)
        topo.addWidget(marca, 0, Qt.AlignHCenter)
        topo.addStretch(1)
        perfil_card = QFrame(self.canvas)
        perfil_card.setObjectName('centralSimuladosPerfil')
        perfil_card.setFixedWidth(170)
        perfil_lay = QVBoxLayout(perfil_card)
        perfil_lay.setContentsMargins(12, 7, 12, 7)
        perfil_lay.setSpacing(2)
        legenda = QLabel('◆   PERFIL ATIVO', perfil_card)
        legenda.setObjectName('centralSimuladosPerfilLegenda')
        perfil_lay.addWidget(legenda)
        self.perfil_nome = QLabel(perfil_ativo or '—', perfil_card)
        self.perfil_nome.setObjectName('centralSimuladosPerfilNome')
        self.perfil_nome.setWordWrap(True)
        perfil_lay.addWidget(self.perfil_nome)
        topo.addWidget(perfil_card, 0, Qt.AlignTop)
        coluna.addLayout(topo)
        coluna.addSpacing(32)

        titulo_linha = QHBoxLayout()
        titulo_linha.setSpacing(17)
        icon_header = _IconeModalidade('prancheta', self.canvas)
        icon_header.setFixedSize(64, 62)
        titulo_linha.addWidget(icon_header, 0, Qt.AlignVCenter)
        divisor = QFrame(self.canvas)
        divisor.setObjectName('centralSimuladosDivisor')
        divisor.setFixedSize(2, 52)
        titulo_linha.addWidget(divisor, 0, Qt.AlignVCenter)
        textos = QVBoxLayout()
        textos.setSpacing(3)
        heading = QLabel('Central de Simulados', self.canvas)
        heading.setObjectName('centralSimuladosTitulo')
        textos.addWidget(heading)
        intro = QLabel('Pratique, avalie e aperfeiçoe seu desempenho.', self.canvas)
        intro.setObjectName('centralSimuladosSubtitulo')
        textos.addWidget(intro)
        titulo_linha.addLayout(textos, 1)
        coluna.addLayout(titulo_linha)
        coluna.addSpacing(32)

        self.canvas.grade = QGridLayout()
        self.canvas.grade.setContentsMargins(0, 0, 0, 0)
        self.canvas.grade.setHorizontalSpacing(12)
        self.canvas.grade.setVerticalSpacing(14)
        self.canvas._cards = [
            _CartaoModalidade('Revisão Inteligente', 'Reforce conteúdos que precisam de revisão.', 'livro', True, abrir_revisao, self.canvas),
            _CartaoModalidade('Treino Adaptativo', 'Pratique questões com foco no seu desempenho.', 'alvo', False, abrir_treino, self.canvas),
            _CartaoModalidade('Simulado', 'Teste seus conhecimentos em condições de prova.', 'prancheta', False, abrir_simulado, self.canvas),
            _CartaoModalidade('Banco de Erros', 'Revisite questões erradas e consolide o aprendizado.', 'banco', False, abrir_erros, self.canvas),
        ]
        coluna.addLayout(self.canvas.grade)
        self.canvas._redistribuir()
        coluna.addSpacing(20)

        self.botao_retomar = QPushButton('Retomar sessão em andamento', self.canvas)
        self.botao_retomar.setObjectName('centralSimuladosRetomar')
        self.botao_retomar.clicked.connect(lambda _=False: self._retomar_sessao_callback())
        self.botao_retomar.setVisible(False)
        self.botao_retomar.setMinimumHeight(38)
        coluna.addWidget(self.botao_retomar, 0, Qt.AlignLeft)
        coluna.addStretch(1)
        # Depois de prontos os widgets, as alturas e a grade responsiva,
        # somente agora vincula o canvas ao scroll area.
        scroll.setWidget(self.canvas)
        self.canvas._colunas = 0
        self.canvas._redistribuir()
        self.set_perfil(perfil_ativo)
        aplicar_tema_central_simulados(self, 'futurista')

    def set_perfil(self, nome):
        self.perfil_nome.setText(str(nome or '—').strip() or '—')

    def atualizar_retomada(self, existe, detalhes=''):
        self.botao_retomar.setVisible(bool(existe))
        if existe:
            self.botao_retomar.setToolTip(detalhes or 'Trazer a sessão ativa para a frente.')


def aplicar_tema_central_simulados(portal, tema):
    tema = str(tema).strip().lower()
    claro = tema == 'claro'
    portal.canvas.definir_claro(claro)
    texto = '#17354d' if claro else '#f3f9ff'
    secundario = '#38667d' if claro else '#afc5d6'
    bg = '#f9fdff' if claro else '#04253c'
    contorno = '#78abc8' if claro else '#356d91'
    hover = '#e8f7ff' if claro else '#083653'
    portal.setStyleSheet('''
        QScrollArea#centralSimuladosScroll, QWidget#centralSimuladosRoot,
        QWidget#centralSimuladosCanvas {border: none; background: transparent;}
        QLabel {background: transparent; border: none; color: %(texto)s;}
        QLabel#centralSimuladosMarca {font-size: 25px; font-weight: 800; color: %(texto)s;}
        QLabel#centralSimuladosMarcaSub {font-size: 8px; letter-spacing: 1px; color: %(secundario)s;}
        QLabel#centralSimuladosTitulo {font-size: 29px; font-weight: 800; color: %(texto)s;}
        QLabel#centralSimuladosSubtitulo {font-size: 13px; font-weight: 400; color: %(secundario)s;}
        QFrame#centralSimuladosPerfil {border: 1px solid %(contorno)s;
          border-radius: 12px; background: %(bg)s;}
        QLabel#centralSimuladosPerfilLegenda {font-size: 9px; font-weight: 600; color: %(secundario)s;}
        QLabel#centralSimuladosPerfilNome {font-size: 13px; font-weight: 700; color: %(texto)s;}
        QFrame#centralSimuladosDivisor {background: #1bb9ed; border: none;}
        QPushButton#simuladosCard, QPushButton#simuladosCardDestaque {
          background: %(bg)s; border: 1px solid %(contorno)s;
          border-radius: 15px; padding: 0px; color: %(texto)s;}
        QPushButton#simuladosCard:hover, QPushButton#simuladosCard:focus,
        QPushButton#simuladosCardDestaque:hover, QPushButton#simuladosCardDestaque:focus {
          background: %(hover)s; border: 2px solid #09cdf6; }
        QPushButton#simuladosCardDestaque {border: 2px solid #05d6ff;}
        QLabel#simuladosCardTitle {font-size: 16px; font-weight: 750; color: %(texto)s;}
        QLabel#simuladosCardDescription {font-size: 12px; color: %(secundario)s;}
        QFrame#simuladosCardAccent {border: none; background: #08d5fd;}
        QFrame#simuladosCardAccentNeutral {border: none; background: #90aabd;}
        QPushButton#centralSimuladosRetomar {background: %(bg)s; border: 1px solid #07bfd9;
          color: %(texto)s; font-size: 13px; border-radius: 9px; padding: 7px 15px;}
        QPushButton#centralSimuladosRetomar:hover {background: %(hover)s;}
    ''' % dict(texto=texto, secundario=secundario, bg=bg, contorno=contorno, hover=hover))
