from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"
DESTINATION = ROOT.parent / "VighnaLab_CODEX_REAUDITORIA_V3153_R1.zip"
ZIP_HASH_FILE = ROOT.parent / "VighnaLab_CODEX_REAUDITORIA_V3153_R1.zip.sha256"
MANIFEST = ARTIFACTS / "MANIFESTO_EVIDENCIAS_SHA256.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    if DESTINATION.exists() or ZIP_HASH_FILE.exists():
        raise FileExistsError("Destino já existe; recusa de sobrescrita")

    for log in (ARTIFACTS / "logs").glob("*.log"):
        raw = log.read_bytes()
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError:
            log.write_text(raw.decode("cp1252", errors="replace"), encoding="utf-8")

    members = sorted(path for path in ARTIFACTS.rglob("*") if path.is_file() and path != MANIFEST)
    manifest = {
        path.relative_to(ARTIFACTS).as_posix(): {
            "bytes": path.stat().st_size,
            "sha256": digest(path.read_bytes()),
        }
        for path in members
    }
    MANIFEST.write_text(json.dumps({
        "formato": "vighnalab-codex-evidencias-sha256-v1",
        "algoritmo": "SHA-256",
        "nota": "Integridade por hash; não é assinatura digital do EXE.",
        "arquivos": manifest,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    members.append(MANIFEST)

    with zipfile.ZipFile(DESTINATION, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(members):
            archive.write(path, arcname=path.relative_to(ARTIFACTS).as_posix())

    with zipfile.ZipFile(DESTINATION) as archive:
        names = archive.namelist()
        if archive.testzip() is not None or len(names) != len(set(names)):
            raise RuntimeError("ZIP inválido ou com nomes duplicados")
        embedded = json.loads(archive.read("MANIFESTO_EVIDENCIAS_SHA256.json"))["arquivos"]
        for name, metadata in embedded.items():
            data = archive.read(name)
            if len(data) != metadata["bytes"] or digest(data) != metadata["sha256"]:
                raise RuntimeError("Evidência divergente: " + name)

    zip_hash = digest(DESTINATION.read_bytes())
    ZIP_HASH_FILE.write_text(f"{zip_hash}  {DESTINATION.name}\n", encoding="ascii")
    print(json.dumps({
        "zip": str(DESTINATION),
        "bytes": DESTINATION.stat().st_size,
        "sha256": zip_hash,
        "arquivos": len(members),
        "integridade": "PASSOU",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
