from __future__ import annotations

from datetime import datetime
from pathlib import Path
import hashlib
import json
import os
import platform
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import zipfile

from versao import VIGHNA_BUILD, VIGHNA_VERSION


NOME_PASTA_CHECKPOINTS = "checkpoints"

EXTENSOES_PROJETO = {
    ".py",
    ".bat",
    ".cmd",
    ".ps1",
    ".spec",
    ".csv",
    ".ico",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".svg",
    ".txt",
    ".md",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".yaml",
    ".yml",
    ".ui",
    ".qrc",
    ".qss",
    ".css",
    ".html",
    ".sql",
}

PASTAS_RECURSIVAS_OPCIONAIS = {
    "assets",
    "resources",
    "recursos",
    "icons",
    "icones",
    "statistics_core",
}

EXTENSOES_RECURSOS = {
    ".py",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".svg",
    ".ico",
    ".json",
    ".txt",
    ".md",
    ".css",
    ".qss",
}

PASTAS_IGNORADAS = {
    ".git",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "env",
    "build",
    "dist",
    "__pycache__",
    "backups",
    NOME_PASTA_CHECKPOINTS,
}

ARQUIVOS_IGNORADOS = {
    ".env",
    "estudos.db-shm",
    "estudos.db-wal",
    # Artefatos legados/temporários não são fontes normativas do projeto.
    "MANIFEST_SHA256.txt",
    "PASSO4_DIFF_ATUAL.patch",
    "PASSO4_STATUS_ATUAL.txt",
    # Metadado interno de um checkpoint extraído na raiz do projeto.
    # Ele é recriado a cada novo ZIP e nunca deve entrar no inventário,
    # senão o ZIP acaba com duas entradas de checkpoint_manifest.json.
    "checkpoint_manifest.json",
}

TAMANHO_MAXIMO_RECURSO = 25 * 1024 * 1024
VERSAO_MANIFESTO_CHECKPOINT = 3

# Estes módulos formam o núcleo atual do VighnaStudy. O inventário dinâmico
# continua protegendo quaisquer novos .py adicionados no futuro; esta lista
# serve para bloquear a restauração de um checkpoint obviamente incompleto.
FONTES_NUCLEO_ATUAL = {
    "main.py",
    "banco.py",
    "tema.py",
    "foco.py",
    "checkpoint.py",
    "backup.py",
    "espacamento.py",
    "jogos.py",
    "importador_pdf.py",
    "inteligencia.py",
    "diagnostico.py",
    "navegacao.py",
    "jornada.py",
    "evolucao.py",
    "laboratorio.py",
    "fila_candidata.py",
    "fila_observacao.py",
    "progresso_edital.py",
    "mapa_dominio.py",
    "regularidade.py",
    "versao.py",
    "statistics_core/__init__.py",
    "statistics_core/models.py",
    "statistics_core/periods.py",
    "statistics_core/repository.py",
    "statistics_core/service.py",
}


def _tem_fontes_essenciais(pasta: Path) -> bool:
    return all(
        (pasta / nome).is_file()
        for nome in ("main.py", "banco.py", "tema.py", "foco.py")
    )


def _adicionar_candidato_e_pais(
    candidatos: list[Path],
    origem: Path,
    max_niveis: int = 7,
) -> None:
    try:
        atual = origem.resolve()
    except OSError:
        return

    for _ in range(max_niveis + 1):
        candidatos.append(atual)
        pai = atual.parent
        if pai == atual:
            break
        atual = pai


