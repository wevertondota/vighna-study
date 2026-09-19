"""Leitura segura de arquivos TXT usados na importação de questões."""

from pathlib import Path


def _decodificar_txt(conteudo: bytes):
    """Decodifica TXT comum do Windows sem adicionar dependências externas.

    Prioriza BOMs explícitos, UTF-8 e, por fim, codificações legadas comuns
    em arquivos produzidos no Windows. Retorna ``(texto, codificacao)``.
    """
    if conteudo.startswith((b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")):
        return conteudo.decode("utf-32"), "UTF-32"

    if conteudo.startswith((b"\xff\xfe", b"\xfe\xff")):
        return conteudo.decode("utf-16"), "UTF-16"

    if conteudo.startswith(b"\xef\xbb\xbf"):
        return conteudo.decode("utf-8-sig"), "UTF-8"

    # Arquivos UTF-16 sem BOM costumam conter muitos bytes NUL.
    amostra = conteudo[:4096]
    if amostra and amostra.count(b"\x00") >= max(2, len(amostra) // 8):
        for codec, rotulo in (("utf-16-le", "UTF-16 LE"), ("utf-16-be", "UTF-16 BE")):
            try:
                texto = conteudo.decode(codec)
            except UnicodeDecodeError:
                continue
            if "\x00" not in texto:
                return texto, rotulo

    try:
        return conteudo.decode("utf-8"), "UTF-8"
    except UnicodeDecodeError:
        pass

    try:
        return conteudo.decode("cp1252"), "Windows-1252"
    except UnicodeDecodeError:
        return conteudo.decode("latin-1"), "ISO-8859-1"


def ler_arquivo_txt_questoes(caminho):
    """Lê um ``.txt`` e devolve estrutura compatível com o importador comum."""
    arquivo = Path(caminho)

    if arquivo.suffix.lower() != ".txt":
        raise ValueError("Selecione um arquivo com extensão .txt.")

    if not arquivo.is_file():
        raise FileNotFoundError(f"Arquivo TXT não encontrado: {arquivo}")

    conteudo = arquivo.read_bytes()
    if not conteudo:
        raise ValueError("O arquivo TXT está vazio.")

    texto, codificacao = _decodificar_txt(conteudo)
    texto = texto.replace("\r\n", "\n").replace("\r", "\n").strip()

    if not texto:
        raise ValueError("O arquivo TXT não contém texto utilizável.")

    # Um TXT de questões é texto puro. NUL residual costuma indicar arquivo
    # binário renomeado ou codificação que não pôde ser reconhecida com segurança.
    if "\x00" in texto:
        raise ValueError(
            "O arquivo contém bytes incompatíveis com texto puro. "
            "Salve-o novamente como UTF-8 e tente importar outra vez."
        )

    return {
        "caminho": str(arquivo),
        "arquivo": arquivo.name,
        "total_paginas": 1,
        "pagina_inicial": 1,
        "pagina_final": 1,
        "texto": texto,
        "faixas_paginas": [],
        "caracteres": len(texto),
        "codificacao": codificacao,
    }
