#!/usr/bin/env python3
"""Benchmark granular do startup do VighnaStudy.

Executa uma cópia temporária do projeto, preservando o Vighna e o banco
originais. Mede Dashboard e Estatísticas por método/aba e gera CSV/JSON.

Uso recomendado na raiz C:\\SistemaEstudos:
    .venv\\Scripts\\python.exe benchmark_startup_detalhado.py --runs 2
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "dist", "build", "backups", "checkpoints",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
}


def _ignore(_dir: str, names: list[str]) -> set[str]:
    return {n for n in names if n in EXCLUDED_DIRS or n.endswith(".pyc")}


METHODS = [
    # Dashboard
    "criar_tela_inicial",
    "atualizar_dashboard",
    "atualizar_regularidade_dashboard",
    "atualizar_planejamento_dashboard",
    "atualizar_progresso_dashboard",
    "atualizar_gamificacao_dashboard",
    "atualizar_hoje_operacional_dashboard",
    # Estatísticas: construção
    "_precarregar_estatisticas_todas_abas",
    "criar_tela_estatisticas",
    "criar_aba_regularidade",
    "criar_aba_conquistas",
    "criar_aba_laboratorio_algoritmo",
    "criar_aba_mapa_dominio",
    # Estatísticas: atualização
    "atualizar_estatisticas",
    "_atualizar_resumo_estatisticas",
    "atualizar_minha_evolucao",
    "_atualizar_aba_regularidade",
    "_atualizar_aba_conquistas",
    "atualizar_laboratorio_algoritmo",
    "_atualizar_aba_estatisticas_disciplinas",
    "_atualizar_aba_mapa_dominio",
    "filtrar_mapa_dominio",
    "_atualizar_aba_estatisticas_fracos",
    "_atualizar_aba_estatisticas_recentes",
    "atualizar_evolucao_temporal",
    "atualizar_progresso_edital",
    "filtrar_progresso_edital",
]

GLOBALS = [
    # Dashboard / núcleo
    "obter_concurso_ativo",
    "obter_metricas_globais_nucleo",
    "contar_banco_erros_pendentes",
    "obter_dashboard",
    "obter_resumo_foco",
    "obter_snapshot_regularidade",
    "listar_pendencias",
    "obter_prioridades_sessao_adaptativa",
    "obter_resumo_simulados_dashboard",
    "obter_metricas_periodo_nucleo",
    "obter_configuracao_int",
    "obter_configuracao_bool",
    "obter_estado_cobertura_revisao",
    # Estatísticas
    "obter_evolucao_historica",
    "obter_analise_temporal",
    "obter_snapshot_progresso_edital",
    "build_domain_map_snapshot",
    "montar_laboratorio",
]


def _patch_main(path: Path) -> None:
    src = path.read_text(encoding="utf-8")

    src = (
        "import os as _bench_os\n"
        "import time as _bench_time\n"
        "import json as _bench_json\n"
        "import functools as _bench_functools\n"
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
        raise RuntimeError("Não encontrei QApplication em main.py")
    src = src.replace(old, new, 1)

    profiler = f'''\n_BENCH_EVENTS = []\n_BENCH_PHASE = "construtor"\n_BENCH_DEPTH = 0\n\ndef _bench_record(nome, inicio, fim, tipo="method", extra=None, depth=0):\n    _BENCH_EVENTS.append({{\n        "nome": str(nome),\n        "tipo": str(tipo),\n        "fase": str(globals().get("_BENCH_PHASE", "")),\n        "ms": round((fim - inicio) * 1000.0, 3),\n        "depth": int(depth),\n        "extra": extra,\n    }})\n\ndef _bench_wrap_method(nome):\n    original = getattr(SistemaEstudos, nome, None)\n    if original is None or not callable(original):\n        return\n    @_bench_functools.wraps(original)\n    def wrapped(*args, **kwargs):\n        global _BENCH_DEPTH\n        depth = _BENCH_DEPTH\n        _BENCH_DEPTH += 1\n        inicio = _bench_time.perf_counter()\n        try:\n            return original(*args, **kwargs)\n        finally:\n            fim = _bench_time.perf_counter()\n            _BENCH_DEPTH -= 1\n            _bench_record("SistemaEstudos." + nome, inicio, fim, "method", depth=depth)\n    setattr(SistemaEstudos, nome, wrapped)\n\ndef _bench_wrap_global(nome):\n    original = globals().get(nome)\n    if original is None or not callable(original):\n        return\n    @_bench_functools.wraps(original)\n    def wrapped(*args, **kwargs):\n        global _BENCH_DEPTH\n        depth = _BENCH_DEPTH\n        _BENCH_DEPTH += 1\n        inicio = _bench_time.perf_counter()\n        try:\n            return original(*args, **kwargs)\n        finally:\n            fim = _bench_time.perf_counter()\n            _BENCH_DEPTH -= 1\n            _bench_record(nome, inicio, fim, "global", depth=depth)\n    globals()[nome] = wrapped\n\nfor _bench_name in {METHODS!r}:\n    _bench_wrap_method(_bench_name)\nfor _bench_name in {GLOBALS!r}:\n    _bench_wrap_global(_bench_name)\n\ndef _bench_notify(texto, percentual=None, detalhe=None):\n    global _BENCH_PHASE\n    _BENCH_PHASE = str(texto)\n    _BENCH_STAGE_MARKS.append({{\n        "texto": str(texto),\n        "percentual": percentual,\n        "t": _bench_time.perf_counter(),\n    }})\n    splash.atualizar(texto, percentual, detalhe)\n'''

    old = "janela = SistemaEstudos(pre_carregar_startup=True)"
    new = (
        "_BENCH_STAGE_MARKS = []\n"
        + profiler
        + "\n_BENCH_CTOR_T0 = _bench_time.perf_counter()\n"
        + "janela = SistemaEstudos(pre_carregar_startup=True)\n"
        + "_BENCH_CTOR_T1 = _bench_time.perf_counter()"
    )
    if old not in src:
        raise RuntimeError("Não encontrei a construção de SistemaEstudos")
    src = src.replace(old, new, 1)

    old = "    janela.precarregar_inicializacao_completa(splash.atualizar)"
    new = (
        "    _BENCH_PRELOAD_T0 = _bench_time.perf_counter()\n"
        "    janela.precarregar_inicializacao_completa(_bench_notify)\n"
        "    _BENCH_PRELOAD_T1 = _bench_time.perf_counter()"
    )
    if old not in src:
        raise RuntimeError("Não encontrei o pré-carregamento")
    src = src.replace(old, new, 1)

    old = """janela.show()\njanela.raise_()\njanela.activateWindow()\nsplash.close()\n\nsys.exit(app.exec())"""
    new = r'''_BENCH_SHOW_T0 = _bench_time.perf_counter()
janela.show()
janela.raise_()
janela.activateWindow()
QApplication.processEvents(QEventLoop.AllEvents, 250)
_BENCH_SHOW_T1 = _bench_time.perf_counter()
splash.close()

_bench_stats_diag = None
try:
    _bench_stats_diag = janela._estado_estatisticas.diagnostico()
except Exception:
    pass

_bench_tables = {}
try:
    for _attr in dir(janela):
        if not _attr.startswith("tabela_"):
            continue
        try:
            _obj = getattr(janela, _attr)
            if hasattr(_obj, "rowCount") and hasattr(_obj, "columnCount"):
                _bench_tables[_attr] = {
                    "rows": int(_obj.rowCount()),
                    "cols": int(_obj.columnCount()),
                }
        except Exception:
            pass
except Exception:
    pass

_bench_log = _bench_os.environ.get("VIGHNA_BENCH_LOG")
if _bench_log:
    _bench_record = {
        "process_t0": _BENCH_PROCESS_T0,
        "before_qapp": _BENCH_BEFORE_QAPP,
        "after_qapp": _BENCH_AFTER_QAPP,
        "ctor_t0": _BENCH_CTOR_T0,
        "ctor_t1": _BENCH_CTOR_T1,
        "preload_t0": globals().get("_BENCH_PRELOAD_T0", _BENCH_CTOR_T1),
        "preload_t1": globals().get("_BENCH_PRELOAD_T1", _BENCH_CTOR_T1),
        "show_t0": _BENCH_SHOW_T0,
        "show_t1": _BENCH_SHOW_T1,
        "stages": _BENCH_STAGE_MARKS,
        "events": _BENCH_EVENTS,
        "estatisticas_diagnostico": _bench_stats_diag,
        "tabelas": _bench_tables,
    }
    with open(_bench_log, "a", encoding="utf-8") as _f:
        _f.write(_bench_json.dumps(_bench_record, ensure_ascii=False) + "\n")

QTimer.singleShot(180, app.quit)
sys.exit(app.exec())'''
    if old not in src:
        raise RuntimeError("Não encontrei o bloco final de exibição")
    src = src.replace(old, new, 1)
    path.write_text(src, encoding="utf-8")


def _find_stage_time(stages: list[dict], prefix: str) -> float | None:
    for item in stages:
        if str(item.get("texto", "")).startswith(prefix):
            return float(item["t"])
    return None


def _ms(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    return round((b - a) * 1000.0, 3)


def _top_level(rec: dict, run_no: int, wall_ms: float) -> dict:
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
        "rodada": run_no,
        "imports_bootstrap_ms": _ms(rec["process_t0"], rec["before_qapp"]),
        "qapplication_ms": _ms(rec["before_qapp"], rec["after_qapp"]),
        "construtor_ms": _ms(rec["ctor_t0"], rec["ctor_t1"]),
        "preload_ms": _ms(rec["preload_t0"], rec["preload_t1"]),
        "dashboard_ms": _ms(t_dash, t_disc),
        "disciplinas_ms": _ms(t_disc, t_central),
        "central_ms": _ms(t_central, t_resumo),
        "resumo_ms": _ms(t_resumo, t_cal),
        "calendario_ms": _ms(t_cal, t_sessao),
        "sessao_ms": _ms(t_sessao, t_stats),
        "estatisticas_ms": _ms(t_stats, t_reports),
        "relatorios_ms": _ms(t_reports, t_final),
        "finalizacao_ms": _ms(t_final, t_ready),
        "show_ms": _ms(rec["show_t0"], rec["show_t1"]),
        "total_ate_paint_ms": _ms(rec["process_t0"], rec["show_t1"]),
        "wall_ms": round(wall_ms, 3),
    }


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields = []
    for row in rows:
        for k in row:
            if k not in fields:
                fields.append(k)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter=";")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=2, help="rodadas (padrão: 2)")
    args = parser.parse_args()
    runs = max(1, min(5, args.runs))

    root = Path(__file__).resolve().parent
    required = [root / "main.py", root / "estudos.db", root / "VighnaStudy.spec"]
    missing = [p.name for p in required if not p.exists()]
    if missing:
        print("Execute este script na raiz do VighnaStudy. Faltando:", ", ".join(missing))
        return 2

    stamp = time.strftime("%Y%m%d_%H%M%S")
    result_json = root / f"benchmark_detalhado_{stamp}.json"
    result_top = root / f"benchmark_detalhado_topo_{stamp}.csv"
    result_events = root / f"benchmark_detalhado_eventos_{stamp}.csv"
    result_summary = root / f"benchmark_detalhado_resumo_{stamp}.csv"
    result_tables = root / f"benchmark_detalhado_tabelas_{stamp}.csv"
    log_jsonl = Path(tempfile.gettempdir()) / f"vighna_deep_bench_{stamp}.jsonl"
    temp_root = Path(tempfile.mkdtemp(prefix="vighna_deep_benchmark_"))

    print(f"Cópia temporária: {temp_root}")
    print("O Vighna e o banco originais não serão alterados.")
    shutil.copytree(root, temp_root, dirs_exist_ok=True, ignore=_ignore)
    original_db = root / "estudos.db"
    bench_db = temp_root / "estudos.db"
    _patch_main(temp_root / "main.py")

    top_rows: list[dict] = []
    event_rows: list[dict] = []
    table_rows: list[dict] = []
    records: list[dict] = []

    try:
        for run_no in range(1, runs + 1):
            shutil.copy2(original_db, bench_db)
            env = os.environ.copy()
            env["VIGHNA_BENCH_LOG"] = str(log_jsonl)
            before = len(log_jsonl.read_text(encoding="utf-8").splitlines()) if log_jsonl.exists() else 0

            print(f"Rodada {run_no}/{runs} ...", flush=True)
            t0 = time.perf_counter()
            proc = subprocess.run(
                [sys.executable, str(temp_root / "main.py")],
                cwd=str(temp_root),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300,
            )
            wall_ms = (time.perf_counter() - t0) * 1000.0
            lines = log_jsonl.read_text(encoding="utf-8").splitlines() if log_jsonl.exists() else []
            if proc.returncode != 0 or len(lines) <= before:
                print("Falha na rodada.")
                if proc.stdout.strip():
                    print("STDOUT:\n", proc.stdout[-6000:])
                if proc.stderr.strip():
                    print("STDERR:\n", proc.stderr[-6000:])
                return proc.returncode or 3

            rec = json.loads(lines[-1])
            records.append(rec)
            top_rows.append(_top_level(rec, run_no, wall_ms))

            for i, ev in enumerate(rec.get("events") or [], 1):
                event_rows.append({
                    "rodada": run_no,
                    "ordem": i,
                    "fase": ev.get("fase", ""),
                    "tipo": ev.get("tipo", ""),
                    "nome": ev.get("nome", ""),
                    "ms": ev.get("ms"),
                    "depth": ev.get("depth"),
                })

            for nome, dims in sorted((rec.get("tabelas") or {}).items()):
                table_rows.append({
                    "rodada": run_no,
                    "tabela": nome,
                    "linhas": dims.get("rows"),
                    "colunas": dims.get("cols"),
                    "celulas": int(dims.get("rows") or 0) * int(dims.get("cols") or 0),
                })

        grouped: dict[tuple[str, str, str], list[float]] = defaultdict(list)
        counts: dict[tuple[str, str, str], list[int]] = defaultdict(list)
        for run_no in range(1, runs + 1):
            per_run: dict[tuple[str, str, str], list[float]] = defaultdict(list)
            for row in event_rows:
                if row["rodada"] == run_no and isinstance(row.get("ms"), (int, float)):
                    key = (row["fase"], row["tipo"], row["nome"])
                    per_run[key].append(float(row["ms"]))
            for key, vals in per_run.items():
                grouped[key].append(sum(vals))
                counts[key].append(len(vals))

        summary_rows = []
        for key, totals in grouped.items():
            fase, tipo, nome = key
            summary_rows.append({
                "fase": fase,
                "tipo": tipo,
                "nome": nome,
                "mediana_ms_por_rodada": round(statistics.median(totals), 3),
                "min_ms": round(min(totals), 3),
                "max_ms": round(max(totals), 3),
                "chamadas_mediana": round(statistics.median(counts[key]), 1),
            })
        summary_rows.sort(key=lambda r: float(r["mediana_ms_por_rodada"]), reverse=True)

        payload = {
            "gerado_em": time.strftime("%Y-%m-%d %H:%M:%S"),
            "python": sys.executable,
            "runs": runs,
            "topo": top_rows,
            "resumo_eventos": summary_rows,
            "estatisticas_diagnostico": [r.get("estatisticas_diagnostico") for r in records],
            "tabelas": table_rows,
        }
        result_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        _write_csv(result_top, top_rows)
        _write_csv(result_events, event_rows)
        _write_csv(result_summary, summary_rows)
        _write_csv(result_tables, table_rows)

        print("\nMAIORES CUSTOS INSTRUMENTADOS (mediana por rodada)")
        print("-" * 110)
        for r in summary_rows[:25]:
            print(f"{r['mediana_ms_por_rodada']:10.1f} ms | {r['fase'][:32]:32s} | {r['nome']}")
        print("-" * 110)
        print("Arquivos gerados:")
        print(result_summary)
        print(result_top)
        print(result_tables)
        print(result_json)
        print("\nEnvie preferencialmente o arquivo 'benchmark_detalhado_resumo_*.csv'.")
        return 0
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
        try:
            log_jsonl.unlink(missing_ok=True)
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