def localizar_pasta_projeto() -> Path:
    """Localiza a raiz editável do Vighna tanto em Python quanto no EXE.

    No build PyInstaller, ``__file__`` costuma apontar para ``_internal`` e o
    executável fica em ``dist/SistemaEstudos``. Os fontes, porém, continuam
    na raiz de desenvolvimento (por exemplo ``C:\\SistemaEstudos``). Por isso
    percorremos os ancestrais das origens conhecidas até encontrar os arquivos
    essenciais, sem fazer busca recursiva pelo disco.
    """
    candidatos: list[Path] = []

    try:
        _adicionar_candidato_e_pais(candidatos, Path.cwd())
    except OSError:
        pass

    try:
        _adicionar_candidato_e_pais(candidatos, Path(__file__).resolve().parent)
    except OSError:
        pass

    if getattr(sys, "frozen", False):
        try:
            _adicionar_candidato_e_pais(
                candidatos,
                Path(sys.executable).resolve().parent,
            )
        except OSError:
            pass

    vistos: set[Path] = set()

    for candidato in candidatos:
        try:
            candidato = candidato.resolve()
        except OSError:
            continue

        if candidato in vistos:
            continue
        vistos.add(candidato)

        if _tem_fontes_essenciais(candidato):
            return candidato

    # Fallback usado apenas para produzir uma mensagem diagnóstica útil.
    if getattr(sys, "frozen", False):
        try:
            return Path(sys.executable).resolve().parent
        except OSError:
            pass


    return Path(__file__).resolve().parent


def localizar_banco_ativo(pasta_projeto: Path | None = None) -> Path:
    """Retorna o banco usado pela execução atual do Vighna.

    No executável, banco.py usa a pasta do .exe. Em execução pelo fonte, usa
    a pasta do projeto. Mantemos exatamente a mesma convenção aqui para que a
    opção 'incluir banco' fotografe os dados realmente em uso.
    """
    if getattr(sys, "frozen", False):
        try:
            return Path(sys.executable).resolve().parent / "estudos.db"
        except OSError:
            pass

    pasta = pasta_projeto or localizar_pasta_projeto()
    return pasta / "estudos.db"


PASTA_PROJETO = localizar_pasta_projeto()
PASTA_CHECKPOINTS = PASTA_PROJETO / NOME_PASTA_CHECKPOINTS


def _sha256(caminho: Path) -> str:
    digest = hashlib.sha256()

    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)

    return digest.hexdigest()


def _slug(texto: str) -> str:
    texto = str(texto or "").strip().lower()
    texto = re.sub(r"[^a-z0-9áàâãéêíóôõúç]+", "-", texto, flags=re.IGNORECASE)
    texto = texto.strip("-")

    # Mantém o nome legível, mas curto o suficiente para caminhos do Windows.
    return texto[:48]


def _validar_fontes(pasta: Path) -> None:
    # Para gerar um checkpoint da versão atual, todos os módulos do núcleo
    # precisam existir. Isto impede que um ZIP aparentemente válido seja criado
    # a partir de uma pasta parcialmente copiada.
    faltantes = [
        nome
        for nome in sorted(FONTES_NUCLEO_ATUAL)
        if not (pasta / nome).is_file()
    ]

    if faltantes:
        raise FileNotFoundError(
            "Não foi possível gerar um checkpoint completo porque "
            "faltam arquivos do núcleo atual do VighnaStudy.\n\n"
            "Ausentes: " + ", ".join(faltantes) + "\n\n"
            f"Pasta verificada: {pasta}"
        )


def _arquivos_do_projeto(pasta: Path) -> list[tuple[Path, str]]:
    encontrados: list[tuple[Path, str]] = []

    for caminho in sorted(pasta.iterdir(), key=lambda p: p.name.lower()):
        if not caminho.is_file():
            continue

        if caminho.name in ARQUIVOS_IGNORADOS:
            continue

        if caminho.name == "estudos.db":
            continue

        if caminho.suffix.lower() not in EXTENSOES_PROJETO:
            continue

        encontrados.append((caminho, caminho.name))

    for nome_pasta in sorted(PASTAS_RECURSIVAS_OPCIONAIS):
        raiz = pasta / nome_pasta

        if not raiz.is_dir():
            continue

        for caminho in sorted(raiz.rglob("*"), key=lambda p: str(p).lower()):
            if not caminho.is_file():
                continue

            partes = set(caminho.relative_to(pasta).parts)
            if partes & PASTAS_IGNORADAS:
                continue

            if caminho.suffix.lower() not in EXTENSOES_RECURSOS:
                continue

            try:
                if caminho.stat().st_size > TAMANHO_MAXIMO_RECURSO:
                    continue
            except OSError:
                continue

            encontrados.append((
                caminho,
                caminho.relative_to(pasta).as_posix(),
            ))

    return encontrados


