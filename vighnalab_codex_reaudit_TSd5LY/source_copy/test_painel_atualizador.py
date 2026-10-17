import unittest.mock
# -*- coding: utf-8 -*-
"""Testes do atualizador V3.1 só em pastas descartáveis, sem VighnaStudy real."""
import hashlib
import json
from pathlib import Path
from unittest.mock import patch as mock_patch
import tempfile
import unittest
import zipfile

import painel_atualizador as a


def patch(root, file, data=b'novo_conteudo', base='3.0.0', nextver='3.1.0', transform=None):
    files={'painel_homologacao.py':data,
           'PAINEL_VERSAO.json':json.dumps({'component':'vighna-panel','version':nextver}).encode()}
    old=a.sha((root/'painel_homologacao.py').read_bytes())
    manifest={'format':a.FORMAT,'component':a.PANEL_ID,'from_version':base,
              'to_version':nextver,'description':'QA sintético',
              'files':{'painel_homologacao.py':{'old_sha256':old,'sha256':a.sha(data)},
                       'PAINEL_VERSAO.json':{'old_sha256':None,'sha256':a.sha(files['PAINEL_VERSAO.json'])}}}
    if transform:transform(manifest,files)
    with zipfile.ZipFile(file,'w') as z:
        z.writestr('manifesto.json',json.dumps(manifest))
        for name,value in files.items():z.writestr(name,value)
    return file

class PanelUpdateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='qa_painel_update_')
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'painel';self.root.mkdir()
        for f in ('painel_homologacao.py','homologador_windows.py','painel_gates.py','painel_checkpoints.py'):
            (self.root/f).write_bytes(b'codigo_antigo')
        self.p=Path(self.tmp.name)/'update.zip'

    def test_01_recusa_pasta_incompleta(self):
        (self.root/'painel_checkpoints.py').unlink()
        with self.assertRaises(a.UpdateError):a.inspect(self.p,self.root)

    def test_02_recusa_zip_que_nao_e_update(self):
        with zipfile.ZipFile(self.p,'w') as z:z.writestr('doc.txt','dados')
        with self.assertRaises(a.UpdateError):a.inspect(self.p,self.root)

    def test_03_inspecao_sem_mutacao(self):
        patch(self.root,self.p)
        before=(self.root/'painel_homologacao.py').read_bytes()
        self.assertEqual(a.inspect(self.p,self.root)['to_version'],'3.1.0')
        self.assertEqual((self.root/'painel_homologacao.py').read_bytes(),before)
        self.assertFalse((self.root/'.painel_updates').exists())

    def test_04_atualiza_e_persiste_versao(self):
        patch(self.root,self.p)
        self.assertEqual(a.apply(self.p,self.root)['status'],'APLICADO')
        self.assertEqual(a.panel_version(self.root),'3.1.0')
        self.assertEqual((self.root/'painel_homologacao.py').read_bytes(),b'novo_conteudo')
        self.assertEqual((self.root/'homologador_windows.py').read_bytes(),b'codigo_antigo')

    def test_05_reversao_manual(self):
        patch(self.root,self.p);a.apply(self.p,self.root)
        self.assertEqual(a.rollback(self.root)['status'],'REVERTIDO')
        self.assertEqual(a.panel_version(self.root),'3.0.0')
        self.assertFalse((self.root/'PAINEL_VERSAO.json').exists())
        self.assertEqual((self.root/'painel_homologacao.py').read_bytes(),b'codigo_antigo')

    def test_06_rejeita_version_incompativel(self):
        patch(self.root,self.p,base='2.0.0')
        with self.assertRaises(a.UpdateError):a.inspect(self.p,self.root)

    def test_07_rejeita_codigo_origem_divergente(self):
        patch(self.root,self.p)
        (self.root/'painel_homologacao.py').write_bytes(b'modificado')
        with self.assertRaises(a.UpdateError):a.inspect(self.p,self.root)

    def test_08_rejeita_hash_de_conteudo(self):
        patch(self.root,self.p,transform=lambda m,f:m['files']['painel_homologacao.py'].update(sha256='0'*64))
        with self.assertRaises(a.UpdateError):a.inspect(self.p,self.root)

    def test_09_rejeita_arquivo_fora_da_lista(self):
        def bad(m,f):
            f['banco.py']=b'codigo';m['files']['banco.py']={'old_sha256':None,'sha256':a.sha(f['banco.py'])}
        patch(self.root,self.p,transform=bad)
        with self.assertRaises(a.UpdateError):a.inspect(self.p,self.root)

    def test_10_rejeita_zip_slip(self):
        patch(self.root,self.p,transform=lambda m,f:f.update({'../x.py':b'X'}))
        with self.assertRaises(a.UpdateError):a.inspect(self.p,self.root)

    def test_11_rejeita_duplicata(self):
        patch(self.root,self.p)
        with zipfile.ZipFile(self.p,'a') as z:z.writestr('painel_homologacao.py','novamente')
        with self.assertRaises(a.UpdateError):a.inspect(self.p,self.root)

    def test_12_rejeita_symlink_de_destino(self):
        patch(self.root,self.p)
        (self.root/'painel_homologacao.py').unlink()
        try:
            (self.root/'painel_homologacao.py').symlink_to(self.root/'homologador_windows.py')
        except OSError as exc:
            if getattr(exc, 'winerror', None) == 1314:
                self.skipTest('Windows sem privilégio para criar symlink real; verificação pendente')
            raise
        with self.assertRaises(a.UpdateError):a.inspect(self.p,self.root)

    def test_12a_rejeita_symlink_sintetico_sem_privilegio(self):
        patch(self.root,self.p)
        unsafe=self.root/'painel_homologacao.py'
        real_is_symlink=Path.is_symlink
        def synthetic_is_symlink(path):
            return path==unsafe or real_is_symlink(path)
        with mock_patch.object(Path,'is_symlink',synthetic_is_symlink):
            with self.assertRaisesRegex(a.UpdateError,'inseguro'):
                a.inspect(self.p,self.root)

    def test_13_falha_injetada_faz_rollback(self):
        patch(self.root,self.p)
        with self.assertRaises(a.UpdateError):a.apply(self.p,self.root,failure_injection=0)
        self.assertEqual((self.root/'painel_homologacao.py').read_bytes(),b'codigo_antigo')
        self.assertEqual(a.panel_version(self.root),'3.0.0')

    def test_14_rejeita_rollback_se_alterado(self):
        patch(self.root,self.p);a.apply(self.p,self.root)
        (self.root/'painel_homologacao.py').write_bytes(b'modificado_depois')
        with self.assertRaises(a.UpdateError):a.rollback(self.root)

    def test_15_rejeita_pasta_de_vighna(self):
        (self.root/'estudos.db').write_bytes(b'sintetico')
        with self.assertRaises(a.UpdateError):a.validate_panel_root(self.root)

    def test_17_recupera_atualizacao_interrompida(self):
        patch(self.root,self.p)
        manifest,_=a.read_package(self.p)
        folder=self.root/'.painel_updates'/'atualizacao_20260101_010101_000001'
        (folder/'anteriores').mkdir(parents=True)
        (folder/'anteriores'/'painel_homologacao.py').write_bytes(b'codigo_antigo')
        (folder/'resultado.json').write_text(json.dumps({
            'status':'preparado','files':manifest['files']}))
        (self.root/'painel_homologacao.py').write_bytes(b'novo_conteudo')
        with self.assertRaises(a.UpdateError):a.inspect(self.p,self.root)
        self.assertEqual(a.recover_incomplete(self.root)['status'],'RECUPERADO')
        self.assertEqual((self.root/'painel_homologacao.py').read_bytes(),b'codigo_antigo')
        self.assertEqual(a.panel_version(self.root),'3.0.0')

    def test_18_recuperacao_rejeita_alteracao_inesperada(self):
        patch(self.root,self.p)
        manifest,_=a.read_package(self.p)
        folder=self.root/'.painel_updates'/'atualizacao_20260101_010101_000001'
        (folder/'anteriores').mkdir(parents=True)
        (folder/'anteriores'/'painel_homologacao.py').write_bytes(b'codigo_antigo')
        (folder/'resultado.json').write_text(json.dumps({
            'status':'preparado','files':manifest['files']}))
        (self.root/'painel_homologacao.py').write_bytes(b'ALTERACAO_EXTERNAMENTE')
        with self.assertRaises(a.UpdateError):a.recover_incomplete(self.root)
        self.assertEqual((self.root/'painel_homologacao.py').read_bytes(),b'ALTERACAO_EXTERNAMENTE')

    def test_19_reverte_falha_depois_de_duas_trocas(self):
        patch(self.root,self.p)
        with self.assertRaises(a.UpdateError):a.apply(self.p,self.root,failure_injection=1)
        self.assertEqual(a.panel_version(self.root),'3.0.0')
        self.assertEqual((self.root/'painel_homologacao.py').read_bytes(),b'codigo_antigo')
        self.assertFalse((self.root/'PAINEL_VERSAO.json').exists())

    def test_16_nao_toca_outros_arquivos(self):
        before={f:(self.root/f).read_bytes() for f in ('homologador_windows.py','painel_gates.py','painel_checkpoints.py')}
        patch(self.root,self.p);a.apply(self.p,self.root)
        for f,data in before.items():self.assertEqual((self.root/f).read_bytes(),data)


