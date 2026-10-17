
"""Reconciliação conservadora R1D + RC2 + inicialização.

Não importa main.py, não executa código recebido, não utiliza o banco
pessoal e não produz pacotes instaláveis.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import stat
import zipfile
from datetime import datetime
from pathlib import Path

FONTES = {
    "base": "e2c0ac43221dcd358cff8a7bb576f1143f81f079a5d4aee5e0d5ee6d9971c51d",
    "rc2": "a3613317c65e3a76ce97c0feb10c1853992f347b054854af4eb09908862f4985",
    "ajuste": "83747a90f8c8c873c52d5cfa6611062cc3a7735c20dd17399d485ec461fbbd7c",
}
MAIN_HASHES = {
    "base": "51cecac37485b83777ebadcfd6a876d4ff4e171370a7e8ad63653b89d66dfbe0",
    "rc2": "6e99832727e864212cb9025c7790b098116af115c2045690d226860b4c823ff0",
    "ajuste": "c6c183039272cce4b75ba79e4eb739d4d1add1ad5b45f38ab78eceb3183d6f94",
}
BUILD_ANTIGO = "structural-m2-int1-settings-r1d-rc2"
BUILD_NOVO = (
    "structural-m2-int1-settings-r1d-rc2-"
    "startup-maximized-compact-nav-v1"
)
MODULOS = (
    "settings_empty_state.py",
    "settings_footer.py",
    "settings_header.py",
    "settings_option.py",
    "settings_option_text.py",
    "settings_scroll.py",
    "settings_search.py",
    "settings_search_logic.py",
    "settings_section.py",
)

class Conflito(ValueError):
    pass

def sha(data):
    return hashlib.sha256(data).hexdigest()

def hash_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _substituir_exato(texto, antes, depois, descricao):
    encontrados = texto.count(antes)
    if encontrados != 1:
        raise Conflito(
            "Trecho ausente ou ambiguo: " + descricao +
            " (" + str(encontrados) + " ocorrencias)"
        )
    return texto.replace(antes, depois, 1)


def _aplicar_inicio(texto):
    texto = texto.replace("\r\n", "\n")

    texto = _substituir_exato(
        texto,
        "        Prioriza os rótulos em desktops de 1366 px e oferece colapso manual.",
        "        Inicia recolhido no Futurista e permite expansão manual pelo botão.",
        "documentacao da barra lateral"
    )

    texto = _substituir_exato(
        texto,
        "        self._sidebar_expandida_manual = None",
        "        # A navegação Futurista inicia recolhida a cada abertura. O botão\n"
        "        # continua permitindo alternar entre os estados durante a sessão.\n"
        "        self._sidebar_expandida_manual = False",
        "estado inicial da barra lateral"
    )

    texto = _substituir_exato(
        texto,
        "        # Em 1366 px a lateral textual tem prioridade. A versão compacta\n"
        "        # continua acessível pelo botão e é o padrão só abaixo de 1240 px.",
        "        # Fallback responsivo para casos sem preferência manual. Na abertura,\n"
        "        # _sidebar_expandida_manual=False mantém a lateral compacta.",
        "documentacao responsiva"
    )

    linhas = texto.splitlines(keepends=True)
    chamadas = [
        i for i, linha in enumerate(linhas)
        if linha.strip() == "janela.show()"
    ]

    if len(chamadas) != 2:
        raise Conflito(
            "Esperadas duas chamadas janela.show(); encontradas "
            + str(len(chamadas))
        )

    indice = chamadas[-1]
    original = linhas[indice]
    if original.rstrip("\n") != "janela.show()":
        raise Conflito("Abertura principal divergente.")

    final = "\n" if original.endswith("\n") else ""
    linhas[indice] = (
        "# A janela principal inicia maximizada, preservando bordas, barra de tarefas\n"
        "# e os controles normais de minimizar/restaurar do sistema operacional.\n"
        "janela.showMaximized()" + final
    )

    resultado = "".join(linhas)
    try:
        ast.parse(resultado)
    except SyntaxError as exc:
        raise Conflito("Inicializacao produziu sintaxe invalida.") from exc
    return resultado


def combinar_main(base, rc2, ajuste):
    esperado = _aplicar_inicio(base)
    oficial = ajuste.replace("\r\n", "\n")

    if esperado != oficial:
        raise Conflito(
            "Os quatro blocos nao reproduzem exatamente o patch oficial."
        )

    combinado = _aplicar_inicio(rc2)
    try:
        ast.parse(combinado)
    except SyntaxError as exc:
        raise Conflito("Fusao RC2 com sintaxe invalida.") from exc
    return combinado


def atualizar_versao(texto):
    if texto.count(BUILD_ANTIGO) != 1:
        raise Conflito(
            "Identificador de build RC2 ausente ou ambíguo."
        )
    novo = texto.replace(BUILD_ANTIGO, BUILD_NOVO, 1)
    try:
        ast.parse(novo)
    except SyntaxError as exc:
        raise Conflito("versao.py inválido.") from exc
    return novo

def _ler_membro(z, nome, hash_esperado=None):
    candidatos = []
    for info in z.infolist():
        path = info.filename.replace("\\", "/")
        partes = path.split("/")
        if info.is_dir():
            continue
        if (path.startswith("/") or ".." in partes
            or ":" in path or any(not p for p in partes)
            or (info.create_system == 3
                and stat.S_ISLNK(info.external_attr >> 16))):
            continue
        if not (path == nome or path.endswith("/" + nome)):
            continue
        if info.file_size > 3_000_000:
            continue
        dados = z.read(info)
        if hash_esperado is None or sha(dados) == hash_esperado:
            candidatos.append(dados)

    if len(candidatos) != 1:
        raise Conflito(
            "Arquivo ausente ou ambíguo: " + nome
        )
    return candidatos[0]

def produzir(fontes):
    if set(fontes) != set(FONTES):
        raise Conflito("São necessárias três fontes identificadas.")

    paths = {k: Path(v) for k, v in fontes.items()}

    for chave, path in paths.items():
        if not path.is_file() or path.stat().st_size > 100_000_000:
            raise Conflito("Fonte inexistente ou excessiva: " + chave)
        if hash_file(path) != FONTES[chave]:
            raise Conflito("SHA-256 divergente: " + chave)

    with (
        zipfile.ZipFile(paths["base"]) as zbase,
        zipfile.ZipFile(paths["rc2"]) as zrc2,
        zipfile.ZipFile(paths["ajuste"]) as zajuste
    ):
        base = _ler_membro(
            zbase, "main.py", MAIN_HASHES["base"]
        )
        rc2 = _ler_membro(
            zrc2, "main.py", MAIN_HASHES["rc2"]
        )
        ajuste = _ler_membro(
            zajuste, "main.py", MAIN_HASHES["ajuste"]
        )

        combinado = combinar_main(
            base.decode("utf-8-sig"),
            rc2.decode("utf-8-sig"),
            ajuste.decode("utf-8-sig")
        ).encode("utf-8")

        versao = _ler_membro(zrc2, "versao.py")
        versao_nova = atualizar_versao(
            versao.decode("utf-8-sig")
        ).encode("utf-8")

        arquivos = {
            "codigo/main.py": combinado,
            "codigo/versao.py": versao_nova,
        }

        for nome in MODULOS:
            conteudo = _ler_membro(
                zrc2, "ui/" + nome
            )
            try:
                ast.parse(conteudo.decode("utf-8-sig"))
            except SyntaxError as exc:
                raise Conflito(
                    "Módulo RC2 com sintaxe inválida: " + nome
                ) from exc
            arquivos["codigo/ui/" + nome] = conteudo

    destino = Path.home() / "VighnaLab" / "Laboratorio_Reconciliacao"
    for pasta in (destino.parent, destino):
        if pasta.is_symlink() or (
            hasattr(pasta, "is_junction") and pasta.is_junction()
        ):
            raise Conflito("Diretório de laboratório inseguro.")

    destino.mkdir(parents=True, exist_ok=True)
    nome = (
        "M2_RC2_RECONCILIADO_LAB_"
        + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        + "_NAO_INSTALAR.zip"
    )
    saida = destino / nome

    relatorio = {
        "format": "vighna-reconciliacao-laboratorio-v1",
        "build": BUILD_NOVO,
        "schema": 25,
        "fontes_sha256": FONTES,
        "arquivos": {
            k: sha(v) for k, v in arquivos.items()
        },
        "conflitos_nao_resolvidos": 0,
        "instalacao_autorizada": False,
        "g7_aprovado": False,
        "aviso": (
            "Candidato de laboratório. Não contém manifesto "
            "instalável nem autorização de implantação."
        ),
    }

    dados = json.dumps(
        relatorio, ensure_ascii=False, indent=2
    ).encode("utf-8")
    arquivos["RELATORIO_RECONCILIACAO.json"] = dados
    arquivos["MANIFESTO_SHA256.json"] = json.dumps(
        {k: sha(v) for k, v in arquivos.items()},
        indent=2
    ).encode("utf-8")

    with zipfile.ZipFile(
        saida, "x", zipfile.ZIP_DEFLATED
    ) as z:
        for nome_arquivo, conteudo in arquivos.items():
            z.writestr(nome_arquivo, conteudo)

    return saida
