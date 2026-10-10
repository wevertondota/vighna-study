"""Janela independente e minimizável do atualizador do VighnaStudy.

Executada com pythonw.exe da .venv após autorização explícita no aplicativo.
Não compartilha o processo principal; não fecha a janela ao minimizá-la.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import sqlite3
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal, QTimer, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient, QPainterPath, QBrush
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QProgressBar, QPushButton, QMessageBox, QTextEdit, QFrame, QScrollArea)
from vighna_update_engine import UpdateError, inspect_package, install_package, recover_incomplete_updates
from ui.updater_steps import PHASES, UpdatePhaseState


def wait_process_exit(pid: int, timeout=240):
    if pid < 1:
        raise UpdateError('Processo do Vighna inválido.')
    if os.name != 'nt':
        limit = time.monotonic() + timeout
        while time.monotonic() < limit:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return
            time.sleep(.5)
        raise UpdateError('O Vighna não terminou o encerramento no prazo.')
    # Espera pelo processo exato, sem recorrer à comparação insegura de nomes.
    import ctypes
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel32.OpenProcess.argtypes = (ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong)
    kernel32.OpenProcess.restype = ctypes.c_void_p
    kernel32.WaitForSingleObject.argtypes = (ctypes.c_void_p, ctypes.c_ulong)
    kernel32.WaitForSingleObject.restype = ctypes.c_ulong
    kernel32.CloseHandle.argtypes = (ctypes.c_void_p,)
    handle = kernel32.OpenProcess(0x00100000, 0, pid)  # SYNCHRONIZE
    if not handle:
        if ctypes.get_last_error() == 87:  # ERROR_INVALID_PARAMETER: PID já não existe
            return
        raise UpdateError('Não foi possível acompanhar o encerramento do Vighna.')
    try:
        result = kernel32.WaitForSingleObject(handle, int(timeout * 1000))
        if result != 0:  # WAIT_OBJECT_0
            raise UpdateError('O Vighna permanece aberto; atualização cancelada com segurança.')
    finally:
        kernel32.CloseHandle(handle)


def no_vighna_running():
    if os.name != 'nt':
        return
    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq VighnaStudy.exe', '/NH'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, errors='replace', timeout=10,
                            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if result.returncode != 0:
        raise UpdateError('Não foi possível conferir outros processos do Vighna.')
    if any(line.strip().lower().startswith('vighnastudy.exe ') for line in result.stdout.splitlines()):
        raise UpdateError('Ainda há uma instância do Vighna aberta. Feche-a antes de atualizar.')


class UpdateThread(QThread):
    step = Signal(int, str)
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, package, root, parent_pid):
        super().__init__()
        self.package = package
        self.root = Path(root)
        self.parent_pid = parent_pid

    def run(self):
        try:
            self.step.emit(0, 'Aguardando fechamento seguro do VighnaStudy...')
            wait_process_exit(self.parent_pid)
            no_vighna_running()
            previous = recover_incomplete_updates(self.root)
            if previous:
                self.step.emit(3, 'Interrupção anterior recuperada; prosseguindo com a nova verificação...')
            self.step.emit(5, 'Verificando novamente a atualização...')
            inspect_package(self.package, self.root)
            python_exe = self.root / '.venv' / 'Scripts' / 'python.exe'
            if not python_exe.is_file():
                raise UpdateError('Python da .venv não encontrado para a compilação. Nada foi instalado.')
            result = install_package(self.package, self.root, python_exe=python_exe,
                                     report=lambda p, message: self.step.emit(p, message))
            self.completed.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))



class FlowProgressBar(QProgressBar):
    """Barra de etapas reais com reflexo animado; nunca avança por tempo."""

    _SHINE_CYCLE = 240
    _SHINE_STEP = 4
    _SHINE_HALF_WIDTH = 120.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self._frame = 0
        self._running = True
        self.setFixedHeight(16)
        self.setTextVisible(False)

    def setRunning(self, enabled):
        self._running = bool(enabled)
        self.update()

    def animate(self):
        if self._running and self.isVisible():
            self._frame = (self._frame + self._SHINE_STEP) % self._SHINE_CYCLE
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        track = QRectF(1.0, 1.0, max(0.0, float(self.width() - 2)),
                       max(0.0, float(self.height() - 2)))
        radius = track.height() / 2.0
        dark = getattr(self, '_dark', True)
        track_path = QPainterPath()
        track_path.addRoundedRect(track, radius, radius)
        painter.fillPath(track_path, QBrush(QColor('#17283E' if dark else '#E5ECF5')))

        steps = max(1, self.maximum() - self.minimum())
        ratio = max(0.0, min(1.0, (self.value() - self.minimum()) / steps))
        fill_width = track.width() * ratio
        if fill_width >= 1.0:
            fill = QRectF(track.x(), track.y(), fill_width, track.height())
            painter.save()
            painter.setClipPath(track_path)
            painter.setClipRect(fill, Qt.IntersectClip)
            base = QLinearGradient(fill.left(), 0, fill.right(), 0)
            base.setColorAt(0.0, QColor('#2876C5'))
            base.setColorAt(0.55, QColor('#319FDD'))
            base.setColorAt(1.0, QColor('#40B9EA'))
            painter.fillRect(fill, QBrush(base))
            if self._running:
                # Reflexo mais legível e mais vivo, ainda sem alterar o valor real do progresso.
                sweep = -self._SHINE_HALF_WIDTH + (
                    self._frame / float(self._SHINE_CYCLE)
                ) * (fill_width + self._SHINE_HALF_WIDTH * 2.0)
                shine = QLinearGradient(
                    sweep - self._SHINE_HALF_WIDTH,
                    0,
                    sweep + self._SHINE_HALF_WIDTH,
                    0,
                )
                shine.setColorAt(0.00, QColor(255, 255, 255, 0))
                shine.setColorAt(0.34, QColor(255, 255, 255, 0))
                shine.setColorAt(0.47, QColor(255, 255, 255, 92))
                shine.setColorAt(0.50, QColor(255, 255, 255, 176))
                shine.setColorAt(0.53, QColor(255, 255, 255, 108))
                shine.setColorAt(0.66, QColor(255, 255, 255, 0))
                shine.setColorAt(1.00, QColor(255, 255, 255, 0))
                painter.fillRect(fill, QBrush(shine))
            painter.restore()
        painter.setPen(QPen(QColor('#315573' if dark else '#BACBDD'), 1.0))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(track_path)
        painter.end()

class UpdaterWindow(QMainWindow):
    """Janela de atualização com linha do tempo; a transação não é modificada."""

    _COLORS = {
        'claro': {
            'pending': ('#F8FAFC', '#CBD5E1', '#64748B'),
            'active': ('#E7F3FF', '#299AD7', '#163E69'),
            'done': ('#F0FDF4', '#86EFAC', '#166534'),
            'error': ('#FEF2F2', '#FCA5A5', '#991B1B'),
        },
        'escuro': {
            'pending': ('#122237', '#31465F', '#A7BBD0'),
            'active': ('#102E49', '#35A9EA', '#EFF9FF'),
            'done': ('#112D2B', '#256E5B', '#D8FFF2'),
            'error': ('#3B1B27', '#FB7185', '#FFE4E6'),
        },
    }
    _GLYPHS = {'pending': '○', 'active': '●', 'done': '✓', 'error': '!'}

    def __init__(self, package, root, pid, theme='claro'):
        super().__init__()
        self.setWindowTitle('VighnaStudy — Atualização segura')
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.resize(744, 706)
        self.setMinimumSize(620, 540)
        self.finished = False
        self.result = None
        self.phase_state = UpdatePhaseState()
        self._is_dark = str(theme).lower() in ('escuro', 'futurista')
        self._theme_colors = self._COLORS['escuro' if self._is_dark else 'claro']
        self._motion_frame = 0
        self._phase_started = time.monotonic()
        self._last_display_second = -1
        self._shown_phase = 0
        self._centered_once = False

        surface = QWidget(self)
        self.setCentralWidget(surface)
        layout = QVBoxLayout(surface)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(9)

        title = QLabel('Atualizando o VighnaStudy')
        font = title.font()
        font.setPointSize(max(font.pointSize(), 16))
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        explanation = QLabel('Seus estudos e suas respostas ficam protegidos. '
                             'Você pode minimizar a janela durante a atualização.')
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        status_row = QHBoxLayout()
        self.phase_count = QLabel('0 de 9 etapas concluídas')
        self.phase_count.setAccessibleName('Quantidade de etapas concluídas')
        status_row.addWidget(self.phase_count)
        status_row.addStretch(1)
        self.live_activity = QLabel('● Em andamento')
        self.live_activity.setObjectName('vighnaUpdaterLiveActivity')
        self.live_activity.setAccessibleName('Atividade da atualização')
        status_row.addWidget(self.live_activity)
        layout.addLayout(status_row)
        self.bar = FlowProgressBar()
        self.bar._dark = self._is_dark
        self.bar.setRange(0, len(PHASES))
        self.bar.setValue(0)
        # Fração estritamente de etapas concluídas; brilho não modifica o valor.
        self.bar.setAccessibleName('Etapas concluídas da atualização')
        layout.addWidget(self.bar)

        self.status = QLabel('Preparando verificação...')
        self.status.setWordWrap(True)
        self.status.setAccessibleName('Operação atual do atualizador')
        layout.addWidget(self.status)

        self.steps_header = QLabel('Etapas da atualização')
        self.steps_header.setObjectName('vighnaUpdaterStepsHeader')
        header_font = self.steps_header.font()
        header_font.setPointSize(max(header_font.pointSize(), 13))
        header_font.setBold(True)
        self.steps_header.setFont(header_font)
        layout.addWidget(self.steps_header)

        self.step_scroll = QScrollArea()
        self.step_scroll.setWidgetResizable(True)
        self.step_scroll.setFrameShape(QFrame.NoFrame)
        self.step_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        container = QWidget()
        self.step_layout = QVBoxLayout(container)
        self.step_layout.setContentsMargins(0, 2, 0, 2)
        self.step_layout.setSpacing(5)
        self.step_panels = []
        self.step_marks = []
        self.step_titles = []
        self.step_badges = []
        for phase in PHASES:
            panel = QFrame()
            line = QHBoxLayout(panel)
            line.setContentsMargins(13, 7, 13, 7)
            line.setSpacing(11)
            mark = QLabel()
            mark.setFixedWidth(30)
            mark.setAlignment(Qt.AlignCenter)
            line.addWidget(mark)
            text_column = QVBoxLayout()
            text_column.setSpacing(2)
            label = QLabel(phase.name)
            text_column.addWidget(label)
            detail = QLabel(phase.detail)
            detail.setWordWrap(True)
            detail.setObjectName('vighnaUpdatePhaseDetail')
            detail.setStyleSheet('font-size: 11px;')
            text_column.addWidget(detail)
            line.addLayout(text_column, 1)
            badge = QLabel('Pendente')
            badge.setObjectName('vighnaUpdaterPhaseBadge')
            badge.setFixedWidth(108)
            badge.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            line.addWidget(badge)
            self.step_badges.append(badge)
            self.step_layout.addWidget(panel)
            self.step_panels.append(panel)
            self.step_marks.append(mark)
            self.step_titles.append((label, detail))
        self.step_layout.addStretch(1)
        self.step_scroll.setWidget(container)
        layout.addWidget(self.step_scroll, 1)

        self.backup_note = QLabel('')
        self.backup_note.setWordWrap(True)
        self.backup_note.setVisible(False)
        layout.addWidget(self.backup_note)

        self.details_button = QPushButton('Ver detalhes técnicos ▾')
        self.details_button.setCheckable(True)
        self.details_button.setChecked(False)
        self.details_button.toggled.connect(self.toggle_details)
        layout.addWidget(self.details_button)
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setMinimumHeight(105)
        self.logs.setMaximumHeight(155)
        self.logs.setVisible(False)
        self.logs.setAccessibleName('Registro técnico da atualização')
        layout.addWidget(self.logs)

        buttons = QHBoxLayout()
        self.minimize = QPushButton('Minimizar')
        self.minimize.clicked.connect(self.showMinimized)
        buttons.addWidget(self.minimize)
        buttons.addStretch(1)
        self.reopen = QPushButton('Abrir o Vighna')
        self.reopen.setEnabled(False)
        self.reopen.clicked.connect(self.launch_app)
        buttons.addWidget(self.reopen)
        self.done = QPushButton('Fechar')
        self.done.setEnabled(False)
        self.done.clicked.connect(self.close)
        buttons.addWidget(self.done)
        layout.addLayout(buttons)
        self._apply_visual_style()
        self._render_phases()
        # Qt agenda repinturas leves enquanto o worker executa em QThread.
        self.motion_timer = QTimer(self)
        self.motion_timer.setInterval(50)
        self.motion_timer.timeout.connect(self._animate_activity)
        self.motion_timer.start()

        self.worker = UpdateThread(package, root, pid)
        self.worker.step.connect(self.on_step)
        self.worker.completed.connect(self.on_complete)
        self.worker.failed.connect(self.on_failure)
        QTimer.singleShot(100, self.worker.start)

    def _apply_visual_style(self):
        """Estilo local à janela; não modifica o tema global do programa."""
        if self._is_dark:
            bg, text, secondary, border = '#071526', '#F3F7FD', '#A7BBD1', '#294664'
            card, hover, muted = '#102238', '#142D47', '#93A8BE'
        else:
            bg, text, secondary, border = '#F7FAFF', '#14253B', '#536B86', '#B9CADC'
            card, hover, muted = '#FFFFFF', '#EAF3FD', '#526B83'
        self.setStyleSheet(f"""
            QMainWindow, QMainWindow > QWidget {{ background-color: {bg}; color: {text}; }}
            QLabel {{ color: {text}; background: transparent; }}
            QScrollArea {{ border: none; background: transparent; }}
            QTextEdit {{ color: {text}; background-color: {card}; border: 1px solid {border};
                         border-radius: 10px; padding: 8px; }}
            QPushButton {{ color: {text}; background-color: {card}; border: 1px solid {border};
                           border-radius: 9px; padding: 9px 15px; min-height: 19px; }}
            QPushButton:hover:!disabled {{ background-color: {hover}; border-color: #3C9FDA; }}
            QPushButton:disabled {{ color: {muted}; background-color: {bg}; }}
            QLabel#vighnaUpdaterLiveActivity {{ color: {'#7BD3FC' if self._is_dark else '#1266A7'};
                                                font-weight: 600; }}
            QLabel#vighnaUpdaterStepsHeader {{
                color: {'#E6F4FF' if self._is_dark else '#123D66'};
                font-weight: 700;
                letter-spacing: 0.4px;
                padding-top: 4px;
                padding-bottom: 3px;
                border-bottom: 1px solid {'#2E5578' if self._is_dark else '#C5D8EA'};
                margin-top: 4px;
            }}
            QPushButton#vighnaUpdaterDetails {{ background-color: {card}; }}
        """)
        self.details_button.setObjectName('vighnaUpdaterDetails')

    def _animate_activity(self):
        """Indica vida sem inventar percentual, duração total ou etapas futuras."""
        if self.finished or self.phase_state.failed:
            return
        self._motion_frame = (self._motion_frame + 1) % 180
        self.bar.animate()
        icons = ('◐', '◓', '◑', '◒')
        current = self.phase_state.current
        self.step_marks[current].setText(icons[(self._motion_frame // 4) % 4])
        elapsed_seconds = int(max(0.0, time.monotonic() - self._phase_started))
        if elapsed_seconds != self._last_display_second:
            self._last_display_second = elapsed_seconds
            self.live_activity.setText(f'● Em andamento · {elapsed_seconds // 60:02d}:{elapsed_seconds % 60:02d} nesta etapa')

    def _render_phases(self):
        state = self.phase_state
        completed = state.completed
        self.phase_count.setText(f'{completed} de {len(PHASES)} etapas concluídas')
        self.bar.setValue(completed)
        status_labels = {'done': 'Concluído', 'active': 'Em andamento',
                         'pending': 'Pendente', 'error': 'Erro'}
        for index, (panel, mark, (label, detail)) in enumerate(
                zip(self.step_panels, self.step_marks, self.step_titles)):
            state_name = state.state_at(index)
            surface, border, ink = self._theme_colors[state_name]
            accent = {'active':'#38BDF8', 'done':'#34D399',
                      'pending':'#64748B', 'error':'#FB7185'}[state_name]
            # Destacar a ação em execução, mas manter concluídas e futuras legíveis.
            outline = '2px' if state_name == 'active' else '1px'
            panel.setStyleSheet('QFrame { background-color: ' + surface +
                                '; border: ' + outline + ' solid ' + border +
                                '; border-radius: 10px; }'
                                'QLabel { border: none; background: transparent; color: ' + ink + '; }')
            mark.setText(self._GLYPHS[state_name])
            mark_size = '23px' if state_name == 'active' else '18px'
            mark.setStyleSheet('font-size: ' + mark_size + '; font-weight: 700; color: ' + accent + ';')
            mark.setToolTip(status_labels[state_name])
            if hasattr(self, 'step_badges'):
                badge = self.step_badges[index]
                badge.setText(status_labels[state_name])
                badge.setStyleSheet('font-size: 11px; color: ' + ink +
                                    '; font-weight: ' + ('700' if state_name == 'active' else '500') + ';')
            label.setText(PHASES[index].name)
            detail.setText(PHASES[index].detail)
            label.setAccessibleName(PHASES[index].name + ' — ' +
                                    {'done':'concluído', 'active':'em andamento',
                                     'pending':'pendente', 'error':'erro'}[state_name])
        if not state.finished and not state.failed:
            self.step_scroll.ensureWidgetVisible(self.step_panels[state.current])

    def toggle_details(self, expanded):
        self.logs.setVisible(expanded)
        self.details_button.setText('Ocultar detalhes técnicos ▴' if expanded
                                    else 'Ver detalhes técnicos ▾')

    def showEvent(self, event):
        super().showEvent(event)
        if not self._centered_once:
            self._centered_once = True
            QTimer.singleShot(0, self._center_window_on_screen)

    def _center_window_on_screen(self):
        screen = self.screen() or QApplication.primaryScreen()
        if not screen:
            return
        available = screen.availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(available.center())
        top_left = frame.topLeft()
        if top_left.x() < available.left():
            top_left.setX(available.left())
        if top_left.y() < available.top():
            top_left.setY(available.top())
        self.move(top_left)

    def on_step(self, percent, message):
        if self.finished:
            return
        self.status.setText(message)
        self.logs.append(message)
        previous_phase = self.phase_state.current
        self.phase_state.observe(percent, message)
        if self.phase_state.current != previous_phase:
            self._phase_started = time.monotonic()
            self._last_display_second = -1
        self._render_phases()

    def on_complete(self, result):
        self.finished = True
        self.result = result
        self.phase_state.succeed()
        if hasattr(self, 'motion_timer'):
            self.motion_timer.stop()
        self.bar.setRunning(False) if hasattr(self.bar, 'setRunning') else None
        if hasattr(self, 'live_activity'):
            self.live_activity.setText('✓ Atualização concluída')
        self._render_phases()
        self.status.setText('Atualização instalada e verificada.')
        backup = str(result.get('backup', ''))
        self.backup_note.setText('Backup de segurança: ' + backup)
        self.backup_note.setToolTip(backup)
        self.backup_note.setVisible(bool(backup))
        self.reopen.setEnabled(True)
        self.done.setEnabled(True)
        self.logs.append('Concluído. O banco principal foi mantido e verificado.')
        # Mesmo comportamento prévio: reabertura automática após sucesso.
        self.launch_app()

    def launch_app(self):
        if not self.result:
            return
        target = Path(self.result['executable'])
        try:
            subprocess.Popen([str(target)], cwd=str(target.parent),
                             creationflags=getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0))
            self.reopen.setEnabled(False)
            self.logs.append('VighnaStudy aberto pelo executável atualizado.')
        except OSError as exc:
            self.logs.append('Não foi possível reabrir automaticamente: ' + str(exc))

    def on_failure(self, message):
        self.finished = True
        self.phase_state.fail()
        if hasattr(self, 'motion_timer'):
            self.motion_timer.stop()
        self.bar.setRunning(False) if hasattr(self.bar, 'setRunning') else None
        if hasattr(self, 'live_activity'):
            self.live_activity.setText('! Atualização interrompida')
        self._render_phases()
        self.status.setText('Atualização não concluída. Verifique os detalhes técnicos.')
        self.backup_note.setText('Se um backup foi iniciado, consulte backups/atualizacoes.')
        self.backup_note.setVisible(True)
        self.logs.append('ERRO: ' + message)
        self.details_button.setChecked(True)  # Expõe a causa, sem ocultá-la no resumo.
        self.done.setEnabled(True)
        QMessageBox.critical(self, 'Atualização interrompida', message)

    def closeEvent(self, event):
        if not self.finished:
            self.showMinimized()
            event.ignore()  # impedir interrupção de transação; X minimiza
            return
        super().closeEvent(event)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', required=True)
    parser.add_argument('--root', required=True)
    parser.add_argument('--parent-pid', type=int, required=True)
    args = parser.parse_args()
    app = QApplication(sys.argv)
    # Reutiliza o tema gravado pelo Vighna, sem alterar o banco e sem
    # depender da execução do aplicativo principal.
    try:
        db = Path(args.root) / 'estudos.db'
        con = sqlite3.connect(db.resolve().as_uri() + '?mode=ro', uri=True, timeout=3)
        try:
            theme_row = con.execute(
                'SELECT valor FROM configuracoes WHERE chave=?', ('tema_interface',)
            ).fetchone()
        finally:
            con.close()
        from tema import aplicar_tema
        current_theme = aplicar_tema(app, theme_row[0] if theme_row else 'claro')
    except (ImportError, OSError, sqlite3.Error, ValueError):
        pass  # em caso de indisponibilidade, janela nativa continua funcional
    window = UpdaterWindow(args.package, args.root, args.parent_pid,
                           theme=locals().get('current_theme', 'claro'))
    window.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
