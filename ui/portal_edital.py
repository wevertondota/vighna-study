"""Área inicial (sem dados inventados) da futura Central do Edital.

O perfil ativo é a única referência do concurso. Esta tela não cria outro
seletor, não importa documentos e não modifica o banco de dados.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)

from ui.design import render_native_qss, render_qss


ESTILO_PORTAL_EDITAL = r"""
QWidget#portalEditalPage { background: {{color:canvas.app}}; }
QScrollArea#portalEditalScroll,
QWidget#portalEditalConteudo { background: transparent; border: none; }
QFrame#portalEditalCabecalho,
QFrame#portalEditalBloco {
    background-color: {{color:surface.secondary}};
    border: 1px solid {{color:border.default}};
    border-radius: 12px;
}
QLabel#portalEditalTitulo {
    color: {{color:text.primary}}; font-size: 19pt; font-weight: 800;
}
QLabel#portalEditalSubtitulo,
QLabel#portalEditalDescricao {
    color: {{color:text.secondary}}; font-size: 10pt;
}
QLabel#portalEditalBlocoTitulo {
    color: {{color:text.primary}}; font-size: 12pt; font-weight: 700;
}
QLabel#portalEditalEstado {
    color: {{color:text.muted}}; font-size: 9pt;
}
QPushButton#portalEditalAcao {
    background-color: {{color:dashboard.nav_surface}};
    color: {{color:dashboard.nav_text}};
    border: 1px solid {{color:dashboard.nav_border}};
    border-radius: 9px; padding: 8px 12px;
    font-size: 9pt; font-weight: 700; min-height: 32px;
}
QPushButton#portalEditalAcao:hover {
    background-color: {{color:dashboard.nav_hover_surface}};
    border-color: {{color:dashboard.nav_hover_border}};
}
"""


def _rotulo(texto, nome, quebra=True):
    item = QLabel(texto)
    item.setObjectName(nome)
    item.setWordWrap(quebra)
    return item


def _acao(texto, executar, parent=None):
    botao = QPushButton(texto, parent)
    botao.setObjectName("portalEditalAcao")
    botao.setCursor(Qt.PointingHandCursor)
    botao.clicked.connect(executar)
    return botao


def criar_portal_edital(voltar_inicio, abrir_progresso, abrir_disciplinas):
    """Monta acesso leve à Central, com atalhos para módulos já existentes."""
    pagina = QWidget()
    pagina.setObjectName("portalEditalPage")
    raiz = QVBoxLayout(pagina)
    raiz.setContentsMargins(0, 0, 0, 0)
    area = QScrollArea(pagina)
    area.setObjectName("portalEditalScroll")
    area.setWidgetResizable(True)
    area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    conteudo = QWidget()
    conteudo.setObjectName("portalEditalConteudo")
    coluna = QVBoxLayout(conteudo)
    coluna.setContentsMargins(18, 15, 18, 20)
    coluna.setSpacing(14)

    cabecalho = QFrame(conteudo)
    cabecalho.setObjectName("portalEditalCabecalho")
    barra = QHBoxLayout(cabecalho)
    barra.setContentsMargins(16, 13, 16, 13)
    titulos = QVBoxLayout()
    titulos.setSpacing(5)
    titulos.addWidget(_rotulo("Central do Edital", "portalEditalTitulo"))
    perfil_nome = _rotulo("Perfil ativo: —", "portalEditalSubtitulo")
    titulos.addWidget(perfil_nome)
    barra.addLayout(titulos, 1)
    barra.addWidget(_acao("← Início", voltar_inicio, cabecalho), 0, Qt.AlignVCenter)
    coluna.addWidget(cabecalho)

    introducao = _rotulo(
        "Esta Central utiliza automaticamente o perfil ativo do VighnaStudy. "
        "O cadastro de documentos, datas e etapas oficiais ainda será implementado; "
        "nenhuma informação de edital é presumida.",
        "portalEditalDescricao",
    )
    coluna.addWidget(introducao)

    acessos = QFrame(conteudo)
    acessos.setObjectName("portalEditalBloco")
    acesso_layout = QVBoxLayout(acessos)
    acesso_layout.setContentsMargins(16, 14, 16, 14)
    acesso_layout.setSpacing(9)
    acesso_layout.addWidget(_rotulo("Ferramentas já disponíveis", "portalEditalBlocoTitulo"))
    linha = QHBoxLayout()
    linha.setSpacing(10)
    linha.addWidget(_acao("Progresso do edital  →", abrir_progresso, acessos))
    linha.addWidget(_acao("Disciplinas do perfil  →", abrir_disciplinas, acessos))
    linha.addStretch(1)
    acesso_layout.addLayout(linha)
    coluna.addWidget(acessos)

    painel = QFrame(conteudo)
    painel.setObjectName("portalEditalBloco")
    painel_layout = QVBoxLayout(painel)
    painel_layout.setContentsMargins(16, 14, 16, 14)
    painel_layout.setSpacing(7)
    painel_layout.addWidget(_rotulo("Acompanhamento oficial", "portalEditalBlocoTitulo"))
    painel_layout.addWidget(_rotulo(
        "Cronograma, etapas, editais, retificações e comunicados: "
        "estrutura reservada para implementação futura.", "portalEditalEstado"
    ))
    coluna.addWidget(painel)
    coluna.addStretch(1)
    area.setWidget(conteudo)
    raiz.addWidget(area)
    pagina.edital_perfil_label = perfil_nome
    return pagina


def atualizar_perfil_portal_edital(pagina, nome):
    rotulo = getattr(pagina, "edital_perfil_label", None)
    if rotulo is not None:
        rotulo.setText("Perfil ativo: " + (str(nome or "").strip() or "—"))


def aplicar_estilo_portal_edital(pagina, tema):
    pagina.setStyleSheet((render_native_qss(ESTILO_PORTAL_EDITAL) if tema == "futurista"
                        else render_qss(tema, ESTILO_PORTAL_EDITAL)))
