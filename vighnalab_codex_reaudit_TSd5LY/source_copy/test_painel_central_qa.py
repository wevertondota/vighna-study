"""Testes autocontidos da Central QA. Não usam dados reais."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch

import painel_central_qa as c


class CentralQATests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="qa_central_test_")
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)
        self.root = self.work / "painel"
        self.root.mkdir()
        for name in ("painel_homologacao.py", "painel_atualizador.py", "painel_g7.py"):
            (self.root / name).write_text("# codigo sintetico\n", encoding="utf-8")
        (self.root / "PAINEL_VERSAO.json").write_text(json.dumps({"component":"vighna-panel", "version":"3.1.45"}))

    def test_01_perfis_invalidos_bloqueados(self):
        with self.assertRaises(c.CentralQAError):
            c.execute(self.root, ["desconhecido"], output_dir=self.work / "out")
        with self.assertRaises(c.CentralQAError):
            c.execute(self.root, [], output_dir=self.work / "out")

    def test_02_geracao_zip_sha256(self):
        output = c.execute(self.root, ["integridade", "sqlite"], output_dir=self.work / "out")
        self.assertEqual(output["resultado"], "APROVADO_ESCOPO")
        with zipfile.ZipFile(output["arquivo"]) as z:
            self.assertIsNone(z.testzip())
            manifest = json.loads(z.read("MANIFESTO_SHA256.json"))
            for name, digest in manifest.items():
                self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(), digest)
            report = json.loads(z.read("RESULTADO_CENTRAL.json"))
            self.assertFalse(report["instalacao_autorizada"])
            self.assertFalse(report["g7_aprovado"])
            self.assertTrue(report["fontes_preservadas"])

    def test_03_nao_copia_banco_pessoal(self):
        (self.root / "meus_dados.sqlite").write_bytes(b"SECRETO")
        cloned = self.work / "CLONE"
        c._copy_sources(self.root, cloned)
        self.assertFalse((cloned / "meus_dados.sqlite").exists())

    def test_04_recusa_pasta_com_vighnastudy(self):
        (self.root / "estudos.db").write_bytes(b"dado sintetico")
        with self.assertRaises(c.CentralQAError):
            c._copy_sources(self.root, self.work / "clone")

    def test_05_rejeita_symlink_de_fonte(self):
        original = self.root / "painel_g7.py"
        original.unlink()
        try:
            original.symlink_to(self.root / "painel_atualizador.py")
        except OSError:
            self.skipTest("SO não permite symlink")
        with self.assertRaises(c.CentralQAError):
            c._copy_sources(self.root, self.work / "clone")

    def test_06_arquivo_originais_intactos(self):
        before = {p.name: c._sha(p.read_bytes()) for p in self.root.iterdir()}
        c.execute(self.root, ["integridade", "sqlite"], output_dir=self.work / "out")
        after = {p.name: c._sha(p.read_bytes()) for p in self.root.iterdir()}
        self.assertEqual(before, after)

    def test_07_pendente_dpi_fora_windows(self):
        if c.sys.platform == "win32":
            self.skipTest("Teste somente fora Windows")
        report = c.execute(self.root, ["dpi"], output_dir=self.work / "out")
        self.assertEqual(report["resultado"], "APROVADO_COM_PENDENCIAS")

    def test_08_saida_dentro_fonte_bloqueada(self):
        with self.assertRaises(c.CentralQAError):
            c.execute(self.root, ["integridade"], output_dir=self.root / "evidencias")

    def test_09_sintetico_nao_e_formal_g7(self):
        report = c.execute(self.root, ["integridade"], output_dir=self.work / "out")
        with zipfile.ZipFile(report["arquivo"]) as z:
            self.assertFalse(json.loads(z.read("RESULTADO_CENTRAL.json"))["g7_aprovado"])

    def test_10_fonte_alterada_durante_testes_bloqueia(self):
        real = c._synthetic_sqlite
        def mutate(work, logfile):
            (self.root / "painel_g7.py").write_text("ALTERACAO SINTETICA")
            return real(work, logfile)
        with patch.object(c, "_synthetic_sqlite", mutate):
            with self.assertRaises(c.CentralQAError):
                c.execute(self.root, ["sqlite"], output_dir=self.work / "out")

    def test_11_nove_perfis_e_estados_validos(self):
        self.assertEqual(len(c.PROFILES), 10)
        self.assertIn("ntfs", c.PROFILES)
        self.assertIn("pyinstaller", c.PROFILES)
        self.assertIn("g7_seguranca", c.PROFILES)
        self.assertIn("g7_prontidao", c.PROFILES)
        self.assertEqual(len(c.STATUS_VALUES), 5)

    def test_12_dpi_e_ntfs_linux_pendentes_sem_falso_sucesso(self):
        if c.sys.platform == "win32":
            self.skipTest("Ensaio específico do Windows no kit integrado")
        out = c.execute(self.root, ["ntfs", "dpi", "pyinstaller"], output_dir=self.work / "out")
        self.assertEqual(out["resultado"], "APROVADO_COM_PENDENCIAS")
        with zipfile.ZipFile(out["arquivo"]) as z:
            report = json.loads(z.read("RESULTADO_CENTRAL.json"))
            for key in ("ntfs", "dpi", "pyinstaller"):
                self.assertEqual(report["perfis"][key]["status"], "PENDENTE")
                self.assertFalse(report["instalacao_autorizada"])

    def test_13_g7_sintetico_nao_concede_aprovacao_formal(self):
        from pathlib import Path
        actual_source = Path(c.__file__).with_name("painel_g7.py")
        clone = self.work / "clone"
        clone.mkdir()
        (clone / "painel_g7.py").write_bytes(actual_source.read_bytes())
        result = c._g7_safety(self.work, clone, self.work / "g7.json")
        self.assertEqual(result["status"], "PASSOU_COM_RESSALVAS")
        self.assertFalse(result["g7_formal_aprovado"])
        self.assertEqual(len(result["verificacoes_sinteticas"]), 4)
        self.assertTrue(all(result["verificacoes_sinteticas"].values()))

    def test_14_arquivo_de_origem_nao_pode_virar_escopo_de_saida(self):
        with self.assertRaises(c.CentralQAError):
            c.execute(self.root, ["integridade"], output_dir=self.root)

    def test_15_resultados_nao_homologam_instalacao(self):
        result = c.execute(self.root, ["integridade", "sqlite"], output_dir=self.work / "out")
        with zipfile.ZipFile(result["arquivo"]) as z:
            report = json.loads(z.read("RESULTADO_CENTRAL.json"))
        self.assertEqual(report["resumo_estados"]["PASSOU"], 2)
        self.assertFalse(report["g7_aprovado"])
        self.assertFalse(report["instalacao_autorizada"])
        self.assertEqual(report["central"], "1.5")

    def test_16_regressoes_incluem_central(self):
        self.assertIn("test_painel_central_qa", c.REGRESSION_MODULES)
        self.assertEqual(len(c.REGRESSION_MODULES), len(set(c.REGRESSION_MODULES)))

    def test_17_ntfs_nao_aprova_rejeicao_generica(self):
        # Em qualquer SO, simular mklink bem-sucedido com uma pasta comum.
        # Rejeição por fontes ausentes NÃO equivale à proteção contra junction.
        import subprocess
        def create_directory(command, *, cwd, **kwargs):
            self.assertEqual(command[:5], ["cmd.exe", "/d", "/c", "mklink", "/J"])
            self.assertEqual(len(command), 7)
            link, target = map(Path, command[5:])
            self.assertEqual(link.name, "atalho_junction")
            self.assertEqual(target.name, "destino")
            link.mkdir()
            return subprocess.CompletedProcess(command, 0, stdout="teste sintetico", stderr="")
        with patch.object(c.sys, "platform", "win32"), patch.object(c.subprocess, "run", side_effect=create_directory):
            result = c._native_ntfs(self.work, self.work / "ntfs_resultado.json")
        self.assertEqual(result["status"], "FALHOU")
        self.assertFalse(result["junction_detectada"])
        self.assertFalse(result["copia_redirecionada_bloqueada"])
        self.assertTrue(result["arquivo_sentinela_intacto"])
        self.assertTrue(result["argumentos_separados"])


    def test_18_g7_prontidao_somente_requisitos(self):
        # Prova que não lê backups e que nem os hashes de referência são
        # confundidos com evidências efetivamente examinadas.
        import shutil
        src = Path(c.__file__).parent / "painel_g7.py"
        shutil.copyfile(src, self.root / "painel_g7.py")
        (self.root / "backup_usuario.db").write_bytes(b"BANCO-SENTINELA-NAO-LER")
        origin = c._sha((self.root / "backup_usuario.db").read_bytes())
        run = c.execute(self.root, ["g7_prontidao"], output_dir=self.work / "out")
        self.assertEqual(run["resultado"], "APROVADO_COM_PENDENCIAS")
        self.assertEqual(run["perfis"]["g7_prontidao"]["status"], "PENDENTE")
        with zipfile.ZipFile(run["arquivo"]) as z:
            plan = json.loads(z.read("G7_PRONTIDAO_REAL.json"))
            self.assertEqual(len(plan["evidencias_g6_exigidas"]), 3)
            self.assertEqual(plan["backup_nuvem_real"], "NAO_ACESSADO")
            self.assertFalse(plan["g7_formal_aprovado"])
            self.assertFalse(plan["instalacao_autorizada"])
            self.assertNotIn(b"BANCO-SENTINELA-NAO-LER", z.read("G7_PRONTIDAO_REAL.json"))
        self.assertEqual(c._sha((self.root / "backup_usuario.db").read_bytes()), origin)

    def test_19_g7_referencia_invalida_falha_fechada(self):
        # Não permitir falso estado de preparação concluída quando o módulo
        # G7 está inválido, incompleto ou tem referência adulterada.
        (self.root / "painel_g7.py").write_text("REFERENCE = {'G6-A': ('incompleto.zip', 'x')}\n", encoding="utf-8")
        run = c.execute(self.root, ["g7_prontidao"], output_dir=self.work / "out")
        self.assertEqual(run["resultado"], "FALHOU")
        self.assertEqual(run["perfis"]["g7_prontidao"]["status"], "FALHOU")

    def test_20_pyinstaller_faltante_nao_instala_automaticamente(self):
        # Independente do estado real do host: PyInstaller ausente resulta em
        # PENDENTE e nunca dispara pip/install nem altera fontes.
        with patch.object(c.sys, "platform", "win32"), patch.object(c.importlib.util, "find_spec", return_value=None):
            res = c._pyinstaller(self.work, self.root, {}, self.work / "pyinstaller.json")
        self.assertEqual(res["status"], "PENDENTE")
        self.assertFalse(res["preflight"]["pyinstaller_disponivel"])
        self.assertFalse(res["preflight"]["build_executado"])



    def test_21_frozen_regressoes_nao_lancam_exe(self):
        from unittest.mock import patch
        with patch.object(c.sys, "frozen", True, create=True), patch.object(c.subprocess, "run", side_effect=AssertionError("subprocess não permitido")):
            result = c._subprocess_test(self.root, {}, self.work / "frozen_regressoes.json", ("test_painel_g7",))
        self.assertEqual(result["status"], "PENDENTE")
        self.assertEqual(json.loads((self.work / "frozen_regressoes.json").read_text())["status"], "PENDENTE")

    def test_22_frozen_pyinstaller_nao_lanca_exe(self):
        from unittest.mock import patch
        with patch.object(c.sys, "frozen", True, create=True), patch.object(c.subprocess, "run", side_effect=AssertionError("subprocess não permitido")):
            result = c._pyinstaller(self.work, self.root, {}, self.work / "frozen_pyinstaller.json")
        self.assertEqual(result["status"], "PENDENTE")
        self.assertIn("congelado", result["motivo"])

    def test_23_modo_python_regressoes_preservado(self):
        from unittest.mock import patch
        import subprocess
        with patch.object(c.sys, "frozen", False, create=True), patch.object(c.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, stdout="", stderr="Ran 1 test in 0.001s\n\nOK")) as runner:
            result = c._subprocess_test(self.root, {}, self.work / "regressoes_py.log", ("test_painel_g7",))
        self.assertEqual(result["status"], "PASSOU")
        self.assertEqual(result["executados"], 1)
        self.assertEqual(runner.call_args.args[0][0], c.sys.executable)


class FrozenEntrypointV3150Tests(unittest.TestCase):
    """Protocolo do ponto de entrada: sem GUI, sem escrita e sem shell."""

    @staticmethod
    def panel():
        import painel_homologacao as p
        return p

    def test_24_ping_posicional_exato(self):
        p = self.panel()
        import io
        from contextlib import redirect_stdout
        output=io.StringIO()
        with patch.object(p, "Painel", side_effect=AssertionError("Tk nao deve iniciar")), redirect_stdout(output):
            rc=p.main([p.QA_CHILD_MARKER,"--protocolo","1","ping"])
        self.assertEqual(rc,0)
        result=json.loads(output.getvalue())
        self.assertEqual(result["resultado"],"OK")
        self.assertEqual(result["protocolo"],1)
        self.assertEqual(result["operacao"],"ping")

    def test_25_frozen_exibe_estado_sem_iniciar_gui(self):
        p=self.panel()
        import io
        from contextlib import redirect_stdout
        out=io.StringIO()
        with patch.object(p.sys,"frozen",True,create=True),patch.object(p,"Painel",side_effect=AssertionError("GUI")),redirect_stdout(out):
            rc=p.main([p.QA_CHILD_MARKER,"--protocolo","1","ping"])
        self.assertEqual(rc,0)
        self.assertTrue(json.loads(out.getvalue())["frozen"])

    def test_26_rejeita_marcador_errado(self):
        self._invalid(["--outro","--protocolo","1","ping"])

    def test_27_rejeita_versao_desconhecida(self):
        self._invalid(["--vighnalab-qa-child","--protocolo","2","ping"])

    def test_28_rejeita_verbo_nao_autorizado(self):
        self._invalid(["--vighnalab-qa-child","--protocolo","1","backup"])

    def test_29_rejeita_argumento_extra(self):
        self._invalid(["--vighnalab-qa-child","--protocolo","1","ping","--arquivo=privado.db"])

    def test_30_rejeita_python_c(self):
        self._invalid(["-c","print(1)"])

    def test_31_rejeita_python_m(self):
        self._invalid(["-m","unittest"])

    def test_32_rejeita_caminho(self):
        self._invalid(["dados.db"])

    def test_33_ping_subprocesso_python_real(self):
        import sys,subprocess
        from pathlib import Path
        root=Path(__file__).resolve().parent
        cp=subprocess.run([sys.executable,"-B",str(root/"painel_homologacao.py"),
              "--vighnalab-qa-child","--protocolo","1","ping"],
              cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=15)
        self.assertEqual(cp.returncode,0,cp.stderr)
        self.assertEqual(json.loads(cp.stdout)["resultado"],"OK")
        self.assertEqual(cp.stderr,"")

    def test_34_rejeicao_subprocesso_real(self):
        import sys,subprocess
        from pathlib import Path
        root=Path(__file__).resolve().parent
        cp=subprocess.run([sys.executable,"-B",str(root/"painel_homologacao.py"),
              "--vighnalab-qa-child","--protocolo","1","unittest"],
              cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=15)
        self.assertEqual(cp.returncode,2)
        self.assertFalse(cp.stdout.strip())
        self.assertEqual(json.loads(cp.stderr)["status"],"REJEITADO")

    def _invalid(self,args):
        p=self.panel()
        import io
        from contextlib import redirect_stderr
        stderr=io.StringIO()
        with patch.object(p,"Painel",side_effect=AssertionError("GUI")),redirect_stderr(stderr):
            code=p.main(args)
        self.assertEqual(code,2)
        self.assertEqual(json.loads(stderr.getvalue())["status"],"REJEITADO")


if __name__ == "__main__":
    unittest.main()


class FrozenReadOnlyV3151Tests(unittest.TestCase):
    """Diagnósticos de leitura permitidos dentro de um EXE congelado."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="qa_readonly_v3151_")
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)

    @staticmethod
    def panel():
        import painel_homologacao
        return painel_homologacao

    def _call(self, verb):
        import io
        from contextlib import redirect_stdout, redirect_stderr
        p=self.panel();out,err=io.StringIO(),io.StringIO()
        with patch.object(p,'Painel',side_effect=AssertionError('GUI aberta indevidamente')):
            with redirect_stdout(out),redirect_stderr(err):
                code=p.main([p.QA_CHILD_MARKER,'--protocolo','1',verb])
        raw=out.getvalue() if code==0 else (out.getvalue() or err.getvalue())
        return code,json.loads(raw)

    def test_35_ambiente_leitura_sem_abrir_gui(self):
        import sys
        code,data=self._call('ambiente')
        self.assertEqual(code,0)
        self.assertEqual(data['operacao'],'ambiente')
        self.assertEqual(data['plataforma'],sys.platform)
        self.assertNotIn('HOME',data)
        self.assertNotIn('caminho',data)

    def test_36_identidade_interna_verificada(self):
        code,data=self._call('identidade')
        self.assertEqual(code,0)
        self.assertEqual(data['versao'],'3.1.53')
        self.assertEqual(data['componente'],'vighna-panel')

    def test_37_componentes_precarregados_sem_importacao_extra(self):
        p=self.panel();import sys
        prior=set(sys.modules)
        code,data=self._call('componentes')
        self.assertEqual(code,0)
        self.assertTrue(all(data['modulos_importados'].values()))
        self.assertEqual(set(data['modulos_importados']),set(p.QA_COMPONENTS))
        self.assertEqual(set(sys.modules),prior)

    def test_38_identidade_ignora_arquivo_no_cwd(self):
        import os
        p=self.panel()
        local=self.work/'falso_cwd';local.mkdir()
        (local/'PAINEL_VERSAO.json').write_text('{"component":"vighna-panel","version":"3.1.999"}')
        old=os.getcwd()
        try:
            os.chdir(local)
            code,data=self._call('identidade')
        finally:os.chdir(old)
        self.assertEqual(code,0)
        self.assertEqual(data['versao'],'3.1.53')

    def test_39_identidade_sem_recurso_falha_fechada(self):
        import io
        from contextlib import redirect_stderr
        p=self.panel();blank=self.work/'sem_recurso';blank.mkdir()
        err=io.StringIO()
        with patch.object(p.sys,'frozen',True,create=True),patch.object(p.sys,'_MEIPASS',str(blank),create=True),redirect_stderr(err):
            code=p.main([p.QA_CHILD_MARKER,'--protocolo','1','identidade'])
        self.assertEqual(code,3)
        self.assertEqual(json.loads(err.getvalue())['status'],'FALHOU')
        self.assertNotIn(str(blank),err.getvalue())

    def test_40_identidade_arquivo_falso_falha_fechada(self):
        import io
        from contextlib import redirect_stderr
        p=self.panel();blank=self.work/'recurso_invalido';blank.mkdir()
        (blank/'PAINEL_VERSAO.json').write_text('isso-nao-e-json')
        err=io.StringIO()
        with patch.object(p.sys,'frozen',True,create=True),patch.object(p.sys,'_MEIPASS',str(blank),create=True),redirect_stderr(err):
            code=p.main([p.QA_CHILD_MARKER,'--protocolo','1','identidade'])
        self.assertEqual(code,3)
        self.assertEqual(json.loads(err.getvalue())['status'],'FALHOU')

    def test_41_componentes_ausentes_ficam_pendentes(self):
        import io
        from contextlib import redirect_stdout
        p=self.panel();out=io.StringIO()
        with patch.dict(p.sys.modules,{'painel_g7':None}),redirect_stdout(out):
            code=p.main([p.QA_CHILD_MARKER,'--protocolo','1','componentes'])
        self.assertEqual(code,3)
        self.assertEqual(json.loads(out.getvalue())['resultado'],'PENDENTE')

    def test_42_extra_em_diagnostico_rejeitado(self):
        import io
        from contextlib import redirect_stderr
        p=self.panel();err=io.StringIO()
        with redirect_stderr(err):
            code=p.main([p.QA_CHILD_MARKER,'--protocolo','1','identidade','--alvo=usuario.db'])
        self.assertEqual(code,2)
        self.assertEqual(json.loads(err.getvalue())['status'],'REJEITADO')

    def test_43_leitura_proibida_e_python_c_rejeitados(self):
        import io
        from contextlib import redirect_stderr
        p=self.panel()
        for args in (['--vighnalab-qa-child','--protocolo','1','backup'], ['-c','import os']):
            err=io.StringIO()
            with redirect_stderr(err):code=p.main(args)
            self.assertEqual(code,2)
            self.assertEqual(json.loads(err.getvalue())['status'],'REJEITADO')

    def test_44_subprocessos_reais_leitura_e_rejeicao(self):
        import subprocess,sys
        path=self.panel().__file__
        for verb in ('ambiente','identidade','componentes'):
            result=subprocess.run([sys.executable,'-B',path,'--vighnalab-qa-child','--protocolo','1',verb],capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,0,(verb,result.stderr))
            self.assertEqual(json.loads(result.stdout)['operacao'],verb)
        result=subprocess.run([sys.executable,'-B',path,'--vighnalab-qa-child','--protocolo','1','apagar'],capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,2)