def _inventario_projeto(pasta: Path) -> dict[str, dict]:
    inventario: dict[str, dict] = {}
    for caminho, nome_zip in _arquivos_do_projeto(pasta):
        try:
            stat = caminho.stat()
            inventario[nome_zip] = {
                "sha256": _sha256(caminho),
                "tamanho_bytes": stat.st_size,
            }
        except OSError:
            continue
    return inventario


def _snapshot_banco(origem: Path, destino: Path) -> None:
    if not origem.is_file():
        raise FileNotFoundError(
            "O arquivo estudos.db não existe; desmarque a opção de incluir o banco "
            "ou crie/abra o banco antes de gerar o checkpoint."
        )

    origem_uri = origem.resolve().as_uri() + "?mode=ro"

    conexao_origem = sqlite3.connect(
        origem_uri,
        uri=True,
        timeout=10,
    )
    conexao_destino = sqlite3.connect(destino)

    try:
        conexao_origem.backup(conexao_destino)
        conexao_destino.commit()

        integridade = conexao_destino.execute(
            "PRAGMA integrity_check"
        ).fetchone()

        if (
            integridade is None
            or str(integridade[0]).lower() != "ok"
        ):
            raise RuntimeError(
                "A cópia temporária do banco não passou na verificação de integridade."
            )
    finally:
        conexao_destino.close()
        conexao_origem.close()


