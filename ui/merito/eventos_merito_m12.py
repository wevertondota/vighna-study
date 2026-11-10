"""M12: fila determinística e sem I/O de eventos confirmados.

O M13 escolherá um gatilho Qt na thread principal e usará esta fila;
esta biblioteca não toca no banco, não cria threads nem timers.
"""
from __future__ import annotations
from dataclasses import dataclass

class EventoM12Invalido(ValueError):
    pass

@dataclass(frozen=True)
class LoteMeritoM12:
    revisao: int
    perfil_id: str
    tentativas: tuple[int, ...]
    motivo: str

class AgendadorMeritoM12:
    def __init__(self, perfil_id: str):
        if not isinstance(perfil_id, str) or not perfil_id.startswith("vighna-"):
            raise EventoM12Invalido("Perfil persistente obrigatório")
        self.perfil_id = perfil_id
        self._revisao = 0
        self._pendentes: set[int] = set()
        self._atendidas: set[int] = set()
        self._simulado_pendente: set[int] = set()
        self._entrega = False
        self._bloqueado = False

    def registrar_tentativa(self, tentativa_id: int | None, *, commit_ok: bool, sem_impacto: bool, simulado_aberto: bool) -> bool:
        """Chamado SÓ após retorno bem-sucedido do banco. Falha não gera evento."""
        if self._bloqueado:
            return False
        if not commit_ok or sem_impacto:
            return False
        if type(tentativa_id) is not int or tentativa_id <= 0:
            raise EventoM12Invalido("Tentativa acadêmica precisa de ID estável")
        if tentativa_id in self._atendidas or tentativa_id in self._pendentes or tentativa_id in self._simulado_pendente:
            return False
        if simulado_aberto:
            self._simulado_pendente.add(tentativa_id)
            return False
        self._pendentes.add(tentativa_id)
        self._revisao += 1
        return True

    def simulado_entregue(self, *, commit_ok: bool) -> bool:
        if self._bloqueado or not commit_ok or not self._simulado_pendente:
            return False
        self._pendentes.update(self._simulado_pendente)
        self._simulado_pendente.clear()
        self._entrega = True
        self._revisao += 1
        return True

    def consultar_lote(self) -> LoteMeritoM12 | None:
        if self._bloqueado or not self._pendentes:
            return None
        return LoteMeritoM12(self._revisao, self.perfil_id, tuple(sorted(self._pendentes)),
                            "simulado_entregue" if self._entrega else "tentativa_confirmada")

    def confirmar_lote(self, lote: LoteMeritoM12, *, auditoria_e_commit_ok: bool) -> bool:
        if self._bloqueado or lote is None or lote.perfil_id != self.perfil_id:
            return False
        if not auditoria_e_commit_ok or lote.revisao != self._revisao:
            return False
        ids = set(lote.tentativas)
        if ids != self._pendentes:
            return False
        self._atendidas.update(ids)
        self._pendentes.clear()
        self._entrega = False
        return True

    def revogar(self):
        self._bloqueado = True
        self._pendentes.clear()
        self._simulado_pendente.clear()

    @property
    def bloqueado(self) -> bool:
        return self._bloqueado
