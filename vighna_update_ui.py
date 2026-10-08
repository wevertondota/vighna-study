"""Entrada da Central de Atualizações, sem modificar banco ou preferências."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFileDialog, QMessageBox
from caminhos import PASTA_DADOS
from vighna_update_engine import UpdateError, inspect_package


def selecionar_e_autorizar(parent):
    root = Path(PASTA_DADOS).resolve()
    selected, _ = QFileDialog.getOpenFileName(parent, 'Selecionar pacote de atualização VighnaStudy',
                                               str(Path.home() / 'Downloads'), 'Pacote Vighna (*.zip)')
    if not selected:
        return False
    try:
        info = inspect_package(selected, root)
    except (UpdateError, OSError) as error:
        QMessageBox.warning(parent, 'Pacote não aceito', str(error))
        return False
    files = '\n'.join('  • ' + path for path in sorted(info['files']))
    summary = (f"Versão instalada: {info['base_version']} ({info['base_build']})\n"
               f"Versão proposta: {info['target_version']} ({info['target_build']})\n\n"
               f"Alterações: {info.get('description', '')}\n\n"
               f"Arquivos de código: \n{files}\n\n"
               "Proteção obrigatória: backup SQLite, conferência de integridade e "
               "bloqueio de mudanças no schema.\n\n"
               "ATENÇÃO: o SHA-256 verifica os arquivos do ZIP, mas NÃO comprova "
               "quem criou o pacote. Importe apenas pacotes de origem confiável.\n\n"
               "O aplicativo será fechado para compilar e instalar. Você poderá "
               "minimizar a janela de atualização.\n\n"
               "Deseja AUTORIZAR a instalação deste pacote?")
    answer = QMessageBox.question(parent, 'Autorizar atualização — VighnaStudy', summary,
                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    if answer != QMessageBox.Yes:
        return False
    updater_script = root / 'vighna_updater.py'
    venv = root / '.venv' / 'Scripts'
    pyw = venv / 'pythonw.exe'
    py = venv / 'python.exe'
    # O atualizador é outro processo; pythonw mantém a janela independente.
    # Para instalação originada da fonte no modo desenvolvedor, permite sys.executable.
    if not updater_script.is_file():
        QMessageBox.critical(parent, 'Atualizador indisponível', 'vighna_updater.py não encontrado.')
        return False
    if os.name == 'nt':
        executable = pyw if pyw.is_file() else py
    else:
        executable = Path(sys.executable)
    if not executable.is_file():
        QMessageBox.critical(parent, 'Atualizador indisponível',
                             'Ambiente Python do Vighna não foi encontrado. Nenhuma alteração foi feita.')
        return False
    args = [str(executable), str(updater_script), '--package', str(Path(selected).resolve()),
            '--root', str(root), '--parent-pid', str(os.getpid())]
    main_window = parent.parentWidget()
    if main_window is None:
        QMessageBox.critical(parent, "Erro de navegação", "Janela principal não identificada; atualização não iniciada.")
        return False
    try:
        subprocess.Popen(args, cwd=str(root),
                         creationflags=getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0))
    except OSError as exc:
        QMessageBox.critical(parent, 'Não foi possível abrir o atualizador', str(exc))
        return False
    # A janela principal conserva sua rotina de encerramento: sessões/Foco podem
    # exigir confirmação e backup, e o atualizador espera o processo terminar.
    parent.accept()
    QTimer.singleShot(100, main_window.close)
    return True
