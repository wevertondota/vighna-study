# -*- coding: utf-8 -*-
"""Gates V3 somente informativos. Nunca produz autorização de instalação.

Um ZIP validado por checksum não autentica sua origem; o aceite humano continua
obrigatório. Evidências vêm apenas do histórico isolado do Painel, não do VighnaStudy.
"""
from __future__ import annotations
from painel_historico import HistoryStore

RC2 = 'structural-m2-int1-settings-r1d-rc2'
PENDENTE = 'PENDENTE'
APROVADO = 'EVIDENCIADO'
FALHOU = 'FALHOU'
BLOQUEADO = 'BLOQUEADO'

GATES = (
    ('G1', 'Integridade e proteção', 'preflight+guardas', 'Preflight e guardas do homologador'),
    ('G2', 'Qt Windows', 'qt', 'Três escalas Qt no Windows; não equivale a DPI físico'),
    ('G3', 'SQLite e rollback sintéticos', 'atualizacao_sintetica', 'Somente dados QA; não testa dados pessoais'),
    ('G4', 'Compilação real PyInstaller', 'pyinstaller', 'Build QA com VighnaStudy.spec original R1D'),
    ('G5', 'Smoke do EXE real isolado', None, 'Não coberto pelo homologador atual'),
    ('G6', 'Atualização final e reversão Windows', None, 'Exige teste próprio de release em cópia descartável'),
    ('G7', 'Auditoria e aprovação humana', None, 'Não é concedida automaticamente pelo painel'),
)


def _state(s: str | None):
    return { 'PASSOU': APROVADO, 'FALHOU': FALHOU, 'BLOQUEADO': BLOQUEADO}.get(s, PENDENTE)


def _pick_run(store: HistoryStore, runs: list[dict], keys: tuple[str, ...]):
    """Última execução contendo TODAS as etapas; evita juntar partes arbitrárias."""
    for run in runs:
        if run.get('target_build') != RC2:
            continue
        steps = {x['step_key']: x['status'] for x in store.steps_for(run['id'])}
        if all(k in steps for k in keys):
            return run, steps
    return None, {}


def evaluate(store: HistoryStore) -> dict:
    runs = store.list_runs()
    result=[]
    for code,title,key,note in GATES:
        keys = (('qt_windows_100','qt_windows_125','qt_windows_150') if key == 'qt'
                else ('preflight','guardas_de_seguranca') if key == 'preflight+guardas'
                else ((key,) if key else ()))
        status=PENDENTE
        source='Nenhuma evidência correspondente registrada'
        if keys:
            run,steps=_pick_run(store,runs,keys)
            if run is not None:
                values=[_state(steps[x]) for x in keys]
                status=(FALHOU if FALHOU in values else
                        BLOQUEADO if BLOQUEADO in values else
                        APROVADO if all(v == APROVADO for v in values) else PENDENTE)
                source=f'Evidência #{run["id"]}: {run["filename"]}'
        result.append({'id':code,'nome':title,'situacao':status,
                       'origem':source,'observacao':note})
    return {'alvo':RC2,'gates':result,
            'evidenciados':sum(x['situacao']==APROVADO for x in result),
            'falhas':sum(x['situacao']==FALHOU for x in result),
            'bloqueados':sum(x['situacao']==BLOQUEADO for x in result),
            'pendentes':sum(x['situacao']==PENDENTE for x in result),
            'instalacao_autorizada':False,
            'parecer':'SOMENTE ACOMPANHAMENTO; SEM AUTORIZAÇÃO DE INSTALAÇÃO',
            'nota':'Hash verifica integridade, não autenticidade. Gates G5–G7 exigem evidência e decisão separadas.'}
