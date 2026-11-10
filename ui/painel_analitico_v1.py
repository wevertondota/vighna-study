"""Central Analítica V1 — tela de acesso, sem duplicar Relatórios/Estatísticas.

Somente consultas leves no banco. Não calcula notas acadêmicas nem altera
Histórico V2; reutiliza os controladores existentes do aplicativo principal.
"""
from __future__ import annotations

from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget,
)

from ui.tempo_baterias_v1 import formatar_duracao, obter_resumo_diario


_TITULOS = (
    ("tempo", "TEMPO EFETIVO HOJE", "0min"),
    ("baterias", "BATERIAS FINALIZADAS", "0"),
    ("pausas", "PAUSAS DESCONTADAS", "0min"),
    ("questoes", "QUESTÕES RESPONDIDAS", "0"),
    ("acertos", "ACERTOS NO DIA", "0"),
    ("desempenho", "DESEMPENHO DO DIA", "—"),
)


class PainelAnaliticoV1(QWidget):
    """Tela principal da nova área Análises; os destinos continuam separados."""

    def __init__(self, *, abrir_relatorios, abrir_estatisticas, abrir_historico,
                 caminho_banco, tema="futurista", parent=None):
        super().__init__(parent)
        self.setObjectName("analiticoRaiz")
        self._caminho_banco = caminho_banco

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea(self)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setObjectName("analiticoScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        raiz.addWidget(scroll)
        conteudo = QWidget()
        conteudo.setObjectName("analiticoConteudo")
        corpo = QVBoxLayout(conteudo)
        corpo.setContentsMargins(26, 22, 26, 22)
        corpo.setSpacing(16)

        tag = QLabel("ARQUIVO NEURAL  /  CENTRAL DE ANÁLISES")
        tag.setObjectName("analiticoTag")
        corpo.addWidget(tag)
        titulo = QLabel("Relatórios, Estatísticas e Histórico")
        titulo.setObjectName("analiticoTitulo")
        titulo.setWordWrap(True)
        corpo.addWidget(titulo)
        desc = QLabel("Indicadores essenciais do dia e acesso direto às análises existentes do VighnaStudy.")
        desc.setObjectName("analiticoDescricao")
        desc.setWordWrap(True)
        corpo.addWidget(desc)

        acessos = QGridLayout()
        acessos.setHorizontalSpacing(12)
        acessos.setVerticalSpacing(10)
        for i, (nome, complemento, acao) in enumerate((
            ("Relatórios", "Documentos e análises detalhadas", abrir_relatorios),
            ("Estatísticas", "Desempenho, evolução e indicadores", abrir_estatisticas),
            ("Histórico acadêmico", "Visão consolidada do Histórico V2", abrir_historico),
        )):
            acesso = QPushButton(nome)
            acesso.setObjectName("analiticoAcesso")
            acesso.setMinimumHeight(60)
            acesso.setCursor(Qt.PointingHandCursor)
            acesso.setToolTip(complemento)
            acesso.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            acesso.clicked.connect(lambda _checked=False, fn=acao: fn())
            acessos.addWidget(acesso, 0, i)
            acessos.setColumnStretch(i, 1)
        corpo.addLayout(acessos)

        divisao = QLabel("PANORAMA DO DIA  /  TODOS OS PERFIS")
        divisao.setObjectName("analiticoSecao")
        corpo.addWidget(divisao)

        self._valores = {}
        indicadores = QGridLayout()
        indicadores.setHorizontalSpacing(12)
        indicadores.setVerticalSpacing(12)
        for i, (chave, rotulo, inicial) in enumerate(_TITULOS):
            card = QFrame()
            card.setObjectName("analiticoCardDestaque" if i == 0 else "analiticoCard")
            col = QVBoxLayout(card)
            col.setContentsMargins(18, 13, 18, 14)
            col.setSpacing(7)
            label = QLabel(rotulo)
            label.setObjectName("analiticoCardRotulo")
            col.addWidget(label)
            valor = QLabel(inicial)
            valor.setObjectName("analiticoCardValor")
            valor.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            col.addWidget(valor)
            self._valores[chave] = valor
            indicadores.addWidget(card, i // 3, i % 3)
            indicadores.setColumnStretch(i % 3, 1)
        corpo.addLayout(indicadores)

        formula = QFrame()
        formula.setObjectName("analiticoMetodo")
        method_box = QVBoxLayout(formula)
        method_box.setContentsMargins(16, 12, 16, 12)
        method_box.setSpacing(5)
        metodo_titulo = QLabel("COMO O TEMPO É CALCULADO")
        metodo_titulo.setObjectName("analiticoMetodoTitulo")
        method_box.addWidget(metodo_titulo)
        metodo = QLabel(
            "Tempo efetivamente estudado = duração da bateria aberta − tempo acumulado "
            "das pausas. O saldo de cada bateria finalizada é somado ao respectivo "
            "dia; sessões que atravessam a meia-noite são divididas por data."
        )
        metodo.setObjectName("analiticoMetodoTexto")
        metodo.setWordWrap(True)
        method_box.addWidget(metodo)
        observacao = QLabel(
            "O contador de tempo começa após esta atualização. Sessões antigas não "
            "possuem histórico persistente de pausas e não são estimadas. "
            "Questões/acertos exibem os registros acadêmicos do dia já existentes. "
            "Uma bateria em andamento só entra no saldo ao ser encerrada."
        )
        observacao.setObjectName("analiticoObservacao")
        observacao.setWordWrap(True)
        method_box.addWidget(observacao)
        corpo.addWidget(formula)

        rodape = QHBoxLayout()
        self._atualizado = QLabel("—")
        self._atualizado.setObjectName("analiticoAtualizado")
        rodape.addWidget(self._atualizado, 1)
        recarregar = QPushButton("Atualizar indicadores")
        recarregar.setObjectName("analiticoAtualizar")
        recarregar.setCursor(Qt.PointingHandCursor)
        recarregar.clicked.connect(self.atualizar_dados)
        rodape.addWidget(recarregar)
        corpo.addLayout(rodape)
        corpo.addStretch(1)
        scroll.setWidget(conteudo)
        self.aplicar_tema(tema)

    def aplicar_tema(self, tema):
        modo = str(tema or "futurista").lower()
        claro = "claro" in modo and "escuro" not in modo
        fundo = "#f5f8fb" if claro else "#061626"
        painel = "#ffffff" if claro else "#0b283e"
        painel2 = "#edf5fb" if claro else "#102f46"
        texto = "#12293b" if claro else "#f5faff"
        secundario = "#435e73" if claro else "#a9cce3"
        borda = "#a6cfe2" if claro else "#216789"
        acento = "#007aa6" if claro else "#40cfff"
        self.setStyleSheet(f"""
            QWidget#analiticoRaiz, QWidget#analiticoConteudo,
            QScrollArea#analiticoScroll {{ background: {fundo}; border: none; }}
            QLabel#analiticoTag, QLabel#analiticoSecao {{ color: {acento};
                font-size: 10px; font-weight: 800; letter-spacing: 1px; background: transparent; }}
            QLabel#analiticoTitulo {{ color: {texto}; font-size: 22px;
                font-weight: 800; background: transparent; }}
            QLabel#analiticoDescricao, QLabel#analiticoAtualizado {{ color: {secundario};
                font-size: 12px; background: transparent; }}
            QPushButton#analiticoAcesso {{ color: {texto}; background: {painel2};
                border: 1px solid {borda}; border-radius: 10px; padding: 10px 14px;
                text-align: left; font-weight: 700; font-size: 14px; }}
            QPushButton#analiticoAcesso:hover, QPushButton#analiticoAcesso:focus {{
                border-color: {acento}; }}
            QFrame#analiticoCard, QFrame#analiticoCardDestaque {{ background: {painel};
                border: 1px solid {borda}; border-radius: 11px; }}
            QFrame#analiticoCardDestaque {{ border: 1px solid {acento}; }}
            QLabel#analiticoCardRotulo {{ color: {secundario}; background: transparent;
                border: none; font-size: 10px; font-weight: 700; }}
            QLabel#analiticoCardValor {{ color: {texto}; background: transparent;
                border: none; font-size: 24px; font-weight: 800; }}
            QFrame#analiticoMetodo {{ background: {painel2}; border: 1px solid {borda};
                border-radius: 9px; }}
            QLabel#analiticoMetodoTitulo {{ color: {acento}; background: transparent;
                border: none; font-size: 11px; font-weight: 700; }}
            QLabel#analiticoMetodoTexto, QLabel#analiticoObservacao {{ color: {secundario};
                background: transparent; border: none; font-size: 12px; }}
            QPushButton#analiticoAtualizar {{ background: {painel2}; color: {texto};
                border: 1px solid {borda}; border-radius: 8px; padding: 8px 14px; }}
            QPushButton#analiticoAtualizar:hover {{ border-color: {acento}; }}
        """)

    def atualizar_dados(self):
        try:
            dados = obter_resumo_diario(self._caminho_banco)
        except Exception as exc:
            self._atualizado.setText(f"Indicadores indisponíveis: {str(exc)[:180]}")
            return
        respondidas = dados["acertos"] + dados["erros"]
        atualizacoes = {
            "tempo": formatar_duracao(dados["tempo_liquido_segundos"]),
            "baterias": str(dados["baterias"]),
            "pausas": formatar_duracao(dados["pausa_segundos"]),
            "questoes": str(respondidas),
            "acertos": str(dados["acertos"]),
            "desempenho": f"{100 * dados['acertos'] / respondidas:.1f}%" if respondidas else "—",
        }
        for chave, valor in atualizacoes.items():
            self._valores[chave].setText(valor)
        self._atualizado.setText(
            "Atualizado em " + datetime.now().strftime("%d/%m/%Y às %H:%M")
            + "  •  Tempo total de baterias concluídas (todos os perfis)"
        )