class FrozenCentralReadOnlyV3152Tests(unittest.TestCase):
    """Apenas diagnósticos de leitura, sem executar interpretador arbitrário."""
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="qa_central_readonly_v3152_")
        self.addCleanup(self.tmp.cleanup)
        self.work=Path(self.tmp.name)
        self.root=Path(__file__).resolve().parent

    def test_45_central_tem_dez_perfis_com_diagnosticos(self):
        self.assertEqual(len(c.PROFILES), 10)
        self.assertEqual(c.PROFILES[-1], 'diagnosticos_exe')
        self.assertEqual(c.ENGINE_VERSION, '1.5')

    def test_46_python_quatro_diagnosticos_e_zip_manifesto(self):
        result=c.execute(self.root, ('diagnosticos_exe',), output_dir=self.work/'evidencias')
        self.assertEqual(result['resultado'], 'APROVADO_ESCOPO')
        with zipfile.ZipFile(result['arquivo']) as z:
            self.assertIsNone(z.testzip())
            data=json.loads(z.read('RESULTADO_CENTRAL.json'))
            self.assertEqual(data['versao_base'], '3.1.53')
            self.assertFalse(data['instalacao_autorizada'])
            self.assertFalse(data['g7_aprovado'])
            profile=data['perfis']['diagnosticos_exe']
            self.assertEqual(profile['status'], 'PASSOU')
            self.assertEqual(len(profile['operacoes']), 4)
            hashes=json.loads(z.read('MANIFESTO_SHA256.json'))
            for name,digest in hashes.items():
                self.assertEqual(c._sha(z.read(name)), digest)

    def test_47_frozen_nao_copia_fontes_e_marca_outros_pendentes(self):
        import subprocess
        self_path=Path(c.sys.executable)
        def fake_run(argv,**kw):
            self.assertEqual(argv[0],str(self_path))
            self.assertEqual(argv[1:4],["--vighnalab-qa-child", "--protocolo", "1"])
            self.assertTrue(kw['env'].get('PYINSTALLER_RESET_ENVIRONMENT'))
            op=argv[4]
            doc={'protocolo':1,'operacao':op,'resultado':'OK','frozen':True}
            if op=='identidade':doc.update({'componente':'vighna-panel','versao':'3.1.53'})
            if op=='componentes':doc['modulos_importados']={n:True for n in ('painel_core','painel_atualizador','painel_central_qa','painel_g7')}
            return subprocess.CompletedProcess(argv,0,stdout=json.dumps(doc),stderr='')
        with patch.object(c.sys,'frozen',True,create=True),patch.object(c,'_copy_sources',side_effect=AssertionError('fontes nao devem ser copiadas')),patch.object(c,'_frozen_integrity',return_value={'status':'PASSOU','recursos':{}}),patch.object(c.subprocess,'run',side_effect=fake_run):
            result=c.execute(self.work/'RAIZ_INEXISTENTE',('integridade','diagnosticos_exe'),output_dir=self.work/'saida')
        self.assertEqual(result['resultado'],'APROVADO_ESCOPO')
        with zipfile.ZipFile(result['arquivo']) as z:
            doc=json.loads(z.read('RESULTADO_CENTRAL.json'))
        self.assertEqual(doc['perfis']['integridade']['status'],'PASSOU')
        self.assertEqual(doc['perfis']['diagnosticos_exe']['status'],'PASSOU')
        self.assertIsNone(doc['fontes_preservadas'])
        self.assertFalse(doc['instalacao_autorizada'])

    def test_48_frozen_rejeita_resposta_com_operacao_trocada(self):
        import subprocess
        def fake_run(cmd, **kwargs):
            doc={'protocolo':1,'operacao':'operacao_falsa','resultado':'OK','frozen':True}
            return subprocess.CompletedProcess(cmd,0,stdout=json.dumps(doc),stderr='')
        with patch.object(c.sys,'frozen',True,create=True), patch.object(c.subprocess,'run',side_effect=fake_run):
            res=c._readonly_child_profile(self.work/'test.json',c._isolated_env(self.work))
        self.assertEqual(res['status'],'FALHOU')
        self.assertEqual(len(res['operacoes']),1)

    def test_49_timeout_e_pendente_nao_vira_aprovado(self):
        import subprocess
        def stalled(cmd,**kw):raise subprocess.TimeoutExpired(cmd, kw['timeout'])
        with patch.object(c.sys,'frozen',True,create=True), patch.object(c.subprocess,'run',side_effect=stalled):
            res=c._readonly_child_profile(self.work/'timeout.json',c._isolated_env(self.work))
        self.assertEqual(res['status'],'FALHOU')

    def test_50_operacao_central_nao_aceita_argumentos_extras(self):
        import painel_homologacao as p
        import io
        from contextlib import redirect_stderr
        err=io.StringIO()
        with redirect_stderr(err):
            code=p.main([p.QA_CHILD_MARKER,'--protocolo','1','central_leitura','--pasta=backup'])
        self.assertEqual(code,2)
        self.assertEqual(json.loads(err.getvalue())['status'],'REJEITADO')

    def test_51_central_leitura_so_diagnosticos_e_sem_gui(self):
        import painel_homologacao as p
        import io
        from contextlib import redirect_stdout
        out=io.StringIO()
        with patch.object(p,'Painel',side_effect=AssertionError('GUI')), redirect_stdout(out):
            rc=p.main([p.QA_CHILD_MARKER,'--protocolo','1','central_leitura'])
        self.assertEqual(rc,0)
        doc=json.loads(out.getvalue())
        self.assertEqual(doc['operacao'],'central_leitura')
        with zipfile.ZipFile(doc['arquivo']) as z:
            d=json.loads(z.read('RESULTADO_CENTRAL.json'))
        self.assertEqual(list(d['perfis']),['diagnosticos_exe'])
        self.assertFalse(d['g7_aprovado'])

    def test_52_nao_usa_endereco_ou_banco_externo(self):
        self.assertNotIn('backup',c._READ_OPS)
        self.assertNotIn('atualizacao',c._READ_OPS)


