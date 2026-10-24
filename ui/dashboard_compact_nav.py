"""Cabeçalho discreto do Dashboard: identidade VighnaStudy e busca (L05e).

Não recria o cabeçalho do portal Início, não modifica os controladores de
estudo e não inclui abas adicionais. A busca reutiliza a ação global atual.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy

from ui.design import render_native_qss, render_qss


QSS_CABECALHO_DASHBOARD = r"""
QFrame#dashboardQuickNav {
    background-color: {{color:surface.secondary}};
    border: 1px solid {{color:border.default}};
    border-radius: 10px;
}
QLabel#dashboardQuickBrand {
    background-color: transparent;
    border: none;
}
QLabel#dashboardQuickBrandName {
    background-color: transparent;
    color: {{color:text.primary}};
    border: none;
    font-size: 13pt;
    font-weight: 700;
}
QPushButton#dashboardQuickSearch {
    background-color: {{color:dashboard.nav_surface}};
    color: {{color:text.secondary}};
    border: 1px solid {{color:border.default}};
    border-radius: 7px;
    padding: 3px 10px;
    text-align: left;
    font-size: 9pt;
}
QPushButton#dashboardQuickSearch:hover,
QPushButton#dashboardQuickSearch:focus {
    background-color: {{color:dashboard.nav_hover_surface}};
    border-color: {{color:dashboard.nav_hover_border}};
    color: {{color:text.primary}};
}
"""


def criar_cabecalho_discreto_dashboard(abrir_busca, logo_pixmap=None) -> QFrame:
    """Exibe somente logo, nome do programa e gatilho da pesquisa existente."""
    painel = QFrame()
    painel.setObjectName("dashboardQuickNav")
    painel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    linha = QHBoxLayout(painel)
    linha.setContentsMargins(12, 5, 12, 5)
    linha.setSpacing(8)

    logo = QLabel()
    logo.setObjectName("dashboardQuickBrand")
    logo.setFixedSize(38, 43)
    logo.setAlignment(Qt.AlignCenter)
    if logo_pixmap is not None and not logo_pixmap.isNull():
        logo.setPixmap(logo_pixmap.scaled(38, 43, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    logo.setToolTip("VighnaStudy")
    linha.addWidget(logo, 0, Qt.AlignVCenter)

    nome = QLabel("VighnaStudy")
    nome.setObjectName("dashboardQuickBrandName")
    linha.addWidget(nome, 0, Qt.AlignVCenter)
    linha.addStretch(1)

    busca = QPushButton("⌕  Buscar no Vighna...     Ctrl+K")
    busca.setObjectName("dashboardQuickSearch")
    busca.setFixedHeight(32)
    busca.setMinimumWidth(160)
    busca.setMaximumWidth(320)
    busca.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    busca.setCursor(Qt.PointingHandCursor)
    busca.setToolTip("Buscar telas, ferramentas, ações e tópicos (Ctrl+K).")
    busca.setAccessibleName("Busca global do VighnaStudy")
    busca.clicked.connect(abrir_busca)
    linha.addWidget(busca, 1, Qt.AlignVCenter)

    painel.busca_global = busca
    painel.marca = logo
    return painel


def aplicar_estilo_cabecalho_dashboard(painel: QFrame, tema: str) -> None:
    """Usa tokens do Design System sem modificar cores globais."""
    painel.setStyleSheet((render_native_qss(QSS_CABECALHO_DASHBOARD) if tema == "futurista"
                        else render_qss(tema, QSS_CABECALHO_DASHBOARD)))
