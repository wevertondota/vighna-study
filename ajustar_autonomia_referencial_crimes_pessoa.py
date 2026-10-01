from __future__ import annotations
import json, re, sqlite3, shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
DB = ROOT/'estudos.db'
BACKUP = ROOT/'estudos_backup_antes_autonomia_referencial_2026-09-30.db'
MANIFEST = ROOT/'manifest_substituicao_crimes_contra_pessoa_2026-09-29.json'
AUDITS = {
    34: Path('/mnt/data/Auditoria_Final_CIE_Crimes_Contra_a_Vida_110Q.txt'),
    38: Path('/mnt/data/Auditoria_Final_Crimes_Contra_a_Honra_40Q.txt'),
    39: Path('/mnt/data/Auditoria_Final_Liberdade_Pessoal_80Q_BLOQUEIO.txt'),
}

# Tags curtas, apenas para tornar a alternativa semanticamente autônoma.
def scope_for(chapter_id:int, label:str) -> str:
    stem = label.split(' — ',1)[0].strip().lower()
    if chapter_id == 34:
        if stem in {'homicídio culposo','perdão judicial'}: return 'Homicídio culposo'
        if stem == 'feminicídio': return 'Feminicídio'
        if stem == 'vicaricídio': return 'Vicaricídio'
        if stem in {'suicídio/automutilação','resultado lesivo','resultado morte','duplicação','meios digitais','posição do autor','resultado gravíssimo especial','resultado morte especial'}:
            return 'Induzimento/instigação/auxílio a suicídio ou automutilação'
        if stem == 'infanticídio': return 'Infanticídio'
        if stem == 'aborto pela gestante': return 'Aborto provocado pela gestante'
        if stem == 'aborto sem consentimento': return 'Aborto provocado por terceiro sem consentimento'
        if stem == 'aborto com consentimento': return 'Aborto provocado por terceiro com consentimento'
        if stem in {'consentimento inválido','aborto qualificado'}: return 'Aborto provocado por terceiro'
        if stem in {'aborto necessário','aborto em gravidez de estupro','aborto não punido'}: return 'Aborto não punido'
        return 'Homicídio'
    if chapter_id == 38:
        if stem.startswith('calúnia') or stem == 'prova da verdade': return 'Calúnia'
        if stem == 'difamação': return 'Difamação'
        if stem.startswith('injúria'): return 'Injúria'
        if stem in {'exclusão','crítica','crítica artística','crítica científica','crítica literária','conceito funcional','publicidade'}:
            return 'Exclusão de injúria ou difamação'
        if stem == 'retratação': return 'Retratação da calúnia ou difamação'
        if stem == 'pedido de explicações': return 'Pedido de explicações nos crimes contra a honra'
        if stem == 'procedibilidade': return 'Procedibilidade nos crimes contra a honra'
        return 'Disposições comuns dos crimes contra a honra'
    if chapter_id == 39:
        m = {
            'constrangimento ilegal':'Constrangimento ilegal', 'bullying':'Bullying', 'cyberbullying':'Cyberbullying',
            'ameaça':'Ameaça', 'ameaça contra mulher':'Ameaça contra a mulher',
            'ameaça ligada ao crime organizado':'Ameaça ligada à criminalidade organizada',
            'ameaça organizada':'Ameaça ligada à criminalidade organizada',
            'perseguição':'Perseguição', 'violência psicológica':'Violência psicológica contra a mulher',
            'violência psicológica tecnológica':'Violência psicológica contra a mulher',
            'sequestro/cárcere':'Sequestro ou cárcere privado',
            'sequestro/cárcere agravado':'Sequestro ou cárcere privado',
            'sequestro/cárcere com sofrimento':'Sequestro ou cárcere privado',
            'sequestro/cárcere organizado':'Sequestro ou cárcere privado ligado à criminalidade organizada',
            'condição análoga à de escravo':'Redução a condição análoga à de escravo',
            'majorante escravo':'Redução a condição análoga à de escravo',
            'retenção':'Redução a condição análoga à de escravo',
            'tráfico de pessoas':'Tráfico de pessoas',
        }
        return m.get(stem, 'Crimes contra a liberdade pessoal')
    raise KeyError(chapter_id)

