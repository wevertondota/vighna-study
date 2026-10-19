"""Entrada da Central de Atualizações, sem modificar banco ou preferências."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QApplication, QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout, QLabel,
    QMessageBox, QPlainTextEdit, QPushButton, QVBoxLayout,
)
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



def _texto_resumido(valor, limite=180):
    """Exibe apenas um resumo; o texto integral permanece nos detalhes."""
    valor = " ".join(str(valor or "").split())
    if len(valor) <= limite:
        return valor
    return valor[:limite - 1].rstrip() + "…"


def _confirmar_instalacao(parent, info, status_text, pacote):
    """Autorização explícita, sem depender da altura de um QMessageBox.

    O identificador técnico nunca é apresentado inteiro em um QLabel:
    toda a informação integral permanece copiável no painel rolável.
    """
    dialogo = QDialog(parent)
    dialogo.setObjectName("vighnaUpdateAuthorizationDialog")
    dialogo.setWindowTitle("Autorizar atualização — VighnaStudy")
    dialogo.setSizeGripEnabled(True)
    # Limite relativo ao monitor: nenhuma linha longa pode deslocar o rodapé.
    tela = parent.screen() if parent is not None and hasattr(parent, "screen") else None
    if tela is None:
        tela = QApplication.primaryScreen()
    area = tela.availableGeometry() if tela is not None else None
    largura = min(720, max(340, area.width() - 60)) if area is not None else 720
    altura = min(490, max(320, area.height() - 70)) if area is not None else 490
    dialogo.resize(largura, altura)

    layout = QVBoxLayout(dialogo)
    layout.setContentsMargins(20, 17, 20, 16)
    layout.setSpacing(11)

    titulo = QLabel("Confirmar atualização do VighnaStudy", dialogo)
    titulo.setObjectName("updateAuthorizationTitle")
    fonte = titulo.font()
    fonte.setPointSize(max(12, fonte.pointSize() + 2))
    fonte.setBold(True)
    titulo.setFont(fonte)
    layout.addWidget(titulo)

    status = QLabel(_texto_resumido(status_text, 140), dialogo)
    status.setWordWrap(True)
    status.setToolTip(status_text)
    layout.addWidget(status)

    nome_pacote = QLabel("Pacote: " + _texto_resumido(Path(pacote).name, 110), dialogo)
    nome_pacote.setWordWrap(True)
    nome_pacote.setToolTip(str(pacote))
    layout.addWidget(nome_pacote)

    versoes = QLabel(
        f"Versão instalada: {info['base_version']}    →    "
        f"Versão proposta: {info['target_version']}", dialogo,
    )
    versoes.setWordWrap(True)
    layout.addWidget(versoes)

    descricao = QLabel(_texto_resumido(info.get('description', ''), 240), dialogo)
    descricao.setWordWrap(True)
    layout.addWidget(descricao)

    detalhes_texto = (
        f"Pacote: {Path(pacote).name}\n"
        f"Situação do ZIP: {status_text}\n\n"
        f"Versão instalada: {info['base_version']}\n"
        f"Build instalado: {info['base_build']}\n\n"
        f"Versão proposta: {info['target_version']}\n"
        f"Build proposto: {info['target_build']}\n\n"
        f"Alterações: {info.get('description', '')}\n\n"
        "Arquivos de código:\n" +
        "\n".join("  • " + caminho for caminho in sorted(info['files']))
        + "\n\n"
        "Proteção obrigatória: backup SQLite, conferência de integridade "
        "e bloqueio de mudanças no schema.\n"
    )

    linha = QHBoxLayout()
    expandir = QPushButton("Mostrar detalhes técnicos ▾", dialogo)
    expandir.setCheckable(True)
    expandir.setToolTip("Consultar o build completo, os arquivos e a origem da atualização")
    linha.addWidget(expandir)
    copiar = QPushButton("Copiar informações", dialogo)
    copiar.setToolTip("Copiar os identificadores e a lista completa de arquivos")
    copiar.clicked.connect(lambda: QApplication.clipboard().setText(detalhes_texto))
    linha.addWidget(copiar)
    linha.addStretch(1)
    layout.addLayout(linha)

    detalhes = QPlainTextEdit(dialogo)
    detalhes.setObjectName("updateAuthorizationDetails")
    detalhes.setReadOnly(True)
    detalhes.setLineWrapMode(QPlainTextEdit.WidgetWidth)
    detalhes.setPlainText(detalhes_texto)
    detalhes.setMinimumHeight(120)
    detalhes.setVisible(False)
    layout.addWidget(detalhes, 1)

    def alternar_detalhes(ativo):
        detalhes.setVisible(ativo)
        expandir.setText("Ocultar detalhes técnicos ▴" if ativo else "Mostrar detalhes técnicos ▾")

    expandir.toggled.connect(alternar_detalhes)
    layout.addStretch(1)

    aviso = QLabel(
        "Proteções: backup SQLite, verificação de integridade e esquema preservado. "
        "A instalação fechará o aplicativo após sua autorização. "
        "O SHA-256 verifica os arquivos do ZIP, mas não a identidade de quem o criou. "
        "Instale apenas pacotes de origem confiável.", dialogo,
    )
    aviso.setWordWrap(True)
    aviso.setObjectName("updateAuthorizationSafetyNote")
    layout.addWidget(aviso)

    botoes = QDialogButtonBox(dialogo)
    autorizar = botoes.addButton("Autorizar instalação", QDialogButtonBox.YesRole)
    cancelar = botoes.addButton("Cancelar", QDialogButtonBox.RejectRole)
    autorizar.setObjectName("updateAuthorizationConfirmButton")
    cancelar.setObjectName("updateAuthorizationCancelButton")
    autorizar.setAutoDefault(False)
    cancelar.setDefault(True)
    autorizar.clicked.connect(dialogo.accept)
    cancelar.clicked.connect(dialogo.reject)
    layout.addWidget(botoes)
    return dialogo.exec() == QDialog.Accepted


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
    if not _confirmar_instalacao(parent, info, status_text, selected):
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
