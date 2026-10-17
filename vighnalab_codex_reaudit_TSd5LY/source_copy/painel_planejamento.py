# -*- coding: utf-8 -*-
"""Leitor estrito do plano VighnaStudy V2-A, sem dependências GUI ou rede.

O arquivo é uma fotografia de um checkpoint, NÃO um estado sincronizado com
ChatGPT, o Windows ou o software principal do VighnaStudy.
"""
from __future__ import annotations
import json
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().with_name("estado_planejamento_v2a.json")
STATUS = {
    "referencia": "Base de referência",
    "homologacao": "Em homologação",
    "laboratorio": "Experimental",
    "planejado": "Planejado",
}

class EstadoInvalido(ValueError):
    pass

def _texto(value, name):
    if not isinstance(value, str) or not value.strip() or len(value) > 1200:
        raise EstadoInvalido("Campo inválido: " + name)
    return value

def validar_estado(obj):
    if not isinstance(obj, dict) or obj.get("schema") != 1:
        raise EstadoInvalido("Schema do planejamento não suportado")
    for campo in ("projeto", "data_referencia", "checkpoint", "origem"):
        _texto(obj.get(campo), campo)
    if obj["projeto"] != "VighnaStudy":
        raise EstadoInvalido("Projeto divergente")
    if obj.get("instalacao_autorizada") is not False or obj.get("sincronizacao_online") is not False:
        raise EstadoInvalido("O plano local não pode autorizar instalação ou alegar sincronização online")
    trabalho = obj.get("trabalho_registrado")
    if not isinstance(trabalho, dict):
        raise EstadoInvalido("Trabalho atual ausente")
    for chave in ("titulo", "detalhe", "situacao"):
        _texto(trabalho.get(chave), chave)
    proximas = obj.get("proximas_atividades")
    if not isinstance(proximas, list) or not 1 <= len(proximas) <= 12:
        raise EstadoInvalido("Próximas atividades inválidas")
    for tarefa in proximas:
        if not isinstance(tarefa, dict):
            raise EstadoInvalido("Tarefa inválida")
        _texto(tarefa.get("nome"), "nome da tarefa")
        _texto(tarefa.get("situacao"), "situação da tarefa")
    marcos = obj.get("marcos")
    if not isinstance(marcos, dict):
        raise EstadoInvalido("Marcos ausentes")
    for name in ("qt_m2", "atualizador", "seguranca", "build", "m3", "instalacao"):
        _texto(marcos.get(name), name)
    lotes = obj.get("macrolotes")
    if not isinstance(lotes, list) or len(lotes) != 9:
        raise EstadoInvalido("O planejamento precisa conter exatamente M1–M9")
    ids = set()
    for lot in lotes:
        if not isinstance(lot, dict):
            raise EstadoInvalido("Registro de macrolote inválido")
        name = _texto(lot.get("id"), "id macrolote")
        if name in ids:
            raise EstadoInvalido("Macrolote duplicado: " + name)
        ids.add(name)
        for key in ("nome", "resumo", "proxima_acao"):
            _texto(lot.get(key), key)
        if lot.get("situacao") not in STATUS:
            raise EstadoInvalido("Situação de macrolote não reconhecida")
    if ids != {"M" + str(n) for n in range(1, 10)}:
        raise EstadoInvalido("Faltam identificadores M1–M9")
    return obj

def carregar_estado(path=DEFAULT_PATH):
    path = Path(path)
    if path.stat().st_size > 120_000:
        raise EstadoInvalido("Arquivo de planejamento excessivamente grande")
    return validar_estado(json.loads(path.read_text(encoding="utf-8")))

def panorama(obj):
    obj = validar_estado(obj)
    retorno = {k: 0 for k in STATUS}
    for macrolote in obj["macrolotes"]:
        retorno[macrolote["situacao"]] += 1
    return retorno