class JunctionDefenseTests(unittest.TestCase):
    """Tests use synthetic panel roots only; never the user's installed panel."""
    setUp=PanelUpdateTests.setUp
    def test_20_rejeita_junction_sintetica_no_armazenamento(self):
        patch(self.root,self.p)
        storage=self.root/'.painel_updates';storage.mkdir()
        marker=storage/'marcador.txt';marker.write_text('NAO_ALTERAR',encoding='utf-8')
        original=a._unsafe_reparse
        with mock_patch.object(a,'_unsafe_reparse',side_effect=lambda p:Path(p)==storage or original(p)):
            for operation in (lambda:a.validate_panel_root(self.root),
                              lambda:a.inspect(self.p,self.root),
                              lambda:a.apply(self.p,self.root),
                              lambda:a.rollback(self.root),
                              lambda:a.recover_incomplete(self.root)):
                with self.assertRaisesRegex(a.UpdateError,'junction'):
                    operation()
            a._save_operation_status(self.root,'APLICADO','INVALIDO')
        self.assertEqual(marker.read_text(encoding='utf-8'),'NAO_ALTERAR')
        self.assertFalse((storage/'ultima_execucao.json').exists())
        self.assertEqual((self.root/'painel_homologacao.py').read_bytes(),b'codigo_antigo')

    def test_21_rejeita_junction_sintetica_no_backup_do_checkpoint(self):
        patch(self.root,self.p);res=a.apply(self.p,self.root)
        checkpoint=Path(res['checkpoint'])
        marker=checkpoint/'anteriores'/'painel_homologacao.py'
        old=marker.read_bytes()
        original=a._unsafe_reparse
        with mock_patch.object(a,'_unsafe_reparse',side_effect=lambda p:Path(p)==checkpoint/'anteriores' or original(p)):
            with self.assertRaisesRegex(a.UpdateError,'junction'):
                a.rollback(self.root)
        self.assertEqual(marker.read_bytes(),old)
        self.assertEqual(a.panel_version(self.root),'3.1.0')

    def test_22_rejeita_junction_sintetica_na_recuperacao(self):
        patch(self.root,self.p)
        manifest,_=a.read_package(self.p)
        folder=self.root/'.painel_updates'/'atualizacao_20260101_010101_000002'
        (folder/'anteriores').mkdir(parents=True)
        (folder/'anteriores'/'painel_homologacao.py').write_bytes(b'codigo_antigo')
        (folder/'resultado.json').write_text(json.dumps({'status':'preparado','files':manifest['files']}),encoding='utf-8')
        (self.root/'painel_homologacao.py').write_bytes(b'novo_conteudo')
        original=a._unsafe_reparse
        with mock_patch.object(a,'_unsafe_reparse',side_effect=lambda p:Path(p)==folder/'anteriores' or original(p)):
            with self.assertRaisesRegex(a.UpdateError,'junction'):
                a.recover_incomplete(self.root)
        self.assertEqual((self.root/'painel_homologacao.py').read_bytes(),b'novo_conteudo')

    def test_23_rejeita_junction_real_windows_sem_instalar(self):
        import os,subprocess,sys
        if sys.platform!='win32':self.skipTest('Junction NTFS exige Windows')
        patch(self.root,self.p)
        external=Path(self.tmp.name)/'externo_sintetico';external.mkdir()
        (external/'nao_alterar.txt').write_text('CONTEUDO_QA',encoding='utf-8')
        storage=self.root/'.painel_updates'
        cmd=['cmd','/c','mklink','/J',str(storage),str(external)]
        response=subprocess.run(cmd,capture_output=True,text=True,errors='replace')
        if response.returncode:
            self.skipTest('Windows não permitiu criar junction de QA: '+response.stderr[:120])
        try:
            self.assertTrue(storage.is_junction())
            with self.assertRaisesRegex(a.UpdateError,'junction'):
                a.inspect(self.p,self.root)
            with self.assertRaisesRegex(a.UpdateError,'junction'):
                a.apply(self.p,self.root)
            with self.assertRaisesRegex(a.UpdateError,'junction'):
                a.recover_incomplete(self.root)
            a._save_operation_status(self.root,'APLICADO','NAO_GRAVAR')
            self.assertEqual((external/'nao_alterar.txt').read_text(encoding='utf-8'),'CONTEUDO_QA')
            self.assertEqual(list(external.iterdir()),[external/'nao_alterar.txt'])
            self.assertEqual((self.root/'painel_homologacao.py').read_bytes(),b'codigo_antigo')
        finally:
            os.rmdir(storage) # rmdir removes the junction, not its target

    def test_24_rejeita_junction_real_windows_no_checkpoint(self):
        import os,subprocess,sys
        if sys.platform!='win32':self.skipTest('Junction NTFS exige Windows')
        patch(self.root,self.p);r=a.apply(self.p,self.root)
        checkpoint=Path(r['checkpoint']);backups=checkpoint/'anteriores'
        destination=Path(self.tmp.name)/'backup_ficticio';backups.rename(destination)
        cmd=['cmd','/c','mklink','/J',str(backups),str(destination)]
        response=subprocess.run(cmd,capture_output=True,text=True,errors='replace')
        if response.returncode:self.skipTest('Windows não permitiu criar junction de QA')
        try:
            self.assertTrue(backups.is_junction())
            with self.assertRaisesRegex(a.UpdateError,'junction'):a.rollback(self.root)
            self.assertEqual(a.panel_version(self.root),'3.1.0')
            self.assertEqual((destination/'painel_homologacao.py').read_bytes(),b'codigo_antigo')
        finally:os.rmdir(backups)


