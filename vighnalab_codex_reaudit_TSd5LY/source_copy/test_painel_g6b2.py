# -*- coding: utf-8 -*-
"""G6-B2 offline, fail-closed structural and isolated unit tests; NO Windows approval."""
import ast
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET
import zipfile

import painel_g6b2 as host
import painel_g6b2_guest as guest


class G6B2Contracts(unittest.TestCase):
    def test_sandbox_network_off_and_readonly_inputs(self):
        xml=host.sandbox_xml(Path(r'C:\qa\entrada'),Path(r'C:\qa\saida'),
                             Path(r'C:\python'),Path(r'C:\qa\site'))
        tree=ET.fromstring(xml)
        for name in ('Networking','ClipboardRedirection','vGPU','PrinterRedirection'):
            self.assertEqual(tree.findtext(name),'Disable')
        mounts=tree.findall('./MappedFolders/MappedFolder')
        self.assertEqual(len(mounts),4)
        self.assertEqual([m.findtext('ReadOnly') for m in mounts],
                         ['true','false','true','true'])
        self.assertIn('G6B2_GUEST.exe',xml)
        self.assertNotIn('estudos.db',xml)

    def test_gate_never_declares_release_authorization(self):
        for name in ('sucesso','falha_compilacao','falha_pos_commit'):
            self.assertIn(name,host.SCENARIOS)
        self.assertEqual(host.SCENARIOS['falha_compilacao'][1], 'pre_commit_no_snapshot')
        self.assertEqual(host.SCENARIOS['falha_pos_commit'][1], 'recovered')

    def test_success_report_requires_all_three_scenarios(self):
        result={'component':'vighna-g6b2-guest','version':'3.1.19',
                'target_build':host.RC2_BUILD,'instalacao_autorizada':False,
                'gate_g6_aprovado':False,'windows_sandbox_executado':True,
                'original_builder_in_guest':True,
                'status':'PASSOU_B2_PYINSTALLER_ORIGINAL_SANDBOX','cenarios':[]}
        with self.assertRaises(host.G6B2SafetyError):host.validate_guest_report(result)
        base=lambda name:{'cenario':name,'status':host.SCENARIOS[name][0],
            'fase_checkpoint':host.SCENARIOS[name][1],
            'historico_final':host.SCENARIOS[name][2],
            'banco_qa_preservado':True,'motor_original_invocado':True,
            'build_original_invocado':True,'pyinstaller_log_sha256':'a'*64,
            'pyinstaller_log_bytes':10,'smoke_antes':{'stable':True},
            'smoke_depois':{'stable':True},
            'comparacoes_sqlite':[{}, {'logica_alterada':False,'fisica_alterada':False}, {'logica_alterada':False}, {'logica_alterada':False}]}
        result['cenarios']=[base(k) for k in host.SCENARIOS]
        host.validate_guest_report(result)
        result['cenarios'][1]['build_original_invocado']=False
        with self.assertRaises(host.G6B2SafetyError):host.validate_guest_report(result)
        result['cenarios'][1]['build_original_invocado']=True
        result['cenarios'][2]['comparacoes_sqlite'][2]['logica_alterada']=True
        with self.assertRaises(host.G6B2SafetyError):host.validate_guest_report(result)

    def test_qa_icon_is_supplied_by_verified_rc2_reference(self):
        import homologador_windows as h
        rc2=h.checked_archive(h.KIT/'insumos'/h.RC2,prefix='codigo/')
        icon=rc2.get('vighnastudy.ico')
        self.assertIsInstance(icon,bytes)
        self.assertEqual(icon[:4],b'\x00\x00\x01\x00')
        with TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'sources';source.mkdir()
            (root/'vighnastudy.ico').write_bytes(icon)
            digest=guest.stage_qa_icon(root,source)
            self.assertEqual(digest,guest.q.hash_file(root/'vighnastudy.ico'))
            self.assertEqual((source/'vighnastudy.ico').read_bytes(),icon)
            with self.assertRaises(RuntimeError):guest.stage_qa_icon(root,source)

    def test_qa_icon_missing_or_tampered_is_blocked(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'s';source.mkdir()
            with self.assertRaises(RuntimeError):guest.stage_qa_icon(root,source)
            (root/'vighnastudy.ico').write_bytes(b'bad-icon')
            with self.assertRaises(RuntimeError):guest.stage_qa_icon(root,source)
            self.assertFalse((source/'vighnastudy.ico').exists())

    def test_guest_requires_icon_prior_to_engine_execution(self):
        tree=ast.parse(Path(guest.__file__).read_text(encoding='utf8'))
        scenario=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run_scenario')
        code=ast.get_source_segment(Path(guest.__file__).read_text(encoding='utf8'),scenario)
        self.assertLess(code.index('stage_qa_icon('),code.index('q.load_engine('))
        self.assertLess(code.index('stage_qa_icon('),code.index('engine.install_package('))
        self.assertNotIn('runner=',code)

    def test_no_approval_even_when_guest_reports_status(self):
        with TemporaryDirectory() as tmp:
            out=Path(tmp)/'evidencias'
            with patch.object(guest.sys,'platform','linux'):
                rc=guest.run(Path(tmp)/'missing',out)
            self.assertEqual(rc,1)
            x=json.loads((out/'RESULTADO_G6B2.json').read_text())
            self.assertFalse(x['instalacao_autorizada'])
            self.assertFalse(x['gate_g6_aprovado'])
            self.assertFalse(x['original_builder_in_guest'])
            manifest=json.loads((out/'MANIFESTO_G6B2_SHA256.json').read_text())
            self.assertEqual(guest.q.hash_file(out/'RESULTADO_G6B2.json'),
                             manifest['RESULTADO_G6B2.json'])

    def test_input_manifest_hash_tamper(self):
        with TemporaryDirectory() as tmp:
            base=Path(tmp)
            for i in range(5):(base/f'{i}.txt').write_text('QA')
            files={p.name:guest.q.hash_file(p) for p in base.iterdir()}
            (base/'MANIFESTO_G6B2.json').write_text(json.dumps({
                'component':'vighna-g6b2-input','target_build':guest.RC2_BUILD,
                'instalacao_autorizada':False,'build_original_dentro_sandbox':True,
                'sha256_files':files}))
            guest.verify_input(base)
            (base/'1.txt').write_text('modified')
            with self.assertRaises(ValueError):guest.verify_input(base)

    def test_input_traversal_rejected(self):
        with TemporaryDirectory() as tmp:
            base=Path(tmp)
            for i in range(5):(base/f'{i}.txt').write_text('QA')
            files={p.name:guest.q.hash_file(p) for p in base.iterdir()}
            files['../private.py']='a'*64
            (base/'MANIFESTO_G6B2.json').write_text(json.dumps({
                'component':'vighna-g6b2-input','target_build':guest.RC2_BUILD,
                'instalacao_autorizada':False,'build_original_dentro_sandbox':True,
                'sha256_files':files}))
            with self.assertRaises(ValueError):guest.verify_input(base)

    def test_runtime_does_not_fallback_to_system_python(self):
        with patch.object(guest,'PYTHON_BASE',Path('/missing/qa/python')), \
             patch.object(guest,'QA_PACKAGES',Path('/missing/qa/site')):
            with self.assertRaises(RuntimeError):guest.runtime_environment()

    def test_checked_qa_runtime_rejects_arbitrary_python(self):
        with TemporaryDirectory() as tmp:
            py=Path(tmp)/'python.exe';py.write_bytes(b'Not a QA venv')
            with self.assertRaises(host.G6B2SafetyError):host.checked_qa_runtime(py)

    def test_exact_original_builder_call_has_no_runner_override(self):
        tree=ast.parse(Path(guest.__file__).read_text(encoding='utf8'))
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and
               isinstance(n.func,ast.Attribute) and n.func.attr=='install_package']
        self.assertEqual(len(calls),1)
        self.assertNotIn('runner',[kw.arg for kw in calls[0].keywords])
        self.assertIn('python_exe',[kw.arg for kw in calls[0].keywords])
        src=Path(guest.__file__).read_text()
        self.assertIn("FALHA_QA_G6B2_BUILD",src)
        self.assertIn("FALHA_QA_G6B2_POST_COMMIT",src)

    def test_g6b2_records_sandbox_closure_without_forced_shutdown(self):
        source=Path(host.__file__).read_text(encoding='utf8')
        self.assertIn("result['encerramento_sandbox'] = b1.close_own_sandbox(",source)
        closer=Path(host.b1.__file__).read_text(encoding='utf8')
        block=closer.split('def close_own_sandbox(')[1].split('def build(')[0]
        self.assertNotIn('process.terminate(',block)
        self.assertNotIn('process.kill(',block)
        self.assertIn('fechamento_pendente_manual',block)

    def test_host_denies_linux(self):
        with patch.object(host.sys,'platform','linux'):
            with self.assertRaises(host.G6B2SafetyError):host.run()

    def test_diagnostic_zip_integrity(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)
            log=path/'BUILD_R1D.log';log.write_text('Synthetic')
            zipname=host.diagnostic_zip(path,{'gate_g6_aprovado':False},[log])
            with zipfile.ZipFile(zipname) as z:
                self.assertIsNone(z.testzip())
                marks=json.loads(z.read('MANIFESTO_SHA256.json'))
                for name,hash in marks.items():
                    self.assertEqual(hash,guest.q.hashlib.sha256(z.read(name)).hexdigest())


if __name__=='__main__': unittest.main()
