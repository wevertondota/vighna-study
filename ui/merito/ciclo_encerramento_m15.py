"""M15: política pura de encerramento sem efeitos colaterais, para teste offline.

A condição de fechamento nunca é 'timeout'. Somente a conclusão confirmada
por um pool dedicado autoriza o fim. Nenhum worker é morto por coerção.
"""
from __future__ import annotations
from enum import Enum

class EstadoEncerramento(str, Enum):
    ATIVO = 'ativo'
    AGUARDANDO = 'aguardando_worker'
    PRONTO = 'pronto'

class CicloEncerramentoM15:
    def __init__(self):
        self._estado = EstadoEncerramento.ATIVO
        self._notificado = False

    @property
    def estado(self) -> EstadoEncerramento:
        return self._estado

    @property
    def fechando(self) -> bool:
        return self._estado != EstadoEncerramento.ATIVO

    @property
    def pronto(self) -> bool:
        return self._estado == EstadoEncerramento.PRONTO

    def iniciar(self, *, pool_concluido: bool) -> bool:
        if type(pool_concluido) is not bool:
            raise TypeError('Resultado do pool deve ser booleano confirmado')
        if self.pronto:
            return True
        self._estado = (EstadoEncerramento.PRONTO if pool_concluido
                        else EstadoEncerramento.AGUARDANDO)
        return self.pronto

    def verificar(self, *, pool_concluido: bool) -> bool:
        if self._estado == EstadoEncerramento.ATIVO:
            raise RuntimeError('Não verificar conclusão antes de solicitar encerramento')
        return self.iniciar(pool_concluido=pool_concluido)

    def consumir_sinal_pronto(self) -> bool:
        """Impede múltiplas retomadas do fechamento em callbacks concorrentes."""
        if not self.pronto or self._notificado:
            return False
        self._notificado = True
        return True
