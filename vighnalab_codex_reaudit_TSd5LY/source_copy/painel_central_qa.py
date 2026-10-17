# -*- coding: utf-8 -*-
"""Central de homologação automatizada do VighnaLab.

Somente fontes do painel em cópia temporária, dados sintéticos e evidências locais.
NÃO instala, NÃO conecta à nuvem, NÃO acessa o banco pessoal e NÃO aprova G7.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from contextlib import closing
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import stat
import subprocess
import sys
import tempfile
import zipfile

ENGINE_VERSION = "1.5"
PROFILES = ("integridade", "regressoes", "sqlite", "g7", "g7_seguranca", "g7_prontidao", "ntfs", "dpi", "pyinstaller", "diagnosticos_exe")
STATUS_VALUES = frozenset(("PASSOU", "PASSOU_COM_RESSALVAS", "PENDENTE", "IGNORADO", "FALHOU"))
REGRESSION_MODULES = (
    "test_painel_atualizador", "test_painel_reconciliacao", "test_historico_v2b",
    "test_painel_v3", "test_painel_core", "test_painel_g7",
    "test_painel_central_qa",
)
# Arquivos de código e dados públicos do painel; nunca copiar bancos, EXEs,
# backups, históricos, configurações pessoais ou o programa VighnaStudy.
FIXED_DATA = (
    "PAINEL_VERSAO.json", "estado_planejamento_v3.json",
    "estado_planejamento_v2a.json", "ESTADO_CONTINUIDADE_V2A.json",
    "ESTADO_CONTINUIDADE_V2B.json", "ESTADO_ATUAL.json",
)
MAX_FILE_BYTES = 650_000
MAX_TOTAL_BYTES = 8_000_000
MAX_LOG_BYTES = 150_000


class CentralQAError(RuntimeError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _blocked_path(path: Path) -> bool:
    if path.is_symlink():
        return True
    junction = getattr(path, "is_junction", None)
    if junction is not None and junction():
        return True
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return bool(getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _copy_sources(root: Path, clone: Path) -> dict:
    root = Path(root).absolute()
    if _blocked_path(root) or not root.is_dir():
        raise CentralQAError("Raiz do painel inválida ou redirecionada")
    if any((root / name).exists() for name in ("estudos.db", "VighnaStudy.exe")):
        raise CentralQAError("Instalação de VighnaStudy detectada: cópia recusada")
    required = ("painel_homologacao.py", "painel_atualizador.py", "painel_g7.py", "PAINEL_VERSAO.json")
    if any(not (root / name).is_file() for name in required):
        raise CentralQAError("Base do VighnaLab incompleta")
    try:
        versao = json.loads((root / "PAINEL_VERSAO.json").read_text(encoding="utf-8"))
        if versao.get("component") != "vighna-panel" or not re.fullmatch(r"3\.\d+\.\d+", versao.get("version", "")):
            raise ValueError("Versão não reconhecida")
    except (ValueError, OSError, TypeError) as exc:
        raise CentralQAError("Identidade da base inválida") from exc
    sources = sorted(p for p in root.iterdir() if p.is_file() and (p.suffix == ".py" or p.name in FIXED_DATA))
    total = 0
    hashes = {}
    clone.mkdir()
    for source in sources:
        if _blocked_path(source):
            raise CentralQAError("Fonte redirecionada ou insegura: " + source.name)
        size = source.stat().st_size
        if size > MAX_FILE_BYTES or total + size > MAX_TOTAL_BYTES:
            raise CentralQAError("Fontes excedem limites de tamanho")
        blob = source.read_bytes()
        if len(blob) != size:
            raise CentralQAError("Fonte modificada durante a leitura")
        (clone / source.name).write_bytes(blob)
        hashes[source.name] = _sha(blob)
        total += size
    return {"versao": versao["version"], "fontes": hashes, "arquivos": len(hashes)}


def _isolated_env(work: Path) -> dict:
    base = work / "PERFIL_SINTETICO"
    env = os.environ.copy()
    for key, relative in (("USERPROFILE", "home"), ("HOME", "home"),
                          ("APPDATA", "roaming"), ("LOCALAPPDATA", "local"),
                          ("TEMP", "temp"), ("TMP", "temp"), ("TMPDIR", "temp")):
        folder = base / relative
        folder.mkdir(parents=True, exist_ok=True)
        env[key] = str(folder)
    for key in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH"):
        env.pop(key, None)
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    return env


def _subprocess_test(clone: Path, env: dict, logfile: Path, modules: tuple[str, ...], *, timeout: int = 150) -> dict:
    # Em PyInstaller, sys.executable aponta para o próprio EXE, não python.exe.
    # Sem interpretador externo explicitamente homologado, nunca executar
    # o EXE com argumentos de unittest; registrar pendência verificável.
    if getattr(sys, "frozen", False):
        result = {"status": "PENDENTE", "motivo": "Regressões externas exigem interpretador Python isolado; EXE congelado não é python.exe", "log": logfile.name}
        _write_json(logfile, result)
        return result
    command = [sys.executable, "-B", "-m", "unittest", "-v", *modules]
    try:
        proc = subprocess.run(command, cwd=clone, env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=timeout, check=False)
        output = ((proc.stdout or "") + "\n" + (proc.stderr or ""))[:MAX_LOG_BYTES]
        logfile.write_text(output, encoding="utf-8")
        n = re.search(r"Ran (\d+) tests?", output)
        skips = re.search(r"skipped=(\d+)", output)
        ignored = [line.strip()[:240] for line in output.splitlines() if " ... skipped " in line]
        count = int(n.group(1)) if n else None
        skipped = int(skips.group(1)) if skips else 0
        return {"status": "PASSOU_COM_RESSALVAS" if proc.returncode == 0 and n and skipped else
                "PASSOU" if proc.returncode == 0 and n else "FALHOU",
                "executados":count, "aprovados":count-skipped if count is not None and proc.returncode == 0 else None,
                "ignorados":skipped, "testes_ignorados":ignored,
                "codigo": proc.returncode, "log": logfile.name}
    except subprocess.TimeoutExpired:
        logfile.write_text("TIMEOUT da suíte isolada\n", encoding="utf-8")
        return {"status": "FALHOU", "motivo": "timeout", "log": logfile.name}
    except OSError as exc:
        logfile.write_text("Falha ao iniciar subprocesso: " + type(exc).__name__, encoding="utf-8")
        return {"status": "FALHOU", "motivo": type(exc).__name__, "log": logfile.name}


def _synthetic_sqlite(work: Path, logfile: Path) -> dict:
    data_dir = work / "SQLITE_SINTETICO"
    data_dir.mkdir()
    original = data_dir / "laboratorio.db"
    backup = data_dir / "backup.db"
    restored = data_dir / "restaurado.db"
    conn = sqlite3.connect(original)
    try:
        conn.execute("CREATE TABLE verificacoes (id INTEGER PRIMARY KEY, valor TEXT NOT NULL)")
        conn.executemany("INSERT INTO verificacoes(valor) VALUES (?)", [(f"SINTETICO-{i:02d}",) for i in range(25)])
        conn.commit()
        with closing(sqlite3.connect(backup)) as dest:
            conn.backup(dest)
    finally:
        conn.close()
    original_sha = _sha(original.read_bytes())
    with closing(sqlite3.connect(backup)) as src, closing(sqlite3.connect(restored)) as target:
        src.backup(target)
    with closing(sqlite3.connect(restored)) as recovered:
        integrity = recovered.execute("PRAGMA integrity_check").fetchone()[0]
        count = recovered.execute("SELECT count(*) FROM verificacoes").fetchone()[0]
    identical = _sha(backup.read_bytes()) == _sha(restored.read_bytes())
    pristine = _sha(original.read_bytes()) == original_sha
    good = integrity == "ok" and count == 25 and identical and pristine
    logfile.write_text(json.dumps({"integridade": integrity, "registros": count,
                                   "copia_igual": identical, "original_intocado": pristine}, indent=2), encoding="utf-8")
    return {"status": "PASSOU" if good else "FALHOU", "registros": count,
            "integridade": integrity, "log": logfile.name, "backup": "sintético; não é backup pessoal"}


def _native_dpi(logfile: Path) -> dict:
    """Mede DPI corrente. Uma leitura nunca certifica 100%,125%,150% simultaneamente."""
    if sys.platform != "win32":
        result = {"status":"PENDENTE", "motivo":"DPI nativo somente Windows", "log": logfile.name}
    else:
        try:
            import ctypes
            dpi = int(ctypes.windll.user32.GetDpiForSystem())
            if dpi < 72 or dpi > 960:
                result = {"status":"FALHOU", "motivo":"DPI retornado inválido", "dpi_sistema": dpi, "log": logfile.name}
            else:
                result = {"status":"PASSOU_COM_RESSALVAS", "dpi_sistema": dpi,
                          "escala_atual_percentual": round(dpi * 100 / 96, 1),
                          "dpis_ainda_nao_homologados": [v for v in (96, 120, 144) if v != dpi],
                          "limite":"Mede somente escala atual; não altera DPI e não certifica layouts a 125/150%",
                          "log": logfile.name}
        except (AttributeError, OSError, ValueError) as exc:
            result = {"status":"PENDENTE", "motivo":type(exc).__name__, "log": logfile.name}
    _write_json(logfile, result)
    return result


def _native_ntfs(work: Path, logfile: Path) -> dict:
    """Testa junction somente entre subpastas descartáveis; não utiliza fontes reais."""
    if sys.platform != "win32":
        result = {"status":"PENDENTE", "motivo":"junction NTFS exige Windows", "log":logfile.name}
        _write_json(logfile, result)
        return result
    # Caminhos em TEMP criado pelo executor: nunca apontar para disco do usuário.
    root = work / "NTFS_SINTETICO"
    root.mkdir()
    target = root / "destino"
    target.mkdir()
    sentinel = target / "SENTINELA_NAO_APAGAR.txt"
    sentinel.write_text("VIGHNA-QA-JUNCTION-ISOLADA\n", encoding="utf-8")
    before = _sha(sentinel.read_bytes())
    link = root / "atalho_junction"
    # cmd /d /c é obrigatório: mklink é comando interno do cmd.exe.
    # subprocess recebe argumentos separados: não encapsular todo o comando em
    # uma única string (cmd.exe pode interpretar as aspas de forma incorreta).
    # As duas rotas são sempre originadas do TEMP descartável deste perfil.
    command = ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)]
    try:
        proc = subprocess.run(command, cwd=root,
                              capture_output=True, text=True, encoding="utf-8", errors="replace",
                              stdin=subprocess.DEVNULL, timeout=15, check=False)
        data = {"comando":"cmd.exe /d /c mklink /J <link_TEMP> <destino_TEMP>",
                "argumentos_separados": True, "codigo_criacao":proc.returncode,
                "saida":((proc.stdout or "") + (proc.stderr or ""))[:1600], "log":logfile.name}
        if proc.returncode != 0 or not link.exists():
            data.update(status="PENDENTE", motivo="Não foi possível criar junction de teste; examinar código e saída")
        else:
            recognized = _blocked_path(link)
            source_blocked = False
            try:
                _copy_sources(link, root / "copia_bloqueada")
            except CentralQAError as exc:
                # Rejeição por falta de fontes não prova proteção contra junction.
                source_blocked = "redirecionada" in str(exc)
            intact = sentinel.is_file() and _sha(sentinel.read_bytes()) == before
            data.update(junction_detectada=recognized, copia_redirecionada_bloqueada=source_blocked,
                        arquivo_sentinela_intacto=intact)
            data["status"] = "PASSOU" if all((recognized, source_blocked, intact)) else "FALHOU"
    except (OSError, subprocess.TimeoutExpired) as exc:
        data = {"status":"PENDENTE", "motivo":type(exc).__name__, "log":logfile.name}
    finally:
        # Não seguir a junction para apagar o destino: usar rmdir no próprio link.
        if link.is_junction() if hasattr(link, "is_junction") else False:
            try: link.rmdir()
            except OSError: pass
    if sentinel.is_file() and _sha(sentinel.read_bytes()) != before:
        data.update(status="FALHOU", motivo="Sentinela alterada")
    _write_json(logfile, data)
    return data


def _g7_safety(work: Path, clone: Path, logfile: Path) -> dict:
    """Exercita bloqueios documentais com evidências fabricadas; nunca acessa G5/G6 reais."""
    import warnings
    try:
        spec = importlib.util.spec_from_file_location("painel_g7_isolado_qa", clone / "painel_g7.py")
        if spec is None or spec.loader is None:
            raise CentralQAError("Módulo G7 indisponível no clone")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sandbox = work / "G7_SEGURANCA_SINTETICA"
        sandbox.mkdir()
        checks = {}
        empty = module.evaluate(sandbox, {"gates": []})
        checks["sem_evidencias_nao_autoriza"] = empty.get("instalacao_autorizada") is False and empty.get("gate_g7_aprovado") is False
        for test, payload in (
            ("travessia", [("../FORA.txt", b"SINTETICO"), ("MANIFESTO_SHA256.json", b"{}")]),
            ("hash_divergente", [("DADO.json", b"DADO"), ("MANIFESTO_SHA256.json", b'{"DADO.json":"' + b"0" * 64 + b'"}')]),
            ("duplicidade", [("REPETIDO.json", b"A"), ("REPETIDO.json", b"B"), ("MANIFESTO_SHA256.json", b"{}")]),
        ):
            bad = sandbox / (test + ".zip")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                with zipfile.ZipFile(bad, "w", compression=zipfile.ZIP_DEFLATED) as z:
                    for name, payload_bytes in payload:
                        z.writestr(name, payload_bytes)
            blocked = False
            try:
                module._load_zip(bad, _sha(bad.read_bytes()))
            except module.G7EvidenceError:
                blocked = True
            checks["zip_" + test + "_bloqueado"] = blocked
        data = {"status":"PASSOU_COM_RESSALVAS" if all(checks.values()) else "FALHOU",
                "verificacoes_sinteticas":checks, "g7_formal_aprovado":False,
                "limite":"Somente documentos sintéticos; não verifica evidências G5/G6 e nem backup real",
                "log":logfile.name}
    except (OSError, ValueError, TypeError, CentralQAError, AttributeError, ImportError) as exc:
        data = {"status":"FALHOU", "motivo":type(exc).__name__+": "+str(exc)[:300], "log":logfile.name}
    _write_json(logfile, data)
    return data



def _g7_readiness(clone: Path, logfile: Path) -> dict:
    """Prepara requisitos G7, sempre sem examinar backups/evidências pessoais.

    A lista é retirada do módulo G7 do CLONE, não de arquivos do usuário.
    Os hashes são identificadores de evidências documentais anteriormente
    fixadas pelo projeto, não comprovação da autoria dos respectivos ZIPs.
    """
    try:
        spec = importlib.util.spec_from_file_location("painel_g7_prontidao_qa", clone / "painel_g7.py")
        if spec is None or spec.loader is None:
            raise CentralQAError("Avaliador documental G7 indisponível")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        reference = getattr(module, "REFERENCE", None)
        required = ("G6-A", "G6-B1", "G6-B2")
        if not isinstance(reference, dict) or set(required) - set(reference):
            raise CentralQAError("Referências G6 incompletas no avaliador")
        proof = {}
        for stage in required:
            filename, checksum = reference[stage]
            if (not isinstance(filename, str) or not filename.endswith(".zip")
                    or "/" in filename or "\\" in filename or filename.startswith(".")
                    or not isinstance(checksum, str) or re.fullmatch(r"[0-9a-f]{64}", checksum) is None):
                raise CentralQAError("Referência documental insegura")
            proof[stage] = {"arquivo_exigido": filename, "sha256_referencia": checksum,
                            "verificado_nesta_execucao": False}
        plan = {
            "status": "PENDENTE",
            "preparacao_documental": "PASSOU",
            "evidencias_g6_exigidas": proof,
            "gates_anteriores": {stage: "NAO_VERIFICADO" for stage in ("G1", "G2", "G3", "G4", "G5")},
            "aceite_formal_g5_g6": "NAO_VERIFICADO",
            "backup_nuvem_real": "NAO_ACESSADO",
            "restauracao_isolada_real": "NAO_EXECUTADA",
            "integridade_banco_real": "NAO_VERIFICADA",
            "g7_formal_aprovado": False,
            "instalacao_autorizada": False,
            "orientacao": [
                "Obter as três evidências G6 previamente revisadas, sem editar os originais.",
                "Conferir hashes e aceites formais G5/G6 em avaliação independente.",
                "Para backup em nuvem, baixar uma cópia para laboratório isolado após escolha explícita do usuário.",
                "Restaurar essa cópia somente em destino novo e vazio, sem substituir bancos existentes.",
                "Verificar integridade, consistência e registros na cópia restaurada; preservar backup original.",
                "O aceite G7 depende de revisão humana; este perfil nunca autoriza instalação."
            ],
            "limite": "Somente inventário de requisitos do código G7 em clone; nenhuma evidência real ou nuvem inspecionada",
            "log": logfile.name,
        }
    except (OSError, ValueError, TypeError, AttributeError, ImportError, CentralQAError) as exc:
        plan = {"status": "FALHOU", "motivo": type(exc).__name__ + ": " + str(exc)[:180], "log": logfile.name,
                "g7_formal_aprovado": False, "instalacao_autorizada": False}
    _write_json(logfile, plan)
    return plan


def _pyinstaller(work: Path, clone: Path, env: dict, logfile: Path) -> dict:
    """Build smoke opcional, nunca instala PyInstaller ou compila VighnaStudy."""
    if getattr(sys, "frozen", False):
        result = {"status": "PENDENTE", "motivo": "Build Python externo indisponível no EXE congelado; executar kit PyInstaller isolado", "log": logfile.name}
        _write_json(logfile, result)
        return result
    if sys.platform != "win32":
        data = {"status":"PENDENTE", "motivo":"PyInstaller Windows só é testado no Windows", "log":logfile.name}
        _write_json(logfile, data)
        return data
    if importlib.util.find_spec("PyInstaller") is None:
        data = {"status":"PENDENTE", "motivo":"PyInstaller não instalado neste Python; nenhuma instalação automática",
                "preflight": {"windows": True, "python": sys.version.split()[0],
                              "pyinstaller_disponivel": False, "build_executado": False,
                              "requer_acao_explicita_para_instalar_dependencia": True}, "log":logfile.name}
        _write_json(logfile, data)
        return data
    script = work / "SMOKE_IMPORTACOES_QA.py"
    script.write_text("import painel_central_qa, painel_homologacao\n"
                      "assert len(painel_central_qa.PROFILES) >= 8\n"
                      "print('VIGHNALAB_QA_BUILD_SMOKE_OK')\n", encoding="utf-8")
    buildroot = work / "PYINSTALLER_SINTETICO"
    buildroot.mkdir()
    executable = buildroot / "dist" / "VighnaLab_QA_SOMENTE_TESTE" / "VighnaLab_QA_SOMENTE_TESTE.exe"
    compile_env = dict(env)
    compile_env["PYINSTALLER_CONFIG_DIR"] = str(buildroot / "pyinstaller_config")
    cmd = [sys.executable, "-B", "-m", "PyInstaller", "--onedir", "--noconfirm", "--noupx",
           "--name", "VighnaLab_QA_SOMENTE_TESTE", "--distpath", str(buildroot / "dist"),
           "--workpath", str(buildroot / "build"), "--specpath", str(buildroot / "spec"),
           "--paths", str(clone), str(script)]
    try:
        proc = subprocess.run(cmd, cwd=work, env=compile_env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=200, check=False)
        logfile.write_text((proc.stdout or "")[-6000:] + "\n" + (proc.stderr or "")[-30000:], encoding="utf-8")
        if proc.returncode != 0 or not executable.is_file():
            return {"status":"FALHOU", "motivo":"Compilação PyInstaller falhou", "codigo":proc.returncode, "log":logfile.name}
        smoke = subprocess.run([str(executable)], cwd=work, env=compile_env, stdin=subprocess.DEVNULL,
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=35, check=False)
        success = smoke.returncode == 0 and "VIGHNALAB_QA_BUILD_SMOKE_OK" in smoke.stdout
        return {"status":"PASSOU_COM_RESSALVAS" if success else "FALHOU", "codigo":smoke.returncode,
                "preflight": {"windows": True, "python": sys.version.split()[0],
                              "pyinstaller_disponivel": True, "build_executado": True},
                "smoke":smoke.stdout[-500:] + smoke.stderr[-500:], "log":logfile.name,
                "limite":"Executável descartável de importação; NÃO testa o instalador final nem a GUI empacotada"}
    except (OSError, subprocess.TimeoutExpired) as exc:
        logfile.write_text("Falha/timeout na compilação sintética: " + type(exc).__name__, encoding="utf-8")
        return {"status":"FALHOU", "motivo":type(exc).__name__, "log":logfile.name}


# V3.1.52 — contrato fechado de diagnósticos do próprio executável.
# Não aceita comandos, scripts, paths, dados reais ou argumentos do usuário.
_READ_OPS = ("ping", "ambiente", "identidade", "componentes")
_READ_MARKER = "--vighnalab-qa-child"


def _readonly_child_profile(logfile: Path, env: dict, *, timeout: int = 35) -> dict:
    """Confere quatro respostas JSON do protocolo estritamente autorizado.

    Em frozen, sys.executable é o próprio EXE e SOMENTE o marcador interno
    é enviado. No Python, invoca o ponto de entrada conhecido no pacote.
    """
    frozen = bool(getattr(sys, "frozen", False))
    exe = Path(sys.executable)
    if frozen:
        prefix = [str(exe)]
    else:
        source = Path(__file__).resolve().with_name("painel_homologacao.py")
        if _blocked_path(source) or not source.is_file():
            result = {"status": "PENDENTE", "motivo": "Ponto de entrada confiável indisponível", "log": logfile.name}
            _write_json(logfile, result)
            return result
        prefix = [str(exe), "-B", str(source)]
    child_env = dict(env)
    if frozen:
        # Evitar herdar o estado do bootloader de uma execução onefile.
        child_env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
    answers = {}
    for op in _READ_OPS:
        cmd = [*prefix, _READ_MARKER, "--protocolo", "1", op]
        try:
            cp = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
                                timeout=timeout, check=False, cwd=str(logfile.parent), env=child_env)
        except (OSError, subprocess.TimeoutExpired) as exc:
            answers[op] = {"status": "FALHOU", "motivo": type(exc).__name__}
            break
        try:
            doc = json.loads(cp.stdout) if len(cp.stdout) <= 8192 else None
        except (json.JSONDecodeError, TypeError):
            doc = None
        good = (cp.returncode == 0 and not cp.stderr.strip() and isinstance(doc, dict)
                and doc.get("protocolo") == 1 and doc.get("operacao") == op
                and doc.get("resultado") == "OK" and doc.get("frozen") is frozen)
        if op == "identidade" and good:
            good = (doc.get("componente") == "vighna-panel" and
                    isinstance(doc.get("versao"), str) and
                    re.fullmatch(r"3\.1\.[0-9]+", doc["versao"]) is not None)
        if op == "componentes" and good:
            expected = ("painel_core", "painel_atualizador", "painel_central_qa", "painel_g7")
            modules = doc.get("modulos_importados")
            good = isinstance(modules, dict) and set(modules) == set(expected) and all(modules.values())
        answers[op] = {"status": "PASSOU" if good else "FALHOU", "codigo": cp.returncode,
                       "resposta": doc if good else None}
        if not good:
            break
    success = len(answers) == len(_READ_OPS) and all(v["status"] == "PASSOU" for v in answers.values())
    result = {"status": "PASSOU" if success else "FALHOU", "frozen": frozen,
              "operacoes": answers, "log": logfile.name,
              "limite": "Somente diagnósticos; não valida backup, rollback, G7 nem regressões externas"}
    _write_json(logfile, result)
    return result



# V3.1.53: provas de leitura de recursos públicos já empacotados na aplicação.
# Hash de REFERÊNCIA compilado na distribuição. Não autentica o distribuidor,
# não examina a pasta de trabalho, fontes externas nem dados pessoais.
FROZEN_RESOURCE_SHA256 = {'PAINEL_VERSAO.json': '91f0fbe8ed57f5d92330798e09605a1c0f2fd8d29332247cc33bc648785b8e56', 'estado_planejamento_v3.json': '3eafcf185c08b6762f78f08fe9c64f7dfd5669465ecde1580224bbd9862a989f', 'estado_planejamento_v2a.json': '773cf404cb84e01bf8fa0b585f1ca38bcfc2990c3e3310347e4f7d9ff4799420'}
FROZEN_RESOURCE_MAX_BYTES = 100_000


def _frozen_integrity(logfile: Path) -> dict:
    """Verifica recursos de leitura embutidos em sys._MEIPASS, sem caminhos externos."""
    if not getattr(sys, "frozen", False):
        result = {"status": "PENDENTE", "motivo": "Teste específico do EXE PyInstaller", "log": logfile.name}
        _write_json(logfile, result)
        return result
    root = Path(getattr(sys, "_MEIPASS", ""))
    evidence = {}
    passed = bool(root.is_dir() and not _blocked_path(root) and root != Path("."))
    for name, expected in FROZEN_RESOURCE_SHA256.items():
        file = root / name
        record = {"status": "FALHOU"}
        try:
            if not passed or _blocked_path(file) or not file.is_file():
                raise ValueError("Recurso não regular ou redirecionado")
            blob = file.read_bytes()
            if len(blob) > FROZEN_RESOURCE_MAX_BYTES:
                raise ValueError("Recurso excede o limite")
            received = _sha(blob)
            if received != expected:
                raise ValueError("Hash do recurso divergente")
            if name == "PAINEL_VERSAO.json":
                version = json.loads(blob.decode("utf-8"))
                if version != {"component": "vighna-panel", "version": "3.1.53"}:
                    raise ValueError("Identidade interna divergente")
            record = {"status": "PASSOU", "sha256": received, "bytes": len(blob)}
        except (OSError, ValueError, UnicodeError, TypeError):
            passed = False
            record = {"status": "FALHOU", "motivo": "Ausente, redirecionado ou inconsistente"}
        evidence[name] = record
    result = {"status": "PASSOU" if passed else "FALHOU", "recursos": evidence,
              "log": logfile.name, "limite": "Confere apenas recursos públicos embutidos com hashes de referência; não é assinatura digital"}
    _write_json(logfile, result)
    return result


def _frozen_sqlite_synthetic(work: Path, logfile: Path) -> dict:
    """Exercita SQLite apenas em tempfile isolado; nunca recebe caminho de usuário."""
    if not getattr(sys, "frozen", False):
        result = {"status": "PENDENTE", "motivo": "Teste específico do EXE PyInstaller", "log": logfile.name}
        _write_json(logfile, result)
        return result
    try:
        result = _synthetic_sqlite(work, logfile)
        result["execucao"] = "EXE; banco sintético descartável"
        result["dados_pessoais_utilizados"] = False
        return result
    except (OSError, sqlite3.Error, ValueError) as exc:
        result = {"status": "FALHOU", "motivo": type(exc).__name__, "log": logfile.name}
        _write_json(logfile, result)
        return result


def _manifest_zip(evidence_dir: Path, destination: Path) -> None:
    members = sorted(p for p in evidence_dir.iterdir() if p.is_file())
    manifest = {p.name: _sha(p.read_bytes()) for p in members}
    _write_json(evidence_dir / "MANIFESTO_SHA256.json", manifest)
    members.append(evidence_dir / "MANIFESTO_SHA256.json")
    temporary = destination.with_suffix(".tmp")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in members:
            z.write(p, arcname=p.name)
    with zipfile.ZipFile(temporary) as z:
        if z.testzip() is not None or len(z.namelist()) != len(set(z.namelist())):
            raise CentralQAError("Falha de integridade no ZIP de evidências")
        for name, sha in manifest.items():
            if _sha(z.read(name)) != sha:
                raise CentralQAError("Manifesto inconsistente com evidências")
    os.replace(temporary, destination)


def execute(root: Path, selected=None, on_progress=None, *, output_dir: Path | None = None) -> dict:
    """Execute perfis sequenciais em clone descartável; devolva relatório e ZIP único.

    `on_progress(name, status)` só recebe strings; widgets Tk devem ser atualizados
    na thread principal pelo chamador, nunca nesta função.
    """
    selected = tuple(selected if selected is not None else PROFILES)
    if not selected or len(selected) != len(set(selected)) or any(x not in PROFILES for x in selected):
        raise CentralQAError("Seleção de perfis inválida")
    if sys.platform == "win32":
        try:
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin():
                raise CentralQAError("Não executar como administrador")
        except AttributeError:
            pass
    root = Path(root)
    output_dir = Path(output_dir) if output_dir is not None else Path(tempfile.gettempdir()) / "VighnaLab_Homologacoes"
    # A única pasta persistente é a de saída de evidências, fora da instalação.
    if _blocked_path(output_dir) or _blocked_path(output_dir.parent):
        raise CentralQAError("Saída redirecionada: operação recusada")
    if output_dir.resolve() == root.resolve() or root.resolve() in output_dir.resolve().parents:
        raise CentralQAError("Evidências não podem ser gravadas na instalação")
    output_dir.mkdir(parents=True, exist_ok=True)
    if _blocked_path(output_dir):
        raise CentralQAError("Pasta de evidências insegura")

    with tempfile.TemporaryDirectory(prefix="vighnalab_central_isolado_") as tmp:
        work = Path(tmp)
        clone = work / "CLONE"
        evidence = work / "EVIDENCIAS"
        evidence.mkdir()
        frozen_mode = bool(getattr(sys, "frozen", False))
        if frozen_mode:
            # PyInstaller não disponibiliza fontes .py como arquivos locais.
            # Não tentar reconstituí-las, executar unittest nem acessar root.
            origin = {"versao": None, "fontes": {}, "arquivos": 0}
        else:
            origin = _copy_sources(root, clone)
        env = _isolated_env(work)
        results = {}
        for profile in selected:
            if on_progress:
                on_progress(profile, "INICIADO")
            if frozen_mode and profile == "integridade":
                results[profile] = _frozen_integrity(evidence / "RECURSOS_EMBUTIDOS.json")
            elif frozen_mode and profile == "sqlite":
                results[profile] = _frozen_sqlite_synthetic(work, evidence / "SQLITE_EXE.log")
            elif frozen_mode and profile != "diagnosticos_exe":
                results[profile] = {"status": "PENDENTE", "motivo":
                    "Perfil exige executor próprio ainda não homologado no EXE"}
            elif profile == "diagnosticos_exe":
                results[profile] = _readonly_child_profile(evidence / "DIAGNOSTICOS_EXE.json", env)
                if results[profile]["status"] == "PASSOU":
                    ident = results[profile]["operacoes"]["identidade"]["resposta"]
                    origin["versao"] = ident["versao"]
            elif profile == "integridade":
                hashes = {name: _sha((clone / name).read_bytes()) for name in origin["fontes"]}
                good = hashes == origin["fontes"]
                results[profile] = {"status": "PASSOU" if good else "FALHOU", "fontes": len(hashes)}
            elif profile == "regressoes":
                results[profile] = _subprocess_test(clone, env, evidence / "REGRESSOES.log", REGRESSION_MODULES)
            elif profile == "sqlite":
                results[profile] = _synthetic_sqlite(work, evidence / "SQLITE_SINTETICO.log")
            elif profile == "g7":
                res = _subprocess_test(clone, env, evidence / "G7_REGRESSOES.log", ("test_painel_g7",), timeout=70)
                res["g7_formal_aprovado"] = False
                res["limite"] = "Regressões documentais; G7 formal não aprovado"
                if res["status"] == "PASSOU": res["status"] = "PASSOU_COM_RESSALVAS"
                results[profile] = res
            elif profile == "g7_seguranca":
                results[profile] = _g7_safety(work, clone, evidence / "G7_SEGURANCA.json")
            elif profile == "g7_prontidao":
                results[profile] = _g7_readiness(clone, evidence / "G7_PRONTIDAO_REAL.json")
            elif profile == "ntfs":
                results[profile] = _native_ntfs(work, evidence / "JUNCTION_NTFS.json")
            elif profile == "dpi":
                results[profile] = _native_dpi(evidence / "DPI_NATIVO.json")
            elif profile == "pyinstaller":
                results[profile] = _pyinstaller(work, clone, env, evidence / "PYINSTALLER.log")
            if results[profile]["status"] not in STATUS_VALUES:
                raise CentralQAError("Resultado de perfil inválido: " + profile)
            if on_progress:
                on_progress(profile, results[profile]["status"])
        # Em frozen não se consulta raiz externa nem arquivos de usuário; os demais
        # perfis são explicitamente pendentes até homologação de executores próprios.
        # O clone não pode mudar as fontes da instalação: comparar todos os hashes de origem.
        originals_intact = (not frozen_mode and all(
            (root / name).is_file() and _sha((root / name).read_bytes()) == digest
            for name, digest in origin["fontes"].items()))
        # Em frozen não afirmar preservação de fontes que não foram examinadas.
        if frozen_mode:
            originals_intact = None
        if originals_intact is False:
            raise CentralQAError("Arquivos de origem alterados durante a execução")
        final_status = "FALHOU" if any(r["status"] == "FALHOU" for r in results.values()) else (
            "APROVADO_COM_PENDENCIAS" if any(r["status"] != "PASSOU" for r in results.values()) else "APROVADO_ESCOPO")
        report = {
            "sistema": "VighnaLab", "central": ENGINE_VERSION,
            "gerado_utc": datetime.now(timezone.utc).isoformat(),
            "versao_base": origin["versao"], "ambiente": {"plataforma": sys.platform, "python": sys.version.split()[0]},
            "perfis": results, "fontes_preservadas": originals_intact,
            "resultado": final_status, "instalacao_autorizada": False, "g7_aprovado": False,
            "resumo_estados": {status:sum(r["status"] == status for r in results.values()) for status in sorted(STATUS_VALUES)},
            "observacoes": ["Python: fontes copiadas; frozen: somente recursos internos, SQLite sintético e diagnósticos autorizados",
                            "DPI: somente medição na escala ativa; 125%/150% exigem medição própria",
                            "PyInstaller (se disponível): somente smoke descartável, não homologação final",
                            "G7 formal, gates G5/G6 e backup de nuvem continuam pendentes",
                            "Preparação G7: inventário documental; não lê evidências reais",
                            "Nenhum programa instalado, nenhum acesso automático à nuvem"],
        }
        _write_json(evidence / "RESULTADO_CENTRAL.json", report)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        destination = output_dir / f"EVIDENCIAS_CENTRAL_VIGHNALAB_{stamp}.zip"
        _manifest_zip(evidence, destination)
        return {"resultado": final_status, "arquivo": str(destination), "perfis": results,
                "versao_base": origin["versao"]}