def gerar_checkpoint(
    descricao: str = "",
    incluir_banco: bool = False,
) -> dict:
    pasta = localizar_pasta_projeto()
    _validar_fontes(pasta)

    pasta_checkpoints = pasta / NOME_PASTA_CHECKPOINTS
    pasta_checkpoints.mkdir(parents=True, exist_ok=True)

    agora = datetime.now()
    identificador = agora.strftime("%Y-%m-%d_%H-%M-%S")
    sufixo = _slug(descricao)

    nome = f"VighnaStudy_checkpoint_{identificador}"
    if sufixo:
        nome += f"_{sufixo}"
    nome += ".zip"

    destino = pasta_checkpoints / nome
    temporario_zip = destino.with_suffix(".zip.tmp")

    arquivos = _arquivos_do_projeto(pasta)

    manifest_arquivos: list[dict] = []
    banco_temporario: Path | None = None
    caminho_banco_ativo: Path | None = None

    try:
        with tempfile.TemporaryDirectory(prefix="vighna_checkpoint_") as pasta_temp:
            if incluir_banco:
                banco_temporario = Path(pasta_temp) / "estudos.db"
                caminho_banco_ativo = localizar_banco_ativo(pasta)
                _snapshot_banco(
                    caminho_banco_ativo,
                    banco_temporario,
                )

            with zipfile.ZipFile(
                temporario_zip,
                "w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=6,
            ) as zip_saida:
                for caminho, nome_zip in arquivos:
                    stat = caminho.stat()
                    hash_arquivo = _sha256(caminho)

                    zip_saida.write(
                        caminho,
                        arcname=nome_zip,
                    )

                    manifest_arquivos.append({
                        "arquivo": nome_zip,
                        "tamanho_bytes": stat.st_size,
                        "sha256": hash_arquivo,
                    })

                if banco_temporario is not None:
                    stat = banco_temporario.stat()
                    hash_arquivo = _sha256(banco_temporario)

                    zip_saida.write(
                        banco_temporario,
                        arcname="estudos.db",
                    )

                    manifest_arquivos.append({
                        "arquivo": "estudos.db",
                        "tamanho_bytes": stat.st_size,
                        "sha256": hash_arquivo,
                        "snapshot_sqlite": True,
                    })

                manifesto = {
                    "formato": "VighnaStudy checkpoint",
                    "versao_manifesto": VERSAO_MANIFESTO_CHECKPOINT,
                    "vighnastudy_versao": VIGHNA_VERSION,
                    "vighnastudy_build": VIGHNA_BUILD,
                    "criado_em": agora.isoformat(timespec="seconds"),
                    "descricao": str(descricao or "").strip(),
                    "pasta_projeto_origem": str(pasta),
                    "banco_incluido": bool(incluir_banco),
                    "modo_protecao": ("completo" if incluir_banco else "codigo"),
                    "protege_fontes": True,
                    "protege_dados": bool(incluir_banco),
                    "banco_origem": (
                        str(caminho_banco_ativo)
                        if caminho_banco_ativo is not None
                        else None
                    ),
                    "python": platform.python_version(),
                    "plataforma": platform.platform(),
                    "quantidade_arquivos": len(manifest_arquivos),
                    "quantidade_fontes_recursos": len(arquivos),
                    "arquivos": manifest_arquivos,
                    "observacao": (
                        "O checkpoint preserva fontes, scripts, configurações editáveis e recursos do projeto. "
                        "Ambientes virtuais, builds, caches, backups e checkpoints anteriores são excluídos por serem reconstruíveis ou redundantes. "
                        "No modo completo, o banco SQLite ativo é incluído como snapshot consistente."
                    ),
                }

                zip_saida.writestr(
                    "checkpoint_manifest.json",
                    json.dumps(
                        manifesto,
                        ensure_ascii=False,
                        indent=2,
                    ).encode("utf-8"),
                )

        os.replace(
            temporario_zip,
            destino,
        )

        # Um checkpoint só é considerado concluído depois de ser reaberto e
        # validado contra o próprio manifesto/hashes.
        inspecionar_checkpoint(destino)

    except Exception:
        try:
            temporario_zip.unlink(missing_ok=True)
        except OSError:
            pass
        raise

    return {
        "caminho": destino,
        "nome": destino.name,
        "criado_em": agora,
        "descricao": str(descricao or "").strip(),
        "banco_incluido": bool(incluir_banco),
        "protecao_completa": bool(incluir_banco),
        "quantidade_arquivos": len(manifest_arquivos),
        "tamanho_bytes": destino.stat().st_size,
    }


def gerar_checkpoint_completo(descricao: str = "") -> dict:
    """Gera o checkpoint recomendado: código/recursos + snapshot do banco ativo."""
    return gerar_checkpoint(
        descricao=descricao,
        incluir_banco=True,
    )


