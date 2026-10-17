from __future__ import annotations

import json
import os
from pathlib import Path
import queue
import stat
import subprocess
import sys
import tempfile
from unittest.mock import patch

LAB_SOURCE = Path(r"C:\Users\TD-PC\AppData\Local\Temp\vighnalab_r1_codex_TSd5LY\source")
sys.path.insert(0, str(LAB_SOURCE))

import painel_core as core
import painel_homologacao as ui


def record(results, name, passed, **details):
    results[name] = {"status": "PASSOU" if passed else "FALHOU", **details}


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="vighnalab_codex_custom_") as raw:
        root = Path(raw)
        bundle = root / "bundle"
        bundle.mkdir()
        resources = {
            "PAINEL_VERSAO.json": b'{\n  "component": "vighna-panel",\n  "version": "3.1.53"\n}\n',
            "estado_planejamento_v3.json": b"{}",
            "estado_planejamento_v2a.json": b"{}",
        }
        for name, data in resources.items():
            (bundle / name).write_bytes(data)
        bundle_before = {p.name: p.read_bytes() for p in bundle.iterdir()}

        state = root / "localappdata" / "VighnaLab" / "painel_configuracao_local.json"
        legacy = root / "legacy" / "painel_configuracao_local.json"
        legacy.parent.mkdir()
        legacy.write_text('{"python_qt":"C:/antigo/python.exe"}', encoding="utf-8")
        legacy.chmod(stat.S_IREAD)
        with patch.object(core, "CONFIG", state), patch.object(core, "LEGACY_CONFIG", legacy), \
                patch.object(core, "APP_ROOT", bundle), patch.object(sys, "frozen", False, create=True):
            loaded = core.load_config()
            old_before = legacy.read_bytes()
            core.save_python_path(" C:/novo/python.exe ")
            old_after = legacy.read_bytes()
            saved = core.load_config()
        record(results, "config_localappdata_e_legado_somente_leitura",
               loaded.get("python_qt") == "C:/antigo/python.exe"
               and saved.get("python_qt") == "C:/novo/python.exe"
               and old_before == old_after and state.is_file(),
               config_destino=str(state), legado_preservado=old_before == old_after)

        denied = root / "denied" / "config.json"
        sentinel = root / "sentinela.txt"
        sentinel.write_text("intacto", encoding="utf-8")
        with patch.object(core, "CONFIG", denied), \
                patch.object(core.tempfile, "mkstemp", side_effect=PermissionError("simulado")):
            core.save_python_path("C:/nao_gravar/python.exe")
        record(results, "config_pasta_sem_escrita_simulada",
               not denied.exists() and sentinel.read_text(encoding="utf-8") == "intacto",
               metodo="PermissionError injetado em tempfile.mkstemp")

        temp_area = root / "temp"
        temp_area.mkdir()
        persistent = root / "localappdata" / "VighnaLab"
        with patch.object(core, "APP_ROOT", bundle), \
                patch.object(core.tempfile, "gettempdir", return_value=str(temp_area)), \
                patch.object(core, "_state_folder", return_value=persistent):
            diagnostics = core.diagnostics_folder()
            dossier = core.dossier_folder()
        record(results, "destinos_diagnostico_e_dossie",
               diagnostics == temp_area / "VighnaLab_Diagnosticos"
               and dossier == persistent / "G7_Dossies"
               and bundle_before == {p.name: p.read_bytes() for p in bundle.iterdir()},
               diagnosticos=str(diagnostics), dossie=str(dossier), saida_no_meipass=False)

        symlink_target = root / "symlink_target.json"
        symlink_target.write_text("sentinela", encoding="utf-8")
        symlink_path = root / "config_symlink.json"
        try:
            symlink_path.symlink_to(symlink_target)
        except OSError as exc:
            results["symlink_real"] = {"status": "NAO_TESTADO", "motivo": f"{type(exc).__name__}: {exc}"}
        else:
            with patch.object(core, "CONFIG", symlink_path):
                core.save_python_path("C:/bloqueado/python.exe")
            record(results, "symlink_real", symlink_target.read_text(encoding="utf-8") == "sentinela")
            symlink_path.unlink(missing_ok=True)

        junction_target = root / "junction_target"
        junction_target.mkdir()
        junction_config = junction_target / "config.json"
        junction_config.write_text("sentinela", encoding="utf-8")
        junction = root / "junction"
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        made = subprocess.run(["cmd.exe", "/d", "/c", "mklink", "/J", str(junction), str(junction_target)],
                              capture_output=True, text=True, encoding="utf-8", errors="replace",
                              creationflags=flags, check=False)
        if made.returncode != 0 or not junction.exists():
            results["junction_real"] = {"status": "NAO_TESTADO", "motivo": (made.stderr or made.stdout).strip()}
        else:
            with patch.object(core, "CONFIG", junction / "config.json"):
                core.save_python_path("C:/bloqueado/python.exe")
            preserved = junction_config.read_text(encoding="utf-8") == "sentinela"
            record(results, "junction_real", preserved, junction_detectada=core._redirected(junction))
            os.rmdir(junction)

        instance = object.__new__(ui.Painel)
        instance.events = queue.Queue()
        worker_cases = {
            "_worker": ("C:/python.exe", "testes"),
            "_worker_g5a": (),
            "_worker_g5b": ("C:/python.exe",),
            "_worker_g5c": ("C:/python.exe",),
            "_worker_g6a": ("C:/python.exe",),
            "_worker_g6b": ("C:/python.exe",),
            "_worker_g6b2": ("C:/python.exe",),
        }
        worker_results = {}
        with patch.object(ui.sys, "frozen", True, create=True), \
                patch.object(ui.subprocess, "Popen", side_effect=AssertionError("subprocesso proibido")):
            for name, args in worker_cases.items():
                getattr(instance, name)(*args)
                event = instance.events.get_nowait()
                worker_results[name] = event[0] == "crash" and "indisponivel" in event[1]
        record(results, "workers_diretos_frozen_bloqueados", all(worker_results.values()), workers=worker_results)

        start_cases = {
            "_start": ("testes",),
            "_start_g5b": (),
            "_start_g5c": (),
            "_start_g6a": (),
            "_start_g6b": (),
            "_start_g6b2": (),
        }
        start_results = {}
        with patch.object(ui.sys, "frozen", True, create=True), \
                patch.object(ui.messagebox, "showwarning", return_value=None), \
                patch.object(ui.subprocess, "Popen", side_effect=AssertionError("subprocesso proibido")):
            for name, args in start_cases.items():
                getattr(instance, name)(*args)
                start_results[name] = True
        record(results, "entradas_gui_frozen_bloqueadas", all(start_results.values()), entradas=start_results)

        after = {p.name: p.read_bytes() for p in bundle.iterdir()}
        record(results, "nenhuma_saida_no_meipass", after == bundle_before,
               arquivos_antes=sorted(bundle_before), arquivos_depois=sorted(after))

    status = "PASSOU" if all(v["status"] in {"PASSOU", "NAO_TESTADO"} for v in results.values()) else "FALHOU"
    print(json.dumps({"status": status, "resultados": results}, ensure_ascii=False, indent=2))
    return 0 if status == "PASSOU" else 1


if __name__ == "__main__":
    raise SystemExit(main())
