"""Dashboard M2-D1C — proprietário único do posicionamento externo dos cards.

A geometria interna (labels, dados, botoes, QSS e algoritmo) nao e alterada.
O controlador e ativado exclusivamente para o Futurista; o legado pode ser
restaurado sem recriar ou desconectar os widgets. Os 382px do Hero sao
preservados por contrato ate validacao da arte em outras alturas.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, QEvent, QTimer, Qt
from PySide6.QtWidgets import QGridLayout, QSizePolicy, QWidget

from .dashboard_geometry_policy import CardMinimums, DashboardGeometryPolicy, Mode
from .dashboard_qt_layout_adapter import DashboardGridAdapter


CALIBRATED_MINIMUMS = CardMinimums(
    recommendation_w=390, recommendation_h=382,
    focus_w=287, focus_h=286,
    progress_w=274, progress_h=238,
    planning_w=454, planning_h=288,
)


class DashboardTwoRowsPolicy(DashboardGeometryPolicy):
    """M2-D1C usa duas faixas ao comportar a dupla; senão empilha.

    Adiar o antigo modo side-pair: medição Windows comprovou que a dupla
    Progresso/Planejamento nao cabe na coluna direita de 689/701 px.
    """
    def choose_mode(self, content_width: int) -> Mode:
        if content_width <= 0:
            raise ValueError("Largura do Dashboard invalida")
        return (Mode.HERO_FULLWIDTH_PAIR if self._can_fullwidth_pair(content_width)
                else Mode.SINGLE_COLUMN)


class DashboardQtLayoutController(QObject):
    """Um dono de geometria, usando layouts Qt e sem chamar setGeometry()."""
    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self.refs = owner._dashboard_modelo_refs
        self.viewport = owner.dashboard_scroll.viewport()
        self.root = self.refs['raiz']
        self.top = self.refs['topo']
        self.old_bottom = self.refs['inferior']
        self.right = owner._dashboard_hero_direita
        self.right_column = owner._dashboard_hero_coluna
        self.bottom_row = owner._dashboard_hero_bottom_row
        self.bottom_layout = owner._dashboard_hero_bottom_layout
        self.cards = {
            'recommendation': owner.dashboard_hoje_acao,
            'focus': self.refs['foco'],
            'progress': self.refs['progresso'],
            'planning': self.refs['planejamento_container'],
        }
        self.planning_card = owner.dashboard_resumo_ia
        self.policy = DashboardTwoRowsPolicy(CALIBRATED_MINIMUMS, gap=12)
        self.host = QWidget(owner.dashboard_hoje_conteudo)
        self.host.setObjectName('dashboardM2D1CGridHost')
        self.host.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.grid = QGridLayout(self.host)
        self.adapter = DashboardGridAdapter(self.grid, self.cards, gap=12, policy=self.policy)
        self.active = False
        self._queued = False
        self._last_width = None
        self._stored_sizes = None
        self.host.hide()
        self.viewport.installEventFilter(self)

    def eventFilter(self, watched, event):
        if watched is self.viewport and event.type() == QEvent.Type.Resize:
            self.request_update()
        return super().eventFilter(watched, event)

    @staticmethod
    def _bounds(widget):
        return (int(widget.minimumHeight()), int(widget.maximumHeight()),
                widget.sizePolicy())

    @staticmethod
    def _restore_bounds(widget, values):
        widget.setMinimumHeight(0)
        widget.setMaximumHeight(16777215)
        minimum, maximum, policy = values
        widget.setMinimumHeight(minimum)
        widget.setMaximumHeight(maximum)
        widget.setSizePolicy(policy)

    def _save_bounds(self):
        return {name:self._bounds(w) for name,w in (
            *self.cards.items(), ('planning_card', self.planning_card),
            ('right', self.right))}

    def activate(self):
        if self.active:
            self.request_update()
            return
        if not self.owner._dashboard_hero_reordenado:
            # A montadora legada deve criar o Hero antes da transferencia.
            return
        self._stored_sizes = self._save_bounds()
        # Retirar as instancias EXATAS de seus gerenciadores anteriores.
        self.top.removeWidget(self.cards['recommendation'])
        self.top.removeWidget(self.right)
        self.right_column.removeWidget(self.cards['focus'])
        self.bottom_layout.removeWidget(self.cards['progress'])
        self.bottom_layout.removeWidget(self.cards['planning'])
        # Os containers antigos ficam vazios e NAO consomem altura/colunas.
        self.right.hide()
        self.bottom_row.hide()
        self.right.setMinimumHeight(0)
        self.right.setMaximumHeight(16777215)
        # Redimensionar sem impor limites inferiores aos sizeHints reais.
        for name in ('focus','progress','planning'):
            w=self.cards[name]
            w.setMinimumHeight(0)
            w.setMaximumHeight(16777215)
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.planning_card.setMinimumHeight(0)
        self.planning_card.setMaximumHeight(16777215)
        self.planning_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # Protecao explicitamente contratada para a arte atual.
        hero=self.cards['recommendation']
        hero.setMinimumHeight(382)
        hero.setMaximumHeight(382)
        self.root.addWidget(self.host)
        self.host.show()
        self.active = True
        self._last_width = None
        self.request_update()

    def _content_width(self):
        margins=self.owner._dashboard_root_layout.contentsMargins()
        return max(1, self.viewport.width()-margins.left()-margins.right())

    def request_update(self):
        if not self.active or self._queued:
            return
        self._queued=True
        QTimer.singleShot(0, self._apply_when_ready)

    def _apply_when_ready(self):
        self._queued=False
        if not self.active:
            return
        width=self._content_width()
        if self._last_width==width:
            return
        self._last_width=width
        result=self.adapter.apply_width(width)
        for w in self.cards.values():
            self.grid.setAlignment(w, Qt.AlignmentFlag.AlignTop)
        # O row 0 ocupa somente a altura do Hero (382); row 1 adapta-se
        # ao Planejamento real, sem cortar o Progresso menor.
        self.grid.invalidate()
        self.host.updateGeometry()
        self.owner.dashboard_hoje_painel.updateGeometry()
        return result

    def deactivate(self):
        if not self.active:
            return
        self.active=False
        self._last_width=None
        while self.grid.count():
            self.grid.takeAt(0)
        # Limpar o cache de modo: na reativacao, a grade esta vazia e os
        # quatro widgets precisam ser inseridos novamente, mesmo se a
        # largura selecionar a mesma composicao anterior.
        self.adapter = DashboardGridAdapter(self.grid, self.cards, gap=12, policy=self.policy)
        self.root.removeWidget(self.host)
        self.host.hide()
        self.right.show()
        self.bottom_row.show()
        # Restaurar imediatamente a estrutura Hero original antes de
        # permitir que o caminho legado reverta para Claro/Escuro.
        self.right_column.insertWidget(0, self.cards['focus'])
        self.bottom_layout.addWidget(self.cards['progress'],1)
        self.bottom_layout.addWidget(self.cards['planning'],1)
        self.top.addWidget(self.cards['recommendation'],56)
        self.top.addWidget(self.right,44)
        self.top.setStretch(0,56)
        self.top.setStretch(1,44)
        for name, widget in (*self.cards.items(), ('planning_card', self.planning_card),
                             ('right',self.right)):
            self._restore_bounds(widget, self._stored_sizes[name])
        self.root.invalidate()
        self.top.invalidate()
        self.old_bottom.invalidate()
