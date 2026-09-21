"""Caminhos persistentes do VighnaStudy.

O banco do usuário deve ter uma única origem, independentemente de o Vighna
ser executado por ``python main.py`` ou pelo executável em ``dist``.
"""
from __future__ import annotations

import sys
from pathlib import Path


def _parece_raiz_projeto(pasta: Path) -> bool:
    return (
        (pasta / "main.py").is_file()
        and (pasta / "VighnaStudy.spec").is_file()
    )


def _candidatos_origem() -> list[Path]:
    candidatos: list[Path] = []

    try:
        candidatos.append(Path.cwd())
    except OSError:
        pass

    try:
        candidatos.append(Path(__file__).resolve().parent)
    except OSError:
        pass

    if getattr(sys, "frozen", False):
        try:
            candidatos.append(Path(sys.executable).resolve().parent)
        except OSError:
            pass

    return candidatos


def localizar_pasta_dados() -> Path:
    """Retorna a raiz que contém o ``estudos.db`` autoritativo.

    Em desenvolvimento, normalmente é a pasta do código. No executável
    ``C:\\SistemaEstudos\\dist\\SistemaEstudos\\VighnaStudy.exe``, percorre
    os ancestrais até encontrar a raiz do projeto. Assim Python e EXE leem e
    gravam exatamente o mesmo banco.
    """
    vistos: set[Path] = set()

    for origem in _candidatos_origem():
        try:
            atual = origem.resolve()
        except OSError:
            continue

        for candidato in (atual, *atual.parents):
            if candidato in vistos:
                continue
            vistos.add(candidato)
            if _parece_raiz_projeto(candidato):
                return candidato

    # Fallback conservador para uma distribuição realmente independente.
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


PASTA_DADOS = localizar_pasta_dados()
CAMINHO_BANCO = PASTA_DADOS / "estudos.db"
PASTA_BACKUPS = PASTA_DADOS / "backups"