# Contratos V3.1.7: barra de progresso e reabertura apenas após êxito.
class PanelV317ProgressTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='v317_progress_')
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'painel'; self.root.mkdir()
        for f in ('painel_homologacao.py','homologador_windows.py',
                  'painel_gates.py','painel_checkpoints.py'):
            (self.root/f).write_bytes(b'original')
        self.p=Path(self.tmp.name)/'patch.zip'

    def test_progress_reportado_durante_backup_e_troca(self):
        patch(self.root,self.p)
        ev=[]
        r=a.apply(self.p,self.root,progress=lambda msg,x: ev.append((msg,x)))
        self.assertEqual(r['status'],'APLICADO')
        self.assertTrue(any('backup' in msg.lower() for msg,x in ev))
        self.assertTrue(any('arquivo' in msg.lower() for msg,x in ev))
        self.assertEqual(ev[-1][1],1.0)
        self.assertTrue(all(0<=x<=1 for _,x in ev))

    def test_rollback_apos_falha_com_progresso(self):
        patch(self.root,self.p)
        ev=[]
        with self.assertRaises(a.UpdateError):
            a.apply(self.p,self.root,failure_injection=0,
                    progress=lambda msg,x: ev.append((msg,x)))
        self.assertEqual((self.root/'painel_homologacao.py').read_bytes(),b'original')
        self.assertFalse((self.root/'PAINEL_VERSAO.json').exists())
        self.assertFalse(any(x==1.0 for _,x in ev))

    def test_reabre_apenas_painel_na_pasta_validada(self):
        received=[]
        a._start_panel_after_success(self.root,launcher=lambda cmd,**kw:received.append((cmd,kw)))
        self.assertEqual(len(received),1)
        self.assertEqual(received[0][0][-1],str(self.root/'painel_homologacao.py'))
        self.assertNotIn('VighnaStudy.exe',str(received))

    def test_reabertura_bloqueada_proxima_do_banco_real(self):
        (self.root/'estudos.db').write_bytes(b'BANCO QA para bloqueio')
        with self.assertRaises(a.UpdateError):
            a._start_panel_after_success(self.root,launcher=lambda *_a,**_kw:self.fail('executou'))

    def test_status_local_sem_autorizacao_de_instalacao(self):
        (self.root/'.painel_updates').mkdir()
        a._save_operation_status(self.root,'APLICADO','Versão: 3.1.7')
        obj=json.loads((self.root/'.painel_updates'/'ultima_execucao.json').read_text(encoding='utf-8'))
        self.assertEqual(obj,{'status':'APLICADO','detalhe':'Versão: 3.1.7'})

    def test_janela_gui_reabre_so_apos_aprovacao(self):
        from unittest.mock import patch as mock
        from types import SimpleNamespace
        import tkinter as tk
        try:
            w=tk.Tk();w.destroy()
        except tk.TclError:
            self.skipTest('Tela Xvfb necessária para widget')
        (self.root/'.painel_updates').mkdir()
        args=SimpleNamespace(root=str(self.root),apply=str(self.p),wait_pid=0)
        callbacks=[]
        with mock.object(a,'apply',return_value={'status':'APLICADO','versao':'3.1.7'}),\
             mock.object(a,'_start_panel_after_success',side_effect=lambda root:callbacks.append(root)):
            self.assertEqual(a._progress_window(args),0)
        self.assertEqual(callbacks,[self.root])
        self.assertEqual(json.loads((self.root/'.painel_updates'/'ultima_execucao.json').read_text(encoding='utf-8'))['status'],'APLICADO')

    def test_janela_gui_nao_reabre_apos_falha(self):
        from unittest.mock import patch as mock
        from types import SimpleNamespace
        import tkinter as tk
        try:
            w=tk.Tk();w.destroy()
        except tk.TclError:
            self.skipTest('Tela Xvfb necessária para widget')
        (self.root/'.painel_updates').mkdir()
        args=SimpleNamespace(root=str(self.root),apply=str(self.p),wait_pid=0)
        with mock.object(a,'apply',side_effect=a.UpdateError('Pacote inválido')),\
             mock.object(a,'_start_panel_after_success',side_effect=AssertionError('Não pode abrir')):
            # For this test, close error dialog after event is consumed.
            import tkinter
            original=tkinter.Tk
            class AutoCloseTk(original):
                def __init__(self,*v,**kw):
                    super().__init__(*v,**kw)
                    self.after(280,self.destroy)
            with mock.object(tkinter,'Tk',AutoCloseTk):
                self.assertEqual(a._progress_window(args),2)
        self.assertEqual(json.loads((self.root/'.painel_updates'/'ultima_execucao.json').read_text(encoding='utf-8'))['status'],'BLOQUEADO')

