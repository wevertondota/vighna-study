import re
import unicodedata
from pathlib import Path

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None


PADRAO_QUESTAO = re.compile(
    r"""
    (?im)
    ^[ \t]*
    (?:
        (?:QUEST(?:ÃO|AO)|Q)
        [ \t]*
        (?:N[º°O]?[ \t]*)?
        (?P<explicito>\d{1,4})
        [ \t]*
        (?:[\.\)\-–:]?[ \t]*)
        |
        (?P<numerico>\d{1,4})
        [ \t]*
        [\.\)\-–:]
        [ \t]*
    )
    """,
    re.VERBOSE
)

PADRAO_ALTERNATIVA = re.compile(
    r"""
    (?im)
    ^[ \t]*
    \(?
    (?P<letra>[A-E])
    \)?
    [ \t]*
    [\)\.\-–:]
    [ \t]*
    """,
    re.VERBOSE
)

PADRAO_GABARITO_INLINE = re.compile(
    r"""
    (?im)
    ^[ \t]*
    (?:GABARITO|RESPOSTA(?:[ \t]+CORRETA)?)
    [ \t]*[:\-–]
    [ \t]*
    (?P<letra>[A-E])
    \b
    .*$
    """,
    re.VERBOSE
)

PADRAO_EXPLICACAO = re.compile(
    r"""
    (?im)
    ^[ \t]*
    (?:
        COMENTÁRIO
        |COMENTARIO
        |EXPLICAÇÃO
        |EXPLICACAO
        |JUSTIFICATIVA
    )
    [ \t]*[:\-–]?
    [ \t]*
    """,
    re.VERBOSE
)

PADRAO_CABECALHO_GABARITO = re.compile(
    r"""
    (?im)
    ^[ \t]*
    (?:
        GABARITO
        |RESPOSTAS(?:[ \t]+CORRETAS)?
        |ANSWER[ \t]+KEY
    )
    [ \t]*[:\-–]?
    [ \t]*
    (?P<resto>.*)
    $
    """,
    re.VERBOSE
)

STOPWORDS_TOPICO = {
    "da", "das", "de", "do", "dos", "e", "em", "no", "na", "nos", "nas",
    "para", "por", "com", "sem", "sobre", "a", "o", "as", "os", "um", "uma",
    "art", "artigo", "capitulo", "capítulo", "secao", "seção", "gerais",
}


def dependencia_pdf_disponivel():
    return PdfReader is not None


