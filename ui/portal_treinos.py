"""Central de Simulados e Treinos — acesso a controladores existentes.

Lote 03: tela puramente de navegação, sem criar sessão ou modificar banco.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)
from ui.design import render_qss

ESTILO_PORTAL_TREINOS = r"""
QWidget#portalTreinosPage { background: {{color:canvas.app}}; }
QScrollArea#portalTreinosScroll, QWidget#portalTreinosCorpo {
    background: transparent; border: none;
}
QFrame#portalTreinosCabecalho, QFrame#portalTreinosCard {
    background-color: {{color:surface.secondary}};
    border: 1px solid {{color:border.default}};
    border-radius: 12px;
}
QFrame#portalTreinosCard[treinoRole="simulado"] {
    border: 1px solid {{color:dashboard.nav_border}};
}
QFrame#portalTreinosCard[treinoRole="adaptativo"] {
    border: 1px solid {{color:feedback.info_border}};
}
QLabel#portalTreinosTitulo { color: {{color:text.primary}}; font-size: 19pt; font-weight: 800; }
QLabel#portalTreinosSubtitulo { color: {{color:text.secondary}}; font-size: 10pt; }
QLabel#portalTreinosRotulo { color: {{color:dashboard.nav_border}}; font-size: 10pt; font-weight: 700; }
QLabel#portalTreinosCardTitulo { color: {{color:text.primary}}; font-size: 12pt; font-weight: 700; }
QLabel#portalTreinosCardDesc { color: {{color:text.secondary}}; font-size: 9pt; }
QLabel#portalTreinosAviso { color: {{color:text.muted}}; font-size: 9pt; }
QPushButton#portalTreinosAcao, QPushButton#portalTreinosNavegar {
    background-color: {{color:dashboard.nav_surface}};
    color: {{color:dashboard.nav_text}};
    border: 1px solid {{color:dashboard.nav_border}};
    border-radius: 8px;
    min-height: 34px;
    padding: 5px 10px;
    font-size: 9pt;
    font-weight: 700;
}
QPushButton#portalTreinosAcao:hover, QPushButton#portalTreinosNavegar:hover {
    background-color: {{color:dashboard.nav_hover_surface}};
    border-color: {{color:dashboard.nav_hover_border}};
}
QPushButton#portalTreinosAcao:disabled, QPushButton#portalTreinosNavegar:disabled {
    background-color: {{color:surface.disabled}};
    color: {{color:text.disabled}};
    border-color: {{color:border.disabled}};
}
"""


def _texto(conteudo, nome, *, quebra=True):
    rotulo = QLabel(conteudo)
    rotulo.setObjectName(nome)
    rotulo.setWordWrap(quebra)
    return rotulo


def _card(titulo, descricao, texto_botao, callback, papel):
    cartao = QFrame()
    cartao.setObjectName("portalTreinosCard")
    cartao.setProperty("treinoRole", papel)
    cartao.setMinimumWidth(235)
    cartao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    layout = QVBoxLayout(cartao)
    layout.setContentsMargins(16, 15, 16, 15)
    layout.setSpacing(9)
    layout.addWidget(_texto(titulo, "portalTreinosCardTitulo"))
    layout.addWidget(_texto(descricao, "portalTreinosCardDesc"))
    layout.addStretch(1)
    botao = QPushButton(texto_botao)
    botao.setObjectName("portalTreinosAcao")
    botao.setCursor(Qt.PointingHandCursor)
    botao.clicked.connect(callback)
    layout.addWidget(botao)
    return cartao


def criar_portal_treinos(*, abrir_inicio, abrir_dashboard, abrir_simulado,
                         abrir_adaptativo, abrir_bateria, abrir_revisao,
                         abrir_erros, abrir_historico, retomar_sessao) -> QWidget:
    """Monta launcher; cada ação aponta para um controlador já existente."""
    pagina = QWidget()
    pagina.setObjectName("portalTreinosPage")
    base = QVBoxLayout(pagina)
    base.setContentsMargins(0, 0, 0, 0)
    scroll = QScrollArea()
    scroll.setObjectName("portalTreinosScroll")
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    corpo = QWidget()
    corpo.setObjectName("portalTreinosCorpo")
    coluna = QVBoxLayout(corpo)
    coluna.setContentsMargins(18, 16, 18, 20)
    coluna.setSpacing(14)

    cabecalho = QFrame()
    cabecalho.setObjectName("portalTreinosCabecalho")
    titulo_layout = QVBoxLayout()
    titulo_layout.setSpacing(4)
    titulo_layout.addWidget(_texto("Simulados e Treinos", "portalTreinosTitulo"))
    titulo_layout.addWidget(_texto(
        "Escolha um modo de prática. As questões, regras e resultados continuam nos módulos originais.",
        "portalTreinosSubtitulo"))
    faixa = QHBoxLayout(cabecalho)
    faixa.setContentsMargins(16, 13, 16, 13)
    faixa.setSpacing(9)
    faixa.addLayout(titulo_layout, 1)
    for texto, funcao in (("← Início", abrir_inicio), ("Dashboard", abrir_dashboard)):
        botao = QPushButton(texto)
        botao.setObjectName("portalTreinosNavegar")
        botao.clicked.connect(funcao)
        botao.setCursor(Qt.PointingHandCursor)
        faixa.addWidget(botao)
    coluna.addWidget(cabecalho)

    coluna.addWidget(_texto("MODALIDADES DISPONÍVEIS", "portalTreinosRotulo"))
    grade = QGridLayout()
    grade.setSpacing(12)
    modalidades = (
        ("Simulado", "Configure uma prova com as questões do perfil ativo.",
         "Configurar simulado  →", abrir_simulado, "simulado"),
        ("Treino adaptativo", "Monte uma sessão orientada pelas necessidades de estudo.",
         "Montar treino  →", abrir_adaptativo, "adaptativo"),
        ("Bateria personalizada", "Escolha os critérios e a quantidade de questões para resolver.",
         "Configurar bateria  →", abrir_bateria, "bateria"),
        ("Revisão inteligente", "Abra a próxima revisão prioritária da fila existente.",
         "Revisar agora  →", abrir_revisao, "revisao"),
        ("Banco de Erros", "Consulte as pendências e as ferramentas de recuperação.",
         "Abrir Banco de Erros  →", abrir_erros, "erros"),
        ("Histórico de questões", "Consulte o histórico registrado no módulo de questões.",
         "Ver histórico  →", abrir_historico, "historico"),
    )
    for indice, dados in enumerate(modalidades):
        grade.addWidget(_card(*dados), indice // 2, indice % 2)
    grade.setColumnStretch(0, 1)
    grade.setColumnStretch(1, 1)
    coluna.addLayout(grade)

    barra = QFrame()
    barra.setObjectName("portalTreinosCabecalho")
    linha = QHBoxLayout(barra)
    linha.setContentsMargins(16, 10, 16, 10)
    linha.addWidget(_texto("Sessão em andamento", "portalTreinosCardTitulo"), 1)
    retomar = QPushButton("Retomar sessão  →")
    retomar.setObjectName("portalTreinosNavegar")
    retomar.setCursor(Qt.PointingHandCursor)
    retomar.setEnabled(False)
    retomar.setToolTip("Disponível quando houver uma bateria ainda aberta.")
    retomar.clicked.connect(retomar_sessao)
    linha.addWidget(retomar)
    coluna.addWidget(barra)
    coluna.addWidget(_texto(
        "A Central apenas organiza os acessos; suas sessões e resultados continuam preservados.",
        "portalTreinosAviso"))
    coluna.addStretch(1)
    scroll.setWidget(corpo)
    base.addWidget(scroll)
    pagina.portal_treinos_retomar = retomar
    return pagina


def atualizar_retomada_treinos(pagina: QWidget, existe_sessao: bool) -> None:
    botao = getattr(pagina, "portal_treinos_retomar", None)
    if botao is not None:
        botao.setEnabled(bool(existe_sessao))


def aplicar_estilo_treinos(pagina: QWidget, tema: str) -> None:
    pagina.setStyleSheet(render_qss(tema, ESTILO_PORTAL_TREINOS))