def auditar_protecao_checkpoint(caminho=None) -> dict:
    """Compara o checkpoint com o estado editável atual do projeto.

    A auditoria responde se todos os arquivos atualmente protegíveis estão no
    checkpoint, se algum deles mudou desde a geração e se há snapshot do banco.
    O banco não é comparado byte a byte porque pode continuar recebendo dados
    depois do checkpoint; a garantia aqui é que um snapshot SQLite íntegro foi
    incluído naquele momento.
    """
    pasta = localizar_pasta_projeto()
    _validar_fontes(pasta)

    if caminho is None:
        ultimo = obter_ultimo_checkpoint()
        if ultimo is None:
            return {
                "existe": False,
                "completo": False,
                "motivo": "Nenhum checkpoint nativo foi encontrado.",
                "faltantes": [],
                "alterados": [],
                "extras": [],
                "banco_incluido": False,
                "versao_igual": False,
            }
        caminho = ultimo["caminho"]

    diagnostico = inspecionar_checkpoint(caminho)
    atual = _inventario_projeto(pasta)
    protegido = {
        nome: dados
        for nome, dados in diagnostico["arquivos"].items()
        if nome != "estudos.db"
    }

    faltantes = sorted(set(atual) - set(protegido))
    extras = sorted(set(protegido) - set(atual))
    alterados = sorted(
        nome for nome in (set(atual) & set(protegido))
        if str(atual[nome].get("sha256")) != str(protegido[nome].get("sha256"))
    )

    manifesto = diagnostico.get("manifesto") or {}
    versao_checkpoint = str(manifesto.get("vighnastudy_versao") or "")
    versao_igual = versao_checkpoint == str(VIGHNA_VERSION)
    banco_incluido = bool(diagnostico.get("banco_incluido"))
    banco_ativo_existe = localizar_banco_ativo(pasta).is_file()

    completo = (
        not faltantes
        and not alterados
        and banco_incluido
        and banco_ativo_existe
        and versao_igual
    )

    if completo:
        motivo = "Fontes/recursos atuais e snapshot do banco estão protegidos."
    elif faltantes or alterados:
        motivo = "O projeto mudou depois do último checkpoint ou há arquivos não protegidos."
    elif not banco_incluido:
        motivo = "O código está protegido, mas o checkpoint não contém estudos.db."
    elif not versao_igual:
        motivo = "O checkpoint pertence a outra versão do VighnaStudy."
    else:
        motivo = "A proteção está incompleta."

    return {
        "existe": True,
        "completo": completo,
        "motivo": motivo,
        "caminho": diagnostico["caminho"],
        "nome": diagnostico["nome"],
        "criado_em": diagnostico.get("criado_em"),
        "versao_checkpoint": versao_checkpoint,
        "versao_atual": str(VIGHNA_VERSION),
        "versao_igual": versao_igual,
        "faltantes": faltantes,
        "alterados": alterados,
        "extras": extras,
        "banco_incluido": banco_incluido,
        "banco_ativo_existe": banco_ativo_existe,
        "quantidade_atual": len(atual),
        "quantidade_protegida": len(protegido),
        "diagnostico": diagnostico,
    }


def listar_checkpoints() -> list[dict]:
    pasta = localizar_pasta_projeto() / NOME_PASTA_CHECKPOINTS
    pasta.mkdir(parents=True, exist_ok=True)

    resultado: list[dict] = []

    for caminho in sorted(
        pasta.glob("VighnaStudy_checkpoint_*.zip"),
        key=lambda p: p.stat().st_mtime if p.exists() else 0,
        reverse=True,
    ):
        try:
            stat = caminho.stat()
        except OSError:
            continue

        resultado.append({
            "caminho": caminho,
            "nome": caminho.name,
            "data_modificacao": datetime.fromtimestamp(stat.st_mtime),
            "tamanho_bytes": stat.st_size,
        })

    return resultado


def obter_ultimo_checkpoint() -> dict | None:
    checkpoints = listar_checkpoints()
    return checkpoints[0] if checkpoints else None


def abrir_pasta_checkpoints() -> Path:
    pasta = localizar_pasta_projeto() / NOME_PASTA_CHECKPOINTS
    pasta.mkdir(parents=True, exist_ok=True)

    if sys.platform.startswith("win"):
        os.startfile(str(pasta))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(pasta)])
    else:
        subprocess.Popen(["xdg-open", str(pasta)])

    return pasta


# ==========================================================
# RESTAURAÇÃO SEGURA DE CHECKPOINTS
# ==========================================================

def _nome_zip_seguro(nome: str) -> bool:
    nome = str(nome or "").replace("\\", "/")
    if not nome or nome.startswith("/"):
        return False
    partes = Path(nome).parts
    if any(parte in ("..", "") for parte in partes):
        return False
    if len(partes) > 0 and ":" in partes[0]:
        return False
    return True


