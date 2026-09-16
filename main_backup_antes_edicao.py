import sys
from datetime import datetime

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
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
    QAbstractItemView,
    QCheckBox
)

from banco import (
    criar_banco,
    listar_disciplinas,
    listar_topicos,
    adicionar_topico,
    registrar_revisao,
    listar_revisoes_topico,
    obter_resumo_topico,
    listar_pendencias,
    obter_dashboard
)


def formatar_data(data):
    if not data:
        return "—"

    return datetime.strptime(
        data,
        "%Y-%m-%d"
    ).strftime("%d/%m/%Y")


def formatar_percentual(valor, casas=1):
    if valor is None:
        return "—"

    return f"{valor:.{casas}f}%".replace(".", ",")


def calcular_prioridade(proxima_revisao, percentual, revisoes):
    """
    Heurística de prioridade (0 a 100).

    Considera:
    - se a revisão vence hoje ou está atrasada;
    - quantos dias de atraso existem;
    - desempenho atual;
    - quantidade de revisões já realizadas.

    Não altera os dados do usuário: serve apenas para ordenar a fila.
    """

    hoje = QDate.currentDate()
    data_revisao = QDate.fromString(
        proxima_revisao,
        "yyyy-MM-dd"
    )

    if not data_revisao.isValid():
        return 0, "SEM DATA", "Data inválida"

    atraso = max(
        0,
        data_revisao.daysTo(hoje)
    )

    # Toda revisão que vence hoje já recebe peso relevante.
    if atraso == 0:
        score = 45.0
        situacao = "HOJE"
        motivo_data = "vence hoje"
    else:
        # Atraso aumenta gradualmente a prioridade.
        score = 50.0 + min(atraso, 20) * 1.5
        situacao = "ATRASADA"
        motivo_data = f"{atraso}d atrasada"

    # Desempenho abaixo de 80% aumenta a prioridade.
    if percentual is None:
        score += 10.0
        motivo_desempenho = "sem %"
    else:
        score += max(
            0.0,
            80.0 - percentual
        ) * 0.8

        motivo_desempenho = (
            f"{percentual:.0f}%"
        )

    # Poucas revisões aumentam a prioridade.
    if revisoes <= 0:
        score += 15.0
    elif revisoes == 1:
        score += 10.0
    elif revisoes == 2:
        score += 5.0

    score = min(
        100.0,
        round(score, 1)
    )

    if score >= 80:
        nivel = "MUITO ALTA"
    elif score >= 60:
        nivel = "ALTA"
    elif score >= 40:
        nivel = "MÉDIA"
    else:
        nivel = "BAIXA"

    motivo = (
        f"{motivo_data} • "
        f"{motivo_desempenho} • "
        f"{revisoes} rev."
    )

    return score, nivel, motivo


