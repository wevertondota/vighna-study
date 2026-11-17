"""Grade de Estudos R6 — organização visual Qt do painel Iniciar Estudo.

Somente aberto pelo botão de acesso. Reutiliza o cadastro e a Central
Integrada de Tópicos; nunca replica ou reinicia o motor de revisões.
"""
from __future__ import annotations

from datetime import date, timedelta
import sqlite3

from PySide6.QtCore import Qt, QDate, QTimer, QRectF
from PySide6.QtGui import (
    QColor, QPainter, QPen, QPainterPath, QFont, QFontMetrics,
    QLinearGradient, QIcon, QPixmap,
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTabBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox, QInputDialog, QDialog,
    QDialogButtonBox, QDateEdit, QCheckBox, QComboBox,
    QSizePolicy, QStyledItemDelegate, QStyle, QStyleOptionViewItem,
)

from ui.grade_estudos_dados_v1 import RepositorioGrade, NOTA_MAX


def _mostrar_data(texto):
    if not texto:
        return '—'
    try:
        return date.fromisoformat(str(texto)[:10]).strftime('%d/%m/%Y')
    except ValueError:
        return str(texto)


def _prazo_data(valor):
    """Converte a data da agenda; nunca usa revisão executada como prazo."""
    if not valor:
        return None
    try:
        return date.fromisoformat(str(valor)[:10])
    except (TypeError, ValueError):
        return None


def _situacao_revisao(valor, hoje):
    """Prazo visual: o mesmo dia local usado pelo calendário do aplicativo."""
    prazo = _prazo_data(valor)
    if prazo is None:
        return 'sem_data'
    if prazo < hoje:
        return 'atrasada'
    if prazo == hoje:
        return 'hoje'
    if prazo <= hoje + timedelta(days=6):
        return 'proximos'
    return 'futura'


def _visivel_por_situacao(linha, condicao, hoje, em_andamento=None):
    if condicao == 'andamento':
        return int(linha.topico_id) in (em_andamento or {})
    situacao = _situacao_revisao(linha.proxima_revisao, hoje)
    if condicao == 'atrasada':
        return situacao == 'atrasada'
    if condicao == 'hoje':
        return situacao == 'hoje'
    if condicao == 'proximos':
        return situacao in ('hoje', 'proximos')
    if condicao == 'sem_data':
        return situacao == 'sem_data'
    return True


def _ordenar_linhas(linhas, modo, hoje=None):
    """Ordena cópia das linhas; a lista do repositório mantém ordem do edital."""
    resultado = list(linhas)
    if modo == 'prioridade':
        referencia = hoje or date.today()
        resultado.sort(key=lambda x: _chave_prioridade(x, referencia))
    elif modo == 'prazo':
        resultado.sort(key=lambda x: (
            _prazo_data(x.proxima_revisao) is None,
            _prazo_data(x.proxima_revisao) or date.max,
            x.topico.casefold(),
        ))
    elif modo == 'desempenho':
        # Sem tentativas não é desempenho zero: esses tópicos ficam ao fim.
        resultado.sort(key=lambda x: (
            not bool(x.tentativas),
            (100 * x.acertos / x.tentativas) if x.tentativas else 101.0,
            x.topico.casefold(),
        ))
    return resultado


def _chave_prioridade(linha, hoje):
    """Agenda oficial primeiro; importância e acertos desempatarão.

    Uma data ausente exige conferência, não é revisão vencida.
    Não escreve prioridade no banco nem substitui o ciclo de revisões.
    """
    situacao = _situacao_revisao(linha.proxima_revisao, hoje)
    grupo = {'atrasada': 0, 'hoje': 1, 'proximos': 2,
             'sem_data': 3, 'futura': 4}[situacao]
    data_prazo = _prazo_data(linha.proxima_revisao)
    taxa = ((100.0 * linha.acertos / linha.tentativas)
            if linha.tentativas else 101.0)
    # Em prazos vencidos, a data mais antiga precede. Dentro do mesmo
    # vencimento, a importância do perfil e a taxa desempatam.
    return (grupo, data_prazo or date.max,
            -max(1, min(5, int(linha.importancia))),
            not bool(linha.tentativas), taxa, linha.topico.casefold())


def _resumo_prazos(linhas, hoje, em_andamento=None):
    contagens = {'andamento': 0, 'atrasada': 0, 'hoje': 0, 'proximos': 0, 'sem_data': 0}
    ativos = em_andamento or {}
    for linha in linhas:
        if int(linha.topico_id) in ativos:
            contagens['andamento'] += 1
        situacao = _situacao_revisao(linha.proxima_revisao, hoje)
        if situacao in contagens:
            contagens[situacao] += 1
    return contagens


