import sys

from datetime import datetime

from PySide6.QtCore import Qt, QDate

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QInputDialog,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QDateEdit,
    QSpinBox,
    QTextEdit,
    QAbstractItemView
)

from banco import (
    criar_banco,
    listar_topicos,
    adicionar_topico,
    registrar_revisao,
    listar_revisoes_topico
)



class JanelaRevisao(QDialog):

    def __init__(self, topico_id, nome_topico, parent=None):
        super().__init__(parent)

        self.topico_id = topico_id

        self.setWindowTitle("Registrar revisão")
        self.resize(550, 550)

        layout = QVBoxLayout(self)

        titulo = QLabel(nome_topico)

        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        formulario = QFormLayout()

        # DATA
        self.data = QDateEdit()

        self.data.setDate(
            QDate.currentDate()
        )

        self.data.setCalendarPopup(True)

        self.data.setDisplayFormat(
            "dd/MM/yyyy"
        )

        # QUESTÕES
        self.questoes = QSpinBox()

        self.questoes.setRange(
            1,
            10000
        )

        self.questoes.setValue(30)

        # ACERTOS
        self.acertos = QSpinBox()

        self.acertos.setRange(
            0,
            30
        )

        self.acertos.setValue(0)

        # RESULTADO
        self.resultado = QLabel("0,00%")

        self.resultado.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        # OBSERVAÇÃO
        self.observacao = QTextEdit()

        self.observacao.setMaximumHeight(70)

        # TEXTO DE ERROS
        self.texto_erros = QTextEdit()

        self.texto_erros.setMaximumHeight(100)

        # CONTINUAÇÃO
        self.continuacao = QTextEdit()

        self.continuacao.setMaximumHeight(70)

        formulario.addRow(
            "Data:",
            self.data
        )

        formulario.addRow(
            "Questões:",
            self.questoes
        )

        formulario.addRow(
            "Acertos:",
            self.acertos
        )

        formulario.addRow(
            "Resultado:",
            self.resultado
        )

        formulario.addRow(
            "Observação:",
            self.observacao
        )

        formulario.addRow(
            "Texto de erros:",
            self.texto_erros
        )

        formulario.addRow(
            "Continuação:",
            self.continuacao
        )

        layout.addLayout(formulario)

        # BOTÕES
        botoes = QDialogButtonBox(
            QDialogButtonBox.Save |
            QDialogButtonBox.Cancel
        )

        botoes.button(
            QDialogButtonBox.Save
        ).setText("Salvar revisão")

        botoes.button(
            QDialogButtonBox.Cancel
        ).setText("Cancelar")

        botoes.accepted.connect(
            self.salvar
        )

        botoes.rejected.connect(
            self.reject
        )

        layout.addWidget(botoes)

        # Atualização automática
        self.questoes.valueChanged.connect(
            self.atualizar_calculos
        )

        self.acertos.valueChanged.connect(
            self.atualizar_calculos
        )

        self.atualizar_calculos()

    def atualizar_calculos(self):

        questoes = self.questoes.value()

        self.acertos.setMaximum(
            questoes
        )

        acertos = self.acertos.value()

        percentual = (
            acertos / questoes
        ) * 100

        texto = (
            f"{percentual:.2f}%"
            .replace(".", ",")
        )

        self.resultado.setText(texto)

    def salvar(self):

        questoes = self.questoes.value()
        acertos = self.acertos.value()

        if acertos > questoes:

            QMessageBox.warning(
                self,
                "Dados inválidos",
                "O número de acertos não pode superar "
                "o número de questões."
            )

            return

        data_banco = (
            self.data.date()
            .toString("yyyy-MM-dd")
        )

        registrar_revisao(
            self.topico_id,
            data_banco,
            questoes,
            acertos,
            self.observacao.toPlainText(),
            self.texto_erros.toPlainText(),
            self.continuacao.toPlainText()
        )

        self.accept()

