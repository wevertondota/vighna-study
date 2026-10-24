"""Biblioteca Futurista — portal de Disciplinas, visualização somente leitura.

Mantém os contratos do VighnaStudy: listar_disciplinas, listar_topicos,
abrir_disciplina, editar_disciplinas e voltar_inicio. A montagem não
modifica dados, não cria banco e não implementa editor alternativo.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QRectF, QPointF, QEvent, QTimer
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView, QBoxLayout, QComboBox, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy,
    QStackedWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from ui.disciplina_grade_data import resumir_disciplinas

# Cores e dimensões extraídas do dossiê oficial 1304×705; os pixels do
# mockup são físicos, enquanto o Qt usa pixels lógicos dependentes do DPI.
QSS_BIBLIOTECA = r"""
QWidget#portalDisciplinasPage, QWidget#bibliotecaBody,
QWidget#bibliotecaCardsHost, QWidget#bibliotecaScrollViewport,
QWidget#bibliotecaAlternativeView {
    background-color: #051523; border: none;
}
QScrollArea#bibliotecaScroll, QScrollArea#bibliotecaScroll > QWidget > QWidget {
    background-color: #051523; border: none;
}
/* Os contêineres intermediários não podem herdar o preenchimento escuro
   global do QSS; o acabamento pertence aos painéis Header, Hero e Cards. */
QWidget#bibliotecaMetrics,
QWidget#bibliotecaHeroRight,
QWidget#bibliotecaTools,
QWidget#bibliotecaSection,
QWidget#bibliotecaFooter,
QStackedWidget#bibliotecaViews {
    background: transparent;
    border: none;
}
QFrame#bibliotecaHeader {
    background: #0B2032; border: 1px solid #17435B; border-radius: 14px;
}
QFrame#bibliotecaHero {
    background: #08263E; border: 1px solid #147697; border-radius: 15px;
}
QFrame#bibliotecaCard {
    background: #0B2336; border: 1px solid #22526A; border-radius: 11px;
}
QFrame#bibliotecaCard[selected="true"] {
    background: #0D3047; border: 1px solid #14C9EB;
}
QFrame#bibliotecaCard:hover { border-color: #288CAB; }
QFrame#bibliotecaCard:focus { border: 2px solid #63DFC4; }
QFrame#bibliotecaCard[selected="true"]:hover { border-color: #14C9EB; }
QFrame#bibliotecaIconBox {
    background: #10364B; border: 1px solid #21627D; border-radius: 9px;
}
QLabel#bibliotecaTitle {
    color: #F0F8FF; font-size: 25px; font-weight: 800; background: transparent;
}
QLabel#bibliotecaSubtitle, QLabel#bibliotecaSecondary,
QLabel#bibliotecaCardDetail, QLabel#bibliotecaHeroDescription {
    color: #96B8C9; font-size: 12px; background: transparent;
}
QLabel#bibliotecaMetricNumber {
    color: #F0F8FF; font-size: 23px; font-weight: 800; background: transparent;
}
QLabel#bibliotecaMetricCaption {
    color: #96B8C9; font-size: 11px; background: transparent;
}
QLabel#bibliotecaEyebrow {
    color: #62BDDE; font-size: 11px; font-weight: 800; background: transparent;
}
QLabel#bibliotecaHeroTitle {
    color: #F0F8FF; font-size: 29px; font-weight: 800; background: transparent;
}
QLabel#bibliotecaHeroCount {
    color: #12CFF5; font-size: 34px; font-weight: 800; background: transparent;
}
QLabel#bibliotecaHeroCountDetail {
    color: #96B8C9; font-size: 12px; background: transparent;
}
QLabel#bibliotecaSectionTitle {
    color: #F0F8FF; font-size: 18px; font-weight: 750; background: transparent;
}
QLabel#bibliotecaCardName {
    color: #F0F8FF; font-size: 14px; font-weight: 750; background: transparent;
}
QLabel#bibliotecaStatus {
    color: #63DFC4; font-size: 11px; font-weight: 700; background: transparent;
}
QLabel#bibliotecaStatus[status="empty"],
QLabel#bibliotecaStatus[status="paused"] { color: #E8AD67; }
/* Apenas o estado do painel selecionado recebe o chip do dossiê.
   O status de cada card continua com a tipografia e geometria anteriores. */
