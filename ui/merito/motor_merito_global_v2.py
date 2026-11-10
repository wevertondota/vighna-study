"""VighnaStudy M02 — domínio puro do mérito global (SEM acesso a banco, Qt ou rede).

Implementação de desenvolvimento. O adaptador real para `banco.py` somente deve
ser ligado depois de auditar o esquema, o alcance de consultas e a instalação.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from collections.abc import Iterable, Mapping

MARCOS: tuple[int, ...] = (
    500, 1000, 1500, 2500, 4000, 6000,
    8500, 11500, 15000, 20000, 27500, 35000,
)
STATUS_VALIDOS = frozenset({"Correta", "Errada", "Pulada"})


@dataclass(frozen=True)
class TentativaMerito:
    """Uma tentativa acadêmica única; não representa uma questão única.

    Um mesmo ID repetido de maneira idêntica equivale à mesma tentativa;
    divergência de conteúdo deve ser reconciliada no repositório, não aqui.
    """

    tentativa_id: str
    status: str
    respondida_em: datetime
    concurso_id: str
    academica: bool = True
    publicada: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.tentativa_id, str) or not self.tentativa_id.strip():
            raise ValueError("ID estável da tentativa é obrigatório")
        if not isinstance(self.concurso_id, str) or not self.concurso_id.strip():
            raise ValueError("ID do concurso é obrigatório")
        if self.status not in STATUS_VALIDOS:
            raise ValueError(f"Status não suportado: {self.status!r}")
        if not isinstance(self.respondida_em, datetime):
            raise TypeError("respondida_em deve ser datetime")
        if type(self.academica) is not bool or type(self.publicada) is not bool:
            raise TypeError("academica e publicada devem ser booleanos")


@dataclass(frozen=True)
class ResumoMeritoGlobal:
    acertos: int
    erros: int
    pulos: int
    tentativas_contabilizadas: int
    saldo: int
    recorde: int
    brasao_atual: int  # maior marco já conquistado, permanente
    conquistas: tuple[int, ...]
    proximo_novo_marco: int | None
    faltam_para_novo_marco: int
    percentual_progresso_novo_marco: float


def _validar_recorde(recorde_persistido: int) -> None:
    if type(recorde_persistido) is not int or recorde_persistido < 0:
        raise ValueError("recorde_persistido exige inteiro não negativo")


def calcular_merito_global(
    tentativas: Iterable[TentativaMerito],
    *,
    recorde_persistido: int = 0,
) -> ResumoMeritoGlobal:
    """Reconstrói resultado global de um snapshot integral de tentativas.

    A coleção deve vir de TODOS os concursos do perfil, sem limitação por
    período e com a semântica confirmada. Tentativas não-acadêmicas e simulados
    ainda sem publicação não geram mérito. A atualização do recorde em banco
    ocorrerá numa etapa separada, exclusivamente depois de validação.
    """
    _validar_recorde(recorde_persistido)
    unicas: dict[str, TentativaMerito] = {}
    for t in tentativas:
        if not isinstance(t, TentativaMerito):
            raise TypeError("A entrada deve conter TentativaMerito")
        antiga = unicas.get(t.tentativa_id)
        if antiga is not None and antiga != t:
            raise ValueError(
                f"Conflito de versões da mesma tentativa: {t.tentativa_id!r}. "
                "Reconciliar dados no repositório antes de calcular."
            )
        unicas[t.tentativa_id] = t

    computaveis = sorted(
        (t for t in unicas.values() if t.academica and t.publicada),
        key=lambda t: (t.respondida_em, t.tentativa_id),
    )
    acertos = erros = pulos = 0
    saldo = recorde_calculado = 0
    for t in computaveis:
        if t.status == "Correta":
            acertos += 1
            saldo += 1
        elif t.status == "Errada":
            erros += 1
            saldo -= 1
        else:
            pulos += 1
        recorde_calculado = max(recorde_calculado, saldo)

    recorde = max(recorde_persistido, recorde_calculado)
    conquistas = tuple(m for m in MARCOS if m <= recorde)
    atual = conquistas[-1] if conquistas else 0
    proximo = next((m for m in MARCOS if m > recorde), None)
    faltam = max(0, proximo - saldo) if proximo is not None else 0
    if proximo is None:
        progresso = 100.0
    else:
        distancia = proximo - atual
        progresso = min(100.0, max(0.0, 100.0 * (saldo - atual) / distancia))

    return ResumoMeritoGlobal(
        acertos=acertos,
        erros=erros,
        pulos=pulos,
        tentativas_contabilizadas=len(computaveis),
        saldo=saldo,
        recorde=recorde,
        brasao_atual=atual,
        conquistas=conquistas,
        proximo_novo_marco=proximo,
        faltam_para_novo_marco=faltam,
        percentual_progresso_novo_marco=round(progresso, 2),
    )


def normalizar_historico_auditado(
    linhas: Iterable[Mapping[str, object]],
    *,
    coluna_id: str,
    coluna_status: str,
    coluna_data: str,
    coluna_concurso_id: str,
    coluna_academica: str,
    coluna_publicada: str,
) -> list[TentativaMerito]:
    """Adaptador SEM I/O; requer mapeamento explícito de banco previamente auditado.

    Não tenta inferir nomes de colunas. Rejeita ausência, NULL, estados
    desconhecidos ou tipos ambíguos para impedir contagem acadêmica incorreta.
    """
    colunas = (
        coluna_id, coluna_status, coluna_data,
        coluna_concurso_id, coluna_academica, coluna_publicada,
    )
    if any(not isinstance(c, str) or not c.strip() for c in colunas):
        raise ValueError("Forneça seis mapeamentos explícitos de coluna")
    saida: list[TentativaMerito] = []
    for indice, linha in enumerate(linhas):
        if not isinstance(linha, Mapping):
            raise TypeError(f"Linha {indice} não é mapeamento")
        ausentes = [c for c in colunas if c not in linha]
        if ausentes:
            raise ValueError(f"Linha {indice} sem colunas: {ausentes}")
        instante = linha[coluna_data]
        if isinstance(instante, str):
            try:
                instante = datetime.fromisoformat(instante)
            except ValueError as exc:
                raise ValueError(f"Data inválida na linha {indice}") from exc
        if not isinstance(instante, datetime):
            raise ValueError(f"Data ausente/inválida na linha {indice}")
        if any(linha[c] is None for c in colunas):
            raise ValueError(f"Linha {indice} possui NULL em campos obrigatórios")
        for coluna in (coluna_academica, coluna_publicada):
            if type(linha[coluna]) is not bool:
                raise TypeError(f"Linha {indice}: {coluna} deve ser bool explícito")
        saida.append(TentativaMerito(
            tentativa_id=str(linha[coluna_id]),
            status=linha[coluna_status],
            respondida_em=instante,
            concurso_id=str(linha[coluna_concurso_id]),
            academica=linha[coluna_academica],
            publicada=linha[coluna_publicada],
        ))
    return saida
