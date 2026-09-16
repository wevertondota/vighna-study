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
    listar_disciplinas,
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
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(titulo)

        formulario = QFormLayout()

        self.data = QDateEdit()
        self.data.setDate(QDate.currentDate())
        self.data.setCalendarPopup(True)
        self.data.setDisplayFormat("dd/MM/yyyy")

        self.questoes = QSpinBox()
        self.questoes.setRange(1, 10000)
        self.questoes.setValue(30)

        self.acertos = QSpinBox()
        self.acertos.setRange(0, 30)
        self.acertos.setValue(0)

        self.resultado = QLabel("0,00%")
        self.resultado.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.observacao = QTextEdit()
        self.observacao.setMaximumHeight(70)

        self.texto_erros = QTextEdit()
        self.texto_erros.setMaximumHeight(100)

        self.continuacao = QTextEdit()
        self.continuacao.setMaximumHeight(70)

        formulario.addRow("Data:", self.data)
        formulario.addRow("Questões:", self.questoes)
        formulario.addRow("Acertos:", self.acertos)
        formulario.addRow("Resultado:", self.resultado)
        formulario.addRow("Observação:", self.observacao)
        formulario.addRow("Texto de erros:", self.texto_erros)
        formulario.addRow("Continuação:", self.continuacao)

        layout.addLayout(formulario)

        botoes = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )

        botoes.button(QDialogButtonBox.Save).setText("Salvar revisão")
        botoes.button(QDialogButtonBox.Cancel).setText("Cancelar")

        botoes.accepted.connect(self.salvar)
        botoes.rejected.connect(self.reject)

        layout.addWidget(botoes)

        self.questoes.valueChanged.connect(self.atualizar_calculos)
        self.acertos.valueChanged.connect(self.atualizar_calculos)

        self.atualizar_calculos()

    def atualizar_calculos(self):
        questoes = self.questoes.value()
        self.acertos.setMaximum(questoes)

        acertos = self.acertos.value()
        percentual = (acertos / questoes) * 100

        self.resultado.setText(
            f"{percentual:.2f}%".replace(".", ",")
        )

    def salvar(self):
        registrar_revisao(
            self.topico_id,
            self.data.date().toString("yyyy-MM-dd"),
            self.questoes.value(),
            self.acertos.value(),
            self.observacao.toPlainText(),
            self.texto_erros.toPlainText(),
            self.continuacao.toPlainText()
        )

        self.accept()


class JanelaTopico(QDialog):
    def __init__(self, topico_id, nome_topico, parent=None):
        super().__init__(parent)

        self.topico_id = topico_id
        self.nome_topico = nome_topico
        self.dados_revisoes = []

        self.setWindowTitle(nome_topico)
        self.resize(850, 600)

        layout = QVBoxLayout(self)

        titulo = QLabel(nome_topico)
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        self.resumo = QLabel()
        self.resumo.setStyleSheet("font-size: 15px;")
        layout.addWidget(self.resumo)

        barra = QHBoxLayout()
        barra.addStretch()

        nova_revisao = QPushButton("+ Nova revisão")
        nova_revisao.clicked.connect(self.nova_revisao)

        barra.addWidget(nova_revisao)
        layout.addLayout(barra)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels([
            "Data",
            "Questões",
            "Acertos",
            "Resultado"
        ])

        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.tabela)

        subtitulo = QLabel("Detalhes da revisão selecionada")
        subtitulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(subtitulo)

        self.detalhes = QTextEdit()
        self.detalhes.setReadOnly(True)
        self.detalhes.setMaximumHeight(160)

        layout.addWidget(self.detalhes)

        self.tabela.itemSelectionChanged.connect(self.mostrar_detalhes)

        self.carregar_historico()

    def carregar_historico(self):
        self.dados_revisoes = listar_revisoes_topico(self.topico_id)

        self.tabela.setRowCount(len(self.dados_revisoes))

        total_questoes = 0
        total_acertos = 0

        for linha, revisao in enumerate(self.dados_revisoes):
            data = revisao[1]
            questoes = revisao[2]
            acertos = revisao[3]
            percentual = revisao[4]

            total_questoes += questoes
            total_acertos += acertos

            data_formatada = datetime.strptime(
                data,
                "%Y-%m-%d"
            ).strftime("%d/%m/%Y")

            valores = [
                data_formatada,
                str(questoes),
                str(acertos),
                f"{percentual:.1f}%".replace(".", ",")
            ]

            for coluna, valor in enumerate(valores):
                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(valor)
                )

        quantidade = len(self.dados_revisoes)

        if total_questoes > 0:
            media = (total_acertos / total_questoes) * 100
            media_texto = f"{media:.1f}%".replace(".", ",")
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

        if janela.exec() == QDialog.Accepted:
            self.carregar_historico()

    def mostrar_detalhes(self):
        linha = self.tabela.currentRow()

        if linha < 0:
            return

        revisao = self.dados_revisoes[linha]

        observacao = revisao[5] or "—"
        texto_erros = revisao[6] or "—"
        continuacao = revisao[7] or "—"

        self.detalhes.setPlainText(
            "OBSERVAÇÃO\n"
            f"{observacao}\n\n"
            "TEXTO DE ERROS\n"
            f"{texto_erros}\n\n"
            "CONTINUAÇÃO\n"
            f"{continuacao}"
        )


