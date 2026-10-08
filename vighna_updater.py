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

from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QProgressBar, QPushButton, QMessageBox, QTextEdit)
from vighna_update_engine import UpdateError, inspect_package, install_package, recover_incomplete_updates


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


class UpdaterWindow(QMainWindow):
    def __init__(self, package, root, pid):
        super().__init__()
        self.setWindowTitle('VighnaStudy — Atualização segura')
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.resize(590, 370)
        self.setMinimumSize(490, 300)
        self.finished = False
        self.result = None
        surface = QWidget(self)
        self.setCentralWidget(surface)
        layout = QVBoxLayout(surface)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(13)
        title = QLabel('Atualizando o VighnaStudy')
        font = title.font()
        font.setPointSize(max(font.pointSize(), 16))
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        explanation = QLabel('Seus estudos e suas respostas ficam protegidos.\n'
                             'Você pode minimizar esta janela e continuar usando o computador.')
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        self.status = QLabel('Preparando verificação...')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.bar = QProgressBar()
        self.bar.setRange(0, 0)  # indeterminado: não inventar estimativas de progresso
        self.bar.setTextVisible(False)
        layout.addWidget(self.bar)
        self.stage = QLabel('Etapas: análise • backup • compilação • instalação • verificação')
        self.stage.setWordWrap(True)
        layout.addWidget(self.stage)
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setMaximumHeight(115)
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
        self.worker = UpdateThread(package, root, pid)
        self.worker.step.connect(self.on_step)
        self.worker.completed.connect(self.on_complete)
        self.worker.failed.connect(self.on_failure)
        QTimer.singleShot(100, self.worker.start)

    def on_step(self, percent, message):
        self.status.setText(message)
        self.logs.append(message)
        if percent >= 100:
            self.stage.setText('Todas as etapas concluídas.')
        elif percent >= 93:
            self.stage.setText('Verificando a instalação e os dados protegidos...')
        elif percent >= 82:
            self.stage.setText('Instalação do novo executável...')
        elif percent >= 38:
            self.stage.setText('Compilação em área isolada; você pode minimizar esta janela.')
        elif percent >= 14:
            self.stage.setText('Backup e preparação dos arquivos...')
        else:
            self.stage.setText('Verificando segurança e compatibilidade...')

    def on_complete(self, result):
        self.finished = True
        self.result = result
        self.bar.setRange(0, 1)
        self.bar.setValue(1)
        self.status.setText('Atualização instalada e verificada.')
        self.stage.setText('Backup de segurança: ' + result['backup'])
        self.reopen.setEnabled(True)
        self.done.setEnabled(True)
        self.logs.append('Concluído. O banco principal foi mantido e verificado.')
        # Reabertura automática após sucesso. A janela independente pode
        # continuar minimizada e ser fechada quando o usuário quiser.
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
        self.bar.setRange(0, 1)
        self.bar.setValue(0)
        self.status.setText('Atualização não concluída.')
        self.stage.setText('Verifique o motivo e o backup em backups/atualizacoes.')
        self.logs.append('ERRO: ' + message)
        self.done.setEnabled(True)
        QMessageBox.critical(self, 'Atualização interrompida', message)

    def closeEvent(self, event):
        if not self.finished:
            self.showMinimized()
            event.ignore()  # impedir interrupção de transação; botão X minimiza
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
        aplicar_tema(app, theme_row[0] if theme_row else 'claro')
    except (ImportError, OSError, sqlite3.Error, ValueError):
        pass  # em caso de indisponibilidade, janela nativa continua funcional
    window = UpdaterWindow(args.package, args.root, args.parent_pid)
    window.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
