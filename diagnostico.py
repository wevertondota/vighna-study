"""Diagnóstico técnico e manutenção segura do VighnaStudy."""

from __future__ import annotations

import platform
import sys
from pathlib import Path

import PySide6
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from banco import CAMINHO_BANCO, conectar
from backup import listar_backups
from checkpoint import obter_ultimo_checkpoint, localizar_pasta_projeto
from versao import VIGHNA_BUILD, VIGHNA_SCHEMA, VIGHNA_VERSION
from auditoria_ciclo_estudo import auditar_ciclo_estudo, texto_auditoria_ciclo, texto_recomendacao_diagnostica


def coletar_diagnostico() -> dict:
    banco = Path(CAMINHO_BANCO)
    resultado = {
        "versao": VIGHNA_VERSION,
        "build": VIGHNA_BUILD,
        "schema_app": VIGHNA_SCHEMA,
        "python": platform.python_version(),
        "pyside": getattr(PySide6, "__version__", "—"),
        "modo_execucao": "EXE compilado" if getattr(sys, "frozen", False) else "Python / fontes",
        "pasta_projeto": str(localizar_pasta_projeto()),
        "banco": str(banco),
        "banco_existe": banco.is_file(),
        "banco_tamanho": banco.stat().st_size if banco.is_file() else 0,
        "integridade": "não verificada",
        "journal_mode": "—",
        "indices": 0,
        "tabelas": 0,
        "freelist": 0,
        "paginas": 0,
        "questoes_fisicas": 0,
        "questoes_ativas": 0,
        "questoes_excluidas": 0,
        "dignidade_sexual_ativas": 0,
        "banco_legado_dist": None,
        "ultimo_checkpoint": None,
        "ultimo_backup": None,
    }

    if banco.is_file():
        with conectar() as conexao:
            integ = conexao.execute("PRAGMA integrity_check").fetchone()
            resultado["integridade"] = str(integ[0]) if integ else "sem resposta"
            jm = conexao.execute("PRAGMA journal_mode").fetchone()
            resultado["journal_mode"] = str(jm[0]) if jm else "—"
            resultado["indices"] = int(conexao.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
            ).fetchone()[0] or 0)
            resultado["tabelas"] = int(conexao.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ).fetchone()[0] or 0)
            resultado["freelist"] = int(conexao.execute("PRAGMA freelist_count").fetchone()[0] or 0)
            resultado["paginas"] = int(conexao.execute("PRAGMA page_count").fetchone()[0] or 0)
            tabelas = {
                str(linha[0])
                for linha in conexao.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            if "questoes" in tabelas:
                resultado["questoes_fisicas"] = int(conexao.execute(
                    "SELECT COUNT(*) FROM questoes"
                ).fetchone()[0] or 0)
                resultado["questoes_ativas"] = int(conexao.execute(
                    "SELECT COUNT(*) FROM questoes WHERE ativa=1 AND COALESCE(excluida,0)=0"
                ).fetchone()[0] or 0)
                resultado["questoes_excluidas"] = int(conexao.execute(
                    "SELECT COUNT(*) FROM questoes WHERE COALESCE(excluida,0)=1"
                ).fetchone()[0] or 0)
                if "topicos" in tabelas:
                    resultado["dignidade_sexual_ativas"] = int(conexao.execute(
                        """
                        SELECT COUNT(*)
                        FROM questoes q
                        JOIN topicos t ON t.id=q.topico_id
                        WHERE q.ativa=1
                          AND COALESCE(q.excluida,0)=0
                          AND UPPER(t.nome) LIKE '%DIGNIDADE SEXUAL%'
                        """
                    ).fetchone()[0] or 0)

    try:
        raiz = Path(resultado["pasta_projeto"])
        legado = raiz / "dist" / "SistemaEstudos" / "estudos.db"
        if legado.is_file() and legado.resolve() != banco.resolve():
            resultado["banco_legado_dist"] = str(legado)
    except Exception:
        pass

    try:
        ultimo = obter_ultimo_checkpoint()
        if ultimo:
            resultado["ultimo_checkpoint"] = {
                "nome": ultimo.get("nome"),
                "caminho": str(ultimo.get("caminho")),
                "tamanho": int(ultimo.get("tamanho_bytes") or 0),
                "data": ultimo.get("data_modificacao"),
            }
    except Exception:
        pass

    try:
        backups = listar_backups()
        if backups:
            ultimo_b = backups[0]
            resultado["ultimo_backup"] = {
                "nome": ultimo_b.get("nome"),
                "caminho": str(ultimo_b.get("caminho")),
                "tamanho": int(ultimo_b.get("tamanho") or 0),
                "data": ultimo_b.get("data_modificacao"),
                "motivo": ultimo_b.get("motivo"),
            }
    except Exception:
        pass
    return resultado


def otimizar_banco_seguro() -> dict:
    """Executa apenas PRAGMA optimize; não faz VACUUM nem reescreve dados."""
    with conectar() as conexao:
        conexao.execute("PRAGMA optimize")
        conexao.commit()
    return coletar_diagnostico()


def _formatar_bytes(valor):
    valor = int(valor or 0)
    if valor < 1024:
        return f"{valor} B"
    if valor < 1024 * 1024:
        return f"{valor / 1024:.1f} KB"
    return f"{valor / (1024 * 1024):.1f} MB"


def texto_diagnostico(dados: dict) -> str:
    ultimo = dados.get("ultimo_checkpoint") or {}
    ultimo_backup = dados.get("ultimo_backup") or {}
    paginas = int(dados.get("paginas") or 0)
    livres = int(dados.get("freelist") or 0)
    fragmentacao = (100.0 * livres / paginas) if paginas else 0.0
    linhas = [
        f"VighnaStudy {dados.get('versao')} ({dados.get('build')})",
        f"Modo: {dados.get('modo_execucao')}",
        f"Python: {dados.get('python')} • PySide6: {dados.get('pyside')}",
        "",
        f"Projeto: {dados.get('pasta_projeto')}",
        f"Banco ativo: {dados.get('banco')}",
        f"Tamanho do banco: {_formatar_bytes(dados.get('banco_tamanho'))}",
        f"Integridade SQLite: {dados.get('integridade')}",
        f"Journal mode: {dados.get('journal_mode')}",
        f"Tabelas: {dados.get('tabelas')} • Índices: {dados.get('indices')}",
        f"Páginas livres: {livres}/{paginas} ({fragmentacao:.1f}%)",
        "",
        f"Questões ativas: {int(dados.get('questoes_ativas') or 0)}",
        f"Questões físicas: {int(dados.get('questoes_fisicas') or 0)}",
        f"Questões na lixeira: {int(dados.get('questoes_excluidas') or 0)}",
        f"Dignidade Sexual — ativas: {int(dados.get('dignidade_sexual_ativas') or 0)}",
        "",
        "Último checkpoint: " + (
            f"{ultimo.get('nome')} • {_formatar_bytes(ultimo.get('tamanho'))}"
            if ultimo else "nenhum encontrado"
        ),
        "Último backup: " + (
            f"{ultimo_backup.get('nome')} • {_formatar_bytes(ultimo_backup.get('tamanho'))}"
            if ultimo_backup else "nenhum encontrado"
        ),
    ]
    if dados.get("banco_legado_dist"):
        linhas += [
            "",
            "ATENÇÃO: existe um estudos.db legado dentro de dist\\SistemaEstudos.",
            f"Cópia legada: {dados.get('banco_legado_dist')}",
            "O banco ativo continua sendo o indicado acima; a cópia em dist não deve ser usada.",
        ]
    if str(dados.get("integridade")).lower() != "ok":
        linhas += ["", "ATENÇÃO: a verificação de integridade do SQLite não retornou 'ok'."]
    return "\n".join(linhas)


class JanelaDiagnosticoVighna(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Diagnóstico — VighnaStudy {VIGHNA_VERSION}")
        self.resize(720, 560)
        self.setMinimumSize(620, 460)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        titulo = QLabel("Diagnóstico e desempenho")
        titulo.setObjectName("pageTitle")
        layout.addWidget(titulo)
        subtitulo = QLabel(
            "Confere a versão, o banco ativo, a integridade SQLite, os índices e o último checkpoint. "
            "A otimização segura usa apenas PRAGMA optimize e não apaga dados."
        )
        subtitulo.setObjectName("pageSubtitle")
        subtitulo.setWordWrap(True)
        layout.addWidget(subtitulo)

        self.texto = QTextEdit()
        self.texto.setReadOnly(True)
        layout.addWidget(self.texto, 1)

        botoes = QHBoxLayout()
        atualizar = QPushButton("Executar diagnóstico")
        atualizar.setObjectName("toolbarButton")
        atualizar.clicked.connect(self.atualizar)
        auditar_ciclo = QPushButton("Auditar ciclo de estudo")
        auditar_ciclo.setObjectName("toolbarButton")
        auditar_ciclo.setToolTip(
            "Verificar o ciclo recomendação → sessão → respostas → revisão → métricas."
        )
        auditar_ciclo.clicked.connect(self.auditar_ciclo)
        otimizar = QPushButton("Otimização segura")
        otimizar.setObjectName("primaryButton")
        otimizar.clicked.connect(self.otimizar)
        copiar = QPushButton("Copiar resumo")
        copiar.setObjectName("subtleButton")
        copiar.clicked.connect(self.copiar)
        fechar = QPushButton("Fechar")
        fechar.setObjectName("subtleButton")
        fechar.clicked.connect(self.accept)
        botoes.addWidget(atualizar)
        botoes.addWidget(auditar_ciclo)
        botoes.addWidget(otimizar)
        botoes.addWidget(copiar)
        botoes.addStretch(1)
        botoes.addWidget(fechar)
        layout.addLayout(botoes)
        self.atualizar()

    def atualizar(self):
        try:
            self.dados = coletar_diagnostico()
            self.texto.setPlainText(texto_diagnostico(self.dados))
        except Exception as erro:
            self.texto.setPlainText(f"Falha no diagnóstico:\n{erro}")


    def auditar_ciclo(self):
        try:
            dados = auditar_ciclo_estudo()
            partes = [texto_auditoria_ciclo(dados)]
            principal = self.parentWidget()
            if principal is not None and hasattr(principal, "montar_recomendacao_estudar_agora_v5"):
                try:
                    if hasattr(principal, "cache_analitico"):
                        principal.cache_analitico.invalidar()
                    recomendacao = principal.montar_recomendacao_estudar_agora_v5()
                    if hasattr(principal, "_enriquecer_recomendacao_com_bateria"):
                        recomendacao = principal._enriquecer_recomendacao_com_bateria(recomendacao)
                    partes.append(texto_recomendacao_diagnostica(recomendacao))
                except Exception as erro_recomendacao:
                    partes.append(
                        "RECOMENDAÇÃO ATUAL — MOTOR V5\n"
                        f"Não foi possível recalcular a recomendação: {erro_recomendacao}"
                    )
            self.texto.setPlainText("\n\n".join(partes))
        except Exception as erro:
            self.texto.setPlainText(f"Falha na auditoria do ciclo de estudo:\n{erro}")

    def otimizar(self):
        try:
            self.dados = otimizar_banco_seguro()
            self.texto.setPlainText(texto_diagnostico(self.dados))
            QMessageBox.information(self, "Otimização", "PRAGMA optimize executado com sucesso.")
        except Exception as erro:
            QMessageBox.critical(self, "Otimização", str(erro))

    def copiar(self):
        QApplication.clipboard().setText(self.texto.toPlainText())