class CartaoFiltroGrade(QPushButton):
    """Filtro Qt compacto: o badge é desenhado sem widgets adicionais.

    A lógica de clique permanece no QPushButton original; a pintura é local
    à Grade e independente do tema global do aplicativo.
    """
    CORES = {
        'todos': '#96BED3', 'andamento': '#2BD3C9',
        'atrasada': '#EC8887', 'hoje': '#70C9EF',
        'proximos': '#B5A1F4', 'sem_data': '#B9C9D4',
    }

    def __init__(self, chave, titulo, parent=None):
        super().__init__(titulo, parent)
        self.chave = chave
        self.titulo = titulo
        self.contagem = None
        self.ativo = False
        self.sobre = False
        self.setObjectName('gradeFiltroCartaoR6')
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50)
        self.setMinimumWidth(118)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAccessibleName(titulo)

    def set_dados(self, titulo, contagem, ativo):
        if (self.titulo, self.contagem, self.ativo) != (titulo, contagem, ativo):
            self.titulo, self.contagem, self.ativo = titulo, contagem, ativo
            self.setText(titulo)  # semântico, a pintura desenha a legenda.
            self.update()

    def enterEvent(self, event):
        self.sobre = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.sobre = False
        self.update()
        super().leaveEvent(event)

    def _desenhar_icone(self, p, x, y, cor):
        p.save()
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor(cor), 1.7))
        p.setBrush(Qt.NoBrush)
        if self.chave == 'andamento':
            triangulo = QPainterPath()
            triangulo.moveTo(x + 3, y)
            triangulo.lineTo(x + 3, y + 16)
            triangulo.lineTo(x + 16, y + 8)
            triangulo.closeSubpath()
            p.drawPath(triangulo)
        elif self.chave == 'todos':
            p.drawRoundedRect(QRectF(x + 2, y, 14, 18), 2, 2)
            for offset in (5, 9, 13):
                p.drawLine(x + 5, y + offset, x + 13, y + offset)
        else:
            p.drawRoundedRect(QRectF(x + 1, y + 2, 17, 15), 2, 2)
            p.drawLine(x + 2, y + 7, x + 17, y + 7)
            p.drawLine(x + 6, y, x + 6, y + 5)
            p.drawLine(x + 13, y, x + 13, y + 5)
            if self.chave == 'atrasada':
                p.drawLine(x + 9, y + 10, x + 9, y + 13)
                p.drawPoint(x + 9, y + 15)
            elif self.chave == 'hoje':
                p.setBrush(QColor(cor))
                p.drawEllipse(QRectF(x + 7, y + 10, 4, 4))
            elif self.chave == 'proximos':
                p.drawLine(x + 5, y + 12, x + 8, y + 14)
                p.drawLine(x + 8, y + 14, x + 14, y + 9)
            else:
                p.drawLine(x + 6, y + 11, x + 13, y + 11)
        p.restore()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        cor = self.CORES[self.chave]
        if not self.isEnabled():
            borda = '#284050'
            fill = QColor('#0B2232')
        else:
            borda = cor if self.ativo else ('#467C99' if self.sobre else '#26526C')
            fill = QColor('#093746' if self.ativo else
                          '#12394F' if self.sobre else '#102D42')
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, fill.lighter(112))
        grad.setColorAt(1, fill.darker(112))
        p.setBrush(grad)
        p.setPen(QPen(QColor(borda), 1.5 if self.ativo else 1))
        p.drawRoundedRect(r, 9, 9)
        if self.hasFocus():
            p.setPen(QPen(QColor('#DBF4FF'), 1, Qt.DashLine))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(r.adjusted(3, 3, -3, -3), 7, 7)
        icon_x = int(r.left()) + 13
        self._desenhar_icone(p, icon_x, (self.height() - 18) // 2, cor)
        direita = self.width() - 12
        if self.contagem is not None:
            quantidade = str(self.contagem)
            fonte_badge = QFont(self.font())
            fonte_badge.setPixelSize(12)
            fonte_badge.setBold(True)
            fm_badge = QFontMetrics(fonte_badge)
            badge_w = max(26, fm_badge.horizontalAdvance(quantidade) + 16)
            direita -= badge_w
            br = QRectF(direita, (self.height() - 24) / 2, badge_w, 24)
            fundo_badge = QColor(cor)
            fundo_badge.setAlpha(42 if not self.ativo else 62)
            p.setPen(Qt.NoPen)
            p.setBrush(fundo_badge)
            p.drawRoundedRect(br, 12, 12)
            p.setFont(fonte_badge)
            p.setPen(QColor('#F3FCFF'))
            p.drawText(br, Qt.AlignCenter, quantidade)
            direita -= 9
        p.setFont(self.font())
        fonte = QFont(self.font())
        fonte.setPixelSize(13)
        fonte.setBold(self.ativo)
        p.setFont(fonte)
        p.setPen(QColor('#E7F6FD' if self.isEnabled() else '#75909D'))
        area = QRectF(icon_x + 30, 0, max(12, direita - icon_x - 30), self.height())
        titulo = QFontMetrics(fonte).elidedText(self.titulo, Qt.ElideRight, int(area.width()))
        p.drawText(area, Qt.AlignVCenter | Qt.AlignLeft, titulo)
        p.end()


class DelegadoTopicoGrade(QStyledItemDelegate):
    """Mostra um marcador de ciclo ativo sem adicionar widgets por linha."""

    def paint(self, painter, option, index):
        if not index.data(Qt.UserRole + 1):
            super().paint(painter, option, index)
            return
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.text = ''
        estilo = opt.widget.style() if opt.widget is not None else None
        if estilo is None:
            super().paint(painter, option, index)
            return
        estilo.drawControl(QStyle.CE_ItemViewItem, opt, painter, opt.widget)
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        area = option.rect.adjusted(9, 0, -8, 0)
        fonte = QFont(option.font)
        fonte.setPixelSize(12)
        metrica = QFontMetrics(fonte)
        fonte_badge = QFont(fonte)
        fonte_badge.setPixelSize(10)
        badge_texto = '▶ Em andamento'
        badge_w = QFontMetrics(fonte_badge).horizontalAdvance(badge_texto) + 20
        largura_texto = max(10, area.width() - badge_w - 12)
        texto = metrica.elidedText(str(index.data(Qt.DisplayRole) or ''),
                                   Qt.ElideRight, largura_texto)
        pintado = min(metrica.horizontalAdvance(texto) + 12, largura_texto + 4)
        painter.setFont(fonte)
        painter.setPen(QColor('#EAF8FF'))
        painter.drawText(QRectF(area.left(), area.top(), largura_texto,
                                area.height()), Qt.AlignVCenter, texto)
        x = area.left() + pintado
        y = area.top() + (area.height() - 20) / 2
        badge_rect = QRectF(x, y, badge_w, 20)
        painter.setPen(QPen(QColor('#198E7D'), 1))
        painter.setBrush(QColor('#06453F'))
        painter.drawRoundedRect(badge_rect, 9, 9)
        painter.setFont(fonte_badge)
        painter.setPen(QColor('#83F1D0'))
        painter.drawText(badge_rect, Qt.AlignCenter, badge_texto)
        painter.restore()


class PaginaGradeEstudos(QWidget):
    """Uma tabela reaproveitada entre as abas evita criar N tabelas grandes."""
    COLS = ['Tópico', 'Questões', 'Acertos / %', 'Rev.',
            'Última', 'Próxima revisão', 'Anotação', 'Ação']
    COLS_GLOBAIS = ['Disciplina', *COLS]
    COLS_RESUMO = ['Disciplina', 'Tópicos', 'Em andamento', 'Atrasadas',
                   'Hoje', '7 dias', 'Sem data', 'Ação']

    def __init__(self, janela, voltar, abrir_topico, parent=None,
                 repositorio=None):
        super().__init__(parent)
        self.setObjectName('gradeEstudosV1')
        self.janela = janela
        self.voltar = voltar
        self.abrir_topico = abrir_topico
        self.repo = repositorio or RepositorioGrade()
        self._disciplinas = []
        self._linhas = []
        self._topicos_por_disciplina = {}
        self._disciplina_por_topico = {}
        self._concurso_id = None
        self._id_disciplina = None
        self._posicoes = {}
        self._carregando = False
        self._origens_agenda = {}
        self._tendencias = {}
        self._situacao_ativa = 'resumo'
        self._escopo_todas = True
        self._resumo_linhas = []
        self._ciclos_ativos = {}
        self._estado_por_perfil = {}
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(17, 13, 17, 12)
        raiz.setSpacing(11)

        # Cabeçalho: retorno existente, identificação da página e ações.
        cab = QHBoxLayout()
        cab.setSpacing(12)
        voltar_btn = QPushButton('← Iniciar estudo')
        voltar_btn.setObjectName('gradeVoltarV1')
        voltar_btn.setCursor(Qt.PointingHandCursor)
        voltar_btn.setFixedHeight(32)
        voltar_btn.clicked.connect(self.voltar)
        cab.addWidget(voltar_btn, 0, Qt.AlignVCenter)
        titulos = QVBoxLayout()
        titulos.setSpacing(0)
        titulo = QLabel('Grade de Estudos e Revisões')
        titulo.setObjectName('gradeTituloV1')
        titulos.addWidget(titulo)
        subtitulo = QLabel('Organize seus tópicos e acompanhe suas revisões')
        subtitulo.setObjectName('gradeSubtituloR6')
        titulos.addWidget(subtitulo)
        cab.addLayout(titulos, 1)
        self.perfil_label = QLabel('')
        self.perfil_label.setObjectName('gradePerfilV1')
        self.perfil_label.setAlignment(Qt.AlignCenter)
        self.perfil_label.setMinimumHeight(33)
        cab.addWidget(self.perfil_label, 0, Qt.AlignVCenter)
        atualizar = QPushButton('↻  Atualizar')
        atualizar.setObjectName('gradeAtualizarV2')
        atualizar.setFixedHeight(34)
        atualizar.clicked.connect(self.atualizar)
        atualizar.setCursor(Qt.PointingHandCursor)
        cab.addWidget(atualizar, 0, Qt.AlignVCenter)
        raiz.addLayout(cab)

        # Abas por disciplina: a primeira mantém o escopo global dourado.
        self.abas = QTabBar()
        self.abas.setObjectName('gradeAbasV1')
        self.abas.setDrawBase(False)
        self.abas.setExpanding(False)
        self.abas.setUsesScrollButtons(True)
        self.abas.setMinimumHeight(36)
        self.abas.currentChanged.connect(self._ao_mudar_aba)
        raiz.addWidget(self.abas)

        # Uma linha horizontal com seis cartões; nenhuma recomendação automática.
        barra_status = QHBoxLayout()
        barra_status.setSpacing(7)
        self.resumo_prazos = QLabel('Tópicos e revisões')
        self.resumo_prazos.setObjectName('gradeTituloResultadosR6')
        self._atalhos_prazos = {}
        for valor, rotulo in (
            ('todos', 'Resumo'), ('andamento', 'Em andamento'),
            ('atrasada', 'Atrasadas'), ('hoje', 'Hoje'),
            ('proximos', '7 dias'), ('sem_data', 'Sem data'),
        ):
            atalho = CartaoFiltroGrade(valor, rotulo, self)
            atalho.clicked.connect(lambda _=False, v=valor: self._filtro_rapido(v))
            barra_status.addWidget(atalho, 1)
            self._atalhos_prazos[valor] = atalho
        raiz.addLayout(barra_status)

        # Barra de resultados integra contagem, pesquisa e ordenação.
        linha_acoes = QHBoxLayout()
        linha_acoes.setSpacing(9)
        linha_acoes.addWidget(self.resumo_prazos, 0, Qt.AlignVCenter)
        divisor = QLabel('│')
        divisor.setObjectName('gradeDivisorResultadosR6')
        linha_acoes.addWidget(divisor, 0, Qt.AlignVCenter)
        self.status = QLabel('')
        self.status.setObjectName('gradeStatusV1')
        self.status.setMinimumWidth(78)
        linha_acoes.addWidget(self.status, 0, Qt.AlignVCenter)
        linha_acoes.addStretch(1)
        self.busca = QLineEdit()
        self.busca.setObjectName('gradeBuscaV1')
        self.busca.setPlaceholderText('Pesquisar tópico ou disciplina...')
        self.busca.setClearButtonEnabled(True)
        self.busca.setMinimumWidth(190)
        self.busca.setMaximumWidth(500)
        self.busca.setFixedHeight(35)
        self.busca.textChanged.connect(lambda _texto: self._filtrar())
        linha_acoes.addWidget(self.busca, 3)

        self.ordenar_label = QLabel('Ordenar:')
        self.ordenar_label.setObjectName('gradeOrdenarLabelR3')
        linha_acoes.addWidget(self.ordenar_label, 0, Qt.AlignVCenter)
        self.ordenacao = QComboBox()
        self.ordenacao.setObjectName('gradeOrdenacaoV2')
        for rotulo, valor in (
            ('Ordem do edital', 'edital'),
            ('Próxima revisão', 'prazo'),
            ('Menor % acerto', 'desempenho'),
            ('Prioridade de revisão', 'prioridade'),
        ):
            self.ordenacao.addItem(rotulo, valor)
        self.ordenacao.setMinimumWidth(148)
        self.ordenacao.setMaximumWidth(184)
        self.ordenacao.setFixedHeight(35)
        self.ordenacao.setAccessibleName('Ordenar tópicos')
        self.ordenacao.currentIndexChanged.connect(lambda _i: self._reordenar())
        linha_acoes.addWidget(self.ordenacao)
        raiz.addLayout(linha_acoes)

        self.tabela = QTableWidget()
        self.tabela.setObjectName('gradeTabelaV1')
        self.tabela.setColumnCount(len(self.COLS))
        self.tabela.setHorizontalHeaderLabels(self.COLS)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setShowGrid(False)
        self.tabela.setWordWrap(False)
        self.tabela.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tabela.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self._delegado_topico = DelegadoTopicoGrade(self.tabela)
        self.tabela.setItemDelegate(self._delegado_topico)
        head = self.tabela.horizontalHeader()
        head.setFixedHeight(33)
        head.setSectionResizeMode(0, QHeaderView.Stretch)
        for c, largura in {1:76, 2:158, 3:48, 4:83,
                           5:126, 6:117, 7:64}.items():
            head.setSectionResizeMode(c, QHeaderView.Fixed)
            self.tabela.setColumnWidth(c, largura)
        self.tabela.cellDoubleClicked.connect(self._duplo_clique)
        raiz.addWidget(self.tabela, 1)
        self.setStyleSheet('''
            QWidget#gradeEstudosV1 {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                  stop:0 #071724,stop:0.56 #061c2f,stop:1 #07263a);
                color:#EAF4FC;
            }
            QLabel#gradeTituloV1 {font-size:21px;font-weight:700;color:#F1F9FF;}
            QLabel#gradeSubtituloR6 {font-size:11px;color:#9CB8C9;}
            QLabel#gradePerfilV1 {font-size:11px;color:#C6E0ED;
                border:1px solid #2C556B;border-radius:8px;
                background:#0C2436;padding:4px 12px;}
            QPushButton#gradeVoltarV1 {background:#0B3248;border:1px solid #286B8A;
                border-radius:7px;color:#D4ECF6;padding:3px 10px;font-size:11px;}
            QPushButton#gradeVoltarV1:hover {border-color:#44C3E8;background:#11425C;}
            QPushButton#gradeAtualizarV2 {background:#08749A;
                border:1px solid #23C9E9;border-radius:8px;
                color:#F4FCFF;font-size:12px;font-weight:600;padding:4px 13px;}
            QPushButton#gradeAtualizarV2:hover {background:#0B8CAF;}
            QTabBar#gradeAbasV1::tab {padding:7px 12px;
                background:#0D2D43;border:1px solid #28556E;
                border-radius:7px;margin-right:3px;color:#D5EAF5;font-size:11px;}
            QTabBar#gradeAbasV1::tab:hover {border-color:#419EC5;background:#123B53;}
            QTabBar#gradeAbasV1::tab:selected {background:#0E4B68;
                border-color:#29A5D3;color:#F5FCFF;font-weight:600;}
            QTabBar#gradeAbasV1::tab:first:selected {background:#40391F;
                border-color:#D9B65D;color:#FFE3A1;}
            QTabBar#gradeAbasV1::tab:first {color:#DFBF77;border-color:#9B8246;}
            QLabel#gradeTituloResultadosR6 {font-size:14px;font-weight:700;
                color:#EAF7FC;}
            QLabel#gradeDivisorResultadosR6 {font-size:14px;color:#365C72;}
            QLabel#gradeStatusV1 {font-size:11px;color:#B1C9D6;}
            QLabel#gradeOrdenarLabelR3 {font-size:11px;color:#BED5E1;}
            QLineEdit#gradeBuscaV1 {background:#0C2A3C;border:1px solid #286481;
                border-radius:7px;color:#F2FBFF;padding:2px 11px;font-size:12px;}
            QLineEdit#gradeBuscaV1:focus {border-color:#29C1E1;background:#0E344B;}
            QComboBox#gradeOrdenacaoV2 {background:#0F3045;border:1px solid #286481;
                border-radius:7px;color:#E5F4FA;padding:2px 10px;font-size:11px;}
            QComboBox#gradeOrdenacaoV2:hover {border-color:#3C98BD;}
            QComboBox#gradeOrdenacaoV2 QAbstractItemView {
                background:#102E42;color:#ECF9FF;selection-background-color:#17618A;}
            QTableWidget#gradeTabelaV1 {background:#081E30;
                alternate-background-color:#0C2B40;color:#E9F6FC;
                border:1px solid #24536C;border-radius:10px;
                selection-background-color:#145373;
                selection-color:#F4FBFF;font-size:12px;}
            QHeaderView::section {background:#123D54;color:#D6EAF5;
                border:0;border-bottom:1px solid #26617A;
                padding:5px 6px;font-size:11px;font-weight:600;}
            QTableWidget#gradeTabelaV1 QTableCornerButton::section {
                background:#123D54;border:0;}
            QTableWidget#gradeTabelaV1 QScrollBar:vertical {background:#071D30;
                width:8px;border:0;}
            QTableWidget#gradeTabelaV1 QScrollBar::handle:vertical {
                background:#246483;border-radius:4px;min-height:24px;}
            QTableWidget#gradeTabelaV1 QScrollBar::add-line:vertical,
            QTableWidget#gradeTabelaV1 QScrollBar::sub-line:vertical {
                background:transparent;height:0;}
            QPushButton#gradeDataDiscreta {background:#142F43;
                border:1px solid #35586F;border-radius:7px;
                color:#D6E8F0;padding:2px 5px;font-size:11px;}
            QPushButton#gradeDataDiscreta:hover {border-color:#4CA8D0;background:#174059;}
            QPushButton#gradeAnotacaoDiscreta {background:transparent;
                border:1px solid transparent;color:#55C9EC;
                padding:1px 4px;font-size:11px;}
            QPushButton#gradeAnotacaoDiscreta:hover {color:#A4E8FA;
                background:#10364B;border-radius:5px;}
            QPushButton#gradeAbrirDiscreto {background:#0A4D6B;
                border:1px solid #2AC5E8;border-radius:7px;
                color:#F2FAFF;font-size:11px;font-weight:600;padding:2px 5px;}
            QPushButton#gradeAbrirDiscreto:hover {background:#0879A0;}
        ''')
        # Atualiza se alterações acadêmicas ocorrerem enquanto a grade existe.
        if hasattr(janela, 'dados_alterados'):
            janela.dados_alterados.connect(self._dados_alterados)

    def showEvent(self, event):
        super().showEvent(event)
        # Sempre lê o perfil e a estrutura atual; nenhuma cópia persistente
        # da lista de disciplinas fica desatualizada.
        QTimer.singleShot(0, self.atualizar)

    def _dados_alterados(self, escopo):
        if str(escopo).lower() in ('all', 'topicos', 'revisoes', 'questoes', 'tentativas'):
            if self.isVisible():
                QTimer.singleShot(0, self.atualizar)

    def atualizar(self):
        if self._carregando:
            return
        self._carregando = True
        try:
            from banco import obter_concurso_ativo
            concurso = obter_concurso_ativo()
            cid = int(concurso[0])
            mudou_perfil = cid != self._concurso_id
            if mudou_perfil:
                if self._concurso_id is not None:
                    self._estado_por_perfil[self._concurso_id] = (
                        self._id_disciplina, self._escopo_todas, self.busca.text(),
                        self._situacao_ativa, self.ordenacao.currentData(),
                    )
                self._posicoes.clear()
                self._topicos_por_disciplina.clear()
                self._disciplina_por_topico.clear()
                anterior = self._estado_por_perfil.get(
                    cid, (None, True, '', 'resumo', 'edital'))
                self._escopo_todas = bool(anterior[1])
                self._situacao_ativa = anterior[3]
                self.busca.blockSignals(True)
                self.busca.setText(anterior[2])
                self.busca.blockSignals(False)
                self.ordenacao.blockSignals(True)
                posicao = self.ordenacao.findData(anterior[4])
                self.ordenacao.setCurrentIndex(max(0, posicao))
                self.ordenacao.blockSignals(False)
                selecionado_id = anterior[0]
            else:
                selecionado_id = self._id_disciplina
                self._posicoes[self._chave_scroll()] = (
                    self.tabela.verticalScrollBar().value())

            self._concurso_id = cid
            self.perfil_label.setText(f'◇  Perfil: {concurso[1]}')
            disciplinas = self.repo.disciplinas(cid)
            self._disciplinas = disciplinas
            self.abas.blockSignals(True)
            while self.abas.count():
                self.abas.removeTab(self.abas.count() - 1)
            self.abas.addTab('Todas')
            self.abas.setTabData(0, None)
            self.abas.setTabTextColor(0, QColor('#e0bb6f'))
            selecionada = 1 if disciplinas else 0
            for i, (ident, nome) in enumerate(disciplinas, start=1):
                self.abas.addTab(nome)
                self.abas.setTabData(i, int(ident))
                if selecionado_id is not None and int(selecionado_id) == int(ident):
                    selecionada = i
            self._id_disciplina = (int(disciplinas[selecionada - 1][0])
                                   if disciplinas and selecionada else
                                   int(disciplinas[0][0]) if disciplinas else None)
            if not disciplinas:
                self._escopo_todas = True
            self.abas.setCurrentIndex(0 if self._escopo_todas else selecionada)
            self.abas.blockSignals(False)
            opcoes = (('resumo', 'andamento', 'atrasada', 'hoje',
                       'proximos', 'sem_data') if self._escopo_todas else
                      ('todos', 'andamento', 'atrasada', 'hoje',
                       'proximos', 'sem_data'))
            if self._situacao_ativa not in opcoes:
                self._situacao_ativa = 'resumo' if self._escopo_todas else 'todos'
            self._atualizar_placeholder()
            self._recarregar_dados_perfil()
            self._atualizar_tabela()
        except Exception as exc:
            QMessageBox.warning(self, 'Grade de Estudos',
                                f'Não foi possível atualizar a grade:\n{exc}')
        finally:
            self._carregando = False

    def _ao_mudar_aba(self, indice):
        if self._carregando or indice < 0 or indice >= self.abas.count():
            return
        self._posicoes[self._chave_scroll()] = self.tabela.verticalScrollBar().value()
        self._escopo_todas = indice == 0
        if self._escopo_todas:
            self._situacao_ativa = 'resumo'
        else:
            self._id_disciplina = int(self.abas.tabData(indice))
            self._situacao_ativa = 'todos'
        # Evita esconder registros por uma pesquisa iniciada em outro contexto.
        self.busca.blockSignals(True)
        self.busca.clear()
        self.busca.blockSignals(False)
        self._atualizar_placeholder()
        self._atualizar_tabela()

    def _atualizar_placeholder(self):
        # O resumo mantém a ordem das disciplinas do edital: esconder uma
        # ordenação que só seria aplicada à lista de tópicos.
        exibe_ordenacao = not self._modo_resumo()
        self.ordenar_label.setVisible(exibe_ordenacao)
        self.ordenacao.setVisible(exibe_ordenacao)
        if self._escopo_todas and self._situacao_ativa == 'resumo':
            self.busca.setPlaceholderText('Pesquisar disciplina...')
        elif self._escopo_todas:
            self.busca.setPlaceholderText('Pesquisar tópico ou disciplina...')
        else:
            self.busca.setPlaceholderText('Pesquisar tópico...')

    def _abrir_disciplina(self, disciplina_id):
        for indice in range(1, self.abas.count()):
            if int(self.abas.tabData(indice)) == int(disciplina_id):
                self.abas.setCurrentIndex(indice)
                return

    def _recarregar_dados_perfil(self):
        """Consulta tópicos apenas do perfil ativo, sem alterar datas/revisões.

        O cache permite calcular contagens globais sem repetir consultas a cada
        letra digitada na busca ou a cada clique de filtro.
        """
        dados = {}
        por_topico = {}
        for disciplina_id, nome in self._disciplinas:
            registros = self.repo.topicos(nome, self._concurso_id)
            dados[int(disciplina_id)] = registros
            for linha in registros:
                por_topico[int(linha.topico_id)] = (int(disciplina_id), nome)
        self._topicos_por_disciplina = dados
        self._disciplina_por_topico = por_topico
        # Mesmo motor de continuidade usado pelo estudo: ciclos ativos do perfil.
        # Consulta agregada, sem inferir progresso a partir da fração Questões.
        self._ciclos_ativos = self.repo.ciclos_em_andamento(self._concurso_id)

    def _modo_global(self):
        return self._escopo_todas

    def _modo_resumo(self):
        return self._escopo_todas and self._situacao_ativa == 'resumo'

    def _chave_scroll(self):
        if self._modo_resumo():
            return 'resumo'
        if self._modo_global():
            return ('global', self._situacao_ativa)
        return (self._id_disciplina, self._situacao_ativa)

    def _linhas_do_perfil(self):
        return [linha for linhas in self._topicos_por_disciplina.values()
                for linha in linhas]

    def _nome_disciplina_atual(self):
        for identidade, nome in self._disciplinas:
            if int(identidade) == self._id_disciplina:
                return nome
        return 'disciplina'

    def _texto_corresponde(self, linha, termo, global_mode):
        if not termo:
            return True
        if termo in linha.topico.casefold():
            return True
        return (global_mode and termo in self._disciplina_por_topico.get(
            int(linha.topico_id), (None, ''))[1].casefold())

    def _configurar_colunas(self):
        resumo = self._modo_resumo()
        global_mode = self._modo_global()
        cabecalhos = (self.COLS_RESUMO if resumo else
                      self.COLS_GLOBAIS if global_mode else self.COLS)
        self.tabela.setColumnCount(len(cabecalhos))
        self.tabela.setHorizontalHeaderLabels(cabecalhos)
        head = self.tabela.horizontalHeader()
        if resumo:
            head.setSectionResizeMode(0, QHeaderView.Stretch)
            for col, largura in {1:76, 2:120, 3:93, 4:69,
                                 5:69, 6:81, 7:66}.items():
                head.setSectionResizeMode(col, QHeaderView.Fixed)
                self.tabela.setColumnWidth(col, largura)
        elif global_mode:
            head.setSectionResizeMode(0, QHeaderView.Fixed)
            self.tabela.setColumnWidth(0, 142)
            head.setSectionResizeMode(1, QHeaderView.Stretch)
            larguras = {2:72, 3:146, 4:44, 5:80, 6:124, 7:107, 8:62}
            for col, largura in larguras.items():
                head.setSectionResizeMode(col, QHeaderView.Fixed)
                self.tabela.setColumnWidth(col, largura)
        else:
            head.setSectionResizeMode(0, QHeaderView.Stretch)
            larguras = {1:76, 2:158, 3:48, 4:83, 5:126, 6:117, 7:64}
            for col, largura in larguras.items():
                head.setSectionResizeMode(col, QHeaderView.Fixed)
                self.tabela.setColumnWidth(col, largura)

    def _atualizar_resumo(self):
        hoje = date.today()
        self._linhas = []
        self._resumo_linhas = []
        self.tabela.setRowCount(0)
        self._configurar_colunas()
        for disciplina_id, nome in self._disciplinas:
            registros = self._topicos_por_disciplina.get(int(disciplina_id), [])
            dados = _resumo_prazos(registros, hoje, self._ciclos_ativos)
            self._resumo_linhas.append((int(disciplina_id), nome, len(registros), dados))
        self.tabela.setRowCount(len(self._resumo_linhas))
        for indice, (ident, nome, total, dados) in enumerate(self._resumo_linhas):
            valores = (nome, str(total), str(dados['andamento']),
                       str(dados['atrasada']), str(dados['hoje']),
                       str(dados['proximos'] + dados['hoje']),
                       str(dados['sem_data']))
            for col, texto in enumerate(valores):
                item = QTableWidgetItem(texto)
                item.setData(Qt.UserRole, ident)
                if col > 0:
                    item.setTextAlignment(Qt.AlignCenter)
                self.tabela.setItem(indice, col, item)
            botao = QPushButton('Abrir')
            botao.setObjectName('gradeAbrirDiscreto')
            botao.setCursor(Qt.PointingHandCursor)
            botao.setAccessibleName('Abrir disciplina ' + nome)
            botao.clicked.connect(lambda _=False, did=ident: self._abrir_disciplina(did))
            self.tabela.setCellWidget(indice, 7, botao)
            self.tabela.setRowHeight(indice, 41)
        self._filtrar()

    def _atualizar_tabela(self):
        if not self._disciplinas or self._id_disciplina is None:
            self._linhas = []
            self.tabela.setRowCount(0)
            self.status.setText('Sem disciplinas no perfil')
            for botao in self._atalhos_prazos.values():
                botao.setEnabled(False)
            return

        if self._modo_resumo():
            self._atualizar_resumo()
            return

        selecionado = self._id_topico_selecionado()
        global_mode = self._modo_global()
        dados = (self._linhas_do_perfil() if global_mode else
                 self._topicos_por_disciplina.get(self._id_disciplina, []))
        hoje = date.today()
        if self._situacao_ativa not in ('todos', 'resumo'):
            # Renderização apenas das linhas do filtro, sem widgets ocultos.
            dados = [linha for linha in dados if _visivel_por_situacao(
                linha, self._situacao_ativa, hoje, self._ciclos_ativos)]
        self._resumo_linhas = []
        self._linhas = _ordenar_linhas(dados, self.ordenacao.currentData(), hoje)
        # Dados auxiliares usados somente na apresentação. Falhas de tendência
        # não devem bloquear a consulta de tópicos da Grade.
        ids_topicos = [linha.topico_id for linha in self._linhas]
        self._origens_agenda = {}
        for inicio in range(0, len(ids_topicos), 400):
            self._origens_agenda.update(self.repo.edicoes_agenda(
                self._concurso_id, ids_topicos[inicio:inicio + 400]))
        try:
            self._tendencias = {}
            for inicio in range(0, len(ids_topicos), 400):
                self._tendencias.update(self.repo.tendencias_recentes(
                    self._concurso_id, ids_topicos[inicio:inicio + 400]))
        except (AttributeError, RuntimeError, sqlite3.OperationalError):
            self._tendencias = {}

        self.tabela.setRowCount(0)
        self._configurar_colunas()
        self.tabela.setRowCount(len(self._linhas))
        deslocamento = 1 if global_mode else 0
        for row_idx, linha in enumerate(self._linhas):
            percentual = (f'{100 * linha.acertos / linha.tentativas:.1f}%'
                          if linha.tentativas else '—')
            diferenca = self._tendencias.get(linha.topico_id)
            tendencia = ((' ↑' if diferenca >= 5 else
                          ' ↓' if diferenca <= -5 else ' →')
                         if diferenca is not None else '')
            textos = [
                linha.topico, f'{linha.respondidas}/{linha.questoes_ativas}',
                f'{linha.acertos}/{linha.tentativas} · {percentual}{tendencia}',
                str(linha.revisoes), _mostrar_data(linha.ultima_revisao),
            ]
            if global_mode:
                textos.insert(0, self._disciplina_por_topico[int(linha.topico_id)][1])
            for col, txt in enumerate(textos):
                item = QTableWidgetItem(str(txt))
                item.setData(Qt.UserRole, int(linha.topico_id))
                if col == deslocamento and int(linha.topico_id) in self._ciclos_ativos:
                    item.setData(Qt.UserRole + 1, True)
                if col >= 1 + deslocamento:
                    item.setTextAlignment(Qt.AlignCenter)
                self.tabela.setItem(row_idx, col, item)
            registro_manual = self._origens_agenda.get(linha.topico_id, object())
            manual_atual = (linha.topico_id in self._origens_agenda and
                            registro_manual == linha.proxima_revisao)
            situacao = _situacao_revisao(linha.proxima_revisao, hoje)
            estado = {
                'atrasada': 'Revisão atrasada', 'hoje': 'Revisão vence hoje',
                'proximos': 'Revisão nos próximos 7 dias',
                'futura': 'Revisão futura', 'sem_data': 'Sem data agendada',
            }[situacao]
            data_btn = QPushButton(('✎ ' if manual_atual else '▣ ') +
                                   (_mostrar_data(linha.proxima_revisao)
                                    if linha.proxima_revisao else 'Sem data'))
            data_btn.setObjectName('gradeDataDiscreta')
            data_btn.setCursor(Qt.PointingHandCursor)
            data_btn.clicked.connect(lambda _=False, r=linha: self._editar_data(r))
            if situacao in ('atrasada', 'hoje', 'proximos'):
                fundo, texto, contorno = {
                    'atrasada': ('#482830', '#ffd0c8', '#b96566'),
                    'hoje': ('#473a2d', '#ffdfad', '#bf9252'),
                    'proximos': ('#0b3541', '#b2eee9', '#277f87'),
                }[situacao]
                data_btn.setStyleSheet(
                    'QPushButton {background:' + fundo + ';color:' + texto +
                    ';border:1px solid ' + contorno +
                    ';border-radius:5px;padding:1px 3px;font-weight:600;}'
                    'QPushButton:hover,QPushButton:focus {border-color:#f5dcb0;}')
            data_btn.setAccessibleName('Próxima revisão de ' + linha.topico +
                ': ' + estado + (', editada manualmente' if manual_atual else ''))
            self.tabela.setCellWidget(row_idx, 5 + deslocamento, data_btn)

            anotacao_btn = QPushButton('Ver nota' if linha.nota.strip() else '+ Anotar')
            anotacao_btn.setObjectName('gradeAnotacaoDiscreta')
            anotacao_btn.setCursor(Qt.PointingHandCursor)
            anotacao_btn.setAccessibleName('Editar anotação do tópico ' + linha.topico)
            anotacao_btn.clicked.connect(lambda _=False, r=linha: self._editar_nota(r))
            self.tabela.setCellWidget(row_idx, 6 + deslocamento, anotacao_btn)

            abrir_btn = QPushButton('Abrir')
            abrir_btn.setObjectName('gradeAbrirDiscreto')
            abrir_btn.setCursor(Qt.PointingHandCursor)
            abrir_btn.setAccessibleName('Abrir tópico ' + linha.topico)
            abrir_btn.clicked.connect(lambda _=False, r=linha: self._abrir(r))
            self.tabela.setCellWidget(row_idx, 7 + deslocamento, abrir_btn)
            self.tabela.setRowHeight(row_idx, 41)
        self._filtrar()
        if selecionado is not None:
            for idx, linha in enumerate(self._linhas):
                if linha.topico_id == selecionado and not self.tabela.isRowHidden(idx):
                    self.tabela.selectRow(idx)
                    break
        chave = self._chave_scroll()
        QTimer.singleShot(0, lambda key=chave: (
            self.tabela.verticalScrollBar().setValue(self._posicoes.get(key, 0))
            if self._chave_scroll() == key else None))

    def _id_topico_selecionado(self):
        indice = self.tabela.currentRow()
        if 0 <= indice < len(self._linhas):
            return self._linhas[indice].topico_id
        return None

    def _reordenar(self):
        if self._carregando or self._id_disciplina is None:
            return
        self._posicoes[self._chave_scroll()] = self.tabela.verticalScrollBar().value()
        self._atualizar_tabela()

    def _filtro_rapido(self, valor):
        if valor not in self._atalhos_prazos:
            return
        proximo = ('resumo' if self._escopo_todas and valor == 'todos'
                   else valor)
        if proximo == self._situacao_ativa:
            return
        self._posicoes[self._chave_scroll()] = self.tabela.verticalScrollBar().value()
        self._situacao_ativa = proximo
        self._atualizar_placeholder()
        self._atualizar_tabela()

    def _filtrar(self):
        termo = self.busca.text().casefold().strip()
        hoje = date.today()
        global_mode = self._modo_global()
        resumo = self._modo_resumo()
        dados = (self._linhas_do_perfil() if global_mode else
                 self._topicos_por_disciplina.get(self._id_disciplina, []))
        # A busca em Resumo filtra nomes de disciplinas; em outras vistas
        # filtra tópicos e, na vista global, também nomes das disciplinas.
        if resumo:
            busca_ids = {ident for ident, nome in self._disciplinas
                         if not termo or termo in nome.casefold()}
            candidatos = [linha for linha in dados
                          if self._disciplina_por_topico.get(
                              int(linha.topico_id), (None, ''))[0] in busca_ids]
        else:
            candidatos = [linha for linha in dados
                          if self._texto_corresponde(linha, termo, global_mode)]
        contagens = _resumo_prazos(candidatos, hoje, self._ciclos_ativos)
        total = len(candidatos)
        visiveis = 0
        if resumo:
            for indice, (did, nome, _n, _c) in enumerate(self._resumo_linhas):
                oculta = bool(termo and termo not in nome.casefold())
                self.tabela.setRowHidden(indice, oculta)
                visiveis += not oculta
        else:
            for indice, linha in enumerate(self._linhas):
                oculta = (not self._texto_corresponde(linha, termo, global_mode)
                          or not _visivel_por_situacao(
                              linha, self._situacao_ativa, hoje, self._ciclos_ativos))
                self.tabela.setRowHidden(indice, oculta)
                visiveis += not oculta

        nomes = {'todos': 'Todos', 'resumo': 'Resumo',
                 'andamento': 'Em andamento', 'atrasada': 'Atrasadas',
                 'hoje': 'Hoje', 'proximos': '7 dias', 'sem_data': 'Sem data'}
        for valor, botao in self._atalhos_prazos.items():
            if valor == 'todos':
                rotulo = 'Resumo' if global_mode else 'Todos'
                contagem = None if global_mode else total
                ativo = resumo or (not global_mode and self._situacao_ativa == 'todos')
            else:
                rotulo = nomes[valor]
                contagem = (contagens[valor] +
                            (contagens['hoje'] if valor == 'proximos' else 0))
                ativo = self._situacao_ativa == valor
            botao.set_dados(rotulo, contagem, ativo)
            botao.setEnabled(True)
            alcance = ('todas as disciplinas do perfil' if global_mode else
                       self._nome_disciplina_atual())
            botao.setAccessibleName(f'{rotulo}: {alcance}' +
                (f', {contagem} tópicos' if contagem is not None else
                 ', resumo por disciplina'))
        if resumo:
            n = visiveis
            self.status.setText(f'{n} disciplina' + ('s' if n != 1 else ''))
        else:
            n = visiveis
            self.status.setText(f'{n} resultado' + ('s' if n != 1 else ''))

    def _duplo_clique(self, indice, coluna):
        if self._modo_resumo():
            if 0 <= indice < len(self._resumo_linhas):
                self._abrir_disciplina(self._resumo_linhas[indice][0])
            return
        # O índice pertence à ordem visual da Grade; a lista _linhas é ordenada
        # antecipadamente e o QTableWidget nunca usa sorting interno.
        if indice < 0 or indice >= len(self._linhas):
            return
        linha = self._linhas[indice]
        if coluna == 5 + int(self._modo_global()):
            self._editar_data(linha)
        elif coluna == 6 + int(self._modo_global()):
            self._editar_nota(linha)
        else:
            self._abrir(linha)

    def _editar_nota(self, linha):
        texto, ok = QInputDialog.getMultiLineText(
            self, f'Anotação — {linha.topico}',
            f'Até {NOTA_MAX} caracteres. Anotação vinculada ao perfil e tópico:',
            linha.nota,
        )
        if not ok:
            return
        if len(texto.strip()) > NOTA_MAX:
            QMessageBox.warning(self, 'Anotação longa', f'O limite é de {NOTA_MAX} caracteres.')
            return
        try:
            self.repo.salvar_nota(self._concurso_id, linha.topico_id, texto)
            self._posicoes[self._chave_scroll()] = self.tabela.verticalScrollBar().value()
            self.atualizar()
        except Exception as exc:
            QMessageBox.warning(self, 'Anotação não salva', str(exc))

    def _editar_data(self, linha):
        dlg = QDialog(self)
        dlg.setWindowTitle(f'Próxima revisão — {linha.topico}')
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel('Alterar a próxima revisão na agenda oficial:'))
        editar = QDateEdit(dlg)
        editar.setCalendarPopup(True)
        editar.setDisplayFormat('dd/MM/yyyy')
        try:
            editar.setDate(QDate.fromString(str(linha.proxima_revisao)[:10], 'yyyy-MM-dd'))
        except (TypeError, ValueError):
            editar.setDate(QDate.currentDate())
        if not editar.date().isValid():
            editar.setDate(QDate.currentDate())
        lay.addWidget(editar)
        limpar = QCheckBox('Remover data agendada')
        limpar.setChecked(False)
        editar.setEnabled(True)
        limpar.toggled.connect(lambda checked: editar.setEnabled(not checked))
        lay.addWidget(limpar)
        lay.addWidget(QLabel('A mudança não contabiliza revisão realizada.'))
        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botoes.accepted.connect(dlg.accept)
        botoes.rejected.connect(dlg.reject)
        lay.addWidget(botoes)
        if dlg.exec() != QDialog.Accepted:
            return
        nova = None if limpar.isChecked() else editar.date().toString('yyyy-MM-dd')
        try:
            mudou = self.repo.atualizar_data_manual(self._concurso_id, linha.topico_id, nova)
            if mudou:
                self.janela.notificar_dados_alterados('revisoes')
            self._posicoes[self._chave_scroll()] = self.tabela.verticalScrollBar().value()
            self.atualizar()
        except Exception as exc:
            QMessageBox.warning(self, 'Data não alterada', str(exc))

    def _abrir(self, linha):
        self._posicoes[self._chave_scroll()] = self.tabela.verticalScrollBar().value()
        try:
            # Reaproveita exatamente a Central Integrada (botão Abrir de Disciplinas).
            self.abrir_topico(linha.topico_id, linha.topico)
        except Exception as exc:
            QMessageBox.warning(self, 'Abrir tópico',
                                f'Não foi possível abrir o tópico:\n{exc}')
        finally:
            self.atualizar()


