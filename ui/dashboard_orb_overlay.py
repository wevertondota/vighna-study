"""P03 - areas Qt invisiveis: Planejamento, Recomendacao, Foco e HUD XP.

Nao altera o GIF, o desenho Aura do XP nem as rotinas de estudo. As tres
esferas sao objetos QPushButton com mascara, sem qualquer paint; o HUD real
recebe um unico QPushButton filho, do tamanho de seu painel.
"""
from __future__ import annotations

from math import ceil, floor

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, Qt, QTimer, Signal
from PySide6.QtGui import QKeySequence, QRegion, QShortcut
from PySide6.QtWidgets import QPushButton, QWidget

from .dashboard_orb_geometry import (
    ART_WIDTH, ART_HEIGHT, HOTSPOTS_1300x715, cover_geometry,
)
from .dashboard_orb_halo import DashboardOrbHalo
from .dashboard_orb_p01_diagnostics import record as _p01_record


class InvisibleOrbButton(QPushButton):
    """Apenas recebe o clique; pintura zero, inclusive em hover/foco."""

    hoverChanged = Signal(bool)

    def __init__(self, parent, key, accessible_name):
        super().__init__(parent)
        self.setObjectName('dashboardInvisibleP03_' + key)
        self.setAccessibleName(accessible_name)
        self.setText('')
        self.setFlat(True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet(
            'QPushButton#dashboardInvisibleP03_' + key +
            ' { background: transparent; border: none; padding: 0px; }'
        )
        self.hide()

    def paintEvent(self, event):
        return

    def enterEvent(self, event):
        super().enterEvent(event)
        self.hoverChanged.emit(True)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.hoverChanged.emit(False)


class DashboardOrbOverlay(QObject):
    orbActivated = Signal(str)

    def __init__(self, owner, root, scroll):
        super().__init__(root)
        self.owner = owner
        self.root = root
        self.scroll = scroll
        self.viewport = scroll.viewport()
        self._scheduled = False
        self._last_geometry = {}
        self._last_state = None
        self._buttons = {}
        # Halo somente visual, filho do mesmo viewport dos botoes P03.
        self._halo = DashboardOrbHalo(self.viewport)
        # P06: reutiliza a MESMA textura gaussiana homologada no P05.
        # Cada halo tem animacao de opacidade independente e nao recebe mouse.
        self._extra_halos = {
            'planejamento': DashboardOrbHalo(self.viewport),
            'foco': DashboardOrbHalo(self.viewport),
        }
        for key, halo in self._extra_halos.items():
            halo.setObjectName('dashboardGlowV2P06_' + key)
        # HUD e widget independente do GIF: ancora em sua propria geometria.
        self._xp_halo = DashboardOrbHalo(self.root)
        self._xp_halo.setObjectName('dashboardGlowV2P06_progresso')
        for hs in HOTSPOTS_1300x715:
            b = InvisibleOrbButton(self.viewport, hs.key, hs.accessible_name)
            b.clicked.connect(lambda _checked=False, key=hs.key: self.activate(key))
            if hs.key == 'recomendacao':
                b.hoverChanged.connect(self._on_recommendation_hover)
            elif hs.key in self._extra_halos:
                b.hoverChanged.connect(
                    lambda inside, key=hs.key: self._on_extra_hover(key, inside)
                )
            self._buttons[hs.key] = b
        # Compatibilidade com o P02 e suas ferramentas de diagnostico.
        self.button = self._buttons['planejamento']
        self._hud_parent = None
        self._hud_button = None
        self._shortcuts = []
        for index, key in enumerate(('planejamento', 'recomendacao', 'foco', 'progresso'), 1):
            sh = QShortcut(QKeySequence(f'Ctrl+Alt+{index}'), self.root)
            sh.setContext(Qt.WindowShortcut)
            sh.activated.connect(lambda key=key: self.activate(key))
            self._shortcuts.append(sh)
        self.root.installEventFilter(self)
        self.viewport.installEventFilter(self)
        self.scroll.verticalScrollBar().valueChanged.connect(self.schedule_sync)
        self.scroll.horizontalScrollBar().valueChanged.connect(self.schedule_sync)
        # O painel de XP e criado tardiamente pelo controlador do cabecalho.
        self._watchdog = QTimer(self)
        self._watchdog.setInterval(700)
        self._watchdog.timeout.connect(self._watch_enabled)
        self._watchdog.start()
        _p01_record('p03_initialized', targets='planning-recommend-focus-xp')
        QTimer.singleShot(0, self.sync)

    def _is_enabled(self):
        try:
            return (self.owner.telas.currentWidget() is self.owner.tela_inicial
                    and self.root.isVisible()
                    and str(self.owner.tema_atual).strip().lower() == 'futurista'
                    and getattr(self.root, '_dashboard_gif_animado', None) is not None
                    and self.root._dashboard_gif_animado.quadro() is not None)
        except (AttributeError, RuntimeError):
            return False

    def activate(self, key):
        if key not in ('planejamento', 'recomendacao', 'foco', 'progresso'):
            return
        enabled = self._is_enabled()
        _p01_record('p03_activate', card=key, enabled=enabled)
        if enabled:
            self.orbActivated.emit(key)

    def _on_recommendation_hover(self, inside):
        # Sem alterar o clicador P03: ilumina por tras do mesmo botao.
        if not self._is_enabled():
            self._halo.reset()
            return
        self._halo.set_hovered(inside)
        if inside:
            self._buttons['recomendacao'].raise_()

    def _on_extra_hover(self, key, inside):
        # Os botões P03 mantêm o controle dos cliques; efeito apenas luminoso.
        halo = self._extra_halos[key]
        if not self._is_enabled():
            halo.reset()
            return
        halo.set_hovered(inside)
        if inside:
            self._buttons[key].raise_()

    def _on_xp_hover(self, inside):
        if not self._is_enabled():
            self._xp_halo.reset()
            return
        self._xp_halo.set_hovered(inside)
        if inside:
            # Mesmo recebendo paint no primeiro plano, não capta cliques.
            self._xp_halo.raise_()

    def _watch_enabled(self):
        enabled = self._is_enabled()
        current_xp = self.root.findChild(QWidget, 'dashboardFloatingXP')
        # Widgets podem nao aparecer se a esfera for recortada; nesse caso
        # nao pedir sync continuamente. Apenas transicao de estado/hud.
        if (current_xp is not self._hud_parent or
                self._last_state != enabled or
                (not enabled and any(b.isVisible() for b in self._buttons.values()))):
            self.schedule_sync()

    def eventFilter(self, watched, event):
        if watched in (self.root, self.viewport, self._hud_parent) and event.type() in (
            QEvent.Resize, QEvent.Move, QEvent.Show, QEvent.Hide, QEvent.LayoutRequest,
        ):
            self.schedule_sync()
        return False

    def schedule_sync(self, *_args):
        if self._scheduled:
            return
        self._scheduled = True
        QTimer.singleShot(0, self._scheduled_sync)

    def _scheduled_sync(self):
        self._scheduled = False
        self.sync()

    def _sync_xp(self, enabled):
        xp = self.root.findChild(QWidget, 'dashboardFloatingXP')
        if xp is not self._hud_parent:
            if self._hud_parent is not None:
                try:
                    self._hud_parent.removeEventFilter(self)
                except RuntimeError:
                    pass
            if self._hud_button is not None:
                self._hud_button.hide()
                self._hud_button.deleteLater()
            self._xp_halo.reset()
            self._hud_button = None
            self._hud_parent = xp
            if xp is not None:
                xp.installEventFilter(self)
                b = InvisibleOrbButton(xp, 'progresso', 'Abrir card Progresso')
                b.clicked.connect(lambda _checked=False: self.activate('progresso'))
                b.hoverChanged.connect(self._on_xp_hover)
                self._hud_button = b
        b = self._hud_button
        if b is None:
            return
        if not enabled or not xp.isVisibleTo(self.root):
            self._xp_halo.reset()
            if not b.isHidden():
                b.hide()
            return
        # O emblema é desenhado pelo HUD nas coordenadas locais (40,38.5)
        # sobre uma referência de 270x80. O centro foi confirmado pela
        # marcação: (1020.7,152.5) na captura de 1366x768.
        xp_pos = xp.mapTo(self.root, QPoint(0, 0))
        sx = xp.width() / 270.0
        sy = xp.height() / 80.0
        self._xp_halo.set_target(
            xp_pos.x() + 40.0 * sx, xp_pos.y() + 38.5 * sy,
            (20.34 / 1.065) * sx, (20.34 / 1.065) * sy,
            self.root.rect(),
        )
        if b.geometry() != xp.rect():
            b.setGeometry(xp.rect())
        if b.isHidden():
            b.show()
            b.raise_()

    def sync(self):
        enabled = self._is_enabled()
        self._last_state = enabled
        for sh in self._shortcuts:
            if sh.isEnabled() != enabled:
                sh.setEnabled(enabled)
        if not enabled or self.root.width() < 1 or self.viewport.width() < 1:
            for b in self._buttons.values():
                if not b.isHidden():
                    b.hide()
            self._halo.reset()
            for halo in self._extra_halos.values():
                halo.reset()
            self._xp_halo.reset()
            self._sync_xp(False)
            return
        geom = cover_geometry(self.root.width(), self.root.height())
        offset = self.root.mapTo(self.viewport, QPoint(0, 0))
        for hs in HOTSPOTS_1300x715:
            button = self._buttons[hs.key]
            scalex = (geom.dest.w / geom.source.w) * geom.art_width / ART_WIDTH
            scaley = (geom.dest.h / geom.source.h) * geom.art_height / ART_HEIGHT
            cx, cy = geom.to_view(hs.circle.cx * geom.art_width / ART_WIDTH,
                                  hs.circle.cy * geom.art_height / ART_HEIGHT)
            ellipse = QRect(floor(cx - hs.circle.rx * scalex) + offset.x(),
                            floor(cy - hs.circle.ry * scaley) + offset.y(),
                            ceil(2 * hs.circle.rx * scalex) + 1,
                            ceil(2 * hs.circle.ry * scaley) + 1)
            region = QRegion(ellipse, QRegion.RegionType.Ellipse)
            if hs.label is not None:
                lx, ly = geom.to_view(hs.label.x * geom.art_width / ART_WIDTH,
                                      hs.label.y * geom.art_height / ART_HEIGHT)
                label = QRect(floor(lx)+offset.x(), floor(ly)+offset.y(),
                              ceil(hs.label.w * scalex)+1,
                              ceil(hs.label.h * scaley)+1)
                region = region.united(QRegion(label))
            region = region.intersected(QRegion(self.viewport.rect()))
            if region.isEmpty():
                if not button.isHidden():
                    button.hide()
                if hs.key == 'recomendacao':
                    self._halo.reset()
                elif hs.key in self._extra_halos:
                    self._extra_halos[hs.key].reset()
                continue
            if hs.key == 'recomendacao':
                # P04-R3: o HALO é ancorado no círculo marcado na arte A
                # (1300x715), independente do centro do botão clicável P03.
                # O anel DOURADO é pintado com raio base * 1.065.
                hx, hy = geom.to_view(
                    467.1 * geom.art_width / ART_WIDTH,
                    298.4 * geom.art_height / ART_HEIGHT,
                )
                self._halo.set_target(
                    hx + offset.x(), hy + offset.y(),
                    (94.8 / 1.065) * scalex,
                    (93.6 / 1.065) * scaley,
                    self.viewport.rect(),
                )
            if hs.key in self._extra_halos:
                # Referências do círculo vermelho convertidas ao GIF A
                # com transformação aferida SIFT/RANSAC (escala 0.99232).
                # Raios representam o contorno DOURADO da textura V2.
                targets = {
                    'planejamento': (186.27, 265.75, 54.42, 54.42),
                    'foco': (732.29, 265.81, 50.94, 50.94),
                }
                tx, ty, radius_x, radius_y = targets[hs.key]
                hx, hy = geom.to_view(
                    tx * geom.art_width / ART_WIDTH,
                    ty * geom.art_height / ART_HEIGHT,
                )
                self._extra_halos[hs.key].set_target(
                    hx + offset.x(), hy + offset.y(),
                    (radius_x / 1.065) * scalex,
                    (radius_y / 1.065) * scaley,
                    self.viewport.rect(),
                )
            bounds = region.boundingRect()
            mask = region.translated(-bounds.x(), -bounds.y())
            signature = (bounds.x(), bounds.y(), bounds.width(), bounds.height(),
                         mask.rectCount())
            if signature != self._last_geometry.get(hs.key):
                button.setGeometry(bounds)
                button.setMask(mask)
                self._last_geometry[hs.key] = signature
            if button.isHidden():
                button.show()
                button.raise_()
        self._sync_xp(True)
