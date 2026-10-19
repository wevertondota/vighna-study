"""Faixa de desenho sempre visível da Caneta de Estudo, inspirada no Paint.

Somente interface; mantém callbacks existentes, sem persistir anotações.
A barra fica fora do conteúdo rolável e das superfícies de rabiscos.
"""

from PySide6.QtCore import QPointF, QRectF, Qt, QSize
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap, QPolygonF
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QSizePolicy, QToolButton, QVBoxLayout, QWidget,
)


CORES = (
    ("#F2C94C", "Amarelo"),
    ("#E64848", "Vermelho"),
    ("#4096E8", "Azul"),
    ("#32B987", "Verde"),
)
ESPESSURAS = ((2, "Fina"), (3, "Média"), (6, "Grossa"))
FERRAMENTAS = (
    ("caneta", "Caneta livre", "caneta"),
    ("marcador", "Marca-texto transparente", "marcador"),
    ("borracha", "Borracha de traços", "borracha"),
    (None, "Modo leitura", "leitura"),
)


def _icone(nome, cor, tamanho=24):
    """Ícones vetoriais próprios; dispensam arquivos e fontes extras."""
    pix = QPixmap(72, 72)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.scale(3, 3)
    p.setPen(QPen(QColor(cor), 1.65, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(Qt.NoBrush)

    if nome == "caneta":
        p.save()
        p.translate(12, 12)
        p.rotate(43)
        p.drawRoundedRect(QRectF(-3.7, -10, 7.4, 15), 1.9, 1.9)
        p.drawLine(QPointF(-3.7, 5), QPointF(0, 10.5))
        p.drawLine(QPointF(3.7, 5), QPointF(0, 10.5))
        p.drawLine(QPointF(-3.7, -6.5), QPointF(3.7, -6.5))
        p.restore()
    elif nome == "marcador":
        p.save()
        p.translate(12, 12)
        p.rotate(43)
        p.drawRoundedRect(QRectF(-5, -9.5, 10, 12.5), 1.3, 1.3)
        p.drawLine(QPointF(-5, 1), QPointF(5, 1))
        p.drawPolygon(QPolygonF([QPointF(-5, 3), QPointF(5, 3),
                                  QPointF(2.5, 8.5), QPointF(-2.5, 8.5)]))
        p.drawLine(QPointF(-2.5, 10), QPointF(2.5, 10))
        p.restore()
    elif nome == "borracha":
        p.save()
        p.translate(12, 12)
        p.rotate(43)
        p.drawRoundedRect(QRectF(-6.5, -8.5, 13, 17), 2.0, 2.0)
        p.drawLine(QPointF(-6.5, 1.5), QPointF(6.5, 1.5))
        p.restore()
        p.drawLine(QPointF(4, 21), QPointF(20, 21))
    elif nome == "leitura":
        olho = QPainterPath()
        olho.moveTo(2.2, 12)
        olho.cubicTo(7.5, 4, 16.5, 4, 21.8, 12)
        olho.cubicTo(16.5, 20, 7.5, 20, 2.2, 12)
        p.drawPath(olho)
        p.drawEllipse(QPointF(12, 12), 3.6, 3.6)
    elif nome == "desfazer":
        caminho = QPainterPath(QPointF(6, 11))
        caminho.cubicTo(12, 7, 21, 9, 20, 16)
        caminho.cubicTo(19.6, 19, 17.2, 20, 14.8, 20)
        p.drawPath(caminho)
        p.drawLine(QPointF(6, 11), QPointF(11, 6))
        p.drawLine(QPointF(6, 11), QPointF(11, 15.5))
    elif nome == "limpar":
        p.drawRoundedRect(6, 7, 12, 14, 1.6, 1.6)
        p.drawLine(4, 7, 20, 7)
        p.drawLine(9, 5, 15, 5)
        p.drawLine(10, 10, 10, 17)
        p.drawLine(14, 10, 14, 17)
        p.drawLine(2.3, 2.3, 21.7, 21.7)
    p.end()
    return QIcon(pix)


def _icone_bolinha(cor, diametro=17):
    pix = QPixmap(72, 72)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(cor))
    p.drawEllipse(QPointF(36, 36), diametro * 1.5, diametro * 1.5)
    p.end()
    return QIcon(pix)


class FaixaCanetaEstudo(QFrame):
    """Paleta fixa e centralizada: modo leitura separado das ferramentas."""

    def __init__(self, on_modo, on_cor, on_espessura, on_desfazer, on_limpar, parent=None):
        super().__init__(parent)
        self.setObjectName("questionStudyInkRibbon")
        self._on_modo = on_modo
        self._on_cor = on_cor
        self._on_espessura = on_espessura
        self._on_desfazer = on_desfazer
        self._on_limpar = on_limpar
        self.botoes_modo = {}
        self.botoes_cor = {}
        self.botoes_espessura = {}

        base = QVBoxLayout(self)
        base.setContentsMargins(4, 0, 4, 0)
        base.setSpacing(0)

        # A barra permanece aberta. Em janelas estreitas a rolagem pertence
        # somente a esta faixa, nunca ao resolvedor inteiro.
        self.conteudo = QScrollArea(self)
        self.conteudo.setObjectName("questionStudyInkRibbonContent")
        self.conteudo.setFrameShape(QFrame.NoFrame)
        self.conteudo.setWidgetResizable(False)
        self.conteudo.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.conteudo.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.conteudo.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.conteudo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.conteudo.setMinimumWidth(0)
        self.conteudo.setFixedHeight(52)

        painel = QFrame()
        painel.setObjectName("questionStudyInkFloatingTools")
        painel.setFixedHeight(44)
        linha = QHBoxLayout(painel)
        linha.setContentsMargins(7, 4, 7, 4)
        linha.setSpacing(2)

        # Modo leitura isolado à esquerda: nunca é uma ferramenta de desenho.
        olho = QToolButton(painel)
        olho.setObjectName("questionStudyInkReadMode")
        olho.setFixedSize(36, 36)
        olho.setCheckable(True)
        olho.setIcon(_icone("leitura", "#9FB0BB"))
        olho.setIconSize(QSize(22, 22))
        olho.setAccessibleName("Modo leitura: cursor normal, desativar desenho")
        olho.setToolTip("Modo leitura — desativar a Caneta e voltar ao cursor normal")
        olho.clicked.connect(lambda _=False: self._on_modo(None))
        linha.addWidget(olho)
        self.botoes_modo[None] = olho
        # Mantém o atributo usado pela janela principal nas versões anteriores.
        # Não funciona como botão de recolher: é o próprio botão de leitura.
        self.botao_recolher = olho
        self._separador(linha, largura=14)

        for modo, nome, icone in FERRAMENTAS:
            if modo is None:
                continue
            botao = QToolButton(painel)
            botao.setObjectName("questionStudyInkTool")
            botao.setCheckable(True)
            botao.setFixedSize(34, 36)
            botao.setIcon(_icone(icone, "#8B97A1"))
            botao.setIconSize(QSize(21, 21))
            botao.setAccessibleName(nome)
            botao.setToolTip(nome + " — marcações temporárias")
            botao.clicked.connect(lambda _=False, valor=modo: self._on_modo(valor))
            linha.addWidget(botao)
            self.botoes_modo[modo] = botao
        self._separador(linha)

        for cor, nome in CORES:
            botao = QToolButton(painel)
            botao.setObjectName("questionStudyInkColor")
            botao.setFixedSize(29, 32)
            botao.setIcon(_icone_bolinha(cor, 12))
            botao.setIconSize(QSize(23, 23))
            botao.setCheckable(True)
            botao.setAccessibleName("Cor " + nome)
            botao.setToolTip("Selecionar cor " + nome)
            botao.clicked.connect(lambda _=False, valor=cor: self._on_cor(valor))
            linha.addWidget(botao)
            self.botoes_cor[cor] = botao
        self._separador(linha)

        for valor, nome in ESPESSURAS:
            botao = QToolButton(painel)
            botao.setObjectName("questionStudyInkWidth")
            botao.setFixedSize(27, 32)
            botao.setCheckable(True)
            botao.setIcon(_icone_bolinha("#89939C", {2: 4.0, 3: 6.5, 6: 9.5}[valor]))
            botao.setIconSize(QSize(22, 22))
            botao.setAccessibleName("Espessura " + nome)
            botao.setToolTip(f"Espessura {nome.lower()} ({valor} px)")
            botao.clicked.connect(lambda _=False, largura=valor: self._on_espessura(largura))
            linha.addWidget(botao)
            self.botoes_espessura[valor] = botao
        self._separador(linha)

        self.botao_desfazer = QToolButton(painel)
        self.botao_desfazer.setObjectName("questionStudyInkUndo")
        self.botao_desfazer.setFixedSize(36, 36)
        self.botao_desfazer.setIcon(_icone("desfazer", "#919BA4"))
        self.botao_desfazer.setIconSize(QSize(21, 21))
        self.botao_desfazer.setAccessibleName("Desfazer último traço")
        self.botao_desfazer.setToolTip("Desfazer a última anotação")
        self.botao_desfazer.clicked.connect(self._on_desfazer)
        linha.addWidget(self.botao_desfazer)

        self.botao_limpar = QToolButton(painel)
        self.botao_limpar.setObjectName("questionStudyInkClear")
        self.botao_limpar.setFixedSize(36, 36)
        self.botao_limpar.setIcon(_icone("limpar", "#919BA4"))
        self.botao_limpar.setIconSize(QSize(21, 21))
        self.botao_limpar.setAccessibleName("Limpar todas as marcações")
        self.botao_limpar.setToolTip("Apagar as marcações desta questão")
        self.botao_limpar.clicked.connect(self._on_limpar)
        linha.addWidget(self.botao_limpar)

        painel.adjustSize()
        self.conteudo.setWidget(painel)
        base.addWidget(self.conteudo)
        self.setStyleSheet("""
            QFrame#questionStudyInkRibbon { background: transparent; border: none; }
            QScrollArea#questionStudyInkRibbonContent { background: transparent; border: 0; }
            QFrame#questionStudyInkFloatingTools {
                background-color: #242A31; border: 1px solid #39404B;
                border-radius: 9px;
            }
            QToolButton#questionStudyInkReadMode,
            QToolButton#questionStudyInkTool,
            QToolButton#questionStudyInkColor,
            QToolButton#questionStudyInkWidth {
                border: 1px solid transparent; border-radius: 7px;
                background: transparent; padding: 0;
            }
            QToolButton#questionStudyInkReadMode {
                border: 1px solid #3E5665;
                background: #293844;
            }
            QToolButton#questionStudyInkReadMode:hover,
            QToolButton#questionStudyInkTool:hover,
            QToolButton#questionStudyInkColor:hover,
            QToolButton#questionStudyInkWidth:hover { background: #354A54; }
            QToolButton#questionStudyInkReadMode:checked {
                background: #124652; border: 2px solid #3CBBC7;
            }
            QToolButton#questionStudyInkTool:checked {
                background: #132F39; border: 1px solid #1D5360;
            }
            QToolButton#questionStudyInkColor:checked,
            QToolButton#questionStudyInkWidth:checked {
                background: #34434F; border: 1px solid #7194A3;
            }
            QToolButton#questionStudyInkUndo,
            QToolButton#questionStudyInkClear {
                background: #313840; border: 1px solid #424B55;
                border-radius: 7px; padding: 0;
            }
            QToolButton#questionStudyInkUndo:hover,
            QToolButton#questionStudyInkClear:hover { background: #40505B; }
            QToolButton#questionStudyInkUndo:disabled,
            QToolButton#questionStudyInkClear:disabled {
                background: #2B3037; border-color: #353D46;
            }
            QScrollBar:horizontal { max-height: 6px; background: transparent; }
            QScrollBar::handle:horizontal {
                background: #536676; border-radius: 3px; min-width: 28px;
            }
        """)

    @staticmethod
    def _separador(linha, largura=9):
        """Divisor real de 1 px, sem QWidget de fundo que herde o tema global."""
        largura = max(1, int(largura))
        margem_esquerda = (largura - 1) // 2
        margem_direita = largura - margem_esquerda - 1
        if margem_esquerda:
            linha.addSpacing(margem_esquerda)
        sep = QFrame()
        sep.setObjectName("questionStudyInkDivider")
        sep.setFixedSize(1, 20)
        sep.setStyleSheet(
            "QFrame#questionStudyInkDivider {"
            "background-color: #52606D; border: none;"
            "padding: 0; margin: 0; }"
        )
        linha.addWidget(sep, 0, Qt.AlignVCenter)
        if margem_direita:
            linha.addSpacing(margem_direita)

    def atualizar(self, modo, cor, espessura, pode_desfazer, ha_tracos):
        nomes = {None: "leitura", "caneta": "caneta", "marcador": "marcador", "borracha": "borracha"}
        for chave, botao in self.botoes_modo.items():
            ativo = chave == modo
            botao.setChecked(ativo)
            cor_icone = ("#76E3E8" if ativo else "#A5BAC6") if chave is None else ("#26AEB5" if ativo else "#8B97A1")
            botao.setIcon(_icone(nomes[chave], cor_icone))
        self.botao_recolher.setAccessibleDescription(
            "Modo leitura ativo: mouse normal" if modo is None else
            "Clique para desativar o desenho e voltar ao mouse normal"
        )
        for chave, botao in self.botoes_cor.items():
            botao.setChecked(chave == cor)
        for chave, botao in self.botoes_espessura.items():
            botao.setChecked(chave == espessura)
        self.botao_desfazer.setEnabled(bool(pode_desfazer))
        self.botao_limpar.setEnabled(bool(ha_tracos))
