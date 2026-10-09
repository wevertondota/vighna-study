"""Regressão do piloto cromático da faixa de inventário — Central de Questões.

Executável também em ambientes sem PySide6, exclusivamente para auditar a
composição QSS sem inicializar a interface. A inspeção visual exige Windows.
"""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import re
import sqlite3
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parent
EXPECTED_QSS_SHA_CANON = {
    'claro': '2ceb672c5eafe8b5e733944231dcef4ed3912ab5b8f6206a45a385aa25daf5bd',
    'escuro': '9d236b75d6fd6df45ff2f3b2765e30a73598d1e98c3a2efbeae40cbd48741341',
    'futurista': 'b1dbad5ab9f4315a84a741ef70660b3b245617453cfae450edeca8b8893c9ffd',
}
EXPECTED_VALUES = {
    'claro': ('#FFFFFF','#DBE3ED','#4338CA','#64748B','#E2E8F0'),
    'escuro': ('#121C2D','#334155','#A5B4FC','#94A3B8','#334155'),
    'futurista': ('#121C2D','#334155','#A5B4FC','#94A3B8','#334155'),
}
ROLES = ('inventory_surface','inventory_border','inventory_value_text','inventory_label_text','inventory_divider')
SELECTORS = ('QFrame#questionsInventoryStrip','QLabel#questionsInventoryValue',
             'QLabel#questionsInventoryLabel','QFrame#questionsInventoryDivider')
PROTECTED = {
    'main.py':'d2e4ebd54ae765ec8f11eabd5e6c6e086e3dfd7bb3d441def8c03705515da4fe',
    'foco.py':'8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed',
    'navegacao.py':'2cb3439a580cf867af9870750a82e06777718961dd84819e0705a96838c8b862',
    'jogos.py':'498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286',
    'checkpoint.py':'947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38',
    'versao.py':'49e9d1b5c82bc10c70bd79ca5f494961e3cae3553cd4b70af1565bca661f9ac2',
}

def _load_tema():
    if importlib.util.find_spec('PySide6') is None and 'PySide6' not in sys.modules:
        pkg = types.ModuleType('PySide6')
        pkg.__path__ = []
        widgets = types.ModuleType('PySide6.QtWidgets')
        widgets.QApplication = type('QApplication',(),{})
        sys.modules['PySide6'] = pkg
        sys.modules['PySide6.QtWidgets'] = widgets
    import tema
    return tema


def _canonical_css(stylesheet):
    return re.sub(r'#[0-9A-Fa-f]{3,8}\b', lambda m: m.group(0).lower(), stylesheet)


class CentralQuestoesInventarioPilotoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from ui.design import ALL_TOKENS, get_theme, token_spec, TokenKind
        cls.tema = _load_tema()
        cls.source = (ROOT/'tema.py').read_text(encoding='utf-8')
        cls.tokens = ALL_TOKENS
        cls.get_theme = staticmethod(get_theme)
        cls.token_spec = staticmethod(token_spec)
        cls.TokenKind = TokenKind

    def test_01_contract_count(self):
        self.assertEqual(len(self.tokens),1250)
        self.assertEqual(sum(t.path.startswith('questions_center.') for t in self.tokens),31)

    def test_02_all_tokens_resolvable_in_three_themes(self):
        for theme_name in EXPECTED_VALUES:
            theme=self.get_theme(theme_name)
            self.assertEqual(len(theme.color_references) + len(theme.gradients),len(self.tokens))
            for role in ROLES:
                self.assertEqual(self.token_spec('questions_center.'+role).kind,self.TokenKind.COLOR)

    def test_03_expected_palette(self):
        for theme_name,expected in EXPECTED_VALUES.items():
            theme=self.get_theme(theme_name)
            self.assertEqual(tuple(theme.color('questions_center.'+r).value for r in ROLES),expected)

    def test_04_only_two_rules_per_selector(self):
        for selector in SELECTORS:
            blocks=re.findall(r'(?ms)^\s*'+re.escape(selector)+r'\s*\{(.*?)^\s*\}',self.source)
            self.assertEqual(len(blocks),2,selector)
            for block in blocks:
                self.assertNotRegex(block,r'#[\da-fA-F]{3,8}\b')

    def test_05_each_token_consumed_twice(self):
        for role in ROLES:
            self.assertEqual(self.source.count('{{color:questions_center.'+role+'}}'),2,role)

    def test_06_no_unresolved_markers(self):
        for name in EXPECTED_VALUES:
            qss=getattr(self.tema,'stylesheet_'+name)()
            self.assertNotIn('{{color:',qss,name)
            self.assertNotIn('{{gradient:',qss,name)

    def test_07_claro_full_qss_parity(self):
        self._assert_full_qss_parity('claro')

    def test_08_escuro_full_qss_parity(self):
        self._assert_full_qss_parity('escuro')

    def test_09_futurista_full_qss_parity(self):
        self._assert_full_qss_parity('futurista')

    def _assert_full_qss_parity(self,name):
        qss=getattr(self.tema,'stylesheet_'+name)()
        normalized=_canonical_css(qss)
        self.assertEqual(hashlib.sha256(normalized.encode()).hexdigest(),EXPECTED_QSS_SHA_CANON[name])

    def test_10_no_noncolor_style_changes_in_pilot(self):
        for selector in SELECTORS:
            blocks=re.findall(r'(?ms)^\s*'+re.escape(selector)+r'\s*\{(.*?)^\s*\}',self.source)
            self.assertEqual(len(blocks),2)
            self.assertEqual(re.sub(r'#[0-9A-Fa-f]{3,8}\b|\{\{color:[^}]+\}\}', '<COLOR>', blocks[0]), re.sub(r'#[0-9A-Fa-f]{3,8}\b|\{\{color:[^}]+\}\}', '<COLOR>', blocks[1]))

    def test_11_protected_files_unchanged(self):
        for filename,hash_expected in PROTECTED.items():
            self.assertEqual(hashlib.sha256((ROOT/filename).read_bytes()).hexdigest(),hash_expected,filename)

    def test_12_database_integrity(self):
        db=sqlite3.connect(f'file:{(ROOT/"estudos.db").as_posix()}?mode=ro',uri=True)
        try:
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
        finally:
            db.close()

if __name__=='__main__':
    unittest.main()
