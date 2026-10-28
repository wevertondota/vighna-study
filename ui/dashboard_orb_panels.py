"""O04-R3: abrir os cards funcionais ORIGINAIS a partir das esferas do GIF V4.

A área inicial mantém a arte livre. Os três cards só mudam de contêiner
visual, e voltam ao layout anterior quando o painel é fechado. Nenhum
algoritmo, sinal, cronômetro ou banco é duplicado.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, QEvent, Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from .dashboard_orb_p01_diagnostics import record as _p01_record

from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget,
)

CARD_LABELS = {
    'planejamento': 'Planejamento',
    'recomendacao': 'Recomendação do Algoritmo',
    'foco': 'Modo Foco',
    'progresso': 'Seu Progresso',
}


class DashboardOrbPanels(QObject):
    """Navegação por esferas; uma só instância funcional de cada card."""

    def __init__(self, owner, root, scroll):
        super().__init__(root)
        self.owner = owner
        self.root = root
        self.viewport = scroll.viewport()
        self.active_key = None
        self._mounted = None
        self._previous_focus = None
        self._pending = False
        self._clean_mode = False
        self._root_layout = root.layout()
        self._original_host = owner.dashboard_hoje_painel

        # Referências aos cards reais; o algoritmo e seus sinais já existem.
        self.cards = {
            'planejamento': owner.dashboard_resumo_ia,
            'recomendacao': owner.dashboard_hoje_acao,
            'foco': owner._dashboard_foco_widget,
            'progresso': owner._dashboard_progresso_widget,
        }
        assert all(card is not None for card in self.cards.values())
        assert self._root_layout.indexOf(self._original_host) >= 0

        # Reserva altura do cenário, mas pinta NADA e não recebe mouse.
        self.scene = QWidget(root)
        self.scene.setObjectName('dashboardOrbCleanSceneO04R1')
        self.scene.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.scene.setStyleSheet(
            'QWidget#dashboardOrbCleanSceneO04R1 {'
            'background: transparent; border: none;}'
        )
        original_index = self._root_layout.indexOf(self._original_host)
        self._root_layout.insertWidget(original_index + 1, self.scene)
        self.scene.hide()

        # Janela não modal dentro do viewport: não interrompe QMovie.
        self.panel = QFrame(self.viewport)
        self.panel.setObjectName('dashboardOrbFunctionalPanelO04R1')
        self.panel.setAccessibleName('Card funcional do Dashboard')
        self.panel.setAttribute(Qt.WA_StyledBackground, True)
        self.panel.setStyleSheet('''
            QFrame#dashboardOrbFunctionalPanelO04R1 {
                background-color: #061726;
                border: 1px solid #41C6EC;
                border-radius: 15px;
            }
            QLabel#dashboardOrbFunctionalTitleO04R1 {
                color: #F3FAFF; font: 700 15pt "Segoe UI";
                background: transparent; border: none;
            }
            QPushButton#dashboardOrbFunctionalCloseO04R1 {
                color: white; background-color: #13334B;
                border: 1px solid #54B4D6; border-radius: 8px;
                font: 700 12pt "Segoe UI";
            }
            QPushButton#dashboardOrbFunctionalCloseO04R1:focus {
                border: 2px solid #FFE69B;
            }
            QWidget#dashboardOrbFunctionalBodyO04R1 {
                background: transparent; border: none;
            }
        ''')
        outer = QVBoxLayout(self.panel)
        outer.setContentsMargins(14, 12, 14, 14)
        outer.setSpacing(8)
        bar = QHBoxLayout()
        self.title = QLabel(self.panel)
        self.title.setObjectName('dashboardOrbFunctionalTitleO04R1')
        bar.addWidget(self.title, 1)
        self.close_button = QPushButton('×', self.panel)
        self.close_button.setObjectName('dashboardOrbFunctionalCloseO04R1')
        self.close_button.setAccessibleName('Fechar card e voltar ao cenário')
        self.close_button.setToolTip('Fechar (Esc)')
        self.close_button.setFixedSize(36, 34)
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.clicked.connect(self.close)
        bar.addWidget(self.close_button)
        outer.addLayout(bar)

        self.body = QWidget(self.panel)
        self.body.setObjectName('dashboardOrbFunctionalBodyO04R1')
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)
        outer.addWidget(self.body, 1)
        self.panel.hide()
        self.escape = QShortcut(QKeySequence('Escape'), self.panel)
        self.escape.setContext(Qt.WidgetWithChildrenShortcut)
        self.escape.activated.connect(self.close)

        self.viewport.installEventFilter(self)
        self.root.installEventFilter(self)
        owner.telas.currentChanged.connect(self._screen_changed)
        QTimer.singleShot(0, self.sync_mode)

    def _futurist(self):
        return str(self.owner.tema_atual).strip().lower() == 'futurista'

    def _dashboard_active(self):
        try:
            return (self.owner.telas.currentWidget() is self.owner.tela_inicial
                    and self.root.isVisible() and self._futurist())
        except (AttributeError, RuntimeError):
            return False

    def _scene_height(self):
        margins = self._root_layout.contentsMargins()
        nav = getattr(self.owner, 'dashboard_quick_nav', None)
        nav_height = nav.height() if nav is not None and nav.isVisibleTo(self.root) else 0
        return max(440, self.viewport.height() - nav_height - margins.top() - 24)

    def sync_mode(self):
        # Esconder só a camada visual; os widgets continuam vivos e são
        # atualizados pelos mesmos métodos do programa, mesmo sem painel aberto.
        clean = self._futurist()
        if not clean and self.active_key is not None:
            self.close()
        if clean != self._clean_mode:
            self._clean_mode = clean
            self._original_host.setVisible(not clean)
            self.scene.setVisible(clean)
            self._root_layout.invalidate()
        if clean:
            height = self._scene_height()
            if self.scene.height() != height or self.scene.minimumHeight() != height:
                self.scene.setFixedHeight(height)
        if self.active_key is not None:
            self._position_panel()
        overlay = getattr(self.owner, '_dashboard_orb_overlay', None)
        if overlay is not None:
            overlay.schedule_sync()

    @staticmethod
    def _slot_in_layout(layout, card):
        """Encontra o QLayout dono real, inclusive dentro de sublayouts Qt.

        O parentWidget() de um QWidget em um QHBoxLayout aninhado e o
        contêiner do QVBoxLayout externo, não necessariamente o QHBoxLayout.
        """
        for index in range(layout.count()):
            item = layout.itemAt(index)
            if item is None:
                continue
            if item.widget() is card:
                stretch = layout.stretch(index) if hasattr(layout, 'stretch') else 0
                return layout, index, item.alignment(), stretch
            child_layout = item.layout()
            if child_layout is not None:
                slot = DashboardOrbPanels._slot_in_layout(child_layout, card)
                if slot is not None:
                    return slot
        return None

    def _card_parent_layout(self, card):
        parent = card.parentWidget()
        ancestor = parent
        while ancestor is not None:
            layout = ancestor.layout()
            if layout is not None:
                slot = self._slot_in_layout(layout, card)
                if slot is not None:
                    found_layout, index, alignment, stretch = slot
                    return parent, found_layout, index, alignment, stretch
            ancestor = ancestor.parentWidget()
        raise RuntimeError('Card fora de um QLayout: ' + card.objectName())

    def _take_card(self, key):
        card = self.cards[key]
        original_parent, original_layout, index, alignment, stretch = self._card_parent_layout(card)
        original_state = (
            card.minimumHeight(), card.maximumHeight(), card.sizePolicy(),
            card.isHidden(),
        )
        original_layout.removeWidget(card)
        try:
            card.setParent(self.body)
            card.setMinimumHeight(0)
            card.setMaximumHeight(16777215)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.body_layout.addWidget(card, 1)
            card.show()
        except Exception:
            # Falha parcial: nenhum card pode ficar sem layout.
            self.body_layout.removeWidget(card)
            card.setParent(original_parent)
            card.setMinimumHeight(original_state[0])
            card.setMaximumHeight(original_state[1])
            card.setSizePolicy(original_state[2])
            original_layout.insertWidget(index, card, stretch, alignment)
            if original_state[3]:
                card.hide()
            else:
                card.show()
            raise
        self._mounted = (key, card, original_parent, original_layout,
                         index, alignment, stretch, original_state)

    def _return_card(self):
        if self._mounted is None:
            return
        key, card, parent, layout, index, alignment, stretch, state = self._mounted
        self._mounted = None
        self.body_layout.removeWidget(card)
        card.setParent(parent)
        # Restaurar medidas e o stretch do layout original, sem recriar sinais.
        card.setMinimumHeight(0)
        card.setMaximumHeight(16777215)
        card.setMinimumHeight(state[0])
        card.setMaximumHeight(state[1])
        card.setSizePolicy(state[2])
        layout.insertWidget(index, card, stretch, alignment)
        if state[3]:
            card.hide()
        else:
            card.show()
        layout.invalidate()

    def open(self, key):
        if key != 'planejamento':
            return self._p01_original_open(key)
        _p01_record('open_requested', dashboard_active=self._dashboard_active(),
                    active_panel=self.active_key is not None)
        try:
            result = self._p01_original_open(key)
        except Exception as error:
            _p01_record('open_exception', exception_type=type(error).__name__,
                        active_panel=self.active_key is not None)
            raise
        _p01_record('open_result', accepted=bool(result),
                    panel_visible=self.panel.isVisible(),
                    active_is_planning=self.active_key == 'planejamento')
        return result

    def _p01_original_open(self, key):
        if key not in self.cards or not self._dashboard_active():
            return False
        self.sync_mode()
        if self.active_key == key:
            # Um segundo clique na mesma esfera fecha o card.
            self.close()
            return True
        if self.active_key is not None:
            self._return_card()
        else:
            self._previous_focus = QApplication.focusWidget()
        # Só confirmar a abertura depois que o widget entrou no painel.
        # Uma falha no layout não pode deixar active_key preso nem ocultar
        # silenciosamente todas as ações seguintes.
        try:
            self._take_card(key)
            self.title.setText(CARD_LABELS[key])
            self._position_panel()
            self.panel.show()
            self.panel.raise_()
            self.active_key = key
            self.close_button.setFocus(Qt.OtherFocusReason)
            return True
        except (RuntimeError, ValueError, AttributeError, TypeError) as error:
            _p01_record('p03_panel_open_error', card=key,
                        exception_type=type(error).__name__)
            self.panel.hide()
            if self._mounted is not None:
                try:
                    self._return_card()
                except (RuntimeError, ValueError, AttributeError, TypeError):
                    _p01_record('p03_restore_failed', card=key)
            self.active_key = None
            return False

    def close(self):
        if self.active_key is None:
            return
        self.panel.hide()
        self._return_card()
        self.active_key = None
        prior = self._previous_focus
        self._previous_focus = None
        if prior is not None:
            try:
                if prior.isVisible() and prior.isEnabled():
                    prior.setFocus(Qt.OtherFocusReason)
            except RuntimeError:
                pass

    def _screen_changed(self, _index):
        if not self._dashboard_active():
            self.close()
        self._schedule_sync()

    def eventFilter(self, watched, event):
        if watched in (self.viewport, self.root):
            if event.type() in (QEvent.Resize, QEvent.Show, QEvent.StyleChange):
                self._schedule_sync()
            elif event.type() == QEvent.Hide and self.active_key is not None:
                if not self._dashboard_active():
                    self.close()
        return False

    def _schedule_sync(self):
        if self._pending:
            return
        self._pending = True
        QTimer.singleShot(0, self._scheduled_sync)

    def _scheduled_sync(self):
        self._pending = False
        self.sync_mode()

    def _position_panel(self):
        w, h = self.viewport.width(), self.viewport.height()
        if w < 1 or h < 1:
            return
        width = min(750, max(1, w - 32))
        height = min(470, max(1, h - 32))
        self.panel.setGeometry((w-width)//2, (h-height)//2, width, height)
