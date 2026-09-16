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

        # Duplo clique também registra revisão
        self.tabela_penal.cellDoubleClicked.connect(
            self.abrir_revisao_linha
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