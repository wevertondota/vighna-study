"""UI Qt reutilizável para tempo efetivo em Estatísticas e Histórico V2.

Nenhuma escrita em SQLite; consulta os tempos registrados nas duas fontes.
"""
from __future__ import annotations

from datetime import date, timedelta

from PySide6.QtCore import Qt, QDate, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QComboBox, QDateEdit, QFrame, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QScrollArea, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from ui.tempo_baterias_v1 import formatar_duracao
from ui.tempo_historico_dados_v1 import (
    consultar_resumo, consultar_serie, formatar_variacao, FonteTempoIndisponivel,
)


def _menos_meses(data, meses):
    novo_mes = data.year * 12 + (data.month-1) - meses
    return date(novo_mes // 12, novo_mes % 12 + 1, 1)


class GraficoTempoEfetivo(QWidget):
    """Barras sem QtCharts ou dependências extras, compatível com PySide6."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._linhas = []
        self._claro = False
        self.setMinimumHeight(190)
        self.setToolTip('Tempo efetivamente estudado, após desconto de pausas')

    def definir(self, linhas, claro=False):
        self._linhas = list(linhas)
        self._claro = bool(claro)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        fg = QColor('#304d61' if self._claro else '#b9d5e6')
        grade = QColor('#dce7ee' if self._claro else '#27465b')
        barra = QColor('#007fa5' if self._claro else '#3ac8ed')
        manual = QColor('#9d6500' if self._claro else '#ddb360')
        vazio = QColor('#b0c5ce' if self._claro else '#426477')
        rect = self.rect().adjusted(42, 12, -12, -27)
        if rect.width() < 80 or rect.height() < 45:
            return
        p.setPen(QPen(grade, 1))
        for nivel in range(5):
            y = rect.bottom() - (rect.height() * nivel / 4)
            p.drawLine(rect.left(), int(y), rect.right(), int(y))
        p.setPen(fg)
        if not self._linhas:
            p.drawText(rect, Qt.AlignCenter, 'Nenhum período disponível')
            return
        limite = max((r['liquido'] for r in self._linhas), default=0)
        if limite <= 0:
            limite = 3600
        valores = [(r['liquido']/3600) for r in self._linhas]
        total = len(valores)
        espaco = rect.width()/max(1,total)
        largura = max(2.0,min(42.0,espaco*0.60))
        fonte = QFont(self.font())
        fonte.setPointSize(8)
        p.setFont(fonte)
        passo = max(1,(total+6)//7)
        for indice, (linha, h) in enumerate(zip(self._linhas, valores)):
            x = rect.left() + indice*espaco + (espaco-largura)/2
            altura = rect.height() * (linha['liquido']/limite)
            if linha['tem_registro'] and linha['liquido'] == 0:
                altura = 2.0
            if altura > 0:
                p.setPen(Qt.NoPen)
                a = altura * linha.get('liquido_baterias', linha['liquido']) / max(1, linha['liquido'])
                b = altura - a
                if a > 0:
                    p.setBrush(barra); p.drawRect(QRectF(x,rect.bottom()-a,largura,a))
                if b > 0:
                    p.setBrush(manual if linha.get('liquido_manual') else vazio)
                    p.drawRect(QRectF(x,rect.bottom()-altura,largura,b))
            if indice % passo == 0 or indice == total-1:
                p.setPen(fg)
                rotulo = linha['rotulo'].split(' – ')[0]
                p.drawText(QRectF(x-13,rect.bottom()+5,max(espaco,largura+26),17),Qt.AlignHCenter|Qt.AlignVCenter,rotulo[:10])
        p.setPen(fg)
        for nivel in range(5):
            y = rect.bottom() - rect.height()*nivel/4
            p.drawText(QRectF(0,y-8,38,16),Qt.AlignRight|Qt.AlignVCenter,
                       f'{limite/3600*nivel/4:.1f}h')


class PainelTempoEfetivo(QWidget):
    """Exibidor independente: modo estatísticas (gráfico) ou histórico (tabela)."""
    def __init__(self, caminho_banco, *, concurso_id=None, modo='estatisticas', tema='futurista', parent=None):
        super().__init__(parent)
        self.caminho_banco = caminho_banco
        self.concurso_id = int(concurso_id) if concurso_id is not None else None
        self.modo = modo
        self._tema = tema
        self.setObjectName('tempoEfetivoWidget')
        raiz_externa = QVBoxLayout(self)
        raiz_externa.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea(self)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        conteudo = QWidget(scroll)
        conteudo.setObjectName('tempoConteudo')
        raiz = QVBoxLayout(conteudo)
        raiz.setContentsMargins(9, 10, 9, 10)
        raiz.setSpacing(10)
        scroll.setWidget(conteudo)
        raiz_externa.addWidget(scroll)
        titulo = QLabel('Tempo efetivo de estudo')
        titulo.setObjectName('tempoTitulo')
        raiz.addWidget(titulo)
        explicacao = QLabel('Tempo efetivo consolidado: baterias concluídas (ciano) e revisões manuais (dourado). Use o filtro de origem para consultar cada fonte.')
        explicacao.setWordWrap(True)
        explicacao.setObjectName('tempoExplicacao')
        raiz.addWidget(explicacao)

        self._resumos = {}
        metricas = QGridLayout()
        metricas.setHorizontalSpacing(8)
        metricas.setVerticalSpacing(8)
        for i, (chave, rotulo) in enumerate((
            ('semana','Esta semana'), ('mes','Este mês'), ('ano','Neste ano'),
            ('total','Total acumulado'), ('media_dia_ativo','Média por dia ativo'),
            ('comparacao','Comparação mensal'),
        )):
            frame = QFrame()
            frame.setObjectName('tempoCard')
            lay = QVBoxLayout(frame)
            lay.setContentsMargins(11,8,11,8)
            sub = QLabel(rotulo)
            sub.setObjectName('tempoRotulo')
            valor = QLabel('—')
            valor.setObjectName('tempoValor')
            valor.setWordWrap(True)
            lay.addWidget(sub)
            lay.addWidget(valor)
            self._resumos[chave] = valor
            metricas.addWidget(frame, i//3, i%3)
        raiz.addLayout(metricas)

        filtros = QHBoxLayout()
        filtros.setSpacing(8)
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(['7 dias','30 dias','90 dias','365 dias','12 meses','Completo','Personalizado'])
        self.combo_periodo.setCurrentText('30 dias' if modo == 'estatisticas' else '90 dias')
        self.combo_grupo = QComboBox()
        self.combo_grupo.addItems(['Dia','Semana','Mês','Ano'])
        self.combo_grupo.setCurrentText('Dia' if modo == 'estatisticas' else 'Semana')
        self.combo_escopo = QComboBox()
        self.combo_escopo.addItems(['Todos os perfis','Perfil atual'])
        self.combo_escopo.setCurrentText('Perfil atual' if modo=='historico' else 'Todos os perfis')
        self.combo_escopo.setEnabled(self.concurso_id is not None)
        self.data_inicio = QDateEdit(QDate.currentDate().addDays(-29))
        self.data_fim = QDateEdit(QDate.currentDate())
        for controle in (self.data_inicio,self.data_fim):
            controle.setDisplayFormat('dd/MM/yyyy')
            controle.setCalendarPopup(True)
            controle.setMaximumDate(QDate.currentDate())
        filtros.addWidget(QLabel('Período'))
        filtros.addWidget(self.combo_periodo)
        filtros.addWidget(QLabel('Agrupar'))
        filtros.addWidget(self.combo_grupo)
        filtros.addWidget(self.combo_escopo)
        self.combo_origem = QComboBox()
        self.combo_origem.addItems(["Todas as origens", "Baterias", "Manual"])
        filtros.addWidget(self.combo_origem)
        self.botao = QPushButton('Consultar')
        filtros.addWidget(self.botao)
        raiz.addLayout(filtros)
        datas = QHBoxLayout()
        self.datas_label = QLabel('De / até')
        datas.addWidget(self.datas_label)
        datas.addWidget(self.data_inicio)
        datas.addWidget(self.data_fim)
        datas.addStretch()
        raiz.addLayout(datas)
        self._datas = (self.datas_label,self.data_inicio,self.data_fim)
        self._mostrar_datas()

        self.grafico = GraficoTempoEfetivo(self)
        raiz.addWidget(self.grafico)
        self.tabela = QTableWidget(0, 7)
        self.tabela.setHorizontalHeaderLabels(['Período','Tempo efetivo','Tempo baterias','Tempo manual','Pausas','Baterias','Registro'])
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for col in (1,2,3,4,5,6):
            self.tabela.horizontalHeader().setSectionResizeMode(col,QHeaderView.ResizeToContents)
        self.tabela.setMinimumHeight(190 if modo=='estatisticas' else 265)
        raiz.addWidget(self.tabela,1)
        self.status = QLabel('—')
        self.status.setObjectName('tempoObservacao')
        self.status.setWordWrap(True)
        raiz.addWidget(self.status)
        for controle in (self.combo_grupo,self.combo_escopo,self.combo_origem):
            controle.currentIndexChanged.connect(self.atualizar)
        self.combo_periodo.currentTextChanged.connect(self._periodo_alterado)
        self.botao.clicked.connect(self.atualizar)
        self.aplicar_tema(tema)

    def definir_concurso(self, concurso_id):
        novo = int(concurso_id) if concurso_id is not None else None
        self.concurso_id = novo
        self.combo_escopo.setEnabled(novo is not None)

    def _periodo_alterado(self, *_):
        periodo = self.combo_periodo.currentText()
        self._mostrar_datas()
        if periodo == '12 meses':
            self.combo_grupo.setCurrentText('Mês')
        elif periodo == 'Completo':
            self.combo_grupo.setCurrentText('Mês')
        elif periodo == '7 dias':
            self.combo_grupo.setCurrentText('Dia')
        if periodo != 'Personalizado':
            self.atualizar()

    def _mostrar_datas(self):
        visivel = self.combo_periodo.currentText()=='Personalizado'
        for widget in self._datas:
            widget.setVisible(visivel)

    def aplicar_tema(self, tema):
        self._tema = tema
        claro = 'claro' in str(tema).lower() and 'escuro' not in str(tema).lower()
        fundo = '#f7fafc' if claro else '#071b2b'
        painel = '#ffffff' if claro else '#0c2b41'
        borda = '#9ec8d8' if claro else '#256589'
        texto = '#18384a' if claro else '#e4f4ff'
        fraco = '#486b7e' if claro else '#b1ccdf'
        self.setStyleSheet(f'''
            QWidget#tempoEfetivoWidget,QWidget#tempoConteudo,QScrollArea {{background:{fundo};color:{texto};}}
            QFrame#tempoCard {{background:{painel};border:1px solid {borda};border-radius:8px;}}
            QLabel {{color:{texto};}}
            QLabel#tempoTitulo {{font-size:18px;font-weight:700;}}
            QLabel#tempoExplicacao,QLabel#tempoRotulo,QLabel#tempoObservacao {{color:{fraco};font-size:11px;}}
            QLabel#tempoValor {{font-size:18px;font-weight:700;}}
            QComboBox,QDateEdit,QPushButton {{background:{painel};color:{texto};border:1px solid {borda};
                padding:5px;border-radius:5px;}}
            QTableWidget {{background:{painel};alternate-background-color:{fundo};color:{texto};
                gridline-color:{borda};}}
            QHeaderView::section {{background:{painel};color:{texto};border:1px solid {borda};padding:4px;}}
        ''')
        self.grafico._claro = claro
        self.grafico.update()

    def _intervalo(self, hoje, primeiro):
        periodo = self.combo_periodo.currentText()
        if periodo == '7 dias':
            return hoje-timedelta(days=6), hoje
        if periodo == '30 dias':
            return hoje-timedelta(days=29), hoje
        if periodo == '90 dias':
            return hoje-timedelta(days=89), hoje
        if periodo == '365 dias':
            return hoje-timedelta(days=364), hoje
        if periodo == '12 meses':
            return _menos_meses(hoje,11), hoje
        if periodo == 'Completo':
            return date.fromisoformat(primeiro) if primeiro else hoje, hoje
        a = self.data_inicio.date().toPython()
        b = self.data_fim.date().toPython()
        if a > b or b > hoje:
            raise ValueError('O intervalo personalizado deve terminar até hoje e ter datas em ordem.')
        return a, b

    def atualizar(self, *_):
        try:
            hoje = date.today()
            perfil = self.concurso_id if self.combo_escopo.currentText()=='Perfil atual' else None
            origem = ("todos","baterias","manual")[self.combo_origem.currentIndex()]
            resumo = consultar_resumo(self.caminho_banco, hoje=hoje, concurso_id=perfil, origem=origem)
            inicio, fim = self._intervalo(hoje, resumo['primeiro_registro'])
            grupo = {'Dia':'dia','Semana':'semana','Mês':'mes','Ano':'ano'}[self.combo_grupo.currentText()]
            serie = consultar_serie(self.caminho_banco, inicio=inicio, fim=fim,agrupamento=grupo,concurso_id=perfil,origem=origem)
            textos = {chave:(formatar_duracao(resumo[chave]) if resumo['primeiro_registro'] else '—') for chave in ('semana','mes','ano','total','media_dia_ativo')}
            textos['comparacao'] = formatar_variacao(resumo['mes'],resumo['mes_anterior']) if resumo['primeiro_registro'] else '—'
            for chave, texto in textos.items():
                self._resumos[chave].setText(texto)
            linhas = serie['linhas']
            self.grafico.definir(linhas[-36:], 'claro' in str(self._tema).lower())
            self.tabela.setUpdatesEnabled(False)
            try:
                self.tabela.setRowCount(len(linhas))
                for i,r in enumerate(linhas):
                    valores = [r['rotulo'],
                               formatar_duracao(r['liquido']) if r['tem_registro'] else '—',
                               formatar_duracao(r['liquido_baterias']) if r['tem_registro'] else '—',
                               formatar_duracao(r['liquido_manual']) if r['tem_registro'] else '—',
                               formatar_duracao(r['pausa']) if r['tem_registro'] else '—',
                               str(r['baterias']) if r['tem_registro'] else '—',
                               'Registrado' if r['tem_registro'] else 'Sem registro']
                    for j,valor in enumerate(valores):
                        item=QTableWidgetItem(valor)
                        if j>0: item.setTextAlignment(Qt.AlignCenter)
                        self.tabela.setItem(i,j,item)
            finally:
                self.tabela.setUpdatesEnabled(True)
            self.status.setText(
                f'Total do intervalo: {formatar_duracao(serie["total_segundos"])}  •  '
                f'{serie["dias_registrados"]} dia(s) com registro  •  '
                f'Primeiro registro: {date.fromisoformat(serie["primeiro_registro"]):%d/%m/%Y}'
                if serie['primeiro_registro'] else
                'Não há tempo efetivo persistido para o escopo escolhido. Registros anteriores à ativação do contador não podem ser recuperados com precisão.'
            )
        except (FonteTempoIndisponivel,ValueError, OSError) as erro:
            self.tabela.setRowCount(0)
            self.grafico.definir([])
            for valor in self._resumos.values(): valor.setText('—')
            self.status.setText(str(erro))
        except Exception:
            self.tabela.setRowCount(0)
            for valor in self._resumos.values(): valor.setText('—')
            self.grafico.definir([])
            self.status.setText('Falha na consulta. Confira a integridade do banco em um clone antes de tentar novamente.')
