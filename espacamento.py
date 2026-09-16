# Regras de espaçamento da revisão.
#
# A matriz considera:
# 1) número da revisão;
# 2) desempenho atual;
# 3) opcionalmente, queda acentuada em relação ao resultado anterior.
#
# Os valores padrão podem ser alterados pelo usuário dentro do programa.

from copy import deepcopy


FAIXAS_PERCENTUAIS = [
    "0-49",
    "50-59",
    "60-69",
    "70-79",
    "80-89",
    "90-94",
    "95-100",
]


TABELA_ESPACAMENTO_PADRAO = {
    1: {
        "0-49": (4, 7),
        "50-59": (6, 8),
        "60-69": (7, 10),
        "70-79": (9, 12),
        "80-89": (12, 16),
        "90-94": (16, 21),
        "95-100": (21, 30),
    },
    2: {
        "0-49": (8, 12),
        "50-59": (10, 14),
        "60-69": (12, 16),
        "70-79": (15, 21),
        "80-89": (21, 30),
        "90-94": (30, 40),
        "95-100": (40, 60),
    },
    3: {
        "0-49": (12, 18),
        "50-59": (15, 21),
        "60-69": (18, 25),
        "70-79": (24, 32),
        "80-89": (30, 45),
        "90-94": (45, 60),
        "95-100": (60, 90),
    },
    4: {
        "0-49": (18, 25),
        "50-59": (21, 30),
        "60-69": (28, 35),
        "70-79": (35, 45),
        "80-89": (45, 60),
        "90-94": (60, 90),
        "95-100": (90, 120),
    },
    5: {
        "0-49": (25, 35),
        "50-59": (30, 40),
        "60-69": (35, 50),
        "70-79": (45, 60),
        "80-89": (60, 90),
        "90-94": (90, 120),
        "95-100": (120, 180),
    },
}


CONFIGURACAO_QUEDA_PADRAO = {
    "limite_moderada": 20,
    "limite_forte": 30,
    "penalizacao_moderada": 15,
    "penalizacao_forte": 25,
}


def obter_tabela_padrao():
    return deepcopy(
        TABELA_ESPACAMENTO_PADRAO
    )


def obter_configuracao_queda_padrao():
    return dict(
        CONFIGURACAO_QUEDA_PADRAO
    )


def normalizar_tabela_espacamento(tabela):
    """
    Aceita inclusive uma tabela carregada de JSON, na qual
    as chaves de revisão chegam como texto e os pares como listas.
    """
    if not isinstance(
        tabela,
        dict
    ):
        raise ValueError(
            "A matriz de espaçamento precisa ser um dicionário."
        )

    normalizada = {}

    for revisao in range(
        1,
        6
    ):
        origem = (
            tabela.get(revisao)
            if revisao in tabela
            else tabela.get(
                str(revisao)
            )
        )

        if not isinstance(
            origem,
            dict
        ):
            raise ValueError(
                f"A coluna da {revisao}ª revisão está ausente."
            )

        normalizada[
            revisao
        ] = {}

        for faixa in FAIXAS_PERCENTUAIS:
            valor = origem.get(
                faixa
            )

            if (
                not isinstance(
                    valor,
                    (list, tuple)
                )
                or len(valor) != 2
            ):
                raise ValueError(
                    f"Intervalo inválido para {faixa} "
                    f"na {revisao}ª revisão."
                )

            minimo = int(
                valor[0]
            )
            maximo = int(
                valor[1]
            )

            normalizada[
                revisao
            ][faixa] = (
                minimo,
                maximo
            )

    validar_tabela_espacamento(
        normalizada
    )

    return normalizada


def validar_tabela_espacamento(
    tabela
):
    """
    Proteções de coerência:
    - todos os dias >= 1;
    - mínimo <= máximo;
    - intervalos não diminuem ao avançar de revisão;
    - faixas de desempenho maiores não recebem intervalos menores.
    """
    for revisao in range(
        1,
        6
    ):
        if revisao not in tabela:
            raise ValueError(
                f"Falta a coluna da {revisao}ª revisão."
            )

        for faixa in FAIXAS_PERCENTUAIS:
            if faixa not in tabela[
                revisao
            ]:
                raise ValueError(
                    f"Falta a faixa {faixa}."
                )

            minimo, maximo = tabela[
                revisao
            ][faixa]

            minimo = int(
                minimo
            )
            maximo = int(
                maximo
            )

            if (
                minimo < 1
                or maximo < 1
            ):
                raise ValueError(
                    "Os intervalos precisam ter pelo menos 1 dia."
                )

            if minimo > maximo:
                raise ValueError(
                    f"Na faixa {faixa} da {revisao}ª revisão, "
                    "o mínimo não pode ser maior que o máximo."
                )

    # Conforme o número de revisões cresce, o intervalo não deve diminuir.
    for faixa in FAIXAS_PERCENTUAIS:
        anterior = None

        for revisao in range(
            1,
            6
        ):
            atual = tabela[
                revisao
            ][faixa]

            if anterior is not None:
                if (
                    atual[0] < anterior[0]
                    or atual[1] < anterior[1]
                ):
                    raise ValueError(
                        f"Na faixa {faixa}, a {revisao}ª revisão "
                        "não pode ter intervalo menor que a revisão anterior."
                    )

            anterior = atual

    # Dentro da mesma revisão, desempenho maior não deve reduzir o intervalo.
    for revisao in range(
        1,
        6
    ):
        anterior = None

        for faixa in FAIXAS_PERCENTUAIS:
            atual = tabela[
                revisao
            ][faixa]

            if anterior is not None:
                if (
                    atual[0] < anterior[0]
                    or atual[1] < anterior[1]
                ):
                    raise ValueError(
                        f"Na {revisao}ª revisão, a faixa {faixa} "
                        "não pode ter intervalo menor que a faixa anterior."
                    )

            anterior = atual

    return True


