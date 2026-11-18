"""Portal Qt da Central de Simulados — harmonia visual profissional R1.

Somente apresentacao: quatro rotas originais, sem novos acessos ao banco,
sem alteracao de sessao, controladores, timers, filtros ou sistema de estudos.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QRectF, QPointF, QSize
from PySide6.QtGui import (
    QColor, QPainter, QPainterPath, QPen, QBrush, QLinearGradient,
)
from PySide6.QtWidgets import (
    QWidget, QLabel, QFrame, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QScrollArea, QSizePolicy,
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
    '''Um único alvo interativo: sem botões falsos ou sublinhados decorativos.'''

    ALTURA = 224

    def __init__(self, titulo, descricao, icone, destaque, callback, parent=None):
        super().__init__(parent)
        # Mantém o parâmetro legado "destaque", mas não privilegia um modo.
        self.setObjectName('simuladosCard')
        self.setAccessibleName(titulo)
        self.setAccessibleDescription(descricao)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(self.ALTURA)
        self.setMinimumWidth(208)
        if callable(callback):
            self.clicked.connect(lambda _=False: callback())
        else:
            self.setEnabled(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 23, 16, 18)
        layout.setSpacing(8)
        icone_widget = _IconeModalidade(icone, self)
        icone_widget.setFixedSize(72, 68)
        layout.addWidget(icone_widget, 0, Qt.AlignHCenter)
        layout.addSpacing(5)

        titulo_widget = QLabel(titulo, self)
        titulo_widget.setObjectName('simuladosCardTitle')
        titulo_widget.setAlignment(Qt.AlignHCenter)
        titulo_widget.setWordWrap(True)
        titulo_widget.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        layout.addWidget(titulo_widget)

        descricao_widget = QLabel(descricao, self)
        descricao_widget.setObjectName('simuladosCardDescription')
        descricao_widget.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        descricao_widget.setWordWrap(True)
        descricao_widget.setMinimumHeight(40)
        descricao_widget.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        layout.addWidget(descricao_widget)
        layout.addStretch(1)


class _FundoSimulados(QWidget):
    '''Superfície vetorial próxima da Home R2, sem recursos externos.'''

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
        largura = self.width()
        colunas = 4 if largura >= 1010 else (2 if largura >= 530 else 1)
        if self._colunas == colunas:
            return
        self._colunas = colunas
        for card in self._cards:
            self.grade.removeWidget(card)
        for i, card in enumerate(self._cards):
            self.grade.addWidget(card, i // colunas, i % colunas)
        for coluna in range(4):
            self.grade.setColumnStretch(coluna, 1 if coluna < colunas else 0)
        # Não permitir que uma linha vazia comprima os cartões.
        for linha in range(4):
            self.grade.setRowStretch(linha, 0)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        w, h = float(self.width()), float(self.height())
        reto = QRectF(self.rect())
        grad = QLinearGradient(0, 0, w, h)
        if self._claro:
            for pos, cor in ((0, '#e5f2fc'), (.50, '#f2f8fd'), (1, '#d3e8f7')):
                grad.setColorAt(pos, QColor(cor))
            traco = QColor(24, 107, 157, 47)
            faixa = QColor(28, 107, 158, 13)
        else:
            for pos, cor in ((0, '#082b43'), (.42, '#051d30'), (1, '#04192b')):
                grad.setColorAt(pos, QColor(cor))
            traco = QColor(11, 151, 193, 62)
            faixa = QColor(16, 107, 151, 22)
        p.fillRect(reto, grad)
        p.setPen(Qt.NoPen)
        p.setBrush(faixa)
        curva = QPainterPath()
        curva.moveTo(0, 0)
        curva.lineTo(w * .42, 0)
        curva.cubicTo(w * .31, 45, w * .17, 91, 0, 137)
        curva.closeSubpath()
        p.drawPath(curva)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(traco, 1.0))
        borda = QPainterPath(QPointF(0, 139))
        borda.cubicTo(QPointF(w * .18, 91), QPointF(w * .31, 45), QPointF(w * .43, 0))
        p.drawPath(borda)
        curva_inferior = QPainterPath(QPointF(w * .61, h + 4))
        curva_inferior.cubicTo(QPointF(w * .79, h * .89), QPointF(w * .95, h * .92), QPointF(w + 8, h * .81))
        p.drawPath(curva_inferior)
        p.end()


class PortalSimuladosNativo(QWidget):
    '''Central de quatro modalidades, mantendo a API invocada por main.py.'''

    def __init__(self, *, perfil_ativo, logo, abrir_revisao, abrir_treino,
                 abrir_simulado, abrir_erros, retomar_sessao):
        super().__init__()
        self.setObjectName('centralSimuladosRoot')
        self.setMinimumSize(400, 400)
        # "logo" continua na assinatura para compatibilidade com o controlador.
        # A marca já está presente na Home; repetir o logotipo aqui a sobrecarregava.
        self._retomar_sessao_callback = retomar_sessao
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
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
        # Preparar todo o layout antes de scroll.setWidget.
        coluna = QVBoxLayout(self.canvas)
        coluna.setContentsMargins(30, 34, 30, 32)
        coluna.setSpacing(0)

        topo = QHBoxLayout()
        topo.setContentsMargins(0, 0, 0, 0)
        topo.setSpacing(16)
        textos = QVBoxLayout()
        textos.setContentsMargins(0, 0, 0, 0)
        textos.setSpacing(5)
        heading = QLabel('Central de Simulados', self.canvas)
        heading.setObjectName('centralSimuladosTitulo')
        textos.addWidget(heading)
        intro = QLabel('Pratique, avalie e aperfeiçoe seu desempenho.', self.canvas)
        intro.setObjectName('centralSimuladosSubtitulo')
        intro.setWordWrap(True)
        textos.addWidget(intro)
        topo.addLayout(textos, 1)

        perfil = QFrame(self.canvas)
        perfil.setObjectName('centralSimuladosPerfil')
        perfil.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        perfil_lay = QHBoxLayout(perfil)
        perfil_lay.setContentsMargins(13, 9, 13, 9)
        perfil_lay.setSpacing(8)
        self.perfil_nome = QLabel('', perfil)
        self.perfil_nome.setObjectName('centralSimuladosPerfilNome')
        self.perfil_nome.setWordWrap(False)
        self.perfil_nome.setMaximumWidth(250)
        perfil_lay.addWidget(self.perfil_nome)
        topo.addWidget(perfil, 0, Qt.AlignTop)
        coluna.addLayout(topo)
        coluna.addSpacing(68)

        self.canvas.grade = QGridLayout()
        self.canvas.grade.setContentsMargins(0, 0, 0, 0)
        self.canvas.grade.setHorizontalSpacing(15)
        self.canvas.grade.setVerticalSpacing(15)
        self.canvas._cards = [
            _CartaoModalidade('Revisão Inteligente',
                'Reforce conteúdos que precisam de revisão.', 'livro', False,
                abrir_revisao, self.canvas),
            _CartaoModalidade('Treino Adaptativo',
                'Pratique questões com foco no seu desempenho.', 'alvo', False,
                abrir_treino, self.canvas),
            _CartaoModalidade('Simulado',
                'Teste seus conhecimentos em condições de prova.', 'prancheta', False,
                abrir_simulado, self.canvas),
            _CartaoModalidade('Banco de Erros',
                'Revisite questões erradas e consolide o aprendizado.', 'banco', False,
                abrir_erros, self.canvas),
        ]
        coluna.addLayout(self.canvas.grade)
        coluna.addSpacing(20)

        self.botao_retomar = QPushButton('Retomar sessão em andamento', self.canvas)
        self.botao_retomar.setObjectName('centralSimuladosRetomar')
        self.botao_retomar.setCursor(Qt.PointingHandCursor)
        self.botao_retomar.setFocusPolicy(Qt.StrongFocus)
        self.botao_retomar.clicked.connect(lambda _=False: self._retomar_sessao_callback())
        self.botao_retomar.setVisible(False)
        self.botao_retomar.setMinimumHeight(38)
        coluna.addWidget(self.botao_retomar, 0, Qt.AlignLeft)
        coluna.addStretch(1)

        scroll.setWidget(self.canvas)
        self.canvas._colunas = 0
        self.canvas._redistribuir()
        self.set_perfil(perfil_ativo)
        aplicar_tema_central_simulados(self, 'futurista')

    def set_perfil(self, nome):
        nome = str(nome or '—').strip() or '—'
        self.perfil_nome.setText('Perfil: ' + nome)
        # Tooltip exclusivamente para texto longo truncado, não por padrão.
        self.perfil_nome.setToolTip(nome if len(nome) > 30 else '')

    def atualizar_retomada(self, existe, detalhes=''):
        self.botao_retomar.setVisible(bool(existe))
        if existe:
            self.botao_retomar.setToolTip(detalhes or 'Trazer a sessão ativa para a frente.')
        else:
            self.botao_retomar.setToolTip('')


def aplicar_tema_central_simulados(portal, tema):
    tema = str(tema).strip().lower()
    claro = tema == 'claro'
    portal.canvas.definir_claro(claro)
    texto = '#183b54' if claro else '#f2f7fc'
    secundario = '#416b80' if claro else '#aec6d8'
    fundo = '#f9fdff' if claro else '#0b273d'
    fundo_primario = '#f0f8fd' if claro else '#103149'
    contorno = '#93b7cc' if claro else '#38617a'
    hover = '#e7f6ff' if claro else '#12354e'
    portal.setStyleSheet('''
        QScrollArea#centralSimuladosScroll,
        QWidget#centralSimuladosRoot, QWidget#centralSimuladosCanvas {
          border: none; background: transparent;
        }
        QLabel {background: transparent; border: none; color: %(texto)s;}
        QLabel#centralSimuladosTitulo {
          font-family: "Segoe UI"; font-size: 30px; font-weight: 700; color: %(texto)s;
        }
        QLabel#centralSimuladosSubtitulo {
          font-family: "Segoe UI"; font-size: 15px; color: %(secundario)s;
        }
        QFrame#centralSimuladosPerfil {
          border: 1px solid %(contorno)s; border-radius: 10px;
          background: %(fundo)s;
        }
        QLabel#centralSimuladosPerfilNome {
          font-family: "Segoe UI"; font-size: 12px; font-weight: 600;
          color: %(texto)s;
        }
        QPushButton#simuladosCard {
          background: %(fundo)s; border: 1px solid %(contorno)s;
          border-radius: 15px; padding: 0px; color: %(texto)s;
        }
        QPushButton#simuladosCard:hover {
          background: %(fundo_primario)s;
          border: 1px solid #16bad8;
        }
        QPushButton#simuladosCard:focus {
          background: %(hover)s;
          border: 2px solid #19d1ed;
        }
        QPushButton#simuladosCard:pressed {
          background: %(fundo_primario)s;
          border: 1px solid #12b8d5;
        }
        QLabel#simuladosCardTitle {
          font-family: "Segoe UI"; font-size: 18px;
          font-weight: 700; color: %(texto)s;
        }
        QLabel#simuladosCardDescription {
          font-family: "Segoe UI"; font-size: 13px;
          color: %(secundario)s;
        }
        QPushButton#centralSimuladosRetomar {
          font-family: "Segoe UI"; background: %(fundo_primario)s;
          border: 1px solid #149fbe; color: %(texto)s;
          font-size: 13px; border-radius: 9px; padding: 7px 15px;
        }
        QPushButton#centralSimuladosRetomar:hover,
        QPushButton#centralSimuladosRetomar:focus {
          background: %(hover)s; border: 1px solid #17c8e7;
        }
    ''' % dict(texto=texto, secundario=secundario, fundo=fundo,
               fundo_primario=fundo_primario, contorno=contorno, hover=hover))