if __name__=='__main__':unittest.main(verbosity=2)



class G7SymlinkWriteDefenseTests(unittest.TestCase):
    """No writes through status, marker or journal symlinks outside QA."""
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='vighna_g7_status_')
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.root=self.base/'panel'
        self.root.mkdir()
        self.store=self.root/'.painel_updates'
        self.store.mkdir()
        self.outside=self.base/'outside.txt'
        self.outside.write_text('SENTINEL_INTACT',encoding='utf8')

    def _symlink_or_skip(self,target:Path, *, directory=False):
        try: target.symlink_to(self.outside,target_is_directory=directory)
        except (OSError,NotImplementedError) as exc:
            self.skipTest('Windows symlink requires Sandbox: '+str(exc))

    def test_status_tmp_symlink_does_not_modify_target(self):
        self._symlink_or_skip(self.store/'ultima_execucao.tmp')
        a._save_operation_status(self.root,'QA','synthetic')
        self.assertEqual(self.outside.read_text(encoding='utf8'),'SENTINEL_INTACT')
        self.assertFalse((self.store/'ultima_execucao.json').exists())

    def test_status_destination_symlink_does_not_modify_target(self):
        self._symlink_or_skip(self.store/'ultima_execucao.json')
        a._save_operation_status(self.root,'QA','synthetic')
        self.assertEqual(self.outside.read_text(encoding='utf8'),'SENTINEL_INTACT')

    def test_marker_symlink_atomic_write_refused(self):
        self._symlink_or_skip(self.store/'ultima_atualizacao.json')
        with self.assertRaises(a.UpdateError):
            a._atomic_local_write(self.store/'ultima_atualizacao.json',b'{}','marcador')
        self.assertEqual(self.outside.read_text(encoding='utf8'),'SENTINEL_INTACT')

    def test_normal_status_is_atomic_and_correct(self):
        a._save_operation_status(self.root,'PASSOU','teste sintético')
        result=json.loads((self.store/'ultima_execucao.json').read_text(encoding='utf8'))
        self.assertEqual(result['status'],'PASSOU')
        self.assertEqual(result['detalhe'],'teste sintético')
        self.assertFalse(list(self.store.glob('painel_atomic_*')))

    def test_mocked_reparse_status_fails_closed(self):
        original=a._unsafe_reparse
        def fake(path):
            if Path(path).name=='ultima_execucao.tmp':return True
            return original(path)
        with unittest.mock.patch.object(a,'_unsafe_reparse',side_effect=fake):
            a._save_operation_status(self.root,'QA','synthetic')
        self.assertFalse((self.store/'ultima_execucao.json').exists())
        self.assertEqual(self.outside.read_text(encoding='utf8'),'SENTINEL_INTACT')