def instalar_grade_em_iniciar_estudo(janela):
    """Liga o cartão Estudo Manual à Grade já existente, sem duplicar atalhos.

    A página continua sendo criada somente no primeiro acesso. A configuração
    dos tópicos, a agenda, o banco e a navegação da Central Integrada não mudam.
    """
    painel = getattr(janela.tela_inicial, '_h36_painel', None)
    if painel is None:
        raise RuntimeError('Grade: tela Iniciar Estudo H36 indisponível')
    if getattr(painel, '_grade_botao_v1', None) is not None:
        return painel._grade_botao_v1
    botao = getattr(painel, 'cartao_manual', None)
    if botao is None:
        raise RuntimeError('Grade: cartão Estudo Manual não encontrado no H36')

    def abrir():
        pagina = getattr(janela, 'tela_grade_estudos_v1', None)
        if pagina is None:
            pagina = PaginaGradeEstudos(
                janela, voltar=janela.voltar_inicio,
                abrir_topico=janela.abrir_central_integrada_topico,
            )
            janela.tela_grade_estudos_v1 = pagina
            janela.telas.addWidget(pagina)
        # O showEvent realiza a atualização, sem duplicar consultas.
        janela.telas.setCurrentWidget(pagina)

    botao.clicked.connect(abrir)
    botao.setAccessibleName('Estudo Manual — abrir Grade de Estudos e Revisões')
    botao.setEnabled(True)
    painel._grade_botao_v1 = botao
    return botao