def normalizar_texto_pdf(texto):
    texto = str(texto or "").lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def limpar_texto_pdf(texto):
    texto = str(texto or "")
    texto = texto.replace("\x00", "")
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")
    texto = re.sub(r"[ \t]+\n", "\n", texto)
    texto = re.sub(r"\n[ \t]+", "\n", texto)
    texto = re.sub(r"[ \t]{2,}", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def extrair_texto_pdf_questoes(
    caminho,
    pagina_inicial=None,
    pagina_final=None
):
    if PdfReader is None:
        raise RuntimeError(
            "A biblioteca pypdf não está instalada. "
            "Execute: python -m pip install pypdf"
        )

    caminho = Path(caminho)

    if not caminho.exists():
        raise FileNotFoundError(caminho)

    reader = PdfReader(str(caminho))

    if reader.is_encrypted:
        try:
            resultado = reader.decrypt("")
        except Exception as erro:
            raise ValueError(
                "O PDF está protegido por senha e não pôde ser aberto."
            ) from erro

        if not resultado:
            raise ValueError(
                "O PDF está protegido por senha e não pôde ser aberto."
            )

    total_paginas = len(reader.pages)

    if total_paginas <= 0:
        raise ValueError("O PDF não possui páginas.")

    inicio = (
        1
        if pagina_inicial is None
        else max(1, int(pagina_inicial))
    )
    fim = (
        total_paginas
        if pagina_final is None
        else min(total_paginas, int(pagina_final))
    )

    if inicio > fim:
        raise ValueError("Intervalo de páginas inválido.")

    partes = []
    faixas_paginas = []
    cursor = 0

    for numero in range(inicio, fim + 1):
        pagina = reader.pages[numero - 1]

        try:
            texto = pagina.extract_text(
                extraction_mode="layout"
            )
        except Exception:
            texto = pagina.extract_text()

        texto = limpar_texto_pdf(texto or "")

        if partes:
            separador = "\n\n"
            partes.append(separador)
            cursor += len(separador)

        inicio_pagina = cursor
        partes.append(texto)
        cursor += len(texto)
        fim_pagina = cursor

        faixas_paginas.append({
            "pagina": numero,
            "inicio": inicio_pagina,
            "fim": fim_pagina,
            "caracteres": len(texto),
        })

    texto_total = "".join(partes)

    return {
        "caminho": str(caminho),
        "arquivo": caminho.name,
        "total_paginas": total_paginas,
        "pagina_inicial": inicio,
        "pagina_final": fim,
        "texto": texto_total,
        "faixas_paginas": faixas_paginas,
        "caracteres": len(texto_total.strip()),
    }


def _pagina_por_posicao(posicao, faixas_paginas):
    for faixa in faixas_paginas or []:
        if (
            posicao >= faixa["inicio"]
            and posicao <= faixa["fim"]
        ):
            return faixa["pagina"]

    return None


def _extrair_pares_gabarito(texto):
    texto = str(texto or "")

    pares = {}

    padrao_par = re.compile(
        r"""
        (?i)
        (?<!\d)
        (\d{1,4})
        [ \t]*
        (?:
            [\.\)\-–:/]
            |\->
            |=>
        )?
        [ \t]*
        ([A-E])
        \b
        """,
        re.VERBOSE
    )

    for numero, letra in padrao_par.findall(texto):
        pares[int(numero)] = letra.upper()

    # Suporta também:
    # 1  2  3  4
    # A  C  B  D
    linhas = [
        linha.strip()
        for linha in texto.splitlines()
        if linha.strip()
    ]

    for indice in range(len(linhas) - 1):
        numeros = re.findall(
            r"(?<!\d)\d{1,4}(?!\d)",
            linhas[indice]
        )
        letras = re.findall(
            r"(?i)(?<![A-Z])[A-E](?![A-Z])",
            linhas[indice + 1]
        )

        if (
            len(numeros) >= 2
            and len(numeros) == len(letras)
        ):
            for numero, letra in zip(
                numeros,
                letras
            ):
                pares[int(numero)] = letra.upper()

    return pares


def separar_gabarito_global(texto):
    texto = str(texto or "")
    correspondencias = list(
        PADRAO_CABECALHO_GABARITO.finditer(texto)
    )

    for correspondencia in reversed(correspondencias):
        linha_cabecalho = correspondencia.group(0)

        # VPQ 1.1 usa "GABARITO: A/B/C/D/E" dentro de cada questão.
        # Essa linha é um gabarito individual, não o início de um bloco geral.
        # Sem esta proteção, números citados na EXPLICAÇÃO (por exemplo,
        # "art. 161" ou "art. 168-A") podem ser lidos como pares de
        # gabarito global e bloquear uma importação válida.
        if PADRAO_GABARITO_INLINE.fullmatch(linha_cabecalho):
            continue

        trecho = (
            correspondencia.group("resto")
            + "\n"
            + texto[correspondencia.end():]
        )

        pares = _extrair_pares_gabarito(trecho)

        if pares:
            return (
                texto[:correspondencia.start()].rstrip(),
                pares,
                trecho.strip(),
            )

    return (
        texto,
        {},
        "",
    )

def _candidatos_questao(texto):
    candidatos = []

    for match in PADRAO_QUESTAO.finditer(texto):
        numero = (
            match.group("explicito")
            or match.group("numerico")
        )

        candidatos.append({
            "numero": int(numero),
            "inicio": match.start(),
            "fim_prefixo": match.end(),
            "explicita": bool(
                match.group("explicito")
            ),
        })

    return candidatos


def _sequencia_alternativas(
    texto,
    inicio,
    limite=None
):
    fim_busca = (
        min(
            len(texto),
            inicio + 10000
        )
        if limite is None
        else min(
            len(texto),
            limite
        )
    )

    marcadores = list(
        PADRAO_ALTERNATIVA.finditer(
            texto,
            inicio,
            fim_busca
        )
    )

    melhor = None

    for indice, marcador in enumerate(marcadores):
        if marcador.group("letra").upper() != "A":
            continue

        sequencia = [marcador]
        esperada = ord("B")

        for proximo in marcadores[indice + 1:]:
            letra = proximo.group("letra").upper()

            if letra == chr(esperada):
                sequencia.append(proximo)
                esperada += 1

                if esperada > ord("E"):
                    break

            elif letra == "A":
                break

        if len(sequencia) >= 2:
            if (
                melhor is None
                or len(sequencia) > len(melhor)
            ):
                melhor = sequencia

            if len(sequencia) >= 4:
                break

    return melhor or []


def _candidato_tem_alternativas(
    texto,
    candidato
):
    sequencia = _sequencia_alternativas(
        texto,
        candidato["fim_prefixo"]
    )
    return len(sequencia) >= 2


def _remover_linha_gabarito(texto):
    return PADRAO_GABARITO_INLINE.sub(
        "",
        texto
    )


def _parsear_bloco_questao(
    bloco,
    numero,
    fim_prefixo_relativo,
    gabarito_global=None
):
    gabarito_global = (
        gabarito_global
        or {}
    )

    gabarito_inline_match = (
        PADRAO_GABARITO_INLINE.search(
            bloco
        )
    )

    gabarito_inline = (
        gabarito_inline_match.group(
            "letra"
        ).upper()
        if gabarito_inline_match
        else None
    )

    explicacao = ""
    explicacao_match = (
        PADRAO_EXPLICACAO.search(
            bloco
        )
    )

    bloco_questao = bloco

    if explicacao_match:
        explicacao = limpar_texto_pdf(
            bloco[
                explicacao_match.end():
            ]
        )
        bloco_questao = bloco[
            :explicacao_match.start()
        ]

    bloco_questao = (
        _remover_linha_gabarito(
            bloco_questao
        )
    )

    alternativos = list(
        PADRAO_ALTERNATIVA.finditer(
            bloco_questao,
            fim_prefixo_relativo
        )
    )

    # Conserva apenas uma sequência A, B, C, D, E.
    sequencia = []

    for indice, marcador in enumerate(alternativos):
        if marcador.group("letra").upper() != "A":
            continue

        atual = [marcador]
        esperada = ord("B")

        for proximo in alternativos[indice + 1:]:
            letra = proximo.group("letra").upper()

            if letra == chr(esperada):
                atual.append(proximo)
                esperada += 1

                if esperada > ord("E"):
                    break
            else:
                break

        if len(atual) >= 2:
            sequencia = atual
            break

    if len(sequencia) < 2:
        return None

    primeiro = sequencia[0]

    enunciado = limpar_texto_pdf(
        bloco_questao[
            fim_prefixo_relativo:
            primeiro.start()
        ]
    )

    if not enunciado:
        return None

    alternativas = []

    for indice, marcador in enumerate(sequencia):
        inicio_texto = marcador.end()

        fim_texto = (
            sequencia[indice + 1].start()
            if indice + 1 < len(sequencia)
            else len(bloco_questao)
        )

        texto_alternativa = limpar_texto_pdf(
            bloco_questao[
                inicio_texto:
                fim_texto
            ]
        )

        # Remove eventual cabeçalho do gabarito que tenha ficado
        # no final da última alternativa.
        cabecalho = (
            PADRAO_CABECALHO_GABARITO.search(
                texto_alternativa
            )
        )

        if cabecalho:
            texto_alternativa = (
                texto_alternativa[
                    :cabecalho.start()
                ].strip()
            )

        if not texto_alternativa:
            continue

        alternativas.append({
            "letra": marcador.group(
                "letra"
            ).upper(),
            "texto": texto_alternativa,
        })

    if len(alternativas) < 2:
        return None

    letras = {
        item["letra"]
        for item in alternativas
    }

    gabarito = (
        gabarito_inline
        or gabarito_global.get(
            numero
        )
    )

    if gabarito not in letras:
        gabarito = None

    return {
        "numero_pdf": numero,
        "enunciado": enunciado,
        "alternativas": alternativas,
        "gabarito": gabarito,
        "explicacao": explicacao,
    }


def _analisar_texto_questoes_pdf_generico(
    texto,
    faixas_paginas=None
):
    texto = limpar_texto_pdf(
        texto
    )

    (
        texto_questoes,
        gabarito_global,
        texto_gabarito,
    ) = separar_gabarito_global(
        texto
    )

    candidatos = _candidatos_questao(
        texto_questoes
    )

    questoes = []
    indice = 0

    while indice < len(candidatos):
        candidato = candidatos[indice]

        if not _candidato_tem_alternativas(
            texto_questoes,
            candidato
        ):
            indice += 1
            continue

        sequencia = _sequencia_alternativas(
            texto_questoes,
            candidato[
                "fim_prefixo"
            ]
        )

        if not sequencia:
            indice += 1
            continue

        ultima_alt_inicio = (
            sequencia[-1].start()
        )

        proximo_indice = None

        for teste_indice in range(
            indice + 1,
            len(candidatos)
        ):
            teste = candidatos[
                teste_indice
            ]

            if teste[
                "inicio"
            ] <= ultima_alt_inicio:
                continue

            if _candidato_tem_alternativas(
                texto_questoes,
                teste
            ):
                proximo_indice = (
                    teste_indice
                )
                break

        fim_bloco = (
            candidatos[
                proximo_indice
            ][
                "inicio"
            ]
            if proximo_indice
            is not None
            else len(
                texto_questoes
            )
        )

        bloco = texto_questoes[
            candidato[
                "inicio"
            ]:
            fim_bloco
        ]

        fim_prefixo_relativo = (
            candidato[
                "fim_prefixo"
            ]
            - candidato[
                "inicio"
            ]
        )

        questao = _parsear_bloco_questao(
            bloco,
            candidato[
                "numero"
            ],
            fim_prefixo_relativo,
            gabarito_global
        )

        if questao is not None:
            questao[
                "pagina"
            ] = _pagina_por_posicao(
                candidato[
                    "inicio"
                ],
                faixas_paginas
            )
            questao[
                "posicao"
            ] = candidato[
                "inicio"
            ]
            questoes.append(
                questao
            )

        indice = (
            proximo_indice
            if proximo_indice
            is not None
            else len(
                candidatos
            )
        )

    # Evita duplicação causada por padrões ambíguos.
    unicas = []
    vistos = set()

    for questao in questoes:
        chave = (
            questao[
                "numero_pdf"
            ],
            normalizar_texto_pdf(
                questao[
                    "enunciado"
                ]
            )[:240],
        )

        if chave in vistos:
            continue

        vistos.add(
            chave
        )
        unicas.append(
            questao
        )

    com_gabarito = sum(
        1
        for questao in unicas
        if questao[
            "gabarito"
        ]
    )

    return {
        "questoes": unicas,
        "gabarito_global": gabarito_global,
        "texto_gabarito": texto_gabarito,
        "quantidade": len(
            unicas
        ),
        "com_gabarito": com_gabarito,
        "sem_gabarito": (
            len(
                unicas
            )
            - com_gabarito
        ),
    }


PADRAO_VPQ_1_0 = re.compile(
    r"""
    (?im)
    ^[ \t]*
    VIGHNA[ \t]+PDF
    [ \t]*[—–-][ \t]*
    VPQ[ \t]+1\.[01]
    [ \t]*$
    """,
    re.VERBOSE
)

PADRAO_VPQ_METADADO = re.compile(
    r"""
    (?im)
    ^[ \t]*
    (?P<chave>
        DISCIPLINA
        |TÓPICO
        |TOPICO
        |TÍTULO
        |TITULO
        |CAPÍTULO
        |CAPITULO
        |FONTE
        |QUANTIDADE
        |ALTERNATIVAS
    )
    [ \t]*:
    [ \t]*
    (?P<valor>.*?)
    [ \t]*$
    """,
    re.VERBOSE
)


def detectar_vpq_1_0(
    texto
):
    texto = str(
        texto
        or ""
    )

    # Procura o selo apenas no início do documento. Isso evita
    # classificar como VPQ um PDF genérico que apenas cite o protocolo.
    inicio = texto[
        :min(
            len(
                texto
            ),
            3000
        )
    ]

    return bool(
        PADRAO_VPQ_1_0.search(
            inicio
        )
    )


def extrair_metadados_vpq_1_0(
    texto
):
    metadados = {
        "disciplina": "",
        "topico": "",
        "capitulo": "",
        "fonte": "",
        "quantidade": None,
        "alternativas": "",
    }

    mapa = {
        "DISCIPLINA": "disciplina",
        "TÓPICO": "topico",
        "TOPICO": "topico",
        "TÍTULO": "topico",
        "TITULO": "topico",
        "CAPÍTULO": "capitulo",
        "CAPITULO": "capitulo",
        "FONTE": "fonte",
        "QUANTIDADE": "quantidade",
        "ALTERNATIVAS": "alternativas",
    }

    for match in PADRAO_VPQ_METADADO.finditer(
        str(
            texto
            or ""
        )
    ):
        chave = mapa.get(
            match.group(
                "chave"
            ).upper()
        )

        if chave is None:
            continue

        valor = limpar_texto_pdf(
            match.group(
                "valor"
            )
        )

        if chave == "quantidade":
            numeros = re.findall(
                r"\d+",
                valor
            )

            metadados[
                "quantidade"
            ] = (
                int(
                    numeros[0]
                )
                if numeros
                else None
            )
        else:
            metadados[
                chave
            ] = valor

    return metadados


def _extrair_gabaritos_individuais_vpq(
    texto_questoes
):
    candidatos = _candidatos_questao(
        texto_questoes
    )

    resultado = {}

    for indice, candidato in enumerate(
        candidatos
    ):
        if not candidato[
            "explicita"
        ]:
            continue

        fim = (
            candidatos[
                indice + 1
            ][
                "inicio"
            ]
            if indice + 1 < len(
                candidatos
            )
            else len(
                texto_questoes
            )
        )

        bloco = texto_questoes[
            candidato[
                "inicio"
            ]:
            fim
        ]

        match = PADRAO_GABARITO_INLINE.search(
            bloco
        )

        if match:
            resultado[
                candidato[
                    "numero"
                ]
            ] = match.group(
                "letra"
            ).upper()

    return resultado


def _normalizar_metadado_vpq(
    valor
):
    valor = normalizar_texto_pdf(
        valor
    )

    if valor in {
        "nao informado",
        "não informado",
        "nao informada",
        "não informada",
        "-",
        "—",
    }:
        return ""

    return valor


def analisar_vpq_1_0(
    texto,
    faixas_paginas=None
):
    texto = limpar_texto_pdf(
        texto
    )

    metadados = (
        extrair_metadados_vpq_1_0(
            texto
        )
    )

    (
        texto_questoes,
        gabarito_global,
        texto_gabarito,
    ) = separar_gabarito_global(
        texto
    )

    gabaritos_individuais = (
        _extrair_gabaritos_individuais_vpq(
            texto_questoes
        )
    )

    analise = (
        _analisar_texto_questoes_pdf_generico(
            texto,
            faixas_paginas
        )
    )

    questoes = analise[
        "questoes"
    ]

    erros = []
    avisos = []

    numeros = [
        int(
            questao[
                "numero_pdf"
            ]
        )
        for questao in questoes
    ]

    encontrados = len(
        questoes
    )

    declaradas = metadados.get(
        "quantidade"
    )

    if declaradas is None:
        avisos.append(
            "O cabeçalho VPQ não informa uma quantidade válida."
        )
    elif declaradas != encontrados:
        erros.append(
            (
                f"Quantidade declarada: {declaradas}; "
                f"questões encontradas: {encontrados}."
            )
        )

    if numeros:
        esperada = list(
            range(
                1,
                len(
                    numeros
                )
                + 1
            )
        )

        if numeros != esperada:
            erros.append(
                (
                    "A sequência das questões não é contínua de 1 até "
                    f"{len(numeros)}. Encontrada: "
                    + ", ".join(
                        str(
                            numero
                        )
                        for numero in numeros[
                            :30
                        ]
                    )
                    + (
                        "..."
                        if len(
                            numeros
                        ) > 30
                        else ""
                    )
                )
            )
    else:
        erros.append(
            "Nenhuma questão estruturada foi encontrada no VPQ."
        )

    numeros_set = set(
        numeros
    )

    globais_set = set(
        int(
            numero
        )
        for numero in gabarito_global.keys()
    )

    individuais_set = set(
        int(
            numero
        )
        for numero in gabaritos_individuais.keys()
    )

    faltando_individual = sorted(
        numeros_set
        - individuais_set
    )

    # Gabarito individual e gabarito geral são duas formas válidas de
    # informar a resposta. Só alerta sobre lacunas quando aquela forma foi
    # efetivamente usada em pelo menos uma questão do arquivo.
    if individuais_set and faltando_individual:
        avisos.append(
            (
                "Questões sem gabarito individual: "
                + ", ".join(
                    str(
                        numero
                    )
                    for numero in faltando_individual[
                        :20
                    ]
                )
                + (
                    "..."
                    if len(
                        faltando_individual
                    ) > 20
                    else ""
                )
            )
        )

    faltando_global = sorted(
        numeros_set
        - globais_set
    )

    extras_global = sorted(
        globais_set
        - numeros_set
    )

    if globais_set and faltando_global:
        avisos.append(
            (
                "Gabarito geral sem entrada para: "
                + ", ".join(
                    str(
                        numero
                    )
                    for numero in faltando_global[
                        :20
                    ]
                )
                + (
                    "..."
                    if len(
                        faltando_global
                    ) > 20
                    else ""
                )
            )
        )

    sem_gabarito_vpq = sorted(
        numeros_set
        - individuais_set
        - globais_set
    )

    if sem_gabarito_vpq:
        erros.append(
            (
                "Questões sem gabarito individual ou geral: "
                + ", ".join(
                    str(numero)
                    for numero in sem_gabarito_vpq[:20]
                )
                + (
                    "..."
                    if len(sem_gabarito_vpq) > 20
                    else ""
                )
            )
        )

    if extras_global:
        erros.append(
            (
                "Gabarito geral contém números sem questão correspondente: "
                + ", ".join(
                    str(
                        numero
                    )
                    for numero in extras_global[
                        :20
                    ]
                )
            )
        )

    conflitos = []

    for numero in sorted(
        numeros_set
        & individuais_set
        & globais_set
    ):
        individual = (
            gabaritos_individuais[
                numero
            ]
        )
        global_ = (
            gabarito_global[
                numero
            ]
        )

        if individual != global_:
            conflitos.append(
                (
                    numero,
                    individual,
                    global_,
                )
            )

    if conflitos:
        erros.append(
            (
                "Conflito entre gabarito individual e geral: "
                + "; ".join(
                    (
                        f"Q{numero} "
                        f"individual={individual} "
                        f"geral={global_}"
                    )
                    for numero, individual, global_
                    in conflitos[
                        :12
                    ]
                )
                + (
                    "..."
                    if len(
                        conflitos
                    ) > 12
                    else ""
                )
            )
        )

    sem_explicacao = []
    alternativas_invalidas = []
    gabaritos_invalidos = []

    for questao in questoes:
        numero = int(
            questao[
                "numero_pdf"
            ]
        )

        alternativas = questao.get(
            "alternativas",
            []
        )

        if not (
            2 <= len(
                alternativas
            ) <= 5
        ):
            alternativas_invalidas.append(
                numero
            )

        letras = {
            alternativa[
                "letra"
            ]
            for alternativa in alternativas
        }

        gabarito = questao.get(
            "gabarito"
        )

        if (
            not gabarito
            or gabarito not in letras
        ):
            gabaritos_invalidos.append(
                numero
            )

        if not str(
            questao.get(
                "explicacao",
                ""
            )
            or ""
        ).strip():
            sem_explicacao.append(
                numero
            )

        questao[
            "gabarito_individual_vpq"
        ] = gabaritos_individuais.get(
            numero
        )
        questao[
            "gabarito_geral_vpq"
        ] = gabarito_global.get(
            numero
        )

    if alternativas_invalidas:
        erros.append(
            (
                "Quantidade inválida de alternativas nas questões: "
                + ", ".join(
                    str(
                        numero
                    )
                    for numero in alternativas_invalidas[
                        :20
                    ]
                )
            )
        )

    if gabaritos_invalidos:
        erros.append(
            (
                "Gabarito ausente ou incompatível com as alternativas: "
                + ", ".join(
                    str(
                        numero
                    )
                    for numero in gabaritos_invalidos[
                        :20
                    ]
                )
            )
        )

    if sem_explicacao:
        avisos.append(
            (
                "Questões sem conteúdo após EXPLICAÇÃO: "
                + ", ".join(
                    str(
                        numero
                    )
                    for numero in sem_explicacao[
                        :20
                    ]
                )
                + (
                    "..."
                    if len(
                        sem_explicacao
                    ) > 20
                    else ""
                )
            )
        )

    if not _normalizar_metadado_vpq(
        metadados.get(
            "disciplina"
        )
    ):
        avisos.append(
            "Disciplina não informada no cabeçalho VPQ."
        )

    if not (
        _normalizar_metadado_vpq(metadados.get("topico"))
        or _normalizar_metadado_vpq(metadados.get("capitulo"))
    ):
        avisos.append(
            "Título ou capítulo não informado no cabeçalho VPQ."
        )

    # Divergências que podem corromper a interpretação bloqueiam
    # a importação. Metadados incompletos e explicação ausente ficam
    # como avisos e podem ser corrigidos/conferidos na tela.
    bloqueia = bool(
        erros
    )

    if bloqueia:
        status = "revisao"
        status_rotulo = "Revisão necessária"
    elif avisos:
        status = "aviso"
        status_rotulo = "VPQ reconhecido com avisos"
    else:
        status = "integro"
        status_rotulo = "Estrutura íntegra"

    return {
        **analise,
        "protocolo": "VPQ 1.1",
        "vpq_detectado": True,
        "vpq_metadados": metadados,
        "vpq_gabaritos_individuais": (
            gabaritos_individuais
        ),
        "vpq_erros": erros,
        "vpq_avisos": avisos,
        "vpq_bloqueia_importacao": bloqueia,
        "vpq_status": status,
        "vpq_status_rotulo": status_rotulo,
        "vpq_quantidade_declarada": declaradas,
        "vpq_quantidade_encontrada": encontrados,
        "vpq_gabaritos_individuais_count": len(
            gabaritos_individuais
        ),
        "vpq_gabaritos_gerais_count": len(
            gabarito_global
        ),
        "vpq_explicacoes_count": (
            encontrados
            - len(
                sem_explicacao
            )
        ),
    }


def analisar_texto_questoes_pdf(
    texto,
    faixas_paginas=None
):
    if detectar_vpq_1_0(
        texto
    ):
        return analisar_vpq_1_0(
            texto,
            faixas_paginas
        )

    analise = (
        _analisar_texto_questoes_pdf_generico(
            texto,
            faixas_paginas
        )
    )

    return {
        **analise,
        "protocolo": "PDF genérico",
        "vpq_detectado": False,
        "vpq_metadados": extrair_metadados_vpq_1_0(texto),
        "vpq_erros": [],
        "vpq_avisos": [],
        "vpq_bloqueia_importacao": False,
        "vpq_status": "generico",
        "vpq_status_rotulo": "PDF genérico",
    }



def sugerir_topico_pdf(
    questao,
    topicos
):
    """
    Sugestão conservadora. Só retorna um tópico quando há evidência
    textual razoável no enunciado/alternativas.

    topicos:
    [
        {
            "topico_id": ...,
            "disciplina": ...,
            "topico": ...
        }
    ]
    """

    texto = normalizar_texto_pdf(
        (
            str(
                questao.get(
                    "enunciado",
                    ""
                )
            )
            + " "
            + " ".join(
                item.get(
                    "texto",
                    ""
                )
                for item in questao.get(
                    "alternativas",
                    []
                )
            )
        )
    )

    resultados = []

    for topico in topicos:
        nome = normalizar_texto_pdf(
            topico.get(
                "topico",
                ""
            )
        )

        if not nome:
            continue

        tokens = [
            token
            for token in re.findall(
                r"[a-z0-9]+",
                nome
            )
            if (
                len(token) >= 4
                and token not in STOPWORDS_TOPICO
            )
        ]

        score = 0.0
        motivo = ""

        if (
            len(nome) >= 4
            and nome in texto
        ):
            score = 100.0
            motivo = "nome do tópico encontrado no texto"

        elif tokens:
            presentes = sum(
                1
                for token in tokens
                if re.search(
                    rf"\b{re.escape(token)}\b",
                    texto
                )
            )

            proporcao = (
                presentes
                / len(tokens)
            )

            score = (
                proporcao
                * 75.0
            )

            if (
                len(tokens) == 1
                and presentes == 1
            ):
                score = max(
                    score,
                    82.0
                )

            if presentes:
                motivo = (
                    f"{presentes}/{len(tokens)} palavra(s)-chave"
                )

        disciplina = normalizar_texto_pdf(
            topico.get(
                "disciplina",
                ""
            )
        )

        if (
            score > 0
            and disciplina
            and disciplina in texto
        ):
            score += 5.0

        resultados.append({
            **topico,
            "score": min(
                100.0,
                score
            ),
            "motivo": motivo,
        })

    resultados.sort(
        key=lambda item: (
            -item[
                "score"
            ],
            item.get(
                "disciplina",
                ""
            ).lower(),
            item.get(
                "topico",
                ""
            ).lower(),
        )
    )

    if not resultados:
        return None

    melhor = resultados[0]
    segundo = (
        resultados[1]
        if len(
            resultados
        ) > 1
        else None
    )

    # Critério conservador para não classificar silenciosamente
    # uma questão em tópico errado.
    if melhor[
        "score"
    ] < 70.0:
        return None

    if (
        segundo is not None
        and melhor[
            "score"
        ] < 100.0
        and (
            melhor[
                "score"
            ]
            - segundo[
                "score"
            ]
        ) < 12.0
    ):
        return None

    return melhor
