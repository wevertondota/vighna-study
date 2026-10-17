# -*- coding: utf-8 -*-
"""Gates, segurança do sincronizador e preservação do motor V2-B."""
from __future__ import annotations
import ast, copy, hashlib, io, json, os, sqlite3, tempfile, unittest, zipfile
from pathlib import Path
from unittest.mock import patch
from painel_historico import HistoryStore
from painel_gates import evaluate, APROVADO, PENDENTE, FALHOU, BLOQUEADO
from painel_checkpoints import read_checkpoint, make_checkpoint, apply_checkpoint, load_effective, CheckpointError, export_status
import painel_planejamento as plane
from test_historico_v2b import fixture

ROOT=Path(__file__).parent

def evfile(file:Path, *, preflight='PASSOU', security='PASSOU', qt='PASSOU', sqlite='PASSOU', build=None):
    steps={'preflight':{'status':preflight},'guardas_de_seguranca':{'status':security},
           'atualizacao_sintetica':{'status':sqlite}}
    steps.update({f'qt_windows_{x}':{'status':qt} for x in ('100','125','150')})
    if build is not None:steps['pyinstaller']={'status':build}
    obj={'homologador':'V1.1','modo':'testes' if build is None else 'build',
         'ambiente':'Windows','python':'3.13','testes':steps,'instalacao_autorizada':False}
    blob=json.dumps(obj).encode()
    entries={'RESUMO_HOMOLOGACAO.json':blob}
    manifest={k:hashlib.sha256(v).hexdigest() for k,v in entries.items()}
    with zipfile.ZipFile(file,'w',zipfile.ZIP_DEFLATED) as z:
        for k,v in entries.items():z.writestr(k,v)
        z.writestr('MANIFESTO_SHA256.json',json.dumps(manifest))
    return file

class V3GatesTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); self.store=HistoryStore(self.root/'hist')
    def test_01_sem_evidencias_tudo_pendente(self):
        x=evaluate(self.store);self.assertEqual(x['pendentes'],7)
    def test_02_nunca_autoriza_instalacao(self):
        self.store.import_zip(evfile(self.root/'pass.zip',build='PASSOU'))
        self.assertIs(evaluate(self.store)['instalacao_autorizada'],False)
    def test_03_passos_1_a_4_documentados(self):
        self.store.import_zip(evfile(self.root/'pass.zip',build='PASSOU'))
        x=evaluate(self.store)
        self.assertEqual([a['situacao'] for a in x['gates']], [APROVADO]*4+[PENDENTE]*3)
    def test_04_sem_build_gate4_pendente(self):
        self.store.import_zip(evfile(self.root/'pass.zip'))
        self.assertEqual(evaluate(self.store)['gates'][3]['situacao'],PENDENTE)
    def test_05_qt_falhou(self):
        self.store.import_zip(evfile(self.root/'fail.zip',qt='FALHOU'))
        self.assertEqual(evaluate(self.store)['gates'][1]['situacao'],FALHOU)
    def test_06_seguranca_bloqueada(self):
        self.store.import_zip(evfile(self.root/'block.zip',security='BLOQUEADO'))
        self.assertEqual(evaluate(self.store)['gates'][0]['situacao'],BLOQUEADO)
    def test_07_falha_mais_recente_prevalece(self):
        self.store.import_zip(evfile(self.root/'old.zip'))
        self.store.import_zip(evfile(self.root/'new.zip',qt='FALHOU'))
        self.assertEqual(evaluate(self.store)['gates'][1]['situacao'],FALHOU)
    def test_08_m3_nao_integrado(self):
        self.assertIn('m2-',evaluate(self.store)['alvo'])
        self.assertNotIn('M3',evaluate(self.store)['alvo'])

