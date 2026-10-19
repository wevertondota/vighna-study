"""Página Início do VighnaStudy: navegação leve, sem acesso ao banco.

Lote 02 — preserva o Dashboard existente e não cria novos motores de estudo.
Os cartões ainda não implementados são desabilitados intencionalmente.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget,
)

from ui.design import render_qss
from tema import normalizar_tema
from ui.portal_background_image import imagem_fundo_inicio_bytes


# Todas as cores provêm de tokens já registrados nos três temas.
ESTILO_PORTAL_INICIO = r"""
QWidget#portalInicioPage { background: {{color:canvas.app}}; }
QScrollArea#portalInicioScroll,
QWidget#portalInicioConteudo {
    background: transparent;
    border: none;
}
QFrame#portalInicioCabecalho,
QFrame#portalInicioCard {
    background-color: {{color:surface.secondary}};
    border: 1px solid {{color:border.default}};
    border-radius: 12px;
}
QFrame#portalInicioCard:hover {
    background-color: {{color:dashboard.nav_hover_surface}};
    border-color: {{color:dashboard.nav_hover_border}};
}
QWidget#portalInicioCardTopo,
QWidget#portalInicioCardRecursos {
    background: transparent;
    border: none;
}
QLabel#portalInicioNumeroCompacto {
    background: transparent;
    border: none;
    color: {{color:text.muted}};
    font-size: 8pt;
    font-weight: 600;
}
QLabel#portalInicioCardTituloCompacto {
    background: transparent;
    border: none;
    color: {{color:text.primary}};
    font-size: 12pt;
    font-weight: 700;
}
QLabel#portalInicioCardTextoCompacto {
    background: transparent;
    border: none;
    color: {{color:text.secondary}};
    font-size: 9pt;
}
QLabel#portalInicioCardDetalheCompacto {
    background: transparent;
    border: none;
    color: {{color:text.secondary}};
    font-size: 9pt;
}
QPushButton#portalInicioAcessoCompacto {
    background-color: {{color:dashboard.nav_surface}};
    border: 1px solid {{color:border.default}};
    border-radius: 7px;
    color: {{color:dashboard.nav_text}};
    font-size: 9pt;
    font-weight: 700;
    padding: 2px 9px;
    min-height: 28px;
}
QPushButton#portalInicioAcessoCompacto:hover,
QPushButton#portalInicioAcessoCompacto:focus {
    background-color: {{color:dashboard.nav_hover_surface}};
    border-color: {{color:dashboard.nav_hover_border}};
    color: {{color:text.primary}};
}
QPushButton#portalInicioAcessoCompacto:disabled {
    background-color: {{color:surface.disabled}};
    color: {{color:text.disabled}};
    border-color: {{color:border.disabled}};
}
QFrame#portalInicioEditalMiniCard {
    background-color: {{color:surface.secondary}};
    border: 1px solid {{color:border.default}};
    border-radius: 11px;
}
QFrame#portalInicioEditalMiniCard:hover {
    background-color: {{color:dashboard.nav_hover_surface}};
    border-color: {{color:dashboard.nav_hover_border}};
}
QFrame#portalInicioEditalMiniCard:focus {
    border: 1px solid {{color:feedback.info_border}};
}
QLabel#portalInicioEditalMiniIcon {
    background: {{color:dashboard.nav_surface}};
    border: 1px solid {{color:border.default}};
    border-radius: 7px;
    color: {{color:dashboard.nav_border}};
    font-size: 17pt;
}
QLabel#portalInicioEditalMiniTitle {
    color: {{color:text.primary}};
    font-size: 10pt;
    font-weight: 700;
}
QLabel#portalInicioEditalMiniProfile {
    color: {{color:text.secondary}};
    font-size: 9pt;
}
QLabel#portalInicioEditalMiniArrow {
    color: {{color:text.secondary}};
    font-size: 15pt;
}
QLabel#portalInicioMarca { color: {{color:text.primary}}; font-size: 16pt; font-weight: 800; }
QLabel#portalInicioTitulo { color: {{color:text.primary}}; font-size: 19pt; font-weight: 800; }
QLabel#portalInicioSubtitulo { color: {{color:text.secondary}}; font-size: 10pt; }
QLabel#portalInicioPerfil { color: {{color:text.secondary}}; font-size: 9pt; }
QLabel#portalInicioEstado { color: {{color:text.muted}}; font-size: 8pt; font-weight: 700; }
QPushButton#portalInicioBusca {
    background-color: {{color:dashboard.nav_surface}};
    color: {{color:dashboard.nav_text}};
    border: 1px solid {{color:dashboard.nav_border}};
    border-radius: 9px;
    min-height: 35px;
    padding: 5px 10px;
    font-size: 9pt;
    font-weight: 700;
}
QPushButton#portalInicioBusca:hover {
    background-color: {{color:dashboard.nav_hover_surface}};
    border-color: {{color:dashboard.nav_hover_border}};
}
"""


class _FundoPortalInicio(QWidget):
    """Fundo cinematográfico em tela única, desenhado sob os cartões.

    Desenha a foto em cover (sem deformação), escurece sem interferir nos
    widgets interativos e reutiliza a imagem escalonada após cada resize.
    O tema Claro mantém o canvas padrão; não afeta outras páginas.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("portalInicioConteudo")
        self._usar_fundo = False
        self._original = None
        self._redimensionada = None
        self._tamanho_cache = None

    def definir_tema(self, tema: str) -> None:
        habilitar = normalizar_tema(tema) in ("escuro", "futurista")
        if self._usar_fundo != habilitar:
            self._usar_fundo = habilitar
            self.update()

    def _pixmap_para_area(self):
        if self._original is None:
            imagem = QPixmap()
            if not imagem.loadFromData(imagem_fundo_inicio_bytes(), "JPG"):
                return None
            self._original = imagem
        tamanho = self.size()
        if tamanho.width() <= 0 or tamanho.height() <= 0:
            return None
        if self._tamanho_cache != tamanho or self._redimensionada is None:
            self._redimensionada = self._original.scaled(
                tamanho, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            self._tamanho_cache = tamanho
        return self._redimensionada

    def paintEvent(self, evento):
        super().paintEvent(evento)
        if not self._usar_fundo:
            return
        pixmap = self._pixmap_para_area()
        if pixmap is None:
            return
        painter = QPainter(self)
        # Centraliza a imagem de fundo sem achatá-la ao maximizar a janela.
        painter.drawPixmap(
            (self.width() - pixmap.width()) // 2,
            (self.height() - pixmap.height()) // 2,
            pixmap,
        )
        # Fundo do aplicativo à frente, em camada escura semitransparente.
        # Mantém o espaço cinematográfico reconhecível sem perder legibilidade.
        painter.fillRect(self.rect(), QColor(3, 8, 16, 146))
        painter.end()


def _label(texto: str, nome: str, *, quebra: bool = True) -> QLabel:
    label = QLabel(texto)
    label.setObjectName(nome)
    label.setWordWrap(quebra)
    return label


class _IconeModulo(QWidget):
    """Ícone vetorial leve, independente de fontes e de bibliotecas opcionais."""

    def __init__(self, papel: str, parent=None):
        super().__init__(parent)
        self.papel = papel
        self._cor = QColor("#27C9ED")
        self.setObjectName("portalInicioCardIcone")
        self.setFixedSize(22, 22)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setToolTip({
            "dashboard": "Dashboard de Estudos",
            "simulados": "Simulados e Treinos",
            "recursos": "Central de Recursos",
        }.get(papel, "Área de estudos"))

    def definir_tema(self, tema: str):
        cor = {
            "claro": "#087D9E",
            "escuro": "#47BBE0",
            "futurista": "#00D1FF",
        }.get(normalizar_tema(tema), "#47BBE0")
        self._cor = QColor(cor)
        self.update()

    def paintEvent(self, evento):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(self._cor, 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)
        if self.papel == "dashboard":
            # Colunas e tendência ascendente.
            painter.drawLine(3, 18, 19, 18)
            painter.drawRect(5, 12, 3, 6)
            painter.drawRect(10, 9, 3, 9)
            painter.drawRect(15, 6, 3, 12)
            painter.drawLine(4, 12, 11, 5)
            painter.drawLine(11, 5, 18, 6)
        elif self.papel == "simulados":
            # Prancheta com marca de conferência.
            painter.drawRoundedRect(5, 4, 13, 16, 2, 2)
            painter.drawLine(9, 3, 14, 3)
            painter.drawLine(9, 12, 11, 14)
            painter.drawLine(11, 14, 15, 10)
        else:
            # Grade de recursos.
            painter.drawRoundedRect(3, 3, 7, 7, 1, 1)
            painter.drawRoundedRect(12, 3, 7, 7, 1, 1)
            painter.drawRoundedRect(3, 12, 7, 7, 1, 1)
            painter.drawRoundedRect(12, 12, 7, 7, 1, 1)
        painter.end()


def _criar_cartao(numero: str, titulo: str, descricao: str, recursos: tuple[str, ...],
                  nome_acao: str, acao, papel: str) -> QFrame:
    """Card de acesso compacto, conforme referência visual; conserva o callback."""
    card = QFrame()
    card.setObjectName("portalInicioCard")
    card.setProperty("portalRole", papel)
    card.setAttribute(Qt.WA_Hover, True)
    card.setMinimumWidth(205)
    # Deixe o Qt acomodar fontes/DPI sem cortar textos. O limite superior
    # impede que os cards voltem ao formato alto anterior.
    card.setMinimumHeight(216)
    card.setMaximumHeight(266)
    card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    coluna = QVBoxLayout(card)
    coluna.setContentsMargins(14, 12, 14, 12)
    coluna.setSpacing(7)

    topo = QWidget(card)
    topo.setObjectName("portalInicioCardTopo")
    topo.setFixedHeight(24)
    topo_layout = QHBoxLayout(topo)
    topo_layout.setContentsMargins(0, 0, 0, 0)
    topo_layout.setSpacing(4)
    icone = _IconeModulo(papel, topo)
    topo_layout.addWidget(icone, 0, Qt.AlignVCenter)
    topo_layout.addStretch(1)
    num = _label(numero, "portalInicioNumeroCompacto", quebra=False)
    num.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    topo_layout.addWidget(num, 0, Qt.AlignVCenter)
    coluna.addWidget(topo)

    titulo_label = _label(titulo, "portalInicioCardTituloCompacto", quebra=False)
    titulo_label.setToolTip({
        "dashboard": "Dashboard de Estudos",
        "simulados": "Simulados e Treinos",
        "recursos": "Central de Recursos",
    }.get(papel, titulo))
    titulo_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    coluna.addWidget(titulo_label)

    descricao_label = _label(descricao, "portalInicioCardTextoCompacto")
    descricao_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    coluna.addWidget(descricao_label)
    coluna.addSpacing(2)

    lista = QWidget(card)
    lista.setObjectName("portalInicioCardRecursos")
    lista_layout = QVBoxLayout(lista)
    lista_layout.setContentsMargins(0, 0, 0, 0)
    lista_layout.setSpacing(4)
    for item in recursos:
        rotulo = _label("•  " + item, "portalInicioCardDetalheCompacto", quebra=False)
        lista_layout.addWidget(rotulo)
    coluna.addWidget(lista)
    coluna.addStretch(1)

    if acao is None:
        coluna.addWidget(_label("EM PREPARAÇÃO", "portalInicioEstado"))
    botao = QPushButton(nome_acao)
    botao.setObjectName("portalInicioAcessoCompacto")
    botao.setFixedHeight(32)
    botao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    botao.setCursor(Qt.PointingHandCursor if acao is not None else Qt.ArrowCursor)
    if acao is None:
        botao.setEnabled(False)
        botao.setToolTip("Este módulo será conectado em um lote posterior.")
    else:
        botao.clicked.connect(acao)
    coluna.addWidget(botao)
    return card
class _CartaoEdital(QFrame):
    """QFrame interativo: evita recorte de layouts dentro de QPushButton.

    Mantém clique em toda a superfície, foco por teclado e rótulo acessível,
    sem criar um controle de perfil ou consulta adicional ao banco.
    """
    clicked = Signal()

    def mousePressEvent(self, evento):
        if evento.button() == Qt.LeftButton:
            evento.accept()
            return
        super().mousePressEvent(evento)

    def mouseReleaseEvent(self, evento):
        if evento.button() == Qt.LeftButton:
            if self.rect().contains(evento.pos()):
                self.clicked.emit()
            evento.accept()
            return
        super().mouseReleaseEvent(evento)

    def keyPressEvent(self, evento):
        if evento.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.clicked.emit()
            evento.accept()
            return
        super().keyPressEvent(evento)


def _criar_mini_cartao_edital(abrir_edital):
    """Card compacto abaixo das três opções, sem cortes e inteiro clicável."""
    cartao = _CartaoEdital()
    cartao.setObjectName("portalInicioEditalMiniCard")
    # A largura acompanha a coluna Dashboard na grade. Mantém a altura compacta.
    cartao.setFixedHeight(70)
    cartao.setMinimumWidth(215)
    cartao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    cartao.setAttribute(Qt.WA_Hover, True)
    cartao.setCursor(Qt.PointingHandCursor)
    cartao.setFocusPolicy(Qt.StrongFocus)
    cartao.setAccessibleName("Meu Edital — perfil ativo")
    cartao.setToolTip("Abrir a Central do Edital do perfil ativo")
    cartao.clicked.connect(abrir_edital)

    linha = QHBoxLayout(cartao)
    linha.setContentsMargins(12, 8, 12, 8)
    linha.setSpacing(10)

    icone = QLabel("▤", cartao)
    icone.setObjectName("portalInicioEditalMiniIcon")
    icone.setAlignment(Qt.AlignCenter)
    icone.setFixedSize(40, 40)

    textos = QVBoxLayout()
    textos.setContentsMargins(0, 0, 0, 0)
    textos.setSpacing(2)
    titulo = _label("Meu Edital", "portalInicioEditalMiniTitle", quebra=False)
    perfil = _label("Perfil ativo", "portalInicioEditalMiniProfile", quebra=False)
    titulo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    perfil.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    textos.addWidget(titulo)
    textos.addWidget(perfil)

    seta = QLabel("↗", cartao)
    seta.setObjectName("portalInicioEditalMiniArrow")
    seta.setAlignment(Qt.AlignCenter)
    seta.setFixedSize(20, 26)

    # Eventos de mouse e teclado pertencem ao cartão inteiro.
    for rotulo in (icone, titulo, perfil, seta):
        rotulo.setAttribute(Qt.WA_TransparentForMouseEvents, True)

    linha.addWidget(icone, 0, Qt.AlignVCenter)
    linha.addLayout(textos, 1)
    linha.addWidget(seta, 0, Qt.AlignVCenter)
    cartao.portal_edital_perfil_label = perfil
    return cartao


def atualizar_perfil_mini_edital(pagina: QWidget, nome_perfil: str) -> None:
    """Acompanha a seleção do perfil já gerenciada pelo controlador principal."""
    cartao = getattr(pagina, "portal_edital_minicard", None)
    if cartao is None:
        return
    nome = str(nome_perfil or "").strip() or "Nenhum perfil selecionado"
    rotulo = cartao.portal_edital_perfil_label
    rotulo.setText(rotulo.fontMetrics().elidedText(nome, Qt.ElideRight, 218))
    rotulo.setToolTip(nome)
    cartao.setAccessibleName("Meu Edital — " + nome)
    cartao.setToolTip("Abrir a Central do Edital do perfil: " + nome)


def criar_portal_inicio(abrir_dashboard, abrir_busca, abrir_questoes,
                        abrir_simulados=None, abrir_recursos=None,
                        cabecalho_compartilhado=None, abrir_edital=None) -> QWidget:
    """Monta página independente e barata, compartilhada pelos três temas."""
    pagina = QWidget()
    pagina.setObjectName("portalInicioPage")
    pagina.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    base = QVBoxLayout(pagina)
    base.setContentsMargins(0, 0, 0, 0)

    scroll = QScrollArea()
    scroll.setObjectName("portalInicioScroll")
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    corpo = _FundoPortalInicio()
    coluna = QVBoxLayout(corpo)
    coluna.setContentsMargins(18, 15, 18, 20)
    coluna.setSpacing(17)

    if cabecalho_compartilhado is not None:
        # Move o MESMO cabeçalho do Dashboard: seletor de perfil, Gerenciar,
        # Central de Questões e Configurações mantêm suas conexões originais.
        # Um único widget possui o seletor: não há duplicação de estado.
        coluna.addWidget(cabecalho_compartilhado)
        perfil = None
    else:
        # Fallback para construtores legados e testes isolados do portal.
        cabecalho = QFrame()
        cabecalho.setObjectName("portalInicioCabecalho")
        cabecalho_layout = QHBoxLayout(cabecalho)
        cabecalho_layout.setContentsMargins(18, 13, 18, 13)
        marca = QVBoxLayout()
        marca.setSpacing(4)
        marca.addWidget(_label("VighnaStudy", "portalInicioMarca"))
        perfil = _label("Perfil ativo", "portalInicioPerfil")
        marca.addWidget(perfil)
        cabecalho_layout.addLayout(marca, 1)
        buscar = QPushButton("⌕  Buscar  ·  Ctrl+K")
        buscar.setObjectName("portalInicioBusca")
        buscar.setCursor(Qt.PointingHandCursor)
        buscar.clicked.connect(abrir_busca)
        cabecalho_layout.addWidget(buscar)
        central = QPushButton("Central de Questões")
        central.setObjectName("portalInicioBusca")
        central.setCursor(Qt.PointingHandCursor)
        central.clicked.connect(abrir_questoes)
        cabecalho_layout.addWidget(central)
        coluna.addWidget(cabecalho)

    coluna.addSpacing(5)
    coluna.addWidget(_label("Escolha para onde deseja ir", "portalInicioTitulo"))
    coluna.addWidget(_label("Três áreas para organizar sua rotina de estudos.", "portalInicioSubtitulo"))

    grade = QGridLayout()
    grade.setContentsMargins(0, 0, 0, 0)
    grade.setHorizontalSpacing(12)
    grade.setVerticalSpacing(18)
    for coluna_indice in range(3):
        grade.setColumnStretch(coluna_indice, 1)

    grade.addWidget(_criar_cartao(
        "01", "Dashboard", "Seu desempenho em um só lugar.",
        ("Foco e tempo", "Metas e progresso", "Recomendações"),
        "Acessar  →", abrir_dashboard, "dashboard"), 0, 0)
    grade.addWidget(_criar_cartao(
        "02", "Simulados", "Pratique e avalie sua evolução.",
        ("Simulados", "Baterias", "Treino adaptativo"),
        "Praticar  →", abrir_simulados, "simulados"), 0, 1)
    grade.addWidget(_criar_cartao(
        "03", "Recursos", "Suas ferramentas de estudo.",
        ("Disciplinas", "Revisões", "Estatísticas"),
        "Explorar  →", abrir_recursos, "recursos"), 0, 2)

    # Compartilha a mesma coluna com Dashboard: bordas esquerda/direita
    # alinhadas automaticamente, sem número fixo de pixels ou resize manual.
    mini_edital = _criar_mini_cartao_edital(abrir_edital) if abrir_edital else None
    if mini_edital is not None:
        grade.addWidget(mini_edital, 1, 0)
    coluna.addLayout(grade, 0)
    coluna.addStretch(1)
    scroll.setWidget(corpo)
    base.addWidget(scroll)
    pagina.portal_perfil_label = perfil
    pagina.portal_edital_minicard = mini_edital
    return pagina


def aplicar_estilo_portal(pagina: QWidget, tema: str) -> None:
    pagina.setStyleSheet(render_qss(tema, ESTILO_PORTAL_INICIO))
    for fundo in pagina.findChildren(_FundoPortalInicio):
        fundo.definir_tema(tema)
    for icone in pagina.findChildren(_IconeModulo):
        icone.definir_tema(tema)