def inspecionar_checkpoint(caminho) -> dict:
    """Valida estrutura, manifesto e hashes antes de qualquer restauração."""
    caminho = Path(caminho).expanduser().resolve()
    if not caminho.is_file():
        raise FileNotFoundError(f"Checkpoint não encontrado: {caminho}")
    if caminho.suffix.lower() != ".zip":
        raise ValueError("O checkpoint precisa ser um arquivo ZIP.")

    try:
        with zipfile.ZipFile(caminho, "r") as zip_entrada:
            nomes = zip_entrada.namelist()
            if "checkpoint_manifest.json" not in nomes:
                raise ValueError(
                    "Este ZIP não possui checkpoint_manifest.json e não pode ser restaurado automaticamente."
                )

            inseguros = [nome for nome in nomes if not _nome_zip_seguro(nome)]
            if inseguros:
                raise ValueError(
                    "O checkpoint contém caminhos inseguros e foi bloqueado: "
                    + ", ".join(inseguros[:5])
                )

            try:
                manifesto = json.loads(
                    zip_entrada.read("checkpoint_manifest.json").decode("utf-8")
                )
            except Exception as erro:
                raise ValueError(f"Manifesto inválido: {erro}") from erro

            if str(manifesto.get("formato") or "") != "VighnaStudy checkpoint":
                raise ValueError("O ZIP não foi reconhecido como checkpoint nativo do VighnaStudy.")

            arquivos_manifesto = list(manifesto.get("arquivos") or [])
            if not arquivos_manifesto:
                raise ValueError("O manifesto não contém arquivos restauráveis.")

            mapa = {}
            for item in arquivos_manifesto:
                nome = str(item.get("arquivo") or "").replace("\\", "/")
                if not _nome_zip_seguro(nome):
                    raise ValueError(f"Caminho inválido no manifesto: {nome}")
                if nome not in nomes:
                    raise ValueError(f"Arquivo ausente no ZIP: {nome}")
                dados = zip_entrada.read(nome)
                esperado = str(item.get("sha256") or "").lower().strip()
                atual = hashlib.sha256(dados).hexdigest()
                if esperado and atual != esperado:
                    raise ValueError(
                        f"Falha de integridade em {nome}: SHA-256 não corresponde ao manifesto."
                    )
                tamanho = item.get("tamanho_bytes")
                if tamanho is not None and int(tamanho) != len(dados):
                    raise ValueError(f"Falha de integridade em {nome}: tamanho divergente.")
                mapa[nome] = {
                    "sha256": atual,
                    "tamanho_bytes": len(dados),
                }

            essenciais = {"main.py", "banco.py", "tema.py", "foco.py"}
            # Checkpoints da versão atual devem carregar o núcleo completo.
            # Mantemos compatibilidade com checkpoints antigos exigindo deles
            # apenas o núcleo histórico mínimo.
            versao_manifesto = int(manifesto.get("versao_manifesto") or 1)
            if versao_manifesto >= VERSAO_MANIFESTO_CHECKPOINT:
                essenciais |= FONTES_NUCLEO_ATUAL
            faltantes = [nome for nome in sorted(essenciais) if nome not in mapa]
            if faltantes:
                raise ValueError(
                    "O checkpoint não contém todos os fontes essenciais: "
                    + ", ".join(faltantes)
                )

            banco_incluido = "estudos.db" in mapa
            return {
                "caminho": caminho,
                "nome": caminho.name,
                "manifesto": manifesto,
                "arquivos": mapa,
                "quantidade_arquivos": len(mapa),
                "banco_incluido": banco_incluido,
                "descricao": str(manifesto.get("descricao") or "").strip(),
                "criado_em": str(manifesto.get("criado_em") or "").strip(),
                "valido": True,
            }
    except zipfile.BadZipFile as erro:
        raise ValueError("O arquivo selecionado não é um ZIP válido.") from erro