class JanelaRevisao(QDialog):
    def __init__(self, topico_id, nome_topico, parent=None):
        super().__init__(parent)

        self.topico_id = topico_id

        self.setWindowTitle("Registrar revisão")
        self.resize(560, 610)

        layout = QVBoxLayout(self)

        titulo = QLabel(nome_topico)
        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )
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

        self.resultado = QLabel("0,00%")
        self.resultado.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        self.agendar = QCheckBox(
            "Agendar próxima revisão"
        )
        self.agendar.setChecked(True)

        self.proxima_revisao = QDateEdit()
        self.proxima_revisao.setDate(
            QDate.currentDate().addDays(7)
        )
        self.proxima_revisao.setCalendarPopup(True)
        self.proxima_revisao.setDisplayFormat("dd/MM/yyyy")

        self.observacao = QTextEdit()
        self.observacao.setMaximumHeight(70)

        self.texto_erros = QTextEdit()
        self.texto_erros.setMaximumHeight(100)

        self.continuacao = QTextEdit()
        self.continuacao.setMaximumHeight(70)

        formulario.addRow(
            "Data da revisão:",
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
            "",
            self.agendar
        )
        formulario.addRow(
            "Próxima revisão:",
            self.proxima_revisao
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

        botoes.accepted.connect(self.salvar)
        botoes.rejected.connect(self.reject)

        layout.addWidget(botoes)

        self.questoes.valueChanged.connect(
            self.atualizar_calculos
        )
        self.acertos.valueChanged.connect(
            self.atualizar_calculos
        )
        self.agendar.toggled.connect(
            self.proxima_revisao.setEnabled
        )

        self.atualizar_calculos()

    def atualizar_calculos(self):
        questoes = self.questoes.value()

        self.acertos.setMaximum(
            questoes
        )

        percentual = (
            self.acertos.value() /
            questoes
        ) * 100

        self.resultado.setText(
            formatar_percentual(
                percentual,
                2
            )
        )

    def salvar(self):
        if self.agendar.isChecked():
            proxima = (
                self.proxima_revisao
                .date()
                .toString("yyyy-MM-dd")
            )
        else:
            proxima = None

        registrar_revisao(
            self.topico_id,
            self.data.date().toString(
                "yyyy-MM-dd"
            ),
            self.questoes.value(),
            self.acertos.value(),
            self.observacao.toPlainText(),
            self.texto_erros.toPlainText(),
            self.continuacao.toPlainText(),
            proxima
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
        self.dados_revisoes = []

        self.setWindowTitle(nome_topico)
        self.resize(900, 650)

        layout = QVBoxLayout(self)

        titulo = QLabel(nome_topico)
        titulo.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )
        layout.addWidget(titulo)

        self.resumo = QLabel()
        self.resumo.setStyleSheet(
            "font-size: 15px;"
        )
        self.resumo.setWordWrap(True)
        layout.addWidget(self.resumo)

        self.aviso_legado = QLabel()
        self.aviso_legado.setWordWrap(True)
        layout.addWidget(
            self.aviso_legado
        )

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
        self.tabela.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addWidget(self.tabela)

        subtitulo = QLabel(
            "Detalhes da revisão selecionada"
        )
        subtitulo.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(subtitulo)

        self.detalhes = QTextEdit()
        self.detalhes.setReadOnly(True)
        self.detalhes.setMaximumHeight(170)

        layout.addWidget(
            self.detalhes
        )

        self.tabela.itemSelectionChanged.connect(
            self.mostrar_detalhes
        )

        self.carregar_historico()

    def carregar_historico(self):
        resumo = obter_resumo_topico(
            self.topico_id
        )

        self.dados_revisoes = (
            listar_revisoes_topico(
                self.topico_id
            )
        )

        self.tabela.setRowCount(
            len(self.dados_revisoes)
        )

        for linha, revisao in enumerate(
            self.dados_revisoes
        ):
            valores = [
                formatar_data(revisao[1]),
                str(revisao[2]),
                str(revisao[3]),
                formatar_percentual(
                    revisao[4]
                )
            ]

            for coluna, valor in enumerate(
                valores
            ):
                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(valor)
                )

        self.resumo.setText(
            f"Revisões totais: "
            f"{resumo['revisoes_totais']}    |    "
            f"Resultado atual: "
            f"{formatar_percentual(resumo['percentual_atual'])}    |    "
            f"Última revisão registrada: "
            f"{formatar_data(resumo['ultima_revisao'])}    |    "
            f"Próxima revisão: "
            f"{formatar_data(resumo['proxima_revisao'])}"
        )

        iniciais = resumo[
            "revisoes_iniciais"
        ]

        if iniciais > 0:
            self.aviso_legado.setText(
                f"{iniciais} revisão(ões) anteriores "
                "foram trazidas do Excel. "
                "A planilha não guardava os detalhes "
                "individuais dessas sessões; "
                "por isso elas entram no total, mas não "
                "aparecem como linhas no histórico abaixo."
            )
        else:
            self.aviso_legado.clear()

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

        revisao = self.dados_revisoes[
            linha
        ]

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

        self.setWindowTitle(
            "Meu Sistema de Estudos"
        )
        self.resize(1220, 780)

        self.telas = QStackedWidget()

        self.tela_inicial = (
            self.criar_tela_inicial()
        )

        self.tela_disciplina = (
            self.criar_tela_disciplina()
        )

        self.telas.addWidget(
            self.tela_inicial
        )
        self.telas.addWidget(
            self.tela_disciplina
        )

        self.setCentralWidget(
            self.telas
        )

        self.atualizar_dashboard()

    def criar_cartao(self, titulo):
        caixa = QWidget()

        layout = QVBoxLayout(
            caixa
        )

        rotulo = QLabel(titulo)
        rotulo.setStyleSheet(
            "font-size: 12px;"
        )

        valor = QLabel("0")
        valor.setStyleSheet(
            "font-size: 24px; "
            "font-weight: bold;"
        )

        layout.addWidget(rotulo)
        layout.addWidget(valor)

        caixa.setStyleSheet(
            "QWidget {"
            "border: 1px solid #d0d0d0;"
            "border-radius: 8px;"
            "padding: 6px;"
            "}"
        )

        return caixa, valor

    def criar_tela_inicial(self):
        tela = QWidget()

        layout = QVBoxLayout(
            tela
        )

        layout.setContentsMargins(
            35,
            30,
            35,
            35
        )

        layout.setSpacing(14)

        titulo = QLabel(
            "GRADE DE REVISÃO E CONTROLE"
        )

        titulo.setStyleSheet(
            "font-size: 26px; "
            "font-weight: bold;"
        )

        subtitulo = QLabel(
            "Visão geral do estudo"
        )

        subtitulo.setStyleSheet(
            "font-size: 15px;"
        )

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        grade = QGridLayout()

        cartao, self.card_hoje = (
            self.criar_cartao(
                "Revisões para hoje"
            )
        )
        grade.addWidget(
            cartao,
            0,
            0
        )

        cartao, self.card_atrasadas = (
            self.criar_cartao(
                "Revisões atrasadas"
            )
        )
        grade.addWidget(
            cartao,
            0,
            1
        )

        cartao, self.card_media = (
            self.criar_cartao(
                "Desempenho atual"
            )
        )
        grade.addWidget(
            cartao,
            0,
            2
        )

        cartao, self.card_revisoes = (
            self.criar_cartao(
                "Revisões registradas"
            )
        )
        grade.addWidget(
            cartao,
            1,
            0
        )

        cartao, self.card_questoes = (
            self.criar_cartao(
                "Questões no programa"
            )
        )
        grade.addWidget(
            cartao,
            1,
            1
        )

        cartao, self.card_topicos = (
            self.criar_cartao(
                "Tópicos cadastrados"
            )
        )
        grade.addWidget(
            cartao,
            1,
            2
        )

        layout.addLayout(grade)

        pendentes_titulo = QLabel(
            "Fila inteligente de revisão"
        )

        pendentes_titulo.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            pendentes_titulo
        )

        explicacao = QLabel(
            "A prioridade combina atraso, desempenho "
            "e quantidade de revisões. "
            "Ela serve para ordenar o que merece atenção primeiro."
        )

        explicacao.setWordWrap(True)

        layout.addWidget(
            explicacao
        )

        self.tabela_pendentes = (
            QTableWidget()
        )

        self.tabela_pendentes.setColumnCount(
            8
        )

        self.tabela_pendentes.setHorizontalHeaderLabels([
            "Disciplina",
            "Tópico",
            "Revisões",
            "Próxima revisão",
            "% atual",
            "Prioridade",
            "Motivo",
            "Score"
        ])

        self.tabela_pendentes.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.tabela_pendentes.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.tabela_pendentes.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.tabela_pendentes.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.Stretch
        )

        self.tabela_pendentes.horizontalHeader().setSectionResizeMode(
            6,
            QHeaderView.Stretch
        )

        self.tabela_pendentes.setColumnWidth(
            0,
            145
        )
        self.tabela_pendentes.setColumnWidth(
            2,
            75
        )
        self.tabela_pendentes.setColumnWidth(
            3,
            125
        )
        self.tabela_pendentes.setColumnWidth(
            4,
            80
        )
        self.tabela_pendentes.setColumnWidth(
            5,
            100
        )
        self.tabela_pendentes.setColumnWidth(
            7,
            65
        )

        self.tabela_pendentes.cellDoubleClicked.connect(
            self.abrir_topico_pendente
        )

        layout.addWidget(
            self.tabela_pendentes,
            1
        )

        disciplinas_titulo = QLabel(
            "Disciplinas"
        )

        disciplinas_titulo.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            disciplinas_titulo
        )

        botoes_layout = QGridLayout()

        for indice, (_, nome) in enumerate(
            listar_disciplinas()
        ):
            botao = QPushButton(nome)
            botao.setMinimumHeight(42)

            botao.clicked.connect(
                lambda checked=False,
                disciplina=nome:
                    self.abrir_disciplina(
                        disciplina
                    )
            )

            linha = indice // 3
            coluna = indice % 3

            botoes_layout.addWidget(
                botao,
                linha,
                coluna
            )

        layout.addLayout(
            botoes_layout
        )

        return tela

    def atualizar_dashboard(self):
        hoje = (
            QDate.currentDate()
            .toString("yyyy-MM-dd")
        )

        resumo = obter_dashboard(
            hoje
        )

        self.card_hoje.setText(
            str(resumo["hoje"])
        )

        self.card_atrasadas.setText(
            str(resumo["atrasadas"])
        )

        self.card_media.setText(
            formatar_percentual(
                resumo["media_atual"]
            )
        )

        self.card_revisoes.setText(
            str(resumo["revisoes_totais"])
        )

        self.card_questoes.setText(
            str(resumo["total_questoes"])
        )

        self.card_topicos.setText(
            str(resumo["total_topicos"])
        )

        pendencias = listar_pendencias(
            hoje
        )

        fila = []

        for dado in pendencias:
            topico_id = dado[0]
            disciplina = dado[1]
            topico = dado[2]
            revisoes = dado[3]
            proxima = dado[4]
            percentual = dado[5]

            score, nivel, motivo = (
                calcular_prioridade(
                    proxima,
                    percentual,
                    revisoes
                )
            )

            fila.append({
                "topico_id": topico_id,
                "disciplina": disciplina,
                "topico": topico,
                "revisoes": revisoes,
                "proxima": proxima,
                "percentual": percentual,
                "score": score,
                "nivel": nivel,
                "motivo": motivo,
            })

        fila.sort(
            key=lambda item: (
                -item["score"],
                item["proxima"],
                item["disciplina"].lower(),
                item["topico"].lower()
            )
        )

        self.tabela_pendentes.setRowCount(
            len(fila)
        )

        for linha, item_fila in enumerate(
            fila
        ):
            valores = [
                item_fila["disciplina"],
                item_fila["topico"],
                str(item_fila["revisoes"]),
                formatar_data(
                    item_fila["proxima"]
                ),
                formatar_percentual(
                    item_fila["percentual"]
                ),
                item_fila["nivel"],
                item_fila["motivo"],
                f"{item_fila['score']:.1f}"
                .replace(".", ",")
            ]

            for coluna, valor in enumerate(
                valores
            ):
                item = QTableWidgetItem(
                    valor
                )

                if coluna == 1:
                    item.setData(
                        Qt.UserRole,
                        item_fila["topico_id"]
                    )

                nivel = item_fila["nivel"]

                if nivel == "MUITO ALTA":
                    item.setBackground(
                        QColor("#F5B7B1")
                    )
                elif nivel == "ALTA":
                    item.setBackground(
                        QColor("#FAD7A0")
                    )
                elif nivel == "MÉDIA":
                    item.setBackground(
                        QColor("#FCF3CF")
                    )

                self.tabela_pendentes.setItem(
                    linha,
                    coluna,
                    item
                )

    def abrir_topico_pendente(
        self,
        linha,
        coluna
    ):
        item = self.tabela_pendentes.item(
            linha,
            1
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

        self.atualizar_dashboard()

    def criar_tela_disciplina(self):
        tela = QWidget()

        layout = QVBoxLayout(
            tela
        )

        layout.setContentsMargins(
            40,
            30,
            40,
            40
        )

        layout.setSpacing(15)

        barra = QHBoxLayout()

        voltar = QPushButton(
            "← Voltar"
        )

        voltar.setFixedWidth(100)

        voltar.clicked.connect(
            self.voltar_inicio
        )

        self.titulo_disciplina = QLabel()

        self.titulo_disciplina.setStyleSheet(
            "font-size: 24px; "
            "font-weight: bold;"
        )

        adicionar = QPushButton(
            "+ Adicionar tópico"
        )

        adicionar.clicked.connect(
            self.novo_topico
        )

        revisar = QPushButton(
            "Registrar revisão"
        )

        revisar.clicked.connect(
            self.revisar_topico_selecionado
        )

        barra.addWidget(voltar)
        barra.addWidget(
            self.titulo_disciplina
        )

        barra.addStretch()

        barra.addWidget(adicionar)
        barra.addWidget(revisar)

        layout.addLayout(barra)

        self.tabela_topicos = (
            QTableWidget()
        )

        self.tabela_topicos.setColumnCount(
            5
        )

        self.tabela_topicos.setHorizontalHeaderLabels([
            "Tópico",
            "Revisões",
            "Última revisão",
            "Próxima revisão",
            "% atual"
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

        self.tabela_topicos.setColumnWidth(
            1,
            90
        )
        self.tabela_topicos.setColumnWidth(
            2,
            135
        )
        self.tabela_topicos.setColumnWidth(
            3,
            135
        )
        self.tabela_topicos.setColumnWidth(
            4,
            90
        )

        self.tabela_topicos.cellDoubleClicked.connect(
            self.abrir_topico
        )

        layout.addWidget(
            self.tabela_topicos
        )

        return tela

    def abrir_disciplina(
        self,
        nome_disciplina
    ):
        self.disciplina_atual = (
            nome_disciplina
        )

        self.titulo_disciplina.setText(
            nome_disciplina
        )

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

        hoje = QDate.currentDate()

        for linha, dado in enumerate(
            dados
        ):
            topico_id = dado[0]
            nome = dado[1]
            revisoes = dado[2]
            ultima = dado[3]
            proxima = dado[4]
            percentual = dado[5]

            valores = [
                nome,
                str(revisoes),
                formatar_data(ultima),
                formatar_data(proxima),
                formatar_percentual(
                    percentual
                )
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

                if coluna == 3 and proxima:
                    data_qt = QDate.fromString(
                        proxima,
                        "yyyy-MM-dd"
                    )

                    if (
                        data_qt.isValid()
                        and data_qt < hoje
                    ):
                        item.setBackground(
                            QColor("#FADBD8")
                        )

                    elif data_qt == hoje:
                        item.setBackground(
                            QColor("#FCF3CF")
                        )

                self.tabela_topicos.setItem(
                    linha,
                    coluna,
                    item
                )

    def novo_topico(self):
        if not self.disciplina_atual:
            return

        nome, confirmou = (
            QInputDialog.getText(
                self,
                "Novo tópico",
                f"Novo tópico de "
                f"{self.disciplina_atual}:"
            )
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

    def revisar_topico_selecionado(
        self
    ):
        linha = (
            self.tabela_topicos
            .currentRow()
        )

        if linha < 0:
            QMessageBox.information(
                self,
                "Selecione um tópico",
                "Primeiro selecione um "
                "tópico da tabela."
            )
            return

        item = self.tabela_topicos.item(
            linha,
            0
        )

        if item is None:
            return

        janela = JanelaRevisao(
            item.data(Qt.UserRole),
            item.text(),
            self
        )

        if janela.exec() == QDialog.Accepted:
            self.carregar_topicos()

    def abrir_topico(
        self,
        linha,
        coluna
    ):
        item = self.tabela_topicos.item(
            linha,
            0
        )

        if item is None:
            return

        janela = JanelaTopico(
            item.data(Qt.UserRole),
            item.text(),
            self
        )

        janela.exec()

        self.carregar_topicos()

    def voltar_inicio(self):
        self.atualizar_dashboard()

        self.telas.setCurrentWidget(
            self.tela_inicial
        )


app = QApplication(sys.argv)

janela = SistemaEstudos()

janela.show()

sys.exit(app.exec())
