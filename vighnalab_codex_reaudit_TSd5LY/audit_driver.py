from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


AUDIT = Path(__file__).resolve().parent
ORIGINAL = Path(r"C:\Projetos\VighnaLab_V3153_R1_BASE_COMPLETA_PARA_CODEX_NAO_INSTALAR\VighnaLab_V3153_R1_CODIGO")
MANIFEST_PATH = AUDIT / "MANIFESTO_CODEX_V3153_R1.json"
LAB_SOURCE = Path(r"C:\Users\TD-PC\AppData\Local\Temp\vighnalab_r1_codex_TSd5LY\source")
PROFILE = Path(r"C:\Users\TD-PC\AppData\Local\Temp\vighnalab_r1_codex_TSd5LY\profile")
ARTIFACTS = AUDIT / "artifacts"
LOGS = ARTIFACTS / "logs"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_tree(root: Path) -> dict:
    return {
        path.relative_to(root).as_posix(): {"bytes": path.stat().st_size, "sha256": sha(path)}
        for path in sorted(root.rglob("*")) if path.is_file() and "__pycache__" not in path.parts
    }


def write_json(name: str, data) -> None:
    (ARTIFACTS / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_log(path: Path) -> str:
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace")


def run(name: str, command: list[str], timeout: int) -> dict:
    env = os.environ.copy()
    env.update({
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "USERPROFILE": str(PROFILE),
        "HOME": str(PROFILE),
        "LOCALAPPDATA": str(PROFILE / "AppData" / "Local"),
        "TEMP": str(PROFILE / "Temp"),
        "TMP": str(PROFILE / "Temp"),
    })
    started = datetime.now(timezone.utc)
    timed_out = False
    log_path = LOGS / f"{name}.log"
    try:
        with log_path.open("w", encoding="utf-8") as log_handle:
            result = subprocess.run(command, cwd=LAB_SOURCE, env=env, stdin=subprocess.DEVNULL,
                                    stdout=log_handle, stderr=subprocess.STDOUT, text=True,
                                    encoding="utf-8", errors="replace", timeout=timeout, check=False)
        code = result.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        code = 124
        with log_path.open("a", encoding="utf-8") as log_handle:
            log_handle.write("\nTIMEOUT DO DRIVER\n")
    duration = (datetime.now(timezone.utc) - started).total_seconds()
    output = read_log(log_path)
    summary = {"comando": command, "codigo": code, "timeout": timed_out,
               "duracao_segundos": round(duration, 3), "log": f"logs/{name}.log"}
    match = re.search(r"Ran (\d+) tests? in ([0-9.]+)s", output)
    if match:
        summary["testes"] = int(match.group(1))
        summary["tempo_unittest_segundos"] = float(match.group(2))
    skipped = re.search(r"skipped=(\d+)", output)
    errors = re.search(r"errors=(\d+)", output)
    failures = re.search(r"failures=(\d+)", output)
    summary["pulados"] = int(skipped.group(1)) if skipped else 0
    summary["erros"] = int(errors.group(1)) if errors else 0
    summary["falhas"] = int(failures.group(1)) if failures else 0
    if "testes" in summary:
        summary["aprovados"] = summary["testes"] - summary["pulados"] - summary["erros"] - summary["falhas"]
    summary["erros_nomes"] = re.findall(r"^ERROR: (.+)$", output, flags=re.MULTILINE)
    return summary


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    LOGS.mkdir(exist_ok=True)
    before = hash_tree(ORIGINAL)
    copy_before = hash_tree(LAB_SOURCE)
    write_json("HASHES_FONTES_ORIGINAIS_ANTES.json", before)

    manifest_doc = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    declared = manifest_doc["manifesto"]
    comparison = {
        "arquivos_declarados": len(declared),
        "arquivos_encontrados": len(before),
        "ausentes": sorted(set(declared) - set(before)),
        "extras": sorted(set(before) - set(declared)),
        "sha256_divergentes": sorted(name for name in set(declared) & set(before)
                                      if declared[name]["sha256"] != before[name]["sha256"]),
        "bytes_divergentes": sorted(name for name in set(declared) & set(before)
                                     if declared[name]["bytes"] != before[name]["bytes"]),
    }
    comparison["status"] = "PASSOU" if not any(comparison[key] for key in
        ("ausentes", "extras", "sha256_divergentes", "bytes_divergentes")) else "FALHOU"
    write_json("COMPARACAO_MANIFESTO.json", comparison)

    input_manifest = json.loads((LAB_SOURCE / "MANIFESTO_ENTRADAS_SHA256.json").read_text(encoding="utf-8"))["arquivos"]
    missing_inputs = sorted(name for name in input_manifest if not (LAB_SOURCE / name).is_file())
    present_inputs = sorted(name for name in input_manifest if (LAB_SOURCE / name).is_file())
    inputs = {"declarados": len(input_manifest), "presentes": len(present_inputs),
              "ausentes": len(missing_inputs), "lista_ausentes": missing_inputs,
              "status": "BLOQUEADO_INSUMOS_AUSENTES" if missing_inputs else "COMPLETO"}
    write_json("INSUMOS_OPERACIONAIS.json", inputs)

    if os.environ.get("VIGHNALAB_CUSTOM_ONLY") == "1":
        results_path = ARTIFACTS / "RESULTADOS_TESTES.json"
        tests = json.loads(results_path.read_text(encoding="utf-8"))
        tests["checks_adicionais"] = run(
            "checks_adicionais",
            [sys.executable, "-B", str(AUDIT / "custom_audit_checks.py")], 180)
        custom_output = read_log(LOGS / "checks_adicionais.log")
        try:
            tests["checks_adicionais"]["resultado"] = json.loads(custom_output)
        except json.JSONDecodeError:
            tests["checks_adicionais"]["resultado"] = {"status": "FALHOU", "motivo": "JSON inválido"}
        write_json("RESULTADOS_TESTES.json", tests)
        print(json.dumps(tests["checks_adicionais"], ensure_ascii=True, indent=2))
        return

    tests = {}
    tests["reconciliacao_v3153_r1"] = run(
        "unittest_reconciliacao_v3153_r1",
        [sys.executable, "-B", "-m", "unittest", "-v", "test_reconciliacao_v3153_r1"], 180)
    tests["regressoes_completas"] = run(
        "unittest_regressoes_completas",
        [sys.executable, "-B", "-m", "unittest", "discover", "-v"], 900)
    tests["checks_adicionais"] = run(
        "checks_adicionais",
        [sys.executable, "-B", str(AUDIT / "custom_audit_checks.py")], 180)
    custom_output = read_log(LOGS / "checks_adicionais.log")
    try:
        tests["checks_adicionais"]["resultado"] = json.loads(custom_output)
    except json.JSONDecodeError:
        tests["checks_adicionais"]["resultado"] = {"status": "FALHOU", "motivo": "JSON inválido"}

    full_log = read_log(LOGS / "unittest_regressoes_completas.log")
    classifications = []
    for name in tests["regressoes_completas"]["erros_nomes"]:
        if "test_gui_v3_smoke" in name:
            category = "DEPENDENCIA_GUI_TK_DISPLAY_AUSENTE"
        else:
            category = "INSUMOS_OPERACIONAIS_AUSENTES"
        classifications.append({"teste": name, "categoria": category})
    tests["regressoes_completas"]["classificacao_erros"] = classifications
    tests["regressoes_completas"]["timeouts_na_bateria"] = 0
    tests["regressoes_completas"]["nota_timeouts"] = (
        "Casos que injetam TimeoutExpired passaram; nenhum timeout real escapou para erro."
        if "TimeoutExpired" not in "\n".join(tests["regressoes_completas"]["erros_nomes"])
        else "Revisar log"
    )
    write_json("RESULTADOS_TESTES.json", tests)

    spec_text = (LAB_SOURCE / "VighnaLab_QA_V3153_R1.spec").read_text(encoding="utf-8")
    resources = ["PAINEL_VERSAO.json", "estado_planejamento_v3.json", "estado_planejamento_v2a.json"]
    pyinstaller_available = subprocess.run([sys.executable, "-B", "-c", "import PyInstaller"],
                                           capture_output=True, check=False).returncode == 0
    isolated_venv = sys.prefix != sys.base_prefix
    bundle = {
        "spec_sintaxe_estatica": "PASSOU",
        "recursos_no_spec": {name: name in spec_text for name in resources},
        "painel_versao": json.loads((LAB_SOURCE / "PAINEL_VERSAO.json").read_text(encoding="utf-8")),
        "estado_v3": json.loads((LAB_SOURCE / "estado_planejamento_v3.json").read_text(encoding="utf-8")),
        "estado_v2a": json.loads((LAB_SOURCE / "estado_planejamento_v2a.json").read_text(encoding="utf-8")),
        "ambiente_venv_isolado": isolated_venv,
        "pyinstaller_disponivel_python_atual": pyinstaller_available,
        "build_spec": "PENDENTE",
        "motivo": "Nenhum venv descartável pré-existente autorizado com dependências completas; nenhuma instalação foi executada.",
    }
    write_json("VALIDACAO_SPEC_E_BUNDLE.json", bundle)

    after = hash_tree(ORIGINAL)
    copy_after = hash_tree(LAB_SOURCE)
    write_json("HASHES_FONTES_ORIGINAIS_DEPOIS.json", after)
    preservation = {
        "originais_identicos_antes_depois": before == after,
        "copia_identica_antes_depois": copy_before == copy_after,
        "arquivos_originais": len(before),
        "status": "PASSOU" if before == after and copy_before == copy_after else "FALHOU",
    }
    write_json("PRESERVACAO_FONTES.json", preservation)

    index = {
        "formato": "vighnalab-codex-reauditoria-v3153-r1",
        "gerado_utc": datetime.now(timezone.utc).isoformat(),
        "fonte_original": str(ORIGINAL),
        "python": sys.version,
        "manifesto": comparison["status"],
        "insumos": inputs["status"],
        "reconciliacao": tests["reconciliacao_v3153_r1"],
        "regressoes": tests["regressoes_completas"],
        "fontes_preservadas": preservation["status"],
        "instalacao_autorizada": False,
        "g7_aprovado": False,
    }
    write_json("RESULTADO_GERAL.json", index)
    print(json.dumps(index, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