class V3CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.state=plane.carregar_estado(ROOT/'estado_planejamento_v3.json')
    def test_09_checkpoint_valido(self):
        file=make_checkpoint(self.state,self.root/'valid.zip')
        self.assertEqual(read_checkpoint(file)['checkpoint'],self.state['checkpoint'])
    def test_10_manifesto_modificado_bloqueado(self):
        p=make_checkpoint(self.state,self.root/'ok.zip')
        with zipfile.ZipFile(p) as z:contents={n:z.read(n) for n in z.namelist()}
        contents['planejamento.json']=contents['planejamento.json'].replace(b'VighnaStudy',b'QualquerApp')
        with zipfile.ZipFile(self.root/'fake.zip','w') as z:
            for n,b in contents.items():z.writestr(n,b)
        with self.assertRaises(CheckpointError):read_checkpoint(self.root/'fake.zip')
    def test_11_instalacao_true_bloqueada(self):
        altered=copy.deepcopy(self.state);altered['instalacao_autorizada']=True
        with self.assertRaises(ValueError):make_checkpoint(altered,self.root/'bad.zip')
    def test_12_synconline_true_bloqueada(self):
        altered=copy.deepcopy(self.state);altered['sincronizacao_online']=True
        with self.assertRaises(ValueError):make_checkpoint(altered,self.root/'bad.zip')
    def test_13_zip_com_codigo_rejeitado(self):
        p=make_checkpoint(self.state,self.root/'ok.zip')
        with zipfile.ZipFile(p,'a') as z:z.writestr('shell.py','print("PERIGO")')
        with self.assertRaises(CheckpointError):read_checkpoint(p)
    def test_14_zip_com_arquivo_extra_rejeitado(self):
        p=make_checkpoint(self.state,self.root/'ok.zip')
        with zipfile.ZipFile(p,'a') as z:z.writestr('outro.json','{}')
        with self.assertRaises(CheckpointError):read_checkpoint(p)
    def test_15_versao_desconhecida_rejeitada(self):
        p=make_checkpoint(self.state,self.root/'ok.zip')
        with zipfile.ZipFile(p) as z: raw=z.read('planejamento.json')
        manifest={'format':'outro','sha256':hashlib.sha256(raw).hexdigest(),
                  'data_checkpoint':self.state['data_referencia']}
        with zipfile.ZipFile(self.root/'bad.zip','w') as z:
            z.writestr('planejamento.json',raw)
            z.writestr('manifesto.json',json.dumps(manifest))
        with self.assertRaises(CheckpointError):read_checkpoint(self.root/'bad.zip')
    def test_16_confirma_importacao_e_persistencia(self):
        p=make_checkpoint(self.state,self.root/'ok.zip')
        self.assertEqual(apply_checkpoint(p,self.root)['checkpoint'],self.state['checkpoint'])
        self.assertEqual(load_effective(self.root)['checkpoint'],self.state['checkpoint'])
    def test_17_segunda_importacao_preserva_anterior(self):
        p=make_checkpoint(self.state,self.root/'ok.zip');apply_checkpoint(p,self.root)
        nextstate=copy.deepcopy(self.state);nextstate['checkpoint']='CHECKPOINT-02'
        np=make_checkpoint(nextstate,self.root/'next.zip');apply_checkpoint(np,self.root)
        old=json.loads((self.root/'planejamento_anterior_v3.json').read_text(encoding='utf-8'))
        self.assertEqual(old['checkpoint'],self.state['checkpoint'])
    def test_18_nao_altera_estado_em_erro(self):
        p=make_checkpoint(self.state,self.root/'ok.zip');apply_checkpoint(p,self.root)
        prev=(self.root/'planejamento_atual_v3.json').read_bytes()
        bad=self.root/'broken.zip';bad.write_bytes(b'zip incorreto')
        with self.assertRaises(CheckpointError):apply_checkpoint(bad,self.root)
        self.assertEqual((self.root/'planejamento_atual_v3.json').read_bytes(),prev)
    def test_19_rejeita_json_gigante(self):
        p=self.root/'giant.zip';p.write_bytes(b'abc'*100_000)
        with self.assertRaises(CheckpointError):read_checkpoint(p)
    def test_20_nao_executa_codigo_externo(self):
        source=(ROOT/'painel_checkpoints.py').read_text()
        self.assertNotIn('eval(',source);self.assertNotIn('exec(',source)
    def test_21_exportacao_apenas_dados(self):
        x=evaluate(HistoryStore(self.root/'hist'))
        out=export_status(self.state,x,self.root/'status.zip')
        with zipfile.ZipFile(out) as z:
            data=json.loads(z.read('STATUS_PARA_CHATGPT.json'))
            self.assertIs(data['instalacao_autorizada'],False)
            self.assertNotIn('estudos.db',z.namelist())
            self.assertEqual(z.testzip(),None)
    def test_22_definicoes_m1_m9_inalteradas(self):
        self.assertEqual([v['id'] for v in self.state['macrolotes']],['M'+str(n) for n in range(1,10)])
    def test_23_m2_rc2_sem_autorizacao(self):
        self.assertEqual(self.state['macrolotes'][1]['situacao'],'homologacao')
        self.assertFalse(self.state['instalacao_autorizada'])
    def test_24_m3_experimental(self):
        self.assertEqual(self.state['macrolotes'][2]['situacao'],'laboratorio')
    def test_25_rejeita_campos_adicionais_ocultos(self):
        altered=copy.deepcopy(self.state);altered['comando_extra']='perigo'
        with self.assertRaises(CheckpointError):make_checkpoint(altered,self.root/'not_allowed.zip')

    def test_26_rejeita_campos_extras_em_marcos(self):
        altered=copy.deepcopy(self.state);altered['marcos']['segredo']='NUNCA'
        with self.assertRaises(CheckpointError):make_checkpoint(altered,self.root/'not_allowed.zip')

    def test_27_importado_e_independente_do_programa(self):
        p=make_checkpoint(self.state,self.root/'ok.zip');apply_checkpoint(p,self.root)
        self.assertTrue((self.root/'planejamento_atual_v3.json').is_file())
        self.assertFalse((self.root/'estudos.db').exists())

if __name__=='__main__':unittest.main()
