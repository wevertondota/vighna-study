"""Entrada da Central de Atualizações, sem modificar banco ou preferências."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFileDialog, QMessageBox
from caminhos import PASTA_DADOS
from vighna_update_engine import UpdateError, inspect_package, package_usage




def _show_package_status(parent, message, full_message=None):
    label = getattr(parent, 'status_verificacao_zip', None)
    if label is not None:
        label.setText(message)
        label.setToolTip(full_message or message)


def _status_text(usage):
    state = usage['state']
    last = usage['record'] or {}
    date = last.get('date', '')
    when = f' • registro: {date}' if date else ''
    fingerprint = usage['sha256'][:12]
    label = {
        'installed_exact': 'JÁ INSTALADO — ZIP idêntico encontrado no histórico',
        'installed_current': 'JÁ INSTALADO — este é o build atualmente em uso',
        'installed_build': 'BUILD JÁ INSTALADO — conteúdo do ZIP não confirmado como idêntico',
        'failed': 'TENTATIVA ANTERIOR FALHOU — ainda não consta como instalado',
        'incomplete': 'TENTATIVA ANTERIOR SEM CONCLUSÃO — verifique antes de repetir',
        'legacy_attempt': 'JÁ SELECIONADO/ENVIADO ANTES — histórico antigo, ZIP não verificável',
        'new': 'PACOTE NOVO — nenhuma instalação anterior encontrada',
    }[state]
    return f'{label}{when} • SHA-256: {fingerprint}…'



def selecionar_e_autorizar(parent):
    root = Path(PASTA_DADOS).resolve()
    selected, _ = QFileDialog.getOpenFileName(parent, 'Selecionar pacote de atualização VighnaStudy',
                                               str(Path.home() / 'Downloads'), 'Pacote Vighna (*.zip)')
    if not selected:
        return False
    try:
        usage = package_usage(selected, root)
    except (UpdateError, OSError) as error:
        _show_package_status(parent, 'ZIP NÃO ACEITO — ' + str(error))
        QMessageBox.warning(parent, 'Pacote não aceito', str(error))
        return False
    status_text = _status_text(usage)
    _show_package_status(parent, status_text, usage['sha256'])
    if usage['state'] in ('installed_exact', 'installed_current', 'installed_build'):
        QMessageBox.information(
            parent, 'Atualização já utilizada — instalação evitada',
            f'{status_text}\n\nArquivo: {Path(selected).name}\n'
            f'Build: {usage["manifest"]["target_build"]}\n\n'
            'Nenhuma instalação será iniciada. Consulte o histórico de atualizações '
            'para conferir as instalações anteriores.')
        return False
    if usage['state'] == 'incomplete':
        QMessageBox.warning(
            parent, 'Tentativa anterior sem confirmação',
            f'{status_text}\n\nHá uma execução iniciada para este ZIP sem resultado final '
            'registrado. Verifique se o atualizador ainda está trabalhando ou se '
            'houve interrupção, antes de tentar novamente.')
        return False
    try:
        info = inspect_package(selected, root)
    except (UpdateError, OSError) as error:
        _show_package_status(parent, status_text + ' • NÃO COMPATÍVEL COM O BUILD ATUAL')
        QMessageBox.warning(parent, 'Pacote não aceito', str(error))
        return False
    files = '\n'.join('  • ' + path for path in sorted(info['files']))
    summary = (f"Situação do ZIP: {status_text}\n\n"
               f"Versão instalada: {info['base_version']} ({info['base_build']})\n"
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
