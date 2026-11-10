"""M13 — árbitro de eventos de mérito, *sem Qt e sem I/O*.

Somente tentativas confirmadas entram na fila. Uma apuração concluída na
thread de trabalho não pode ser publicada se uma tentativa posterior alterou
a geração do despacho. Falhas suspendem a ponte até nova homologação.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

from .eventos_merito_m12 import AgendadorMeritoM12, LoteMeritoM12
from .contrato_historico_merito import ResultadoIntegracao

class DespachoM13Invalido(RuntimeError):
    pass

@dataclass(frozen=True)
class RequisicaoMeritoM13:
    numero: int
    geracao: int
    lote: LoteMeritoM12 | None
    motivo: str

class DespachanteMeritoM13:
    def __init__(self, perfil_id: str):
        self._eventos = AgendadorMeritoM12(perfil_id)
        self.perfil_id = perfil_id
        self._geracao = 0
        self._numero = 0
        self._inicial = False
        self._ocupado: RequisicaoMeritoM13 | None = None
        self._revogado = False

    @property
    def revogado(self) -> bool:
        return self._revogado

    @property
    def ocupado(self) -> bool:
        return self._ocupado is not None

    @property
    def tem_pendencias(self) -> bool:
        return not self._revogado and (self._inicial or self._eventos.consultar_lote() is not None)

    def solicitar_inicial(self) -> bool:
        if self._revogado or self._inicial:
            return False
        self._inicial = True
        self._geracao += 1
        return True

    def registrar_tentativa(self, tentativa_id: int, *, commit_ok: bool = True,
                            sem_impacto: bool = False, simulado_aberto: bool = False) -> bool:
        if self._revogado:
            return False
        mudou = self._eventos.registrar_tentativa(
            tentativa_id, commit_ok=commit_ok,
            sem_impacto=sem_impacto, simulado_aberto=simulado_aberto)
        if mudou:
            self._geracao += 1
        return mudou

    def simulado_entregue(self, *, commit_ok: bool, concluida: bool) -> bool:
        # O leitor M09 publica o simulado apenas se concluída=1, encerrado_em!=NULL.
        # Encerramento incompleto não deve liberar tentativas antecipadamente.
        if self._revogado or not concluida:
            return False
        mudou = self._eventos.simulado_entregue(commit_ok=commit_ok)
        if mudou:
            self._geracao += 1
        return mudou

    def iniciar(self) -> RequisicaoMeritoM13 | None:
        if self._revogado or self._ocupado is not None:
            return None
        lote = self._eventos.consultar_lote()
        if lote is None and not self._inicial:
            return None
        self._numero += 1
        req = RequisicaoMeritoM13(self._numero, self._geracao, lote,
                                  "apuração_inicial" if self._inicial and lote is None
                                  else "tentativas_confirmadas")
        self._ocupado = req
        return req

    def concluir(self, req: RequisicaoMeritoM13, resultado: ResultadoIntegracao,
                 publicar: Callable[[ResultadoIntegracao], object]) -> str:
        """Somente o chamador da thread UI pode invocar este método.

        Em gerações antigas, descarta resultado da UI; a gravação já efetivada
        no banco lateral permanece válida e será reconciliada no próximo lote.
        """
        if self._revogado or self._ocupado != req:
            return "ignorado"
        self._ocupado = None
        if req.geracao != self._geracao:
            return "obsoleto"
        if (not isinstance(resultado, ResultadoIntegracao)
                or resultado.gravacao_realizada is not True):
            self.revogar()
            raise DespachoM13Invalido("Somente resultado auditado e COMMIT confirmado")
        if not callable(publicar):
            self.revogar()
            raise DespachoM13Invalido("Publicador Qt principal indisponível")
        if req.lote is not None:
            atual = self._eventos.consultar_lote()
            if atual != req.lote:
                return "obsoleto"
        try:
            publicar(resultado)  # Chamada única, síncrona, pela thread do Qt.
            if req.lote is not None and not self._eventos.confirmar_lote(
                req.lote, auditoria_e_commit_ok=True):
                raise DespachoM13Invalido("Falha ao confirmar lote após publicação")
        except Exception as exc:
            self.revogar()
            raise DespachoM13Invalido("Falha na publicação do mérito") from exc
        self._inicial = False
        return "publicado"

    def falhar(self, req: RequisicaoMeritoM13) -> bool:
        if self._ocupado != req or self._revogado:
            return False
        self.revogar()
        return True

    def revogar(self) -> None:
        self._revogado = True
        self._ocupado = None
        self._inicial = False
        self._eventos.revogar()
