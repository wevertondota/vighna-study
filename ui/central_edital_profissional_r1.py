"""Central do Edital: apresentação operacional dos indicadores acadêmicos existentes.

R1: não modifica consultas, banco, critérios de cobertura, alertas ou projeções.
O portal original permanece vivo e pode ser restaurado por rollback do atualizador.
"""
from __future__ import annotations

from collections import Counter

from PySide6.QtCore import QEvent, QObject, Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QScrollArea, QSizePolicy, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView,
)


def _label(text="", name="", wrap=False):
    obj = QLabel(text)
    if name:
        obj.setObjectName(name)
    obj.setWordWrap(wrap)
    return obj


def _button(text, callback, primary=False):
    button = QPushButton(text)
    button.setObjectName("ed2ButtonPrimary" if primary else "ed2ButtonSecondary")
    button.setCursor(Qt.PointingHandCursor)
    button.clicked.connect(callback)
    button.setMinimumHeight(34)
    return button


def _card():
    item = QFrame()
    item.setObjectName("ed2Card")
    item.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    return item


def _layout(frame, margins=(18, 16, 18, 16), spacing=11):
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    return layout


def _pct(value):
    return "—" if value is None else f"{float(value):.0f}%"


def _score(value):
    return "—" if value is None else f"{float(value):.0f}/100"


