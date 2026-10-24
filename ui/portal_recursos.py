"""Central de Recursos do VighnaStudy — L05c (rotas e prioridades).

UI da Central: os 27 recursos permanecem. A Revisao Inteligente passa
para Questoes e a rota Disciplinas abre a lista do perfil com acesso aos
topicos editaveis. O catalogo e filtrado localmente, sem BD.
"""

import unicodedata

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import (
    QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from icones import criar_icone
from ui.design import render_native_qss, render_qss


# Identificadores, categorias, titulos e descricoes preservados do L05.
CATALOGO_RECURSOS = (
    ("inicio", "Navegação", "Início", "Voltar ao portal das três áreas."),
    ("dashboard", "Navegação", "Dashboard de Estudos", "Foco, metas, recomendação e progresso."),
    ("simulados_treinos", "Navegação", "Simulados e Treinos", "Central das modalidades de prática."),
    ("foco", "Estudo", "Modo Foco", "Cronômetro de concentração e sessões."),
    ("disciplinas", "Estudo", "Disciplinas e tópicos", "Listar disciplinas do perfil e gerenciar seus tópicos."),
    ("algoritmo", "Estudo", "Recomendação do algoritmo", "Ir à próxima sessão sugerida."),
    ("jornada", "Estudo", "Jornada do Dia", "Planejar e executar a sequência de estudo."),
    ("questoes", "Questões", "Central de Questões", "Cadastrar, importar e gerenciar o banco."),
    ("bateria", "Questões", "Bateria personalizada", "Configurar uma sessão de questões."),
    ("simulado", "Questões", "Simulado", "Montar uma prova com questões do perfil."),
    ("adaptativo", "Questões", "Treino adaptativo", "Praticar questões por necessidade."),
    ("revisao", "Questões", "Revisão Inteligente", "Acessar a fila de revisões prioritárias."),
    ("banco_erros", "Questões", "Banco de Erros", "Consultar pendências e recuperação."),
    ("historico", "Questões", "Histórico de questões", "Consultar tentativas registradas."),
    ("calendario", "Planejamento", "Calendário", "Consultar tarefas, dias e revisões."),
    ("plano_acao", "Planejamento", "Plano de Ação", "Ver o planejamento automático existente."),
    ("config_planejamento", "Planejamento", "Configuração de planejamento", "Ajustar parâmetros de estudo."),
    ("fechamento", "Planejamento", "Fechamento semanal", "Consultar o balanço da semana."),
    ("estatisticas", "Análise", "Estatísticas", "Analisar acertos, tempo e evolução."),
    ("relatorios", "Análise", "Relatórios", "Consultar relatórios do desempenho."),
    ("progresso_edital", "Análise", "Progresso do edital", "Ver cobertura e avanço do conteúdo."),
    ("previsao_edital", "Análise", "Previsão do edital", "Analisar estimativas e projeções."),
    ("alertas", "Análise", "Alertas de conteúdo", "Examinar pontos que exigem atenção."),
    ("pausa", "Ferramentas", "Pausa & Desafios", "Acessar jogos e pausas."),
    ("perfis", "Ferramentas", "Gerenciar perfis", "Criar ou ajustar concursos ativos."),
    ("configuracoes", "Ferramentas", "Configurações", "Preferências, aparência e atualizações."),
    ("diagnostico", "Ferramentas", "Diagnóstico técnico", "Verificar a integridade do ambiente."),
)

# A vitrine nao duplica entradas: itens destacados sao retirados de seus
# grupos originais e a Navegacao aparece por ultimo, de modo compacto.
PRIORITARIOS = (
    "questoes", "estatisticas", "relatorios",
    "disciplinas", "calendario",
)
GRUPOS_SECUNDARIOS = (
    "Questões", "Estudo", "Planejamento", "Análise", "Ferramentas", "Navegação",
)

# Nome QtAwesome + alternativa textual, caso a fonte opcional nao esteja instalada.
ICONES_RECURSOS = {
    "questoes": ("fa6s.database", "▦"),
    "estatisticas": ("fa6s.chart-column", "▥"),
    "relatorios": ("fa6s.chart-pie", "◔"),
    "disciplinas": ("fa6s.book-open", "▣"),
    "revisao": ("fa6s.arrows-rotate", "↻"),
    "calendario": ("fa6s.calendar-days", "▦"),
    "inicio": ("fa6s.house", "⌂"),
    "dashboard": ("fa6s.chart-line", "▥"),
    "simulados_treinos": ("fa6s.clipboard-check", "☷"),
    "foco": ("fa6s.bullseye", "◎"),
    "algoritmo": ("fa6s.wand-magic-sparkles", "✧"),
    "jornada": ("fa6s.list-check", "☷"),
    "bateria": ("fa6s.list-check", "☷"),
    "simulado": ("fa6s.file-circle-check", "▤"),
    "adaptativo": ("fa6s.sliders", "≡"),
    "banco_erros": ("fa6s.triangle-exclamation", "!"),
    "historico": ("fa6s.clock-rotate-left", "◷"),
    "plano_acao": ("fa6s.route", "↗"),
    "config_planejamento": ("fa6s.sliders", "≡"),
    "fechamento": ("fa6s.calendar-check", "✓"),
    "progresso_edital": ("fa6s.bars-progress", "▤"),
    "previsao_edital": ("fa6s.chart-line", "↗"),
    "alertas": ("fa6s.bell", "!"),
    "pausa": ("fa6s.trophy", "☆"),
    "perfis": ("fa6s.users", "♙"),
    "configuracoes": ("fa6s.gear", "⚙"),
    "diagnostico": ("fa6s.stethoscope", "+"),
}

ESTILO_PORTAL_RECURSOS = r"""
QWidget#portalRecursosPage { background: {{color:canvas.app}}; }
QScrollArea#portalRecursosScroll, QWidget#portalRecursosConteudo {
    background: transparent; border: none;
}
QFrame#portalRecursosCabecalho {
    background-color: {{color:surface.secondary}};
    border: 1px solid {{color:border.default}};
    border-radius: 11px;
}
QLabel#portalRecursosTitulo { color: {{color:text.primary}}; font-size: 19pt; font-weight: 800; }
QLabel#portalRecursosSubtitulo { color: {{color:text.secondary}}; font-size: 10pt; }
QLabel#portalRecursosGrupo { color: {{color:text.primary}}; font-size: 12pt; font-weight: 700; }
QLabel#portalRecursosGrupoContador { color: {{color:text.muted}}; font-size: 9pt; }
QFrame#portalRecursosDivisor { background-color: {{color:border.default}}; border: none; max-height: 1px; }
QLabel#portalRecursosCardTitulo { color: {{color:text.primary}}; font-size: 10pt; font-weight: 700; }
QLabel#portalRecursosCardDescricao { color: {{color:text.secondary}}; font-size: 9pt; }
QLabel#portalRecursosCardSeta { color: {{color:text.muted}}; font-size: 15pt; }
QLabel#portalRecursosIcone { color: {{color:dashboard.nav_border}}; font-size: 15pt; }
QLabel#portalRecursosContador { color: {{color:text.muted}}; font-size: 9pt; }
QLineEdit#portalRecursosFiltro, QComboBox#portalRecursosCategoria {
    background-color: {{color:surface.secondary}};
    color: {{color:text.primary}};
    border: 1px solid {{color:border.default}};
    border-radius: 8px;
    min-height: 32px;
    padding: 4px 9px;
    selection-background-color: {{color:dashboard.nav_surface}};
}
/* Cartao clicavel baseado em QFrame: duas linhas de QLabel sem recorte de
   conteudo pelo QStyle de QPushButton. Mouse e teclado sao tratados no widget. */
QFrame#portalRecursosCard {
    background-color: {{color:surface.secondary}};
    border: 1px solid {{color:border.default}};
    border-radius: 10px;
}
QFrame#portalRecursosCard[portalFeatured="true"] {
    border-color: {{color:dashboard.nav_border}};
}
QFrame#portalRecursosCard:hover,
QFrame#portalRecursosCard:focus {
    background-color: {{color:dashboard.nav_hover_surface}};
    border-color: {{color:dashboard.nav_hover_border}};
}
QFrame#portalRecursosCard[portalPressed="true"] {
    background-color: {{color:dashboard.nav_surface}};
}
QPushButton#portalRecursosVoltar {
    background-color: {{color:dashboard.nav_surface}};
    color: {{color:dashboard.nav_text}};
    border: 1px solid {{color:dashboard.nav_border}};
    border-radius: 8px;
    min-height: 30px;
    padding: 4px 9px;
    font-size: 9pt;
    font-weight: 700;
}
QPushButton#portalRecursosVoltar:hover {
    background-color: {{color:dashboard.nav_hover_surface}};
    border-color: {{color:dashboard.nav_hover_border}};
}
"""


class CartaoRecurso(QFrame):
    """Card acessivel e acionavel, sem usar QPushButton como layout pai.

    QFrame deixa os QLabel renderizarem o tamanho natural, inclusive sob
    escalas DPI diferentes. A navegacao por mouse/Enter/Espaco e preservada.
    """
    clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("portalRecursosCard")
        self.setAttribute(Qt.WA_Hover, True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.PointingHandCursor)
        self._mouse_pressionado = False

    def mousePressEvent(self, evento):
        if evento.button() == Qt.LeftButton:
            self.setFocus(Qt.MouseFocusReason)
            self._mouse_pressionado = True
            self.setProperty("portalPressed", True)
            self.style().unpolish(self)
            self.style().polish(self)
            evento.accept()
            return
        super().mousePressEvent(evento)

    def mouseReleaseEvent(self, evento):
        if evento.button() == Qt.LeftButton:
            ativar = self._mouse_pressionado and self.rect().contains(evento.pos())
            self._mouse_pressionado = False
            self.setProperty("portalPressed", False)
            self.style().unpolish(self)
            self.style().polish(self)
            if ativar:
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


def _texto(conteudo, nome, quebra=True):
    texto = QLabel(conteudo)
    texto.setObjectName(nome)
    texto.setWordWrap(quebra)
    # Evita interceptar o mouse no card clicavel que contem os textos.
    texto.setAttribute(Qt.WA_TransparentForMouseEvents, True)
    return texto


def normalizar_filtro(texto):
    texto = unicodedata.normalize("NFKD", str(texto or "").casefold())
    return "".join(c for c in texto if not unicodedata.combining(c)).strip()


def _criar_card(ident, rotulo, descricao, acao, *, destaque=False, compacto=False):
    """Card sem clipping: QLabel e layout dimensionam o QFrame naturalmente."""
    card = CartaoRecurso()
    card.setProperty("portalFeatured", bool(destaque))
    card.setProperty("portalCompact", bool(compacto))
    card.setAccessibleName(f"Abrir {rotulo}")
    card.setAccessibleDescription(descricao)
    card.setToolTip(f"Abrir {rotulo} — {descricao}")
    card.setMinimumWidth(0)
    card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
    # Altura MINIMA, nao fixa: permite crescimento por DPI e quebra de texto.
    card.setMinimumHeight(48 if compacto else (74 if destaque else 70))
    card.clicked.connect(acao)

    linha = QHBoxLayout(card)
    linha.setContentsMargins(11, 10 if not compacto else 8, 11, 10 if not compacto else 8)
    linha.setSpacing(11)
    icone = _texto("", "portalRecursosIcone", False)
    icone.setAlignment(Qt.AlignCenter)
    icone.setFixedSize(26, 26)
    linha.addWidget(icone)

    info = QVBoxLayout()
    info.setContentsMargins(0, 0, 0, 0)
    info.setSpacing(4)
    titulo = _texto(rotulo, "portalRecursosCardTitulo", not compacto)
    titulo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
    info.addWidget(titulo)
    if not compacto:
        subtitulo = _texto(descricao, "portalRecursosCardDescricao")
        subtitulo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        info.addWidget(subtitulo)
    linha.addLayout(info, 1)

    seta = _texto("›", "portalRecursosCardSeta", False)
    seta.setAlignment(Qt.AlignCenter)
    seta.setFixedWidth(16)
    linha.addWidget(seta)
    return card, icone


def _pintar_icone(rotulo, ident, tema):
    nome, fallback = ICONES_RECURSOS[ident]
    icone = criar_icone(nome, tema=tema, papel="destaque")
    imagem = icone.pixmap(QSize(20, 20))
    if imagem.isNull():
        rotulo.clear()
        rotulo.setText(fallback)
    else:
        rotulo.setText("")
        rotulo.setPixmap(imagem)


def criar_portal_recursos(*, abrir_inicio, abrir_dashboard, abrir_destinos):
    """Cria a central reorganizada sem modificar nenhum destino registrado."""
    mapa = dict(abrir_destinos)
    ids = {r[0] for r in CATALOGO_RECURSOS}
    if ids != set(mapa) or len(ids) != len(CATALOGO_RECURSOS):
        raise ValueError("O catálogo de recursos exige uma rota única para cada destino")

    pagina = QWidget()
    pagina.setObjectName("portalRecursosPage")
    base = QVBoxLayout(pagina)
    base.setContentsMargins(0, 0, 0, 0)
    scroll = QScrollArea()
    scroll.setObjectName("portalRecursosScroll")
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    corpo = QWidget()
    corpo.setObjectName("portalRecursosConteudo")
    coluna = QVBoxLayout(corpo)
    coluna.setContentsMargins(18, 16, 18, 20)
    coluna.setSpacing(12)

    topo = QFrame()
    topo.setObjectName("portalRecursosCabecalho")
    linha_topo = QHBoxLayout(topo)
    linha_topo.setContentsMargins(16, 13, 16, 13)
    titulo = QVBoxLayout()
    titulo.setSpacing(4)
    titulo.addWidget(_texto("Central de Recursos", "portalRecursosTitulo"))
    titulo.addWidget(_texto("Ferramentas do VighnaStudy, organizadas por função.", "portalRecursosSubtitulo"))
    linha_topo.addLayout(titulo, 1)
    for rotulo, acao in (("← Início", abrir_inicio), ("Dashboard", abrir_dashboard)):
        botao = QPushButton(rotulo)
        botao.setObjectName("portalRecursosVoltar")
        botao.setCursor(Qt.PointingHandCursor)
        botao.clicked.connect(lambda _checked=False, fn=acao: fn())
        linha_topo.addWidget(botao)
    coluna.addWidget(topo)

    filtros = QHBoxLayout()
    filtros.setSpacing(10)
    busca = QLineEdit()
    busca.setObjectName("portalRecursosFiltro")
    busca.setPlaceholderText("Buscar ferramenta, tela ou assunto...")
    busca.setClearButtonEnabled(True)
    busca.setAccessibleName("Buscar recursos")
    filtros.addWidget(busca, 1)
    categoria = QComboBox()
    categoria.setObjectName("portalRecursosCategoria")
    categoria.addItem("Todas as categorias")
    categoria.addItem("Ferramentas principais")
    for nome in GRUPOS_SECUNDARIOS:
        categoria.addItem(nome)
    categoria.setMinimumWidth(165)
    categoria.setAccessibleName("Filtrar categoria de recursos")
    filtros.addWidget(categoria)
    coluna.addLayout(filtros)

    contador = _texto("", "portalRecursosContador")
    coluna.addWidget(contador)

    # Cada item aparece uma vez: primeiro seis destaques, depois os demais.
    por_id = {item[0]: item for item in CATALOGO_RECURSOS}
    secao_dados = [("Ferramentas principais", [por_id[i] for i in PRIORITARIOS])]
    for nome in GRUPOS_SECUNDARIOS:
        secao_dados.append((nome, [item for item in CATALOGO_RECURSOS
                                   if item[1] == nome and item[0] not in PRIORITARIOS]))
    grupos = []
    icones = []
    for nome, itens in secao_dados:
        if not itens:
            continue
        secao = QWidget()
        secao_layout = QVBoxLayout(secao)
        secao_layout.setContentsMargins(0, 4, 0, 0)
        secao_layout.setSpacing(9)
        cabecalho = QHBoxLayout()
        cabecalho.addWidget(_texto(nome, "portalRecursosGrupo"))
        qtde = _texto("", "portalRecursosGrupoContador")
        cabecalho.addStretch(1)
        cabecalho.addWidget(qtde)
        secao_layout.addLayout(cabecalho)
        divisoria = QFrame()
        divisoria.setObjectName("portalRecursosDivisor")
        divisoria.setFixedHeight(1)
        secao_layout.addWidget(divisoria)
        grade = QGridLayout()
        grade.setSpacing(9)
        colunas = 3 if nome == "Navegação" else 2
        for coluna_idx in range(colunas):
            grade.setColumnStretch(coluna_idx, 1)
        secao_layout.addLayout(grade)
        widgets = []
        for ident, grupo, rotulo, descricao in itens:
            card, icone = _criar_card(ident, rotulo, descricao, mapa[ident],
                                      destaque=nome == "Ferramentas principais",
                                      compacto=nome == "Navegação")
            widgets.append((card, ident, grupo, rotulo, descricao))
            icones.append((icone, ident))
        grupos.append((nome, secao, grade, qtde, colunas, widgets))
        coluna.addWidget(secao)
    coluna.addStretch(1)

    def filtrar():
        termo = normalizar_filtro(busca.text())
        opcao = categoria.currentText()
        quantidade = 0
        for nome, secao, grade, qtde, colunas, widgets in grupos:
            # Filtro de categoria respeita a categoria original do item; a
            # vitrine aceita filtro geral ou especificamente de destaques.
            posicao = 0
            for card, _, grupo, rotulo, descricao in widgets:
                dentro = (opcao == "Todas as categorias" or
                          (opcao == "Ferramentas principais" and nome == opcao) or
                          (opcao == grupo and opcao != "Ferramentas principais"))
                encontrado = not termo or termo in normalizar_filtro(
                    nome + " " + grupo + " " + rotulo + " " + descricao)
                visivel = dentro and encontrado
                grade.removeWidget(card)
                if visivel:
                    grade.addWidget(card, posicao // colunas, posicao % colunas)
                    posicao += 1
                    quantidade += 1
                card.setVisible(visivel)
            qtde.setText(f"{posicao} recursos" if posicao != 1 else "1 recurso")
            secao.setVisible(posicao > 0)
        contador.setText(f"{quantidade} recurso(s) disponível(is)" if quantidade else
                         "Nenhum recurso encontrado. Experimente outro termo.")

    busca.textChanged.connect(lambda _texto: filtrar())
    categoria.currentIndexChanged.connect(lambda _indice: filtrar())
    filtrar()
    scroll.setWidget(corpo)
    base.addWidget(scroll)
    pagina.portal_recursos_busca = busca
    pagina.portal_recursos_categoria = categoria
    pagina.portal_recursos_icones = icones
    pagina.portal_recursos_grupos = grupos
    return pagina


def aplicar_estilo_recursos(pagina, tema):
    pagina.setStyleSheet((render_native_qss(ESTILO_PORTAL_RECURSOS) if tema == "futurista"
                        else render_qss(tema, ESTILO_PORTAL_RECURSOS)))
    for rotulo, ident in getattr(pagina, "portal_recursos_icones", ()):
        _pintar_icone(rotulo, ident, tema)
