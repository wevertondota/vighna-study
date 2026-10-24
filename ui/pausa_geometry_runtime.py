"""Medição sob demanda da janela Pausa & Desafios (VighnaStudy).

Atalho Ctrl+Shift+F11, apenas quando a janela de jogos está aberta.
Coleta tamanhos/posições, limites, dicas de tamanho, layouts, DPI, abas e
áreas roláveis; alterna temporariamente as abas e devolve à aba original.
Exporta JSON completo, TXT resumo e PNG de cada aba no diretório escolhido.
Nenhuma escrita no banco de dados, nenhuma mudança permanente de geometria.

As dimensões registradas são pixels lógicos Qt, e os PNGs representam somente
os conteúdos visíveis, sem a moldura nativa da janela do Windows.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

_FORMAT = 'vighna-pausa-desafios-full-widget-geometry-r1'


def _size(s):
    return {'width': int(s.width()), 'height': int(s.height())} if s is not None else None


def _rect(r):
    return {'x': int(r.x()), 'y': int(r.y()), 'width': int(r.width()), 'height': int(r.height())} if r is not None else None


def _margins(m):
    return ({'left': int(m.left()), 'top': int(m.top()),
             'right': int(m.right()), 'bottom': int(m.bottom())} if m is not None else None)


def _enum_name(value):
    return str(getattr(value, 'name', value))


def _layout_info(layout, depth=0):
    if layout is None:
        return None
    info = {
        'class': type(layout).__name__,
        'geometry': _rect(layout.geometry()),
        'contents_margins': _margins(layout.contentsMargins()),
        'spacing': int(layout.spacing()),
        'minimum_size': _size(layout.minimumSize()),
        'preferred_size': _size(layout.sizeHint()),
        'item_count': int(layout.count()),
    }
    for prop, method in [('horizontal_spacing','horizontalSpacing'),
                         ('vertical_spacing','verticalSpacing'),
                         ('rows','rowCount'),('columns','columnCount')]:
        if hasattr(layout, method):
            try:
                info[prop] = int(getattr(layout, method)())
            except (TypeError, ValueError, RuntimeError):
                pass
    items = []
    for index in range(min(2000, int(layout.count()))):
        try:
            item = layout.itemAt(index)
            if item is None:
                continue
            target = item.widget()
            sublayout = item.layout()
            items.append({
                'index': index,
                'type': 'widget' if target is not None else ('layout' if sublayout is not None else 'spacer'),
                'object_name': str(target.objectName() or '') if target is not None else '',
                'widget_class': type(target).__name__ if target is not None else '',
                'layout_class': type(sublayout).__name__ if sublayout is not None else '',
                'geometry': _rect(item.geometry()),
                'minimum_size': _size(item.minimumSize()),
                'preferred_size': _size(item.sizeHint()),
                'maximum_size': _size(item.maximumSize()),
                'expanding_directions': str(item.expandingDirections()),
                'nested_layout': (_layout_info(sublayout, depth + 1)
                                  if sublayout is not None and depth < 18 else None),
            })
        except (RuntimeError, AttributeError, TypeError):
            items.append({'index': index, 'error': 'item_inacessivel'})
    info['items'] = items
    return info


def _measure_widget(widget, dialog, path):
    """Geometria física do widget e das restrições Qt, sem texto real."""
    from PySide6.QtWidgets import QLabel, QPushButton, QAbstractButton, QScrollArea
    info = {
        'path': path,
        'class': type(widget).__name__,
        'object_name': str(widget.objectName() or ''),
        'visible': bool(widget.isVisible()),
        'enabled': bool(widget.isEnabled()),
        'geometry_in_parent': _rect(widget.geometry()),
        'rect': _rect(widget.rect()),
        'contents_rect': _rect(widget.contentsRect()),
        'minimum_size': _size(widget.minimumSize()),
        'maximum_size': _size(widget.maximumSize()),
        'preferred_size': _size(widget.sizeHint()),
        'minimum_size_hint': _size(widget.minimumSizeHint()),
        'size_policy': {
            'horizontal': _enum_name(widget.sizePolicy().horizontalPolicy()),
            'vertical': _enum_name(widget.sizePolicy().verticalPolicy()),
            'has_height_for_width': bool(widget.hasHeightForWidth()),
        },
        'layout': _layout_info(widget.layout()),
    }
    try:
        pos = widget.mapTo(dialog, widget.rect().topLeft())
        info['rect_in_dialog'] = {'x': int(pos.x()), 'y': int(pos.y()),
                                  'width': int(widget.width()), 'height': int(widget.height())}
        pos = widget.mapToGlobal(widget.rect().topLeft())
        info['rect_on_screen'] = {'x': int(pos.x()), 'y': int(pos.y()),
                                  'width': int(widget.width()), 'height': int(widget.height())}
    except (RuntimeError, TypeError, AttributeError):
        info['rect_in_dialog'] = None
        info['rect_on_screen'] = None
    if isinstance(widget, QScrollArea):
        viewport = widget.viewport()
        vbar = widget.verticalScrollBar()
        hbar = widget.horizontalScrollBar()
        info['scroll_area'] = {
            'viewport_size': _size(viewport.size()),
            'vertical': {'minimum': int(vbar.minimum()), 'maximum': int(vbar.maximum()),
                         'value': int(vbar.value()), 'page_step': int(vbar.pageStep())},
            'horizontal': {'minimum': int(hbar.minimum()), 'maximum': int(hbar.maximum()),
                           'value': int(hbar.value()), 'page_step': int(hbar.pageStep())},
        }
    if isinstance(widget, (QLabel, QAbstractButton, QPushButton)):
        label = str(widget.text() or '')
        if label:
            rect = widget.contentsRect()
            preferred_text_width = int(widget.fontMetrics().horizontalAdvance(label))
            wrapped = bool(isinstance(widget, QLabel) and widget.wordWrap())
            info['text_metrics'] = {
                'length': len(label), 'natural_width': preferred_text_width,
                'content_width': int(rect.width()), 'content_height': int(rect.height()),
                'word_wrap': wrapped,
                'possible_horizontal_clip': bool(widget.isVisible() and not wrapped and
                                                  preferred_text_width > rect.width()),
            }
    return info


def _tree(root, dialog, *, max_nodes=4500):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QWidget
    nodes = []
    stack = [(root, f'{type(root).__name__}[0]', 0)]
    while stack and len(nodes) < max_nodes:
        w, path, depth = stack.pop()
        try:
            nodes.append(_measure_widget(w, dialog, path))
            if depth >= 40:
                continue
            children = w.findChildren(QWidget, Qt.FindDirectChildrenOnly)
            counters = {}
            named_children = []
            for child in children:
                cls = type(child).__name__
                index = counters.get(cls, 0)
                counters[cls] = index + 1
                objname = str(child.objectName() or '')
                named_children.append((child, f'{path}/{cls}[{index}]' +
                                       (f'#{objname}' if objname else '')))
            for child, child_path in reversed(named_children):
                stack.append((child, child_path, depth + 1))
        except (RuntimeError, AttributeError, TypeError) as exc:
            nodes.append({'path': path, 'error': type(exc).__name__})
    return {'nodes': nodes, 'node_count': len(nodes), 'truncated': bool(stack)}


def _tab_state(tabs):
    bar = tabs.tabBar()
    return {
        'current_index': int(tabs.currentIndex()),
        'count': int(tabs.count()),
        'tabs': [{
            'index': i,
            'name': str(tabs.tabText(i)),
            'enabled': bool(tabs.isTabEnabled(i)),
            'tab_rect_in_bar': _rect(bar.tabRect(i)),
            'page_size': _size(tabs.widget(i).size()),
        } for i in range(tabs.count())],
        'tab_bar_geometry': _rect(bar.geometry()),
    }


def _dialog_state(dialog):
    win = dialog.windowHandle()
    screen = win.screen() if win is not None else dialog.screen()
    out = {
        'dialog_geometry': _measure_widget(dialog, dialog, 'JanelaPausaDesafios[0]'),
        'frame_geometry': _rect(dialog.frameGeometry()),
        'normal_geometry': _rect(dialog.normalGeometry()),
        'client_size': _size(dialog.size()),
        'screen': None,
    }
    if screen is not None:
        out['screen'] = {
            'available_geometry': _rect(screen.availableGeometry()),
            'full_geometry': _rect(screen.geometry()),
            'device_pixel_ratio': float(screen.devicePixelRatio()),
            'logical_dpi': float(screen.logicalDotsPerInch()),
            'physical_dpi': float(screen.physicalDotsPerInch()),
        }
    return out


def collect_pause_geometry(dialog, *, screenshot_folder=None):
    """Coleta todas as abas; restaura a aba original mesmo em caso de falha."""
    from PySide6.QtWidgets import QApplication
    tabs = dialog.tabs
    initial_tab = tabs.currentIndex()
    snapshot = {
        'format': _FORMAT,
        'captured_utc': datetime.now(timezone.utc).isoformat(),
        'measurement_units': 'pixels lógicos Qt (não pixels físicos do PNG)',
        'privacy': 'JSON/TXT contêm apenas geometria, nomes de classes e métricas de texto; PNGs contêm a interface visível.',
        'code_declared_default_window': {'width': 1050, 'height': 780},
        'code_declared_minimum_window': {'width': 900, 'height': 650},
        'dialog': _dialog_state(dialog),
        'initial_tab': int(initial_tab),
        'common_widgets': _tree(dialog, dialog),
        'tab_bar': _tab_state(tabs),
        'game_tabs': [],
    }
    try:
        for i in range(tabs.count()):
            tabs.setCurrentIndex(i)
            QApplication.processEvents()
            QApplication.processEvents()
            page = tabs.widget(i)
            item = {
                'index': i, 'title': str(tabs.tabText(i)),
                'tab_rect_in_bar': _rect(tabs.tabBar().tabRect(i)),
                'page_widget': _measure_widget(page, dialog, f'game_tab[{i}]'),
                'widget_tree': _tree(page, dialog),
            }
            if screenshot_folder is not None:
                path = Path(screenshot_folder) / f'Pausa_Desafios_Aba_{i+1}.png'
                item['client_screenshot'] = path.name
                if not dialog.grab().save(str(path), 'PNG'):
                    item['screenshot_error'] = 'Qt não conseguiu gravar PNG'
            snapshot['game_tabs'].append(item)
    finally:
        tabs.setCurrentIndex(initial_tab)
        QApplication.processEvents()
    snapshot['after_restore_tab_index'] = int(tabs.currentIndex())
    return snapshot


def format_pause_summary(snapshot):
    d = snapshot['dialog']
    w = d['client_size']
    scr = d.get('screen') or {}
    lines = [
        'VIGHNASTUDY — PAUSA E DESAFIOS — MEDIDAS REAIS DO QT',
        'Formato: ' + snapshot['format'],
        'Data UTC: ' + snapshot['captured_utc'],
        '',
        'Todas as medidas abaixo são em pixels lógicos Qt.',
        f'Janela cliente: {w["width"]} x {w["height"]}',
        'Mínimo declarado no código: 900 x 650; tamanho inicial declarado: 1050 x 780.',
        f'Escala (devicePixelRatio): {scr.get("device_pixel_ratio", "indisponível")}',
        f'DPI lógico: {scr.get("logical_dpi", "indisponível")}',
        f'Área disponível da tela: {scr.get("available_geometry", "indisponível")}',
        '',
        'CONTÊINERES PRINCIPAIS',
    ]
    common = snapshot['common_widgets']['nodes']
    labels = ('pauseHubTitle', 'pauseHubSubtitle','pauseBackButton','pauseTimerPanel',
              'pauseTimerStatus','pauseTimerValue','pauseRecordsPanel',
              'pauseRecordCard','pauseRecordTitle','pauseRecordValue','pauseGamesTabs')
    for n in common:
        if n.get('object_name') in labels:
            rect = n['rect_in_dialog'] or n['geometry_in_parent']
            lines.append(f'{n["object_name"]:22s} | {n["class"]:16s} | '
                         f'x={rect["x"]:4d} y={rect["y"]:4d} '
                         f'w={rect["width"]:4d} h={rect["height"]:4d} '
                         f'| visível={n["visible"]}')
    lines.extend(['', 'ABAS DE JOGOS'])
    for tab in snapshot['game_tabs']:
        r = tab['page_widget']['rect_in_dialog'] or tab['page_widget']['geometry_in_parent']
        lines.append(f'Aba {tab["index"]+1}: {tab["title"]}; '
                     f'x={r["x"]}, y={r["y"]}, largura={r["width"]}, altura={r["height"]}; '
                     f'{tab["widget_tree"]["node_count"]} widgets catalogados.')
        clipped = [n for n in tab['widget_tree']['nodes'] if n.get('text_metrics',{}).get('possible_horizontal_clip')]
        if clipped:
            lines.append(f'  Alerta: {len(clipped)} textos potencialmente cortados na horizontal.')
    lines += [
        '',
        f'TOTAL DE WIDGETS (árvore da janela): {snapshot["common_widgets"]["node_count"]}',
        'JSON: contém todos os widgets, layouts, margens, espaçamentos, tamanhos mínimo/máximo/preferido,',
        'retângulos relativos/na janela/na tela, status e métricas de texto.',
        'As capturas PNG mostram apenas o conteúdo cliente do Qt, sem a borda nativa Windows.',
        'A coleta percorreu as cinco abas e restaurou a originalmente selecionada.',
        'Observação: widgets internos de abas ocultas são medidos com cada aba selecionada,',
        'mas conteúdos que dependem de iniciar uma partida podem aparecer em estado inicial.',
    ]
    return '\n'.join(lines) + '\n'


def export_pause_measurements(dialog, folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    snapshot = collect_pause_geometry(dialog, screenshot_folder=folder)
    (folder / 'Vighna_Pausa_Desafios_Dimensoes.json').write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (folder / 'Vighna_Pausa_Desafios_Resumo.txt').write_text(
        format_pause_summary(snapshot), encoding='utf-8')
    return folder, snapshot


def attach_pause_geometry_shortcut(dialog):
    """Instala comando único na janela Pausa, nunca interfere no Dashboard."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QKeySequence, QShortcut
    from PySide6.QtWidgets import QFileDialog, QMessageBox

    existing = getattr(dialog, '_pausa_geometry_shortcut', None)
    if existing is not None:
        return existing

    def exportar():
        if getattr(dialog, '_pausa_geometry_exportando', False):
            return
        parent = QFileDialog.getExistingDirectory(
            dialog, 'Escolher pasta para exportar todas as dimensões da Pausa e Desafios',
            str(Path.home()))
        if not parent:
            return
        foldername = 'Vighna_Pausa_Desafios_Dimensoes_' + datetime.now().strftime('%Y%m%d_%H%M%S')
        target = Path(parent) / foldername
        dialog._pausa_geometry_exportando = True
        try:
            path, snap = export_pause_measurements(dialog, target)
        except (OSError, RuntimeError, ValueError, TypeError, AttributeError) as exc:
            QMessageBox.warning(dialog, 'Geometria não exportada',
                                'Não foi possível concluir a coleta: ' + str(exc))
        else:
            QMessageBox.information(dialog, 'Medições exportadas',
                f'Geometria exportada para:\n{path}\n\n'
                f'{len(snap["game_tabs"])} abas medidas. Arquivos JSON, TXT e PNG.\n'
                'Nenhuma configuração ou dado do banco foi modificado.')
        finally:
            dialog._pausa_geometry_exportando = False

    shortcut = QShortcut(QKeySequence('Ctrl+Shift+F11'), dialog)
    shortcut.setContext(Qt.WindowShortcut)
    shortcut.activated.connect(exportar)
    dialog._pausa_geometry_shortcut = shortcut
    return shortcut
