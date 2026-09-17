"""Busca global e navegação rápida do VighnaStudy."""

from __future__ import annotations

import difflib
import unicodedata

from PySide6.QtCore import Qt, QEvent
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


def _pontuar_item(item, termo):
    """Pontua correspondência direta e aproximada sem exigir digitação exata."""
    termo = _normalizar(termo)
    if not termo:
        return float(item.get("prioridade", 0) or 0)

    titulo = _normalizar(item.get("titulo"))
    categoria = _normalizar(item.get("categoria"))
    descricao = _normalizar(item.get("descricao"))
    termos = _normalizar(item.get("termos"))
    alvo = " ".join((titulo, categoria, descricao, termos)).strip()
    tokens = [t for t in termo.split() if t]

    if not alvo:
        return -1

    score = 0.0
    if termo == titulo:
        score += 180
    elif titulo.startswith(termo):
        score += 120
    elif termo in titulo:
        score += 95
    elif termo in alvo:
        score += 70

    palavras = alvo.split()
    for token in tokens:
        if token in titulo:
            score += 34
            continue
        if token in alvo:
            score += 22
            continue

        # Pequenos erros de digitação continuam encontrando a opção desejada.
        melhor = 0.0
        for palavra in palavras:
            if len(token) < 3 or len(palavra) < 3:
                continue
            melhor = max(melhor, difflib.SequenceMatcher(None, token, palavra).ratio())
        if melhor >= 0.72:
            score += 15 * melhor
        elif melhor >= 0.60 and len(token) >= 5:
            score += 8 * melhor
        else:
            return -1

    score += float(item.get("prioridade", 0) or 0) * 0.05
    return score


