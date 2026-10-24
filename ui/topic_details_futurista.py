"""Scoped Futurista visual contract for JanelaTopico."""

TOPIC_PREMIUM_QSS = r"""
/* VighnaStudy Topic Premium, Futurista identity; scoped to JanelaTopico only. */
QDialog#topicDetailsDialog {background:#071725;color:#DDF4FF;font-family:"Segoe UI";font-size:9pt;}
QDialog#topicDetailsDialog QWidget#topicOverviewContent,
QDialog#topicDetailsDialog QWidget#topicHistoryContent,
QDialog#topicDetailsDialog QScrollArea#topicOverviewScroll,
QDialog#topicDetailsDialog QScrollArea#topicHistoryScroll {background:transparent;border:0;}
QDialog#topicDetailsDialog QTabWidget#topicDetailsTabs::pane {border:0;background:transparent;}
QDialog#topicDetailsDialog QFrame#topicHeroCard {background:transparent;border:0;}
QDialog#topicDetailsDialog QLabel#topicBreadcrumb {color:#69A6BC;font-size:8pt;}
QDialog#topicDetailsDialog QLabel#topicHeroTitle {color:#F4FAFF;font-size:17pt;font-weight:800;}
QDialog#topicDetailsDialog QLabel#topicHeroSubtitle {color:#8FBDCE;font-size:8pt;}
QDialog#topicDetailsDialog QPushButton#topicQuestionsButton,
QDialog#topicDetailsDialog QPushButton#topicStudyButton {
 min-height:27px;border-radius:9px;padding:4px 14px;font-weight:800;
}
QDialog#topicDetailsDialog QPushButton#topicQuestionsButton {color:#C4E9FC;background:#0C273A;border:1px solid #245B78;}
QDialog#topicDetailsDialog QPushButton#topicQuestionsButton:hover {background:#143951;border-color:#39C5E7;}
QDialog#topicDetailsDialog QPushButton#topicStudyButton {color:white;border:1px solid #6966FF;background:#4B4FF0;}
QDialog#topicDetailsDialog QPushButton#topicStudyButton:hover {background:#6164FF;}
QDialog#topicDetailsDialog QFrame#topicSummaryCard {background:#0A2233;border:1px solid #087EA6;border-radius:13px;}
QDialog#topicDetailsDialog QFrame#topicSummaryHalf {background:transparent;border:0;}
QDialog#topicDetailsDialog QLabel#topicSummaryEyebrow {font-size:9pt;font-weight:800;color:#C3EBF7;}
QDialog#topicDetailsDialog QLabel#topicDomainScoreModern {color:#00C9EB;font-size:19pt;font-weight:900;}
QDialog#topicDetailsDialog QLabel#topicDomainLevelModern {background:transparent;color:#9FC5D7;font-size:8pt;padding:0;border:0;}
QDialog#topicDetailsDialog QProgressBar#topicDomainBarModern,
QDialog#topicDetailsDialog QProgressBar#topicDiagnosticBar {background:#1B394D;border:0;border-radius:3px;}
QDialog#topicDetailsDialog QProgressBar#topicDomainBarModern::chunk {background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #27A6FC,stop:1 #47D3C9);border-radius:3px;}
QDialog#topicDetailsDialog QProgressBar#topicDiagnosticBar::chunk {background:#16ACDB;border-radius:3px;}
QDialog#topicDetailsDialog QProgressBar#topicDiagnosticBar[metric="dominio_estabilidade"]::chunk {background:#E0B35B;}
QDialog#topicDetailsDialog QLabel#topicNextStatus {color:#FFB3B9;background:#552432;border:0;border-radius:7px;padding:3px 8px;font-weight:800;font-size:8pt;}
QDialog#topicDetailsDialog QLabel#topicNextStatus[scheduleState="today"] {color:#C5FFE9;background:#134A38;}
QDialog#topicDetailsDialog QLabel#topicNextStatus[scheduleState="future"],
QDialog#topicDetailsDialog QLabel#topicNextStatus[scheduleState="soon"] {color:#B5F1FF;background:#143C58;}
QDialog#topicDetailsDialog QLabel#topicNextStatus[scheduleState="none"] {color:#A3C8D6;background:#213A4B;}
QDialog#topicDetailsDialog QLabel#topicNextDate {color:#EDF9FF;font-size:13pt;font-weight:900;}
QDialog#topicDetailsDialog QLabel#topicNextDescription {color:#95BDD0;font-size:8.5pt;}
QDialog#topicDetailsDialog QPushButton#topicNextPrimaryButton {color:white;background:#5052F2;border:1px solid #6D72FF;border-radius:9px;font-weight:800;}
QDialog#topicDetailsDialog QPushButton#topicNextPrimaryButton:hover {background:#6268FF;}
QDialog#topicDetailsDialog QFrame#topicDomainCardModern,
QDialog#topicDetailsDialog QFrame#topicDiagnosticCard,
QDialog#topicDetailsDialog QFrame#topicEvidenceCard,
QDialog#topicDetailsDialog QFrame#topicHistoryCard,
QDialog#topicDetailsDialog QFrame#topicHistoryDetailsCard,
QDialog#topicDetailsDialog QFrame#topicEvolutionCard,
QDialog#topicDetailsDialog QFrame#topicHistorySummary {background:#0C2232;border:1px solid #1E536E;border-radius:12px;}
QDialog#topicDetailsDialog QLabel#topicDomainTitleModern,
QDialog#topicDetailsDialog QLabel#topicSectionTitle {color:#E2F7FE;font-size:10pt;font-weight:900;}
QDialog#topicDetailsDialog QLabel#topicDomainComponentLabelModern {color:#A1C7D6;font-size:8.5pt;}
QDialog#topicDetailsDialog QLabel#topicDomainComponentValueModern {color:#D9F4FF;font-size:9pt;font-weight:800;}
QDialog#topicDetailsDialog QLabel#topicDiagnosticPositive {color:#56DDC4;font-size:8pt;font-weight:800;}
QDialog#topicDetailsDialog QLabel#topicDiagnosticAttention {color:#F5BF6A;font-size:8pt;font-weight:800;}
QDialog#topicDetailsDialog QLabel#topicDomainInsightText {color:#B6D6E4;font-size:8.5pt;}
QDialog#topicDetailsDialog QFrame#topicDiagnosticDivider {background:#285069;border:0;}
QDialog#topicDetailsDialog QLabel#topicLastPractice {color:#A9DCFF;background:#123248;padding:7px 9px;border-radius:6px;font-size:8.6pt;}
QDialog#topicDetailsDialog QFrame#topicEvidenceMetric {background:#112E42;border:1px solid #163D53;border-radius:7px;}
QDialog#topicDetailsDialog QLabel#topicEvidenceValue {color:#E6F7FF;font-size:12pt;font-weight:900;}
QDialog#topicDetailsDialog QLabel#topicEvidenceCaption {color:#7EABC0;font-size:7.6pt;}
QDialog#topicDetailsDialog QPushButton#topicEvidenceLink {background:transparent;border:0;color:#6AE1EF;padding:4px 2px;font-size:8pt;font-weight:800;}
QDialog#topicDetailsDialog QPushButton#topicEvidenceLink:hover {color:white;text-decoration:underline;}
QDialog#topicDetailsDialog QLabel#topicLegacyNotice {color:#ECCB77;background:#383020;border:1px solid #66542C;border-radius:6px;padding:5px 8px;font-size:7.8pt;}
QDialog#topicDetailsDialog QLabel#topicHistoryStatValue {color:#E6F9FF;font-size:11pt;font-weight:800;}
QDialog#topicDetailsDialog QLabel#topicDomainEvidenceModern {color:#9CC4D4;font-size:8pt;}
QDialog#topicDetailsDialog QTableWidget#topicHistoryTable {background:#0B2639;alternate-background-color:#102E42;border:1px solid #1E526B;color:#CDEAFF;selection-background-color:#194F6C;selection-color:white;gridline-color:#204B63;}
QDialog#topicDetailsDialog QTableWidget#topicHistoryTable QHeaderView::section {background:#13394E;color:#C7EFFF;border:0;border-bottom:1px solid #27647E;padding:6px;}
QDialog#topicDetailsDialog QPushButton#topicHistoryButton,
QDialog#topicDetailsDialog QPushButton#dangerButton,
QDialog#topicDetailsDialog QPushButton#topicNextSecondaryButton,
QDialog#topicDetailsDialog QPushButton#topicNextGhostButton {color:#C7E9F5;background:#113247;border:1px solid #275B74;border-radius:7px;padding:5px 9px;}
QDialog#topicDetailsDialog QPushButton#dangerButton {color:#FFD6D7;border-color:#7B3942;}
QDialog#topicDetailsDialog QLabel#topicHistoryHint,
QDialog#topicDetailsDialog QLabel#topicEvolutionSummary {color:#92C3D4;font-size:8.5pt;}
"""