class FrozenIntegritySQLiteV3153Tests(unittest.TestCase):
    """Novos contratos frozen apenas com entradas embutidas e TEMP sintético."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="vighnalab_3153_test_")
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)

    def _resources(self):
        embedded = self.work / "RECURSOS_EMBUTIDOS"
        embedded.mkdir(exist_ok=True)
        src = Path(__file__).parent
        for name in c.FROZEN_RESOURCE_SHA256:
            (embedded / name).write_bytes((src / name).read_bytes())
        return embedded

    def test_53_integridade_embutida_correspondente(self):
        with patch.object(c.sys, "frozen", True, create=True), patch.object(c.sys, "_MEIPASS", str(self._resources()), create=True):
            result = c._frozen_integrity(self.work / "validado.json")
        self.assertEqual(result["status"], "PASSOU")
        self.assertEqual(len(result["recursos"]), 3)

    def test_54_recurso_adulterado_falha_fechada(self):
        emb = self._resources()
        (emb / "PAINEL_VERSAO.json").write_text('{"component":"vighna-panel","version":"3.1.999"}')
        with patch.object(c.sys, "frozen", True, create=True), patch.object(c.sys, "_MEIPASS", str(emb), create=True):
            result = c._frozen_integrity(self.work / "adulterado.json")
        self.assertEqual(result["status"], "FALHOU")

    def test_55_recurso_ausente_rejeitado(self):
        emb = self._resources()
        (emb / "estado_planejamento_v3.json").unlink()
        with patch.object(c.sys, "frozen", True, create=True), patch.object(c.sys, "_MEIPASS", str(emb), create=True):
            self.assertEqual(c._frozen_integrity(self.work / "ausente.json")["status"], "FALHOU")

    def test_56_recurso_redirecionado_rejeitado(self):
        emb = self._resources()
        target = emb / "PAINEL_VERSAO.json"
        target.unlink()
        try:
            target.symlink_to(Path(__file__).parent / 'PAINEL_VERSAO.json')
        except OSError:
            self.skipTest("Windows não permite symlink")
        with patch.object(c.sys, "frozen", True, create=True), patch.object(c.sys, "_MEIPASS", str(emb), create=True):
            self.assertEqual(c._frozen_integrity(self.work / "link.json")["status"], "FALHOU")

    def test_57_nao_le_diretorio_atual(self):
        emb = self._resources()
        (self.work / "PAINEL_VERSAO.json").write_text('{}',encoding='utf-8')
        with patch.object(c.sys, "frozen", True, create=True), patch.object(c.sys, "_MEIPASS", str(emb), create=True):
            self.assertEqual(c._frozen_integrity(self.work / "cwd.json")["status"], "PASSOU")

    def test_58_sqlite_frozen_somente_sintetico(self):
        with patch.object(c.sys,"frozen",True,create=True):
            result=c._frozen_sqlite_synthetic(self.work,self.work / "sqlite.json")
        self.assertEqual(result["status"],"PASSOU")
        self.assertFalse(result["dados_pessoais_utilizados"])
        self.assertEqual(result["registros"],25)

    def test_59_sqlite_frozen_falha_controlada(self):
        with patch.object(c.sys,"frozen",True,create=True), patch.object(c, "_synthetic_sqlite", side_effect=OSError("erro simulado")):
            result=c._frozen_sqlite_synthetic(self.work,self.work / "falha_sqlite.json")
        self.assertEqual(result["status"],"FALHOU")

    def test_60_central_segura_nao_aceita_argumentos_extras(self):
        import painel_homologacao as p
        import io
        from contextlib import redirect_stderr
        out=io.StringIO()
        with redirect_stderr(out):
            rc=p.main([p.QA_CHILD_MARKER,"--protocolo","1","central_segura","--arquivo=estudos.db"])
        self.assertEqual(rc,2)
        self.assertEqual(json.loads(out.getvalue())["status"],"REJEITADO")

    def test_61_central_segura_python_zip_tres_perfis(self):
        import painel_homologacao as p
        import io
        from contextlib import redirect_stdout
        out=io.StringIO()
        with redirect_stdout(out):
            rc=p.main([p.QA_CHILD_MARKER,"--protocolo","1","central_segura"])
        self.assertEqual(rc,0)
        r=json.loads(out.getvalue())
        with zipfile.ZipFile(r["arquivo"]) as z:
            data=json.loads(z.read("RESULTADO_CENTRAL.json"))
        self.assertEqual(set(data["perfis"]),{"diagnosticos_exe","integridade","sqlite"})
        self.assertFalse(data["g7_aprovado"])

    def test_62_frozen_execucao_somente_perfis_permitidos(self):
        emb=self._resources()
        import subprocess
        def fake_run(args, **kw):
            op=args[-1]
            doc={"protocolo":1,"operacao":op,"resultado":"OK","frozen":True}
            if op=='identidade':doc.update({"componente":"vighna-panel","versao":"3.1.53"})
            if op=='componentes':doc['modulos_importados']={n:True for n in ('painel_core','painel_atualizador','painel_central_qa','painel_g7')}
            return subprocess.CompletedProcess(args,0,json.dumps(doc),"")
        with patch.object(c.sys,"frozen",True,create=True), patch.object(c.sys,"_MEIPASS",str(emb),create=True), patch.object(c.subprocess,"run", side_effect=fake_run),patch.object(c, "_copy_sources", side_effect=AssertionError("não copiar fontes")):
            result=c.execute(self.work/'RAIZ_NAO_EXISTENTE',('diagnosticos_exe','integridade','sqlite','g7'),output_dir=self.work/'EVIDENCIAS_SAIDA')
        self.assertEqual(result['resultado'],'APROVADO_COM_PENDENCIAS')
        self.assertEqual(result['perfis']['integridade']['status'],'PASSOU')
        self.assertEqual(result['perfis']['sqlite']['status'],'PASSOU')
        self.assertEqual(result['perfis']['g7']['status'],'PENDENTE')
        self.assertIsNone(json.loads(zipfile.ZipFile(result['arquivo']).read('RESULTADO_CENTRAL.json'))['fontes_preservadas'])
