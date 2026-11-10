"""M12: identidade local separada do nome visível e do concurso.

Checkpoint de desenvolvimento. Por padrão só lê identidade existente;
a criação precisa de `laboratorio=True` e diretório explicitamente fornecido.
Não toca no banco de questões e não presume uma pasta Windows.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import os
import uuid

ARQUIVO = "identidade_merito_vighna_m12.json"
ESQUEMA = 1

class IdentidadeM12Invalida(RuntimeError):
    pass

@dataclass(frozen=True)
class IdentidadeM12:
    perfil_id: str
    instalacao_uuid: str
    criada_em: str
    diretorio_persistente: Path


def _canon(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def _validar(pasta: Path, dados: dict) -> IdentidadeM12:
    try:
        if set(dados) != {"schema", "app", "perfil_id", "instalacao_uuid", "criada_em", "sha256"}:
            raise ValueError("Campos inesperados")
        esperado = dados["sha256"]
        conteudo = {k: v for k, v in dados.items() if k != "sha256"}
        if dados["schema"] != ESQUEMA or dados["app"] != "VighnaStudy":
            raise ValueError("Esquema ou aplicativo errado")
        ident = uuid.UUID(dados["instalacao_uuid"])
        if ident.version != 4 or str(ident) != dados["instalacao_uuid"]:
            raise ValueError("UUID inválido")
        if dados["perfil_id"] != "vighna-" + ident.hex:
            raise ValueError("Perfil incompatível com instalação")
        datetime.fromisoformat(dados["criada_em"].replace("Z", "+00:00"))
        if not isinstance(esperado, str) or len(esperado) != 64 or sha256(_canon(conteudo)).hexdigest() != esperado:
            raise ValueError("Integridade inconsistente")
        return IdentidadeM12(dados["perfil_id"], str(ident), dados["criada_em"], pasta)
    except (TypeError, ValueError, KeyError) as exc:
        raise IdentidadeM12Invalida("Identidade inconsistente; não regenerar silenciosamente") from exc


def obter_identidade(pasta_dados: str | Path, *, criar_em_laboratorio: bool = False) -> IdentidadeM12:
    """A identidade é durável dentro de uma pasta EXPLÍCITA, fora da instalação.

    Um arquivo já existente nunca é sobrescrito. Corrupção falha fechado.
    SHA-256 detecta alterações acidentais, não prova autenticidade contra ataque.
    """
    pasta = Path(pasta_dados).expanduser().resolve(strict=False)
    caminho = pasta / ARQUIVO
    if caminho.is_symlink():
        raise IdentidadeM12Invalida("Identidade por symlink não autorizada")
    if not caminho.exists():
        if not criar_em_laboratorio:
            raise IdentidadeM12Invalida("Identidade ausente; criação só autorizada em laboratório")
        pasta.mkdir(parents=True, exist_ok=True)
        uid = uuid.uuid4()
        payload = {"schema": ESQUEMA, "app": "VighnaStudy", "perfil_id": "vighna-" + uid.hex,
                   "instalacao_uuid": str(uid),
                   "criada_em": datetime.now(timezone.utc).isoformat()}
        dados = dict(payload, sha256=sha256(_canon(payload)).hexdigest())
        dados_bytes = _canon(dados) + b"\n"
        try:
            # Criação atômica exclusiva: segunda execução não altera a primeira.
            fd = os.open(caminho, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass  # outro processo já criou; ler e conferir abaixo
        else:
            with os.fdopen(fd, 'wb') as f:
                f.write(dados_bytes)
                f.flush()
                os.fsync(f.fileno())
    if not caminho.is_file() or caminho.is_symlink():
        raise IdentidadeM12Invalida("Arquivo local ausente ou inseguro")
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IdentidadeM12Invalida("Identidade local inacessível ou corrompida") from exc
    if not isinstance(dados, dict):
        raise IdentidadeM12Invalida("Formato local inválido")
    return _validar(pasta, dados)
