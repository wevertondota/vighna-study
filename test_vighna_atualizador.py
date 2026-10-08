"""Testes de segurança e transação, sem modificar o banco real do Vighna."""
from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
import zipfile
from contextlib import closing
from pathlib import Path

from vighna_update_engine import (FORMAT, UpdateError, backup_database,
                                  check_database, inspect_package, install_package,
                                  package_usage, recover_incomplete_updates, sha256_bytes,
                                  valid_source_path)

OLD = 'base-build'
NEW = 'updated-build'
VERSION = '0.29.59'
SCHEMA = 25


def make_version(build, schema=SCHEMA):
    return f'VIGHNA_VERSION = "{VERSION}"\nVIGHNA_BUILD = "{build}"\nVIGHNA_SCHEMA = {schema}\n'.encode()


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'program'
        self.root.mkdir()
        (self.root / 'versao.py').write_bytes(make_version(OLD))
        (self.root / 'main.py').write_text('x = 3\n')
        (self.root / 'VighnaStudy.spec').write_text('fake_spec = 1\n')
        install = self.root / 'dist' / 'SistemaEstudos'
        install.mkdir(parents=True)
        (install / 'VighnaStudy.exe').write_text('original executable')
        self.db = self.root / 'estudos.db'
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute('CREATE TABLE respostas (id INTEGER PRIMARY KEY, valor TEXT)')
            db.executemany('INSERT INTO respostas(valor) VALUES (?)', [('certa',), ('errada',)])
        self.package = Path(self.tmp.name) / 'update.zip'

    def query(self, sql, db=None):
        with closing(sqlite3.connect(db or self.db)) as connection:
            return connection.execute(sql).fetchall()

    def create_package(self, *, build=NEW, schema=SCHEMA, data=None, change=None):
        data = data or {'versao.py':make_version(build), 'main.py':b'x = 4\n'}
        manifest = {'format':FORMAT,'base_version':VERSION,'base_build':OLD,
                    'target_version':VERSION,'target_build':build,'schema':schema,
                    'description':'teste isolado', 'files':{k:sha256_bytes(v) for k,v in data.items()}}
        if change:
            change(manifest)
        with zipfile.ZipFile(self.package,'w') as zipfile_out:
            zipfile_out.writestr('manifest.json', json.dumps(manifest))
            for k,v in data.items():
                zipfile_out.writestr(k,v)
        return self.package

    def fake_build(self, work, output, report):
        output.mkdir(parents=True)
        (output / 'VighnaStudy.exe').write_text('updated executable')

    def test_valid_package_and_install_preserves_data(self):
        self.create_package()
        m = inspect_package(self.package,self.root)
        self.assertEqual(m['target_build'],NEW)
        result = install_package(self.package,self.root,python_exe='python',runner=self.fake_build)
        self.assertEqual((self.root/'dist'/'SistemaEstudos'/'VighnaStudy.exe').read_text(),'updated executable')
        self.assertEqual((self.root/'main.py').read_text(),'x = 4\n')
        self.assertEqual(self.query('SELECT valor FROM respostas ORDER BY id'),[('certa',),('errada',)])
        self.assertEqual(self.query('SELECT COUNT(*) FROM respostas', result['backup']+'/estudos.db')[0],(2,))
        self.assertEqual((Path(result['backup'])/'anterior_executavel'/'VighnaStudy.exe').read_text(),'original executable')

    def test_block_database_in_package(self):
        self.create_package(data={'versao.py':make_version(NEW),'estudos.db':b'WRONG'})
        with self.assertRaises(UpdateError):inspect_package(self.package,self.root)

    def test_block_traversal(self):
        self.create_package(data={'versao.py':make_version(NEW),'../run.py':b'print(1)'})
        with self.assertRaises(UpdateError):inspect_package(self.package,self.root)

    def test_source_path_accepts_only_python_modules(self):
        self.assertTrue(valid_source_path('ui/design/tokens.py'))
        self.assertTrue(valid_source_path('statistics_core/metrics.py'))
        for path in ('ui/not-a-module.py', 'ui/package.py/child.py',
                     'ui/.hidden.py', 'unknown/module.py'):
            with self.subTest(path=path):
                self.assertFalse(valid_source_path(path))

    def test_block_schema_change(self):
        self.create_package(schema=SCHEMA+1,data={'versao.py':make_version(NEW,SCHEMA+1)})
        with self.assertRaises(UpdateError):inspect_package(self.package,self.root)

    def test_block_incompatible_baseline(self):
        self.create_package(change=lambda m: m.update(base_build='other'))
        with self.assertRaises(UpdateError):inspect_package(self.package,self.root)

    def test_block_bad_hash(self):
        self.create_package(change=lambda m: m['files'].update({'main.py':'0'*64}))
        with self.assertRaises(UpdateError):inspect_package(self.package,self.root)

    def test_block_version_mismatch(self):
        self.create_package(change=lambda m: m.update(target_build='unexpected'))
        with self.assertRaises(UpdateError):inspect_package(self.package,self.root)

    def test_package_usage_distinguishes_new_installed_failed_and_current(self):
        self.create_package()
        usage = package_usage(self.package, self.root)
        self.assertEqual(usage['state'], 'new')
        digest = usage['sha256']
        history = self.root / 'backups' / 'atualizacoes' / 'historico.jsonl'
        history.parent.mkdir(parents=True)

        installed = [
            {'id':'run-installed', 'status':'started', 'package':self.package.name,
             'sha256':digest, 'to':NEW},
            {'id':'run-installed', 'status':'installed', 'package':self.package.name,
             'sha256':digest, 'to':NEW},
        ]
        history.write_text('\n'.join(json.dumps(item) for item in installed) + '\n')
        self.assertEqual(package_usage(self.package, self.root)['state'], 'installed_exact')

        failed = {'id':'run-failed', 'status':'failed', 'package':self.package.name,
                  'sha256':digest, 'to':NEW}
        history.write_text(json.dumps(failed) + '\n')
        self.assertEqual(package_usage(self.package, self.root)['state'], 'failed')

        history.unlink()
        (self.root / 'versao.py').write_bytes(make_version(NEW))
        self.assertEqual(package_usage(self.package, self.root)['state'], 'installed_current')

    def test_compile_failure_leaves_original_program_and_db(self):
        self.create_package()
        def broken(*_):raise RuntimeError('compilation failed')
        with self.assertRaises(UpdateError):
            install_package(self.package,self.root,python_exe='python',runner=broken)
        self.assertEqual((self.root/'main.py').read_text(),'x = 3\n')
        self.assertEqual((self.root/'dist'/'SistemaEstudos'/'VighnaStudy.exe').read_text(),'original executable')
        self.assertEqual(self.query('SELECT COUNT(*) FROM respostas')[0],(2,))

    def test_invalid_python_leaves_original(self):
        self.create_package(data={'versao.py':make_version(NEW),'main.py':b'if = = invalid'})
        with self.assertRaises(UpdateError):
            install_package(self.package,self.root,python_exe='python',runner=self.fake_build)
        self.assertEqual((self.root/'main.py').read_text(),'x = 3\n')

    def test_recover_interrupted_swap(self):
        import shutil
        base = self.root / 'backups' / 'atualizacoes' / 'interrupted'
        saved = base / 'sources'
        saved.mkdir(parents=True)
        shutil.copy2(self.root / 'main.py', saved / 'main.py')
        (self.root / 'main.py').write_text('x = 999\n')
        target = self.root / 'dist' / 'SistemaEstudos'
        target.rename(base / 'anterior_executavel')
        target.mkdir()
        (target / 'VighnaStudy.exe').write_text('partial installation')
        (base / 'state.json').write_text(json.dumps({'phase':'committing','sources':{'main.py':True}}))
        self.assertEqual(recover_incomplete_updates(self.root), ['interrupted'])
        self.assertEqual((self.root/'main.py').read_text(), 'x = 3\n')
        self.assertEqual((target/'VighnaStudy.exe').read_text(), 'original executable')
        self.assertEqual(recover_incomplete_updates(self.root), [])

    def test_failure_after_swap_rolls_back_source_and_exe(self):
        from unittest.mock import patch
        import vighna_update_engine as engine
        self.create_package()
        calls = [0]
        check = engine.check_database
        def fail_last(path):
            calls[0] += 1
            if calls[0] == 4:
                raise UpdateError('injected after swap')
            return check(path)
        with patch.object(engine, 'check_database', side_effect=fail_last):
            with self.assertRaises(UpdateError):
                install_package(self.package,self.root,python_exe='python',runner=self.fake_build)
        self.assertEqual((self.root/'main.py').read_text(),'x = 3\n')
        self.assertEqual((self.root/'versao.py').read_bytes(),make_version(OLD))
        self.assertEqual((self.root/'dist'/'SistemaEstudos'/'VighnaStudy.exe').read_text(),
                         'original executable')
        self.assertEqual(self.query('SELECT COUNT(*) FROM respostas')[0],(2,))

    def test_backup_is_consistent(self):
        backup = Path(self.tmp.name) / 'b.db'
        backup_database(self.db,backup)
        check_database(backup)
        self.assertEqual(self.query('SELECT COUNT(*) FROM respostas', backup)[0][0],2)


if __name__ == '__main__':unittest.main(verbosity=2)
