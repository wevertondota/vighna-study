# -*- coding: utf-8 -*-
"""Verificações G5-A; jamais executa VighnaStudy.exe."""
import json
from pathlib import Path
import unittest
import zipfile
import tempfile
from unittest.mock import patch
import sys
import os
import subprocess
import painel_g5_ui as e
import painel_g5_preflight as pre

class PreflightTests(unittest.TestCase):
    def test_01_sintetico(self):
        r=pre.run_g5_a()
        self.assertEqual(r['status'],'DIAGNOSTICO_APROVADO')
    def test_02_nao_autoriza_g5(self):
        r=pre.run_g5_a();self.assertFalse(r['g5_aprovado'])
        self.assertFalse(r['instalacao_autorizada'])
    def test_03_ensaios_completos(self):
        r=pre.run_g5_a()
        self.assertEqual(len(r['resultados']),8)
        self.assertTrue(all(x['passou'] for x in r['resultados']))
    def test_04_hash_fonte(self):
        r=pre.run_g5_a();self.assertEqual(len(r['fonte_sha256']),64)
    def test_05_sem_exe_real(self):
        s=Path(pre.__file__).read_text(encoding='utf8')
        self.assertNotIn('VighnaStudy.exe',s)
        self.assertNotIn('PyInstaller',s)

    def test_06_zips_com_ambos_separadores(self):
        for name in ('codigo\\caminhos.py', 'codigo/caminhos.py'):
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as td:
                    f=Path(td)/'fonte.zip'
                    with zipfile.ZipFile(f,'w') as z:
                        z.writestr(name,b'conteudo_teste')
                    with zipfile.ZipFile(f) as z:
                        self.assertEqual(pre._read_source_member(z,'codigo/caminhos.py'),b'conteudo_teste')

    def test_07_zip_ambiguo_rejeitado(self):
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/'duplicado.zip'
            with zipfile.ZipFile(f,'w') as z:
                z.writestr('codigo\\caminhos.py',b'primeiro')
                z.writestr('codigo/caminhos.py',b'segundo')
            with zipfile.ZipFile(f) as z:
                with self.assertRaises(ValueError):
                    pre._read_source_member(z,'codigo/caminhos.py')

    def test_08_zip_sem_arquivo_rejeitado(self):
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/'vazio.zip'
            with zipfile.ZipFile(f,'w') as z:z.writestr('outro.py',b'nada')
            with zipfile.ZipFile(f) as z:
                with self.assertRaisesRegex(ValueError,'ausente'):
                    pre._read_source_member(z,'codigo/caminhos.py')

    def test_09_zip_original_pode_ser_lido_com_separador_normalizado(self):
        with zipfile.ZipFile(pre.SRC) as z:
            for filename in ('caminhos.py','banco.py','backup.py','versao.py'):
                self.assertTrue(pre._read_source_member(z,'codigo/'+filename))

    def test_10_simulacao_de_normalizacao_do_windows(self):
        # Simulate ZipInfo filename normalization (original header unchanged).
        with patch('zipfile._sanitize_filename',
                   side_effect=lambda n:n.replace('\\','/')):
            with zipfile.ZipFile(pre.SRC) as z:
                self.assertTrue(pre._read_source_member(z,'codigo/caminhos.py'))

    def test_11_estrutura_zip_original_nao_muda(self):
        raw=pre.SRC.read_bytes()
        pre.run_g5_a()
        self.assertEqual(raw,pre.SRC.read_bytes())

    def test_12_execucao_integral_zip_normalizado(self):
        with tempfile.TemporaryDirectory() as td:
            alternate=Path(td)/'codigo_normalizado.zip'
            with zipfile.ZipFile(pre.SRC) as source, zipfile.ZipFile(alternate,'w',zipfile.ZIP_DEFLATED) as target:
                for entry in source.infolist():
                    target.writestr(entry.filename.replace('\\','/'),source.read(entry))
            with patch.object(pre,'SRC',alternate):
                self.assertEqual(pre.run_g5_a()['status'],'DIAGNOSTICO_APROVADO')



class QtEnvironmentTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory(prefix="vighna_qa_env_test_")
        self.addCleanup(t.cleanup)
        self.home = Path(t.name)
        self.target = e.destination(self.home)

    def test_01_destino_estavel(self):
        self.assertEqual(self.target, self.home/'VighnaLab'/'Ambiente_Qt_Homologador')
    def test_02_nunca_usa_programa_principal(self):
        self.assertNotIn('estudos.db',str(self.target))
        self.assertNotIn('VighnaStudy.exe',str(self.target))
    def test_03_rejeita_destino_arbitrario(self):
        with self.assertRaises(e.EnvironmentError):
            e.verify_destination(self.home/'Desktop', self.home)
    def test_04_rejeita_pasta_existente_nao_gerenciada(self):
        self.target.mkdir(parents=True)
        (self.target/'meus_arquivos.txt').write_text('intocavel')
        with self.assertRaises(e.EnvironmentError):
            e.verify_destination(self.target,self.home)
        self.assertEqual((self.target/'meus_arquivos.txt').read_text(),'intocavel')
    def test_05_rejeita_pasta_do_programa(self):
        self.target.parent.mkdir(parents=True)
        (self.target.parent/'estudos.db').write_bytes(b'pessoal')
        with self.assertRaises(e.EnvironmentError):
            e.verify_destination(self.target,self.home)
        self.assertEqual((self.target.parent/'estudos.db').read_bytes(),b'pessoal')
    def test_06_rejeita_symlink(self):
        with tempfile.TemporaryDirectory() as linkhome:
            self.target.parent.parent.mkdir(parents=True,exist_ok=True)
            try:
                self.target.parent.symlink_to(Path(linkhome), target_is_directory=True)
            except OSError as exc:
                if getattr(exc,'winerror',None)==1314:
                    self.skipTest('Windows sem privilégio para symlink real; gate não comprovado')
                raise
            with self.assertRaises(e.EnvironmentError):
                e.verify_destination(self.target,self.home)
    def test_06a_rejeita_symlink_simulado_sem_privilegio(self):
        # Confere o contrato de bloqueio; NÃO substitui o teste real de symlink.
        original=Path.is_symlink
        unsafe=self.target.parent
        with patch.object(Path,'is_symlink',lambda obj: obj==unsafe or original(obj)):
            with self.assertRaises(e.EnvironmentError):
                e.verify_destination(self.target,self.home)

    def test_07_ambiente_novo_nao_muda_python_principal(self):
        self.assertFalse(self.target.exists())
        before = sys.executable
        with patch.object(e, 'probe', return_value={'python':'3.13'}):
            r = e.prepare(home=self.home, base_python=Path(sys.executable))
        self.assertEqual(r['status'],'PREPARADO')
        self.assertEqual(sys.executable,before)
        self.assertTrue((self.target/'pyvenv.cfg').exists())
        self.assertTrue((self.target/e.MARKER).exists())
        self.assertTrue(e.interpreter(self.target).is_file())
    def test_08_reutilizar_sem_reinstalar(self):
        with patch.object(e,'probe',return_value={'pyside6':'6.11.2'}):
            e.prepare(home=self.home,base_python=Path(sys.executable))
            with patch.object(e,'subprocess') as sub:
                sub.run.side_effect = AssertionError('nao chamar pip')
                # A verificação de versão é executada pelo runner (não pelo subprocess global quando mockado).
                def fake_runner(cmd,**kwargs):
                    return subprocess.CompletedProcess(cmd,0,'3.13\n','')
                result=e.prepare(home=self.home, base_python=Path(sys.executable), runner=fake_runner)
                self.assertEqual(result['status'],'PREPARADO')
    def test_09_sem_python_3_13_nao_cria_pasta(self):
        def f(cmd,**kw): return subprocess.CompletedProcess(cmd,0,'3.12\n','')
        with self.assertRaisesRegex(e.EnvironmentError,'3.13'):
            e.prepare(home=self.home,base_python=Path(sys.executable),runner=f)
        self.assertFalse(self.target.exists())
    def test_10_rejeita_executavel_ausente(self):
        with self.assertRaises(e.EnvironmentError):
            e.prepare(home=self.home,base_python=self.home/'doesnotexist.exe')
    def test_11_limpa_variaveis_perigosas(self):
        with patch.dict(os.environ,{'PYTHONPATH':'PESSOAL','QT_PLUGIN_PATH':'PESSOAL'}):
            vars=e.clean_env()
        self.assertNotIn('PYTHONPATH',vars);self.assertNotIn('QT_PLUGIN_PATH',vars)
        self.assertEqual(vars['PYTHONNOUSERSITE'],'1')
    def test_12_nao_seleciona_em_falha_de_pip(self):
        with patch.object(e,'probe',side_effect=e.EnvironmentError('dependencias ausentes')):
            def fake_runner(cmd,**kw):
                if '-m' in cmd and 'pip' in cmd:
                    return subprocess.CompletedProcess(cmd,1,'','sem conexao')
                return subprocess.run(cmd,**kw)
            with self.assertRaisesRegex(e.EnvironmentError,'sem conexao'):
                e.prepare(home=self.home,base_python=Path(sys.executable),runner=fake_runner)
        self.assertTrue((self.target/e.MARKER).is_file())
        self.assertTrue((self.target/'pyvenv.cfg').is_file())
    def test_13_pasta_gerenciada_incompleta_rejeitada(self):
        self.target.mkdir(parents=True)
        (self.target/e.MARKER).write_text('{}')
        with self.assertRaises(e.EnvironmentError):
            e.verify_destination(self.target,self.home)
    def test_14_pins_explicitos_e_sem_python_global(self):
        self.assertIn('PySide6==6.11.2',e.DEPENDENCIES)
        self.assertIn('pyinstaller==6.22.3',e.DEPENDENCIES)
        self.assertIn('qtawesome==1.4.0',e.DEPENDENCIES)
    def test_15_proibido_rodar_exe_vighna(self):
        text=Path(e.__file__).read_text(encoding='utf8')
        self.assertNotIn('subprocess.Popen(["VighnaStudy.exe"', text)
    def test_16_importacao_nao_cria_pasta(self):
        self.assertFalse(self.target.exists())
        self.assertTrue(e.destination(self.home).name.endswith('Homologador'))


