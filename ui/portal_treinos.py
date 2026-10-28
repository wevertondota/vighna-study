"""Central de Simulados e Treinos: navegação compacta e retomada condicional.

Somente apresentação e atalhos para os controladores existentes. Sem consulta,
escrita em banco ou criação de uma segunda sessão de questões.
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)
from ui.design import render_native_qss, render_qss


ESTILO_PORTAL_TREINOS = r"""
QWidget#portalTreinosPage { background: {{color:canvas.app}}; }
QScrollArea#portalTreinosScroll, QWidget#portalTreinosCorpo {
    background: transparent; border: none;
}
QFrame#portalTreinosCabecalho, QFrame#portalTreinosCard,
QFrame#portalTreinosRetomadaCard {
    background-color: {{color:surface.secondary}};
    border: 1px solid {{color:border.default}};
    border-radius: 12px;
}
QFrame#portalTreinosCard[treinoRole="bateria"],
QFrame#portalTreinosRetomadaCard {
    border-color: {{color:dashboard.nav_border}};
}
QFrame#portalTreinosCard[treinoRole="adaptativo"] {
    border-color: {{color:feedback.info_border}};
}
/* Sem :hover em toda a área: menos recalculo de estilo em movimentos
   do mouse. O contorno de foco fica visível para navegação por teclado. */
