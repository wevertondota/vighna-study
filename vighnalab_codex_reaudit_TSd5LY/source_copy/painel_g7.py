# -*- coding: utf-8 -*-
"""G7 — auditoria documental em modo somente leitura; NUNCA autoriza instalação.

Lê apenas três evidências G6 previamente revisadas e os metadados de Gates
fornecidos pelo painel. Não executa ZIPs, não extrai binários nem abre SQLite.
SHA-256 representa integridade/consistência, NÃO identidade do emissor.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
import zipfile

RC2 = 'structural-m2-int1-settings-r1d-rc2'
REFERENCE = {
    'G6-A': ('G6_A_DIAGNOSTICO_20261013_032012_074778.zip',
             '3dcdf13e787f7af20f67c6b7ad27640105549d7bef14e928a39c84b5c91ef2de'),
    'G6-B1': ('G6_B1_EVIDENCIA_APROVADA_20261013_122825.zip',
              '5344d6b1fed3c1170ac668ba82a6f0d079af31c38ceee1f7648aa558bf237b56'),
    'G6-B2': ('G6_B2_DIAGNOSTICO_20261013_133334_559402.zip',
              '6e8217bc79fa413f585c6e088b1e5d8ddee7c3294f6599ebf94d91406ab81544'),
}
MAX_ZIP = 12_000_000
MAX_TOTAL = 22_000_000
MAX_SINGLE = 6_000_000
MAX_MEMBERS = 32

class G7EvidenceError(ValueError):
    pass


def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for b in iter(lambda: stream.read(1_048_576),b''):h.update(b)
    return h.hexdigest()


def _load_zip(path: Path, expected_sha: str) -> dict[str,bytes]:
    if path.is_symlink() or not path.is_file() or not 0<path.stat().st_size<=MAX_ZIP:
        raise G7EvidenceError('Arquivo ausente, link ou tamanho acima do limite')
    if digest(path)!=expected_sha:
        raise G7EvidenceError('SHA-256 do ZIP diverge da evidência já revisada')
    try:
        with zipfile.ZipFile(path) as z:
            infos=z.infolist()
            if not 2<=len(infos)<=MAX_MEMBERS or sum(i.file_size for i in infos)>MAX_TOTAL:
                raise G7EvidenceError('Conteúdo acima da cota')
            names=[i.filename for i in infos]
            if len(names)!=len(set(n.casefold() for n in names)):
                raise G7EvidenceError('Nomes duplicados no ZIP')
            for i in infos:
                if (i.is_dir() or '/' in i.filename or '\\' in i.filename
                    or ':' in i.filename or i.filename.startswith('.')
                    or (i.flag_bits & 1) or i.file_size>MAX_SINGLE):
                    raise G7EvidenceError('Entrada insegura no ZIP')
            data={i.filename:z.read(i) for i in infos}
            if z.testzip() is not None:
                raise G7EvidenceError('CRC divergente')
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise G7EvidenceError('ZIP inválido: '+type(exc).__name__) from exc
    if 'MANIFESTO_SHA256.json' not in data:
        raise G7EvidenceError('Manifesto SHA-256 não encontrado')
    try:
        hashes=json.loads(data['MANIFESTO_SHA256.json'].decode('utf-8-sig'))
    except (UnicodeError,ValueError) as exc:
        raise G7EvidenceError('Manifesto JSON inválido') from exc
    if not isinstance(hashes,dict) or set(hashes)!=set(data)-{'MANIFESTO_SHA256.json'}:
        raise G7EvidenceError('Manifesto não cobre exatamente o conteúdo')
    for name,val in hashes.items():
        if not isinstance(val,str) or len(val)!=64 or hashlib.sha256(data[name]).hexdigest()!=val.lower():
            raise G7EvidenceError('Hash interno divergente: '+name)
    return data


def _json_member(data:dict[str,bytes], name:str)->dict:
    if name not in data:
        raise G7EvidenceError('Resultado obrigatório ausente: '+name)
    try:obj=json.loads(data[name].decode('utf-8-sig'))
    except (UnicodeError,ValueError) as exc:raise G7EvidenceError('JSON inválido: '+name) from exc
    if not isinstance(obj,dict):raise G7EvidenceError('Resultado não é objeto: '+name)
    return obj


def _true(obj:dict, key:str)->bool:
    return obj.get(key) is True


def _false(obj:dict, key:str)->bool:
    return obj.get(key) is False


def _scenarios(guest:dict, stage:str)->None:
    expected=(
        {'sucesso':'ATUALIZACAO_SINTETICA_APLICADA','build':'FALHA_SIMULADA_REVERTIDA',
         'after_commit':'FALHA_SIMULADA_REVERTIDA'} if stage=='G6-A' else
        {'sucesso':'PASSOU_B1_TRANSACAO_REAL','falha_compilacao':'PASSOU_B1_ROLLBACK_REAL',
         'falha_pos_commit':'PASSOU_B1_ROLLBACK_REAL'} if stage=='G6-B1' else
        {'sucesso':'PASSOU_B2_BUILD_ORIGINAL','falha_compilacao':'PASSOU_B2_ROLLBACK_ORIGINAL',
         'falha_pos_commit':'PASSOU_B2_ROLLBACK_ORIGINAL'}
    )
    items=guest.get('cenarios')
    if not isinstance(items,list) or len(items)!=3 or any(not isinstance(i,dict) for i in items):
        raise G7EvidenceError('Três cenários válidos são obrigatórios')
    states={i.get('cenario'):i.get('status') for i in items}
    if states!=expected:
        raise G7EvidenceError('Cenários ausentes, duplicados ou com estado inesperado')
    if stage=='G6-A':return
    for scenario in items:
        key=scenario['cenario']
        if (not _true(scenario,'banco_qa_preservado') or
            not _true(scenario,'motor_original_invocado') or
            not _true(scenario.get('smoke_antes') or {},'stable') or
            not _true(scenario.get('smoke_depois') or {},'stable') or
            scenario.get('fase_checkpoint')!=('installed' if key=='sucesso' else
                'pre_commit_no_snapshot' if key=='falha_compilacao' else 'recovered') or
            scenario.get('historico_final')!=('installed' if key=='sucesso' else 'failed')):
            raise G7EvidenceError('Banco, smoke, motor ou checkpoint inconsistente: '+key)
        comparisons=scenario.get('comparacoes_sqlite')
        if not isinstance(comparisons,list) or not any(
            c.get('de')=='apos_iniciar_executavel_r1d' and
            str(c.get('para','')).startswith('apos_transacao_') and
            c.get('logica_alterada') is False and c.get('fisica_alterada') is False
            for c in comparisons if isinstance(c,dict)):
            raise G7EvidenceError('Preservação transacional não demonstrada: '+key)
        if stage=='G6-B2' and not _true(scenario,'build_original_invocado'):
            raise G7EvidenceError('PyInstaller original não demonstrado: '+key)


def review_g6(stage:str, path:Path)->dict:
    name,pinned_sha=REFERENCE[stage]
    result={'etapa':stage,'arquivo':name,'sha256_referencia':pinned_sha,'status':'BLOQUEADO'}
    try:
        if path.name!=name: raise G7EvidenceError('Nome de evidência não corresponde à referência')
        data=_load_zip(path,pinned_sha)
        if stage=='G6-A':
            obj=_json_member(data,'RESUMO_G6A.json')
            if (obj.get('component')!='vighna-g6a-synthetic' or obj.get('alvo')!=RC2 or
                obj.get('resultado')!='PASSOU_G6A_SINTETICO' or
                not _false(obj,'instalacao_autorizada') or not _false(obj,'gate_g6_aprovado') or
                not _false(obj,'execucao_exe_real')):
                raise G7EvidenceError('Identidade e escopo do G6-A incoerentes')
            _scenarios(obj,stage)
        else:
            prefix='G6B1' if stage=='G6-B1' else 'G6B2'
            host=_json_member(data,'RESUMO_'+prefix+'.json')
            guest=_json_member(data,'RESULTADO_'+prefix+'.json')
            component=('vighna-g6b1-' if stage=='G6-B1' else 'vighna-g6b2-')
            status=('PASSOU_B1_EXECUTAVEIS_REAIS' if stage=='G6-B1' else
                    'PASSOU_B2_PYINSTALLER_ORIGINAL_SANDBOX')
            if (host.get('component')!=component+'host' or guest.get('component')!=component+'guest'
                or host.get('status')!=status or guest.get('status')!=status
                or host.get('guest')!=guest
                or host.get('target_build')!=RC2 or guest.get('target_build')!=RC2
                or not _false(host,'instalacao_autorizada') or not _false(guest,'instalacao_autorizada')
                or not _false(host,'gate_g6_aprovado') or not _false(guest,'gate_g6_aprovado')
                or not _false(host,'user_db_or_installation_used')
                or not _true(host,'windows_sandbox_executado')
                or not _true(guest,'windows_sandbox_executado')):
                raise G7EvidenceError('Relatórios host/guest incoerentes')
            if stage=='G6-B1' and (not _true(host,'original_engine_exercised_in_guest') or
                not _true(guest,'engine_original_qa') or not _true(host,'guest_probe_passed')
                or not _false(host,'original_builder_in_guest')):
                raise G7EvidenceError('Contratos do G6-B1 incoerentes')
            if stage=='G6-B2' and (not _true(host,'original_builder_in_guest') or
                not _true(guest,'original_builder_in_guest')):
                raise G7EvidenceError('Build original não comprovado')
            internal='MANIFESTO_'+prefix+'_SHA256.json'
            internal_manifest=_json_member(data,internal)
            need={'RESULTADO_'+prefix+'.json'}
            if stage=='G6-B1':need.add('DIAGNOSTICO_SQLITE_G6B1.json')
            if not need<=set(internal_manifest):raise G7EvidenceError('Manifesto guest incompleto')
            for filename in need:
                if internal_manifest[filename]!=hashlib.sha256(data[filename]).hexdigest():
                    raise G7EvidenceError('Manifesto guest divergente: '+filename)
            _scenarios(guest,stage)
        result.update(status='EVIDENCIA_CONFERIDA',cenarios=3,
                      observacao='Consistência de integridade e contratos verificada; autoria não autenticada')
    except (G7EvidenceError,OSError,KeyError,TypeError) as exc:
        result['motivo']=str(exc)[:220]
    return result


def evaluate(archive_dir:Path, gate_report:dict)->dict:
    folder=Path(archive_dir)
    if folder.is_symlink() or not folder.is_dir():
        raise G7EvidenceError('Selecione pasta de evidências válida, sem links')
    review={key:review_g6(key,folder/name) for key,(name,_) in REFERENCE.items()}
    gates={g.get('id'):g.get('situacao') for g in gate_report.get('gates',[])
           if isinstance(g,dict)}
    earlier={key:gates.get(key,'PENDENTE') for key in ('G1','G2','G3','G4','G5')}
    pending=[]
    pending.extend(key+': evidência não estabelecida' for key,val in earlier.items() if val!='EVIDENCIADO')
    pending.extend(key+': '+item.get('motivo','bloqueado') for key,item in review.items()
                   if item['status']!='EVIDENCIA_CONFERIDA')
    pending.extend([
        'Aceite formal independente dos Gates G5 e G6 não apresentado',
        'Nove falhas históricas da suíte ampla V3.1.16 sem reclassificação e reteste integral documentados',
        'Validação operacional no Windows do encerramento controlado V3.1.20 não comprovada',
        'Teste integral de backup/restauração e release final ainda sem aceite documental',
        'Identidade/autoria das evidências não autenticadas apenas pelos hashes',
        'Aprovação humana, verificação de backup externo e decisão de implantação ausentes',
    ])
    return {'component':'vighnalab-g7-readiness','versao_painel':'3.1.22',
            'target_build':RC2, 'gerado_em_utc':datetime.now(timezone.utc).isoformat(),
            'resultado':'PENDENTE_REVISAO_FORMAL', 'gates_anteriores':earlier,
            'evidencias_g6':review,'pendencias':pending,
            'gate_g6_aprovado':False,'gate_g7_aprovado':False,
            'instalacao_autorizada':False,
            'limite':'SHA-256 comprova integridade/consistência, não autoria. Relatório não libera instalação.',
            'acoes_realizadas':'Leitura de ZIPs QA e metadados; nenhum banco pessoal acessado.'}


def export(report:dict, output:Path)->Path:
    """Empacota apenas JSON de parecer e manifesto, sem ZIP-fonte, banco ou EXE."""
    path=Path(output)
    if path.suffix.lower()!='.zip' or not path.name.startswith('G7_DOSSIE_PRELIMINAR_'):
        raise G7EvidenceError('Destino deve ser ZIP de dossiê G7')
    if path.exists() or not path.parent.is_dir():
        raise G7EvidenceError('Destino já existe ou pasta indisponível')
    if report.get('instalacao_autorizada') is not False or report.get('gate_g7_aprovado') is not False:
        raise G7EvidenceError('Dossiê não pode aprovar instalação')
    raw=json.dumps(report,indent=2,ensure_ascii=False).encode('utf-8')
    payload={'PARECER_G7.json':raw}
    payload['MANIFESTO_SHA256.json']=json.dumps({'PARECER_G7.json':hashlib.sha256(raw).hexdigest()},indent=2).encode()
    fd,temp=tempfile.mkstemp(prefix='.g7_temp_',suffix='.zip',dir=path.parent)
    os.close(fd)
    try:
        with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
            for name,data in payload.items():z.writestr(name,data)
        with zipfile.ZipFile(temp) as z:
            if z.testzip() is not None:raise G7EvidenceError('Dossiê ZIP corrompido')
        if path.exists():raise G7EvidenceError('Destino passou a existir; operação cancelada')
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)
    return path