class G5CValidationTests(unittest.TestCase):
    def _valid_report(self):
        return {'component':'vighna-g5c-sandbox','alvo':e.G5B_TARGET_BUILD,
            'status':'PASSOU_G5C','instalacao_autorizada':False,'banco_sintetico':True,
            'rede':'Disable','clipboard':'Disable','execucoes':[
                {'fase':'primeira','janela_detectada':True},
                {'fase':'segunda','janela_detectada':True}],
            'dashboard_verificado':True,'dashboard_evidencia':'COMPROVADO_POR_IDENTIFICADORES',
            'navegacao_configuracoes':'CONFIRMADA','config_janela_titulo':'Configurações — VighnaStudy',
            'captura_inicio':True,'captura_dashboard':True,'captura_configuracoes':True,
            'retorno_dashboard':'CONFIRMADO_POR_IMAGEM_E_FECHAMENTO','captura_retorno_dashboard':True,
            'encerramento_controlado':True,'reinicializacao':True,'banco_cabecalho_ok':True,
            'janela_qa_verificada':True,'sessao_grafica':{'sessao_igual':True}}

    def test_01_protecao_sandbox(self):
        import xml.etree.ElementTree as ET
        data=e.g5b_sandbox_configuration(Path(r'C:\QA\src'),Path(r'C:\QA\out')).replace('G5B_EXECUTAR_NO_SANDBOX.ps1','G5C_EXECUTAR_NO_SANDBOX.ps1')
        root=ET.fromstring(data)
        self.assertEqual(root.findtext('Networking'),'Disable')
        self.assertEqual(root.findtext('ClipboardRedirection'),'Disable')
        self.assertEqual([x.findtext('ReadOnly') for x in root.findall('./MappedFolders/MappedFolder')],['true','false'])
        self.assertIn('G5C_EXECUTAR_NO_SANDBOX.ps1',root.findtext('LogonCommand/Command'))

    def test_02_exe_so_guest(self):
        self.assertIn('Start-Process -FilePath $exe',e.G5C_SANDBOX_PS)
        self.assertIn(r'C:\VighnaQA\Execucao',e.G5C_SANDBOX_PS)
        self.assertNotIn('shutdown.exe /s /t 0',e.G5C_SANDBOX_PS)
        self.assertIn('CloseMainWindow()',e.G5C_SANDBOX_PS)

    def test_03_relatorio_confirmado(self):
        o=self._valid_report()
        self.assertEqual(e.g5c_validate_report(json.dumps(o).encode())['status'],'PASSOU_G5C')

    def test_04_nao_aceita_autorizacao(self):
        o=self._valid_report();o['instalacao_autorizada']=True
        with self.assertRaises(e.G5BSafetyError):e.g5c_validate_report(json.dumps(o).encode())

    def test_05_nao_aceita_sucesso_sem_navegacao(self):
        o=self._valid_report();o['navegacao_configuracoes']='PENDENTE'
        with self.assertRaises(e.G5BSafetyError):e.g5c_validate_report(json.dumps(o).encode())

    def test_06_nao_aceita_sucesso_sem_sqlite(self):
        o=self._valid_report();o['banco_cabecalho_ok']=False
        with self.assertRaises(e.G5BSafetyError):e.g5c_validate_report(json.dumps(o).encode())

    def test_07_relatorio_parcial_honesto(self):
        o=self._valid_report();o['status']='PARCIAL';o['dashboard_verificado']=False;o['navegacao_configuracoes']='PENDENTE'
        self.assertEqual(e.g5c_validate_report(json.dumps(o).encode())['status'],'PARCIAL')

    def test_08_relatorio_malformado(self):
        with self.assertRaises(e.G5BSafetyError):e.g5c_validate_report(b'{}')
        with self.assertRaises(e.G5BSafetyError):e.g5c_validate_report(b'a'*40001)

    def test_09_sqlite_sintetico_passou(self):
        import sqlite3,hashlib
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/'estudos.db'
            c=sqlite3.connect(f);c.execute('CREATE TABLE disciplina (id INTEGER PRIMARY KEY)');c.commit();c.close()
            digest=hashlib.sha256(f.read_bytes()).hexdigest()
            self.assertEqual(e.g5c_sqlite_check(f,digest)['status'],'PASSOU')

    def test_10_sqlite_hash_modificado(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/'estudos.db';c=sqlite3.connect(f);c.execute('CREATE TABLE x (id INT)');c.commit();c.close()
            self.assertEqual(e.g5c_sqlite_check(f,'0'*64)['status'],'FALHOU')

    def test_11_sqlite_ausente(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(e.g5c_sqlite_check(Path(td)/'vazio.db','')['status'],'BLOQUEADO')

    def test_12_zip_sem_banco_ou_exe(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'z.zip';e.g5c_make_evidence({'status':'PARCIAL','instalacao_autorizada':False},path,
                {'RESULTADO_GUEST_G5C.json':b'{}','BANCO_G5C_SINTETICO.db':b'segredo'})
            with zipfile.ZipFile(path) as z:
                self.assertIsNone(z.testzip());self.assertNotIn('BANCO_G5C_SINTETICO.db',z.namelist())
                hashes=json.loads(z.read('MANIFESTO_SHA256.json'))
                import hashlib
                self.assertTrue(all(hashlib.sha256(z.read(k)).hexdigest()==digest for k,digest in hashes.items()))

    def test_13_bloqueia_linux(self):
        if sys.platform!='win32':
            with self.assertRaises(e.G5BSafetyError):e.g5c_run()

    def test_14_ui_nao_autoriza_g5(self):
        source=Path(e.__file__).read_text(encoding='utf8')
        self.assertIn("'g5_aprovado':False",source)
        self.assertIn("'instalacao_autorizada':False",source)

    def test_15_configuracao_do_guest_sem_shutdown(self):
        self.assertIn("RESULTADO_G5C.json",e.G5C_SANDBOX_PS)
        self.assertIn("$env:LOCALAPPDATA",e.G5C_SANDBOX_PS)
        self.assertIn("BANCO_G5C_SINTETICO.db",e.G5C_SANDBOX_PS)

class G5CHostStagingTests(unittest.TestCase):
    def test_emite_zip_se_compilacao_for_bloqueada(self):
        from unittest.mock import patch
        import hashlib
        with tempfile.TemporaryDirectory(prefix='g5c_staging_') as tmp:
            root=Path(tmp);(root/'System32').mkdir()
            (root/'System32'/'WindowsSandbox.exe').write_bytes(b'FAKE_NEVER_RUN')
            lab=root/'G5B_Laboratorios'/'G5B_G5C_TESTE'
            class BlockedBuild:
                returncode=1
                def wait(self,timeout=None):return 1
            with (patch.object(e.sys,'platform','win32'),
                  patch.dict(os.environ,{'WINDIR':str(root)}),
                  patch.object(e,'g5b_folder',return_value=lab),
                  patch.object(pre,'run_g5_a',return_value={'status':'DIAGNOSTICO_APROVADO'}),
                  patch.object(e,'g5b_check_root',return_value=lab),
                  patch.object(e.subprocess,'Popen',return_value=BlockedBuild()) as popen):
                self.assertEqual(e.g5c_run(),1)
            self.assertEqual(popen.call_count,1)
            self.assertIn('PyInstaller',str(popen.call_args))
            outputs=list(lab.glob('G5_C_DIAGNOSTICO_*.zip'))
            self.assertEqual(len(outputs),1)
            with zipfile.ZipFile(outputs[0]) as z:
                self.assertIsNone(z.testzip())
                obj=json.loads(z.read('RESUMO_G5C.json'))
                self.assertEqual(obj['status'],'BLOQUEADO')
                self.assertFalse(obj['instalacao_autorizada'])
                hashes=json.loads(z.read('MANIFESTO_SHA256.json'))
                self.assertTrue(all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in hashes.items()))
            self.assertFalse((lab/'G5C_LABORATORIO.wsb').exists())


class SandboxG5BTests(unittest.TestCase):
    def test_01_configuracao_duas_pastas_somente_qa(self):
        import xml.etree.ElementTree as ET
        data=e.g5b_sandbox_configuration(Path(r'C:\QA\input'),Path(r'C:\QA\output'))
        root=ET.fromstring(data)
        self.assertEqual(root.findtext('Networking'),'Disable')
        self.assertEqual(root.findtext('ClipboardRedirection'),'Disable')
        self.assertEqual(root.findtext('vGPU'),'Disable')
        maps=root.findall('./MappedFolders/MappedFolder')
        self.assertEqual(len(maps),2)
        self.assertEqual([m.findtext('ReadOnly') for m in maps],['true','false'])
        self.assertEqual([m.findtext('HostFolder') for m in maps],[r'C:\QA\input',r'C:\QA\output'])
        self.assertIn('G5B_EXECUTAR_NO_SANDBOX.ps1',root.findtext('LogonCommand/Command'))
    def test_02_guest_script_limita_execucao(self):
        script=e.G5B_SANDBOX_PS
        self.assertIn('Start-Process -FilePath $exe',script)
        self.assertIn('Stop-Process -Id $p.Id',script)
        self.assertIn('shutdown.exe /s /t 0',script)
        self.assertIn('Copy-Item -Destination $folder',script)
        self.assertIn('RESULTADO_G5B.json',script)
    def test_03_guest_nao_pode_forjar_aprovacao(self):
        import json
        obj={'component':'vighna-g5b-sandbox','alvo':e.G5B_TARGET_BUILD,
             'status':'PASSOU_G5B','processo_iniciado':True,
             'janela_detectada':False,'estabilidade':True,'instalacao_autorizada':False}
        with self.assertRaises(e.G5BSafetyError):e.g5b_validate_guest_report(json.dumps(obj).encode())
    def test_04_guest_sucesso_somente_condicionado(self):
        import json
        obj={'component':'vighna-g5b-sandbox','alvo':e.G5B_TARGET_BUILD,
             'status':'PASSOU_G5B','processo_iniciado':True,
             'janela_detectada':True,'estabilidade':True,'instalacao_autorizada':False}
        self.assertEqual(e.g5b_validate_guest_report(json.dumps(obj).encode())['status'],'PASSOU_G5B')
    def test_05_guest_nao_autoriza_instalacao(self):
        import json
        obj={'component':'vighna-g5b-sandbox','alvo':e.G5B_TARGET_BUILD,'status':'FALHOU',
             'instalacao_autorizada':True}
        with self.assertRaises(e.G5BSafetyError):e.g5b_validate_guest_report(json.dumps(obj).encode())
    def test_06_relatorio_invalido_bloqueado(self):
        with self.assertRaises(e.G5BSafetyError):e.g5b_validate_guest_report(b'<>')
        with self.assertRaises(e.G5BSafetyError):e.g5b_validate_guest_report(b'0'*30001)
    def test_07_laboratorio_existente_bloqueado(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)/'VighnaLab'/'G5B_Laboratorios';base.mkdir(parents=True)
            target=e.g5b_folder(base,'TESTE');target.mkdir()
            with self.assertRaises(e.G5BSafetyError):e.g5b_check_root(target,base=base)
    def test_08_laboratorio_com_banco_real_bloqueado(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)/'VighnaLab'/'G5B_Laboratorios';base.mkdir(parents=True)
            (base/'estudos.db').write_bytes(b'dados intocados')
            with self.assertRaises(e.G5BSafetyError):e.g5b_check_root(e.g5b_folder(base,'TESTE'),base=base)
            self.assertEqual((base/'estudos.db').read_bytes(),b'dados intocados')
    def test_09_laboratorio_fora_do_destino_bloqueado(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            with self.assertRaises(e.G5BSafetyError):e.g5b_check_root(base/'VighnaStudy',base=base)
    def test_10_evidencia_hash_validado(self):
        import hashlib,json
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'evidencia.zip'
            e.g5b_make_evidence({'status':'BLOQUEADO','g5_aprovado':False},path,{'teste.txt':b'ok'})
            with zipfile.ZipFile(path) as z:
                self.assertIsNone(z.testzip())
                h=json.loads(z.read('MANIFESTO_SHA256.json'))
                self.assertTrue(all(hashlib.sha256(z.read(k)).hexdigest()==v for k,v in h.items()))
    def test_11_bloqueia_execucao_linux(self):
        if sys.platform != 'win32':
            with self.assertRaises(e.G5BSafetyError): e.g5b_run()
    def test_12_nao_toca_codigo_principal_ou_gate(self):
        self.assertFalse(hasattr(e,'autorizacao_instalacao'))
        self.assertIn('g5c_pendente',Path(e.__file__).read_text(encoding='utf8'))


class G5BHostStagingRegressionTests(unittest.TestCase):
    def test_host_staging_emite_zip_apos_falha_de_build_sintetica(self):
        """Cobre a sequência real até preparar o nome do ZIP e interrompe
        ANTES de executar PyInstaller ou iniciar Windows Sandbox.
        """
        from unittest.mock import patch
        from pathlib import Path
        import json
        import hashlib
        with tempfile.TemporaryDirectory(prefix='vighna_g5b_preparacao_') as tmp:
            root=Path(tmp)
            system32=root/'System32'
            system32.mkdir()
            (system32/'WindowsSandbox.exe').write_bytes(b'SANDBOX_FALSO_NUNCA_EXECUTAR')
            lab=root/'G5B_Laboratorios'/'G5B_TESTE'
            class FalhaCompilacaoSimulada:
                returncode=1
                def poll(self): return 1
                def wait(self,*a,**kw): return 1
            with (patch.object(e.sys, 'platform', 'win32'),
                  patch.dict(os.environ, {'WINDIR':str(root)}),
                  patch.object(e,'g5b_folder',return_value=lab),
                  patch.object(pre,'run_g5_a',return_value={'status':'DIAGNOSTICO_APROVADO'}),
                  patch.object(e,'g5b_check_root',return_value=lab),
                  patch.object(e.subprocess,'Popen', return_value=FalhaCompilacaoSimulada()) as popen):
                exit_code=e.g5b_run()
            self.assertEqual(exit_code,1)
            self.assertEqual(popen.call_count,1,'A execução do Sandbox é proibida no teste.')
            self.assertEqual(popen.call_args.args[0][2:4],['-m','PyInstaller'])
            zips=list(lab.glob('G5_B_DIAGNOSTICO_*.zip'))
            self.assertEqual(len(zips),1,'O ZIP deve ser gerado em uma falha segura da compilação.')
            with zipfile.ZipFile(zips[0]) as archive:
                self.assertIsNone(archive.testzip())
                resumo=json.loads(archive.read('RESUMO_G5B.json'))
                hashes=json.loads(archive.read('MANIFESTO_SHA256.json'))
                for name,digest in hashes.items():
                    self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(),digest)
            self.assertEqual(resumo['status'],'BLOQUEADO')
            self.assertFalse(resumo['g5_aprovado'])
            self.assertFalse(resumo['instalacao_autorizada'])
            self.assertIn('Compilação QA falhou', resumo['motivo'])
            self.assertFalse((lab/'G5B_LABORATORIO.wsb').exists())
            self.assertFalse((lab/'SAIDA_SINTETICA'/'RESULTADO_G5B.json').exists())

    def test_codigo_nao_mistura_path_e_string_no_nome_da_evidencia(self):
        import ast
        tree=ast.parse(Path(e.__file__).read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node,ast.BinOp) and isinstance(node.op,ast.Add):
                self.assertFalse(
                    isinstance(node.left,ast.BinOp) and isinstance(node.left.op,ast.Div),
                    'Path / nome + texto é uma expressão inválida: linha '+str(node.lineno))

# V3.1.6: maior segurança no relatório de navegação e serialização do guest.
class G5C316SafetyTests(unittest.TestCase):
    def test_g5c_usa_utf8_bom_no_script_guest(self):
        source=Path(e.__file__).read_text(encoding='utf8')
        self.assertIn("write_text(G5C_SANDBOX_PS,encoding='utf-8-sig')",source)

    def test_sem_clique_cego_fora_da_area_util(self):
        code=e.G5C_SANDBOX_PS
        self.assertIn('$report.transicao_tela_detectada',code)
        self.assertIn("SendWait('^k')",code)
        self.assertNotIn('mouse_event(0x0002',code)
        self.assertNotIn('SetCursorPos($x,$y)',code)
        self.assertIn('QAGetConfigTitle',code)

    def test_sem_execucao_do_exe_no_host(self):
        source=Path(e.__file__).read_text(encoding='utf8')
        self.assertIn("if sys.platform!='win32'",source)
        self.assertNotIn('subprocess.Popen([str(built)',source)

# Testes de layout e contratos V3.1.6 (sem dependências do Vighna principal)
class GateV316ContractTests(unittest.TestCase):
    def test_inicial_nao_pode_confirmar_dashboard(self):
        # A simples palavra no portal não representa transição de tela.
        self.assertNotIn("if ($name -match '(?i)dashboard')",e.G5C_SANDBOX_PS)
        self.assertIn("SendWait('^h')",e.G5C_SANDBOX_PS)
        self.assertIn("'Escolha para onde deseja ir'", "'Escolha para onde deseja ir'")
        self.assertIn('dashboard_evidencia',e.G5C_SANDBOX_PS)
        self.assertIn('COMPROVADO_POR_IDENTIFICADORES',e.G5C_SANDBOX_PS)
        self.assertIn('CAPTURA_TRANSICAO_AUDITORIA',e.G5C_SANDBOX_PS)

    def _good(self):
        return {'component':'vighna-g5c-sandbox','alvo':e.G5B_TARGET_BUILD,
            'status':'PASSOU_G5C','instalacao_autorizada':False,'banco_sintetico':True,
            'rede':'Disable','clipboard':'Disable','execucoes':[
                {'fase':'primeira','janela_detectada':True},
                {'fase':'segunda','janela_detectada':True}],
            'dashboard_verificado':True,'dashboard_evidencia':'COMPROVADO_POR_IDENTIFICADORES',
            'navegacao_configuracoes':'CONFIRMADA','config_janela_titulo':'Configurações — VighnaStudy',
            'captura_inicio':True,'captura_dashboard':True,'captura_configuracoes':True,
            'retorno_dashboard':'CONFIRMADO_POR_IMAGEM_E_FECHAMENTO','captura_retorno_dashboard':True,
            'encerramento_controlado':True,'reinicializacao':True,'banco_cabecalho_ok':True,
            'janela_qa_verificada':True,'sessao_grafica':{'sessao_igual':True}}

    def test_relatorio_sucesso_precisa_titulo_modal(self):
        r=self._good();r['config_janela_titulo']='VighnaStudy 0.29.59'
        with self.assertRaises(e.G5BSafetyError):e.g5c_validate_report(json.dumps(r).encode())

    def test_relatorio_sucesso_precisa_identificador_dashboard(self):
        r=self._good();r['dashboard_evidencia']='CAPTURA_TRANSICAO_AUDITORIA'
        with self.assertRaises(e.G5BSafetyError):e.g5c_validate_report(json.dumps(r).encode())

    def test_relatorio_sucesso_precisa_captura_configuracoes(self):
        r=self._good();r['captura_configuracoes']=False
        with self.assertRaises(e.G5BSafetyError):e.g5c_validate_report(json.dumps(r).encode())

    def test_relatorio_sucesso_precisa_capturas_de_ambos_estados(self):
        r=self._good();r['captura_dashboard']=False
        with self.assertRaises(e.G5BSafetyError):e.g5c_validate_report(json.dumps(r).encode())

    def test_relatorio_parcial_permite_auditoria_de_captura(self):
        r=self._good();r.update(status='PARCIAL',dashboard_verificado=False,
                                dashboard_evidencia='CAPTURA_TRANSICAO_AUDITORIA',
                                navegacao_configuracoes='PENDENTE',captura_configuracoes=False)
        self.assertEqual('PARCIAL',e.g5c_validate_report(json.dumps(r).encode())['status'])

    def test_3_capturas_zip_e_hash_sem_banco(self):
        import hashlib
        png=b'\x89PNG\r\n\x1a\n'+b'QA'
        with tempfile.TemporaryDirectory() as td:
            dest=Path(td)/'out.zip'
            e.g5c_make_evidence({'status':'PARCIAL'},dest,{
                'CAPTURA_G5C_INICIO.png':png,'CAPTURA_G5C_DASHBOARD.png':png,
                'CAPTURA_G5C_CONFIGURACOES.png':png,'BANCO_G5C_SINTETICO.db':b'SEGREDO'})
            import zipfile
            with zipfile.ZipFile(dest) as z:
                self.assertNotIn('BANCO_G5C_SINTETICO.db',z.namelist())
                for name in ('CAPTURA_G5C_INICIO.png','CAPTURA_G5C_DASHBOARD.png','CAPTURA_G5C_CONFIGURACOES.png'):
                    self.assertIn(name,z.namelist())
                h=json.loads(z.read('MANIFESTO_SHA256.json'))
                self.assertTrue(all(hashlib.sha256(z.read(n)).hexdigest()==sha for n,sha in h.items()))

class ScrollingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import tkinter as tk
        try:
            tk.Tk().destroy()
        except tk.TclError:
            raise unittest.SkipTest('Tk depende de servidor de tela (Xvfb em laboratório)')

    def test_rodape_fixo_com_rolagem(self):
        import painel_homologacao as m
        app=m.Painel()
        self.addCleanup(app.destroy)
        app.geometry('960x640+0+0')
        app._show_page('testes')
        app.update()
        self.assertTrue(app.tests_scrollbar.winfo_ismapped())
        self.assertTrue(app.folder_btn.winfo_ismapped())
        self.assertTrue(app.copy_btn.winfo_ismapped())
        self.assertEqual(str(app.folder_btn.cget('state')),'disabled')
        self.assertEqual(str(app.copy_btn.cget('state')),'disabled')
        self.assertGreater(app.tests_canvas.bbox('all')[3], app.tests_canvas.winfo_height())
        initial=app.tests_canvas.yview()
        app.tests_canvas.yview_moveto(1.0)
        app.update()
        self.assertGreater(app.tests_canvas.yview()[0],initial[0])
        # Rodapé permanece na geometria da janela, inclusive após rolagem.
        self.assertLess(app.folder_btn.winfo_rooty()+app.folder_btn.winfo_height(),
                        app.winfo_rooty()+app.winfo_height()+1)
        self.assertLess(app.copy_btn.winfo_rooty()+app.copy_btn.winfo_height(),
                        app.winfo_rooty()+app.winfo_height()+1)
        self.assertGreater(app.folder_btn.winfo_width(),120)

    def test_botoes_resultado_somente_zip_existente(self):
        import painel_homologacao as m
        app=m.Painel();self.addCleanup(app.destroy)
        app._show_page('testes');app.update()
        with tempfile.TemporaryDirectory() as td:
            z=Path(td)/'qa.zip';z.write_bytes(b'ZIP')
            app.new_zip=z;app.result_text.set(str(z));app.update()
            self.assertEqual(str(app.folder_btn.cget('state')),'normal')
            self.assertEqual(str(app.copy_btn.cget('state')),'normal')
            app.new_zip=None;app.result_text.set('Sem arquivo');app.update()
            self.assertEqual(str(app.folder_btn.cget('state')),'disabled')


class G5C317NavigationContracts(unittest.TestCase):
    def test_busca_oficial_rc2_nao_clique_por_coordenada(self):
        ps=e.G5C_SANDBOX_PS
        self.assertIn("SendWait('^k')",ps)
        self.assertIn("SendWait('configuracoes')",ps)
        self.assertIn("SendWait('{ENTER}')",ps)
        self.assertIn("'Buscar no Vighna'",ps)
        self.assertIn('QAGetConfigTitle',ps)
        self.assertNotIn('mouse_event(0x0002',ps)

    def test_aprovacao_exige_retorno_ao_dashboard(self):
        import json
        r=GateV316ContractTests()._good()
        r['retorno_dashboard']='PENDENTE'
        with self.assertRaises(e.G5BSafetyError):
            e.g5c_validate_report(json.dumps(r).encode())
        r['retorno_dashboard']='CONFIRMADO_POR_IMAGEM_E_FECHAMENTO'
        r['captura_retorno_dashboard']=False
        with self.assertRaises(e.G5BSafetyError):
            e.g5c_validate_report(json.dumps(r).encode())

    def test_arquivo_retorno_evidencia_zip(self):
        with tempfile.TemporaryDirectory() as t:
            target=Path(t)/'out.zip'
            e.g5c_make_evidence({'status':'PARCIAL'},target,
                {'CAPTURA_G5C_RETORNO_DASHBOARD.png':b'\x89PNG\r\n\x1a\nQA'})
            with zipfile.ZipFile(target) as z:
                self.assertIn('CAPTURA_G5C_RETORNO_DASHBOARD.png',z.namelist())


class G5C318CaptureResilienceTests(unittest.TestCase):
    """Contratos para a falha real WinError CopyFromScreen do diagnóstico Windows."""
    def test_captura_tem_retry_e_alternativa_restrita(self):
        ps=e.G5C_SANDBOX_PS
        self.assertIn('for($attempt=1;$attempt -le 3;$attempt++)',ps)
        self.assertIn('[VighnaQAWin]::PrintWindow',ps)
        self.assertIn('$pidOwned -ne [int]$script:qaProcessId',ps)
        self.assertIn('GetWindowRect($hw',ps)
        self.assertIn('PrintWindow sem conteúdo visual confiável',ps)

    def test_falha_de_captura_nao_gera_throw_ao_chamador(self):
        ps=e.G5C_SANDBOX_PS
        start=ps.index('function Save-QACapture($filename)')
        end=ps.index('function QACaptureDifference',start)
        fn=ps[start:end]
        self.assertIn('captura_erros[$filename]',fn)
        self.assertIn('return $false',fn)
        self.assertIn('finally',fn)
        self.assertIn('$graphics.Dispose()',fn)
        self.assertIn('$bmp.Dispose()',fn)
        self.assertNotIn("throw 'Falha de captura definitiva'",fn)

    def test_captura_falha_mas_reinicio_sqlite_continuam(self):
        ps=e.G5C_SANDBOX_PS
        self.assertLess(ps.index("Save-QACapture 'CAPTURA_G5C_INICIO.png'"),ps.index('$second=Start-QAProcess'))
        self.assertLess(ps.index('$second=Start-QAProcess'),ps.index('if(Test-Path -LiteralPath $database'))
        self.assertNotIn('if(!$report.captura_inicio) {throw',ps)
        self.assertNotIn('if(!$report.captura_dashboard) {throw',ps)
        self.assertIn('DASHBOARD_NAO_ACESSIVEL_SEM_FOCO',ps)

    def test_sem_aprovacao_de_navegacao_sem_capturas(self):
        o=GateV316ContractTests()._good()
        for k in ('captura_inicio','captura_dashboard','captura_configuracoes','captura_retorno_dashboard'):
            bad=o.copy();bad[k]=False
            with self.subTest(campo=k),self.assertRaises(e.G5BSafetyError):
                e.g5c_validate_report(json.dumps(bad).encode())
        bad=o.copy();bad['status']='PARCIAL';bad['captura_inicio']=False
        bad['captura_erros']={'CAPTURA_G5C_INICIO.png':'Identificador inválido'}
        self.assertEqual('PARCIAL',e.g5c_validate_report(json.dumps(bad).encode())['status'])

    def test_status_e_versao_reais_no_host(self):
        import painel_atualizador
        source=Path(e.__file__).read_text(encoding='utf8')
        self.assertIn("'versao_painel':__import__('painel_atualizador').panel_version(h.KIT)",source)
        metadata=json.loads((Path(e.__file__).parent/'PAINEL_VERSAO.json').read_text(encoding='utf-8'))
        self.assertEqual(painel_atualizador.panel_version(Path(e.__file__).parent), metadata['version'])
        self.assertIn('capturas_pendentes',source)
        self.assertIn('erros_captura',source)

    def test_janela_por_pid_sem_dependencia_do_foreground(self):
        ps=e.G5C_SANDBOX_PS
        self.assertIn('public static IntPtr WindowFor(int pid, bool settings)',ps)
        self.assertIn('function QAGetVerifiedWindow($processId',ps)
        self.assertIn('QAGetVerifiedWindow $script:qaProcessId $preferSettings',ps)
        self.assertIn("throw 'PrintWindow bloqueado: HWND não pertence ao EXE QA.'",ps)
        capture=ps[ps.index('function Save-QACapture'):ps.index('function QACaptureDifference')]
        self.assertIn('WindowFor',ps)
        self.assertNotIn('$hw=[VighnaQAWin]::GetForegroundWindow()',capture)

    def test_foco_comprovado_antes_de_teclas(self):
        ps=e.G5C_SANDBOX_PS
        self.assertIn('function QAEnsureFocus($processId,$step)',ps)
        self.assertIn('GetWindowThreadProcessId($hw,[ref]$owner)',ps)
        self.assertIn('QAAssertGuestForeground $first.proc.Id',ps)
        self.assertIn("'FOCO_INDISPONIVEL_BUSCA_BLOQUEADA'",ps)
        self.assertIn("'FOCO_INDISPONIVEL_FECHAMENTO_BLOQUEADO'",ps)
        self.assertIn('GetWindowThreadProcessId($hw,[ref]$foregroundPid)',ps)
        self.assertIn('QAInvokeOwnedButton',ps)
        self.assertNotIn('mouse_event(0x0002',ps)

    def test_diagnostico_da_sessao_persistido(self):
        ps=e.G5C_SANDBOX_PS
        for key in ('sessao_grafica','foco_eventos','janela_qa_eventos','uia_eventos',
                    'user_interactive','monitores','qa_session','foreground_pid'):
            self.assertIn(key,ps)
        self.assertIn('QARecordSession $first.proc.Id',ps)
        self.assertLess(ps.index('QARecordSession $first.proc.Id'),ps.index('$second=Start-QAProcess'))

    def test_sucesso_exige_identidade_janela_e_sessao(self):
        r=GateV316ContractTests()._good()
        for key in ('janela_qa_verificada','sessao_grafica'):
            bad=r.copy();bad.pop(key,None)
            with self.subTest(key=key), self.assertRaises(e.G5BSafetyError):
                e.g5c_validate_report(json.dumps(bad).encode())
        for bad in (dict(r,janela_qa_verificada=False),dict(r,sessao_grafica={'sessao_igual':False})):
            with self.assertRaises(e.G5BSafetyError):
                e.g5c_validate_report(json.dumps(bad).encode())

    def test_snapshot_de_erro_real_nao_e_aprovacao(self):
        real=Path('/mnt/data/G5_C_DIAGNOSTICO_20261013_020755.zip')
        if not real.is_file():self.skipTest('Evidência anterior não disponível')
        with zipfile.ZipFile(real) as z:
            obj=json.loads(z.read('RESULTADO_GUEST_G5C.json'))
        self.assertEqual(obj['status'],'FALHOU')
        self.assertIn('CopyFromScreen',obj['motivo'])
        self.assertFalse(obj['reinicializacao'])
        self.assertEqual(e.g5c_validate_report(json.dumps(obj).encode())['status'],'FALHOU')

    def test_nunca_executa_qa_no_host_ou_autoriza_instalacao(self):
        src=Path(e.__file__).read_text(encoding='utf8')
        self.assertIn("'instalacao_autorizada':False",src)
        self.assertNotIn('subprocess.Popen([str(built)',src)
        self.assertIn('sandbox_rede',src)


class G6ATests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='g6a_new_tests_')
        self.addCleanup(self.tmp.cleanup)
        self.home=Path(self.tmp.name)

    def test_g6a_safe_root(self):
        expected=self.home/'VighnaLab'/'G6A_Laboratorios'
        with self.assertRaises(e.G5BSafetyError):
            e.g6a_safety_root(self.home/'Downloads')
        with patch.object(e.Path,'home',return_value=self.home):
            self.assertEqual(e.g6a_safety_root(expected),expected)

    def test_g6a_blocks_existing_personal_db(self):
        directory=self.home/'VighnaLab'
        directory.mkdir()
        (directory/'estudos.db').write_bytes(b'PESSOAL-NAO-ALTERAR')
        with patch.object(e.Path,'home',return_value=self.home):
            with self.assertRaises(e.G5BSafetyError):e.g6a_run(persist=False)
        self.assertEqual((directory/'estudos.db').read_bytes(),b'PESSOAL-NAO-ALTERAR')

    def test_g6a_success_uses_original_engine(self):
        with patch.object(e.Path,'home',return_value=self.home):
            result=e.g6a_run(persist=False)
        self.assertEqual(result['resultado'],'PASSOU_G6A_SINTETICO')
        self.assertEqual(result['cenarios'][0]['historico_final'],'installed')
        self.assertTrue(result['cenarios'][0]['build_usou_exe_ficticio'])
        self.assertFalse(result['execucao_exe_real'])
        self.assertFalse(result['gate_g6_aprovado'])
        self.assertFalse(result['instalacao_autorizada'])
        self.assertEqual(list((self.home/'VighnaLab'/'G6A_Laboratorios').glob('G6A_*')),[])

    def test_g6a_rollbacks_and_db(self):
        with patch.object(e.Path,'home',return_value=self.home):
            result=e.g6a_run(persist=False)
        self.assertEqual([r['status'] for r in result['cenarios'][1:]],
                         ['FALHA_SIMULADA_REVERTIDA']*2)
        self.assertTrue(all(r['banco_qa_integridade']=='ok' for r in result['cenarios']))
        self.assertEqual(result['cenarios'][2]['historico_final'],'failed')

    def test_g6a_all_sqlite_connections_explicitly_closed(self):
        """Detecta a regressão real: context manager SQLite não fecha o handle."""
        import sqlite3
        opened = []
        native_connect = sqlite3.connect

        class TrackedConnection(sqlite3.Connection):
            closed_explicitly = False

            def close(self):
                self.closed_explicitly = True
                return super().close()

        def connect_tracked(*args, **kwargs):
            kwargs.setdefault('factory', TrackedConnection)
            con = native_connect(*args, **kwargs)
            opened.append(con)  # Mantém referências vivas até a verificação
            return con

        with patch.object(e.Path, 'home', return_value=self.home):
            with patch.object(sqlite3, 'connect', side_effect=connect_tracked):
                result = e.g6a_run(persist=False)
        self.assertEqual(len(result['cenarios']), 3)
        self.assertGreaterEqual(len(opened), 6)
        self.assertTrue(all(c.closed_explicitly for c in opened),
                        'Há conexão SQLite sem close(): no Windows bloqueia rmtree')

    def test_g6a_original_exception_survives_failed_cleanup(self):
        import io, shutil
        from contextlib import redirect_stderr
        with patch.object(e.Path, 'home', return_value=self.home):
            with patch.object(e, 'g6a_exercise', side_effect=RuntimeError('CAUSA_RAIZ_QA')):
                with patch.object(shutil, 'rmtree', side_effect=PermissionError('WINERROR32_FAKE')):
                    buf = io.StringIO()
                    with redirect_stderr(buf):
                        with self.assertRaisesRegex(RuntimeError, 'CAUSA_RAIZ_QA'):
                            e.g6a_run(persist=False)
                    self.assertIn('WINERROR32_FAKE', buf.getvalue())

    def test_g6a_report_zip_sha_and_no_db(self):
        with patch.object(e.Path,'home',return_value=self.home):
            e.g6a_run(persist=True)
        files=list((self.home/'VighnaLab'/'G6A_Laboratorios').glob('G6_A_DIAGNOSTICO_*.zip'))
        self.assertEqual(len(files),1)
        with zipfile.ZipFile(files[0]) as z:
            self.assertEqual(set(z.namelist()),{'RESUMO_G6A.json','MANIFESTO_SHA256.json'})
            checks=json.loads(z.read('MANIFESTO_SHA256.json'))
            self.assertEqual(checks['RESUMO_G6A.json'], __import__('hashlib').sha256(z.read('RESUMO_G6A.json')).hexdigest())
            self.assertFalse(json.loads(z.read('RESUMO_G6A.json'))['instalacao_autorizada'])

    def _g5_fixture(self):
        import hashlib,struct,zlib
        # PNG sintético pequeno, válido como cabeçalho; nenhum dado pessoal incluído.
        def chunk(kind,payload):
            return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff)
        width,height=480,320
        raw=b''.join(b'\x00'+(b'\xff\xff\xff')*width for _ in range(height))
        png=(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+
             chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
        host={'component':'vighna-g5c-host','alvo':e.G5B_TARGET_BUILD,
              'status':'EVIDENCIA_G5C_COMPLETA','validacao_interface':'CONFIRMADA',
              'validacao_sqlite':'PASSOU','g5_aprovado':False,'instalacao_autorizada':False}
        guest={'component':'vighna-g5c-sandbox','alvo':e.G5B_TARGET_BUILD,
               'status':'PASSOU_G5C','instalacao_autorizada':False,
               'dashboard_verificado':True,'navegacao_configuracoes':'CONFIRMADA',
               'captura_configuracoes':True,'captura_dashboard':True,'captura_inicio':True,
               'captura_retorno_dashboard':True,'reinicializacao':True,
               'encerramento_controlado':True,'banco_criado':True,'banco_cabecalho_ok':True,
               'rede':'Disable','clipboard':'Disable'}
        records={'RESUMO_G5C.json':json.dumps(host).encode(),
                 'RESULTADO_GUEST_G5C.json':json.dumps(guest).encode(),
                 'LOG_PYINSTALLER_G5C.txt':b'QA_TESTE_SINTETICO_NAO_COMPROVA_BUILD'}
        for name in ('INICIO','DASHBOARD','CONFIGURACOES','RETORNO_DASHBOARD'):
            records['CAPTURA_G5C_'+name+'.png']=png
        manifest={key:hashlib.sha256(content).hexdigest() for key,content in records.items()}
        records['MANIFESTO_SHA256.json']=json.dumps(manifest).encode()
        fixture=self.home/'fixture_g5.zip'
        with zipfile.ZipFile(fixture,'w') as z:
            for name,content in records.items():z.writestr(name,content)
        return fixture

    def test_g5c_import_structural_fixture(self):
        candidate=self._g5_fixture()
        result=e.g5c_register_evidence(candidate,home=self.home)
        self.assertEqual(result['status'],'EVIDENCIADO_DOCUMENTALMENTE')
        self.assertEqual(e.g5c_load_registry(home=self.home)['arquivo_sha256'],result['arquivo_sha256'])
        self.assertFalse(result['instalacao_autorizada'])

    def test_g5c_tampered_image_rejected(self):
        candidate=self._g5_fixture()
        with zipfile.ZipFile(candidate) as z:
            entries={n:z.read(n) for n in z.namelist()}
        entries['CAPTURA_G5C_INICIO.png']=b'NOPE'+entries['CAPTURA_G5C_INICIO.png'][4:]
        forged=self.home/'bad.zip'
        with zipfile.ZipFile(forged,'w') as z:
            for n,b in entries.items():z.writestr(n,b)
        with self.assertRaises(e.G5BSafetyError):e.g5c_verify_evidence(forged)
        self.assertIsNone(e.g5c_load_registry(home=self.home))

    def test_g5c_claim_without_screenshots_rejected(self):
        forged=self.home/'bad.zip'
        with zipfile.ZipFile(forged,'w') as z:z.writestr('RESUMO_G5C.json','{"status":"EVIDENCIA_G5C_COMPLETA"}')
        with self.assertRaises(e.G5BSafetyError):e.g5c_verify_evidence(forged)

    def test_g6a_engine_code_static_does_not_use_real_installed_files(self):
        source=Path(e.__file__).read_text(encoding='utf8')
        a=source.index('def g6a_exercise(')
        b=source.index('def g6a_run(',a)
        snippet=source[a:b]
        self.assertIn('engine.install_package(',snippet)
        self.assertIn('FALHA_QA_SIMULADA_APOS_COMMIT',snippet)
        self.assertIn('FAKE',snippet.upper())


if __name__=='__main__':unittest.main(verbosity=2)
