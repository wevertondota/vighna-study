"""Dashboard M2-D1C — proprietário único do posicionamento externo dos cards.

A geometria interna (labels, dados, botoes, QSS e algoritmo) nao e alterada.
O controlador e ativado exclusivamente para o Futurista; o legado pode ser
restaurado sem recriar ou desconectar os widgets. A altura do Hero e especifica do card e permite um recorte proporcional da arte.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, QEvent, QTimer, Qt
from PySide6.QtWidgets import QGridLayout, QSizePolicy, QWidget, QVBoxLayout, QSpacerItem

from .dashboard_geometry_policy import CardMinimums, DashboardGeometryPolicy, Mode
from .dashboard_qt_layout_adapter import DashboardGridAdapter


CALIBRATED_MINIMUMS = CardMinimums(
    recommendation_w=390, recommendation_h=273,
    focus_w=430, focus_h=273,
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
        # R2: a linha vermelha indica a nova BORDA SUPERIOR (33 px abaixo).
        # Wrapper isolado com margem superior: o card reduz para 273 px,
        # preservando a borda inferior de 306 px e deixando o Foco intacto.
        self.recommendation_holder = QWidget(self.host)
        self.recommendation_holder.setObjectName('dashboardRecommendationOffsetHolder')
        self.recommendation_holder.setFixedHeight(306)
        self.recommendation_holder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.recommendation_holder_layout = QVBoxLayout(self.recommendation_holder)
        self.recommendation_holder_layout.setContentsMargins(0, 33, 0, 0)
        self.recommendation_holder_layout.setSpacing(0)
        # Alinhamento do Foco com a Recomendacao R2: mesma caixa total
        # de 306 px e mesmo deslocamento superior de 33 px.
        self.focus_holder = QWidget(self.host)
        self.focus_holder.setObjectName('dashboardFocusOffsetHolder')
        self.focus_holder.setFixedHeight(165)
        self.focus_holder.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.focus_holder_layout = QVBoxLayout(self.focus_holder)
        self.focus_holder_layout.setContentsMargins(0, 0, 0, 0)
        self.focus_holder_layout.setSpacing(0)
        self._grid_cards = dict(self.cards)
        self._grid_cards['recommendation'] = self.recommendation_holder
        self._grid_cards['focus'] = self.focus_holder
        self.adapter = DashboardGridAdapter(self.grid, self._grid_cards, gap=12, policy=self.policy)
        self.active = False
        self._queued = False
        self._last_width = None
        self._stored_sizes = None
        self._stored_focus_inner = None
        self._stored_focus_styles = None
        self._right_space = QSpacerItem(
            1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        # R2: a cor escura vinha dos QUATRO QWidget estruturais que usam
        # o fundo padrao de QWidget no tema Futurista (#07111e). O painel
        # externo QFrame ja era transparente: altera-lo sozinho nao resolve.
        self._surface_styles_before = None
        self.host.hide()
        self.viewport.installEventFilter(self)

    def _clear_structural_surfaces(self):
        """Mostra o cenário do Dashboard nas margens entre os dois cards.

        Preserva o QSS das próprias cartas, a arte, a borda ciano e os widgets
        funcionais. Aplica a correção somente enquanto a grade está ativa.
        """
        if self._surface_styles_before is not None:
            return
        wrappers = (
            self.owner.dashboard_hoje_conteudo,
            self.host,
            self.recommendation_holder,
            self.focus_holder,
        )
        self._surface_styles_before = tuple(
            (widget, widget.styleSheet()) for widget in wrappers
        )
        for widget, original in self._surface_styles_before:
            # O seletor exato, combinado ao estilo LOCAL do próprio widget,
            # vence a regra global `QWidget { background-color: #07111e; }`.
            # Não usar `QWidget { ... }` sem objectName: isso afetaria cards.
            nome = widget.objectName()
            widget.setStyleSheet(
                original + "\nQWidget#" + nome
                + " { background-color: transparent; border: none; }"
            )

    def _restore_structural_surfaces(self):
        """Restaura integralmente estilos anteriores ao sair do Futurista."""
        styles = self._surface_styles_before
        if styles is None:
            return
        for widget, original in styles:
            widget.setStyleSheet(original)
        self._surface_styles_before = None

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
        self._clear_structural_surfaces()
        self._stored_sizes = self._save_bounds()
        # Retirar as instancias EXATAS de seus gerenciadores anteriores.
        self.top.removeWidget(self.cards['recommendation'])
        self.recommendation_holder_layout.addWidget(
            self.cards['recommendation'], 0, Qt.AlignTop
        )
        self.recommendation_holder.show()
        self.top.removeWidget(self.right)
        self.right_column.removeWidget(self.cards['focus'])
        self.focus_holder_layout.addWidget(self.cards['focus'], 0, Qt.AlignTop)
        self.focus_holder.show()
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
        # Coluna esquerda da referência: recomendação 665x273,
        # Foco abaixo 665x165; coluna direita livre para o GIF dourado.
        # O mesmo card Foco e seus sinais são conservados.
        focus_card = self.cards['focus']
        focus_card.setMinimumHeight(165)
        focus_card.setMaximumHeight(165)
        metrics = focus_card.findChild(QWidget, 'focusDashboardMetricsRow')
        artwork = focus_card.findChild(QWidget, 'focusDashboardArtSlot')
        assert metrics is not None and artwork is not None, 'Componente Foco incompleto'
        focus_layout = self.owner._dashboard_foco_card_layout
        margins = focus_layout.contentsMargins()
        button = self.owner.dashboard_iniciar_foco
        self._stored_focus_inner = {
            'metrics_height': metrics.height(),
            'art_width': artwork.width(),
            'art_height': artwork.height(),
            'button_height': button.height(),
            'margins': (margins.left(), margins.top(), margins.right(), margins.bottom()),
            'spacing': focus_layout.spacing(),
        }
        # Compactar internamente sem ocultar meta, progresso, CTA ou
        # ampulheta. Mantem 160+ px reais e evita que sizeHint force scroll.
        metrics.setFixedHeight(54)
        artwork.setFixedSize(88, 84)
        focus_layout.setContentsMargins(12, 5, 12, 5)
        focus_layout.setSpacing(1)
        button.setFixedHeight(36)
        progress = self.owner.dashboard_hoje_foco_barra
        detail = self.owner.dashboard_hoje_foco_detalhe
        self._stored_focus_inner['progress_height'] = (progress.minimumHeight(), progress.maximumHeight())
        self._stored_focus_inner['detail_height'] = (detail.minimumHeight(), detail.maximumHeight())
        progress.setFixedHeight(9)
        detail.setFixedHeight(15)
        self._stored_focus_styles = []
        compact_styles = {
            'focusDashboardCardIcon': 'background: rgba(3, 35, 64, 0.7); border: 1px solid rgba(0, 212, 255, 0.85); border-radius: 16px; padding: 0px;',
            'dashboardTodayFocusValue': 'color: #00DEFF; font-size: 29px; font-weight: 800; background: transparent;',
            'focusDashboardCaption': 'color: #F0FAFF; font-size: 11px; background: transparent;',
            'focusDashboardGoalIcon': 'background: transparent; color: #00DEFF; font-size: 15px;',
            'focusDashboardGoalTitle': 'color: #E6F7FF; font-size: 12px; font-weight: 600; background: transparent;',
            'focusDashboardGoalValue': 'color: #FFFFFF; font-size: 13px; font-weight: 700; background: transparent;',
            'focusDashboardDetail': 'color: #EBF5FF; font-size: 11px; background: transparent; padding: 0px;',
            'dashboardFocusPrimaryButton': (
                'QPushButton#dashboardFocusPrimaryButton {'
                'background: qlineargradient(x1:0, y1:0, x2:1, y2:0,'
                'stop:0 rgba(17, 90, 148, 0.97), stop:1 rgba(27, 118, 174, 0.97));'
                'border: 1px solid rgba(0, 225, 255, 0.78); border-radius: 11px;'
                'color: #F6FBFF; font-size: 14px; font-weight: 700; padding: 3px 12px; }'
                'QPushButton#dashboardFocusPrimaryButton:focus { border: 2px solid #8BF4FF; }'
            ),
        }
        for name, style in compact_styles.items():
            widget = focus_card.findChild(QWidget, name)
            if widget is None:
                raise RuntimeError('Componente ausente para Foco compacto: ' + name)
            self._stored_focus_styles.append((widget, widget.styleSheet()))
            widget.setStyleSheet(style)
        icon = focus_card.findChild(QWidget, 'focusDashboardCardIcon')
        goal_icon = focus_card.findChild(QWidget, 'focusDashboardGoalIcon')
        self._stored_focus_inner['icon_size'] = icon.size()
        self._stored_focus_inner['goal_icon_size'] = goal_icon.size()
        self._stored_focus_inner['inner_layouts'] = []
        for widget_name in ('focusDashboardMetricsRow',
                            'focusDashboardTimeColumn', 'focusDashboardGoalColumn'):
            widget = focus_card.findChild(QWidget, widget_name)
            if widget is not None and widget.layout() is not None:
                layout = widget.layout()
                margins = layout.contentsMargins()
                self._stored_focus_inner['inner_layouts'].append((
                    layout, (margins.left(), margins.top(), margins.right(), margins.bottom()),
                    layout.spacing()))
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(2)
        icon.setFixedSize(32, 32)
        goal_icon.setFixedSize(22, 22)
        self.planning_card.setMinimumHeight(0)
        self.planning_card.setMaximumHeight(16777215)
        self.planning_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # R2: 273 px de card + 33 px de margem = 306 px de área total.
        # A parte de baixo permanece no mesmo alinhamento de R1.
        hero=self.cards['recommendation']
        hero.setMinimumHeight(273)
        hero.setMaximumHeight(273)
        self.root.addWidget(self.host)
        # A visao Futurista transfere o progresso para a barra superior.
        # O card inferior e preservado em memoria para reversao de tema.
        self.cards['progress'].hide()
        # Planejamento real segue atualizado em seu card preservado, mas
        # somente a faixa compacta aparece no Futurista.
        self.cards['planning'].hide()
        topo = self.owner.dashboard_quick_nav
        topo.planejamento_faixa.show()
        # Nova faixa modular do Planejamento: 72px. A primeira linha do
        # Progresso (68px + margens) nao deve colidir com a segunda linha.
        # Altura total agora acompanha as duas linhas compactas:
        # 71 px da primeira linha + 3 px de espacamento + 62 px do
        # Planejamento + 2 px de folga Qt = 138 px.
        # Em 158 px a sobra expandia a primeira linha e afastava os cards.
        topo.setFixedHeight(138)
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
        # O controlador de densidade pode reaplicar margens gerais no resize.
        # Reafirmar as margens compactas sem modificar o motor do Foco.
        focus_layout = self.owner._dashboard_foco_card_layout
        focus_layout.setContentsMargins(12, 5, 12, 5)
        focus_layout.setSpacing(1)
        width=self._content_width()
        if self._last_width==width:
            return
        self._last_width=width
        # A nova composição usa duas linhas à esquerda e nenhuma carta à
        # direita; não chamar o adaptador de quatro cartas (evita repais
        # transitorios de Planejamento/Progresso ao redimensionar).
        self.cards['progress'].hide()
        self.cards['planning'].hide()
        # Não utilizar HERO_FULLWIDTH_PAIR: ele ocuparia ambas as colunas.
        # A coluna 1 recebe apenas espaço expansível TRANSPARENTE.
        while self.grid.count():
            self.grid.takeAt(0)
        width_left = min(665, width)
        self.recommendation_holder.setFixedWidth(width_left)
        self.focus_holder.setFixedWidth(width_left)
        self.grid.addWidget(self.recommendation_holder, 0, 0,
                            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.grid.addWidget(self.focus_holder, 1, 0,
                            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        # Criar novo QSpacerItem: o anterior pode ter sido destruido apos takeAt().
        self._right_space = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.grid.addItem(self._right_space, 0, 1, 2, 1)
        self.grid.setColumnStretch(0, 0)
        self.grid.setColumnStretch(1, 1)
        self.grid.setRowStretch(0, 0)
        self.grid.setRowStretch(1, 0)
        self.grid.setVerticalSpacing(12)
        # O lado direito fica livre para o cérebro e o estudioso dourado.
        self.grid.invalidate()
        self.host.updateGeometry()
        self.owner.dashboard_hoje_painel.updateGeometry()
        return None

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
        self.adapter = DashboardGridAdapter(self.grid, self._grid_cards, gap=12, policy=self.policy)
        self._right_space = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.root.removeWidget(self.host)
        self.host.hide()
        self._restore_structural_surfaces()
        self.recommendation_holder_layout.removeWidget(self.cards['recommendation'])
        self.recommendation_holder.hide()
        self.focus_holder_layout.removeWidget(self.cards['focus'])
        self.focus_holder.hide()
        # Recuperar as medidas internas antes de recolocar o card no legado.
        if self._stored_focus_inner is not None:
            state = self._stored_focus_inner
            for widget, style in self._stored_focus_styles or ():
                widget.setStyleSheet(style)
            self._stored_focus_styles = None
            icon = self.cards['focus'].findChild(QWidget, 'focusDashboardCardIcon')
            goal_icon = self.cards['focus'].findChild(QWidget, 'focusDashboardGoalIcon')
            for layout, margins, spacing in state.get('inner_layouts', ()):
                layout.setContentsMargins(*margins)
                layout.setSpacing(spacing)
            if icon is not None:
                icon.setFixedSize(state['icon_size'])
            if goal_icon is not None:
                goal_icon.setFixedSize(state['goal_icon_size'])
            progress = self.owner.dashboard_hoje_foco_barra
            detail = self.owner.dashboard_hoje_foco_detalhe
            progress.setMinimumHeight(0)
            progress.setMaximumHeight(16777215)
            detail.setMinimumHeight(0)
            detail.setMaximumHeight(16777215)
            progress.setMinimumHeight(state['progress_height'][0])
            progress.setMaximumHeight(state['progress_height'][1])
            detail.setMinimumHeight(state['detail_height'][0])
            detail.setMaximumHeight(state['detail_height'][1])
            metrics = self.cards['focus'].findChild(QWidget, 'focusDashboardMetricsRow')
            artwork = self.cards['focus'].findChild(QWidget, 'focusDashboardArtSlot')
            if metrics is not None:
                metrics.setFixedHeight(state['metrics_height'])
            if artwork is not None:
                artwork.setFixedSize(state['art_width'], state['art_height'])
            self.owner.dashboard_iniciar_foco.setFixedHeight(state['button_height'])
            self.owner._dashboard_foco_card_layout.setContentsMargins(*state['margins'])
            self.owner._dashboard_foco_card_layout.setSpacing(state['spacing'])
            self._stored_focus_inner = None
        topo = self.owner.dashboard_quick_nav
        topo.planejamento_faixa.hide()
        topo.setFixedHeight(72)
        self.right.show()
        self.bottom_row.show()
        # Restaurar imediatamente a estrutura Hero original antes de
        # permitir que o caminho legado reverta para Claro/Escuro.
        self.right_column.insertWidget(0, self.cards['focus'])
        self.bottom_layout.addWidget(self.cards['progress'],1)
        self.cards['progress'].show()
        self.bottom_layout.addWidget(self.cards['planning'],1)
        self.cards['planning'].show()
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
