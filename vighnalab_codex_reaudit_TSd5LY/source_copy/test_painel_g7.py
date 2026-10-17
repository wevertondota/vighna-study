# -*- coding: utf-8 -*-
"""Auditoria de regressão de G7 estritamente sintética e sem execuções externas."""
import copy, hashlib, json, tempfile, unittest, zipfile
from pathlib import Path
from unittest.mock import patch
import painel_g7 as g

class G7Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.folder=Path(self.tmp.name)
        self.gates={'gates':[{'id':'G'+str(n),'situacao':'EVIDENCIADO'} for n in range(1,6)]}

    def test_01_vazio_bloqueia(self):
        o=g.evaluate(self.folder,self.gates)
        self.assertFalse(o['instalacao_autorizada'])
        self.assertEqual(sum(x['status']=='BLOQUEADO' for x in o['evidencias_g6'].values()),3)
    def test_02_gates_nao_aprovam_g7(self):
        o=g.evaluate(self.folder,self.gates)
        self.assertFalse(o['gate_g6_aprovado']);self.assertFalse(o['gate_g7_aprovado'])
        self.assertIn('Nove falhas',str(o['pendencias']))
    def test_03_sem_g1_g5(self):
        o=g.evaluate(self.folder,{'gates':[]})
        self.assertEqual(len(o['gates_anteriores']),5)
        self.assertIn('G1: evidência não estabelecida',o['pendencias'])
    def test_04_zip_corrompido(self):
        path=self.folder/g.REFERENCE['G6-A'][0];path.write_bytes(b'corrompido')
        self.assertEqual(g.review_g6('G6-A',path)['status'],'BLOQUEADO')
    def test_05_zip_sem_manifesto(self):
        path=self.folder/'bad.zip'
        with zipfile.ZipFile(path,'w') as z:z.writestr('RESUMO_G6A.json','{}')
        with patch.object(g,'digest',return_value='pin'):
            with self.assertRaises(g.G7EvidenceError):g._load_zip(path,'pin')
    def test_06_zip_com_entrada_insegura(self):
        path=self.folder/'bad.zip'
        with zipfile.ZipFile(path,'w') as z:
            z.writestr('../path.txt','x');z.writestr('MANIFESTO_SHA256.json','{}')
        with patch.object(g,'digest',return_value='pin'):
            with self.assertRaises(g.G7EvidenceError):g._load_zip(path,'pin')
    def test_07_hash_interno_trocado(self):
        path=self.folder/'bad.zip'
        with zipfile.ZipFile(path,'w') as z:
            z.writestr('RESUMO_G6A.json','alterado')
            z.writestr('MANIFESTO_SHA256.json',json.dumps({'RESUMO_G6A.json':'f'*64}))
        with patch.object(g,'digest',return_value='pin'):
            with self.assertRaises(g.G7EvidenceError):g._load_zip(path,'pin')
    def test_08_cenario_duplicado_rejeitado(self):
        obj={'cenarios':[{'cenario':'sucesso','status':'PASSOU_B2_BUILD_ORIGINAL'}]*3}
        with self.assertRaises(g.G7EvidenceError):g._scenarios(obj,'G6-B2')
    def test_09_build_false_rejeitado(self):
        scene={'cenario':'sucesso','status':'PASSOU_B2_BUILD_ORIGINAL',
               'banco_qa_preservado':True,'motor_original_invocado':True,
               'build_original_invocado':False,'smoke_antes':{'stable':True},
               'smoke_depois':{'stable':True},'fase_checkpoint':'installed',
               'historico_final':'installed','comparacoes_sqlite':[{'de':'apos_iniciar_executavel_r1d',
               'para':'apos_transacao_sucesso','logica_alterada':False,'fisica_alterada':False}]}
        obj={'cenarios':[scene,{'cenario':'falha_compilacao','status':'PASSOU_B2_ROLLBACK_ORIGINAL'},
                                {'cenario':'falha_pos_commit','status':'PASSOU_B2_ROLLBACK_ORIGINAL'}]}
        with self.assertRaises(g.G7EvidenceError):g._scenarios(obj,'G6-B2')
    def test_10_dossie_sem_exes(self):
        output=self.folder/'G7_DOSSIE_PRELIMINAR_teste.zip'
        report=g.evaluate(self.folder,self.gates)
        g.export(report,output)
        with zipfile.ZipFile(output) as z:
            self.assertEqual(set(z.namelist()),{'PARECER_G7.json','MANIFESTO_SHA256.json'})
            self.assertFalse(json.loads(z.read('PARECER_G7.json'))['instalacao_autorizada'])
            self.assertEqual(json.loads(z.read('MANIFESTO_SHA256.json'))['PARECER_G7.json'],
                             hashlib.sha256(z.read('PARECER_G7.json')).hexdigest())
        with self.assertRaises(g.G7EvidenceError):g.export(report,output)
    def test_11_nao_aceita_parecer_que_autoriza(self):
        o=g.evaluate(self.folder,self.gates);o['instalacao_autorizada']=True
        with self.assertRaises(g.G7EvidenceError):g.export(o,self.folder/'G7_DOSSIE_PRELIMINAR_bad.zip')
    def test_12_nome_arquivo_importa(self):
        p=self.folder/'outro.zip';p.write_bytes(b'foo')
        self.assertEqual(g.review_g6('G6-A',p)['status'],'BLOQUEADO')
    def test_13_b2_nao_aceita_wal_mutado(self):
        # Comprovação exige preservação física E lógica na transação.
        name='G6-B2'; s={'cenario':'sucesso','status':'PASSOU_B2_BUILD_ORIGINAL',
            'banco_qa_preservado':True,'motor_original_invocado':True,'build_original_invocado':True,
            'smoke_antes':{'stable':True},'smoke_depois':{'stable':True},
            'fase_checkpoint':'installed','historico_final':'installed',
            'comparacoes_sqlite':[{'de':'apos_iniciar_executavel_r1d','para':'apos_transacao_sucesso',
                                    'logica_alterada':False,'fisica_alterada':True}]}
        with self.assertRaises(g.G7EvidenceError):g._scenarios({'cenarios':[s,s,s]},name)

if __name__=='__main__':unittest.main()
