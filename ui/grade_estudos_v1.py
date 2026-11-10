"""Grade de Estudos V1 — painel interno do Iniciar estudo.

Somente aberto pelo botão de acesso. Reutiliza o cadastro e a Central
Integrada de Tópicos; nunca replica ou reinicia o motor de revisões.
"""
from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QLineEdit, QTabBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QSizePolicy, QMessageBox, QInputDialog, QDialog,
    QDialogButtonBox, QDateEdit, QCheckBox,
)

from ui.grade_estudos_dados_v1 import RepositorioGrade, NOTA_MAX


def _mostrar_data(texto):
    if not texto:
        return '—'
    try:
        return date.fromisoformat(str(texto)[:10]).strftime('%d/%m/%Y')
    except ValueError:
        return str(texto)


class PaginaGradeEstudos(QWidget):
    """Uma tabela reaproveitada entre as abas evita criar N tabelas grandes."""
    COLS = ['Tópico', 'Questões', 'Acertos', '% acerto', 'Rev.',
            'Última', 'Próxima revisão', 'Anotação', 'Ação']

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
        self._concurso_id = None
        self._id_disciplina = None
        self._posicoes = {}
        self._carregando = False
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(25, 18, 25, 16)
        raiz.setSpacing(14)

        cab = QHBoxLayout()
        voltar_btn = QPushButton('← Iniciar estudo')
        voltar_btn.setObjectName('gradeVoltarV1')
        voltar_btn.setCursor(Qt.PointingHandCursor)
        voltar_btn.clicked.connect(self.voltar)
        cab.addWidget(voltar_btn)
        titulo = QLabel('Grade de Estudos e Revisões')
        titulo.setObjectName('gradeTituloV1')
        cab.addWidget(titulo, 1)
        self.perfil_label = QLabel('')
        self.perfil_label.setObjectName('gradePerfilV1')
        cab.addWidget(self.perfil_label)
        raiz.addLayout(cab)

        desc = QLabel('Organize tópicos, ajuste datas e abra a revisão pelo mesmo acesso de Disciplinas.')
        desc.setObjectName('gradeSubtituloV1')
        raiz.addWidget(desc)

        filtros = QHBoxLayout()
        self.disciplinas_label = QLabel('Disciplinas')
        self.disciplinas_label.setObjectName('gradeDisciplinasLabelV1')
        filtros.addWidget(self.disciplinas_label)
        self.abas = QTabBar()
        self.abas.setObjectName('gradeAbasV1')
        self.abas.setExpanding(False)
        self.abas.setUsesScrollButtons(True)
        self.abas.currentChanged.connect(self._ao_mudar_aba)
        filtros.addWidget(self.abas, 1)
        raiz.addLayout(filtros)

        linha_acoes = QHBoxLayout()
        self.busca = QLineEdit()
        self.busca.setObjectName('gradeBuscaV1')
        self.busca.setPlaceholderText('Filtrar tópicos...')
        self.busca.setClearButtonEnabled(True)
        self.busca.textChanged.connect(lambda _texto: self._filtrar())
        linha_acoes.addWidget(self.busca, 1)
        self.status = QLabel('')
        self.status.setObjectName('gradeStatusV1')
        linha_acoes.addWidget(self.status)
        atualizar = QPushButton('Atualizar')
        atualizar.clicked.connect(self.atualizar)
        atualizar.setCursor(Qt.PointingHandCursor)
        linha_acoes.addWidget(atualizar)
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
        head = self.tabela.horizontalHeader()
        head.setSectionResizeMode(0, QHeaderView.Stretch)
        for c, width in {1:82, 2:94, 3:74, 4:56, 5:86, 6:128, 7:150, 8:83}.items():
            head.setSectionResizeMode(c, QHeaderView.Fixed)
            self.tabela.setColumnWidth(c, width)
        self.tabela.cellDoubleClicked.connect(self._duplo_clique)
        raiz.addWidget(self.tabela, 1)
        aviso = QLabel('O % de acerto considera apenas tentativas registradas no perfil. '
                       'Datas editadas atualizam o Calendário, sem registrar revisão executada. '
                       'A agenda automática continua seguindo o ciclo integral.')
        aviso.setObjectName('gradeAvisoV1')
        aviso.setWordWrap(True)
        raiz.addWidget(aviso)
        self.setStyleSheet('''
            QWidget#gradeEstudosV1 { background-color:#061a2b; color:#e7f4ff; }
            QLabel#gradeTituloV1 {font-size:24px; font-weight:700; color:#f5fbff;}
            QLabel#gradeSubtituloV1, QLabel#gradeAvisoV1 {color:#abc7d9; font-size:12px;}
            QLabel#gradePerfilV1, QLabel#gradeStatusV1 {color:#79c9e8;}
            QLabel#gradeDisciplinasLabelV1 {color:#a8cce1; font-size:12px;}
            QTabBar#gradeAbasV1::tab {padding:9px 15px; background:#0d3048;
                border:1px solid #1e5976; border-radius:6px; margin:1px; color:#cfebff;}
            QTabBar#gradeAbasV1::tab:selected {background:#07557c; border-color:#16c6e9; color:white;}
            QTableWidget#gradeTabelaV1 {background:#071e32; alternate-background-color:#0d283e;
                color:#e8f5ff; border:1px solid #1b4c67; gridline-color:transparent;
                selection-background-color:#14577c;}
            QHeaderView::section {background:#12354b; color:#ccebf7; border:0;
                border-bottom:1px solid #1c688b; padding:7px;}
            QPushButton {background:#0c344f; color:#e8f7ff; border:1px solid #20779b;
                border-radius:7px; min-height:27px; padding:2px 10px;}
            QPushButton:hover {background:#07587c; border-color:#17c1e4;}
            QLineEdit {background:#071e32; border:1px solid #24678b; border-radius:6px;
                color:white; min-height:30px; padding:2px 9px;}
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
            if cid != self._concurso_id:
                # Uma mesma disciplina pode existir em dois perfis, mas o
                # estado da navegação não deve migrar entre eles.
                self._posicoes.clear()
            elif self._id_disciplina is not None:
                self._posicoes[self._id_disciplina] = (
                    self.tabela.verticalScrollBar().value()
                )
            antigo = self._id_disciplina if cid == self._concurso_id else None
            self._concurso_id = cid
            self.perfil_label.setText(f'Perfil: {concurso[1]}')
            disciplinas = self.repo.disciplinas(cid)
            self._disciplinas = disciplinas
            self.abas.blockSignals(True)
            while self.abas.count():
                self.abas.removeTab(self.abas.count() - 1)
            selecionada = 0
            for i, (ident, nome) in enumerate(disciplinas):
                self.abas.addTab(nome)
                self.abas.setTabData(i, int(ident))
                if antigo == ident:
                    selecionada = i
            self.abas.setCurrentIndex(selecionada if disciplinas else -1)
            self.abas.blockSignals(False)
            self._id_disciplina = int(disciplinas[selecionada][0]) if disciplinas else None
            self._atualizar_tabela()
        except Exception as exc:
            QMessageBox.warning(self, 'Grade de Estudos', f'Não foi possível atualizar a grade:\n{exc}')
        finally:
            self._carregando = False

    def _ao_mudar_aba(self, indice):
        if self._carregando or indice < 0 or indice >= len(self._disciplinas):
            return
        if self._id_disciplina is not None:
            self._posicoes[self._id_disciplina] = self.tabela.verticalScrollBar().value()
        self._id_disciplina = self._disciplinas[indice][0]
        self._atualizar_tabela()

    def _atualizar_tabela(self):
        indice = self.abas.currentIndex()
        if indice < 0 or indice >= len(self._disciplinas):
            self._linhas = []
            self.tabela.setRowCount(0)
            self.status.setText('Sem disciplinas no perfil')
            return
        nome = self._disciplinas[indice][1]
        self._linhas = self.repo.topicos(nome, self._concurso_id)
        self.tabela.setRowCount(0)
        self.tabela.setRowCount(len(self._linhas))
        hoje = date.today().isoformat()
        for row_idx, linha in enumerate(self._linhas):
            texts = [
                linha.topico,
                f'{linha.respondidas}/{linha.questoes_ativas}',
                f'{linha.acertos}/{linha.tentativas}',
                # Percentual de ACERTOS: nunca confundir a nota de domínio
                # importada/derivada com a taxa de respostas corretas.
                (f'{100*linha.acertos/linha.tentativas:.1f}%' if linha.tentativas
                 else '—'),
                str(linha.revisoes), _mostrar_data(linha.ultima_revisao),
            ]
            for col, txt in enumerate(texts):
                item = QTableWidgetItem(str(txt))
                item.setToolTip(
                    ('Taxa de acertos nas tentativas deste perfil; '
                     'sem respostas registradas não há percentual.'
                     if col == 3 else str(txt))
                )
                item.setData(Qt.UserRole, int(linha.topico_id))
                if col > 0:
                    item.setTextAlignment(Qt.AlignCenter)
                self.tabela.setItem(row_idx, col, item)
            data_btn = QPushButton('✎ '+_mostrar_data(linha.proxima_revisao))
            data_btn.setToolTip('Editar a data da agenda, sem registrar revisão')
            data_btn.clicked.connect(lambda _=False, r=linha: self._editar_data(r))
            if linha.proxima_revisao and str(linha.proxima_revisao)[:10] < hoje:
                data_btn.setStyleSheet('color:#ffd89c; border-color:#b17645;')
            self.tabela.setCellWidget(row_idx, 6, data_btn)
            # O botão não pode truncar a nota duas vezes (string e Qt).
            # A anotação integral continua acessível via tooltip e editor.
            nota_resumo = (linha.nota[:13].rstrip() + '…'
                           if len(linha.nota) > 13 else linha.nota)
            anotacao_btn = QPushButton(('✎ ' + nota_resumo) if linha.nota else '+ Anotar')
            anotacao_btn.setToolTip(
                'Clique para ler ou editar a anotação completa:\n' + linha.nota
                if linha.nota else 'Adicionar anotação curta'
            )
            anotacao_btn.setAccessibleName('Editar anotação do tópico ' + linha.topico)
            anotacao_btn.clicked.connect(lambda _=False, r=linha: self._editar_nota(r))
            self.tabela.setCellWidget(row_idx, 7, anotacao_btn)
            abrir_btn = QPushButton('Abrir')
            abrir_btn.setToolTip('Abrir a Central Integrada deste tópico (mesma ação de Disciplinas)')
            abrir_btn.clicked.connect(lambda _=False, r=linha: self._abrir(r))
            self.tabela.setCellWidget(row_idx, 8, abrir_btn)
            self.tabela.setRowHeight(row_idx, 41)
        self._filtrar()
        disciplina_id = self._id_disciplina
        QTimer.singleShot(0, lambda did=disciplina_id: (
            self.tabela.verticalScrollBar().setValue(self._posicoes.get(did, 0))
            if self._id_disciplina == did else None
        ))

    def _filtrar(self):
        termo = self.busca.text().casefold().strip()
        visiveis = 0
        for i, row in enumerate(self._linhas):
            oculta = bool(termo and termo not in row.topico.casefold())
            self.tabela.setRowHidden(i, oculta)
            visiveis += not oculta
        self.status.setText(
            f'{visiveis}/{len(self._linhas)} tópicos' if termo
            else f'{len(self._linhas)} tópicos'
        )

    def _duplo_clique(self, indice, coluna):
        if indice < 0 or indice >= len(self._linhas):
            return
        linha = self._linhas[indice]
        if coluna == 6:
            self._editar_data(linha)
        elif coluna == 7:
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
            self._posicoes[self._id_disciplina] = self.tabela.verticalScrollBar().value()
            self._atualizar_tabela()
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
            self._posicoes[self._id_disciplina] = self.tabela.verticalScrollBar().value()
            self._atualizar_tabela()
        except Exception as exc:
            QMessageBox.warning(self, 'Data não alterada', str(exc))

    def _abrir(self, linha):
        self._posicoes[self._id_disciplina] = self.tabela.verticalScrollBar().value()
        try:
            # Reaproveita exatamente a Central Integrada (botão Abrir de Disciplinas).
            self.abrir_topico(linha.topico_id, linha.topico)
        except Exception as exc:
            QMessageBox.warning(self, 'Abrir tópico',
                                f'Não foi possível abrir o tópico:\n{exc}')
        finally:
            self.atualizar()


def instalar_grade_em_iniciar_estudo(janela):
    """Apenas um botão adicional; a tela nova é construída no primeiro clique."""
    painel = getattr(janela.tela_inicial, '_h36_painel', None)
    if painel is None:
        raise RuntimeError('Grade: tela Iniciar estudo H36 indisponível')
    if getattr(painel, '_grade_botao_v1', None) is not None:
        return painel._grade_botao_v1

    linha = QHBoxLayout()
    linha.setContentsMargins(0, 12, 0, 0)
    linha.addStretch(1)
    botao = QPushButton('▦  Grade de Estudos e Revisões  →')
    botao.setObjectName('abrirGradeEstudosV1')
    botao.setFixedHeight(42)
    botao.setMinimumWidth(290)
    botao.setMaximumWidth(410)
    botao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    botao.setCursor(Qt.PointingHandCursor)
    botao.setToolTip('Organizar tópicos, datas, desempenho e abrir revisões')
    botao.setStyleSheet('''
        QPushButton#abrirGradeEstudosV1 { background:#0b3650; color:#eaf9ff;
          border:1px solid #12b3d4; border-radius:10px;
          font-family:"Segoe UI"; font-size:16px; font-weight:600; }
        QPushButton#abrirGradeEstudosV1:hover { background:#0b6285; color:white; }
    ''')
    linha.addWidget(botao, 0)
    linha.addStretch(1)
    conteudo = painel.cenario
    layout = conteudo.layout()
    # Coloca logo abaixo dos três cards, preservando dimensões e ações antigas.
    layout.insertLayout(layout.count()-1, linha)
    painel._grade_botao_v1 = botao

    def abrir():
        pagina = getattr(janela, 'tela_grade_estudos_v1', None)
        if pagina is None:
            pagina = PaginaGradeEstudos(
                janela, voltar=janela.voltar_inicio,
                abrir_topico=janela.abrir_central_integrada_topico,
            )
            janela.tela_grade_estudos_v1 = pagina
            janela.telas.addWidget(pagina)
        # A abertura da página dispara showEvent, que faz uma única leitura.
        # Evita duplicar consultas ou alertas no primeiro acesso.
        janela.telas.setCurrentWidget(pagina)

    botao.clicked.connect(abrir)
    return botao
