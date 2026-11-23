"""VighnaNotes M1 — descobertas vinculadas a tópicos, sem alterar estudos.db.

Camada de dados SQLite independente da inteligência acadêmica. Uma anotação
é informação registrada pelo estudante; NÃO é evidência de domínio nem norma
jurídica validada. Dados locais, sem rede. Exportação explícita TXT/JSON.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QFileDialog, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QMessageBox,
    QPushButton, QSplitter, QTextEdit, QVBoxLayout, QWidget,
    QTabWidget, QFrame, QToolButton, QScrollArea, QStackedWidget,
    QGridLayout, QMenu, QStyledItemDelegate, QStyle,
)

CATEGORIAS = (
    ("complemento", "Complemento teórico"),
    ("excecao", "Exceção ou caso-limite"),
    ("duvida", "Dúvida a verificar"),
    ("correcao", "Possível correção de questão"),
)
CATEGORIA_TEXTO = dict(CATEGORIAS)


def _agora():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _identificador(valor):
    try:
        return int(valor) if valor not in (None, "") else None
    except (ValueError, TypeError):
        return None


class RepositorioVighnaNotes:
    """Armazenamento independente ao lado do banco acadêmico existente."""

    def __init__(self, caminho=None):
        if caminho is None:
            from caminhos import CAMINHO_BANCO
            caminho = Path(CAMINHO_BANCO).resolve().parent / "vighnanotes.db"
        self.caminho = Path(caminho)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        self._preparar()

    def _conectar(self):
        conn = sqlite3.connect(str(self.caminho), timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=10000")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _preparar(self):
        with self._conectar() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    perfil_id INTEGER NOT NULL DEFAULT 0,
                    disciplina TEXT NOT NULL DEFAULT '',
                    topico_id INTEGER,
                    topico TEXT NOT NULL DEFAULT '',
                    capitulo TEXT NOT NULL DEFAULT '',
                    microtema_id TEXT NOT NULL DEFAULT '',
                    questao_id INTEGER,
                    categoria TEXT NOT NULL DEFAULT 'complemento',
                    texto TEXT NOT NULL,
                    para_questoes INTEGER NOT NULL DEFAULT 1,
                    verificada INTEGER NOT NULL DEFAULT 0,
                    aproveitada INTEGER NOT NULL DEFAULT 0,
                    arquivada INTEGER NOT NULL DEFAULT 0,
                    criado_em TEXT NOT NULL,
                    atualizado_em TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vnotes_topico ON notas(perfil_id, topico_id, arquivada)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vnotes_questao ON notas(questao_id)")
            conn.execute("PRAGMA user_version=1")

    def salvar(self, *, id=None, perfil_id=0, disciplina='', topico_id=None,
               topico='', capitulo='', microtema_id='', questao_id=None,
               categoria='complemento', texto='', para_questoes=True,
               verificada=False, aproveitada=False):
        texto = str(texto).strip()
        if not texto:
            raise ValueError("A anotação precisa ter algum conteúdo.")
        if len(texto) > 25000:
            raise ValueError("A anotação excede o limite de 25.000 caracteres.")
        if categoria not in CATEGORIA_TEXTO:
            raise ValueError("Categoria de anotação inválida.")
        campos = dict(
            perfil_id=_identificador(perfil_id) or 0,
            disciplina=str(disciplina or '').strip()[:250],
            topico_id=_identificador(topico_id),
            topico=str(topico or '').strip()[:500],
            capitulo=str(capitulo or '').strip()[:500],
            microtema_id=str(microtema_id or '').strip()[:120],
            questao_id=_identificador(questao_id), categoria=categoria,
            texto=texto, para_questoes=int(bool(para_questoes)),
            verificada=int(bool(verificada)), aproveitada=int(bool(aproveitada)),
            atualizado_em=_agora(),
        )
        with self._conectar() as conn:
            if id is not None:
                existente = conn.execute("SELECT id FROM notas WHERE id=? AND arquivada=0", (int(id),)).fetchone()
                if existente is None:
                    raise ValueError("Anotação não encontrada ou arquivada.")
                keys = list(campos)
                conn.execute("UPDATE notas SET " + ", ".join(f"{k}=?" for k in keys) + " WHERE id=?",
                             [campos[k] for k in keys] + [int(id)])
                return int(id)
            campos['criado_em'] = campos['atualizado_em']
            keys = list(campos)
            cursor = conn.execute(
                "INSERT INTO notas (" + ",".join(keys) + ") VALUES (" + ",".join('?' for _ in keys) + ")",
                [campos[k] for k in keys],
            )
            return int(cursor.lastrowid)

    def buscar(self, *, perfil_id=0, topico_id=None, disciplina='', topico='',
               texto_busca='', apenas_futuras=False, incluir_arquivadas=False):
        cond = ["perfil_id=?"]
        params = [_identificador(perfil_id) or 0]
        if topico_id is not None:
            cond.append("topico_id=?")
            params.append(_identificador(topico_id))
        elif disciplina and topico:
            cond += ["disciplina=?", "topico=?"]
            params += [str(disciplina), str(topico)]
        elif disciplina:
            cond.append("disciplina=?")
            params.append(str(disciplina))
        if not incluir_arquivadas:
            cond.append("arquivada=0")
        if apenas_futuras:
            cond += ["para_questoes=1", "aproveitada=0"]
        if texto_busca.strip():
            cond.append("(texto LIKE ? OR topico LIKE ? OR disciplina LIKE ? OR capitulo LIKE ? OR microtema_id LIKE ?)")
            term = '%' + texto_busca.strip()[:200] + '%'
            params += [term] * 5
        query = "SELECT * FROM notas WHERE " + " AND ".join(cond) + " ORDER BY atualizado_em DESC, id DESC"
        with self._conectar() as conn:
            return [dict(row) for row in conn.execute(query, params)]

    def obter(self, id):
        with self._conectar() as conn:
            row = conn.execute("SELECT * FROM notas WHERE id=?", (int(id),)).fetchone()
            return dict(row) if row else None

    def arquivar(self, id):
        with self._conectar() as conn:
            conn.execute("UPDATE notas SET arquivada=1, atualizado_em=? WHERE id=?", (_agora(), int(id)))

    def restaurar(self, id):
        with self._conectar() as conn:
            conn.execute("UPDATE notas SET arquivada=0, atualizado_em=? WHERE id=?", (_agora(), int(id)))

    def criar_backup(self, destino):
        destino = Path(destino)
        if destino.resolve() == self.caminho.resolve():
            raise ValueError("Escolha outro arquivo para o backup.")
        with self._conectar() as origem, sqlite3.connect(str(destino)) as copia:
            origem.backup(copia)


def _exportar_txt(registros):
    linhas = ["VIGHNANOTES M1 — CADERNO DE DESCOBERTAS",
              "Anotações do estudante; conferir informações legais antes de gerar questões.",
              f"Exportação: {_agora()}", f"Registros: {len(registros)}", ""]
    for idx, nota in enumerate(registros, 1):
        linhas.extend([
            f"[{idx}] ID VighnaNotes: {nota['id']}",
            f"Disciplina: {nota['disciplina'] or 'Não informada'}",
            f"Tópico: {nota['topico'] or 'Não informado'} | ID: {nota['topico_id']}",
            f"Capítulo: {nota['capitulo'] or '—'} | Microtema: {nota['microtema_id'] or '—'}",
            f"Questão de origem: {nota['questao_id'] or '—'}",
            f"Categoria: {CATEGORIA_TEXTO.get(nota['categoria'], nota['categoria'])}",
            f"Usar em novas questões: {'SIM' if nota['para_questoes'] else 'NÃO'}",
            f"Conferência: {'VERIFICADA' if nota['verificada'] else 'PENDENTE'}",
            f"Já aproveitada: {'SIM' if nota['aproveitada'] else 'NÃO'}",
            "Observação:", nota['texto'], "", "-" * 60, "",
        ])
    return "\n".join(linhas)


class _NotaVisualDelegate(QStyledItemDelegate):
    """Cartões nativos na lista, sem widgets clicáveis adicionais."""

    def sizeHint(self, option, index):
        return QSize(max(180, option.rect.width()), 78)

    def paint(self, painter, option, index):
        titulo, assunto, situacao = index.data(Qt.UserRole + 1) or ("Anotação", "", "")
        selecionada = bool(option.state & QStyle.State_Selected)
        area = option.rect.adjusted(5, 3, -5, -3)
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QPen(QColor("#23C5DD" if selecionada else "#264B61"), 1))
        painter.setBrush(QColor("#17415A" if selecionada else "#0E293C"))
        painter.drawRoundedRect(area, 7, 7)

        esquerda = area.left() + 13
        largura = max(20, area.width() - 26)
        fonte = QFont("Segoe UI", 10)
        fonte.setWeight(QFont.DemiBold)
        painter.setFont(fonte)
        painter.setPen(QColor("#F0FAFF"))
        painter.drawText(QRect(esquerda, area.top() + 7, largura, 21),
                         Qt.AlignLeft | Qt.AlignVCenter,
                         painter.fontMetrics().elidedText(str(titulo), Qt.ElideRight, largura))

        fonte.setPointSize(9)
        fonte.setWeight(QFont.Normal)
        painter.setFont(fonte)
        painter.setPen(QColor("#A4C0CF"))
        painter.drawText(QRect(esquerda, area.top() + 29, largura, 17),
                         Qt.AlignLeft | Qt.AlignVCenter,
                         painter.fontMetrics().elidedText(str(assunto), Qt.ElideRight, largura))
        painter.setPen(QColor("#E0B970" if "próximas" in str(situacao) else "#7ED4E3"))
        painter.drawText(QRect(esquerda, area.top() + 48, largura, 17),
                         Qt.AlignLeft | Qt.AlignVCenter,
                         painter.fontMetrics().elidedText(str(situacao), Qt.ElideRight, largura))
        painter.restore()


class JanelaVighnaNotes(QDialog):
    """VighnaNotes M3: interface refinada, escrita e consulta independentes.

    O modelo de dados permanece o M1. Não há migração nem alteração acadêmica.
    """

    def __init__(self, *, contexto=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("VighnaNotes · Caderno de Descobertas")
        self.setObjectName("vighnaNotesM1Dialog")
        self.setWindowFlag(Qt.Window, True)
        self.setModal(False)
        self.resize(985, 650)
        self.setMinimumSize(735, 495)
        self.repo = RepositorioVighnaNotes()
        self.contexto = dict(contexto or {})
        self._id_em_edicao = None
        self._id_consulta = None
        self._notas_visiveis = []
        self._estado_salvo = None
        self.setStyleSheet("""
            /* M3 - identidade local, sem efeitos Gaussian/blur ou dependências externas */
            QDialog#vighnaNotesM1Dialog {
                background-color:#071A28; color:#EAF5FA;
                font-family:'Segoe UI'; font-size:12px;
            }
            QLabel { color:#D2E5EE; background:transparent; }
            QFrame#vnotesHero {
                background:#0C293C; border:1px solid #25495E; border-radius:9px;
            }
            QLabel#vnotesBrandMark {
                background:#123F56; color:#41D3E8;
                border:1px solid #2F8EA6; border-radius:8px;
                font-size:15px; font-weight:700;
            }
            QLabel#vnotesHeroTitle { color:#F2FBFF; font-size:19px; font-weight:700; }
            QLabel#vnotesHeroSub { color:#8DB8CA; font-size:10px; font-weight:600; }
            QLabel#vnotesHeroTag { color:#E0B970; font-size:10px; font-weight:600; }
            QTabWidget#vnotesTabs::pane {
                background:#091F30; border:1px solid #25485C;
                border-top:1px solid #25485C; border-radius:8px;
            }
            QTabWidget#vnotesTabs QTabBar::tab {
                background:#0D283B; color:#A8C7D7;
                border:1px solid #25495E; border-bottom:3px solid #25495E;
                border-top-left-radius:7px; border-top-right-radius:7px;
                padding:10px 22px; min-width:142px;
                font-weight:600; margin-right:3px;
            }
            QTabWidget#vnotesTabs QTabBar::tab:selected {
                background:#124157; color:#F7FCFF;
                border-bottom:3px solid #21BED7;
            }
            QTabWidget#vnotesTabs QTabBar::tab:hover:!selected {
                background:#17364A; color:#E3F5FC;
            }
            QFrame#vnotesContext {
                background:#0E2B40;
                border:1px solid #2D576A; border-left:3px solid #1BBAD5;
                border-radius:8px;
            }
            QLabel#vnotesContextEyebrow {
                color:#51C7DB; font-size:10px; font-weight:700;
            }
            QLabel#vnotesDisciplina { color:#F0FBFF; font-size:13px; font-weight:700; }
            QLabel#vnotesTopico { color:#C5E1EE; font-size:12px; }
            QLabel#vnotesContextHelp { color:#8FB5C6; font-size:10px; }
            QLabel#vnotesEditorTitle { font-size:14px; font-weight:700; color:#ECF9FF; }
            QLabel#vnotesCharCount { font-size:10px; color:#88ADBF; }
            QLineEdit,QTextEdit,QListWidget,QComboBox {
                background:#112F43; color:#EFFAFF; border:1px solid #31566C;
                border-radius:7px; padding:8px; selection-background-color:#187898;
                selection-color:#FFFFFF;
            }
            QTextEdit#vnotesWriter {
                background:#0C2538; border:1px solid #3B657B;
                font-family:'Segoe UI'; font-size:13px;
                padding:13px; border-radius:8px;
            }
            QTextEdit#vnotesWriter:focus { border:2px solid #23BAD4; padding:12px; }
            QTextEdit#vnotesPreview { background:#0B2436; border-color:#294E63; }
            QLineEdit:focus,QTextEdit:focus,QComboBox:focus {
                border:1px solid #22BDD7;
            }
            QComboBox {padding-right:12px;min-height:19px;}
            QComboBox QAbstractItemView {
                background:#102F42; color:#EDF8FE; selection-background-color:#175D7C;
                border:1px solid #367089;
            }
            QPushButton,QToolButton {
                background:#16394F; color:#DDEFF7; border:1px solid #315F78;
                border-radius:7px; padding:9px 14px; font-weight:600;
                min-height:18px;
            }
            QPushButton:hover,QToolButton:hover { background:#1B4D65; border-color:#4887A0; }
            QPushButton:pressed,QToolButton:pressed {background:#123447;}
            QPushButton:focus,QToolButton:focus {border-color:#24BBD6;}
            QPushButton:disabled,QToolButton:disabled {
                color:#7693A4; border-color:#264559; background:#102938;
            }
            QPushButton#vnotesSalvar {
                background:#087FA7; color:#FFFFFF;
                border:1px solid #25C4DC; font-weight:700;
            }
            QPushButton#vnotesSalvar:hover {background:#0A94BD;}
            QPushButton#vnotesArquivar {
                background:#102D3D; color:#C4D6DF;
                border:1px solid #355268;
            }
            QPushButton#vnotesArquivar:hover {background:#204054;}
            QToolButton#vnotesDetailsToggle {
                background:transparent; color:#9DDCE9; border:0;
                text-align:left; padding:7px 4px; font-weight:600;
            }
            QToolButton#vnotesDetailsToggle:hover {color:#E4FAFF; background:#102D42;}
            QFrame#vnotesDetails {
                background:#0C273A; border:1px solid #2A5267; border-radius:8px;
            }
            QFrame#vnotesNextCard {
                background:#103044; border:1px solid #27556D; border-radius:8px;
            }
            QCheckBox { color:#C5DEEA; spacing:8px; }
            /* Marcadores de checkbox nativos: mantém o símbolo de seleção do Windows/Qt. */
            QFrame#vnotesPreviewCard {
                background:#0B2639; border:1px solid #2E546B; border-radius:8px;
            }
            QLabel#vnotesPreviewTitle {color:#F0FBFF;font-size:14px;font-weight:700;}
            QLabel#vnotesPreviewInfo {color:#95BDCD;font-size:11px;}
            QListWidget#vnotesList {
                background:#091F31; border:1px solid #24495D; padding:4px;
            }
            QListWidget#vnotesList::item {border:0; padding:0;}
            QSplitter::handle {background:#2A4B5E; width:1px;}
            QScrollArea {border:0;background:transparent;}
            QScrollBar:vertical {
                background:#0B2637; width:10px; margin:1px;
            }
            QScrollBar::handle:vertical {
                background:#345F74; border-radius:4px; min-height:28px;
            }
            QScrollBar::handle:vertical:hover {background:#4387A1;}
            QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical {height:0;}
            QMenu {background:#0E2B3F;color:#ECF8FE;border:1px solid #396B84;}
            QMenu::item {padding:8px 20px;}
            QMenu::item:selected {background:#16546F;}
        """)
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(16, 13, 16, 12)
        raiz.setSpacing(9)
        hero = QFrame()
        hero.setObjectName("vnotesHero")
        faixa_titulo = QHBoxLayout(hero)
        faixa_titulo.setContentsMargins(14, 10, 14, 10)
        faixa_titulo.setSpacing(11)
        marca = QLabel("VN")
        marca.setObjectName("vnotesBrandMark")
        marca.setAlignment(Qt.AlignCenter)
        marca.setFixedSize(39, 39)
        faixa_titulo.addWidget(marca)
        textos = QVBoxLayout()
        textos.setSpacing(1)
        titulo = QLabel("VighnaNotes")
        titulo.setObjectName("vnotesHeroTitle")
        textos.addWidget(titulo)
        subtitulo = QLabel("CADERNO DE DESCOBERTAS")
        subtitulo.setObjectName("vnotesHeroSub")
        textos.addWidget(subtitulo)
        faixa_titulo.addLayout(textos)
        faixa_titulo.addStretch(1)
        marcador = QLabel("ESTUDO ORGANIZADO")
        marcador.setObjectName("vnotesHeroTag")
        faixa_titulo.addWidget(marcador)
        raiz.addWidget(hero)
        self.abas = QTabWidget()
        self.abas.setObjectName("vnotesTabs")
        self.abas.tabBar().setExpanding(False)
        raiz.addWidget(self.abas, 1)
        self._montar_editor()
        self._montar_consulta()
        self.abas.addTab(self.pagina_editor, "Nova anotação")
        self.abas.addTab(self.pagina_consulta, "Consultar caderno")
        self._nova(checar=False)
        self._recarregar()
        self.abas.setCurrentWidget(self.pagina_editor)
        self.texto.setFocus()

    def _montar_editor(self):
        self.pagina_editor = QWidget()
        pagina_layout = QVBoxLayout(self.pagina_editor)
        pagina_layout.setContentsMargins(10, 10, 10, 10)
        pagina_layout.setSpacing(7)

        rolagem = QScrollArea()
        rolagem.setWidgetResizable(True)
        rolagem.setFrameShape(QFrame.NoFrame)
        rolagem.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        bloco = QWidget()
        corpo = QVBoxLayout(bloco)
        corpo.setContentsMargins(6, 4, 8, 4)
        corpo.setSpacing(10)

        contexto_box = QFrame()
        contexto_box.setObjectName("vnotesContext")
        cb = QVBoxLayout(contexto_box)
        cb.setContentsMargins(13, 10, 13, 10)
        cb.setSpacing(3)
        contexto_eyebrow = QLabel("ASSUNTO VINCULADO")
        contexto_eyebrow.setObjectName("vnotesContextEyebrow")
        cb.addWidget(contexto_eyebrow)
        self.disciplina_resumo = QLabel("")
        self.disciplina_resumo.setObjectName("vnotesDisciplina")
        cb.addWidget(self.disciplina_resumo)
        self.topico_resumo = QLabel("")
        self.topico_resumo.setObjectName("vnotesTopico")
        self.topico_resumo.setWordWrap(True)
        cb.addWidget(self.topico_resumo)
        self.contexto_label = QLabel("Dados preenchidos automaticamente. Para alterar, abra Detalhes adicionais.")
        self.contexto_label.setObjectName("vnotesContextHelp")
        cb.addWidget(self.contexto_label)
        corpo.addWidget(contexto_box)

        titulo_linha = QHBoxLayout()
        texto_titulo = QLabel("O que você descobriu?")
        texto_titulo.setObjectName("vnotesEditorTitle")
        titulo_linha.addWidget(texto_titulo)
        titulo_linha.addStretch(1)
        self.contador_caracteres = QLabel("0 / 25.000")
        self.contador_caracteres.setObjectName("vnotesCharCount")
        titulo_linha.addWidget(self.contador_caracteres)
        corpo.addLayout(titulo_linha)
        self.texto = QTextEdit()
        self.texto.setObjectName("vnotesWriter")
        self.texto.textChanged.connect(self._atualizar_contador)
        self.texto.setAcceptRichText(False)
        self.texto.setMinimumHeight(180)
        self.texto.setPlaceholderText(
            "Registre uma regra, exceção, distinção ou ponto que precisa virar questão no futuro..."
        )
        corpo.addWidget(self.texto, 1)

        categoria_linha = QHBoxLayout()
        categoria_linha.addWidget(QLabel("Tipo de anotação"))
        self.categoria = QComboBox()
        for code, label in CATEGORIAS:
            self.categoria.addItem(label, code)
        self.categoria.setMinimumWidth(225)
        categoria_linha.addWidget(self.categoria)
        categoria_linha.addStretch(1)
        corpo.addLayout(categoria_linha)

        self.para_questoes = QCheckBox("Considerar na elaboração de novas questões")
        self.para_questoes.setChecked(True)
        opcao_card = QFrame()
        opcao_card.setObjectName("vnotesNextCard")
        opcao_layout = QVBoxLayout(opcao_card)
        opcao_layout.setContentsMargins(12, 8, 12, 8)
        opcao_layout.setSpacing(2)
        opcao_layout.addWidget(self.para_questoes)
        dica_questoes = QLabel("Levar esta descoberta para a próxima reformulação da bateria")
        dica_questoes.setStyleSheet("font-size:10px;color:#8FB6C6;padding-left:25px;")
        opcao_layout.addWidget(dica_questoes)
        corpo.addWidget(opcao_card)

        self.detalhes_botao = QToolButton()
        self.detalhes_botao.setObjectName("vnotesDetailsToggle")
        self.detalhes_botao.setText("Detalhes adicionais (opcional)")
        self.detalhes_botao.setArrowType(Qt.RightArrow)
        self.detalhes_botao.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.detalhes_botao.setCheckable(True)
        self.detalhes_botao.setChecked(False)
        self.detalhes_botao.toggled.connect(self._alternar_detalhes)
        corpo.addWidget(self.detalhes_botao, 0, Qt.AlignLeft)

        self.detalhes = QFrame()
        self.detalhes.setObjectName("vnotesDetails")
        grade = QGridLayout(self.detalhes)
        grade.setContentsMargins(13, 12, 13, 12)
        grade.setSpacing(8)
        self.disciplina = QLineEdit()
        self.topico = QLineEdit()
        self.topico_id = QLineEdit()
        self.capitulo = QLineEdit()
        self.microtema = QLineEdit()
        self.questao_origem = QLineEdit()
        self.questao_origem.setPlaceholderText("ID da questão, se houver")
        self.topico_id.setPlaceholderText("ID numérico")
        self.microtema.setPlaceholderText("Identificador ou descrição")
        for i, (rotulo, campo) in enumerate((
            ("Disciplina", self.disciplina),
            ("Tópico", self.topico),
            ("ID do tópico", self.topico_id),
            ("Capítulo", self.capitulo),
            ("Microtema", self.microtema),
            ("Questão de origem", self.questao_origem),
        )):
            coluna = i % 2
            linha = i // 2
            grade.addWidget(QLabel(rotulo), linha * 2, coluna)
            grade.addWidget(campo, linha * 2 + 1, coluna)
        rotulo_status = QLabel("Acompanhamento")
        rotulo_status.setStyleSheet("font-weight:700;color:#b6dceb;")
        grade.addWidget(rotulo_status, 6, 0, 1, 2)
        self.conferencia = QComboBox()
        self.conferencia.addItem("Pendente de conferência", False)
        self.conferencia.addItem("Conferida", True)
        self.aproveitamento = QComboBox()
        self.aproveitamento.addItem("Ainda não aproveitada", False)
        self.aproveitamento.addItem("Já aproveitada", True)
        grade.addWidget(QLabel("Conferência"), 7, 0)
        grade.addWidget(QLabel("Uso em nova bateria"), 7, 1)
        grade.addWidget(self.conferencia, 8, 0)
        grade.addWidget(self.aproveitamento, 8, 1)
        self.detalhes.setVisible(False)
        corpo.addWidget(self.detalhes)
        corpo.addStretch(1)
        rolagem.setWidget(bloco)
        pagina_layout.addWidget(rolagem, 1)

        faixa_botoes = QHBoxLayout()
        self.feedback = QLabel("")
        self.feedback.setStyleSheet("color:#7be0d8;font-size:11px;")
        faixa_botoes.addWidget(self.feedback, 1)
        self.botao_novo = QPushButton("Nova anotação")
        self.botao_novo.setObjectName("vnotesNovo")
        self.botao_novo.clicked.connect(self._nova)
        faixa_botoes.addWidget(self.botao_novo)
        self.salvar = QPushButton("Salvar anotação")
        self.salvar.setObjectName("vnotesSalvar")
        self.salvar.clicked.connect(self._salvar)
        faixa_botoes.addWidget(self.salvar)
        pagina_layout.addLayout(faixa_botoes)

        aviso = QLabel("As anotações não alteram as evidências do VighnaKnowledge.")
        aviso.setStyleSheet("color:#85aabc;font-size:11px;")
        pagina_layout.addWidget(aviso)

    def _montar_consulta(self):
        self.pagina_consulta = QWidget()
        layout = QVBoxLayout(self.pagina_consulta)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(9)
        self.busca = QLineEdit()
        self.busca.setPlaceholderText("Pesquisar por texto, disciplina, tópico ou microtema...")
        self.busca.textChanged.connect(self._recarregar)
        layout.addWidget(self.busca)

        filtros = QHBoxLayout()
        self.apenas_topico = QCheckBox("Somente o tópico atual")
        tem_topico = self.contexto.get("topico_id") is not None or bool(self.contexto.get("topico"))
        self._tem_topico_contexto = bool(tem_topico)
        self.apenas_topico.setVisible(self._tem_topico_contexto)
        self.apenas_topico.setChecked(bool(tem_topico))
        self.apenas_topico.toggled.connect(self._recarregar)
        filtros.addWidget(self.apenas_topico)
        self.apenas_pendentes = QCheckBox("Para novas questões")
        self.apenas_pendentes.toggled.connect(self._recarregar)
        filtros.addWidget(self.apenas_pendentes)
        self.mostrar_arquivadas = QCheckBox("Incluir arquivadas")
        self.mostrar_arquivadas.toggled.connect(self._recarregar)
        filtros.addWidget(self.mostrar_arquivadas)
        filtros.addStretch(1)
        layout.addLayout(filtros)

        self.resultados = QStackedWidget()
        layout.addWidget(self.resultados, 1)
        self.vazio = QWidget()
        vazio_layout = QVBoxLayout(self.vazio)
        vazio_layout.addStretch(1)
        self.vazio_titulo = QLabel("Nenhuma anotação neste filtro")
        self.vazio_titulo.setAlignment(Qt.AlignCenter)
        self.vazio_titulo.setStyleSheet("font-size:17px;font-weight:700;color:#e0f2fa;")
        vazio_layout.addWidget(self.vazio_titulo)
        self.vazio_sub = QLabel("Registre uma descoberta ou ajuste os filtros de consulta.")
        self.vazio_sub.setWordWrap(True)
        self.vazio_sub.setAlignment(Qt.AlignCenter)
        vazio_layout.addWidget(self.vazio_sub)
        ir_nova = QPushButton("Criar anotação")
        ir_nova.setObjectName("vnotesCriarVazio")
        ir_nova.clicked.connect(self._ir_para_nova)
        linha_nova = QHBoxLayout()
        linha_nova.addStretch(1)
        linha_nova.addWidget(ir_nova)
        linha_nova.addStretch(1)
        vazio_layout.addLayout(linha_nova)
        vazio_layout.addStretch(2)
        self.resultados.addWidget(self.vazio)

        self.paineis = QSplitter(Qt.Horizontal)
        self.lista = QListWidget()
        self.lista.setObjectName("vnotesList")
        self.lista.setItemDelegate(_NotaVisualDelegate(self.lista))
        self.lista.setSpacing(2)
        self.lista.currentItemChanged.connect(self._preview)
        self.paineis.addWidget(self.lista)
        detalhe = QFrame()
        detalhe.setObjectName("vnotesPreviewCard")
        detalhe_layout = QVBoxLayout(detalhe)
        detalhe_layout.setContentsMargins(14, 13, 14, 13)
        detalhe_layout.setSpacing(8)
        self.preview_cabecalho = QLabel("Selecione uma anotação")
        self.preview_cabecalho.setWordWrap(True)
        self.preview_cabecalho.setObjectName("vnotesPreviewTitle")
        detalhe_layout.addWidget(self.preview_cabecalho)
        self.preview_info = QLabel("")
        self.preview_info.setWordWrap(True)
        self.preview_info.setObjectName("vnotesPreviewInfo")
        detalhe_layout.addWidget(self.preview_info)
        self.preview_texto = QTextEdit()
        self.preview_texto.setObjectName("vnotesPreview")
        self.preview_texto.setReadOnly(True)
        detalhe_layout.addWidget(self.preview_texto, 1)
        preview_acoes = QHBoxLayout()
        self.editar = QPushButton("Editar anotação")
        self.editar.setObjectName("vnotesEditar")
        self.editar.clicked.connect(self._editar_selecionada)
        preview_acoes.addWidget(self.editar)
        self.botao_arquivar = QPushButton("Arquivar")
        self.botao_arquivar.setObjectName("vnotesArquivar")
        self.botao_arquivar.clicked.connect(self._arquivar)
        preview_acoes.addWidget(self.botao_arquivar)
        preview_acoes.addStretch(1)
        detalhe_layout.addLayout(preview_acoes)
        self.paineis.addWidget(detalhe)
        self.paineis.setStretchFactor(0, 2)
        self.paineis.setStretchFactor(1, 3)
        self.paineis.setSizes([340, 570])
        self.resultados.addWidget(self.paineis)

        rodape = QHBoxLayout()
        self.contador = QLabel("0 anotações")
        self.contador.setStyleSheet("color:#9cbfce;font-size:11px;")
        rodape.addWidget(self.contador)
        rodape.addStretch(1)
        ferramentas = QToolButton()
        ferramentas.setObjectName("vnotesFerramentas")
        ferramentas.setText("Exportar e backup")
        ferramentas.setPopupMode(QToolButton.InstantPopup)
        menu = QMenu(ferramentas)
        menu.addAction("Exportar TXT", lambda: self._exportar("txt"))
        menu.addAction("Exportar JSON", lambda: self._exportar("json"))
        menu.addSeparator()
        menu.addAction("Backup do caderno", self._backup)
        ferramentas.setMenu(menu)
        rodape.addWidget(ferramentas)
        layout.addLayout(rodape)
        self._habilitar_preview(False)

    def _atualizar_contador(self):
        self.contador_caracteres.setText(f"{len(self.texto.toPlainText()):,} / 25.000".replace(",", "."))

    def _alternar_detalhes(self, aberto):
        self.detalhes.setVisible(bool(aberto))
        self.detalhes_botao.setArrowType(Qt.DownArrow if aberto else Qt.RightArrow)

    def _snapshot(self):
        return (
            self._id_em_edicao, self.disciplina.text(), self.topico.text(),
            self.topico_id.text(), self.capitulo.text(), self.microtema.text(),
            self.questao_origem.text(), self.categoria.currentData(),
            self.texto.toPlainText(), self.para_questoes.isChecked(),
            self.conferencia.currentData(), self.aproveitamento.currentData(),
        )

    def _rascunho_alterado(self):
        return self._estado_salvo is not None and self._snapshot() != self._estado_salvo

    def _confirmar_descarte(self):
        if not self._rascunho_alterado():
            return True
        return QMessageBox.question(
            self, "Anotação não salva",
            "Existem alterações não salvas. Deseja descartá-las?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        ) == QMessageBox.Yes

    def closeEvent(self, event):
        if self._confirmar_descarte():
            super().closeEvent(event)
        else:
            event.ignore()

    def _contexto_resumo(self):
        return (str(self.contexto.get("disciplina") or "Disciplina não especificada") +
                (" · " + str(self.contexto["topico"]) if self.contexto.get("topico") else ""))

    def _atualizar_contexto_editor(self):
        self.disciplina_resumo.setText(self.disciplina.text().strip() or "Disciplina não especificada")
        self.topico_resumo.setText(self.topico.text().strip() or "Sem tópico específico")

    def _nova(self, *_, checar=True):
        if checar and not self._confirmar_descarte():
            return False
        c = self.contexto
        self._id_em_edicao = None
        for campo, chave in ((self.disciplina, "disciplina"), (self.topico, "topico"),
                              (self.capitulo, "capitulo"), (self.microtema, "microtema_id")):
            campo.setText(str(c.get(chave) or ""))
        self.topico_id.setText(str(c["topico_id"]) if c.get("topico_id") is not None else "")
        self.questao_origem.setText(str(c["questao_id"]) if c.get("questao_id") is not None else "")
        self.categoria.setCurrentIndex(0)
        self.texto.clear()
        self.para_questoes.setChecked(True)
        self.conferencia.setCurrentIndex(0)
        self.aproveitamento.setCurrentIndex(0)
        self.salvar.setText("Salvar anotação")
        self.salvar.setEnabled(True)
        self.abas.setTabText(self.abas.indexOf(self.pagina_editor), "Nova anotação")
        self.feedback.clear()
        self.detalhes_botao.setChecked(False)
        self._atualizar_contexto_editor()
        self._estado_salvo = self._snapshot()
        return True

    def _ir_para_nova(self):
        if self._nova():
            self.abas.setCurrentWidget(self.pagina_editor)
            self.texto.setFocus()

    def _recarregar(self, *_):
        try:
            c = self.contexto
            no_topico = self.apenas_topico.isChecked() and self._tem_topico_contexto
            self._notas_visiveis = self.repo.buscar(
                perfil_id=c.get("perfil_id"),
                topico_id=c.get("topico_id") if no_topico else None,
                disciplina=c.get("disciplina", "") if no_topico else "",
                topico=c.get("topico", "") if no_topico else "",
                texto_busca=self.busca.text(),
                apenas_futuras=self.apenas_pendentes.isChecked(),
                incluir_arquivadas=self.mostrar_arquivadas.isChecked(),
            )
        except Exception as exc:
            QMessageBox.warning(self, "Caderno", "Não foi possível consultar as anotações:\n" + str(exc))
            return
        anterior = self._id_consulta
        self.lista.blockSignals(True)
        self.lista.clear()
        selecionado = -1
        for i, nota in enumerate(self._notas_visiveis):
            trecho = nota["texto"].strip().splitlines()[0][:73]
            subtitulo = nota["topico"] or nota["disciplina"] or "Sem tópico"
            estado = ("Arquivada" if nota["arquivada"] else
                      "Para próximas questões" if nota["para_questoes"] and not nota["aproveitada"] else
                      "Já aproveitada" if nota["aproveitada"] else "Anotação")
            item = QListWidgetItem(trecho)
            item.setData(Qt.UserRole, int(nota["id"]))
            item.setData(Qt.UserRole + 1, (trecho, subtitulo, estado))
            self.lista.addItem(item)
            if nota["id"] == anterior:
                selecionado = i
        self.lista.blockSignals(False)
        quantidade = len(self._notas_visiveis)
        self.contador.setText(f"{quantidade} anotação(ões) encontradas")
        self.resultados.setCurrentWidget(self.paineis if quantidade else self.vazio)
        if not quantidade:
            self._id_consulta = None
            self.vazio_titulo.setText("Nenhuma anotação neste filtro")
            self.vazio_sub.setText("Registre sua primeira descoberta ou ajuste os filtros de consulta.")
            self._habilitar_preview(False)
        else:
            self.lista.setCurrentRow(max(0, selecionado))
            self._preview(self.lista.currentItem(), None)

    def _habilitar_preview(self, habilitar):
        self.editar.setEnabled(habilitar)
        self.botao_arquivar.setEnabled(habilitar)
        if not habilitar:
            self.preview_cabecalho.setText("Selecione uma anotação")
            self.preview_info.clear()
            self.preview_texto.clear()

    def _preview(self, item, _anterior):
        if item is None:
            self._id_consulta = None
            self._habilitar_preview(False)
            return
        nota = self.repo.obter(item.data(Qt.UserRole))
        if not nota:
            self._id_consulta = None
            self._habilitar_preview(False)
            return
        self._id_consulta = int(nota["id"])
        self.preview_cabecalho.setText(nota["topico"] or nota["disciplina"] or "Anotação")
        detalhes = [nota["disciplina"], CATEGORIA_TEXTO.get(nota["categoria"], "")]
        if nota["capitulo"]:
            detalhes.append("Capítulo: " + nota["capitulo"])
        if nota["microtema_id"]:
            detalhes.append("Microtema: " + nota["microtema_id"])
        if nota["para_questoes"] and not nota["aproveitada"]:
            detalhes.append("Para novas questões")
        if nota["verificada"]:
            detalhes.append("Conferida")
        if nota["aproveitada"]:
            detalhes.append("Já aproveitada")
        if nota["arquivada"]:
            detalhes.append("Arquivada")
        self.preview_info.setText(" · ".join(p for p in detalhes if p))
        self.preview_texto.setPlainText(nota["texto"])
        self.editar.setEnabled(not bool(nota["arquivada"]))
        self.botao_arquivar.setEnabled(True)
        self.botao_arquivar.setText("Restaurar" if nota["arquivada"] else "Arquivar")

    def _editar_selecionada(self):
        if self._id_consulta is None:
            return
        nota = self.repo.obter(self._id_consulta)
        if not nota or nota["arquivada"] or not self._confirmar_descarte():
            return
        self._id_em_edicao = int(nota["id"])
        self.disciplina.setText(nota["disciplina"])
        self.topico.setText(nota["topico"])
        self.topico_id.setText(str(nota["topico_id"]) if nota["topico_id"] is not None else "")
        self.capitulo.setText(nota["capitulo"])
        self.microtema.setText(nota["microtema_id"])
        self.questao_origem.setText(str(nota["questao_id"]) if nota["questao_id"] is not None else "")
        self.categoria.setCurrentIndex(max(0, self.categoria.findData(nota["categoria"])))
        self.texto.setPlainText(nota["texto"])
        self.para_questoes.setChecked(bool(nota["para_questoes"]))
        self.conferencia.setCurrentIndex(1 if nota["verificada"] else 0)
        self.aproveitamento.setCurrentIndex(1 if nota["aproveitada"] else 0)
        self.salvar.setText("Salvar alterações")
        self.salvar.setEnabled(True)
        self.feedback.clear()
        self._atualizar_contexto_editor()
        self.abas.setTabText(self.abas.indexOf(self.pagina_editor), "Editar anotação")
        self._estado_salvo = self._snapshot()
        self.abas.setCurrentWidget(self.pagina_editor)
        self.texto.setFocus()

    def _salvar(self):
        try:
            novo_id = self.repo.salvar(
                id=self._id_em_edicao,
                perfil_id=self.contexto.get("perfil_id"),
                disciplina=self.disciplina.text(), topico_id=self.topico_id.text(),
                topico=self.topico.text(), capitulo=self.capitulo.text(),
                microtema_id=self.microtema.text(), questao_id=self.questao_origem.text(),
                categoria=self.categoria.currentData(), texto=self.texto.toPlainText(),
                para_questoes=self.para_questoes.isChecked(),
                verificada=bool(self.conferencia.currentData()),
                aproveitada=bool(self.aproveitamento.currentData()),
            )
        except (ValueError, sqlite3.Error, OSError) as exc:
            QMessageBox.warning(self, "Não foi possível salvar", str(exc))
            return
        self._id_em_edicao = novo_id
        self._atualizar_contexto_editor()
        self._estado_salvo = self._snapshot()
        self.abas.setTabText(self.abas.indexOf(self.pagina_editor), "Editar anotação")
        self.salvar.setText("Salvar alterações")
        self.feedback.setText("Anotação salva.")
        self._recarregar()

    def _arquivar(self):
        if self._id_consulta is None:
            return
        nota = self.repo.obter(self._id_consulta)
        if not nota:
            return
        arquivada = bool(nota["arquivada"])
        mensagem = ("Restaurar esta anotação para o caderno?" if arquivada
                    else "Arquivar esta anotação? Ela não será apagada do banco.")
        if QMessageBox.question(
            self, "Restaurar anotação" if arquivada else "Arquivar anotação",
            mensagem, QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        ) != QMessageBox.Yes:
            return
        if self._id_em_edicao == self._id_consulta and not self._confirmar_descarte():
            return
        try:
            if arquivada:
                self.repo.restaurar(self._id_consulta)
            else:
                self.repo.arquivar(self._id_consulta)
        except (sqlite3.Error, OSError) as exc:
            QMessageBox.warning(self, "Caderno", str(exc))
            return
        if self._id_em_edicao == self._id_consulta:
            self._nova(checar=False)
        self._recarregar()

    def _exportar(self, formato):
        if not self._notas_visiveis:
            QMessageBox.information(self, "Caderno", "Nenhuma anotação para exportar com os filtros atuais.")
            return
        extensao = ".txt" if formato == "txt" else ".json"
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Exportar anotações", "VighnaNotes_Anotacoes" + extensao,
            "Arquivo de texto (*.txt)" if formato == "txt" else "JSON (*.json)",
        )
        if not caminho:
            return
        try:
            if formato == "txt":
                Path(caminho).write_text(_exportar_txt(self._notas_visiveis), encoding="utf-8-sig")
            else:
                dados = {"formato": "VighnaNotes-M1", "exportado_em": _agora(),
                         "aviso": "Anotações do estudante. Exigem conferência legal.",
                         "notas": self._notas_visiveis}
                Path(caminho).write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Exportação", "Não foi possível exportar:\n" + str(exc))
            return
        QMessageBox.information(self, "Exportação", "Arquivo salvo:\n" + caminho)

    def _backup(self):
        destino, _ = QFileDialog.getSaveFileName(
            self, "Backup do Caderno de Descobertas", "vighnanotes_backup.db",
            "Banco SQLite (*.db)",
        )
        if not destino:
            return
        try:
            self.repo.criar_backup(destino)
        except (sqlite3.Error, OSError, ValueError) as exc:
            QMessageBox.warning(self, "Backup", "Não foi possível criar backup:\n" + str(exc))
            return
        QMessageBox.information(self, "Backup", "Backup concluído:\n" + destino)


def abrir_caderno(parent=None, contexto=None):
    """Abre o editor por padrão e preserva rascunhos se a janela já existir."""
    if parent is None:
        raise ValueError("É necessário informar a janela de origem.")
    novo_contexto = dict(contexto or {})
    antiga = getattr(parent, "_janela_vighnanotes_m1", None)
    if antiga is not None and antiga.isVisible():
        if antiga.contexto == novo_contexto:
            antiga.abas.setCurrentWidget(antiga.pagina_editor)
            antiga.raise_()
            antiga.activateWindow()
            antiga.texto.setFocus()
            return antiga
        antiga.close()
        if antiga.isVisible():  # usuário cancelou o descarte do rascunho
            antiga.raise_()
            antiga.activateWindow()
            return antiga
    dlg = JanelaVighnaNotes(contexto=novo_contexto, parent=parent)
    parent._janela_vighnanotes_m1 = dlg
    dlg.show()
    dlg.raise_()
    dlg.activateWindow()
    dlg.texto.setFocus()
    return dlg