QLabel#bibliotecaStatus[heroChip="true"] {
    background-color: rgba(22, 99, 81, 0.28);
    border: 1px solid rgba(99, 223, 196, 0.35);
    border-radius: 8px;
    padding: 2px 9px;
}
QLabel#bibliotecaStatus[heroChip="true"][status="empty"],
QLabel#bibliotecaStatus[heroChip="true"][status="paused"] {
    background-color: rgba(118, 79, 34, 0.26);
    border-color: rgba(232, 173, 103, 0.40);
}
QFrame#bibliotecaDivider {
    background-color: #22526A; border: none; min-width: 1px; max-width: 1px;
}
QFrame#bibliotecaCardDivider {
    background-color: #22526A; border: none; min-height: 1px; max-height: 1px;
}
QPushButton#bibliotecaManage, QPushButton#bibliotecaCardAction,
QPushButton#bibliotecaBack, QPushButton#bibliotecaMode {
    color: #D5ECF8; background: #0B2235; border: 1px solid #22526A;
    border-radius: 9px; font-size: 12px; font-weight: 750;
}
QPushButton#bibliotecaManage:hover, QPushButton#bibliotecaCardAction:hover,
QPushButton#bibliotecaBack:hover { background: #16435B; border-color: #14C9EB; }
QPushButton#bibliotecaManage:focus, QPushButton#bibliotecaCardAction:focus,
QPushButton#bibliotecaBack:focus, QPushButton#bibliotecaMode:focus {
    border: 2px solid #63DFC4;
}
QPushButton#bibliotecaPrimary {
    color: #F0F8FF; background: #0A6587; border: 1px solid #128DB2;
    border-radius: 9px; font-size: 12px; font-weight: 800;
}
QPushButton#bibliotecaPrimary:hover { background: #0D789A; border-color: #14C9EB; }
QPushButton#bibliotecaPrimary:disabled { color: #6B8799; background: #092536; border-color: #205068; }
QPushButton#bibliotecaPrimary:focus { border: 2px solid #63DFC4; }
QPushButton#bibliotecaCardAction { border: none; background: transparent; color: #96B8C9; }
QFrame#bibliotecaCard[selected="true"] QPushButton#bibliotecaCardAction { color: #12CFF5; }
QPushButton#bibliotecaCardAction:hover { color: #63DFC4; background: transparent; border: none; }
QPushButton#bibliotecaMode:checked { background: #0C425A; border-color: #14C9EB; color: #F0F8FF; }
QLineEdit#bibliotecaSearch, QComboBox#bibliotecaFilter, QComboBox#bibliotecaSort {
    background: #0B2235; color: #D5ECF8; border: 1px solid #22526A;
    border-radius: 9px; padding: 5px 12px; font-size: 12px;
}
QLineEdit#bibliotecaSearch:focus, QComboBox#bibliotecaFilter:focus,
QComboBox#bibliotecaSort:focus { border-color: #14C9EB; }
QComboBox#bibliotecaFilter::drop-down, QComboBox#bibliotecaSort::drop-down { border: none; width: 25px; }
QComboBox#bibliotecaFilter QAbstractItemView, QComboBox#bibliotecaSort QAbstractItemView {
    background: #0B2235; color: #F0F8FF; selection-background-color: #0D3047;
}
QTableWidget#bibliotecaTable {
    background: #0B2336; alternate-background-color: #0B2032;
    color: #F0F8FF; gridline-color: #22526A; border: 1px solid #22526A;
    border-radius: 10px; font-size: 12px;
    selection-background-color: #0D3047; selection-color: #F0F8FF;
}
QTableWidget#bibliotecaTable QHeaderView::section {
    background: #0B2032; color: #D5ECF8; border: none;
    border-right: 1px solid #22526A; border-bottom: 1px solid #22526A;
    padding: 8px;
}
"""


class IconeBiblioteca(QWidget):
    """Ícone vetorial simples desenhado em QPainter; não requer arquivos externos."""

    def __init__(self, tipo="book", tamanho=32, parent=None):
        super().__init__(parent)
        self.tipo = tipo
        self.setFixedSize(tamanho, tamanho)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        cor = QColor("#54C9E7")
        painter.setPen(QPen(cor, 1.7))
        painter.setBrush(Qt.NoBrush)
        w = float(self.width()); h = float(self.height())
        painter.translate(w / 2.0, h / 2.0)
        painter.scale(min(w, h) / 30.0, min(w, h) / 30.0)
        r = lambda x, y, aw, ah: QRectF(x, y, aw, ah)
        tipo = self.tipo
        if tipo == "library":
            # Marca do cabeçalho do dossiê: três colunas verticais; o ícone
            # de livro usado pelas disciplinas permanece sem alterações.
            painter.setBrush(QBrush(QColor(18, 207, 245, 110)))
            painter.drawRoundedRect(r(-11, -1, 5, 12), 1.1, 1.1)
            painter.drawRoundedRect(r(-3, -10, 5, 21), 1.1, 1.1)
            painter.drawRoundedRect(r(5, -5, 5, 16), 1.1, 1.1)
        elif tipo == "book":
            painter.drawRoundedRect(r(-11, -10, 9, 20), 2, 2)
            painter.drawRoundedRect(r(2, -10, 9, 20), 2, 2)
            painter.drawLine(-8, -6, -5, -6)
            painter.drawLine(5, -6, 8, -6)
        elif tipo == "calculator":
            painter.drawRoundedRect(r(-9, -11, 18, 22), 2, 2)
            painter.drawRect(r(-6, -7, 12, 4))
            for x in (-5, 0, 5):
                for y in (2, 7):
                    painter.drawEllipse(QPointF(x, y), 1, 1)
        elif tipo == "scales":
            painter.drawLine(0, -11, 0, 10)
            painter.drawLine(-11, -5, 11, -5)
            painter.drawLine(-8, -5, -11, 3)
            painter.drawLine(-5, -5, -2, 3)
            painter.drawLine(5, -5, 2, 3)
            painter.drawLine(8, -5, 11, 3)
            painter.drawLine(-12, 4, -1, 4)
            painter.drawLine(1, 4, 12, 4)
            painter.drawLine(-7, 10, 7, 10)
        elif tipo == "monitor":
            painter.drawRoundedRect(r(-12, -9, 24, 17), 2, 2)
            painter.drawLine(0, 8, 0, 12)
            painter.drawLine(-6, 12, 6, 12)
        elif tipo == "shield":
            from PySide6.QtGui import QPainterPath
            path = QPainterPath()
            path.moveTo(0, -12)
            path.lineTo(10, -8)
            path.lineTo(9, 2)
            path.quadTo(7, 8, 0, 12)
            path.quadTo(-7, 8, -9, 2)
            path.lineTo(-10, -8)
            path.closeSubpath()
            painter.drawPath(path)
            painter.drawLine(-4, 0, -1, 4)
            painter.drawLine(-1, 4, 5, -4)
        elif tipo == "building":
            painter.drawLine(-12, -5, 0, -12)
            painter.drawLine(0, -12, 12, -5)
            painter.drawLine(-12, -5, 12, -5)
            painter.drawLine(-12, 10, 12, 10)
            for x in (-7, 0, 7):
                painter.drawLine(x, -3, x, 8)
        elif tipo == "briefcase":
            painter.drawRoundedRect(r(-12, -6, 24, 17), 2, 2)
            painter.drawRoundedRect(r(-5, -11, 10, 5), 1, 1)
            painter.drawLine(-12, 1, 12, 1)
        elif tipo == "car":
            painter.drawRoundedRect(r(-12, -2, 24, 11), 2, 2)
            painter.drawLine(-8, -2, -5, -8)
            painter.drawLine(-5, -8, 5, -8)
            painter.drawLine(5, -8, 8, -2)
            painter.drawEllipse(QPointF(-7, 9), 2, 2)
            painter.drawEllipse(QPointF(7, 9), 2, 2)
        elif tipo == "edit":
            painter.drawRect(r(-10, -10, 19, 19))
            painter.drawLine(-5, 4, 7, -8)
        else:
            painter.drawRoundedRect(r(-10, -10, 20, 20), 3, 3)
        painter.end()


def _icone_lupa():
    """Ícone vetorial da busca, independente de fonte e de tema do Windows."""
    desenho = QPixmap(20, 20)
    desenho.fill(Qt.transparent)
    painter = QPainter(desenho)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setPen(QPen(QColor("#62B8D2"), 1.8))
    painter.setBrush(Qt.NoBrush)
    painter.drawEllipse(QRectF(3.0, 3.0, 10.0, 10.0))
    painter.drawLine(QPointF(11.7, 11.7), QPointF(17.0, 17.0))
    painter.end()
    return QIcon(desenho)


def filtrar_e_ordenar(registros, busca="", filtro="all", ordem="padrao"):
    """Projeção pura usada por Cards e Grade, sem modificar a fonte."""
    busca = str(busca or "").strip().casefold()
    filtro = str(filtro or "all")
    filtrados = []
    for reg in registros:
        nome = reg["disciplina"]
        qtd = int(reg.get("quantidade_topicos") or 0)
        pausada = bool(reg.get("pausado"))
        if busca and busca not in nome.casefold():
            continue
        if filtro == "active" and (pausada or not qtd):
            continue
        if filtro == "empty" and qtd:
            continue
        if filtro == "paused" and not pausada:
            continue
        if filtro.startswith("name:") and nome != filtro[5:]:
            continue
        filtrados.append(reg)
    if ordem == "az":
        filtrados.sort(key=lambda r: r["disciplina"].casefold())
    elif ordem == "za":
        filtrados.sort(key=lambda r: r["disciplina"].casefold(), reverse=True)
    elif ordem == "maior":
        filtrados.sort(key=lambda r: (-int(r.get("quantidade_topicos") or 0), r["disciplina"].casefold()))
    elif ordem == "menor":
        filtrados.sort(key=lambda r: (int(r.get("quantidade_topicos") or 0), r["disciplina"].casefold()))
    return filtrados


def _icone_tipo(nome):
    s = str(nome or "").casefold()
    if "matem" in s: return "calculator"
    if "constituc" in s: return "building"
    if "administr" in s: return "briefcase"
    if "penal" in s: return "shield"
    if "trânsito" in s or "transito" in s or "trânsito" in s or "ctb" in s: return "car"
    if "inform" in s: return "monitor"
    if "lei" in s or "legisla" in s: return "scales"
    return "book"


def _icone_caixa(tipo, tamanho=34, objeto="bibliotecaIconBox"):
    frame = QFrame()
    frame.setObjectName(objeto)
    frame.setFixedSize(tamanho, tamanho)
    lay = QHBoxLayout(frame)
    lay.setContentsMargins(2, 2, 2, 2)
    lay.addWidget(IconeBiblioteca(tipo, max(20, tamanho - 12)), 0, Qt.AlignCenter)
    return frame


class CartaoDisciplina(QFrame):
    """Card selecionável por mouse e teclado, com ação direta de abrir tópicos."""
    def __init__(self, registro, selecionar, abrir, parent=None):
        super().__init__(parent)
        self.registro = registro
        self._selecionar = selecionar
        self._abrir = abrir
        self.setObjectName("bibliotecaCard")
        self.setProperty("selected", "false")
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAccessibleName(f"Disciplina {registro['disciplina']}")
        self.setToolTip("Clique ou pressione Enter para selecionar; use a ação para abrir os tópicos.")
        self.setFixedHeight(116)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(11, 10, 10, 9)
        lay.setSpacing(5)
        cab = QHBoxLayout()
        cab.setSpacing(9)
        cab.addWidget(_icone_caixa(_icone_tipo(registro['disciplina']), 35))
        textos = QVBoxLayout()
        textos.setSpacing(2)
        titulo = QLabel(registro["disciplina"])
        titulo.setObjectName("bibliotecaCardName")
        titulo.setWordWrap(True)
        titulo.setMaximumHeight(37)
        self.nome_label = titulo
        textos.addWidget(titulo)
        qtd = int(registro.get("quantidade_topicos") or 0)
        if qtd:
            detalhe = f"{qtd} tópico{'s' if qtd != 1 else ''} cadastrado{'s' if qtd != 1 else ''}"
        else:
            detalhe = "Nenhum tópico cadastrado"
        desc = QLabel(detalhe)
        desc.setObjectName("bibliotecaCardDetail")
        desc.setWordWrap(False)
        textos.addWidget(desc)
        cab.addLayout(textos, 1)
        lay.addLayout(cab, 1)
        divisoria = QFrame()
        divisoria.setObjectName("bibliotecaCardDivider")
        divisoria.setFixedHeight(1)
        lay.addWidget(divisoria)
        rodape = QHBoxLayout()
        rodape.setSpacing(5)
        status = QLabel("●  " + ("Pausada" if registro['pausado'] else "Sem tópicos" if qtd == 0 else "Ativa"))
        status.setObjectName("bibliotecaStatus")
        status.setProperty("status", "paused" if registro['pausado'] else "empty" if qtd == 0 else "active")
        rodape.addWidget(status)
        rodape.addStretch(1)
        texto_acao = "Configurar  →" if qtd == 0 else "Abrir tópicos  →"
        acao = QPushButton(texto_acao)
        acao.setObjectName("bibliotecaCardAction")
        acao.setCursor(Qt.PointingHandCursor)
        acao.setFixedHeight(24)
        acao.setToolTip("Abrir o gerenciamento da disciplina" if qtd == 0 else "Abrir tópicos")
        acao.clicked.connect(lambda checked=False: self._abrir(self.registro["disciplina"]))
        rodape.addWidget(acao)
        lay.addLayout(rodape)

    def definir_selecionado(self, selecionado):
        valor = "true" if selecionado else "false"
        if self.property("selected") == valor:
            return
        self.setProperty("selected", valor)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._selecionar(self.registro["disciplina"])
            self.setFocus()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self._selecionar(self.registro["disciplina"])
            event.accept()
            return
        super().keyPressEvent(event)


class TelaDisciplinasPerfil(QWidget):
    """Portal visual sem efeitos colaterais; usa os callbacks originais."""

    def __init__(self, listar_disciplinas, abrir_disciplina, editar_disciplinas,
                 voltar_inicio, listar_topicos=None, parent=None):
        super().__init__(parent)
        self.setObjectName("portalDisciplinasPage")
        self._listar = listar_disciplinas
        self._listar_topicos = listar_topicos or (lambda _nome: [])
        self._abrir = abrir_disciplina
        self._editar = editar_disciplinas
        self._voltar = voltar_inicio
        self._registros = []
        self._cards = []
        self._selecionada = None
        self._perfil = "—"
        self._colunas = 0
        self._updating = False
        self._compacto = False
        self._header_compacto = False
        self._filtro_dados = []
        # A largura definitiva é a do viewport, conhecida após o layout Qt.
        # Coalesce resize/show do scroll, do viewport e da página.
        self._adaptacao_pendente = False
        self._adaptando = False
        self._ultima_largura_aplicada = None

        pagina = QVBoxLayout(self)
        pagina.setContentsMargins(0, 0, 0, 0)
        self.scroll = QScrollArea()
        self.scroll.setObjectName("bibliotecaScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        pagina.addWidget(self.scroll)

        self.corpo = QWidget()
        self.corpo.setObjectName("bibliotecaBody")
        self.conteudo = QVBoxLayout(self.corpo)
        self.conteudo.setContentsMargins(18, 15, 18, 4)
        self.conteudo.setSpacing(12)

        self._montar_cabecalho()
        self._montar_destaque()
        self._montar_ferramentas()
        self._montar_mosaico()
        self.scroll.setWidget(self.corpo)
        self.scroll.viewport().installEventFilter(self)
        self._agendar_adaptacao()

    def _montar_cabecalho(self):
        self.header = QFrame()
        self.header.setObjectName("bibliotecaHeader")
        # O tamanho mínimo respeita o mockup, mas o sizeHint pode crescer
        # para comportar fonte/DPI: nenhuma altura fixa no cabeçalho.
        self.header.setMinimumHeight(84)
        self.header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.header_root = QVBoxLayout(self.header)
        self.header_root.setContentsMargins(14, 10, 13, 10)
        self.header_root.setSpacing(2)
        self.header_lay = QHBoxLayout()
        self.header_lay.setSpacing(14)
        self.header_root.addLayout(self.header_lay)
        # Essa segunda faixa não integra o layout em resolução normal.
        # Só será conectada em viewports verdadeiramente estreitos.
        self.header_extra = QHBoxLayout()
        self.header_extra.setContentsMargins(0, 0, 0, 0)
        self.header_lay.addWidget(_icone_caixa("library", 50))
        titulos = QVBoxLayout()
        titulos.setSpacing(1)
        self.titulo = QLabel("Minha biblioteca")
        self.titulo.setObjectName("bibliotecaTitle")
        titulos.addWidget(self.titulo)
        self.subtitulo = QLabel("Disciplinas do perfil • —")
        self.subtitulo.setObjectName("bibliotecaSubtitle")
        titulos.addWidget(self.subtitulo)
        self.header_lay.addLayout(titulos, 1)
        self.metricas = QWidget()
        self.metricas.setObjectName("bibliotecaMetrics")
        metricas_lay = QHBoxLayout(self.metricas)
        metricas_lay.setContentsMargins(0, 0, 0, 0)
        metricas_lay.setSpacing(20)
        self.metric_values = []
        for legenda in ("disciplinas", "tópicos", "sem tópicos"):
            col = QVBoxLayout()
            col.setSpacing(2)
            val = QLabel("0")
            val.setObjectName("bibliotecaMetricNumber")
            lab = QLabel(legenda)
            lab.setObjectName("bibliotecaMetricCaption")
            col.addWidget(val)
            col.addWidget(lab)
            metricas_lay.addLayout(col)
            self.metric_values.append(val)
        self.metricas.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.header_lay.addWidget(self.metricas, 0, Qt.AlignVCenter)
        self.botao_editar = QPushButton("Gerenciar")
        self.botao_editar.setObjectName("bibliotecaManage")
        self.botao_editar.setFixedSize(143, 40)
        self.botao_editar.setCursor(Qt.PointingHandCursor)
        self.botao_editar.clicked.connect(self._editar)
        self.header_lay.addWidget(self.botao_editar, 0, Qt.AlignVCenter)
        self.conteudo.addWidget(self.header)

    def _montar_destaque(self):
        self.destaque = QFrame()
        self.destaque.setObjectName("bibliotecaHero")
        self.destaque.setFixedHeight(172)
        self.hero_lay = QBoxLayout(QBoxLayout.LeftToRight, self.destaque)
        self.hero_lay.setContentsMargins(20, 16, 26, 16)
        self.hero_lay.setSpacing(15)
        self.icone_selecionado = _icone_caixa("shield", 70)
        self.hero_lay.addWidget(self.icone_selecionado, 0, Qt.AlignVCenter)
        self.identidade = QVBoxLayout()
        self.identidade.setSpacing(6)
        pequeno = QLabel("DISCIPLINA SELECIONADA")
        pequeno.setObjectName("bibliotecaEyebrow")
        self.identidade.addWidget(pequeno)
        self.nome_selecionado = QLabel("—")
        self.nome_selecionado.setObjectName("bibliotecaHeroTitle")
        self.nome_selecionado.setWordWrap(True)
        self.identidade.addWidget(self.nome_selecionado)
        self.desc_selecionada = QLabel("")
        self.desc_selecionada.setObjectName("bibliotecaHeroDescription")
        self.desc_selecionada.setWordWrap(True)
        self.identidade.addWidget(self.desc_selecionada)
        self.chip = QLabel("—")
        self.chip.setObjectName("bibliotecaStatus")
        self.chip.setProperty("heroChip", "true")
        self.chip.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.identidade.addWidget(self.chip, 0, Qt.AlignLeft)
        self.identidade.addStretch(1)
        self.hero_lay.addLayout(self.identidade, 1)
        self.divisor = QFrame()
        self.divisor.setObjectName("bibliotecaDivider")
        self.divisor.setFixedWidth(1)
        self.hero_lay.addWidget(self.divisor)
        self.hero_right = QWidget()
        self.hero_right.setObjectName("bibliotecaHeroRight")
        self.hero_right.setFixedWidth(324)
        right = QVBoxLayout(self.hero_right)
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(5)
        rotulo = QLabel("CONTEÚDO CADASTRADO")
        rotulo.setObjectName("bibliotecaEyebrow")
        right.addWidget(rotulo)
        self.contagem_destaque = QLabel("0")
        self.contagem_destaque.setObjectName("bibliotecaHeroCount")
        right.addWidget(self.contagem_destaque)
        descricao = QLabel("tópicos disponíveis")
        descricao.setObjectName("bibliotecaHeroCountDetail")
        right.addWidget(descricao)
        right.addStretch(1)
        self.abrir_selecionado = QPushButton("Abrir tópicos  →")
        self.abrir_selecionado.setObjectName("bibliotecaPrimary")
        self.abrir_selecionado.setFixedHeight(46)
        self.abrir_selecionado.setCursor(Qt.PointingHandCursor)
        self.abrir_selecionado.clicked.connect(self._abrir_linha)
        right.addWidget(self.abrir_selecionado)
        self.hero_lay.addWidget(self.hero_right)
        self.conteudo.addWidget(self.destaque)

    def _montar_ferramentas(self):
        self.tools = QWidget()
        self.tools.setObjectName("bibliotecaTools")
        self.tools_lay = QGridLayout(self.tools)
        self.tools_lay.setContentsMargins(0, 0, 0, 0)
        self.tools_lay.setHorizontalSpacing(12)
        self.tools_lay.setVerticalSpacing(10)
        self._toolbar_modo = None
        self.busca = QLineEdit()
        self.busca.setObjectName("bibliotecaSearch")
        self.busca.setPlaceholderText("Buscar disciplina...")
        # A lupa acrescenta um ícone à esquerda sem alterar a altura ou a
        # distribuição da barra de controles.
        self.busca.addAction(_icone_lupa(), QLineEdit.ActionPosition.LeadingPosition)
        self.busca.setClearButtonEnabled(True)
        self.busca.setFixedHeight(48)
        self.busca.textChanged.connect(self._aplicar_filtros)
        self.busca.setMinimumWidth(100)
        self.filtro_disciplina = QComboBox()
        self.filtro_disciplina.setObjectName("bibliotecaFilter")
        self.filtro_disciplina.setFixedHeight(48)
        self.filtro_disciplina.currentIndexChanged.connect(self._aplicar_filtros)
        self.filtro_disciplina.setMinimumWidth(105)
        self.ordenacao = QComboBox()
        self.ordenacao.setObjectName("bibliotecaSort")
        self.ordenacao.setFixedHeight(48)
        for texto, chave in (("Padrão", "padrao"), ("Nome A–Z", "az"),
                             ("Nome Z–A", "za"), ("Mais tópicos", "maior"),
                             ("Menos tópicos", "menor")):
            self.ordenacao.addItem(texto, chave)
        self.ordenacao.currentIndexChanged.connect(self._aplicar_filtros)
        self.ordenacao.setMinimumWidth(110)
        self.botao_cards = QPushButton("▦  Cards")
        self.botao_cards.setObjectName("bibliotecaMode")
        self.botao_cards.setCheckable(True)
        self.botao_cards.setChecked(True)
        self.botao_cards.setFixedHeight(48)
        self.botao_cards.setToolTip("Alternar entre Cards e Grade")
        self.botao_cards.clicked.connect(self._mudar_modo)
        self._organizar_ferramentas(1268)
        self.conteudo.addWidget(self.tools)

    def _organizar_ferramentas(self, largura):
        modo = 'wide' if largura >= 1130 else 'mid' if largura >= 565 else 'narrow'
        if modo == self._toolbar_modo:
            return
        self._toolbar_modo = modo
        widgets = (self.busca, self.filtro_disciplina, self.ordenacao, self.botao_cards)
        for widget in widgets:
            self.tools_lay.removeWidget(widget)
            widget.setMinimumWidth(0)
            widget.setMaximumWidth(16777215)
        for coluna in range(4):
            self.tools_lay.setColumnStretch(coluna, 0)
        if modo == 'wide':
            self.filtro_disciplina.setFixedWidth(234)
            self.ordenacao.setFixedWidth(137)
            self.botao_cards.setFixedWidth(132)
            for i, widget in enumerate(widgets):
                self.tools_lay.addWidget(widget, 0, i)
            self.tools_lay.setColumnStretch(0, 1)
        elif modo == 'mid':
            self.tools_lay.addWidget(self.busca, 0, 0, 1, 4)
            self.tools_lay.addWidget(self.filtro_disciplina, 1, 0, 1, 2)
            self.tools_lay.addWidget(self.ordenacao, 1, 2)
            self.tools_lay.addWidget(self.botao_cards, 1, 3)
            for coluna in range(4):
                self.tools_lay.setColumnStretch(coluna, 1)
        else:
            for i, widget in enumerate(widgets):
                self.tools_lay.addWidget(widget, i, 0)
            self.tools_lay.setColumnStretch(0, 1)
        self.tools.updateGeometry()

    def _largura_util_atual(self):
        """Largura lógica realmente disponível, sem depender do tamanho inicial.

        O QScrollArea pode emitir resize antes de ajustar seu viewport. Quando
        os dois divergem muito, usamos a largura do scroll que iniciou o
        evento e sincronizamos novamente no resize do viewport.
        """
        externa = self.scroll.width() - 2 * self.scroll.frameWidth()
        if externa < 120:
            return None
        vp = self.scroll.viewport().width()
        if vp < 120 or abs(externa - vp) > 40:
            sb = self.scroll.verticalScrollBar()
            barra = sb.width() if sb.isVisible() else 0
            disponivel = externa - barra
        else:
            disponivel = vp
        return max(0, int(disponivel) - 36)

    def _agendar_adaptacao(self):
        """Atualização posterior ao ciclo de layout; evita widths transitórias."""
        if self._adaptacao_pendente:
            return
        self._adaptacao_pendente = True
        QTimer.singleShot(0, self._sincronizar_adaptacao)

    def _sincronizar_adaptacao(self):
        self._adaptacao_pendente = False
        if self._adaptando or not self.isVisible():
            return
        largura = self._largura_util_atual()
        if largura is None:
            return
        if largura == self._ultima_largura_aplicada:
            return
        self._adaptando = True
        try:
            self._adaptar_largura(largura)
            self._redistribuir_grade(largura)
            self._ultima_largura_aplicada = largura
        finally:
            self._adaptando = False

    def _adaptar_largura(self, largura=None):
        if largura is None:
            largura = self._largura_util_atual()
        if largura is None:
            return
        self._organizar_ferramentas(largura)
        # Critério exclusivo do cabeçalho: não confundir a largura que
        # aciona o Hero vertical (<820) com a necessidade de outra faixa
        # para os três indicadores. No alvo 1304x705 tudo fica na mesma linha.
        header_compacto = largura < 760
        if header_compacto != self._header_compacto:
            self._header_compacto = header_compacto
            if header_compacto:
                self.header_lay.removeWidget(self.metricas)
                self.header_root.addLayout(self.header_extra)
                self.header_extra.addWidget(self.metricas, 0, Qt.AlignLeft)
            else:
                self.header_extra.removeWidget(self.metricas)
                self.header_root.removeItem(self.header_extra)
                self.header_lay.insertWidget(
                    self.header_lay.count() - 1, self.metricas, 0, Qt.AlignVCenter
                )
            self.header.updateGeometry()

        # Regra anterior do Hero preservada: este lote não modifica o painel.
        compacto = largura < 820
        if compacto == self._compacto:
            return
        self._compacto = compacto
        if compacto:
            self.icone_selecionado.hide()
            self.divisor.hide()
            self.hero_lay.setDirection(QBoxLayout.TopToBottom)
            self.hero_right.setMinimumWidth(0)
            self.hero_right.setMaximumWidth(16777215)
            self.destaque.setFixedHeight(280)
        else:
            self.hero_lay.setDirection(QBoxLayout.LeftToRight)
            self.icone_selecionado.show()
            self.divisor.show()
            self.hero_right.setFixedWidth(324)
            self.destaque.setFixedHeight(172)

    def _montar_mosaico(self):
        secao = QHBoxLayout()
        secao.setSpacing(8)
        titulo = QLabel("Explorar disciplinas")
        titulo.setObjectName("bibliotecaSectionTitle")
        secao.addWidget(titulo)
        secao.addStretch(1)
        self.contador = QLabel("0 disciplinas disponíveis")
        self.contador.setObjectName("bibliotecaSecondary")
        secao.addWidget(self.contador)
        self.secao = QWidget()
        self.secao.setObjectName("bibliotecaSection")
        self.secao.setFixedHeight(30)
        self.secao.setLayout(secao)
        self.conteudo.addWidget(self.secao)

        self.views = QStackedWidget()
        self.views.setObjectName("bibliotecaViews")
        self.views.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.cards_host = QWidget()
        self.cards_host.setObjectName("bibliotecaCardsHost")
        self.grid = QGridLayout(self.cards_host)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(12)
        self.grid.setVerticalSpacing(10)
        self.grid.setAlignment(Qt.AlignTop)
        self.views.addWidget(self.cards_host)

        self.grade = QTableWidget(0, 4)
        self.grade.setObjectName("bibliotecaTable")
        self.grade.setHorizontalHeaderLabels(("Disciplina", "Tópicos", "Situação", "Abrir"))
        self.grade.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.grade.setSelectionMode(QAbstractItemView.SingleSelection)
        self.grade.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.grade.setAlternatingRowColors(True)
        self.grade.verticalHeader().hide()
        self.grade.horizontalHeader().setStretchLastSection(True)
        self.grade.setColumnWidth(0, 380)
        self.grade.setColumnWidth(1, 120)
        self.grade.setColumnWidth(2, 170)
        self.grade.verticalHeader().setDefaultSectionSize(43)
        self.grade.itemSelectionChanged.connect(self._selecionar_na_grade)
        self.grade.itemDoubleClicked.connect(self._abrir_na_grade)
        self.views.addWidget(self.grade)
        self.conteudo.addWidget(self.views)

        self.rodape = QWidget()
        self.rodape.setObjectName("bibliotecaFooter")
        rodape_lay = QHBoxLayout(self.rodape)
        rodape_lay.setContentsMargins(2, 0, 2, 0)
        small = QLabel("VighnaStudy  •  Biblioteca de Disciplinas")
        small.setObjectName("bibliotecaSecondary")
        rodape_lay.addWidget(small)
        rodape_lay.addStretch(1)
        self.botao_voltar = QPushButton("←  Início")
        self.botao_voltar.setObjectName("bibliotecaBack")
        self.botao_voltar.setFixedHeight(32)
        self.botao_voltar.clicked.connect(self._voltar)
        rodape_lay.addWidget(self.botao_voltar)
        self.rodape.setFixedHeight(34)
        # Com poucos resultados, manter o rodapé próximo à base da janela.
        # Com muitos cards, deixar a área crescer e recorrer à rolagem.
        self.conteudo.addStretch(1)
        self.conteudo.addWidget(self.rodape)

    def atualizar(self, perfil_nome):
        """Atualização sempre originada das APIs oficiais; não persiste seleção."""
        self._updating = True
        try:
            self._perfil = perfil_nome or "—"
            self.subtitulo.setText(f"Disciplinas do perfil • {self._perfil}")
            disciplinas = list(self._listar())
            self._registros = resumir_disciplinas(disciplinas, self._listar_topicos)
            if self._selecionada not in {r['disciplina'] for r in self._registros}:
                self._selecionada = self._registros[0]['disciplina'] if self._registros else None
            self.metric_values[0].setText(str(len(self._registros)))
            self.metric_values[1].setText(str(sum(int(r['quantidade_topicos']) for r in self._registros)))
            self.metric_values[2].setText(str(sum(1 for r in self._registros if int(r['quantidade_topicos']) == 0)))
            selecionado = self.filtro_disciplina.currentData() or "all"
            self.filtro_disciplina.blockSignals(True)
            self.filtro_disciplina.clear()
            for texto, chave in (("Todas as disciplinas", "all"), ("Ativas", "active"),
                                 ("Sem tópicos", "empty"), ("Pausadas", "paused")):
                self.filtro_disciplina.addItem(texto, chave)
            # Mantém a opção anterior de filtrar por disciplina nominal.
            if self._registros:
                self.filtro_disciplina.insertSeparator(self.filtro_disciplina.count())
            for reg in self._registros:
                self.filtro_disciplina.addItem(reg['disciplina'], 'name:'+reg['disciplina'])
            ix = self.filtro_disciplina.findData(selecionado)
            self.filtro_disciplina.setCurrentIndex(ix if ix >= 0 else 0)
            self.filtro_disciplina.blockSignals(False)
        finally:
            self._updating = False
        self._aplicar_filtros()
        self.scroll.verticalScrollBar().setValue(0)
        self._agendar_adaptacao()

    def _dados_visiveis(self):
        return filtrar_e_ordenar(
            self._registros,
            busca=self.busca.text(),
            filtro=self.filtro_disciplina.currentData(),
            ordem=self.ordenacao.currentData(),
        )

    def _aplicar_filtros(self, *_args):
        if self._updating:
            return
        self._filtro_dados = self._dados_visiveis()
        quant = len(self._filtro_dados)
        self.contador.setText(f"{quant} disciplina{'s' if quant != 1 else ''} disponíve{'is' if quant != 1 else 'l'}")
        if self._selecionada not in {r['disciplina'] for r in self._filtro_dados}:
            self._selecionada = self._filtro_dados[0]['disciplina'] if self._filtro_dados else None
        self._recriar_cards()
        self._preencher_grade()
        self._atualizar_destaque()

    def _recriar_cards(self):
        for card in self._cards:
            self.grid.removeWidget(card)
            card.setParent(None)
            card.deleteLater()
        self._cards.clear()
        for reg in self._filtro_dados:
            card = CartaoDisciplina(reg, self._selecionar, self._abrir, self.cards_host)
            self._cards.append(card)
        self._colunas = 0
        self._redistribuir_grade()

    def _redistribuir_grade(self, largura=None):
        # Mesma largura efetiva utilizada pelo cabeçalho, Hero e ferramentas.
        if largura is None:
            largura = self._largura_util_atual()
        if largura is None:
            return
        cols = 4 if largura >= 1130 else 3 if largura >= 850 else 2 if largura >= 565 else 1
        if self._colunas == cols:
            self._atualizar_altura_views(cols)
            return
        self._colunas = cols
        while self.grid.count():
            self.grid.takeAt(0)
        for c in range(4):
            self.grid.setColumnStretch(c, 1 if c < cols else 0)
            self.grid.setColumnMinimumWidth(c, 0)
        for i, card in enumerate(self._cards):
            self.grid.addWidget(card, i // cols, i % cols)
        self._atualizar_altura_views(cols)

    def _atualizar_altura_views(self, cols):
        linhas = max(1, (len(self._cards) + cols - 1) // cols)
        altura_cards = linhas * 116 + (linhas - 1) * 10
        altura_tabela = max(180, min(520, 42 + 43 * len(self._filtro_dados)))
        # Impede que o sizeHint da tabela oculta estique os cards.
        self.cards_host.setFixedHeight(altura_cards)
        self.views.setFixedHeight(altura_cards if self.views.currentIndex() == 0 else altura_tabela)

    def _preencher_grade(self):
        self.grade.blockSignals(True)
        self.grade.setRowCount(len(self._filtro_dados))
        for i, reg in enumerate(self._filtro_dados):
            nome = reg['disciplina']
            qtd = int(reg['quantidade_topicos'] or 0)
            for c, texto in enumerate((nome, str(qtd), reg['situacao'])):
                item = QTableWidgetItem(texto)
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.grade.setItem(i, c, item)
            botao = QPushButton('Configurar →' if qtd == 0 else 'Abrir tópicos →')
            botao.setObjectName('bibliotecaCardAction')
            botao.clicked.connect(lambda checked=False, disciplina=nome: self._abrir(disciplina))
            self.grade.setCellWidget(i, 3, botao)
            if nome == self._selecionada:
                self.grade.selectRow(i)
        self.grade.blockSignals(False)

    def _selecionar_na_grade(self):
        if self._updating or self.views.currentIndex() != 1:
            return
        row = self.grade.currentRow()
        if 0 <= row < len(self._filtro_dados):
            self._selecionar(self._filtro_dados[row]['disciplina'])

    def _abrir_na_grade(self, item):
        row = item.row()
        if 0 <= row < len(self._filtro_dados):
            self._abrir(self._filtro_dados[row]['disciplina'])

    def _selecionar(self, nome):
        if nome not in {r['disciplina'] for r in self._filtro_dados}:
            return
        self._selecionada = nome
        for card in self._cards:
            card.definir_selecionado(card.registro['disciplina'] == nome)
        self._atualizar_destaque()

    def _atualizar_destaque(self):
        reg = next((r for r in self._filtro_dados if r['disciplina'] == self._selecionada), None)
        for card in self._cards:
            card.definir_selecionado(bool(reg) and card.registro['disciplina'] == reg['disciplina'])
        if reg is None:
            self.nome_selecionado.setText('Nenhuma disciplina selecionada')
            self.desc_selecionada.setText('Ajuste a pesquisa ou o filtro para encontrar uma disciplina.')
            self.chip.setText('—')
            self.contagem_destaque.setText('0')
            self.abrir_selecionado.setEnabled(False)
            return
        nome = reg['disciplina']
        qtd = int(reg['quantidade_topicos'] or 0)
        self.nome_selecionado.setText(nome)
        self.desc_selecionada.setText(
            f"Conteúdos desta disciplina • {qtd} tópico{'s' if qtd != 1 else ''} cadastrado{'s' if qtd != 1 else ''}"
        )
        estado = 'Pausada' if reg['pausado'] else 'Sem tópicos' if qtd == 0 else 'Ativa'
        self.chip.setText('●  '+estado)
        self.chip.setProperty('status', 'paused' if reg['pausado'] else 'empty' if qtd == 0 else 'active')
        self.chip.style().unpolish(self.chip)
        self.chip.style().polish(self.chip)
        self.contagem_destaque.setText(str(qtd))
        self.abrir_selecionado.setText('Configurar  →' if qtd == 0 else 'Abrir tópicos  →')
        self.abrir_selecionado.setEnabled(True)
        # Atualizar o ícone sem criar componentes externos/estado duplicado.
        self.icone_selecionado.layout().itemAt(0).widget().tipo = _icone_tipo(nome)
        self.icone_selecionado.update()
        self.icone_selecionado.layout().itemAt(0).widget().update()

    def _abrir_linha(self, *_args):
        if self._selecionada and any(r['disciplina'] == self._selecionada for r in self._registros):
            self._abrir(self._selecionada)

    def _mudar_modo(self, checked):
        self.views.setCurrentIndex(0 if checked else 1)
        self.botao_cards.setText('▦  Cards' if checked else '☷  Grade')
        self._redistribuir_grade()

    def eventFilter(self, watched, event):
        # QWidget::resizeEvent da página não recebe necessariamente a alteração
        # da largura útil gerada pelo scroll vertical e pela barra lateral.
        if watched is self.scroll.viewport() and event.type() in (
            QEvent.Resize, QEvent.Show,
        ):
            self._agendar_adaptacao()
        return super().eventFilter(watched, event)

    def showEvent(self, event):
        super().showEvent(event)
        self._agendar_adaptacao()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._agendar_adaptacao()


def criar_portal_disciplinas(listar_disciplinas, abrir_disciplina,
                             editar_disciplinas, voltar_inicio, listar_topicos=None):
    return TelaDisciplinasPerfil(
        listar_disciplinas, abrir_disciplina, editar_disciplinas, voltar_inicio,
        listar_topicos=listar_topicos,
    )


def aplicar_estilo_portal_disciplinas(pagina, tema):
    # Identidade nativa única desejada: Futurista. A entrada tema permanece para
    # compatibilidade com chamadas antigas enquanto o projeto é migrado.
    pagina.setStyleSheet(QSS_BIBLIOTECA)
