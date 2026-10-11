"""Página Início do VighnaStudy: navegação leve, sem acesso ao banco.

Lote 02 — preserva o Dashboard existente e não cria novos motores de estudo.
Os cartões ainda não implementados são desabilitados intencionalmente.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget,
)

from ui.design import render_qss


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
    border-radius: 13px;
}
QFrame#portalInicioCard[portalRole="dashboard"] {
    border: 1px solid {{color:dashboard.nav_border}};
}
QFrame#portalInicioCard[portalRole="simulados"] {
    border: 1px solid {{color:feedback.info_border}};
}
QFrame#portalInicioCard[portalRole="recursos"] {
    border: 1px solid {{color:border.strong}};
}
QLabel#portalInicioMarca { color: {{color:text.primary}}; font-size: 16pt; font-weight: 800; }
QLabel#portalInicioTitulo { color: {{color:text.primary}}; font-size: 19pt; font-weight: 800; }
QLabel#portalInicioSubtitulo { color: {{color:text.secondary}}; font-size: 10pt; }
QLabel#portalInicioPerfil { color: {{color:text.secondary}}; font-size: 9pt; }
QLabel#portalInicioNumero { color: {{color:dashboard.nav_border}}; font-size: 17pt; font-weight: 800; }
QLabel#portalInicioCardTitulo { color: {{color:text.primary}}; font-size: 13pt; font-weight: 700; }
QLabel#portalInicioCardTexto { color: {{color:text.secondary}}; font-size: 9pt; }
QLabel#portalInicioCardDetalhe { color: {{color:text.secondary}}; font-size: 9pt; }
QLabel#portalInicioEstado { color: {{color:text.muted}}; font-size: 8pt; font-weight: 700; }
QPushButton#portalInicioAcesso,
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
QPushButton#portalInicioAcesso:hover,
QPushButton#portalInicioBusca:hover {
    background-color: {{color:dashboard.nav_hover_surface}};
    border-color: {{color:dashboard.nav_hover_border}};
}
QPushButton#portalInicioAcesso:disabled {
    background-color: {{color:surface.disabled}};
    color: {{color:text.disabled}};
    border-color: {{color:border.disabled}};
}
"""


def _label(texto: str, nome: str, *, quebra: bool = True) -> QLabel:
    label = QLabel(texto)
    label.setObjectName(nome)
    label.setWordWrap(quebra)
    return label


def _criar_cartao(numero: str, titulo: str, descricao: str, recursos: tuple[str, ...],
                  nome_acao: str, acao, papel: str) -> QFrame:
    card = QFrame()
    card.setObjectName("portalInicioCard")
    card.setProperty("portalRole", papel)
    card.setMinimumWidth(215)
    card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    coluna = QVBoxLayout(card)
    coluna.setContentsMargins(15, 15, 15, 15)
    coluna.setSpacing(11)

    coluna.addWidget(_label(numero, "portalInicioNumero", quebra=False))
    coluna.addWidget(_label(titulo, "portalInicioCardTitulo"))
    coluna.addWidget(_label(descricao, "portalInicioCardTexto"))
    coluna.addSpacing(5)
    detalhes = QFrame()
    detalhes.setObjectName("portalInicioDetalhes")
    bloco = QVBoxLayout(detalhes)
    bloco.setContentsMargins(4, 4, 4, 4)
    bloco.setSpacing(10)
    for item in recursos:
        bloco.addWidget(_label("•  " + item, "portalInicioCardDetalhe"))
    coluna.addWidget(detalhes)
    coluna.addStretch(1)

    if acao is None:
        coluna.addWidget(_label("EM PREPARAÇÃO", "portalInicioEstado"))
    botao = QPushButton(nome_acao)
    botao.setObjectName("portalInicioAcesso")
    botao.setCursor(Qt.PointingHandCursor if acao is not None else Qt.ArrowCursor)
    if acao is None:
        botao.setEnabled(False)
        botao.setToolTip("Este módulo será conectado em um lote posterior.")
    else:
        botao.clicked.connect(acao)
    coluna.addWidget(botao)
    return card


def criar_portal_inicio(abrir_dashboard, abrir_busca, abrir_questoes,
                        abrir_simulados=None, abrir_recursos=None,
                        cabecalho_compartilhado=None) -> QWidget:
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
    corpo = QWidget()
    corpo.setObjectName("portalInicioConteudo")
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

    linha = QHBoxLayout()
    linha.setSpacing(12)
    linha.addWidget(_criar_cartao(
        "01", "Dashboard de Estudos",
        "Continue acompanhando seu estudo diário no painel atual.",
        ("Foco e tempo efetivo", "Metas e planejamento", "Recomendação do algoritmo", "Progresso e conquistas"),
        "Abrir Dashboard  →", abrir_dashboard, "dashboard"), 1)
    linha.addWidget(_criar_cartao(
        "02", "Simulados e Treinos",
        "Área dedicada às modalidades de prática e avaliação.",
        ("Simulados configuráveis", "Baterias por disciplina", "Treino adaptativo", "Resultados e retomada"),
        "Abrir Simulados e Treinos  →", abrir_simulados, "simulados"), 1)
    linha.addWidget(_criar_cartao(
        "03", "Central de Recursos",
        "Encontre as ferramentas do VighnaStudy em um só lugar.",
        ("Disciplinas e questões", "Revisões e calendário", "Estatísticas e relatórios", "Ferramentas e configurações"),
        "Explorar todas as ferramentas  →", abrir_recursos, "recursos"), 1)
    coluna.addLayout(linha, 1)
    coluna.addStretch(1)
    scroll.setWidget(corpo)
    base.addWidget(scroll)
    pagina.portal_perfil_label = perfil
    return pagina


def aplicar_estilo_portal(pagina: QWidget, tema: str) -> None:
    pagina.setStyleSheet(render_qss(tema, ESTILO_PORTAL_INICIO))