ANCHORS = {
    'Homicídio culposo':['homicídio culposo'], 'Feminicídio':['feminicídio'], 'Vicaricídio':['vicaricídio'],
    'Induzimento/instigação/auxílio a suicídio ou automutilação':['suicídio','automutilação'],
    'Infanticídio':['infanticídio'], 'Aborto provocado pela gestante':['aborto'],
    'Aborto provocado por terceiro sem consentimento':['aborto'], 'Aborto provocado por terceiro com consentimento':['aborto'],
    'Aborto provocado por terceiro':['aborto'], 'Aborto não punido':['aborto'], 'Homicídio':['homicídio'],
    'Calúnia':['calúnia'], 'Difamação':['difamação'], 'Injúria':['injúria'],
    'Exclusão de injúria ou difamação':['injúria','difamação'], 'Retratação da calúnia ou difamação':['retratação','calúnia','difamação'],
    'Pedido de explicações nos crimes contra a honra':['pedido de explicações'], 'Procedibilidade nos crimes contra a honra':['procedibilidade','queixa','representação','requisição'],
    'Disposições comuns dos crimes contra a honra':['crimes contra a honra','calúnia','difamação','injúria'],
    'Constrangimento ilegal':['constrangimento ilegal'], 'Bullying':['bullying','intimidação sistemática'], 'Cyberbullying':['cyberbullying','intimidação sistemática virtual'],
    'Ameaça':['ameaça'], 'Ameaça contra a mulher':['ameaça'], 'Ameaça ligada à criminalidade organizada':['ameaça','criminalidade organizada'],
    'Perseguição':['perseguição'], 'Violência psicológica contra a mulher':['violência psicológica'],
    'Sequestro ou cárcere privado':['sequestro','cárcere'], 'Sequestro ou cárcere privado ligado à criminalidade organizada':['sequestro','cárcere'],
    'Redução a condição análoga à de escravo':['condição análoga','escravo'], 'Tráfico de pessoas':['tráfico de pessoas'],
}

def parse_audit(path:Path):
    out={}
    txt=path.read_text(encoding='utf-8')
    for line in txt.splitlines():
        m=re.match(r'^Q(\d+):\s*(.*)$',line)
        if not m: continue
        qn=int(m.group(1)); out[qn]={}
        for part in m.group(2).split(' | '):
            mm=re.match(r'\s*([A-E])=(.*?) \[',part)
            if mm: out[qn][mm.group(1)]=mm.group(2).strip()
    return out

def has_anchor(text:str, scope:str)->bool:
    t=text.lower()
    return any(a in t for a in ANCHORS.get(scope,[]))

def add_scope(text:str, scope:str)->str:
    return f'{scope} — {text}'

# Padrões que denunciam referência genérica. Mesmo sem esses padrões, nos três capítulos mistos
# o tag é adicionado quando não há nenhum referente material explícito.
GENERIC = re.compile(r'''(?ix)
\bness[ae]s?\b|\bess[ae]s?\b|\bdess[ae]s?\b|
\bforma\s+(?:básica|especial|agravada|qualificada|resultante)\b|
\bmodalidade\s+(?:básica|especial|agravada|qualificada|consensual)\b|
\bhipótese\s+(?:especial|digital|agravada|qualificada|resultante)\b|
\bcondutas?\s+equiparad[ao]s?\b|^\s*(?:a|o)\s+(?:regra|redução|aumento|majorante|minorante|exceção|exclusão|retratação|pena)\b
''')

manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
qid_to_qnum={}
for ch in manifest['capitulos']:
    ids=ch['ids_reutilizados']+ch['ids_inseridos']
    for i,qid in enumerate(ids,1): qid_to_qnum[qid]=(ch['capitulo_id'],i)

