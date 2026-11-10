"""M05 — projeção de estado do catálogo VighnaStudy (somente leitura).

O estado inicial é SEM_APURACAO. Não existem números de progresso ou
brasões supostamente conquistados enquanto o histórico real não estiver auditado.
Este módulo não abre banco, não salva QSettings e não atribui conquistas.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
from .contrato_historico_merito import ResultadoIntegracao
from .motor_merito_global_v2 import MARCOS, ResumoMeritoGlobal


@dataclass(frozen=True)
class CartaoBrasao:
    marco: int
    estado: str  # aguardando | conquistado | bloqueado
    destaque_atual: bool


@dataclass(frozen=True)
class VisaoCatalogo:
    apurado: bool
    cartoes: tuple[CartaoBrasao, ...]
    saldo: int | None
    recorde: int | None
    brasao_atual: int | None
    proximo_marco: int | None
    faltam: int | None
    progresso_pct: float | None
    fonte: str | None


def visao_aguardando() -> VisaoCatalogo:
    return VisaoCatalogo(
        apurado=False,
        cartoes=tuple(CartaoBrasao(m, "aguardando", False) for m in MARCOS),
        saldo=None, recorde=None, brasao_atual=None,
        proximo_marco=None, faltam=None, progresso_pct=None, fonte=None,
    )


def _conferir_resumo(r: ResumoMeritoGlobal) -> None:
    """Confere invariantes do resumo calculado; dados ainda exigem auditoria de origem."""
    if not isinstance(r, ResumoMeritoGlobal):
        raise TypeError("Resumo deve ser ResumoMeritoGlobal")
    for chave in ('acertos','erros','pulos','tentativas_contabilizadas','saldo','recorde',
                  'brasao_atual','faltam_para_novo_marco'):
        valor = getattr(r, chave)
        if type(valor) is not int:
            raise TypeError(f'{chave} deve ser inteiro')
    if min(r.acertos, r.erros, r.pulos, r.tentativas_contabilizadas, r.recorde, r.faltam_para_novo_marco)<0:
        raise ValueError('Contadores e recorde não podem ser negativos')
    if r.saldo != r.acertos-r.erros:
        raise ValueError('Saldo divergente do histórico')
    if r.tentativas_contabilizadas != r.acertos+r.erros+r.pulos:
        raise ValueError('Total de tentativas divergente')
    esperado = tuple(m for m in MARCOS if m <= r.recorde)
    if tuple(r.conquistas) != esperado:
        raise ValueError('Conquistas incoerentes com recorde')
    if r.brasao_atual != (esperado[-1] if esperado else 0):
        raise ValueError('Brasão atual incoerente')
    prox = next((m for m in MARCOS if m>r.recorde),None)
    if r.proximo_novo_marco != prox:
        raise ValueError('Próximo marco incoerente')
    faltam = max(0, prox-r.saldo) if prox is not None else 0
    if r.faltam_para_novo_marco != faltam:
        raise ValueError('Distância até o marco incoerente')
    pct = r.percentual_progresso_novo_marco
    if not isinstance(pct,(int,float)) or not isfinite(pct) or pct<0 or pct>100:
        raise ValueError('Percentual inválido')
    if r.recorde < r.saldo:
        raise ValueError('Recorde menor que saldo atual')


def projetar_resultado_auditado(resultado: ResultadoIntegracao) -> VisaoCatalogo:
    """Prepara UI somente a partir do contrato integral certificado do M03.

    Quem fizer a integração real DEVE obter ResultadoIntegracao pelo adaptador
    homologado e não por objetos fabricados a partir de tela ou de concurso ativo.
    """
    if not isinstance(resultado, ResultadoIntegracao):
        raise TypeError('Somente ResultadoIntegracao do contrato M03 é aceito')
    if not isinstance(resultado.origem_auditada,str) or not resultado.origem_auditada.strip():
        raise ValueError('Fonte auditada não identificada')
    if type(resultado.linhas_auditadas) is not int or resultado.linhas_auditadas<0:
        raise ValueError('Quantidade de linhas inválida')
    if not isinstance(resultado.concursos_contabilizados,tuple):
        raise ValueError('Conjunto de concursos inválido')
    r=resultado.resumo
    _conferir_resumo(r)
    if r.tentativas_contabilizadas>resultado.linhas_auditadas:
        raise ValueError('Resumo excede número de linhas auditadas')
    if not isinstance(resultado.gravacao_realizada,bool):
        raise ValueError('Estado de gravação inválido')
    return VisaoCatalogo(
        apurado=True,
        cartoes=tuple(CartaoBrasao(m,'conquistado' if m in r.conquistas else 'bloqueado',m==r.brasao_atual)
                      for m in MARCOS),
        saldo=r.saldo, recorde=r.recorde,
        brasao_atual=r.brasao_atual,
        proximo_marco=r.proximo_novo_marco,
        faltam=r.faltam_para_novo_marco,
        progresso_pct=r.percentual_progresso_novo_marco,
        fonte=resultado.origem_auditada,
    )