class CentralEditalProfissional(QObject):
    """Apresentador visual ligado às fontes acadêmicas originais do aplicativo."""

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.page = app.tela_portal_edital
        self._loading = False
        self._installed = False
        self._make_page()

    def _make_page(self):
        # Não altera a árvore Qt interna do portal original: ela permanece viva
        # para métricas, atualizadores, callbacks e posterior rollback.
        self._original_children = [
            c for c in self.page.children() if isinstance(c, QWidget)
        ]
        for child in self._original_children:
            child.hide()

        self.overlay = QScrollArea(self.page)
        self.overlay.setObjectName("ed2Scroll")
        self.overlay.setWidgetResizable(True)
        self.overlay.setFrameShape(QFrame.NoFrame)
        self.overlay.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.overlay.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.overlay.setGeometry(self.page.rect())
        self.overlay.raise_()

        root = QWidget()
        root.setObjectName("ed2Root")
        self.overlay.setWidget(root)
        self.outer = QVBoxLayout(root)
        self.outer.setContentsMargins(22, 20, 22, 26)
        self.outer.setSpacing(13)

        top = QHBoxLayout()
        top.setSpacing(12)
        name = QVBoxLayout()
        name.setSpacing(2)
        name.addWidget(_label("Meu Edital", "ed2Title"))
        name.addWidget(_label(
            "Cobertura, pendências e evolução do conteúdo programático",
            "ed2SubTitle", True,
        ))
        top.addLayout(name, 1)
        self.profile = _label("Perfil: —", "ed2Profile")
        top.addWidget(self.profile, 0, Qt.AlignVCenter)
        top.addWidget(_button("Atualizar", self.atualizar), 0, Qt.AlignVCenter)
        self.outer.addLayout(top)

        hero = _card()
        h = _layout(hero, (19, 15, 19, 16), 10)
        summary = QHBoxLayout()
        left = QVBoxLayout()
        left.setSpacing(4)
        left.addWidget(_label("Cobertura do edital", "ed2SectionTitle"))
        self.count = _label("— tópicos", "ed2Quiet")
        left.addWidget(self.count)
        summary.addLayout(left, 1)
        self.percent = _label("—", "ed2MajorNumber")
        summary.addWidget(self.percent, 0, Qt.AlignVCenter)
        h.addLayout(summary)
        self.progress = QProgressBar()
        self.progress.setObjectName("ed2Progress")
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 100)
        self.progress.setFixedHeight(9)
        h.addWidget(self.progress)

        kpis = QHBoxLayout()
        kpis.setSpacing(9)
        self.restantes = self._metric("Não iniciados", kpis)
        self.questions = self._metric("Questões cobertas", kpis)
        self.mastery = self._metric("Índice de domínio", kpis)
        h.addLayout(kpis)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(_button("Ver progresso detalhado", self.app.abrir_progresso_edital, True))
        h.addLayout(buttons)

        self.advanced_button = _button("Indicadores complementares  ▸", self._toggle_advanced)
        h.addWidget(self.advanced_button, 0, Qt.AlignLeft)
        self.advanced = QFrame()
        self.advanced.setObjectName("ed2Advanced")
        advanced_line = QHBoxLayout(self.advanced)
        advanced_line.setContentsMargins(12, 10, 12, 10)
        self.sufficient = _label("Evidência suficiente: —", "ed2Quiet")
        self.consolidated = _label("Tópicos consolidados: —", "ed2Quiet")
        advanced_line.addWidget(self.sufficient)
        advanced_line.addWidget(self.consolidated)
        advanced_line.addStretch()
        self.advanced.hide()
        h.addWidget(self.advanced)
        self.outer.addWidget(hero)

        alerts_header = QHBoxLayout()
        alerts_header.addWidget(_label("Pendências prioritárias", "ed2SectionTitle"))
        self.alert_count = _label("", "ed2Quiet")
        alerts_header.addStretch()
        alerts_header.addWidget(self.alert_count)
        self.outer.addLayout(alerts_header)

        self.alert_box = _card()
        self.alert_layout = _layout(self.alert_box, (12, 8, 12, 9), 2)
        self.outer.addWidget(self.alert_box)
        footer = QHBoxLayout()
        footer.addStretch()
        footer.addWidget(_button("Consultar todas as pendências", self.app.abrir_alertas_conteudo))
        self.outer.addLayout(footer)

        projection = _card()
        proj = _layout(projection, (18, 14, 18, 14), 7)
        proj_top = QHBoxLayout()
        proj_top.addWidget(_label("Projeção de cobertura", "ed2SectionTitle"))
        proj_top.addStretch()
        proj_top.addWidget(_label("ESTIMATIVA INTERNA", "ed2SmallTag"))
        proj.addLayout(proj_top)
        self.forecast = _label("—", "ed2Forecast")
        proj.addWidget(self.forecast)
        self.forecast_basis = _label("", "ed2Quiet", True)
        proj.addWidget(self.forecast_basis)
        proj.addWidget(_label(
            "Não representa data oficial de prova, edital ou garantia de conclusão.",
            "ed2Fine", True,
        ))
        self.outer.addWidget(projection)

        table_heading = QHBoxLayout()
        table_heading.addWidget(_label("Progresso por disciplina", "ed2SectionTitle"))
        table_heading.addStretch()
        table_heading.addWidget(_button("Abrir disciplinas", self.app.abrir_disciplinas_topicos_perfil))
        self.outer.addLayout(table_heading)
        table_card = _card()
        tc = _layout(table_card, (10, 10, 10, 10), 7)
        self.table = QTableWidget(0, 6)
        self.table.setObjectName("ed2Table")
        self.table.setHorizontalHeaderLabels([
            "Disciplina", "Tópicos", "Cobertura", "Domínio", "Alertas", "Ação"
        ])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().hide()
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, 6):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        self.table.setMinimumHeight(110)
        self.table.setMaximumHeight(350)
        self.table.cellDoubleClicked.connect(self._open_row)
        tc.addWidget(self.table)
        self.empty = _label("", "ed2Quiet", True)
        tc.addWidget(self.empty)
        self.outer.addWidget(table_card)

        # As ações originais de planejamento continuam disponíveis, porém
        # recolhidas para não disputar prioridade com a cobertura e as pendências.
        self.planning_button = _button("Planejamento e metas  ▸", self.mostrar_planejamento)
        self.outer.addWidget(self.planning_button, 0, Qt.AlignLeft)
        self.planning_frame = QFrame()
        self.planning_frame.setObjectName("ed2Planning")
        self.planning_layout = _layout(self.planning_frame, (0, 0, 0, 0), 0)
        old_planning = getattr(self.app, "dashboard_planejamento_painel", None)
        if old_planning is not None:
            original_parent = old_planning.parentWidget()
            if original_parent is not None and original_parent.layout() is not None:
                original_parent.layout().removeWidget(old_planning)
            old_planning.setParent(self.planning_frame)
            self.planning_layout.addWidget(old_planning)
            old_planning.setStyleSheet(self.app.dashboard_visual_root.styleSheet())
        self.planning_frame.hide()
        self.outer.addWidget(self.planning_frame)
        self.outer.addStretch()

        self.status = _label("", "ed2Fine", True)
        self.outer.addWidget(self.status)
        self.set_tema(getattr(self.app, "tema_atual", "futurista"))
        self.page.installEventFilter(self)
        self.overlay.show()
        self._installed = True
        QTimer.singleShot(0, self.atualizar)

    def _metric(self, title, host):
        panel = QFrame()
        panel.setObjectName("ed2Metric")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 9, 12, 9)
        layout.setSpacing(4)
        layout.addWidget(_label(title, "ed2MetricName"))
        number = _label("—", "ed2MetricNumber")
        layout.addWidget(number)
        host.addWidget(panel, 1)
        return number

    def mostrar_planejamento(self):
        visible = not self.planning_frame.isVisible()
        self.planning_frame.setVisible(visible)
        self.planning_button.setText(
            "Planejamento e metas  ▾" if visible else "Planejamento e metas  ▸"
        )
        if visible:
            QTimer.singleShot(0, lambda: self.overlay.ensureWidgetVisible(
                self.planning_frame, 0, 20
            ))

    def _toggle_advanced(self):
        open_ = not self.advanced.isVisible()
        self.advanced.setVisible(open_)
        self.advanced_button.setText(
            "Indicadores complementares  ▾" if open_
            else "Indicadores complementares  ▸"
        )

    def eventFilter(self, watched, event):
        if watched is self.page and event.type() in (QEvent.Resize, QEvent.Show):
            self.overlay.setGeometry(self.page.rect())
            self.overlay.raise_()
            if event.type() == QEvent.Show:
                QTimer.singleShot(0, self.atualizar)
        return False

    def set_tema(self, tema):
        light = str(tema or "").lower() == "claro"
        if light:
            bg, panel, inset, border = "#F3F7FB", "#FFFFFF", "#ECF4F9", "#CDDDE9"
            text, muted, accent = "#17334B", "#5E7486", "#087F9F"
            row_a, row_b = "#FFFFFF", "#F3F8FC"
        else:
            bg, panel, inset, border = "#071B2C", "#0E2739", "#102F43", "#2C5065"
            text, muted, accent = "#EAF4FA", "#9DB8C9", "#39C4DF"
            row_a, row_b = "#0B2233", "#102B3D"
        self.overlay.setStyleSheet(f"""
            QScrollArea#ed2Scroll, QWidget#ed2Root {{background: {bg}; border: none;}}
            QFrame#ed2Card {{background: {panel}; border:1px solid {border}; border-radius:12px;}}
            QLabel {{color:{text}; background:transparent;}}
            QLabel#ed2Title {{font-size:22px; font-weight:700;}}
            QLabel#ed2SubTitle, QLabel#ed2Quiet {{font-size:12px; color:{muted};}}
            QLabel#ed2Profile {{font-size:12px; font-weight:600; color:{text};
                background:{inset}; border:1px solid {border}; border-radius:8px;
                padding:8px 12px;}}
            QLabel#ed2SectionTitle {{font-size:15px; font-weight:700;}}
            QLabel#ed2MajorNumber {{font-size:31px; font-weight:700; color:{accent};}}
            QLabel#ed2Forecast {{font-size:19px; font-weight:650;}}
            QLabel#ed2SmallTag {{font-size:10px; color:{muted}; letter-spacing:0.3px;}}
            QLabel#ed2MetricName {{font-size:11px; color:{muted};}}
            QLabel#ed2MetricNumber {{font-size:20px; font-weight:700; color:{text};}}
            QLabel#ed2Fine {{font-size:11px; color:{muted};}}
            QFrame#ed2Metric, QFrame#ed2Advanced {{background:{inset}; border:1px solid {border}; border-radius:8px;}}
            QProgressBar#ed2Progress {{background:{inset}; border:none; border-radius:4px;}}
            QProgressBar#ed2Progress::chunk {{background:{accent}; border-radius:4px;}}
            QPushButton#ed2ButtonPrimary {{color:{text}; background:{inset}; border:1px solid {accent};
                border-radius:7px; padding:6px 12px; font-weight:600;}}
            QPushButton#ed2ButtonSecondary {{color:{text}; background:transparent; border:1px solid {border};
                border-radius:7px; padding:6px 12px;}}
            QPushButton#ed2ButtonPrimary:hover, QPushButton#ed2ButtonSecondary:hover {{border-color:{accent};}}
            QPushButton:focus {{border:2px solid {accent};}}
            QFrame#ed2Alert {{border:none; border-bottom:1px solid {border}; background:transparent;}}
            QLabel#ed2Critical {{color:#E59B96; font-size:11px; font-weight:700;}}
            QLabel#ed2Caution {{color:#DBB779; font-size:11px; font-weight:700;}}
            QLabel#ed2Neutral {{color:{muted}; font-size:11px; font-weight:600;}}
            QLabel#ed2AlertTitle {{font-size:12px; font-weight:600;}}
            QTableWidget#ed2Table {{background:{row_a}; alternate-background-color:{row_b};
                color:{text}; border:1px solid {border}; border-radius:7px;
                selection-background-color:{inset}; selection-color:{text}; font-size:12px;}}
            QTableWidget#ed2Table QHeaderView::section {{background:{inset};color:{text};
                border:none; border-bottom:1px solid {border}; padding:9px 8px; font-weight:600;}}
            QTableWidget#ed2Table QTableCornerButton::section {{background:{inset}; border:none;}}
            QScrollBar:vertical {{background:{bg}; width:10px;}}
            QScrollBar::handle:vertical {{background:{border}; border-radius:4px; min-height:30px;}}
        """)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _make_alert(self, alert):
        frame = QFrame()
        frame.setObjectName("ed2Alert")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 9, 10, 10)
        layout.setSpacing(4)
        severity = str(alert.get("nivel_alerta") or "Monitorar")
        tag = _label(severity, {
            "Crítico": "ed2Critical", "Atenção": "ed2Caution",
        }.get(severity, "ed2Neutral"))
        layout.addWidget(tag)
        title = str(alert.get("disciplina") or "Disciplina") + "  ·  " + str(alert.get("topico") or "Tópico")
        label = _label(title, "ed2AlertTitle", True)
        layout.addWidget(label)
        reason = str(alert.get("motivo_alerta") or "")
        if reason:
            layout.addWidget(_label(reason, "ed2Quiet", True))
        return frame

    def _open_row(self, row, _column=0):
        item = self.table.item(row, 0)
        if item is not None:
            self.app._abrir_detalhe_disciplina_edital_v2(item.text())

    def atualizar(self):
        if self._loading:
            return
        self._loading = True
        try:
            self.profile.setText("Perfil: " + (self.app.combo_concurso.currentText().strip() or "—"))
            # Usa as MESMAS fontes que alimentam o progresso e os alertas existentes.
            concurso_id = self.app._edital_id_perfil_ativo_v2()
            snapshot = self.app.montar_snapshot_progresso_edital(concurso_id)
            alerts = self.app.montar_alertas_conteudo(concurso_id)
            forecast = self.app.calcular_previsao_edital(concurso_id)

            total = int(snapshot.get("total_topics") or 0)
            started = int(snapshot.get("started_topics") or 0)
            coverage = snapshot.get("topic_coverage_rate")
            self.count.setText(f"{started} de {total} tópicos iniciados")
            self.percent.setText(_pct(coverage))
            self.progress.setValue(max(0, min(100, int(round(float(coverage or 0))))))
            self.restantes.setText(str(max(0, total - started)))
            self.questions.setText(_pct(snapshot.get("question_coverage_rate")))
            self.mastery.setText(_score(snapshot.get("global_mastery_score")))
            self.sufficient.setText("Evidência suficiente: " + _pct(snapshot.get("sufficient_evidence_rate")))
            self.consolidated.setText(f"Consolidados: {int(snapshot.get('consolidated_topics') or 0)}")

            critical = sum(1 for a in alerts if a.get("nivel_alerta") == "Crítico")
            self.alert_count.setText(
                f"{len(alerts)} alerta{'s' if len(alerts)!=1 else ''}"
                + (f" · {critical} crítico{'s' if critical!=1 else ''}" if critical else "")
            )
            self._clear_layout(self.alert_layout)
            if alerts:
                for a in alerts[:3]:
                    self.alert_layout.addWidget(self._make_alert(a))
            else:
                self.alert_layout.addWidget(_label("Nenhuma pendência prioritária identificada.", "ed2Quiet"))

            data_estimada = forecast.get("previsao_cobertura")
            if total == 0:
                self.forecast.setText("Sem conteúdo cadastrado")
                self.forecast_basis.setText("Cadastre os tópicos do perfil para habilitar projeções.")
            elif started >= total:
                self.forecast.setText("Cobertura dos tópicos iniciada")
                self.forecast_basis.setText("A consolidação é acompanhada separadamente da cobertura.")
            elif data_estimada is None or not data_estimada.get("data") or not data_estimada["data"].isValid():
                self.forecast.setText("Dados insuficientes para projetar a data")
                self.forecast_basis.setText(f"{max(0,total-started)} tópicos restantes. A estimativa exige ritmo histórico suficiente.")
            else:
                self.forecast.setText(data_estimada["data"].toString("dd/MM/yyyy"))
                rate = forecast.get("ritmo_inicio")
                self.forecast_basis.setText(
                    f"{max(0,total-started)} tópicos restantes · ritmo observado: {float(rate or 0):.1f} tópico(s)/semana"
                )

            disciplines = list(snapshot.get("disciplinas") or [])
            by_disc = Counter(str(a.get("disciplina") or "") for a in alerts)
            self.table.setUpdatesEnabled(False)
            self.table.setRowCount(len(disciplines))
            for row, record in enumerate(disciplines):
                disc = str(record.get("disciplina") or "—")
                vals = [
                    disc, str(int(record.get("total_topicos") or 0)),
                    _pct(record.get("cobertura_topicos")),
                    _score(record.get("dominio")), str(by_disc[disc]), "",
                ]
                for col, val in enumerate(vals):
                    if col == 5:
                        continue
                    cell = QTableWidgetItem(val)
                    if col:
                        cell.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, cell)
                btn = _button("Detalhes", lambda _checked=False, d=disc: self.app._abrir_detalhe_disciplina_edital_v2(d))
                self.table.setCellWidget(row, 5, btn)
                self.table.setRowHeight(row, 42)
            self.table.setUpdatesEnabled(True)
            # Tabela compacta: ocupa o necessário até o teto de altura; demais linhas possuem scroll.
            height = 42 + min(len(disciplines), 7) * 42 + 2
            self.table.setFixedHeight(max(90, min(340, height)))
            self.empty.setText("Nenhuma disciplina cadastrada." if not disciplines else "")
            self.status.setText("")
        except Exception as exc:
            self.table.setUpdatesEnabled(True)
            self.status.setText(
                "Não foi possível atualizar todos os indicadores desta visualização. "
                "Os dados acadêmicos não foram modificados. " + str(exc)[:160]
            )
        finally:
            self._loading = False


def instalar_central_edital_profissional(app):
    old = getattr(app, "_central_edital_profissional_r1", None)
    if old is not None:
        return old
    view = CentralEditalProfissional(app)
    app._central_edital_profissional_r1 = view
    return view
