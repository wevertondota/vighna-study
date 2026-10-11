"""Portal de Disciplinas: resumo por matéria e cards tradicionais.

A grade mostra uma linha por disciplina e abre a tela original com tópicos,
capítulos e edição, sem duplicar controllers nem alterar dados persistidos.
"""

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QFrame, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QStackedWidget, QTableView, QVBoxLayout, QWidget,
)

from ui.design import render_qss, qss_color
from ui.disciplina_grade_data import resumir_disciplinas

QSS_PORTAL_DISCIPLINAS = r"""
QWidget#portalDisciplinasPage { background: {{color:canvas.app}}; }
QScrollArea#portalDisciplinasScroll, QWidget#portalDisciplinasBody,
QWidget#portalDisciplinasCards, QStackedWidget#portalDisciplinasViews {
    background: transparent; border: none;
}
QFrame#portalDisciplinasHeader, QFrame#portalDisciplinasCard {
    background-color: {{color:surface.secondary}};
    border: 1px solid {{color:border.default}};
    border-radius: 11px;
}
QLabel#portalDisciplinasTitle {
    color: {{color:text.primary}}; font-size: 18pt; font-weight: 800;
    background: transparent; border: none;
}
QLabel#portalDisciplinasSubtitle,
QLabel#portalDisciplinasProfile,
QLabel#portalDisciplinasCardDetail,
QLabel#portalDisciplinasEmpty,
QLabel#portalDisciplinasHint {
    color: {{color:text.secondary}}; font-size: 9pt;
    background: transparent; border: none;
}
QLabel#portalDisciplinasCount {
    color: {{color:text.muted}}; font-size: 9pt;
    background: transparent; border: none;
}
QLabel#portalDisciplinasCardName {
    color: {{color:text.primary}}; font-size: 11pt; font-weight: 700;
    background: transparent; border: none;
}
QPushButton#portalDisciplinasOpen,
QPushButton#portalDisciplinasEdit,
QPushButton#portalDisciplinasBack,
QPushButton#portalDisciplinasView,
QPushButton#portalDisciplinasOpenSelected {
    background-color: {{color:dashboard.nav_surface}};
    color: {{color:dashboard.nav_text}};
    border: 1px solid {{color:dashboard.nav_border}};
    border-radius: 8px;
    min-height: 30px;
    padding: 4px 12px;
    font-size: 9pt;
    font-weight: 700;
}
QPushButton#portalDisciplinasView:checked {
    background-color: {{color:dashboard.nav_hover_surface}};
    border-color: {{color:dashboard.nav_hover_border}};
}
QPushButton#portalDisciplinasOpen:hover,
QPushButton#portalDisciplinasEdit:hover,
QPushButton#portalDisciplinasBack:hover,
QPushButton#portalDisciplinasView:hover,
QPushButton#portalDisciplinasOpenSelected:hover {
    background-color: {{color:dashboard.nav_hover_surface}};
    border-color: {{color:dashboard.nav_hover_border}};
}
QPushButton#portalDisciplinasOpenSelected:disabled {
    color: {{color:text.disabled}};
    background-color: {{color:surface.disabled}};
    border-color: {{color:border.disabled}};
}
QLineEdit#portalDisciplinasSearch,
QComboBox#portalDisciplinasFilter {
    color: {{color:text.primary}};
    background-color: {{color:surface.secondary}};
    border: 1px solid {{color:border.default}};
    border-radius: 7px;
    padding: 5px 8px;
    min-height: 30px;
    font-size: 9pt;
}
QLineEdit#portalDisciplinasSearch:focus,
QComboBox#portalDisciplinasFilter:focus {
    border-color: {{color:dashboard.nav_border}};
}
QTableView#portalDisciplinasTable {
    background-color: {{color:surface.secondary}};
    alternate-background-color: {{color:surface.primary}};
    color: {{color:text.primary}};
    border: 1px solid {{color:border.default}};
    border-radius: 7px;
    gridline-color: {{color:border.default}};
    selection-background-color: {{color:dashboard.nav_hover_surface}};
    selection-color: {{color:text.primary}};
    font-size: 9pt;
}
QTableView#portalDisciplinasTable::item { padding: 4px 7px; }
QHeaderView::section {
    background: {{color:surface.secondary}};
    color: {{color:text.primary}};
    border: none;
    border-right: 1px solid {{color:border.default}};
    border-bottom: 1px solid {{color:border.default}};
    padding: 7px 8px;
    font-weight: 700;
}
"""


