"""M2-D1A — diagnóstico sob demanda da geometria real do Dashboard.

Só leitura. Não reorganiza/mostra/oculta/redimensiona widgets e não usa SQL.
A exportação é iniciada exclusivamente pelo usuário via Ctrl+Shift+F12, com
escolha explícita do arquivo de destino. Nenhum dado é salvo automaticamente.

Não exige importação de PySide6 para testar as funções puras deste módulo.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .dashboard_geometry_policy import DashboardGeometryPolicy


_CARD_ATTRS = {
    'recommendation': 'dashboard_hoje_acao',
    'planning': 'dashboard_resumo_ia',
}
_REF_CARDS = {'focus': 'foco', 'progress': 'progresso'}


def _size(s):
    if s is None:
        return None
    return {'width': int(s.width()), 'height': int(s.height())}


def _rect(r):
    if r is None:
        return None
    return {'x': int(r.x()), 'y': int(r.y()), 'width': int(r.width()), 'height': int(r.height())}


def _margins(m):
    if m is None:
        return None
    return {'left': int(m.left()), 'top': int(m.top()),
            'right': int(m.right()), 'bottom': int(m.bottom())}


def _inspect(widget):
    if widget is None:
        return {'present': False}
    try:
        info = {
            'present': True,
            'type': type(widget).__name__,
            'object_name': str(widget.objectName() or ''),
            'visible': bool(widget.isVisible()),
            'geometry': _rect(widget.geometry()),
            'contents_rect': _rect(widget.contentsRect()),
            'size_hint': _size(widget.sizeHint()),
            'minimum_size_hint': _size(widget.minimumSizeHint()),
            'minimum_size': _size(widget.minimumSize()),
            'maximum_size': _size(widget.maximumSize()),
        }
        try:
            p = widget.mapToGlobal(widget.rect().topLeft())
            info['screen_rect'] = {'x': int(p.x()), 'y': int(p.y()),
                                   'width': int(widget.width()), 'height': int(widget.height())}
        except (AttributeError, TypeError, RuntimeError):
            info['screen_rect'] = None
        lay = widget.layout()
        if lay is not None:
            info['layout'] = {'type': type(lay).__name__, 'spacing': int(lay.spacing()),
                              'margins': _margins(lay.contentsMargins()),
                              'minimum_size': _size(lay.minimumSize()),
                              'size_hint': _size(lay.sizeHint())}
        return info
    except (AttributeError, RuntimeError, TypeError) as exc:
        return {'present': True, 'error': type(exc).__name__}


def _visible_text_geometry(widget):
    """Lê apenas tamanhos/métricas do texto, nunca o conteúdo do usuário."""
    try:
        from PySide6.QtWidgets import QLabel, QPushButton
    except ImportError:
        return []
    if widget is None:
        return []
    found = []
    for typ in (QLabel, QPushButton):
        for child in widget.findChildren(typ):
            if not child.isVisible():
                continue
            text = str(child.text() or '')
            if not text:
                continue
            rect = child.contentsRect()
            fm = child.fontMetrics()
            natural_w = int(fm.horizontalAdvance(text))
            is_wrapped = bool(isinstance(child, QLabel) and child.wordWrap())
            found.append({
                'object_name': str(child.objectName() or ''),
                'type': type(child).__name__,
                'width': int(rect.width()), 'height': int(rect.height()),
                'text_length': len(text),
                'natural_text_width': natural_w,
                'word_wrap': is_wrapped,
                'possible_horizontal_clip': bool(not is_wrapped and natural_w > rect.width()),
            })
    return found


def collect_dashboard_geometry(window):
    """Executar na thread GUI, com a janela visível e layouts calculados."""
    refs = getattr(window, '_dashboard_modelo_refs', None) or {}
    scroll = getattr(window, 'dashboard_scroll', None)
    viewport = scroll.viewport() if scroll is not None else None
    hero = getattr(window, 'dashboard_hoje_painel', None)
    sidebar = getattr(window, 'dashboard_sidebar', None)
    root = getattr(window, 'dashboard_hoje_painel', None)
    cards = {k: _inspect(getattr(window, v, None)) for k, v in _CARD_ATTRS.items()}
    cards.update({k: _inspect(refs.get(v)) for k, v in _REF_CARDS.items()})
    containers = {
        'dashboard_panel': _inspect(hero),
        'dashboard_scroll': _inspect(scroll),
        'viewport': _inspect(viewport),
        'right_column': _inspect(getattr(window, '_dashboard_hero_direita', None)),
        'bottom_row': _inspect(getattr(window, '_dashboard_hero_bottom_row', None)),
        'planning_container': _inspect(refs.get('planejamento_container')),
        'sidebar': _inspect(sidebar),
        'quick_nav': _inspect(getattr(window, 'dashboard_quick_nav', None)),
    }
    actual_width = int(hero.contentsRect().width()) if hero is not None else 0
    viewport_width = int(viewport.contentsRect().width()) if viewport is not None else 0
    # A largura do painel inclui sua própria borda e padding. Para o modelo
    # de layout, preferir a largura do conteúdo interno do painel.
    layout = hero.layout() if hero is not None else None
    if layout is not None:
        mg = layout.contentsMargins()
        actual_width = max(0, actual_width - mg.left() - mg.right())
    hypothesis = None
    if actual_width > 0:
        plan = DashboardGeometryPolicy().plan(actual_width, int(viewport.height()) if viewport is not None and viewport.height() > 0 else None)
        hypothesis = {
            'mode': plan.mode.value,
            'available_width': plan.available_width,
            'content_height': plan.content_height,
            'needs_vertical_scroll': plan.needs_vertical_scroll,
            'reasons': list(plan.reasons),
            'cards': {k: {'x': v.x, 'y': v.y, 'width': v.width, 'height': v.height}
                      for k, v in plan.cards.items()},
            'caution': 'Hipótese matemática; NÃO aplicada aos widgets e não validada visualmente.',
        }
    screen = window.screen() if hasattr(window, 'screen') else None
    return {
        'format': 'vighna-dashboard-real-geometry-m2d1a-v1',
        'captured_utc': datetime.now(timezone.utc).isoformat(),
        'privacy': 'Não contém textos de estudos nem informações do banco; apenas métricas de UI.',
        'window': _inspect(window),
        'screen': {'device_pixel_ratio': float(screen.devicePixelRatio()),
                   'logical_dpi': float(screen.logicalDotsPerInch()),
                   'physical_dpi': float(screen.physicalDotsPerInch())} if screen is not None else None,
        'viewport_width': viewport_width,
        'available_content_width': actual_width,
        'hero_active': bool(getattr(window, '_dashboard_hero_reordenado', False)),
        'cards': cards,
        'containers': containers,
        'text_metrics': {k: _visible_text_geometry(
            getattr(window, _CARD_ATTRS[k], None) if k in _CARD_ATTRS else refs.get(_REF_CARDS[k]))
            for k in ('recommendation', 'focus', 'progress', 'planning')},
        'shadow_policy': hypothesis,
    }


def save_snapshot(snapshot, path):
    target = Path(path)
    target.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return target


def attach_dashboard_geometry_shortcut(window):
    """Adiciona atalho não visual; apenas coleta se usuário solicitar.

    A referência fica no main window para não expirar por GC.
    """
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QKeySequence, QShortcut
    from PySide6.QtWidgets import QFileDialog, QMessageBox

    if getattr(window, '_dashboard_geometry_shortcut', None) is not None:
        return window._dashboard_geometry_shortcut

    def exportar():
        panel = getattr(window, 'dashboard_hoje_painel', None)
        if panel is None or not panel.isVisible():
            return
        nome = 'Vighna_Dashboard_Geometria.json'
        destino, _ = QFileDialog.getSaveFileName(
            window, 'Exportar geometria do Dashboard', str(Path.home() / nome),
            'Diagnóstico JSON (*.json)'
        )
        if not destino:
            return
        try:
            save_snapshot(collect_dashboard_geometry(window), destino)
        except (OSError, RuntimeError, ValueError, TypeError, AttributeError) as exc:
            QMessageBox.warning(window, 'Diagnóstico não exportado',
                                f'Não foi possível exportar as medições: {exc}')
            return
        QMessageBox.information(window, 'Diagnóstico exportado',
                                'Medições do Dashboard salvas. Nenhuma geometria foi alterada.')

    shortcut = QShortcut(QKeySequence('Ctrl+Shift+F12'), window)
    shortcut.setContext(Qt.ApplicationShortcut)
    shortcut.activated.connect(exportar)
    window._dashboard_geometry_shortcut = shortcut
    return shortcut