class JanelaTopico(QDialog):

    def __init__(
        self,
        topico_id,
        nome_topico,
        parent=None
    ):
        super().__init__(parent)

        self.topico_id = topico_id
        self.nome_topico = nome_topico

        self.setWindowTitle(nome_topico)
        self.resize(850, 600)

        layout = QVBoxLayout(self)

        # TÍTULO
        titulo = QLabel(nome_topico)

        titulo.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        # RESUMO
        self.resumo = QLabel()

        self.resumo.setStyleSheet(
            "font-size: 15px;"
        )

        layout.addWidget(self.resumo)

        # BOTÃO NOVA REVISÃO
        barra = QHBoxLayout()

        barra.addStretch()

        nova_revisao = QPushButton(
            "+ Nova revisão"
        )

        nova_revisao.clicked.connect(
            self.nova_revisao
        )

        barra.addWidget(nova_revisao)

        layout.addLayout(barra)

        # HISTÓRICO
        self.tabela = QTableWidget()

        self.tabela.setColumnCount(4)

        self.tabela.setHorizontalHeaderLabels([
            "Data",
            "Questões",
            "Acertos",
            "Resultado"
        ])

        self.tabela.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.tabela.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addWidget(self.tabela)

        # DETALHES
        subtitulo = QLabel(
            "Detalhes da revisão selecionada"
        )

        subtitulo.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )

        layout.addWidget(subtitulo)

        self.detalhes = QTextEdit()

        self.detalhes.setReadOnly(True)
        self.detalhes.setMaximumHeight(160)

        layout.addWidget(self.detalhes)

        self.tabela.itemSelectionChanged.connect(
            self.mostrar_detalhes
        )

        self.carregar_historico()

    def carregar_historico(self):

        self.dados_revisoes = listar_revisoes_topico(
            self.topico_id
        )

        self.tabela.setRowCount(
            len(self.dados_revisoes)
        )

        total_questoes = 0
        total_acertos = 0

        for linha, revisao in enumerate(
            self.dados_revisoes
        ):

            data = revisao[1]
            questoes = revisao[2]
            acertos = revisao[3]
            percentual = revisao[4]

            total_questoes += questoes
            total_acertos += acertos

            data_formatada = datetime.strptime(
                data,
                "%Y-%m-%d"
            ).strftime(
                "%d/%m/%Y"
            )

            percentual_formatado = (
                f"{percentual:.1f}%"
                .replace(".", ",")
            )

            valores = [
                data_formatada,
                str(questoes),
                str(acertos),
                percentual_formatado
            ]

            for coluna, valor in enumerate(valores):

                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(valor)
                )

        quantidade = len(
            self.dados_revisoes
        )

        if total_questoes > 0:

            media = (
                total_acertos /
                total_questoes
            ) * 100

            media_texto = (
                f"{media:.1f}%"
                .replace(".", ",")
            )

        else:

            media_texto = "—"

        if quantidade > 0:

            ultimo = (
                f"{self.dados_revisoes[0][4]:.1f}%"
                .replace(".", ",")
            )

        else:

            ultimo = "—"

        self.resumo.setText(
            f"Revisões: {quantidade}    |    "
            f"Média geral: {media_texto}    |    "
            f"Último resultado: {ultimo}"
        )

        self.detalhes.clear()

    def nova_revisao(self):

        janela = JanelaRevisao(
            self.topico_id,
            self.nome_topico,
            self
        )

        resultado = janela.exec()

        if resultado == QDialog.Accepted:
            self.carregar_historico()

    def mostrar_detalhes(self):

        linha = self.tabela.currentRow()

        if linha < 0:
            return

        revisao = self.dados_revisoes[
            linha
        ]

        observacao = revisao[5] or ""
        texto_erros = revisao[6] or ""
        continuacao = revisao[7] or ""

        texto = (
            "OBSERVAÇÃO\n"
            f"{observacao or '—'}\n\n"

            "TEXTO DE ERROS\n"
            f"{texto_erros or '—'}\n\n"

            "CONTINUAÇÃO\n"
            f"{continuacao or '—'}"
        )

        self.detalhes.setPlainText(texto)