def _faixa_percentual(percentual):
    percentual = max(
        0.0,
        min(
            100.0,
            float(percentual)
        )
    )

    if percentual < 50:
        return "0-49", 0.0, 50.0

    if percentual < 60:
        return "50-59", 50.0, 60.0

    if percentual < 70:
        return "60-69", 60.0, 70.0

    if percentual < 80:
        return "70-79", 70.0, 80.0

    if percentual < 90:
        return "80-89", 80.0, 90.0

    if percentual < 95:
        return "90-94", 90.0, 95.0

    return "95-100", 95.0, 100.0


def calcular_sugestao_espacamento(
    numero_revisao,
    percentual_atual,
    percentual_anterior=None,
    aplicar_penalizacao=True,
    tabela_espacamento=None,
    limite_queda_moderada=20,
    limite_queda_forte=30,
    penalizacao_moderada=15,
    penalizacao_forte=25
):
    numero_revisao = max(
        1,
        int(numero_revisao)
    )

    coluna_revisao = min(
        numero_revisao,
        5
    )

    percentual_atual = max(
        0.0,
        min(
            100.0,
            float(percentual_atual)
        )
    )

    if tabela_espacamento is None:
        tabela = obter_tabela_padrao()
    else:
        tabela = normalizar_tabela_espacamento(
            tabela_espacamento
        )

    limite_queda_moderada = float(
        limite_queda_moderada
    )
    limite_queda_forte = float(
        limite_queda_forte
    )

    penalizacao_moderada = max(
        0,
        min(
            90,
            int(penalizacao_moderada)
        )
    )

    penalizacao_forte = max(
        0,
        min(
            90,
            int(penalizacao_forte)
        )
    )

    if (
        limite_queda_forte
        <= limite_queda_moderada
    ):
        raise ValueError(
            "O limite de queda forte precisa ser maior "
            "que o limite de queda moderada."
        )

    faixa_nome, limite_inferior, limite_superior = (
        _faixa_percentual(
            percentual_atual
        )
    )

    faixa_min, faixa_max = (
        tabela[
            coluna_revisao
        ][faixa_nome]
    )

    tamanho_faixa_percentual = (
        limite_superior -
        limite_inferior
    )

    if tamanho_faixa_percentual <= 0:
        posicao = 0.0
    else:
        posicao = (
            percentual_atual -
            limite_inferior
        ) / tamanho_faixa_percentual

    posicao = max(
        0.0,
        min(
            1.0,
            posicao
        )
    )

    dias_base = round(
        faixa_min
        + posicao
        * (
            faixa_max
            - faixa_min
        )
    )

    queda_pontos = 0.0
    penalizacao_percentual = 0

    if percentual_anterior is not None:
        percentual_anterior = float(
            percentual_anterior
        )

        queda_pontos = max(
            0.0,
            percentual_anterior
            - percentual_atual
        )

        if aplicar_penalizacao:
            if (
                queda_pontos
                >= limite_queda_forte
            ):
                penalizacao_percentual = (
                    penalizacao_forte
                )
            elif (
                queda_pontos
                >= limite_queda_moderada
            ):
                penalizacao_percentual = (
                    penalizacao_moderada
                )

    fator = (
        1.0
        - penalizacao_percentual
        / 100.0
    )

    dias_finais = max(
        1,
        round(
            dias_base
            * fator
        )
    )

    return {
        "numero_revisao": numero_revisao,
        "coluna_revisao": coluna_revisao,
        "faixa_percentual": faixa_nome,
        "faixa_min": faixa_min,
        "faixa_max": faixa_max,
        "dias_base": dias_base,
        "dias": dias_finais,
        "percentual_atual": percentual_atual,
        "percentual_anterior": percentual_anterior,
        "queda_pontos": queda_pontos,
        "penalizacao_percentual": penalizacao_percentual,
        "penalizacao_ativada": bool(
            aplicar_penalizacao
        ),
        "limite_queda_moderada": limite_queda_moderada,
        "limite_queda_forte": limite_queda_forte,
        "penalizacao_moderada": penalizacao_moderada,
        "penalizacao_forte": penalizacao_forte,
    }
