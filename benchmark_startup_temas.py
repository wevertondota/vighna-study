#!/usr/bin/env python3
"""Benchmark controlado do startup do VighnaStudy por tema.

Executa o projeto em uma cópia temporária para não alterar o banco nem os
arquivos do Vighna original. Compara Futurista, Claro e sem QSS global.

Uso recomendado no Windows, na raiz C:\\SistemaEstudos:
    .venv\\Scripts\\python.exe benchmark_startup_temas.py --runs 3

Gera CSV e JSON ao lado deste script.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path


EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "dist", "build", "backups", "checkpoints",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
}


def _ignore(_dir: str, names: list[str]) -> set[str]:
    return {n for n in names if n in EXCLUDED_DIRS or n.endswith(".pyc")}


def _patch_main(path: Path) -> None:
    src = path.read_text(encoding="utf-8")

    src = (
        "import os as _bench_os\n"
        "import time as _bench_time\n"
        "_BENCH_PROCESS_T0 = _bench_time.perf_counter()\n"
        + src
    )

    old = "app = QApplication(sys.argv)"
    new = (
        "_BENCH_BEFORE_QAPP = _bench_time.perf_counter()\n"
        "app = QApplication(sys.argv)\n"
        "_BENCH_AFTER_QAPP = _bench_time.perf_counter()"
    )
    if old not in src:
        raise RuntimeError("Não encontrei a criação de QApplication em main.py")
    src = src.replace(old, new, 1)

    old = "janela = SistemaEstudos(pre_carregar_startup=True)"
    new = (
        "_BENCH_CTOR_T0 = _bench_time.perf_counter()\n"
        "janela = SistemaEstudos(pre_carregar_startup=True)\n"
        "_BENCH_CTOR_T1 = _bench_time.perf_counter()\n"
        "_BENCH_STAGE_MARKS = []\n"
        "def _bench_notify(texto, percentual=None, detalhe=None):\n"
        "    _BENCH_STAGE_MARKS.append({\n"
        "        'texto': str(texto),\n"
        "        'percentual': percentual,\n"
        "        't': _bench_time.perf_counter(),\n"
        "    })\n"
        "    splash.atualizar(texto, percentual, detalhe)"
    )
    if old not in src:
        raise RuntimeError("Não encontrei a construção de SistemaEstudos em main.py")
    src = src.replace(old, new, 1)

    old = "    janela.precarregar_inicializacao_completa(splash.atualizar)"
    new = (
        "    _BENCH_PRELOAD_T0 = _bench_time.perf_counter()\n"
        "    janela.precarregar_inicializacao_completa(_bench_notify)\n"
        "    _BENCH_PRELOAD_T1 = _bench_time.perf_counter()"
    )
    if old not in src:
        raise RuntimeError("Não encontrei a chamada de pré-carregamento em main.py")
    src = src.replace(old, new, 1)

    old = """janela.show()\njanela.raise_()\njanela.activateWindow()\nsplash.close()\n\nsys.exit(app.exec())"""
    new = """_BENCH_SHOW_T0 = _bench_time.perf_counter()\njanela.show()\njanela.raise_()\njanela.activateWindow()\nQApplication.processEvents(QEventLoop.AllEvents, 250)\n_BENCH_SHOW_T1 = _bench_time.perf_counter()\nsplash.close()\n\n_bench_log = _bench_os.environ.get("VIGHNA_BENCH_LOG")\nif _bench_log:\n    _bench_record = {\n        "mode": _bench_os.environ.get("VIGHNA_BENCH_MODE", ""),\n        "process_t0": _BENCH_PROCESS_T0,\n        "before_qapp": _BENCH_BEFORE_QAPP,\n        "after_qapp": _BENCH_AFTER_QAPP,\n        "ctor_t0": _BENCH_CTOR_T0,\n        "ctor_t1": _BENCH_CTOR_T1,\n        "preload_t0": globals().get("_BENCH_PRELOAD_T0", _BENCH_CTOR_T1),\n        "preload_t1": globals().get("_BENCH_PRELOAD_T1", _BENCH_CTOR_T1),\n        "show_t0": _BENCH_SHOW_T0,\n        "show_t1": _BENCH_SHOW_T1,\n        "stages": _BENCH_STAGE_MARKS,\n    }\n    with open(_bench_log, "a", encoding="utf-8") as _f:\n        _f.write(json.dumps(_bench_record, ensure_ascii=False) + "\\n")\n\nQTimer.singleShot(180, app.quit)\nsys.exit(app.exec())"""
    if old not in src:
        raise RuntimeError("Não encontrei o bloco final de exibição em main.py")
    src = src.replace(old, new, 1)
    path.write_text(src, encoding="utf-8")


def _patch_theme(path: Path) -> None:
    src = path.read_text(encoding="utf-8")
    src = "import os as _bench_os\n" + src
    needle = """    tema = normalizar_tema(\n        tema\n    )\n\n    app.setStyle(\n        \"Fusion\"\n    )"""
    replacement = """    tema = normalizar_tema(\n        tema\n    )\n\n    if _bench_os.environ.get("VIGHNA_BENCH_NO_QSS") == "1":\n        app.setStyle("Fusion")\n        app.setStyleSheet("")\n        return tema\n\n    app.setStyle(\n        \"Fusion\"\n    )"""
    if needle not in src:
        raise RuntimeError("Não encontrei aplicar_tema() no formato esperado em tema.py")
    src = src.replace(needle, replacement, 1)
    path.write_text(src, encoding="utf-8")


def _set_theme(db: Path, theme: str) -> None:
    con = sqlite3.connect(db)
    try:
        con.execute(
            "INSERT INTO configuracoes(chave, valor) VALUES('tema_interface', ?) "
            "ON CONFLICT(chave) DO UPDATE SET valor=excluded.valor",
            (theme,),
        )
        con.commit()
    finally:
        con.close()


def _find_stage_time(stages: list[dict], prefix: str) -> float | None:
    for item in stages:
        if str(item.get("texto", "")).startswith(prefix):
            return float(item["t"])
    return None


def _ms(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    return round((b - a) * 1000.0, 3)


def _flatten(rec: dict, wall_ms: float, run_no: int) -> dict:
    stages = rec.get("stages") or []
    t_dash = _find_stage_time(stages, "Preparando o Dashboard")
    t_disc = _find_stage_time(stages, "Preparando disciplinas")
    t_central = _find_stage_time(stages, "Preparando a Central")
    t_resumo = _find_stage_time(stages, "Preparando o Resumo")
    t_cal = _find_stage_time(stages, "Preparando o Calendário")
    t_sessao = _find_stage_time(stages, "Preparando sessões")
    t_stats = _find_stage_time(stages, "Preparando Estatísticas")
    t_reports = _find_stage_time(stages, "Preparando Relatórios")
    t_final = _find_stage_time(stages, "Finalizando a interface")
    t_ready = _find_stage_time(stages, "Tudo pronto")

    return {
        "modo": rec.get("mode", ""),
        "rodada": run_no,
        "imports_e_bootstrap_ms": _ms(rec["process_t0"], rec["before_qapp"]),
        "qapplication_ms": _ms(rec["before_qapp"], rec["after_qapp"]),
        "construtor_dashboard_tema_ms": _ms(rec["ctor_t0"], rec["ctor_t1"]),
        "preload_total_ms": _ms(rec["preload_t0"], rec["preload_t1"]),
        "dashboard_ms": _ms(t_dash, t_disc),
        "disciplinas_ms": _ms(t_disc, t_central),
        "central_ms": _ms(t_central, t_resumo),
        "resumo_ms": _ms(t_resumo, t_cal),
        "calendario_ms": _ms(t_cal, t_sessao),
        "sessao_ms": _ms(t_sessao, t_stats),
        "estatisticas_ms": _ms(t_stats, t_reports),
        "relatorios_ms": _ms(t_reports, t_final),
        "finalizacao_ms": _ms(t_final, t_ready),
        "show_primeiro_paint_ms": _ms(rec["show_t0"], rec["show_t1"]),
        "total_interno_ate_paint_ms": _ms(rec["process_t0"], rec["show_t1"]),
        "wall_process_ms": round(wall_ms, 3),
    }


def _median_summary(rows: list[dict]) -> list[dict]:
    out = []
    modes = []
    for r in rows:
        if r["modo"] not in modes:
            modes.append(r["modo"])
    numeric = [k for k in rows[0] if k not in {"modo", "rodada"}]
    for mode in modes:
        subset = [r for r in rows if r["modo"] == mode]
        item = {"modo": mode, "rodadas": len(subset)}
        for key in numeric:
            vals = [r[key] for r in subset if isinstance(r.get(key), (int, float))]
            item[key] = round(statistics.median(vals), 3) if vals else None
        out.append(item)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3, help="rodadas por modo (padrão: 3)")
    args = parser.parse_args()
    runs = max(1, min(10, args.runs))

    root = Path(__file__).resolve().parent
    required = [root / "main.py", root / "tema.py", root / "estudos.db", root / "VighnaStudy.spec"]
    missing = [str(p.name) for p in required if not p.exists()]
    if missing:
        print("Execute este script na raiz do VighnaStudy. Faltando:", ", ".join(missing))
        return 2

    stamp = time.strftime("%Y%m%d_%H%M%S")
    result_json = root / f"benchmark_temas_{stamp}.json"
    result_csv = root / f"benchmark_temas_{stamp}.csv"
    log_jsonl = Path(tempfile.gettempdir()) / f"vighna_theme_bench_{stamp}.jsonl"
    temp_root = Path(tempfile.mkdtemp(prefix="vighna_theme_benchmark_"))

    print(f"Cópia temporária: {temp_root}")
    print("O banco original não será alterado.")
    shutil.copytree(root, temp_root, dirs_exist_ok=True, ignore=_ignore)
    original_db = root / "estudos.db"
    bench_db = temp_root / "estudos.db"

    _patch_main(temp_root / "main.py")
    _patch_theme(temp_root / "tema.py")

    modes = [
        ("futurista", "futurista", False),
        ("claro", "claro", False),
        ("sem_qss", "claro", True),
    ]
    rows: list[dict] = []

    try:
        for mode_name, db_theme, no_qss in modes:
            for run_no in range(1, runs + 1):
                shutil.copy2(original_db, bench_db)
                _set_theme(bench_db, db_theme)
                try:
                    (temp_root / "backups").mkdir(exist_ok=True)
                except Exception:
                    pass

                before_lines = 0
                if log_jsonl.exists():
                    before_lines = len(log_jsonl.read_text(encoding="utf-8").splitlines())

                env = os.environ.copy()
                env["VIGHNA_BENCH_MODE"] = mode_name
                env["VIGHNA_BENCH_LOG"] = str(log_jsonl)
                env["VIGHNA_BENCH_NO_QSS"] = "1" if no_qss else "0"

                print(f"[{mode_name}] rodada {run_no}/{runs} ...", flush=True)
                t0 = time.perf_counter()
                proc = subprocess.run(
                    [sys.executable, str(temp_root / "main.py")],
                    cwd=str(temp_root),
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=180,
                )
                wall_ms = (time.perf_counter() - t0) * 1000.0

                lines = log_jsonl.read_text(encoding="utf-8").splitlines() if log_jsonl.exists() else []
                if proc.returncode != 0 or len(lines) <= before_lines:
                    print("Falha na rodada.")
                    if proc.stdout.strip():
                        print("STDOUT:\n", proc.stdout[-4000:])
                    if proc.stderr.strip():
                        print("STDERR:\n", proc.stderr[-4000:])
                    return proc.returncode or 3

                rec = json.loads(lines[-1])
                rows.append(_flatten(rec, wall_ms, run_no))

        summary = _median_summary(rows)
        payload = {
            "gerado_em": time.strftime("%Y-%m-%d %H:%M:%S"),
            "python": sys.executable,
            "runs_por_modo": runs,
            "rodadas": rows,
            "medianas": summary,
        }
        result_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        fields = list(rows[0].keys())
        with result_csv.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=fields, delimiter=";")
            w.writeheader()
            w.writerows(rows)

        print("\nMEDIANAS (ms)")
        print("-" * 92)
        for s in summary:
            print(
                f"{s['modo']:10s} | total até paint: {s.get('total_interno_ate_paint_ms', 0):8.1f} | "
                f"construtor: {s.get('construtor_dashboard_tema_ms', 0):7.1f} | "
                f"preload: {s.get('preload_total_ms', 0):8.1f} | "
                f"Central: {s.get('central_ms', 0):7.1f} | "
                f"Estat.: {s.get('estatisticas_ms', 0):7.1f} | "
                f"Relat.: {s.get('relatorios_ms', 0):7.1f}"
            )
        print("-" * 92)
        print(f"JSON: {result_json}")
        print(f"CSV : {result_csv}")
        return 0
    finally:
        try:
            shutil.rmtree(temp_root, ignore_errors=True)
        except Exception:
            pass
        try:
            log_jsonl.unlink(missing_ok=True)
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
