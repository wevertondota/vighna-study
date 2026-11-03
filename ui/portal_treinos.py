"""Central de Simulados e Treinos: navegação compacta e retomada condicional.

Somente apresentação e atalhos para os controladores existentes. Sem consulta,
escrita em banco ou criação de uma segunda sessão de questões.
"""
from PySide6.QtCore import Qt, QTimer, QBuffer, QByteArray, QIODevice, QSettings, QRectF
from PySide6.QtWidgets import (
    QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget, QStackedWidget, QMenu,
)
from PySide6.QtGui import QMovie, QPainter, QColor, QPen
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



# Regiões medidas sobre a imagem ORIGINAL 1300 × 715; não esticam com a janela.
# As ações são QPushButtons reais, sem clonar os motores de questões.
_ESFERAS_CLICAVEIS = (
    ("Revisão Inteligente", (312, 160, 193, 178), "revisao"),
    ("Treino Adaptativo", (802, 159, 193, 182), "adaptativo"),
    ("Simulado", (220, 327, 207, 186), "simulado"),
    ("Banco de Erros", (878, 327, 207, 186), "erros"),
)


class _CenaSimulados(QWidget):
    """GIF cinematográfico com quatro botões Qt reais alinhados à arte.

    Não é um QLabel sobre o qual se desenham botões: o QMovie apenas fornece
    o pixmap ao paintEvent; controles permanecem acima e acessíveis por teclado.
    """

    def __init__(self, acoes, ferramentas):
        super().__init__()
        self.setObjectName("portalTreinosCena")
        self.setMinimumSize(320, 240)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self._movie = None
        self._buffer = None
        self._dados = None
        self._alvo = QRectF()
        self._hover_ativo = None
        self._botoes = []
        for titulo, retangulo, chave in _ESFERAS_CLICAVEIS:
            botao = QPushButton(self)
            botao.setObjectName("portalTreinosOrbClick")
            botao.setAccessibleName("Abrir " + titulo)
            botao.setToolTip("Abrir " + titulo)
            botao.setCursor(Qt.PointingHandCursor)
            botao.setFocusPolicy(Qt.StrongFocus)
            botao.setStyleSheet("QPushButton#portalTreinosOrbClick { background: transparent; border: none; }"
                                "QPushButton#portalTreinosOrbClick:focus { border: 1px solid #4FB2E5; border-radius: 65px; }")
            botao.clicked.connect(acoes[chave])
            self._botoes.append((botao, retangulo))

        self._menu_button = QPushButton("Ferramentas  ▾", self)
        self._menu_button.setObjectName("portalTreinosSceneTools")
        self._menu_button.setAccessibleName("Acessos complementares de Simulados e Treinos")
        self._menu_button.setFocusPolicy(Qt.StrongFocus)
        self._menu_button.setCursor(Qt.PointingHandCursor)
        self._menu_button.setStyleSheet(
            "QPushButton#portalTreinosSceneTools {background-color: rgba(4,9,17,190); "
            "border: 1px solid #41556F; border-radius: 7px; color: #E4F2FA; "
            "padding: 5px 10px; font-size: 9pt;}"
            "QPushButton#portalTreinosSceneTools:hover, QPushButton#portalTreinosSceneTools:focus "
            "{border-color: #4FB2E5; background-color: rgba(20,40,62,235);}"
        )
        self._menu = QMenu(self)
        self._menu.setStyleSheet("QMenu {background-color: #0E1926; color: #E4F2FA; border: 1px solid #41556F;}"
                                 "QMenu::item:selected {background-color: #14283E;}")
        for rotulo, callback in ferramentas:
            self._menu.addAction(rotulo, callback)
        self._menu_button.clicked.connect(lambda: self._menu.exec(
            self._menu_button.mapToGlobal(self._menu_button.rect().topRight())))

        self._retomar = QPushButton("Retomar sessão", self)
        self._retomar.setObjectName("portalTreinosSceneResume")
        self._retomar.setCursor(Qt.PointingHandCursor)
        self._retomar.setFocusPolicy(Qt.StrongFocus)
        self._retomar.setStyleSheet("QPushButton#portalTreinosSceneResume {background-color: #14283E; "
                                    "color: #E4F2FA; border: 1px solid #4FB2E5; "
                                    "border-radius: 7px; padding: 5px 12px;}")
        self._retomar.clicked.connect(acoes["retomar"])
        self._retomar.setVisible(False)
        self._tem_retomada = False
        # Quando o usuário alterna para outro programa, também pausa o GIF.
        app = QApplication.instance()
        if app is not None:
            app.applicationStateChanged.connect(
                lambda _estado: self._sincronizar_movie())

    def definir_retomada(self, ativa, detalhes=""):
        self._tem_retomada = bool(ativa)
        self._retomar.setToolTip(detalhes or "Retomar sessão de questões")
        self._retomar.setVisible(self.isVisible() and self._tem_retomada)

    def _iniciar_movie(self):
        if self._movie is not None:
            return
        try:
            # Importar/decode somente quando esta tela for efetivamente exibida.
            from ui.simulados_gif_background import dados_gif_simulados
            self._dados = QByteArray(dados_gif_simulados())
            self._buffer = QBuffer(self)
            self._buffer.setData(self._dados)
            if not self._buffer.open(QIODevice.ReadOnly):
                return
            self._movie = QMovie(self._buffer, QByteArray(b"gif"), self)
            self._movie.setCacheMode(QMovie.CacheMode.CacheNone)
            if not self._movie.isValid():
                self._movie = None
                return
            self._movie.frameChanged.connect(lambda _idx: self.update())
        except Exception:
            # Fallback de UI: ferramentas e motor de estudos continuam acessíveis.
            self._movie = None

    def _reduzir_movimento(self):
        import os
        ambiente = os.environ.get("VIGHNA_HOME_REDUZIR_MOVIMENTO", "").strip().lower()
        if ambiente in ("1", "true", "sim", "yes", "on"):
            return True
        return QSettings("VighnaStudy", "Home").value(
            "acessibilidade/reduzir_movimento", False, type=bool)

    def _sincronizar_movie(self):
        if self._movie is None:
            return
        janela = self.window()
        animar = (self.isVisible() and not self._reduzir_movimento()
                  and not janela.isMinimized()
                  and QApplication.applicationState() == Qt.ApplicationActive)
        if animar:
            if self._movie.state() == QMovie.MovieState.NotRunning:
                self._movie.start()
            elif self._movie.state() == QMovie.MovieState.Paused:
                self._movie.setPaused(False)
        elif self._movie.state() == QMovie.MovieState.Running:
            self._movie.setPaused(True)
        if self._movie.currentPixmap().isNull() and self._movie.state() == QMovie.MovieState.NotRunning:
            self._movie.jumpToFrame(0)
        self.update()

    def showEvent(self, evento):
        super().showEvent(evento)
        self._iniciar_movie()
        self._sincronizar_movie()
        self._retomar.setVisible(self._tem_retomada)

    def hideEvent(self, evento):
        if self._movie is not None and self._movie.state() == QMovie.MovieState.Running:
            self._movie.setPaused(True)
        super().hideEvent(evento)

    def changeEvent(self, evento):
        super().changeEvent(evento)
        if self._movie is not None:
            QTimer.singleShot(0, self._sincronizar_movie)

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        largura, altura = self.width(), self.height()
        escala = min(largura / 1300.0, altura / 715.0)
        w, h = 1300 * escala, 715 * escala
        x, y = (largura - w) / 2.0, (altura - h) / 2.0
        self._alvo = QRectF(x, y, w, h)
        for botao, (rx, ry, rw, rh) in self._botoes:
            botao.setGeometry(round(x+rx*escala), round(y+ry*escala),
                               round(rw*escala), round(rh*escala))
        self._menu_button.adjustSize()
        self._menu_button.move(max(6, round(x+12*escala)),
                               max(6, round(y+h-34*escala)))
        self._retomar.adjustSize()
        self._retomar.move(min(largura-self._retomar.width()-6, round(x+w-self._retomar.width()-12*escala)),
                          max(6, round(y+h-34*escala)))

    def paintEvent(self, evento):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#040911"))
        if self._movie is not None:
            quadro = self._movie.currentPixmap()
            if not quadro.isNull():
                painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
                painter.drawPixmap(self._alvo, quadro, QRectF(quadro.rect()))
        elif not self._alvo.isNull():
            painter.setPen(QColor("#E4F2FA"))
            painter.drawText(self.rect(), Qt.AlignCenter,
                             "Câmara de Treinamento — use Ferramentas para abrir o painel completo")
        painter.end()


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

    # Cena visual fica na primeira página. A antiga central, com todos os
    # cards funcionais e o quadro-mãe reparentado do Dashboard, continua viva
    # na segunda página e pode ser aberta por Ferramentas > Painel completo.
    base.removeWidget(scroll)
    pilha = QStackedWidget(pagina)
    pilha.setObjectName("portalTreinosVisualStack")
    cena = _CenaSimulados(
        {
            "revisao": abrir_revisao,
            "adaptativo": abrir_adaptativo,
            "simulado": abrir_simulado,
            "erros": abrir_erros,
            "retomar": retomar_sessao,
        },
        [
            ("Painel completo e estatísticas", lambda: pilha.setCurrentWidget(scroll)),
            ("Bateria personalizada / Modo manual", abrir_bateria),
            ("Histórico de questões", abrir_historico),
            ("Início", abrir_inicio),
            ("Dashboard", abrir_dashboard),
        ],
    )
    pilha.addWidget(cena)
    pilha.addWidget(scroll)
    base.addWidget(pilha)
    pilha.setCurrentWidget(cena)
    pagina.portal_treinos_pilha = pilha
    pagina.portal_treinos_cena = cena
    botao_cena = QPushButton("Voltar à Câmara de Treinamento")
    botao_cena.setObjectName("portalTreinosNavegar")
    botao_cena.setCursor(Qt.PointingHandCursor)
    botao_cena.clicked.connect(lambda: pilha.setCurrentWidget(cena))
    faixa.addWidget(botao_cena)
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
    cena = getattr(pagina, "portal_treinos_cena", None)
    if cena is not None:
        cena.definir_retomada(existe_sessao, novo_detalhe)


def aplicar_estilo_treinos(pagina: QWidget, tema: str) -> None:
    pagina.setStyleSheet((render_native_qss(ESTILO_PORTAL_TREINOS) if tema == "futurista"
                        else render_qss(tema, ESTILO_PORTAL_TREINOS)))