class SistemaEstudos(QMainWindow):


    def __init__(self):
        super().__init__()

        criar_banco()

        self.setWindowTitle(
            "Meu Sistema de Estudos"
        )

        self.resize(
            1000,
            650
        )

        self.telas = QStackedWidget()

        self.tela_inicial = (
            self.criar_tela_inicial()
        )

        self.tela_penal = (
            self.criar_tela_penal()
        )

        self.telas.addWidget(
            self.tela_inicial
        )

        self.telas.addWidget(
            self.tela_penal
        )

        self.setCentralWidget(
            self.telas
        )

    # ==========================================
    # TELA INICIAL
    # ==========================================

    def criar_tela_inicial(self):

        tela = QWidget()

        layout = QVBoxLayout(tela)

        layout.setContentsMargins(
            40, 40, 40, 40
        )

        layout.setSpacing(12)

        titulo = QLabel(
            "GRADE DE REVISÃO E CONTROLE"
        )

        titulo.setStyleSheet(
            "font-size: 24px; "
            "font-weight: bold;"
        )

        subtitulo = QLabel(
            "Selecione uma disciplina"
        )

        penal = QPushButton(
            "Direito Penal"
        )

        administrativo = QPushButton(
            "Direito Administrativo"
        )

        ctb = QPushButton("CTB")

        portugues = QPushButton(
            "Português"
        )

        matematica = QPushButton(
            "Matemática"
        )

        informatica = QPushButton(
            "Informática"
        )

        botoes = [
            penal,
            administrativo,
            ctb,
            portugues,
            matematica,
            informatica
        ]

        for botao in botoes:

            botao.setMinimumHeight(45)

        penal.clicked.connect(
            self.abrir_penal
        )

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        layout.addSpacing(25)

        for botao in botoes:

            layout.addWidget(botao)

        layout.addStretch()

        return tela

    # ==========================================
    # DIREITO PENAL
    # ==========================================

    def criar_tela_penal(self):

        tela = QWidget()

        layout = QVBoxLayout(tela)

        layout.setContentsMargins(
            40, 30, 40, 40
        )

        barra = QHBoxLayout()

        voltar = QPushButton(
            "← Voltar"
        )

        voltar.setFixedWidth(100)

        titulo = QLabel(
            "Direito Penal"
        )

        titulo.setStyleSheet(
            "font-size: 24px; "
            "font-weight: bold;"
        )

        adicionar = QPushButton(
            "+ Adicionar tópico"
        )

        revisar = QPushButton(
            "Registrar revisão"
        )

        voltar.clicked.connect(
            self.voltar_inicio
        )

        adicionar.clicked.connect(
            self.novo_topico_penal
        )

        revisar.clicked.connect(
            self.revisar_topico_selecionado
        )

        barra.addWidget(voltar)
        barra.addWidget(titulo)

        barra.addStretch()

        barra.addWidget(adicionar)
        barra.addWidget(revisar)

        layout.addLayout(barra)

        # TABELA

        self.tabela_penal = QTableWidget()

        self.tabela_penal.setColumnCount(4)

        self.tabela_penal.setHorizontalHeaderLabels([
            "Tópico",
            "Revisões",
            "Última revisão",
            "Acertos"
        ])

        self.tabela_penal.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.tabela_penal.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.tabela_penal.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.tabela_penal.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.Stretch
        )

        self.tabela_penal.setColumnWidth(
            1,
            100
        )

        self.tabela_penal.setColumnWidth(
            2,
            160
        )

        self.tabela_penal.setColumnWidth(
            3,
            110
        )

                # Duplo clique abre o histórico do tópico
        self.tabela_penal.cellDoubleClicked.connect(
            self.abrir_topico
        )

        layout.addWidget(
            self.tabela_penal
        )

        return tela

    # ==========================================
    # CARREGAR TÓPICOS
    # ==========================================

    def carregar_penal(self):

        dados = listar_topicos(
            "Direito Penal"
        )

        self.tabela_penal.setRowCount(
            len(dados)
        )

        for linha, dado in enumerate(dados):

            topico_id = dado[0]
            nome = dado[1]
            revisoes = dado[2]
            data = dado[3]
            percentual = dado[4]

            if data:

                data_formatada = (
                    datetime.strptime(
                        data,
                        "%Y-%m-%d"
                    )
                    .strftime(
                        "%d/%m/%Y"
                    )
                )

            else:

                data_formatada = "—"

            if percentual is None:

                percentual_formatado = "—"

            else:

                percentual_formatado = (
                    f"{percentual:.1f}%"
                    .replace(".", ",")
                )

            valores = [
                nome,
                str(revisoes),
                data_formatada,
                percentual_formatado
            ]

            for coluna, valor in enumerate(
                valores
            ):

                item = QTableWidgetItem(
                    valor
                )

                if coluna == 0:

                    item.setData(
                        Qt.UserRole,
                        topico_id
                    )

                self.tabela_penal.setItem(
                    linha,
                    coluna,
                    item
                )

    # ==========================================
    # NOVO TÓPICO
    # ==========================================

    def novo_topico_penal(self):

        nome, confirmou = (
            QInputDialog.getText(
                self,
                "Novo tópico",
                "Nome do tópico:"
            )
        )

        if not confirmou:
            return

        nome = nome.strip()

        if not nome:
            return

        criado = adicionar_topico(
            "Direito Penal",
            nome
        )

        if criado:

            self.carregar_penal()

        else:

            QMessageBox.information(
                self,
                "Tópico existente",
                "Esse tópico já está "
                "cadastrado."
            )

    # ==========================================
    # REGISTRAR REVISÃO
    # ==========================================

    def revisar_topico_selecionado(self):

        linha = (
            self.tabela_penal.currentRow()
        )

        if linha < 0:

            QMessageBox.information(
                self,
                "Selecione um tópico",
                "Primeiro selecione um "
                "tópico da tabela."
            )

            return

        self.abrir_revisao_linha(
            linha,
            0
        )

    def abrir_revisao_linha(
        self,
        linha,
        coluna
    ):

        item = self.tabela_penal.item(
            linha,
            0
        )

        if item is None:
            return

        topico_id = item.data(
            Qt.UserRole
        )

        nome_topico = item.text()

        janela = JanelaRevisao(
            topico_id,
            nome_topico,
            self
        )

        resultado = janela.exec()

        if resultado == QDialog.Accepted:

            self.carregar_penal()

       # ==========================================
    # NAVEGAÇÃO
    # ==========================================

    def abrir_topico(self, linha, coluna):

        item = self.tabela_penal.item(
            linha,
            0
        )

        if item is None:
            return

        topico_id = item.data(
            Qt.UserRole
        )

        nome_topico = item.text()

        janela = JanelaTopico(
            topico_id,
            nome_topico,
            self
        )

        janela.exec()

        self.carregar_penal()

    def abrir_penal(self):

        self.carregar_penal()

        self.telas.setCurrentWidget(
            self.tela_penal
        )

    def voltar_inicio(self):

        self.telas.setCurrentWidget(
            self.tela_inicial
        )


app = QApplication(sys.argv)

janela = SistemaEstudos()

janela.show()

sys.exit(app.exec())