class JanelaBuscaGlobal(QDialog):
    """Command palette do VighnaStudy.

    Recebe comandos principais e, opcionalmente, tópicos do perfil ativo. Em
    branco mostra atalhos/recentes; ao digitar, pesquisa ferramentas, ações e
    tópicos com tolerância a pequenas variações de escrita.
    """

    def __init__(self, comandos, topicos=None, recentes=None, parent=None):
        super().__init__(parent)
        self.comandos = [dict(item) for item in (comandos or [])]
        self.topicos = [dict(item) for item in (topicos or [])]
        self.recentes = [str(item) for item in (recentes or []) if item]
        self.resultado = None
        self.acao = None
        self._visiveis = []

        self.setObjectName("globalSearchDialog")
        self.setWindowTitle("Buscar no Vighna")
        self.resize(780, 510)
        self.setMinimumSize(640, 420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        topo = QHBoxLayout()
        topo.setSpacing(10)
        titulo_bloco = QVBoxLayout()
        titulo_bloco.setSpacing(1)

        titulo = QLabel("Buscar no Vighna")
        titulo.setObjectName("globalSearchTitle")
        subtitulo = QLabel(
            "Encontre telas, ferramentas, ações e tópicos sem percorrer os menus."
        )
        subtitulo.setObjectName("globalSearchSubtitle")
        subtitulo.setWordWrap(True)
        titulo_bloco.addWidget(titulo)
        titulo_bloco.addWidget(subtitulo)

        atalho = QLabel("Ctrl+K")
        atalho.setObjectName("globalSearchShortcut")
        atalho.setAlignment(Qt.AlignCenter)

        topo.addLayout(titulo_bloco, 1)
        topo.addWidget(atalho, 0, Qt.AlignTop | Qt.AlignRight)
        layout.addLayout(topo)

        self.busca = QLineEdit()
        self.busca.setObjectName("globalSearchInput")
        self.busca.setPlaceholderText("Buscar telas, ferramentas, ações e tópicos…")
        self.busca.setClearButtonEnabled(True)
        self.busca.textChanged.connect(self.filtrar)
        self.busca.returnPressed.connect(self._escolher_atual)
        layout.addWidget(self.busca)

        self.tabela = QTableWidget(0, 3)
        self.tabela.setObjectName("globalSearchResults")
        self.tabela.setHorizontalHeaderLabels(["Categoria", "Opção", "Atalho"])
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabela.setShowGrid(False)
        self.tabela.horizontalHeader().setStretchLastSection(False)
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabela.doubleClicked.connect(lambda _idx: self._escolher_atual())
        layout.addWidget(self.tabela, 1)

        rodape = QHBoxLayout()
        self.status = QLabel("")
        self.status.setObjectName("globalSearchStatus")
        dica = QLabel("↑↓ navegar  •  Enter abrir  •  Esc fechar")
        dica.setObjectName("globalSearchHint")
        rodape.addWidget(self.status, 1)
        rodape.addWidget(dica, 0, Qt.AlignRight)
        layout.addLayout(rodape)

        fechar = QPushButton("Fechar")
        fechar.setObjectName("globalSearchCloseButton")
        fechar.clicked.connect(self.reject)
        fechar.setVisible(False)
        layout.addWidget(fechar)

        self.busca.installEventFilter(self)
        self.filtrar("")
        self.busca.setFocus()

    def eventFilter(self, objeto, evento):
        if objeto is self.busca and evento.type() == QEvent.KeyPress:
            if evento.key() in (Qt.Key_Down, Qt.Key_Up):
                total = self.tabela.rowCount()
                if total <= 0:
                    return True
                atual = self.tabela.currentRow()
                if atual < 0:
                    atual = 0
                elif evento.key() == Qt.Key_Down:
                    atual = min(total - 1, atual + 1)
                else:
                    atual = max(0, atual - 1)
                self.tabela.selectRow(atual)
                self.tabela.scrollToItem(self.tabela.item(atual, 1))
                return True
        return super().eventFilter(objeto, evento)

    def _itens_iniciais(self):
        por_id = {
            str(item.get("id")): item
            for item in self.comandos
            if item.get("id")
        }
        escolhidos = []
        vistos = set()

        for comando_id in self.recentes[:5]:
            item = por_id.get(comando_id)
            if not item or comando_id in vistos:
                continue
            copia = dict(item)
            copia["categoria_exibicao"] = "RECENTES"
            escolhidos.append(copia)
            vistos.add(comando_id)

        ordenados = sorted(
            self.comandos,
            key=lambda item: (-int(item.get("prioridade", 0) or 0), str(item.get("titulo") or "")),
        )
        for item in ordenados:
            comando_id = str(item.get("id") or "")
            if comando_id in vistos:
                continue
            copia = dict(item)
            copia["categoria_exibicao"] = "ACESSO RÁPIDO"
            escolhidos.append(copia)
            if comando_id:
                vistos.add(comando_id)
            if len(escolhidos) >= 10:
                break
        return escolhidos

    def filtrar(self, texto):
        termo = _normalizar(texto)
        if not termo:
            visiveis = self._itens_iniciais()
            mensagem = "Acesso rápido" if not self.recentes else "Ações recentes e acesso rápido"
        else:
            candidatos = []
            for item in self.comandos:
                copia = dict(item)
                copia.setdefault("tipo", "comando")
                candidatos.append(copia)
            for topico in self.topicos:
                candidatos.append({
                    "tipo": "topico",
                    "id": f"topico:{topico.get('topico_id')}",
                    "categoria": "TÓPICOS",
                    "titulo": str(topico.get("topico") or "—"),
                    "descricao": str(topico.get("disciplina") or "—"),
                    "termos": (
                        f"{topico.get('disciplina', '')} {topico.get('topico', '')} "
                        "estudar revisar questoes questões"
                    ),
                    "prioridade": 5,
                    "atalho": "",
                    "topico": topico,
                })

            pontuados = []
            for item in candidatos:
                score = _pontuar_item(item, termo)
                if score >= 0:
                    pontuados.append((score, item))
            pontuados.sort(
                key=lambda par: (-par[0], str(par[1].get("titulo") or ""))
            )
            visiveis = [item for _score, item in pontuados[:80]]
            mensagem = f"{len(visiveis)} resultado(s)"

        self._visiveis = visiveis
        self.tabela.setRowCount(len(visiveis))
        for linha, item in enumerate(visiveis):
            categoria = str(item.get("categoria_exibicao") or item.get("categoria") or "GERAL")
            titulo = str(item.get("titulo") or "—")
            descricao = str(item.get("descricao") or "").strip()
            atalho = str(item.get("atalho") or "")
            texto_opcao = titulo if not descricao else f"{titulo}   ·   {descricao}"

            c = QTableWidgetItem(categoria)
            o = QTableWidgetItem(texto_opcao)
            a = QTableWidgetItem(atalho)
            a.setTextAlignment(Qt.AlignCenter)
            o.setData(Qt.UserRole, item)
            self.tabela.setItem(linha, 0, c)
            self.tabela.setItem(linha, 1, o)
            self.tabela.setItem(linha, 2, a)
            self.tabela.setRowHeight(linha, 38)

        if visiveis:
            self.tabela.selectRow(0)
        self.status.setText(mensagem)

    def _escolher_atual(self):
        linha = self.tabela.currentRow()
        if linha < 0 or linha >= len(self._visiveis):
            return
        self.resultado = dict(self._visiveis[linha])
        self.acao = str(self.resultado.get("id") or "")
        self.accept()
