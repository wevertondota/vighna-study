from __future__ import annotations

import os
import shutil
import sqlite3
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
ESSENCIAIS = {"disciplinas", "topicos", "revisoes"}


def fmt_data(ts: float) -> str:
    try:
        return datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        return "—"


def validar_db(caminho: Path) -> tuple[bool, str]:
    caminho = Path(caminho)
    if not caminho.exists() or not caminho.is_file():
        return False, "arquivo inexistente"
    con = None
    try:
        uri = caminho.resolve().as_uri() + "?mode=ro"
        con = sqlite3.connect(uri, uri=True, timeout=5)
        resultado = con.execute("PRAGMA integrity_check").fetchone()
        if not resultado or str(resultado[0]).strip().lower() != "ok":
            return False, f"integrity_check: {resultado[0] if resultado else 'sem resultado'}"
        tabelas = {
            str(linha[0])
            for linha in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        faltantes = ESSENCIAIS - tabelas
        if faltantes:
            return False, "estrutura incompleta: " + ", ".join(sorted(faltantes))
        return True, "OK"
    except sqlite3.Error as erro:
        return False, str(erro)
    finally:
        if con is not None:
            try:
                con.close()
            except Exception:
                pass


def bancos_ativos() -> list[Path]:
    candidatos = [BASE / "estudos.db", BASE / "dist" / "SistemaEstudos" / "estudos.db"]
    return [p for p in candidatos if p.exists()]


def backups_candidatos() -> list[tuple[str, Path, float]]:
    itens: list[tuple[str, Path, float]] = []
    pastas = [BASE / "backups", BASE / "dist" / "SistemaEstudos" / "backups"]
    vistos: set[Path] = set()
    for pasta in pastas:
        if not pasta.exists():
            continue
        for p in pasta.glob("estudos_*.db"):
            try:
                rp = p.resolve()
                if rp in vistos:
                    continue
                vistos.add(rp)
                itens.append(("backup", p, p.stat().st_mtime))
            except OSError:
                pass
    return itens


def checkpoints_candidatos() -> list[tuple[str, Path, float]]:
    itens: list[tuple[str, Path, float]] = []
    pastas = [BASE / "checkpoints", BASE / "dist" / "SistemaEstudos" / "checkpoints"]
    vistos: set[Path] = set()
    for pasta in pastas:
        if not pasta.exists():
            continue
        for p in pasta.glob("VighnaStudy_checkpoint_*.zip"):
            try:
                rp = p.resolve()
                if rp in vistos:
                    continue
                vistos.add(rp)
                with zipfile.ZipFile(p, "r") as z:
                    if "estudos.db" in z.namelist():
                        itens.append(("checkpoint", p, p.stat().st_mtime))
            except Exception:
                pass
    return itens


def extrair_checkpoint_temporario(zip_path: Path, pasta: Path) -> Path:
    destino = pasta / "estudos_checkpoint.db"
    with zipfile.ZipFile(zip_path, "r") as z:
        dados = z.read("estudos.db")
        destino.write_bytes(dados)
    return destino


def preservar_corrompido(alvo: Path) -> Path:
    pasta = BASE / "recuperacao_banco"
    pasta.mkdir(parents=True, exist_ok=True)
    carimbo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    rotulo = "dist" if "dist" in alvo.parts else "raiz"
    destino = pasta / f"estudos_corrompido_{carimbo}_{rotulo}.db"
    shutil.copy2(alvo, destino)
    for sufixo in ("-wal", "-shm"):
        origem_extra = Path(str(alvo) + sufixo)
        if origem_extra.exists():
            shutil.copy2(origem_extra, Path(str(destino) + sufixo))
    return destino


def restaurar_para(alvo: Path, origem_db: Path) -> None:
    alvo.parent.mkdir(parents=True, exist_ok=True)
    temp = alvo.with_name(alvo.name + ".recuperacao.tmp")
    shutil.copy2(origem_db, temp)
    ok, msg = validar_db(temp)
    if not ok:
        temp.unlink(missing_ok=True)
        raise RuntimeError(f"A cópia temporária não é íntegra: {msg}")
    for sufixo in ("-wal", "-shm"):
        Path(str(alvo) + sufixo).unlink(missing_ok=True)
    os.replace(temp, alvo)


def main() -> int:
    print("\n============================================================")
    print("       VighnaStudy — Recuperação segura do estudos.db")
    print("============================================================\n")
    print(f"Pasta do projeto: {BASE}\n")

    ativos = bancos_ativos()
    if not ativos:
        print("Nenhum estudos.db foi encontrado na raiz ou no executável.")
        return 2

    status_ativos: list[tuple[Path, bool, str]] = []
    print("Bancos encontrados:")
    for p in ativos:
        ok, msg = validar_db(p)
        status_ativos.append((p, ok, msg))
        print(f"  [{'OK' if ok else 'ERRO'}] {p}")
        print(f"       {msg}")
    print()

    corrompidos = [p for p, ok, _ in status_ativos if not ok]
    if not corrompidos:
        print("Todos os bancos encontrados passaram no PRAGMA integrity_check.")
        print("Nenhuma restauração foi feita.")
        return 0

    validos: list[tuple[float, str, Path, Path | None]] = []

    # Um banco ativo íntegro também pode recuperar o outro alvo.
    for p, ok, _ in status_ativos:
        if ok:
            validos.append((p.stat().st_mtime, "banco ativo íntegro", p, None))

    for tipo, p, ts in backups_candidatos():
        ok, msg = validar_db(p)
        if ok:
            validos.append((ts, tipo, p, None))

    tempdirs: list[tempfile.TemporaryDirectory] = []
    for tipo, p, ts in checkpoints_candidatos():
        try:
            td = tempfile.TemporaryDirectory(prefix="vighna_recovery_")
            tempdirs.append(td)
            extraido = extrair_checkpoint_temporario(p, Path(td.name))
            ok, msg = validar_db(extraido)
            if ok:
                validos.append((ts, tipo, p, extraido))
        except Exception:
            continue

    validos.sort(key=lambda x: x[0], reverse=True)

    if not validos:
        print("Não encontrei backup/checkpoint íntegro automaticamente.")
        print("Os bancos corrompidos NÃO foram alterados.")
        print("Envie o conteúdo das pastas backups e checkpoints para análise.")
        for td in tempdirs:
            td.cleanup()
        return 3

    print("Fontes íntegras encontradas (mais recente primeiro):")
    for i, (ts, tipo, p, _) in enumerate(validos[:12], start=1):
        print(f"  {i:>2}. {fmt_data(ts)} | {tipo} | {p}")

    escolhido = validos[0]
    print("\nFonte sugerida:")
    print(f"  {fmt_data(escolhido[0])} | {escolhido[1]} | {escolhido[2]}")
    resposta = input("\nRestaurar os bancos corrompidos usando esta fonte? [S/N]: ").strip().lower()
    if resposta not in {"s", "sim", "y", "yes"}:
        print("Operação cancelada. Nenhum banco foi alterado.")
        for td in tempdirs:
            td.cleanup()
        return 0

    origem_db = escolhido[3] if escolhido[3] is not None else escolhido[2]

    for alvo in corrompidos:
        preservado = preservar_corrompido(alvo)
        print(f"\nCópia bruta preservada em: {preservado}")
        restaurar_para(alvo, origem_db)
        ok, msg = validar_db(alvo)
        if not ok:
            raise RuntimeError(f"Restauração de {alvo} não passou na validação: {msg}")
        print(f"Restaurado e validado: {alvo}")

    print("\nRECUPERAÇÃO CONCLUÍDA COM SUCESSO.")
    print("Abra primeiro com: python main.py")
    for td in tempdirs:
        td.cleanup()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nOperação cancelada.")
        raise SystemExit(130)
    except Exception as erro:
        print(f"\nERRO NA RECUPERAÇÃO: {erro}")
        raise SystemExit(1)