audit_maps={cid:parse_audit(p) for cid,p in AUDITS.items()}
shutil.copy2(DB,BACKUP)
con=sqlite3.connect(DB)
con.row_factory=sqlite3.Row
con.execute('PRAGMA foreign_keys=ON')
cur=con.cursor()
changes=[]

# 1) Capítulos I, V e VI: usar o mapa auditado de microtema para adicionar contexto somente quando falta referente explícito.
for cid in (34,38,39):
    rows=cur.execute('''SELECT q.id qid,a.id aid,a.letra,a.texto FROM questoes q JOIN alternativas_questoes a ON a.questao_id=q.id
        WHERE q.topico_id=22 AND q.capitulo_id=? AND q.ativa=1 AND q.excluida=0 ORDER BY q.id,a.ordem''',(cid,)).fetchall()
    for r in rows:
        qnum=qid_to_qnum[int(r['qid'])][1]
        label=audit_maps[cid][qnum][r['letra']]
        scope=scope_for(cid,label)
        old=r['texto']
        # Nos capítulos de alternativas independentes, ausência do referente do microtema já é suficiente para ajuste.
        if not has_anchor(old,scope):
            new=add_scope(old,scope)
            cur.execute('UPDATE alternativas_questoes SET texto=? WHERE id=?',(new,r['aid']))
            changes.append((r['qid'],r['letra'],old,new,scope))

# 2) Rixa: enunciados mistos e referências genéricas; explicitar o instituto.
for r in cur.execute('''SELECT q.id qid,a.id aid,a.letra,a.texto FROM questoes q JOIN alternativas_questoes a ON a.questao_id=q.id
    WHERE q.topico_id=22 AND q.capitulo_id=37 AND q.ativa=1 AND q.excluida=0 ORDER BY q.id,a.ordem''').fetchall():
    old=r['texto']
    if 'rixa' not in old.lower():
        new=add_scope(old,'Rixa')
        cur.execute('UPDATE alternativas_questoes SET texto=? WHERE id=?',(new,r['aid']))
        changes.append((r['qid'],r['letra'],old,new,'Rixa'))

# 3) Lesões corporais: corrigir apenas opções sem referente material claro.
manual = {
    (5720,'A'):'Lesão corporal — Ofender a integridade corporal ou a saúde de outrem configura a forma básica, punida com detenção de três meses a um ano.',
}
# 4) Periclitação: pontos de referência genérica encontrados na auditoria.
manual.update({
    (5748,'D'):'Exposição ou abandono de recém-nascido — A forma básica prevê detenção de seis meses a dois anos.',
    (5901,'B'):'Perigo decorrente de transporte irregular para prestação de serviços — A majorante alcança estabelecimentos de qualquer natureza.',
    (5910,'B'):'Perigo decorrente de transporte irregular para prestação de serviços — A majorante não se limita a estabelecimentos industriais.',
})
for (qid,letra),new in manual.items():
    rr=cur.execute('SELECT a.id,a.texto FROM alternativas_questoes a JOIN questoes q ON q.id=a.questao_id WHERE q.id=? AND a.letra=? AND q.topico_id=22 AND q.ativa=1 AND q.excluida=0',(qid,letra)).fetchone()
    if rr and rr['texto']!=new:
        cur.execute('UPDATE alternativas_questoes SET texto=? WHERE id=?',(new,rr['id']))
        changes.append((qid,letra,rr['texto'],new,'manual'))

# Atualizar updated_at das questões efetivamente alteradas, sem tocar em IDs/gabaritos/status.
changed_qids=sorted({int(x[0]) for x in changes})
if changed_qids:
    marks=','.join('?'*len(changed_qids))
    cur.execute(f"UPDATE questoes SET atualizado_em=datetime('now','localtime') WHERE id IN ({marks})",changed_qids)