class SistemaEstudos(QMainWindow):
    def __init__(self):
        super().__init__()

        criar_banco()

        self.disciplina_atual = None

        self.setWindowTitle("Meu Sistema de Estudos")
        self.resize(1000, 650)

        self.telas = QStackedWidget()

        self.tela_inicial = self.criar_tela_inicial()
        self.tela_disciplina = self.criar_tela_disciplina()

        self.telas.addWidget(self.tela_inicial)
        self.telas.addWidget(self.tela_disciplina)

        self.setCentralWidget(self.telas)

    def criar_tela_inicial(self):
        tela = QWidget()
        layout = QVBoxLayout(tela)

        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)

        titulo = QLabel("GRADE DE REVISÃO E CONTROLE")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")

        subtitulo = QLabel("Selecione uma disciplina")
        subtitulo.setStyleSheet("font-size: 16px;")

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(25)

        for _, nome in listar_disciplinas():
            botao = QPushButton(nome)
            botao.setMinimumHeight(45)
            botao.clicked.connect(
                lambda checked=False, disciplina=nome:
                    self.abrir_disciplina(disciplina)
            )
            layout.addWidget(botao)

        layout.addStretch()

        return tela

    def criar_tela_disciplina(self):
        tela = QWidget()
        layout = QVBoxLayout(tela)

        layout.setContentsMargins(40, 30, 40, 40)
        layout.setSpacing(15)

        barra = QHBoxLayout()

        voltar = QPushButton("← Voltar")
        voltar.setFixedWidth(100)
        voltar.clicked.connect(self.voltar_inicio)

        self.titulo_disciplina = QLabel()
        self.titulo_disciplina.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        adicionar = QPushButton("+ Adicionar tópico")
        adicionar.clicked.connect(self.novo_topico)

        revisar = QPushButton("Registrar revisão")
        revisar.clicked.connect(self.revisar_topico_selecionado)

        barra.addWidget(voltar)
        barra.addWidget(self.titulo_disciplina)
        barra.addStretch()
        barra.addWidget(adicionar)
        barra.addWidget(revisar)

        layout.addLayout(barra)

        self.tabela_topicos = QTableWidget()
        self.tabela_topicos.setColumnCount(4)
        self.tabela_topicos.setHorizontalHeaderLabels([
            "Tópico",
            "Revisões",
            "Última revisão",
            "Acertos"
        ])

        self.tabela_topicos.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.tabela_topicos.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.tabela_topicos.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.tabela_topicos.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.Stretch
        )

        self.tabela_topicos.setColumnWidth(1, 100)
        self.tabela_topicos.setColumnWidth(2, 160)
        self.tabela_topicos.setColumnWidth(3, 110)

        self.tabela_topicos.cellDoubleClicked.connect(
            self.abrir_topico
        )

        layout.addWidget(self.tabela_topicos)

        return tela

    def abrir_disciplina(self, nome_disciplina):
        self.disciplina_atual = nome_disciplina
        self.titulo_disciplina.setText(nome_disciplina)

        self.carregar_topicos()

        self.telas.setCurrentWidget(
            self.tela_disciplina
        )

    def carregar_topicos(self):
        if not self.disciplina_atual:
            return

        dados = listar_topicos(
            self.disciplina_atual
        )

        self.tabela_topicos.setRowCount(
            len(dados)
        )

        for linha, dado in enumerate(dados):
            topico_id = dado[0]
            nome = dado[1]
            revisoes = dado[2]
            data = dado[3]
            percentual = dado[4]

            if data:
                data_formatada = datetime.strptime(
                    data,
                    "%Y-%m-%d"
                ).strftime("%d/%m/%Y")
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

            for coluna, valor in enumerate(valores):
                item = QTableWidgetItem(valor)

                if coluna == 0:
                    item.setData(
                        Qt.UserRole,
                        topico_id
                    )

                self.tabela_topicos.setItem(
                    linha,
                    coluna,
                    item
                )

    def novo_topico(self):
        if not self.disciplina_atual:
            return

        nome, confirmou = QInputDialog.getText(
            self,
            "Novo tópico",
            f"Novo tópico de {self.disciplina_atual}:"
        )

        if not confirmou:
            return

        nome = nome.strip()

        if not nome:
            return

        criado = adicionar_topico(
            self.disciplina_atual,
            nome
        )

        if criado:
            self.carregar_topicos()
        else:
            QMessageBox.information(
                self,
                "Tópico existente",
                "Esse tópico já está cadastrado."
            )

    def revisar_topico_selecionado(self):
        linha = self.tabela_topicos.currentRow()

        if linha < 0:
            QMessageBox.information(
                self,
                "Selecione um tópico",
                "Primeiro selecione um tópico da tabela."
            )
            return

        self.registrar_revisao_linha(linha)

    def registrar_revisao_linha(self, linha):
        item = self.tabela_topicos.item(
            linha,
            0
        )

        if item is None:
            return

        topico_id = item.data(Qt.UserRole)
        nome_topico = item.text()

        janela = JanelaRevisao(
            topico_id,
            nome_topico,
            self
        )

        if janela.exec() == QDialog.Accepted:
            self.carregar_topicos()

    def abrir_topico(self, linha, coluna):
        item = self.tabela_topicos.item(
            linha,
            0
        )

        if item is None:
            return

        topico_id = item.data(Qt.UserRole)
        nome_topico = item.text()

        janela = JanelaTopico(
            topico_id,
            nome_topico,
            self
        )

        janela.exec()

        self.carregar_topicos()

    def voltar_inicio(self):
        self.telas.setCurrentWidget(
            self.tela_inicial
        )


app = QApplication(sys.argv)

janela = SistemaEstudos()
janela.show()

sys.exit(app.exec())