class ModeloGradeDisciplinas(QAbstractTableModel):
    """Uma linha por disciplina, sem expandir tópicos ou capítulos."""

    COLUNAS = ('Disciplina', 'Tópicos', 'Situação', 'Acessar')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.linhas = []
        self.tema = 'futurista'

    def definir_linhas(self, linhas):
        self.beginResetModel()
        self.linhas = list(linhas)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.linhas)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.COLUNAS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.COLUNAS[section] if 0 <= section < len(self.COLUNAS) else None
        return super().headerData(section, orientation, role)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self.linhas):
            return None
        linha = self.linhas[index.row()]
        coluna = index.column()
        if role == Qt.DisplayRole:
            return (
                linha['disciplina'], str(linha['quantidade_topicos']),
                linha['situacao'], ''
            )[coluna]
        if role == Qt.UserRole:
            return (
                linha['disciplina'].casefold(), linha['quantidade_topicos'],
                linha['situacao'].casefold(), linha['disciplina'].casefold()
            )[coluna]
        if role == Qt.TextAlignmentRole and coluna >= 1:
            return Qt.AlignCenter
        if role == Qt.ToolTipRole:
            if coluna == 0:
                return 'Clique para abrir os tópicos e capítulos na tela original.'
            if coluna == 1:
                return 'Quantidade de tópicos cadastrados nesta disciplina (não inclui capítulos).'
            if coluna == 3:
                return 'Abrir a tela de tópicos e capítulos desta disciplina.'
        if role == Qt.ForegroundRole:
            if linha['pausado']:
                return QColor(qss_color(self.tema, 'text.muted'))
            if coluna == 2:
                chave = ('text.muted' if linha['situacao'] == 'Sem tópicos'
                         else 'feedback.success_text')
                return QColor(qss_color(self.tema, chave))
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


