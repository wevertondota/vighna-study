"""QA V3.1.53-R1 em fontes descartaveis; nao abre GUI nem dados reais."""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import painel_core as core
import painel_homologacao as ui
import painel_central_qa as qa
ROOT = Path(__file__).parent

class ReconciliacaoR1(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='vighnalab_r1_')
        self.addCleanup(self.tmp.cleanup)
        self.temp=Path(self.tmp.name)
        self.bundle=self.temp/'bundle'
        self.bundle.mkdir()
        for name in qa.FROZEN_RESOURCE_SHA256:
            (self.bundle/name).write_bytes((ROOT/name).read_bytes())

    def test_01_hash_identidade_fonte(self):
        self.assertEqual(hashlib.sha256((ROOT/'PAINEL_VERSAO.json').read_bytes()).hexdigest(),ui.QA_IDENTITY_SHA256)
        self.assertEqual(ui.QA_IDENTITY_SHA256,qa.FROZEN_RESOURCE_SHA256['PAINEL_VERSAO.json'])
        self.assertEqual(json.loads((ROOT/'PAINEL_VERSAO.json').read_text())['version'], ui.QA_IDENTITY_VERSION)

    def test_02_identidade_frozen_autentica_hash(self):
        with patch.object(ui.sys,'frozen',True,create=True),patch.object(ui.sys,'_MEIPASS',str(self.bundle),create=True):
            self.assertEqual(ui._qa_identity()['versao'],'3.1.53')

    def test_03_negativo_versao_maliciosa(self):
        (self.bundle/'PAINEL_VERSAO.json').write_text('{"component":"vighna-panel","version":"3.1.99"}',encoding='utf8')
        with patch.object(ui.sys,'frozen',True,create=True),patch.object(ui.sys,'_MEIPASS',str(self.bundle),create=True):
            with self.assertRaises(RuntimeError):ui._qa_identity()

    def test_04_negativo_json_reordenado(self):
        (self.bundle/'PAINEL_VERSAO.json').write_text('{"version":"3.1.53","component":"vighna-panel"}',encoding='utf8')
        with patch.object(ui.sys,'frozen',True,create=True),patch.object(ui.sys,'_MEIPASS',str(self.bundle),create=True):
            with self.assertRaises(RuntimeError):ui._qa_identity()

    def test_05_recurso_ausente(self):
        (self.bundle/'PAINEL_VERSAO.json').unlink()
        with patch.object(ui.sys,'frozen',True,create=True),patch.object(ui.sys,'_MEIPASS',str(self.bundle),create=True):
            with self.assertRaises(RuntimeError):ui._qa_identity()

    def test_06_sem_meipass_falha_fechado(self):
        with patch.object(ui.sys,'frozen',True,create=True),patch.object(ui.sys,'_MEIPASS',None,create=True):
            with self.assertRaises(RuntimeError):ui._qa_identity()

    def test_07_redirecionamento_falha_fechado(self):
        source=self.bundle/'PAINEL_VERSAO.json'
        source.unlink()
        try:source.symlink_to(ROOT/'PAINEL_VERSAO.json')
        except OSError:self.skipTest('symlink indisponivel')
        with patch.object(ui.sys,'frozen',True,create=True),patch.object(ui.sys,'_MEIPASS',str(self.bundle),create=True):
            with self.assertRaises(RuntimeError):ui._qa_identity()

    def test_08_recursos_planejamento_triplo(self):
        self.assertEqual(set(qa.FROZEN_RESOURCE_SHA256),{'PAINEL_VERSAO.json','estado_planejamento_v3.json','estado_planejamento_v2a.json'})
        with patch.object(qa.sys,'frozen',True,create=True),patch.object(qa.sys,'_MEIPASS',str(self.bundle),create=True):
            result=qa._frozen_integrity(self.temp/'recursos.json')
        self.assertEqual(result['status'],'PASSOU')

    def test_09_config_salva_fora_recursos(self):
        state=self.temp/'estado'/'config.json'
        with patch.object(core,'CONFIG',state),patch.object(core,'APP_ROOT',self.bundle):
            core.save_python_path(' C:/lab/python.exe ')
            self.assertEqual(core.load_config()['python_qt'],'C:/lab/python.exe')
        self.assertTrue(state.is_file())
        self.assertFalse((self.bundle/'painel_configuracao_local.json').exists())

    def test_10_config_link_nao_sobrescrito(self):
        target=self.temp/'original.json';target.write_text('sentinela',encoding='utf8')
        link=self.temp/'link.json'
        try:link.symlink_to(target)
        except OSError:self.skipTest('symlink indisponivel')
        with patch.object(core,'CONFIG',link):core.save_python_path('outro')
        self.assertEqual(target.read_text('utf8'),'sentinela')

    def test_11_diagnosticos_nao_usam_app_root(self):
        with patch.object(core,'APP_ROOT',self.bundle),patch.object(core.tempfile,'gettempdir',return_value=str(self.temp)):
            result=core.diagnostics_folder()
        self.assertEqual(result,self.temp/'VighnaLab_Diagnosticos')

    def test_11a_dossie_persistente_fora_recursos(self):
        state=self.temp/'estado'
        with patch.object(core,'_state_folder',return_value=state),patch.object(core,'APP_ROOT',self.bundle):
            destination=core.dossier_folder()
        self.assertEqual(destination,state/'G7_Dossies')
        self.assertTrue(destination.is_dir())
        self.assertFalse((self.bundle/'G7_Dossies').exists())

    def test_12_guardas_gui_antes_de_subprocessos(self):
        tree=ast.parse((ROOT/'painel_homologacao.py').read_text('utf8'))
        klass=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Painel')
        functions={n.name:n for n in klass.body if isinstance(n,ast.FunctionDef)}
        for name in ('_start','_start_g5b','_start_g5c','_start_g6a','_start_g6b','_start_g6b2'):
            body=functions[name].body
            self.assertIsInstance(body[0],ast.If,name)
            self.assertIn('_block_frozen_external',ast.unparse(body[0]),name)

    def test_13_guardas_workers(self):
        tree=ast.parse((ROOT/'painel_homologacao.py').read_text('utf8'))
        klass=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Painel')
        functions={n.name:n for n in klass.body if isinstance(n,ast.FunctionDef)}
        for name in ('_worker','_worker_g5b','_worker_g5c','_worker_g6a','_worker_g6b','_worker_g6b2','_worker_g5a'):
            self.assertIsInstance(functions[name].body[0],ast.If,name)
            self.assertIn('frozen',ast.unparse(functions[name].body[0]),name)

    def test_14_spec_tem_tres_recursos(self):
        spec=(ROOT/'VighnaLab_QA_V3153_R1.spec').read_text('utf8')
        for item in qa.FROZEN_RESOURCE_SHA256:self.assertIn(item,spec)
        self.assertIn('Analysis(',spec)

    def test_15_protocolo_rejeita_argumentos_extras(self):
        self.assertEqual(ui._qa_child_dispatch([ui.QA_CHILD_MARKER,'--protocolo','1','identidade','--destino=estudos.db']),2)
        self.assertEqual(ui._qa_child_dispatch(['-c','print(123)']),2)

if __name__ == '__main__':unittest.main(verbosity=2)
