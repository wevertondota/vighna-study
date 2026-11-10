"""M13 — parte pesada da apuração executável no worker, sem Qt.

Usa o M09/M10 e a verificação de durabilidade M11. NÃO publica no M08
nesta thread. A publicação é entregue à thread principal pelo adaptador Qt.
M25 admite modo 'producao' somente depois de revalidar origem oficial e identidade.
"""
from __future__ import annotations
from .contrato_historico_merito import ResultadoIntegracao
from .integracao_merito_m11 import EscopoM11, IntegracaoM11Desativada, _verificar_apos_commit
from .persistencia_merito_m10 import apurar_e_persistir_merito


def apurar_no_worker_m13(escopo: EscopoM11) -> ResultadoIntegracao:
    if not isinstance(escopo, EscopoM11) or escopo.modo not in ("laboratorio", "producao"):
        raise IntegracaoM11Desativada("M13 recebeu escopo não autorizado")
    if escopo.modo == "producao":
        from .ativacao_producao_m25 import validar_escopo_producao_m25
        validar_escopo_producao_m25(escopo)
    anterior = None
    if escopo.modo == "producao":
        from .persistencia_merito_m10 import ler_estado_merito
        anterior = ler_estado_merito(escopo.banco_merito, escopo.perfil_id)
    persistido = apurar_e_persistir_merito(
        escopo.banco_academico, escopo.banco_merito, perfil_id=escopo.perfil_id)
    _verificar_apos_commit(persistido, escopo=escopo)
    if escopo.modo == "producao":
        from .ativacao_producao_m25 import backup_conquistas_m25
        backup_conquistas_m25(escopo, anterior, persistido)
    if persistido.resultado.gravacao_realizada is not True:
        raise RuntimeError("Resultado sem COMMIT certificado")
    return persistido.resultado
