# -*- coding: utf-8 -*-
"""Lógica sem interface gráfica para o painel de homologação.

Não acessa o VighnaStudy instalado; apenas localiza resultados criados
pelo homologador portátil e cria diagnósticos da própria interface.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import zipfile

APP_ROOT = Path(__file__).resolve().parent
# Recursos empacotados sao SOMENTE LEITURA. Configuracoes e diagnosticos
# devem sobreviver ao _MEIPASS temporario de PyInstaller e nao alterar fontes.
LEGACY_CONFIG = APP_ROOT / "painel_configuracao_local.json"

def _state_folder() -> Path:
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA")
        if base:
            return Path(base) / "VighnaLab"
        return Path.home() / "AppData" / "Local" / "VighnaLab"
    return Path(os.environ.get("XDG_STATE_HOME") or (Path.home() / ".local" / "state")) / "VighnaLab"

CONFIG = _state_folder() / "painel_configuracao_local.json"

def _redirected(path: Path) -> bool:
    if path.is_symlink() or (getattr(path, "is_junction", lambda: False)()):
        return True
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return bool(getattr(info, "st_file_attributes", 0) & 0x400)

MARKER = re.compile(r"^ZIP DE (?:EVIDENCIAS|DIAGNOSTICO) CRIADO:\s*(.+?)\s*$")


def load_config() -> dict:
    # Compatibilidade: apenas no modo fonte ler configuracao antiga;
    # nao gravar nem procurar estado persistente dentro do bundle frozen.
    candidates = [CONFIG]
    if not getattr(__import__("sys"), "frozen", False) and CONFIG != LEGACY_CONFIG:
        candidates.append(LEGACY_CONFIG)
    for path in candidates:
        try:
            if _redirected(path) or _redirected(path.parent):
                continue
            obj = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(obj, dict):
                return obj
        except (FileNotFoundError, ValueError, OSError):
            continue
    return {}


def suggested_python_path() -> str:
    """Sugere somente o ambiente Qt já confirmado pelo usuário, se ainda existir.

    Não procura instalações do VighnaStudy nem percorre o disco.
    """
    candidate = (Path.home() / "Downloads" / "rascunho" / "Nova pasta"
                 / "homologacao_M2_INT1_RC1_20261012_024047"
                 / "qtvenv" / "Scripts" / "python.exe")
    return str(candidate) if candidate.is_file() else ""


def save_python_path(value: str) -> None:
    obj = {"python_qt": value.strip()}
    target = CONFIG
    try:
        if _redirected(target.parent) or _redirected(target):
            raise OSError("Configuracao redirecionada")
        target.parent.mkdir(parents=True, exist_ok=True)
        if _redirected(target.parent) or _redirected(target):
            raise OSError("Configuracao redirecionada")
        fd, temporary = tempfile.mkstemp(prefix=".vighnalab_config_", suffix=".tmp", dir=target.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(obj, handle, ensure_ascii=False, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            if _redirected(target.parent) or _redirected(target):
                raise OSError("Configuracao redirecionada")
            os.replace(temporary, target)
        finally:
            Path(temporary).unlink(missing_ok=True)
    except OSError:
        # Configuracao opcional: falha na escrita nao prejudica os testes.
        return


def candidate_result_dirs() -> list[Path]:
    paths = [
        Path.home() / "Documents" / "VighnaStudy_Homologacao_Resultados",
        Path(tempfile.gettempdir()) / "VighnaStudy_Homologacao_Resultados",
    ]
    # Resultados antigos podem ser encontrados na origem, mas nunca criados la.
    if not getattr(__import__("sys"), "frozen", False):
        paths.append(APP_ROOT)
    seen = set()
    result = []
    for p in paths:
        key = os.path.normcase(str(p.absolute()))
        if key not in seen:
            seen.add(key)
            result.append(p)
    return result


def parse_result_path(line: str) -> Path | None:
    found = MARKER.search(line.strip())
    if not found:
        return None
    return Path(found.group(1).strip().strip('"'))


def latest_result(start_timestamp: float = 0) -> Path | None:
    """Seleciona resultado de forma determinística, sem abrir o ZIP.

    Ordem: modificação (ns), criação/metadados (ns) e caminho lexical como
    último desempate. Em empate de timestamps, não é possível afirmar qual
    arquivo foi gerado por último; o critério apenas evita escolha aleatória.
    """
    candidates = []
    for folder in candidate_result_dirs():
        try:
            paths = folder.glob("RESULTADOS_HOMOLOGACAO_WINDOWS_*.zip")
            for path in paths:
                try:
                    if not path.is_file():
                        continue
                    stat = path.stat()
                    if stat.st_mtime >= start_timestamp - 2.5:
                        candidates.append((stat.st_mtime_ns, stat.st_ctime_ns,
                                           str(path), path))
                except OSError:
                    # Um resultado pode desaparecer enquanto é criado/removido.
                    continue
        except OSError:
            continue
    return max(candidates)[3] if candidates else None


def inspect_result(path: Path) -> dict:
    """Lê somente metadados da evidência; não extrai nem executa conteúdo."""
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise ValueError("O ZIP de resultados está danificado")
        names = set(z.namelist())
        if "RESUMO_HOMOLOGACAO.json" not in names:
            raise ValueError("Resumo do homologador não encontrado")
        obj = json.loads(z.read("RESUMO_HOMOLOGACAO.json"))
        if not isinstance(obj, dict):
            raise ValueError("Resumo inválido")
        result = obj.get("resultados", {})
        if not isinstance(result, dict):
            result = {}
        tests = obj.get("testes", {})
        if not isinstance(tests, dict):
            tests = {}
        blocked = [n for n, t in tests.items() if isinstance(t, dict) and t.get("status") == "BLOQUEADO"]
        failed = [n for n, t in tests.items() if isinstance(t, dict) and t.get("status") == "FALHOU"]
        return {"modo": obj.get("modo", "indefinido"), "falhas": result.get("falhas", len(failed)),
                "bloqueados": result.get("bloqueados", len(blocked)),
                "qt_aprovado": all(tests.get("qt_windows_"+label, {}).get("status") == "PASSOU"
                                   for label in ("100", "125", "150")),
                "qt_bloqueado": any("qt_windows" in name and name in blocked for name in tests),
                "build": tests.get("pyinstaller", {}).get("status", "NAO SOLICITADO"),
                "erro": obj.get("erro"),
                "status_instalacao": "NAO AUTORIZADA"}


def diagnostics_folder() -> Path:
    # Nunca gravar na raiz dos modulos, em _MEIPASS ou em pasta escolhida por evidencias.
    folder = Path(tempfile.gettempdir()) / "VighnaLab_Diagnosticos"
    if _redirected(folder) or _redirected(folder.parent):
        raise OSError("Pasta de diagnosticos redirecionada")
    folder.mkdir(parents=True, exist_ok=True)
    if _redirected(folder):
        raise OSError("Pasta de diagnosticos redirecionada")
    return folder


def dossier_folder() -> Path:
    """Local persistente exclusivo do VighnaLab; nunca APP_ROOT/_MEIPASS."""
    folder = _state_folder() / "G7_Dossies"
    if _redirected(folder.parent) or _redirected(folder):
        raise OSError("Pasta de dossies redirecionada")
    folder.mkdir(parents=True, exist_ok=True)
    if _redirected(folder):
        raise OSError("Pasta de dossies redirecionada")
    return folder


def emergency_report(reason: str, output_lines: list[str]) -> Path:
    """Registra falha do PAINEL; nunca envia dados pela internet."""
    folder = diagnostics_folder()
    name = "DIAGNOSTICO_PAINEL_HOMOLOGACAO_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".zip"
    path = folder / name
    text = "\n".join(output_lines[-1200:])[:350000]
    home = str(Path.home())
    if home:
        text = text.replace(home, "<PERFIL_WINDOWS>")
        reason = reason.replace(home, "<PERFIL_WINDOWS>")
    entries = {
        "ERRO_PAINEL.txt": reason.encode("utf-8"),
        "SAIDA_PROCESSO.txt": text.encode("utf-8"),
        "CONTEXTO.json": json.dumps({"sistema":"painel V1","instalacao_autorizada":False}, indent=2).encode("utf-8")
    }
    manifest = {k: hashlib.sha256(v).hexdigest() for k,v in entries.items()}
    entries["MANIFESTO_SHA256.json"] = json.dumps(manifest, indent=2).encode("utf-8")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for item, data in entries.items():
            z.writestr(item, data)
    return path
