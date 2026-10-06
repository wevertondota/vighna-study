from PySide6.QtWidgets import QApplication
from ui.design import render_qss


TEMAS_VALIDOS = {
    "claro",
    "escuro",
    "futurista"
}


# Design System do Dashboard — tema claro.
#
# A paleta fica centralizada aqui para evitar cores espalhadas pelo main.py.
# Os estilos do Dashboard usam seletores por objectName, portanto esta camada
# não altera indiscriminadamente outros QWidget, diálogos, tabelas ou telas.

# ============================================================
# Dashboard — Recomendação do algoritmo + resumo compacto
# ============================================================
ESTILO_INTELIGENCIA_RESUMO_CLARO = r"""
QWidget#dashboardRoot QFrame#dashboardInsightSummary {
    background-color: #FFFFFF;
    border: 1px solid #DCE4ED;
    border-radius: 11px;
}
QWidget#dashboardRoot QFrame#algorithmRecommendationBody {
    background-color: #F8FBFF;
    border: 1px solid #E1EAF4;
    border-radius: 10px;
}
QWidget#dashboardRoot QLabel#algorithmDashboardBadge {
    color: #2F6EAA;
    background-color: #EDF5FF;
    border: 1px solid #CFE2F6;
    border-radius: 8px;
    padding: 2px 7px;
    font-size: 8pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#algorithmDashboardSignature {
    color: #6484A4;
    font-size: 8.5pt;
    font-weight: 700;
}
QWidget#dashboardRoot QLabel#algorithmRecommendationTitle {
    color: #17263A;
    font-size: 13pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#algorithmRecommendationDetail {
    color: #6C7C90;
    font-size: 9pt;
}
QWidget#dashboardRoot QLabel#algorithmInsightChip {
    border-radius: 7px;
    padding: 5px 8px;
    font-size: 8.5pt;
    font-weight: 700;
}
QWidget#dashboardRoot QLabel#algorithmInsightChip[chipRole="review"] {
    color: #B93846;
    background-color: #FFF1F3;
    border: 1px solid #F5D3D8;
}
QWidget#dashboardRoot QLabel#algorithmInsightChip[chipRole="attention"] {
    color: #9A6614;
    background-color: #FFF8E8;
    border: 1px solid #F0DEB4;
}
QWidget#dashboardRoot QLabel#algorithmInsightChip[chipRole="focus"] {
    color: #28679E;
    background-color: #EEF6FF;
    border: 1px solid #D2E6FA;
}
QWidget#dashboardRoot QLabel#dashboardInsightSummaryIcon {
    color: #377DB4;
    background-color: #EFF7FE;
    border: 1px solid #D4E8F7;
    border-radius: 9px;
    font-size: 14px;
    font-weight: 900;
}
QWidget#dashboardRoot QLabel#dashboardInsightSummaryTitle {
    color: #18263A;
    font-size: 11pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#dashboardInsightSummaryDate {
    color: #7C899B;
    font-size: 8.5pt;
}
QWidget#dashboardRoot QFrame#dashboardInsightSummaryRow {
    background-color: #FAFCFE;
    border: 1px solid #E3EAF2;
    border-radius: 8px;
}
QWidget#dashboardRoot QFrame#dashboardInsightSummaryRow[summaryRole="pending"] {
    background-color: #FFF8F9;
    border-color: #F2DADD;
}
QWidget#dashboardRoot QFrame#dashboardInsightSummaryRow[summaryRole="streak"] {
    background-color: #FFFBF2;
    border-color: #F1E5C9;
}
QWidget#dashboardRoot QLabel#dashboardInsightSummaryRowTitle {
    color: #24344A;
    font-size: 9pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#dashboardInsightSummaryRowDetail {
    color: #8490A1;
    font-size: 8pt;
}
QWidget#dashboardRoot QLabel#dashboardInsightSummaryRowValue {
    color: #183A6B;
    font-size: 10pt;
    font-weight: 800;
}
QWidget#dashboardRoot QProgressBar#dashboardInsightSummaryProgress {
    background-color: #E8EDF3;
    border: none;
    border-radius: 3px;
}
QWidget#dashboardRoot QProgressBar#dashboardInsightSummaryProgress::chunk {
    background-color: #2F73C9;
    border-radius: 3px;
}

QWidget#dashboardRoot QLabel#dashboardPlanningHeroTitle {
    color: #4E6A86;
    font-size: 8.5pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#dashboardPlanningHeroValue {
    color: #0F3989;
    font-size: 24pt;
    font-weight: 900;
}
QWidget#dashboardRoot QLabel#dashboardPlanningHeroDetail {
    color: #66788C;
    font-size: 8.5pt;
    font-weight: 600;
}
QWidget#dashboardRoot QFrame#dashboardPlanningOperational {
    background-color: #FAFCFE;
    border: 1px solid #E3EAF2;
    border-radius: 8px;
}
QWidget#dashboardRoot QLabel#dashboardPlanningOperationalValue {
    color: #183A6B;
    font-size: 12pt;
    font-weight: 900;
}
QWidget#dashboardRoot QFrame#dashboardPlanningDivider {
    color: #DCE4ED;
    background-color: #DCE4ED;
    border: none;
    max-width: 1px;
}
QWidget#dashboardRoot QLabel#dashboardPlanningWeekLabel {
    color: #6F8092;
    font-size: 8pt;
    font-weight: 700;
}
"""

ESTILO_INTELIGENCIA_RESUMO_ESCURO = r"""
QWidget#dashboardRoot QFrame#dashboardInsightSummary,
QWidget#dashboardRoot QFrame#algorithmRecommendationBody {
    background-color: #162333;
    border: 1px solid #354B62;
    border-radius: 11px;
}
QWidget#dashboardRoot QLabel#algorithmDashboardBadge,
QWidget#dashboardRoot QLabel#algorithmInsightChip,
QWidget#dashboardRoot QFrame#dashboardInsightSummaryRow {
    background-color: #1B2C3E;
    color: #CFE0EF;
    border: 1px solid #3A536B;
    border-radius: 8px;
}
QWidget#dashboardRoot QLabel#algorithmRecommendationTitle,
QWidget#dashboardRoot QLabel#dashboardInsightSummaryTitle,
QWidget#dashboardRoot QLabel#dashboardInsightSummaryRowTitle,
QWidget#dashboardRoot QLabel#dashboardInsightSummaryRowValue {
    color: #F1F6FB;
}
QWidget#dashboardRoot QLabel#algorithmRecommendationDetail,
QWidget#dashboardRoot QLabel#algorithmDashboardSignature,
QWidget#dashboardRoot QLabel#dashboardInsightSummaryDate,
QWidget#dashboardRoot QLabel#dashboardInsightSummaryRowDetail {
    color: #9FB1C3;
}
QWidget#dashboardRoot QProgressBar#dashboardInsightSummaryProgress {
    background-color: #263A4D;
    border: none;
    border-radius: 3px;
}
QWidget#dashboardRoot QProgressBar#dashboardInsightSummaryProgress::chunk {
    background-color: #4C7FD1;
    border-radius: 3px;
}

QWidget#dashboardRoot QLabel#dashboardPlanningHeroTitle {
    color: #9FB1C3;
    font-size: 8.5pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#dashboardPlanningHeroValue {
    color: #F1F6FB;
    font-size: 24pt;
    font-weight: 900;
}
QWidget#dashboardRoot QLabel#dashboardPlanningHeroDetail {
    color: #9FB1C3;
    font-size: 8.5pt;
    font-weight: 600;
}
QWidget#dashboardRoot QFrame#dashboardPlanningOperational {
    background-color: #1B2C3E;
    border: 1px solid #3A536B;
    border-radius: 8px;
}
QWidget#dashboardRoot QLabel#dashboardPlanningOperationalValue {
    color: #F1F6FB;
    font-size: 12pt;
    font-weight: 900;
}
QWidget#dashboardRoot QFrame#dashboardPlanningDivider {
    color: #3A536B;
    background-color: #3A536B;
    border: none;
    max-width: 1px;
}
QWidget#dashboardRoot QLabel#dashboardPlanningWeekLabel {
    color: #9FB1C3;
    font-size: 8pt;
    font-weight: 700;
}
"""

ESTILO_INTELIGENCIA_RESUMO_FUTURISTA = r"""
QWidget#dashboardRoot QFrame#dashboardInsightSummary,
QWidget#dashboardRoot QFrame#algorithmRecommendationBody {
    background-color: #10283C;
    border: 1px solid #3F7599;
    border-radius: 11px;
}
QWidget#dashboardRoot QLabel#algorithmDashboardBadge,
QWidget#dashboardRoot QLabel#algorithmInsightChip,
QWidget#dashboardRoot QFrame#dashboardInsightSummaryRow {
    background-color: #123149;
    color: #D9F3FF;
    border: 1px solid #447DA1;
    border-radius: 8px;
}
QWidget#dashboardRoot QLabel#algorithmRecommendationTitle,
QWidget#dashboardRoot QLabel#dashboardInsightSummaryTitle,
QWidget#dashboardRoot QLabel#dashboardInsightSummaryRowTitle,
QWidget#dashboardRoot QLabel#dashboardInsightSummaryRowValue {
    color: #F2FCFF;
}
QWidget#dashboardRoot QLabel#algorithmRecommendationDetail,
QWidget#dashboardRoot QLabel#algorithmDashboardSignature,
QWidget#dashboardRoot QLabel#dashboardInsightSummaryDate,
QWidget#dashboardRoot QLabel#dashboardInsightSummaryRowDetail {
    color: #9BCBDD;
}
QWidget#dashboardRoot QProgressBar#dashboardInsightSummaryProgress {
    background-color: #17384F;
    border: none;
    border-radius: 3px;
}
QWidget#dashboardRoot QProgressBar#dashboardInsightSummaryProgress::chunk {
    background-color: #5ED8FF;
    border-radius: 3px;
}

QWidget#dashboardRoot QLabel#dashboardPlanningHeroTitle {
    color: #9BCBDD;
    font-size: 8.5pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#dashboardPlanningHeroValue {
    color: #F2FCFF;
    font-size: 24pt;
    font-weight: 900;
}
QWidget#dashboardRoot QLabel#dashboardPlanningHeroDetail {
    color: #9BCBDD;
    font-size: 8.5pt;
    font-weight: 600;
}
QWidget#dashboardRoot QFrame#dashboardPlanningOperational {
    background-color: #123149;
    border: 1px solid #447DA1;
    border-radius: 8px;
}
QWidget#dashboardRoot QLabel#dashboardPlanningOperationalValue {
    color: #F2FCFF;
    font-size: 12pt;
    font-weight: 900;
}
QWidget#dashboardRoot QFrame#dashboardPlanningDivider {
    color: #447DA1;
    background-color: #447DA1;
    border: none;
    max-width: 1px;
}
QWidget#dashboardRoot QLabel#dashboardPlanningWeekLabel {
    color: #9BCBDD;
    font-size: 8pt;
    font-weight: 700;
}
"""

PALETA_DASHBOARD_CLARO = {
    "fundo": "#EBF2FA",
    "superficie": "#FFFFFF",
    "borda": "#E2E8F0",
    "borda_controle": "#DCE3EE",
    "borda_controle_forte": "#A0AEC0",
    "primaria": "#0F3989",
    "primaria_hover": "#1A4BA8",
    "primaria_pressed": "#0A3266",
    "texto": "#1A202C",
    "texto_secundario": "#2D3748",
    "texto_suave": "#718096",
    "hover_claro": "#EDF2F7",
    "trilho": "#E2E8F0",
}


# Lista de tópicos da disciplina.
#
# Esta tabela possui regras próprias porque precisa comunicar três estados sem
# misturá-los: linha normal/ativa, conteúdo desligado e seleção atual. A cor de
# fundo fica reservada à zebragem e à seleção; conteúdo desligado é sinalizado
# principalmente pela tipografia esmaecida.
ESTILO_TOPICOS_DISCIPLINA_CLARO = r"""
QTableWidget#disciplineTopicsTable {
    background-color: #ffffff;
    alternate-background-color: #f8fbff;
    color: #1f2937;
    border: 1px solid #dbe3ed;
    border-radius: 8px;
    gridline-color: #e8edf4;
    selection-background-color: #dbeafe;
    selection-color: #111827;
}
QTableWidget#disciplineTopicsTable::item:selected {
    background-color: #dbeafe;
    color: #111827;
}
QTableWidget#disciplineTopicsTable QHeaderView::section {
    background-color: #f8fafc;
    color: #475569;
    border: none;
    border-right: 1px solid #e2e8f0;
    border-bottom: 1px solid #dbe3ed;
}
QWidget#disciplineTopicCell,
QWidget#disciplineTopicCell QLabel#disciplineTopicCellLabel {
    background: transparent;
}
QWidget#disciplineTopicCell QLabel#disciplineTopicCellLabel {
    color: #1f2937;
}
QWidget#disciplineTopicCell[inactive="true"] QLabel#disciplineTopicCellLabel {
    color: #64748b;
}
QWidget#disciplineTopicCell QToolButton#topicExpandButton {
    background: transparent;
    border: none;
    color: #475569;
    padding: 0px;
}
QWidget#disciplineTopicCell[inactive="true"] QToolButton#topicExpandButton {
    color: #94a3b8;
}
"""

ESTILO_TOPICOS_DISCIPLINA_ESCURO = r"""
QTableWidget#disciplineTopicsTable {
    background-color: #182235;
    alternate-background-color: #1b2739;
    color: #e5e7eb;
    border: 1px solid #334155;
    border-radius: 8px;
    gridline-color: #334155;
    selection-background-color: #24496f;
    selection-color: #ffffff;
}
QTableWidget#disciplineTopicsTable::item:selected {
    background-color: #24496f;
    color: #ffffff;
}
QTableWidget#disciplineTopicsTable QHeaderView::section {
    background-color: #1f2937;
    color: #cbd5e1;
    border: none;
    border-right: 1px solid #334155;
    border-bottom: 1px solid #475569;
}
QWidget#disciplineTopicCell,
QWidget#disciplineTopicCell QLabel#disciplineTopicCellLabel {
    background: transparent;
}
QWidget#disciplineTopicCell QLabel#disciplineTopicCellLabel {
    color: #e5e7eb;
}
QWidget#disciplineTopicCell[inactive="true"] QLabel#disciplineTopicCellLabel {
    color: #94a3b8;
}
QWidget#disciplineTopicCell QToolButton#topicExpandButton {
    background: transparent;
    border: none;
    color: #cbd5e1;
    padding: 0px;
}
QWidget#disciplineTopicCell[inactive="true"] QToolButton#topicExpandButton {
    color: #64748b;
}
"""

ESTILO_TOPICOS_DISCIPLINA_FUTURISTA = r"""
QTableWidget#disciplineTopicsTable {
    background-color: #0a192b;
    alternate-background-color: #0d2131;
    color: #e7f3ff;
    border: 1px solid #305474;
    border-radius: 10px;
    gridline-color: #20394f;
    selection-background-color: #155073;
    selection-color: #ffffff;
}
QTableWidget#disciplineTopicsTable::item:selected {
    background-color: #155073;
    color: #ffffff;
}
QTableWidget#disciplineTopicsTable QHeaderView::section {
    background-color: #10243a;
    color: #b7cede;
    border: none;
    border-right: 1px solid #284965;
    border-bottom: 1px solid #346080;
}
QWidget#disciplineTopicCell,
QWidget#disciplineTopicCell QLabel#disciplineTopicCellLabel {
    background: transparent;
}
QWidget#disciplineTopicCell QLabel#disciplineTopicCellLabel {
    color: #e7f3ff;
}
QWidget#disciplineTopicCell[inactive="true"] QLabel#disciplineTopicCellLabel {
    color: #8fa8b8;
}
QWidget#disciplineTopicCell QToolButton#topicExpandButton {
    background: transparent;
    border: none;
    color: #b7cede;
    padding: 0px;
}
QWidget#disciplineTopicCell[inactive="true"] QToolButton#topicExpandButton {
    color: #688395;
}
"""


def normalizar_tema(tema):
    tema = str(
        tema or "claro"
    ).strip().lower()

    if tema not in TEMAS_VALIDOS:
        return "claro"

    return tema




ESTILO_JORNADA_CLARO = r"""
QPushButton#planningJourneyButton, QPushButton#journeyPrimaryButton {
    background-color: #326fd3; color: #ffffff; border: 1px solid #326fd3;
    border-radius: 8px; font-weight: 800; padding: 6px 12px;
}
QPushButton#planningJourneyButton:hover, QPushButton#journeyPrimaryButton:hover {
    background-color: #285fb5; border-color: #285fb5;
}
QPushButton#planningJourneyButton[journeyState="pausada"] {
    background-color: #fff7e6; color: #9a6511; border-color: #e5bd70;
}
QPushButton#planningJourneyButton[journeyState="encerrada"] {
    background-color: #f3f5f8; color: #6b7280; border-color: #d8dee8;
}
QFrame#journeySummaryCard { background-color: #f7faff; border: 1px solid #cfdeef; border-radius: 11px; }
QLabel#journeyStatLabel, QLabel#journeyMetaText, QLabel#journeyHint { color: #65758a; font-size: 8.5pt; }
QLabel#journeyStatValue { color: #245f9f; font-size: 15pt; font-weight: 900; }
QLabel#journeyStatusBadge { background-color: #e8f2ff; color: #2d67a7; border: 1px solid #b9d2ee; border-radius: 8px; padding: 5px 10px; font-weight: 800; }
QLabel#journeyStatusBadge[journeyState="pausada"] { background-color: #fff5db; color: #98610c; border-color: #e9c777; }
QLabel#journeyStatusBadge[journeyState="encerrada"] { background-color: #f1f3f6; color: #747b86; border-color: #d8dde5; }
QProgressBar#journeyProgress { min-height: 8px; max-height: 8px; background-color: #e5edf7; border: none; border-radius: 4px; }
QProgressBar#journeyProgress::chunk { background-color: #34a6bf; border-radius: 4px; }
QTableWidget#journeyTable { background-color: #ffffff; border: 1px solid #d9e3ef; border-radius: 9px; }
"""

ESTILO_JORNADA_ESCURO = r"""
QPushButton#planningJourneyButton, QPushButton#journeyPrimaryButton {
    background-color: #416ab7; color: #ffffff; border: 1px solid #4c7bcf; border-radius: 8px; font-weight: 800; padding: 6px 12px;
}
QPushButton#planningJourneyButton:hover, QPushButton#journeyPrimaryButton:hover { background-color: #355ba3; }
QPushButton#planningJourneyButton[journeyState="pausada"] { background-color: #3d321c; color: #e9c576; border-color: #725f32; }
QPushButton#planningJourneyButton[journeyState="encerrada"] { background-color: #202936; color: #8391a2; border-color: #364657; }
QFrame#journeySummaryCard { background-color: #162333; border: 1px solid #354b62; border-radius: 11px; }
QLabel#journeyStatLabel, QLabel#journeyMetaText, QLabel#journeyHint { color: #91a4b8; font-size: 8.5pt; }
QLabel#journeyStatValue { color: #a9d3ff; font-size: 15pt; font-weight: 900; }
QLabel#journeyStatusBadge { background-color: #173552; color: #a8d5ff; border: 1px solid #42688c; border-radius: 8px; padding: 5px 10px; font-weight: 800; }
QLabel#journeyStatusBadge[journeyState="pausada"] { background-color: #3b301c; color: #e6c271; border-color: #725e31; }
QLabel#journeyStatusBadge[journeyState="encerrada"] { background-color: #222c38; color: #8a98a8; border-color: #3b4b5c; }
QProgressBar#journeyProgress { min-height: 8px; max-height: 8px; background-color: #27384a; border: none; border-radius: 4px; }
QProgressBar#journeyProgress::chunk { background-color: #4f9fc5; border-radius: 4px; }
QTableWidget#journeyTable { background-color: #151f2d; border: 1px solid #33465a; border-radius: 9px; }
"""

ESTILO_JORNADA_FUTURISTA = r"""
QPushButton#planningJourneyButton, QPushButton#journeyPrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #355f9f, stop:1 #4c7ee0);
    color: #ffffff; border: 1px solid #7dadff; border-radius: 10px; font-weight: 800; padding: 6px 12px;
}
QPushButton#planningJourneyButton:hover, QPushButton#journeyPrimaryButton:hover { border-color: #b5d3ff; }
QPushButton#planningJourneyButton[journeyState="pausada"] { background-color: #3b311d; color: #f0ca72; border-color: #806b39; }
QPushButton#planningJourneyButton[journeyState="encerrada"] { background-color: #132333; color: #718b9d; border-color: #2f5268; }
QFrame#journeySummaryCard { background-color: #10283c; border: 1px solid #3f7599; border-radius: 12px; }
QLabel#journeyStatLabel, QLabel#journeyMetaText, QLabel#journeyHint { color: #82abc5; font-size: 8.5pt; }
QLabel#journeyStatValue { color: #bce7ff; font-size: 15pt; font-weight: 900; }
QLabel#journeyStatusBadge { background-color: #113650; color: #9fe2ff; border: 1px solid #4d94ba; border-radius: 9px; padding: 5px 10px; font-weight: 800; }
QLabel#journeyStatusBadge[journeyState="pausada"] { background-color: #392f1b; color: #f1ce78; border-color: #806b39; }
QLabel#journeyStatusBadge[journeyState="encerrada"] { background-color: #152635; color: #7c9bad; border-color: #315b72; }
QProgressBar#journeyProgress { min-height: 8px; max-height: 8px; background-color: #173046; border: 1px solid #2e5c78; border-radius: 4px; }
QProgressBar#journeyProgress::chunk { background-color: #55a7d5; border-radius: 4px; }
QTableWidget#journeyTable { background-color: #101f30; border: 1px solid #315d79; border-radius: 10px; }
"""


ESTILO_DASHBOARD_MODERNO_CLARO = r"""
/* Dashboard moderno — camada final do tema claro */
QWidget#dashboardPage,
QScrollArea#dashboardScroll,
QWidget#dashboardRoot {
    background-color: #f3f6fb;
}

QWidget#dashboardRoot QLabel {
    background-color: transparent;
}

QFrame#dashboardTopBar {
    background-color: #ffffff;
    border: 1px solid #dbe4ef;
    border-radius: 16px;
}

QWidget#dashboardRoot QLabel#pageTitle {
    color: #10233f;
    font-size: 20px;
    font-weight: 900;
}

QWidget#dashboardRoot QLabel#pageSubtitle {
    color: #738196;
    font-size: 9pt;
}

QWidget#dashboardRoot QFrame#topProfileBar {
    background-color: #f6f8fc;
    border: 1px solid #dce5f0;
    border-radius: 11px;
}

QWidget#dashboardRoot QFrame#dashboardTodayPanel,
QWidget#dashboardRoot QFrame#dashboardQuickAccess,
QWidget#dashboardRoot QFrame#dashboardOverviewCard,
QWidget#dashboardRoot QFrame#dashboardNotificationsPanel,
QWidget#dashboardRoot QFrame#planningPanel,
QWidget#dashboardRoot QFrame#studyNowPanel,
QWidget#dashboardRoot QFrame#priorityQueuePanel,
QWidget#dashboardRoot QFrame#dashboardCenterBar {
    background-color: #ffffff;
    border: 1px solid #d9e3ef;
    border-radius: 14px;
}

QWidget#dashboardRoot QFrame#dashboardTodayFocus,
QWidget#dashboardRoot QFrame#dashboardTodayMetric {
    border-radius: 11px;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #f8fbff, stop:0.5 #ffffff, stop:1 #f8fbff);
    border-color: #c8d9ec;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] {
    background: transparent;
    border: none;
    border-radius: 0px;
}

QWidget#dashboardRoot QFrame#dashboardTodaySeparator {
    background-color: #d7e4f0;
    border: none;
    min-height: 1px;
    max-height: 1px;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#dashboardSectionToggle {
    background: transparent;
    border: none;
    color: #536f8b;
    font-size: 8.7pt;
    font-weight: 800;
    padding: 4px 4px;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#toolbarButton,
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#pauseNavButton {
    background-color: #fbfdff;
    color: #355874;
    border: 1px solid #d2dfec;
    border-radius: 11px;
    font-size: 8.85pt;
    font-weight: 700;
    padding: 6px 14px;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#toolbarButton:hover,
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#pauseNavButton:hover {
    background-color: #f0f6fd;
    border-color: #b7cfe7;
    color: #214d78;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#focusNavButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #c53b4b, stop:1 #e05d66);
    color: #ffffff;
    border: 1px solid #b33a46;
    border-radius: 11px;
    font-size: 9.2pt;
    font-weight: 850;
    letter-spacing: 0.2px;
    padding: 6px 15px;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#focusNavButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #b43342, stop:1 #d4515b);
    border-color: #9f303b;
}

QWidget#dashboardRoot QPushButton#toolbarButton,
QWidget#dashboardRoot QPushButton#focusNavButton,
QWidget#dashboardRoot QPushButton#pauseNavButton {
    border-radius: 10px;
    font-weight: 700;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess QPushButton#dashboardSectionToggle {
    color: #294866;
    font-size: 9.5pt;
    font-weight: 900;
}

QWidget#dashboardRoot QPushButton#focusNavButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #c91f2b, stop:0.52 #dc2626, stop:1 #ef4444);
    color: #ffffff;
    border: 1px solid #a91520;
    border-radius: 11px;
    font-family: "Segoe UI Semibold";
    font-size: 11pt;
    font-weight: 900;
    letter-spacing: 0.5px;
    padding: 7px 18px;
}

QWidget#dashboardRoot QPushButton#focusNavButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #b81924, stop:0.52 #cf202b, stop:1 #e43742);
    border-color: #8f111a;
}

QWidget#dashboardRoot QPushButton#focusNavButton:pressed {
    background-color: #a91520;
    border-color: #7f1018;
}

QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #ffffff, stop:0.54 #eef5ff, stop:1 #f7fbff);
    border: 1px solid #b9d0eb;
    border-radius: 18px;
}

QWidget#dashboardRoot QLabel#dashboardGuidedHeroEyebrow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1f5ba9, stop:1 #367bd2);
    color: #ffffff;
    border: 1px solid #194b8e;
    border-radius: 8px;
    padding: 5px 11px;
    font-size: 8.7pt;
    font-weight: 900;
    letter-spacing: 1px;
}

QWidget#dashboardRoot QFrame#dashboardGuidedInfoCard {
    background-color: rgba(255, 255, 255, 0.82);
    border: 1px solid #d4e2f1;
    border-radius: 13px;
}

QWidget#dashboardRoot QLabel#dashboardGuidedInfoHeading {
    color: #183b67;
    font-size: 10pt;
    font-weight: 900;
}

QWidget#dashboardRoot QLabel#dashboardGuidedHeroGuide {
    color: #536d89;
    font-size: 8.8pt;
    font-weight: 600;
}

QWidget#dashboardRoot QLabel#dashboardGuidedInfoCriteria {
    background-color: #edf5ff;
    color: #2d6098;
    border: 1px solid #c9ddf3;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 7.8pt;
    font-weight: 900;
    letter-spacing: 0.3px;
}

QWidget#dashboardRoot QFrame#dashboardGuidedActionBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ffffff, stop:1 #edf5ff);
    border: 2px solid #b8d0eb;
    border-radius: 16px;
    min-width: 380px;
}

QWidget#dashboardRoot QLabel#dashboardGuidedActionEyebrow {
    color: #2d67ab;
    font-size: 8.2pt;
    font-weight: 900;
    letter-spacing: 1px;
}

QWidget#dashboardRoot QLabel#dashboardGuidedActionHint {
    color: #617a96;
    font-size: 8.6pt;
    font-weight: 700;
}

QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayPrimaryButton {
    min-width: 320px;
    min-height: 54px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #205dcc, stop:0.52 #2869df, stop:1 #377cf0);
    border: 1px solid #174cae;
    border-radius: 14px;
    font-size: 11.5pt;
    font-weight: 900;
}

QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayPrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #194fac, stop:0.52 #215bc7, stop:1 #2e6ddd);
    border-color: #103e92;
}

QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayPrimaryButton:pressed {
    background-color: #174cae;
    border-color: #103e92;
}

QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] QLabel#dashboardTodayActionTitle {
    color: #102a4e;
    font-size: 16pt;
    font-weight: 900;
}

QWidget#dashboardRoot QFrame#questionsHeroActions {
    background-color: #ffffff;
    border: 1px solid #d9e3ef;
    border-radius: 14px;
}

QWidget#dashboardRoot QLabel#questionsHeroTitle {
    color: #172b48;
    font-size: 10pt;
    font-weight: 900;
}

QWidget#dashboardRoot QLabel#questionsHeroDescription {
    color: #6b7a90;
    font-size: 8.5pt;
}

QWidget#dashboardRoot QPushButton#dashboardGroupToggle,
QWidget#dashboardRoot QPushButton#dashboardSectionToggle,
QWidget#dashboardRoot QPushButton#dashboardSectionToggleCentered,
QWidget#dashboardRoot QPushButton#dashboardProjectionTitleButton {
    color: #243b5a;
    font-size: 9.5pt;
    font-weight: 800;
}

QWidget#dashboardRoot QFrame#dashboardAttentionCard,
QWidget#dashboardRoot QFrame#dailyGoalBox,
QWidget#dashboardRoot QFrame#weeklyLoadBox,
QWidget#dashboardRoot QFrame#weeklyGoalBox,
QWidget#dashboardRoot QFrame#studyActionCard,
QWidget#dashboardRoot QFrame#strategyCompactCard {
    border-radius: 11px;
}

QWidget#dashboardRoot QTableWidget#priorityQueueTable {
    background-color: #ffffff;
    alternate-background-color: #f6f8fc;
    border: 1px solid #dce5ef;
    border-radius: 10px;
    selection-background-color: #e8f1ff;
    selection-color: #17375e;
}

QWidget#dashboardRoot QTableWidget#priorityQueueTable QHeaderView::section {
    background-color: #f2f6fb;
    color: #50627a;
    border: none;
    border-bottom: 1px solid #d9e3ef;
    padding: 7px 8px;
    font-weight: 800;
}

/* Pills que mantêm preenchimento após a limpeza visual dos textos. */
QWidget#dashboardRoot QLabel#dashboardTodayDate,
QWidget#dashboardRoot QLabel#planningTotalBadge {
    background-color: #eef4fb;
}

QWidget#dashboardRoot QLabel#studyReviewSourceBadge,
QWidget#dashboardRoot QLabel#priorityQueueSourceBadge {
    background-color: #edf5ff;
}

QWidget#dashboardRoot QLabel#assessmentBadge {
    background-color: #fff3d8;
}

QWidget#dashboardRoot QLabel#dashboardAttentionBadge {
    background-color: #fff0c8;
}

QWidget#dashboardRoot QFrame#dashboardAttentionCard[alertState="ok"] QLabel#dashboardAttentionBadge {
    background-color: #eaf5ee;
}

QWidget#dashboardRoot QFrame#dashboardAttentionCard[alertState="critico"] QLabel#dashboardAttentionBadge {
    background-color: #fde9e6;
}

QWidget#dashboardRoot QLabel#dashboardPaceBadge {
    background-color: #e9f2fd;
}

QWidget#dashboardRoot QLabel#weeklyGoalStatus {
    background-color: #f1f5f9;
}

QWidget#dashboardRoot QLabel#weeklyGoalStatus[weekState="concluida"] {
    background-color: #eaf6ee;
}

QWidget#dashboardRoot QLabel#weeklyGoalStatus[weekState="atencao"] {
    background-color: #fff4da;
}

/* HOJE — dois protagonistas: Foco + Questões */
QWidget#dashboardRoot QFrame#dashboardTodayFocus[protagonist="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #fff8f8, stop:0.58 #fff3f4, stop:1 #fffafa);
    border: 1px solid #e7c3c9;
    border-radius: 16px;
}

QWidget#dashboardRoot QFrame#dashboardTodayMetric[protagonist="true"][metricKind="questions"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #f5f9ff, stop:0.58 #eef5ff, stop:1 #f8fbff);
    border: 1px solid #bfd3eb;
    border-radius: 16px;
}

QWidget#dashboardRoot QLabel#dashboardProtagonistTitle {
    color: #233a54;
    font-size: 9.4pt;
    font-weight: 900;
    letter-spacing: 0.8px;
}

QWidget#dashboardRoot QLabel#dashboardProtagonistBadge {
    color: #697d92;
    background-color: rgba(255, 255, 255, 0.72);
    border: 1px solid #d8e2ec;
    border-radius: 7px;
    padding: 3px 7px;
    font-size: 7.2pt;
    font-weight: 800;
    letter-spacing: 0.5px;
}

QWidget#dashboardRoot QLabel#dashboardProtagonistCaption {
    color: #708399;
    font-size: 8.5pt;
    font-weight: 600;
    padding-bottom: 3px;
}

QWidget#dashboardRoot QFrame#dashboardTodayFocus[protagonist="true"] QLabel#dashboardTodayFocusValue {
    color: #b73545;
    font-size: 22pt;
    font-weight: 900;
}

QWidget#dashboardRoot QLabel#dashboardQuestionsHeroValue {
    color: #245fa8;
    font-size: 22pt;
    font-weight: 900;
}

QWidget#dashboardRoot QFrame#dashboardTodayMetric[compact="true"] {
    background-color: rgba(255, 255, 255, 0.68);
    border: 1px solid #d8e4ef;
    border-radius: 10px;
}

QWidget#dashboardRoot QFrame#dashboardTodayMetric[compact="true"][metricKind="review"] {
    background-color: rgba(239, 249, 243, 0.88);
    border-color: #c7e3d1;
}

QWidget#dashboardRoot QFrame#dashboardTodayMetric[compact="true"] QLabel#dashboardTodayMetricValue {
    font-size: 11.5pt;
}

QWidget#dashboardRoot QFrame#dashboardTodayMetric[compact="true"] QLabel#dashboardTodayDetail {
    font-size: 7.75pt;
}

QWidget#dashboardRoot QPushButton#dashboardFocusPrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #bf3545, stop:1 #dc5662);
    color: #ffffff;
    border: 1px solid #b5303f;
    border-radius: 11px;
    font-size: 9.5pt;
    font-weight: 900;
    padding: 8px 18px;
}

QWidget#dashboardRoot QPushButton#dashboardFocusPrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ad2e3d, stop:1 #cd4956);
    border-color: #9f2936;
}

QWidget#dashboardRoot QPushButton#dashboardQuestionsPrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2f68be, stop:1 #3e7dde);
    color: #ffffff;
    border: 1px solid #2b60ae;
    border-radius: 11px;
    font-size: 9.5pt;
    font-weight: 900;
    padding: 8px 18px;
}

QWidget#dashboardRoot QPushButton#dashboardQuestionsPrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #285ca9, stop:1 #3470ca);
    border-color: #245394;
}

"""


ESTILO_DASHBOARD_MODERNO_ESCURO = r"""
/* Dashboard moderno — camada final do tema escuro */
QWidget#dashboardPage,
QScrollArea#dashboardScroll,
QWidget#dashboardRoot {
    background-color: #0e1623;
}

QWidget#dashboardRoot QLabel {
    background-color: transparent;
}

QFrame#dashboardTopBar,
QWidget#dashboardRoot QFrame#dashboardTodayPanel,
QWidget#dashboardRoot QFrame#dashboardQuickAccess,
QWidget#dashboardRoot QFrame#dashboardOverviewCard,
QWidget#dashboardRoot QFrame#dashboardNotificationsPanel,
QWidget#dashboardRoot QFrame#planningPanel,
QWidget#dashboardRoot QFrame#studyNowPanel,
QWidget#dashboardRoot QFrame#priorityQueuePanel,
QWidget#dashboardRoot QFrame#dashboardCenterBar,
QWidget#dashboardRoot QFrame#questionsHeroActions {
    background-color: #151f2d;
    border: 1px solid #2d4054;
    border-radius: 14px;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #132235, stop:0.5 #151f2d, stop:1 #132235);
    border-color: #35516d;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] {
    background: transparent;
    border: none;
    border-radius: 0px;
}

QWidget#dashboardRoot QFrame#dashboardTodaySeparator {
    background-color: #2a3c4f;
    border: none;
    min-height: 1px;
    max-height: 1px;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#dashboardSectionToggle {
    background: transparent;
    border: none;
    color: #9fb6cb;
    font-size: 8.7pt;
    font-weight: 800;
    padding: 4px 4px;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#toolbarButton,
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#pauseNavButton {
    background-color: #182534;
    color: #bed0e1;
    border: 1px solid #33495e;
    border-radius: 9px;
    font-size: 8.8pt;
    font-weight: 700;
    padding: 5px 12px;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#toolbarButton:hover,
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#pauseNavButton:hover {
    background-color: #203246;
    border-color: #476987;
    color: #e0eefb;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#focusNavButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #a52a37, stop:1 #c64551);
    color: #ffffff;
    border: 1px solid #cf5f69;
    border-radius: 9px;
    font-size: 9.2pt;
    font-weight: 850;
    letter-spacing: 0.2px;
    padding: 5px 14px;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#focusNavButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #b83340, stop:1 #d4535e);
    border-color: #e57a83;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess QPushButton#dashboardSectionToggle {
    color: #c8dbed;
    font-size: 9.5pt;
    font-weight: 900;
}

QWidget#dashboardRoot QPushButton#focusNavButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #b91c2a, stop:0.52 #d92d3a, stop:1 #f04451);
    color: #ffffff;
    border: 1px solid #ff6973;
    border-radius: 11px;
    font-family: "Segoe UI Semibold";
    font-size: 11pt;
    font-weight: 900;
    letter-spacing: 0.5px;
    padding: 7px 18px;
}

QWidget#dashboardRoot QPushButton#focusNavButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #cf2634, stop:0.52 #e63b47, stop:1 #ff5964);
    border-color: #ff9298;
}

QWidget#dashboardRoot QPushButton#focusNavButton:pressed {
    background-color: #9f1723;
    border-color: #ff5964;
}

QWidget#dashboardRoot QLabel#pageTitle { color: #f1f6fb; font-size: 20px; font-weight: 900; }
QWidget#dashboardRoot QLabel#pageSubtitle { color: #8fa1b5; font-size: 9pt; }

QWidget#dashboardRoot QFrame#topProfileBar {
    background-color: #111b28;
    border: 1px solid #30445a;
    border-radius: 11px;
}

QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #172437, stop:0.55 #142b45, stop:1 #172334);
    border: 1px solid #3d6387;
    border-radius: 18px;
}

QWidget#dashboardRoot QLabel#dashboardGuidedHeroEyebrow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #315f9b, stop:1 #4a82c4);
    color: #f5f9ff;
    border: 1px solid #6d9cd2;
    border-radius: 8px;
    padding: 5px 11px;
    font-size: 8.7pt;
    font-weight: 900;
    letter-spacing: 1px;
}

QWidget#dashboardRoot QFrame#dashboardGuidedInfoCard,
QWidget#dashboardRoot QFrame#dashboardGuidedActionBox {
    background-color: #111d2b;
    border: 1px solid #334d66;
    border-radius: 13px;
}

QWidget#dashboardRoot QLabel#dashboardGuidedInfoHeading {
    color: #dcecff;
    font-size: 10pt;
    font-weight: 900;
}

QWidget#dashboardRoot QLabel#dashboardGuidedHeroGuide {
    color: #9db2c7;
    font-size: 8.8pt;
    font-weight: 600;
}

QWidget#dashboardRoot QLabel#dashboardGuidedInfoCriteria {
    background-color: #172a3e;
    color: #9cc9f3;
    border: 1px solid #385b7b;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 7.8pt;
    font-weight: 900;
    letter-spacing: 0.3px;
}

QWidget#dashboardRoot QFrame#dashboardGuidedActionBox {
    min-width: 380px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #18283a, stop:1 #101c29);
    border: 2px solid #496b8e;
    border-radius: 16px;
}

QWidget#dashboardRoot QLabel#dashboardGuidedActionEyebrow {
    color: #8fc4f2;
    font-size: 8.2pt;
    font-weight: 900;
    letter-spacing: 1px;
}

QWidget#dashboardRoot QLabel#dashboardGuidedActionHint {
    color: #9db2c7;
    font-size: 8.6pt;
    font-weight: 700;
}

QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayPrimaryButton {
    min-width: 320px;
    min-height: 54px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #315fae, stop:0.52 #3f72c8, stop:1 #5488de);
    border: 1px solid #78a7ee;
    border-radius: 14px;
    font-size: 11.5pt;
    font-weight: 900;
}

QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayPrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3c6cbc, stop:0.52 #4c80d4, stop:1 #6297e9);
    border-color: #a3c6ff;
}

QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayPrimaryButton:pressed {
    background-color: #294f91;
    border-color: #6f9cde;
}

QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] QLabel#dashboardTodayActionTitle {
    color: #eef6ff;
    font-size: 16pt;
    font-weight: 900;
}

QWidget#dashboardRoot QPushButton#dashboardGroupToggle,
QWidget#dashboardRoot QPushButton#dashboardSectionToggle,
QWidget#dashboardRoot QPushButton#dashboardSectionToggleCentered,
QWidget#dashboardRoot QPushButton#dashboardProjectionTitleButton {
    color: #d7e4f2;
    font-size: 9.5pt;
    font-weight: 800;
}

QWidget#dashboardRoot QFrame#dashboardAttentionCard,
QWidget#dashboardRoot QFrame#dailyGoalBox,
QWidget#dashboardRoot QFrame#weeklyLoadBox,
QWidget#dashboardRoot QFrame#weeklyGoalBox,
QWidget#dashboardRoot QFrame#studyActionCard,
QWidget#dashboardRoot QFrame#strategyCompactCard {
    border-radius: 11px;
}

QWidget#dashboardRoot QTableWidget#priorityQueueTable {
    background-color: #111a27;
    alternate-background-color: #172231;
    border: 1px solid #30445a;
    border-radius: 10px;
    selection-background-color: #24496f;
    selection-color: #ffffff;
}

QWidget#dashboardRoot QTableWidget#priorityQueueTable QHeaderView::section {
    background-color: #192536;
    color: #aebfd0;
    border: none;
    border-bottom: 1px solid #30445a;
    padding: 7px 8px;
    font-weight: 800;
}

QWidget#dashboardRoot QLabel#dashboardTodayDate,
QWidget#dashboardRoot QLabel#planningTotalBadge,
QWidget#dashboardRoot QLabel#weeklyGoalStatus {
    background-color: #202d3c;
}

QWidget#dashboardRoot QLabel#studyReviewSourceBadge,
QWidget#dashboardRoot QLabel#priorityQueueSourceBadge,
QWidget#dashboardRoot QLabel#dashboardPaceBadge {
    background-color: #173552;
}

QWidget#dashboardRoot QLabel#assessmentBadge,
QWidget#dashboardRoot QLabel#dashboardAttentionBadge {
    background-color: #3b321f;
}

QWidget#dashboardRoot QFrame#dashboardAttentionCard[alertState="ok"] QLabel#dashboardAttentionBadge,
QWidget#dashboardRoot QLabel#weeklyGoalStatus[weekState="concluida"] {
    background-color: #21372d;
}

QWidget#dashboardRoot QFrame#dashboardAttentionCard[alertState="critico"] QLabel#dashboardAttentionBadge,
QWidget#dashboardRoot QLabel#weeklyGoalStatus[weekState="atencao"] {
    background-color: #432827;
}

/* HOJE — dois protagonistas: Foco + Questões */
QWidget#dashboardRoot QFrame#dashboardTodayFocus[protagonist="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #241c24, stop:0.58 #2d2027, stop:1 #211c24);
    border: 1px solid #68434d;
    border-radius: 16px;
}

QWidget#dashboardRoot QFrame#dashboardTodayMetric[protagonist="true"][metricKind="questions"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #162337, stop:0.58 #172b43, stop:1 #142236);
    border: 1px solid #3c5f83;
    border-radius: 16px;
}

QWidget#dashboardRoot QLabel#dashboardProtagonistTitle {
    color: #dce9f5;
    font-size: 9.4pt;
    font-weight: 900;
    letter-spacing: 0.8px;
}

QWidget#dashboardRoot QLabel#dashboardProtagonistBadge {
    color: #a9bed1;
    background-color: rgba(30, 45, 62, 0.82);
    border: 1px solid #40566c;
    border-radius: 7px;
    padding: 3px 7px;
    font-size: 7.2pt;
    font-weight: 800;
    letter-spacing: 0.5px;
}

QWidget#dashboardRoot QLabel#dashboardProtagonistCaption {
    color: #93a9bd;
    font-size: 8.5pt;
    font-weight: 600;
    padding-bottom: 3px;
}

QWidget#dashboardRoot QFrame#dashboardTodayFocus[protagonist="true"] QLabel#dashboardTodayFocusValue {
    color: #ff9aa6;
    font-size: 22pt;
    font-weight: 900;
}

QWidget#dashboardRoot QLabel#dashboardQuestionsHeroValue {
    color: #9cc8ff;
    font-size: 22pt;
    font-weight: 900;
}

QWidget#dashboardRoot QFrame#dashboardTodayMetric[compact="true"] {
    background-color: rgba(20, 32, 46, 0.82);
    border: 1px solid #334b61;
    border-radius: 10px;
}

QWidget#dashboardRoot QFrame#dashboardTodayMetric[compact="true"][metricKind="review"] {
    background-color: rgba(23, 47, 37, 0.88);
    border-color: #3d6951;
}

QWidget#dashboardRoot QFrame#dashboardTodayMetric[compact="true"] QLabel#dashboardTodayMetricValue {
    font-size: 11.5pt;
}
QWidget#dashboardRoot QFrame#dashboardTodayMetric[compact="true"] QLabel#dashboardTodayDetail { font-size: 7.75pt; }

QWidget#dashboardRoot QPushButton#dashboardFocusPrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #b83444, stop:1 #d65361);
    color: #ffffff;
    border: 1px solid #df6672;
    border-radius: 11px;
    font-size: 9.5pt;
    font-weight: 900;
    padding: 8px 18px;
}
QWidget#dashboardRoot QPushButton#dashboardFocusPrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ca4050, stop:1 #e66470);
}

QWidget#dashboardRoot QPushButton#dashboardQuestionsPrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #315f9e, stop:1 #4279c5);
    color: #ffffff;
    border: 1px solid #5486cc;
    border-radius: 11px;
    font-size: 9.5pt;
    font-weight: 900;
    padding: 8px 18px;
}
QWidget#dashboardRoot QPushButton#dashboardQuestionsPrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3a6dae, stop:1 #508bd9);
}

"""


ESTILO_DASHBOARD_MODERNO_FUTURISTA = r"""
/* Dashboard moderno — acabamento do tema futurista */
QWidget#dashboardPage,
QScrollArea#dashboardScroll,
QWidget#dashboardRoot { background-color: #07111e; }

QFrame#dashboardTopBar,
QWidget#dashboardRoot QFrame#dashboardTodayPanel,
QWidget#dashboardRoot QFrame#dashboardQuickAccess,
QWidget#dashboardRoot QFrame#dashboardOverviewCard,
QWidget#dashboardRoot QFrame#dashboardNotificationsPanel,
QWidget#dashboardRoot QFrame#planningPanel,
QWidget#dashboardRoot QFrame#studyNowPanel,
QWidget#dashboardRoot QFrame#priorityQueuePanel,
QWidget#dashboardRoot QFrame#dashboardCenterBar,
QWidget#dashboardRoot QFrame#questionsHeroActions {
    background-color: #0d1d2c;
    border: 1px solid #315b76;
    border-radius: 15px;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0b2132, stop:0.5 #0d2a3e, stop:1 #0b2132);
    border-color: #3c7494;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] {
    background: transparent;
    border: none;
    border-radius: 0px;
}

QWidget#dashboardRoot QFrame#dashboardTodaySeparator {
    background-color: #28546b;
    border: none;
    min-height: 1px;
    max-height: 1px;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#dashboardSectionToggle {
    background: transparent;
    border: none;
    color: #8fc5df;
    font-size: 8.7pt;
    font-weight: 800;
    padding: 4px 4px;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#toolbarButton,
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#pauseNavButton {
    background-color: #0e2638;
    color: #b6d9e8;
    border: 1px solid #35617a;
    border-radius: 9px;
    font-size: 8.8pt;
    font-weight: 700;
    padding: 5px 12px;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#toolbarButton:hover,
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#pauseNavButton:hover {
    background-color: #12344a;
    border-color: #4d8caf;
    color: #e5f8ff;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#focusNavButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #a72b3d, stop:1 #cc4658);
    color: #ffffff;
    border: 1px solid #e06a79;
    border-radius: 9px;
    font-size: 9.2pt;
    font-weight: 850;
    letter-spacing: 0.2px;
    padding: 5px 14px;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#focusNavButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ba3547, stop:1 #df5668);
    border-color: #f18b97;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess QPushButton#dashboardSectionToggle {
    color: #a9dcf4;
    font-size: 9.5pt;
    font-weight: 900;
}

QWidget#dashboardRoot QPushButton#focusNavButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #b51f31, stop:0.52 #d62b3d, stop:1 #f04458);
    color: #ffffff;
    border: 1px solid #ff7382;
    border-radius: 11px;
    font-family: "Segoe UI Semibold";
    font-size: 11pt;
    font-weight: 900;
    letter-spacing: 0.5px;
    padding: 7px 18px;
}

QWidget#dashboardRoot QPushButton#focusNavButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ce293b, stop:0.52 #e83b4c, stop:1 #ff596b);
    border-color: #ffabb3;
}

QWidget#dashboardRoot QPushButton#focusNavButton:pressed {
    background-color: #981827;
    border-color: #ff596b;
}

QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0d2234, stop:0.52 #10314a, stop:1 #102234);
    border: 1px solid #4f88ad;
    border-radius: 18px;
}

QWidget#dashboardRoot QLabel#dashboardGuidedHeroEyebrow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #176991, stop:1 #2f94bf);
    color: #f2fcff;
    border: 1px solid #6bc3e7;
    border-radius: 8px;
    padding: 5px 11px;
    font-size: 8.7pt;
    font-weight: 900;
    letter-spacing: 1px;
}

QWidget#dashboardRoot QFrame#dashboardGuidedInfoCard,
QWidget#dashboardRoot QFrame#dashboardGuidedActionBox {
    background-color: #0a1b2a;
    border: 1px solid #35607b;
}

QWidget#dashboardRoot QLabel#dashboardGuidedInfoHeading {
    color: #dff7ff;
    font-size: 10pt;
    font-weight: 900;
}

QWidget#dashboardRoot QLabel#dashboardGuidedHeroGuide {
    color: #9ec3d5;
    font-size: 8.8pt;
    font-weight: 600;
}

QWidget#dashboardRoot QLabel#dashboardGuidedInfoCriteria {
    background-color: #0e2a3d;
    color: #9be3ff;
    border: 1px solid #397894;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 7.8pt;
    font-weight: 900;
    letter-spacing: 0.3px;
}

QWidget#dashboardRoot QFrame#dashboardGuidedActionBox {
    min-width: 380px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #102d43, stop:1 #091a29);
    border: 2px solid #4f91b8;
    border-radius: 17px;
}

QWidget#dashboardRoot QLabel#dashboardGuidedActionEyebrow {
    color: #8ee2ff;
    font-size: 8.2pt;
    font-weight: 900;
    letter-spacing: 1px;
}

QWidget#dashboardRoot QLabel#dashboardGuidedActionHint {
    color: #9ec9dc;
    font-size: 8.6pt;
    font-weight: 700;
}

QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayPrimaryButton {
    min-width: 320px;
    min-height: 54px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #255cb1, stop:0.5 #3777d6, stop:1 #4d91f2);
    border: 1px solid #8bc0ff;
    border-radius: 15px;
    font-size: 11.5pt;
    font-weight: 900;
}

QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayPrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2f6bc5, stop:0.5 #4388e6, stop:1 #5da4ff);
    border-color: #d2e9ff;
}

QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayPrimaryButton:pressed {
    background-color: #214e94;
    border-color: #79b4f5;
}

QWidget#dashboardRoot QTableWidget#priorityQueueTable {
    background-color: #091724;
    alternate-background-color: #0d2131;
    border-color: #315b76;
    selection-background-color: #155073;
}

QWidget#dashboardRoot QTableWidget#priorityQueueTable QHeaderView::section {
    background-color: #10283a;
    color: #9ec8dc;
    border-bottom-color: #315b76;
}

/* HOJE — dois protagonistas: Foco + Questões */
QWidget#dashboardRoot QFrame#dashboardTodayFocus[protagonist="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #211827, stop:0.55 #2b1d2a, stop:1 #151b28);
    border: 1px solid #875062;
    border-radius: 16px;
}
QWidget#dashboardRoot QFrame#dashboardTodayMetric[protagonist="true"][metricKind="questions"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0c2031, stop:0.55 #0e2b40, stop:1 #0b1f31);
    border: 1px solid #427fa3;
    border-radius: 16px;
}
QWidget#dashboardRoot QLabel#dashboardProtagonistTitle {
    color: #d9f2ff;
    font-size: 9.4pt;
    font-weight: 900;
    letter-spacing: 0.9px;
}
QWidget#dashboardRoot QLabel#dashboardProtagonistBadge {
    color: #9bcce1;
    background-color: rgba(12, 39, 57, 0.86);
    border: 1px solid #37657d;
    border-radius: 7px;
    padding: 3px 7px;
    font-size: 7.2pt;
    font-weight: 800;
    letter-spacing: 0.5px;
}
QWidget#dashboardRoot QLabel#dashboardProtagonistCaption {
    color: #8eb8cc;
    font-size: 8.5pt;
    font-weight: 600;
    padding-bottom: 3px;
}
QWidget#dashboardRoot QFrame#dashboardTodayFocus[protagonist="true"] QLabel#dashboardTodayFocusValue {
    color: #ff9fb0;
    font-size: 22pt;
    font-weight: 900;
}
QWidget#dashboardRoot QLabel#dashboardQuestionsHeroValue {
    color: #91ddff;
    font-size: 22pt;
    font-weight: 900;
}
QWidget#dashboardRoot QFrame#dashboardTodayMetric[compact="true"] {
    background-color: rgba(8, 30, 45, 0.86);
    border: 1px solid #315c73;
    border-radius: 10px;
}
QWidget#dashboardRoot QFrame#dashboardTodayMetric[compact="true"][metricKind="review"] {
    background-color: rgba(17, 49, 41, 0.9);
    border-color: #3f7965;
}
QWidget#dashboardRoot QFrame#dashboardTodayMetric[compact="true"] QLabel#dashboardTodayMetricValue { font-size: 11.5pt; }
QWidget#dashboardRoot QFrame#dashboardTodayMetric[compact="true"] QLabel#dashboardTodayDetail { font-size: 7.75pt; }

QWidget#dashboardRoot QPushButton#dashboardFocusPrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #b93449, stop:1 #dc5368);
    color: #ffffff;
    border: 1px solid #eb7182;
    border-radius: 11px;
    font-size: 9.5pt;
    font-weight: 900;
    padding: 8px 18px;
}
QWidget#dashboardRoot QPushButton#dashboardFocusPrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #cb4055, stop:1 #ef6679);
}
QWidget#dashboardRoot QPushButton#dashboardQuestionsPrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #25678a, stop:1 #358db7);
    color: #ffffff;
    border: 1px solid #57add1;
    border-radius: 11px;
    font-size: 9.5pt;
    font-weight: 900;
    padding: 8px 18px;
}
QWidget#dashboardRoot QPushButton#dashboardQuestionsPrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2d789f, stop:1 #42a0cb);
}

"""


# ============================================================
# Dashboard — módulo Foco + Sessão rápida
# Camada final para manter a mesma linguagem de "Estudo por questões".
# ============================================================

ESTILO_FOCO_DASHBOARD_CLARO = r"""
QWidget#dashboardRoot QFrame#dashboardFocusPanel,
QWidget#dashboardRoot QFrame#dashboardFocusPanel QLabel,
QWidget#dashboardRoot QFrame#dashboardFocusPanel QPushButton {
    font-family: "Segoe UI Variable Text", "Segoe UI";
}
QWidget#dashboardRoot QFrame#dashboardFocusPanel {
    background-color: #ffffff;
    border: 1px solid #d6e0eb;
    border-radius: 16px;
}
QWidget#dashboardRoot QFrame#dashboardFocusPanel QPushButton#dashboardSectionToggle {
    color: #17385f;
    font-size: 10pt;
    font-weight: 800;
    padding: 1px 0px;
}
QWidget#dashboardRoot QLabel#focusDashboardIcon {
    color: #326ca8;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #f7fbff, stop:1 #edf5ff);
    border: 1px solid #c8dcef;
    border-radius: 10px;
    font-size: 17pt;
    font-weight: 700;
}
QWidget#dashboardRoot QLabel#focusDashboardSubtitle {
    color: #708096;
    font-size: 8.55pt;
    font-weight: 500;
}
QWidget#dashboardRoot QFrame#dashboardFocusPanel QLabel#dashboardTodayDate {
    color: #48627f;
    background-color: #f2f6fb;
    border: 1px solid #d7e2ee;
    border-radius: 8px;
    padding: 4px 9px;
    font-size: 7.9pt;
    font-weight: 700;
}
QWidget#dashboardRoot QLabel#focusDashboardMetricText {
    color: #31577f;
    font-size: 8.35pt;
    font-weight: 700;
}
QWidget#dashboardRoot QLabel#focusDashboardMetricText[metricKind="time"] {
    color: #244f80;
}
QWidget#dashboardRoot QLabel#focusDashboardMetricText[metricKind="sessions"] {
    color: #456a8c;
}
QWidget#dashboardRoot QLabel#focusDashboardMetricText[metricKind="goal"] {
    color: #718095;
    font-weight: 600;
}
QWidget#dashboardRoot QFrame#focusDashboardMainCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #fffdfd, stop:0.68 #fffafb, stop:1 #fff7f8);
    border: 1px solid #e7d4d9;
    border-radius: 12px;
}
QWidget#dashboardRoot QFrame#focusQuickCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #fcfeff, stop:0.68 #f8fbfd, stop:1 #f5fbfb);
    border: 1px solid #d2e0e5;
    border-radius: 12px;
}
QWidget#dashboardRoot QLabel#focusDashboardCardIcon {
    color: #be3c50;
    background-color: #fff1f3;
    border: 1px solid #efcbd1;
    border-radius: 11px;
    font-size: 17pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#focusQuickIcon {
    color: #2d7d86;
    background-color: #edf8f8;
    border: 1px solid #c7e1e2;
    border-radius: 11px;
    font-size: 18pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#focusDashboardCardTitle {
    color: #172b48;
    font-size: 11.2pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#focusDashboardBadge {
    color: #a43b4c;
    background-color: #fff3f5;
    border: 1px solid #edcbd1;
    border-radius: 7px;
    padding: 3px 7px;
    font-size: 6.9pt;
    font-weight: 800;
    letter-spacing: 0.45px;
}
QWidget#dashboardRoot QLabel#focusDashboardDescription,
QWidget#dashboardRoot QLabel#focusDashboardDetail,
QWidget#dashboardRoot QLabel#focusQuickHint {
    color: #65758a;
    font-size: 8.45pt;
    font-weight: 500;
}
QWidget#dashboardRoot QLabel#focusDashboardDetail,
QWidget#dashboardRoot QLabel#focusQuickHint {
    color: #708198;
    font-size: 8.15pt;
}
QWidget#dashboardRoot QLabel#focusDashboardCaption {
    color: #756c75;
    font-size: 8.25pt;
    font-weight: 600;
    padding-bottom: 3px;
}
QWidget#dashboardRoot QFrame#focusDashboardMainCard QLabel#dashboardTodayFocusValue {
    color: #c4364a;
    font-size: 22pt;
    font-weight: 850;
}
QWidget#dashboardRoot QLabel#focusQuickEyebrow {
    color: #526b83;
    font-size: 7.45pt;
    font-weight: 800;
    letter-spacing: 0.55px;
}
QWidget#dashboardRoot QFrame#focusDashboardMainCard QPushButton#dashboardFocusPrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #c43a4d, stop:1 #da5261);
    color: #ffffff;
    border: 1px solid #b83245;
    border-radius: 10px;
    font-size: 9.15pt;
    font-weight: 800;
    padding: 8px 16px;
}
QWidget#dashboardRoot QFrame#focusDashboardMainCard QPushButton#dashboardFocusPrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #b43144, stop:1 #cc4657);
    border-color: #a42b3c;
}
QWidget#dashboardRoot QFrame#focusDashboardMainCard QPushButton#dashboardFocusPrimaryButton:pressed {
    background-color: #aa2f40;
    border-color: #972637;
}
QWidget#dashboardRoot QPushButton#focusQuickPresetButton {
    background-color: #ffffff;
    color: #49677f;
    border: 1px solid #cad8e4;
    border-radius: 9px;
    font-size: 8.65pt;
    font-weight: 700;
    padding: 6px 10px;
}
QWidget#dashboardRoot QPushButton#focusQuickPresetButton:hover {
    background-color: #f2f8fa;
    border-color: #9ec4c8;
    color: #2b737b;
}
QWidget#dashboardRoot QPushButton#focusQuickPresetButton:checked {
    background-color: #eaf7f7;
    color: #226f77;
    border: 1px solid #67aeb1;
    font-weight: 800;
}
QWidget#dashboardRoot QPushButton#focusQuickStartButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2f8790, stop:1 #3d9ba3);
    color: #ffffff;
    border: 1px solid #2b7d85;
    border-radius: 10px;
    font-size: 9.15pt;
    font-weight: 800;
    padding: 8px 16px;
}
QWidget#dashboardRoot QPushButton#focusQuickStartButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #297981, stop:1 #358d95);
    border-color: #246e75;
}
QWidget#dashboardRoot QPushButton#focusQuickStartButton:pressed {
    background-color: #256f77;
    border-color: #1f6168;
}
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] {
    background-color: #f7f9fc;
    border: 1px solid #dce5ef;
    border-radius: 10px;
}
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#dashboardSectionToggle {
    color: #536a82;
    font-size: 8.55pt;
    font-weight: 800;
    padding: 4px 3px;
}
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#toolbarButton,
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#pauseNavButton {
    background-color: #ffffff;
    color: #294967;
    border: 1px solid #d0dce8;
    border-radius: 9px;
    font-size: 8.6pt;
    font-weight: 700;
    padding: 5px 12px;
}
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#toolbarButton:hover,
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#pauseNavButton:hover {
    background-color: #edf4fb;
    border-color: #b5cadf;
    color: #1f5b91;
}
"""

ESTILO_FOCO_DASHBOARD_ESCURO = r"""
QWidget#dashboardRoot QFrame#dashboardFocusPanel,
QWidget#dashboardRoot QFrame#dashboardFocusPanel QLabel,
QWidget#dashboardRoot QFrame#dashboardFocusPanel QPushButton {
    font-family: "Segoe UI Variable Text", "Segoe UI";
}
QWidget#dashboardRoot QFrame#dashboardFocusPanel {
    background-color: #151f2d;
    border: 1px solid #304357;
    border-radius: 16px;
}
QWidget#dashboardRoot QFrame#dashboardFocusPanel QPushButton#dashboardSectionToggle {
    color: #e7f0f8;
    font-size: 10pt;
    font-weight: 800;
    padding: 1px 0px;
}
QWidget#dashboardRoot QLabel#focusDashboardIcon {
    color: #9bcaf1;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1c2c3d, stop:1 #17283a);
    border: 1px solid #3a536c;
    border-radius: 10px;
    font-size: 17pt;
    font-weight: 700;
}
QWidget#dashboardRoot QLabel#focusDashboardSubtitle {
    color: #91a2b6;
    font-size: 8.55pt;
    font-weight: 500;
}
QWidget#dashboardRoot QFrame#dashboardFocusPanel QLabel#dashboardTodayDate {
    color: #aac0d4;
    background-color: #1b2a3a;
    border: 1px solid #344b61;
    border-radius: 8px;
    padding: 4px 9px;
    font-size: 7.9pt;
    font-weight: 700;
}
QWidget#dashboardRoot QLabel#focusDashboardMetricText {
    color: #a4bfd9;
    font-size: 8.35pt;
    font-weight: 700;
}
QWidget#dashboardRoot QLabel#focusDashboardMetricText[metricKind="time"] { color: #b6d5f1; }
QWidget#dashboardRoot QLabel#focusDashboardMetricText[metricKind="sessions"] { color: #9eb7ce; }
QWidget#dashboardRoot QLabel#focusDashboardMetricText[metricKind="goal"] { color: #8294a8; font-weight: 600; }
QWidget#dashboardRoot QFrame#focusDashboardMainCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #241d25, stop:0.7 #281f26, stop:1 #2b2027);
    border: 1px solid #66434d;
    border-radius: 12px;
}
QWidget#dashboardRoot QFrame#focusQuickCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #172534, stop:0.7 #152432, stop:1 #142732);
    border: 1px solid #355461;
    border-radius: 12px;
}
QWidget#dashboardRoot QLabel#focusDashboardCardIcon {
    color: #ff9cab;
    background-color: #37242b;
    border: 1px solid #774854;
    border-radius: 11px;
    font-size: 17pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#focusQuickIcon {
    color: #8ed4d9;
    background-color: #173438;
    border: 1px solid #3e6a6f;
    border-radius: 11px;
    font-size: 18pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#focusDashboardCardTitle {
    color: #edf3f8;
    font-size: 11.2pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#focusDashboardBadge {
    color: #f0b0ba;
    background-color: #3a272e;
    border: 1px solid #714752;
    border-radius: 7px;
    padding: 3px 7px;
    font-size: 6.9pt;
    font-weight: 800;
    letter-spacing: 0.45px;
}
QWidget#dashboardRoot QLabel#focusDashboardDescription,
QWidget#dashboardRoot QLabel#focusDashboardDetail,
QWidget#dashboardRoot QLabel#focusQuickHint {
    color: #9babbc;
    font-size: 8.45pt;
    font-weight: 500;
}
QWidget#dashboardRoot QLabel#focusDashboardDetail,
QWidget#dashboardRoot QLabel#focusQuickHint {
    color: #8fa2b5;
    font-size: 8.15pt;
}
QWidget#dashboardRoot QLabel#focusDashboardCaption {
    color: #b99aa3;
    font-size: 8.25pt;
    font-weight: 600;
    padding-bottom: 3px;
}
QWidget#dashboardRoot QFrame#focusDashboardMainCard QLabel#dashboardTodayFocusValue {
    color: #ff90a1;
    font-size: 22pt;
    font-weight: 850;
}
QWidget#dashboardRoot QLabel#focusQuickEyebrow {
    color: #91a9bf;
    font-size: 7.45pt;
    font-weight: 800;
    letter-spacing: 0.55px;
}
QWidget#dashboardRoot QFrame#focusDashboardMainCard QPushButton#dashboardFocusPrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #a92f40, stop:1 #c84958);
    color: #ffffff;
    border: 1px solid #d35a68;
    border-radius: 10px;
    font-size: 9.15pt;
    font-weight: 800;
    padding: 8px 16px;
}
QWidget#dashboardRoot QFrame#focusDashboardMainCard QPushButton#dashboardFocusPrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ba3a4a, stop:1 #d85866);
    border-color: #e36f7a;
}
QWidget#dashboardRoot QPushButton#focusQuickPresetButton {
    background-color: #182635;
    color: #bed0e0;
    border: 1px solid #354d61;
    border-radius: 9px;
    font-size: 8.65pt;
    font-weight: 700;
    padding: 6px 10px;
}
QWidget#dashboardRoot QPushButton#focusQuickPresetButton:hover {
    background-color: #20343f;
    border-color: #4f7a7f;
    color: #d9f0f1;
}
QWidget#dashboardRoot QPushButton#focusQuickPresetButton:checked {
    background-color: #1c4145;
    color: #bcebed;
    border: 1px solid #5f9ca1;
    font-weight: 800;
}
QWidget#dashboardRoot QPushButton#focusQuickStartButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2e7780, stop:1 #3a9097);
    color: #ffffff;
    border: 1px solid #4a9aa2;
    border-radius: 10px;
    font-size: 9.15pt;
    font-weight: 800;
    padding: 8px 16px;
}
QWidget#dashboardRoot QPushButton#focusQuickStartButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #378891, stop:1 #47a1a8);
    border-color: #66b3b9;
}
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] {
    background-color: #182331;
    border: 1px solid #30465a;
    border-radius: 10px;
}
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#dashboardSectionToggle {
    color: #9fb5ca;
    font-size: 8.55pt;
    font-weight: 800;
    padding: 4px 3px;
}
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#toolbarButton,
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#pauseNavButton {
    background-color: #1b2938;
    color: #c2d1df;
    border: 1px solid #344b60;
    border-radius: 9px;
    font-size: 8.6pt;
    font-weight: 700;
    padding: 5px 12px;
}
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#toolbarButton:hover,
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#pauseNavButton:hover {
    background-color: #22364a;
    border-color: #4a6d8a;
    color: #e5f0f9;
}
"""

ESTILO_FOCO_DASHBOARD_FUTURISTA = r"""
QWidget#dashboardRoot QLabel#focusDashboardMetricText[metricKind="time"] { color: #CBD5E1; }
QWidget#dashboardRoot QLabel#focusDashboardMetricText[metricKind="sessions"] { color: #AEB7C4; }
QWidget#dashboardRoot QLabel#focusDashboardMetricText[metricKind="goal"] { color: #8E97A6; font-weight: 600; }
QWidget#dashboardRoot QFrame#focusDashboardMainCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #232A36, stop:0.6 #242B37, stop:1 #202733);
    border: 1px solid #4B5667;
    border-radius: 12px;
}
QWidget#dashboardRoot QFrame#focusQuickCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #202833, stop:0.7 #212935, stop:1 #1E2531);
    border: 1px solid #465163;
    border-radius: 12px;
}
QWidget#dashboardRoot QLabel#focusDashboardCardIcon {
    color: #F6A9B5;
    background-color: #3B2A33;
    border: 1px solid #8E6271;
    border-radius: 11px;
    font-size: 17pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#focusQuickIcon {
    color: #D8FFF4;
    background-color: #2A4247;
    border: 1px solid #68998F;
    border-radius: 11px;
    font-size: 18pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#focusDashboardCardTitle {
    color: #F4F7FB;
    font-size: 11.2pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#focusDashboardBadge {
    color: #FFC5CF;
    background-color: rgba(84, 50, 59, 228);
    border: 1px solid #976874;
    border-radius: 7px;
    padding: 3px 7px;
    font-size: 6.9pt;
    font-weight: 800;
    letter-spacing: 0.45px;
}
QWidget#dashboardRoot QLabel#focusDashboardDescription,
QWidget#dashboardRoot QLabel#focusDashboardDetail,
QWidget#dashboardRoot QLabel#focusQuickHint {
    color: #C2CAD4;
    font-size: 8.45pt;
    font-weight: 500;
}
QWidget#dashboardRoot QLabel#focusDashboardDetail,
QWidget#dashboardRoot QLabel#focusQuickHint {
    color: #BAC4CF;
    font-size: 8.15pt;
}
QWidget#dashboardRoot QLabel#focusDashboardCaption {
    color: #D2AAB3;
    font-size: 8.25pt;
    font-weight: 600;
    padding-bottom: 3px;
}
QWidget#dashboardRoot QFrame#focusDashboardMainCard QLabel#dashboardTodayFocusValue {
    color: #F6AAB5;
    font-size: 22pt;
    font-weight: 850;
}
QWidget#dashboardRoot QLabel#focusQuickEyebrow {
    color: #C0CAD5;
    font-size: 7.45pt;
    font-weight: 800;
    letter-spacing: 0.55px;
}
QWidget#dashboardRoot QFrame#focusDashboardMainCard QPushButton#dashboardFocusPrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4447E8, stop:1 #3B40D4);
    color: #FFFFFF;
    border: 1px solid #7C83FF;
    border-radius: 10px;
    font-size: 9.15pt;
    font-weight: 800;
    padding: 8px 16px;
}
QWidget#dashboardRoot QFrame#focusDashboardMainCard QPushButton#dashboardFocusPrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5254F3, stop:1 #484DE0);
    border-color: #AAB1FF;
}
QWidget#dashboardRoot QFrame#focusDashboardMainCard QPushButton#dashboardFocusPrimaryButton:pressed {
    background-color: #363BB8;
    border-color: #6C73F4;
}
QWidget#dashboardRoot QPushButton#focusQuickPresetButton {
    background-color: #232C37;
    color: #D4DCE6;
    border: 1px solid #566173;
    border-radius: 9px;
    font-size: 8.65pt;
    font-weight: 700;
    padding: 6px 10px;
}
QWidget#dashboardRoot QPushButton#focusQuickPresetButton:hover {
    background-color: #2A3442;
    border-color: #728096;
    color: #F2F5F9;
}
QWidget#dashboardRoot QPushButton#focusQuickPresetButton:checked {
    background-color: #2F3A4A;
    color: #FFFFFF;
    border: 1px solid #8D9AB0;
    font-weight: 800;
}
QWidget#dashboardRoot QPushButton#focusQuickStartButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4447E8, stop:1 #3B40D4);
    color: #FFFFFF;
    border: 1px solid #7C83FF;
    border-radius: 10px;
    font-size: 9.15pt;
    font-weight: 800;
    padding: 8px 16px;
}
QWidget#dashboardRoot QPushButton#focusQuickStartButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5254F3, stop:1 #484DE0);
    border-color: #AAB1FF;
}
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] {
    background-color: #212935;
    border: 1px solid #475365;
    border-radius: 10px;
}
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#dashboardSectionToggle {
    color: #CDD6E0;
    font-size: 8.55pt;
    font-weight: 800;
    padding: 4px 3px;
}
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#toolbarButton,
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#pauseNavButton {
    background-color: #222B36;
    color: #D5DDE7;
    border: 1px solid #556072;
    border-radius: 9px;
    font-size: 8.6pt;
    font-weight: 700;
    padding: 5px 12px;
}
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#toolbarButton:hover,
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#pauseNavButton:hover {
    background-color: #2B3542;
    border-color: #758297;
    color: #FFFFFF;
}
"""

ESTILO_ALGORITMO_DASHBOARD_CLARO = r"""
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] {
    background-color: #ffffff;
    border: 1px solid #d3dce9;
    border-radius: 13px;
}
QWidget#dashboardRoot QLabel#algorithmDashboardIcon {
    background-color: #edf6ff;
    color: #2b67aa;
    border: 1px solid #c7dcf4;
    border-radius: 14px;
    font-size: 20px;
    font-weight: 900;
}
QWidget#dashboardRoot QLabel#algorithmDashboardTitle {
    color: #111827;
    font-size: 10.2pt;
    font-weight: 900;
}
QWidget#dashboardRoot QLabel#algorithmDashboardSubtitle {
    color: #58677c;
    font-size: 8.8pt;
}
QWidget#dashboardRoot QLabel#algorithmDashboardReady {
    color: #2b639d;
    font-size: 8.4pt;
    font-weight: 900;
    letter-spacing: 0.9px;
}
QWidget#dashboardRoot QPushButton#algorithmDashboardHelp {
    background-color: #fbfdff;
    color: #315b87;
    border: 1px solid #d2dfec;
    border-radius: 9px;
    font-size: 9pt;
    font-weight: 800;
}
QWidget#dashboardRoot QPushButton#algorithmDashboardHelp:hover {
    background-color: #f0f6fd;
    border-color: #b7cfe7;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayPrimaryButton {
    min-width: 320px;
    min-height: 40px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #245dcc, stop:0.52 #2f6edc, stop:1 #3e7fec);
    color: #ffffff;
    border: 1px solid #1d52b4;
    border-radius: 10px;
    font-family: "Segoe UI Semibold";
    font-size: 10.4pt;
    font-weight: 900;
    letter-spacing: 0.2px;
    padding: 5px 18px;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayPrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1f52b8, stop:0.52 #2862c8, stop:1 #3673d9);
    border-color: #16469e;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayPrimaryButton:pressed {
    background-color: #1d52b4;
    border-color: #153f8d;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayButton {
    background: transparent;
    color: #2c6196;
    border: none;
    border-radius: 0px;
    font-size: 8.8pt;
    font-weight: 800;
    text-decoration: underline;
    padding: 3px 8px;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayButton:hover {
    background: transparent;
    color: #164d86;
}
"""

ESTILO_ALGORITMO_DASHBOARD_ESCURO = r"""
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] {
    background-color: #101b29;
    border: 1px solid #304157;
    border-radius: 13px;
}
QWidget#dashboardRoot QLabel#algorithmDashboardIcon {
    background-color: #17304b;
    color: #a9d3ff;
    border: 1px solid #365e83;
    border-radius: 14px;
    font-size: 20px;
    font-weight: 900;
}
QWidget#dashboardRoot QLabel#algorithmDashboardTitle {
    color: #f3f6fb;
    font-size: 10.2pt;
    font-weight: 900;
}
QWidget#dashboardRoot QLabel#algorithmDashboardSubtitle {
    color: #94a4b9;
    font-size: 8.8pt;
}
QWidget#dashboardRoot QLabel#algorithmDashboardReady {
    color: #9cc9f3;
    font-size: 8.4pt;
    font-weight: 900;
    letter-spacing: 0.9px;
}
QWidget#dashboardRoot QPushButton#algorithmDashboardHelp {
    background-color: #132131;
    color: #a8c7e5;
    border: 1px solid #354a61;
    border-radius: 9px;
    font-size: 9pt;
    font-weight: 800;
}
QWidget#dashboardRoot QPushButton#algorithmDashboardHelp:hover {
    background-color: #192b40;
    border-color: #4c6682;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayPrimaryButton {
    min-width: 320px;
    min-height: 40px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #315fae, stop:0.52 #3f72c8, stop:1 #5488de);
    color: #ffffff;
    border: 1px solid #78a7ee;
    border-radius: 10px;
    font-family: "Segoe UI Semibold";
    font-size: 10.4pt;
    font-weight: 900;
    letter-spacing: 0.2px;
    padding: 5px 18px;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayPrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3c6cbc, stop:0.52 #4c80d4, stop:1 #6297e9);
    border-color: #a3c6ff;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayPrimaryButton:pressed {
    background-color: #294f91;
    border-color: #6f9cde;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayButton {
    background: transparent;
    color: #9ec7ee;
    border: none;
    border-radius: 0px;
    font-size: 8.8pt;
    font-weight: 800;
    text-decoration: underline;
    padding: 3px 8px;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayButton:hover {
    background: transparent;
    color: #d7eaff;
}
"""

ESTILO_ALGORITMO_DASHBOARD_FUTURISTA = r"""
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #202733, stop:0.55 #222A36, stop:1 #1D2430
    );
    border: 1px solid #475363;
    border-radius: 14px;
}
QWidget#dashboardRoot QLabel#algorithmDashboardIcon {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #3B4554, stop:1 #2E3643
    );
    color: #E5ECF3;
    border: 1px solid #626E80;
    border-radius: 14px;
    font-size: 20px;
    font-weight: 900;
}
QWidget#dashboardRoot QLabel#algorithmDashboardTitle {
    color: #F3F7FB;
    font-size: 10.2pt;
    font-weight: 900;
}
QWidget#dashboardRoot QLabel#algorithmDashboardSubtitle {
    color: #B5BFCA;
    font-size: 8.8pt;
}
QWidget#dashboardRoot QLabel#algorithmDashboardReady {
    color: #C3CCD8;
    font-size: 8.4pt;
    font-weight: 900;
    letter-spacing: 0.9px;
}
QWidget#dashboardRoot QPushButton#algorithmDashboardHelp {
    background-color: #262E3A;
    color: #CFD7E1;
    border: 1px solid #596577;
    border-radius: 9px;
    font-size: 9pt;
    font-weight: 800;
}
QWidget#dashboardRoot QPushButton#algorithmDashboardHelp:hover {
    background-color: #303948;
    border-color: #7B8698;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayPrimaryButton {
    min-width: 320px;
    min-height: 40px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4447E8, stop:0.5 #4347E1, stop:1 #3C42D2);
    color: #FFFFFF;
    border: 1px solid #7C83FF;
    border-radius: 10px;
    font-family: "Segoe UI Semibold";
    font-size: 10.4pt;
    font-weight: 900;
    letter-spacing: 0.2px;
    padding: 5px 18px;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayPrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5355F2, stop:0.5 #4F54EB, stop:1 #464DDE);
    border-color: #B1B7FF;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayPrimaryButton:pressed {
    background-color: #363BB8;
    border-color: #6C73F4;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayButton {
    background: transparent;
    color: #C9D2DE;
    border: none;
    border-radius: 0px;
    font-size: 8.8pt;
    font-weight: 800;
    text-decoration: underline;
    padding: 3px 8px;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayButton:hover {
    background: transparent;
    color: #F3F7FB;
}
"""

ESTILO_BUSCA_GLOBAL_CLARO = r"""
QWidget#dashboardRoot QPushButton#globalSearchTrigger {
    background-color: #f7f9fc;
    color: #607086;
    border: 1px solid #d8e2ee;
    border-radius: 10px;
    font-size: 8.8pt;
    font-weight: 650;
    text-align: left;
    padding: 6px 11px;
}
QWidget#dashboardRoot QPushButton#globalSearchTrigger:hover {
    background-color: #eef5ff;
    color: #285f9d;
    border-color: #b9d1ec;
}
QDialog#globalSearchDialog {
    background-color: #f5f8fc;
}
QDialog#globalSearchDialog QLabel#globalSearchTitle {
    color: #10233f;
    font-size: 16pt;
    font-weight: 900;
}
QDialog#globalSearchDialog QLabel#globalSearchSubtitle,
QDialog#globalSearchDialog QLabel#globalSearchStatus,
QDialog#globalSearchDialog QLabel#globalSearchHint {
    color: #718096;
    font-size: 8.7pt;
}
QDialog#globalSearchDialog QLabel#globalSearchShortcut {
    background-color: #edf3fa;
    color: #49637f;
    border: 1px solid #d1deeb;
    border-radius: 7px;
    padding: 4px 8px;
    font-size: 8pt;
    font-weight: 800;
}
QDialog#globalSearchDialog QLineEdit#globalSearchInput {
    min-height: 38px;
    background-color: #ffffff;
    color: #16263d;
    border: 1px solid #bfd1e5;
    border-radius: 10px;
    padding: 0 12px;
    font-size: 10pt;
    selection-background-color: #cfe2fb;
}
QDialog#globalSearchDialog QLineEdit#globalSearchInput:focus {
    border: 1px solid #4b88cf;
}
QDialog#globalSearchDialog QTableWidget#globalSearchResults {
    background-color: #ffffff;
    alternate-background-color: #f8fbff;
    color: #203149;
    border: 1px solid #d8e3ef;
    border-radius: 10px;
    gridline-color: transparent;
    selection-background-color: #e7f1ff;
    selection-color: #174f8a;
}
QDialog#globalSearchDialog QTableWidget#globalSearchResults::item {
    border-bottom: 1px solid #edf2f7;
    padding: 6px 8px;
}
QDialog#globalSearchDialog QHeaderView::section {
    background-color: #f4f7fb;
    color: #617187;
    border: none;
    border-bottom: 1px solid #dbe5ef;
    padding: 7px 8px;
    font-size: 8pt;
    font-weight: 800;
}
"""

ESTILO_BUSCA_GLOBAL_ESCURO = r"""
QWidget#dashboardRoot QPushButton#globalSearchTrigger {
    background-color: #111b28;
    color: #9eb0c3;
    border: 1px solid #30445a;
    border-radius: 10px;
    font-size: 8.8pt;
    font-weight: 650;
    text-align: left;
    padding: 6px 11px;
}
QWidget#dashboardRoot QPushButton#globalSearchTrigger:hover {
    background-color: #17263a;
    color: #cce3fb;
    border-color: #486887;
}
QDialog#globalSearchDialog {
    background-color: #0f1722;
}
QDialog#globalSearchDialog QLabel#globalSearchTitle {
    color: #f2f6fb;
    font-size: 16pt;
    font-weight: 900;
}
QDialog#globalSearchDialog QLabel#globalSearchSubtitle,
QDialog#globalSearchDialog QLabel#globalSearchStatus,
QDialog#globalSearchDialog QLabel#globalSearchHint {
    color: #8fa1b5;
    font-size: 8.7pt;
}
QDialog#globalSearchDialog QLabel#globalSearchShortcut {
    background-color: #172334;
    color: #a9bdd2;
    border: 1px solid #34495f;
    border-radius: 7px;
    padding: 4px 8px;
    font-size: 8pt;
    font-weight: 800;
}
QDialog#globalSearchDialog QLineEdit#globalSearchInput {
    min-height: 38px;
    background-color: #111c2a;
    color: #edf4fb;
    border: 1px solid #3d5873;
    border-radius: 10px;
    padding: 0 12px;
    font-size: 10pt;
    selection-background-color: #315f91;
}
QDialog#globalSearchDialog QLineEdit#globalSearchInput:focus {
    border: 1px solid #6aa3df;
}
QDialog#globalSearchDialog QTableWidget#globalSearchResults {
    background-color: #111c2a;
    color: #dbe6f1;
    border: 1px solid #30465e;
    border-radius: 10px;
    gridline-color: transparent;
    selection-background-color: #203d5d;
    selection-color: #eaf5ff;
}
QDialog#globalSearchDialog QTableWidget#globalSearchResults::item {
    border-bottom: 1px solid #203044;
    padding: 6px 8px;
}
QDialog#globalSearchDialog QHeaderView::section {
    background-color: #142131;
    color: #90a4b8;
    border: none;
    border-bottom: 1px solid #30445a;
    padding: 7px 8px;
    font-size: 8pt;
    font-weight: 800;
}
"""


# ============================================================
# Dashboard — Futurista Neo
# Camada final de refinamento visual do Dashboard futurista.
# Não altera o módulo Foco: os seletores abaixo evitam deliberadamente
# dashboardFocusPanel/focusDashboardMainCard/dashboardFocusPrimaryButton.
# ============================================================
ESTILO_DASHBOARD_NEO_FUTURISTA = r"""
/* Base — paleta escura neutra com acentos azul-violeta e verde. */
QWidget#dashboardPage,
QScrollArea#dashboardScroll,
QWidget#dashboardRoot {
    background-color: #0B111D;
}

QWidget#dashboardRoot QLabel#pageTitle {
    color: #F5F7FB;
    font-size: 20px;
    font-weight: 900;
}
QWidget#dashboardRoot QLabel#pageSubtitle {
    color: #B4BECA;
    font-size: 9pt;
}

QWidget#dashboardRoot QFrame#dashboardTopBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0D1420, stop:0.52 #0F1622, stop:1 #0C1320);
    border: 1px solid #1E2634;
    border-radius: 16px;
}
QWidget#dashboardRoot QFrame#topProfileBar {
    background-color: #111925;
    border: 1px solid #313948;
    border-radius: 11px;
}
QWidget#dashboardRoot QLabel#topProfileLabel {
    color: #BDC6D1;
    font-size: 8.2pt;
    font-weight: 800;
    letter-spacing: 0.7px;
}
QWidget#dashboardRoot QComboBox#topProfileCombo {
    background-color: #202935;
    color: #F2F5F9;
    border: 1px solid #4A5362;
    border-radius: 9px;
    padding: 4px 10px;
}
QWidget#dashboardRoot QComboBox#topProfileCombo:hover,
QWidget#dashboardRoot QComboBox#topProfileCombo:focus {
    background-color: #293341;
    border-color: #6D7888;
}

QWidget#dashboardRoot QPushButton#globalSearchTrigger {
    background-color: #212A35;
    color: #C2CAD4;
    border: 1px solid #48515F;
    border-radius: 11px;
    font-size: 8.8pt;
    font-weight: 700;
    text-align: left;
    padding: 6px 12px;
}
QWidget#dashboardRoot QPushButton#globalSearchTrigger:hover {
    background-color: #293342;
    color: #F3F7FB;
    border-color: #636E7D;
}

QWidget#dashboardRoot QPushButton#questionsNavButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #212A35, stop:1 #1F2732);
    color: #F7FAFC;
    border: 1px solid #666F7C;
    border-radius: 10px;
    font-weight: 850;
    padding: 6px 15px;
}
QWidget#dashboardRoot QPushButton#questionsNavButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #283241, stop:1 #252E3B);
    border-color: #8892A0;
}
QWidget#dashboardRoot QPushButton#questionsNavButton:pressed {
    background-color: #1A212C;
    border-color: #596371;
}

QWidget#dashboardRoot QPushButton#topAccentButton {
    background-color: #232C38;
    border: 1px solid #5E6876;
    border-radius: 11px;
    padding: 0px;
}
QWidget#dashboardRoot QPushButton#topAccentButton:hover {
    background-color: #2B3542;
    border-color: #7B8695;
}
QWidget#dashboardRoot QPushButton#topAccentButton:pressed {
    background-color: #1C2430;
}

QWidget#dashboardRoot QPushButton#subtleButton {
    background-color: #232B36;
    color: #D1D9E2;
    border: 1px solid #5A6472;
    border-radius: 9px;
    font-weight: 700;
    padding: 5px 12px;
}
QWidget#dashboardRoot QPushButton#subtleButton:hover {
    background-color: #2C3643;
    color: #FFFFFF;
    border-color: #7A8594;
}

QWidget#dashboardRoot QFrame#dashboardInsightSummary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #202733, stop:0.52 #222A36, stop:1 #1D2430);
    border: 1px solid #475364;
    border-radius: 15px;
}
QWidget#dashboardRoot QLabel#dashboardInsightSummaryIcon {
    color: #E5ECF3;
    background-color: #39414D;
    border: 1px solid #697587;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 900;
}
QWidget#dashboardRoot QLabel#dashboardInsightSummaryTitle {
    color: #F3F7FB;
    font-size: 10.7pt;
    font-weight: 850;
}
QWidget#dashboardRoot QLabel#dashboardInsightSummaryDate {
    color: #B8C1CD;
    font-size: 8.5pt;
}
QWidget#dashboardRoot QLabel#dashboardPlanningHeroTitle {
    color: #D7DEE7;
    font-size: 8.8pt;
    font-weight: 850;
    letter-spacing: 0.6px;
}
QWidget#dashboardRoot QLabel#dashboardPlanningHeroValue {
    color: #F8FAFC;
    font-size: 25pt;
    font-weight: 900;
}
QWidget#dashboardRoot QLabel#dashboardPlanningHeroDetail {
    color: #C3CBD5;
    font-size: 8.4pt;
    font-weight: 600;
}
QWidget#dashboardRoot QProgressBar#dashboardInsightSummaryProgress {
    background-color: #3B424F;
    border: none;
    border-radius: 4px;
}
QWidget#dashboardRoot QProgressBar#dashboardInsightSummaryProgress::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #B9FFE3, stop:1 #D5FFF0);
    border-radius: 4px;
}
QWidget#dashboardRoot QFrame#dashboardPlanningOperational {
    background-color: transparent;
    border: none;
    border-radius: 0px;
}
QWidget#dashboardRoot QLabel#dashboardInsightSummaryRowTitle {
    color: #EFF4F9;
    font-size: 8.6pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#dashboardPlanningOperationalValue {
    color: #F9FBFC;
    font-size: 12.7pt;
    font-weight: 900;
}
QWidget#dashboardRoot QLabel#dashboardInsightSummaryRowDetail {
    color: #C0C8D2;
    font-size: 8.2pt;
}
QWidget#dashboardRoot QFrame#dashboardPlanningDivider {
    color: rgba(191, 201, 214, 0.28);
    background-color: rgba(191, 201, 214, 0.28);
    border: none;
    max-width: 1px;
}
QWidget#dashboardRoot QLabel#dashboardPlanningWeekLabel {
    color: #C8D0DA;
    font-size: 7.8pt;
    font-weight: 700;
}
QWidget#dashboardRoot QLabel#weeklyGoalStatus {
    background-color: #3E4654;
    color: #E7EDF3;
    border: 1px solid #616C7A;
    border-radius: 9px;
    padding: 3px 9px;
    font-size: 7.7pt;
    font-weight: 800;
}
QWidget#dashboardRoot QLabel#weeklyGoalStatus[weekState="concluida"] {
    background-color: #305345;
    color: #D2FFE7;
    border-color: #58A07A;
}
QWidget#dashboardRoot QLabel#weeklyGoalStatus[weekState="atencao"] {
    background-color: #5A402D;
    color: #FFE2C0;
    border-color: #D39A64;
}
QWidget#dashboardRoot QLabel#weeklyGoalStatus[weekState="andamento"] {
    background-color: #46506A;
    color: #E6EBFF;
    border-color: #707AA0;
}
QWidget#dashboardRoot QPushButton#planningSummaryButton {
    background-color: #202833;
    color: #E0E7EF;
    border: 1px solid #596474;
    border-radius: 11px;
    font-weight: 800;
    padding: 7px 12px;
}
QWidget#dashboardRoot QPushButton#planningSummaryButton:hover {
    background-color: #293341;
    color: #FFFFFF;
    border-color: #7B8698;
}

QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"],
QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #202733, stop:0.52 #222A36, stop:1 #1D2430);
    border: 1px solid #475364;
    border-radius: 15px;
}
QWidget#dashboardRoot QLabel#algorithmDashboardIcon {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #404957, stop:1 #2F3744);
    color: #E5ECF3;
    border: 1px solid #697587;
    border-radius: 13px;
}
QWidget#dashboardRoot QLabel#algorithmDashboardTitle {
    color: #F3F7FB;
    font-size: 10.4pt;
    font-weight: 900;
}
QWidget#dashboardRoot QLabel#algorithmDashboardSubtitle {
    color: #B4BEC9;
    font-size: 8.7pt;
}
QWidget#dashboardRoot QPushButton#algorithmDashboardHelp {
    background-color: #252E3A;
    color: #D1D9E2;
    border: 1px solid #5E6A7C;
    border-radius: 9px;
}
QWidget#dashboardRoot QPushButton#algorithmDashboardHelp:hover {
    background-color: #2F3947;
    color: #FFFFFF;
    border-color: #7E899A;
}
QWidget#dashboardRoot QFrame#algorithmRecommendationBody {
    background-color: #202833;
    border: 1px solid #465263;
    border-radius: 11px;
}
QWidget#dashboardRoot QLabel#algorithmDashboardReady {
    color: #C4CDD8;
    font-size: 8.4pt;
    font-weight: 900;
    letter-spacing: 1px;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayPrimaryButton,
QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayPrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4447E8, stop:0.52 #4347E1, stop:1 #3C42D2);
    color: #FFFFFF;
    border: 1px solid #7C83FF;
    border-radius: 11px;
    font-size: 10.5pt;
    font-weight: 900;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayPrimaryButton:hover,
QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayPrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5355F2, stop:0.52 #4F54EB, stop:1 #464DDE);
    border-color: #B1B7FF;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayButton,
QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayButton {
    background: transparent;
    color: #CBD3DE;
    border: none;
    text-decoration: underline;
    font-weight: 750;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayButton:hover,
QWidget#dashboardRoot QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayButton:hover {
    color: #F4F7FB;
}

QWidget#dashboardRoot QFrame#focusQuickCard[cardRole="progress"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #14A779, stop:0.55 #13835F, stop:1 #16534D);
    border: 1px solid #39C39A;
    border-radius: 15px;
}
QWidget#dashboardRoot QFrame#focusQuickCard[cardRole="progress"] QLabel#focusQuickIcon {
    background-color: rgba(255, 255, 255, 0.12);
    color: #E8FFF8;
    border: 1px solid rgba(232, 255, 248, 0.35);
    border-radius: 10px;
}
QWidget#dashboardRoot QFrame#focusQuickCard[cardRole="progress"] QLabel#focusDashboardCardTitle {
    color: #F6FFFC;
    font-weight: 850;
}
QWidget#dashboardRoot QFrame#focusQuickCard[cardRole="progress"] QLabel#focusDashboardDescription,
QWidget#dashboardRoot QFrame#focusQuickCard[cardRole="progress"] QLabel#focusDashboardDetail,
QWidget#dashboardRoot QFrame#focusQuickCard[cardRole="progress"] QLabel#focusQuickHint {
    color: #D7FFF3;
}
QWidget#dashboardRoot QFrame#focusQuickCard[cardRole="progress"] QLabel#dashboardProgressBadge {
    background-color: rgba(255, 255, 255, 0.14);
    color: #F7FFFC;
    border: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: 20px;
    font-size: 10pt;
    font-weight: 900;
}
QWidget#dashboardRoot QFrame#focusQuickCard[cardRole="progress"] QProgressBar#dashboardTodayProgress {
    background-color: rgba(12, 43, 37, 0.45);
    border: none;
    border-radius: 4px;
}
QWidget#dashboardRoot QFrame#focusQuickCard[cardRole="progress"] QProgressBar#dashboardTodayProgress::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #B7FFE6, stop:1 #F0FFF9);
    border-radius: 4px;
}
QWidget#dashboardRoot QFrame#focusQuickCard[cardRole="progress"] QPushButton#subtleButton {
    background-color: #202833;
    color: #F1F7FB;
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 9px;
}
QWidget#dashboardRoot QFrame#focusQuickCard[cardRole="progress"] QPushButton#subtleButton:hover {
    background-color: #293341;
    color: #FFFFFF;
    border-color: rgba(255, 255, 255, 0.32);
}

QWidget#dashboardRoot QFrame#dashboardOverviewCard,
QWidget#dashboardRoot QFrame#dashboardNotificationsPanel,
QWidget#dashboardRoot QFrame#planningPanel,
QWidget#dashboardRoot QFrame#studyNowPanel,
QWidget#dashboardRoot QFrame#priorityQueuePanel,
QWidget#dashboardRoot QFrame#dashboardCenterBar {
    background-color: #202833;
    border: 1px solid #445061;
    border-radius: 14px;
}
QWidget#dashboardRoot QFrame#dashboardQuickAccess {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1F2733, stop:0.5 #212A36, stop:1 #1E2531);
    border: 1px solid #475364;
    border-radius: 13px;
}
"""

ESTILO_BUSCA_GLOBAL_FUTURISTA = r"""
QWidget#dashboardRoot QPushButton#globalSearchTrigger {
    background-color: #212A35;
    color: #C2CAD4;
    border: 1px solid #48515F;
    border-radius: 10px;
    font-size: 8.8pt;
    font-weight: 700;
    text-align: left;
    padding: 6px 11px;
}
QWidget#dashboardRoot QPushButton#globalSearchTrigger:hover {
    background-color: #293342;
    color: #F3F7FB;
    border-color: #636E7D;
}
QDialog#globalSearchDialog {
    background-color: #0F1520;
}
QDialog#globalSearchDialog QLabel#globalSearchTitle {
    color: #F3F7FB;
    font-size: 16pt;
    font-weight: 900;
}
QDialog#globalSearchDialog QLabel#globalSearchSubtitle,
QDialog#globalSearchDialog QLabel#globalSearchStatus,
QDialog#globalSearchDialog QLabel#globalSearchHint {
    color: #AEB7C4;
    font-size: 8.7pt;
}
QDialog#globalSearchDialog QLabel#globalSearchShortcut {
    background-color: #232C38;
    color: #D3DBE5;
    border: 1px solid #5D6774;
    border-radius: 7px;
    padding: 4px 8px;
    font-size: 8pt;
    font-weight: 800;
}
QDialog#globalSearchDialog QLineEdit#globalSearchInput {
    min-height: 38px;
    background-color: #202833;
    color: #F3F7FB;
    border: 1px solid #4C5563;
    border-radius: 10px;
    padding: 0 12px;
    font-size: 10pt;
    selection-background-color: #555AF0;
}
QDialog#globalSearchDialog QLineEdit#globalSearchInput:focus {
    border: 1px solid #8086FF;
}
QDialog#globalSearchDialog QTableWidget#globalSearchResults {
    background-color: #1D2430;
    color: #DDE5EE;
    border: 1px solid #465162;
    border-radius: 10px;
    gridline-color: transparent;
    selection-background-color: #343C8A;
    selection-color: #F8FAFC;
}
QDialog#globalSearchDialog QTableWidget#globalSearchResults::item {
    border-bottom: 1px solid #2E3644;
    padding: 6px 8px;
}
QDialog#globalSearchDialog QHeaderView::section {
    background-color: #232C38;
    color: #C2CAD4;
    border: none;
    border-bottom: 1px solid #465162;
    padding: 7px 8px;
    font-size: 8pt;
    font-weight: 800;
}
"""

# ============================================================
# Dashboard — paleta harmônica do topo (tema claro)# ============================================================
# Dashboard — paleta harmônica do topo (tema claro)
# Alinha Foco, Algoritmo e Estudo por questões à linguagem
# cromática dos cards da seção "Visão geral": superfícies neutras,
# bordas suaves e cor concentrada em indicadores e ações.
# ============================================================
ESTILO_PALETA_HARMONICA_DASHBOARD_CLARO = r"""
QWidget#dashboardRoot QFrame#dashboardFocusPanel,
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"],
QWidget#dashboardRoot QFrame#studyNowPanel {
    background-color: #ffffff;
    border: 1px solid #d4dce7;
    border-radius: 14px;
}

/*
   Paleta semântica do Dashboard
   Azul claro / ciano = estrutura, foco e inteligência
   Verde               = treino, progresso e evolução
   Âmbar                = avaliação e atenção
*/

/* Foco — azul-petróleo/ciano, sem competir com o verde do treino */
QWidget#dashboardRoot QFrame#focusDashboardMainCard,
QWidget#dashboardRoot QFrame#focusQuickCard {
    background-color: #ffffff;
    border: 1px solid #dce4ed;
    border-radius: 11px;
}
QWidget#dashboardRoot QFrame#focusDashboardMainCard {
    border-color: #d1e5eb;
}
QWidget#dashboardRoot QFrame#focusQuickCard {
    border-color: #cfe6ec;
}
QWidget#dashboardRoot QLabel#focusDashboardIcon {
    color: #397f95;
    background-color: #f1f8fb;
    border: 1px solid #d2e7ed;
}
QWidget#dashboardRoot QLabel#focusDashboardCardIcon {
    color: #347f91;
    background-color: #f1fafb;
    border: 1px solid #cfe8ec;
}
QWidget#dashboardRoot QLabel#focusQuickIcon {
    color: #3295a7;
    background-color: #effafd;
    border: 1px solid #cde8ee;
}
QWidget#dashboardRoot QLabel#focusDashboardCardTitle,
QWidget#dashboardRoot QFrame#dashboardFocusPanel QPushButton#dashboardSectionToggle {
    color: #1d2737;
}
QWidget#dashboardRoot QLabel#focusDashboardSubtitle,
QWidget#dashboardRoot QLabel#focusDashboardDescription,
QWidget#dashboardRoot QLabel#focusDashboardDetail,
QWidget#dashboardRoot QLabel#focusQuickHint,
QWidget#dashboardRoot QLabel#focusDashboardCaption {
    color: #7c899b;
}
QWidget#dashboardRoot QLabel#focusDashboardMetricText {
    color: #66778c;
}
QWidget#dashboardRoot QLabel#focusDashboardMetricText[metricKind="time"] {
    color: #347f91;
}
QWidget#dashboardRoot QLabel#focusDashboardMetricText[metricKind="sessions"] {
    color: #3d7f9c;
}
QWidget#dashboardRoot QLabel#focusDashboardMetricText[metricKind="goal"] {
    color: #8a95a5;
}
QWidget#dashboardRoot QLabel#focusDashboardBadge {
    color: #34798a;
    background-color: #f1fafb;
    border: 1px solid #cfe8ec;
}
QWidget#dashboardRoot QFrame#focusDashboardMainCard QLabel#dashboardTodayFocusValue {
    color: #2f788b;
}
QWidget#dashboardRoot QLabel#focusQuickEyebrow {
    color: #5d7388;
}
QWidget#dashboardRoot QFrame#focusDashboardMainCard QPushButton#dashboardFocusPrimaryButton {
    background-color: #3d8193;
    color: #ffffff;
    border: 1px solid #367587;
    border-radius: 9px;
}
QWidget#dashboardRoot QFrame#focusDashboardMainCard QPushButton#dashboardFocusPrimaryButton:hover {
    background-color: #357589;
    border-color: #306a7c;
}
QWidget#dashboardRoot QFrame#focusDashboardMainCard QPushButton#dashboardFocusPrimaryButton:pressed {
    background-color: #306a7c;
    border-color: #2b6070;
}
QWidget#dashboardRoot QPushButton#focusQuickPresetButton {
    background-color: #fbfcfe;
    color: #52677c;
    border: 1px solid #d7e0e9;
}
QWidget#dashboardRoot QPushButton#focusQuickPresetButton:hover {
    background-color: #f0f9fb;
    border-color: #b9dce4;
    color: #2d8192;
}
QWidget#dashboardRoot QPushButton#focusQuickPresetButton:checked {
    background-color: #eaf8fb;
    color: #277d8f;
    border: 1px solid #83c5d1;
}
QWidget#dashboardRoot QPushButton#focusQuickStartButton {
    background-color: #3aa2b2;
    color: #ffffff;
    border: 1px solid #3394a4;
    border-radius: 9px;
}
QWidget#dashboardRoot QPushButton#focusQuickStartButton:hover {
    background-color: #3293a3;
    border-color: #2e8796;
}
QWidget#dashboardRoot QPushButton#focusQuickStartButton:pressed {
    background-color: #2e8796;
    border-color: #297987;
}
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] {
    background-color: #f8fafc;
    border: 1px solid #e0e6ee;
}

/* Algoritmo — azul Vighna mais leve, ainda é o CTA principal */
QWidget#dashboardRoot QLabel#algorithmDashboardIcon {
    background-color: #f1f6fc;
    color: #477fae;
    border: 1px solid #d4e3f0;
}
QWidget#dashboardRoot QLabel#algorithmDashboardTitle {
    color: #1d2737;
}
QWidget#dashboardRoot QLabel#algorithmDashboardSubtitle {
    color: #7c899b;
}
QWidget#dashboardRoot QLabel#algorithmDashboardReady {
    color: #477fae;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayPrimaryButton {
    background-color: #4b83c9;
    color: #ffffff;
    border: 1px solid #4277b8;
    border-radius: 11px;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayPrimaryButton:hover {
    background-color: #4278ba;
    border-color: #3b6da9;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayPrimaryButton:pressed {
    background-color: #3b6da9;
    border-color: #35629a;
}
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"] QPushButton#dashboardTodayButton {
    color: #557fa9;
}

/* Estudo por questões — azul suave, verde e âmbar */
QWidget#dashboardRoot QFrame#studyActionCard,
QWidget#dashboardRoot QFrame#strategyCompactCard {
    background-color: #ffffff;
    border: 1px solid #dce4ed;
    border-radius: 11px;
}
QWidget#dashboardRoot QFrame#studyActionCard[actionRole="review"] {
    border-color: #d2e2ef;
}
QWidget#dashboardRoot QFrame#strategyCompactCard[actionRole="adaptive"] {
    background-color: #ffffff;
    border-color: #d4e7dd;
}
QWidget#dashboardRoot QFrame#strategyCompactCard[actionRole="simulation"] {
    background-color: #ffffff;
    border-color: #ecdcb9;
}
QWidget#dashboardRoot QLabel#studyNowIcon {
    color: #527da3;
    background-color: #f2f7fb;
    border: 1px solid #d6e3ec;
}
QWidget#dashboardRoot QLabel#studyCardIcon {
    color: #4d789d;
    background-color: #f2f7fb;
    border: 1px solid #d4e3ee;
}
QWidget#dashboardRoot QLabel#strategyCardIcon {
    color: #4b8965;
    background-color: #f2faf5;
    border: 1px solid #d5eadc;
}
QWidget#dashboardRoot QFrame#strategyCompactCard[actionRole="simulation"] QLabel#strategyCardIcon {
    color: #a47622;
    background-color: #fff9ed;
    border-color: #eeddb8;
}
QWidget#dashboardRoot QLabel#studyActionTitle,
QWidget#dashboardRoot QLabel#strategyCardTitle,
QWidget#dashboardRoot QLabel#studyReviewDetail {
    color: #1d2737;
}
QWidget#dashboardRoot QLabel#studyActionDescription,
QWidget#dashboardRoot QLabel#strategyCardDescription,
QWidget#dashboardRoot QLabel#studyReviewFooter,
QWidget#dashboardRoot QLabel#studyReviewCount {
    color: #7c899b;
}
QWidget#dashboardRoot QLabel#studyAdaptiveCriteria {
    color: #4b8965;
}
QWidget#dashboardRoot QPushButton#adaptiveDashboardButton {
    background-color: #4f8e69;
    color: #ffffff;
    border: 1px solid #467f5e;
}
QWidget#dashboardRoot QPushButton#adaptiveDashboardButton:hover {
    background-color: #467f5e;
    border-color: #3f7355;
}
QWidget#dashboardRoot QPushButton#mockExamDashboardButton {
    background-color: #d09a34;
    color: #ffffff;
    border: 1px solid #be8b2d;
}
QWidget#dashboardRoot QPushButton#mockExamDashboardButton:hover {
    background-color: #be8b2d;
    border-color: #ad7e28;
}
QWidget#dashboardRoot QFrame#assessmentStat {
    background-color: #f8fafc;
    border: 1px solid #e0e6ee;
}
QWidget#dashboardRoot QLabel#assessmentStatValue {
    color: #477fae;
}
QWidget#dashboardRoot QFrame#studyManualFooter {
    background-color: #f8fafc;
    border: 1px solid #e0e6ee;
}
"""


# Camada final do Dashboard claro. Ela é deliberadamente curta e específica:
# redefine somente os componentes principais do Dashboard e deixa as demais
# telas e os temas Escuro/Futurista intactos.
ESTILO_DESIGN_SYSTEM_DASHBOARD_CLARO = r"""
/* ============================================================
   VIGHNA DESIGN SYSTEM — DASHBOARD CLARO
   ============================================================ */

QWidget#dashboardPage,
QScrollArea#dashboardScroll,
QWidget#dashboardRoot {
    background-color: %(fundo)s;
}

QWidget#dashboardRoot QFrame#dashboardTopBar,
QWidget#dashboardRoot QFrame#dashboardFocusPanel,
QWidget#dashboardRoot QFrame#dashboardTodayAction[simpleHero="true"],
QWidget#dashboardRoot QFrame#studyNowPanel,
QWidget#dashboardRoot QFrame#dashboardOverviewCard,
QWidget#dashboardRoot QFrame#dashboardNotificationsPanel,
QWidget#dashboardRoot QFrame#planningPanel,
QWidget#dashboardRoot QFrame#dashboardProjectionPanel {
    background-color: %(superficie)s;
    border: 1px solid %(borda)s;
}

QWidget#dashboardRoot QFrame#focusDashboardMainCard,
QWidget#dashboardRoot QFrame#focusQuickCard {
    background-color: %(superficie)s;
    border: 1px solid %(borda)s;
    border-radius: 8px;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] {
    background-color: %(superficie)s;
    border: 1px solid %(borda)s;
    border-radius: 8px;
}

QWidget#dashboardRoot QLabel#focusDashboardCardTitle,
QWidget#dashboardRoot QLabel#algorithmDashboardTitle,
QWidget#dashboardRoot QLabel#dashboardQuickAccessTitle,
QWidget#dashboardRoot QPushButton#dashboardSectionToggle {
    color: %(texto)s;
}

QWidget#dashboardRoot QLabel#focusDashboardDescription,
QWidget#dashboardRoot QLabel#focusDashboardCaption,
QWidget#dashboardRoot QLabel#focusDashboardDetail,
QWidget#dashboardRoot QLabel#focusQuickHint,
QWidget#dashboardRoot QLabel#algorithmDashboardSubtitle,
QWidget#dashboardRoot QLabel#dashboardActionSectionSubtitle {
    color: %(texto_suave)s;
}

QWidget#dashboardRoot QLabel#dashboardTodayFocusValue,
QWidget#dashboardRoot QLabel#algorithmDashboardReady {
    color: %(texto)s;
}

QWidget#dashboardRoot QLabel#dashboardProgressBadge {
    background-color: %(primaria)s;
    color: #FFFFFF;
    border: none;
    border-radius: 21px;
    font-size: 16px;
    font-weight: 800;
}

QWidget#dashboardRoot QProgressBar#dashboardTodayProgress {
    background-color: %(trilho)s;
    border: none;
    border-radius: 4px;
}

QWidget#dashboardRoot QProgressBar#dashboardTodayProgress::chunk {
    background-color: %(primaria)s;
    border-radius: 4px;
}

/* Ações realmente primárias do Dashboard. */
QWidget#dashboardRoot QPushButton#dashboardFocusPrimaryButton,
QWidget#dashboardRoot QPushButton#dashboardTodayPrimaryButton {
    background-color: %(primaria)s;
    color: #FFFFFF;
    border: 1px solid %(primaria)s;
    border-radius: 6px;
    font-weight: 800;
}

QWidget#dashboardRoot QPushButton#dashboardFocusPrimaryButton:hover,
QWidget#dashboardRoot QPushButton#dashboardTodayPrimaryButton:hover {
    background-color: %(primaria_hover)s;
    border-color: %(primaria_hover)s;
}

QWidget#dashboardRoot QPushButton#dashboardFocusPrimaryButton:pressed,
QWidget#dashboardRoot QPushButton#dashboardTodayPrimaryButton:pressed {
    background-color: %(primaria_pressed)s;
    border-color: %(primaria_pressed)s;
}

/* Navegação e ações secundárias permanecem vazadas. */
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#toolbarButton,
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#pauseNavButton,
QWidget#dashboardRoot QPushButton#subtleButton,
QWidget#dashboardRoot QPushButton#dashboardTodayButton,
QWidget#dashboardRoot QPushButton#questionsNavButton {
    background-color: %(superficie)s;
    color: %(texto_secundario)s;
    border: 1px solid %(borda_controle_forte)s;
    border-radius: 6px;
    font-weight: 600;
}

QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#toolbarButton:hover,
QWidget#dashboardRoot QFrame#dashboardQuickAccess[embedded="true"] QPushButton#pauseNavButton:hover,
QWidget#dashboardRoot QPushButton#subtleButton:hover,
QWidget#dashboardRoot QPushButton#dashboardTodayButton:hover,
QWidget#dashboardRoot QPushButton#questionsNavButton:hover {
    background-color: %(hover_claro)s;
    color: %(texto)s;
    border-color: %(borda_controle_forte)s;
}

/* Configurações: somente o ícone sobre o fundo do próprio Dashboard. */
QWidget#dashboardRoot QPushButton#topAccentButton {
    background: transparent;
    border: none;
    border-radius: 6px;
    padding: 0px;
}

QWidget#dashboardRoot QPushButton#topAccentButton:hover {
    background-color: %(hover_claro)s;
}

QWidget#dashboardRoot QFrame#topProfileBar {
    background-color: %(superficie)s;
    border: 1px solid %(borda_controle)s;
}
""" % PALETA_DASHBOARD_CLARO



# ============================================================
# Resolvedor de questões — modo concentração
# Mantém a linguagem dos cards do Dashboard, mas reduz ornamentos no
# conteúdo pedagógico. A variante futurista sobrescreve esta base ao final.
# ============================================================
ESTILO_RESOLVEDOR_CLARO = r"""
QDialog#questionSolverDialog {
    background-color: #F5F7FA;
}
QDialog#questionSolverDialog QLabel#pageTitle {
    color: #172033;
    font-size: 19px;
    font-weight: 900;
}
QDialog#questionSolverDialog QLabel#pageSubtitle {
    color: #718096;
    font-size: 8.6pt;
}
QDialog#questionSolverDialog QFrame#questionSessionOverviewCard {
    background-color: #FFFFFF;
    border: 1px solid #DDE4EC;
    border-radius: 14px;
}
QDialog#questionSolverDialog QLabel#questionSessionEyebrow {
    color: #7B8797;
    font-size: 7.6pt;
    font-weight: 850;
    letter-spacing: 0.8px;
}
QDialog#questionSolverDialog QLabel#questionSessionProgressText {
    color: #202B3C;
    font-size: 9pt;
    font-weight: 850;
}
QDialog#questionSolverDialog QLabel#questionSessionCycleText {
    color: #657286;
    font-size: 8.5pt;
    font-weight: 700;
}
QDialog#questionSolverDialog QProgressBar#questionSessionProgress {
    background-color: #E8EDF3;
    border: none;
    border-radius: 4px;
}
QDialog#questionSolverDialog QProgressBar#questionSessionProgress::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4F5FE8, stop:1 #6B86F2);
    border-radius: 4px;
}
QDialog#questionSolverDialog QFrame#questionSessionMiniStat {
    background-color: #F7F9FC;
    border: 1px solid #E3E8EF;
    border-radius: 9px;
}
QDialog#questionSolverDialog QLabel#questionSessionMiniLabel {
    color: #7A8798;
    font-size: 8pt;
    font-weight: 700;
}
QDialog#questionSolverDialog QLabel#questionSessionMiniValue {
    color: #1F2937;
    font-size: 9.5pt;
    font-weight: 900;
}
QDialog#questionSolverDialog QLabel#questionSessionMiniValue[metricRole="success"] { color: #17815D; }
QDialog#questionSolverDialog QLabel#questionSessionMiniValue[metricRole="danger"] { color: #C44758; }
QDialog#questionSolverDialog QLabel#questionSessionMiniValue[metricRole="warning"] { color: #B16A18; }
QDialog#questionSolverDialog QFrame#questionSessionFocusBar {
    background-color: #F7F9FC;
    border: 1px solid #E1E6ED;
    border-radius: 10px;
}
QDialog#questionSolverDialog QLabel#questionSessionFocusState {
    color: #536173;
    font-size: 8.3pt;
    font-weight: 800;
}
QDialog#questionSolverDialog QLabel#questionSolverDiscipline {
    color: #5866C8;
    font-size: 7.8pt;
    font-weight: 900;
    letter-spacing: 0.8px;
}
QDialog#questionSolverDialog QLabel#questionSolverMeta {
    color: #5D697A;
    font-size: 8.7pt;
    font-weight: 700;
}
QDialog#questionSolverDialog QFrame#questionSolverStatementCard {
    background-color: #FFFFFF;
    border: 1px solid #DCE3EB;
    border-radius: 12px;
}
QDialog#questionSolverDialog QLabel#questionSolverQuestionIndex {
    color: #606BC9;
    font-size: 7.8pt;
    font-weight: 900;
    letter-spacing: 0.8px;
}
QDialog#questionSolverDialog QLabel#questionSolverStatement {
    color: #172033;
    font-size: 10.8pt;
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative {
    background-color: {{color:answer.normal_surface}};
    border: 1px solid {{color:answer.normal_border}};
    border-radius: 10px;
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative[answerState="normal"]:hover {
    background-color: {{color:answer.hover_surface}};
    border-color: {{color:answer.hover_border}};
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative[selectionState="selected"][answerState="normal"] {
    background-color: {{color:answer.selected_surface}};
    border: 1px solid {{color:answer.selected_border}};
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative[answerState="correta"] {
    background-color: {{color:answer.correct_surface}};
    border-color: {{color:answer.correct_border}};
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative[answerState="errada"] {
    background-color: {{color:answer.incorrect_surface}};
    border-color: {{color:answer.incorrect_border}};
}
QDialog#questionSolverDialog QRadioButton#questionSolverRadio::indicator {
    width: 17px;
    height: 17px;
    border: 2px solid {{color:answer.indicator_border}};
    border-radius: 9px;
    background-color: {{color:answer.indicator_surface}};
}
QDialog#questionSolverDialog QRadioButton#questionSolverRadio::indicator:hover {
    border-color: {{color:answer.indicator_hover_border}};
}
QDialog#questionSolverDialog QRadioButton#questionSolverRadio::indicator:checked {
    background-color: {{color:answer.checked_indicator}};
    border-color: {{color:answer.indicator_checked_border}};
}
QDialog#questionSolverDialog QFrame#questionSessionActionPanel {
    background-color: #FFFFFF;
    border: 1px solid #DDE4EC;
    border-radius: 13px;
}
QDialog#questionSolverDialog QPushButton#questionSessionSkipButton {
    background-color: #F5F7FA;
    color: #4F5D6E;
    border: 1px solid #CCD5DF;
    border-radius: 9px;
    font-weight: 750;
}
QDialog#questionSolverDialog QPushButton#questionSessionSkipButton:hover {
    background-color: #EDF1F5;
    border-color: #AFBAC8;
}
QDialog#questionSolverDialog QPushButton#primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4B50DF, stop:1 #586DE3);
    color: #FFFFFF;
    border: 1px solid #7885F0;
    border-radius: 9px;
    font-weight: 850;
}
QDialog#questionSolverDialog QPushButton#primaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #595EE8, stop:1 #6579EC);
    border-color: #98A2F7;
}
QDialog#questionSolverDialog QPushButton#questionSessionEndButton {
    background-color: #FFF7F8;
    color: #A54050;
    border: 1px solid #E9BCC4;
    border-radius: 9px;
    font-weight: 750;
}
QDialog#questionSolverDialog QPushButton#questionSessionEndButton:hover {
    background-color: #FFF0F2;
    border-color: #DC929E;
}
"""

ESTILO_RESOLVEDOR_ESCURO = r"""
QDialog#questionSolverDialog {
    background-color: #101722;
}
QDialog#questionSolverDialog QLabel#pageTitle {
    color: #F3F6FA;
    font-size: 19px;
    font-weight: 900;
}
QDialog#questionSolverDialog QLabel#pageSubtitle {
    color: #96A3B3;
    font-size: 8.6pt;
}
QDialog#questionSolverDialog QFrame#questionSessionOverviewCard {
    background-color: #182230;
    border: 1px solid #344154;
    border-radius: 14px;
}
QDialog#questionSolverDialog QLabel#questionSessionEyebrow {
    color: #8392A5;
    font-size: 7.6pt;
    font-weight: 850;
    letter-spacing: 0.8px;
}
QDialog#questionSolverDialog QLabel#questionSessionProgressText {
    color: #EDF2F7;
    font-size: 9pt;
    font-weight: 850;
}
QDialog#questionSolverDialog QLabel#questionSessionCycleText {
    color: #A1ADBB;
    font-size: 8.5pt;
    font-weight: 700;
}
QDialog#questionSolverDialog QProgressBar#questionSessionProgress {
    background-color: #2C3745;
    border: none;
    border-radius: 4px;
}
QDialog#questionSolverDialog QProgressBar#questionSessionProgress::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5964E8, stop:1 #6E8BEF);
    border-radius: 4px;
}
QDialog#questionSolverDialog QFrame#questionSessionMiniStat {
    background-color: #141D29;
    border: 1px solid #2D3949;
    border-radius: 9px;
}
QDialog#questionSolverDialog QLabel#questionSessionMiniLabel {
    color: #8D9BAD;
    font-size: 8pt;
    font-weight: 700;
}
QDialog#questionSolverDialog QLabel#questionSessionMiniValue {
    color: #F2F5F8;
    font-size: 9.5pt;
    font-weight: 900;
}
QDialog#questionSolverDialog QLabel#questionSessionMiniValue[metricRole="success"] { color: #79D6AA; }
QDialog#questionSolverDialog QLabel#questionSessionMiniValue[metricRole="danger"] { color: #F08A98; }
QDialog#questionSolverDialog QLabel#questionSessionMiniValue[metricRole="warning"] { color: #E5B16B; }
QDialog#questionSolverDialog QFrame#questionSessionFocusBar {
    background-color: #151E2A;
    border: 1px solid #303D4E;
    border-radius: 10px;
}
QDialog#questionSolverDialog QLabel#questionSessionFocusState {
    color: #A7B4C3;
    font-size: 8.3pt;
    font-weight: 800;
}
QDialog#questionSolverDialog QLabel#questionSolverDiscipline {
    color: #96A0FF;
    font-size: 7.8pt;
    font-weight: 900;
    letter-spacing: 0.8px;
}
QDialog#questionSolverDialog QLabel#questionSolverMeta {
    color: #A8B4C2;
    font-size: 8.7pt;
    font-weight: 700;
}
QDialog#questionSolverDialog QFrame#questionSolverStatementCard {
    background-color: #182230;
    border: 1px solid #344154;
    border-radius: 12px;
}
QDialog#questionSolverDialog QLabel#questionSolverQuestionIndex {
    color: #9BA4FF;
    font-size: 7.8pt;
    font-weight: 900;
    letter-spacing: 0.8px;
}
QDialog#questionSolverDialog QLabel#questionSolverStatement {
    color: #F2F6FA;
    font-size: 10.8pt;
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative {
    background-color: {{color:answer.normal_surface}};
    border: 1px solid {{color:answer.normal_border}};
    border-radius: 10px;
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative[answerState="normal"]:hover {
    background-color: {{color:answer.hover_surface}};
    border-color: {{color:answer.hover_border}};
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative[selectionState="selected"][answerState="normal"] {
    background-color: {{color:answer.selected_surface}};
    border: 1px solid {{color:answer.selected_border}};
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative[answerState="correta"] {
    background-color: {{color:answer.correct_surface}};
    border-color: {{color:answer.correct_border}};
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative[answerState="errada"] {
    background-color: {{color:answer.incorrect_surface}};
    border-color: {{color:answer.incorrect_border}};
}
QDialog#questionSolverDialog QRadioButton#questionSolverRadio::indicator {
    width: 17px;
    height: 17px;
    border: 2px solid {{color:answer.indicator_border}};
    border-radius: 9px;
    background-color: {{color:answer.indicator_surface}};
}
QDialog#questionSolverDialog QRadioButton#questionSolverRadio::indicator:hover {
    border-color: {{color:answer.indicator_hover_border}};
}
QDialog#questionSolverDialog QRadioButton#questionSolverRadio::indicator:checked {
    background-color: {{color:answer.checked_indicator}};
    border-color: {{color:answer.indicator_checked_border}};
}
QDialog#questionSolverDialog QFrame#questionSessionActionPanel {
    background-color: #182230;
    border: 1px solid #344154;
    border-radius: 13px;
}
QDialog#questionSolverDialog QPushButton#questionSessionSkipButton {
    background-color: #202B39;
    color: #C8D1DC;
    border: 1px solid #445265;
    border-radius: 9px;
    font-weight: 750;
}
QDialog#questionSolverDialog QPushButton#questionSessionSkipButton:hover {
    background-color: #273444;
    border-color: #607086;
}
QDialog#questionSolverDialog QPushButton#primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4B50DF, stop:1 #586DE3);
    color: #FFFFFF;
    border: 1px solid #7885F0;
    border-radius: 9px;
    font-weight: 850;
}
QDialog#questionSolverDialog QPushButton#primaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #595EE8, stop:1 #6579EC);
    border-color: #A2AAFF;
}
QDialog#questionSolverDialog QPushButton#questionSessionEndButton {
    background-color: #2B2027;
    color: #FFB8C2;
    border: 1px solid #724350;
    border-radius: 9px;
    font-weight: 750;
}
QDialog#questionSolverDialog QPushButton#questionSessionEndButton:hover {
    background-color: #38262D;
    border-color: #985766;
}
"""

ESTILO_RESOLVEDOR_FUTURISTA = r"""
/* Resolver — mesma família visual do Dashboard Neo, com menor ruído. */
QDialog#questionSolverDialog {
    background-color: #0B111D;
}
QDialog#questionSolverDialog QLabel#pageTitle {
    color: #F5F7FB;
    font-size: 20px;
    font-weight: 900;
}
QDialog#questionSolverDialog QLabel#pageSubtitle {
    color: #AAB5C2;
    font-size: 8.6pt;
}
QDialog#questionSolverDialog QFrame#questionSessionOverviewCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #202733, stop:0.55 #222A36, stop:1 #1D2430);
    border: 1px solid #475364;
    border-radius: 15px;
}
QDialog#questionSolverDialog QLabel#questionSessionEyebrow {
    color: #AAB4C0;
    font-size: 7.5pt;
    font-weight: 900;
    letter-spacing: 0.9px;
}
QDialog#questionSolverDialog QLabel#questionSessionProgressText {
    color: #F5F7FB;
    font-size: 9.1pt;
    font-weight: 900;
}
QDialog#questionSolverDialog QLabel#questionSessionCycleText {
    color: #B8C1CD;
    font-size: 8.4pt;
    font-weight: 700;
}
QDialog#questionSolverDialog QProgressBar#questionSessionProgress {
    background-color: #3B424F;
    border: none;
    border-radius: 4px;
}
QDialog#questionSolverDialog QProgressBar#questionSessionProgress::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5358EA, stop:0.52 #5B64EE, stop:1 #718BF5);
    border-radius: 4px;
}
QDialog#questionSolverDialog QFrame#questionSessionMiniStat {
    background-color: #171F2B;
    border: 1px solid #344050;
    border-radius: 10px;
}
QDialog#questionSolverDialog QLabel#questionSessionMiniLabel {
    color: #98A5B4;
    font-size: 7.9pt;
    font-weight: 700;
}
QDialog#questionSolverDialog QLabel#questionSessionMiniValue {
    color: #F8FAFC;
    font-size: 9.5pt;
    font-weight: 900;
}
QDialog#questionSolverDialog QLabel#questionSessionMiniValue[metricRole="success"] { color: #82DBB4; }
QDialog#questionSolverDialog QLabel#questionSessionMiniValue[metricRole="danger"] { color: #F28B99; }
QDialog#questionSolverDialog QLabel#questionSessionMiniValue[metricRole="warning"] { color: #E9B66E; }
QDialog#questionSolverDialog QFrame#questionSessionFocusBar {
    background-color: #151D28;
    border: 1px solid #354151;
    border-radius: 11px;
}
QDialog#questionSolverDialog QLabel#questionSessionFocusState {
    color: #B1BCC9;
    font-size: 8.2pt;
    font-weight: 800;
}
QDialog#questionSolverDialog QFrame#questionSessionFocusBar QPushButton#subtleButton,
QDialog#questionSolverDialog QPushButton#subtleButton {
    background-color: #232B36;
    color: #D1D9E2;
    border: 1px solid #5A6472;
    border-radius: 9px;
    font-weight: 750;
}
QDialog#questionSolverDialog QFrame#questionSessionFocusBar QPushButton#subtleButton:hover,
QDialog#questionSolverDialog QPushButton#subtleButton:hover {
    background-color: #2C3643;
    color: #FFFFFF;
    border-color: #7A8594;
}
QDialog#questionSolverDialog QLabel#questionSolverDiscipline {
    color: #969FFF;
    font-size: 7.7pt;
    font-weight: 900;
    letter-spacing: 0.9px;
}
QDialog#questionSolverDialog QLabel#questionSolverMeta {
    color: #B6C0CB;
    font-size: 8.8pt;
    font-weight: 700;
}
QDialog#questionSolverDialog QFrame#questionSolverStatementCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #171F2B, stop:1 #141C27);
    border: 1px solid #3C4858;
    border-radius: 13px;
}
QDialog#questionSolverDialog QLabel#questionSolverQuestionIndex {
    color: #9BA4FF;
    font-size: 7.7pt;
    font-weight: 900;
    letter-spacing: 0.9px;
}
QDialog#questionSolverDialog QLabel#questionSolverStatement {
    color: #F2F6FA;
    font-size: 10.9pt;
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative {
    background-color: {{color:answer.normal_surface}};
    border: 1px solid {{color:answer.normal_border}};
    border-radius: 11px;
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative[answerState="normal"]:hover {
    background-color: {{color:answer.hover_surface}};
    border-color: {{color:answer.hover_border}};
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative[selectionState="selected"][answerState="normal"] {
    background: {{gradient:answer.selected_gradient}};
    border: 1px solid {{color:answer.selected_border}};
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative[answerState="correta"] {
    background: {{gradient:answer.correct_gradient}};
    border-color: {{color:answer.correct_border}};
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative[answerState="errada"] {
    background: {{gradient:answer.incorrect_gradient}};
    border-color: {{color:answer.incorrect_border}};
}
QDialog#questionSolverDialog QRadioButton#questionSolverRadio {
    color: {{color:answer.indicator_text}};
    font-weight: 900;
    spacing: 7px;
}
QDialog#questionSolverDialog QRadioButton#questionSolverRadio::indicator {
    width: 17px;
    height: 17px;
    border: 2px solid {{color:answer.indicator_border}};
    border-radius: 9px;
    background-color: {{color:answer.indicator_surface}};
}
QDialog#questionSolverDialog QRadioButton#questionSolverRadio::indicator:hover {
    border-color: {{color:answer.indicator_hover_border}};
}
QDialog#questionSolverDialog QRadioButton#questionSolverRadio::indicator:checked {
    background-color: {{color:answer.checked_indicator}};
    border-color: {{color:answer.indicator_checked_border}};
}
QDialog#questionSolverDialog QLabel#questionSolverAlternativeText {
    color: {{color:answer.normal_text}};
    font-size: 9.8pt;
}
QDialog#questionSolverDialog QToolButton#questionSolverEliminateButton {
    color: {{color:answer.eliminate_text}};
    border: none;
    background: transparent;
}
QDialog#questionSolverDialog QToolButton#questionSolverEliminateButton:hover {
    background-color: {{color:answer.eliminate_hover_surface}};
    color: {{color:answer.eliminate_hover_text}};
    border-radius: 6px;
}
QDialog#questionSolverDialog QFrame#questionSessionActionPanel {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #171F2B, stop:1 #151D28);
    border: 1px solid #3A4656;
    border-radius: 13px;
}
QDialog#questionSolverDialog QCheckBox#questionSessionDoubt,
QDialog#questionSolverDialog QCheckBox#questionSessionAnalysisFlag {
    color: #B7C1CD;
    background: transparent;
    font-size: 8.6pt;
}
QDialog#questionSolverDialog QCheckBox#questionSessionDoubt:checked { color: #AEB5FF; }
QDialog#questionSolverDialog QCheckBox#questionSessionAnalysisFlag:checked { color: #F0C47C; }
QDialog#questionSolverDialog QPushButton#questionSessionSkipButton {
    background-color: #202833;
    color: #CED6E0;
    border: 1px solid #505B69;
    border-radius: 10px;
    font-weight: 800;
}
QDialog#questionSolverDialog QPushButton#questionSessionSkipButton:hover {
    background-color: #293341;
    color: #FFFFFF;
    border-color: #707C8B;
}
QDialog#questionSolverDialog QPushButton#primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4447E8, stop:0.52 #4347E1, stop:1 #3C42D2);
    color: #FFFFFF;
    border: 1px solid #7C83FF;
    border-radius: 10px;
    font-size: 9.2pt;
    font-weight: 900;
}
QDialog#questionSolverDialog QPushButton#primaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5355F2, stop:0.52 #4F54EB, stop:1 #464DDE);
    border-color: #B1B7FF;
}
QDialog#questionSolverDialog QPushButton#questionSessionEndButton {
    background-color: #2A2026;
    color: #FFBAC4;
    border: 1px solid #70434F;
    border-radius: 10px;
    font-weight: 800;
}
QDialog#questionSolverDialog QPushButton#questionSessionEndButton:hover {
    background-color: #38262E;
    border-color: #9A5968;
    color: #FFD5DB;
}
QDialog#questionSolverDialog QFrame#questionSolverFeedback {
    background-color: {{color:answer.explanation_surface}};
    border: 1px solid {{color:answer.explanation_border}};
    border-radius: 11px;
}
"""


ESTILO_TOPICO_DETALHES_CLARO = r"""
QDialog#topicDetailsDialog {
    background-color: #F5F7FA;
}
QDialog#topicDetailsDialog QFrame#topicHeroCard,
QDialog#topicDetailsDialog QFrame#topicEvolutionCard,
QDialog#topicDetailsDialog QFrame#topicHistoryCard,
QDialog#topicDetailsDialog QFrame#topicHistoryDetailsCard {
    background-color: #FFFFFF;
    border: 1px solid #DCE4ED;
    border-radius: 13px;
}
QDialog#topicDetailsDialog QLabel#topicBreadcrumb {
    color: #5C7FA2;
    font-size: 8.5pt;
    font-weight: 700;
}
QDialog#topicDetailsDialog QLabel#topicHeroTitle {
    color: #17263A;
    font-size: 18pt;
    font-weight: 900;
}
QDialog#topicDetailsDialog QLabel#topicHeroSubtitle {
    color: #728094;
    font-size: 9pt;
}
QDialog#topicDetailsDialog QPushButton#topicStudyButton {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #356FD0,stop:1 #4D7FE0);
    color: #FFFFFF;
    border: 1px solid #5D8DE2;
    border-radius: 10px;
    font-weight: 900;
    padding: 7px 16px;
}
QDialog#topicDetailsDialog QPushButton#topicStudyButton:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #2E63BC,stop:1 #416FD0);
    border-color: #7EA6EA;
}
QDialog#topicDetailsDialog QPushButton#topicQuestionsButton,
QDialog#topicDetailsDialog QPushButton#topicHistoryButton,
QDialog#topicDetailsDialog QPushButton#topicNextSecondaryButton,
QDialog#topicDetailsDialog QPushButton#topicNextGhostButton {
    background-color: #FFFFFF;
    color: #37658F;
    border: 1px solid #C8D8E8;
    border-radius: 9px;
    font-weight: 700;
    padding: 6px 12px;
}
QDialog#topicDetailsDialog QPushButton#topicQuestionsButton:hover,
QDialog#topicDetailsDialog QPushButton#topicHistoryButton:hover,
QDialog#topicDetailsDialog QPushButton#topicNextSecondaryButton:hover,
QDialog#topicDetailsDialog QPushButton#topicNextGhostButton:hover {
    background-color: #F1F7FD;
    border-color: #90B6DA;
    color: #245782;
}
QDialog#topicDetailsDialog QFrame#topicMetricCard {
    background-color: #F8FAFD;
    border: 1px solid #DCE5EF;
    border-radius: 10px;
}
QDialog#topicDetailsDialog QFrame#topicMetricCard[metricRole="domain"] {
    background-color: #F1F7FF;
    border-color: #C7DAF2;
}
QDialog#topicDetailsDialog QLabel#topicMetricLabel,
QDialog#topicDetailsDialog QLabel#topicCompactMetricLabel {
    color: #748398;
    font-size: 8.2pt;
    font-weight: 700;
}
QDialog#topicDetailsDialog QLabel#topicMetricValue {
    color: #17263A;
    font-size: 13pt;
    font-weight: 900;
}
QDialog#topicDetailsDialog QFrame#topicMetricCard[metricRole="domain"] QLabel#topicMetricValue {
    color: #2D65B5;
}
QDialog#topicDetailsDialog QFrame#topicCompactMetric {
    background-color: #F8FAFC;
    border: 1px solid #E1E7EF;
    border-radius: 8px;
}
QDialog#topicDetailsDialog QLabel#topicCompactMetricValue {
    color: #334A62;
    font-size: 8.7pt;
    font-weight: 900;
}
QDialog#topicDetailsDialog QLabel#topicLegacyNotice {
    color: #8A641B;
    background-color: #FFF9EA;
    border: 1px solid #EAD9AA;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 8.2pt;
}
QDialog#topicDetailsDialog QTabWidget#topicDetailsTabs::pane {
    border: 0;
    background: transparent;
}
QDialog#topicDetailsDialog QTabWidget#topicDetailsTabs QTabBar::tab {
    background: transparent;
    color: #708197;
    border: 0;
    border-bottom: 2px solid transparent;
    padding: 8px 15px;
    font-weight: 700;
}
QDialog#topicDetailsDialog QTabWidget#topicDetailsTabs QTabBar::tab:selected {
    color: #286AA3;
    border-bottom-color: #3A8FD0;
}
QDialog#topicDetailsDialog QFrame#topicDomainCardModern {
    background-color: #F8FBFF;
    border: 1px solid #CFE0F2;
    border-radius: 13px;
}
QDialog#topicDetailsDialog QLabel#topicDomainTitleModern,
QDialog#topicDetailsDialog QLabel#topicSectionTitle {
    color: #1B2B3E;
    font-size: 10.5pt;
    font-weight: 900;
}
QDialog#topicDetailsDialog QLabel#topicDomainSubtitleModern,
QDialog#topicDetailsDialog QLabel#topicEvolutionSummary,
QDialog#topicDetailsDialog QLabel#topicHistoryHint {
    color: #728094;
    font-size: 8.4pt;
}
QDialog#topicDetailsDialog QLabel#topicDomainScoreModern {
    color: #2D65B5;
    font-size: 18px;
    font-weight: 900;
}
QDialog#topicDetailsDialog QLabel#topicDomainLevelModern {
    background-color: #E8EEF5;
    color: #52657A;
    border-radius: 8px;
    padding: 4px 8px;
    font-size: 8.2pt;
    font-weight: 900;
}
QDialog#topicDetailsDialog QLabel#topicDomainLevelModern[domainLevel="critico"],
QDialog#topicDetailsDialog QLabel#topicDomainLevelModern[domainLevel="fragil"] { background-color:#FDEAEA; color:#B43E45; }
QDialog#topicDetailsDialog QLabel#topicDomainLevelModern[domainLevel="desenvolvimento"],
QDialog#topicDetailsDialog QLabel#topicDomainLevelModern[domainLevel="consolidando"] { background-color:#FFF3D7; color:#956313; }
QDialog#topicDetailsDialog QLabel#topicDomainLevelModern[domainLevel="dominado"],
QDialog#topicDetailsDialog QLabel#topicDomainLevelModern[domainLevel="forte"] { background-color:#E6F6ED; color:#24714A; }
QDialog#topicDetailsDialog QProgressBar#topicDomainBarModern {
    background-color: #DFE8F2;
    border: none;
    border-radius: 4px;
}
QDialog#topicDetailsDialog QProgressBar#topicDomainBarModern::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #4D7FE0,stop:1 #55C8B3);
    border-radius: 4px;
}
QDialog#topicDetailsDialog QFrame#topicDomainComponentModern {
    background-color: #FFFFFF;
    border: 1px solid #DFE7F0;
    border-radius: 8px;
}
QDialog#topicDetailsDialog QLabel#topicDomainComponentLabelModern,
QDialog#topicDetailsDialog QLabel#topicDomainEvidenceLabel {
    color: #7A899B;
    font-size: 7.7pt;
    font-weight: 700;
}
QDialog#topicDetailsDialog QLabel#topicDomainComponentValueModern {
    color: #203349;
    font-size: 10.5pt;
    font-weight: 900;
}
QDialog#topicDetailsDialog QFrame#topicDomainInsight {
    background-color: #FFFFFF;
    border: 1px solid #DDE6EF;
    border-radius: 8px;
}
QDialog#topicDetailsDialog QFrame#topicDomainInsight[insightRole="strength"] { border-color:#BFDCCA; background-color:#F6FBF8; }
QDialog#topicDetailsDialog QFrame#topicDomainInsight[insightRole="attention"] { border-color:#E7D7AE; background-color:#FFFBF1; }
QDialog#topicDetailsDialog QLabel#topicDomainInsightTitle {
    color: #738397;
    font-size: 7.5pt;
    font-weight: 900;
}
QDialog#topicDetailsDialog QFrame#topicDomainInsight[insightRole="strength"] QLabel#topicDomainInsightText { color:#367258; }
QDialog#topicDetailsDialog QFrame#topicDomainInsight[insightRole="attention"] QLabel#topicDomainInsightText { color:#8D6B27; }
QDialog#topicDetailsDialog QLabel#topicDomainInsightText,
QDialog#topicDetailsDialog QLabel#topicDomainEvidenceModern {
    font-size: 8.2pt;
}
QDialog#topicDetailsDialog QLabel#topicDomainEvidenceModern { color:#54677B; }
QDialog#topicDetailsDialog QFrame#topicNextStepCard {
    background-color: #F6F9FD;
    border: 1px solid #D4E0EC;
    border-radius: 13px;
}
QDialog#topicDetailsDialog QLabel#topicNextEyebrow {
    color: #71839A;
    font-size: 8pt;
    font-weight: 900;
}
QDialog#topicDetailsDialog QLabel#topicNextStatus {
    color: #4F657A;
    background-color: #E8EEF5;
    border-radius: 8px;
    padding: 4px 8px;
    font-size: 7.8pt;
    font-weight: 900;
}
QDialog#topicDetailsDialog QLabel#topicNextStatus[scheduleState="overdue"] { color:#B0444A; background-color:#FDEAEA; }
QDialog#topicDetailsDialog QLabel#topicNextStatus[scheduleState="today"] { color:#986618; background-color:#FFF0D0; }
QDialog#topicDetailsDialog QLabel#topicNextStatus[scheduleState="soon"] { color:#2F6FA6; background-color:#EAF4FE; }
QDialog#topicDetailsDialog QLabel#topicNextStatus[scheduleState="future"] { color:#337A5B; background-color:#E8F6EE; }
QDialog#topicDetailsDialog QLabel#topicNextDate { color:#1D3550; font-size:17px; font-weight:900; }
QDialog#topicDetailsDialog QLabel#topicNextDescription,
QDialog#topicDetailsDialog QLabel#topicNextMeta { color:#6D7C8E; font-size:8.4pt; }
QDialog#topicDetailsDialog QPushButton#topicNextPrimaryButton {
    background-color:#356FD0; color:#FFFFFF; border:1px solid #5A8DDD; border-radius:9px; font-weight:900; padding:7px 12px;
}
QDialog#topicDetailsDialog QPushButton#topicNextPrimaryButton:hover { background-color:#2D63BC; border-color:#79A5E7; }
QDialog#topicDetailsDialog QFrame#topicEvolutionEmpty {
    background-color:#F8FAFC;
    border:1px dashed #CBD8E5;
    border-radius:10px;
}
QDialog#topicDetailsDialog QLabel#topicEvolutionEmptyIcon { color:#72A4CF; font-size:24px; }
QDialog#topicDetailsDialog QLabel#topicEvolutionEmptyTitle { color:#2C435A; font-size:10pt; font-weight:900; }
QDialog#topicDetailsDialog QLabel#topicEvolutionEmptyText { color:#788696; font-size:8.5pt; }
QDialog#topicDetailsDialog QTableWidget#topicHistoryTable {
    background-color:#FFFFFF;
    alternate-background-color:#F8FAFC;
    border:1px solid #DFE6EE;
    border-radius:8px;
}
"""

ESTILO_TOPICO_DETALHES_ESCURO = r"""
QDialog#topicDetailsDialog { background-color:#111827; }
QDialog#topicDetailsDialog QFrame#topicHeroCard,
QDialog#topicDetailsDialog QFrame#topicEvolutionCard,
QDialog#topicDetailsDialog QFrame#topicHistoryCard,
QDialog#topicDetailsDialog QFrame#topicHistoryDetailsCard {
    background-color:#182235; border:1px solid #334155; border-radius:13px;
}
QDialog#topicDetailsDialog QLabel#topicBreadcrumb { color:#88A4C0; font-size:8.5pt; font-weight:700; }
QDialog#topicDetailsDialog QLabel#topicHeroTitle { color:#F4F8FC; font-size:18pt; font-weight:900; }
QDialog#topicDetailsDialog QLabel#topicHeroSubtitle { color:#94A3B8; font-size:9pt; }
QDialog#topicDetailsDialog QPushButton#topicStudyButton { background-color:#416AB7; color:#FFF; border:1px solid #527FD0; border-radius:10px; font-weight:900; padding:7px 16px; }
QDialog#topicDetailsDialog QPushButton#topicStudyButton:hover { background-color:#355BA3; border-color:#6E98DF; }
QDialog#topicDetailsDialog QPushButton#topicQuestionsButton,
QDialog#topicDetailsDialog QPushButton#topicHistoryButton,
QDialog#topicDetailsDialog QPushButton#topicNextSecondaryButton,
QDialog#topicDetailsDialog QPushButton#topicNextGhostButton { background-color:#172536; color:#BCD7F0; border:1px solid #3A5877; border-radius:9px; font-weight:700; padding:6px 12px; }
QDialog#topicDetailsDialog QPushButton#topicQuestionsButton:hover,
QDialog#topicDetailsDialog QPushButton#topicHistoryButton:hover,
QDialog#topicDetailsDialog QPushButton#topicNextSecondaryButton:hover,
QDialog#topicDetailsDialog QPushButton#topicNextGhostButton:hover { background-color:#20374F; border-color:#527BA5; color:#E5F2FF; }
QDialog#topicDetailsDialog QFrame#topicMetricCard { background-color:#172131; border:1px solid #33465A; border-radius:10px; }
QDialog#topicDetailsDialog QFrame#topicMetricCard[metricRole="domain"] { background-color:#172536; border-color:#365574; }
QDialog#topicDetailsDialog QLabel#topicMetricLabel,
QDialog#topicDetailsDialog QLabel#topicCompactMetricLabel { color:#8CA4BB; font-size:8.2pt; font-weight:700; }
QDialog#topicDetailsDialog QLabel#topicMetricValue { color:#E8F1FA; font-size:13pt; font-weight:900; }
QDialog#topicDetailsDialog QFrame#topicMetricCard[metricRole="domain"] QLabel#topicMetricValue { color:#A9D3FF; }
QDialog#topicDetailsDialog QFrame#topicCompactMetric { background-color:#151F2D; border:1px solid #33465A; border-radius:8px; }
QDialog#topicDetailsDialog QLabel#topicCompactMetricValue { color:#C5D8EA; font-size:8.7pt; font-weight:900; }
QDialog#topicDetailsDialog QLabel#topicLegacyNotice { color:#D9BC7B; background-color:#332A1B; border:1px solid #675637; border-radius:8px; padding:6px 10px; font-size:8.2pt; }
QDialog#topicDetailsDialog QTabWidget#topicDetailsTabs::pane { border:0; background:transparent; }
QDialog#topicDetailsDialog QTabWidget#topicDetailsTabs QTabBar::tab { background:transparent; color:#8296AB; border:0; border-bottom:2px solid transparent; padding:8px 15px; font-weight:700; }
QDialog#topicDetailsDialog QTabWidget#topicDetailsTabs QTabBar::tab:selected { color:#BBD9F5; border-bottom-color:#5B94C7; }
QDialog#topicDetailsDialog QFrame#topicDomainCardModern { background-color:#172033; border:1px solid #365574; border-radius:13px; }
QDialog#topicDetailsDialog QLabel#topicDomainTitleModern,
QDialog#topicDetailsDialog QLabel#topicSectionTitle { color:#EEF5FB; font-size:10.5pt; font-weight:900; }
QDialog#topicDetailsDialog QLabel#topicDomainSubtitleModern,
QDialog#topicDetailsDialog QLabel#topicEvolutionSummary,
QDialog#topicDetailsDialog QLabel#topicHistoryHint { color:#8CA4BB; font-size:8.4pt; }
QDialog#topicDetailsDialog QLabel#topicDomainScoreModern { color:#A9D3FF; font-size:18px; font-weight:900; }
QDialog#topicDetailsDialog QLabel#topicDomainLevelModern { background-color:#334155; color:#CBD5E1; border-radius:8px; padding:4px 8px; font-size:8.2pt; font-weight:900; }
QDialog#topicDetailsDialog QLabel#topicDomainLevelModern[domainLevel="critico"],
QDialog#topicDetailsDialog QLabel#topicDomainLevelModern[domainLevel="fragil"] { background-color:#451C20; color:#F4A8AF; }
QDialog#topicDetailsDialog QLabel#topicDomainLevelModern[domainLevel="desenvolvimento"],
QDialog#topicDetailsDialog QLabel#topicDomainLevelModern[domainLevel="consolidando"] { background-color:#42351C; color:#F2CE7B; }
QDialog#topicDetailsDialog QLabel#topicDomainLevelModern[domainLevel="dominado"],
QDialog#topicDetailsDialog QLabel#topicDomainLevelModern[domainLevel="forte"] { background-color:#17372B; color:#8ED5AD; }
QDialog#topicDetailsDialog QProgressBar#topicDomainBarModern { background-color:#2C3D50; border:none; border-radius:4px; }
QDialog#topicDetailsDialog QProgressBar#topicDomainBarModern::chunk { background-color:#5596CF; border-radius:4px; }
QDialog#topicDetailsDialog QFrame#topicDomainComponentModern { background-color:#182235; border:1px solid #33465A; border-radius:8px; }
QDialog#topicDetailsDialog QLabel#topicDomainComponentLabelModern,
QDialog#topicDetailsDialog QLabel#topicDomainEvidenceLabel { color:#849BB1; font-size:7.7pt; font-weight:700; }
QDialog#topicDetailsDialog QLabel#topicDomainComponentValueModern { color:#E8F1F9; font-size:10.5pt; font-weight:900; }
QDialog#topicDetailsDialog QFrame#topicDomainInsight { background-color:#172131; border:1px solid #33465A; border-radius:8px; }
QDialog#topicDetailsDialog QFrame#topicDomainInsight[insightRole="strength"] { border-color:#365F4C; background-color:#172A24; }
QDialog#topicDetailsDialog QFrame#topicDomainInsight[insightRole="attention"] { border-color:#665638; background-color:#30291D; }
QDialog#topicDetailsDialog QLabel#topicDomainInsightTitle { color:#849BB1; font-size:7.5pt; font-weight:900; }
QDialog#topicDetailsDialog QFrame#topicDomainInsight[insightRole="strength"] QLabel#topicDomainInsightText { color:#91D6AC; }
QDialog#topicDetailsDialog QFrame#topicDomainInsight[insightRole="attention"] QLabel#topicDomainInsightText { color:#D9BC7B; }
QDialog#topicDetailsDialog QLabel#topicDomainInsightText,
QDialog#topicDetailsDialog QLabel#topicDomainEvidenceModern { font-size:8.2pt; }
QDialog#topicDetailsDialog QLabel#topicDomainEvidenceModern { color:#9CB0C3; }
QDialog#topicDetailsDialog QFrame#topicNextStepCard { background-color:#151F2D; border:1px solid #33465A; border-radius:13px; }
QDialog#topicDetailsDialog QLabel#topicNextEyebrow { color:#8CA4BB; font-size:8pt; font-weight:900; }
QDialog#topicDetailsDialog QLabel#topicNextStatus { color:#B7C5D4; background-color:#2B3949; border-radius:8px; padding:4px 8px; font-size:7.8pt; font-weight:900; }
QDialog#topicDetailsDialog QLabel#topicNextStatus[scheduleState="overdue"] { color:#F4A8AF; background-color:#451C20; }
QDialog#topicDetailsDialog QLabel#topicNextStatus[scheduleState="today"] { color:#F1CA75; background-color:#42351C; }
QDialog#topicDetailsDialog QLabel#topicNextStatus[scheduleState="soon"] { color:#A9D3FF; background-color:#20374F; }
QDialog#topicDetailsDialog QLabel#topicNextStatus[scheduleState="future"] { color:#91D6AC; background-color:#17372B; }
QDialog#topicDetailsDialog QLabel#topicNextDate { color:#E0EDF8; font-size:17px; font-weight:900; }
QDialog#topicDetailsDialog QLabel#topicNextDescription,
QDialog#topicDetailsDialog QLabel#topicNextMeta { color:#8CA4BB; font-size:8.4pt; }
QDialog#topicDetailsDialog QPushButton#topicNextPrimaryButton { background-color:#416AB7; color:#FFF; border:1px solid #527FD0; border-radius:9px; font-weight:900; padding:7px 12px; }
QDialog#topicDetailsDialog QPushButton#topicNextPrimaryButton:hover { background-color:#355BA3; border-color:#6E98DF; }
QDialog#topicDetailsDialog QFrame#topicEvolutionEmpty { background-color:#151F2D; border:1px dashed #3A4B5D; border-radius:10px; }
QDialog#topicDetailsDialog QLabel#topicEvolutionEmptyIcon { color:#6FA8D4; font-size:24px; }
QDialog#topicDetailsDialog QLabel#topicEvolutionEmptyTitle { color:#DDEAF5; font-size:10pt; font-weight:900; }
QDialog#topicDetailsDialog QLabel#topicEvolutionEmptyText { color:#879AAD; font-size:8.5pt; }
QDialog#topicDetailsDialog QTableWidget#topicHistoryTable { background-color:#151F2D; alternate-background-color:#172536; border:1px solid #33465A; border-radius:8px; }
"""

ESTILO_TOPICO_DETALHES_FUTURISTA = r"""
QDialog#topicDetailsDialog { background-color:#07111E; }
QDialog#topicDetailsDialog QFrame#topicHeroCard,
QDialog#topicDetailsDialog QFrame#topicEvolutionCard,
QDialog#topicDetailsDialog QFrame#topicHistoryCard,
QDialog#topicDetailsDialog QFrame#topicHistoryDetailsCard {
    background-color:#0D1D2D; border:1px solid #2E5A77; border-radius:13px;
}
QDialog#topicDetailsDialog QLabel#topicBreadcrumb { color:#78A9C7; }
QDialog#topicDetailsDialog QLabel#topicHeroTitle { color:#ECFAFF; }
QDialog#topicDetailsDialog QLabel#topicHeroSubtitle { color:#82A8BE; }
QDialog#topicDetailsDialog QPushButton#topicStudyButton,
QDialog#topicDetailsDialog QPushButton#topicNextPrimaryButton {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #4447E8,stop:0.5 #4F54EB,stop:1 #5355F2);
    color:#FFF; border:1px solid #8488FF;
}
QDialog#topicDetailsDialog QPushButton#topicStudyButton:hover,
QDialog#topicDetailsDialog QPushButton#topicNextPrimaryButton:hover { border-color:#B8BBFF; }
QDialog#topicDetailsDialog QPushButton#topicQuestionsButton,
QDialog#topicDetailsDialog QPushButton#topicHistoryButton,
QDialog#topicDetailsDialog QPushButton#topicNextSecondaryButton,
QDialog#topicDetailsDialog QPushButton#topicNextGhostButton { background-color:#10263A; color:#BCE7FF; border-color:#376D90; }
QDialog#topicDetailsDialog QPushButton#topicQuestionsButton:hover,
QDialog#topicDetailsDialog QPushButton#topicHistoryButton:hover,
QDialog#topicDetailsDialog QPushButton#topicNextSecondaryButton:hover,
QDialog#topicDetailsDialog QPushButton#topicNextGhostButton:hover { background-color:#17344B; border-color:#57B9DF; color:#EEFBFF; }
QDialog#topicDetailsDialog QFrame#topicMetricCard { background-color:#102236; border:1px solid #2F5872; }
QDialog#topicDetailsDialog QFrame#topicMetricCard[metricRole="domain"] { background-color:#102A3F; border-color:#397AA3; }
QDialog#topicDetailsDialog QLabel#topicMetricLabel,
QDialog#topicDetailsDialog QLabel#topicCompactMetricLabel { color:#78A2BC; }
QDialog#topicDetailsDialog QLabel#topicMetricValue { color:#E7F7FF; }
QDialog#topicDetailsDialog QFrame#topicMetricCard[metricRole="domain"] QLabel#topicMetricValue { color:#A8DFFF; }
QDialog#topicDetailsDialog QFrame#topicCompactMetric { background-color:#0C1D2D; border-color:#294C63; }
QDialog#topicDetailsDialog QLabel#topicCompactMetricValue { color:#B9DAEC; }
QDialog#topicDetailsDialog QLabel#topicLegacyNotice { color:#E1BB67; background-color:rgba(57,43,20,220); border-color:#755F34; }
QDialog#topicDetailsDialog QTabWidget#topicDetailsTabs QTabBar::tab { color:#7396AC; }
QDialog#topicDetailsDialog QTabWidget#topicDetailsTabs QTabBar::tab:selected { color:#C8F5FF; border-bottom-color:#55D4E6; }
QDialog#topicDetailsDialog QFrame#topicDomainCardModern { background-color:#0E2234; border-color:#326783; }
QDialog#topicDetailsDialog QLabel#topicDomainTitleModern,
QDialog#topicDetailsDialog QLabel#topicSectionTitle { color:#E6F8FF; }
QDialog#topicDetailsDialog QLabel#topicDomainSubtitleModern,
QDialog#topicDetailsDialog QLabel#topicEvolutionSummary,
QDialog#topicDetailsDialog QLabel#topicHistoryHint { color:#7FA6BD; }
QDialog#topicDetailsDialog QLabel#topicDomainScoreModern { color:#A9E4FF; }
QDialog#topicDetailsDialog QLabel#topicDomainLevelModern { background-color:#173047; color:#BBDDF0; }
QDialog#topicDetailsDialog QProgressBar#topicDomainBarModern { background-color:#173046; }
QDialog#topicDetailsDialog QProgressBar#topicDomainBarModern::chunk { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #4F6EF0,stop:0.55 #62BFE7,stop:1 #62DCC0); }
QDialog#topicDetailsDialog QFrame#topicDomainComponentModern { background-color:rgba(10,30,46,225); border-color:#2D5269; }
QDialog#topicDetailsDialog QLabel#topicDomainComponentLabelModern,
QDialog#topicDetailsDialog QLabel#topicDomainEvidenceLabel { color:#759DB5; }
QDialog#topicDetailsDialog QLabel#topicDomainComponentValueModern { color:#DDF5FF; }
QDialog#topicDetailsDialog QFrame#topicDomainInsight { background-color:#0D2031; border-color:#2A4E65; }
QDialog#topicDetailsDialog QFrame#topicDomainInsight[insightRole="strength"] { background-color:rgba(18,55,42,220); border-color:#36745A; }
QDialog#topicDetailsDialog QFrame#topicDomainInsight[insightRole="attention"] { background-color:rgba(57,43,20,220); border-color:#755F34; }
QDialog#topicDetailsDialog QLabel#topicDomainEvidenceModern { color:#8FB4C8; }
QDialog#topicDetailsDialog QFrame#topicNextStepCard { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #102A3D,stop:1 #0D2032); border-color:#356C8C; }
QDialog#topicDetailsDialog QLabel#topicNextEyebrow { color:#7FAAC3; }
QDialog#topicDetailsDialog QLabel#topicNextStatus { background-color:#173047; color:#A9D6EC; }
QDialog#topicDetailsDialog QLabel#topicNextDate { color:#EAF9FF; }
QDialog#topicDetailsDialog QLabel#topicNextDescription,
QDialog#topicDetailsDialog QLabel#topicNextMeta { color:#82A9BE; }
QDialog#topicDetailsDialog QFrame#topicEvolutionEmpty { background-color:#0B1C2B; border-color:#31556D; }
QDialog#topicDetailsDialog QLabel#topicEvolutionEmptyIcon { color:#5FC8E7; }
QDialog#topicDetailsDialog QLabel#topicEvolutionEmptyTitle { color:#DDF7FF; }
QDialog#topicDetailsDialog QLabel#topicEvolutionEmptyText { color:#789CB0; }
QDialog#topicDetailsDialog QTableWidget#topicHistoryTable { background-color:#0B1B2A; alternate-background-color:#0E2234; border-color:#2C536B; }
"""


# ============================================================
# Estado de eliminação do resolvedor — alta especificidade
#
# Estes seletores são deliberadamente tão específicos quanto a camada
# ESTILO_RESOLVEDOR_* acima. As versões anteriores usavam seletores globais
# menos específicos; por isso o tachado da fonte aparecia, mas o card podia
# continuar com a mesma cor/borda normal no tema Futurista.
# ============================================================
ESTILO_RESOLVEDOR_ELIMINADAS_CLARO = r"""
QDialog#questionSolverDialog QFrame#questionSolverAlternative[eliminated="true"][answerState="normal"] {
    background-color: {{color:answer.struck_surface}};
    border: 2px dashed {{color:answer.struck_border}};
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative[eliminated="true"][answerState="normal"]:hover {
    background-color: {{color:answer.struck_hover_surface}};
    border-color: {{color:answer.struck_hover_border}};
}
QDialog#questionSolverDialog QLabel#questionSolverAlternativeText[eliminated="true"],
QDialog#questionSolverDialog QRadioButton#questionSolverRadio[eliminated="true"] {
    color: {{color:answer.struck_text}};
}
QDialog#questionSolverDialog QToolButton#questionSolverEliminateButton:checked {
    background-color: {{color:answer.eliminate_checked_surface}};
    color: {{color:answer.eliminate_checked_text}};
    border: 1px solid {{color:answer.eliminate_checked_border}};
    border-radius: 6px;
}
"""

ESTILO_RESOLVEDOR_ELIMINADAS_ESCURO = r"""
QDialog#questionSolverDialog QFrame#questionSolverAlternative[eliminated="true"][answerState="normal"] {
    background-color: {{color:answer.struck_surface}};
    border: 2px dashed {{color:answer.struck_border}};
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative[eliminated="true"][answerState="normal"]:hover {
    background-color: {{color:answer.struck_hover_surface}};
    border-color: {{color:answer.struck_hover_border}};
}
QDialog#questionSolverDialog QLabel#questionSolverAlternativeText[eliminated="true"],
QDialog#questionSolverDialog QRadioButton#questionSolverRadio[eliminated="true"] {
    color: {{color:answer.struck_text}};
}
QDialog#questionSolverDialog QToolButton#questionSolverEliminateButton:checked {
    background-color: {{color:answer.eliminate_checked_surface}};
    color: {{color:answer.eliminate_checked_text}};
    border: 1px solid {{color:answer.eliminate_checked_border}};
    border-radius: 6px;
}
"""

ESTILO_RESOLVEDOR_ELIMINADAS_FUTURISTA = r"""
QDialog#questionSolverDialog QFrame#questionSolverAlternative[eliminated="true"][answerState="normal"] {
    background: {{gradient:answer.struck_gradient}};
    border: 2px dashed {{color:answer.struck_border}};
}
QDialog#questionSolverDialog QFrame#questionSolverAlternative[eliminated="true"][answerState="normal"]:hover {
    background-color: {{color:answer.struck_hover_surface}};
    border-color: {{color:answer.struck_hover_border}};
}
QDialog#questionSolverDialog QLabel#questionSolverAlternativeText[eliminated="true"],
QDialog#questionSolverDialog QRadioButton#questionSolverRadio[eliminated="true"] {
    color: {{color:answer.struck_text}};
}
QDialog#questionSolverDialog QToolButton#questionSolverEliminateButton:checked {
    background-color: {{color:answer.eliminate_checked_surface}};
    color: {{color:answer.eliminate_checked_text}};
    border: 1px solid {{color:answer.eliminate_checked_border}};
    border-radius: 6px;
}
"""

# Foco de navegação por teclado. Fica por último na composição do tema para
# continuar visível também quando a alternativa está selecionada ou eliminada.
ESTILO_RESOLVEDOR_TECLADO_CLARO = r"""
QDialog#questionSolverDialog QFrame#questionSolverAlternative[keyboardFocus="true"][answerState="normal"] {
    border: 2px solid {{color:answer.keyboard_focus_border}};
}
"""

ESTILO_RESOLVEDOR_TECLADO_ESCURO = r"""
QDialog#questionSolverDialog QFrame#questionSolverAlternative[keyboardFocus="true"][answerState="normal"] {
    border: 2px solid {{color:answer.keyboard_focus_border}};
}
"""

ESTILO_RESOLVEDOR_TECLADO_FUTURISTA = r"""
QDialog#questionSolverDialog QFrame#questionSolverAlternative[keyboardFocus="true"][answerState="normal"] {
    border: 2px solid {{color:answer.keyboard_focus_border}};
}
"""

ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_CLARO = r"""
QDialog#questionSolverDialog QLabel#questionSolverExplanationTitle {
    color: {{color:answer.explanation_title_text}};
    font-size: 8.5pt;
    font-weight: 800;
}
QDialog#questionSolverDialog QToolButton#questionSolverExplanationEditButton {
    background-color: #FFFFFF;
    color: #475569;
    border: 1px solid #CBD5E1;
    border-radius: 7px;
    font-size: 13pt;
    font-weight: 800;
}
QDialog#questionSolverDialog QToolButton#questionSolverExplanationEditButton:hover {
    background-color: #EEF2FF;
    color: #4338CA;
    border-color: #A5B4FC;
}
QDialog#questionSolverDialog QTextEdit#questionSolverExplanationEditor {
    background-color: {{color:answer.editor_surface}};
    color: {{color:answer.editor_text}};
    border: 1px solid {{color:answer.editor_border}};
    border-radius: 8px;
    padding: 7px;
}
QDialog#questionSolverDialog QPushButton#questionSolverExplanationSaveButton {
    background-color: #4F46E5;
    color: #FFFFFF;
    border: 1px solid #4338CA;
    border-radius: 8px;
    font-weight: 800;
    padding: 6px 14px;
}
QDialog#questionSolverDialog QPushButton#questionSolverExplanationCancelButton {
    background-color: #FFFFFF;
    color: #475569;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    font-weight: 700;
    padding: 6px 14px;
}
"""

ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_ESCURO = r"""
QDialog#questionSolverDialog QLabel#questionSolverExplanationTitle {
    color: {{color:answer.explanation_title_text}};
    font-size: 8.5pt;
    font-weight: 800;
}
QDialog#questionSolverDialog QToolButton#questionSolverExplanationEditButton {
    background-color: #182235;
    color: #CBD5E1;
    border: 1px solid #475569;
    border-radius: 7px;
    font-size: 13pt;
    font-weight: 800;
}
QDialog#questionSolverDialog QToolButton#questionSolverExplanationEditButton:hover {
    background-color: #273449;
    color: #FFFFFF;
    border-color: #8B95FF;
}
QDialog#questionSolverDialog QTextEdit#questionSolverExplanationEditor {
    background-color: {{color:answer.editor_surface}};
    color: {{color:answer.editor_text}};
    border: 1px solid {{color:answer.editor_border}};
    border-radius: 8px;
    padding: 7px;
}
QDialog#questionSolverDialog QPushButton#questionSolverExplanationSaveButton {
    background-color: #6366F1;
    color: #FFFFFF;
    border: 1px solid #818CF8;
    border-radius: 8px;
    font-weight: 800;
    padding: 6px 14px;
}
QDialog#questionSolverDialog QPushButton#questionSolverExplanationCancelButton {
    background-color: #1F2937;
    color: #CBD5E1;
    border: 1px solid #475569;
    border-radius: 8px;
    font-weight: 700;
    padding: 6px 14px;
}
"""

ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_FUTURISTA = r"""
QDialog#questionSolverDialog QLabel#questionSolverExplanationTitle {
    color: {{color:answer.explanation_title_text}};
    font-size: 8.5pt;
    font-weight: 800;
}
QDialog#questionSolverDialog QToolButton#questionSolverExplanationEditButton {
    background-color: #0D1D2D;
    color: #B6D9E8;
    border: 1px solid #355F82;
    border-radius: 7px;
    font-size: 13pt;
    font-weight: 800;
}
QDialog#questionSolverDialog QToolButton#questionSolverExplanationEditButton:hover {
    background-color: #15324A;
    color: #F2FBFF;
    border-color: #4BC9F2;
}
QDialog#questionSolverDialog QTextEdit#questionSolverExplanationEditor {
    background-color: {{color:answer.editor_surface}};
    color: {{color:answer.editor_text}};
    border: 1px solid {{color:answer.editor_border}};
    border-radius: 8px;
    padding: 7px;
    selection-background-color: {{color:answer.editor_selection}};
    selection-color: {{color:text.selection_accent}};
}
QDialog#questionSolverDialog QPushButton#questionSolverExplanationSaveButton {
    background-color: #19527A;
    color: #F1FAFF;
    border: 1px solid #4BC9F2;
    border-radius: 8px;
    font-weight: 800;
    padding: 6px 14px;
}
QDialog#questionSolverDialog QPushButton#questionSolverExplanationCancelButton {
    background-color: #0D1D2D;
    color: #B6D9E8;
    border: 1px solid #355F82;
    border-radius: 8px;
    font-weight: 700;
    padding: 6px 14px;
}
"""


ESTILO_CALENDARIO_PREVISAO_CLARO = r"""
QPushButton#calendarViewToggle {
    min-height: 30px;
    padding: 4px 13px;
    background-color: {{color:calendar.forecast_toggle_surface}};
    color: {{color:calendar.forecast_toggle_text}};
    border: 1px solid {{color:calendar.forecast_toggle_border}};
    border-radius: 8px;
    font-weight: 700;
}
QPushButton#calendarViewToggle:hover {
    background-color: {{color:calendar.forecast_toggle_hover_surface}};
    color: {{color:calendar.forecast_toggle_hover_text}};
    border-color: {{color:calendar.forecast_toggle_hover_border}};
}
QPushButton#calendarViewToggle:checked {
    background-color: {{color:calendar.forecast_toggle_checked_surface}};
    color: {{color:calendar.forecast_action_text}};
    border-color: {{color:calendar.forecast_toggle_checked_border}};
}
QLabel#calendarForecastHeaderHint,
QLabel#calendarForecastSubtitle,
QLabel#calendarForecastUpdated,
QLabel#calendarForecastReason,
QLabel#calendarForecastDayDate {
    color: {{color:calendar.forecast_meta_text}};
    background: {{color:action.ghost}};
}
QFrame#calendarForecastPanel {
    background-color: {{color:calendar.forecast_panel_surface}};
    border: 1px solid {{color:calendar.forecast_panel_border}};
    border-radius: 11px;
}
QLabel#calendarForecastTitle {
    color: {{color:calendar.forecast_title_text}};
    font-size: 15px;
    font-weight: 800;
}
QLabel#calendarForecastNotice {
    color: {{color:calendar.forecast_notice_text}};
    background-color: {{color:calendar.week_predicted_surface}};
    border: 1px solid {{color:calendar.week_predicted_border}};
    border-radius: 8px;
    padding: 7px 9px;
}
QScrollArea#calendarForecastScroll,
QScrollArea#calendarForecastScroll > QWidget > QWidget,
QWidget#calendarForecastBoard {
    background-color: {{color:action.ghost}};
    border: none;
}
QFrame#calendarForecastDay {
    background-color: {{color:calendar.week_predicted_surface}};
    border: 1px solid {{color:calendar.week_predicted_border}};
    border-radius: 10px;
}
QFrame#calendarForecastDay[dayState="today"] {
    background-color: {{color:calendar.forecast_today_surface}};
    border: 1px solid {{color:calendar.today_border}};
}
QFrame#calendarForecastDay[dayState="past"] {
    background-color: {{color:calendar.forecast_past_surface}};
    border: 1px solid {{color:calendar.forecast_past_border}};
}
QLabel#calendarForecastDayName {
    color: {{color:calendar.week_predicted_text}};
    font-weight: 800;
    font-size: 10.5pt;
}
QLabel#calendarForecastDayDate {
    font-size: 8.5pt;
    font-weight: 600;
}
QLabel#calendarForecastDayCount {
    background-color: {{color:calendar.forecast_count_surface}};
    color: {{color:calendar.forecast_count_text}};
    border-radius: 7px;
    padding: 2px 7px;
    font-size: 8pt;
    font-weight: 800;
}
QFrame#calendarForecastCard {
    background-color: {{color:calendar.forecast_card_surface}};
    border: 1px solid {{color:calendar.forecast_panel_border}};
    border-left: 3px solid {{color:calendar.forecast_card_accent}};
    border-radius: 8px;
}
QFrame#calendarForecastCard[forecastKind="revisao"] {
    border-left-color: {{color:calendar.forecast_review}};
}
QFrame#calendarForecastCard[forecastKind="realizado"] {
    border-left-color: {{color:calendar.forecast_completed}};
}
QFrame#calendarForecastCard[forecastKind="recomendacao"] {
    border-left-color: {{color:calendar.forecast_recommendation}};
}
QFrame#calendarForecastCard[forecastKind="simulado"] {
    border-left-color: {{color:calendar.forecast_simulation}};
}
QLabel#calendarForecastDiscipline {
    color: {{color:calendar.forecast_discipline_text}};
    font-size: 8pt;
    font-weight: 800;
}
QLabel#calendarForecastCardTitle {
    color: {{color:calendar.forecast_card_text}};
    font-size: 9.5pt;
    font-weight: 700;
}
QLabel#calendarForecastKind,
QLabel#calendarForecastLoad {
    background-color: {{color:calendar.forecast_badge_surface}};
    color: {{color:calendar.forecast_badge_text}};
    border: 1px solid {{color:calendar.forecast_badge_border}};
    border-radius: 6px;
    padding: 2px 5px;
    font-size: 7.5pt;
    font-weight: 700;
}
QLabel#calendarForecastReason {
    font-size: 7.8pt;
}
QToolButton#calendarForecastOpen {
    background-color: {{color:action.ghost}};
    color: {{color:calendar.forecast_open_text}};
    border: 1px solid {{color:action.ghost}};
    border-radius: 6px;
    font-weight: 800;
}
QToolButton#calendarForecastOpen:hover {
    background-color: {{color:calendar.forecast_open_hover_surface}};
    color: {{color:calendar.forecast_action_text}};
    border-color: {{color:calendar.forecast_open_hover_border}};
}
QLabel#calendarForecastDayEmpty,
QLabel#calendarForecastEmpty {
    color: {{color:calendar.forecast_empty_text}};
    background: {{color:action.ghost}};
    padding: 18px 7px;
}
"""

ESTILO_CALENDARIO_PREVISAO_ESCURO = r"""
QPushButton#calendarViewToggle {
    min-height: 30px;
    padding: 4px 13px;
    background-color: {{color:calendar.forecast_toggle_surface}};
    color: {{color:calendar.forecast_toggle_text}};
    border: 1px solid {{color:calendar.forecast_toggle_border}};
    border-radius: 8px;
    font-weight: 700;
}
QPushButton#calendarViewToggle:hover {
    background-color: {{color:calendar.forecast_toggle_hover_surface}};
    color: {{color:calendar.forecast_toggle_hover_text}};
    border-color: {{color:calendar.forecast_toggle_hover_border}};
}
QPushButton#calendarViewToggle:checked {
    background-color: {{color:calendar.forecast_toggle_checked_surface}};
    color: {{color:calendar.forecast_action_text}};
    border-color: {{color:calendar.forecast_toggle_checked_border}};
}
QLabel#calendarForecastHeaderHint,
QLabel#calendarForecastSubtitle,
QLabel#calendarForecastUpdated,
QLabel#calendarForecastReason,
QLabel#calendarForecastDayDate {
    color: {{color:calendar.forecast_meta_text}};
    background: {{color:action.ghost}};
}
QFrame#calendarForecastPanel {
    background-color: {{color:calendar.forecast_panel_surface}};
    border: 1px solid {{color:calendar.forecast_panel_border}};
    border-radius: 11px;
}
QLabel#calendarForecastTitle {
    color: {{color:calendar.forecast_title_text}};
    font-size: 15px;
    font-weight: 800;
}
QLabel#calendarForecastNotice {
    color: {{color:calendar.forecast_notice_text}};
    background-color: {{color:calendar.week_predicted_surface}};
    border: 1px solid {{color:calendar.week_predicted_border}};
    border-radius: 8px;
    padding: 7px 9px;
}
QScrollArea#calendarForecastScroll,
QScrollArea#calendarForecastScroll > QWidget > QWidget,
QWidget#calendarForecastBoard {
    background-color: {{color:action.ghost}};
    border: none;
}
QFrame#calendarForecastDay {
    background-color: {{color:calendar.week_predicted_surface}};
    border: 1px solid {{color:calendar.week_predicted_border}};
    border-radius: 10px;
}
QFrame#calendarForecastDay[dayState="today"] {
    background-color: {{color:calendar.forecast_today_surface}};
    border: 1px solid {{color:calendar.today_border}};
}
QFrame#calendarForecastDay[dayState="past"] {
    background-color: {{color:calendar.forecast_past_surface}};
    border: 1px solid {{color:calendar.forecast_past_border}};
}
QLabel#calendarForecastDayName {
    color: {{color:calendar.week_predicted_text}};
    font-weight: 800;
    font-size: 10.5pt;
}
QLabel#calendarForecastDayDate {
    font-size: 8.5pt;
    font-weight: 600;
}
QLabel#calendarForecastDayCount {
    background-color: {{color:calendar.forecast_count_surface}};
    color: {{color:calendar.forecast_count_text}};
    border-radius: 7px;
    padding: 2px 7px;
    font-size: 8pt;
    font-weight: 800;
}
QFrame#calendarForecastCard {
    background-color: {{color:calendar.forecast_card_surface}};
    border: 1px solid {{color:calendar.forecast_panel_border}};
    border-left: 3px solid {{color:calendar.forecast_card_accent}};
    border-radius: 8px;
}
QFrame#calendarForecastCard[forecastKind="revisao"] {
    border-left-color: {{color:calendar.forecast_review}};
}
QFrame#calendarForecastCard[forecastKind="realizado"] {
    border-left-color: {{color:calendar.forecast_completed}};
}
QFrame#calendarForecastCard[forecastKind="recomendacao"] {
    border-left-color: {{color:calendar.forecast_recommendation}};
}
QFrame#calendarForecastCard[forecastKind="simulado"] {
    border-left-color: {{color:calendar.forecast_simulation}};
}
QLabel#calendarForecastDiscipline {
    color: {{color:calendar.forecast_discipline_text}};
    font-size: 8pt;
    font-weight: 800;
}
QLabel#calendarForecastCardTitle {
    color: {{color:calendar.forecast_card_text}};
    font-size: 9.5pt;
    font-weight: 700;
}
QLabel#calendarForecastKind,
QLabel#calendarForecastLoad {
    background-color: {{color:calendar.forecast_badge_surface}};
    color: {{color:calendar.forecast_badge_text}};
    border: 1px solid {{color:calendar.forecast_badge_border}};
    border-radius: 6px;
    padding: 2px 5px;
    font-size: 7.5pt;
    font-weight: 700;
}
QLabel#calendarForecastReason {
    font-size: 7.8pt;
}
QToolButton#calendarForecastOpen {
    background-color: {{color:action.ghost}};
    color: {{color:calendar.forecast_open_text}};
    border: 1px solid {{color:action.ghost}};
    border-radius: 6px;
    font-weight: 800;
}
QToolButton#calendarForecastOpen:hover {
    background-color: {{color:calendar.forecast_open_hover_surface}};
    color: {{color:calendar.forecast_action_text}};
    border-color: {{color:calendar.forecast_open_hover_border}};
}
QLabel#calendarForecastDayEmpty,
QLabel#calendarForecastEmpty {
    color: {{color:calendar.forecast_empty_text}};
    background: {{color:action.ghost}};
    padding: 18px 7px;
}
"""

ESTILO_CALENDARIO_PREVISAO_FUTURISTA = r"""
QPushButton#calendarViewToggle {
    min-height: 30px;
    padding: 4px 13px;
    background-color: {{color:calendar.forecast_toggle_surface}};
    color: {{color:calendar.forecast_toggle_text}};
    border: 1px solid {{color:calendar.forecast_toggle_border}};
    border-radius: 8px;
    font-weight: 700;
}
QPushButton#calendarViewToggle:hover {
    background-color: {{color:calendar.forecast_toggle_hover_surface}};
    color: {{color:calendar.forecast_toggle_hover_text}};
    border-color: {{color:calendar.forecast_toggle_hover_border}};
}
QPushButton#calendarViewToggle:checked {
    background-color: {{color:calendar.forecast_toggle_checked_surface}};
    color: {{color:calendar.forecast_action_text}};
    border-color: {{color:calendar.forecast_toggle_checked_border}};
}
QLabel#calendarForecastHeaderHint,
QLabel#calendarForecastSubtitle,
QLabel#calendarForecastUpdated,
QLabel#calendarForecastReason,
QLabel#calendarForecastDayDate {
    color: {{color:calendar.forecast_meta_text}};
    background: {{color:action.ghost}};
}
QFrame#calendarForecastPanel {
    background-color: {{color:calendar.forecast_panel_surface}};
    border: 1px solid {{color:calendar.forecast_panel_border}};
    border-radius: 11px;
}
QLabel#calendarForecastTitle {
    color: {{color:calendar.forecast_title_text}};
    font-size: 15px;
    font-weight: 800;
}
QLabel#calendarForecastNotice {
    color: {{color:calendar.forecast_notice_text}};
    background-color: {{color:calendar.week_predicted_surface}};
    border: 1px solid {{color:calendar.week_predicted_border}};
    border-radius: 8px;
    padding: 7px 9px;
}
QScrollArea#calendarForecastScroll,
QScrollArea#calendarForecastScroll > QWidget > QWidget,
QWidget#calendarForecastBoard {
    background-color: {{color:action.ghost}};
    border: none;
}
QFrame#calendarForecastDay {
    background-color: {{color:calendar.week_predicted_surface}};
    border: 1px solid {{color:calendar.week_predicted_border}};
    border-radius: 10px;
}
QFrame#calendarForecastDay[dayState="today"] {
    background-color: {{color:calendar.forecast_today_surface}};
    border: 1px solid {{color:calendar.today_border}};
}
QFrame#calendarForecastDay[dayState="past"] {
    background-color: {{color:calendar.forecast_past_surface}};
    border: 1px solid {{color:calendar.forecast_past_border}};
}
QLabel#calendarForecastDayName {
    color: {{color:calendar.week_predicted_text}};
    font-weight: 800;
    font-size: 10.5pt;
}
QLabel#calendarForecastDayDate {
    font-size: 8.5pt;
    font-weight: 600;
}
QLabel#calendarForecastDayCount {
    background-color: {{color:calendar.forecast_count_surface}};
    color: {{color:calendar.forecast_count_text}};
    border-radius: 7px;
    padding: 2px 7px;
    font-size: 8pt;
    font-weight: 800;
}
QFrame#calendarForecastCard {
    background-color: {{color:calendar.forecast_card_surface}};
    border: 1px solid {{color:calendar.forecast_panel_border}};
    border-left: 3px solid {{color:calendar.forecast_card_accent}};
    border-radius: 8px;
}
QFrame#calendarForecastCard[forecastKind="revisao"] {
    border-left-color: {{color:calendar.forecast_review}};
}
QFrame#calendarForecastCard[forecastKind="realizado"] {
    border-left-color: {{color:calendar.forecast_completed}};
}
QFrame#calendarForecastCard[forecastKind="recomendacao"] {
    border-left-color: {{color:calendar.forecast_recommendation}};
}
QFrame#calendarForecastCard[forecastKind="simulado"] {
    border-left-color: {{color:calendar.forecast_simulation}};
}
QLabel#calendarForecastDiscipline {
    color: {{color:calendar.forecast_discipline_text}};
    font-size: 8pt;
    font-weight: 800;
}
QLabel#calendarForecastCardTitle {
    color: {{color:calendar.forecast_card_text}};
    font-size: 9.5pt;
    font-weight: 700;
}
QLabel#calendarForecastKind,
QLabel#calendarForecastLoad {
    background-color: {{color:calendar.forecast_badge_surface}};
    color: {{color:calendar.forecast_badge_text}};
    border: 1px solid {{color:calendar.forecast_badge_border}};
    border-radius: 6px;
    padding: 2px 5px;
    font-size: 7.5pt;
    font-weight: 700;
}
QLabel#calendarForecastReason {
    font-size: 7.8pt;
}
QToolButton#calendarForecastOpen {
    background-color: {{color:action.ghost}};
    color: {{color:calendar.forecast_open_text}};
    border: 1px solid {{color:action.ghost}};
    border-radius: 6px;
    font-weight: 800;
}
QToolButton#calendarForecastOpen:hover {
    background-color: {{color:calendar.forecast_open_hover_surface}};
    color: {{color:calendar.forecast_action_text}};
    border-color: {{color:calendar.forecast_open_hover_border}};
}
QLabel#calendarForecastDayEmpty,
QLabel#calendarForecastEmpty {
    color: {{color:calendar.forecast_empty_text}};
    background: {{color:action.ghost}};
    padding: 18px 7px;
}
"""

def stylesheet_claro():
    return render_qss("claro", r"""
    * {
        font-family: "Segoe UI";
        font-size: 10pt;
    }

    QMainWindow,
    QDialog,
    QWidget {
        background-color: #f5f7fa;
        color: #1f2937;
    }

    /* Textos e controles de seleção não devem pintar o fundo genérico de
       QWidget. Isso evita retângulos internos atrás de frases dentro de cards. */
    QLabel,
    QCheckBox,
    QRadioButton {
        background-color: transparent;
    }

    QScrollArea,
    QScrollArea > QWidget > QWidget {
        background-color: transparent;
        border: none;
    }

    QLabel#pageTitle {
        font-size: 24px;
        font-weight: 700;
        color: #111827;
    }

    QLabel#pageSubtitle {
        font-size: 11pt;
        color: #64748b;
    }

    QLabel#sectionTitle {
        font-size: 15px;
        font-weight: 700;
        color: #111827;
        padding-top: 4px;
    }

    QLabel#mutedLabel {
        color: #64748b;
    }

    QFrame#contextBar {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 10px;
    }


    QFrame#dashboardCenterBar {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 10px;
    }


    QFrame#calendarPanel,
    QFrame#calendarDayPanel {
        background-color: {{color:calendar.surface}};
        border: 1px solid {{color:calendar.border}};
        border-radius: 11px;
    }

    QLabel#calendarDateTitle {
        background: {{color:action.ghost}};
        color: {{color:calendar.title_text}};
        font-size: 15px;
        font-weight: 700;
    }

    QLabel#calendarCountBadge {
        background-color: {{color:calendar.badge_surface}};
        color: {{color:calendar.badge_text}};
        border: 1px solid {{color:calendar.badge_border}};
        border-radius: 7px;
        padding: 4px 8px;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#calendarLegendToday {
        color: {{color:calendar.legend_today}};
        background: {{color:action.ghost}};
        font-weight: 600;
    }

    QLabel#calendarLegendLate {
        color: {{color:calendar.legend_late}};
        background: {{color:action.ghost}};
        font-weight: 600;
    }

    QLabel#calendarLegendFuture {
        color: {{color:calendar.legend_scheduled}};
        background: {{color:action.ghost}};
        font-weight: 600;
    }

    QCalendarWidget#reviewCalendar {
        background-color: {{color:calendar.surface}};
        border: none;
    }

    QCalendarWidget#reviewCalendar QWidget#qt_calendar_navigationbar {
        background-color: {{color:calendar.navigation_surface}};
        border-radius: 8px;
    }

    QCalendarWidget#reviewCalendar QToolButton {
        background-color: {{color:action.ghost}};
        color: {{color:calendar.text}};
        border: none;
        border-radius: 6px;
        padding: 5px 8px;
        font-weight: 700;
    }

    QCalendarWidget#reviewCalendar QToolButton:hover {
        background-color: {{color:calendar.navigation_hover_surface}};
    }

    QCalendarWidget#reviewCalendar QSpinBox {
        background-color: {{color:calendar.input_surface}};
        color: {{color:calendar.text}};
        border: 1px solid {{color:calendar.input_border}};
        border-radius: 6px;
        padding: 3px 6px;
    }

    QCalendarWidget#reviewCalendar QAbstractItemView {
        background-color: {{color:calendar.surface}};
        color: {{color:calendar.text}};
        selection-background-color: {{color:calendar.selected_surface}};
        selection-color: {{color:calendar.selected_text}};
        border: none;
        outline: none;
    }

    QWidget#dashboardHeaderSide {
        background: transparent;
        border: none;
    }

    QLabel#disciplineSectionTitle {
        background: transparent;
        color: #111827;
        font-size: 19px;
        font-weight: 700;
    }

    QLabel#contextLabel {
        background: transparent;
        color: #475569;
        font-weight: 700;
    }

    QLabel#queueCount {
        background: transparent;
        color: #64748b;
        font-size: 9pt;
        font-weight: 600;
    }

    QPushButton#subtleButton {
        min-height: 28px;
        padding: 4px 10px;
        background-color: transparent;
        color: #475569;
        border: 1px solid #cbd5e1;
        border-radius: 7px;
        font-weight: 600;
    }

    QPushButton#subtleButton:hover {
        background-color: #f1f5f9;
        border-color: #94a3b8;
    }


    QLabel#profileBadge {
        background-color: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 5px 10px;
        font-size: 9pt;
        font-weight: 700;
    }

    QFrame#topProfileBar {
        background-color: #f8fbff;
        border: 1px solid #d2e0ef;
        border-radius: 11px;
    }

    QLabel#topProfileLabel {
        color: #315c8a;
        font-size: 8.0pt;
        font-weight: 900;
        letter-spacing: 0.45px;
    }

    QLabel#topProfileHint {
        color: #71849a;
        font-size: 8.2pt;
    }

    QComboBox#topProfileCombo {
        min-height: 32px;
        background-color: #ffffff;
        color: #153453;
        border: 1px solid #b8cee5;
        border-radius: 8px;
        padding: 2px 10px;
        font-weight: 800;
    }

    QComboBox#topProfileCombo:hover,
    QComboBox#topProfileCombo:focus {
        border-color: #6ea5dd;
        background-color: #fbfdff;
    }

    QFrame#miniStat {
        background-color: #fbfdff;
        border: 1px solid #d9e5f0;
        border-radius: 10px;
    }

    QLabel#miniStatLabel {
        background: transparent;
        color: #64748b;
        font-size: 9pt;
    }

    QLabel#miniStatValue {
        background: transparent;
        color: #111827;
        font-size: 17px;
        font-weight: 700;
    }

    QFrame#filterBar {
        background-color: #fbfdff;
        border: 1px solid #d6e2ef;
        border-radius: 10px;
    }

    QLabel#filterCount {
        background-color: #f1f5f9;
        color: #475569;
        border: 1px solid #e2e8f0;
        border-radius: 7px;
        padding: 5px 9px;
        font-size: 9pt;
        font-weight: 600;
    }

    QPushButton#dangerButton {
        min-height: 30px;
        padding: 6px 12px;
        background-color: #ffffff;
        color: #b91c1c;
        border: 1px solid #fecaca;
        border-radius: 8px;
        font-weight: 600;
    }

    QPushButton#dangerButton:hover {
        background-color: #fef2f2;
        border-color: #fca5a5;
    }

    QPushButton#rowActionButton {
        min-height: 0px;
        padding: 1px 6px;
        background: transparent;
        color: #475569;
        border: 1px solid #cbd5e1;
        border-radius: 5px;
        font-size: 9pt;
        font-weight: 400;
    }

    QPushButton#rowActionButton:hover {
        background-color: #f1f5f9;
        border-color: #94a3b8;
    }
QPushButton#sectionEditButton {
        min-height: 0px;
        padding: 5px 13px;
        background-color: #eaf2ff;
        color: #1d4ed8;
        border: 1px solid #93c5fd;
        border-radius: 8px;
        font-size: 9.5pt;
        font-weight: 700;
    }
QPushButton#sectionEditButton:hover {
        background-color: #dbeafe;
        border-color: #60a5fa;
        color: #1e40af;
    }

    QPushButton#sectionEditButton:pressed {
        background-color: #bfdbfe;
        border-color: #3b82f6;
    }


    QFrame#dialogCard {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 11px;
    }

    QFrame#dialogCard QLabel {
        background: transparent;
    }

    QFrame#topicDomainCard {
        background-color: #f8fbff;
        border: 1px solid #bfdbfe;
        border-radius: 10px;
    }

    QFrame#topicDomainCard QLabel {
        background: transparent;
    }

    QLabel#topicDomainTitle {
        color: #111827;
        font-size: 10.5pt;
        font-weight: 800;
    }

    QLabel#topicDomainSubtitle {
        color: #64748b;
        font-size: 8.5pt;
    }

    QLabel#topicDomainScore {
        color: #1d4ed8;
        font-size: 18px;
        font-weight: 900;
    }

    QLabel#topicDomainLevel {
        background-color: #e2e8f0;
        color: #475569;
        border-radius: 7px;
        padding: 5px 8px;
        font-size: 8.5pt;
        font-weight: 800;
    }

    QLabel#topicDomainLevel[domainLevel="critico"],
    QLabel#topicDomainLevel[domainLevel="fragil"] {
        background-color: #fee2e2;
        color: #b91c1c;
    }

    QLabel#topicDomainLevel[domainLevel="desenvolvimento"],
    QLabel#topicDomainLevel[domainLevel="consolidando"] {
        background-color: #fef3c7;
        color: #92400e;
    }

    QLabel#topicDomainLevel[domainLevel="dominado"],
    QLabel#topicDomainLevel[domainLevel="forte"] {
        background-color: #dcfce7;
        color: #166534;
    }

    QProgressBar#topicDomainBar {
        background-color: #e2e8f0;
        border: none;
        border-radius: 4px;
    }

    QProgressBar#topicDomainBar::chunk {
        background-color: #2563eb;
        border-radius: 4px;
    }

    QFrame#topicDomainComponent {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 7px;
    }

    QLabel#topicDomainComponentLabel {
        color: #64748b;
        font-size: 7.8pt;
    }

    QLabel#topicDomainComponentValue {
        color: #111827;
        font-size: 11pt;
        font-weight: 800;
    }

    QLabel#topicDomainEvidence {
        color: #334155;
        font-size: 8.4pt;
        font-weight: 600;
    }

    QLabel#topicDomainReasons {
        color: #64748b;
        font-size: 8.2pt;
    }

    QFrame#metricCard {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
    }

    QLabel#metricLabel {
        background: transparent;
        color: #64748b;
        font-size: 9pt;
    }

    QLabel#metricValue {
        background: transparent;
        color: #111827;
        font-size: 15px;
        font-weight: 700;
    }

    QLabel#fieldLabel {
        background: transparent;
        color: #64748b;
        font-size: 9pt;
        font-weight: 600;
    }

    QLabel#sessionBadge {
        background-color: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 5px 9px;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#resultValue {
        background-color: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        font-size: 17px;
        font-weight: 800;
        padding: 4px 8px;
    }

    QFrame#suggestionCard {
        background-color: #f8fbff;
        border: 1px solid #bfdbfe;
        border-radius: 11px;
    }

    QFrame#suggestionCard QLabel {
        background: transparent;
    }

    QLabel#suggestionStrong {
        background: transparent;
        color: #1d4ed8;
        font-size: 12pt;
        font-weight: 700;
    }

    QLabel#infoNotice {
        background-color: #fffbeb;
        color: #92400e;
        border: 1px solid #fde68a;
        border-radius: 9px;
        padding: 8px 10px;
        font-size: 9pt;
    }

    QTextEdit#detailsReadOnly {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
    }


    QPushButton#dashboardSectionToggle,
    QPushButton#dashboardSectionToggleCentered {
        background: transparent;
        color: #111827;
        border: none;
        border-radius: 5px;
        padding: 1px 4px;
        font-size: 11pt;
        font-weight: 800;
        text-align: left;
    }

    QPushButton#dashboardSectionToggle:hover,
    QPushButton#dashboardSectionToggleCentered:hover {
        background-color: #eef4fb;
        color: #1d4ed8;
    }

    QPushButton#dashboardSectionToggleCentered {
        text-align: center;
    }

    QPushButton#dashboardSectionToggle[expanded="false"],
    QPushButton#dashboardSectionToggleCentered[expanded="false"] {
        color: #334155;
    }

    QWidget#dashboardCollapsibleContent {
        background: transparent;
    }

    QFrame#syllabusProgressPanel {
        background-color: #f8fbff;
        border: 1px solid #cddbea;
        border-radius: 10px;
    }

    QFrame#syllabusProgressPanel QLabel,
    QFrame#syllabusDashboardCoverage QLabel,
    QFrame#syllabusDashboardStat QLabel {
        background: transparent;
    }

    QLabel#syllabusDashboardTitle {
        color: #111827;
        font-size: 11pt;
        font-weight: 800;
    }

    QFrame#syllabusDashboardCoverage,
    QFrame#syllabusDashboardStat {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }

    QLabel#syllabusDashboardMetricLabel {
        color: #64748b;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#syllabusDashboardMetricValue {
        color: #111827;
        font-size: 14px;
        font-weight: 800;
    }

    QLabel#syllabusDashboardHint {
        color: #64748b;
        font-size: 8pt;
    }

    QPushButton#syllabusOpenButton {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #1d4ed8;
        border-radius: 7px;
        padding: 6px 12px;
        font-weight: 700;
    }

    QPushButton#syllabusOpenButton:hover {
        background-color: #1d4ed8;
    }

    QProgressBar#syllabusDashboardBar {
        background-color: #e2e8f0;
        border: none;
        border-radius: 4px;
    }

    QProgressBar#syllabusDashboardBar::chunk {
        background-color: #3b82f6;
        border-radius: 4px;
    }

    QFrame#questionReviewIntegrationCard {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
    }

    QLabel#questionReviewIntegrationTitle {
        color: #166534;
        font-size: 9.5pt;
        font-weight: 800;
    }

    QLabel#questionReviewIntegrationText {
        color: #166534;
        font-size: 8.5pt;
    }

    QFrame#questionsInsightsBar {
        background-color: #f8fbff;
        border: 1px solid #cddbea;
        border-radius: 9px;
    }

    QFrame#questionsInsightsBar QLabel {
        background: transparent;
    }

    QLabel#questionsInsightsTitle {
        color: #111827;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#questionsInsightsDescription {
        color: #64748b;
        font-size: 8.5pt;
    }

    QLabel#questionsInsightsSummary {
        color: #475569;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QPushButton#questionsHistoryButton {
        background-color: #ffffff;
        color: #1d4ed8;
        border: 1px solid #93c5fd;
        border-radius: 7px;
        padding: 6px 11px;
        font-weight: 800;
    }

    QPushButton#questionsHistoryButton:hover {
        background-color: #eff6ff;
        border-color: #60a5fa;
    }

    QFrame#questionHistoryStat,
    QFrame#questionHistoryFilterCard {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 9px;
    }

    QTabWidget#questionHistoryTabs::pane {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 9px;
        top: -1px;
    }

    QTabWidget#questionHistoryTabs QTabBar::tab {
        background-color: #eef2f7;
        color: #475569;
        border: 1px solid #dbe3ed;
        padding: 8px 18px;
        min-width: 120px;
        font-weight: 800;
    }

    QTabWidget#questionHistoryTabs QTabBar::tab:selected {
        background-color: #2563eb;
        color: #ffffff;
        border-color: #1d4ed8;
    }

    QTableWidget#questionHistoryTable,
    QTableWidget#questionErrorBookTable {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QLabel#questionErrorBookRule {
        background-color: #f8fafc;
        color: #64748b;
        border: 1px solid #e2e8f0;
        border-radius: 7px;
        padding: 7px 9px;
        font-size: 8.5pt;
    }

    QPushButton#questionRetryButton {
        background-color: #ffffff;
        color: #475569;
        border: 1px solid #cbd5e1;
        border-radius: 7px;
        padding: 6px 10px;
        font-weight: 700;
    }

    QPushButton#questionRetryButton:hover {
        background-color: #f8fafc;
        border-color: #94a3b8;
    }

    QPushButton#questionReviewErrorsButton {
        background-color: #b91c1c;
        color: #ffffff;
        border: 1px solid #991b1b;
        border-radius: 7px;
        padding: 6px 11px;
        font-weight: 800;
    }

    QPushButton#questionReviewErrorsButton:hover {
        background-color: #991b1b;
    }

    QFrame#questionsHeroActions {
        background-color: #fbfdff;
        border: 1px solid #d7e2ee;
        border-radius: 12px;
    }

    QFrame#questionsHeroActions QLabel {
        background: transparent;
    }

    QPushButton#questionsAnalysisButton,
    QPushButton#questionsAnalysisCompleteButton {
        background-color: #fffbeb;
        color: #92400e;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 7px 12px;
        font-weight: 800;
    }

    QPushButton#questionsAnalysisButton:hover,
    QPushButton#questionsAnalysisCompleteButton:hover {
        background-color: #fef3c7;
        border-color: #d97706;
    }

    QPushButton#questionsAnalysisButton:checked {
        background-color: #d97706;
        color: #ffffff;
        border-color: #b45309;
    }

    QPushButton#questionsAnalysisButton:disabled,
    QPushButton#questionsAnalysisCompleteButton:disabled {
        background-color: #f8fafc;
        color: #94a3b8;
        border-color: #cbd5e1;
    }

    QToolButton#questionsImportMenuButton,
    QToolButton#questionsMoreMenuButton {
        background-color: #ffffff;
        color: #334155;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 7px 12px;
        font-weight: 700;
    }

    QToolButton#questionsImportMenuButton:hover,
    QToolButton#questionsMoreMenuButton:hover {
        background-color: #f8fafc;
        border-color: #94a3b8;
        color: #1d4ed8;
    }

    QFrame#questionsInventoryStrip {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 11px;
    }

    QFrame#questionsInventoryItem {
        background: transparent;
        border: none;
    }

    QLabel#questionsInventoryValue {
        background: transparent;
        color: #4338ca;
        font-size: 14pt;
        font-weight: 900;
    }

    QLabel#questionsInventoryLabel {
        background: transparent;
        color: #64748b;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QFrame#questionsInventoryDivider {
        background-color: #e2e8f0;
        border: none;
    }

    QFrame#questionsWorkspaceCard {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 12px;
    }

    QFrame#questionsWorkspaceCard QFrame#questionsFoundationNotice {
        background: transparent;
        border: none;
    }

    QFrame#questionsWorkspaceCard QFrame#questionsFilterBar {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 9px;
    }

    QLabel#questionsHeroTitle {
        color: #12253d;
        font-size: 10.7pt;
        font-weight: 900;
    }

    QLabel#questionsHeroDescription {
        color: #627387;
        font-size: 8.7pt;
    }

    QFrame#questionsHeroDivider {
        background-color: #dbe3ed;
        border: none;
        margin-top: 3px;
        margin-bottom: 3px;
    }

    QPushButton#questionsSolveHeroButton {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #1d4ed8;
        border-radius: 9px;
        padding: 10px 18px;
        font-size: 10.5pt;
        font-weight: 800;
    }

    QPushButton#questionsSolveHeroButton:hover {
        background-color: #1d4ed8;
        border-color: #1e40af;
    }

    QPushButton#questionsSolveHeroButton:disabled {
        background-color: #e2e8f0;
        color: #94a3b8;
        border-color: #cbd5e1;
    }

    QPushButton#questionsNewHeroButton {
        background-color: #ffffff;
        color: #1d4ed8;
        border: 1px solid #93c5fd;
        border-radius: 9px;
        padding: 10px 18px;
        font-size: 10.5pt;
        font-weight: 800;
    }

    QPushButton#questionsNewHeroButton:hover {
        background-color: #eff6ff;
        border-color: #60a5fa;
    }

    QPushButton#questionsSolveButton {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #1d4ed8;
        border-radius: 7px;
        padding: 6px 11px;
        font-weight: 800;
    }

    QPushButton#questionsSolveButton:hover {
        background-color: #1d4ed8;
    }

    QPushButton#questionsSolveButton:disabled {
        background-color: #e2e8f0;
        color: #94a3b8;
        border-color: #cbd5e1;
    }

    QLabel#questionSmartStrategy {
        background-color: #eff6ff;
        color: #1e3a8a;
        border: 1px solid #bfdbfe;
        border-radius: 7px;
        padding: 8px 10px;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QPushButton#smartReviewDashboardButton {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #1d4ed8;
        border-radius: 8px;
        padding: 7px 12px;
        font-weight: 800;
    }

    QPushButton#smartReviewDashboardButton:hover {
        background-color: #1d4ed8;
        border-color: #1e40af;
    }

    QPushButton#smartReviewDashboardButton:disabled {
        background-color: #e2e8f0;
        color: #94a3b8;
        border-color: #cbd5e1;
    }

    QFrame#adaptiveSessionConfigCard,
    QFrame#adaptiveTopicsCard,
    QFrame#adaptivePreviewCard {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 10px;
    }

    QFrame#adaptiveSessionConfigCard QLabel,
    QFrame#adaptiveTopicsCard QLabel,
    QFrame#adaptivePreviewCard QLabel {
        background: transparent;
    }

    QLabel#adaptiveSectionTitle {
        color: #111827;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#adaptivePreviewSummary {
        color: #1d4ed8;
        font-size: 9pt;
        font-weight: 800;
    }

    QLabel#adaptivePreviewReasons {
        color: #334155;
        font-size: 8.6pt;
        font-weight: 600;
    }

    QLabel#adaptivePreviewNotice {
        background-color: #eff6ff;
        color: #1e40af;
        border: 1px solid #bfdbfe;
        border-radius: 7px;
        padding: 6px 8px;
        font-size: 8.2pt;
    }

    QPushButton#adaptiveSessionStartButton,
    QPushButton#adaptiveDashboardButton,
    QPushButton#questionsAdaptiveButton {
        background-color: #1d4ed8;
        color: #ffffff;
        border: 1px solid #1d4ed8;
        border-radius: 8px;
        padding: 7px 12px;
        font-weight: 800;
    }

    QPushButton#adaptiveSessionStartButton:hover,
    QPushButton#adaptiveDashboardButton:hover,
    QPushButton#questionsAdaptiveButton:hover {
        background-color: #1e40af;
        border-color: #1e40af;
    }

    QFrame#questionsAdaptiveBar {
        background-color: #f8fbff;
        border: 1px solid #bfdbfe;
        border-radius: 9px;
    }

    QFrame#questionsAdaptiveBar QLabel {
        background: transparent;
    }

    QLabel#questionsAdaptiveTitle {
        color: #1e3a8a;
        font-size: 9.5pt;
        font-weight: 800;
    }

    QLabel#questionsAdaptiveDescription {
        color: #64748b;
        font-size: 8.4pt;
    }

    QFrame#adaptiveSummaryCard {
        background-color: #f8fbff;
        border: 1px solid #bfdbfe;
        border-radius: 9px;
    }

    QFrame#adaptiveSummaryCard QLabel {
        background: transparent;
    }

    QLabel#adaptiveSummaryTitle {
        color: #1e3a8a;
        font-size: 9.5pt;
        font-weight: 800;
    }

    QLabel#adaptiveSummaryText {
        color: #334155;
        font-size: 8.5pt;
    }

    QFrame#effectivenessFilterBar {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 9px;
    }

    QFrame#effectivenessFilterBar QLabel {
        background: transparent;
        color: #475569;
    }

    QLabel#effectivenessTrackingNotice {
        color: #64748b;
        font-size: 8.2pt;
    }

    QFrame#effectivenessStatCard {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 9px;
    }

    QFrame#effectivenessStatCard QLabel {
        background: transparent;
    }

    QLabel#effectivenessStatLabel {
        color: #64748b;
        font-size: 8.6pt;
        font-weight: 700;
    }

    QLabel#effectivenessStatValue {
        color: #111827;
        font-size: 16px;
        font-weight: 900;
    }

    QLabel#effectivenessStatHint {
        color: #94a3b8;
        font-size: 8pt;
    }

    QFrame#effectivenessCalibrationCard {
        background-color: #f8fbff;
        border: 1px solid #bfdbfe;
        border-radius: 9px;
    }

    QFrame#effectivenessCalibrationCard QLabel {
        background: transparent;
    }

    QLabel#effectivenessCalibrationTitle {
        color: #1e3a8a;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#effectivenessCalibrationBadge {
        background-color: #f1f5f9;
        color: #475569;
        border: 1px solid #cbd5e1;
        border-radius: 7px;
        padding: 4px 8px;
        font-size: 8.3pt;
        font-weight: 800;
    }

    QLabel#effectivenessCalibrationBadge[calibrationLevel="inicial"],
    QLabel#effectivenessCalibrationBadge[calibrationLevel="moderada"] {
        background-color: #fffbeb;
        color: #92400e;
        border-color: #fde68a;
    }

    QLabel#effectivenessCalibrationBadge[calibrationLevel="forte"] {
        background-color: #f0fdf4;
        color: #166534;
        border-color: #86efac;
    }

    QLabel#effectivenessCalibrationText {
        color: #334155;
        font-size: 8.6pt;
    }

    QLabel#effectivenessWeights {
        color: #1e40af;
        font-size: 8.4pt;
        font-weight: 700;
    }

    QLabel#effectivenessObservations {
        color: #64748b;
        font-size: 8.4pt;
    }

    QFrame#effectivenessImpactCard {
        background-color: #f8fbff;
        border: 1px solid #bfdbfe;
        border-radius: 9px;
    }

    QFrame#effectivenessImpactCard QLabel {
        background: transparent;
    }

    QLabel#effectivenessImpactTitle {
        color: #1e3a8a;
        font-size: 9.5pt;
        font-weight: 800;
    }

    QFrame#effectivenessImpactMetric {
        background-color: #ffffff;
        border: 1px solid #dbeafe;
        border-radius: 7px;
    }

    QLabel#effectivenessImpactLabel {
        color: #64748b;
        font-size: 8pt;
    }

    QLabel#effectivenessImpactValue {
        color: #111827;
        font-size: 9.5pt;
        font-weight: 800;
    }

    QLabel#effectivenessImpactFooter {
        color: #64748b;
        font-size: 8.2pt;
    }

    QPushButton#effectivenessOpenButton,
    QPushButton#questionsEffectivenessButton {
        background-color: #ffffff;
        color: #1d4ed8;
        border: 1px solid #93c5fd;
        border-radius: 7px;
        padding: 6px 10px;
        font-weight: 700;
    }

    QPushButton#effectivenessOpenButton:hover,
    QPushButton#questionsEffectivenessButton:hover {
        background-color: #eff6ff;
        border-color: #60a5fa;
    }

    QFrame#mockExamConfigCard {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 10px;
    }

    QFrame#mockExamConfigCard QLabel {
        background: transparent;
        color: #334155;
    }

    QLabel#mockExamRuleNotice {
        background-color: #fffbeb;
        color: #92400e;
        border: 1px solid #fde68a;
        border-radius: 8px;
        padding: 7px 9px;
        font-size: 8.4pt;
        font-weight: 600;
    }

    QLabel#mockExamSectionTitle {
        color: #111827;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#mockExamPreviewSummary {
        color: #1d4ed8;
        font-size: 9pt;
        font-weight: 800;
    }

    QLabel#mockExamVighnaExplanation {
        color: #64748b;
        font-size: 8.4pt;
    }

    QPushButton#mockExamStartButton,
    QPushButton#mockExamDashboardButton {
        background-color: #7c3aed;
        color: #ffffff;
        border: 1px solid #6d28d9;
        border-radius: 8px;
        padding: 7px 12px;
        font-weight: 800;
    }

    QPushButton#mockExamStartButton:hover,
    QPushButton#mockExamDashboardButton:hover {
        background-color: #6d28d9;
        border-color: #5b21b6;
    }

    QPushButton#questionsMockExamButton {
        background-color: #ffffff;
        color: #6d28d9;
        border: 1px solid #c4b5fd;
        border-radius: 7px;
        padding: 6px 10px;
        font-weight: 800;
    }

    QPushButton#questionsMockExamButton:hover {
        background-color: #f5f3ff;
        border-color: #a78bfa;
    }

    QLabel#mockExamTimer {
        background-color: #f5f3ff;
        color: #6d28d9;
        border: 1px solid #c4b5fd;
        border-radius: 7px;
        padding: 5px 8px;
        font-size: 9pt;
        font-weight: 900;
    }

    QLabel#mockExamResultSectionTitle {
        color: #111827;
        font-size: 9.5pt;
        font-weight: 800;
    }

    QLabel#mockExamCorrectionNotice {
        background-color: #f5f3ff;
        color: #5b21b6;
        border: 1px solid #c4b5fd;
        border-radius: 8px;
        padding: 7px 9px;
        font-size: 8.4pt;
        font-weight: 600;
    }

    QFrame#questionSessionConfigCard,
    QFrame#questionSessionSummaryCard {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 9px;
    }

    QLabel#questionSessionProfile,
    QLabel#questionSessionAvailability {
        background-color: #f8fafc;
        color: #475569;
        border: 1px solid #e2e8f0;
        border-radius: 7px;
        padding: 7px 9px;
        font-weight: 700;
    }

    QLabel#questionSessionAvailability[availabilityState="ok"] {
        background-color: #f0fdf4;
        color: #15803d;
        border-color: #bbf7d0;
    }

    QLabel#questionSessionAvailability[availabilityState="empty"] {
        background-color: #fff7ed;
        color: #c2410c;
        border-color: #fed7aa;
    }

    QLabel#questionSessionProgressText {
        color: #334155;
        font-weight: 800;
    }

    QProgressBar#questionSessionProgress {
        background-color: #e2e8f0;
        border: none;
        border-radius: 3px;
    }

    QProgressBar#questionSessionProgress::chunk {
        background-color: #3b82f6;
        border-radius: 3px;
    }

    QFrame#questionSessionMiniStat {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 7px;
    }

    QLabel#questionSessionMiniLabel {
        color: #64748b;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#questionSessionMiniValue {
        color: #111827;
        font-size: 10pt;
        font-weight: 800;
    }

    QPushButton#questionSessionEndButton {
        background-color: #ffffff;
        color: #b91c1c;
        border: 1px solid #fecaca;
        border-radius: 7px;
        padding: 6px 10px;
        font-weight: 700;
    }

    QPushButton#questionSessionEndButton:hover {
        background-color: #fef2f2;
    }

    QPushButton#questionSessionSkipButton {
        background-color: #ffffff;
        color: #475569;
        border: 1px solid #cbd5e1;
        border-radius: 7px;
        padding: 6px 12px;
        font-weight: 700;
    }

    QPushButton#questionSessionSkipButton:hover {
        background-color: #f8fafc;
    }

    QScrollArea#questionSolverScroll {
        background: transparent;
        border: none;
    }

    QWidget#questionSolverContent {
        background: transparent;
    }

    QLabel#questionSolverMeta {
        color: #64748b;
        font-size: 9pt;
        font-weight: 700;
    }

    QFrame#questionSolverStatementCard {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 10px;
    }

    QLabel#questionSolverStatement {
        color: #111827;
        font-size: 11pt;
    }

    QFrame#questionSolverAlternative {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 9px;
    }

    QFrame#questionSolverAlternative[answerState="correta"] {
        background-color: #f0fdf4;
        border-color: #86efac;
    }

    QFrame#questionSolverAlternative[answerState="errada"] {
        background-color: #fef2f2;
        border-color: #fca5a5;
    }

    QRadioButton#questionSolverRadio {
        color: {{color:answer.indicator_text}};
        font-weight: 800;
        spacing: 5px;
    }

    QLabel#questionSolverAlternativeText {
        color: {{color:answer.normal_text}};
        font-size: 10pt;
    }

    QFrame#questionSolverAlternative[eliminated="true"][answerState="normal"] {
        background-color: #eef2f6;
        border: 1px dashed #94a3b8;
    }

    QLabel#questionSolverAlternativeText[eliminated="true"],
    QRadioButton#questionSolverRadio[eliminated="true"] {
        color: #64748b;
    }

    QToolButton#questionSolverEliminateButton:checked {
        background-color: #e2e8f0;
        color: #475569;
        border: 1px solid #94a3b8;
    }

    QToolButton#questionSolverEliminateButton {
        background: transparent;
        color: {{color:answer.eliminate_text}};
        border: none;
        border-radius: 5px;
        font-size: 11pt;
        padding: 0;
    }

    QToolButton#questionSolverEliminateButton:hover {
        background-color: {{color:answer.eliminate_hover_surface}};
        color: {{color:answer.eliminate_hover_text}};
    }

    QToolButton#questionSolverEliminateButton:checked {
        background-color: #e2e8f0;
        color: #334155;
    }

    QToolButton#questionSolverEliminateButton:disabled {
        color: {{color:answer.disabled_text}};
    }

    QCheckBox#questionSessionDoubt {
        background: transparent;
        color: #475569;
        font-weight: 700;
        spacing: 9px;
        padding: 4px 0;
    }

    QCheckBox#questionSessionDoubt:checked {
        color: #1d4ed8;
    }

    QCheckBox#questionSessionDoubt::indicator {
        background-color: #ffffff;
        border: 2px solid #64748b;
        border-radius: 5px;
        width: 20px;
        height: 20px;
    }

    QCheckBox#questionSessionDoubt::indicator:hover {
        border-color: #2563eb;
    }

    QCheckBox#questionSessionDoubt::indicator:checked {
        background-color: #2563eb;
        border-color: #1d4ed8;
    }

    QCheckBox#questionSessionDoubt::indicator:disabled {
        background-color: #e2e8f0;
        border-color: #94a3b8;
    }

    QCheckBox#questionSessionAnalysisFlag {
        background: transparent;
        color: #64748b;
        font-weight: 600;
        spacing: 7px;
        padding: 4px 8px;
    }

    QCheckBox#questionSessionAnalysisFlag:checked {
        color: #92400e;
        font-weight: 700;
    }

    QCheckBox#questionSessionAnalysisFlag::indicator {
        background-color: #ffffff;
        border: 2px solid #94a3b8;
        border-radius: 4px;
        width: 16px;
        height: 16px;
    }

    QCheckBox#questionSessionAnalysisFlag::indicator:hover {
        border-color: #d97706;
    }

    QCheckBox#questionSessionAnalysisFlag::indicator:checked {
        background-color: #f59e0b;
        border-color: #b45309;
    }

    QFrame#questionSessionActionPanel {
        background: transparent;
        border: none;
    }

    QFrame#questionSolverFeedback {
        background-color: {{color:answer.explanation_surface}};
        border: 1px solid {{color:answer.explanation_border}};
        border-radius: 9px;
    }

    QFrame#questionSolverFeedback[resultState="correta"] {
        background-color: #f0fdf4;
        border-color: #86efac;
    }

    QFrame#questionSolverFeedback[resultState="errada"] {
        background-color: #fef2f2;
        border-color: #fca5a5;
    }

    QLabel#questionSolverFeedbackTitle {
        color: #111827;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#questionSolverExplanation {
        color: {{color:answer.explanation_text}};
        font-size: 9.5pt;
    }

    QLabel#questionSessionSummaryDetail {
        background-color: #eff6ff;
        color: #1e3a8a;
        border: 1px solid #bfdbfe;
        border-radius: 7px;
        padding: 7px 9px;
        font-weight: 700;
    }

    QTableWidget#questionSessionSummaryTable {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QPushButton#questionsNavButton {
        background-color: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        border-radius: 7px;
        padding: 6px 9px;
        font-weight: 800;
    }

    QPushButton#questionsNavButton:hover {
        background-color: #dbeafe;
        border-color: #93c5fd;
    }

    QFrame#questionsFoundationNotice {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
    }

    QLabel#questionsFoundationText {
        background: transparent;
        color: #1e3a8a;
        font-size: 9pt;
        font-weight: 600;
    }

    QFrame#questionsFilterBar {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 9px;
    }

    QTableWidget#questionsTable {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 9px;
        gridline-color: transparent;
        font-size: 9pt;
    }

    QTableWidget#questionsTable QHeaderView::section {
        padding-left: 6px;
        padding-right: 6px;
    }

    QTabWidget#promptLibraryTabs::pane {
        border: 1px solid #dbe3ed;
        border-radius: 9px;
        background-color: #f8fafc;
        top: -1px;
    }

    QTabWidget#promptLibraryTabs QTabBar::tab {
        background-color: #eef2f7;
        color: #64748b;
        border: 1px solid #dbe3ed;
        border-bottom: none;
        padding: 8px 15px;
        margin-right: 3px;
        font-weight: 700;
    }

    QTabWidget#promptLibraryTabs QTabBar::tab:selected {
        background-color: #ffffff;
        color: #1d4ed8;
    }

    QLabel#promptProtocolIntro {
        background-color: #eff6ff;
        color: #1e40af;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 8.5pt;
        font-weight: 600;
    }

    QFrame#promptProtocolCard {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 10px;
    }

    QLabel#promptProtocolTitle {
        color: #111827;
        font-size: 11pt;
        font-weight: 800;
    }

    QLabel#promptProtocolDescription {
        color: #64748b;
        font-size: 8.7pt;
    }

    QLabel#promptProtocolBadge {
        background-color: #ecfdf5;
        color: #047857;
        border: 1px solid #a7f3d0;
        border-radius: 6px;
        padding: 4px 8px;
        font-size: 7.8pt;
        font-weight: 800;
    }

    QLabel#promptProtocolUsage {
        background-color: #fff7ed;
        color: #9a3412;
        border: 1px solid #fed7aa;
        border-radius: 7px;
        padding: 7px 9px;
        font-size: 8.5pt;
    }

    QTextEdit#promptProtocolEditor {
        background-color: #f8fafc;
        color: #1f2937;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 9px;
        font-family: Consolas;
        font-size: 9pt;
    }

    QPushButton#promptProtocolCopyButton {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #1d4ed8;
        border-radius: 7px;
        padding: 7px 12px;
        font-weight: 800;
    }

    QPushButton#promptProtocolCopyButton:hover {
        background-color: #1d4ed8;
    }

    QPushButton#promptProtocolDuplicateButton {
        background-color: #ffffff;
        color: #475569;
        border: 1px solid #cbd5e1;
        border-radius: 7px;
        padding: 7px 12px;
        font-weight: 700;
    }

    QPushButton#promptProtocolDuplicateButton:hover {
        background-color: #f8fafc;
        border-color: #94a3b8;
    }

    QLabel#promptProtocolStatus {
        color: #64748b;
        font-size: 8.2pt;
        font-weight: 600;
    }

    QPushButton#questionsPromptsButton {
        background-color: #fff7ed;
        color: #9a3412;
        border: 1px solid #fed7aa;
        border-radius: 7px;
        padding: 6px 11px;
        font-weight: 800;
    }

    QPushButton#questionsPromptsButton:hover {
        background-color: #ffedd5;
        border-color: #fdba74;
    }

    QLabel#promptLibraryHint {
        background-color: #f8fafc;
        color: #64748b;
        border: 1px solid #e2e8f0;
        border-radius: 7px;
        padding: 7px 9px;
        font-size: 8.5pt;
    }

    QFrame#promptLibraryFilter,
    QFrame#promptLibraryListCard,
    QFrame#promptLibraryEditorCard {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 9px;
    }

    QLabel#promptLibrarySectionTitle {
        color: #111827;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#promptLibraryTextLabel {
        color: #334155;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#promptLibraryStatus {
        color: #64748b;
        font-size: 8.5pt;
        font-weight: 600;
    }

    QTableWidget#promptLibraryTable {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QTextEdit#promptLibraryEditor {
        background-color: #ffffff;
        color: #111827;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 8px;
        font-family: Consolas;
        font-size: 9pt;
    }

    QPushButton#promptNewButton {
        background-color: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        border-radius: 7px;
        padding: 6px 9px;
        font-weight: 800;
    }

    QPushButton#promptNewButton:hover {
        background-color: #dbeafe;
        border-color: #93c5fd;
    }

    QPushButton#promptCopyButton {
        background-color: #fff7ed;
        color: #9a3412;
        border: 1px solid #fdba74;
        border-radius: 7px;
        padding: 7px 11px;
        font-weight: 800;
    }

    QPushButton#promptCopyButton:hover {
        background-color: #ffedd5;
    }

    QPushButton#questionsPdfImportButton {
        background-color: #faf5ff;
        color: #7e22ce;
        border: 1px solid #e9d5ff;
        border-radius: 7px;
        padding: 6px 11px;
        font-weight: 800;
    }

    QPushButton#questionsPdfImportButton:hover {
        background-color: #f3e8ff;
        border-color: #d8b4fe;
    }

    QFrame#vpqImportStatus {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 9px;
    }

    QFrame#vpqImportStatus[vpqState="integro"] {
        background-color: #f0fdf4;
        border-color: #86efac;
    }

    QFrame#vpqImportStatus[vpqState="aviso"] {
        background-color: #fffbeb;
        border-color: #fde68a;
    }

    QFrame#vpqImportStatus[vpqState="revisao"] {
        background-color: #fef2f2;
        border-color: #fecaca;
    }

    QLabel#vpqImportBadge {
        background-color: #1d4ed8;
        color: #ffffff;
        border-radius: 6px;
        padding: 4px 8px;
        font-size: 8pt;
        font-weight: 800;
    }

    QLabel#vpqImportResult {
        color: #334155;
        font-size: 9pt;
        font-weight: 800;
    }

    QLabel#vpqImportResult[vpqState="integro"] {
        color: #15803d;
    }

    QLabel#vpqImportResult[vpqState="aviso"] {
        color: #a16207;
    }

    QLabel#vpqImportResult[vpqState="revisao"] {
        color: #b91c1c;
    }

    QLabel#vpqImportMeta {
        color: #334155;
        font-size: 8.7pt;
        font-weight: 700;
    }

    QLabel#vpqImportLink {
        color: #475569;
        font-size: 8.5pt;
        font-weight: 600;
    }

    QLabel#vpqImportLink[linkState="ok"] {
        color: #15803d;
    }

    QLabel#vpqImportLink[linkState="warning"] {
        color: #a16207;
    }

    QLabel#vpqImportDetails {
        color: #475569;
        font-size: 8.4pt;
    }

    QFrame#pdfImportSummary,
    QFrame#pdfImportDefaults {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 9px;
    }

    QLabel#pdfImportFile {
        color: #111827;
        font-weight: 800;
    }

    QLabel#pdfImportMeta {
        color: #64748b;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#pdfImportHint {
        background-color: #f8fafc;
        color: #64748b;
        border: 1px solid #e2e8f0;
        border-radius: 7px;
        padding: 7px 9px;
        font-size: 8.5pt;
    }

    QTableWidget#pdfImportTable {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QComboBox#pdfTopicCombo,
    QComboBox#pdfAnswerCombo {
        min-height: 27px;
    }

    QTextEdit#pdfExtractedText {
        font-family: Consolas;
        font-size: 9pt;
    }

    QTextEdit#textQuestionImportEditor {
        background-color: #ffffff;
        color: #172033;
        border: 1px solid #dbe3ed;
        border-radius: 9px;
        padding: 10px;
        font-family: Consolas;
        font-size: 9pt;
        selection-background-color: #dbeafe;
    }

    QTextEdit#textQuestionImportEditor:focus {
        border: 1px solid #7aa7df;
    }

    QPushButton#questionsImportButton {
        background-color: #f0fdf4;
        color: #15803d;
        border: 1px solid #bbf7d0;
        border-radius: 7px;
        padding: 6px 9px;
        font-weight: 800;
    }

    QPushButton#questionsImportButton:hover {
        background-color: #dcfce7;
        border-color: #86efac;
    }

    QLabel#questionIntegrityNotice {
        background-color: #eff6ff;
        color: #1e40af;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 8.7pt;
        font-weight: 600;
    }

    QLabel#questionSnapshotNotice {
        background-color: #f0fdf4;
        color: #166534;
        border: 1px solid #86efac;
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 8.7pt;
        font-weight: 600;
    }

    QLabel#questionSnapshotNotice[snapshotState="legado"] {
        background-color: #fffbeb;
        color: #92400e;
        border-color: #fde68a;
    }

    QLabel#questionArchivedNotice {
        background-color: #f8fafc;
        color: #64748b;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 8.7pt;
        font-weight: 600;
    }

    QScrollArea#questionEditorScroll,
    QScrollArea#questionViewerScroll {
        background: transparent;
        border: none;
    }

    QWidget#questionEditorContent {
        background: transparent;
    }

    QFrame#questionEditorCard,
    QFrame#questionViewerCard,
    QFrame#questionAlternative,
    QFrame#questionExplanationCard {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 9px;
    }

    QFrame#questionCorrectAlternative {
        background-color: #f0fdf4;
        border: 1px solid #86efac;
        border-radius: 9px;
    }

    QLabel#questionEditorSectionTitle {
        color: #111827;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#questionAlternativeLetter {
        color: #334155;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#questionAlternativeText {
        background: transparent;
        color: #1f2937;
        font-size: 10pt;
    }

    QLabel#questionViewerMeta,
    QLabel#questionViewerPath,
    QLabel#questionViewerSource {
        color: #64748b;
        font-size: 9pt;
        font-weight: 600;
    }

    QLabel#questionViewerStatement {
        color: #111827;
        font-size: 10.5pt;
    }

    QLabel#questionCorrectBadge {
        background-color: #dcfce7;
        color: #15803d;
        border: 1px solid #86efac;
        border-radius: 7px;
        padding: 3px 7px;
        font-size: 8pt;
        font-weight: 800;
    }

    QFrame#syllabusForecastStrip {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
    }

    QFrame#syllabusForecastStrip QLabel {
        background: transparent;
    }

    QLabel#syllabusForecastIcon {
        color: #2563eb;
        font-size: 14pt;
        font-weight: 800;
    }

    QLabel#syllabusForecastText {
        color: #1e3a8a;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#syllabusForecastSummary {
        color: #475569;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QPushButton#syllabusForecastButton {
        background-color: #ffffff;
        color: #1d4ed8;
        border: 1px solid #93c5fd;
        border-radius: 7px;
        padding: 5px 10px;
        font-weight: 700;
    }

    QPushButton#syllabusForecastButton:hover {
        background-color: #dbeafe;
        border-color: #60a5fa;
    }

    QFrame#syllabusForecastCard {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 10px;
    }

    QFrame#syllabusForecastCard QLabel,
    QFrame#syllabusForecastMetricCard QLabel {
        background: transparent;
    }

    QFrame#syllabusForecastMetricCard {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 9px;
    }

    QLabel#syllabusForecastMetricTitle {
        color: #334155;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#syllabusForecastBigValue {
        color: #111827;
        font-size: 18px;
        font-weight: 800;
    }

    QLabel#syllabusForecastDetail {
        color: #64748b;
        font-size: 8.5pt;
    }

    QLabel#syllabusForecastDate {
        color: #1d4ed8;
        font-size: 9pt;
        font-weight: 800;
    }

    QLabel#syllabusForecastStatus,
    QLabel#syllabusForecastBase {
        background-color: #f1f5f9;
        color: #475569;
        border: 1px solid #e2e8f0;
        border-radius: 7px;
        padding: 5px 8px;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#syllabusForecastStatus[forecastState="boa"],
    QLabel#syllabusForecastBase[forecastState="boa"] {
        background-color: #f0fdf4;
        color: #15803d;
        border-color: #bbf7d0;
    }

    QLabel#syllabusForecastStatus[forecastState="moderada"],
    QLabel#syllabusForecastBase[forecastState="moderada"] {
        background-color: #fffbeb;
        color: #a16207;
        border-color: #fde68a;
    }

    QLabel#syllabusForecastStatus[forecastState="limitada"],
    QLabel#syllabusForecastBase[forecastState="limitada"] {
        background-color: #fff7ed;
        color: #c2410c;
        border-color: #fed7aa;
    }

    QLabel#syllabusForecastStatus[forecastState="insuficiente"],
    QLabel#syllabusForecastBase[forecastState="insuficiente"] {
        background-color: #f8fafc;
        color: #64748b;
        border-color: #cbd5e1;
    }

    QProgressBar#syllabusForecastProgress {
        background-color: #e2e8f0;
        border: none;
        border-radius: 4px;
    }

    QProgressBar#syllabusForecastProgress::chunk {
        background-color: #3b82f6;
        border-radius: 4px;
    }

    QTableWidget#syllabusForecastTable {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QLabel#syllabusForecastNote {
        background-color: #f8fafc;
        color: #64748b;
        border: 1px solid #e2e8f0;
        border-radius: 7px;
        padding: 8px 9px;
        font-size: 8.5pt;
    }

    QFrame#syllabusAlertStrip {
        background-color: #f8fafc;
        border: 1px solid #dbe3ed;
        border-radius: 8px;
    }

    QFrame#syllabusAlertStrip[alertState="ok"] {
        background-color: #f0fdf4;
        border-color: #bbf7d0;
    }

    QFrame#syllabusAlertStrip[alertState="monitorar"] {
        background-color: #fffbeb;
        border-color: #fde68a;
    }

    QFrame#syllabusAlertStrip[alertState="atencao"] {
        background-color: #fff7ed;
        border-color: #fed7aa;
    }

    QFrame#syllabusAlertStrip[alertState="critico"] {
        background-color: #fef2f2;
        border-color: #fecaca;
    }

    QFrame#syllabusAlertStrip QLabel {
        background: transparent;
    }

    QLabel#syllabusAlertIcon {
        color: #b45309;
        font-size: 14pt;
        font-weight: 800;
    }

    QLabel#syllabusAlertText {
        color: #334155;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#syllabusAlertSummary {
        color: #64748b;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QPushButton#syllabusAlertButton {
        background-color: #ffffff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        border-radius: 7px;
        padding: 5px 10px;
        font-weight: 700;
    }

    QPushButton#syllabusAlertButton:hover {
        background-color: #eff6ff;
        border-color: #93c5fd;
    }

    QPushButton#syllabusAlertButton:disabled {
        background-color: #f8fafc;
        color: #94a3b8;
        border-color: #e2e8f0;
    }

    QFrame#syllabusAlertsCard {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 10px;
    }

    QFrame#syllabusAlertsCard QLabel,
    QFrame#syllabusAlertStat QLabel {
        background: transparent;
    }

    QFrame#syllabusAlertStat {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }

    QFrame#syllabusAlertStat[alertLevel="critico"] {
        background-color: #fef2f2;
        border-color: #fecaca;
    }

    QFrame#syllabusAlertStat[alertLevel="atencao"] {
        background-color: #fff7ed;
        border-color: #fed7aa;
    }

    QFrame#syllabusAlertStat[alertLevel="monitorar"] {
        background-color: #fffbeb;
        border-color: #fde68a;
    }

    QLabel#syllabusAlertsEmpty {
        background-color: #f8fafc;
        color: #64748b;
        border: 1px dashed #cbd5e1;
        border-radius: 8px;
        padding: 12px;
        font-size: 9pt;
    }

    QLabel#syllabusAlertsRule {
        background-color: #f8fafc;
        color: #64748b;
        border: 1px solid #e2e8f0;
        border-radius: 7px;
        padding: 7px 9px;
        font-size: 8.5pt;
    }

    QTableWidget#syllabusAlertsTable {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QScrollArea#syllabusProgressScroll {
        background: transparent;
        border: none;
    }

    QWidget#syllabusProgressContent {
        background: transparent;
    }

    QFrame#syllabusStat,
    QFrame#syllabusRules,
    QFrame#syllabusDisciplineCard,
    QFrame#syllabusTopicsCard {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 10px;
    }

    QFrame#syllabusStat QLabel,
    QFrame#syllabusRules QLabel,
    QFrame#syllabusDisciplineCard QLabel,
    QFrame#syllabusTopicsCard QLabel {
        background: transparent;
    }

    QLabel#syllabusStatHint {
        color: #64748b;
        font-size: 8pt;
    }

    QLabel#syllabusSectionTitle {
        color: #111827;
        font-size: 11pt;
        font-weight: 800;
    }

    QTableWidget#syllabusDisciplineTable,
    QTableWidget#syllabusTopicsTable {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QProgressBar#syllabusCoverageBar {
        background-color: #e2e8f0;
        color: #334155;
        border: none;
        border-radius: 6px;
        font-size: 8pt;
        font-weight: 700;
        text-align: center;
    }

    QProgressBar#syllabusCoverageBar::chunk {
        background-color: #60a5fa;
        border-radius: 6px;
    }

    QScrollArea#evolutionScroll {
        background: transparent;
        border: none;
    }

    QWidget#evolutionContent {
        background: transparent;
    }

    QFrame#evolutionFilterBar {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 10px;
    }

    QLabel#evolutionPeriodBadge {
        background-color: #f1f5f9;
        color: #475569;
        border: 1px solid #e2e8f0;
        border-radius: 7px;
        padding: 5px 8px;
        font-size: 9pt;
        font-weight: 600;
    }

    QFrame#evolutionStat,
    QFrame#evolutionChartCard,
    QFrame#evolutionDisciplineCard {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 10px;
    }

    QFrame#evolutionStat QLabel,
    QFrame#evolutionChartCard QLabel,
    QFrame#evolutionDisciplineCard QLabel {
        background: transparent;
    }

    QLabel#evolutionSectionTitle {
        color: #111827;
        font-size: 15px;
        font-weight: 700;
    }

    QLabel#evolutionTrend {
        color: #64748b;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#evolutionTrend[trendState="positiva"] {
        color: #15803d;
    }

    QLabel#evolutionTrend[trendState="negativa"] {
        color: #b91c1c;
    }

    QTableWidget#evolutionDisciplineTable {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QTabWidget#statisticsTabs QTabBar {
        background-color: #dfe8f3;
        border: 1px solid #c7d2e0;
        border-radius: 10px;
        padding: 4px;
    }

    QTabWidget#statisticsTabs QTabBar::tab {
        background-color: #f8fafc;
        color: #334155;
        border: 1px solid #d7e0ea;
        border-radius: 8px;
        padding: 10px 18px;
        min-height: 25px;
        min-width: 96px;
        font-size: 10pt;
        font-weight: 700;
        margin-right: 4px;
    }

    QTabWidget#statisticsTabs QTabBar::tab:hover {
        background-color: #eaf2ff;
        color: #1d4ed8;
        border-color: #93c5fd;
    }

    QTabWidget#statisticsTabs QTabBar::tab:selected {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #1d4ed8;
        font-weight: 800;
    }

    QTabWidget#statisticsTabs::pane {
        border: 1px solid #dbe3ed;
        border-radius: 10px;
        background-color: #ffffff;
        top: -1px;
    }


    QLabel#reportPeriodLabel {
        background-color: #f1f5f9;
        color: #475569;
        border: 1px solid #e2e8f0;
        border-radius: 7px;
        padding: 5px 9px;
        font-size: 9pt;
        font-weight: 600;
    }

    QFrame#comparisonPanel {
        background-color: #f8fafc;
        border: 1px solid #dbe3ed;
        border-radius: 11px;
    }

    QFrame#comparisonPanel QLabel {
        background: transparent;
    }

    QFrame#comparisonMetric {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 9px;
    }

    QLabel#comparisonValue {
        background: transparent;
        color: #475569;
        font-size: 13pt;
        font-weight: 800;
    }

    QLabel#comparisonValue[reportTrend="positive"] {
        color: #15803d;
    }

    QLabel#comparisonValue[reportTrend="negative"] {
        color: #b91c1c;
    }

    QLabel#comparisonValue[reportTrend="neutral"] {
        color: #64748b;
    }

    QTabWidget#reportTabs::pane {
        border: 1px solid #dbe3ed;
        border-radius: 10px;
        background-color: #ffffff;
        top: -1px;
    }


    QFrame#settingsSearchBar {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 10px;
    }

    QLineEdit#settingsSearchInput {
        background-color: #f8fafc;
        border-color: #e2e8f0;
    }

    QLabel#settingsSearchCount {
        background-color: #f1f5f9;
        color: #64748b;
        border: 1px solid #e2e8f0;
        border-radius: 7px;
        padding: 5px 8px;
        font-size: 9pt;
        font-weight: 600;
    }

    QFrame#settingsSection {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 11px;
    }

    QFrame#settingsSection QLabel {
        background: transparent;
    }

    QLabel#settingsSectionTitle {
        color: #111827;
        font-size: 15px;
        font-weight: 700;
    }

    QLabel#settingsSectionDescription {
        color: #64748b;
        font-size: 9pt;
    }

    QFrame#settingsOption {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 9px;
    }

    QFrame#settingsOption QLabel,
    QFrame#settingsOption QCheckBox {
        background: transparent;
    }

    QLabel#configOptionTitle {
        color: #1f2937;
        font-size: 10pt;
        font-weight: 700;
    }

    QCheckBox#configMainCheck {
        color: #1f2937;
        font-weight: 700;
    }

    QFrame#settingsFooter {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 10px;
    }

    QFrame#settingsFooter QLabel {
        background: transparent;
    }

    QLabel#settingsEmptyState {
        background-color: #ffffff;
        color: #64748b;
        border: 1px dashed #cbd5e1;
        border-radius: 10px;
        padding: 20px;
        font-size: 10pt;
    }

    QFrame#cardResumo {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
    }

    QPushButton#planningRedistributeButton {
        min-height: 0px;
        background-color: #fff7ed;
        color: #9a3412;
        border: 1px solid #fed7aa;
        border-radius: 7px;
        padding: 4px 10px;
        font-size: 9pt;
        font-weight: 700;
    }

    QPushButton#planningRedistributeButton:hover {
        background-color: #ffedd5;
        border-color: #fdba74;
        color: #7c2d12;
    }

    QPushButton#planningRedistributeButton[hasSuggestion="true"] {
        background-color: #ffedd5;
        border-color: #fb923c;
        color: #9a3412;
        font-weight: 800;
    }

    QFrame#redistributionStat {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 9px;
    }

    QFrame#redistributionStat QLabel {
        background: transparent;
    }

    QLabel#redistributionNotice {
        background-color: #fff7ed;
        color: #9a3412;
        border: 1px solid #fed7aa;
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 9pt;
    }

    QLabel#redistributionEmpty {
        background-color: #f8fafc;
        color: #64748b;
        border: 1px dashed #cbd5e1;
        border-radius: 9px;
        padding: 18px;
    }

    QTableWidget#redistributionTable {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QPushButton#planningSummaryButton {
        min-height: 0px;
        background-color: #f8fafc;
        color: #334155;
        border: 1px solid #cbd5e1;
        border-radius: 7px;
        padding: 4px 10px;
        font-size: 9pt;
        font-weight: 700;
    }

    QPushButton#planningSummaryButton:hover {
        background-color: #f1f5f9;
        border-color: #94a3b8;
        color: #0f172a;
    }

    QFrame#dailySummaryGoal,
    QFrame#dailySummaryComparison,
    QFrame#dailySummaryTopics {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 11px;
    }

    QFrame#dailySummaryGoal QLabel,
    QFrame#dailySummaryComparison QLabel,
    QFrame#dailySummaryTopics QLabel {
        background: transparent;
    }

    QLabel#dailySummarySectionTitle {
        color: #111827;
        font-size: 15px;
        font-weight: 700;
    }

    QLabel#dailySummaryGoalValue {
        color: #111827;
        font-size: 11pt;
        font-weight: 700;
    }

    QLabel#dailySummaryHint {
        color: #64748b;
        font-size: 9pt;
    }

    QLabel#dailySummaryHint[goalState="concluida"] {
        color: #15803d;
        font-weight: 700;
    }

    QProgressBar#dailySummaryProgress {
        background-color: #e2e8f0;
        border: none;
        border-radius: 4px;
    }

    QProgressBar#dailySummaryProgress::chunk {
        background-color: #3b82f6;
        border-radius: 4px;
    }

    QProgressBar#dailySummaryProgress[goalState="concluida"]::chunk {
        background-color: #22c55e;
    }

    QFrame#dailySummaryCompareCard {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 9px;
    }

    QLabel#dailySummaryCompareValue {
        color: #111827;
        font-size: 13px;
        font-weight: 700;
    }

    QLabel#dailySummaryCompareAverage {
        color: #64748b;
        font-size: 9pt;
    }

    QLabel#dailySummaryTrend {
        color: #64748b;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#dailySummaryTrend[trendState="positiva"] {
        color: #15803d;
    }

    QLabel#dailySummaryTrend[trendState="negativa"] {
        color: #b91c1c;
    }

    QTableWidget#dailySummaryTable {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QFrame#studySessionStartCard,
    QFrame#sessionSummaryStat {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 10px;
    }

    QFrame#studySessionStartCard QLabel,
    QFrame#sessionSummaryStat QLabel {
        background: transparent;
    }

    QLabel#sessionSummaryObjective {
        background-color: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 7px 10px;
        font-size: 9.5pt;
        font-weight: 700;
    }

    QTableWidget#sessionSummaryTable {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QPushButton#studySessionPauseButton {
        background-color: #f8fafc;
        color: #475569;
        border: 1px solid #cbd5e1;
        border-radius: 7px;
        padding: 6px 12px;
        font-weight: 700;
    }

    QPushButton#studySessionPauseButton:hover {
        background-color: #eef2f7;
        color: #1f2937;
    }

    QPushButton#studySessionEndButton {
        background-color: #fff1f2;
        color: #be123c;
        border: 1px solid #fecdd3;
        border-radius: 7px;
        padding: 6px 12px;
        font-weight: 700;
    }

    QPushButton#studySessionEndButton:hover {
        background-color: #ffe4e6;
        border-color: #fda4af;
    }

    QPushButton#studySessionSkipButton {
        background-color: #fff7ed;
        color: #c2410c;
        border: 1px solid #fed7aa;
        border-radius: 7px;
        padding: 7px 12px;
        font-weight: 700;
    }

    QPushButton#studySessionSkipButton:hover {
        background-color: #ffedd5;
        border-color: #fdba74;
    }

    QFrame#studySessionCurrentCard,
    QFrame#studySessionQueueCard {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 11px;
    }

    QFrame#studySessionCurrentCard QLabel,
    QFrame#studySessionQueueCard QLabel {
        background: transparent;
    }

    QFrame#studySessionCurrentCard {
        border: 1px solid #bfdbfe;
        background-color: #f8fbff;
    }

    QLabel#studySessionEyebrow {
        color: #2563eb;
        font-size: 8.5pt;
        font-weight: 800;
    }

    QLabel#studySessionPosition {
        color: #64748b;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#studySessionDiscipline {
        color: #475569;
        font-size: 10pt;
        font-weight: 700;
    }

    QLabel#studySessionTopic {
        color: #111827;
        font-size: 20px;
        font-weight: 700;
    }

    QLabel#studySessionDetailValue {
        color: #1f2937;
        font-size: 10pt;
        font-weight: 700;
    }

    QLabel#studySessionSectionTitle {
        color: #111827;
        font-size: 15px;
        font-weight: 700;
    }

    QTableWidget#studySessionTable {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QFrame#planningPanel {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 11px;
    }

    QFrame#planningPanel QLabel {
        background: transparent;
    }

    QPushButton#planningGoalButton {
        min-height: 0px;
        background-color: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        border-radius: 7px;
        padding: 4px 10px;
        font-size: 9pt;
        font-weight: 700;
    }

    QPushButton#planningGoalButton:hover {
        background-color: #dbeafe;
        border-color: #93c5fd;
        color: #1e40af;
    }

    QScrollArea#planningSettingsScroll {
        background: transparent;
        border: none;
    }

    QWidget#planningSettingsContent {
        background: transparent;
    }

    QFrame#planningSettingsCard {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 10px;
    }

    QFrame#planningSettingsCard QLabel {
        background: transparent;
    }

    QLabel#planningSettingsTitle {
        color: #111827;
        font-size: 11pt;
        font-weight: 700;
    }

    QLabel#planningLoadLight {
        color: #15803d;
        font-weight: 700;
    }

    QLabel#planningLoadModerate {
        color: #a16207;
        font-weight: 700;
    }

    QLabel#planningLoadHigh {
        color: #b91c1c;
        font-weight: 700;
    }

    QLabel#planningTitle {
        color: #111827;
        font-size: 15px;
        font-weight: 700;
    }

    QLabel#planningTotalBadge {
        background-color: #f1f5f9;
        color: #475569;
        border: 1px solid #e2e8f0;
        border-radius: 7px;
        padding: 5px 9px;
        font-size: 9pt;
        font-weight: 700;
    }

    QFrame#weeklyGoalBox {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 9px;
    }

    QFrame#weeklyGoalBox QLabel,
    QFrame#weeklyGoalMetric QLabel {
        background: transparent;
    }

    QLabel#weeklyGoalTitle {
        color: #111827;
        font-size: 10pt;
        font-weight: 700;
    }

    QLabel#weeklyGoalPeriod {
        color: #64748b;
        font-size: 9pt;
        font-weight: 600;
    }

    QLabel#weeklyGoalStatus {
        background-color: #f1f5f9;
        color: #475569;
        border: 1px solid #e2e8f0;
        border-radius: 7px;
        padding: 4px 8px;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#weeklyGoalStatus[weekState="concluida"] {
        background-color: #dcfce7;
        color: #15803d;
        border-color: #bbf7d0;
    }

    QLabel#weeklyGoalStatus[weekState="atencao"] {
        background-color: #fff7ed;
        color: #c2410c;
        border-color: #fed7aa;
    }

    QFrame#weeklyGoalMetric {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }

    QLabel#weeklyGoalMetricTitle {
        color: #475569;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#weeklyGoalValue {
        color: #111827;
        font-size: 14px;
        font-weight: 700;
    }

    QLabel#weeklyGoalHint {
        color: #64748b;
        font-size: 8pt;
    }

    QLabel#weeklyGoalHint[goalState="concluida"] {
        color: #15803d;
        font-weight: 700;
    }

    QProgressBar#weeklyGoalProgress {
        background-color: #e2e8f0;
        border: none;
        border-radius: 4px;
    }

    QProgressBar#weeklyGoalProgress::chunk {
        background-color: #3b82f6;
        border-radius: 4px;
    }

    QProgressBar#weeklyGoalProgress[goalState="concluida"]::chunk {
        background-color: #22c55e;
    }

    QFrame#dailyGoalBox,
    QFrame#weeklyLoadBox {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 9px;
    }

    QLabel#planningItemTitle {
        color: #475569;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#dailyGoalValue {
        color: #111827;
        font-size: 17px;
        font-weight: 700;
    }

    QLabel#planningHint {
        color: #64748b;
        font-size: 8.5pt;
    }

    QLabel#planningHint[goalState="concluida"] {
        color: #15803d;
        font-weight: 700;
    }

    QProgressBar#dailyGoalProgress {
        background-color: #e2e8f0;
        border: none;
        border-radius: 4px;
    }

    QProgressBar#dailyGoalProgress::chunk {
        background-color: #3b82f6;
        border-radius: 4px;
    }

    QProgressBar#dailyGoalProgress[goalState="concluida"]::chunk {
        background-color: #22c55e;
    }

    QFrame#weekDayLoad {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        min-width: 58px;
    }

    QFrame#weekDayLoad[loadLevel="leve"] {
        background-color: #f0fdf4;
        border-color: #bbf7d0;
    }

    QFrame#weekDayLoad[loadLevel="moderada"] {
        background-color: #fffbeb;
        border-color: #fde68a;
    }

    QFrame#weekDayLoad[loadLevel="alta"] {
        background-color: #fff1f2;
        border-color: #fecdd3;
    }

    QLabel#weekDayName {
        color: #475569;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#weekDayDate {
        color: #94a3b8;
        font-size: 8pt;
    }

    QLabel#weekDayCount {
        color: #111827;
        font-size: 16px;
        font-weight: 700;
    }

    QFrame#cardResumo:hover {
        border: 1px solid #cbd5e1;
    }

    QLabel#cardTitulo {
        border: none;
        background: transparent;
        color: #64748b;
        font-size: 10pt;
    }

    QLabel#cardValor {
        border: none;
        background: transparent;
        color: #111827;
        font-size: 21px;
        font-weight: 700;
    }

    QPushButton {
        min-height: 30px;
        padding: 6px 12px;
        background-color: {{color:action.secondary}};
        color: {{color:text.primary}};
        border: 1px solid {{color:border.strong}};
        border-radius: 8px;
    }

    QPushButton:hover {
        background-color: {{color:action.secondary_hover}};
        border-color: {{color:border.hover}};
    }

    QPushButton:pressed {
        background-color: {{color:action.secondary_pressed}};
    }

    QPushButton:disabled {
        color: {{color:text.disabled}};
        background-color: {{color:action.secondary_disabled}};
        border-color: {{color:border.disabled}};
    }

    QPushButton#primaryButton {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #2563eb;
        font-weight: 700;
    }

    QPushButton#primaryButton:hover {
        background-color: #1d4ed8;
        border-color: #1d4ed8;
    }

    QPushButton#toolbarButton {
        background-color: #f8fbff;
        border: 1px solid #d3e0ee;
        color: #25415f;
        min-height: 32px;
    }

    QPushButton#toolbarButton:hover {
        background-color: #eef5fc;
        border-color: #b8cee5;
    }

    QPushButton#disciplineButton {
        min-height: 42px;
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        font-weight: 600;
        text-align: left;
        padding-left: 14px;
    }

    QPushButton#disciplineButton:hover {
        background-color: #eff6ff;
        border-color: #93c5fd;
    }

    QLineEdit,
    QComboBox,
    QSpinBox,
    QDateEdit,
    QTextEdit {
        min-height: 30px;
        padding: 4px 8px;
        background-color: #ffffff;
        color: #111827;
        border: 1px solid #cbd5e1;
        border-radius: 7px;
        selection-background-color: #bfdbfe;
        selection-color: #111827;
    }

    QLineEdit:focus,
    QComboBox:focus,
    QSpinBox:focus,
    QDateEdit:focus,
    QTextEdit:focus {
        border: 1px solid #3b82f6;
    }

    QComboBox QAbstractItemView {
        background-color: #ffffff;
        color: #111827;
        selection-background-color: #dbeafe;
        selection-color: #111827;
        border: 1px solid #cbd5e1;
    }

    QTableWidget,
    QTreeWidget {
        background-color: #ffffff;
        color: #1f2937;
        border: 1px solid #dbe3ed;
        border-radius: 8px;
        gridline-color: #e5e7eb;
        selection-background-color: #dbeafe;
        selection-color: #111827;
    }

    QTableWidget::item,
    QTreeWidget::item {
        padding: 5px;
    }

    QTableWidget::item:selected,
    QTreeWidget::item:selected {
        background-color: #dbeafe;
        color: #111827;
    }

    QHeaderView::section {
        background-color: #f8fafc;
        color: #475569;
        border: none;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #dbe3ed;
        padding: 7px;
        font-weight: 600;
    }

    QTabWidget::pane {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 8px;
        top: -1px;
    }

    QTabBar::tab {
        background-color: #eef2f7;
        color: #475569;
        padding: 8px 14px;
        margin-right: 2px;
        border-top-left-radius: 7px;
        border-top-right-radius: 7px;
    }

    QTabBar::tab:selected {
        background-color: #ffffff;
        color: #1d4ed8;
        font-weight: 700;
    }

    QCheckBox {
        spacing: 8px;
    }

    QCheckBox::indicator {
        width: 17px;
        height: 17px;
    }

    QFrame[frameShape="4"],
    QFrame[frameShape="5"] {
        color: #dbe3ed;
    }

    QToolTip {
        background-color: {{color:surface.inverse}};
        color: {{color:text.on_action}};
        border: none;
        padding: 5px;
    }


    /* ======================================================
       VIGHNA VISUAL V1 — CLARO
       Inspirado no layout de referência fornecido pelo usuário
       ====================================================== */

    QMainWindow,
    QDialog,
    QWidget {
        background-color: #f4f6fa;
        color: #182033;
    }

    QLabel#pageTitle {
        color: #111827;
        font-weight: 800;
    }

    QLabel#pageSubtitle,
    QLabel#mutedLabel {
        color: #68758d;
    }

    QFrame#dashboardCenterBar,
    QFrame#contextBar {
        background-color: #ffffff;
        border: 1px solid #d5dce8;
        border-radius: 11px;
    }

    QLabel#profileBadge {
        background-color: #f0edff;
        color: #5545c8;
        border: 1px solid #cdc6ff;
        border-radius: 8px;
        padding: 5px 10px;
        font-weight: 800;
    }

    QFrame#cardResumo {
        background-color: #ffffff;
        border: 1px solid #d5dce8;
        border-radius: 12px;
    }

    QFrame#cardResumo:hover {
        border: 1px solid #bfc8d8;
        background-color: #fbfcfe;
    }

    QFrame#cardResumo[metricRole="performance"] {
        background-color: #eaf8f2;
        border: 1px solid #b9e5d1;
    }

    QFrame#cardResumo[metricRole="performance"] QLabel#cardTitulo {
        color: #315f52;
    }

    QFrame#cardResumo[metricRole="performance"] QLabel#cardValor {
        color: #168765;
    }

    QLabel#cardTitulo {
        color: #4f5b70;
        font-size: 10pt;
        font-weight: 600;
    }

    QLabel#cardValor {
        color: #5f52ba;
        font-size: 21px;
        font-weight: 800;
    }

    QFrame#syllabusProgressPanel,
    QFrame#planningPanel {
        background-color: #ffffff;
        border: 1px solid #d5dce8;
        border-radius: 12px;
    }

    QFrame#syllabusDashboardCoverage,
    QFrame#syllabusDashboardStat,
    QFrame#dailyGoalBox,
    QFrame#weeklyLoadBox,
    QFrame#weeklyGoalBox,
    QFrame#weeklyGoalMetric {
        background-color: #f8f9fc;
        border: 1px solid #d8deea;
        border-radius: 9px;
    }

    QFrame#weekDayLoad {
        background-color: #f7f8fb;
        border: 1px solid #d8deea;
        border-radius: 9px;
    }

    QFrame#weekDayLoad[today="true"] {
        background-color: #f3f0ff;
        border: 1px solid #7566df;
    }

    QFrame#weekDayLoad[today="true"] QLabel#weekDayName,
    QFrame#weekDayLoad[today="true"] QLabel#weekDayDate,
    QFrame#weekDayLoad[today="true"] QLabel#weekDayCount {
        color: #5c4dcc;
        font-weight: 800;
    }

    QFrame#weekDayLoad[loadLevel="leve"][today="false"] {
        background-color: #f4fbf7;
        border-color: #d2eadc;
    }

    QFrame#weekDayLoad[loadLevel="moderada"][today="false"] {
        background-color: #fffaf0;
        border-color: #f1dfb6;
    }

    QFrame#weekDayLoad[loadLevel="alta"][today="false"] {
        background-color: #fff4f5;
        border-color: #efcfd4;
    }

    QPushButton#dashboardSectionToggle,
    QPushButton#dashboardSectionToggleCentered {
        color: #20293a;
        font-weight: 800;
    }

    QPushButton#dashboardSectionToggle:hover,
    QPushButton#dashboardSectionToggleCentered:hover {
        background-color: #f1efff;
        color: #5d4fd1;
    }

    QPushButton#toolbarButton,
    QPushButton#subtleButton {
        background-color: #ffffff;
        color: #263044;
        border: 1px solid #cfd6e2;
        border-radius: 8px;
    }

    QPushButton#toolbarButton:hover,
    QPushButton#subtleButton:hover {
        background-color: #f6f4ff;
        color: #5545c8;
        border-color: #b9afff;
    }

    QPushButton#questionsNavButton {
        background-color: #f1eeff;
        color: #5a49cf;
        border: 1px solid #d9d2ff;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#questionsNavButton:hover {
        background-color: #e8e3ff;
        border-color: #bfb5ff;
    }

    QPushButton#topAccentButton,
    QPushButton#primaryButton,
    QPushButton#syllabusOpenButton,
    QPushButton#syllabusAlertButton,
    QPushButton#syllabusForecastButton,
    QPushButton#planningGoalButton,
    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton,
    QPushButton#effectivenessOpenButton,
    QPushButton#questionsEffectivenessButton {
        background-color: #6254d9;
        color: #ffffff;
        border: 1px solid #6254d9;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#topAccentButton:hover,
    QPushButton#primaryButton:hover,
    QPushButton#syllabusOpenButton:hover,
    QPushButton#syllabusAlertButton:hover,
    QPushButton#syllabusForecastButton:hover,
    QPushButton#planningGoalButton:hover,
    QPushButton#planningSummaryButton:hover,
    QPushButton#planningRedistributeButton:hover,
    QPushButton#effectivenessOpenButton:hover,
    QPushButton#questionsEffectivenessButton:hover {
        background-color: #5144c5;
        border-color: #5144c5;
        color: #ffffff;
    }

    QFrame#syllabusAlertStrip,
    QFrame#syllabusAlertStrip[alertState="monitorar"],
    QFrame#syllabusAlertStrip[alertState="atencao"] {
        background-color: #fff4dc;
        border: 1px solid #e8c984;
        border-radius: 9px;
    }

    QFrame#syllabusForecastStrip {
        background-color: #fff4dc;
        border: 1px solid #e8c984;
        border-radius: 9px;
    }

    QLabel#syllabusAlertIcon,
    QLabel#syllabusForecastIcon {
        color: #b67a20;
    }

    QLabel#syllabusAlertText,
    QLabel#syllabusForecastText {
        color: #7b5823;
    }

    QLabel#syllabusAlertSummary,
    QLabel#syllabusForecastSummary {
        color: #745f3e;
    }

    QProgressBar#syllabusDashboardBar,
    QProgressBar#dailyGoalProgress,
    QProgressBar#weeklyGoalProgress,
    QProgressBar#questionSessionProgress,
    QProgressBar#topicDomainBar {
        background-color: #e5e8f0;
        border: none;
        border-radius: 4px;
    }

    QProgressBar#syllabusDashboardBar::chunk,
    QProgressBar#dailyGoalProgress::chunk,
    QProgressBar#weeklyGoalProgress::chunk,
    QProgressBar#questionSessionProgress::chunk,
    QProgressBar#topicDomainBar::chunk {
        background-color: #6b5ce7;
        border-radius: 4px;
    }

    QLineEdit,
    QComboBox,
    QSpinBox,
    QDateEdit,
    QTextEdit {
        background-color: {{color:surface.primary}};
        color: {{color:text.control}};
        border: 1px solid {{color:border.default}};
        border-radius: 8px;
        selection-background-color: {{color:overlay.selection}};
        selection-color: {{color:text.control}};
    }

    QLineEdit:focus,
    QComboBox:focus,
    QSpinBox:focus,
    QDateEdit:focus,
    QTextEdit:focus {
        border: 1px solid {{color:focus.ring}};
    }

    QComboBox QAbstractItemView {
        background-color: {{color:surface.elevated}};
        color: {{color:text.control}};
        selection-background-color: {{color:action.ghost_hover}};
        selection-color: {{color:text.selection_accent}};
        border: 1px solid {{color:border.default}};
    }

    QTableWidget,
    QTreeWidget {
        background-color: {{color:surface.secondary}};
        color: {{color:text.secondary}};
        border: 1px solid {{color:border.subtle}};
        border-radius: 9px;
        gridline-color: {{color:border.grid}};
        selection-background-color: {{color:surface.selected}};
        selection-color: {{color:text.selected}};
    }

    QHeaderView::section {
        background-color: {{color:surface.tertiary}};
        color: {{color:text.header}};
        border: none;
        border-right: 1px solid {{color:border.divider}};
        border-bottom: 1px solid {{color:border.divider_strong}};
        padding: 7px;
        font-weight: 700;
    }

    QTabWidget::pane {
        background-color: {{color:surface.secondary}};
        border: 1px solid {{color:border.subtle}};
        border-radius: 9px;
    }

    QTabBar::tab {
        background-color: {{color:surface.inset}};
        color: {{color:text.muted}};
        padding: 8px 14px;
    }

    QTabBar::tab:selected {
        background-color: {{color:surface.primary}};
        color: {{color:text.link}};
        font-weight: 800;
    }

    QScrollBar:vertical {
        background: {{color:surface.inset}};
        width: 10px;
        margin: 0px;
        border: none;
    }

    QScrollBar::handle:vertical {
        background: {{color:surface.interactive}};
        min-height: 28px;
        border-radius: 5px;
    }

    QScrollBar::handle:vertical:hover {
        background: {{color:surface.hover}};
    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {
        background: {{color:action.ghost}};
        height: 0px;
    }




    /* ======================================================
       AJUSTE CLARO V1 — BOTÕES AZUIS
       Mantém Escuro e Futurista independentes e inalterados.
       ====================================================== */

    QPushButton#topAccentButton,
    QPushButton#primaryButton,
    QPushButton#syllabusOpenButton,
    QPushButton#syllabusAlertButton,
    QPushButton#syllabusForecastButton,
    QPushButton#planningGoalButton,
    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton,
    QPushButton#effectivenessOpenButton,
    QPushButton#questionsEffectivenessButton,
    QPushButton#adaptiveSessionStartButton,
    QPushButton#adaptiveDashboardButton,
    QPushButton#questionsAdaptiveButton,
    QPushButton#mockExamStartButton,
    QPushButton#mockExamDashboardButton {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #2563eb;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#topAccentButton:hover,
    QPushButton#primaryButton:hover,
    QPushButton#syllabusOpenButton:hover,
    QPushButton#syllabusAlertButton:hover,
    QPushButton#syllabusForecastButton:hover,
    QPushButton#planningGoalButton:hover,
    QPushButton#planningSummaryButton:hover,
    QPushButton#planningRedistributeButton:hover,
    QPushButton#effectivenessOpenButton:hover,
    QPushButton#questionsEffectivenessButton:hover,
    QPushButton#adaptiveSessionStartButton:hover,
    QPushButton#adaptiveDashboardButton:hover,
    QPushButton#questionsAdaptiveButton:hover,
    QPushButton#mockExamStartButton:hover,
    QPushButton#mockExamDashboardButton:hover {
        background-color: #1d4ed8;
        border-color: #1d4ed8;
        color: #ffffff;
    }

    QPushButton#questionsNavButton,
    QPushButton#questionsMockExamButton {
        background-color: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#questionsNavButton:hover,
    QPushButton#questionsMockExamButton:hover {
        background-color: #dbeafe;
        color: #1e40af;
        border-color: #93c5fd;
    }




    /* Dashboard: Estudar / Avaliar / Revisões prioritárias */
    QFrame#studyNowPanel,
    QFrame#priorityQueuePanel {
        background-color: #ffffff;
        border: 1px solid #d3dce9;
        border-radius: 12px;
    }

    QLabel#dashboardActionSectionTitle {
        color: #172033;
        font-size: 9.5pt;
        font-weight: 900;
    }

    QLabel#dashboardActionSectionSubtitle,
    QLabel#studyActionDescription,
    QLabel#studyScoreBreakdown,
    QLabel#priorityQueueExplanation,
    QLabel#assessmentDescription {
        color: #65758b;
        font-size: 8.6pt;
    }

    QFrame#studyActionCard {
        background-color: #f8faff;
        border: 1px solid #d7e0ed;
        border-radius: 10px;
    }

    QFrame#studyActionCard[actionRole="review"] {
        border-color: #c8dcf8;
    }

    QFrame#studyActionCard[actionRole="adaptive"] {
        background-color: #faf9ff;
        border-color: #d9d2f5;
    }

    QLabel#studyActionTitle {
        color: #1b2a40;
        font-size: 9.6pt;
        font-weight: 900;
    }

    QLabel#studyActionMetric {
        color: #173f78;
        font-size: 11pt;
        font-weight: 800;
    }

    QLabel#studyReviewSourceBadge,
    QLabel#priorityQueueSourceBadge {
        background-color: #e9f3ff;
        color: #2362aa;
        border: 1px solid #bcd8f5;
        border-radius: 7px;
        padding: 3px 7px;
        font-size: 7.4pt;
        font-weight: 800;
    }

    QLabel#studyAdaptiveCriteria {
        color: #6253bd;
        font-size: 8.3pt;
        font-weight: 700;
    }

    QPushButton#studyManualButton {
        background-color: #ffffff;
        color: #24579b;
        border: 1px solid #a9c4e8;
        border-radius: 8px;
        padding: 6px 10px;
        font-weight: 700;
    }

    QPushButton#smartReviewDashboardButton {
        background-color: #2f6de5;
        color: #ffffff;
        border: 1px solid #2f6de5;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#adaptiveDashboardButton {
        background-color: #386fdc;
        color: #ffffff;
        border: 1px solid #386fdc;
        border-radius: 8px;
        font-weight: 800;
    }

    QFrame#assessmentPanel {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #f4f8ff,
            stop:1 #f4f3ff
        );
        border: 1px solid #bdccec;
        border-radius: 12px;
    }

    QLabel#assessmentTitle {
        color: #244f94;
        font-size: 11pt;
        font-weight: 900;
    }

    QLabel#assessmentBadge {
        background-color: #e8e4ff;
        color: #5e49c6;
        border: 1px solid #c7bdf5;
        border-radius: 7px;
        padding: 3px 7px;
        font-size: 7.5pt;
        font-weight: 900;
    }

    QLabel#assessmentHeadline {
        color: #172033;
        font-size: 10pt;
        font-weight: 800;
    }

    QFrame#assessmentStat {
        background-color: #ffffff;
        border: 1px solid #d2dbea;
        border-radius: 8px;
    }

    QLabel#assessmentStatLabel {
        color: #7a8799;
        font-size: 7.7pt;
    }

    QLabel#assessmentStatValue {
        color: #325eb5;
        font-size: 11pt;
        font-weight: 900;
    }

    QPushButton#mockExamDashboardButton {
        background-color: #2f63d8;
        color: #ffffff;
        border: 1px solid #2f63d8;
        border-radius: 9px;
        font-weight: 900;
        padding: 7px 12px;
    }




    /* Estudar Agora — composição compacta */

    QFrame#studyNowPanel {
        background-color: #ffffff;
        border: 1px solid #d3dce9;
        border-radius: 13px;
    }

    QFrame#studyManualFooter {
        background-color: #f7f9fc;
        border: 1px solid #dce5ef;
        border-radius: 10px;
    }

    QLabel#studyNowIcon {
        background-color: #edf6ff;
        border: 1px solid #c7dcf4;
        border-radius: 14px;
        font-size: 27px;
    }

    QLabel#dashboardActionSectionTitle {
        color: #101827;
        font-size: 16pt;
        font-weight: 900;
    }

    QLabel#dashboardActionSectionSubtitle {
        color: #58677c;
        font-size: 9pt;
    }

    QLabel#studyColumnTitle {
        color: #172033;
        font-size: 11pt;
        font-weight: 900;
    }

    QFrame#studyActionCard {
        background-color: #fbfcfe;
        border: 1px solid #cdd8e6;
        border-radius: 11px;
    }

    QFrame#studyActionCard[actionRole="review"] {
        border-color: #bcd8f1;
    }

    QLabel#studyCardIcon {
        background-color: #e9fbff;
        border: 1px solid #a9e5ee;
        border-radius: 13px;
        font-size: 25px;
    }

    QLabel#studyActionTitle,
    QLabel#strategyCardTitle {
        color: #111827;
        font-size: 12pt;
        font-weight: 900;
    }

    QLabel#studyReviewCount {
        color: #52627a;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#studyActionDescription,
    QLabel#strategyCardDescription,
    QLabel#studyReviewFooter {
        color: #5f6d80;
        font-size: 8.6pt;
    }

    QLabel#studyReviewDetail {
        color: #172033;
        font-size: 8.8pt;
        font-weight: 700;
    }

    QLabel#studyReviewSourceBadge {
        background-color: #e7f4ff;
        color: #2466a8;
        border: 1px solid #b8d8ef;
        border-radius: 7px;
        padding: 3px 7px;
        font-size: 7.3pt;
        font-weight: 900;
    }

    QFrame#strategyCompactCard {
        background-color: #fbfcfe;
        border: 1px solid #cdd8e6;
        border-radius: 11px;
    }

    QFrame#strategyCompactCard[actionRole="adaptive"] {
        border-color: #d5cef5;
        background-color: #fbfaff;
    }

    QFrame#strategyCompactCard[actionRole="simulation"] {
        border-color: #ecd29b;
        background-color: #fffdf8;
    }

    QLabel#strategyCardIcon {
        background-color: #f4f2ff;
        border: 1px solid #dad3ff;
        border-radius: 13px;
        font-size: 24px;
    }

    QFrame#strategyCompactCard[actionRole="simulation"] QLabel#strategyCardIcon {
        background-color: #fff7e7;
        border-color: #f2d59c;
    }

    QLabel#studyAdaptiveCriteria {
        color: #6757c7;
        font-size: 8.1pt;
        font-weight: 700;
    }

    QPushButton#studyManualButton,
    QPushButton#smartReviewDashboardButton {
        background-color: #2f6de5;
        color: #ffffff;
        border: 1px solid #2f6de5;
        border-radius: 9px;
        font-weight: 900;
    }

    QPushButton#studyManualButton:hover,
    QPushButton#smartReviewDashboardButton:hover {
        background-color: #245cc8;
        border-color: #245cc8;
    }

    QPushButton#adaptiveDashboardButton {
        background-color: #6a4fdf;
        color: #ffffff;
        border: 1px solid #6a4fdf;
        border-radius: 9px;
        font-weight: 900;
    }

    QPushButton#adaptiveDashboardButton:hover {
        background-color: #5a42c8;
    }

    QPushButton#mockExamDashboardButton {
        background-color: #e99812;
        color: #ffffff;
        border: 1px solid #e99812;
        border-radius: 9px;
        font-weight: 900;
    }

    QPushButton#mockExamDashboardButton:hover {
        background-color: #cc8109;
    }

    QLabel#assessmentBadge {
        background-color: #fff2d9;
        color: #a66909;
        border: 1px solid #e9c67e;
        border-radius: 7px;
        padding: 3px 6px;
        font-size: 7pt;
        font-weight: 900;
    }

    QFrame#assessmentStat {
        background-color: #f8fafc;
        border: 1px solid #d7dfeb;
        border-radius: 7px;
    }

    QLabel#assessmentStatLabel {
        color: #6b7789;
        font-size: 7.3pt;
    }

    QLabel#assessmentStatValue {
        color: #244f86;
        font-size: 10pt;
        font-weight: 900;
    }




    /* Dashboard superior V1 */

    QFrame#dashboardHeroCard {
        background-color: #ffffff;
        border: 1px solid #cfd8e5;
        border-radius: 13px;
    }

    QLabel#dashboardHeroTitle {
        color: #121826;
        font-size: 12.5pt;
        font-weight: 900;
    }

    QLabel#dashboardHeroInfo {
        color: #687386;
        font-size: 13pt;
        font-weight: 700;
    }

    QFrame#dashboardStatusPill {
        border-radius: 9px;
    }

    QFrame#dashboardStatusPill[statusRole="today"] {
        background-color: #e5f7ec;
        border: 1px solid #c7ead4;
    }

    QFrame#dashboardStatusPill[statusRole="late"] {
        background-color: #fff2cb;
        border: 1px solid #e8ca74;
    }

    QLabel#dashboardStatusPillLabel,
    QLabel#dashboardStatusPillValue {
        font-size: 11pt;
        font-weight: 900;
    }

    QFrame#dashboardStatusPill[statusRole="today"] QLabel {
        color: #26734d;
    }

    QFrame#dashboardStatusPill[statusRole="late"] QLabel {
        color: #8b5b0e;
    }

    QPushButton#dashboardProgressTitleButton {
        background: transparent;
        border: none;
        color: #111827;
        text-align: left;
        padding: 0px;
        font-size: 12.5pt;
        font-weight: 900;
    }

    QLabel#dashboardContestLabel {
        color: #273244;
        font-weight: 700;
    }

    QComboBox#dashboardContestCombo {
        background-color: #ffffff;
        color: #182033;
        border: 1px solid #c7d0dd;
        border-radius: 9px;
        padding: 5px 9px;
    }

    QFrame#dashboardProgressDivider {
        background-color: #d7dde7;
        border: none;
    }

    QLabel#dashboardProgressSubtitle {
        color: #69778a;
        font-size: 8.5pt;
    }

    QLabel#dashboardProgressPercent {
        color: #111827;
        font-size: 11pt;
        font-weight: 900;
    }

    QProgressBar#dashboardHeroProgressBar {
        background-color: #dfe5ec;
        border: none;
        border-radius: 8px;
    }

    QProgressBar#dashboardHeroProgressBar::chunk {
        background-color: #20c5c9;
        border-radius: 8px;
    }

    QLabel#dashboardProgressLegendLabel,
    QLabel#dashboardProgressLegendValue {
        color: #202938;
        font-size: 8.2pt;
    }

    QLabel#dashboardProgressLegendValue {
        font-weight: 900;
    }

    QFrame#dashboardProgressLegend[legendRole="notStarted"] QLabel#dashboardProgressLegendDot {
        color: #59616c;
    }

    QFrame#dashboardProgressLegend[legendRole="worked"] QLabel#dashboardProgressLegendDot {
        color: #1fc1ca;
    }

    QFrame#dashboardProgressLegend[legendRole="consolidating"] QLabel#dashboardProgressLegendDot {
        color: #9c59e6;
    }

    QFrame#dashboardProgressLegend[legendRole="consolidated"] QLabel#dashboardProgressLegendDot {
        color: #39b875;
    }

    QFrame#dashboardDomainBadge {
        background-color: #f2f6fb;
        border: 1px solid #d2dbe7;
        border-radius: 7px;
    }

    QLabel#dashboardDomainLabel {
        color: #68758a;
    }

    QLabel#dashboardDomainValue {
        color: #182033;
        font-weight: 900;
    }

    QFrame#dashboardNotificationsPanel {
        background-color: #ffffff;
        border: 1px solid #cfd8e5;
        border-radius: 12px;
    }

    QLabel#dashboardNotificationsTitle {
        color: #111827;
        font-size: 11.5pt;
        font-weight: 900;
    }

    QLabel#dashboardNotificationsMenu {
        color: #69778a;
        font-weight: 900;
    }

    QFrame#dashboardAlertActionCard {
        background-color: #fff1c9;
        border: 1px solid #dfb547;
        border-radius: 12px;
    }

    QLabel#dashboardAlertActionIcon {
        color: #a56b0d;
        font-size: 17pt;
        font-weight: 900;
    }

    QLabel#dashboardAlertActionSummary {
        color: #805411;
        font-weight: 800;
    }

    QFrame#dashboardQuickStats {
        background-color: #ffffff;
        border: 1px solid #cfd8e5;
        border-radius: 11px;
    }

    QLabel#dashboardQuickStatLabel {
        color: #59677a;
    }

    QLabel#dashboardQuickStatValue {
        color: #182033;
        font-size: 10pt;
        font-weight: 900;
    }




    /* Central de avisos do edital */

    QFrame#dashboardNotificationsPanel {
        background-color: #ffffff;
        border: 1px solid #cfd8e5;
        border-radius: 12px;
    }

    QLabel#dashboardNotificationsTitle {
        color: #111827;
        font-size: 11.5pt;
        font-weight: 900;
    }

    QLabel#dashboardNotificationsSubtitle {
        color: #758297;
        font-size: 8pt;
    }

    QFrame#dashboardNoticeRow {
        border-left: none;
        border-right: none;
        border-bottom: none;
        border-radius: 0px;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] {
        background-color: #fff4d9;
        border-top: 1px solid #e8c46c;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"][alertState="ok"] {
        background-color: #eef8f2;
        border-top: 1px solid #c3e4d0;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"][alertState="critico"] {
        background-color: #fff0ed;
        border-top: 1px solid #e7a49b;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] {
        background-color: #f5f8fc;
        border-top: 1px solid #dbe3ed;
    }

    QLabel#dashboardNoticeIcon {
        background-color: rgba(255,255,255,150);
        color: #9a6812;
        border: 1px solid #e5c779;
        border-radius: 9px;
        font-size: 15pt;
        font-weight: 900;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeIcon {
        color: #326aa8;
        border-color: #bdd2e8;
    }

    QLabel#dashboardNoticeLabel {
        color: #7b8798;
        font-size: 7.2pt;
        font-weight: 900;
    }

    QLabel#dashboardNoticeTitle {
        color: #172033;
        font-size: 9.4pt;
        font-weight: 800;
    }

    QLabel#dashboardNoticeDescription {
        color: #68778b;
        font-size: 8.2pt;
    }

    QLabel#dashboardNoticeSummary {
        background-color: rgba(255,255,255,170);
        color: #7e5a18;
        border: 1px solid #e4ca8c;
        border-radius: 7px;
        padding: 4px 7px;
        font-size: 7.8pt;
        font-weight: 800;
    }

    QFrame#dashboardNoticeRow[alertState="ok"] QLabel#dashboardNoticeSummary {
        color: #397655;
        border-color: #bfdcca;
    }

    QFrame#dashboardNotificationsFooter {
        background-color: #fafbfd;
        border-top: 1px solid #dfe5ed;
        border-bottom-left-radius: 11px;
        border-bottom-right-radius: 11px;
    }

    QLabel#dashboardQuickStatLabel {
        color: #738095;
        font-size: 8pt;
    }

    QLabel#dashboardQuickStatValue {
        color: #172033;
        font-size: 9.3pt;
        font-weight: 900;
    }

    QLabel#dashboardNotificationsFooterText {
        color: #98a2b1;
        font-size: 7.7pt;
    }




    /* REFINO CLEAN V1 — CLARO */

    QLabel#pageTitle {
        color: #151c2a;
        font-size: 18pt;
        font-weight: 700;
    }

    QLabel#pageSubtitle {
        color: #69778c;
        font-size: 9pt;
        font-weight: 400;
    }

    QPushButton#toolbarButton,
    QPushButton#topAccentButton {
        min-height: 34px;
        padding: 5px 12px;
        font-size: 9pt;
        font-weight: 600;
        border-radius: 8px;
    }

    QPushButton#toolbarButton {
        background-color: #ffffff;
        color: #273346;
        border: 1px solid #d1d9e5;
    }

    QPushButton#toolbarButton:hover {
        background-color: #f5f8fc;
        color: #265fae;
        border-color: #b6c9e2;
    }

    QPushButton#topAccentButton {
        background-color: #326fd3;
        color: #ffffff;
        border: 1px solid #326fd3;
    }

    QFrame#dashboardHeroCard,
    QFrame#dashboardNotificationsPanel,
    QFrame#planningPanel,
    QFrame#studyNowPanel,
    QFrame#priorityQueuePanel {
        border-radius: 11px;
    }

    QLabel#dashboardHeroTitle {
        color: #192232;
        font-size: 10.5pt;
        font-weight: 700;
    }

    QLabel#dashboardHeroInfo {
        color: #8a96a7;
        font-size: 9.5pt;
        font-weight: 600;
    }

    QFrame#dashboardStatusPill {
        min-height: 30px;
        border-radius: 7px;
    }

    QLabel#dashboardStatusPillLabel {
        font-size: 8.5pt;
        font-weight: 600;
    }

    QLabel#dashboardStatusPillValue {
        font-size: 10pt;
        font-weight: 700;
    }

    QPushButton#dashboardProgressTitleButton {
        color: #192232;
        font-size: 10.5pt;
        font-weight: 700;
    }

    QLabel#dashboardProgressPercent {
        font-size: 10pt;
        font-weight: 700;
    }

    QLabel#dashboardProgressLegendLabel,
    QLabel#dashboardProgressLegendValue {
        font-size: 7.8pt;
    }

    QLabel#dashboardProgressLegendValue,
    QLabel#dashboardDomainValue {
        font-weight: 700;
    }

    QLabel#dashboardNotificationsTitle {
        color: #192232;
        font-size: 10pt;
        font-weight: 700;
    }

    QLabel#dashboardNotificationsSubtitle {
        color: #8390a2;
        font-size: 7.7pt;
    }

    QLabel#dashboardNoticeIcon {
        background-color: transparent;
        border: none;
        font-size: 12pt;
        font-weight: 700;
    }

    QLabel#dashboardNoticeLabel {
        color: #7c8797;
        font-size: 6.8pt;
        font-weight: 700;
    }

    QLabel#dashboardNoticeTitle {
        color: #263143;
        font-size: 8.7pt;
        font-weight: 600;
    }

    QLabel#dashboardNoticeDescription {
        color: #758296;
        font-size: 7.8pt;
    }

    QLabel#dashboardNoticeSummary {
        background-color: transparent;
        border: none;
        color: #8a6a2c;
        font-size: 7.5pt;
        font-weight: 600;
        padding: 0px;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] {
        background-color: #fff8e8;
        border-top: 1px solid #ebd9ac;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] {
        background-color: #f8fafc;
        border-top: 1px solid #e3e8ef;
    }

    QFrame#dashboardNotificationsFooter {
        background-color: #fbfcfd;
    }

    QLabel#dashboardQuickStatLabel {
        color: #7a8799;
        font-size: 7.7pt;
    }

    QLabel#dashboardQuickStatValue {
        color: #263143;
        font-size: 8.7pt;
        font-weight: 700;
    }

    QLabel#studyNowIcon,
    QLabel#studyCardIcon,
    QLabel#strategyCardIcon {
        background-color: transparent;
        border: none;
        color: #65778d;
        font-size: 15pt;
        font-weight: 600;
    }

    QLabel#dashboardActionSectionTitle {
        color: #192232;
        font-size: 13pt;
        font-weight: 700;
    }

    QLabel#dashboardActionSectionSubtitle {
        color: #758296;
        font-size: 8.5pt;
        font-weight: 400;
    }

    QLabel#studyColumnTitle {
        color: #344154;
        font-size: 9.5pt;
        font-weight: 700;
    }

    QLabel#studyActionTitle,
    QLabel#strategyCardTitle {
        color: #202a3b;
        font-size: 10.5pt;
        font-weight: 700;
    }

    QLabel#studyReviewCount {
        color: #768499;
        font-size: 8pt;
        font-weight: 500;
    }

    QLabel#studyActionDescription,
    QLabel#strategyCardDescription,
    QLabel#studyReviewFooter {
        color: #758296;
        font-size: 8pt;
        font-weight: 400;
    }

    QLabel#studyReviewDetail {
        color: #445166;
        font-size: 8.2pt;
        font-weight: 600;
    }

    QLabel#studyReviewSourceBadge,
    QLabel#priorityQueueSourceBadge,
    QLabel#assessmentBadge {
        border-radius: 6px;
        padding: 2px 6px;
        font-size: 6.7pt;
        font-weight: 600;
    }

    QLabel#studyAdaptiveCriteria {
        color: #7773a9;
        font-size: 7.6pt;
        font-weight: 500;
    }

    QPushButton#studyManualButton,
    QPushButton#smartReviewDashboardButton,
    QPushButton#adaptiveDashboardButton,
    QPushButton#mockExamDashboardButton,
    QPushButton#syllabusAlertButton,
    QPushButton#syllabusForecastButton,
    QPushButton#effectivenessOpenButton,
    QPushButton#syllabusOpenButton {
        min-height: 32px;
        padding: 5px 10px;
        border-radius: 7px;
        font-size: 8.5pt;
        font-weight: 600;
    }

    QPushButton#studyManualButton,
    QPushButton#smartReviewDashboardButton,
    QPushButton#syllabusAlertButton,
    QPushButton#syllabusForecastButton,
    QPushButton#effectivenessOpenButton,
    QPushButton#syllabusOpenButton {
        background-color: #326fd3;
        border: 1px solid #326fd3;
        color: #ffffff;
    }

    QPushButton#adaptiveDashboardButton {
        background-color: #5d62bd;
        border: 1px solid #5d62bd;
        color: #ffffff;
    }

    QPushButton#mockExamDashboardButton {
        background-color: #bf8530;
        border: 1px solid #bf8530;
        color: #ffffff;
    }

    QFrame#studyActionCard,
    QFrame#strategyCompactCard {
        border-radius: 9px;
        background-color: #fbfcfe;
    }

    QFrame#studyActionCard[actionRole="review"] {
        border-color: #d1deed;
    }

    QFrame#strategyCompactCard[actionRole="adaptive"] {
        background-color: #fbfbfe;
        border-color: #dddcef;
    }

    QFrame#strategyCompactCard[actionRole="simulation"] {
        background-color: #fffdf9;
        border-color: #eadfc9;
    }

    QFrame#assessmentStat {
        border-radius: 6px;
        background-color: #f7f9fc;
        border-color: #e0e6ee;
    }

    QLabel#assessmentStatLabel {
        color: #8792a2;
        font-size: 6.8pt;
    }

    QLabel#assessmentStatValue {
        color: #3d526c;
        font-size: 9pt;
        font-weight: 700;
    }




    /* Setas compactas — Visão geral / Notificações */

    QPushButton#dashboardGroupToggle {
        background: transparent;
        color: #536174;
        border: none;
        text-align: left;
        padding: 3px 5px;
        font-size: 8.8pt;
        font-weight: 600;
    }

    QPushButton#dashboardGroupToggle:hover {
        background-color: #f1f4f8;
        color: #2f609e;
        border-radius: 6px;
    }

    QPushButton#dashboardGroupToggle[expanded="false"] {
        color: #65758a;
    }




    /* Status do dia + Desempenho refinados */

    QLabel#dashboardStatusTotal {
        color: #202b3d;
        font-size: 17pt;
        font-weight: 700;
    }

    QLabel#dashboardStatusSubtitle {
        color: #7a8798;
        font-size: 8.3pt;
        font-weight: 400;
    }

    QFrame#dashboardStatusLine {
        background: transparent;
        border: none;
    }

    QLabel#dashboardStatusDot {
        font-size: 7.5pt;
    }

    QFrame#dashboardStatusLine[statusRole="today"] QLabel#dashboardStatusDot {
        color: #48ad79;
    }

    QFrame#dashboardStatusLine[statusRole="late"] QLabel#dashboardStatusDot {
        color: #d29a3d;
    }

    QLabel#dashboardStatusLineLabel {
        color: #657287;
        font-size: 8.5pt;
        font-weight: 500;
    }

    QLabel#dashboardStatusLineValue {
        color: #263143;
        font-size: 9.5pt;
        font-weight: 700;
    }

    QLabel#dashboardStatusContext {
        background-color: #f2f6fa;
        color: #607084;
        border: 1px solid #dfe6ee;
        border-radius: 7px;
        padding: 3px 7px;
        font-size: 7.6pt;
        font-weight: 600;
    }

    QLabel#dashboardStatusContext[statusRole="ok"] {
        background-color: #edf8f1;
        color: #43815d;
        border-color: #d1ead9;
    }

    QLabel#dashboardStatusContext[statusRole="attention"] {
        background-color: #fff7e7;
        color: #9a6c24;
        border-color: #ebd9b3;
    }

    QLabel#dashboardPerformanceCaption {
        color: #7b8798;
        font-size: 7.8pt;
        font-weight: 500;
    }

    QLabel#dashboardTrendLabel {
        color: #8793a3;
        font-size: 7.5pt;
    }

    QLabel#dashboardTrendValue {
        color: #758195;
        font-size: 7.7pt;
        font-weight: 600;
    }

    QLabel#dashboardTrendValue[trendRole="positive"] {
        color: #3d8b61;
    }

    QLabel#dashboardTrendValue[trendRole="negative"] {
        color: #b05b5b;
    }

    QLabel#dashboardTrendValue[trendRole="stable"] {
        color: #63748a;
    }




    /* ======================================================
       VISÃO GERAL HARMÔNICA — CLARO
       ====================================================== */

    QFrame#dashboardOverviewCard {
        background-color: #ffffff;
        border: 1px solid #d4dce7;
        border-radius: 11px;
    }

    QLabel#dashboardOverviewTitle {
        color: #1d2737;
        font-size: 10.5pt;
        font-weight: 700;
    }

    QLabel#dashboardOverviewInfo {
        color: #96a1b0;
        font-size: 8.5pt;
        font-weight: 600;
    }

    QLabel#dashboardRhythmMainValue {
        color: #243044;
        font-size: 18pt;
        font-weight: 700;
    }

    QLabel#dashboardRhythmCaption {
        color: #7c899b;
        font-size: 8pt;
        font-weight: 400;
    }

    QFrame#dashboardRhythmMetric {
        background-color: #f8fafc;
        border: 1px solid #e0e6ee;
        border-radius: 8px;
    }

    QFrame#dashboardRhythmMetric[metricRole="today"] {
        background-color: #f3faf6;
        border-color: #d8ebdf;
    }

    QFrame#dashboardRhythmMetric[metricRole="late"] {
        background-color: #fffaf1;
        border-color: #eee0bf;
    }

    QLabel#dashboardRhythmMetricValue {
        color: #263143;
        font-size: 11pt;
        font-weight: 700;
    }

    QFrame#dashboardRhythmMetric[metricRole="today"] QLabel#dashboardRhythmMetricValue {
        color: #438160;
    }

    QFrame#dashboardRhythmMetric[metricRole="late"] QLabel#dashboardRhythmMetricValue {
        color: #9b702b;
    }

    QLabel#dashboardRhythmMetricLabel {
        color: #788598;
        font-size: 7.5pt;
        font-weight: 500;
    }

    QLabel#dashboardRhythmStatus {
        background-color: transparent;
        color: #6d7a8c;
        border: none;
        font-size: 7.7pt;
        font-weight: 600;
    }

    QLabel#dashboardRhythmStatus[statusRole="ok"] {
        color: #4d8765;
    }

    QLabel#dashboardRhythmStatus[statusRole="attention"] {
        color: #9b702b;
    }

    QLabel#dashboardQualityCaption {
        color: #7f8b9b;
        font-size: 7.7pt;
        font-weight: 500;
    }

    QFrame#dashboardOverviewDivider {
        background-color: #e4e9ef;
        border: none;
    }

    QLabel#dashboardQualityTrendLabel {
        color: #8793a2;
        font-size: 7.5pt;
    }

    QLabel#dashboardQualityTrendValue {
        color: #778496;
        font-size: 7.7pt;
        font-weight: 600;
    }

    QLabel#dashboardQualityTrendValue[trendRole="positive"] {
        color: #43845f;
    }

    QLabel#dashboardQualityTrendValue[trendRole="negative"] {
        color: #ad6161;
    }

    QLabel#dashboardQualityTrendValue[trendRole="stable"] {
        color: #68798c;
    }

    QPushButton#dashboardProjectionTitleButton {
        background: transparent;
        color: #1d2737;
        border: none;
        text-align: left;
        padding: 0px;
        font-size: 10.5pt;
        font-weight: 700;
    }

    QPushButton#dashboardProjectionTitleButton:hover {
        color: #356aa9;
    }

    QLabel#dashboardProjectionContestLabel {
        color: #7a8798;
        font-size: 8pt;
        font-weight: 600;
    }

    QLabel#dashboardProjectionCaption {
        color: #7e8a9b;
        font-size: 7.7pt;
    }

    QLabel#dashboardProjectionDetail {
        color: #47556a;
        font-size: 8.3pt;
        font-weight: 600;
    }

    QLabel#dashboardProjectionPercent {
        color: #243044;
        font-size: 16pt;
        font-weight: 700;
    }

    QProgressBar#dashboardProjectionBar {
        background-color: #e5eaf0;
        border: none;
        border-radius: 6px;
    }

    QProgressBar#dashboardProjectionBar::chunk {
        background-color: #36bfb9;
        border-radius: 6px;
    }

    QFrame#dashboardProjectionMetric {
        background-color: #f8fafc;
        border: 1px solid #e1e6ed;
        border-radius: 7px;
    }

    QLabel#dashboardProjectionMetricLabel {
        color: #7b8798;
        font-size: 7.4pt;
    }

    QLabel#dashboardProjectionMetricValue {
        color: #2c3748;
        font-size: 8.7pt;
        font-weight: 700;
    }

    QFrame#dashboardProjectionMetric[metricRole="consolidating"] QLabel#dashboardProjectionMetricValue {
        color: #785bb0;
    }

    QFrame#dashboardProjectionMetric[metricRole="consolidated"] QLabel#dashboardProjectionMetricValue {
        color: #438461;
    }

    QFrame#dashboardProjectionMetric[metricRole="domain"] QLabel#dashboardProjectionMetricValue {
        color: #356b91;
    }




    /* Ritmo + Qualidade V2 — Claro */

    QFrame#dashboardOverviewVerticalDivider {
        background-color: #e4e9ef;
        border: none;
    }

    QLabel#dashboardRhythmMainValue {
        color: #202b3c;
        font-size: 19pt;
        font-weight: 700;
    }

    QLabel#dashboardRhythmCaption {
        color: #7b889a;
        font-size: 8pt;
        font-weight: 400;
    }

    QFrame#dashboardRhythmLine {
        background: transparent;
        border: none;
    }

    QLabel#dashboardRhythmDot {
        font-size: 7pt;
    }

    QFrame#dashboardRhythmLine[metricRole="today"] QLabel#dashboardRhythmDot {
        color: #53a879;
    }

    QFrame#dashboardRhythmLine[metricRole="late"] QLabel#dashboardRhythmDot {
        color: #c9943c;
    }

    QLabel#dashboardRhythmLineLabel {
        color: #667386;
        font-size: 8.4pt;
        font-weight: 500;
    }

    QLabel#dashboardRhythmLineValue {
        color: #253044;
        font-size: 11pt;
        font-weight: 700;
    }

    QFrame#dashboardRhythmLine[metricRole="today"] QLabel#dashboardRhythmLineValue {
        color: #43805f;
    }

    QFrame#dashboardRhythmLine[metricRole="late"] QLabel#dashboardRhythmLineValue {
        color: #946a27;
    }

    QLabel#dashboardRhythmStatus {
        color: #69778a;
        background: transparent;
        border: none;
        padding: 1px 0px;
        font-size: 7.7pt;
        font-weight: 600;
    }

    QLabel#dashboardRhythmStatus[statusRole="ok"] {
        color: #4e8062;
    }

    QLabel#dashboardRhythmStatus[statusRole="attention"] {
        color: #926b2d;
    }

    QLabel#dashboardQualityEyebrow {
        color: #8b96a6;
        font-size: 6.9pt;
        font-weight: 600;
    }

    QLabel#dashboardQualityCaption {
        color: #364357;
        font-size: 9.2pt;
        font-weight: 600;
    }

    QFrame#dashboardQualityTrendBox {
        background-color: #f7f9fc;
        border: 1px solid #e1e6ed;
        border-radius: 7px;
    }

    QLabel#dashboardQualityTrendValue {
        color: #536176;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#dashboardQualityTrendValue[trendRole="positive"] {
        color: #40815d;
    }

    QLabel#dashboardQualityTrendValue[trendRole="negative"] {
        color: #a95c5c;
    }

    QLabel#dashboardQualityTrendValue[trendRole="stable"] {
        color: #637488;
    }

    QLabel#dashboardQualityTrendLabel {
        color: #8a96a6;
        font-size: 6.9pt;
        font-weight: 400;
    }

    QLabel#dashboardQualityFooter {
        color: #9aa4b1;
        font-size: 6.8pt;
        font-weight: 400;
    }




    /* ======================================================
       PLANEJAMENTO REORGANIZADO V1 — CLARO
       ====================================================== */

    QFrame#planningPanel {
        background-color: #ffffff;
        border: 1px solid #d4dce7;
        border-radius: 11px;
    }

    QLabel#planningSectionSubtitle {
        color: #7c899a;
        font-size: 8pt;
        font-weight: 400;
    }

    QLabel#planningSubsectionTitle {
        color: #273246;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#planningSubsectionHint {
        color: #8994a4;
        font-size: 7.5pt;
        font-weight: 400;
    }

    QLabel#planningMicroLabel {
        color: #929dac;
        font-size: 7pt;
        font-weight: 400;
    }

    QFrame#dailyGoalBox,
    QFrame#weeklyLoadBox,
    QFrame#weeklyGoalBox {
        background-color: #f9fbfd;
        border: 1px solid #dfe5ed;
        border-radius: 9px;
    }

    QLabel#planningItemTitle,
    QLabel#weeklyGoalTitle {
        color: #344055;
        font-size: 8.7pt;
        font-weight: 700;
    }

    QLabel#dailyGoalValue {
        color: #202b3d;
        font-size: 13pt;
        font-weight: 700;
    }

    QLabel#planningTotalBadge {
        background-color: #f2f5f9;
        color: #657286;
        border: 1px solid #dbe2ea;
        border-radius: 6px;
        padding: 3px 7px;
        font-size: 7.3pt;
        font-weight: 600;
    }

    QProgressBar#dailyGoalProgress {
        background-color: #e5eaf0;
        border: none;
        border-radius: 4px;
    }

    QProgressBar#dailyGoalProgress::chunk {
        background-color: #3976d5;
        border-radius: 4px;
    }

    QLabel#planningHint {
        color: #778497;
        font-size: 7.4pt;
    }

    QFrame#weekDayLoad {
        background-color: #ffffff;
        border: 1px solid #e0e6ed;
        border-radius: 8px;
        min-height: 62px;
    }

    QFrame#weekDayLoad[today="true"] {
        background-color: #f2f6ff;
        border-color: #7fa4ea;
    }

    QFrame#weekDayLoad[loadLevel="leve"][today="false"] {
        background-color: #f6fbf8;
        border-color: #d6e9dd;
    }

    QFrame#weekDayLoad[loadLevel="moderada"][today="false"] {
        background-color: #fffaf1;
        border-color: #ead9b7;
    }

    QFrame#weekDayLoad[loadLevel="alta"][today="false"] {
        background-color: #fff3f1;
        border-color: #e8c6c1;
    }

    QLabel#weekDayName {
        color: #526176;
        font-size: 7.5pt;
        font-weight: 600;
    }

    QLabel#weekDayDate {
        color: #9aa4b1;
        font-size: 6.8pt;
    }

    QLabel#weekDayCount {
        color: #273246;
        font-size: 10pt;
        font-weight: 700;
    }

    QFrame#weekDayLoad[today="true"] QLabel#weekDayName,
    QFrame#weekDayLoad[today="true"] QLabel#weekDayCount {
        color: #3b61b4;
    }

    QPushButton#planningGoalButton,
    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton,
    QPushButton#weeklyGoalSetupButton {
        min-height: 30px;
        padding: 4px 10px;
        border-radius: 7px;
        font-size: 8pt;
        font-weight: 600;
    }

    QPushButton#planningGoalButton {
        background-color: #326fd3;
        color: #ffffff;
        border: 1px solid #326fd3;
    }

    QPushButton#planningSummaryButton {
        background-color: #ffffff;
        color: #47627f;
        border: 1px solid #cfd9e5;
    }

    QPushButton#planningRedistributeButton {
        background-color: #ffffff;
        color: #47627f;
        border: 1px solid #cfd9e5;
    }

    QPushButton#planningRedistributeButton[hasSuggestion="true"] {
        background-color: #fff7e8;
        color: #9a6a22;
        border-color: #e8cf9d;
    }

    QPushButton#weeklyGoalSetupButton {
        background-color: #ffffff;
        color: #3268b3;
        border: 1px solid #bfd0e4;
    }

    QFrame#weeklyGoalEmptyState {
        background-color: #ffffff;
        border: 1px dashed #d6dee8;
        border-radius: 8px;
    }

    QLabel#weeklyGoalEmptyTitle {
        color: #455368;
        font-size: 8.3pt;
        font-weight: 600;
    }

    QLabel#weeklyGoalEmptyDescription {
        color: #8793a3;
        font-size: 7.4pt;
    }

    QLabel#weeklyGoalPeriod {
        color: #8490a1;
        font-size: 7.4pt;
    }

    QLabel#weeklyGoalStatus {
        border-radius: 6px;
        padding: 3px 7px;
        font-size: 7.2pt;
        font-weight: 600;
    }

    QFrame#weeklyGoalMetric {
        background-color: #ffffff;
        border: 1px solid #e0e6ed;
        border-radius: 7px;
    }

    QLabel#weeklyGoalMetricTitle {
        color: #748195;
        font-size: 7.3pt;
        font-weight: 600;
    }

    QLabel#weeklyGoalValue {
        color: #293548;
        font-size: 9.5pt;
        font-weight: 700;
    }

    QLabel#weeklyGoalHint {
        color: #8c97a6;
        font-size: 7pt;
    }




    /* ======================================================
       REFINO DE PALETA DO DASHBOARD - CLARO V1
       ====================================================== */

    QFrame#dashboardOverviewCard,
    QFrame#dashboardNotificationsPanel,
    QFrame#planningPanel,
    QFrame#dashboardProjectionPanel {
        background-color: #ffffff;
        border: 1px solid #d8e0ea;
        border-radius: 12px;
    }

    QLabel#dashboardOverviewTitle,
    QPushButton#dashboardProjectionTitleButton {
        color: #1f2d3d;
    }

    QLabel#dashboardOverviewInfo {
        color: #9aa6b5;
    }

    QFrame#dashboardOverviewDivider,
    QFrame#dashboardOverviewVerticalDivider {
        background-color: #e6ebf2;
    }

    QLabel#dashboardRhythmMainValue {
        color: #1f2d3d;
    }

    QLabel#dashboardRhythmCaption,
    QLabel#dashboardQualityCaption,
    QLabel#dashboardQualityEyebrow,
    QLabel#dashboardQualityFooter,
    QLabel#dashboardProjectionCaption,
    QLabel#dashboardProjectionContestLabel,
    QLabel#dashboardProjectionMetricLabel,
    QLabel#dashboardNotificationsSubtitle {
        color: #7c8a9d;
    }

    QLabel#dashboardRhythmLineLabel,
    QLabel#dashboardProjectionDetail,
    QLabel#dashboardProjectionMetricValue,
    QLabel#dashboardNoticeSummary,
    QLabel#dashboardNoticeDescription {
        color: #556579;
    }

    QLabel#dashboardRhythmLineValue,
    QLabel#dashboardProjectionPercent,
    QLabel#dashboardQualityTrendValue[trendRole="stable"] {
        color: #233247;
    }

    QFrame#dashboardRhythmLine[metricRole="today"] QLabel#dashboardRhythmDot,
    QFrame#dashboardRhythmLine[metricRole="today"] QLabel#dashboardRhythmLineValue,
    QLabel#dashboardRhythmStatus[statusRole="ok"] {
        color: #4d9278;
    }

    QFrame#dashboardRhythmLine[metricRole="late"] QLabel#dashboardRhythmDot,
    QFrame#dashboardRhythmLine[metricRole="late"] QLabel#dashboardRhythmLineValue,
    QLabel#dashboardRhythmStatus[statusRole="attention"] {
        color: #9a7330;
    }

    QFrame#dashboardQualityTrendBox {
        background-color: #f7fafd;
        border: 1px solid #e2e9f1;
        border-radius: 8px;
    }

    QLabel#dashboardQualityTrendValue[trendRole="positive"] {
        color: #488d73;
    }

    QLabel#dashboardQualityTrendValue[trendRole="negative"] {
        color: #b46a6a;
    }

    QProgressBar#dashboardProjectionBar {
        background-color: #e7edf3;
        border-radius: 6px;
    }

    QProgressBar#dashboardProjectionBar::chunk {
        background-color: #2fb4c7;
        border-radius: 6px;
    }

    QFrame#dashboardProjectionMetric {
        background-color: #f8fbfd;
        border: 1px solid #e1e8f0;
        border-radius: 8px;
    }

    QFrame#dashboardProjectionMetric[metricRole="consolidating"] QLabel#dashboardProjectionMetricValue {
        color: #6d7fd6;
    }

    QFrame#dashboardProjectionMetric[metricRole="consolidated"] QLabel#dashboardProjectionMetricValue {
        color: #4b9677;
    }

    QFrame#dashboardProjectionMetric[metricRole="domain"] QLabel#dashboardProjectionMetricValue {
        color: #356fcf;
    }

    QFrame#dashboardNoticeRow {
        border-radius: 10px;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] {
        background-color: #fff8ea;
        border: 1px solid #ead7aa;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"][alertState="ok"] {
        background-color: #f5fbf7;
        border: 1px solid #d9eadf;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"][alertState="critico"] {
        background-color: #fff2f1;
        border: 1px solid #ebc8c5;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] {
        background-color: #f8fbfd;
        border: 1px solid #dde6ef;
    }

    QLabel#dashboardNoticeLabel {
        color: #8a95a3;
        font-size: 7.2pt;
        font-weight: 600;
    }

    QLabel#dashboardNoticeTitle {
        color: #223247;
        font-size: 9pt;
        font-weight: 600;
    }

    QLabel#dashboardNoticeIcon {
        color: #366ecc;
        background-color: #edf4ff;
        border: 1px solid #d2e1fb;
        border-radius: 15px;
        font-size: 11pt;
        font-weight: 700;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] QLabel#dashboardNoticeIcon {
        color: #b17a1d;
        background-color: #fff4d8;
        border-color: #efd59c;
    }

    QPushButton#primaryButton,
    QPushButton#syllabusOpenButton,
    QPushButton#syllabusAlertButton,
    QPushButton#syllabusForecastButton,
    QPushButton#effectivenessOpenButton,
    QPushButton#planningGoalButton {
        background-color: #2f6fdf;
        color: #ffffff;
        border: 1px solid #2f6fdf;
        border-radius: 8px;
        font-weight: 700;
    }

    QPushButton#primaryButton:hover,
    QPushButton#syllabusOpenButton:hover,
    QPushButton#syllabusAlertButton:hover,
    QPushButton#syllabusForecastButton:hover,
    QPushButton#effectivenessOpenButton:hover,
    QPushButton#planningGoalButton:hover {
        background-color: #255dbe;
        border-color: #255dbe;
    }

    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton,
    QPushButton#weeklyGoalSetupButton,
    QPushButton#subtleButton {
        background-color: #ffffff;
        color: #476076;
        border: 1px solid #cfd8e3;
        border-radius: 8px;
        font-weight: 600;
    }

    QPushButton#planningSummaryButton:hover,
    QPushButton#planningRedistributeButton:hover,
    QPushButton#weeklyGoalSetupButton:hover,
    QPushButton#subtleButton:hover {
        background-color: #f5f8fc;
        border-color: #b9c8d7;
    }

    QPushButton#planningRedistributeButton[hasSuggestion="true"] {
        background-color: #fff7e8;
        color: #9d7029;
        border-color: #ead09d;
    }


    /* Ação única do Planejamento */
    QPushButton#planningGoalButton {
        min-height: 34px;
        padding: 5px 14px;
        background-color: #2f6fdf;
        color: #ffffff;
        border: 1px solid #2f6fdf;
        border-radius: 8px;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QPushButton#planningGoalButton:hover {
        background-color: #255dbe;
        border-color: #255dbe;
    }




    /* Correção de contraste no hover — Planejamento */
    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton {
        background-color: #ffffff;
        color: #40566f;
        border: 1px solid #cbd7e4;
        border-radius: 8px;
        font-weight: 600;
    }

    QPushButton#planningSummaryButton:hover,
    QPushButton#planningRedistributeButton:hover {
        background-color: #edf4fd;
        color: #245eaa;
        border: 1px solid #9fbce1;
    }

    QPushButton#planningSummaryButton:pressed,
    QPushButton#planningRedistributeButton:pressed {
        background-color: #e2edf9;
        color: #1f528f;
        border-color: #8aaad2;
    }

    QPushButton#planningRedistributeButton[hasSuggestion="true"] {
        background-color: #fff7e8;
        color: #946820;
        border-color: #e7ce9a;
    }

    QPushButton#planningRedistributeButton[hasSuggestion="true"]:hover {
        background-color: #fff0d2;
        color: #7c5619;
        border-color: #d9b86f;
    }



    /* ======================================================
       NOTIFICAÇÕES — CORES HARMONIZADAS V1 / CLARO
       ====================================================== */

    QFrame#dashboardNotificationsPanel {
        background-color: #ffffff;
        border: 1px solid #d8e0ea;
        border-radius: 11px;
    }

    /* Atenção: quente, porém discreto. */
    QFrame#dashboardNoticeRow[noticeRole="alert"] {
        background-color: #fff9ee;
        border: 1px solid #ead9b5;
        border-radius: 9px;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"][alertState="ok"] {
        background-color: #f5faf7;
        border-color: #d4e7db;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"][alertState="critico"] {
        background-color: #fff3f1;
        border-color: #e8cbc7;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] QLabel#dashboardNoticeLabel {
        color: #9a762f;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] QLabel#dashboardNoticeTitle {
        color: #5f4a26;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] QLabel#dashboardNoticeDescription,
    QFrame#dashboardNoticeRow[noticeRole="alert"] QLabel#dashboardNoticeSummary {
        color: #8b6e37;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] QLabel#dashboardNoticeIcon {
        background-color: #fff1cf;
        color: #ad7b1e;
        border: 1px solid #e8cf94;
        border-radius: 15px;
    }

    /* Previsão/cobertura: azul informativo suave. */
    QFrame#dashboardNoticeRow[noticeRole="forecast"] {
        background-color: #f4f8fd;
        border: 1px solid #d4e2f0;
        border-radius: 9px;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeLabel {
        color: #6687ad;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeTitle {
        color: #315d8d;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeDescription,
    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeSummary {
        color: #66809d;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeIcon {
        background-color: #eaf3fd;
        color: #3c74b5;
        border: 1px solid #c7dcef;
        border-radius: 15px;
    }

    QPushButton#syllabusAlertButton {
        background-color: #bf8a31;
        color: #ffffff;
        border: 1px solid #bf8a31;
        border-radius: 8px;
        font-weight: 700;
    }

    QPushButton#syllabusAlertButton:hover {
        background-color: #a97829;
        color: #ffffff;
        border-color: #a97829;
    }

    QPushButton#syllabusForecastButton {
        background-color: #3d78c5;
        color: #ffffff;
        border: 1px solid #3d78c5;
        border-radius: 8px;
        font-weight: 700;
    }

    QPushButton#syllabusForecastButton:hover {
        background-color: #3268ad;
        color: #ffffff;
        border-color: #3268ad;
    }

    QFrame#dashboardNotificationsFooter {
        background-color: #fbfcfe;
        border-top: 1px solid #e2e8ef;
    }




    /* Questões — ação principal do menu */

    QPushButton#questionsNavButton {
        min-height: 34px;
        min-width: 96px;
        padding: 5px 13px;
        background-color: #2388b8;
        color: #ffffff;
        border: 1px solid #2388b8;
        border-radius: 8px;
        font-size: 9pt;
        font-weight: 700;
    }

    QPushButton#questionsNavButton:hover {
        background-color: #1d76a0;
        color: #ffffff;
        border-color: #1d76a0;
    }

    QPushButton#questionsNavButton:pressed {
        background-color: #176486;
        color: #ffffff;
        border-color: #176486;
    }




    /* ======================================================
       PALETA HARMONIZADA — BOTÕES (CLARO)
       Objetivo: unificar a linguagem visual dos CTAs
       mantendo destaque nos mais importantes.
       ====================================================== */

    QPushButton#toolbarButton,
    QPushButton#subtleButton {
        background-color: #ffffff;
        color: #334155;
        border: 1px solid #cfd8e3;
        border-radius: 8px;
    }

    QPushButton#toolbarButton:hover,
    QPushButton#subtleButton:hover {
        background-color: #f6fbff;
        color: #235f98;
        border-color: #9fc7e7;
    }

    QPushButton#questionsNavButton,
    QPushButton#questionsImportButton,
    QPushButton#questionsPdfImportButton,
    QPushButton#questionsSolveButton,
    QPushButton#questionsSolveHeroButton,
    QPushButton#questionsNewHeroButton,
    QPushButton#questionsPromptsButton,
    QPushButton#questionsHistoryButton,
    QPushButton#questionsEffectivenessButton {
        background-color: #2f8ab5;
        color: #ffffff;
        border: 1px solid #2f8ab5;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#questionsNavButton:hover,
    QPushButton#questionsImportButton:hover,
    QPushButton#questionsPdfImportButton:hover,
    QPushButton#questionsSolveButton:hover,
    QPushButton#questionsSolveHeroButton:hover,
    QPushButton#questionsNewHeroButton:hover,
    QPushButton#questionsPromptsButton:hover,
    QPushButton#questionsHistoryButton:hover,
    QPushButton#questionsEffectivenessButton:hover {
        background-color: #27779c;
        border-color: #27779c;
        color: #ffffff;
    }

    QPushButton#topAccentButton,
    QPushButton#primaryButton,
    QPushButton#syllabusOpenButton,
    QPushButton#planningGoalButton,
    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton,
    QPushButton#effectivenessOpenButton,
    QPushButton#smartReviewDashboardButton,
    QPushButton#rowActionButton,
    QPushButton#weeklyGoalSetupButton,
    QPushButton#questionSessionEndButton,
    QPushButton#studySessionEndButton,
    QPushButton#mockExamStartButton {
        background-color: #326fd3;
        color: #ffffff;
        border: 1px solid #326fd3;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#topAccentButton:hover,
    QPushButton#primaryButton:hover,
    QPushButton#syllabusOpenButton:hover,
    QPushButton#planningGoalButton:hover,
    QPushButton#planningSummaryButton:hover,
    QPushButton#planningRedistributeButton:hover,
    QPushButton#effectivenessOpenButton:hover,
    QPushButton#smartReviewDashboardButton:hover,
    QPushButton#rowActionButton:hover,
    QPushButton#weeklyGoalSetupButton:hover,
    QPushButton#questionSessionEndButton:hover,
    QPushButton#studySessionEndButton:hover,
    QPushButton#mockExamStartButton:hover {
        background-color: #285fb5;
        border-color: #285fb5;
        color: #ffffff;
    }

    QPushButton#adaptiveDashboardButton,
    QPushButton#questionsAdaptiveButton,
    QPushButton#adaptiveSessionStartButton {
        background-color: #3ca38f;
        color: #ffffff;
        border: 1px solid #3ca38f;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#adaptiveDashboardButton:hover,
    QPushButton#questionsAdaptiveButton:hover,
    QPushButton#adaptiveSessionStartButton:hover {
        background-color: #328a79;
        border-color: #328a79;
        color: #ffffff;
    }

    QPushButton#syllabusAlertButton,
    QPushButton#mockExamDashboardButton,
    QPushButton#questionsMockExamButton {
        background-color: #d69a2e;
        color: #ffffff;
        border: 1px solid #d69a2e;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#syllabusAlertButton:hover,
    QPushButton#mockExamDashboardButton:hover,
    QPushButton#questionsMockExamButton:hover {
        background-color: #bd8420;
        border-color: #bd8420;
        color: #ffffff;
    }

    QPushButton#syllabusForecastButton {
        background-color: #ffffff;
        color: #326fd3;
        border: 1px solid #9ec0f3;
        border-radius: 8px;
        font-weight: 700;
    }

    QPushButton#syllabusForecastButton:hover {
        background-color: #eef5ff;
        color: #285fb5;
        border-color: #7fa8e8;
    }




    /* Integridade histórica — Questões */

    QLabel#questionsIntegrityBadge {
        background-color: #f4f7fb;
        color: #66758a;
        border: 1px solid #d8e1eb;
        border-radius: 7px;
        padding: 4px 8px;
        font-size: 7.5pt;
        font-weight: 700;
    }

    QLabel#questionsIntegrityBadge[integrityState="ok"] {
        background-color: #edf8f2;
        color: #3f7e5b;
        border-color: #cbe5d5;
    }

    QLabel#questionsIntegrityBadge[integrityState="legacy"] {
        background-color: #f2f7fd;
        color: #426b93;
        border-color: #cbdced;
    }

    QLabel#questionsIntegrityBadge[integrityState="warning"] {
        background-color: #fff7e8;
        color: #946820;
        border-color: #ecd6a9;
    }




    /* Minha evolução V1 — Claro */

    QFrame#myEvolutionFilterBar,
    QFrame#myEvolutionPanel,
    QFrame#myEvolutionStatCard {
        background-color: #ffffff;
        border: 1px solid #d8e0ea;
        border-radius: 10px;
    }

    QLabel#myEvolutionTitle,
    QLabel#myEvolutionSectionTitle {
        color: #1f2d3d;
        font-weight: 700;
    }

    QLabel#myEvolutionTitle {
        font-size: 11pt;
    }

    QLabel#myEvolutionSectionTitle {
        font-size: 9.5pt;
    }

    QLabel#myEvolutionStatLabel {
        color: #758397;
        font-size: 7.8pt;
        font-weight: 600;
    }

    QLabel#myEvolutionStatValue {
        color: #233247;
        font-size: 15pt;
        font-weight: 700;
    }

    QLabel#myEvolutionStatDetail {
        color: #8995a5;
        font-size: 7.3pt;
    }

    QFrame#myEvolutionInsight {
        background-color: #f8fafc;
        border: 1px solid #e2e8ef;
        border-radius: 8px;
    }

    QFrame#myEvolutionInsight[insightRole="positive"] {
        background-color: #f3faf6;
        border-color: #d7eadf;
    }

    QFrame#myEvolutionInsight[insightRole="attention"] {
        background-color: #fff8eb;
        border-color: #ead9b3;
    }

    QFrame#myEvolutionInsight[insightRole="recovery"] {
        background-color: #f3f8ff;
        border-color: #d4e2f4;
    }

    QLabel#myEvolutionInsightLabel {
        color: #7d8999;
        font-size: 7.2pt;
        font-weight: 600;
    }

    QLabel#myEvolutionInsightValue {
        color: #28364a;
        font-size: 9.2pt;
        font-weight: 700;
    }

    QLabel#myEvolutionInsightDetail {
        color: #7f8c9e;
        font-size: 7.2pt;
    }




    /* Índice de Domínio V2 */

    QFrame#topicDomainCard {
        background-color: #f8fbff;
        border: 1px solid #c7d9ef;
        border-radius: 11px;
    }

    QFrame#topicDomainComponent {
        background-color: #ffffff;
        border: 1px solid #e0e7ef;
        border-radius: 8px;
    }

    QLabel#topicDomainStrengths {
        color: #39785a;
        background-color: #f1f8f4;
        border: 1px solid #d5e9dc;
        border-radius: 7px;
        padding: 5px 8px;
        font-size: 8.1pt;
        font-weight: 600;
    }

    QLabel#topicDomainReasons {
        color: #7a5a2d;
        background-color: #fff9ed;
        border: 1px solid #ead9b5;
        border-radius: 7px;
        padding: 5px 8px;
        font-size: 8.1pt;
    }




    /* ======================================================
       RELATÓRIOS ESTRATÉGICOS V1 — CLARO
       ====================================================== */

    QScrollArea#strategicReportScroll,
    QWidget#strategicReportContent {
        background: transparent;
        border: none;
    }

    QLabel#strategicReportTitle {
        color: #172033;
        font-size: 12pt;
        font-weight: 800;
    }

    QLabel#strategicReportSubtitle,
    QLabel#strategicReportMuted {
        color: #64748b;
        font-size: 8.7pt;
    }

    QFrame#strategicMetricCard {
        background-color: #f8fbff;
        border: 1px solid #d6e3f0;
        border-radius: 10px;
    }

    QLabel#strategicMetricTitle {
        color: #64748b;
        font-size: 8.4pt;
        font-weight: 700;
    }

    QLabel#strategicMetricValue {
        color: #172033;
        font-size: 15pt;
        font-weight: 800;
    }

    QLabel#strategicMetricValue[prepState="attention"] {
        color: #b45309;
    }

    QLabel#strategicMetricValue[prepState="building"] {
        color: #9a6a1b;
    }

    QLabel#strategicMetricValue[prepState="good"] {
        color: #326fd3;
    }

    QLabel#strategicMetricValue[prepState="strong"] {
        color: #27816f;
    }

    QLabel#strategicMetricValue[prepState="insufficient"] {
        color: #64748b;
    }

    QLabel#strategicMetricDetail {
        color: #738196;
        font-size: 8.1pt;
    }

    QFrame#strategicReportPanel {
        background-color: #f8fafc;
        border: 1px solid #dbe3ed;
        border-radius: 11px;
    }

    QLabel#strategicReportSectionTitle {
        color: #263044;
        font-size: 9.5pt;
        font-weight: 800;
    }

    QFrame#strategicEvolutionItem {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }

    QLabel#strategicEvolutionValue {
        color: #334155;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#strategicEvolutionValue[trend="positive"] {
        color: #27816f;
    }

    QLabel#strategicEvolutionValue[trend="negative"] {
        color: #b45309;
    }

    QLabel#strategicEvolutionValue[trend="neutral"] {
        color: #64748b;
    }

    QLabel#strategicRiskItem,
    QLabel#strategicActionItem {
        border-radius: 8px;
        padding: 7px 9px;
        font-size: 8.4pt;
    }

    QLabel#strategicRiskItem[riskLevel="alto"] {
        background-color: #fff2ec;
        color: #8a3f21;
        border: 1px solid #f0c1aa;
    }

    QLabel#strategicRiskItem[riskLevel="medio"] {
        background-color: #fff8e8;
        color: #7a571d;
        border: 1px solid #e7cd8b;
    }

    QLabel#strategicRiskItem[riskLevel="baixo"] {
        background-color: #eef8f4;
        color: #326f61;
        border: 1px solid #badccf;
    }

    QLabel#strategicActionItem {
        background-color: #f2f7ff;
        color: #31577f;
        border: 1px solid #c5d8f1;
    }

    QTableWidget#strategicReportTable {
        background-color: #ffffff;
        border: 1px solid #dbe3ed;
        border-radius: 8px;
    }




    /* Plano de Ação Automático V1 */
    QPushButton#planningAutoPlanButton,
    QPushButton#autoPlanAcceptButton {
        background-color: #326fd3;
        color: #ffffff;
        border: 1px solid #326fd3;
        border-radius: 8px;
        font-weight: 800;
    }
    QPushButton#planningAutoPlanButton:hover,
    QPushButton#autoPlanAcceptButton:hover {
        background-color: #285fb5;
        color: #ffffff;
        border-color: #285fb5;
    }
    QPushButton#planningAutoPlanButton[hasPlan="true"] {
        background-color: #2f8ab5;
        border-color: #2f8ab5;
    }
    QPushButton#planningAutoPlanButton[hasPlan="true"]:hover {
        background-color: #27779c;
        border-color: #27779c;
    }
    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton {
        background-color: #ffffff;
        color: #326fd3;
        border: 1px solid #a9c2e8;
        border-radius: 8px;
        font-weight: 700;
    }
    QPushButton#planningSummaryButton:hover,
    QPushButton#planningRedistributeButton:hover {
        background-color: #eef5ff;
        color: #285fb5;
        border-color: #7fa8e8;
    }
    QFrame#autoPlanStat {
        background-color: #f8fbff;
        border: 1px solid #d6e4f5;
        border-radius: 9px;
    }
    QLabel#autoPlanSavedNotice {
        background-color: #eff8f6;
        color: #236858;
        border: 1px solid #b9ded5;
        border-radius: 8px;
        padding: 7px 10px;
    }
    QLabel#autoPlanContext {
        color: #52657a;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 7px 10px;
    }




    /* ======================================================
       PAUSA & DESAFIOS — CLARO
       ====================================================== */

    QPushButton#pauseNavButton {
        min-height: 34px;
        padding: 5px 12px;
        background-color: #eef8f8;
        color: #286d70;
        border: 1px solid #b9dcdd;
        border-radius: 8px;
        font-size: 9pt;
        font-weight: 700;
    }

    QPushButton#pauseNavButton:hover {
        background-color: #e0f2f2;
        color: #205d60;
        border-color: #8fc9cb;
    }

    QLabel#pauseHubTitle {
        color: #182433;
        font-size: 17px;
        font-weight: 800;
    }

    QLabel#pauseHubSubtitle,
    QLabel#gameHint,
    QLabel#pauseTimerStatus {
        color: #64748b;
        font-size: 9pt;
    }

    QFrame#pauseTimerPanel {
        background-color: #f3fafa;
        border: 1px solid #c7e1e1;
        border-radius: 10px;
    }

    QFrame#pauseRecordsPanel,
    QFrame#gameBoardPanel {
        background-color: #ffffff;
        border: 1px solid #d9e2ec;
        border-radius: 11px;
    }

    QFrame#pauseRecordCard {
        background-color: #f8fafc;
        border: 1px solid #e1e8f0;
        border-radius: 8px;
    }

    QLabel#pauseSectionTitle,
    QLabel#gameTitle {
        color: #243449;
        font-weight: 800;
    }

    QLabel#pauseSectionTitle {
        font-size: 9.5pt;
    }

    QLabel#gameTitle {
        font-size: 13pt;
    }

    QLabel#pauseRecordTitle {
        color: #64748b;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#pauseRecordValue,
    QLabel#gameMetric {
        color: #214f70;
        font-weight: 800;
    }

    QLabel#gameStatus {
        color: #526276;
        font-size: 9pt;
    }

    QLabel#pauseTimerValue {
        min-width: 74px;
        padding: 4px 10px;
        background-color: #ffffff;
        color: #286d70;
        border: 1px solid #b9dcdd;
        border-radius: 7px;
        font-size: 12pt;
        font-weight: 900;
    }

    QPushButton#pausePrimaryButton,
    QPushButton#gamePrimaryButton {
        background-color: #2d8b8d;
        color: #ffffff;
        border: 1px solid #2d8b8d;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#pausePrimaryButton:hover,
    QPushButton#gamePrimaryButton:hover {
        background-color: #247678;
        border-color: #247678;
        color: #ffffff;
    }

    QPushButton#pauseSecondaryButton,
    QPushButton#pauseBackButton {
        background-color: #ffffff;
        color: #326fd3;
        border: 1px solid #a9c4ee;
        border-radius: 8px;
        font-weight: 700;
    }

    QPushButton#pauseSecondaryButton:hover,
    QPushButton#pauseBackButton:hover {
        background-color: #eef5ff;
        color: #285fb5;
        border-color: #7fa8e8;
    }

    QPushButton#chimpCellButton,
    QPushButton#memoryCardButton,
    QPushButton#sequenceCellButton,
    QPushButton#puzzleTileButton,
    QPushButton#rotationOptionButton {
        min-height: 46px;
        background-color: #f7fafc;
        color: #243449;
        border: 1px solid #cfd9e5;
        border-radius: 9px;
        font-size: 12pt;
        font-weight: 900;
    }

    QScrollArea#rotationScrollArea,
    QWidget#rotationScrollContent,
    QWidget#rotationOptionsContainer {
        background: transparent;
        border: none;
    }

    QPushButton#rotationOptionButton {
        min-height: 112px;
        padding: 0px;
    }

    QPushButton#chimpCellButton[cellState="number"] {
        background-color: #edf5ff;
        color: #275f9f;
        border-color: #9fc3ec;
    }

    QPushButton#chimpCellButton[cellState="correct"] {
        background-color: #e6f7f3;
        color: #257565;
        border-color: #8bd2c3;
    }

    QPushButton#memoryCardButton[cardState="hidden"] {
        background-color: #eef3f8;
        color: #60758a;
        border-color: #c9d5e1;
    }

    QPushButton#memoryCardButton[cardState="open"] {
        background-color: #e9f2ff;
        color: #255f9e;
        border-color: #8fb8e8;
    }

    QPushButton#memoryCardButton[cardState="matched"] {
        background-color: #e4f6f0;
        color: #247060;
        border-color: #8ccbbb;
    }

    QPushButton#sequenceCellButton {
        background-color: #edf2f7;
        border-color: #cbd6e2;
    }

    QPushButton#sequenceCellButton[lit="true"] {
        background-color: #e6b85a;
        border-color: #c9922c;
    }

    QPushButton#puzzleTileButton[tileState="movable"] {
        background-color: #edf5ff;
        color: #275f9f;
        border-color: #98bee9;
    }

    QPushButton#puzzleTileButton[tileState="blank"] {
        background-color: #edf1f5;
        border-color: #e0e6ed;
        color: transparent;
    }

    QPushButton#rotationOptionButton[answerState="correct"] {
        background-color: #e4f6f0;
        border-color: #60b89e;
    }

    QPushButton#rotationOptionButton[answerState="wrong"] {
        background-color: #fff0f1;
        border-color: #d88b96;
    }




    /* MODO FOCO — CLARO */
    QPushButton#focusNavButton {
        min-height: 34px;
        padding: 5px 12px;
        background-color: #edf5ff;
        color: #285f9e;
        border: 1px solid #b7d1ee;
        border-radius: 8px;
        font-size: 9pt;
        font-weight: 800;
    }
    QPushButton#focusNavButton:hover {
        background-color: #dfeeff;
        color: #214f84;
        border-color: #8db7e4;
    }
    QScrollArea#focusScrollArea { border: none; background: transparent; }
    QWidget#focusScrollContent { background: transparent; }
    QLabel#focusTitle { color: #182433; font-size: 17px; font-weight: 800; }
    QLabel#focusSubtitle, QLabel#focusWindowHint, QLabel#focusStatLabel, QLabel#focusStatusLabel {
        color: #64748b; font-size: 9pt;
    }
    QFrame#focusStatsPanel { background-color: #f6f9fd; border: 1px solid #d8e2ee; border-radius: 10px; }
    QLabel#focusStatValue { color: #285f9e; font-size: 13pt; font-weight: 900; }
    QFrame#focusConfigPanel, QFrame#focusRecentPanel {
        background-color: #ffffff; border: 1px solid #d9e2ec; border-radius: 11px;
    }
    QFrame#focusOptionalPanel {
        background-color: #f8fbff; border: 1px dashed #c9d8e8; border-radius: 10px;
    }
    QLabel#focusAutoQuestionsNotice {
        background-color: #eef6ff;
        color: #245889;
        border: 1px solid #b9d3ee;
        border-radius: 9px;
        padding: 8px 12px;
        font-size: 9pt;
        font-weight: 800;
    }
    QFrame#focusActivePanel {
        background-color: #f3f8ff; border: 1px solid #bcd4ef; border-radius: 12px;
    }
    QLabel#focusSectionTitle, QLabel#focusContextLabel { color: #243449; font-weight: 800; }
    QLabel#focusTimerValue { color: #285f9e; font-size: 32px; font-weight: 900; }
    QLabel#dashboardFocusSummary { color: #53708c; font-size: 8.4pt; font-weight: 700; }
    QPushButton#focusPresetButton, QPushButton#focusSecondaryButton, QPushButton#focusPauseButton {
        background-color: #ffffff; color: #32679f; border: 1px solid #b9cee4; border-radius: 8px; font-weight: 700;
    }
    QPushButton#focusPresetButton:hover, QPushButton#focusSecondaryButton:hover, QPushButton#focusPauseButton:hover {
        background-color: #eef6ff; border-color: #8db7e4; color: #245889;
    }
    QPushButton#focusPrimaryButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #c91f2b, stop:0.52 #dc2626, stop:1 #ef4444);
        color: #ffffff; border: 1px solid #a91520; border-radius: 10px;
        font-weight: 900; font-size: 10.2pt; padding: 8px 22px;
    }
    QPushButton#focusPrimaryButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #b81924, stop:0.52 #cf202b, stop:1 #e43742);
        border-color: #8f111a;
    }
    QPushButton#focusPrimaryButton:pressed { background-color: #a91520; border-color: #7f1018; }
    QPushButton#focusDangerButton {
        background-color: #fff7f5; color: #a84a3f; border: 1px solid #e4b6b0; border-radius: 8px; font-weight: 700;
    }
    QPushButton#focusDangerButton:hover { background-color: #ffebe8; border-color: #d8948b; }

    QFrame#postFocusHero { background-color: #f2f7ff; border: 1px solid #bfd5ee; border-radius: 12px; }
    QFrame#postFocusContentCard { background-color: #ffffff; border: 1px solid #d9e2ec; border-radius: 10px; }
    QFrame#postFocusResultCard { background-color: #f6fbf7; border: 1px solid #bfdcc7; border-radius: 10px; }
    QLabel#postFocusResultValue { color: #247344; font-size: 13pt; font-weight: 900; }
    QPushButton#postFocusContinue { background-color: #e9f3ff; color: #235fae; border: 1px solid #afccea; border-radius: 9px; font-weight: 900; padding: 7px 14px; }
    QPushButton#postFocusContinue:hover { background-color: #dcecff; border-color: #8eb7e1; }
    QLabel#postFocusEyebrow { color: #53708c; font-size: 8.3pt; font-weight: 800; }
    QLabel#postFocusTime { color: #235fae; font-size: 25px; font-weight: 900; }
    QLabel#postFocusStatus, QLabel#postFocusDetail, QLabel#postFocusNote { color: #64748b; }
    QLabel#postFocusContentTitle { color: #203247; font-size: 11pt; font-weight: 800; }
    QLabel#postFocusQuestion { color: #203247; font-size: 10.5pt; font-weight: 900; }
    QPushButton#postFocusPrimary { background-color: #326fd3; color: #ffffff; border: 1px solid #326fd3; border-radius: 9px; font-weight: 800; padding: 7px 14px; }
    QPushButton#postFocusPrimary:hover { background-color: #285fb5; border-color: #285fb5; }
    QPushButton#postFocusSecondary { background-color: #ffffff; color: #32679f; border: 1px solid #b9cee4; border-radius: 9px; font-weight: 800; padding: 7px 14px; }
    QPushButton#postFocusSecondary:hover { background-color: #eef6ff; border-color: #8db7e4; }
    QPushButton#postFocusGhost { background: transparent; color: #53708c; border: 1px solid #d1dbe6; border-radius: 8px; font-weight: 700; padding: 6px 12px; }
    QPushButton#postFocusGhost:hover { background-color: #f4f7fb; color: #2c5279; }
    QPushButton#postFocusSecondary:disabled { color: #9aa9b8; background-color: #f4f6f8; border-color: #dce3ea; }
    QFrame#focusHeroPanel { background-color: #eef6ff; border: 1px solid #cfe0f2; border-radius: 14px; }
    QLabel#focusHeroEyebrow { color: #5e7b98; font-size: 8.3pt; font-weight: 800; letter-spacing: 0.4px; }
    QLabel#focusHeroValue { color: #285f9e; font-size: 24px; font-weight: 900; }
    QLabel#focusHeroStatus { color: #203247; font-size: 10pt; font-weight: 800; }
    QLabel#focusHeroNote, QLabel#focusConfigHint, QLabel#focusHistoryHint, QLabel#focusFieldLabel { color: #64748b; }
    QFrame#focusHeroMiniCard { background-color: #ffffff; border: 1px solid #d8e2ee; border-radius: 11px; }
    QLabel#focusHeroMiniLabel { color: #6b7d90; font-size: 8.2pt; font-weight: 700; }
    QLabel#focusHeroMiniValue { color: #244f83; font-size: 12pt; font-weight: 900; }
    QLabel#postFocusDialogTitle { color: #203247; font-size: 16px; font-weight: 900; }
    QLabel#postFocusDialogSubtitle { color: #64748b; }
    QFrame#postFocusMiniCard { background-color: #ffffff; border: 1px solid #d9e2ec; border-radius: 10px; }
    QLabel#postFocusMiniLabel { color: #6b7d90; font-size: 8.2pt; font-weight: 800; }
    QLabel#postFocusMiniValue { color: #235fae; font-size: 11.5pt; font-weight: 900; }
    QProgressBar#focusProgressBar { min-height: 8px; max-height: 8px; background-color: #e4edf7; border: none; border-radius: 4px; }
    QProgressBar#focusProgressBar::chunk { background-color: #3b82d0; border-radius: 4px; }


    


    /* ======================================================
       HOJE OPERACIONAL — CLARO
       ====================================================== */
    QFrame#dashboardTodayPanel {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fbfdff, stop:0.55 #f4f8fd, stop:1 #f9fbfe);
        border: 1px solid #c7d8ea;
        border-radius: 14px;
    }
    QLabel#dashboardTodayTitle {
        color: #172b43;
        font-size: 11.5pt;
        font-weight: 900;
    }
    QLabel#dashboardTodayDate {
        color: #4c6e91;
        background-color: #eef4fb;
        border: 1px solid #d7e3ef;
        border-radius: 7px;
        padding: 3px 8px;
        font-size: 8.5pt;
        font-weight: 700;
    }
    QLabel#dashboardTodayStatus {
        color: #567595;
        font-size: 8.7pt;
        font-weight: 800;
    }
    QFrame#dashboardTodayFocus {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #eef5ff, stop:1 #f6faff);
        border: 1px solid #bfd4eb;
        border-radius: 13px;
    }
    QFrame#dashboardTodayMetric {
        background-color: rgba(255, 255, 255, 0.95);
        border: 1px solid #d4e0eb;
        border-radius: 13px;
    }
    QFrame#dashboardTodayMetric[metricRole="late"] {
        background-color: #fff7f4;
        border-color: #e8c9c2;
    }
    QFrame#dashboardTodayMetric[metricRole="today"] {
        background-color: #fffaf1;
        border-color: #e6d4ad;
    }
    QFrame#dashboardTodayMetric[metricRole="ok"] {
        background-color: #f4faf7;
        border-color: #cfe4d8;
    }
    QFrame#dashboardTodayMetric[metricRole="active"] {
        background-color: #f3f8fe;
        border-color: #c6d9ee;
    }
    QFrame#dashboardTodayMetric[metricKind="review"] {
        background-color: #eef8f2;
        border-color: #badfc7;
    }
    QLabel#dashboardTodayEyebrow {
        color: #5a738d;
        font-size: 7.9pt;
        font-weight: 900;
        letter-spacing: 0.35px;
    }
    QLabel#dashboardTodayFocusValue {
        color: #225ea3;
        font-size: 14.5pt;
        font-weight: 900;
    }
    QLabel#dashboardTodayMetricValue {
        color: #243a52;
        font-size: 14.5pt;
        font-weight: 900;
    }
    QFrame#dashboardTodayMetric[metricRole="late"] QLabel#dashboardTodayMetricValue { color: #b55347; }
    QFrame#dashboardTodayMetric[metricRole="today"] QLabel#dashboardTodayMetricValue { color: #a9761a; }
    QFrame#dashboardTodayMetric[metricRole="ok"] QLabel#dashboardTodayMetricValue { color: #397854; }
    QFrame#dashboardTodayMetric[metricRole="active"] QLabel#dashboardTodayMetricValue { color: #356da7; }
    QFrame#dashboardTodayMetric[metricKind="review"] QLabel#dashboardTodayEyebrow { color: #30704a; }
    QFrame#dashboardTodayMetric[metricKind="review"] QLabel#dashboardTodayMetricValue { color: #23824b; }
    QLabel#dashboardTodayDetail {
        color: #61778d;
        font-size: 8.35pt;
        font-weight: 500;
    }
    QFrame#dashboardQuickAccess {
        background-color: transparent;
        border: none;
        border-radius: 0px;
    }
    QLabel#dashboardQuickAccessTitle {
        color: #4b6682;
        font-size: 7.9pt;
        font-weight: 900;
        letter-spacing: 0.35px;
    }
    QProgressBar#dashboardTodayProgress {
        min-height: 7px;
        max-height: 7px;
        background-color: #dce8f5;
        border: none;
        border-radius: 3px;
    }
    QProgressBar#dashboardTodayProgress::chunk {
        background-color: #3d7fd0;
        border-radius: 3px;
    }
    QFrame#dashboardTodayAction {
        background-color: #f2f7fd;
        border: 1px solid #c8dced;
        border-radius: 10px;
    }
    QFrame#dashboardTodayAction[actionRole="late"] {
        background-color: #fff8ed;
        border-color: #e7cf9d;
    }
    QFrame#dashboardTodayAction[actionRole="strategic"] {
        background-color: #f5f4fb;
        border-color: #d6d2eb;
    }
    QFrame#dashboardTodayAction[actionRole="active"] {
        background-color: #edf7f2;
        border-color: #c7dfd1;
    }
    QLabel#dashboardTodayActionTitle {
        color: #20364e;
        font-size: 10.2pt;
        font-weight: 900;
    }
    QPushButton#dashboardTodayPrimaryButton {
        background-color: #326fd3;
        color: #ffffff;
        border: 1px solid #326fd3;
        border-radius: 9px;
        font-weight: 900;
        font-size: 9.5pt;
        padding: 7px 17px;
    }
    QPushButton#dashboardTodayPrimaryButton:hover {
        background-color: #285fb5;
        border-color: #285fb5;
    }
    QPushButton#dashboardTodayButton {
        background-color: #ffffff;
        color: #32679f;
        border: 1px solid #b9cee4;
        border-radius: 8px;
        font-weight: 800;
        padding: 6px 13px;
    }
    QPushButton#dashboardTodayButton:hover {
        background-color: #eef6ff;
        border-color: #8db7e4;
        color: #245889;
    }

    /* HERO CENTRAL — modo guiado */
    QFrame#dashboardTodayAction[heroCentral="true"] {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f8fbff, stop:0.48 #eff5ff, stop:1 #f7fbff);
        border: 1px solid #bdd3ec;
        border-radius: 16px;
    }
    QFrame#dashboardTodayAction[heroCentral="true"][actionRole="late"] {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f7fbff, stop:0.52 #eef5ff, stop:1 #f9fbff);
        border-color: #9fc4ee;
    }
    QFrame#dashboardTodayAction[heroCentral="true"][actionRole="strategic"] {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fbfbff, stop:0.55 #f1f0ff, stop:1 #fafbff);
        border-color: #c8c1ef;
    }
    QFrame#dashboardTodayAction[heroCentral="true"][actionRole="active"] {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f7fbff, stop:0.52 #eef5ff, stop:1 #f7fbff);
        border-color: #bfd7ee;
    }
    QLabel#dashboardGuidedHeroEyebrow {
        color: #3a73b3; font-size: 8.3pt; font-weight: 900; letter-spacing: 1px;
    }
    QFrame#dashboardTodayAction[heroCentral="true"] QLabel#dashboardTodayActionTitle {
        color: #1a3553; font-size: 12.8pt; font-weight: 800;
    }
    QLabel#dashboardGuidedHeroDetail { color: #4f6780; font-size: 9pt; font-weight: 700; }
    QLabel#dashboardGuidedHeroGuide { color: #4f6780; font-size: 8.8pt; line-height: 1.35em; }
    QLabel#dashboardGuidedInfoTitle { color: #17365c; font-size: 9.1pt; font-weight: 900; }
    QFrame#dashboardGuidedInfoCard {
        background-color: rgba(248, 251, 255, 0.96);
        border: 1px solid #d2e1f2;
        border-radius: 12px;
    }
    QFrame#dashboardGuidedActionBox {
        background-color: rgba(232, 240, 250, 0.92);
        border: 1px solid #b7cfea;
        border-radius: 16px;
        min-width: 460px;
    }
    QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayPrimaryButton {
        background-color: #2563d9; color: #ffffff; border: 1px solid #1f57c3;
        border-radius: 12px; font-size: 11.2pt; font-weight: 900; padding: 11px 34px;
    }
    QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayPrimaryButton:hover {
        background-color: #1f57c3; border-color: #184aa9;
    }
    QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayButton {
        background-color: transparent; border: none; color: #3d6fa4;
        text-decoration: underline; font-weight: 800; padding: 4px 10px;
    }
    QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayButton:hover { color: #245889; }

    QLabel#studyScoreBreakdown { font-weight: 700; }

    /* ======================================================
       CENTRAL DE ATENÇÃO — NOTIFICAÇÕES ÚTEIS V2 / CLARO
       ====================================================== */

    QFrame#dashboardAttentionCard {
        border-radius: 9px;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"] {
        background-color: #fff9ee;
        border: 1px solid #ead9b5;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"][alertState="ok"] {
        background-color: #f5faf7;
        border-color: #d4e7db;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"][alertState="critico"] {
        background-color: #fff3f1;
        border-color: #e8cbc7;
    }

    QFrame#dashboardAttentionCard[attentionRole="pace"] {
        background-color: #f4f8fd;
        border: 1px solid #d4e2f0;
    }

    QLabel#dashboardAttentionIcon {
        font-size: 11pt;
        font-weight: 800;
        border-radius: 16px;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"] QLabel#dashboardAttentionIcon {
        background-color: #fff1cf;
        color: #ad7b1e;
        border: 1px solid #e8cf94;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"][alertState="ok"] QLabel#dashboardAttentionIcon {
        background-color: #e9f5ed;
        color: #3f7d59;
        border-color: #c9e1d1;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"][alertState="critico"] QLabel#dashboardAttentionIcon {
        background-color: #fde9e6;
        color: #b55249;
        border-color: #e8c1bd;
    }

    QFrame#dashboardAttentionCard[attentionRole="pace"] QLabel#dashboardAttentionIcon {
        background-color: #eaf3fd;
        color: #3c74b5;
        border: 1px solid #c7dcef;
    }

    QLabel#dashboardAttentionEyebrow {
        color: #768496;
        font-size: 7.5pt;
        font-weight: 700;
    }

    QLabel#dashboardAttentionTitle {
        color: #27364a;
        font-size: 9.5pt;
        font-weight: 700;
    }

    QLabel#dashboardAttentionDescription {
        color: #6b7787;
        font-size: 8.5pt;
    }

    QLabel#dashboardAttentionMeta {
        color: #7d8794;
        font-size: 8pt;
    }

    QLabel#dashboardAttentionBadge,
    QLabel#dashboardPaceBadge {
        padding: 3px 9px;
        border-radius: 8px;
        font-size: 7.5pt;
        font-weight: 700;
    }

    QLabel#dashboardAttentionBadge {
        background-color: #fff0c8;
        color: #8b6724;
        border: 1px solid #e2c986;
    }

    QFrame#dashboardAttentionCard[alertState="ok"] QLabel#dashboardAttentionBadge {
        background-color: #eaf5ee;
        color: #47785a;
        border-color: #c9e0d0;
    }

    QFrame#dashboardAttentionCard[alertState="critico"] QLabel#dashboardAttentionBadge {
        background-color: #fde9e6;
        color: #a94d45;
        border-color: #e8c1bd;
    }

    QLabel#dashboardPaceBadge {
        background-color: #e9f2fd;
        color: #3e6fa8;
        border: 1px solid #c9dced;
    }

    QFrame#dashboardAttentionFooter {
        background-color: #fbfcfe;
        border: 1px solid #e1e7ef;
        border-radius: 7px;
    }

    QLabel#dashboardAttentionFooterItem {
        color: #536173;
        font-size: 8pt;
        font-weight: 600;
    }

    QLabel#dashboardAttentionFooterHint {
        color: #8994a3;
        font-size: 7.5pt;
    }

""" + ESTILO_JORNADA_CLARO + ESTILO_DASHBOARD_MODERNO_CLARO + ESTILO_FOCO_DASHBOARD_CLARO + ESTILO_ALGORITMO_DASHBOARD_CLARO + ESTILO_BUSCA_GLOBAL_CLARO + ESTILO_PALETA_HARMONICA_DASHBOARD_CLARO + ESTILO_DESIGN_SYSTEM_DASHBOARD_CLARO + ESTILO_INTELIGENCIA_RESUMO_CLARO + ESTILO_TOPICOS_DISCIPLINA_CLARO + ESTILO_RESOLVEDOR_CLARO + ESTILO_TOPICO_DETALHES_CLARO + ESTILO_RESOLVEDOR_ELIMINADAS_CLARO + ESTILO_RESOLVEDOR_TECLADO_CLARO + ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_CLARO + ESTILO_CALENDARIO_PREVISAO_CLARO)


def stylesheet_escuro():
    return render_qss("escuro", r"""
    * {
        font-family: "Segoe UI";
        font-size: 10pt;
    }

    QMainWindow,
    QDialog,
    QWidget {
        background-color: #111827;
        color: #e5e7eb;
    }

    /* Textos e controles de seleção permanecem transparentes sobre o card.
       Evita o efeito de "quadrante" escuro atrás de cada linha de texto. */
    QLabel,
    QCheckBox,
    QRadioButton {
        background-color: transparent;
    }

    QScrollArea,
    QScrollArea > QWidget > QWidget {
        background-color: transparent;
        border: none;
    }

    QLabel#pageTitle {
        font-size: 24px;
        font-weight: 700;
        color: #f8fafc;
    }

    QLabel#pageSubtitle {
        font-size: 11pt;
        color: #94a3b8;
    }

    QLabel#sectionTitle {
        font-size: 15px;
        font-weight: 700;
        color: #f8fafc;
        padding-top: 4px;
    }

    QLabel#mutedLabel {
        color: #94a3b8;
    }

    QFrame#contextBar {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 10px;
    }


    QFrame#dashboardCenterBar {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 10px;
    }


    QFrame#calendarPanel,
    QFrame#calendarDayPanel {
        background-color: {{color:calendar.surface}};
        border: 1px solid {{color:calendar.border}};
        border-radius: 11px;
    }

    QLabel#calendarDateTitle {
        background: {{color:action.ghost}};
        color: {{color:calendar.title_text}};
        font-size: 15px;
        font-weight: 700;
    }

    QLabel#calendarCountBadge {
        background-color: {{color:calendar.badge_surface}};
        color: {{color:calendar.badge_text}};
        border: 1px solid {{color:calendar.badge_border}};
        border-radius: 7px;
        padding: 4px 8px;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#calendarLegendToday {
        color: {{color:calendar.legend_today}};
        background: {{color:action.ghost}};
        font-weight: 600;
    }

    QLabel#calendarLegendLate {
        color: {{color:calendar.legend_late}};
        background: {{color:action.ghost}};
        font-weight: 600;
    }

    QLabel#calendarLegendFuture {
        color: {{color:calendar.legend_scheduled}};
        background: {{color:action.ghost}};
        font-weight: 600;
    }

    QCalendarWidget#reviewCalendar {
        background-color: {{color:calendar.surface}};
        border: none;
    }

    QCalendarWidget#reviewCalendar QWidget#qt_calendar_navigationbar {
        background-color: {{color:calendar.navigation_surface}};
        border-radius: 8px;
    }

    QCalendarWidget#reviewCalendar QToolButton {
        background-color: {{color:action.ghost}};
        color: {{color:calendar.text}};
        border: none;
        border-radius: 6px;
        padding: 5px 8px;
        font-weight: 700;
    }

    QCalendarWidget#reviewCalendar QToolButton:hover {
        background-color: {{color:calendar.navigation_hover_surface}};
    }

    QCalendarWidget#reviewCalendar QSpinBox {
        background-color: {{color:calendar.input_surface}};
        color: {{color:calendar.text}};
        border: 1px solid {{color:calendar.input_border}};
        border-radius: 6px;
        padding: 3px 6px;
    }

    QCalendarWidget#reviewCalendar QAbstractItemView {
        background-color: {{color:calendar.surface}};
        color: {{color:calendar.text}};
        selection-background-color: {{color:calendar.selected_surface}};
        selection-color: {{color:calendar.selected_text}};
        border: none;
        outline: none;
    }

    QWidget#dashboardHeaderSide {
        background: transparent;
        border: none;
    }

    QLabel#disciplineSectionTitle {
        background: transparent;
        color: #f8fafc;
        font-size: 19px;
        font-weight: 700;
    }

    QLabel#contextLabel {
        background: transparent;
        color: #cbd5e1;
        font-weight: 700;
    }

    QLabel#queueCount {
        background: transparent;
        color: #94a3b8;
        font-size: 9pt;
        font-weight: 600;
    }

    QPushButton#subtleButton {
        min-height: 28px;
        padding: 4px 10px;
        background-color: transparent;
        color: #cbd5e1;
        border: 1px solid #475569;
        border-radius: 7px;
        font-weight: 600;
    }

    QPushButton#subtleButton:hover {
        background-color: #273449;
        border-color: #64748b;
    }


    QLabel#profileBadge {
        background-color: #172554;
        color: #93c5fd;
        border: 1px solid #1e3a8a;
        border-radius: 8px;
        padding: 5px 10px;
        font-size: 9pt;
        font-weight: 700;
    }

    QFrame#miniStat {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QLabel#miniStatLabel {
        background: transparent;
        color: #94a3b8;
        font-size: 9pt;
    }

    QLabel#miniStatValue {
        background: transparent;
        color: #f8fafc;
        font-size: 17px;
        font-weight: 700;
    }

    QFrame#filterBar {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QLabel#filterCount {
        background-color: #273449;
        color: #cbd5e1;
        border: 1px solid #334155;
        border-radius: 7px;
        padding: 5px 9px;
        font-size: 9pt;
        font-weight: 600;
    }

    QPushButton#dangerButton {
        min-height: 30px;
        padding: 6px 12px;
        background-color: #182235;
        color: #fca5a5;
        border: 1px solid #7f1d1d;
        border-radius: 8px;
        font-weight: 600;
    }

    QPushButton#dangerButton:hover {
        background-color: #3f1d27;
        border-color: #991b1b;
    }

    QPushButton#rowActionButton {
        min-height: 0px;
        padding: 1px 6px;
        background: transparent;
        color: #cbd5e1;
        border: 1px solid #475569;
        border-radius: 5px;
        font-size: 9pt;
        font-weight: 400;
    }

    QPushButton#rowActionButton:hover {
        background-color: #273449;
        border-color: #64748b;
    }


    QPushButton#sectionEditButton {
        min-height: 0px;
        padding: 5px 13px;
        background-color: #172554;
        color: #bfdbfe;
        border: 1px solid #3b82f6;
        border-radius: 8px;
        font-size: 9.5pt;
        font-weight: 700;
    }

    QPushButton#sectionEditButton:hover {
        background-color: #1e3a8a;
        border-color: #60a5fa;
        color: #dbeafe;
    }

    QPushButton#sectionEditButton:pressed {
        background-color: #1e40af;
        border-color: #93c5fd;
    }


    QFrame#dialogCard {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 11px;
    }

    QFrame#dialogCard QLabel {
        background: transparent;
    }

    QFrame#topicDomainCard {
        background-color: #172033;
        border: 1px solid #1e3a8a;
        border-radius: 10px;
    }

    QFrame#topicDomainCard QLabel {
        background: transparent;
    }

    QLabel#topicDomainTitle {
        color: #f8fafc;
        font-size: 10.5pt;
        font-weight: 800;
    }

    QLabel#topicDomainSubtitle {
        color: #94a3b8;
        font-size: 8.5pt;
    }

    QLabel#topicDomainScore {
        color: #93c5fd;
        font-size: 18px;
        font-weight: 900;
    }

    QLabel#topicDomainLevel {
        background-color: #334155;
        color: #cbd5e1;
        border-radius: 7px;
        padding: 5px 8px;
        font-size: 8.5pt;
        font-weight: 800;
    }

    QLabel#topicDomainLevel[domainLevel="critico"],
    QLabel#topicDomainLevel[domainLevel="fragil"] {
        background-color: #450a0a;
        color: #fca5a5;
    }

    QLabel#topicDomainLevel[domainLevel="desenvolvimento"],
    QLabel#topicDomainLevel[domainLevel="consolidando"] {
        background-color: #422006;
        color: #fde68a;
    }

    QLabel#topicDomainLevel[domainLevel="dominado"],
    QLabel#topicDomainLevel[domainLevel="forte"] {
        background-color: #052e16;
        color: #86efac;
    }

    QProgressBar#topicDomainBar {
        background-color: #334155;
        border: none;
        border-radius: 4px;
    }

    QProgressBar#topicDomainBar::chunk {
        background-color: #3b82f6;
        border-radius: 4px;
    }

    QFrame#topicDomainComponent {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 7px;
    }

    QLabel#topicDomainComponentLabel {
        color: #94a3b8;
        font-size: 7.8pt;
    }

    QLabel#topicDomainComponentValue {
        color: #f8fafc;
        font-size: 11pt;
        font-weight: 800;
    }

    QLabel#topicDomainEvidence {
        color: #cbd5e1;
        font-size: 8.4pt;
        font-weight: 600;
    }

    QLabel#topicDomainReasons {
        color: #94a3b8;
        font-size: 8.2pt;
    }

    QFrame#metricCard {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QLabel#metricLabel {
        background: transparent;
        color: #94a3b8;
        font-size: 9pt;
    }

    QLabel#metricValue {
        background: transparent;
        color: #f8fafc;
        font-size: 15px;
        font-weight: 700;
    }

    QLabel#fieldLabel {
        background: transparent;
        color: #94a3b8;
        font-size: 9pt;
        font-weight: 600;
    }

    QLabel#sessionBadge {
        background-color: #172554;
        color: #93c5fd;
        border: 1px solid #1e3a8a;
        border-radius: 8px;
        padding: 5px 9px;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#resultValue {
        background-color: #172554;
        color: #93c5fd;
        border: 1px solid #1e3a8a;
        border-radius: 8px;
        font-size: 17px;
        font-weight: 800;
        padding: 4px 8px;
    }

    QFrame#suggestionCard {
        background-color: #172033;
        border: 1px solid #1e3a8a;
        border-radius: 11px;
    }

    QFrame#suggestionCard QLabel {
        background: transparent;
    }

    QLabel#suggestionStrong {
        background: transparent;
        color: #93c5fd;
        font-size: 12pt;
        font-weight: 700;
    }

    QLabel#infoNotice {
        background-color: #422006;
        color: #fde68a;
        border: 1px solid #854d0e;
        border-radius: 9px;
        padding: 8px 10px;
        font-size: 9pt;
    }

    QTextEdit#detailsReadOnly {
        background-color: #172033;
        border: 1px solid #334155;
    }


    QPushButton#dashboardSectionToggle,
    QPushButton#dashboardSectionToggleCentered {
        background: transparent;
        color: #f8fafc;
        border: none;
        border-radius: 5px;
        padding: 1px 4px;
        font-size: 11pt;
        font-weight: 800;
        text-align: left;
    }

    QPushButton#dashboardSectionToggle:hover,
    QPushButton#dashboardSectionToggleCentered:hover {
        background-color: #243247;
        color: #93c5fd;
    }

    QPushButton#dashboardSectionToggleCentered {
        text-align: center;
    }

    QPushButton#dashboardSectionToggle[expanded="false"],
    QPushButton#dashboardSectionToggleCentered[expanded="false"] {
        color: #cbd5e1;
    }

    QWidget#dashboardCollapsibleContent {
        background: transparent;
    }

    QFrame#syllabusProgressPanel {
        background-color: #121c2d;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QFrame#syllabusProgressPanel QLabel,
    QFrame#syllabusDashboardCoverage QLabel,
    QFrame#syllabusDashboardStat QLabel {
        background: transparent;
    }

    QLabel#syllabusDashboardTitle {
        color: #f8fafc;
        font-size: 11pt;
        font-weight: 800;
    }

    QFrame#syllabusDashboardCoverage,
    QFrame#syllabusDashboardStat {
        background-color: #1f2937;
        border: 1px solid #334155;
        border-radius: 8px;
    }

    QLabel#syllabusDashboardMetricLabel {
        color: #94a3b8;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#syllabusDashboardMetricValue {
        color: #f8fafc;
        font-size: 14px;
        font-weight: 800;
    }

    QLabel#syllabusDashboardHint {
        color: #94a3b8;
        font-size: 8pt;
    }

    QPushButton#syllabusOpenButton {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #60a5fa;
        border-radius: 7px;
        padding: 6px 12px;
        font-weight: 700;
    }

    QPushButton#syllabusOpenButton:hover {
        background-color: #1d4ed8;
    }

    QProgressBar#syllabusDashboardBar {
        background-color: #334155;
        border: none;
        border-radius: 4px;
    }

    QProgressBar#syllabusDashboardBar::chunk {
        background-color: #60a5fa;
        border-radius: 4px;
    }

    QFrame#questionReviewIntegrationCard {
        background-color: #163523;
        border: 1px solid #166534;
        border-radius: 8px;
    }

    QLabel#questionReviewIntegrationTitle {
        color: #bbf7d0;
        font-size: 9.5pt;
        font-weight: 800;
    }

    QLabel#questionReviewIntegrationText {
        color: #86efac;
        font-size: 8.5pt;
    }

    QFrame#questionsInsightsBar {
        background-color: #121c2d;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QFrame#questionsInsightsBar QLabel {
        background: transparent;
    }

    QLabel#questionsInsightsTitle {
        color: #f8fafc;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#questionsInsightsDescription {
        color: #94a3b8;
        font-size: 8.5pt;
    }

    QLabel#questionsInsightsSummary {
        color: #cbd5e1;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QPushButton#questionsHistoryButton {
        background-color: #1f2937;
        color: #bfdbfe;
        border: 1px solid #3b82f6;
        border-radius: 7px;
        padding: 6px 11px;
        font-weight: 800;
    }

    QPushButton#questionsHistoryButton:hover {
        background-color: #172554;
        border-color: #60a5fa;
    }

    QFrame#questionHistoryStat,
    QFrame#questionHistoryFilterCard {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QTabWidget#questionHistoryTabs::pane {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 9px;
        top: -1px;
    }

    QTabWidget#questionHistoryTabs QTabBar::tab {
        background-color: #273449;
        color: #cbd5e1;
        border: 1px solid #334155;
        padding: 8px 18px;
        min-width: 120px;
        font-weight: 800;
    }

    QTabWidget#questionHistoryTabs QTabBar::tab:selected {
        background-color: #2563eb;
        color: #ffffff;
        border-color: #60a5fa;
    }

    QTableWidget#questionHistoryTable,
    QTableWidget#questionErrorBookTable {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QLabel#questionErrorBookRule {
        background-color: #1f2937;
        color: #94a3b8;
        border: 1px solid #334155;
        border-radius: 7px;
        padding: 7px 9px;
        font-size: 8.5pt;
    }

    QPushButton#questionRetryButton {
        background-color: #1f2937;
        color: #cbd5e1;
        border: 1px solid #475569;
        border-radius: 7px;
        padding: 6px 10px;
        font-weight: 700;
    }

    QPushButton#questionRetryButton:hover {
        background-color: #273449;
        border-color: #64748b;
    }

    QPushButton#questionReviewErrorsButton {
        background-color: #991b1b;
        color: #ffffff;
        border: 1px solid #ef4444;
        border-radius: 7px;
        padding: 6px 11px;
        font-weight: 800;
    }

    QPushButton#questionReviewErrorsButton:hover {
        background-color: #b91c1c;
    }

    QFrame#questionsHeroActions {
        background-color: #121c2d;
        border: 1px solid #334155;
        border-radius: 11px;
    }

    QFrame#questionsHeroActions QLabel {
        background: transparent;
    }

    QPushButton#questionsAnalysisButton,
    QPushButton#questionsAnalysisCompleteButton {
        background-color: #2d2415;
        color: #fbbf24;
        border: 1px solid #b45309;
        border-radius: 8px;
        padding: 7px 12px;
        font-weight: 800;
    }

    QPushButton#questionsAnalysisButton:hover,
    QPushButton#questionsAnalysisCompleteButton:hover {
        background-color: #3a2d17;
        border-color: #f59e0b;
    }

    QPushButton#questionsAnalysisButton:checked {
        background-color: #b45309;
        color: #fff7ed;
        border-color: #fbbf24;
    }

    QPushButton#questionsAnalysisButton:disabled,
    QPushButton#questionsAnalysisCompleteButton:disabled {
        background-color: #1f2937;
        color: #64748b;
        border-color: #475569;
    }

    QToolButton#questionsImportMenuButton,
    QToolButton#questionsMoreMenuButton {
        background-color: #182235;
        color: #cbd5e1;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 7px 12px;
        font-weight: 700;
    }

    QToolButton#questionsImportMenuButton:hover,
    QToolButton#questionsMoreMenuButton:hover {
        background-color: #1f2937;
        border-color: #64748b;
        color: #93c5fd;
    }

    QFrame#questionsInventoryStrip {
        background-color: #121c2d;
        border: 1px solid #334155;
        border-radius: 11px;
    }

    QFrame#questionsInventoryItem {
        background: transparent;
        border: none;
    }

    QLabel#questionsInventoryValue {
        background: transparent;
        color: #a5b4fc;
        font-size: 14pt;
        font-weight: 900;
    }

    QLabel#questionsInventoryLabel {
        background: transparent;
        color: #94a3b8;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QFrame#questionsInventoryDivider {
        background-color: #334155;
        border: none;
    }

    QFrame#questionsWorkspaceCard {
        background-color: #121c2d;
        border: 1px solid #334155;
        border-radius: 12px;
    }

    QFrame#questionsWorkspaceCard QFrame#questionsFoundationNotice {
        background: transparent;
        border: none;
    }

    QFrame#questionsWorkspaceCard QFrame#questionsFilterBar {
        background-color: #111827;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QLabel#questionsHeroTitle {
        color: #f8fafc;
        font-size: 10.5pt;
        font-weight: 800;
    }

    QLabel#questionsHeroDescription {
        color: #94a3b8;
        font-size: 8.5pt;
    }

    QFrame#questionsHeroDivider {
        background-color: #334155;
        border: none;
        margin-top: 3px;
        margin-bottom: 3px;
    }

    QPushButton#questionsSolveHeroButton {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #60a5fa;
        border-radius: 9px;
        padding: 10px 18px;
        font-size: 10.5pt;
        font-weight: 800;
    }

    QPushButton#questionsSolveHeroButton:hover {
        background-color: #1d4ed8;
        border-color: #93c5fd;
    }

    QPushButton#questionsSolveHeroButton:disabled {
        background-color: #273449;
        color: #64748b;
        border-color: #334155;
    }

    QPushButton#questionsNewHeroButton {
        background-color: #1f2937;
        color: #bfdbfe;
        border: 1px solid #3b82f6;
        border-radius: 9px;
        padding: 10px 18px;
        font-size: 10.5pt;
        font-weight: 800;
    }

    QPushButton#questionsNewHeroButton:hover {
        background-color: #172554;
        border-color: #60a5fa;
    }

    QPushButton#questionsSolveButton {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #60a5fa;
        border-radius: 7px;
        padding: 6px 11px;
        font-weight: 800;
    }

    QPushButton#questionsSolveButton:hover {
        background-color: #1d4ed8;
    }

    QPushButton#questionsSolveButton:disabled {
        background-color: #273449;
        color: #64748b;
        border-color: #334155;
    }

    QLabel#questionSmartStrategy {
        background-color: #172554;
        color: #bfdbfe;
        border: 1px solid #1d4ed8;
        border-radius: 7px;
        padding: 8px 10px;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QPushButton#smartReviewDashboardButton {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #60a5fa;
        border-radius: 8px;
        padding: 7px 12px;
        font-weight: 800;
    }

    QPushButton#smartReviewDashboardButton:hover {
        background-color: #1d4ed8;
        border-color: #93c5fd;
    }

    QPushButton#smartReviewDashboardButton:disabled {
        background-color: #273449;
        color: #64748b;
        border-color: #334155;
    }

    QLabel#questionIntegrityNotice {
        background-color: #172554;
        color: #bfdbfe;
        border: 1px solid #1d4ed8;
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 8.7pt;
        font-weight: 600;
    }

    QLabel#questionSnapshotNotice {
        background-color: #052e16;
        color: #bbf7d0;
        border: 1px solid #15803d;
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 8.7pt;
        font-weight: 600;
    }

    QLabel#questionSnapshotNotice[snapshotState="legado"] {
        background-color: #422006;
        color: #fde68a;
        border-color: #a16207;
    }

    QLabel#questionArchivedNotice {
        background-color: #1f2937;
        color: #94a3b8;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 8.7pt;
        font-weight: 600;
    }

    QFrame#adaptiveSessionConfigCard,
    QFrame#adaptiveTopicsCard,
    QFrame#adaptivePreviewCard {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QFrame#adaptiveSessionConfigCard QLabel,
    QFrame#adaptiveTopicsCard QLabel,
    QFrame#adaptivePreviewCard QLabel {
        background: transparent;
    }

    QLabel#adaptiveSectionTitle {
        color: #f8fafc;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#adaptivePreviewSummary {
        color: #93c5fd;
        font-size: 9pt;
        font-weight: 800;
    }

    QLabel#adaptivePreviewReasons {
        color: #cbd5e1;
        font-size: 8.6pt;
        font-weight: 600;
    }

    QLabel#adaptivePreviewNotice {
        background-color: #172554;
        color: #bfdbfe;
        border: 1px solid #1e3a8a;
        border-radius: 7px;
        padding: 6px 8px;
        font-size: 8.2pt;
    }

    QPushButton#adaptiveSessionStartButton,
    QPushButton#adaptiveDashboardButton,
    QPushButton#questionsAdaptiveButton {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #2563eb;
        border-radius: 8px;
        padding: 7px 12px;
        font-weight: 800;
    }

    QPushButton#adaptiveSessionStartButton:hover,
    QPushButton#adaptiveDashboardButton:hover,
    QPushButton#questionsAdaptiveButton:hover {
        background-color: #1d4ed8;
        border-color: #60a5fa;
    }

    QFrame#questionsAdaptiveBar {
        background-color: #172033;
        border: 1px solid #1e3a8a;
        border-radius: 9px;
    }

    QFrame#questionsAdaptiveBar QLabel {
        background: transparent;
    }

    QLabel#questionsAdaptiveTitle {
        color: #93c5fd;
        font-size: 9.5pt;
        font-weight: 800;
    }

    QLabel#questionsAdaptiveDescription {
        color: #94a3b8;
        font-size: 8.4pt;
    }

    QFrame#adaptiveSummaryCard {
        background-color: #172033;
        border: 1px solid #1e3a8a;
        border-radius: 9px;
    }

    QFrame#adaptiveSummaryCard QLabel {
        background: transparent;
    }

    QLabel#adaptiveSummaryTitle {
        color: #93c5fd;
        font-size: 9.5pt;
        font-weight: 800;
    }

    QLabel#adaptiveSummaryText {
        color: #cbd5e1;
        font-size: 8.5pt;
    }

    QFrame#effectivenessFilterBar {
        background-color: #172033;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QFrame#effectivenessFilterBar QLabel {
        background: transparent;
        color: #cbd5e1;
    }

    QLabel#effectivenessTrackingNotice {
        color: #94a3b8;
        font-size: 8.2pt;
    }

    QFrame#effectivenessStatCard {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QFrame#effectivenessStatCard QLabel {
        background: transparent;
    }

    QLabel#effectivenessStatLabel {
        color: #94a3b8;
        font-size: 8.6pt;
        font-weight: 700;
    }

    QLabel#effectivenessStatValue {
        color: #f8fafc;
        font-size: 16px;
        font-weight: 900;
    }

    QLabel#effectivenessStatHint {
        color: #64748b;
        font-size: 8pt;
    }

    QFrame#effectivenessCalibrationCard {
        background-color: #172033;
        border: 1px solid #1e3a8a;
        border-radius: 9px;
    }

    QFrame#effectivenessCalibrationCard QLabel {
        background: transparent;
    }

    QLabel#effectivenessCalibrationTitle {
        color: #93c5fd;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#effectivenessCalibrationBadge {
        background-color: #1f2937;
        color: #cbd5e1;
        border: 1px solid #475569;
        border-radius: 7px;
        padding: 4px 8px;
        font-size: 8.3pt;
        font-weight: 800;
    }

    QLabel#effectivenessCalibrationBadge[calibrationLevel="inicial"],
    QLabel#effectivenessCalibrationBadge[calibrationLevel="moderada"] {
        background-color: #422006;
        color: #fde68a;
        border-color: #a16207;
    }

    QLabel#effectivenessCalibrationBadge[calibrationLevel="forte"] {
        background-color: #052e16;
        color: #86efac;
        border-color: #15803d;
    }

    QLabel#effectivenessCalibrationText {
        color: #cbd5e1;
        font-size: 8.6pt;
    }

    QLabel#effectivenessWeights {
        color: #93c5fd;
        font-size: 8.4pt;
        font-weight: 700;
    }

    QLabel#effectivenessObservations {
        color: #94a3b8;
        font-size: 8.4pt;
    }

    QFrame#effectivenessImpactCard {
        background-color: #172033;
        border: 1px solid #1e3a8a;
        border-radius: 9px;
    }

    QFrame#effectivenessImpactCard QLabel {
        background: transparent;
    }

    QLabel#effectivenessImpactTitle {
        color: #93c5fd;
        font-size: 9.5pt;
        font-weight: 800;
    }

    QFrame#effectivenessImpactMetric {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 7px;
    }

    QLabel#effectivenessImpactLabel {
        color: #94a3b8;
        font-size: 8pt;
    }

    QLabel#effectivenessImpactValue {
        color: #f8fafc;
        font-size: 9.5pt;
        font-weight: 800;
    }

    QLabel#effectivenessImpactFooter {
        color: #94a3b8;
        font-size: 8.2pt;
    }

    QPushButton#effectivenessOpenButton,
    QPushButton#questionsEffectivenessButton {
        background-color: #1f2937;
        color: #bfdbfe;
        border: 1px solid #3b82f6;
        border-radius: 7px;
        padding: 6px 10px;
        font-weight: 700;
    }

    QPushButton#effectivenessOpenButton:hover,
    QPushButton#questionsEffectivenessButton:hover {
        background-color: #172554;
        border-color: #60a5fa;
    }

    QFrame#mockExamConfigCard {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QFrame#mockExamConfigCard QLabel {
        background: transparent;
        color: #cbd5e1;
    }

    QLabel#mockExamRuleNotice {
        background-color: #422006;
        color: #fde68a;
        border: 1px solid #a16207;
        border-radius: 8px;
        padding: 7px 9px;
        font-size: 8.4pt;
        font-weight: 600;
    }

    QLabel#mockExamSectionTitle {
        color: #f8fafc;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#mockExamPreviewSummary {
        color: #c4b5fd;
        font-size: 9pt;
        font-weight: 800;
    }

    QLabel#mockExamVighnaExplanation {
        color: #94a3b8;
        font-size: 8.4pt;
    }

    QPushButton#mockExamStartButton,
    QPushButton#mockExamDashboardButton {
        background-color: #7c3aed;
        color: #ffffff;
        border: 1px solid #a78bfa;
        border-radius: 8px;
        padding: 7px 12px;
        font-weight: 800;
    }

    QPushButton#mockExamStartButton:hover,
    QPushButton#mockExamDashboardButton:hover {
        background-color: #6d28d9;
        border-color: #c4b5fd;
    }

    QPushButton#questionsMockExamButton {
        background-color: #1f2937;
        color: #ddd6fe;
        border: 1px solid #8b5cf6;
        border-radius: 7px;
        padding: 6px 10px;
        font-weight: 800;
    }

    QPushButton#questionsMockExamButton:hover {
        background-color: #2e1065;
        border-color: #a78bfa;
    }

    QLabel#mockExamTimer {
        background-color: #2e1065;
        color: #ddd6fe;
        border: 1px solid #7c3aed;
        border-radius: 7px;
        padding: 5px 8px;
        font-size: 9pt;
        font-weight: 900;
    }

    QLabel#mockExamResultSectionTitle {
        color: #f8fafc;
        font-size: 9.5pt;
        font-weight: 800;
    }

    QLabel#mockExamCorrectionNotice {
        background-color: #2e1065;
        color: #ddd6fe;
        border: 1px solid #7c3aed;
        border-radius: 8px;
        padding: 7px 9px;
        font-size: 8.4pt;
        font-weight: 600;
    }

    QFrame#questionSessionConfigCard,
    QFrame#questionSessionSummaryCard {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QLabel#questionSessionProfile,
    QLabel#questionSessionAvailability {
        background-color: #1f2937;
        color: #cbd5e1;
        border: 1px solid #334155;
        border-radius: 7px;
        padding: 7px 9px;
        font-weight: 700;
    }

    QLabel#questionSessionAvailability[availabilityState="ok"] {
        background-color: #163523;
        color: #86efac;
        border-color: #166534;
    }

    QLabel#questionSessionAvailability[availabilityState="empty"] {
        background-color: #431407;
        color: #fdba74;
        border-color: #9a3412;
    }

    QLabel#questionSessionProgressText {
        color: #cbd5e1;
        font-weight: 800;
    }

    QProgressBar#questionSessionProgress {
        background-color: #334155;
        border: none;
        border-radius: 3px;
    }

    QProgressBar#questionSessionProgress::chunk {
        background-color: #60a5fa;
        border-radius: 3px;
    }

    QFrame#questionSessionMiniStat {
        background-color: #1f2937;
        border: 1px solid #334155;
        border-radius: 7px;
    }

    QLabel#questionSessionMiniLabel {
        color: #94a3b8;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#questionSessionMiniValue {
        color: #f8fafc;
        font-size: 10pt;
        font-weight: 800;
    }

    QPushButton#questionSessionEndButton {
        background-color: #3f1218;
        color: #fecaca;
        border: 1px solid #991b1b;
        border-radius: 7px;
        padding: 6px 10px;
        font-weight: 700;
    }

    QPushButton#questionSessionEndButton:hover {
        background-color: #57151d;
    }

    QPushButton#questionSessionSkipButton {
        background-color: #1f2937;
        color: #cbd5e1;
        border: 1px solid #475569;
        border-radius: 7px;
        padding: 6px 12px;
        font-weight: 700;
    }

    QPushButton#questionSessionSkipButton:hover {
        background-color: #273449;
    }

    QScrollArea#questionSolverScroll {
        background: transparent;
        border: none;
    }

    QWidget#questionSolverContent {
        background: transparent;
    }

    QLabel#questionSolverMeta {
        color: #94a3b8;
        font-size: 9pt;
        font-weight: 700;
    }

    QFrame#questionSolverStatementCard {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QLabel#questionSolverStatement {
        color: #f8fafc;
        font-size: 11pt;
    }

    QFrame#questionSolverAlternative {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QFrame#questionSolverAlternative[answerState="correta"] {
        background-color: #163523;
        border-color: #22c55e;
    }

    QFrame#questionSolverAlternative[answerState="errada"] {
        background-color: #3f1218;
        border-color: #ef4444;
    }

    QRadioButton#questionSolverRadio {
        color: {{color:answer.indicator_text}};
        font-weight: 800;
        spacing: 5px;
    }

    QLabel#questionSolverAlternativeText {
        color: {{color:answer.normal_text}};
        font-size: 10pt;
    }

    QFrame#questionSolverAlternative[eliminated="true"][answerState="normal"] {
        background-color: #0b1220;
        border: 1px dashed #475569;
    }

    QLabel#questionSolverAlternativeText[eliminated="true"],
    QRadioButton#questionSolverRadio[eliminated="true"] {
        color: #52657a;
    }

    QToolButton#questionSolverEliminateButton:checked {
        background-color: #1f2937;
        color: #94a3b8;
        border: 1px solid #475569;
    }

    QToolButton#questionSolverEliminateButton {
        background: transparent;
        color: {{color:answer.eliminate_text}};
        border: none;
        border-radius: 5px;
        font-size: 11pt;
        padding: 0;
    }

    QToolButton#questionSolverEliminateButton:hover {
        background-color: {{color:answer.eliminate_hover_surface}};
        color: {{color:answer.eliminate_hover_text}};
    }

    QToolButton#questionSolverEliminateButton:checked {
        background-color: #334155;
        color: #e2e8f0;
    }

    QToolButton#questionSolverEliminateButton:disabled {
        color: {{color:answer.disabled_text}};
    }

    QCheckBox#questionSessionDoubt {
        background: transparent;
        color: #cbd5e1;
        font-weight: 700;
        spacing: 9px;
        padding: 4px 0;
    }

    QCheckBox#questionSessionDoubt:checked {
        color: #93c5fd;
    }

    QCheckBox#questionSessionDoubt::indicator {
        background-color: #111827;
        border: 2px solid #94a3b8;
        border-radius: 5px;
        width: 20px;
        height: 20px;
    }

    QCheckBox#questionSessionDoubt::indicator:hover {
        border-color: #60a5fa;
    }

    QCheckBox#questionSessionDoubt::indicator:checked {
        background-color: #3b82f6;
        border-color: #93c5fd;
    }

    QCheckBox#questionSessionDoubt::indicator:disabled {
        background-color: #1f2937;
        border-color: #475569;
    }

    QCheckBox#questionSessionAnalysisFlag {
        background: transparent;
        color: #94a3b8;
        font-weight: 600;
        spacing: 7px;
        padding: 4px 8px;
    }

    QCheckBox#questionSessionAnalysisFlag:checked {
        color: #fbbf24;
        font-weight: 700;
    }

    QCheckBox#questionSessionAnalysisFlag::indicator {
        background-color: #111827;
        border: 2px solid #64748b;
        border-radius: 4px;
        width: 16px;
        height: 16px;
    }

    QCheckBox#questionSessionAnalysisFlag::indicator:hover {
        border-color: #f59e0b;
    }

    QCheckBox#questionSessionAnalysisFlag::indicator:checked {
        background-color: #d97706;
        border-color: #fbbf24;
    }

    QFrame#questionSessionActionPanel {
        background: transparent;
        border: none;
    }

    QFrame#questionSolverFeedback {
        background-color: {{color:answer.explanation_surface}};
        border: 1px solid {{color:answer.explanation_border}};
        border-radius: 9px;
    }

    QFrame#questionSolverFeedback[resultState="correta"] {
        background-color: #163523;
        border-color: #22c55e;
    }

    QFrame#questionSolverFeedback[resultState="errada"] {
        background-color: #3f1218;
        border-color: #ef4444;
    }

    QLabel#questionSolverFeedbackTitle {
        color: #f8fafc;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#questionSolverExplanation {
        color: {{color:answer.explanation_text}};
        font-size: 9.5pt;
    }

    QLabel#questionSessionSummaryDetail {
        background-color: #172554;
        color: #bfdbfe;
        border: 1px solid #1d4ed8;
        border-radius: 7px;
        padding: 7px 9px;
        font-weight: 700;
    }

    QTableWidget#questionSessionSummaryTable {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QPushButton#questionsNavButton {
        background-color: #172554;
        color: #bfdbfe;
        border: 1px solid #1d4ed8;
        border-radius: 7px;
        padding: 6px 11px;
        font-weight: 800;
    }

    QPushButton#questionsNavButton:hover {
        background-color: #1e3a8a;
        border-color: #60a5fa;
    }

    QFrame#questionsFoundationNotice {
        background-color: #172554;
        border: 1px solid #1d4ed8;
        border-radius: 8px;
    }

    QLabel#questionsFoundationText {
        background: transparent;
        color: #dbeafe;
        font-size: 9pt;
        font-weight: 600;
    }

    QFrame#questionsFilterBar {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QTableWidget#questionsTable {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 9px;
        gridline-color: transparent;
        font-size: 9pt;
    }

    QTableWidget#questionsTable QHeaderView::section {
        padding-left: 6px;
        padding-right: 6px;
    }

    QTabWidget#promptLibraryTabs::pane {
        border: 1px solid #334155;
        border-radius: 9px;
        background-color: #111827;
        top: -1px;
    }

    QTabWidget#promptLibraryTabs QTabBar::tab {
        background-color: #1f2937;
        color: #94a3b8;
        border: 1px solid #334155;
        border-bottom: none;
        padding: 8px 15px;
        margin-right: 3px;
        font-weight: 700;
    }

    QTabWidget#promptLibraryTabs QTabBar::tab:selected {
        background-color: #182235;
        color: #93c5fd;
    }

    QLabel#promptProtocolIntro {
        background-color: #172554;
        color: #bfdbfe;
        border: 1px solid #1d4ed8;
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 8.5pt;
        font-weight: 600;
    }

    QFrame#promptProtocolCard {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QLabel#promptProtocolTitle {
        color: #f8fafc;
        font-size: 11pt;
        font-weight: 800;
    }

    QLabel#promptProtocolDescription {
        color: #94a3b8;
        font-size: 8.7pt;
    }

    QLabel#promptProtocolBadge {
        background-color: #064e3b;
        color: #a7f3d0;
        border: 1px solid #047857;
        border-radius: 6px;
        padding: 4px 8px;
        font-size: 7.8pt;
        font-weight: 800;
    }

    QLabel#promptProtocolUsage {
        background-color: #431407;
        color: #fed7aa;
        border: 1px solid #9a3412;
        border-radius: 7px;
        padding: 7px 9px;
        font-size: 8.5pt;
    }

    QTextEdit#promptProtocolEditor {
        background-color: #111827;
        color: #e2e8f0;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 9px;
        font-family: Consolas;
        font-size: 9pt;
    }

    QPushButton#promptProtocolCopyButton {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #60a5fa;
        border-radius: 7px;
        padding: 7px 12px;
        font-weight: 800;
    }

    QPushButton#promptProtocolCopyButton:hover {
        background-color: #1d4ed8;
    }

    QPushButton#promptProtocolDuplicateButton {
        background-color: #1f2937;
        color: #cbd5e1;
        border: 1px solid #475569;
        border-radius: 7px;
        padding: 7px 12px;
        font-weight: 700;
    }

    QPushButton#promptProtocolDuplicateButton:hover {
        background-color: #273449;
        border-color: #64748b;
    }

    QLabel#promptProtocolStatus {
        color: #94a3b8;
        font-size: 8.2pt;
        font-weight: 600;
    }

    QPushButton#questionsPromptsButton {
        background-color: #431407;
        color: #fed7aa;
        border: 1px solid #9a3412;
        border-radius: 7px;
        padding: 6px 11px;
        font-weight: 800;
    }

    QPushButton#questionsPromptsButton:hover {
        background-color: #7c2d12;
        border-color: #fb923c;
    }

    QLabel#promptLibraryHint {
        background-color: #1f2937;
        color: #94a3b8;
        border: 1px solid #334155;
        border-radius: 7px;
        padding: 7px 9px;
        font-size: 8.5pt;
    }

    QFrame#promptLibraryFilter,
    QFrame#promptLibraryListCard,
    QFrame#promptLibraryEditorCard {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QLabel#promptLibrarySectionTitle {
        color: #f8fafc;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#promptLibraryTextLabel {
        color: #cbd5e1;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#promptLibraryStatus {
        color: #94a3b8;
        font-size: 8.5pt;
        font-weight: 600;
    }

    QTableWidget#promptLibraryTable {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QTextEdit#promptLibraryEditor {
        background-color: #111827;
        color: #f8fafc;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 8px;
        font-family: Consolas;
        font-size: 9pt;
    }

    QPushButton#promptNewButton {
        background-color: #172554;
        color: #bfdbfe;
        border: 1px solid #1d4ed8;
        border-radius: 7px;
        padding: 6px 9px;
        font-weight: 800;
    }

    QPushButton#promptNewButton:hover {
        background-color: #1e3a8a;
        border-color: #60a5fa;
    }

    QPushButton#promptCopyButton {
        background-color: #431407;
        color: #fed7aa;
        border: 1px solid #c2410c;
        border-radius: 7px;
        padding: 7px 11px;
        font-weight: 800;
    }

    QPushButton#promptCopyButton:hover {
        background-color: #7c2d12;
    }

    QPushButton#questionsPdfImportButton {
        background-color: #32174d;
        color: #e9d5ff;
        border: 1px solid #7e22ce;
        border-radius: 7px;
        padding: 6px 11px;
        font-weight: 800;
    }

    QPushButton#questionsPdfImportButton:hover {
        background-color: #4c1d66;
        border-color: #c084fc;
    }

    QFrame#vpqImportStatus {
        background-color: #1f2937;
        border: 1px solid #475569;
        border-radius: 9px;
    }

    QFrame#vpqImportStatus[vpqState="integro"] {
        background-color: #052e16;
        border-color: #15803d;
    }

    QFrame#vpqImportStatus[vpqState="aviso"] {
        background-color: #422006;
        border-color: #a16207;
    }

    QFrame#vpqImportStatus[vpqState="revisao"] {
        background-color: #450a0a;
        border-color: #b91c1c;
    }

    QLabel#vpqImportBadge {
        background-color: #2563eb;
        color: #ffffff;
        border-radius: 6px;
        padding: 4px 8px;
        font-size: 8pt;
        font-weight: 800;
    }

    QLabel#vpqImportResult {
        color: #cbd5e1;
        font-size: 9pt;
        font-weight: 800;
    }

    QLabel#vpqImportResult[vpqState="integro"] {
        color: #86efac;
    }

    QLabel#vpqImportResult[vpqState="aviso"] {
        color: #fde68a;
    }

    QLabel#vpqImportResult[vpqState="revisao"] {
        color: #fca5a5;
    }

    QLabel#vpqImportMeta {
        color: #cbd5e1;
        font-size: 8.7pt;
        font-weight: 700;
    }

    QLabel#vpqImportLink {
        color: #94a3b8;
        font-size: 8.5pt;
        font-weight: 600;
    }

    QLabel#vpqImportLink[linkState="ok"] {
        color: #86efac;
    }

    QLabel#vpqImportLink[linkState="warning"] {
        color: #fde68a;
    }

    QLabel#vpqImportDetails {
        color: #cbd5e1;
        font-size: 8.4pt;
    }

    QFrame#pdfImportSummary,
    QFrame#pdfImportDefaults {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QLabel#pdfImportFile {
        color: #f8fafc;
        font-weight: 800;
    }

    QLabel#pdfImportMeta {
        color: #94a3b8;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#pdfImportHint {
        background-color: #1f2937;
        color: #94a3b8;
        border: 1px solid #334155;
        border-radius: 7px;
        padding: 7px 9px;
        font-size: 8.5pt;
    }

    QTableWidget#pdfImportTable {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QComboBox#pdfTopicCombo,
    QComboBox#pdfAnswerCombo {
        min-height: 27px;
    }

    QTextEdit#pdfExtractedText {
        font-family: Consolas;
        font-size: 9pt;
    }

    QTextEdit#textQuestionImportEditor {
        background-color: #111827;
        color: #e5edf7;
        border: 1px solid #334155;
        border-radius: 9px;
        padding: 10px;
        font-family: Consolas;
        font-size: 9pt;
        selection-background-color: #1d4ed8;
    }

    QTextEdit#textQuestionImportEditor:focus {
        border: 1px solid #4f86c8;
    }

    QPushButton#questionsImportButton {
        background-color: #163523;
        color: #86efac;
        border: 1px solid #166534;
        border-radius: 7px;
        padding: 6px 11px;
        font-weight: 800;
    }

    QPushButton#questionsImportButton:hover {
        background-color: #14532d;
        border-color: #22c55e;
    }

    QLabel#questionIntegrityNotice {
        background-color: #172554;
        color: #bfdbfe;
        border: 1px solid #1d4ed8;
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 8.7pt;
        font-weight: 600;
    }

    QLabel#questionSnapshotNotice {
        background-color: #052e16;
        color: #bbf7d0;
        border: 1px solid #15803d;
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 8.7pt;
        font-weight: 600;
    }

    QLabel#questionSnapshotNotice[snapshotState="legado"] {
        background-color: #422006;
        color: #fde68a;
        border-color: #a16207;
    }

    QLabel#questionArchivedNotice {
        background-color: #1f2937;
        color: #94a3b8;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 8.7pt;
        font-weight: 600;
    }

    QScrollArea#questionEditorScroll,
    QScrollArea#questionViewerScroll {
        background: transparent;
        border: none;
    }

    QWidget#questionEditorContent {
        background: transparent;
    }

    QFrame#questionEditorCard,
    QFrame#questionViewerCard,
    QFrame#questionAlternative,
    QFrame#questionExplanationCard {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QFrame#questionCorrectAlternative {
        background-color: #163523;
        border: 1px solid #22c55e;
        border-radius: 9px;
    }

    QLabel#questionEditorSectionTitle {
        color: #f8fafc;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#questionAlternativeLetter {
        color: #cbd5e1;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#questionAlternativeText {
        background: transparent;
        color: #e5e7eb;
        font-size: 10pt;
    }

    QLabel#questionViewerMeta,
    QLabel#questionViewerPath,
    QLabel#questionViewerSource {
        color: #94a3b8;
        font-size: 9pt;
        font-weight: 600;
    }

    QLabel#questionViewerStatement {
        color: #f8fafc;
        font-size: 10.5pt;
    }

    QLabel#questionCorrectBadge {
        background-color: #14532d;
        color: #bbf7d0;
        border: 1px solid #22c55e;
        border-radius: 7px;
        padding: 3px 7px;
        font-size: 8pt;
        font-weight: 800;
    }

    QFrame#syllabusForecastStrip {
        background-color: #172554;
        border: 1px solid #1d4ed8;
        border-radius: 8px;
    }

    QFrame#syllabusForecastStrip QLabel {
        background: transparent;
    }

    QLabel#syllabusForecastIcon {
        color: #93c5fd;
        font-size: 14pt;
        font-weight: 800;
    }

    QLabel#syllabusForecastText {
        color: #dbeafe;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#syllabusForecastSummary {
        color: #bfdbfe;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QPushButton#syllabusForecastButton {
        background-color: #1e3a8a;
        color: #ffffff;
        border: 1px solid #60a5fa;
        border-radius: 7px;
        padding: 5px 10px;
        font-weight: 700;
    }

    QPushButton#syllabusForecastButton:hover {
        background-color: #1d4ed8;
    }

    QFrame#syllabusForecastCard {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QFrame#syllabusForecastCard QLabel,
    QFrame#syllabusForecastMetricCard QLabel {
        background: transparent;
    }

    QFrame#syllabusForecastMetricCard {
        background-color: #1f2937;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QLabel#syllabusForecastMetricTitle {
        color: #e2e8f0;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#syllabusForecastBigValue {
        color: #f8fafc;
        font-size: 18px;
        font-weight: 800;
    }

    QLabel#syllabusForecastDetail {
        color: #94a3b8;
        font-size: 8.5pt;
    }

    QLabel#syllabusForecastDate {
        color: #93c5fd;
        font-size: 9pt;
        font-weight: 800;
    }

    QLabel#syllabusForecastStatus,
    QLabel#syllabusForecastBase {
        background-color: #273449;
        color: #cbd5e1;
        border: 1px solid #334155;
        border-radius: 7px;
        padding: 5px 8px;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#syllabusForecastStatus[forecastState="boa"],
    QLabel#syllabusForecastBase[forecastState="boa"] {
        background-color: #163523;
        color: #86efac;
        border-color: #166534;
    }

    QLabel#syllabusForecastStatus[forecastState="moderada"],
    QLabel#syllabusForecastBase[forecastState="moderada"] {
        background-color: #332907;
        color: #fde68a;
        border-color: #854d0e;
    }

    QLabel#syllabusForecastStatus[forecastState="limitada"],
    QLabel#syllabusForecastBase[forecastState="limitada"] {
        background-color: #431407;
        color: #fdba74;
        border-color: #9a3412;
    }

    QLabel#syllabusForecastStatus[forecastState="insuficiente"],
    QLabel#syllabusForecastBase[forecastState="insuficiente"] {
        background-color: #273449;
        color: #94a3b8;
        border-color: #475569;
    }

    QProgressBar#syllabusForecastProgress {
        background-color: #334155;
        border: none;
        border-radius: 4px;
    }

    QProgressBar#syllabusForecastProgress::chunk {
        background-color: #60a5fa;
        border-radius: 4px;
    }

    QTableWidget#syllabusForecastTable {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QLabel#syllabusForecastNote {
        background-color: #1f2937;
        color: #94a3b8;
        border: 1px solid #334155;
        border-radius: 7px;
        padding: 8px 9px;
        font-size: 8.5pt;
    }

    QFrame#syllabusAlertStrip {
        background-color: #1f2937;
        border: 1px solid #334155;
        border-radius: 8px;
    }

    QFrame#syllabusAlertStrip[alertState="ok"] {
        background-color: #132a1c;
        border-color: #166534;
    }

    QFrame#syllabusAlertStrip[alertState="monitorar"] {
        background-color: #332907;
        border-color: #854d0e;
    }

    QFrame#syllabusAlertStrip[alertState="atencao"] {
        background-color: #431407;
        border-color: #9a3412;
    }

    QFrame#syllabusAlertStrip[alertState="critico"] {
        background-color: #3f1218;
        border-color: #991b1b;
    }

    QFrame#syllabusAlertStrip QLabel {
        background: transparent;
    }

    QLabel#syllabusAlertIcon {
        color: #fbbf24;
        font-size: 14pt;
        font-weight: 800;
    }

    QLabel#syllabusAlertText {
        color: #e2e8f0;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#syllabusAlertSummary {
        color: #94a3b8;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QPushButton#syllabusAlertButton {
        background-color: #172554;
        color: #bfdbfe;
        border: 1px solid #1d4ed8;
        border-radius: 7px;
        padding: 5px 10px;
        font-weight: 700;
    }

    QPushButton#syllabusAlertButton:hover {
        background-color: #1e3a8a;
        border-color: #60a5fa;
    }

    QPushButton#syllabusAlertButton:disabled {
        background-color: #273449;
        color: #64748b;
        border-color: #334155;
    }

    QFrame#syllabusAlertsCard {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QFrame#syllabusAlertsCard QLabel,
    QFrame#syllabusAlertStat QLabel {
        background: transparent;
    }

    QFrame#syllabusAlertStat {
        background-color: #1f2937;
        border: 1px solid #334155;
        border-radius: 8px;
    }

    QFrame#syllabusAlertStat[alertLevel="critico"] {
        background-color: #3f1218;
        border-color: #991b1b;
    }

    QFrame#syllabusAlertStat[alertLevel="atencao"] {
        background-color: #431407;
        border-color: #9a3412;
    }

    QFrame#syllabusAlertStat[alertLevel="monitorar"] {
        background-color: #332907;
        border-color: #854d0e;
    }

    QLabel#syllabusAlertsEmpty {
        background-color: #1f2937;
        color: #94a3b8;
        border: 1px dashed #475569;
        border-radius: 8px;
        padding: 12px;
        font-size: 9pt;
    }

    QLabel#syllabusAlertsRule {
        background-color: #1f2937;
        color: #94a3b8;
        border: 1px solid #334155;
        border-radius: 7px;
        padding: 7px 9px;
        font-size: 8.5pt;
    }

    QTableWidget#syllabusAlertsTable {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QScrollArea#syllabusProgressScroll {
        background: transparent;
        border: none;
    }

    QWidget#syllabusProgressContent {
        background: transparent;
    }

    QFrame#syllabusStat,
    QFrame#syllabusRules,
    QFrame#syllabusDisciplineCard,
    QFrame#syllabusTopicsCard {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QFrame#syllabusStat QLabel,
    QFrame#syllabusRules QLabel,
    QFrame#syllabusDisciplineCard QLabel,
    QFrame#syllabusTopicsCard QLabel {
        background: transparent;
    }

    QLabel#syllabusStatHint {
        color: #94a3b8;
        font-size: 8pt;
    }

    QLabel#syllabusSectionTitle {
        color: #f8fafc;
        font-size: 11pt;
        font-weight: 800;
    }

    QTableWidget#syllabusDisciplineTable,
    QTableWidget#syllabusTopicsTable {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QProgressBar#syllabusCoverageBar {
        background-color: #334155;
        color: #e2e8f0;
        border: none;
        border-radius: 6px;
        font-size: 8pt;
        font-weight: 700;
        text-align: center;
    }

    QProgressBar#syllabusCoverageBar::chunk {
        background-color: #60a5fa;
        border-radius: 6px;
    }

    QScrollArea#evolutionScroll {
        background: transparent;
        border: none;
    }

    QWidget#evolutionContent {
        background: transparent;
    }

    QFrame#evolutionFilterBar {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QLabel#evolutionPeriodBadge {
        background-color: #273449;
        color: #cbd5e1;
        border: 1px solid #334155;
        border-radius: 7px;
        padding: 5px 8px;
        font-size: 9pt;
        font-weight: 600;
    }

    QFrame#evolutionStat,
    QFrame#evolutionChartCard,
    QFrame#evolutionDisciplineCard {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QFrame#evolutionStat QLabel,
    QFrame#evolutionChartCard QLabel,
    QFrame#evolutionDisciplineCard QLabel {
        background: transparent;
    }

    QLabel#evolutionSectionTitle {
        color: #f8fafc;
        font-size: 15px;
        font-weight: 700;
    }

    QLabel#evolutionTrend {
        color: #94a3b8;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#evolutionTrend[trendState="positiva"] {
        color: #86efac;
    }

    QLabel#evolutionTrend[trendState="negativa"] {
        color: #fca5a5;
    }

    QTableWidget#evolutionDisciplineTable {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QTabWidget#statisticsTabs QTabBar {
        background-color: #111827;
        border: 1px solid #475569;
        border-radius: 10px;
        padding: 4px;
    }

    QTabWidget#statisticsTabs QTabBar::tab {
        background-color: #1f2937;
        color: #cbd5e1;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 10px 18px;
        min-height: 25px;
        min-width: 96px;
        font-size: 10pt;
        font-weight: 700;
        margin-right: 4px;
    }

    QTabWidget#statisticsTabs QTabBar::tab:hover {
        background-color: #1e3a8a;
        color: #dbeafe;
        border-color: #60a5fa;
    }

    QTabWidget#statisticsTabs QTabBar::tab:selected {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #60a5fa;
        font-weight: 800;
    }

    QTabWidget#statisticsTabs::pane {
        border: 1px solid #334155;
        border-radius: 10px;
        background-color: #182235;
        top: -1px;
    }


    QLabel#reportPeriodLabel {
        background-color: #273449;
        color: #cbd5e1;
        border: 1px solid #334155;
        border-radius: 7px;
        padding: 5px 9px;
        font-size: 9pt;
        font-weight: 600;
    }

    QFrame#comparisonPanel {
        background-color: #172033;
        border: 1px solid #334155;
        border-radius: 11px;
    }

    QFrame#comparisonPanel QLabel {
        background: transparent;
    }

    QFrame#comparisonMetric {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QLabel#comparisonValue {
        background: transparent;
        color: #cbd5e1;
        font-size: 13pt;
        font-weight: 800;
    }

    QLabel#comparisonValue[reportTrend="positive"] {
        color: #86efac;
    }

    QLabel#comparisonValue[reportTrend="negative"] {
        color: #fca5a5;
    }

    QLabel#comparisonValue[reportTrend="neutral"] {
        color: #94a3b8;
    }

    QTabWidget#reportTabs::pane {
        border: 1px solid #334155;
        border-radius: 10px;
        background-color: #182235;
        top: -1px;
    }


    QFrame#settingsSearchBar {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QLineEdit#settingsSearchInput {
        background-color: #172033;
        border-color: #334155;
    }

    QLabel#settingsSearchCount {
        background-color: #273449;
        color: #94a3b8;
        border: 1px solid #334155;
        border-radius: 7px;
        padding: 5px 8px;
        font-size: 9pt;
        font-weight: 600;
    }

    QFrame#settingsSection {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 11px;
    }

    QFrame#settingsSection QLabel {
        background: transparent;
    }

    QLabel#settingsSectionTitle {
        color: #f8fafc;
        font-size: 15px;
        font-weight: 700;
    }

    QLabel#settingsSectionDescription {
        color: #94a3b8;
        font-size: 9pt;
    }

    QFrame#settingsOption {
        background-color: #172033;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QFrame#settingsOption QLabel,
    QFrame#settingsOption QCheckBox {
        background: transparent;
    }

    QLabel#configOptionTitle {
        color: #e5e7eb;
        font-size: 10pt;
        font-weight: 700;
    }

    QCheckBox#configMainCheck {
        color: #e5e7eb;
        font-weight: 700;
    }

    QFrame#settingsFooter {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QFrame#settingsFooter QLabel {
        background: transparent;
    }

    QLabel#settingsEmptyState {
        background-color: #182235;
        color: #94a3b8;
        border: 1px dashed #475569;
        border-radius: 10px;
        padding: 20px;
        font-size: 10pt;
    }

    QFrame#cardResumo {
        background-color: #1f2937;
        border: 1px solid #334155;
        border-radius: 12px;
    }

    QPushButton#planningRedistributeButton {
        min-height: 0px;
        background-color: #431407;
        color: #fed7aa;
        border: 1px solid #c2410c;
        border-radius: 7px;
        padding: 4px 10px;
        font-size: 9pt;
        font-weight: 700;
    }

    QPushButton#planningRedistributeButton:hover {
        background-color: #7c2d12;
        border-color: #fb923c;
        color: #ffedd5;
    }

    QPushButton#planningRedistributeButton[hasSuggestion="true"] {
        background-color: #7c2d12;
        border-color: #fb923c;
        color: #ffedd5;
        font-weight: 800;
    }

    QFrame#redistributionStat {
        background-color: #1f2937;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QFrame#redistributionStat QLabel {
        background: transparent;
    }

    QLabel#redistributionNotice {
        background-color: #431407;
        color: #fed7aa;
        border: 1px solid #9a3412;
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 9pt;
    }

    QLabel#redistributionEmpty {
        background-color: #182235;
        color: #94a3b8;
        border: 1px dashed #475569;
        border-radius: 9px;
        padding: 18px;
    }

    QTableWidget#redistributionTable {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QPushButton#planningSummaryButton {
        min-height: 0px;
        background-color: #273449;
        color: #cbd5e1;
        border: 1px solid #475569;
        border-radius: 7px;
        padding: 4px 10px;
        font-size: 9pt;
        font-weight: 700;
    }

    QPushButton#planningSummaryButton:hover {
        background-color: #334155;
        border-color: #64748b;
        color: #f8fafc;
    }

    QFrame#dailySummaryGoal,
    QFrame#dailySummaryComparison,
    QFrame#dailySummaryTopics {
        background-color: #1f2937;
        border: 1px solid #334155;
        border-radius: 11px;
    }

    QFrame#dailySummaryGoal QLabel,
    QFrame#dailySummaryComparison QLabel,
    QFrame#dailySummaryTopics QLabel {
        background: transparent;
    }

    QLabel#dailySummarySectionTitle {
        color: #f8fafc;
        font-size: 15px;
        font-weight: 700;
    }

    QLabel#dailySummaryGoalValue {
        color: #f8fafc;
        font-size: 11pt;
        font-weight: 700;
    }

    QLabel#dailySummaryHint {
        color: #94a3b8;
        font-size: 9pt;
    }

    QLabel#dailySummaryHint[goalState="concluida"] {
        color: #86efac;
        font-weight: 700;
    }

    QProgressBar#dailySummaryProgress {
        background-color: #334155;
        border: none;
        border-radius: 4px;
    }

    QProgressBar#dailySummaryProgress::chunk {
        background-color: #60a5fa;
        border-radius: 4px;
    }

    QProgressBar#dailySummaryProgress[goalState="concluida"]::chunk {
        background-color: #4ade80;
    }

    QFrame#dailySummaryCompareCard {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QLabel#dailySummaryCompareValue {
        color: #f8fafc;
        font-size: 13px;
        font-weight: 700;
    }

    QLabel#dailySummaryCompareAverage {
        color: #94a3b8;
        font-size: 9pt;
    }

    QLabel#dailySummaryTrend {
        color: #94a3b8;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#dailySummaryTrend[trendState="positiva"] {
        color: #86efac;
    }

    QLabel#dailySummaryTrend[trendState="negativa"] {
        color: #fca5a5;
    }

    QTableWidget#dailySummaryTable {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QFrame#studySessionStartCard,
    QFrame#sessionSummaryStat {
        background-color: #1f2937;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QFrame#studySessionStartCard QLabel,
    QFrame#sessionSummaryStat QLabel {
        background: transparent;
    }

    QLabel#sessionSummaryObjective {
        background-color: #172554;
        color: #bfdbfe;
        border: 1px solid #1d4ed8;
        border-radius: 8px;
        padding: 7px 10px;
        font-size: 9.5pt;
        font-weight: 700;
    }

    QTableWidget#sessionSummaryTable {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QPushButton#studySessionPauseButton {
        background-color: #273449;
        color: #cbd5e1;
        border: 1px solid #475569;
        border-radius: 7px;
        padding: 6px 12px;
        font-weight: 700;
    }

    QPushButton#studySessionPauseButton:hover {
        background-color: #334155;
        color: #f8fafc;
    }

    QPushButton#studySessionEndButton {
        background-color: #4c0519;
        color: #fda4af;
        border: 1px solid #9f1239;
        border-radius: 7px;
        padding: 6px 12px;
        font-weight: 700;
    }

    QPushButton#studySessionEndButton:hover {
        background-color: #881337;
        color: #ffe4e6;
    }

    QPushButton#studySessionSkipButton {
        background-color: #431407;
        color: #fdba74;
        border: 1px solid #9a3412;
        border-radius: 7px;
        padding: 7px 12px;
        font-weight: 700;
    }

    QPushButton#studySessionSkipButton:hover {
        background-color: #7c2d12;
        color: #ffedd5;
    }

    QFrame#studySessionCurrentCard,
    QFrame#studySessionQueueCard {
        background-color: #1f2937;
        border: 1px solid #334155;
        border-radius: 11px;
    }

    QFrame#studySessionCurrentCard QLabel,
    QFrame#studySessionQueueCard QLabel {
        background: transparent;
    }

    QFrame#studySessionCurrentCard {
        border: 1px solid #1d4ed8;
        background-color: #172033;
    }

    QLabel#studySessionEyebrow {
        color: #93c5fd;
        font-size: 8.5pt;
        font-weight: 800;
    }

    QLabel#studySessionPosition {
        color: #94a3b8;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#studySessionDiscipline {
        color: #cbd5e1;
        font-size: 10pt;
        font-weight: 700;
    }

    QLabel#studySessionTopic {
        color: #f8fafc;
        font-size: 20px;
        font-weight: 700;
    }

    QLabel#studySessionDetailValue {
        color: #e5e7eb;
        font-size: 10pt;
        font-weight: 700;
    }

    QLabel#studySessionSectionTitle {
        color: #f8fafc;
        font-size: 15px;
        font-weight: 700;
    }

    QTableWidget#studySessionTable {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 8px;
        gridline-color: transparent;
    }

    QFrame#planningPanel {
        background-color: #1f2937;
        border: 1px solid #334155;
        border-radius: 11px;
    }

    QFrame#planningPanel QLabel {
        background: transparent;
    }

    QPushButton#planningGoalButton {
        min-height: 0px;
        background-color: #172554;
        color: #bfdbfe;
        border: 1px solid #3b82f6;
        border-radius: 7px;
        padding: 4px 10px;
        font-size: 9pt;
        font-weight: 700;
    }

    QPushButton#planningGoalButton:hover {
        background-color: #1e3a8a;
        border-color: #60a5fa;
        color: #dbeafe;
    }

    QScrollArea#planningSettingsScroll {
        background: transparent;
        border: none;
    }

    QWidget#planningSettingsContent {
        background: transparent;
    }

    QFrame#planningSettingsCard {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    QFrame#planningSettingsCard QLabel {
        background: transparent;
    }

    QLabel#planningSettingsTitle {
        color: #f8fafc;
        font-size: 11pt;
        font-weight: 700;
    }

    QLabel#planningLoadLight {
        color: #86efac;
        font-weight: 700;
    }

    QLabel#planningLoadModerate {
        color: #fde68a;
        font-weight: 700;
    }

    QLabel#planningLoadHigh {
        color: #fca5a5;
        font-weight: 700;
    }

    QLabel#planningTitle {
        color: #f8fafc;
        font-size: 15px;
        font-weight: 700;
    }

    QLabel#planningTotalBadge {
        background-color: #273449;
        color: #cbd5e1;
        border: 1px solid #334155;
        border-radius: 7px;
        padding: 5px 9px;
        font-size: 9pt;
        font-weight: 700;
    }

    QFrame#weeklyGoalBox {
        background-color: #172033;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QFrame#weeklyGoalBox QLabel,
    QFrame#weeklyGoalMetric QLabel {
        background: transparent;
    }

    QLabel#weeklyGoalTitle {
        color: #f8fafc;
        font-size: 10pt;
        font-weight: 700;
    }

    QLabel#weeklyGoalPeriod {
        color: #94a3b8;
        font-size: 9pt;
        font-weight: 600;
    }

    QLabel#weeklyGoalStatus {
        background-color: #273449;
        color: #cbd5e1;
        border: 1px solid #334155;
        border-radius: 7px;
        padding: 4px 8px;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#weeklyGoalStatus[weekState="concluida"] {
        background-color: #163523;
        color: #86efac;
        border-color: #166534;
    }

    QLabel#weeklyGoalStatus[weekState="atencao"] {
        background-color: #431407;
        color: #fdba74;
        border-color: #9a3412;
    }

    QFrame#weeklyGoalMetric {
        background-color: #1f2937;
        border: 1px solid #334155;
        border-radius: 8px;
    }

    QLabel#weeklyGoalMetricTitle {
        color: #94a3b8;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#weeklyGoalValue {
        color: #f8fafc;
        font-size: 14px;
        font-weight: 700;
    }

    QLabel#weeklyGoalHint {
        color: #94a3b8;
        font-size: 8pt;
    }

    QLabel#weeklyGoalHint[goalState="concluida"] {
        color: #86efac;
        font-weight: 700;
    }

    QProgressBar#weeklyGoalProgress {
        background-color: #334155;
        border: none;
        border-radius: 4px;
    }

    QProgressBar#weeklyGoalProgress::chunk {
        background-color: #60a5fa;
        border-radius: 4px;
    }

    QProgressBar#weeklyGoalProgress[goalState="concluida"]::chunk {
        background-color: #4ade80;
    }

    QFrame#dailyGoalBox,
    QFrame#weeklyLoadBox {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 9px;
    }

    QLabel#planningItemTitle {
        color: #94a3b8;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#dailyGoalValue {
        color: #f8fafc;
        font-size: 17px;
        font-weight: 700;
    }

    QLabel#planningHint {
        color: #94a3b8;
        font-size: 8.5pt;
    }

    QLabel#planningHint[goalState="concluida"] {
        color: #86efac;
        font-weight: 700;
    }

    QProgressBar#dailyGoalProgress {
        background-color: #334155;
        border: none;
        border-radius: 4px;
    }

    QProgressBar#dailyGoalProgress::chunk {
        background-color: #60a5fa;
        border-radius: 4px;
    }

    QProgressBar#dailyGoalProgress[goalState="concluida"]::chunk {
        background-color: #4ade80;
    }

    QFrame#weekDayLoad {
        background-color: #1f2937;
        border: 1px solid #334155;
        border-radius: 8px;
        min-width: 58px;
    }

    QFrame#weekDayLoad[loadLevel="leve"] {
        background-color: #163523;
        border-color: #166534;
    }

    QFrame#weekDayLoad[loadLevel="moderada"] {
        background-color: #3a2e0b;
        border-color: #854d0e;
    }

    QFrame#weekDayLoad[loadLevel="alta"] {
        background-color: #3f1d27;
        border-color: #9f1239;
    }

    QLabel#weekDayName {
        color: #cbd5e1;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#weekDayDate {
        color: #64748b;
        font-size: 8pt;
    }

    QLabel#weekDayCount {
        color: #f8fafc;
        font-size: 16px;
        font-weight: 700;
    }

    QFrame#cardResumo:hover {
        border: 1px solid #475569;
    }

    QLabel#cardTitulo {
        border: none;
        background: transparent;
        color: #94a3b8;
        font-size: 10pt;
    }

    QLabel#cardValor {
        border: none;
        background: transparent;
        color: #f8fafc;
        font-size: 21px;
        font-weight: 700;
    }

    QPushButton {
        min-height: 30px;
        padding: 6px 12px;
        background-color: {{color:action.secondary}};
        color: {{color:text.primary}};
        border: 1px solid {{color:border.strong}};
        border-radius: 8px;
    }

    QPushButton:hover {
        background-color: {{color:action.secondary_hover}};
        border-color: {{color:border.hover}};
    }

    QPushButton:pressed {
        background-color: {{color:action.secondary_pressed}};
    }

    QPushButton:disabled {
        color: {{color:text.disabled}};
        background-color: {{color:action.secondary_disabled}};
        border-color: {{color:border.disabled}};
    }

    QPushButton#primaryButton {
        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #3b82f6;
        font-weight: 700;
    }

    QPushButton#primaryButton:hover {
        background-color: #1d4ed8;
        border-color: #60a5fa;
    }

    QPushButton#toolbarButton {
        background-color: #1f2937;
        min-height: 32px;
    }

    QPushButton#disciplineButton {
        min-height: 42px;
        background-color: #1f2937;
        border: 1px solid #334155;
        font-weight: 600;
        text-align: left;
        padding-left: 14px;
    }

    QPushButton#disciplineButton:hover {
        background-color: #172554;
        border-color: #3b82f6;
    }

    QLineEdit,
    QComboBox,
    QSpinBox,
    QDateEdit,
    QTextEdit {
        min-height: 30px;
        padding: 4px 8px;
        background-color: #1f2937;
        color: #f1f5f9;
        border: 1px solid #475569;
        border-radius: 7px;
        selection-background-color: #1d4ed8;
        selection-color: #ffffff;
    }

    QLineEdit:focus,
    QComboBox:focus,
    QSpinBox:focus,
    QDateEdit:focus,
    QTextEdit:focus {
        border: 1px solid #60a5fa;
    }

    QComboBox QAbstractItemView {
        background-color: #1f2937;
        color: #f1f5f9;
        selection-background-color: #1d4ed8;
        selection-color: #ffffff;
        border: 1px solid #475569;
    }

    QTableWidget,
    QTreeWidget {
        background-color: #182235;
        color: #e5e7eb;
        border: 1px solid #334155;
        border-radius: 8px;
        gridline-color: #334155;
        selection-background-color: #1d4ed8;
        selection-color: #ffffff;
    }

    QTableWidget::item,
    QTreeWidget::item {
        padding: 5px;
    }

    QTableWidget::item:selected,
    QTreeWidget::item:selected {
        background-color: #1d4ed8;
        color: #ffffff;
    }

    QHeaderView::section {
        background-color: #1f2937;
        color: #cbd5e1;
        border: none;
        border-right: 1px solid #334155;
        border-bottom: 1px solid #475569;
        padding: 7px;
        font-weight: 600;
    }

    QTabWidget::pane {
        background-color: #182235;
        border: 1px solid #334155;
        border-radius: 8px;
        top: -1px;
    }

    QTabBar::tab {
        background-color: #1f2937;
        color: #94a3b8;
        padding: 8px 14px;
        margin-right: 2px;
        border-top-left-radius: 7px;
        border-top-right-radius: 7px;
    }

    QTabBar::tab:selected {
        background-color: #182235;
        color: #93c5fd;
        font-weight: 700;
    }

    QCheckBox {
        spacing: 8px;
    }

    QCheckBox::indicator {
        width: 17px;
        height: 17px;
    }

    QFrame[frameShape="4"],
    QFrame[frameShape="5"] {
        color: #334155;
    }

    QToolTip {
        background-color: {{color:surface.inverse}};
        color: {{color:text.inverse}};
        border: none;
        padding: 5px;
    }


    /* ======================================================
       VIGHNA VISUAL V1 — ESCURO
       Inspirado no layout de referência fornecido pelo usuário
       ====================================================== */

    QMainWindow,
    QDialog,
    QWidget {
        background-color: #0d1624;
        color: #e9edf5;
    }

    QLabel#pageTitle {
        color: #f4f6fb;
        font-weight: 800;
    }

    QLabel#pageSubtitle,
    QLabel#mutedLabel {
        color: #95a1b6;
    }

    QFrame#dashboardCenterBar,
    QFrame#contextBar {
        background-color: #121e2d;
        border: 1px solid #304157;
        border-radius: 11px;
    }

    QLabel#profileBadge {
        background-color: #211f48;
        color: #c4baff;
        border: 1px solid #4b438d;
        border-radius: 8px;
        padding: 5px 10px;
        font-weight: 800;
    }

    QFrame#cardResumo {
        background-color: #182535;
        border: 1px solid #314357;
        border-radius: 12px;
    }

    QFrame#cardResumo:hover {
        background-color: #1b2a3c;
        border: 1px solid #465b73;
    }

    QFrame#cardResumo[metricRole="performance"] {
        background-color: #16362f;
        border: 1px solid #276a59;
    }

    QFrame#cardResumo[metricRole="performance"] QLabel#cardTitulo {
        color: #b4d8cc;
    }

    QFrame#cardResumo[metricRole="performance"] QLabel#cardValor {
        color: #59dfa9;
    }

    QLabel#cardTitulo {
        color: #d1d8e4;
        font-size: 10pt;
        font-weight: 600;
    }

    QLabel#cardValor {
        color: #b7adff;
        font-size: 21px;
        font-weight: 800;
    }

    QFrame#syllabusProgressPanel,
    QFrame#planningPanel {
        background-color: #101b29;
        border: 1px solid #304157;
        border-radius: 12px;
    }

    QFrame#syllabusDashboardCoverage,
    QFrame#syllabusDashboardStat,
    QFrame#dailyGoalBox,
    QFrame#weeklyLoadBox,
    QFrame#weeklyGoalBox,
    QFrame#weeklyGoalMetric {
        background-color: #182535;
        border: 1px solid #314357;
        border-radius: 9px;
    }

    QFrame#weekDayLoad {
        background-color: #172434;
        border: 1px solid #314357;
        border-radius: 9px;
    }

    QFrame#weekDayLoad[today="true"] {
        background-color: #211f48;
        border: 1px solid #7568da;
    }

    QFrame#weekDayLoad[today="true"] QLabel#weekDayName,
    QFrame#weekDayLoad[today="true"] QLabel#weekDayDate,
    QFrame#weekDayLoad[today="true"] QLabel#weekDayCount {
        color: #bfb5ff;
        font-weight: 800;
    }

    QFrame#weekDayLoad[loadLevel="leve"][today="false"] {
        background-color: #142d29;
        border-color: #27554b;
    }

    QFrame#weekDayLoad[loadLevel="moderada"][today="false"] {
        background-color: #2c281c;
        border-color: #665735;
    }

    QFrame#weekDayLoad[loadLevel="alta"][today="false"] {
        background-color: #321f27;
        border-color: #72404c;
    }

    QPushButton#dashboardSectionToggle,
    QPushButton#dashboardSectionToggleCentered {
        color: #e7ebf3;
        font-weight: 800;
    }

    QPushButton#dashboardSectionToggle:hover,
    QPushButton#dashboardSectionToggleCentered:hover {
        background-color: #201e43;
        color: #c2b9ff;
    }

    QPushButton#toolbarButton,
    QPushButton#subtleButton {
        background-color: #121e2d;
        color: #e2e7ef;
        border: 1px solid #35475d;
        border-radius: 8px;
    }

    QPushButton#toolbarButton:hover,
    QPushButton#subtleButton:hover {
        background-color: #1e2144;
        color: #c4baff;
        border-color: #665bc4;
    }

    QPushButton#questionsNavButton {
        background-color: #211f48;
        color: #c4baff;
        border: 1px solid #4d468a;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#questionsNavButton:hover {
        background-color: #2b285c;
        border-color: #7166c9;
    }

    QPushButton#topAccentButton,
    QPushButton#primaryButton,
    QPushButton#syllabusOpenButton,
    QPushButton#syllabusAlertButton,
    QPushButton#syllabusForecastButton,
    QPushButton#planningGoalButton,
    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton,
    QPushButton#effectivenessOpenButton,
    QPushButton#questionsEffectivenessButton {
        background-color: #6d5ce7;
        color: #ffffff;
        border: 1px solid #7869eb;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#topAccentButton:hover,
    QPushButton#primaryButton:hover,
    QPushButton#syllabusOpenButton:hover,
    QPushButton#syllabusAlertButton:hover,
    QPushButton#syllabusForecastButton:hover,
    QPushButton#planningGoalButton:hover,
    QPushButton#planningSummaryButton:hover,
    QPushButton#planningRedistributeButton:hover,
    QPushButton#effectivenessOpenButton:hover,
    QPushButton#questionsEffectivenessButton:hover {
        background-color: #7a69ef;
        border-color: #8b7df5;
        color: #ffffff;
    }

    QFrame#syllabusAlertStrip,
    QFrame#syllabusAlertStrip[alertState="monitorar"],
    QFrame#syllabusAlertStrip[alertState="atencao"] {
        background-color: #2a2419;
        border: 1px solid #685737;
        border-radius: 9px;
    }

    QFrame#syllabusForecastStrip {
        background-color: #2a2419;
        border: 1px solid #685737;
        border-radius: 9px;
    }

    QLabel#syllabusAlertIcon,
    QLabel#syllabusForecastIcon {
        color: #d49a43;
    }

    QLabel#syllabusAlertText,
    QLabel#syllabusForecastText {
        color: #d9b978;
    }

    QLabel#syllabusAlertSummary,
    QLabel#syllabusForecastSummary {
        color: #c9b68e;
    }

    QProgressBar#syllabusDashboardBar,
    QProgressBar#dailyGoalProgress,
    QProgressBar#weeklyGoalProgress,
    QProgressBar#questionSessionProgress,
    QProgressBar#topicDomainBar {
        background-color: #263548;
        border: none;
        border-radius: 4px;
    }

    QProgressBar#syllabusDashboardBar::chunk,
    QProgressBar#dailyGoalProgress::chunk,
    QProgressBar#weeklyGoalProgress::chunk,
    QProgressBar#questionSessionProgress::chunk,
    QProgressBar#topicDomainBar::chunk {
        background-color: #7b6aed;
        border-radius: 4px;
    }

    QLineEdit,
    QComboBox,
    QSpinBox,
    QDateEdit,
    QTextEdit {
        background-color: {{color:surface.primary}};
        color: {{color:text.control}};
        border: 1px solid {{color:border.default}};
        border-radius: 8px;
        selection-background-color: {{color:overlay.selection}};
        selection-color: {{color:text.on_action}};
    }

    QLineEdit:focus,
    QComboBox:focus,
    QSpinBox:focus,
    QDateEdit:focus,
    QTextEdit:focus {
        border: 1px solid {{color:focus.ring}};
    }

    QComboBox QAbstractItemView {
        background-color: {{color:surface.elevated}};
        color: {{color:text.control}};
        selection-background-color: {{color:action.ghost_hover}};
        selection-color: {{color:text.selection_accent}};
        border: 1px solid {{color:border.default}};
    }

    QTableWidget,
    QTreeWidget {
        background-color: {{color:surface.secondary}};
        color: {{color:text.secondary}};
        border: 1px solid {{color:border.subtle}};
        border-radius: 9px;
        gridline-color: {{color:border.grid}};
        selection-background-color: {{color:surface.selected}};
        selection-color: {{color:text.on_action}};
    }

    QHeaderView::section {
        background-color: {{color:surface.tertiary}};
        color: {{color:text.header}};
        border: none;
        border-right: 1px solid {{color:border.divider}};
        border-bottom: 1px solid {{color:border.divider_strong}};
        padding: 7px;
        font-weight: 700;
    }

    QTabWidget::pane {
        background-color: {{color:surface.secondary}};
        border: 1px solid {{color:border.subtle}};
        border-radius: 9px;
    }

    QTabBar::tab {
        background-color: {{color:surface.tertiary}};
        color: {{color:text.muted}};
        padding: 8px 14px;
    }

    QTabBar::tab:selected {
        background-color: {{color:surface.secondary}};
        color: {{color:text.link}};
        font-weight: 800;
    }

    QScrollBar:vertical {
        background: {{color:surface.inset}};
        width: 10px;
        margin: 0px;
        border: none;
    }

    QScrollBar::handle:vertical {
        background: {{color:surface.interactive}};
        min-height: 28px;
        border-radius: 5px;
    }

    QScrollBar::handle:vertical:hover {
        background: {{color:surface.hover}};
    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {
        background: {{color:action.ghost}};
        height: 0px;
    }




    /* Dashboard: Estudar / Avaliar / Revisões prioritárias */
    QFrame#studyNowPanel,
    QFrame#priorityQueuePanel {
        background-color: #101b29;
        border: 1px solid #304157;
        border-radius: 12px;
    }

    QLabel#dashboardActionSectionTitle {
        color: #f2f6fb;
        font-size: 9.5pt;
        font-weight: 900;
    }

    QLabel#dashboardActionSectionSubtitle,
    QLabel#studyActionDescription,
    QLabel#studyScoreBreakdown,
    QLabel#priorityQueueExplanation,
    QLabel#assessmentDescription {
        color: #94a4b9;
        font-size: 8.6pt;
    }

    QFrame#studyActionCard {
        background-color: #172435;
        border: 1px solid #31465f;
        border-radius: 10px;
    }

    QFrame#studyActionCard[actionRole="review"] {
        border-color: #356697;
    }

    QFrame#studyActionCard[actionRole="adaptive"] {
        border-color: #5b51a6;
    }

    QLabel#studyActionTitle {
        color: #edf5ff;
        font-size: 9.6pt;
        font-weight: 900;
    }

    QLabel#studyActionMetric {
        color: #92c5ff;
        font-size: 11pt;
        font-weight: 800;
    }

    QLabel#studyReviewSourceBadge,
    QLabel#priorityQueueSourceBadge {
        background-color: #17324d;
        color: #8fcaff;
        border: 1px solid #315d86;
        border-radius: 7px;
        padding: 3px 7px;
        font-size: 7.4pt;
        font-weight: 800;
    }

    QLabel#studyAdaptiveCriteria {
        color: #bcb2ff;
        font-size: 8.3pt;
        font-weight: 700;
    }

    QPushButton#studyManualButton {
        background-color: #162334;
        color: #b9cee5;
        border: 1px solid #3c536e;
        border-radius: 8px;
        padding: 6px 10px;
        font-weight: 700;
    }

    QPushButton#smartReviewDashboardButton {
        background-color: #2f6bc8;
        color: #ffffff;
        border: 1px solid #4784df;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#adaptiveDashboardButton {
        background-color: #6254cf;
        color: #ffffff;
        border: 1px solid #796de0;
        border-radius: 8px;
        font-weight: 800;
    }

    QFrame#assessmentPanel {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #111f30,
            stop:1 #191a35
        );
        border: 1px solid #405b82;
        border-radius: 12px;
    }

    QLabel#assessmentTitle {
        color: #9bcaff;
        font-size: 11pt;
        font-weight: 900;
    }

    QLabel#assessmentBadge {
        background-color: #2b2455;
        color: #c7bfff;
        border: 1px solid #6055a3;
        border-radius: 7px;
        padding: 3px 7px;
        font-size: 7.5pt;
        font-weight: 900;
    }

    QLabel#assessmentHeadline {
        color: #eef4fb;
        font-size: 10pt;
        font-weight: 800;
    }

    QFrame#assessmentStat {
        background-color: #172435;
        border: 1px solid #354b66;
        border-radius: 8px;
    }

    QLabel#assessmentStatLabel {
        color: #8496ad;
        font-size: 7.7pt;
    }

    QLabel#assessmentStatValue {
        color: #c3bbff;
        font-size: 11pt;
        font-weight: 900;
    }

    QPushButton#mockExamDashboardButton {
        background-color: #4f50c8;
        color: #ffffff;
        border: 1px solid #6d70e5;
        border-radius: 9px;
        font-weight: 900;
        padding: 7px 12px;
    }




    /* Estudar Agora — composição compacta */

    QFrame#studyNowPanel {
        background-color: #101b29;
        border: 1px solid #304157;
        border-radius: 13px;
    }

    QFrame#studyManualFooter {
        background-color: #0e1825;
        border: 1px solid #304157;
        border-radius: 10px;
    }

    QLabel#studyNowIcon {
        background-color: #17304b;
        border: 1px solid #365e83;
        border-radius: 14px;
        font-size: 27px;
    }

    QLabel#dashboardActionSectionTitle {
        color: #f3f6fb;
        font-size: 16pt;
        font-weight: 900;
    }

    QLabel#dashboardActionSectionSubtitle {
        color: #94a4b9;
        font-size: 9pt;
    }

    QLabel#studyColumnTitle {
        color: #edf3fb;
        font-size: 11pt;
        font-weight: 900;
    }

    QFrame#studyActionCard,
    QFrame#strategyCompactCard {
        background-color: #172435;
        border: 1px solid #354a64;
        border-radius: 11px;
    }

    QFrame#studyActionCard[actionRole="review"] {
        border-color: #3972a5;
    }

    QFrame#strategyCompactCard[actionRole="adaptive"] {
        border-color: #6155aa;
    }

    QFrame#strategyCompactCard[actionRole="simulation"] {
        border-color: #8b6631;
        background-color: #211f1a;
    }

    QLabel#studyCardIcon {
        background-color: #13354a;
        border: 1px solid #2e7797;
        border-radius: 13px;
        font-size: 25px;
    }

    QLabel#strategyCardIcon {
        background-color: #28234d;
        border: 1px solid #5f56a8;
        border-radius: 13px;
        font-size: 24px;
    }

    QFrame#strategyCompactCard[actionRole="simulation"] QLabel#strategyCardIcon {
        background-color: #39290f;
        border-color: #9a6b26;
    }

    QLabel#studyActionTitle,
    QLabel#strategyCardTitle {
        color: #f0f5fb;
        font-size: 12pt;
        font-weight: 900;
    }

    QLabel#studyReviewCount {
        color: #9db1c8;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#studyActionDescription,
    QLabel#strategyCardDescription,
    QLabel#studyReviewFooter {
        color: #99a8bb;
        font-size: 8.6pt;
    }

    QLabel#studyReviewDetail {
        color: #dbe6f2;
        font-size: 8.8pt;
        font-weight: 700;
    }

    QLabel#studyReviewSourceBadge {
        background-color: #17324d;
        color: #8fcaff;
        border: 1px solid #315d86;
        border-radius: 7px;
        padding: 3px 7px;
        font-size: 7.3pt;
        font-weight: 900;
    }

    QLabel#studyAdaptiveCriteria {
        color: #bcb2ff;
        font-size: 8.1pt;
        font-weight: 700;
    }

    QPushButton#studyManualButton,
    QPushButton#smartReviewDashboardButton {
        background-color: #2f6bc8;
        color: #ffffff;
        border: 1px solid #4784df;
        border-radius: 9px;
        font-weight: 900;
    }

    QPushButton#adaptiveDashboardButton {
        background-color: #6254cf;
        color: #ffffff;
        border: 1px solid #796de0;
        border-radius: 9px;
        font-weight: 900;
    }

    QPushButton#mockExamDashboardButton {
        background-color: #c07b17;
        color: #ffffff;
        border: 1px solid #d59128;
        border-radius: 9px;
        font-weight: 900;
    }

    QLabel#assessmentBadge {
        background-color: #39290f;
        color: #f4c56f;
        border: 1px solid #8f6428;
        border-radius: 7px;
        padding: 3px 6px;
        font-size: 7pt;
        font-weight: 900;
    }

    QFrame#assessmentStat {
        background-color: #111e2e;
        border: 1px solid #344b66;
        border-radius: 7px;
    }

    QLabel#assessmentStatLabel {
        color: #8396ad;
        font-size: 7.3pt;
    }

    QLabel#assessmentStatValue {
        color: #b8d6f7;
        font-size: 10pt;
        font-weight: 900;
    }




    /* Dashboard superior V1 */

    QFrame#dashboardHeroCard {
        background-color: #111d2b;
        border: 1px solid #32465d;
        border-radius: 13px;
    }

    QLabel#dashboardHeroTitle {
        color: #f0f5fb;
        font-size: 12.5pt;
        font-weight: 900;
    }

    QLabel#dashboardHeroInfo {
        color: #93a5ba;
        font-size: 13pt;
        font-weight: 700;
    }

    QFrame#dashboardStatusPill[statusRole="today"] {
        background-color: #17382d;
        border: 1px solid #2e6b55;
        border-radius: 9px;
    }

    QFrame#dashboardStatusPill[statusRole="late"] {
        background-color: #3a2b13;
        border: 1px solid #7c5a24;
        border-radius: 9px;
    }

    QLabel#dashboardStatusPillLabel,
    QLabel#dashboardStatusPillValue {
        font-size: 11pt;
        font-weight: 900;
    }

    QFrame#dashboardStatusPill[statusRole="today"] QLabel {
        color: #8ce5bb;
    }

    QFrame#dashboardStatusPill[statusRole="late"] QLabel {
        color: #f0bf69;
    }

    QPushButton#dashboardProgressTitleButton {
        background: transparent;
        border: none;
        color: #f0f5fb;
        text-align: left;
        padding: 0px;
        font-size: 12.5pt;
        font-weight: 900;
    }

    QLabel#dashboardContestLabel {
        color: #c0ccda;
        font-weight: 700;
    }

    QComboBox#dashboardContestCombo {
        background-color: #162435;
        color: #eef5fb;
        border: 1px solid #41546c;
        border-radius: 9px;
        padding: 5px 9px;
    }

    QFrame#dashboardProgressDivider {
        background-color: #314257;
        border: none;
    }

    QLabel#dashboardProgressSubtitle {
        color: #92a3b7;
    }

    QLabel#dashboardProgressPercent {
        color: #f1f6fb;
        font-size: 11pt;
        font-weight: 900;
    }

    QProgressBar#dashboardHeroProgressBar {
        background-color: #263444;
        border: none;
        border-radius: 8px;
    }

    QProgressBar#dashboardHeroProgressBar::chunk {
        background-color: #27cbd1;
        border-radius: 8px;
    }

    QLabel#dashboardProgressLegendLabel,
    QLabel#dashboardProgressLegendValue {
        color: #c8d3df;
        font-size: 8.2pt;
    }

    QLabel#dashboardProgressLegendValue {
        font-weight: 900;
    }

    QFrame#dashboardProgressLegend[legendRole="notStarted"] QLabel#dashboardProgressLegendDot {
        color: #7f8a97;
    }

    QFrame#dashboardProgressLegend[legendRole="worked"] QLabel#dashboardProgressLegendDot {
        color: #3ad4dc;
    }

    QFrame#dashboardProgressLegend[legendRole="consolidating"] QLabel#dashboardProgressLegendDot {
        color: #ad7ef2;
    }

    QFrame#dashboardProgressLegend[legendRole="consolidated"] QLabel#dashboardProgressLegendDot {
        color: #63d79a;
    }

    QFrame#dashboardDomainBadge {
        background-color: #172536;
        border: 1px solid #34495f;
        border-radius: 7px;
    }

    QLabel#dashboardDomainLabel {
        color: #93a4b8;
    }

    QLabel#dashboardDomainValue {
        color: #edf4fb;
        font-weight: 900;
    }

    QFrame#dashboardNotificationsPanel {
        background-color: #111d2b;
        border: 1px solid #32465d;
        border-radius: 12px;
    }

    QLabel#dashboardNotificationsTitle {
        color: #f0f5fb;
        font-size: 11.5pt;
        font-weight: 900;
    }

    QLabel#dashboardNotificationsMenu {
        color: #93a4b8;
        font-weight: 900;
    }

    QFrame#dashboardAlertActionCard {
        background-color: #392b15;
        border: 1px solid #8b6427;
        border-radius: 12px;
    }

    QLabel#dashboardAlertActionIcon {
        color: #f0bd64;
        font-size: 17pt;
        font-weight: 900;
    }

    QLabel#dashboardAlertActionSummary {
        color: #e3c18b;
        font-weight: 800;
    }

    QFrame#dashboardQuickStats {
        background-color: #111d2b;
        border: 1px solid #32465d;
        border-radius: 11px;
    }

    QLabel#dashboardQuickStatLabel {
        color: #94a4b9;
    }

    QLabel#dashboardQuickStatValue {
        color: #f0f5fb;
        font-size: 10pt;
        font-weight: 900;
    }




    /* Central de avisos do edital */

    QFrame#dashboardNotificationsPanel {
        background-color: #111d2b;
        border: 1px solid #32465d;
        border-radius: 12px;
    }

    QLabel#dashboardNotificationsTitle {
        color: #f0f5fb;
        font-size: 11.5pt;
        font-weight: 900;
    }

    QLabel#dashboardNotificationsSubtitle {
        color: #8f9fb3;
        font-size: 8pt;
    }

    QFrame#dashboardNoticeRow {
        border-left: none;
        border-right: none;
        border-bottom: none;
        border-radius: 0px;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] {
        background-color: #322814;
        border-top: 1px solid #725926;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"][alertState="ok"] {
        background-color: #173028;
        border-top: 1px solid #315a4a;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"][alertState="critico"] {
        background-color: #39201f;
        border-top: 1px solid #7d4641;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] {
        background-color: #142334;
        border-top: 1px solid #31465e;
    }

    QLabel#dashboardNoticeIcon {
        background-color: #201b11;
        color: #e9b553;
        border: 1px solid #785c27;
        border-radius: 9px;
        font-size: 15pt;
        font-weight: 900;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeIcon {
        color: #82bff2;
        border-color: #416a8c;
    }

    QLabel#dashboardNoticeLabel {
        color: #9baabd;
        font-size: 7.2pt;
        font-weight: 900;
    }

    QLabel#dashboardNoticeTitle {
        color: #eef4fb;
        font-size: 9.4pt;
        font-weight: 800;
    }

    QLabel#dashboardNoticeDescription {
        color: #96a6b9;
        font-size: 8.2pt;
    }

    QLabel#dashboardNoticeSummary {
        background-color: #201b11;
        color: #e6c27b;
        border: 1px solid #6f572a;
        border-radius: 7px;
        padding: 4px 7px;
        font-size: 7.8pt;
        font-weight: 800;
    }

    QFrame#dashboardNoticeRow[alertState="ok"] QLabel#dashboardNoticeSummary {
        color: #8fdbb2;
        border-color: #315b49;
    }

    QFrame#dashboardNotificationsFooter {
        background-color: #0f1a27;
        border-top: 1px solid #2d4055;
        border-bottom-left-radius: 11px;
        border-bottom-right-radius: 11px;
    }

    QLabel#dashboardQuickStatLabel {
        color: #8c9db2;
        font-size: 8pt;
    }

    QLabel#dashboardQuickStatValue {
        color: #edf4fb;
        font-size: 9.3pt;
        font-weight: 900;
    }

    QLabel#dashboardNotificationsFooterText {
        color: #718398;
        font-size: 7.7pt;
    }




    /* REFINO CLEAN V1 — ESCURO */

    QLabel#pageTitle {
        color: #eef3f8;
        font-size: 18pt;
        font-weight: 700;
    }

    QLabel#pageSubtitle {
        color: #8f9caf;
        font-size: 9pt;
        font-weight: 400;
    }

    QPushButton#toolbarButton,
    QPushButton#topAccentButton {
        min-height: 34px;
        padding: 5px 12px;
        font-size: 9pt;
        font-weight: 600;
        border-radius: 8px;
    }

    QPushButton#toolbarButton {
        background-color: #142131;
        color: #dce4ed;
        border: 1px solid #34475d;
    }

    QPushButton#topAccentButton {
        background-color: #416ab7;
        color: #ffffff;
        border: 1px solid #416ab7;
    }

    QLabel#dashboardHeroTitle,
    QPushButton#dashboardProgressTitleButton {
        color: #e8eef5;
        font-size: 10.5pt;
        font-weight: 700;
    }

    QLabel#dashboardHeroInfo {
        color: #8394a8;
        font-size: 9.5pt;
        font-weight: 600;
    }

    QLabel#dashboardStatusPillLabel {
        font-size: 8.5pt;
        font-weight: 600;
    }

    QLabel#dashboardStatusPillValue {
        font-size: 10pt;
        font-weight: 700;
    }

    QLabel#dashboardProgressPercent {
        font-size: 10pt;
        font-weight: 700;
    }

    QLabel#dashboardProgressLegendLabel,
    QLabel#dashboardProgressLegendValue {
        font-size: 7.8pt;
    }

    QLabel#dashboardProgressLegendValue,
    QLabel#dashboardDomainValue {
        font-weight: 700;
    }

    QLabel#dashboardNotificationsTitle {
        color: #e8eef5;
        font-size: 10pt;
        font-weight: 700;
    }

    QLabel#dashboardNotificationsSubtitle {
        color: #8292a6;
        font-size: 7.7pt;
    }

    QLabel#dashboardNoticeIcon {
        background-color: transparent;
        border: none;
        font-size: 12pt;
        font-weight: 700;
    }

    QLabel#dashboardNoticeLabel {
        color: #8797aa;
        font-size: 6.8pt;
        font-weight: 700;
    }

    QLabel#dashboardNoticeTitle {
        color: #dce5ee;
        font-size: 8.7pt;
        font-weight: 600;
    }

    QLabel#dashboardNoticeDescription {
        color: #8d9db0;
        font-size: 7.8pt;
    }

    QLabel#dashboardNoticeSummary {
        background-color: transparent;
        border: none;
        color: #c4a774;
        font-size: 7.5pt;
        font-weight: 600;
        padding: 0px;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] {
        background-color: #282318;
        border-top: 1px solid #514629;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] {
        background-color: #132131;
        border-top: 1px solid #2c3e52;
    }

    QLabel#dashboardQuickStatLabel {
        color: #8797aa;
        font-size: 7.7pt;
    }

    QLabel#dashboardQuickStatValue {
        color: #dce5ee;
        font-size: 8.7pt;
        font-weight: 700;
    }

    QLabel#studyNowIcon,
    QLabel#studyCardIcon,
    QLabel#strategyCardIcon {
        background-color: transparent;
        border: none;
        color: #8da0b5;
        font-size: 15pt;
        font-weight: 600;
    }

    QLabel#dashboardActionSectionTitle {
        color: #e8eef5;
        font-size: 13pt;
        font-weight: 700;
    }

    QLabel#dashboardActionSectionSubtitle {
        color: #8c9caf;
        font-size: 8.5pt;
        font-weight: 400;
    }

    QLabel#studyColumnTitle {
        color: #cbd5e1;
        font-size: 9.5pt;
        font-weight: 700;
    }

    QLabel#studyActionTitle,
    QLabel#strategyCardTitle {
        color: #e1e8f0;
        font-size: 10.5pt;
        font-weight: 700;
    }

    QLabel#studyReviewCount {
        color: #8fa0b4;
        font-size: 8pt;
        font-weight: 500;
    }

    QLabel#studyActionDescription,
    QLabel#strategyCardDescription,
    QLabel#studyReviewFooter {
        color: #8e9eb1;
        font-size: 8pt;
        font-weight: 400;
    }

    QLabel#studyReviewDetail {
        color: #bac6d3;
        font-size: 8.2pt;
        font-weight: 600;
    }

    QLabel#studyReviewSourceBadge,
    QLabel#priorityQueueSourceBadge,
    QLabel#assessmentBadge {
        border-radius: 6px;
        padding: 2px 6px;
        font-size: 6.7pt;
        font-weight: 600;
    }

    QLabel#studyAdaptiveCriteria {
        color: #a9a3ce;
        font-size: 7.6pt;
        font-weight: 500;
    }

    QPushButton#studyManualButton,
    QPushButton#smartReviewDashboardButton,
    QPushButton#adaptiveDashboardButton,
    QPushButton#mockExamDashboardButton,
    QPushButton#syllabusAlertButton,
    QPushButton#syllabusForecastButton,
    QPushButton#effectivenessOpenButton,
    QPushButton#syllabusOpenButton {
        min-height: 32px;
        padding: 5px 10px;
        border-radius: 7px;
        font-size: 8.5pt;
        font-weight: 600;
    }

    QPushButton#studyManualButton,
    QPushButton#smartReviewDashboardButton,
    QPushButton#syllabusAlertButton,
    QPushButton#syllabusForecastButton,
    QPushButton#effectivenessOpenButton,
    QPushButton#syllabusOpenButton {
        background-color: #416fb9;
        border: 1px solid #416fb9;
        color: #ffffff;
    }

    QPushButton#adaptiveDashboardButton {
        background-color: #5c59a8;
        border: 1px solid #5c59a8;
        color: #ffffff;
    }

    QPushButton#mockExamDashboardButton {
        background-color: #a8742c;
        border: 1px solid #a8742c;
        color: #ffffff;
    }

    QFrame#studyActionCard,
    QFrame#strategyCompactCard {
        border-radius: 9px;
        background-color: #152232;
    }

    QFrame#studyActionCard[actionRole="review"] {
        border-color: #34516d;
    }

    QFrame#strategyCompactCard[actionRole="adaptive"] {
        background-color: #171f31;
        border-color: #45425f;
    }

    QFrame#strategyCompactCard[actionRole="simulation"] {
        background-color: #201e19;
        border-color: #594a32;
    }

    QFrame#assessmentStat {
        border-radius: 6px;
        background-color: #101c2a;
        border-color: #2d4055;
    }

    QLabel#assessmentStatLabel {
        color: #7f90a4;
        font-size: 6.8pt;
    }

    QLabel#assessmentStatValue {
        color: #b7c9da;
        font-size: 9pt;
        font-weight: 700;
    }




    /* Setas compactas — Visão geral / Notificações */

    QPushButton#dashboardGroupToggle {
        background: transparent;
        color: #9aaabd;
        border: none;
        text-align: left;
        padding: 3px 5px;
        font-size: 8.8pt;
        font-weight: 600;
    }

    QPushButton#dashboardGroupToggle:hover {
        background-color: #172536;
        color: #bcd7ed;
        border-radius: 6px;
    }

    QPushButton#dashboardGroupToggle[expanded="false"] {
        color: #8294a8;
    }




    /* Status do dia + Desempenho refinados */

    QLabel#dashboardStatusTotal {
        color: #e6edf5;
        font-size: 17pt;
        font-weight: 700;
    }

    QLabel#dashboardStatusSubtitle {
        color: #8f9eb0;
        font-size: 8.3pt;
    }

    QFrame#dashboardStatusLine {
        background: transparent;
        border: none;
    }

    QLabel#dashboardStatusDot {
        font-size: 7.5pt;
    }

    QFrame#dashboardStatusLine[statusRole="today"] QLabel#dashboardStatusDot {
        color: #65c995;
    }

    QFrame#dashboardStatusLine[statusRole="late"] QLabel#dashboardStatusDot {
        color: #dbad5f;
    }

    QLabel#dashboardStatusLineLabel {
        color: #9aa9bb;
        font-size: 8.5pt;
        font-weight: 500;
    }

    QLabel#dashboardStatusLineValue {
        color: #dce5ee;
        font-size: 9.5pt;
        font-weight: 700;
    }

    QLabel#dashboardStatusContext {
        background-color: #172434;
        color: #9aabba;
        border: 1px solid #304257;
        border-radius: 7px;
        padding: 3px 7px;
        font-size: 7.6pt;
        font-weight: 600;
    }

    QLabel#dashboardStatusContext[statusRole="ok"] {
        background-color: #173026;
        color: #8dd0aa;
        border-color: #2f5947;
    }

    QLabel#dashboardStatusContext[statusRole="attention"] {
        background-color: #302719;
        color: #d6b06c;
        border-color: #5f4c29;
    }

    QLabel#dashboardPerformanceCaption {
        color: #8898aa;
        font-size: 7.8pt;
        font-weight: 500;
    }

    QLabel#dashboardTrendLabel {
        color: #8292a5;
        font-size: 7.5pt;
    }

    QLabel#dashboardTrendValue {
        color: #94a4b6;
        font-size: 7.7pt;
        font-weight: 600;
    }

    QLabel#dashboardTrendValue[trendRole="positive"] {
        color: #79cda0;
    }

    QLabel#dashboardTrendValue[trendRole="negative"] {
        color: #dc8b8b;
    }

    QLabel#dashboardTrendValue[trendRole="stable"] {
        color: #9caabc;
    }




    /* ======================================================
       VISÃO GERAL HARMÔNICA — ESCURO
       ====================================================== */

    QFrame#dashboardOverviewCard {
        background-color: #111d2b;
        border: 1px solid #33475d;
        border-radius: 11px;
    }

    QLabel#dashboardOverviewTitle {
        color: #e7edf4;
        font-size: 10.5pt;
        font-weight: 700;
    }

    QLabel#dashboardOverviewInfo {
        color: #718398;
        font-size: 8.5pt;
        font-weight: 600;
    }

    QLabel#dashboardRhythmMainValue {
        color: #e3ebf3;
        font-size: 18pt;
        font-weight: 700;
    }

    QLabel#dashboardRhythmCaption {
        color: #8b9aab;
        font-size: 8pt;
    }

    QFrame#dashboardRhythmMetric {
        background-color: #152333;
        border: 1px solid #2e4054;
        border-radius: 8px;
    }

    QFrame#dashboardRhythmMetric[metricRole="today"] {
        background-color: #172a25;
        border-color: #2e4d42;
    }

    QFrame#dashboardRhythmMetric[metricRole="late"] {
        background-color: #2a251a;
        border-color: #51452c;
    }

    QLabel#dashboardRhythmMetricValue {
        color: #d9e3ec;
        font-size: 11pt;
        font-weight: 700;
    }

    QFrame#dashboardRhythmMetric[metricRole="today"] QLabel#dashboardRhythmMetricValue {
        color: #84c7a0;
    }

    QFrame#dashboardRhythmMetric[metricRole="late"] QLabel#dashboardRhythmMetricValue {
        color: #d1ab67;
    }

    QLabel#dashboardRhythmMetricLabel {
        color: #8d9cae;
        font-size: 7.5pt;
    }

    QLabel#dashboardRhythmStatus {
        background: transparent;
        border: none;
        color: #8f9eaf;
        font-size: 7.7pt;
        font-weight: 600;
    }

    QLabel#dashboardRhythmStatus[statusRole="ok"] {
        color: #81c39d;
    }

    QLabel#dashboardRhythmStatus[statusRole="attention"] {
        color: #d0a862;
    }

    QLabel#dashboardQualityCaption {
        color: #8797a9;
        font-size: 7.7pt;
        font-weight: 500;
    }

    QFrame#dashboardOverviewDivider {
        background-color: #2f4155;
        border: none;
    }

    QLabel#dashboardQualityTrendLabel {
        color: #8292a4;
        font-size: 7.5pt;
    }

    QLabel#dashboardQualityTrendValue {
        color: #93a3b5;
        font-size: 7.7pt;
        font-weight: 600;
    }

    QLabel#dashboardQualityTrendValue[trendRole="positive"] {
        color: #7bc79b;
    }

    QLabel#dashboardQualityTrendValue[trendRole="negative"] {
        color: #d48787;
    }

    QPushButton#dashboardProjectionTitleButton {
        background: transparent;
        color: #e7edf4;
        border: none;
        text-align: left;
        padding: 0px;
        font-size: 10.5pt;
        font-weight: 700;
    }

    QLabel#dashboardProjectionContestLabel {
        color: #91a0b1;
        font-size: 8pt;
        font-weight: 600;
    }

    QLabel#dashboardProjectionCaption {
        color: #8797a9;
        font-size: 7.7pt;
    }

    QLabel#dashboardProjectionDetail {
        color: #bac6d2;
        font-size: 8.3pt;
        font-weight: 600;
    }

    QLabel#dashboardProjectionPercent {
        color: #e3ebf3;
        font-size: 16pt;
        font-weight: 700;
    }

    QProgressBar#dashboardProjectionBar {
        background-color: #263443;
        border: none;
        border-radius: 6px;
    }

    QProgressBar#dashboardProjectionBar::chunk {
        background-color: #35bcb4;
        border-radius: 6px;
    }

    QFrame#dashboardProjectionMetric {
        background-color: #152333;
        border: 1px solid #2e4054;
        border-radius: 7px;
    }

    QLabel#dashboardProjectionMetricLabel {
        color: #8797aa;
        font-size: 7.4pt;
    }

    QLabel#dashboardProjectionMetricValue {
        color: #dae3ec;
        font-size: 8.7pt;
        font-weight: 700;
    }

    QFrame#dashboardProjectionMetric[metricRole="consolidating"] QLabel#dashboardProjectionMetricValue {
        color: #ab94d6;
    }

    QFrame#dashboardProjectionMetric[metricRole="consolidated"] QLabel#dashboardProjectionMetricValue {
        color: #80c59c;
    }

    QFrame#dashboardProjectionMetric[metricRole="domain"] QLabel#dashboardProjectionMetricValue {
        color: #8ebbd4;
    }




    /* Ritmo + Qualidade V2 — Escuro */

    QFrame#dashboardOverviewVerticalDivider {
        background-color: #2e4053;
        border: none;
    }

    QLabel#dashboardRhythmMainValue {
        color: #e4ebf3;
        font-size: 19pt;
        font-weight: 700;
    }

    QLabel#dashboardRhythmCaption {
        color: #8b9aab;
        font-size: 8pt;
    }

    QFrame#dashboardRhythmLine {
        background: transparent;
        border: none;
    }

    QLabel#dashboardRhythmDot {
        font-size: 7pt;
    }

    QFrame#dashboardRhythmLine[metricRole="today"] QLabel#dashboardRhythmDot {
        color: #68bf91;
    }

    QFrame#dashboardRhythmLine[metricRole="late"] QLabel#dashboardRhythmDot {
        color: #d0a458;
    }

    QLabel#dashboardRhythmLineLabel {
        color: #93a2b4;
        font-size: 8.4pt;
        font-weight: 500;
    }

    QLabel#dashboardRhythmLineValue {
        color: #dce5ee;
        font-size: 11pt;
        font-weight: 700;
    }

    QFrame#dashboardRhythmLine[metricRole="today"] QLabel#dashboardRhythmLineValue {
        color: #82c9a1;
    }

    QFrame#dashboardRhythmLine[metricRole="late"] QLabel#dashboardRhythmLineValue {
        color: #d1aa66;
    }

    QLabel#dashboardRhythmStatus {
        color: #8e9eaf;
        background: transparent;
        border: none;
        padding: 1px 0px;
        font-size: 7.7pt;
        font-weight: 600;
    }

    QLabel#dashboardRhythmStatus[statusRole="ok"] {
        color: #81c39d;
    }

    QLabel#dashboardRhythmStatus[statusRole="attention"] {
        color: #d0aa67;
    }

    QLabel#dashboardQualityEyebrow {
        color: #788a9f;
        font-size: 6.9pt;
        font-weight: 600;
    }

    QLabel#dashboardQualityCaption {
        color: #c6d1dd;
        font-size: 9.2pt;
        font-weight: 600;
    }

    QFrame#dashboardQualityTrendBox {
        background-color: #142131;
        border: 1px solid #2d4054;
        border-radius: 7px;
    }

    QLabel#dashboardQualityTrendValue {
        color: #a6b5c6;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#dashboardQualityTrendValue[trendRole="positive"] {
        color: #79c79d;
    }

    QLabel#dashboardQualityTrendValue[trendRole="negative"] {
        color: #d28585;
    }

    QLabel#dashboardQualityTrendValue[trendRole="stable"] {
        color: #a2afbf;
    }

    QLabel#dashboardQualityTrendLabel {
        color: #77899e;
        font-size: 6.9pt;
    }

    QLabel#dashboardQualityFooter {
        color: #65778b;
        font-size: 6.8pt;
    }




    /* ======================================================
       PLANEJAMENTO REORGANIZADO V1 — ESCURO
       ====================================================== */

    QFrame#planningPanel {
        background-color: #111d2b;
        border: 1px solid #33475d;
        border-radius: 11px;
    }

    QLabel#planningSectionSubtitle {
        color: #8999aa;
        font-size: 8pt;
    }

    QLabel#planningSubsectionTitle {
        color: #d6dfe8;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#planningSubsectionHint,
    QLabel#planningMicroLabel {
        color: #78899d;
        font-size: 7.4pt;
    }

    QFrame#dailyGoalBox,
    QFrame#weeklyLoadBox,
    QFrame#weeklyGoalBox {
        background-color: #142131;
        border: 1px solid #2e4054;
        border-radius: 9px;
    }

    QLabel#planningItemTitle,
    QLabel#weeklyGoalTitle {
        color: #cbd6e0;
        font-size: 8.7pt;
        font-weight: 700;
    }

    QLabel#dailyGoalValue {
        color: #e1e8f0;
        font-size: 13pt;
        font-weight: 700;
    }

    QLabel#planningTotalBadge {
        background-color: #182536;
        color: #91a1b4;
        border: 1px solid #33465b;
        border-radius: 6px;
        padding: 3px 7px;
        font-size: 7.3pt;
        font-weight: 600;
    }

    QProgressBar#dailyGoalProgress {
        background-color: #263646;
        border: none;
        border-radius: 4px;
    }

    QProgressBar#dailyGoalProgress::chunk {
        background-color: #4779c7;
        border-radius: 4px;
    }

    QLabel#planningHint {
        color: #8796a8;
        font-size: 7.4pt;
    }

    QFrame#weekDayLoad {
        background-color: #111e2d;
        border: 1px solid #2d4054;
        border-radius: 8px;
        min-height: 62px;
    }

    QFrame#weekDayLoad[today="true"] {
        background-color: #172944;
        border-color: #5078b9;
    }

    QFrame#weekDayLoad[loadLevel="leve"][today="false"] {
        background-color: #15271f;
        border-color: #2d4a3d;
    }

    QFrame#weekDayLoad[loadLevel="moderada"][today="false"] {
        background-color: #292317;
        border-color: #55482b;
    }

    QFrame#weekDayLoad[loadLevel="alta"][today="false"] {
        background-color: #2d1d1d;
        border-color: #5e3737;
    }

    QLabel#weekDayName {
        color: #95a4b6;
        font-size: 7.5pt;
        font-weight: 600;
    }

    QLabel#weekDayDate {
        color: #687b91;
        font-size: 6.8pt;
    }

    QLabel#weekDayCount {
        color: #dce5ee;
        font-size: 10pt;
        font-weight: 700;
    }

    QFrame#weekDayLoad[today="true"] QLabel#weekDayName,
    QFrame#weekDayLoad[today="true"] QLabel#weekDayCount {
        color: #a9c8f5;
    }

    QPushButton#planningGoalButton,
    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton,
    QPushButton#weeklyGoalSetupButton {
        min-height: 30px;
        padding: 4px 10px;
        border-radius: 7px;
        font-size: 8pt;
        font-weight: 600;
    }

    QPushButton#planningGoalButton {
        background-color: #416fb9;
        color: #ffffff;
        border: 1px solid #416fb9;
    }

    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton,
    QPushButton#weeklyGoalSetupButton {
        background-color: #162435;
        color: #b9c8d7;
        border: 1px solid #34495f;
    }

    QPushButton#planningRedistributeButton[hasSuggestion="true"] {
        background-color: #31291a;
        color: #d4b171;
        border-color: #66542c;
    }

    QFrame#weeklyGoalEmptyState {
        background-color: #111e2d;
        border: 1px dashed #34475a;
        border-radius: 8px;
    }

    QLabel#weeklyGoalEmptyTitle {
        color: #c0ccd8;
        font-size: 8.3pt;
        font-weight: 600;
    }

    QLabel#weeklyGoalEmptyDescription {
        color: #8191a4;
        font-size: 7.4pt;
    }

    QLabel#weeklyGoalPeriod {
        color: #8393a6;
        font-size: 7.4pt;
    }

    QFrame#weeklyGoalMetric {
        background-color: #111e2d;
        border: 1px solid #2d4054;
        border-radius: 7px;
    }

    QLabel#weeklyGoalMetricTitle {
        color: #8192a5;
        font-size: 7.3pt;
        font-weight: 600;
    }

    QLabel#weeklyGoalValue {
        color: #dce5ee;
        font-size: 9.5pt;
        font-weight: 700;
    }

    QLabel#weeklyGoalHint {
        color: #788a9e;
        font-size: 7pt;
    }




    /* Ação única do Planejamento */
    QPushButton#planningGoalButton {
        min-height: 34px;
        padding: 5px 14px;
        background-color: #416fb9;
        color: #ffffff;
        border: 1px solid #416fb9;
        border-radius: 8px;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QPushButton#planningGoalButton:hover {
        background-color: #365f9f;
        border-color: #365f9f;
    }




    /* Correção de contraste no hover — Planejamento */
    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton {
        background-color: #162435;
        color: #b9c9d8;
        border: 1px solid #34495f;
        border-radius: 8px;
        font-weight: 600;
    }

    QPushButton#planningSummaryButton:hover,
    QPushButton#planningRedistributeButton:hover {
        background-color: #20364b;
        color: #e2edf6;
        border: 1px solid #4b6b88;
    }

    QPushButton#planningSummaryButton:pressed,
    QPushButton#planningRedistributeButton:pressed {
        background-color: #29435a;
        color: #ffffff;
        border-color: #5d7e9c;
    }

    QPushButton#planningRedistributeButton[hasSuggestion="true"] {
        background-color: #31291a;
        color: #d4b171;
        border-color: #66542c;
    }

    QPushButton#planningRedistributeButton[hasSuggestion="true"]:hover {
        background-color: #40331d;
        color: #efd095;
        border-color: #80693a;
    }



    /* ======================================================
       NOTIFICAÇÕES — CORES HARMONIZADAS V1 / ESCURO
       ====================================================== */

    QFrame#dashboardNoticeRow[noticeRole="alert"] {
        background-color: #2a2418;
        border: 1px solid #5f502d;
        border-radius: 9px;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"][alertState="ok"] {
        background-color: #172820;
        border-color: #315044;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"][alertState="critico"] {
        background-color: #301f1f;
        border-color: #64403d;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] QLabel#dashboardNoticeLabel {
        color: #c6a665;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] QLabel#dashboardNoticeTitle {
        color: #e3c98e;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] QLabel#dashboardNoticeDescription,
    QFrame#dashboardNoticeRow[noticeRole="alert"] QLabel#dashboardNoticeSummary {
        color: #bfa87a;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] QLabel#dashboardNoticeIcon {
        background-color: #382d18;
        color: #e1b85b;
        border: 1px solid #6f592d;
        border-radius: 15px;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] {
        background-color: #142333;
        border: 1px solid #304c67;
        border-radius: 9px;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeLabel {
        color: #7fa4c7;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeTitle {
        color: #a9cae8;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeDescription,
    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeSummary {
        color: #8fa9c0;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeIcon {
        background-color: #182d42;
        color: #86b9e4;
        border: 1px solid #3c6385;
        border-radius: 15px;
    }

    QPushButton#syllabusAlertButton {
        background-color: #9e742d;
        color: #ffffff;
        border: 1px solid #b18743;
        border-radius: 8px;
        font-weight: 700;
    }

    QPushButton#syllabusAlertButton:hover {
        background-color: #b18438;
        color: #ffffff;
        border-color: #c39951;
    }

    QPushButton#syllabusForecastButton {
        background-color: #3f6fa8;
        color: #ffffff;
        border: 1px solid #4c83bd;
        border-radius: 8px;
        font-weight: 700;
    }

    QPushButton#syllabusForecastButton:hover {
        background-color: #4b7fba;
        color: #ffffff;
        border-color: #5b91cb;
    }




    /* Questões — ação principal do menu */

    QPushButton#questionsNavButton {
        min-height: 34px;
        min-width: 96px;
        padding: 5px 13px;
        background-color: #176b82;
        color: #eefcff;
        border: 1px solid #2c8fa5;
        border-radius: 8px;
        font-size: 9pt;
        font-weight: 700;
    }

    QPushButton#questionsNavButton:hover {
        background-color: #1c7b94;
        color: #ffffff;
        border-color: #48a8ba;
    }

    QPushButton#questionsNavButton:pressed {
        background-color: #14596d;
        color: #ffffff;
        border-color: #287b90;
    }




    /* PALETA HARMONIZADA — BOTÕES (ESCURO) */

    QPushButton#toolbarButton,
    QPushButton#subtleButton {
        background-color: #162333;
        color: #dce6f0;
        border: 1px solid #33475e;
        border-radius: 8px;
    }

    QPushButton#toolbarButton:hover,
    QPushButton#subtleButton:hover {
        background-color: #1c3145;
        color: #9bd5ff;
        border-color: #4d89b8;
    }

    QPushButton#questionsNavButton,
    QPushButton#questionsImportButton,
    QPushButton#questionsPdfImportButton,
    QPushButton#questionsSolveButton,
    QPushButton#questionsSolveHeroButton,
    QPushButton#questionsNewHeroButton,
    QPushButton#questionsPromptsButton,
    QPushButton#questionsHistoryButton,
    QPushButton#questionsEffectivenessButton {
        background-color: #176b82;
        color: #eefcff;
        border: 1px solid #2d91a7;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#questionsNavButton:hover,
    QPushButton#questionsImportButton:hover,
    QPushButton#questionsPdfImportButton:hover,
    QPushButton#questionsSolveButton:hover,
    QPushButton#questionsSolveHeroButton:hover,
    QPushButton#questionsNewHeroButton:hover,
    QPushButton#questionsPromptsButton:hover,
    QPushButton#questionsHistoryButton:hover,
    QPushButton#questionsEffectivenessButton:hover {
        background-color: #1b7c95;
        border-color: #43abc0;
        color: #ffffff;
    }

    QPushButton#topAccentButton,
    QPushButton#primaryButton,
    QPushButton#syllabusOpenButton,
    QPushButton#planningGoalButton,
    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton,
    QPushButton#effectivenessOpenButton,
    QPushButton#smartReviewDashboardButton,
    QPushButton#rowActionButton,
    QPushButton#weeklyGoalSetupButton,
    QPushButton#questionSessionEndButton,
    QPushButton#studySessionEndButton,
    QPushButton#mockExamStartButton {
        background-color: #416ab7;
        color: #ffffff;
        border: 1px solid #4c7bcf;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#topAccentButton:hover,
    QPushButton#primaryButton:hover,
    QPushButton#syllabusOpenButton:hover,
    QPushButton#planningGoalButton:hover,
    QPushButton#planningSummaryButton:hover,
    QPushButton#planningRedistributeButton:hover,
    QPushButton#effectivenessOpenButton:hover,
    QPushButton#smartReviewDashboardButton:hover,
    QPushButton#rowActionButton:hover,
    QPushButton#weeklyGoalSetupButton:hover,
    QPushButton#questionSessionEndButton:hover,
    QPushButton#studySessionEndButton:hover,
    QPushButton#mockExamStartButton:hover {
        background-color: #355ba3;
        border-color: #426ec4;
        color: #ffffff;
    }

    QPushButton#adaptiveDashboardButton,
    QPushButton#questionsAdaptiveButton,
    QPushButton#adaptiveSessionStartButton {
        background-color: #2e8b7b;
        color: #ffffff;
        border: 1px solid #38a18e;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#adaptiveDashboardButton:hover,
    QPushButton#questionsAdaptiveButton:hover,
    QPushButton#adaptiveSessionStartButton:hover {
        background-color: #287667;
        border-color: #38a18e;
        color: #ffffff;
    }

    QPushButton#syllabusAlertButton,
    QPushButton#mockExamDashboardButton,
    QPushButton#questionsMockExamButton {
        background-color: #a97523;
        color: #ffffff;
        border: 1px solid #c6923d;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#syllabusAlertButton:hover,
    QPushButton#mockExamDashboardButton:hover,
    QPushButton#questionsMockExamButton:hover {
        background-color: #8f641c;
        border-color: #ba8c43;
        color: #ffffff;
    }

    QPushButton#syllabusForecastButton {
        background-color: #142131;
        color: #9fd0ff;
        border: 1px solid #4c7bcf;
        border-radius: 8px;
        font-weight: 700;
    }

    QPushButton#syllabusForecastButton:hover {
        background-color: #1a2d43;
        color: #d8ebff;
        border-color: #6a99ee;
    }




    /* Integridade histórica — Questões */

    QLabel#questionsIntegrityBadge {
        background-color: #172434;
        color: #91a2b6;
        border: 1px solid #31445a;
        border-radius: 7px;
        padding: 4px 8px;
        font-size: 7.5pt;
        font-weight: 700;
    }

    QLabel#questionsIntegrityBadge[integrityState="ok"] {
        background-color: #173027;
        color: #82c9a0;
        border-color: #315a48;
    }

    QLabel#questionsIntegrityBadge[integrityState="legacy"] {
        background-color: #162b3d;
        color: #8eb8dd;
        border-color: #31536e;
    }

    QLabel#questionsIntegrityBadge[integrityState="warning"] {
        background-color: #302719;
        color: #d2ad69;
        border-color: #5f4d2a;
    }




    /* Minha evolução V1 — Escuro */

    QFrame#myEvolutionFilterBar,
    QFrame#myEvolutionPanel,
    QFrame#myEvolutionStatCard {
        background-color: #111d2b;
        border: 1px solid #33475d;
        border-radius: 10px;
    }

    QLabel#myEvolutionTitle,
    QLabel#myEvolutionSectionTitle {
        color: #e6edf4;
        font-weight: 700;
    }

    QLabel#myEvolutionTitle { font-size: 11pt; }
    QLabel#myEvolutionSectionTitle { font-size: 9.5pt; }

    QLabel#myEvolutionStatLabel {
        color: #8999ac;
        font-size: 7.8pt;
        font-weight: 600;
    }

    QLabel#myEvolutionStatValue {
        color: #e0e8f0;
        font-size: 15pt;
        font-weight: 700;
    }

    QLabel#myEvolutionStatDetail {
        color: #78899d;
        font-size: 7.3pt;
    }

    QFrame#myEvolutionInsight {
        background-color: #142131;
        border: 1px solid #2f4256;
        border-radius: 8px;
    }

    QFrame#myEvolutionInsight[insightRole="positive"] {
        background-color: #152820;
        border-color: #2f5142;
    }

    QFrame#myEvolutionInsight[insightRole="attention"] {
        background-color: #2b2519;
        border-color: #57482b;
    }

    QFrame#myEvolutionInsight[insightRole="recovery"] {
        background-color: #15263a;
        border-color: #31506c;
    }

    QLabel#myEvolutionInsightLabel {
        color: #8293a7;
        font-size: 7.2pt;
        font-weight: 600;
    }

    QLabel#myEvolutionInsightValue {
        color: #d7e1ea;
        font-size: 9.2pt;
        font-weight: 700;
    }

    QLabel#myEvolutionInsightDetail {
        color: #7e90a4;
        font-size: 7.2pt;
    }




    /* Índice de Domínio V2 */

    QFrame#topicDomainComponent {
        background-color: #182536;
        border: 1px solid #33475c;
        border-radius: 8px;
    }

    QLabel#topicDomainStrengths {
        color: #8fd2aa;
        background-color: #163126;
        border: 1px solid #315b48;
        border-radius: 7px;
        padding: 5px 8px;
        font-size: 8.1pt;
        font-weight: 600;
    }

    QLabel#topicDomainReasons {
        color: #d5b67b;
        background-color: #302718;
        border: 1px solid #5d4d2d;
        border-radius: 7px;
        padding: 5px 8px;
        font-size: 8.1pt;
    }




    /* RELATÓRIOS ESTRATÉGICOS V1 — ESCURO */

    QScrollArea#strategicReportScroll,
    QWidget#strategicReportContent {
        background: transparent;
        border: none;
    }

    QLabel#strategicReportTitle {
        color: #e7edf5;
        font-size: 12pt;
        font-weight: 800;
    }

    QLabel#strategicReportSubtitle,
    QLabel#strategicReportMuted {
        color: #91a1b4;
        font-size: 8.7pt;
    }

    QFrame#strategicMetricCard {
        background-color: #162333;
        border: 1px solid #33475d;
        border-radius: 10px;
    }

    QLabel#strategicMetricTitle {
        color: #93a4b8;
        font-size: 8.4pt;
        font-weight: 700;
    }

    QLabel#strategicMetricValue {
        color: #edf4fb;
        font-size: 15pt;
        font-weight: 800;
    }

    QLabel#strategicMetricValue[prepState="attention"] {
        color: #e2ad55;
    }

    QLabel#strategicMetricValue[prepState="building"] {
        color: #d7b46a;
    }

    QLabel#strategicMetricValue[prepState="good"] {
        color: #86b3ff;
    }

    QLabel#strategicMetricValue[prepState="strong"] {
        color: #6cc9b3;
    }

    QLabel#strategicMetricValue[prepState="insufficient"] {
        color: #91a1b4;
    }

    QLabel#strategicMetricDetail {
        color: #8394a8;
        font-size: 8.1pt;
    }

    QFrame#strategicReportPanel {
        background-color: #142131;
        border: 1px solid #33475d;
        border-radius: 11px;
    }

    QLabel#strategicReportSectionTitle {
        color: #dce6f0;
        font-size: 9.5pt;
        font-weight: 800;
    }

    QFrame#strategicEvolutionItem {
        background-color: #182638;
        border: 1px solid #35495f;
        border-radius: 8px;
    }

    QLabel#strategicEvolutionValue {
        color: #d6e0eb;
        font-size: 10pt;
        font-weight: 800;
    }

    QLabel#strategicEvolutionValue[trend="positive"] {
        color: #6cc9b3;
    }

    QLabel#strategicEvolutionValue[trend="negative"] {
        color: #e2ad55;
    }

    QLabel#strategicEvolutionValue[trend="neutral"] {
        color: #91a1b4;
    }

    QLabel#strategicRiskItem,
    QLabel#strategicActionItem {
        border-radius: 8px;
        padding: 7px 9px;
        font-size: 8.4pt;
    }

    QLabel#strategicRiskItem[riskLevel="alto"] {
        background-color: #3a241e;
        color: #efb49b;
        border: 1px solid #704636;
    }

    QLabel#strategicRiskItem[riskLevel="medio"] {
        background-color: #352d1d;
        color: #e5c783;
        border: 1px solid #665536;
    }

    QLabel#strategicRiskItem[riskLevel="baixo"] {
        background-color: #17342e;
        color: #8fd7c5;
        border: 1px solid #315f55;
    }

    QLabel#strategicActionItem {
        background-color: #172a42;
        color: #a9cbf6;
        border: 1px solid #365b85;
    }

    QTableWidget#strategicReportTable {
        background-color: #142131;
        border: 1px solid #33475d;
        border-radius: 8px;
    }




    /* Plano de Ação Automático V1 */
    QPushButton#planningAutoPlanButton,
    QPushButton#autoPlanAcceptButton {
        background-color: #416ab7;
        color: #ffffff;
        border: 1px solid #4c7bcf;
        border-radius: 8px;
        font-weight: 800;
    }
    QPushButton#planningAutoPlanButton:hover,
    QPushButton#autoPlanAcceptButton:hover {
        background-color: #355ba3;
        color: #ffffff;
        border-color: #5b87d2;
    }
    QPushButton#planningAutoPlanButton[hasPlan="true"] {
        background-color: #176b82;
        border-color: #2d91a7;
    }
    QPushButton#planningAutoPlanButton[hasPlan="true"]:hover {
        background-color: #1b7c95;
        border-color: #43abc0;
    }
    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton {
        background-color: #142131;
        color: #a8cdfd;
        border: 1px solid #476b9f;
        border-radius: 8px;
        font-weight: 700;
    }
    QPushButton#planningSummaryButton:hover,
    QPushButton#planningRedistributeButton:hover {
        background-color: #1b2f47;
        color: #e3f0ff;
        border-color: #6493d4;
    }
    QFrame#autoPlanStat {
        background-color: #152334;
        border: 1px solid #32485f;
        border-radius: 9px;
    }
    QLabel#autoPlanSavedNotice {
        background-color: #14302d;
        color: #a9e2d5;
        border: 1px solid #2f6f65;
        border-radius: 8px;
        padding: 7px 10px;
    }
    QLabel#autoPlanContext {
        color: #9eafc2;
        background-color: #142131;
        border: 1px solid #32485f;
        border-radius: 8px;
        padding: 7px 10px;
    }




    /* PAUSA & DESAFIOS — ESCURO */

    QPushButton#pauseNavButton {
        min-height: 34px;
        padding: 5px 12px;
        background-color: #18333a;
        color: #9de0df;
        border: 1px solid #376b70;
        border-radius: 8px;
        font-size: 9pt;
        font-weight: 700;
    }

    QPushButton#pauseNavButton:hover {
        background-color: #20454c;
        color: #c4f1ef;
        border-color: #4f8e91;
    }

    QLabel#pauseHubTitle {
        color: #eef5fb;
        font-size: 17px;
        font-weight: 800;
    }

    QLabel#pauseHubSubtitle,
    QLabel#gameHint,
    QLabel#pauseTimerStatus {
        color: #8fa2b5;
        font-size: 9pt;
    }

    QFrame#pauseTimerPanel {
        background-color: #142a31;
        border: 1px solid #31565f;
        border-radius: 10px;
    }

    QFrame#pauseRecordsPanel,
    QFrame#gameBoardPanel {
        background-color: #151f2d;
        border: 1px solid #33465a;
        border-radius: 11px;
    }

    QFrame#pauseRecordCard {
        background-color: #192636;
        border: 1px solid #33475d;
        border-radius: 8px;
    }

    QLabel#pauseSectionTitle,
    QLabel#gameTitle {
        color: #e8eef5;
        font-weight: 800;
    }

    QLabel#pauseSectionTitle { font-size: 9.5pt; }
    QLabel#gameTitle { font-size: 13pt; }

    QLabel#pauseRecordTitle {
        color: #8799ad;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#pauseRecordValue,
    QLabel#gameMetric {
        color: #9dd9e1;
        font-weight: 800;
    }

    QLabel#gameStatus {
        color: #a5b2c1;
        font-size: 9pt;
    }

    QLabel#pauseTimerValue {
        min-width: 74px;
        padding: 4px 10px;
        background-color: #162333;
        color: #a5e6e2;
        border: 1px solid #3f7478;
        border-radius: 7px;
        font-size: 12pt;
        font-weight: 900;
    }

    QPushButton#pausePrimaryButton,
    QPushButton#gamePrimaryButton {
        background-color: #287779;
        color: #ffffff;
        border: 1px solid #3b9798;
        border-radius: 8px;
        font-weight: 800;
    }

    QPushButton#pausePrimaryButton:hover,
    QPushButton#gamePrimaryButton:hover {
        background-color: #328a8c;
        border-color: #50a8a9;
        color: #ffffff;
    }

    QPushButton#pauseSecondaryButton,
    QPushButton#pauseBackButton {
        background-color: #162333;
        color: #a9c9ff;
        border: 1px solid #4e6f9e;
        border-radius: 8px;
        font-weight: 700;
    }

    QPushButton#pauseSecondaryButton:hover,
    QPushButton#pauseBackButton:hover {
        background-color: #1b3048;
        color: #d7e7ff;
        border-color: #6b92ca;
    }

    QPushButton#chimpCellButton,
    QPushButton#memoryCardButton,
    QPushButton#sequenceCellButton,
    QPushButton#puzzleTileButton,
    QPushButton#rotationOptionButton {
        background-color: #1b2939;
        color: #dfe8f2;
        border: 1px solid #3a4e64;
        border-radius: 9px;
        font-size: 12pt;
        font-weight: 900;
    }

    QScrollArea#rotationScrollArea,
    QWidget#rotationScrollContent,
    QWidget#rotationOptionsContainer {
        background: transparent;
        border: none;
    }

    QPushButton#rotationOptionButton {
        min-height: 112px;
        padding: 0px;
    }

    QPushButton#chimpCellButton[cellState="number"] {
        background-color: #1d3550;
        color: #a8cff7;
        border-color: #4f79a5;
    }

    QPushButton#chimpCellButton[cellState="correct"] {
        background-color: #173b35;
        color: #9ae0ce;
        border-color: #3f8173;
    }

    QPushButton#memoryCardButton[cardState="hidden"] {
        background-color: #202d3d;
        color: #8da0b4;
        border-color: #3b4f65;
    }

    QPushButton#memoryCardButton[cardState="open"] {
        background-color: #1d3855;
        color: #b2d5fb;
        border-color: #557fae;
    }

    QPushButton#memoryCardButton[cardState="matched"] {
        background-color: #183a34;
        color: #9ee0d0;
        border-color: #477f73;
    }

    QPushButton#sequenceCellButton {
        background-color: #202e3e;
        border-color: #3c5065;
    }

    QPushButton#sequenceCellButton[lit="true"] {
        background-color: #a97625;
        border-color: #d2a049;
    }

    QPushButton#puzzleTileButton[tileState="movable"] {
        background-color: #1c3855;
        color: #acd2fa;
        border-color: #527ba8;
    }

    QPushButton#puzzleTileButton[tileState="blank"] {
        background-color: #121c29;
        border-color: #26384b;
        color: transparent;
    }

    QPushButton#rotationOptionButton[answerState="correct"] {
        background-color: #183a34;
        border-color: #477f73;
    }

    QPushButton#rotationOptionButton[answerState="wrong"] {
        background-color: #45232b;
        border-color: #a45f6e;
    }




    /* MODO FOCO — ESCURO */
    QPushButton#focusNavButton {
        min-height: 34px; padding: 5px 12px; background-color: #182b43; color: #a9d3ff;
        border: 1px solid #3e6690; border-radius: 8px; font-size: 9pt; font-weight: 800;
    }
    QPushButton#focusNavButton:hover { background-color: #203b58; color: #d2e9ff; border-color: #5689bd; }
    QScrollArea#focusScrollArea { border: none; background: transparent; }
    QWidget#focusScrollContent { background: transparent; }
    QLabel#focusTitle { color: #eef5fb; font-size: 17px; font-weight: 800; }
    QLabel#focusSubtitle, QLabel#focusWindowHint, QLabel#focusStatLabel, QLabel#focusStatusLabel { color: #8fa2b5; font-size: 9pt; }
    QFrame#focusStatsPanel { background-color: #142232; border: 1px solid #33495f; border-radius: 10px; }
    QLabel#focusStatValue { color: #9dcbff; font-size: 13pt; font-weight: 900; }
    QFrame#focusConfigPanel, QFrame#focusRecentPanel { background-color: #151f2d; border: 1px solid #33465a; border-radius: 11px; }
    QFrame#focusActivePanel { background-color: #15283c; border: 1px solid #3b6289; border-radius: 12px; }
    QLabel#focusSectionTitle, QLabel#focusContextLabel { color: #e8eef5; font-weight: 800; }
    QLabel#focusTimerValue { color: #a9d3ff; font-size: 32px; font-weight: 900; }
    QLabel#dashboardFocusSummary { color: #8ca4bb; font-size: 8.4pt; font-weight: 700; }
    QPushButton#focusPresetButton, QPushButton#focusSecondaryButton, QPushButton#focusPauseButton {
        background-color: #172536; color: #b9d8f7; border: 1px solid #3a5877; border-radius: 8px; font-weight: 700;
    }
    QPushButton#focusPresetButton:hover, QPushButton#focusSecondaryButton:hover, QPushButton#focusPauseButton:hover {
        background-color: #20374f; border-color: #527ba5; color: #e0f0ff;
    }
    QPushButton#focusPrimaryButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #b91c2a, stop:0.52 #d92d3a, stop:1 #f04451);
        color: #ffffff; border: 1px solid #ff6973; border-radius: 10px;
        font-weight: 900; font-size: 10.2pt; padding: 8px 22px;
    }
    QPushButton#focusPrimaryButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #cf2634, stop:0.52 #e63b47, stop:1 #ff5964);
        border-color: #ff9298;
    }
    QPushButton#focusPrimaryButton:pressed { background-color: #9f1723; border-color: #ff5964; }
    QPushButton#focusDangerButton { background-color: #392322; color: #f0b6ae; border: 1px solid #70433e; border-radius: 8px; font-weight: 700; }
    QPushButton#focusDangerButton:hover { background-color: #4b2b28; border-color: #945950; }

    QFrame#postFocusHero { background-color: #172536; border: 1px solid #365574; border-radius: 12px; }
    QFrame#postFocusContentCard { background-color: #151f2d; border: 1px solid #33465a; border-radius: 10px; }
    QFrame#postFocusResultCard { background-color: #172a24; border: 1px solid #365f4c; border-radius: 10px; }
    QLabel#postFocusResultValue { color: #91d6ac; font-size: 13pt; font-weight: 900; }
    QPushButton#postFocusContinue { background-color: #20374f; color: #d6eaff; border: 1px solid #527ba5; border-radius: 9px; font-weight: 900; padding: 7px 14px; }
    QPushButton#postFocusContinue:hover { background-color: #294760; border-color: #6b95bf; }
    QLabel#postFocusEyebrow { color: #8ca4bb; font-size: 8.3pt; font-weight: 800; }
    QLabel#postFocusTime { color: #a9d3ff; font-size: 25px; font-weight: 900; }
    QLabel#postFocusStatus, QLabel#postFocusDetail, QLabel#postFocusNote { color: #8ca4bb; }
    QLabel#postFocusContentTitle, QLabel#postFocusQuestion { color: #e0edf8; font-weight: 800; }
    QLabel#postFocusQuestion { font-size: 10.5pt; font-weight: 900; }
    QPushButton#postFocusPrimary { background-color: #416ab7; color: #ffffff; border: 1px solid #4c7bcf; border-radius: 9px; font-weight: 800; padding: 7px 14px; }
    QPushButton#postFocusPrimary:hover { background-color: #355ba3; border-color: #426ec4; }
    QPushButton#postFocusSecondary { background-color: #172536; color: #b9d8f7; border: 1px solid #3a5877; border-radius: 9px; font-weight: 800; padding: 7px 14px; }
    QPushButton#postFocusSecondary:hover { background-color: #20374f; border-color: #527ba5; }
    QPushButton#postFocusGhost { background: transparent; color: #8ca4bb; border: 1px solid #33465a; border-radius: 8px; font-weight: 700; padding: 6px 12px; }
    QPushButton#postFocusGhost:hover { background-color: #1b2a3b; color: #d2e6f8; }
    QPushButton#postFocusSecondary:disabled { color: #627488; background-color: #17202b; border-color: #2b3949; }
    QFrame#focusHeroPanel { background-color: #15283c; border: 1px solid #3b6289; border-radius: 14px; }
    QLabel#focusHeroEyebrow { color: #8ca4bb; font-size: 8.3pt; font-weight: 800; letter-spacing: 0.4px; }
    QLabel#focusHeroValue { color: #a9d3ff; font-size: 24px; font-weight: 900; }
    QLabel#focusHeroStatus { color: #e0edf8; font-size: 10pt; font-weight: 800; }
    QLabel#focusHeroNote, QLabel#focusConfigHint, QLabel#focusHistoryHint, QLabel#focusFieldLabel { color: #8ca4bb; }
    QFrame#focusHeroMiniCard { background-color: #172536; border: 1px solid #3a5877; border-radius: 11px; }
    QLabel#focusHeroMiniLabel { color: #90a8bf; font-size: 8.2pt; font-weight: 700; }
    QLabel#focusHeroMiniValue { color: #d6eaff; font-size: 12pt; font-weight: 900; }
    QLabel#postFocusDialogTitle { color: #e0edf8; font-size: 16px; font-weight: 900; }
    QLabel#postFocusDialogSubtitle { color: #8ca4bb; }
    QFrame#postFocusMiniCard { background-color: #172536; border: 1px solid #365574; border-radius: 10px; }
    QLabel#postFocusMiniLabel { color: #8ca4bb; font-size: 8.2pt; font-weight: 800; }
    QLabel#postFocusMiniValue { color: #d6eaff; font-size: 11.5pt; font-weight: 900; }
    QProgressBar#focusProgressBar { min-height: 8px; max-height: 8px; background-color: #27384a; border: none; border-radius: 4px; }
    QProgressBar#focusProgressBar::chunk { background-color: #4f83c5; border-radius: 4px; }


    


    /* ======================================================
       HOJE OPERACIONAL — ESCURO
       ====================================================== */
    QFrame#dashboardTodayPanel {
        background-color: #111d2b;
        border: 1px solid #33485e;
        border-radius: 12px;
    }
    QLabel#dashboardTodayTitle { color: #eef5ff; font-size: 11.5pt; font-weight: 900; }
    QLabel#dashboardTodayDate {
        color: #b5cee7; background-color: #18283a; border: 1px solid #36516c;
        border-radius: 7px; padding: 3px 8px; font-size: 8.5pt; font-weight: 700;
    }
    QLabel#dashboardTodayStatus { color: #8fa7be; font-size: 8.7pt; font-weight: 700; }
    QFrame#dashboardTodayFocus {
        background-color: #14273a; border: 1px solid #365a7a; border-radius: 10px;
    }
    QFrame#dashboardTodayMetric {
        background-color: #151f2d; border: 1px solid #33465a; border-radius: 10px;
    }
    QFrame#dashboardTodayMetric[metricRole="late"] { background-color: #342320; border-color: #70463f; }
    QFrame#dashboardTodayMetric[metricRole="today"] { background-color: #322a1d; border-color: #6d5a34; }
    QFrame#dashboardTodayMetric[metricRole="ok"] { background-color: #182a22; border-color: #355c46; }
    QFrame#dashboardTodayMetric[metricRole="active"] { background-color: #16283a; border-color: #365a7a; }
    QFrame#dashboardTodayMetric[metricKind="review"] { background-color: #182d24; border-color: #3f7455; }
    QLabel#dashboardTodayEyebrow { color: #8ca4bb; font-size: 7.9pt; font-weight: 900; }
    QLabel#dashboardTodayFocusValue { color: #9dccff; font-size: 15pt; font-weight: 900; }
    QLabel#dashboardTodayMetricValue { color: #e8eef6; font-size: 14pt; font-weight: 900; }
    QFrame#dashboardTodayMetric[metricRole="late"] QLabel#dashboardTodayMetricValue { color: #f0a398; }
    QFrame#dashboardTodayMetric[metricRole="today"] QLabel#dashboardTodayMetricValue { color: #e3bd6a; }
    QFrame#dashboardTodayMetric[metricRole="ok"] QLabel#dashboardTodayMetricValue { color: #8fc5a2; }
    QFrame#dashboardTodayMetric[metricRole="active"] QLabel#dashboardTodayMetricValue { color: #9bc7f2; }
    QFrame#dashboardTodayMetric[metricKind="review"] QLabel#dashboardTodayEyebrow { color: #9bd3ae; }
    QFrame#dashboardTodayMetric[metricKind="review"] QLabel#dashboardTodayMetricValue { color: #7ed49d; }
    QLabel#dashboardTodayDetail { color: #91a6ba; font-size: 8.2pt; }
    QFrame#dashboardQuickAccess { background-color: #162333; border: 1px solid #354b62; border-radius: 12px; }
    QLabel#dashboardQuickAccessTitle { color: #a3b7ca; font-size: 8.6pt; font-weight: 900; }
    QProgressBar#dashboardTodayProgress {
        min-height: 7px; max-height: 7px; background-color: #263b50; border: none; border-radius: 3px;
    }
    QProgressBar#dashboardTodayProgress::chunk { background-color: #4d83c5; border-radius: 3px; }
    QFrame#dashboardTodayAction {
        background-color: #142639; border: 1px solid #365875; border-radius: 10px;
    }
    QFrame#dashboardTodayAction[actionRole="late"] { background-color: #30291c; border-color: #69572f; }
    QFrame#dashboardTodayAction[actionRole="strategic"] { background-color: #24243a; border-color: #4e4d72; }
    QFrame#dashboardTodayAction[actionRole="active"] { background-color: #172b24; border-color: #385e4a; }
    QLabel#dashboardTodayActionTitle { color: #edf4fb; font-size: 10.2pt; font-weight: 900; }
    QPushButton#dashboardTodayPrimaryButton {
        background-color: #416ab7; color: #ffffff; border: 1px solid #4c7bcf;
        border-radius: 9px; font-weight: 900; font-size: 9.5pt; padding: 7px 17px;
    }
    QPushButton#dashboardTodayPrimaryButton:hover { background-color: #355ba3; border-color: #426ec4; }
    QPushButton#dashboardTodayButton {
        background-color: #172536; color: #b9d8f7; border: 1px solid #3a5877;
        border-radius: 8px; font-weight: 800; padding: 6px 13px;
    }
    QPushButton#dashboardTodayButton:hover { background-color: #20374f; border-color: #527ba5; color: #e0f0ff; }

    /* HERO CENTRAL — modo guiado */
    QFrame#dashboardTodayAction[heroCentral="true"] {
        background-color: #14283d; border: 2px solid #416b96; border-radius: 15px;
    }
    QFrame#dashboardTodayAction[heroCentral="true"][actionRole="late"] { background-color: #182335; border-color: #446892; }
    QFrame#dashboardTodayAction[heroCentral="true"][actionRole="strategic"] { background-color: #252641; border-color: #5c5a88; }
    QFrame#dashboardTodayAction[heroCentral="true"][actionRole="active"] { background-color: #183027; border-color: #47765d; }
    QLabel#dashboardGuidedHeroEyebrow { color: #8cc8ff; font-size: 8.4pt; font-weight: 900; letter-spacing: 1px; }
    QFrame#dashboardTodayAction[heroCentral="true"] QLabel#dashboardTodayActionTitle { color: #f1f7ff; font-size: 12.8pt; font-weight: 800; }
    QLabel#dashboardGuidedHeroDetail { color: #b0c5da; font-size: 9pt; font-weight: 700; }
    QLabel#dashboardGuidedHeroGuide { color: #91a9c0; font-size: 8.6pt; }
    QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayPrimaryButton {
        background-color: #4778cc; color: #ffffff; border: 1px solid #6a9be9; border-radius: 11px;
        font-size: 11pt; font-weight: 900; padding: 10px 28px;
    }
    QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayPrimaryButton:hover { background-color: #3d69b7; }
    QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayButton {
        background-color: transparent; border: none; color: #9bc7f2; text-decoration: underline; font-weight: 800; padding: 4px 10px;
    }
    QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayButton:hover { color: #d9edff; }

    QLabel#studyScoreBreakdown { font-weight: 700; }

    /* ======================================================
       CENTRAL DE ATENÇÃO — NOTIFICAÇÕES ÚTEIS V2 / ESCURO
       ====================================================== */

    QFrame#dashboardAttentionCard {
        border-radius: 9px;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"] {
        background-color: #2b271f;
        border: 1px solid #5c5137;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"][alertState="ok"] {
        background-color: #1d2b25;
        border-color: #365545;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"][alertState="critico"] {
        background-color: #322120;
        border-color: #6f4441;
    }

    QFrame#dashboardAttentionCard[attentionRole="pace"] {
        background-color: #1c2835;
        border: 1px solid #36516e;
    }

    QLabel#dashboardAttentionIcon {
        font-size: 11pt;
        font-weight: 800;
        border-radius: 16px;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"] QLabel#dashboardAttentionIcon {
        background-color: #3b321f;
        color: #e1b95f;
        border: 1px solid #6c5a31;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"][alertState="ok"] QLabel#dashboardAttentionIcon {
        background-color: #21382d;
        color: #79bf93;
        border-color: #3f6650;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"][alertState="critico"] QLabel#dashboardAttentionIcon {
        background-color: #432727;
        color: #e38b82;
        border-color: #754541;
    }

    QFrame#dashboardAttentionCard[attentionRole="pace"] QLabel#dashboardAttentionIcon {
        background-color: #213549;
        color: #79b6df;
        border: 1px solid #416b8a;
    }

    QLabel#dashboardAttentionEyebrow {
        color: #8c9aad;
        font-size: 7.5pt;
        font-weight: 700;
    }

    QLabel#dashboardAttentionTitle {
        color: #dde6f1;
        font-size: 9.5pt;
        font-weight: 700;
    }

    QLabel#dashboardAttentionDescription {
        color: #a7b2c1;
        font-size: 8.5pt;
    }

    QLabel#dashboardAttentionMeta {
        color: #94a0af;
        font-size: 8pt;
    }

    QLabel#dashboardAttentionBadge,
    QLabel#dashboardPaceBadge {
        padding: 3px 9px;
        border-radius: 8px;
        font-size: 7.5pt;
        font-weight: 700;
    }

    QLabel#dashboardAttentionBadge {
        background-color: #3b321f;
        color: #e0b968;
        border: 1px solid #66572f;
    }

    QFrame#dashboardAttentionCard[alertState="ok"] QLabel#dashboardAttentionBadge {
        background-color: #21372d;
        color: #79bf93;
        border-color: #3d624e;
    }

    QFrame#dashboardAttentionCard[alertState="critico"] QLabel#dashboardAttentionBadge {
        background-color: #432827;
        color: #e59087;
        border-color: #714641;
    }

    QLabel#dashboardPaceBadge {
        background-color: #21364b;
        color: #84b9dc;
        border: 1px solid #3d6381;
    }

    QFrame#dashboardAttentionFooter {
        background-color: #1d242d;
        border: 1px solid #343e4b;
        border-radius: 7px;
    }

    QLabel#dashboardAttentionFooterItem {
        color: #aeb9c7;
        font-size: 8pt;
        font-weight: 600;
    }

    QLabel#dashboardAttentionFooterHint {
        color: #778393;
        font-size: 7.5pt;
    }

""" + ESTILO_JORNADA_ESCURO + ESTILO_DASHBOARD_MODERNO_ESCURO + ESTILO_FOCO_DASHBOARD_ESCURO + ESTILO_ALGORITMO_DASHBOARD_ESCURO + ESTILO_BUSCA_GLOBAL_ESCURO + ESTILO_INTELIGENCIA_RESUMO_ESCURO + ESTILO_TOPICOS_DISCIPLINA_ESCURO + ESTILO_RESOLVEDOR_ESCURO + ESTILO_TOPICO_DETALHES_ESCURO + ESTILO_RESOLVEDOR_ELIMINADAS_ESCURO + ESTILO_RESOLVEDOR_TECLADO_ESCURO + ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_ESCURO + ESTILO_CALENDARIO_PREVISAO_ESCURO)



def stylesheet_futurista():
    """
    Terceira opção visual do VighnaStudy.

    O tema Futurista herda toda a cobertura de componentes do tema escuro
    e aplica uma camada final de overrides. Isso mantém compatibilidade com
    telas antigas e novas sem alterar os estilos Claro/Escuro existentes.
    """

    return stylesheet_escuro() + render_qss("futurista", r"""

    /* ======================================================
       VIGHNA FUTURISTA — TERCEIRO TEMA
       ====================================================== */

    QMainWindow,
    QDialog,
    QWidget {
        background-color: #07111e;
        color: #eaf7ff;
    }

    /* Correção visual global do Futurista: QLabel/QCheckBox/QRadioButton
       herdam QWidget, mas não devem repintar o fundo-base dentro dos cards.
       Os componentes que realmente precisam de fundo (badges/avisos) mantêm
       seus estilos específicos por objectName. */
    QLabel,
    QCheckBox,
    QRadioButton {
        background-color: transparent;
    }

    QScrollArea,
    QScrollArea > QWidget > QWidget {
        background-color: transparent;
    }

    QLabel#pageTitle {
        color: #f3fbff;
        font-weight: 800;
    }

    QLabel#pageSubtitle,
    QLabel#mutedLabel {
        color: #87a6c2;
    }

    QLabel#questionAlternativeText {
        background: transparent;
        color: #EAF7FF;
    }

    /* Resolver questões — futurista
       Evita faixas escuras internas herdadas do background genérico de QWidget
       e harmoniza a estrutura dos cards de enunciado/alternativas. */
    QFrame#questionSolverStatementCard,
    QFrame#questionSolverAlternative {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #0f1f31,
            stop:0.58 #0b1828,
            stop:1 #091523);
        border: 1px solid #345a7d;
        border-radius: 10px;
    }
    QFrame#questionSolverAlternative[answerState="correta"] {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #123126,
            stop:1 #0d241c);
        border-color: #3ecf8e;
    }
    QFrame#questionSolverAlternative[answerState="errada"] {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #3a1820,
            stop:1 #2a1017);
        border-color: #ff6677;
    }
    QLabel#questionSolverStatement,
    QLabel#questionSolverAlternativeText,
    QLabel#questionSolverMeta,
    QRadioButton#questionSolverRadio,
    QToolButton#questionSolverEliminateButton,
    QCheckBox#questionSessionDoubt,
    QCheckBox#questionSessionAnalysisFlag {
        background: transparent;
    }
    QLabel#questionSolverStatement {
        color: #eef9ff;
    }
    QLabel#questionSolverAlternativeText {
        color: #e6f2fb;
    }
    QFrame#questionSolverAlternative[eliminated="true"][answerState="normal"] {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #07111b,
            stop:1 #050c14);
        border: 1px dashed #31506a;
    }
    QFrame#questionSolverAlternative[eliminated="true"][answerState="normal"]:hover {
        border-color: #3d6787;
    }
    QLabel#questionSolverAlternativeText[eliminated="true"],
    QRadioButton#questionSolverRadio[eliminated="true"] {
        color: #526f84;
    }
    QToolButton#questionSolverEliminateButton:checked {
        background-color: #10283a;
        color: #8eacc2;
        border: 1px solid #3d6787;
        border-radius: 6px;
    }
    QRadioButton#questionSolverRadio {
        color: #d9ecff;
        font-weight: 800;
    }
    QToolButton#questionSolverEliminateButton {
        color: #7f9ab0;
    }
    QToolButton#questionSolverEliminateButton:hover {
        background-color: rgba(124, 176, 221, 0.14);
        color: #dcefff;
        border-radius: 6px;
    }
    QToolButton#questionSolverEliminateButton:checked {
        background-color: rgba(124, 176, 221, 0.20);
        color: #eef9ff;
        border-radius: 6px;
    }

    /* Refinos globais — Futurista
       Camada sutil para os controles de uso geral do programa. */
    QPushButton {
        background-color: {{color:action.secondary}};
        color: {{color:text.primary}};
        border: 1px solid {{color:border.strong}};
        border-radius: 9px;
        padding: 6px 12px;
    }
    QPushButton:hover {
        background-color: {{color:action.secondary_hover}};
        border-color: {{color:border.hover}};
        color: {{color:text.interactive_hover}};
    }
    QPushButton:pressed {
        background-color: {{color:action.secondary_pressed}};
        border-color: {{color:border.active}};
    }
    QPushButton:disabled {
        background-color: {{color:action.secondary_disabled}};
        color: {{color:text.disabled}};
        border-color: {{color:border.disabled}};
    }

    QToolButton {
        background-color: transparent;
        color: #bddcff;
        border: 1px solid transparent;
        border-radius: 7px;
        padding: 4px 8px;
    }
    QToolButton:hover {
        background-color: rgba(108, 168, 214, 0.10);
        border-color: #376688;
        color: #edf9ff;
    }

    QLineEdit,
    QTextEdit,
    QPlainTextEdit,
    QAbstractSpinBox,
    QComboBox {
        background-color: {{color:surface.primary}};
        color: {{color:text.control_subtle}};
        border: 1px solid {{color:border.control_subtle}};
        border-radius: 9px;
        padding: 6px 10px;
        selection-background-color: {{color:overlay.selection_subtle}};
        selection-color: {{color:text.on_action}};
    }
    QLineEdit:hover,
    QTextEdit:hover,
    QPlainTextEdit:hover,
    QAbstractSpinBox:hover,
    QComboBox:hover {
        border-color: {{color:border.control_hover}};
    }
    QLineEdit:focus,
    QTextEdit:focus,
    QPlainTextEdit:focus,
    QAbstractSpinBox:focus,
    QComboBox:focus {
        border: 1px solid {{color:border.focus}};
        background-color: {{color:surface.focused}};
    }
    QLineEdit[readOnly="true"],
    QTextEdit[readOnly="true"],
    QPlainTextEdit[readOnly="true"] {
        background-color: {{color:canvas.inset}};
        color: {{color:text.readonly}};
    }
    QComboBox QAbstractItemView {
        background-color: #0d1d2d;
        color: #e7f5ff;
        border: 1px solid #3a688c;
        selection-background-color: #1d466d;
        selection-color: #ffffff;
        outline: none;
    }

    QListWidget,
    QTreeWidget,
    QTableWidget,
    QTableView {
        background-color: #0c1a29;
        alternate-background-color: #102032;
        color: #e4f3ff;
        border: 1px solid #315a7a;
        border-radius: 10px;
        gridline-color: #264760;
        selection-background-color: #1d4f79;
        selection-color: #ffffff;
    }
    QHeaderView::section {
        background-color: #102235;
        color: #cfe9ff;
        border: 1px solid #315a7a;
        padding: 6px 8px;
        font-weight: 800;
    }

    QTabWidget::pane {
        border: 1px solid #315a7a;
        background-color: #0c1a29;
        border-radius: 10px;
        top: -1px;
    }
    QTabBar::tab {
        background-color: #0f2235;
        color: #a9cae2;
        border: 1px solid #315a7a;
        border-bottom: none;
        border-top-left-radius: 9px;
        border-top-right-radius: 9px;
        padding: 7px 12px;
        margin-right: 3px;
        font-weight: 700;
    }
    QTabBar::tab:selected {
        background-color: #17344e;
        color: #f1fbff;
        border-color: #5faed8;
    }
    QTabBar::tab:hover:!selected {
        background-color: #13304a;
        color: #dff4ff;
    }

    QGroupBox {
        border: 1px solid #315a7a;
        border-radius: 10px;
        margin-top: 12px;
        padding-top: 10px;
        color: #e4f3ff;
        background-color: rgba(12, 26, 41, 0.35);
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
        color: #9fd6f5;
        font-weight: 800;
    }

    QCheckBox,
    QRadioButton {
        color: {{color:text.choice}};
        spacing: 8px;
    }
    QCheckBox::indicator,
    QRadioButton::indicator {
        width: 16px;
        height: 16px;
    }
    QCheckBox::indicator {
        background-color: {{color:surface.primary}};
        border: 1px solid {{color:border.control_indicator}};
        border-radius: 4px;
    }
    QRadioButton::indicator {
        background-color: {{color:surface.primary}};
        border: 1px solid {{color:border.control_indicator}};
        border-radius: 8px;
    }
    QCheckBox::indicator:checked,
    QRadioButton::indicator:checked {
        background-color: {{color:action.checked}};
        border-color: {{color:border.checked}};
    }

    QProgressBar {
        background-color: {{color:progress.track}};
        color: {{color:progress.text}};
        border: 1px solid {{color:progress.border}};
        border-radius: 6px;
        text-align: center;
    }
    QProgressBar::chunk {
        background-color: {{color:progress.fill}};
        border-radius: 5px;
    }

    QMenu {
        background-color: #0d1d2d;
        color: #e7f5ff;
        border: 1px solid #376486;
    }
    QMenu::item {
        padding: 6px 22px 6px 16px;
        background-color: transparent;
    }
    QMenu::item:selected {
        background-color: #17324b;
        color: #ffffff;
    }
    QToolTip {
        background-color: {{color:surface.inverse}};
        color: {{color:text.control}};
        border: 1px solid {{color:border.selected}};
        padding: 5px 7px;
    }

    QScrollBar:vertical {
        background-color: #08131f;
        width: 12px;
        margin: 2px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical {
        background-color: #274761;
        min-height: 28px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #35658b;
    }
    QScrollBar:horizontal {
        background-color: #08131f;
        height: 12px;
        margin: 2px;
        border-radius: 6px;
    }
    QScrollBar::handle:horizontal {
        background-color: #274761;
        min-width: 28px;
        border-radius: 6px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #35658b;
    }
    QScrollBar::add-line,
    QScrollBar::sub-line,
    QScrollBar::add-page,
    QScrollBar::sub-page {
        background: none;
        border: none;
    }

    QFrame#dashboardCenterBar,
    QFrame#contextBar,
    QFrame#syllabusProgressPanel,
    QFrame#planningPanel {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #0e2034,
            stop:0.55 #0a1829,
            stop:1 #071321);
        border: 1px solid #315c84;
        border-radius: 15px;
    }

    QFrame#cardResumo {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #162b42,
            stop:0.55 #102238,
            stop:1 #0b192b);
        border: 1px solid #3b6388;
        border-radius: 14px;
    }

    QFrame#cardResumo:hover {
        border: 1px solid #52ddff;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #19334c,
            stop:1 #0d2035);
    }

    QFrame#cardResumo[metricRole="performance"] {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #103a3b,
            stop:0.55 #11303a,
            stop:1 #0c2032);
        border: 1px solid #50e2bc;
    }

    QLabel#cardTitulo {
        color: #a8bfd5;
        font-weight: 600;
    }

    QLabel#cardValor {
        color: #d6eaff;
        font-size: 22px;
        font-weight: 800;
    }

    QFrame#cardResumo[metricRole="performance"] QLabel#cardValor {
        color: #67efc2;
    }

    QLabel#profileBadge {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #173f61,
            stop:1 #332668);
        color: #afeaff;
        border: 1px solid #50a9e5;
        border-radius: 9px;
        padding: 5px 11px;
        font-weight: 800;
    }

    QPushButton#toolbarButton,
    QPushButton#subtleButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #162b42,
            stop:1 #0d1d30);
        color: #e7f5ff;
        border: 1px solid #40688d;
        border-radius: 10px;
        font-weight: 600;
    }

    QPushButton#toolbarButton:hover,
    QPushButton#subtleButton:hover {
        border: 1px solid #56dfff;
        color: #c8f6ff;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #1a3854,
            stop:1 #10263d);
    }

    QPushButton#questionsNavButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #0f6173,
            stop:0.5 #195f87,
            stop:1 #30499e);
        color: #c5fbff;
        border: 1px solid #55efff;
        border-radius: 10px;
        font-weight: 800;
    }

    QPushButton#questionsNavButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #137689,
            stop:1 #3a58b9);
        border: 1px solid #89f6ff;
    }

    QPushButton#topAccentButton,
    QPushButton#primaryButton,
    QPushButton#syllabusOpenButton,
    QPushButton#syllabusAlertButton,
    QPushButton#syllabusForecastButton,
    QPushButton#planningGoalButton,
    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton,
    QPushButton#effectivenessOpenButton,
    QPushButton#questionsEffectivenessButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #405dec,
            stop:0.5 #685ff1,
            stop:1 #8a4fe8);
        color: #ffffff;
        border: 1px solid #8c89ff;
        border-radius: 10px;
        font-weight: 800;
    }

    QPushButton#topAccentButton:hover,
    QPushButton#primaryButton:hover,
    QPushButton#syllabusOpenButton:hover,
    QPushButton#syllabusAlertButton:hover,
    QPushButton#syllabusForecastButton:hover,
    QPushButton#planningGoalButton:hover,
    QPushButton#planningSummaryButton:hover,
    QPushButton#planningRedistributeButton:hover,
    QPushButton#effectivenessOpenButton:hover,
    QPushButton#questionsEffectivenessButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #526cff,
            stop:1 #985eff);
        border: 1px solid #b6b3ff;
    }

    QFrame#syllabusDashboardCoverage,
    QFrame#syllabusDashboardStat,
    QFrame#dailyGoalBox,
    QFrame#weeklyLoadBox,
    QFrame#weeklyGoalBox,
    QFrame#weeklyGoalMetric,
    QFrame#weekDayLoad {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #132a41,
            stop:1 #0b1a2c);
        border: 1px solid #385d80;
        border-radius: 11px;
    }

    QFrame#weekDayLoad[today="true"] {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #30265f,
            stop:1 #0f4960);
        border: 1px solid #69efff;
    }

    QFrame#weekDayLoad[today="true"] QLabel#weekDayName,
    QFrame#weekDayLoad[today="true"] QLabel#weekDayDate,
    QFrame#weekDayLoad[today="true"] QLabel#weekDayCount {
        color: #d9fcff;
        font-weight: 800;
    }

    QFrame#weekDayLoad[loadLevel="leve"][today="false"] {
        border-color: #43ad89;
    }

    QFrame#weekDayLoad[loadLevel="moderada"][today="false"] {
        border-color: #bf8d42;
    }

    QFrame#weekDayLoad[loadLevel="alta"][today="false"] {
        border-color: #c65f72;
    }

    QFrame#syllabusAlertStrip,
    QFrame#syllabusAlertStrip[alertState="monitorar"],
    QFrame#syllabusAlertStrip[alertState="atencao"] {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #3a2413,
            stop:1 #1b1d20);
        border: 1px solid #d08c31;
        border-radius: 11px;
    }

    QFrame#syllabusForecastStrip {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #182240,
            stop:1 #0d1a2a);
        border: 1px solid #5778d8;
        border-radius: 11px;
    }

    QLabel#syllabusAlertIcon,
    QLabel#syllabusAlertText {
        color: #f2b654;
    }

    QLabel#syllabusForecastIcon,
    QLabel#syllabusForecastText {
        color: #7fd8ff;
    }

    QLabel#syllabusAlertSummary,
    QLabel#syllabusForecastSummary {
        color: #c9d7e7;
    }

    QProgressBar#syllabusDashboardBar,
    QProgressBar#dailyGoalProgress,
    QProgressBar#weeklyGoalProgress,
    QProgressBar#questionSessionProgress,
    QProgressBar#topicDomainBar {
        background-color: #18304a;
        border: 1px solid #31506d;
        border-radius: 5px;
    }

    QProgressBar#syllabusDashboardBar::chunk,
    QProgressBar#dailyGoalProgress::chunk,
    QProgressBar#weeklyGoalProgress::chunk,
    QProgressBar#questionSessionProgress::chunk,
    QProgressBar#topicDomainBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #4de7ff,
            stop:0.5 #7279ff,
            stop:1 #62efbd);
        border-radius: 5px;
    }

    QLineEdit,
    QComboBox,
    QSpinBox,
    QDateEdit,
    QTextEdit {
        background: {{gradient:gradient.control_input}};
        color: {{color:text.control}};
        border: 1px solid {{color:border.default}};
        border-radius: 10px;
        selection-background-color: {{color:overlay.selection}};
        selection-color: {{color:text.on_action}};
    }

    QLineEdit:focus,
    QComboBox:focus,
    QSpinBox:focus,
    QDateEdit:focus,
    QTextEdit:focus {
        border: 1px solid {{color:focus.ring}};
    }

    QComboBox QAbstractItemView {
        background-color: {{color:surface.elevated}};
        color: {{color:text.popup}};
        selection-background-color: {{color:action.ghost_hover}};
        selection-color: {{color:text.selection_accent}};
        border: 1px solid {{color:border.default}};
    }

    QTableWidget,
    QTreeWidget {
        background-color: {{color:surface.secondary}};
        color: {{color:text.secondary}};
        border: 1px solid {{color:border.subtle}};
        border-radius: 10px;
        gridline-color: {{color:border.grid}};
        selection-background-color: {{color:surface.selected}};
        selection-color: {{color:text.on_action}};
    }

    QHeaderView::section {
        background: {{gradient:gradient.control_header}};
        color: {{color:text.header}};
        border: none;
        border-right: 1px solid {{color:border.divider}};
        border-bottom: 1px solid {{color:border.divider_strong}};
        padding: 8px;
        font-weight: 700;
    }

    QTabWidget::pane {
        background-color: {{color:surface.secondary}};
        border: 1px solid {{color:border.subtle}};
        border-radius: 10px;
    }

    QTabBar::tab {
        background: {{gradient:gradient.control_tab}};
        color: {{color:text.muted}};
        border: 1px solid #315573;
        border-bottom: none;
        border-top-left-radius: 9px;
        border-top-right-radius: 9px;
        padding: 8px 14px;
        margin-right: 3px;
    }

    QTabBar::tab:selected {
        background: {{gradient:gradient.control_selected}};
        color: {{color:text.link}};
        border: 1px solid #55e7ff;
        font-weight: 800;
    }

    QFrame#effectivenessCalibrationCard,
    QFrame#effectivenessImpactCard,
    QFrame#adaptiveSessionConfigCard,
    QFrame#adaptiveTopicsCard,
    QFrame#adaptivePreviewCard,
    QFrame#adaptiveSummaryCard,
    QFrame#questionsAdaptiveBar,
    QFrame#mockExamConfigCard {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #12283f,
            stop:1 #09192b);
        border: 1px solid #37628a;
        border-radius: 11px;
    }

    QLabel#effectivenessCalibrationTitle,
    QLabel#effectivenessImpactTitle,
    QLabel#adaptiveSectionTitle,
    QLabel#adaptiveSummaryTitle,
    QLabel#questionsAdaptiveTitle,
    QLabel#mockExamSectionTitle {
        color: #aeeeff;
    }

    QPushButton#adaptiveSessionStartButton,
    QPushButton#adaptiveDashboardButton,
    QPushButton#questionsAdaptiveButton,
    QPushButton#mockExamStartButton,
    QPushButton#mockExamDashboardButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #216bcb,
            stop:0.5 #535fe2,
            stop:1 #7c48dc);
        color: #ffffff;
        border: 1px solid #6fa8ff;
        border-radius: 9px;
        font-weight: 800;
    }

    QPushButton#questionsMockExamButton {
        background-color: #152843;
        color: #c7d6ff;
        border: 1px solid #6d75d9;
        border-radius: 8px;
        font-weight: 800;
    }

    QLabel#mockExamTimer {
        background-color: #152a46;
        color: #9eeeff;
        border: 1px solid #42cae9;
        border-radius: 8px;
        font-weight: 900;
    }

    QScrollBar:vertical {
        background: {{color:surface.inset}};
        width: 10px;
        border: none;
    }

    QScrollBar::handle:vertical {
        background: {{color:surface.interactive}};
        min-height: 28px;
        border-radius: 5px;
    }

    QScrollBar::handle:vertical:hover {
        background: {{color:surface.hover}};
    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {
        background: {{color:action.ghost}};
        height: 0px;
    }


    /* Dashboard: Estudar / Avaliar / Revisões prioritárias */
    QFrame#studyNowPanel,
    QFrame#priorityQueuePanel {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(10,24,40,245),
            stop:1 rgba(7,16,29,245)
        );
        border: 1px solid #285e82;
        border-radius: 13px;
    }

    QLabel#dashboardActionSectionTitle {
        color: #b9efff;
        font-size: 9.5pt;
        font-weight: 900;
    }

    QLabel#dashboardActionSectionSubtitle,
    QLabel#studyActionDescription,
    QLabel#studyScoreBreakdown,
    QLabel#priorityQueueExplanation,
    QLabel#assessmentDescription {
        color: #8fb1c9;
        font-size: 8.6pt;
    }

    QFrame#studyActionCard {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(14,35,53,245),
            stop:1 rgba(11,22,39,245)
        );
        border: 1px solid #315b78;
        border-radius: 11px;
    }

    QFrame#studyActionCard[actionRole="review"] {
        border: 1px solid #38aee3;
    }

    QFrame#studyActionCard[actionRole="adaptive"] {
        border: 1px solid #736bdf;
    }

    QLabel#studyActionTitle {
        color: #d8f7ff;
        font-size: 9.6pt;
        font-weight: 900;
    }

    QLabel#studyActionMetric {
        color: #72ddff;
        font-size: 11pt;
        font-weight: 800;
    }

    QLabel#studyReviewSourceBadge,
    QLabel#priorityQueueSourceBadge {
        background-color: rgba(12,77,101,220);
        color: #9bf2ff;
        border: 1px solid #3bc9e8;
        border-radius: 7px;
        padding: 3px 7px;
        font-size: 7.4pt;
        font-weight: 800;
    }

    QLabel#studyAdaptiveCriteria {
        color: #afa9ff;
        font-size: 8.3pt;
        font-weight: 700;
    }

    QPushButton#studyManualButton {
        background-color: rgba(16,31,49,240);
        color: #b8d9ed;
        border: 1px solid #3f6f8e;
        border-radius: 8px;
        padding: 6px 10px;
        font-weight: 700;
    }

    QPushButton#smartReviewDashboardButton {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #1978a6,
            stop:1 #2f6be0
        );
        color: #ffffff;
        border: 1px solid #54d8ff;
        border-radius: 8px;
        font-weight: 900;
    }

    QPushButton#adaptiveDashboardButton {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #4d55d7,
            stop:1 #8453e4
        );
        color: #ffffff;
        border: 1px solid #9a8cff;
        border-radius: 8px;
        font-weight: 900;
    }

    QFrame#assessmentPanel {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(10,38,55,245),
            stop:0.55 rgba(13,24,48,245),
            stop:1 rgba(31,20,64,245)
        );
        border: 1px solid #4b91c7;
        border-radius: 13px;
    }

    QLabel#assessmentTitle {
        color: #79ecff;
        font-size: 11pt;
        font-weight: 900;
    }

    QLabel#assessmentBadge {
        background-color: rgba(55,37,105,225);
        color: #d0c8ff;
        border: 1px solid #8675ec;
        border-radius: 7px;
        padding: 3px 7px;
        font-size: 7.5pt;
        font-weight: 900;
    }

    QLabel#assessmentHeadline {
        color: #f0f8ff;
        font-size: 10pt;
        font-weight: 800;
    }

    QFrame#assessmentStat {
        background-color: rgba(10,24,42,230);
        border: 1px solid #3c6a91;
        border-radius: 8px;
    }

    QLabel#assessmentStatLabel {
        color: #87a9c0;
        font-size: 7.7pt;
    }

    QLabel#assessmentStatValue {
        color: #9defff;
        font-size: 11pt;
        font-weight: 900;
    }

    QPushButton#mockExamDashboardButton {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #1f75b0,
            stop:1 #6658df
        );
        color: #ffffff;
        border: 1px solid #65dfff;
        border-radius: 9px;
        font-weight: 900;
        padding: 7px 12px;
    }




    /* Estudar Agora — composição compacta */

    QFrame#studyNowPanel {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #0b2033,
            stop:0.55 #08192b,
            stop:1 #071422
        );
        border: 1px solid #2c658b;
        border-radius: 14px;
    }

    QFrame#studyManualFooter {
        background-color: #081827;
        border: 1px solid #2c658b;
        border-radius: 10px;
    }

    QLabel#studyNowIcon {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #123e62,
            stop:1 #2d285f
        );
        border: 1px solid #56dbff;
        border-radius: 14px;
        font-size: 27px;
    }

    QLabel#dashboardActionSectionTitle {
        color: #d9f7ff;
        font-size: 16pt;
        font-weight: 900;
    }

    QLabel#dashboardActionSectionSubtitle {
        color: #8db2ca;
        font-size: 9pt;
    }

    QLabel#studyColumnTitle {
        color: #c8efff;
        font-size: 11pt;
        font-weight: 900;
    }

    QFrame#studyActionCard,
    QFrame#strategyCompactCard {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(15,37,57,245),
            stop:1 rgba(9,23,40,245)
        );
        border: 1px solid #315d7c;
        border-radius: 11px;
    }

    QFrame#studyActionCard[actionRole="review"] {
        border: 1px solid #3ccff0;
    }

    QFrame#strategyCompactCard[actionRole="adaptive"] {
        border: 1px solid #8076ef;
    }

    QFrame#strategyCompactCard[actionRole="simulation"] {
        border: 1px solid #e0a641;
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(45,34,16,245),
            stop:1 rgba(16,24,38,245)
        );
    }

    QLabel#studyCardIcon {
        background-color: rgba(8,75,93,225);
        border: 1px solid #4ae8f7;
        border-radius: 13px;
        font-size: 25px;
    }

    QLabel#strategyCardIcon {
        background-color: rgba(53,40,107,225);
        border: 1px solid #8f80f5;
        border-radius: 13px;
        font-size: 24px;
    }

    QFrame#strategyCompactCard[actionRole="simulation"] QLabel#strategyCardIcon {
        background-color: rgba(104,67,10,225);
        border-color: #f0b24a;
    }

    QLabel#studyActionTitle,
    QLabel#strategyCardTitle {
        color: #f0fbff;
        font-size: 12pt;
        font-weight: 900;
    }

    QLabel#studyReviewCount {
        color: #94c7d9;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QLabel#studyActionDescription,
    QLabel#strategyCardDescription,
    QLabel#studyReviewFooter {
        color: #91adbf;
        font-size: 8.6pt;
    }

    QLabel#studyReviewDetail {
        color: #d7f6ff;
        font-size: 8.8pt;
        font-weight: 700;
    }

    QLabel#studyReviewSourceBadge {
        background-color: rgba(12,77,101,225);
        color: #a5f2ff;
        border: 1px solid #3bc9e8;
        border-radius: 7px;
        padding: 3px 7px;
        font-size: 7.3pt;
        font-weight: 900;
    }

    QLabel#studyAdaptiveCriteria {
        color: #bdb5ff;
        font-size: 8.1pt;
        font-weight: 700;
    }

    QPushButton#studyManualButton,
    QPushButton#smartReviewDashboardButton {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #1b79a7,
            stop:1 #2d67db
        );
        color: #ffffff;
        border: 1px solid #55dfff;
        border-radius: 9px;
        font-weight: 900;
    }

    QPushButton#adaptiveDashboardButton {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #4f58d8,
            stop:1 #8555e5
        );
        color: #ffffff;
        border: 1px solid #9d91ff;
        border-radius: 9px;
        font-weight: 900;
    }

    QPushButton#mockExamDashboardButton {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #bc7010,
            stop:1 #e69a15
        );
        color: #ffffff;
        border: 1px solid #f0b047;
        border-radius: 9px;
        font-weight: 900;
    }

    QLabel#assessmentBadge {
        background-color: rgba(111,73,13,225);
        color: #ffd88b;
        border: 1px solid #e7a842;
        border-radius: 7px;
        padding: 3px 6px;
        font-size: 7pt;
        font-weight: 900;
    }

    QFrame#assessmentStat {
        background-color: rgba(9,28,45,230);
        border: 1px solid #396583;
        border-radius: 7px;
    }

    QLabel#assessmentStatLabel {
        color: #83a7bd;
        font-size: 7.3pt;
    }

    QLabel#assessmentStatValue {
        color: #a6ecff;
        font-size: 10pt;
        font-weight: 900;
    }




    /* Dashboard superior V1 */

    QFrame#dashboardHeroCard {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #0d2236,
            stop:1 #081626
        );
        border: 1px solid #326889;
        border-radius: 14px;
    }

    QFrame#dashboardHeroCard[heroRole="performance"] {
        border-color: #42cdbf;
    }

    QLabel#dashboardHeroTitle {
        color: #d9f7ff;
        font-size: 12.5pt;
        font-weight: 900;
    }

    QLabel#dashboardHeroInfo {
        color: #80b8d2;
        font-size: 13pt;
        font-weight: 700;
    }

    QFrame#dashboardStatusPill[statusRole="today"] {
        background-color: rgba(21,80,65,225);
        border: 1px solid #4bdaa8;
        border-radius: 9px;
    }

    QFrame#dashboardStatusPill[statusRole="late"] {
        background-color: rgba(91,55,13,225);
        border: 1px solid #e0a03c;
        border-radius: 9px;
    }

    QLabel#dashboardStatusPillLabel,
    QLabel#dashboardStatusPillValue {
        font-size: 11pt;
        font-weight: 900;
    }

    QFrame#dashboardStatusPill[statusRole="today"] QLabel {
        color: #93ffd4;
    }

    QFrame#dashboardStatusPill[statusRole="late"] QLabel {
        color: #ffd081;
    }

    QPushButton#dashboardProgressTitleButton {
        background: transparent;
        border: none;
        color: #d9f7ff;
        text-align: left;
        padding: 0px;
        font-size: 12.5pt;
        font-weight: 900;
    }

    QLabel#dashboardContestLabel {
        color: #b2cee0;
        font-weight: 700;
    }

    QComboBox#dashboardContestCombo {
        background-color: #10263a;
        color: #eaf8ff;
        border: 1px solid #447293;
        border-radius: 9px;
        padding: 5px 9px;
    }

    QFrame#dashboardProgressDivider {
        background-color: #2e5875;
        border: none;
    }

    QLabel#dashboardProgressSubtitle {
        color: #8fadc2;
    }

    QLabel#dashboardProgressPercent {
        color: #eaffff;
        font-size: 11pt;
        font-weight: 900;
    }

    QProgressBar#dashboardHeroProgressBar {
        background-color: #1b3041;
        border: 1px solid #2c526c;
        border-radius: 8px;
    }

    QProgressBar#dashboardHeroProgressBar::chunk {
        background-color: #2cd8dd;
        border-radius: 8px;
    }

    QLabel#dashboardProgressLegendLabel,
    QLabel#dashboardProgressLegendValue {
        color: #c5dbe8;
        font-size: 8.2pt;
    }

    QLabel#dashboardProgressLegendValue {
        font-weight: 900;
    }

    QFrame#dashboardProgressLegend[legendRole="notStarted"] QLabel#dashboardProgressLegendDot {
        color: #718697;
    }

    QFrame#dashboardProgressLegend[legendRole="worked"] QLabel#dashboardProgressLegendDot {
        color: #31ddea;
    }

    QFrame#dashboardProgressLegend[legendRole="consolidating"] QLabel#dashboardProgressLegendDot {
        color: #bd75ff;
    }

    QFrame#dashboardProgressLegend[legendRole="consolidated"] QLabel#dashboardProgressLegendDot {
        color: #63efac;
    }

    QFrame#dashboardDomainBadge {
        background-color: rgba(13,38,57,230);
        border: 1px solid #3d6e8d;
        border-radius: 7px;
    }

    QLabel#dashboardDomainLabel {
        color: #86abc0;
    }

    QLabel#dashboardDomainValue {
        color: #9beeff;
        font-weight: 900;
    }

    QFrame#dashboardNotificationsPanel {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #0d2236,
            stop:1 #081626
        );
        border: 1px solid #326889;
        border-radius: 13px;
    }

    QLabel#dashboardNotificationsTitle {
        color: #d9f7ff;
        font-size: 11.5pt;
        font-weight: 900;
    }

    QLabel#dashboardNotificationsMenu {
        color: #78aeca;
        font-weight: 900;
    }

    QFrame#dashboardAlertActionCard {
        background-color: rgba(73,48,15,235);
        border: 1px solid #d89a38;
        border-radius: 12px;
    }

    QLabel#dashboardAlertActionIcon {
        color: #ffc66d;
        font-size: 17pt;
        font-weight: 900;
    }

    QLabel#dashboardAlertActionSummary {
        color: #f0ce94;
        font-weight: 800;
    }

    QFrame#dashboardQuickStats {
        background-color: #0d2134;
        border: 1px solid #315d7d;
        border-radius: 11px;
    }

    QLabel#dashboardQuickStatLabel {
        color: #8dabbe;
    }

    QLabel#dashboardQuickStatValue {
        color: #d9f7ff;
        font-size: 10pt;
        font-weight: 900;
    }




    /* Central de avisos do edital */

    QFrame#dashboardNotificationsPanel {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #0d2236,
            stop:1 #081626
        );
        border: 1px solid #326889;
        border-radius: 13px;
    }

    QLabel#dashboardNotificationsTitle {
        color: #d9f7ff;
        font-size: 11.5pt;
        font-weight: 900;
    }

    QLabel#dashboardNotificationsSubtitle {
        color: #81a7bd;
        font-size: 8pt;
    }

    QFrame#dashboardNoticeRow {
        border-left: none;
        border-right: none;
        border-bottom: none;
        border-radius: 0px;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] {
        background-color: rgba(72,47,13,235);
        border-top: 1px solid #d49a38;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"][alertState="ok"] {
        background-color: rgba(13,60,49,235);
        border-top: 1px solid #3fc494;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"][alertState="critico"] {
        background-color: rgba(79,31,31,235);
        border-top: 1px solid #de655f;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] {
        background-color: rgba(10,35,56,235);
        border-top: 1px solid #386c91;
    }

    QLabel#dashboardNoticeIcon {
        background-color: rgba(32,24,11,220);
        color: #ffd16f;
        border: 1px solid #d89c3b;
        border-radius: 9px;
        font-size: 15pt;
        font-weight: 900;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeIcon {
        background-color: rgba(10,35,54,220);
        color: #7de4ff;
        border-color: #3ab7dc;
    }

    QLabel#dashboardNoticeLabel {
        color: #91aec1;
        font-size: 7.2pt;
        font-weight: 900;
    }

    QLabel#dashboardNoticeTitle {
        color: #e5faff;
        font-size: 9.4pt;
        font-weight: 800;
    }

    QLabel#dashboardNoticeDescription {
        color: #96b4c7;
        font-size: 8.2pt;
    }

    QLabel#dashboardNoticeSummary {
        background-color: rgba(34,25,11,220);
        color: #f2cb7a;
        border: 1px solid #a77b31;
        border-radius: 7px;
        padding: 4px 7px;
        font-size: 7.8pt;
        font-weight: 800;
    }

    QFrame#dashboardNoticeRow[alertState="ok"] QLabel#dashboardNoticeSummary {
        color: #86efbb;
        border-color: #398f6d;
    }

    QFrame#dashboardNotificationsFooter {
        background-color: rgba(7,19,32,235);
        border-top: 1px solid #28526e;
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
    }

    QLabel#dashboardQuickStatLabel {
        color: #81a2b8;
        font-size: 8pt;
    }

    QLabel#dashboardQuickStatValue {
        color: #d9f7ff;
        font-size: 9.3pt;
        font-weight: 900;
    }

    QLabel#dashboardNotificationsFooterText {
        color: #64869c;
        font-size: 7.7pt;
    }




    /* REFINO CLEAN V1 — FUTURISTA */

    QLabel#pageTitle {
        color: #e7f5fb;
        font-size: 18pt;
        font-weight: 700;
    }

    QLabel#pageSubtitle {
        color: #7f9fb4;
        font-size: 9pt;
        font-weight: 400;
    }

    QPushButton#toolbarButton,
    QPushButton#topAccentButton {
        min-height: 34px;
        padding: 5px 12px;
        font-size: 9pt;
        font-weight: 600;
        border-radius: 8px;
    }

    QPushButton#toolbarButton {
        background-color: #102033;
        color: #d2e4ef;
        border: 1px solid #31516a;
    }

    QPushButton#topAccentButton {
        background-color: #375f9f;
        color: #ffffff;
        border: 1px solid #4777ba;
    }

    QFrame#dashboardHeroCard,
    QFrame#dashboardNotificationsPanel,
    QFrame#planningPanel,
    QFrame#studyNowPanel,
    QFrame#priorityQueuePanel {
        border-radius: 11px;
        border-color: #2d5874;
    }

    QLabel#dashboardHeroTitle,
    QPushButton#dashboardProgressTitleButton {
        color: #dbeef7;
        font-size: 10.5pt;
        font-weight: 700;
    }

    QLabel#dashboardHeroInfo {
        color: #7293a8;
        font-size: 9.5pt;
        font-weight: 600;
    }

    QLabel#dashboardStatusPillLabel {
        font-size: 8.5pt;
        font-weight: 600;
    }

    QLabel#dashboardStatusPillValue {
        font-size: 10pt;
        font-weight: 700;
    }

    QLabel#dashboardProgressPercent {
        font-size: 10pt;
        font-weight: 700;
    }

    QLabel#dashboardProgressLegendLabel,
    QLabel#dashboardProgressLegendValue {
        font-size: 7.8pt;
    }

    QLabel#dashboardProgressLegendValue,
    QLabel#dashboardDomainValue {
        font-weight: 700;
    }

    QLabel#dashboardNotificationsTitle {
        color: #dbeef7;
        font-size: 10pt;
        font-weight: 700;
    }

    QLabel#dashboardNotificationsSubtitle {
        color: #7898ad;
        font-size: 7.7pt;
    }

    QLabel#dashboardNoticeIcon {
        background-color: transparent;
        border: none;
        font-size: 12pt;
        font-weight: 700;
    }

    QLabel#dashboardNoticeLabel {
        color: #7f9db0;
        font-size: 6.8pt;
        font-weight: 700;
    }

    QLabel#dashboardNoticeTitle {
        color: #d8ebf5;
        font-size: 8.7pt;
        font-weight: 600;
    }

    QLabel#dashboardNoticeDescription {
        color: #819fb2;
        font-size: 7.8pt;
    }

    QLabel#dashboardNoticeSummary {
        background-color: transparent;
        border: none;
        color: #c8ab72;
        font-size: 7.5pt;
        font-weight: 600;
        padding: 0px;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] {
        background-color: rgba(54,41,20,220);
        border-top: 1px solid #806733;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] {
        background-color: rgba(10,30,48,225);
        border-top: 1px solid #2c5570;
    }

    QLabel#dashboardQuickStatLabel {
        color: #7898ad;
        font-size: 7.7pt;
    }

    QLabel#dashboardQuickStatValue {
        color: #d8ebf5;
        font-size: 8.7pt;
        font-weight: 700;
    }

    QLabel#studyNowIcon,
    QLabel#studyCardIcon,
    QLabel#strategyCardIcon {
        background-color: transparent;
        border: none;
        color: #77a5bd;
        font-size: 15pt;
        font-weight: 600;
    }

    QLabel#dashboardActionSectionTitle {
        color: #dbeef7;
        font-size: 13pt;
        font-weight: 700;
    }

    QLabel#dashboardActionSectionSubtitle {
        color: #819fb2;
        font-size: 8.5pt;
        font-weight: 400;
    }

    QLabel#studyColumnTitle {
        color: #bdd4df;
        font-size: 9.5pt;
        font-weight: 700;
    }

    QLabel#studyActionTitle,
    QLabel#strategyCardTitle {
        color: #d8eaf3;
        font-size: 10.5pt;
        font-weight: 700;
    }

    QLabel#studyReviewCount {
        color: #7f9db1;
        font-size: 8pt;
        font-weight: 500;
    }

    QLabel#studyActionDescription,
    QLabel#strategyCardDescription,
    QLabel#studyReviewFooter {
        color: #819fb2;
        font-size: 8pt;
        font-weight: 400;
    }

    QLabel#studyReviewDetail {
        color: #adc4d1;
        font-size: 8.2pt;
        font-weight: 600;
    }

    QLabel#studyReviewSourceBadge,
    QLabel#priorityQueueSourceBadge,
    QLabel#assessmentBadge {
        border-radius: 6px;
        padding: 2px 6px;
        font-size: 6.7pt;
        font-weight: 600;
    }

    QLabel#studyAdaptiveCriteria {
        color: #9292b8;
        font-size: 7.6pt;
        font-weight: 500;
    }

    QPushButton#studyManualButton,
    QPushButton#smartReviewDashboardButton,
    QPushButton#adaptiveDashboardButton,
    QPushButton#mockExamDashboardButton,
    QPushButton#syllabusAlertButton,
    QPushButton#syllabusForecastButton,
    QPushButton#effectivenessOpenButton,
    QPushButton#syllabusOpenButton {
        min-height: 32px;
        padding: 5px 10px;
        border-radius: 7px;
        font-size: 8.5pt;
        font-weight: 600;
    }

    QPushButton#studyManualButton,
    QPushButton#smartReviewDashboardButton,
    QPushButton#syllabusAlertButton,
    QPushButton#syllabusForecastButton,
    QPushButton#effectivenessOpenButton,
    QPushButton#syllabusOpenButton {
        background-color: #396eaa;
        border: 1px solid #477fb8;
        color: #ffffff;
    }

    QPushButton#adaptiveDashboardButton {
        background-color: #555b9f;
        border: 1px solid #696fb2;
        color: #ffffff;
    }

    QPushButton#mockExamDashboardButton {
        background-color: #9e7436;
        border: 1px solid #b28949;
        color: #ffffff;
    }

    QFrame#studyActionCard,
    QFrame#strategyCompactCard {
        border-radius: 9px;
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(12,31,47,235),
            stop:1 rgba(9,22,36,235)
        );
        border-color: #2c5069;
    }

    QFrame#strategyCompactCard[actionRole="adaptive"] {
        border-color: #454965;
    }

    QFrame#strategyCompactCard[actionRole="simulation"] {
        border-color: #5c5038;
    }

    QFrame#assessmentStat {
        border-radius: 6px;
        background-color: rgba(8,24,38,220);
        border-color: #29475c;
    }

    QLabel#assessmentStatLabel {
        color: #7392a6;
        font-size: 6.8pt;
    }

    QLabel#assessmentStatValue {
        color: #a8c7d7;
        font-size: 9pt;
        font-weight: 700;
    }




    /* Setas compactas — Visão geral / Notificações */

    QPushButton#dashboardGroupToggle {
        background: transparent;
        color: #84a8bc;
        border: none;
        text-align: left;
        padding: 3px 5px;
        font-size: 8.8pt;
        font-weight: 600;
    }

    QPushButton#dashboardGroupToggle:hover {
        background-color: rgba(18,46,66,180);
        color: #a8d9eb;
        border-radius: 6px;
    }

    QPushButton#dashboardGroupToggle[expanded="false"] {
        color: #708fa2;
    }




    /* Status do dia + Desempenho refinados */

    QLabel#dashboardStatusTotal {
        color: #d9edf6;
        font-size: 17pt;
        font-weight: 700;
    }

    QLabel#dashboardStatusSubtitle {
        color: #7f9db0;
        font-size: 8.3pt;
    }

    QFrame#dashboardStatusLine {
        background: transparent;
        border: none;
    }

    QLabel#dashboardStatusDot {
        font-size: 7.5pt;
    }

    QFrame#dashboardStatusLine[statusRole="today"] QLabel#dashboardStatusDot {
        color: #68cba1;
    }

    QFrame#dashboardStatusLine[statusRole="late"] QLabel#dashboardStatusDot {
        color: #caa158;
    }

    QLabel#dashboardStatusLineLabel {
        color: #8ca6b7;
        font-size: 8.5pt;
        font-weight: 500;
    }

    QLabel#dashboardStatusLineValue {
        color: #d3e7f0;
        font-size: 9.5pt;
        font-weight: 700;
    }

    QLabel#dashboardStatusContext {
        background-color: rgba(13,33,49,220);
        color: #89a6b7;
        border: 1px solid #2b5068;
        border-radius: 7px;
        padding: 3px 7px;
        font-size: 7.6pt;
        font-weight: 600;
    }

    QLabel#dashboardStatusContext[statusRole="ok"] {
        background-color: rgba(17,52,41,220);
        color: #8bd2ac;
        border-color: #2e7056;
    }

    QLabel#dashboardStatusContext[statusRole="attention"] {
        background-color: rgba(56,43,22,220);
        color: #cfad70;
        border-color: #725b32;
    }

    QLabel#dashboardPerformanceCaption {
        color: #7e9aab;
        font-size: 7.8pt;
        font-weight: 500;
    }

    QLabel#dashboardTrendLabel {
        color: #7895a7;
        font-size: 7.5pt;
    }

    QLabel#dashboardTrendValue {
        color: #8da8b8;
        font-size: 7.7pt;
        font-weight: 600;
    }

    QLabel#dashboardTrendValue[trendRole="positive"] {
        color: #73caa2;
    }

    QLabel#dashboardTrendValue[trendRole="negative"] {
        color: #d68787;
    }

    QLabel#dashboardTrendValue[trendRole="stable"] {
        color: #8da8b8;
    }




    /* ======================================================
       VISÃO GERAL HARMÔNICA — FUTURISTA
       ====================================================== */

    QFrame#dashboardOverviewCard {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #0d2032,
            stop:1 #091725
        );
        border: 1px solid #2d5670;
        border-radius: 11px;
    }

    QLabel#dashboardOverviewTitle {
        color: #d8ebf4;
        font-size: 10.5pt;
        font-weight: 700;
    }

    QLabel#dashboardOverviewInfo {
        color: #65879c;
        font-size: 8.5pt;
        font-weight: 600;
    }

    QLabel#dashboardRhythmMainValue {
        color: #deeff7;
        font-size: 18pt;
        font-weight: 700;
    }

    QLabel#dashboardRhythmCaption {
        color: #7e9bad;
        font-size: 8pt;
    }

    QFrame#dashboardRhythmMetric {
        background-color: rgba(12,31,47,220);
        border: 1px solid #294b61;
        border-radius: 8px;
    }

    QFrame#dashboardRhythmMetric[metricRole="today"] {
        border-color: #316657;
    }

    QFrame#dashboardRhythmMetric[metricRole="late"] {
        border-color: #665331;
    }

    QLabel#dashboardRhythmMetricValue {
        color: #d7e8ef;
        font-size: 11pt;
        font-weight: 700;
    }

    QFrame#dashboardRhythmMetric[metricRole="today"] QLabel#dashboardRhythmMetricValue {
        color: #83c8a4;
    }

    QFrame#dashboardRhythmMetric[metricRole="late"] QLabel#dashboardRhythmMetricValue {
        color: #c9a564;
    }

    QLabel#dashboardRhythmMetricLabel {
        color: #7d98aa;
        font-size: 7.5pt;
    }

    QLabel#dashboardRhythmStatus {
        background: transparent;
        border: none;
        color: #819daf;
        font-size: 7.7pt;
        font-weight: 600;
    }

    QLabel#dashboardRhythmStatus[statusRole="ok"] {
        color: #76bd98;
    }

    QLabel#dashboardRhythmStatus[statusRole="attention"] {
        color: #c7a15e;
    }

    QLabel#dashboardQualityCaption {
        color: #7895a7;
        font-size: 7.7pt;
        font-weight: 500;
    }

    QFrame#dashboardOverviewDivider {
        background-color: #284a60;
        border: none;
    }

    QLabel#dashboardQualityTrendLabel {
        color: #7591a3;
        font-size: 7.5pt;
    }

    QLabel#dashboardQualityTrendValue {
        color: #88a4b5;
        font-size: 7.7pt;
        font-weight: 600;
    }

    QLabel#dashboardQualityTrendValue[trendRole="positive"] {
        color: #72bf98;
    }

    QLabel#dashboardQualityTrendValue[trendRole="negative"] {
        color: #cb8181;
    }

    QPushButton#dashboardProjectionTitleButton {
        background: transparent;
        color: #d8ebf4;
        border: none;
        text-align: left;
        padding: 0px;
        font-size: 10.5pt;
        font-weight: 700;
    }

    QLabel#dashboardProjectionContestLabel {
        color: #819dae;
        font-size: 8pt;
        font-weight: 600;
    }

    QLabel#dashboardProjectionCaption {
        color: #7895a7;
        font-size: 7.7pt;
    }

    QLabel#dashboardProjectionDetail {
        color: #abc1cd;
        font-size: 8.3pt;
        font-weight: 600;
    }

    QLabel#dashboardProjectionPercent {
        color: #deeff7;
        font-size: 16pt;
        font-weight: 700;
    }

    QProgressBar#dashboardProjectionBar {
        background-color: #1a3041;
        border: 1px solid #294b60;
        border-radius: 6px;
    }

    QProgressBar#dashboardProjectionBar::chunk {
        background-color: #3bbeb8;
        border-radius: 6px;
    }

    QFrame#dashboardProjectionMetric {
        background-color: rgba(12,31,47,220);
        border: 1px solid #294b61;
        border-radius: 7px;
    }

    QLabel#dashboardProjectionMetricLabel {
        color: #7895a8;
        font-size: 7.4pt;
    }

    QLabel#dashboardProjectionMetricValue {
        color: #d3e5ed;
        font-size: 8.7pt;
        font-weight: 700;
    }

    QFrame#dashboardProjectionMetric[metricRole="consolidating"] QLabel#dashboardProjectionMetricValue {
        color: #9f91c8;
    }

    QFrame#dashboardProjectionMetric[metricRole="consolidated"] QLabel#dashboardProjectionMetricValue {
        color: #76be96;
    }

    QFrame#dashboardProjectionMetric[metricRole="domain"] QLabel#dashboardProjectionMetricValue {
        color: #82afc8;
    }




    /* Ritmo + Qualidade V2 — Futurista */

    QFrame#dashboardOverviewVerticalDivider {
        background-color: #28485d;
        border: none;
    }

    QLabel#dashboardRhythmMainValue {
        color: #ddecf4;
        font-size: 19pt;
        font-weight: 700;
    }

    QLabel#dashboardRhythmCaption {
        color: #7e9aac;
        font-size: 8pt;
    }

    QFrame#dashboardRhythmLine {
        background: transparent;
        border: none;
    }

    QLabel#dashboardRhythmDot {
        font-size: 7pt;
    }

    QFrame#dashboardRhythmLine[metricRole="today"] QLabel#dashboardRhythmDot {
        color: #6bc39a;
    }

    QFrame#dashboardRhythmLine[metricRole="late"] QLabel#dashboardRhythmDot {
        color: #c9a15a;
    }

    QLabel#dashboardRhythmLineLabel {
        color: #839faf;
        font-size: 8.4pt;
        font-weight: 500;
    }

    QLabel#dashboardRhythmLineValue {
        color: #d3e4ec;
        font-size: 11pt;
        font-weight: 700;
    }

    QFrame#dashboardRhythmLine[metricRole="today"] QLabel#dashboardRhythmLineValue {
        color: #7ec7a0;
    }

    QFrame#dashboardRhythmLine[metricRole="late"] QLabel#dashboardRhythmLineValue {
        color: #caa461;
    }

    QLabel#dashboardRhythmStatus {
        color: #819cac;
        background: transparent;
        border: none;
        padding: 1px 0px;
        font-size: 7.7pt;
        font-weight: 600;
    }

    QLabel#dashboardRhythmStatus[statusRole="ok"] {
        color: #78bd98;
    }

    QLabel#dashboardRhythmStatus[statusRole="attention"] {
        color: #c5a05f;
    }

    QLabel#dashboardQualityEyebrow {
        color: #718da0;
        font-size: 6.9pt;
        font-weight: 600;
    }

    QLabel#dashboardQualityCaption {
        color: #c0d4df;
        font-size: 9.2pt;
        font-weight: 600;
    }

    QFrame#dashboardQualityTrendBox {
        background-color: rgba(9,29,44,220);
        border: 1px solid #29495e;
        border-radius: 7px;
    }

    QLabel#dashboardQualityTrendValue {
        color: #9eb8c7;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#dashboardQualityTrendValue[trendRole="positive"] {
        color: #75c29a;
    }

    QLabel#dashboardQualityTrendValue[trendRole="negative"] {
        color: #ce8080;
    }

    QLabel#dashboardQualityTrendValue[trendRole="stable"] {
        color: #9aafbd;
    }

    QLabel#dashboardQualityTrendLabel {
        color: #6f8b9c;
        font-size: 6.9pt;
    }

    QLabel#dashboardQualityFooter {
        color: #5f7c8e;
        font-size: 6.8pt;
    }




    /* ======================================================
       PLANEJAMENTO REORGANIZADO V1 — FUTURISTA
       ====================================================== */

    QFrame#planningPanel {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #0d2032,
            stop:1 #091725
        );
        border: 1px solid #2d5670;
        border-radius: 11px;
    }

    QLabel#planningSectionSubtitle {
        color: #7997aa;
        font-size: 8pt;
    }

    QLabel#planningSubsectionTitle {
        color: #c6dce7;
        font-size: 9pt;
        font-weight: 700;
    }

    QLabel#planningSubsectionHint,
    QLabel#planningMicroLabel {
        color: #6f8ca0;
        font-size: 7.4pt;
    }

    QFrame#dailyGoalBox,
    QFrame#weeklyLoadBox,
    QFrame#weeklyGoalBox {
        background-color: rgba(11,30,46,225);
        border: 1px solid #294b61;
        border-radius: 9px;
    }

    QLabel#planningItemTitle,
    QLabel#weeklyGoalTitle {
        color: #bfd5df;
        font-size: 8.7pt;
        font-weight: 700;
    }

    QLabel#dailyGoalValue {
        color: #dcecf3;
        font-size: 13pt;
        font-weight: 700;
    }

    QLabel#planningTotalBadge {
        background-color: rgba(10,27,42,220);
        color: #83a0b2;
        border: 1px solid #2d536a;
        border-radius: 6px;
        padding: 3px 7px;
        font-size: 7.3pt;
        font-weight: 600;
    }

    QProgressBar#dailyGoalProgress {
        background-color: #1c3343;
        border: none;
        border-radius: 4px;
    }

    QProgressBar#dailyGoalProgress::chunk {
        background-color: #3b78b1;
        border-radius: 4px;
    }

    QLabel#planningHint {
        color: #7895a8;
        font-size: 7.4pt;
    }

    QFrame#weekDayLoad {
        background-color: rgba(8,25,39,220);
        border: 1px solid #29495e;
        border-radius: 8px;
        min-height: 62px;
    }

    QFrame#weekDayLoad[today="true"] {
        background-color: rgba(19,43,67,225);
        border-color: #4677a5;
    }

    QFrame#weekDayLoad[loadLevel="leve"][today="false"] {
        border-color: #315544;
    }

    QFrame#weekDayLoad[loadLevel="moderada"][today="false"] {
        border-color: #625336;
    }

    QFrame#weekDayLoad[loadLevel="alta"][today="false"] {
        border-color: #6b3f3f;
    }

    QLabel#weekDayName {
        color: #819eaf;
        font-size: 7.5pt;
        font-weight: 600;
    }

    QLabel#weekDayDate {
        color: #5e7c90;
        font-size: 6.8pt;
    }

    QLabel#weekDayCount {
        color: #d4e6ee;
        font-size: 10pt;
        font-weight: 700;
    }

    QFrame#weekDayLoad[today="true"] QLabel#weekDayName,
    QFrame#weekDayLoad[today="true"] QLabel#weekDayCount {
        color: #9fc9e3;
    }

    QPushButton#planningGoalButton,
    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton,
    QPushButton#weeklyGoalSetupButton {
        min-height: 30px;
        padding: 4px 10px;
        border-radius: 7px;
        font-size: 8pt;
        font-weight: 600;
    }

    QPushButton#planningGoalButton {
        background-color: #396eaa;
        color: #ffffff;
        border: 1px solid #477fb8;
    }

    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton,
    QPushButton#weeklyGoalSetupButton {
        background-color: rgba(12,31,47,225);
        color: #aac2d0;
        border: 1px solid #31566e;
    }

    QPushButton#planningRedistributeButton[hasSuggestion="true"] {
        background-color: rgba(58,45,23,225);
        color: #caaa6e;
        border-color: #735e34;
    }

    QFrame#weeklyGoalEmptyState {
        background-color: rgba(8,25,39,220);
        border: 1px dashed #30536a;
        border-radius: 8px;
    }

    QLabel#weeklyGoalEmptyTitle {
        color: #b7ced9;
        font-size: 8.3pt;
        font-weight: 600;
    }

    QLabel#weeklyGoalEmptyDescription {
        color: #7794a6;
        font-size: 7.4pt;
    }

    QLabel#weeklyGoalPeriod {
        color: #7794a7;
        font-size: 7.4pt;
    }

    QFrame#weeklyGoalMetric {
        background-color: rgba(8,25,39,220);
        border: 1px solid #29495e;
        border-radius: 7px;
    }

    QLabel#weeklyGoalMetricTitle {
        color: #7794a8;
        font-size: 7.3pt;
        font-weight: 600;
    }

    QLabel#weeklyGoalValue {
        color: #d2e4ec;
        font-size: 9.5pt;
        font-weight: 700;
    }

    QLabel#weeklyGoalHint {
        color: #6e8a9d;
        font-size: 7pt;
    }




    /* Ação única do Planejamento */
    QPushButton#planningGoalButton {
        min-height: 34px;
        padding: 5px 14px;
        background-color: #396eaa;
        color: #ffffff;
        border: 1px solid #477fb8;
        border-radius: 8px;
        font-size: 8.5pt;
        font-weight: 700;
    }

    QPushButton#planningGoalButton:hover {
        background-color: #315f91;
        border-color: #416f9e;
    }




    /* Correção de contraste no hover — Planejamento */
    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton {
        background-color: rgba(12,31,47,225);
        color: #aac2d0;
        border: 1px solid #31566e;
        border-radius: 8px;
        font-weight: 600;
    }

    QPushButton#planningSummaryButton:hover,
    QPushButton#planningRedistributeButton:hover {
        background-color: rgba(20,48,69,235);
        color: #d9f0fa;
        border: 1px solid #477a98;
    }

    QPushButton#planningSummaryButton:pressed,
    QPushButton#planningRedistributeButton:pressed {
        background-color: rgba(27,60,83,240);
        color: #ffffff;
        border-color: #5790ad;
    }

    QPushButton#planningRedistributeButton[hasSuggestion="true"] {
        background-color: rgba(58,45,23,225);
        color: #caaa6e;
        border-color: #735e34;
    }

    QPushButton#planningRedistributeButton[hasSuggestion="true"]:hover {
        background-color: rgba(72,56,27,235);
        color: #ebcc8d;
        border-color: #917749;
    }



    /* ======================================================
       NOTIFICAÇÕES — CORES HARMONIZADAS V1 / FUTURISTA
       ====================================================== */

    QFrame#dashboardNoticeRow[noticeRole="alert"] {
        background-color: rgba(49,39,21,225);
        border: 1px solid #735d32;
        border-radius: 9px;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"][alertState="ok"] {
        background-color: rgba(16,43,34,225);
        border-color: #32634f;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"][alertState="critico"] {
        background-color: rgba(51,26,27,225);
        border-color: #774646;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] QLabel#dashboardNoticeLabel {
        color: #c5a66d;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] QLabel#dashboardNoticeTitle {
        color: #e0c68d;
    }

    QFrame#dashboardNoticeRow[noticeRole="alert"] QLabel#dashboardNoticeIcon {
        background-color: rgba(58,44,20,225);
        color: #e2b85e;
        border: 1px solid #816936;
        border-radius: 15px;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] {
        background-color: rgba(10,32,50,230);
        border: 1px solid #315976;
        border-radius: 9px;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeLabel {
        color: #78a1bc;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeTitle {
        color: #9fc8df;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeDescription,
    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeSummary {
        color: #82a7bb;
    }

    QFrame#dashboardNoticeRow[noticeRole="forecast"] QLabel#dashboardNoticeIcon {
        background-color: rgba(13,44,64,225);
        color: #7cc6e8;
        border: 1px solid #3c7795;
        border-radius: 15px;
    }

    QPushButton#syllabusAlertButton {
        background-color: #8f6b31;
        color: #ffffff;
        border: 1px solid #a58243;
        border-radius: 8px;
        font-weight: 700;
    }

    QPushButton#syllabusAlertButton:hover {
        background-color: #a17937;
        color: #ffffff;
        border-color: #b58e4c;
    }

    QPushButton#syllabusForecastButton {
        background-color: #386f9e;
        color: #ffffff;
        border: 1px solid #4784b2;
        border-radius: 8px;
        font-weight: 700;
    }

    QPushButton#syllabusForecastButton:hover {
        background-color: #427cae;
        color: #ffffff;
        border-color: #5592c0;
    }




    /* Questões — ação principal do menu */

    QPushButton#questionsNavButton {
        min-height: 34px;
        min-width: 96px;
        padding: 5px 13px;
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #126f80,
            stop:1 #286e9c
        );
        color: #e9fdff;
        border: 1px solid #50cfe0;
        border-radius: 9px;
        font-size: 9pt;
        font-weight: 700;
    }

    QPushButton#questionsNavButton:hover {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #178598,
            stop:1 #347faf
        );
        color: #ffffff;
        border-color: #7fe4ef;
    }

    QPushButton#questionsNavButton:pressed {
        background-color: #155d74;
        color: #ffffff;
        border-color: #48adbd;
    }




    /* PALETA HARMONIZADA — BOTÕES (FUTURISTA) */

    QPushButton#toolbarButton,
    QPushButton#subtleButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #162b42,
            stop:1 #0d1d30);
        color: #e7f5ff;
        border: 1px solid #40688d;
        border-radius: 10px;
    }

    QPushButton#toolbarButton:hover,
    QPushButton#subtleButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #1a3854,
            stop:1 #10263d);
        color: #c8f6ff;
        border-color: #56dfff;
    }

    QPushButton#questionsNavButton,
    QPushButton#questionsImportButton,
    QPushButton#questionsPdfImportButton,
    QPushButton#questionsSolveButton,
    QPushButton#questionsSolveHeroButton,
    QPushButton#questionsNewHeroButton,
    QPushButton#questionsPromptsButton,
    QPushButton#questionsHistoryButton,
    QPushButton#questionsEffectivenessButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #126f80,
            stop:1 #286e9c);
        color: #ecfdff;
        border: 1px solid #59dbe9;
        border-radius: 10px;
        font-weight: 800;
    }

    QPushButton#questionsNavButton:hover,
    QPushButton#questionsImportButton:hover,
    QPushButton#questionsPdfImportButton:hover,
    QPushButton#questionsSolveButton:hover,
    QPushButton#questionsSolveHeroButton:hover,
    QPushButton#questionsNewHeroButton:hover,
    QPushButton#questionsPromptsButton:hover,
    QPushButton#questionsHistoryButton:hover,
    QPushButton#questionsEffectivenessButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #178598,
            stop:1 #347faf);
        border-color: #8beef6;
        color: #ffffff;
    }

    QPushButton#topAccentButton,
    QPushButton#primaryButton,
    QPushButton#syllabusOpenButton,
    QPushButton#planningGoalButton,
    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton,
    QPushButton#effectivenessOpenButton,
    QPushButton#smartReviewDashboardButton,
    QPushButton#rowActionButton,
    QPushButton#weeklyGoalSetupButton,
    QPushButton#questionSessionEndButton,
    QPushButton#studySessionEndButton,
    QPushButton#mockExamStartButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #355f9f,
            stop:1 #4c7ee0);
        color: #ffffff;
        border: 1px solid #7dadff;
        border-radius: 10px;
        font-weight: 800;
    }

    QPushButton#topAccentButton:hover,
    QPushButton#primaryButton:hover,
    QPushButton#syllabusOpenButton:hover,
    QPushButton#planningGoalButton:hover,
    QPushButton#planningSummaryButton:hover,
    QPushButton#planningRedistributeButton:hover,
    QPushButton#effectivenessOpenButton:hover,
    QPushButton#smartReviewDashboardButton:hover,
    QPushButton#rowActionButton:hover,
    QPushButton#weeklyGoalSetupButton:hover,
    QPushButton#questionSessionEndButton:hover,
    QPushButton#studySessionEndButton:hover,
    QPushButton#mockExamStartButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #2f558d,
            stop:1 #436dbe);
        border-color: #96bbff;
        color: #ffffff;
    }

    QPushButton#adaptiveDashboardButton,
    QPushButton#questionsAdaptiveButton,
    QPushButton#adaptiveSessionStartButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #1d6f67,
            stop:1 #2fa88f);
        color: #f0fffc;
        border: 1px solid #67d8bf;
        border-radius: 10px;
        font-weight: 800;
    }

    QPushButton#adaptiveDashboardButton:hover,
    QPushButton#questionsAdaptiveButton:hover,
    QPushButton#adaptiveSessionStartButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #24837a,
            stop:1 #38b89e);
        border-color: #89efd6;
        color: #ffffff;
    }

    QPushButton#syllabusAlertButton,
    QPushButton#mockExamDashboardButton,
    QPushButton#questionsMockExamButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #a36d1e,
            stop:1 #d09a35);
        color: #fffaf0;
        border: 1px solid #f5c86d;
        border-radius: 10px;
        font-weight: 800;
    }

    QPushButton#syllabusAlertButton:hover,
    QPushButton#mockExamDashboardButton:hover,
    QPushButton#questionsMockExamButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #8f5e18,
            stop:1 #b88329);
        border-color: #ffd98c;
        color: #ffffff;
    }

    QPushButton#syllabusForecastButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #142131,
            stop:1 #17314a);
        color: #a3d9ff;
        border: 1px solid #5f8dd8;
        border-radius: 10px;
        font-weight: 700;
    }

    QPushButton#syllabusForecastButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #19304a,
            stop:1 #1f3e5e);
        color: #e8f8ff;
        border-color: #85b8ff;
    }




    /* Integridade histórica — Questões */

    QLabel#questionsIntegrityBadge {
        background-color: rgba(12,31,47,225);
        color: #819fb2;
        border: 1px solid #2c5169;
        border-radius: 8px;
        padding: 4px 8px;
        font-size: 7.5pt;
        font-weight: 700;
    }

    QLabel#questionsIntegrityBadge[integrityState="ok"] {
        background-color: rgba(17,52,41,220);
        color: #7bc39d;
        border-color: #33725a;
    }

    QLabel#questionsIntegrityBadge[integrityState="legacy"] {
        background-color: rgba(12,40,58,225);
        color: #84bddb;
        border-color: #356986;
    }

    QLabel#questionsIntegrityBadge[integrityState="warning"] {
        background-color: rgba(57,44,23,225);
        color: #c9a664;
        border-color: #725c34;
    }




    /* Minha evolução V1 — Futurista */

    QFrame#myEvolutionFilterBar,
    QFrame#myEvolutionPanel,
    QFrame#myEvolutionStatCard {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #0d2032,
            stop:1 #091725
        );
        border: 1px solid #2d5670;
        border-radius: 10px;
    }

    QLabel#myEvolutionTitle,
    QLabel#myEvolutionSectionTitle {
        color: #d8ebf4;
        font-weight: 700;
    }

    QLabel#myEvolutionTitle { font-size: 11pt; }
    QLabel#myEvolutionSectionTitle { font-size: 9.5pt; }

    QLabel#myEvolutionStatLabel {
        color: #7794a7;
        font-size: 7.8pt;
        font-weight: 600;
    }

    QLabel#myEvolutionStatValue {
        color: #dcecf3;
        font-size: 15pt;
        font-weight: 700;
    }

    QLabel#myEvolutionStatDetail {
        color: #6f8ca0;
        font-size: 7.3pt;
    }

    QFrame#myEvolutionInsight {
        background-color: rgba(9,28,43,225);
        border: 1px solid #294b61;
        border-radius: 8px;
    }

    QFrame#myEvolutionInsight[insightRole="positive"] {
        border-color: #326553;
    }

    QFrame#myEvolutionInsight[insightRole="attention"] {
        border-color: #6a5835;
    }

    QFrame#myEvolutionInsight[insightRole="recovery"] {
        border-color: #315c78;
    }

    QLabel#myEvolutionInsightLabel {
        color: #7591a4;
        font-size: 7.2pt;
        font-weight: 600;
    }

    QLabel#myEvolutionInsightValue {
        color: #d3e5ed;
        font-size: 9.2pt;
        font-weight: 700;
    }

    QLabel#myEvolutionInsightDetail {
        color: #6f8c9f;
        font-size: 7.2pt;
    }




    /* Índice de Domínio V2 */

    QFrame#topicDomainComponent {
        background-color: rgba(10, 30, 46, 225);
        border: 1px solid #2d5269;
        border-radius: 8px;
    }

    QLabel#topicDomainStrengths {
        color: #8fd8b2;
        background-color: rgba(18, 55, 42, 220);
        border: 1px solid #36745a;
        border-radius: 7px;
        padding: 5px 8px;
        font-size: 8.1pt;
        font-weight: 600;
    }

    QLabel#topicDomainReasons {
        color: #d5b977;
        background-color: rgba(57, 43, 20, 220);
        border: 1px solid #755f34;
        border-radius: 7px;
        padding: 5px 8px;
        font-size: 8.1pt;
    }




    /* RELATÓRIOS ESTRATÉGICOS V1 — FUTURISTA */

    QFrame#strategicMetricCard,
    QFrame#strategicReportPanel {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #132b40,
            stop:1 #102237);
        border: 1px solid #315b76;
        border-radius: 11px;
    }

    QLabel#strategicReportTitle {
        color: #dff8ff;
    }

    QLabel#strategicMetricValue[prepState="good"] {
        color: #7fc7ff;
    }

    QLabel#strategicMetricValue[prepState="strong"] {
        color: #73e0c8;
    }

    QLabel#strategicMetricValue[prepState="attention"],
    QLabel#strategicMetricValue[prepState="building"] {
        color: #f1c874;
    }

    QFrame#strategicEvolutionItem {
        background-color: #11263a;
        border: 1px solid #2f5872;
    }

    QLabel#strategicActionItem {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #17334b,
            stop:1 #173b52);
        color: #b7e8ff;
        border: 1px solid #3f7797;
    }

    QLabel#strategicRiskItem[riskLevel="alto"] {
        background-color: #3b2723;
        color: #ffc1a9;
        border: 1px solid #7c5141;
    }

    QLabel#strategicRiskItem[riskLevel="medio"] {
        background-color: #39321f;
        color: #f2d48b;
        border: 1px solid #74623a;
    }

    QLabel#strategicRiskItem[riskLevel="baixo"] {
        background-color: #153832;
        color: #91edd6;
        border: 1px solid #367365;
    }




    /* Plano de Ação Automático V1 */
    QPushButton#planningAutoPlanButton,
    QPushButton#autoPlanAcceptButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #355f9f, stop:1 #4c7ee0);
        color: #ffffff;
        border: 1px solid #7dadff;
        border-radius: 10px;
        font-weight: 800;
    }
    QPushButton#planningAutoPlanButton:hover,
    QPushButton#autoPlanAcceptButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #2f558d, stop:1 #436dbe);
        border-color: #96bbff;
        color: #ffffff;
    }
    QPushButton#planningAutoPlanButton[hasPlan="true"] {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #126f80, stop:1 #286e9c);
        border-color: #59dbe9;
    }
    QPushButton#planningSummaryButton,
    QPushButton#planningRedistributeButton {
        background-color: #102033;
        color: #b3ddff;
        border: 1px solid #4777ba;
        border-radius: 10px;
        font-weight: 700;
    }
    QPushButton#planningSummaryButton:hover,
    QPushButton#planningRedistributeButton:hover {
        background-color: #17304a;
        color: #effbff;
        border-color: #6ba8e8;
    }
    QFrame#autoPlanStat {
        background-color: #102033;
        border: 1px solid #31516a;
        border-radius: 10px;
    }
    QLabel#autoPlanSavedNotice {
        background-color: #103539;
        color: #b8f5eb;
        border: 1px solid #3b8890;
        border-radius: 9px;
        padding: 7px 10px;
    }
    QLabel#autoPlanContext {
        color: #a8c1d2;
        background-color: #102033;
        border: 1px solid #31516a;
        border-radius: 9px;
        padding: 7px 10px;
    }




    /* PAUSA & DESAFIOS — FUTURISTA */

    QPushButton#pauseNavButton {
        min-height: 34px;
        padding: 5px 12px;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #143b43, stop:1 #17374f);
        color: #aaf7f2;
        border: 1px solid #4bc2c5;
        border-radius: 10px;
        font-size: 9pt;
        font-weight: 700;
    }

    QPushButton#pauseNavButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #19505a, stop:1 #1f4a67);
        color: #e2ffff;
        border-color: #72e4e5;
    }

    QFrame#pauseTimerPanel {
        background-color: #102b35;
        border: 1px solid #2f7180;
        border-radius: 11px;
    }

    QFrame#pauseRecordsPanel,
    QFrame#gameBoardPanel {
        background-color: #101f30;
        border: 1px solid #315d79;
        border-radius: 12px;
    }

    QFrame#pauseRecordCard {
        background-color: #13283a;
        border: 1px solid #315d79;
        border-radius: 9px;
    }

    QLabel#pauseHubTitle,
    QLabel#gameTitle,
    QLabel#pauseSectionTitle {
        color: #e1f7ff;
        font-weight: 800;
    }

    QLabel#pauseHubTitle { font-size: 17px; }
    QLabel#gameTitle { font-size: 13pt; }
    QLabel#pauseHubSubtitle,
    QLabel#gameHint,
    QLabel#pauseTimerStatus,
    QLabel#gameStatus { color: #8eafc3; }

    QLabel#pauseRecordValue,
    QLabel#gameMetric,
    QLabel#pauseTimerValue {
        color: #8de7e5;
        font-weight: 900;
    }

    QLabel#pauseTimerValue {
        min-width: 74px;
        padding: 4px 10px;
        background-color: #102033;
        border: 1px solid #49aeb9;
        border-radius: 8px;
        font-size: 12pt;
    }

    QPushButton#pausePrimaryButton,
    QPushButton#gamePrimaryButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #1d7476, stop:1 #307f91);
        color: #ffffff;
        border: 1px solid #62d6d5;
        border-radius: 10px;
        font-weight: 800;
    }

    QPushButton#pauseBackButton,
    QPushButton#pauseSecondaryButton {
        background-color: #102033;
        color: #b6d9ff;
        border: 1px solid #4f7eb7;
        border-radius: 10px;
        font-weight: 700;
    }

    QPushButton#chimpCellButton,
    QPushButton#memoryCardButton,
    QPushButton#sequenceCellButton,
    QPushButton#puzzleTileButton,
    QPushButton#rotationOptionButton {
        background-color: #14283b;
        color: #e5f5ff;
        border: 1px solid #386681;
        border-radius: 10px;
        font-size: 12pt;
        font-weight: 900;
    }

    QScrollArea#rotationScrollArea,
    QWidget#rotationScrollContent,
    QWidget#rotationOptionsContainer {
        background: transparent;
        border: none;
    }

    QPushButton#rotationOptionButton {
        min-height: 112px;
        padding: 0px;
    }

    QPushButton#chimpCellButton[cellState="number"],
    QPushButton#memoryCardButton[cardState="open"],
    QPushButton#puzzleTileButton[tileState="movable"] {
        background-color: #173b5c;
        color: #b7e3ff;
        border-color: #5aa9dc;
    }

    QPushButton#chimpCellButton[cellState="correct"],
    QPushButton#memoryCardButton[cardState="matched"] {
        background-color: #17413d;
        color: #aaf6e4;
        border-color: #53baa7;
    }

    QPushButton#sequenceCellButton[lit="true"] {
        background-color: #b17f2b;
        border-color: #f0c15d;
    }

    QPushButton#puzzleTileButton[tileState="blank"] {
        background-color: #0d1825;
        border-color: #203d52;
        color: transparent;
    }

    QPushButton#rotationOptionButton[answerState="correct"] {
        background-color: #17413d;
        border-color: #53baa7;
    }

    QPushButton#rotationOptionButton[answerState="wrong"] {
        background-color: #48212f;
        border-color: #c25978;
    }




    /* MODO FOCO — FUTURISTA */
    QPushButton#focusNavButton {
        min-height: 34px; padding: 5px 12px;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #17334e, stop:1 #244d73);
        color: #c5eaff; border: 1px solid #5799c9; border-radius: 10px; font-size: 9pt; font-weight: 800;
    }
    QPushButton#focusNavButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1d4363, stop:1 #2d6089);
        color: #f0fbff; border-color: #76c0e9;
    }
    QScrollArea#focusScrollArea { border: none; background: transparent; }
    QWidget#focusScrollContent { background: transparent; }
    QLabel#focusTitle, QLabel#focusSectionTitle, QLabel#focusContextLabel { color: #e1f7ff; font-weight: 800; }
    QLabel#focusTitle { font-size: 17px; }
    QLabel#focusSubtitle, QLabel#focusWindowHint, QLabel#focusStatLabel, QLabel#focusStatusLabel { color: #8eafc3; }
    QFrame#focusStatsPanel { background-color: #102638; border: 1px solid #315d79; border-radius: 11px; }
    QLabel#focusStatValue, QLabel#focusTimerValue { color: #8fd8ff; font-weight: 900; }
    QLabel#focusStatValue { font-size: 13pt; }
    QLabel#focusTimerValue { font-size: 32px; }
    QFrame#focusConfigPanel, QFrame#focusRecentPanel { background-color: #101f30; border: 1px solid #315d79; border-radius: 12px; }
    QFrame#focusActivePanel { background-color: #10283c; border: 1px solid #3f7599; border-radius: 12px; }
    QLabel#dashboardFocusSummary { color: #82abc5; font-size: 8.4pt; font-weight: 700; }
    QPushButton#focusPresetButton, QPushButton#focusSecondaryButton, QPushButton#focusPauseButton {
        background-color: #132b40; color: #bce7ff; border: 1px solid #3e7397; border-radius: 9px; font-weight: 700;
    }
    QPushButton#focusPresetButton:hover, QPushButton#focusSecondaryButton:hover, QPushButton#focusPauseButton:hover {
        background-color: #183850; color: #edfbff; border-color: #65b9df;
    }
    QPushButton#focusPrimaryButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #b51f31, stop:0.52 #d62b3d, stop:1 #f04458);
        color: #ffffff; border: 1px solid #ff7382; border-radius: 12px;
        font-weight: 900; font-size: 10.2pt; padding: 8px 22px;
    }
    QPushButton#focusPrimaryButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #ce293b, stop:0.52 #e83b4c, stop:1 #ff596b);
        border-color: #ffabb3;
    }
    QPushButton#focusPrimaryButton:pressed { background-color: #981827; border-color: #ff596b; }
    QPushButton#focusDangerButton { background-color: #402827; color: #ffd0c9; border: 1px solid #8d554d; border-radius: 9px; font-weight: 700; }

    QFrame#postFocusHero { background-color: #10283c; border: 1px solid #3f7599; border-radius: 12px; }
    QFrame#postFocusContentCard { background-color: #101f30; border: 1px solid #315d79; border-radius: 10px; }
    QFrame#postFocusResultCard { background-color: #102c2b; border: 1px solid #34756d; border-radius: 10px; }
    QLabel#postFocusResultValue { color: #8de2c2; font-size: 13pt; font-weight: 900; }
    QPushButton#postFocusContinue { background-color: #173b55; color: #d9f4ff; border: 1px solid #4f8fb7; border-radius: 10px; font-weight: 900; padding: 7px 14px; }
    QPushButton#postFocusContinue:hover { background-color: #1d4967; border-color: #70b7df; }
    QLabel#postFocusEyebrow { color: #82abc5; font-size: 8.3pt; font-weight: 800; }
    QLabel#postFocusTime { color: #bce7ff; font-size: 25px; font-weight: 900; }
    QLabel#postFocusStatus, QLabel#postFocusDetail, QLabel#postFocusNote { color: #82abc5; }
    QLabel#postFocusContentTitle, QLabel#postFocusQuestion { color: #eaf8ff; font-weight: 800; }
    QLabel#postFocusQuestion { font-size: 10.5pt; font-weight: 900; }
    QPushButton#postFocusPrimary { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #355f9f, stop:1 #4c7ee0); color: #ffffff; border: 1px solid #7dadff; border-radius: 10px; font-weight: 900; padding: 7px 14px; }
    QPushButton#postFocusPrimary:hover { border-color: #b9d7ff; }
    QPushButton#postFocusSecondary { background-color: #132b40; color: #bce7ff; border: 1px solid #3e7397; border-radius: 9px; font-weight: 800; padding: 7px 14px; }
    QPushButton#postFocusSecondary:hover { background-color: #183850; border-color: #65b9df; }
    QPushButton#postFocusGhost { background: transparent; color: #82abc5; border: 1px solid #315d79; border-radius: 8px; font-weight: 700; padding: 6px 12px; }
    QPushButton#postFocusGhost:hover { background-color: #132b40; color: #d9f4ff; }
    QPushButton#postFocusSecondary:disabled { color: #55768b; background-color: #102231; border-color: #29495e; }
    QFrame#focusHeroPanel { background-color: #10283c; border: 1px solid #3f7599; border-radius: 14px; }
    QLabel#focusHeroEyebrow { color: #82abc5; font-size: 8.3pt; font-weight: 800; letter-spacing: 0.45px; }
    QLabel#focusHeroValue { color: #bce7ff; font-size: 24px; font-weight: 900; }
    QLabel#focusHeroStatus { color: #eaf8ff; font-size: 10pt; font-weight: 800; }
    QLabel#focusHeroNote, QLabel#focusConfigHint, QLabel#focusHistoryHint, QLabel#focusFieldLabel { color: #82abc5; }
    QFrame#focusHeroMiniCard { background-color: #132b40; border: 1px solid #3e7397; border-radius: 11px; }
    QLabel#focusHeroMiniLabel { color: #82abc5; font-size: 8.2pt; font-weight: 700; }
    QLabel#focusHeroMiniValue { color: #d9f4ff; font-size: 12pt; font-weight: 900; }
    QLabel#postFocusDialogTitle { color: #eaf8ff; font-size: 16px; font-weight: 900; }
    QLabel#postFocusDialogSubtitle { color: #82abc5; }
    QFrame#postFocusMiniCard { background-color: #132b40; border: 1px solid #3e7397; border-radius: 10px; }
    QLabel#postFocusMiniLabel { color: #82abc5; font-size: 8.2pt; font-weight: 800; }
    QLabel#postFocusMiniValue { color: #d9f4ff; font-size: 11.5pt; font-weight: 900; }
    QProgressBar#focusProgressBar { min-height: 8px; max-height: 8px; background-color: #173046; border: 1px solid #2e5c78; border-radius: 4px; }
    QProgressBar#focusProgressBar::chunk { background-color: #55a7d5; border-radius: 4px; }


    


    /* ======================================================
       HOJE OPERACIONAL — FUTURISTA
       ====================================================== */
    QFrame#dashboardTodayPanel {
        background-color: #0d1d2c; border: 1px solid #2f6282; border-radius: 13px;
    }
    QLabel#dashboardTodayTitle { color: #edfaff; font-size: 11.5pt; font-weight: 900; }
    QLabel#dashboardTodayDate {
        color: #bfeaff; background-color: #102a3d; border: 1px solid #387ba1;
        border-radius: 7px; padding: 3px 8px; font-size: 8.5pt; font-weight: 800;
    }
    QLabel#dashboardTodayStatus { color: #78a7c4; font-size: 8.7pt; font-weight: 700; }
    QFrame#dashboardTodayFocus { background-color: #102a3f; border: 1px solid #397aa3; border-radius: 11px; }
    QFrame#dashboardTodayMetric { background-color: #102233; border: 1px solid #315d79; border-radius: 11px; }
    QFrame#dashboardTodayMetric[metricRole="late"] { background-color: #342626; border-color: #80504b; }
    QFrame#dashboardTodayMetric[metricRole="today"] { background-color: #322a1d; border-color: #7b6537; }
    QFrame#dashboardTodayMetric[metricRole="ok"] { background-color: #142c29; border-color: #397267; }
    QFrame#dashboardTodayMetric[metricRole="active"] { background-color: #102a3f; border-color: #397aa3; }
    QFrame#dashboardTodayMetric[metricKind="review"] { background-color: #142e27; border-color: #3f7c61; }
    QLabel#dashboardTodayEyebrow { color: #79abc8; font-size: 7.9pt; font-weight: 900; }
    QLabel#dashboardTodayFocusValue { color: #a9ddff; font-size: 15pt; font-weight: 900; }
    QLabel#dashboardTodayMetricValue { color: #eefaff; font-size: 14pt; font-weight: 900; }
    QFrame#dashboardTodayMetric[metricRole="late"] QLabel#dashboardTodayMetricValue { color: #ffaca2; }
    QFrame#dashboardTodayMetric[metricRole="today"] QLabel#dashboardTodayMetricValue { color: #edc86f; }
    QFrame#dashboardTodayMetric[metricRole="ok"] QLabel#dashboardTodayMetricValue { color: #8ddbc6; }
    QFrame#dashboardTodayMetric[metricRole="active"] QLabel#dashboardTodayMetricValue { color: #a9ddff; }
    QFrame#dashboardTodayMetric[metricKind="review"] QLabel#dashboardTodayEyebrow { color: #9dd9b1; }
    QFrame#dashboardTodayMetric[metricKind="review"] QLabel#dashboardTodayMetricValue { color: #80dda2; }
    QLabel#dashboardTodayDetail { color: #8fb7ce; font-size: 8.2pt; }
    QFrame#dashboardQuickAccess { background-color: #10283c; border: 1px solid #3f7599; border-radius: 12px; }
    QLabel#dashboardQuickAccessTitle { color: #8fc4df; font-size: 8.6pt; font-weight: 900; }
    QProgressBar#dashboardTodayProgress {
        min-height: 7px; max-height: 7px; background-color: #18364c;
        border: 1px solid #2e5c78; border-radius: 3px;
    }
    QProgressBar#dashboardTodayProgress::chunk { background-color: #55a7d5; border-radius: 3px; }
    QFrame#dashboardTodayAction { background-color: #10283c; border: 1px solid #3f7599; border-radius: 11px; }
    QFrame#dashboardTodayAction[actionRole="late"] { background-color: #322b1e; border-color: #7a6334; }
    QFrame#dashboardTodayAction[actionRole="strategic"] { background-color: #202944; border-color: #566b9c; }
    QFrame#dashboardTodayAction[actionRole="active"] { background-color: #15302d; border-color: #3a746b; }
    QLabel#dashboardTodayActionTitle { color: #eefaff; font-size: 10.2pt; font-weight: 900; }
    QPushButton#dashboardTodayPrimaryButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #355f9f, stop:1 #4c7ee0);
        color: #ffffff; border: 1px solid #7dadff; border-radius: 10px;
        font-weight: 900; font-size: 9.5pt; padding: 7px 17px;
    }
    QPushButton#dashboardTodayPrimaryButton:hover { border-color: #c7e0ff; }
    QPushButton#dashboardTodayButton {
        background-color: #132b40; color: #bce7ff; border: 1px solid #3e7397; border-radius: 9px;
        font-weight: 800; padding: 6px 13px;
    }
    QPushButton#dashboardTodayButton:hover { background-color: #183850; color: #edfbff; border-color: #65b9df; }

    /* HERO CENTRAL — modo guiado */
    QFrame#dashboardTodayAction[heroCentral="true"] {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0d2234, stop:0.5 #12324a, stop:1 #0d2234);
        border: 2px solid #4b93bf; border-radius: 16px;
    }
    QFrame#dashboardTodayAction[heroCentral="true"][actionRole="late"] { background-color: #13283c; border-color: #4b88b8; }
    QFrame#dashboardTodayAction[heroCentral="true"][actionRole="strategic"] { background-color: #202b49; border-color: #687fbd; }
    QFrame#dashboardTodayAction[heroCentral="true"][actionRole="active"] { background-color: #15332f; border-color: #4a897c; }
    QLabel#dashboardGuidedHeroEyebrow { color: #8ee2ff; font-size: 8.4pt; font-weight: 900; letter-spacing: 1px; }
    QFrame#dashboardTodayAction[heroCentral="true"] QLabel#dashboardTodayActionTitle { color: #f2fcff; font-size: 12.8pt; font-weight: 800; }
    QLabel#dashboardGuidedHeroDetail { color: #b2d8eb; font-size: 9pt; font-weight: 700; }
    QLabel#dashboardGuidedHeroGuide { color: #8fbbd2; font-size: 8.6pt; }
    QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayPrimaryButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2d64c3, stop:1 #4b8cff);
        color: #ffffff; border: 1px solid #9cc7ff; border-radius: 12px;
        font-size: 11pt; font-weight: 900; padding: 10px 28px;
    }
    QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayPrimaryButton:hover { border-color: #e0f2ff; }
    QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayButton {
        background-color: transparent; border: none; color: #9edcff; text-decoration: underline; font-weight: 800; padding: 4px 10px;
    }
    QFrame#dashboardTodayAction[heroCentral="true"] QPushButton#dashboardTodayButton:hover { color: #effcff; }

    QLabel#studyScoreBreakdown { font-weight: 700; }

    /* ======================================================
       CENTRAL DE ATENÇÃO — NOTIFICAÇÕES ÚTEIS V2 / FUTURISTA
       ====================================================== */

    QFrame#dashboardAttentionCard {
        border-radius: 9px;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"] {
        background-color: rgba(49,39,21,225);
        border: 1px solid #735d32;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"][alertState="ok"] {
        background-color: rgba(16,43,34,225);
        border-color: #32634f;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"][alertState="critico"] {
        background-color: rgba(51,26,27,225);
        border-color: #774646;
    }

    QFrame#dashboardAttentionCard[attentionRole="pace"] {
        background-color: rgba(10,32,50,230);
        border: 1px solid #315976;
    }

    QLabel#dashboardAttentionIcon {
        font-size: 11pt;
        font-weight: 800;
        border-radius: 16px;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"] QLabel#dashboardAttentionIcon {
        background-color: rgba(58,44,20,225);
        color: #e2b85e;
        border: 1px solid #816936;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"][alertState="ok"] QLabel#dashboardAttentionIcon {
        background-color: rgba(22,62,45,225);
        color: #78d0a0;
        border-color: #3b7759;
    }

    QFrame#dashboardAttentionCard[attentionRole="priority"][alertState="critico"] QLabel#dashboardAttentionIcon {
        background-color: rgba(66,31,31,230);
        color: #ee8b83;
        border-color: #824947;
    }

    QFrame#dashboardAttentionCard[attentionRole="pace"] QLabel#dashboardAttentionIcon {
        background-color: rgba(13,44,64,225);
        color: #7cc6e8;
        border: 1px solid #3c7795;
    }

    QLabel#dashboardAttentionEyebrow {
        color: #7896aa;
        font-size: 7.5pt;
        font-weight: 700;
    }

    QLabel#dashboardAttentionTitle {
        color: #d5edf6;
        font-size: 9.5pt;
        font-weight: 700;
    }

    QLabel#dashboardAttentionDescription {
        color: #8eafbf;
        font-size: 8.5pt;
    }

    QLabel#dashboardAttentionMeta {
        color: #7f9dab;
        font-size: 8pt;
    }

    QLabel#dashboardAttentionBadge,
    QLabel#dashboardPaceBadge {
        padding: 3px 9px;
        border-radius: 8px;
        font-size: 7.5pt;
        font-weight: 700;
    }

    QLabel#dashboardAttentionBadge {
        background-color: rgba(58,44,20,225);
        color: #e3bd69;
        border: 1px solid #7a6336;
    }

    QFrame#dashboardAttentionCard[alertState="ok"] QLabel#dashboardAttentionBadge {
        background-color: rgba(21,57,42,230);
        color: #7dd0a1;
        border-color: #3c7457;
    }

    QFrame#dashboardAttentionCard[alertState="critico"] QLabel#dashboardAttentionBadge {
        background-color: rgba(66,31,31,230);
        color: #ee8b83;
        border-color: #824947;
    }

    QLabel#dashboardPaceBadge {
        background-color: rgba(13,44,64,225);
        color: #82c7e6;
        border: 1px solid #3a718d;
    }

    QFrame#dashboardAttentionFooter {
        background-color: rgba(11,26,38,220);
        border: 1px solid #294354;
        border-radius: 7px;
    }

    QLabel#dashboardAttentionFooterItem {
        color: #9eb9c7;
        font-size: 8pt;
        font-weight: 600;
    }

    QLabel#dashboardAttentionFooterHint {
        color: #657f8d;
        font-size: 7.5pt;
    }

""" + ESTILO_JORNADA_FUTURISTA + ESTILO_DASHBOARD_MODERNO_FUTURISTA + ESTILO_FOCO_DASHBOARD_FUTURISTA + ESTILO_ALGORITMO_DASHBOARD_FUTURISTA + ESTILO_BUSCA_GLOBAL_FUTURISTA + ESTILO_INTELIGENCIA_RESUMO_FUTURISTA + ESTILO_TOPICOS_DISCIPLINA_FUTURISTA + ESTILO_DASHBOARD_NEO_FUTURISTA + ESTILO_RESOLVEDOR_FUTURISTA + ESTILO_TOPICO_DETALHES_FUTURISTA + ESTILO_RESOLVEDOR_ELIMINADAS_FUTURISTA + ESTILO_RESOLVEDOR_TECLADO_FUTURISTA + ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_FUTURISTA + ESTILO_CALENDARIO_PREVISAO_FUTURISTA)

def aplicar_tema(
    app,
    tema
):
    tema = normalizar_tema(
        tema
    )

    app.setStyle(
        "Fusion"
    )

    if tema == "escuro":
        app.setStyleSheet(
            stylesheet_escuro()
        )
    elif tema == "futurista":
        app.setStyleSheet(
            stylesheet_futurista()
        )
    else:
        app.setStyleSheet(
            stylesheet_claro()
        )

    return tema
