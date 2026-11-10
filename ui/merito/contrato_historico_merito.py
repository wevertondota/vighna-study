"""VighnaStudy M03 — contrato de integração para histórico acadêmico GLOBAL.

OFFLINE, read-only, independente de PySide6 e do banco real.
Não consulta o SQLite nem altera dados. É obrigatório auditar `banco.py`
antes de substituir a fonte de linhas de teste por uma consulta real.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from collections.abc import Iterable, Mapping
from typing import Any

from .motor_merito_global_v2 import (
    ResumoMeritoGlobal, calcular_merito_global, normalizar_historico_auditado,
)


@dataclass(frozen=True)
class MapeamentoHistorico:
    """Nomes reais das colunas, que devem ser verificados em `banco.py`."""
    tentativa_id: str
    status: str
    data: str
    concurso_id: str
    academica: str
    publicada: str

    def validar(self) -> None:
        nomes = tuple(vars(self).values())
        if any(not isinstance(v, str) or not v.strip() for v in nomes):
            raise ValueError("Todas as seis colunas exigem nomes explícitos")
        if len(set(nomes)) != len(nomes):
            raise ValueError("Colunas mapeadas não podem se repetir")


@dataclass(frozen=True)
class CertidaoDeCompletude:
    """Declarações que o adaptador do banco PRECISA verificar, não pressupor.

    IDs de concurso fornecidos explicitamente e cobrindo a fonte verificada.
    A identidade estável é de TENTATIVA acadêmica, não de questão.
    """
    todos_concursos: bool
    sem_limite_de_linhas: bool
    desde_primeira_tentativa: bool
    identificadores_estaveis: bool
    resultados_academicos_e_publicacao_auditados: bool
    concurso_ids_esperados: tuple[str, ...]
    concurso_ids_consultados: tuple[str, ...]
    linhas_exportadas: int
    origem_auditada: str

    def validar(self) -> None:
        flags = (
            self.todos_concursos,
            self.sem_limite_de_linhas,
            self.desde_primeira_tentativa,
            self.identificadores_estaveis,
            self.resultados_academicos_e_publicacao_auditados,
        )
        if any(type(x) is not bool for x in flags) or not all(flags):
            raise ValueError("Fonte não homologada: escopo global/completude/semântica pendente")
        if type(self.linhas_exportadas) is not int or self.linhas_exportadas < 0:
            raise ValueError("Quantidade exportada inválida")
        if not isinstance(self.origem_auditada, str) or not self.origem_auditada.strip():
            raise ValueError("A origem auditada deve ser identificada")
        for ids in (self.concurso_ids_esperados, self.concurso_ids_consultados):
            if not isinstance(ids, tuple) or any(not isinstance(x, str) or not x.strip() for x in ids):
                raise ValueError("IDs de concurso inválidos")
            if len(set(ids)) != len(ids):
                raise ValueError("IDs de concurso repetidos")
        if set(self.concurso_ids_esperados) != set(self.concurso_ids_consultados):
            raise ValueError("Cobertura incompleta de concursos")
        if not self.concurso_ids_esperados:
            raise ValueError("Não há comprovação do universo de concursos")


@dataclass(frozen=True)
class ResultadoIntegracao:
    resumo: ResumoMeritoGlobal
    linhas_auditadas: int
    concursos_contabilizados: tuple[str, ...]
    origem_auditada: str
    # Este resultado é somente uma simulação do estado esperado;
    # em produção o recorde dependerá da gravação transacional posterior.
    gravacao_realizada: bool = False


def conferir_e_calcular(
    linhas: Iterable[Mapping[str, Any]],
    *,
    mapeamento: MapeamentoHistorico,
    certidao: CertidaoDeCompletude,
    recorde_persistido: int = 0,
) -> ResultadoIntegracao:
    """Falha fechado para dados incompletos, colunas ausentes ou origens não auditadas."""
    mapeamento.validar()
    certidao.validar()
    copia = list(linhas)
    if len(copia) != certidao.linhas_exportadas:
        raise ValueError("Snapshot truncado: contagem de linhas não confere")
    tentativas = normalizar_historico_auditado(
        copia,
        coluna_id=mapeamento.tentativa_id,
        coluna_status=mapeamento.status,
        coluna_data=mapeamento.data,
        coluna_concurso_id=mapeamento.concurso_id,
        coluna_academica=mapeamento.academica,
        coluna_publicada=mapeamento.publicada,
    )
    previstos = set(certidao.concurso_ids_consultados)
    presentes = {t.concurso_id for t in tentativas}
    if not presentes.issubset(previstos):
        raise ValueError(f"Há tentativas fora dos concursos declarados: {sorted(presentes-previstos)}")
    tipos_de_data = {t.respondida_em.tzinfo is None or t.respondida_em.utcoffset() is None for t in tentativas}
    if len(tipos_de_data) > 1:
        raise ValueError("Datas com e sem fuso misturadas: padronizar no adaptador")
    # M02 aplica a regra global: acerto +1, erro -1, pulo 0;
    # penalidade -6 pertence somente ao COMBO da Constelação R2.
    resumo = calcular_merito_global(tentativas, recorde_persistido=recorde_persistido)
    return ResultadoIntegracao(
        resumo=resumo,
        linhas_auditadas=len(copia),
        concursos_contabilizados=tuple(sorted(presentes)),
        origem_auditada=certidao.origem_auditada,
    )