class FrozenPanelSafetyTests(unittest.TestCase):
    def test_frozen_reabertura_bloqueada_antes_de_subprocesso(self):
        from unittest.mock import patch
        import painel_atualizador as updater
        with patch.object(updater.sys, "frozen", True, create=True), patch.object(updater.subprocess, "Popen", side_effect=AssertionError("não iniciar")):
            with self.assertRaises(updater.UpdateError):
                updater._start_panel_after_success(Path("/pasta/sintetica"))

    def test_frozen_g5a_nao_usa_exe_como_python(self):
        from unittest.mock import patch
        import painel_g5_preflight as preflight
        with patch.object(preflight.sys, "frozen", True, create=True), patch.object(preflight.subprocess, "run", side_effect=AssertionError("não iniciar")):
            with self.assertRaises(ValueError):
                preflight.run_g5_a()

class FrozenGUIGuardTests(unittest.TestCase):
    def test_frozen_update_does_not_close_panel_or_spawn(self):
        from unittest.mock import patch
        import painel_homologacao as gui
        class Dummy:
            def destroy(self):
                raise AssertionError("Painel não deve fechar")
        with patch.object(gui.sys, 'frozen', True, create=True), \
             patch.object(gui.messagebox, 'showwarning') as warning, \
             patch.object(gui.subprocess, 'Popen', side_effect=AssertionError('não executar')):
            gui.Painel._start_external_update(Dummy(), 'apply', 'pacote.zip')
        warning.assert_called_once()

    def test_frozen_prepare_qt_does_not_spawn(self):
        from unittest.mock import patch
        import painel_homologacao as gui
        with patch.object(gui.sys, 'frozen', True, create=True), \
             patch.object(gui.messagebox, 'showwarning') as warning, \
             patch.object(gui.subprocess, 'Popen', side_effect=AssertionError('não executar')):
            gui.Painel._prepare_managed_qt(object())
        warning.assert_called_once()

class FrozenG5AGuardTests(unittest.TestCase):
    def test_frozen_g5a_does_not_spawn(self):
        from unittest.mock import patch
        import painel_homologacao as gui
        with patch.object(gui.sys, 'frozen', True, create=True), \
             patch.object(gui.messagebox, 'showwarning') as warning, \
             patch.object(gui.threading, 'Thread', side_effect=AssertionError('não lançar thread')):
            gui.Painel._start_g5a(object())
        warning.assert_called_once()