QFrame#portalTreinosCard:focus {
    border-color: {{color:dashboard.nav_hover_border}};
}
QLabel#portalTreinosTitulo { color: {{color:text.primary}}; font-size: 19pt; font-weight: 800; }
QLabel#portalTreinosSubtitulo { color: {{color:text.secondary}}; font-size: 9pt; }
QLabel#portalTreinosRotulo { color: {{color:dashboard.nav_border}}; font-size: 9pt; font-weight: 800; }
QLabel#portalTreinosCardTitulo { color: {{color:text.primary}}; font-size: 11pt; font-weight: 700; }
QLabel#portalTreinosCardDesc { color: {{color:text.secondary}}; font-size: 9pt; }
QLabel#portalTreinosCardAcesso { color: {{color:dashboard.nav_border}}; font-size: 9pt; font-weight: 700; }
QLabel#portalTreinosSessaoTitulo { color: {{color:text.primary}}; font-size: 11pt; font-weight: 800; }
QLabel#portalTreinosSessaoDetalhes { color: {{color:text.secondary}}; font-size: 9pt; }
QLabel#portalTreinosAviso { color: {{color:text.muted}}; font-size: 8pt; }
QPushButton#portalTreinosNavegar, QPushButton#portalTreinosRetomar {
    background-color: {{color:dashboard.nav_surface}};
    color: {{color:dashboard.nav_text}};
    border: 1px solid {{color:dashboard.nav_border}};
    border-radius: 8px;
    min-height: 29px;
    padding: 4px 11px;
    font-size: 9pt;
    font-weight: 700;
}
QPushButton#portalTreinosNavegar:hover, QPushButton#portalTreinosRetomar:hover {
    background-color: {{color:dashboard.nav_hover_surface}};
    border-color: {{color:dashboard.nav_hover_border}};
}
"""


def _texto(conteudo, nome, *, quebra=True, transparente=False):
    rotulo = QLabel(conteudo)
    rotulo.setObjectName(nome)
    rotulo.setWordWrap(quebra)
    if transparente:
        rotulo.setAttribute(Qt.WA_TransparentForMouseEvents, True)
    return rotulo


class _CardModalidade(QFrame):
    """Cartão acessível via mouse ou teclado, sem botões enormes internos."""

    def __init__(self, titulo, descricao, callback, papel, *, compacto=False):
        super().__init__()
        self._callback = callback
        self._acionamento_pendente = False
        self.setObjectName("portalTreinosCard")
        self.setProperty("treinoRole", papel)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAccessibleName(f"Abrir {titulo}")
        self.setToolTip(f"Abrir {titulo}")
        self.setMinimumWidth(230)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        coluna = QVBoxLayout(self)
        coluna.setContentsMargins(15, 11 if compacto else 14, 15, 11 if compacto else 14)
        coluna.setSpacing(4 if compacto else 6)

        titulo_linha = QHBoxLayout()
        titulo_linha.setSpacing(8)
        titulo_linha.addWidget(_texto(
            titulo, "portalTreinosCardTitulo", transparente=True), 1)
        titulo_linha.addWidget(_texto(
            "↗", "portalTreinosCardAcesso", quebra=False, transparente=True))
        coluna.addLayout(titulo_linha)
        coluna.addWidget(_texto(
            descricao, "portalTreinosCardDesc", transparente=True))

    def _agendar_acao(self):
        """Solta o evento de mouse/teclado antes de iniciar uma modalidade."""
        if self._acionamento_pendente:
            return
        self._acionamento_pendente = True
        QTimer.singleShot(0, self._executar_acao)

    def _executar_acao(self):
        try:
            self._callback()
        finally:
            self._acionamento_pendente = False

    def mouseReleaseEvent(self, evento):
        if evento.button() == Qt.LeftButton and self.rect().contains(evento.pos()):
            self._agendar_acao()
            evento.accept()
            return
        super().mouseReleaseEvent(evento)

    def keyPressEvent(self, evento):
        if evento.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self._agendar_acao()
            evento.accept()
            return
        super().keyPressEvent(evento)


def criar_portal_treinos(*, abrir_inicio, abrir_dashboard, abrir_simulado,
                         abrir_adaptativo, abrir_bateria, abrir_revisao,
                         abrir_erros, abrir_historico, retomar_sessao) -> QWidget:
    """Cria a Central sem iniciar módulos nem consultar o banco de dados."""
    pagina = QWidget()
    pagina.setObjectName("portalTreinosPage")
    base = QVBoxLayout(pagina)
    base.setContentsMargins(0, 0, 0, 0)

    scroll = QScrollArea()
    scroll.setObjectName("portalTreinosScroll")
    pagina.portal_treinos_scroll = scroll
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    corpo = QWidget()
    corpo.setObjectName("portalTreinosCorpo")
    coluna = QVBoxLayout(corpo)
    coluna.setContentsMargins(18, 16, 18, 20)
    coluna.setSpacing(12)
    # Ponto de inserção seguro para reparenting do quadro-mãe original.
    pagina.portal_treinos_conteudo_layout = coluna

    cabecalho = QFrame()
    cabecalho.setObjectName("portalTreinosCabecalho")
    faixa = QHBoxLayout(cabecalho)
    faixa.setContentsMargins(16, 12, 16, 12)
    faixa.setSpacing(9)
    titulo_layout = QVBoxLayout()
    titulo_layout.setSpacing(3)
    titulo_layout.addWidget(_texto("Simulados e Treinos", "portalTreinosTitulo"))
    titulo_layout.addWidget(_texto(
        "Escolha a modalidade e continue seus estudos.", "portalTreinosSubtitulo"))
    faixa.addLayout(titulo_layout, 1)
    for texto, funcao in (("← Início", abrir_inicio), ("Dashboard", abrir_dashboard)):
        botao = QPushButton(texto)
        botao.setObjectName("portalTreinosNavegar")
        botao.setCursor(Qt.PointingHandCursor)
        botao.clicked.connect(funcao)
        faixa.addWidget(botao)
    coluna.addWidget(cabecalho)

    # A faixa completa só aparece se a janela de questões realmente existir.
    # Ela não corresponde a uma sessão recuperável após fechar o aplicativo.
    grupo_retomada = QWidget()
    grupo_layout = QVBoxLayout(grupo_retomada)
    grupo_layout.setContentsMargins(0, 2, 0, 0)
    grupo_layout.setSpacing(7)
    grupo_layout.addWidget(_texto("CONTINUAR ESTUDANDO", "portalTreinosRotulo"))
    barra = QFrame()
    barra.setObjectName("portalTreinosRetomadaCard")
    linha = QHBoxLayout(barra)
    linha.setContentsMargins(15, 11, 15, 11)
    linha.setSpacing(12)
    informacoes = QVBoxLayout()
    informacoes.setSpacing(3)
    informacoes.addWidget(_texto("Sessão em andamento", "portalTreinosSessaoTitulo"))
    detalhe = _texto("Bateria aberta para retomada.", "portalTreinosSessaoDetalhes")
    informacoes.addWidget(detalhe)
    linha.addLayout(informacoes, 1)
    retomar = QPushButton("Retomar sessão  →")
    retomar.setObjectName("portalTreinosRetomar")
    retomar.setCursor(Qt.PointingHandCursor)
    retomar.clicked.connect(retomar_sessao)
    linha.addWidget(retomar)
    grupo_layout.addWidget(barra)
    coluna.addWidget(grupo_retomada)
    grupo_retomada.hide()

    coluna.addWidget(_texto("MODALIDADES DE PRÁTICA", "portalTreinosRotulo"))
    grade = QGridLayout()
    grade.setSpacing(11)
    modalidades = (
        ("Bateria personalizada", "Selecione critérios e quantidade de questões.", abrir_bateria, "bateria"),
        ("Treino adaptativo", "Pratique de acordo com suas necessidades.", abrir_adaptativo, "adaptativo"),
        ("Simulado", "Configure uma prova do perfil ativo.", abrir_simulado, "simulado"),
        ("Revisão inteligente", "Acesse a próxima revisão prioritária.", abrir_revisao, "revisao"),
    )
    for indice, (titulo, desc, funcao, papel) in enumerate(modalidades):
        grade.addWidget(_CardModalidade(titulo, desc, funcao, papel), indice // 2, indice % 2)
    grade.setColumnStretch(0, 1)
    grade.setColumnStretch(1, 1)
    coluna.addLayout(grade)

    coluna.addWidget(_texto("RECUPERAÇÃO E ACOMPANHAMENTO", "portalTreinosRotulo"))
    auxiliares = QGridLayout()
    auxiliares.setSpacing(11)
    for coluna_idx, (titulo, desc, funcao, papel) in enumerate((
        ("Banco de Erros", "Revise questões pendentes e recuperações.", abrir_erros, "erros"),
        ("Histórico de questões", "Consulte as respostas já registradas.", abrir_historico, "historico"),
    )):
        auxiliares.addWidget(_CardModalidade(
            titulo, desc, funcao, papel, compacto=True), 0, coluna_idx)
    auxiliares.setColumnStretch(0, 1)
    auxiliares.setColumnStretch(1, 1)
    coluna.addLayout(auxiliares)
    coluna.addWidget(_texto(
        "Os modos de estudo continuam usando as sessões, regras e resultados originais.",
        "portalTreinosAviso"))
    coluna.addStretch(1)
    scroll.setWidget(corpo)
    base.addWidget(scroll)
    pagina.portal_treinos_retomar = retomar
    pagina.portal_treinos_grupo_retomada = grupo_retomada
    pagina.portal_treinos_detalhes = detalhe
    return pagina


def atualizar_retomada_treinos(pagina: QWidget, existe_sessao: bool,
                               detalhes: str = "") -> None:
    """Exibe a retomada somente durante uma bateria viva na aplicação."""
    botao = getattr(pagina, "portal_treinos_retomar", None)
    grupo = getattr(pagina, "portal_treinos_grupo_retomada", None)
    detalhe = getattr(pagina, "portal_treinos_detalhes", None)
    novo_detalhe = detalhes or "Bateria aberta para retomada."
    if detalhe is not None and detalhe.text() != novo_detalhe:
        detalhe.setText(novo_detalhe)
    if botao is not None and botao.isEnabled() != bool(existe_sessao):
        botao.setEnabled(bool(existe_sessao))
    if grupo is not None and grupo.isHidden() == bool(existe_sessao):
        grupo.setVisible(bool(existe_sessao))


def aplicar_estilo_treinos(pagina: QWidget, tema: str) -> None:
    pagina.setStyleSheet((render_native_qss(ESTILO_PORTAL_TREINOS) if tema == "futurista"
                        else render_qss(tema, ESTILO_PORTAL_TREINOS)))
