# -*- coding: utf-8 -*-
"""G6-B1 safeguards. No real executable or Sandbox launched by these tests."""
import hashlib
import json
import shutil
import sqlite3
from contextlib import closing
from pathlib import Path, PureWindowsPath, PosixPath
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET
import zipfile

import painel_g6b as host
import painel_g6b_guest as guest


class G6B1Tests(unittest.TestCase):
    @staticmethod
    def _synthetic_db(path):
        with closing(sqlite3.connect(path)) as con:
            with con:
                con.execute('CREATE TABLE g6b_marker(id INTEGER PRIMARY KEY, data TEXT)')
                con.execute('INSERT INTO g6b_marker VALUES (39,?)',('SOMENTE_QA_G6B1',))

    def test_sqlite_snapshot_records_physical_logical_and_auxiliary_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/'estudos.db'
            with closing(sqlite3.connect(db)) as writer:
                writer.execute('PRAGMA journal_mode=WAL')
                writer.execute('CREATE TABLE g6b_marker(id INTEGER PRIMARY KEY, data TEXT)')
                writer.execute('INSERT INTO g6b_marker VALUES (39,?)',('SOMENTE_QA_G6B1',))
                writer.commit()
                snap=guest.sqlite_snapshot(db,'apos_criar_sqlite_sintetico')
        self.assertEqual(snap['integridade'],['ok'])
        self.assertEqual(snap['chaves_estrangeiras'],[])
        self.assertEqual(snap['marcador_qa'],[[39,'SOMENTE_QA_G6B1']])
        self.assertIn('g6b_marker',snap['tabelas'])
        self.assertTrue(snap['arquivos_fisicos']['estudos.db']['existe'])
        self.assertTrue(snap['arquivos_fisicos']['estudos.db-wal']['existe'])
        self.assertTrue(snap['arquivos_fisicos']['estudos.db-shm']['existe'])
        self.assertEqual(len(snap['arquivos_fisicos']['estudos.db']['sha256']),64)

    def test_sqlite_divergence_names_first_changed_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/'estudos.db';self._synthetic_db(db)
            before=guest.sqlite_snapshot(db,'baseline_r1d')
            with closing(sqlite3.connect(db)) as con:
                with con:
                    con.execute("UPDATE g6b_marker SET data='ALTERADO_SEM_AUTORIZACAO'")
            after=guest.sqlite_snapshot(db,'apos_transacao')
            with self.assertRaises(guest.SQLiteDivergence) as caught:
                guest.require_sqlite_preserved(before,after,physical=True)
        self.assertEqual(caught.exception.divergence['categoria'],'registros')
        self.assertEqual(caught.exception.divergence['item'],
                         'g6b_marker.registros_sha256')

    def test_sqlite_sequence_is_physical_but_still_strict_during_transaction(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/'estudos.db'
            with closing(sqlite3.connect(db)) as con:
                with con:
                    con.execute('CREATE TABLE g6b_marker(id INTEGER PRIMARY KEY, data TEXT)')
                    con.execute('INSERT INTO g6b_marker VALUES (39,?)',('SOMENTE_QA_G6B1',))
                    con.execute('CREATE TABLE startup_cache(id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT)')
            before=guest.sqlite_snapshot(db,'antes_startup')
            with closing(sqlite3.connect(db)) as con:
                with con:
                    con.execute("INSERT INTO startup_cache(data) VALUES ('transitorio')")
                    con.execute('DELETE FROM startup_cache')
            after=guest.sqlite_snapshot(db,'depois_startup')
        comparison=guest.sqlite_comparison(before,after)
        self.assertFalse(comparison['logica_alterada'])
        self.assertTrue(comparison['fisica_alterada'])
        guest.require_sqlite_preserved(before,after,physical=False)
        with self.assertRaises(guest.SQLiteDivergence) as caught:
            guest.require_sqlite_preserved(before,after,physical=True)
        self.assertEqual(caught.exception.divergence['categoria'],
                         'metadado_fisico_sqlite')
        self.assertEqual(caught.exception.divergence['item'],'sqlite_sequence')

    def test_sandbox_offline_and_limited_mounts(self):
        xml=host.sandbox_xml(Path(r'C:\QA\input'),Path(r'C:\QA\output'))
        tree=ET.fromstring(xml)
        for n in ('Networking','ClipboardRedirection','vGPU','PrinterRedirection'):
            self.assertEqual(tree.findtext(n),'Disable')
        maps=tree.findall('.//MappedFolder')
        self.assertEqual(len(maps),2)
        self.assertEqual([m.findtext('ReadOnly') for m in maps],['true','false'])
        self.assertNotIn('estudos.db',xml)
        self.assertIn('G6B1_GUEST.exe',xml)

    def test_sandbox_closure_graceful_and_pid_scoped(self):
        class Process:
            def __init__(self, running=True, timeout=False):
                self.running=running;self.timeout=timeout
                self.pid=12345;self.terminated=0;self.killed=0;self.waited=0
            def poll(self):return None if self.running else 0
            def terminate(self):self.terminated+=1;self.running=False
            def kill(self):self.killed+=1;self.running=False
            def wait(self,timeout):
                self.waited+=1
                if self.timeout:raise host.subprocess.TimeoutExpired('sandbox',timeout)
                self.running=False;return 0

        with patch.object(host,'_request_close_owned_sandbox_window',return_value=1) as close:
            running=Process()
            result=host.close_own_sandbox(running)
            self.assertEqual(result['estado'],'encerrado_graciosamente')
            close.assert_called_once_with(12345)
            self.assertEqual((running.terminated,running.killed),(0,0))
        with patch.object(host,'_request_close_owned_sandbox_window',return_value=0):
            running=Process()
            result=host.close_own_sandbox(running)
            self.assertEqual(result['estado'],'janela_nao_identificada_fechamento_manual')
            self.assertEqual((running.terminated,running.killed,running.waited),(0,0,0))
        with patch.object(host,'_request_close_owned_sandbox_window',return_value=1):
            waiting=Process(timeout=True)
            result=host.close_own_sandbox(waiting,timeout=1)
            self.assertEqual(result['estado'],'fechamento_pendente_manual')
            self.assertEqual((waiting.terminated,waiting.killed),(0,0))
        ended=Process(running=False)
        self.assertEqual(host.close_own_sandbox(ended)['estado'],'ja_encerrado')
        self.assertEqual((ended.terminated,ended.killed),(0,0))

    def test_sandbox_close_does_not_probe_unowned_pid(self):
        class NoPID:
            def poll(self):return None
        with patch.object(host,'_request_close_owned_sandbox_window') as callback:
            result=host.close_own_sandbox(NoPID())
        self.assertEqual(result['estado'],'pid_indisponivel_fechamento_manual')
        callback.assert_not_called()

    def test_reject_foreign_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with self.assertRaises(host.G6BSafetyError):
                host.ensure_safe(root/'AppData',home=root)

    def test_reject_personal_database_by_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp)
            (home/'VighnaLab').mkdir()
            (home/'VighnaLab'/'estudos.db').write_bytes(b'personal')
            with self.assertRaises(host.G6BSafetyError):
                host.ensure_safe(host.root_qa(home),home=home)

    def test_guest_reject_traversal_and_db_from_source(self):
        for name in ('../path.py',r'C:\private.py','estudos.db','assets/plugin.dll'):
            with tempfile.TemporaryDirectory() as tmp:
                z=Path(tmp)/'s.zip'
                with zipfile.ZipFile(z,'w') as f:f.writestr(name,b'xxx')
                with self.assertRaises(ValueError):
                    guest.safe_extract_sources(z,Path(tmp)/'output')

    def test_guest_hash_reject_tampered_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for i in range(11): (root/f'{i}.txt').write_text('safe')
            meta={p.name:guest.hash_file(p) for p in root.iterdir()}
            (root/'MANIFESTO_G6B1.json').write_text(json.dumps({'component':'vighna-g6b1-input',
                'target_build':guest.RC2_BUILD,'instalacao_autorizada':False,
                'sha256_files':meta}))
            guest.verify_input(root)
            (root/'0.txt').write_text('tampered')
            with self.assertRaises(ValueError):guest.verify_input(root)

    def test_guest_workspace_windows_path_avoids_path_plus_string(self):
        base=PureWindowsPath(r'C:\Windows\Temp')
        target=guest.guest_workspace_dir(base,'20261013_034706_871556')
        self.assertIsInstance(target,PureWindowsPath)
        self.assertEqual(target.parent,base)
        self.assertEqual(target.name,'VighnaG6B1_20261013_034706_871556')
        self.assertRaises(TypeError, lambda: base / 'VighnaG6B1_' + '20261013')

    def test_guest_synthetic_control_flow_does_not_use_any_real_exe(self):
        # Pure mocks: only validates workdir construction and the status state-machine.
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            results=[]
            def fake_scenario(workspace, inp, key):
                self.assertTrue(workspace.is_dir())
                self.assertEqual(workspace.parent,root)
                self.assertTrue(workspace.name.startswith('VighnaG6B1_'))
                results.append(key)
                return {'cenario':key,'mock':True}
            with (patch.object(guest.sys,'platform','win32'),
                  patch.dict(guest.os.environ,{'TEMP':str(root)}),
                  patch.object(guest,'verify_input',return_value={}),
                  patch.object(guest,'scenario',side_effect=fake_scenario)):
                code=guest.run(root/'unused',root/'output')
            self.assertEqual(code,0)
            self.assertEqual(results,['sucesso','falha_compilacao','falha_pos_commit'])
            report=json.loads((root/'output'/'RESULTADO_G6B1.json').read_text())
            self.assertEqual(len(report['cenarios']),3)
            self.assertTrue(report['engine_original_qa'])  # mocked; not Windows approval
            self.assertFalse(report['gate_g6_aprovado'])
            self.assertEqual(list(root.glob('VighnaG6B1_*')),[])

    def test_guest_preserves_partial_scenario_evidence_on_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            partial={'cenario':'sucesso','status':'FALHOU_OU_BLOQUEADO',
                     'operacao_falhou':'verificar_sqlite_apos_transacao',
                     'primeira_divergencia':{'categoria':'registros','item':'g6b_marker'}}
            def fail_scenario(*_args):
                raise guest.ScenarioFailure('divergiu',partial)
            with (patch.object(guest.sys,'platform','win32'),
                  patch.dict(guest.os.environ,{'TEMP':str(root)}),
                  patch.object(guest,'verify_input',return_value={}),
                  patch.object(guest,'scenario',side_effect=fail_scenario)):
                code=guest.run(root/'unused',root/'output')
            report=json.loads((root/'output'/'RESULTADO_G6B1.json').read_text())
            diagnostic=json.loads((root/'output'/'DIAGNOSTICO_SQLITE_G6B1.json').read_text())
        self.assertEqual(code,1)
        self.assertEqual(report['cenarios'],[partial])
        self.assertEqual(diagnostic['cenarios'],[partial])
        self.assertEqual(report['cenarios'][0]['operacao_falhou'],
                         'verificar_sqlite_apos_transacao')

    def test_dynamic_engine_dependency_capture_includes_uuid(self):
        # The real QA engine was dynamically loaded inside frozen guest.
        # PyInstaller will not see imports in the loaded .py without this list.
        import homologador_windows as h
        from zipfile import ZipFile
        source=h.KIT/'insumos'/'BASE_R1D_SOMENTE_FONTES_QA.zip'
        with ZipFile(source) as archive:
            imports=host.engine_hidden_imports(archive.read('vighna_update_engine.py'))
        self.assertTrue({'ast','tempfile','uuid','sqlite3','zipfile'} <= set(imports))
        self.assertEqual(len(imports),len(set(imports)))
        self.assertTrue(all(x in host.sys.stdlib_module_names for x in imports))

    def test_pyinstaller_guest_command_contains_hidden_imports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'SPEC_GUEST').mkdir()
            executable=root/'DIST_GUEST'/'G6B1_GUEST.exe'
            executable.parent.mkdir()
            executable.write_bytes(b'STUB_BUILD_OUTPUT')
            script=root/'guest.py';script.write_text('# QA only\n')
            py=root/'python.exe';py.write_bytes(b'STUB_PYTHON')
            with patch('homologador_windows.environment_qa',return_value={}), \
                 patch.object(host.subprocess,'Popen',return_value=SimpleNamespace(wait=lambda timeout:0)) as proc:
                result=host.build(py,script,root,'GUEST',is_guest=True,
                                  hidden_imports=('ast','tempfile','uuid'))
            command=proc.call_args.args[0]
            self.assertEqual(result,executable)
            self.assertTrue(all('--hidden-import='+n in command
                                for n in ('ast','tempfile','uuid')))

    def test_dynamic_engine_dependency_capture_rejects_nonstdlib(self):
        with self.assertRaises(host.G6BSafetyError):
            host.engine_hidden_imports(b'import ast, tempfile, uuid\nimport unknown_library_qa_987\n')
        with self.assertRaises(host.G6BSafetyError):
            host.engine_hidden_imports(b'import ast, tempfile, uuid\nfrom .other import X\n')

    def test_frozen_guest_import_preflight_pass_and_reject(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); exe=root/'G6B1_GUEST.exe';exe.write_bytes(b'executable_mock')
            with patch('homologador_windows.environment_qa',return_value={}), \
                 patch.object(host.subprocess,'run',return_value=SimpleNamespace(
                     returncode=0,stdout=b'G6B1_ENGINE_IMPORT_OK\n',stderr=b'')) as proc:
                log=host.probe_frozen_guest(exe,b'# QA engine\n',root)
                self.assertTrue(log.is_file())
                self.assertIn('--probe-engine',proc.call_args.args[0])
                self.assertFalse((root/'PROBE_ENGINE_QA'/'vighna_update_engine.py').is_symlink())
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);exe=root/'G6B1_GUEST.exe';exe.write_bytes(b'executable_mock')
            with patch('homologador_windows.environment_qa',return_value={}), \
                 patch.object(host.subprocess,'run',return_value=SimpleNamespace(
                     returncode=1,stdout=b'',stderr=b"ModuleNotFoundError: No module named 'uuid'")):
                with self.assertRaises(host.G6BSafetyError):
                    host.probe_frozen_guest(exe,b'# QA engine\n',root)
                self.assertIn(b'uuid',(root/'PROBE_GUEST.log').read_bytes())

    def test_actual_qa_engine_transactions_with_stub_binaries(self):
        # Real *unmodified* engine, genuine signed-by-manifest QA source ZIP
        # and RC2 source update, but NO launch of binaries / no Sandbox.
        import homologador_windows as h
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            incoming=root/'INPUT';incoming.mkdir()
            shutil.copy2(h.KIT/'insumos'/'BASE_R1D_SOMENTE_FONTES_QA.zip',
                         incoming/'BASE_R1D_SOMENTE_FONTES_QA.zip')
            shutil.copy2(h.KIT/'insumos'/'CANDIDATO_QA_R1D_PARA_M2_RC2_NAO_INSTALAR.zip',
                         incoming/'CANDIDATO_QA_R1D_PARA_M2_RC2_NAO_INSTALAR.zip')
            for label in ('R1D','RC2'):
                directory=incoming/label;directory.mkdir()
                (directory/'VighnaStudy.exe').write_bytes(('STUB_ONLY_'+label).encode())
            with patch.object(guest,'smoke',return_value={
                    'stable':True,'window_observed':True,'process_started':True}):
                results=[guest.scenario(root,incoming,name)
                    for name in ('sucesso','falha_compilacao','falha_pos_commit')]
        self.assertEqual([r['status'] for r in results],[
            'PASSOU_B1_TRANSACAO_REAL','PASSOU_B1_ROLLBACK_REAL',
            'PASSOU_B1_ROLLBACK_REAL'])
        self.assertEqual([r['fase_checkpoint'] for r in results],[
            'installed','pre_commit_no_snapshot','recovered'])
        self.assertTrue(all(r['banco_qa_preservado'] for r in results))

    def test_r1d_initialization_becomes_transaction_baseline(self):
        """Regression: first R1D start may initialize schema before the update."""
        import homologador_windows as h
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);incoming=root/'INPUT';incoming.mkdir()
            shutil.copy2(h.KIT/'insumos'/'BASE_R1D_SOMENTE_FONTES_QA.zip',
                         incoming/'BASE_R1D_SOMENTE_FONTES_QA.zip')
            shutil.copy2(h.KIT/'insumos'/'CANDIDATO_QA_R1D_PARA_M2_RC2_NAO_INSTALAR.zip',
                         incoming/'CANDIDATO_QA_R1D_PARA_M2_RC2_NAO_INSTALAR.zip')
            for label in ('R1D','RC2'):
                directory=incoming/label;directory.mkdir()
                (directory/'VighnaStudy.exe').write_bytes(('STUB_ONLY_'+label).encode())
            initialized=set()
            def initialize_on_first_r1d(_folder,scenario_root,label):
                db=scenario_root/'codigo'/'estudos.db'
                if label=='r1d' and db not in initialized:
                    with closing(sqlite3.connect(db)) as con:
                        with con:
                            con.execute('CREATE TABLE schema_criado_pelo_r1d(valor TEXT)')
                            con.execute("INSERT INTO schema_criado_pelo_r1d VALUES ('esperado')")
                    initialized.add(db)
                return {'stable':True,'window_observed':True,'process_started':True}
            with patch.object(guest,'smoke',side_effect=initialize_on_first_r1d):
                try:
                    result=guest.scenario(root,incoming,'sucesso')
                except guest.ScenarioFailure as exc:
                    self.fail(json.dumps(exc.diagnostic.get('primeira_divergencia'),
                                         ensure_ascii=False,indent=2))
        comparisons={item['classificacao']:item
                     for item in result['comparacoes_sqlite']}
        self.assertTrue(comparisons['INICIALIZACAO_R1D_OBSERVADA']['logica_alterada'])
        self.assertFalse(comparisons['PRESERVACAO_TRANSACIONAL_EXATA']['logica_alterada'])
        self.assertTrue(result['banco_qa_preservado'])

    def test_guest_does_not_run_on_linux(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'out'
            with patch.object(guest.sys,'platform','linux'):
                code=guest.run(Path(tmp)/'in',out)
            self.assertEqual(code,1)
            report=json.loads((out/'RESULTADO_G6B1.json').read_text())
            self.assertFalse(report['instalacao_autorizada'])
            self.assertFalse(report['gate_g6_aprovado'])

    def test_guest_real_builder_not_claimed(self):
        src=Path(guest.__file__).read_text(encoding='utf-8')
        self.assertIn("'build_original_dentro_sandbox':False",src)
        self.assertIn("runner=runner",src)
        self.assertNotIn("instalacao_autorizada':True",src)

    def test_host_preflight_not_available_on_linux(self):
        with patch.object(host.sys,'platform','linux'):
            with self.assertRaises(host.G6BSafetyError):host.run()


if __name__=='__main__':unittest.main()

class G7SandboxVerifiedCloseTests(unittest.TestCase):
    """Fail-closed PID/HWND tests; no actual Sandbox processes are started."""
    launch_pid = 21816
    client_pid = 8284
    good_after = {launch_pid:'WindowsSandbox.exe', client_pid:'WindowsSandboxClient.exe'}
    good_windows = [{'hwnd':4196368,'pid':client_pid}]

    def test_documented_windows_pattern_selects_only_new_client(self):
        item=host.verified_qa_client_candidate({},self.good_after,self.good_windows,self.launch_pid)
        self.assertEqual(item,self.good_windows[0])

    def test_preexisting_process_prevents_close(self):
        self.assertIsNone(host.verified_qa_client_candidate({900:'WindowsSandboxClient.exe'},
            self.good_after,self.good_windows,self.launch_pid))

    def test_extra_client_prevents_close(self):
        after=self.good_after | {900:'WindowsSandboxClient.exe'}
        self.assertIsNone(host.verified_qa_client_candidate({},after,self.good_windows,self.launch_pid))

    def test_multiple_windows_prevents_close(self):
        windows=self.good_windows+[{'hwnd':4196399,'pid':self.client_pid}]
        self.assertIsNone(host.verified_qa_client_candidate({},self.good_after,windows,self.launch_pid))

    def test_wrong_launcher_prevents_close(self):
        self.assertIsNone(host.verified_qa_client_candidate({},self.good_after,self.good_windows,25592))

    def test_no_guest_evidence_does_not_send_wm_close(self):
        class Proc:
            pid=21816
            def poll(self):return None
        with (patch.object(host,'post_close_verified_client') as post,
              patch.object(host,'_request_close_owned_sandbox_window') as legacy):
            report=host.close_own_sandbox(Proc(), ownership_snapshot={},evidence_confirmed=False)
        self.assertIn('manual',report['estado'])
        post.assert_not_called();legacy.assert_not_called()

    def test_client_revalidation_race_prevents_close(self):
        class Proc:
            pid=21816
        with (patch.object(host,'sandbox_processes_qa',side_effect=[self.good_after,{}]),
              patch.object(host,'visible_client_windows',return_value=self.good_windows),
              patch.object(host,'post_close_verified_client') as post):
            result=host.close_verified_qa_client(Proc(),before={})
        self.assertIn('manual',result['estado'])
        post.assert_not_called()

    def test_one_wm_close_and_both_processes_required(self):
        class Proc:
            pid=21816
            def wait(self,timeout):return 0
            def terminate(self):raise AssertionError('termination forbidden')
            def kill(self):raise AssertionError('kill forbidden')
        with (patch.object(host,'sandbox_processes_qa',side_effect=[self.good_after,self.good_after,{}]),
              patch.object(host,'visible_client_windows',return_value=self.good_windows),
              patch.object(host,'post_close_verified_client',return_value=True) as post):
            result=host.close_verified_qa_client(Proc(),before={})
        self.assertEqual(result['estado'],'encerrado_graciosamente')
        self.assertTrue(result['ambos_processos_encerrados'])
        self.assertFalse(result['fechamento_forcado'])
        post.assert_called_once_with(4196368,8284)

    def test_ownership_snapshot_never_calls_legacy_pid_closer(self):
        class Proc:
            pid=21816
            def poll(self):return None
        with (patch.object(host,'close_verified_qa_client',return_value={'estado':'manual'}) as fn,
              patch.object(host,'_request_close_owned_sandbox_window') as legacy):
            host.close_own_sandbox(Proc(),ownership_snapshot={},evidence_confirmed=True)
        fn.assert_called_once()
        legacy.assert_not_called()

    def test_window_api_not_called_off_windows(self):
        with patch.object(host.sys,'platform','linux'):
            self.assertFalse(host.post_close_verified_client(4196368,8284))
            self.assertEqual(host.visible_client_windows({8284:'WindowsSandboxClient.exe'}),[])


class G7AutoConfirmSandboxDialogTests(unittest.TestCase):
    """Fail closed on unknown dialogs; no native Windows calls are executed here."""
    TITLE = 'Área Restrita do Windows'
    BODY = ('Tem certeza de que deseja fechar a Área Restrita do Windows? '
            'Quando a Área Restrita do Windows for fechada, todo o seu conteúdo '
            'será descartado e perdido permanentemente.')

    def test_accepts_documented_ptbr_native_message(self):
        self.assertTrue(host._is_expected_sandbox_discard_message(
            self.TITLE, self.BODY,'OK','Cancelar'))

    def test_rejects_unrelated_warning_even_with_same_title(self):
        self.assertFalse(host._is_expected_sandbox_discard_message(
            self.TITLE,'O programa está atualizando dados!','OK','Cancelar'))

    def test_rejects_substituted_title(self):
        self.assertFalse(host._is_expected_sandbox_discard_message(
            'Atualização do Windows',self.BODY,'OK','Cancelar'))

    def test_rejects_unsafe_buttons(self):
        self.assertFalse(host._is_expected_sandbox_discard_message(
            self.TITLE,self.BODY,'Excluir','Cancelar'))
        self.assertFalse(host._is_expected_sandbox_discard_message(
            self.TITLE,self.BODY,'OK','Fechar'))

    def test_rejects_partial_or_different_text(self):
        self.assertFalse(host._is_expected_sandbox_discard_message(
            self.TITLE,'Tem certeza de que deseja fechar a Área Restrita do Windows?',
            'OK','Cancelar'))

    def test_english_requires_all_native_warning_terms(self):
        self.assertTrue(host._is_expected_sandbox_discard_message(
            'Windows Sandbox',('Are you sure you want to close Windows Sandbox? '
            'When Windows Sandbox is closed, all of its content will be '
            'discarded and permanently lost.'),'OK','Cancel'))
        self.assertFalse(host._is_expected_sandbox_discard_message(
            'Windows Sandbox','Are you sure you want to close Windows Sandbox?',
            'OK','Cancel'))

    def test_without_evidence_confirmation_does_not_enter_automatic_path(self):
        class Proc:
            pid=21816
            def poll(self):return None
        with patch.object(host,'_confirm_owned_sandbox_discard') as auto:
            r=host.close_own_sandbox(Proc(),ownership_snapshot={},evidence_confirmed=False)
        self.assertFalse(r['fechamento_forcado'])
        auto.assert_not_called()

    def test_simulated_native_dialog_confirmed_after_wmclose(self):
        class Proc:
            pid=21816
            def __init__(self):self.attempts=0
            def wait(self, timeout):
                self.attempts+=1
                if self.attempts==1:raise host.subprocess.TimeoutExpired('sandbox',timeout)
                return 0
            def terminate(self):raise AssertionError('forced shutdown')
            def kill(self):raise AssertionError('forced shutdown')
        after={21816:'WindowsSandbox.exe',8284:'WindowsSandboxClient.exe'}
        with (patch.object(host,'sandbox_processes_qa',side_effect=[after,after,after,{}]),
              patch.object(host,'visible_client_windows',return_value=[{'hwnd':4196368,'pid':8284}]),
              patch.object(host,'post_close_verified_client',return_value=True),
              patch.object(host,'_confirm_owned_sandbox_discard',return_value={
                 'acao':'confirmacao_automatica_enviada','clicou_ok':True,'dialogo_nativo_validado':True}) as confirm):
            r=host.close_verified_qa_client(Proc(),before={})
        self.assertTrue(r['confirmacao_automatica'])
        self.assertEqual(r['estado'],'encerrado_graciosamente')
        confirm.assert_called_once()

    def test_simulated_unknown_dialog_is_manual(self):
        class Proc:
            pid=21816
            def wait(self,timeout):raise host.subprocess.TimeoutExpired('sandbox',timeout)
            def terminate(self):raise AssertionError('forced shutdown')
            def kill(self):raise AssertionError('forced shutdown')
        after={21816:'WindowsSandbox.exe',8284:'WindowsSandboxClient.exe'}
        with (patch.object(host,'sandbox_processes_qa',side_effect=[after,after]),
              patch.object(host,'visible_client_windows',return_value=[{'hwnd':4196368,'pid':8284}]),
              patch.object(host,'post_close_verified_client',return_value=True),
              patch.object(host,'_confirm_owned_sandbox_discard',return_value={
                 'acao':'confirmacao_manual','clicou_ok':False,'motivo':'texto_desconhecido'})):
            r=host.close_verified_qa_client(Proc(),before={},timeout=0.2)
        self.assertEqual(r['estado'],'fechamento_pendente_manual')
        self.assertFalse(r['confirmacao_automatica'])
        self.assertFalse(r['fechamento_forcado'])

    def test_off_windows_never_displays_dialog(self):
        with patch.object(host.sys,'platform','linux'):
            self.assertIsNone(host._native_sandbox_discard_dialog(8284,4196368))
            self.assertFalse(host._confirm_owned_sandbox_discard(8284,4196368,{1:'WindowsSandbox.exe'})['clicou_ok'])



class G7UnownedDiscardDialogWindowsTests(unittest.TestCase):
    """Observed Windows 2026-10-13: main and dialog are peer #32770 windows."""
    main=4917058
    dialog=2951338
    top=[{'hwnd':main,'owner_hwnd':0,'parent_hwnd':0},
         {'hwnd':dialog,'owner_hwnd':0,'parent_hwnd':0}]

    def test_real_observed_independent_dialog_is_selected(self):
        self.assertEqual(host._select_verified_sandbox_modal(self.top,self.main),self.dialog)

    def test_order_does_not_change_selection(self):
        self.assertEqual(host._select_verified_sandbox_modal(self.top[::-1],self.main),self.dialog)

    def test_expected_ownership_of_dialog_also_valid(self):
        windows=[self.top[0],self.top[1] | {'owner_hwnd':self.main}]
        self.assertEqual(host._select_verified_sandbox_modal(windows,self.main),self.dialog)

    def test_main_window_missing_is_rejected(self):
        windows=[{'hwnd':111,'owner_hwnd':0,'parent_hwnd':0},self.top[1]]
        self.assertIsNone(host._select_verified_sandbox_modal(windows,self.main))

    def test_third_same_process_dialog_is_ambiguous(self):
        windows=self.top+[{'hwnd':999,'owner_hwnd':0,'parent_hwnd':0}]
        self.assertIsNone(host._select_verified_sandbox_modal(windows,self.main))

    def test_unknown_parent_or_owner_fails_closed(self):
        for modified in ({'parent_hwnd':888},{'owner_hwnd':777}):
            self.assertIsNone(host._select_verified_sandbox_modal(
                [self.top[0],self.top[1] | modified],self.main))

    def test_duplicate_hwnd_is_rejected(self):
        self.assertIsNone(host._select_verified_sandbox_modal([self.top[0],self.top[0]],self.main))

    def test_invalid_main_or_handle_is_rejected(self):
        self.assertIsNone(host._select_verified_sandbox_modal(self.top,0))
        self.assertIsNone(host._select_verified_sandbox_modal([self.top[0],self.top[1] | {'hwnd':0}],self.main))

    def test_main_must_be_top_level_and_unowned(self):
        self.assertIsNone(host._select_verified_sandbox_modal(
            [self.top[0] | {'owner_hwnd':111},self.top[1]],self.main))

    def test_text_and_buttons_still_mandatory(self):
        cls=G7AutoConfirmSandboxDialogTests
        self.assertTrue(host._is_expected_sandbox_discard_message(cls.TITLE,cls.BODY,'OK','Cancelar'))
        self.assertFalse(host._is_expected_sandbox_discard_message(cls.TITLE,'erro desconhecido','OK','Cancelar'))
