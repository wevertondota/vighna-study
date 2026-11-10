"""VighnaStudy M11 — ponte controlada M09 -> M10 -> M08.

DESENVOLVIMENTO M25, não instalável sem homologação Windows.
Produção exige revalidação contínua de origem, identidade e pasta lateral.

Sequência: leitura auditada M09, COMMIT M10, releitura do registro de mérito,
verificação de consistência e só então publicação no coordenador M08.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .motor_merito_global_v2 import MARCOS
from .sincronizacao_merito_m08 import CoordenadorMeritoM08, EstadoSincronizadoM08
from .persistencia_merito_m10 import (
    ApuracaoPersistidaM10, apurar_e_persistir_merito, ler_estado_merito,
    _perfil, PersistenciaMeritoInvalida,
)


class IntegracaoM11Desativada(RuntimeError):
    """A leitura/gravação não é autorizada neste checkpoint."""


class IntegracaoM11Invalida(RuntimeError):
    """Falha fechada: estado não deve ser divulgado como mérito apurado."""


@dataclass(frozen=True)
class EscopoM11:
    perfil_id: str
    banco_academico: Path
    banco_merito: Path
    modo: str = "inativo"  # inativo, laboratorio ou producao validada

    def __post_init__(self):
        _perfil(self.perfil_id)
        if self.modo not in ("inativo", "laboratorio", "producao"):
            raise ValueError("Modo de apuração inválido")
        if not isinstance(self.banco_academico, (str, Path)) or not isinstance(self.banco_merito, (str, Path)):
            raise TypeError("Caminhos precisam ser string ou Path")
        p = Path(self.banco_academico).expanduser().resolve(strict=False)
        q = Path(self.banco_merito).expanduser().resolve(strict=False)
        if p == q or (p.exists() and q.exists() and p.samefile(q)):
            raise ValueError("O armazenamento de mérito não pode ser o banco acadêmico")
        object.__setattr__(self, 'banco_academico', p)
        object.__setattr__(self, 'banco_merito', q)


@dataclass(frozen=True)
class EntregaM11:
    revisao: int
    atualizado: bool
    saldo: int
    recorde: int
    brasao_atual: int
    perfil_id: str
    conquistas: tuple[int, ...]
    estado_ui: EstadoSincronizadoM08


def _verificar_apos_commit(
    apuracao: ApuracaoPersistidaM10,
    *, escopo: EscopoM11,
) -> None:
    """Verificação adicional do contrato; NÃO substitui auditoria de banco M09."""
    if not isinstance(apuracao, ApuracaoPersistidaM10):
        raise IntegracaoM11Invalida("Saída M10 não reconhecida")
    if apuracao.resultado.gravacao_realizada is not True:
        raise IntegracaoM11Invalida("Resultado recebido antes do COMMIT")
    estado, resumo = apuracao.estado, apuracao.resultado.resumo
    if estado.perfil_id != escopo.perfil_id:
        raise IntegracaoM11Invalida("Perfil incorreto após persistência")
    if estado.origem_auditada != apuracao.resultado.origem_auditada:
        raise IntegracaoM11Invalida("Origem divergente após persistência")
    for nome, atributo in (
        ('acertos', 'acertos'), ('erros', 'erros'), ('pulos', 'pulos'),
        ('saldo', 'saldo'), ('recorde', 'recorde'),
        ('tentativas_contabilizadas', 'tentativas_contabilizadas'),
    ):
        if getattr(estado, atributo) != getattr(resumo, nome):
            raise IntegracaoM11Invalida(f"Contador inconsistente: {nome}")
    marcos = tuple(c.marco for c in estado.conquistas)
    if marcos != tuple(m for m in MARCOS if m <= estado.recorde):
        raise IntegracaoM11Invalida("Conquistas inconsistentes com recorde")
    if marcos != resumo.conquistas:
        raise IntegracaoM11Invalida("Conquistas não correspondem ao resultado auditado")
    if apuracao.linhas_lidas != apuracao.resultado.linhas_auditadas:
        raise IntegracaoM11Invalida("Quantidade de linhas inconsistentes")
    # Reabre o arquivo para verificar se o resultado é realmente durável.
    confirmado = ler_estado_merito(escopo.banco_merito, escopo.perfil_id)
    if confirmado != estado:
        raise IntegracaoM11Invalida("Releitura do armazenamento difere do resultado")


class OrquestradorMeritoM11:
    """Ponte desligada por padrão; não tem Qt, polling nem acesso ao banco na criação.

    Vincula um único perfil e um único par de caminhos à instância. A interface
    deve consultar snapshot() e receber notificações somente após COMMIT.
    """

    def __init__(
        self, escopo: EscopoM11, *,
        coordenador: CoordenadorMeritoM08 | None = None,
        notificar: Callable[[EstadoSincronizadoM08], None] | None = None,
    ):
        if not isinstance(escopo, EscopoM11):
            raise TypeError("EscopoM11 é obrigatório")
        if coordenador is not None and not isinstance(coordenador, CoordenadorMeritoM08):
            raise TypeError("Coordenador M08 inválido")
        if notificar is not None and not callable(notificar):
            raise TypeError("Notificador inválido")
        self.escopo = escopo
        self._coordenador = coordenador or CoordenadorMeritoM08()
        # Coordenador externo não pode já estar publicado: sem perfil associado.
        if self._coordenador.snapshot().visao.apurado:
            raise IntegracaoM11Invalida("Coordenador existente não pode ser reaproveitado sem reconciliar perfil")
        self._notificar = notificar
        self._ocupado = False
        self._revogado = False

    def snapshot(self) -> EstadoSincronizadoM08:
        return self._coordenador.snapshot()

    def _enviar(self, estado: EstadoSincronizadoM08, mudou: bool):
        if mudou and self._notificar is not None:
            self._notificar(estado)

    def invalidar(self, motivo: str) -> EstadoSincronizadoM08:
        estado, mudou = self._coordenador.invalidar(motivo)
        self._enviar(estado, mudou)
        return estado

    def revogar(self, motivo: str = "Integração M11 desativada") -> EstadoSincronizadoM08:
        self._revogado = True
        return self.invalidar(motivo)

    def apurar_publicar(self) -> EntregaM11:
        if self._revogado or self.escopo.modo not in ("laboratorio", "producao"):
            raise IntegracaoM11Desativada("M11 não autoriza escopo inativo ou revogado")
        if self.escopo.modo == "producao":
            from .ativacao_producao_m25 import validar_escopo_producao_m25
            validar_escopo_producao_m25(self.escopo)
        if self._ocupado:
            raise IntegracaoM11Invalida("Apuração simultânea no mesmo coordenador")
        self._ocupado = True
        try:
            anterior_m25 = None
            if self.escopo.modo == "producao":
                from .persistencia_merito_m10 import ler_estado_merito
                anterior_m25 = ler_estado_merito(self.escopo.banco_merito, self.escopo.perfil_id)
            resultado = apurar_e_persistir_merito(
                self.escopo.banco_academico, self.escopo.banco_merito,
                perfil_id=self.escopo.perfil_id,
            )
            _verificar_apos_commit(resultado, escopo=self.escopo)
            if self.escopo.modo == "producao":
                from .ativacao_producao_m25 import backup_conquistas_m25
                backup_conquistas_m25(self.escopo, anterior_m25, resultado)
            ui, mudou = self._coordenador.publicar(resultado.resultado)
            self._enviar(ui, mudou)
            r = resultado.resultado.resumo
            return EntregaM11(
                revisao=ui.revisao, atualizado=mudou,
                saldo=r.saldo, recorde=r.recorde,
                brasao_atual=r.brasao_atual,
                perfil_id=self.escopo.perfil_id,
                conquistas=r.conquistas,
                estado_ui=ui,
            )
        except Exception as exc:
            # Não deixar o brasão da bateria/perfil apresentado como auditado
            # quando a leitura, commit, releitura ou notificação falhar.
            try:
                self.invalidar("Mérito global aguardando nova auditoria")
            except Exception:
                pass
            raise IntegracaoM11Invalida("Falha na apuração/publicação M11; exibição invalidada") from exc
        finally:
            self._ocupado = False