# Atualizar snapshots SOMENTE de itens ainda não respondidos, preservando histórico já respondido e tentativas.
# Isso permite continuar a bateria atual sem reset e já ver os textos corrigidos nos itens pendentes.
updated_snapshots=0
for item in cur.execute('''SELECT i.id,i.questao_id FROM itens_sessao_questoes i
    JOIN sessoes_questoes s ON s.id=i.sessao_id
    WHERE i.questao_id IN (SELECT id FROM questoes WHERE topico_id=22 AND ativa=1 AND excluida=0)
      AND i.estado IN ('nao_alcancada','nao_respondida','planejada','apresentada')''').fetchall():
    qid=item['questao_id']
    if qid not in changed_qids: continue
    alts=[dict(x) for x in cur.execute('SELECT letra,texto,correta,ordem FROM alternativas_questoes WHERE questao_id=? ORDER BY ordem',(qid,)).fetchall()]
    cur.execute('UPDATE itens_sessao_questoes SET alternativas_snapshot=? WHERE id=?',(json.dumps(alts,ensure_ascii=False),item['id']))
    updated_snapshots+=1

con.commit()
# validações
integrity=cur.execute('PRAGMA integrity_check').fetchone()[0]
fk=cur.execute('PRAGMA foreign_key_check').fetchall()
active_q=cur.execute('SELECT count(*) FROM questoes WHERE topico_id=22 AND ativa=1 AND excluida=0').fetchone()[0]
active_a=cur.execute('''SELECT count(*) FROM alternativas_questoes a JOIN questoes q ON q.id=a.questao_id WHERE q.topico_id=22 AND q.ativa=1 AND q.excluida=0''').fetchone()[0]
cycle=cur.execute("SELECT id,status FROM ciclos_questoes WHERE topico_id=22 AND status='ativo' ORDER BY id DESC LIMIT 1").fetchone()
cycle_stats=None
if cycle:
    cycle_stats=dict(cur.execute("SELECT count(*) total, sum(estado='respondida') respondidas, sum(estado='pendente') pendentes FROM ciclo_questoes_itens WHERE ciclo_id=?",(cycle['id'],)).fetchone())
attempts=cur.execute('SELECT count(*) FROM tentativas_questoes WHERE topico_id_snapshot=22 OR questao_id IN (SELECT id FROM questoes WHERE topico_id=22)').fetchone()[0]
# Gabarito e estrutura continuam válidos
bad=[]
for q in cur.execute('SELECT id FROM questoes WHERE topico_id=22 AND ativa=1 AND excluida=0'):
    stats=cur.execute('SELECT count(*) n,sum(correta) c,count(distinct letra) l FROM alternativas_questoes WHERE questao_id=?',(q['id'],)).fetchone()
    if tuple(stats)!=(5,1,5): bad.append((q['id'],tuple(stats)))
con.close()

report={
    'data':'2026-09-30', 'topico_id':22, 'questoes_ativas':active_q,'alternativas_ativas':active_a,
    'alternativas_ajustadas':len(changes),'questoes_ajustadas':len(changed_qids),
    'snapshots_pendentes_atualizados':updated_snapshots,'tentativas_preservadas':attempts,
    'ciclo_ativo':dict(cycle) if cycle else None,'ciclo_ativo_estado':cycle_stats,
    'integrity_check':integrity,'foreign_key_violations':len(fk),'questoes_estrutura_invalida':bad,
    'estrategia':'UPDATE in-place de alternativas; IDs, gabaritos, ciclo, tentativas e itens respondidos preservados',
    'mudancas':[{'questao_id':q,'letra':l,'antes':o,'depois':n,'escopo':s} for q,l,o,n,s in changes],
}
(ROOT/'RELATORIO_AJUSTE_AUTONOMIA_REFERENCIAL_CRIMES_PESSOA_2026-09-30.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='mudancas'},ensure_ascii=False,indent=2))
