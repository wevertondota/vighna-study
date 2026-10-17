# -*- coding: utf-8 -*-
"""Importação offline, estrita e reversível de checkpoints JSON de planejamento.

Formato V3: ZIP com 'planejamento.json' e 'manifesto.json' apenas.
O SHA-256 protege a integridade, NÃO autentica o autor nem autoriza instalação.
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import io
import json
import os
import tempfile
import zipfile

import painel_planejamento as plan

BUNDLED_V3 = Path(__file__).with_name("estado_planejamento_v3.json")
from painel_historico import storage_root

FORMAT='vighna-plano-checkpoint-v3'
MAX_ZIP=180_000
MAX_JSON=120_000
MAX_ENTRIES=2

class CheckpointError(ValueError):pass


def imported_path(root:Path|None=None)->Path:
    return (Path(root) if root is not None else storage_root())/'planejamento_atual_v3.json'


def sha(content:bytes)->str:return hashlib.sha256(content).hexdigest()


def strict_fields(state:dict) -> None:
    """Não importar chaves desconhecidas ou dados ocultos em checkpoints."""
    allowed={'schema','projeto','data_referencia','checkpoint','origem',
             'instalacao_autorizada','sincronizacao_online','trabalho_registrado',
             'proximas_atividades','marcos','macrolotes'}
    if set(state)!=allowed:
        raise CheckpointError('Chaves inesperadas ou ausentes no planejamento')
    if set(state['trabalho_registrado'])!={'titulo','detalhe','situacao'}:
        raise CheckpointError('Campos inesperados em trabalho_registrado')
    if any(set(x)!={'nome','situacao'} for x in state['proximas_atividades']):
        raise CheckpointError('Campos inesperados nas próximas atividades')
    if any(set(x)!={'id','nome','situacao','resumo','proxima_acao'} for x in state['macrolotes']):
        raise CheckpointError('Campos inesperados nos macrolotes')
    if set(state['marcos'])!={'qt_m2','atualizador','seguranca','build','m3','instalacao'}:
        raise CheckpointError('Campos inesperados nos marcos')


def read_checkpoint(file:Path)->dict:
    file=Path(file)
    if not file.is_file() or file.stat().st_size > MAX_ZIP:
        raise CheckpointError('Pacote ausente ou grande demais')
    try:
        with zipfile.ZipFile(file) as z:
            infos=z.infolist()
            if len(infos)!=MAX_ENTRIES or {i.filename for i in infos}!={'planejamento.json','manifesto.json'}:
                raise CheckpointError('O ZIP deve conter somente planejamento.json e manifesto.json')
            if z.testzip() is not None or any(i.is_dir() or i.file_size>MAX_JSON or (i.flag_bits & 1) for i in infos):
                raise CheckpointError('ZIP inválido, criptografado ou fora dos limites')
            state_raw=z.read('planejamento.json')
            manifest=json.loads(z.read('manifesto.json').decode('utf-8'))
            state=json.loads(state_raw.decode('utf-8'))
    except (OSError,UnicodeError,zipfile.BadZipFile,KeyError,json.JSONDecodeError) as exc:
        raise CheckpointError('Não foi possível ler os dados JSON do checkpoint') from exc
    if not isinstance(manifest,dict) or manifest.get('format') != FORMAT:
        raise CheckpointError('Formato de manifesto desconhecido')
    if set(manifest) != {'format','sha256','data_checkpoint'} or manifest['sha256'] != sha(state_raw):
        raise CheckpointError('Manifesto ou SHA-256 divergente')
    if not isinstance(state,dict) or manifest['data_checkpoint']!=state.get('data_referencia'):
        raise CheckpointError('Data de referência divergente')
    try:
        plan.validar_estado(state)
        strict_fields(state)
    except (ValueError,TypeError,KeyError) as exc:raise CheckpointError('Planejamento inválido: '+str(exc)) from exc
    # Um arquivo de dados nunca libera instalação, integra M3 nem altera código.
    if state['instalacao_autorizada'] is not False or state['sincronizacao_online'] is not False:
        raise CheckpointError('Estado não pode autorizar instalação/sincronização')
    return state


def make_checkpoint(state:dict,output:Path)->Path:
    """Apenas para produzir os checkpoints da conversa; não executa código externo."""
    plan.validar_estado(state)
    strict_fields(state)
    raw=json.dumps(state,ensure_ascii=False,indent=2,sort_keys=True).encode('utf-8')
    manifest={'format':FORMAT,'sha256':sha(raw),'data_checkpoint':state['data_referencia']}
    output=Path(output)
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('planejamento.json',raw)
        z.writestr('manifesto.json',json.dumps(manifest,ensure_ascii=False,indent=2).encode())
    return output


def load_effective(root:Path|None=None)->dict:
    imported=imported_path(root)
    if not imported.is_file():return plan.carregar_estado(BUNDLED_V3 if BUNDLED_V3.exists() else plan.DEFAULT_PATH)
    # Mesmo se o arquivo local tiver sido adulterado, não interpretar código.
    try:
        if imported.stat().st_size > MAX_JSON:raise CheckpointError('Estado local excessivo')
        state=plan.validar_estado(json.loads(imported.read_text(encoding='utf-8')))
        strict_fields(state)
        return state
    except (OSError,ValueError,TypeError) as exc:
        raise CheckpointError('Checkpoint local ilegível ou inválido; não foi substituído: '+str(exc)) from exc


def apply_checkpoint(file:Path,root:Path|None=None)->dict:
    """Operação manual, depois de confirmação visual: substituição atômica local.

    Preserva a cópia anterior no mesmo armazenamento, sem tocar no VighnaStudy.
    """
    state=read_checkpoint(file)
    destination=imported_path(root)
    destination.parent.mkdir(parents=True,exist_ok=True)
    old=destination.read_bytes() if destination.is_file() else None
    if old is not None:
        # Recusar estado local inválido em vez de sobrescrever um problema.
        load_effective(root)
    temp=destination.parent/(destination.name+'.novo')
    backup=destination.parent/'planejamento_anterior_v3.json'
    try:
        if old is not None:
            with backup.open('wb') as f:
                f.write(old);f.flush();os.fsync(f.fileno())
        with temp.open('xb') as f:
            f.write(json.dumps(state,ensure_ascii=False,indent=2).encode('utf-8'))
            f.flush();os.fsync(f.fileno())
        os.replace(temp,destination)
    finally:
        temp.unlink(missing_ok=True)
    return state


def export_status(state:dict, gate_summary:dict, output:Path)->Path:
    """Exporta somente planejamento, resumo de gates e dados não sensíveis."""
    plan.validar_estado(state)
    strict_fields(state)
    safe_gates=[{k:row[k] for k in ('id','nome','situacao','observacao')} for row in gate_summary['gates']]
    content={'format':'vighna-status-export-v3','planejamento':state,
             'gates':safe_gates,'instalacao_autorizada':False,
             'aviso':'Dados locais, não são telemetria nem autenticação de evidência.'}
    raw=json.dumps(content,ensure_ascii=False,indent=2).encode('utf-8')
    output=Path(output)
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('STATUS_PARA_CHATGPT.json',raw)
        z.writestr('MANIFESTO_SHA256.json',json.dumps({'STATUS_PARA_CHATGPT.json':sha(raw)}))
    return output
