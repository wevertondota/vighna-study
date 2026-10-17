# -*- coding: utf-8 -*-
"""Testes puros de modelo e garantias de escopo da V2-A."""
from __future__ import annotations
import ast
import copy
import json
from pathlib import Path
import unittest

import painel_planejamento as p

ROOT=Path(__file__).resolve().parent

class PlanejamentoV2ATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=p.carregar_estado()

    def test_01_nove_macrolotes(self):
        self.assertEqual([x['id'] for x in self.data['macrolotes']], ['M'+str(i) for i in range(1,10)])

    def test_02_estado_valido(self):
        self.assertIs(p.validar_estado(self.data), self.data)

    def test_03_status_agrupados(self):
        self.assertEqual(p.panorama(self.data), dict(referencia=1,homologacao=1,laboratorio=1,planejado=6))

    def test_04_m2_em_homologacao(self):
        self.assertEqual(self.data['macrolotes'][1]['situacao'], 'homologacao')

    def test_05_m3_nao_integrado(self):
        self.assertEqual(self.data['macrolotes'][2]['situacao'], 'laboratorio')
        self.assertIn('não integrado',self.data['marcos']['m3'])

    def test_06_nao_autoriza_instalacao(self):
        self.assertIs(self.data['instalacao_autorizada'], False)
        self.assertIn('Nenhuma autorização',self.data['marcos']['instalacao'])

    def test_07_nao_alega_sincronizacao(self):
        self.assertFalse(self.data['sincronizacao_online'])
        self.assertIn('manual',self.data['origem'])

    def test_08_rejeita_autorizacao_falsa(self):
        d=copy.deepcopy(self.data); d['instalacao_autorizada']=True
        with self.assertRaises(p.EstadoInvalido):p.validar_estado(d)

    def test_09_rejeita_sincronizacao_falsa(self):
        d=copy.deepcopy(self.data); d['sincronizacao_online']=True
        with self.assertRaises(p.EstadoInvalido):p.validar_estado(d)

    def test_10_rejeita_duplicidade(self):
        d=copy.deepcopy(self.data);d['macrolotes'][-1]['id']='M8'
        with self.assertRaises(p.EstadoInvalido):p.validar_estado(d)

    def test_11_rejeita_lista_incompleta(self):
        d=copy.deepcopy(self.data);d['macrolotes'].pop()
        with self.assertRaises(p.EstadoInvalido):p.validar_estado(d)

    def test_12_rejeita_status_inventado(self):
        d=copy.deepcopy(self.data);d['macrolotes'][3]['situacao']='instalado'
        with self.assertRaises(p.EstadoInvalido):p.validar_estado(d)

    def test_13_rejeita_schema_novo(self):
        d=copy.deepcopy(self.data);d['schema']=2
        with self.assertRaises(p.EstadoInvalido):p.validar_estado(d)

    def test_14_nao_executa_codigo_no_plano(self):
        source=ROOT.joinpath('painel_planejamento.py').read_text(encoding='utf8')
        self.assertNotIn('eval(',source)
        self.assertNotIn('exec(',source)

    def test_15_callbacks_motor_preservados(self):
        import hashlib
        current=ast.parse((ROOT/'painel_homologacao.py').read_bytes())
        klass=next(x for x in current.body if isinstance(x,ast.ClassDef) and x.name=='Painel')
        funcs={x.name:x for x in klass.body if isinstance(x,ast.FunctionDef)}
        expected = {'_append': '6f33d2a048e79b14656aa034501dbb5109acc1dc9c1716bd3416689ba6c137f1', '_choose_python': 'f80a19633752d333602de553bf66fd998b3e42026a58027bfaf6d659f42cbad1', '_probe': '9c363b06c13d01163df605fcc55e3f4a7bd563c30726d046f0df05acd2eea806', '_verify_python': '7401837a9c90652dc3828d33b1ccfbdc3e1ba04dcf6e1e3a56fd4568929980b3', '_worker': 'dd95b56ec312e5b67f3b7b76dc245e3fab687650d7c674ee0362038415ec9ee5', '_poll_queue': 'de9830bf937fbde5a00265a11f224cb8b2477b25a683f62ad435c4eb795736c0', '_end_run': '8a3b52613b75c89fbdea1497e121b7763c3628bd346eea61bd0a817c43a30ac5', '_open_result_folder': 'fed4e6d5666bd8349151eea2c6e4432c85033cb36b85974b0aace8115d9fce40', '_copy_result': '2df1ceaa910de533d0465cc73e076d14263a6566d5249faff087ac22c4c83b16'}
        # _start recebeu um bloqueio frozen legitimo: conferir contrato, nao AST rigida.
        start_src=ast.unparse(funcs['_start'])
        self.assertIn('_block_frozen_external',start_src)
        self.assertLess(start_src.index('_block_frozen_external'),start_src.index('self._probe'))
        for name, fingerprint in expected.items():
            with self.subTest(method=name):
                actual_node = funcs[name]
                # V2-B acrescenta somente o gancho de registro ao final da execução.
                # Para auditar o motor anterior, remove-se esse único bloco novo da AST.
                if name == '_worker':
                    # Apenas remover guarda de bloqueio frozen para conferir
                    # que o motor legado permaneceu bytecode/AST equivalente.
                    import copy
                    actual_node=copy.deepcopy(actual_node)
                    blocked=actual_node.body.pop(0)
                    self.assertIsInstance(blocked,ast.If)
                    self.assertIn('frozen',ast.unparse(blocked))
                if name == '_end_run':
                    import copy
                    actual_node=copy.deepcopy(actual_node)
                    expected_pos=next(i for i,node in enumerate(actual_node.body)
                        if isinstance(node,ast.If)
                        and 'history_view' in ast.unparse(node.test))
                    removed=actual_node.body.pop(expected_pos)
                    self.assertIn('import_file',ast.unparse(removed))
                actual=hashlib.sha256(ast.dump(actual_node,include_attributes=False).encode()).hexdigest()
                self.assertEqual(actual,fingerprint)

    def test_16_motor_producao_nao_modificado(self):
        from zipfile import ZipFile
        with ZipFile(ROOT/'insumos'/'CANDIDATO_QA_R1D_PARA_M2_RC2_NAO_INSTALAR.zip') as z:
            self.assertNotIn('banco.py',z.namelist())
            self.assertNotIn('VighnaStudy.spec',z.namelist())

    def test_17_existe_atividade_de_build_na_lista(self):
        self.assertTrue(any('Compilar' in t['nome'] for t in self.data['proximas_atividades']))

    def test_18_os_modulos_nao_importam_codigo_do_vighna(self):
        for mod in ('painel_planejamento.py','painel_homologacao.py'):
            src=(ROOT/mod).read_text(encoding='utf8')
            self.assertNotIn('import banco',src)
            self.assertNotIn('import main',src)

if __name__=='__main__':unittest.main(verbosity=2)
