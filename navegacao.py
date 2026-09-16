"""Busca global e navegação rápida do VighnaStudy."""

from __future__ import annotations

import unicodedata

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


def _normalizar(texto):
    texto = unicodedata.normalize("NFD", str(texto or "").lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return " ".join(texto.split())


class JanelaBuscaGlobal(QDialog):
    def __init__(self, itens, parent=None):
        super().__init__(parent)
        self.itens = list(itens or [])
        self.resultado = None
        self.acao = None
        self.setWindowTitle("Busca rápida — VighnaStudy")
        self.resize(760, 520)
        self.setMinimumSize(620, 420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        titulo = QLabel("Busca rápida")
        titulo.setObjectName("pageTitle")
        layout.addWidget(titulo)

        subtitulo = QLabel(
            "Procure um tópico do perfil ativo e vá direto para Foco, Questões ou Revisão. Atalho: Ctrl+K."
        )
        subtitulo.setObjectName("pageSubtitle")
        subtitulo.setWordWrap(True)
        layout.addWidget(subtitulo)

        self.busca = QLineEdit()
        self.busca.setPlaceholderText("Digite disciplina ou tópico…")
        self.busca.setClearButtonEnabled(True)
        self.busca.textChanged.connect(self.filtrar)
        self.busca.returnPressed.connect(lambda: self._escolher("estudar"))
        layout.addWidget(self.busca)

        self.tabela = QTableWidget(0, 3)
        self.tabela.setHorizontalHeaderLabels(["Disciplina", "Tópico", "Importância"])
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabela.horizontalHeader().setStretchLastSection(False)
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabela.doubleClicked.connect(lambda _idx: self._escolher("estudar"))
        layout.addWidget(self.tabela, 1)

        self.status = QLabel("")
        self.status.setObjectName("mutedLabel")
        layout.addWidget(self.status)

        botoes = QHBoxLayout()
        estudar = QPushButton("Estudar no Foco")
        estudar.setObjectName("primaryButton")
        estudar.clicked.connect(lambda: self._escolher("estudar"))
        questoes = QPushButton("Questões")
        questoes.setObjectName("questionsNavButton")
        questoes.clicked.connect(lambda: self._escolher("questoes"))
        revisar = QPushButton("Registrar revisão")
        revisar.setObjectName("subtleButton")
        revisar.clicked.connect(lambda: self._escolher("revisao"))
        fechar = QPushButton("Fechar")
        fechar.setObjectName("subtleButton")
        fechar.clicked.connect(self.reject)
        botoes.addWidget(estudar)
        botoes.addWidget(questoes)
        botoes.addWidget(revisar)
        botoes.addStretch(1)
        botoes.addWidget(fechar)
        layout.addLayout(botoes)

        self._visiveis = []
        self.filtrar("")
        self.busca.setFocus()

    def filtrar(self, texto):
        termo = _normalizar(texto)
        tokens = [t for t in termo.split() if t]
        visiveis = []
        for item in self.itens:
            alvo = _normalizar(f"{item.get('disciplina', '')} {item.get('topico', '')}")
            if all(token in alvo for token in tokens):
                visiveis.append(item)
        self._visiveis = visiveis[:300]
        self.tabela.setRowCount(len(self._visiveis))
        for linha, item in enumerate(self._visiveis):
            d = QTableWidgetItem(str(item.get("disciplina") or "—"))
            t = QTableWidgetItem(str(item.get("topico") or "—"))
            t.setData(Qt.UserRole, item)
            i = QTableWidgetItem(f"{int(item.get('importancia', 3) or 3)}/5")
            i.setTextAlignment(Qt.AlignCenter)
            self.tabela.setItem(linha, 0, d)
            self.tabela.setItem(linha, 1, t)
            self.tabela.setItem(linha, 2, i)
        if self._visiveis:
            self.tabela.selectRow(0)
        self.status.setText(
            f"{len(self._visiveis)} resultado(s)" + (" • refine a busca para reduzir a lista" if len(self._visiveis) >= 300 else "")
        )

    def _escolher(self, acao):
        linha = self.tabela.currentRow()
        if linha < 0 or linha >= len(self._visiveis):
            return
        self.resultado = dict(self._visiveis[linha])
        self.acao = str(acao)
        self.accept()
