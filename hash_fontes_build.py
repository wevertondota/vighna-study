"""Fingerprint determinístico das fontes usadas no build do VighnaStudy.

Serve apenas ao atualizar_exe.bat. Se qualquer fonte de produção mudar, o
cache local do PyInstaller é descartado antes do próximo build incremental.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXCLUIR_DIRETORIOS = {
    ".venv",
    "__pycache__",
    "build",
    "build_pyinstaller",
    "dist",
    "dist_nova",
    "checkpoints",
    "backups",
    "backups_codigo",
    "recuperacao_banco",
}
EXCLUIR_PREFIXOS_DIRETORIO = (
    "backup_codigo_pre_patch_",
    "backup_patch_",
)


def arquivo_de_producao(caminho: Path) -> bool:
    rel = caminho.relative_to(ROOT)
    if any(parte in EXCLUIR_DIRETORIOS for parte in rel.parts[:-1]):
        return False
    if any(
        parte.startswith(EXCLUIR_PREFIXOS_DIRETORIO)
        for parte in rel.parts[:-1]
    ):
        return False
    nome = caminho.name.lower()
    if nome.startswith(("test_", "benchmark_", "main_backup", "banco_backup")):
        return False
    if nome.endswith((".bak.py", ".bak")):
        return False
    return caminho.suffix.lower() == ".py"


def fingerprint() -> str:
    arquivos = [p for p in ROOT.rglob("*.py") if arquivo_de_producao(p)]
    for extra in (ROOT / "VighnaStudy.spec",):
        if extra.exists():
            arquivos.append(extra)

    digest = hashlib.sha256()
    for caminho in sorted(set(arquivos), key=lambda p: p.relative_to(ROOT).as_posix().lower()):
        rel = caminho.relative_to(ROOT).as_posix().encode("utf-8")
        dados = caminho.read_bytes()
        digest.update(len(rel).to_bytes(4, "big"))
        digest.update(rel)
        digest.update(len(dados).to_bytes(8, "big"))
        digest.update(dados)
    return digest.hexdigest()


if __name__ == "__main__":
    print(fingerprint())