def _restaurar_snapshot_banco(origem: Path, destino: Path) -> None:
    origem_uri = origem.resolve().as_uri() + "?mode=ro"
    origem_con = sqlite3.connect(origem_uri, uri=True, timeout=10)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino_con = sqlite3.connect(destino, timeout=10)
    try:
        origem_con.backup(destino_con)
        destino_con.commit()
        resultado = destino_con.execute("PRAGMA integrity_check").fetchone()
        if resultado is None or str(resultado[0]).lower() != "ok":
            raise RuntimeError("O banco restaurado não passou na verificação de integridade.")
    finally:
        destino_con.close()
        origem_con.close()


def restaurar_checkpoint(caminho, restaurar_banco: bool = False) -> dict:
    """Restaura os arquivos de um checkpoint nativo após validação integral.

    Antes de tocar nos arquivos atuais, cria um checkpoint de segurança. O
    banco só é restaurado quando solicitado explicitamente e quando existe no
    checkpoint. Arquivos extras da instalação atual nunca são apagados.
    """
    diagnostico = inspecionar_checkpoint(caminho)
    pasta = localizar_pasta_projeto()
    _validar_fontes(pasta)

    if restaurar_banco and not diagnostico["banco_incluido"]:
        raise ValueError("O checkpoint selecionado não contém estudos.db.")

    # Rede de segurança obrigatória antes de qualquer alteração.
    banco_atual = localizar_banco_ativo(pasta)
    seguranca = gerar_checkpoint(
        descricao="antes-restauracao-completo",
        incluir_banco=banco_atual.is_file(),
    )

    restaurados = []
    caminho = Path(caminho).resolve()

    with tempfile.TemporaryDirectory(prefix="vighna_restore_") as temp_dir:
        temp = Path(temp_dir)
        with zipfile.ZipFile(caminho, "r") as zip_entrada:
            for nome in diagnostico["arquivos"]:
                if nome == "estudos.db":
                    if restaurar_banco:
                        destino_temp = temp / "estudos.db"
                        destino_temp.write_bytes(zip_entrada.read(nome))
                    continue

                # Apenas o conjunto seguro que o próprio gerador de checkpoint
                # admite. Isso bloqueia executáveis e pastas de build.
                relativo = Path(nome)
                if relativo.parts and relativo.parts[0] in PASTAS_IGNORADAS:
                    continue
                extensao = relativo.suffix.lower()
                permitido = (
                    extensao in EXTENSOES_PROJETO
                    or (
                        relativo.parts
                        and relativo.parts[0] in PASTAS_RECURSIVAS_OPCIONAIS
                        and extensao in EXTENSOES_RECURSOS
                    )
                )
                if not permitido:
                    continue

                origem_temp = temp / relativo
                origem_temp.parent.mkdir(parents=True, exist_ok=True)
                origem_temp.write_bytes(zip_entrada.read(nome))

                destino = (pasta / relativo).resolve()
                try:
                    destino.relative_to(pasta.resolve())
                except ValueError as erro:
                    raise ValueError(f"Destino inseguro bloqueado: {nome}") from erro

                destino.parent.mkdir(parents=True, exist_ok=True)
                substituto = destino.with_name(destino.name + ".restore_tmp")
                shutil.copy2(origem_temp, substituto)
                os.replace(substituto, destino)
                restaurados.append(nome)

        banco_restaurado = False
        if restaurar_banco:
            banco_temp = temp / "estudos.db"
            if not banco_temp.is_file():
                raise RuntimeError("A cópia do banco não pôde ser extraída do checkpoint.")
            _restaurar_snapshot_banco(
                banco_temp,
                localizar_banco_ativo(pasta),
            )
            banco_restaurado = True

    return {
        "checkpoint": diagnostico,
        "checkpoint_seguranca": seguranca,
        "arquivos_restaurados": restaurados,
        "quantidade_restaurada": len(restaurados),
        "banco_restaurado": banco_restaurado,
        "pasta_projeto": pasta,
        "reinicio_recomendado": True,
    }
