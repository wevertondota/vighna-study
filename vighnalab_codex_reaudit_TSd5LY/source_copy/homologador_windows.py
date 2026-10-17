# -*- coding: utf-8 -*-
"""Homologador VighnaStudy Windows V1 — laboratório independente, NÃO INSTALA.

Não usa instalação principal, não aceita diretório de instalação, não abre banco pessoal.
Executa somente arquivos auditados e inclusos no próprio pacote.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import traceback
import zipfile

KIT = Path(__file__).resolve().parent
BASE = "BASE_R1D_SOMENTE_FONTES_QA.zip"
PATCH = "CANDIDATO_QA_R1D_PARA_M2_RC2_NAO_INSTALAR.zip"
RC2 = "M2_RC2_FONTE_REFERENCIA_NAO_INSTALAR.zip"
EXPECTED_BASE = "structural-m1c-readpilot-restore-offline-r1d-v1"
EXPECTED_TARGET = "structural-m2-int1-settings-r1d-rc2"
MAX_ARCHIVE_UNCOMPRESSED = 25 * 1024 * 1024
MAX_MEMBER = 4 * 1024 * 1024
FORBIDDEN_SUFFIXES = (".db", ".sqlite", ".sqlite3", ".exe", ".dll", ".pyd", ".db-wal", ".db-shm")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def is_bad_path(name: str) -> bool:
    name = name.replace("\\", "/")
    parts = PurePosixPath(name).parts
    return (
        not name or not parts or name.startswith(("/", "\\"))
        or ":" in name or any(p in ("", ".", "..") for p in parts)
        or name != PurePosixPath(name).as_posix()
        or name.endswith("/") or any(name.lower().endswith(s) for s in FORBIDDEN_SUFFIXES)
    )


def verify_package_member(info: zipfile.ZipInfo, normalized: str) -> None:
    if is_bad_path(normalized):
        raise ValueError("Nome de arquivo inseguro no ZIP: " + normalized)
    if info.file_size > MAX_MEMBER:
        raise ValueError("Arquivo grande demais no ZIP: " + normalized)
    if info.create_system == 3 and stat.S_ISLNK(info.external_attr >> 16):
        raise ValueError("Link simbólico proibido no ZIP: " + normalized)


def checked_archive(path: Path, *, prefix: str = "") -> dict[str, bytes]:
    result = {}
    total = 0
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            name = info.filename.replace("\\", "/")
            if prefix:
                if not name.startswith(prefix):
                    if name in {"DIFF_RC1_RC2.patch", "HASHES_SHA256.csv",
                                "MANIFESTO_RC2.json", "NAO_INSTALAR.txt"}:
                        continue  # Metadados do pacote de código, não são fontes de QA.
                    raise ValueError("Arquivo inesperado fora do prefixo esperado: " + name)
                name = name[len(prefix):]
            verify_package_member(info, name)
            if name.lower() in {k.lower() for k in result}:
                raise ValueError("Nome duplicado no ZIP: " + name)
            total += info.file_size
            if total > MAX_ARCHIVE_UNCOMPRESSED:
                raise ValueError("ZIP excede orçamento de dados QA")
            result[name] = archive.read(info)
    return result


def ensure_not_user_installation() -> None:
    # Bloqueia uma extração acidental dentro/ao lado da instalação principal.
    for directory in (KIT, KIT.parent, KIT.parent.parent):
        if (directory / "estudos.db").exists() or (directory / "VighnaStudy.exe").exists():
            raise ValueError("Homologador extraido na pasta de uma instalacao real: BLOQUEADO")
        if (directory / "dist" / "VighnaStudy" / "VighnaStudy.exe").exists():
            raise ValueError("Pasta de instalacao/compilacao real detectada: BLOQUEADO")


def verify_inputs() -> dict:
    ensure_not_user_installation()
    meta = json.loads((KIT / "MANIFESTO_ENTRADAS_SHA256.json").read_text(encoding="utf-8"))
    for rel, expected in meta["arquivos"].items():
        file = KIT / rel
        if not file.is_file() or digest_file(file) != expected:
            raise ValueError("ARQUIVO AUSENTE OU ALTERADO: " + rel)
    return meta


def write_sources(files: dict[str, bytes], destination: Path):
    destination.mkdir(parents=True, exist_ok=False)
    for name, content in files.items():
        # checked_archive already screened traversal, symlinks, executables and databases.
        target = destination.joinpath(*PurePosixPath(name).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def run_command(cmd: list[str], *, cwd: Path, env: dict, outfile: Path, timeout: int) -> dict:
    try:
        r = subprocess.run(cmd, cwd=str(cwd), env=env, text=True, encoding="utf-8",
                           errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=timeout, check=False)
        text = r.stdout or ""
        if len(text) > 2_000_000:
            text = text[:200_000] + "\n...\n[SAIDA LIMITADA]\n...\n" + text[-1_000_000:]
        outfile.parent.mkdir(parents=True, exist_ok=True)
        outfile.write_text(text, encoding="utf-8")
        return {"retorno": r.returncode, "log": outfile.name, "status": "PASSOU" if r.returncode == 0 else
                "BLOQUEADO" if r.returncode == 77 else "FALHOU"}
    except subprocess.TimeoutExpired as exc:
        outfile.write_text("TIMEOUT: %s\n" % (exc,), encoding="utf-8")
        return {"retorno": 124, "log": outfile.name, "status": "FALHOU", "causa": "timeout"}


def environment_qa(work: Path) -> dict:
    env = os.environ.copy()
    fake = work / "PERFIL_SINTETICO"
    for folder in ("AppData/Roaming", "AppData/Local", "Temp", "Home", "QtConfig"):
        (fake / folder).mkdir(parents=True, exist_ok=True)
    env.update({
        "APPDATA": str(fake / "AppData/Roaming"),
        "LOCALAPPDATA": str(fake / "AppData/Local"),
        "USERPROFILE": str(fake / "Home"),
        "HOME": str(fake / "Home"),
        "TEMP": str(fake / "Temp"),
        "TMP": str(fake / "Temp"),
        "TMPDIR": str(fake / "Temp"),
        "XDG_CONFIG_HOME": str(fake / "QtConfig"),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "PYTHONUTF8": "1",
        "QT_QPA_PLATFORM": "windows",
        "QT_LOGGING_RULES": "qt.qpa.*=false",
    })
    for inherited in (
        "PYTHONPATH", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH",
        "QT_QML_IMPORT_PATH", "QT_QML2_IMPORT_PATH",
    ):
        env.pop(inherited, None)
    return env


def inspect_static(b: dict[str, bytes], patch: dict[str, bytes], rc2: dict[str, bytes]) -> dict:
    manifest = json.loads(patch["manifest.json"].decode("utf-8-sig"))
    expected_files = {n for n in patch if n != "manifest.json"}
    assert set(manifest["files"]) == expected_files and len(expected_files) == 11
    assert manifest["base_build"] == EXPECTED_BASE
    assert manifest["target_build"] == EXPECTED_TARGET
    assert manifest["schema"] == 25 and manifest["base_version"] == "0.29.59"
    for file in expected_files:
        assert digest(patch[file]) == manifest["files"][file], file
    assert "VighnaStudy.spec" not in expected_files
    assert "banco.py" not in expected_files and "backup.py" not in expected_files
    assert patch["main.py"] == rc2["main.py"], "RC2 diverge do pacote direto"
    assert patch["versao.py"] == rc2["versao.py"], "RC2 diverge do pacote direto"
    assert "VighnaStudy.spec" in b and "VighnaStudy.spec" in rc2
    python_names = [n for n in rc2 if n.endswith(".py")]
    for n in python_names:
        compile(rc2[n], n, "exec")
    for n in expected_files:
        if n.endswith(".py"):
            compile(patch[n], n, "exec")
    assert EXPECTED_BASE in b["versao.py"].decode("utf-8")
    assert EXPECTED_TARGET in patch["versao.py"].decode("utf-8")
    return {
        "status": "PASSOU", "arquivos_atualizacao": len(expected_files),
        "modulos_python_rc2_compilados": len(python_names),
        "main_rc2_sha256": digest(rc2["main.py"]),
        "spec_r1d_sha256": digest(b["VighnaStudy.spec"]),
        "spec_rc2_original_diverge": b["VighnaStudy.spec"] != rc2["VighnaStudy.spec"],
    }


def report_zip(evidence: Path, output: Path, summary: dict):
    entries = {}
    for path in sorted(evidence.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(evidence).as_posix()
        if path.stat().st_size > 8_000_000:
            # Nunca deixar logs enormes esconderem falhas ou dados indesejados.
            continue
        entries[rel] = path.read_bytes()
    entries["RESUMO_HOMOLOGACAO.json"] = json.dumps(
        summary, indent=2, ensure_ascii=False).encode("utf-8")
    hashes = {name: digest(content) for name, content in entries.items()}
    entries["MANIFESTO_SHA256.json"] = json.dumps(hashes, indent=2).encode("utf-8")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, data in entries.items():
            z.writestr(name, data)
    with zipfile.ZipFile(output) as z:
        if z.testzip() is not None:
            raise RuntimeError("Falha na integridade do ZIP de saída")
        for name, sha in hashes.items():
            if digest(z.read(name)) != sha:
                raise RuntimeError("Hash divergente na evidência: " + name)


def preflight_selftest() -> dict:
    assert is_bad_path("../estudos.db")
    assert is_bad_path("D:/dados.txt")
    assert is_bad_path("estudos.db")
    assert is_bad_path("backups/estudos.db-wal")
    assert not is_bad_path("ui/settings_search.py")
    assert not is_bad_path("main.py")
    meta = verify_inputs()
    b = checked_archive(KIT / "insumos" / BASE)
    p = checked_archive(KIT / "insumos" / PATCH)
    r = checked_archive(KIT / "insumos" / RC2, prefix="codigo/")
    static = inspect_static(b, p, r)
    return {"status": "PASSOU", "arquivos_com_hash": len(meta["arquivos"]),
            "baseline_qa": len(b), "patch_qa": len(p), "rc2_fonte": len(r),
            "contrato_estatico": static}



def evidence_destination() -> Path:
    """Preferência: pasta extraída. Nunca grava em uma pasta de instalação real."""
    try:
        ensure_not_user_installation()
        KIT.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix=".homologador_probe_", dir=KIT, delete=True):
            pass
        return KIT
    except (OSError, ValueError):
        # Área de diagnóstico independente se pasta extraída for insegura ou somente leitura.
        for fallback in (Path.home() / "Documents" / "VighnaStudy_Homologacao_Resultados",
                         Path(tempfile.gettempdir()) / "VighnaStudy_Homologacao_Resultados"):
            try:
                fallback.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(prefix=".homologador_probe_", dir=fallback, delete=True):
                    pass
                return fallback
            except OSError:
                continue
        raise RuntimeError("Nenhuma pasta segura e gravavel para relatorios foi encontrada.")


def stage(message: str) -> None:
    print("ETAPA_HOMOLOGADOR:", message, flush=True)


def safe_error_details() -> str:
    message = traceback.format_exc()
    # Evita expor nomes de perfil e caminhos reais do usuario no ZIP de evidencias.
    for target, replacement in (
        (str(Path.home()), "<PERFIL_WINDOWS>"),
        (str(KIT), "<PASTA_HOMOLOGADOR>"),
        (str(Path(tempfile.gettempdir())), "<TEMP>"),
    ):
        if target:
            message = message.replace(target, replacement)
    return message


def do_run(mode: str) -> int:
    if sys.platform != "win32":
        print("BLOQUEADO: este teste de sistema deve ser executado no Windows.", file=sys.stderr)
        return 77
    runid = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_dir = evidence_destination()
    result_zip = output_dir / ("RESULTADOS_HOMOLOGACAO_WINDOWS_" + runid + ".zip")
    evidence = None
    sandbox = None
    summary = {"homologador": "V1.1", "ambiente": "Windows", "modo": mode,
               "decisao": "NAO_HOMOLOGADO_AUTOMATICAMENTE",
               "instalacao_autorizada": False, "executavel_real_iniciado": False,
               "testes": {}}
    stage("Verificando arquivos e hashes; a instalacao principal nao sera utilizada.")
    try:
        check = preflight_selftest()
        stage("Integridade de origem: APROVADA. Criando laboratorio temporario.")
        sandbox = Path(tempfile.mkdtemp(prefix="Vighna_Homologacao_QA_"))
        evidence = sandbox / "EVIDENCIAS"
        evidence.mkdir()
        env = environment_qa(sandbox)
        summary["python"] = platform.python_version()
        summary["sistema"] = platform.system()
        summary["testes"]["preflight"] = check
        stage("Executando as guardas de seguranca do homologador.")
        guardas = run_command(
            [sys.executable, "-B", "-m", "unittest", "-v", "test_protecao_homologador"],
            cwd=KIT, env=env,
            outfile=evidence / "testes_seguranca_homologador.log", timeout=70)
        summary["testes"]["guardas_de_seguranca"] = guardas
        if guardas["status"] != "PASSOU":
            raise RuntimeError("As guardas de segurança do homologador não passaram.")
        b = checked_archive(KIT / "insumos" / BASE)
        patch = checked_archive(KIT / "insumos" / PATCH)
        rc2 = checked_archive(KIT / "insumos" / RC2, prefix="codigo/")
        # Cópia de referência sem bancos e com .spec exatamente da R1D.
        rc2["VighnaStudy.spec"] = b["VighnaStudy.spec"]
        code = sandbox / "CODIGO_M2_RC2_QA"
        write_sources(rc2, code)
        # Testes transacionais com dados sintéticos e EXE falso.
        tests = sandbox / "TESTES_QA"
        tests.mkdir()
        for test in (KIT / "testes").glob("*.py"):
            (tests / test.name).write_bytes(test.read_bytes())
        (tests / BASE).write_bytes((KIT / "insumos" / BASE).read_bytes())
        (tests / PATCH).write_bytes((KIT / "insumos" / PATCH).read_bytes())
        testcmd = [sys.executable, "-B", "-m", "unittest", "-v",
                   "test_gate_direto_r1d_rc2", "test_gate6_casos_borda",
                   "test_vighna_atualizador", "test_gate6_spec_compat_estatica"]
        stage("Executando testes de atualizacao/rollback apenas com banco sintetico.")
        summary["testes"]["atualizacao_sintetica"] = run_command(
            testcmd, cwd=tests, env=env,
            outfile=evidence / "testes_atualizacao_sintetica.log", timeout=240)
        # O teste de Qt extrai apenas JanelaConfiguracoes por AST, sem importar main/banco.
        try:
            import PySide6  # noqa
            qt_available = True
        except (ImportError, OSError):
            qt_available = False
        if not qt_available:
            stage("PySide6 nao encontrado neste Python. Testes Qt: BLOQUEADOS, nao aprovados.")
            summary["testes"]["qt_windows"] = {
                "status": "BLOQUEADO", "causa": "PySide6 indisponivel. Nada sera instalado automaticamente."}
        else:
            for factor, label in ((1.0, "100"), (1.25, "125"), (1.50, "150")):
                stage("Qt Windows: escala simulada " + label + "%.")
                scope = evidence / ("qt_windows_" + label)
                scope.mkdir()
                envqt = env.copy()
                envqt["QT_SCALE_FACTOR"] = str(factor)
                r = run_command([sys.executable, "-B", str(KIT / "qt" / "validador_qt_rc2_isolado.py"),
                                 "--source", str(code), "--output", str(scope)],
                                cwd=scope, env=envqt,
                                outfile=scope / "execucao_qt.log", timeout=180)
                summary["testes"]["qt_windows_" + label] = r
        if mode == "build":
            stage("Modo opcional: tentando compilacao em copia QA, sem executar EXE.")
            # Processo opcional: compila cópia QA com VighnaStudy.spec da R1D.
            try:
                import PyInstaller  # noqa
                import qtawesome  # noqa
                can_build = True
            except (ImportError, OSError):
                can_build = False
            if not can_build:
                summary["testes"]["pyinstaller"] = {
                    "status": "BLOQUEADO", "causa": "PyInstaller ou qtawesome ausente"}
            else:
                r = run_command([sys.executable, "-B", "-m", "PyInstaller", "--noconfirm",
                                 "--distpath", str(sandbox / "DIST_QA"),
                                 "--workpath", str(sandbox / "BUILD_QA"),
                                 "VighnaStudy.spec"],
                                cwd=code, env=env, outfile=evidence / "compilacao_pyinstaller.log",
                                timeout=1200)
                exe = sandbox / "DIST_QA" / "VighnaStudy" / "VighnaStudy.exe"
                if r["retorno"] == 0 and exe.is_file():
                    r["exe_sha256"] = digest_file(exe)
                    r["exe_bytes"] = exe.stat().st_size
                    r["observacao"] = "EXE produzido em QA, NAO EXECUTADO nem instalado."
                elif r["retorno"] == 0:
                    r["status"] = "FALHOU"
                    r["causa"] = "Build retornou 0, mas EXE ausente."
                summary["testes"]["pyinstaller"] = r
        summary["resultados"] = {
            "aprovados": sum(v.get("status") == "PASSOU" for v in summary["testes"].values()),
            "falhas": sum(v.get("status") == "FALHOU" for v in summary["testes"].values()),
            "bloqueados": sum(v.get("status") == "BLOQUEADO" for v in summary["testes"].values()),
        }
        stage("Empacotando todas as evidencias em ZIP.")
        report_zip(evidence, result_zip, summary)
        print("\nRESULTADO: ", json.dumps(summary["resultados"], ensure_ascii=False), flush=True)
        print("ZIP DE EVIDENCIAS CRIADO:", result_zip, flush=True)
        print("PASTA DE RESULTADOS:", output_dir, flush=True)
        print("STATUS: NAO HOMOLOGADO PARA INSTALACAO. Envie o ZIP ao ChatGPT.")
        return 1 if summary["resultados"]["falhas"] else 0
    except Exception as error:
        print("BLOQUEADO / ERRO:", type(error).__name__, str(error), file=sys.stderr, flush=True)
        details = safe_error_details()
        if evidence is None:
            # A V1 encerrava aqui sem qualquer ZIP. V1.1 garante diagnostico emergencial.
            try:
                if sandbox is None:
                    sandbox = Path(tempfile.mkdtemp(prefix="Vighna_Homologacao_QA_"))
                evidence = sandbox / "EVIDENCIAS"
                evidence.mkdir(parents=True, exist_ok=True)
            except Exception:
                evidence = None
        summary["erro"] = {"tipo": type(error).__name__, "mensagem": str(error)}
        summary["decisao"] = "FALHA_OU_BLOQUEIO_NAO_HOMOLOGADO"
        if evidence is not None:
            try:
                (evidence / "erro_diagnostico_sanitizado.txt").write_text(details, encoding="utf-8")
                report_zip(evidence, result_zip, summary)
                print("ZIP DE DIAGNOSTICO CRIADO:", result_zip, flush=True)
                print("PASTA DE RESULTADOS:", output_dir, flush=True)
            except Exception as exc:
                print("ERRO AO GERAR ZIP:", type(exc).__name__, str(exc), file=sys.stderr, flush=True)
        return 1
    finally:
        if sandbox is not None and sandbox.name.startswith("Vighna_Homologacao_QA_") and sandbox.parent == Path(tempfile.gettempdir()):
            shutil.rmtree(sandbox, ignore_errors=True)


if __name__ == "__main__":
    arg = argparse.ArgumentParser()
    arg.add_argument("--modo", choices=("testes", "build"), default="testes")
    arg.add_argument("--selftest", action="store_true")
    options = arg.parse_args()
    if options.selftest:
        print(json.dumps(preflight_selftest(), ensure_ascii=False, indent=2))
        sys.exit(0)
    sys.exit(do_run(options.modo))