class FiltroGradeDisciplinas(QSortFilterProxyModel):
    """Pesquisa e filtro agem somente sobre a lista de disciplinas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.disciplina = ''
        self.texto = ''
        self.setSortRole(Qt.UserRole)

    def definir_filtro(self, disciplina='', texto=''):
        self.disciplina = str(disciplina or '').strip()
        self.texto = str(texto or '').strip().casefold()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        modelo = self.sourceModel()
        if modelo is None or source_row >= len(modelo.linhas):
            return False
        item = modelo.linhas[source_row]
        return ((not self.disciplina or item['disciplina'] == self.disciplina)
                and (not self.texto or self.texto in item['disciplina'].casefold()))


class TelaDisciplinasPerfil(QWidget):
    """Resumo de disciplinas por padrão; edição detalhada já existente."""

    def __init__(self, listar_disciplinas, abrir_disciplina, editar_disciplinas,
                 voltar_inicio, listar_topicos=None, parent=None):
        super().__init__(parent)
        self.setObjectName('portalDisciplinasPage')
        self._listar = listar_disciplinas
        self._listar_topicos = listar_topicos or (lambda _nome: [])
        self._abrir = abrir_disciplina
        self._cards = []
        self._colunas = None
        self._registros = []
        pagina = QVBoxLayout(self)
        pagina.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName('portalDisciplinasScroll')
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll = scroll
        pagina.addWidget(scroll)

        corpo = QWidget()
        corpo.setObjectName('portalDisciplinasBody')
        coluna = QVBoxLayout(corpo)
        coluna.setContentsMargins(22, 17, 22, 22)
        coluna.setSpacing(12)

        cabecalho = QFrame()
        cabecalho.setObjectName('portalDisciplinasHeader')
        topo = QHBoxLayout(cabecalho)
        topo.setContentsMargins(17, 13, 17, 13)
        topo.setSpacing(12)
        titulos = QVBoxLayout()
        titulos.setSpacing(5)
        self.titulo = QLabel('Disciplinas do perfil')
        self.titulo.setObjectName('portalDisciplinasTitle')
        titulos.addWidget(self.titulo)
        subtitulo = QLabel('Escolha uma disciplina para consultar e editar seus tópicos e capítulos.')
        subtitulo.setObjectName('portalDisciplinasSubtitle')
        subtitulo.setWordWrap(True)
        titulos.addWidget(subtitulo)
        self.perfil = QLabel('Perfil ativo')
        self.perfil.setObjectName('portalDisciplinasProfile')
        titulos.addWidget(self.perfil)
        topo.addLayout(titulos, 1)

        botoes = QVBoxLayout()
        botoes.setSpacing(7)
        editar = QPushButton('Editar disciplinas')
        editar.setObjectName('portalDisciplinasEdit')
        editar.setCursor(Qt.PointingHandCursor)
        editar.setToolTip('Adicionar, renomear, pausar ou excluir disciplinas do perfil.')
        editar.clicked.connect(editar_disciplinas)
        botoes.addWidget(editar)
        voltar = QPushButton('← Início')
        voltar.setObjectName('portalDisciplinasBack')
        voltar.clicked.connect(voltar_inicio)
        botoes.addWidget(voltar)
        topo.addLayout(botoes)
        coluna.addWidget(cabecalho)

        barra_filtro = QHBoxLayout()
        barra_filtro.setSpacing(8)
        self.filtro_disciplina = QComboBox()
        self.filtro_disciplina.setObjectName('portalDisciplinasFilter')
        self.filtro_disciplina.setMinimumWidth(175)
        self.filtro_disciplina.currentIndexChanged.connect(self._aplicar_filtros)
        barra_filtro.addWidget(self.filtro_disciplina)
        self.busca = QLineEdit()
        self.busca.setObjectName('portalDisciplinasSearch')
        self.busca.setPlaceholderText('Buscar disciplina...')
        self.busca.setClearButtonEnabled(True)
        self.busca.textChanged.connect(self._aplicar_filtros)
        barra_filtro.addWidget(self.busca, 1)

        self.botao_grade = QPushButton('Grade')
        self.botao_cards = QPushButton('Cards')
        for botao in (self.botao_grade, self.botao_cards):
            botao.setObjectName('portalDisciplinasView')
            botao.setCheckable(True)
            botao.setCursor(Qt.PointingHandCursor)
            barra_filtro.addWidget(botao)
        self.botao_grade.clicked.connect(lambda: self._mostrar_modo(0))
        self.botao_cards.clicked.connect(lambda: self._mostrar_modo(1))
        self.botao_grade.setChecked(True)
        coluna.addLayout(barra_filtro)

        self.contador = QLabel('')
        self.contador.setObjectName('portalDisciplinasCount')
        coluna.addWidget(self.contador)

        self.visualizacoes = QStackedWidget()
        self.visualizacoes.setObjectName('portalDisciplinasViews')
        self.modelo = ModeloGradeDisciplinas(self)
        self.filtro = FiltroGradeDisciplinas(self)
        self.filtro.setSourceModel(self.modelo)
        self.tabela = QTableView()
        self.tabela.setObjectName('portalDisciplinasTable')
        self.tabela.setModel(self.filtro)
        self.tabela.setSortingEnabled(True)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.verticalHeader().hide()
        self.tabela.verticalHeader().setDefaultSectionSize(52)
        self.tabela.horizontalHeader().setMinimumHeight(35)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for indice, largura in enumerate((350, 105, 135, 165)):
            self.tabela.setColumnWidth(indice, largura)
        self.tabela.setMinimumHeight(130)
        self.tabela.doubleClicked.connect(self._abrir_duplo_clique)
        self.tabela.clicked.connect(self._abrir_clique_disciplina)
        self.tabela.selectionModel().selectionChanged.connect(self._atualizar_selecao)
        self.visualizacoes.addWidget(self.tabela)

        self.cards_container = QWidget()
        self.cards_container.setObjectName('portalDisciplinasCards')
        self.grade = QGridLayout(self.cards_container)
        self.grade.setContentsMargins(0, 0, 0, 0)
        self.grade.setHorizontalSpacing(12)
        self.grade.setVerticalSpacing(12)
        self.visualizacoes.addWidget(self.cards_container)
        coluna.addWidget(self.visualizacoes, 1)

        barra_rodape = QHBoxLayout()
        ajuda = QLabel('Clique no nome da disciplina ou em Abrir tópicos para consultar os conteúdos detalhados.')
        ajuda.setObjectName('portalDisciplinasHint')
        ajuda.setWordWrap(True)
        barra_rodape.addWidget(ajuda, 1)
        self.abrir_selecionado = QPushButton('Abrir tópicos da disciplina →')
        self.abrir_selecionado.setObjectName('portalDisciplinasOpenSelected')
        self.abrir_selecionado.setEnabled(False)
        self.abrir_selecionado.clicked.connect(self._abrir_linha)
        barra_rodape.addWidget(self.abrir_selecionado)
        coluna.addLayout(barra_rodape)
        coluna.addStretch(1)
        scroll.setWidget(corpo)
        self.corpo = corpo
        self._mostrar_modo(0)

    def atualizar(self, perfil_nome):
        self.perfil.setText('Perfil ativo: ' + (perfil_nome or '—'))
        disciplinas = list(self._listar())
        self._registros = resumir_disciplinas(disciplinas, self._listar_topicos)
        self.modelo.definir_linhas(self._registros)
        self._recriar_cards(disciplinas)
        selecionado = self.filtro_disciplina.currentData() or ''
        self.filtro_disciplina.blockSignals(True)
        self.filtro_disciplina.clear()
        self.filtro_disciplina.addItem('Todas as disciplinas', '')
        for _id, nome, _pausada in disciplinas:
            self.filtro_disciplina.addItem(str(nome), str(nome))
        for indice in range(self.filtro_disciplina.count()):
            if self.filtro_disciplina.itemData(indice) == selecionado:
                self.filtro_disciplina.setCurrentIndex(indice)
                break
        self.filtro_disciplina.blockSignals(False)
        self._aplicar_filtros()
        self.tabela.setFixedHeight(min(620, max(130, 45 + 52 * len(disciplinas))))
        self.tabela.clearSelection()
        self._atualizar_selecao()
        self.scroll.verticalScrollBar().setValue(0)

    def _recriar_cards(self, disciplinas):
        for card in self._cards:
            self.grade.removeWidget(card)
            card.deleteLater()
        self._cards.clear()
        self._colunas = None
        if not disciplinas:
            texto = QLabel('Nenhuma disciplina neste perfil. Use “Editar disciplinas” para cadastrar ou vincular disciplinas.')
            texto.setObjectName('portalDisciplinasEmpty')
            texto.setWordWrap(True)
            self._cards.append(texto)
        for _id, nome, pausada in disciplinas:
            card = QFrame()
            card.setObjectName('portalDisciplinasCard')
            card.setProperty('disciplinaNome', str(nome))
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            card.setMinimumHeight(126)
            interno = QVBoxLayout(card)
            interno.setContentsMargins(15, 13, 15, 13)
            interno.setSpacing(7)
            titulo = QLabel(str(nome))
            titulo.setObjectName('portalDisciplinasCardName')
            titulo.setWordWrap(True)
            interno.addWidget(titulo)
            detalhe = QLabel('Desligada temporariamente • tópicos disponíveis para edição' if pausada
                            else 'Consultar e editar tópicos desta disciplina')
            detalhe.setObjectName('portalDisciplinasCardDetail')
            detalhe.setWordWrap(True)
            interno.addWidget(detalhe)
            interno.addStretch(1)
            abrir = QPushButton('Abrir tópicos  →')
            abrir.setObjectName('portalDisciplinasOpen')
            abrir.setCursor(Qt.PointingHandCursor)
            abrir.clicked.connect(lambda _checked=False, disciplina=nome: self._abrir(disciplina))
            interno.addWidget(abrir)
            self._cards.append(card)
        self._redistribuir(self.corpo.width())

    def _mostrar_modo(self, indice):
        self.visualizacoes.setCurrentIndex(indice)
        self.botao_grade.setChecked(indice == 0)
        self.botao_cards.setChecked(indice == 1)
        self.abrir_selecionado.setVisible(indice == 0)

    def _aplicar_filtros(self, *_args):
        disciplina = self.filtro_disciplina.currentData() or ''
        texto = self.busca.text().strip()
        self.filtro.definir_filtro(disciplina, texto)
        disciplina_escolhida = str(disciplina or '')
        busca = texto.casefold()
        for card in self._cards:
            nome = card.property('disciplinaNome') or ''
            if not nome:
                card.setVisible(not busca and not disciplina_escolhida)
            else:
                card.setVisible((not disciplina_escolhida or nome == disciplina_escolhida) and
                                (not busca or busca in str(nome).casefold()))
        self.contador.setText(
            f"{self.filtro.rowCount()} disciplina(s) visível(is) · "
            f"{len(self._registros)} disciplina(s) do perfil"
        )
        self._preencher_botoes_abrir()
        self._atualizar_selecao()

    def _registro_selecionado(self):
        indice = self.tabela.currentIndex()
        if not indice.isValid():
            return None
        origem = self.filtro.mapToSource(indice)
        if not origem.isValid() or origem.row() >= len(self.modelo.linhas):
            return None
        return self.modelo.linhas[origem.row()]

    def _atualizar_selecao(self, *_args):
        self.abrir_selecionado.setEnabled(self._registro_selecionado() is not None)

    def _abrir_linha(self, indice=None, *_args):
        if indice is not None and hasattr(indice, 'isValid') and indice.isValid():
            origem = self.filtro.mapToSource(indice)
            if origem.isValid() and origem.row() < len(self.modelo.linhas):
                self._abrir(self.modelo.linhas[origem.row()]['disciplina'])
                return
        selecionado = self._registro_selecionado()
        if selecionado:
            self._abrir(selecionado['disciplina'])

    def _abrir_clique_disciplina(self, indice):
        # Um clique no nome abre a disciplina, sem precisar de duplo clique.
        if indice.isValid() and indice.column() == 0:
            self._abrir_linha(indice)

    def _abrir_duplo_clique(self, indice):
        # Evita segunda abertura quando o primeiro clique no nome já navegou.
        if indice.isValid() and indice.column() != 0:
            self._abrir_linha(indice)

    def _preencher_botoes_abrir(self):
        # São poucas disciplinas: um botão real por linha oferece uma ação
        # acessível também via Tab/Enter, sem alterar os dados da tabela.
        for linha in range(self.filtro.rowCount()):
            indice = self.filtro.index(linha, 3)
            origem = self.filtro.mapToSource(indice)
            if not origem.isValid():
                continue
            nome = self.modelo.linhas[origem.row()]['disciplina']
            botao = QPushButton('Abrir tópicos  →')
            botao.setObjectName('portalDisciplinasOpen')
            botao.setCursor(Qt.PointingHandCursor)
            botao.setToolTip('Abrir os tópicos e capítulos de ' + nome)
            botao.clicked.connect(lambda _checked=False, disciplina=nome: self._abrir(disciplina))
            self.tabela.setIndexWidget(indice, botao)

    def _redistribuir(self, largura):
        colunas = 3 if largura >= 1020 else 2 if largura >= 620 else 1
        if self._colunas == colunas:
            return
        self._colunas = colunas
        while self.grade.count():
            self.grade.takeAt(0)
        for coluna in range(3):
            self.grade.setColumnStretch(coluna, 1 if coluna < colunas else 0)
        for indice, card in enumerate(self._cards):
            self.grade.addWidget(card, indice // colunas, indice % colunas)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._cards:
            self._redistribuir(self.corpo.width())


def criar_portal_disciplinas(listar_disciplinas, abrir_disciplina,
                             editar_disciplinas, voltar_inicio, listar_topicos=None):
    return TelaDisciplinasPerfil(
        listar_disciplinas, abrir_disciplina, editar_disciplinas, voltar_inicio,
        listar_topicos=listar_topicos,
    )


def aplicar_estilo_portal_disciplinas(pagina, tema):
    pagina.modelo.tema = tema
    pagina.setStyleSheet(render_qss(tema, QSS_PORTAL_DISCIPLINAS))
