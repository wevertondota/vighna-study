# -*- coding: utf-8 -*-
"""V2-B — persistência, importação, deduplicação, segurança e regressões."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from contextlib import closing
import shutil
import sqlite3
import tempfile
import unittest
import zipfile

from painel_historico import HistoryStore, HistoryError, inspect_evidence, category_for, sha_file


def fixture(path, *, qt='PASSOU', sqlite='PASSOU', build=None, qt_checks=33):
    summary={'homologador':'V1.1','modo':'testes' if build is None else 'build',
             'ambiente':'Windows','python':'3.13.15','instalacao_autorizada':False,
             'testes':{'preflight':{'status':'PASSOU'},
                       'atualizacao_sintetica':{'status':sqlite,'log':'tests.log'},
                       'qt_windows_100':{'status':qt}},
             'resultados':{'falhas':int(qt=='FALHOU')+int(sqlite=='FALHOU'),
                           'bloqueados':int(qt=='BLOQUEADO')+int(sqlite=='BLOQUEADO')}}
    if build is not None:
        summary['testes']['pyinstaller']={'status':build}
    files={'RESUMO_HOMOLOGACAO.json':json.dumps(summary).encode('utf-8'),
           'tests.log':b'Ran 82 tests in 1.200s\n\nOK\n',
           'qt_windows_100/qt_gate_resultados.json':json.dumps({
               'testes':qt_checks,'aprovados':qt_checks if qt=='PASSOU' else 0}).encode('utf-8')}
    hashes={k:hashlib.sha256(v).hexdigest() for k,v in files.items()}
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for k,v in files.items(): z.writestr(k,v)
        z.writestr('MANIFESTO_SHA256.json',json.dumps(hashes))
    return path


class HistoryV2BTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='qa_historico_')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.store=HistoryStore(self.root/'indice')
        self.file=fixture(self.root/'resultado_a.zip')

    def test_01_validates_realistic_zip(self):
        data=inspect_evidence(self.file)
        self.assertEqual(data['aprovados'],3)
        self.assertEqual(data['falhas'],0)

    def test_02_creates_persistent_db_outside_evidence(self):
        self.assertTrue(self.store.db_path.is_file())
        self.assertNotEqual(self.store.root,self.store.evidence)

    def test_03_import_and_read(self):
        pk,created=self.store.import_zip(self.file)
        self.assertTrue(created)
        self.assertEqual(len(self.store.steps_for(pk)),3)

    def test_04_deduplicate_by_content_not_filename(self):
        a,_=self.store.import_zip(self.file)
        copy=self.root/'outro_nome.zip'
        shutil.copy2(self.file,copy)
        b,created=self.store.import_zip(copy)
        self.assertEqual((a,created),(b,False))
        self.assertEqual(len(self.store.list_runs()),1)

    def test_05_restart_without_losing_history(self):
        pk,_=self.store.import_zip(self.file)
        new=HistoryStore(self.root/'indice')
        self.assertEqual(new.list_runs()[0]['id'],pk)
        self.assertTrue(new.evidence_path(pk).exists())

    def test_06_category_filter(self):
        self.store.import_zip(self.file)
        self.assertEqual(len(self.store.list_runs(category='Qt')),1)
        self.assertEqual(len(self.store.list_runs(category='Segurança')),0)

    def test_07_status_filter(self):
        self.store.import_zip(self.file)
        self.store.import_zip(fixture(self.root/'resultado_b.zip',qt='FALHOU'))
        self.assertEqual(len(self.store.list_runs(status='Com falhas')),1)
        self.assertEqual(len(self.store.list_runs(status='Aprovados')),1)

    def test_08_blocked_is_not_approved(self):
        self.store.import_zip(fixture(self.root/'blocked.zip',qt='BLOQUEADO'))
        self.assertEqual(len(self.store.list_runs(status='Bloqueados')),1)
        self.assertEqual(len(self.store.list_runs(status='Aprovados')),0)

    def test_09_filename_search(self):
        self.store.import_zip(self.file)
        self.assertEqual(len(self.store.list_runs(query='resultado_a')),1)
        self.assertEqual(len(self.store.list_runs(query='qualquercoisa')),0)

    def test_10_comparison_detects_regression(self):
        a,_=self.store.import_zip(self.file)
        b,_=self.store.import_zip(fixture(self.root/'fail.zip',qt='FALHOU'))
        comparison=self.store.compare(a,b)
        self.assertIn('qt_windows_100',comparison['regressoes'])

    def test_11_comparison_detects_improvement(self):
        a,_=self.store.import_zip(fixture(self.root/'fail.zip',qt='FALHOU'))
        b,_=self.store.import_zip(self.file)
        self.assertIn('qt_windows_100',self.store.compare(a,b)['melhorias'])

    def test_12_comparison_fails_same_id(self):
        a,_=self.store.import_zip(self.file)
        with self.assertRaises(HistoryError):self.store.compare(a,a)

    def test_13_comparison_detects_check_count(self):
        a,_=self.store.import_zip(self.file)
        b,_=self.store.import_zip(fixture(self.root/'more.zip',qt_checks=34))
        self.assertIn('qt_windows_100',[s['etapa'] for s in self.store.compare(a,b)['mudancas']])

    def test_14_export_with_index_and_evidence(self):
        self.store.import_zip(self.file)
        target=self.root/'historico_exportado.zip'
        self.store.export_backup(target)
        with zipfile.ZipFile(target) as z:
            self.assertIsNone(z.testzip())
            self.assertIn('historico_v2b.sqlite3',z.namelist())
            self.assertEqual(len([n for n in z.namelist() if n.startswith('evidencias/')]),1)

    def test_15_export_rejects_overwrite(self):
        target=self.root/'existing.zip'
        target.write_bytes(b'SENTINELA')
        with self.assertRaises(HistoryError):self.store.export_backup(target)
        self.assertEqual(target.read_bytes(),b'SENTINELA')

    def test_16_export_rejects_inside_store(self):
        with self.assertRaises(HistoryError):self.store.export_backup(self.store.root/'interno.zip')

    def test_17_immutable_evidence_verified(self):
        pk,_=self.store.import_zip(self.file)
        self.store.evidence_path(pk).write_bytes(b'tampered')
        with self.assertRaises(HistoryError):self.store.evidence_path(pk)

    def test_18_tampered_member_rejected(self):
        tampered=self.root/'tamper.zip'
        with zipfile.ZipFile(self.file) as z:
            names={x:z.read(x) for x in z.namelist()}
        names['tests.log']=b'alterado'
        with zipfile.ZipFile(tampered,'w') as z:
            for n,v in names.items():z.writestr(n,v)
        with self.assertRaises(HistoryError):self.store.import_zip(tampered)
        self.assertEqual(self.store.list_runs(),[])

    def test_19_missing_summary_rejected(self):
        file=self.root/'wrong.zip'
        with zipfile.ZipFile(file,'w') as z:z.writestr('outro.txt',b'a')
        with self.assertRaises(HistoryError):self.store.import_zip(file)

    def test_20_invalid_json_rejected(self):
        file=self.root/'invalid.zip'
        with zipfile.ZipFile(file,'w') as z:
            z.writestr('RESUMO_HOMOLOGACAO.json',b'{invalid')
            z.writestr('MANIFESTO_SHA256.json',b'{}')
        with self.assertRaises(HistoryError):self.store.import_zip(file)

    def test_21_duplicate_archive_names_rejected(self):
        file=self.root/'duplicates.zip'
        with zipfile.ZipFile(file,'w') as z:
            z.writestr('RESUMO_HOMOLOGACAO.json',b'{}')
            z.writestr('RESUMO_HOMOLOGACAO.json',b'{}')
        with self.assertRaises(HistoryError):self.store.import_zip(file)

    def test_22_no_personal_db_access(self):
        self.store.import_zip(self.file)
        with closing(sqlite3.connect(self.store.db_path)) as c:
            names={row[0] for row in c.execute('SELECT name FROM sqlite_master WHERE type="table"')}
        self.assertIn('runs',names)
        self.assertNotIn('questoes',names)

    def test_23_export_valid_index(self):
        self.store.import_zip(self.file)
        target=self.store.export_backup(self.root/'archive.zip')
        with zipfile.ZipFile(target) as z:
            f=self.root/'restaurado.sqlite3';f.write_bytes(z.read('historico_v2b.sqlite3'))
        with closing(sqlite3.connect(f)) as c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM runs').fetchone()[0],1)

    def test_24_import_from_actual_user_evidence_when_available(self):
        file=Path('/mnt/data/RESULTADOS_HOMOLOGACAO_WINDOWS_20261012_211051_499355.zip')
        if not file.exists():self.skipTest('Somente laboratório com evidência real')
        pk,new=self.store.import_zip(file)
        self.assertTrue(new)
        s=self.store.steps_for(pk)
        counts={x['step_key']:x['checks'] for x in s}
        self.assertEqual(counts['atualizacao_sintetica'],82)
        self.assertEqual(counts['guardas_de_seguranca'],19)
        self.assertEqual(counts['qt_windows_150'],33)


if __name__=='__main__':unittest.main(verbosity=2)
