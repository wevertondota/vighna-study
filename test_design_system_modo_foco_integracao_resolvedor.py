import hashlib, re, sqlite3, unittest
from pathlib import Path
import tema
from _design_system_test_helpers import strip_focus_mode_resolver_integration_source
from ui.design import ALL_TOKENS, COMPONENT_TOKEN_COUNT, SEMANTIC_TOKEN_COUNT, TokenKind, get_theme, token_spec
from versao import VIGHNA_BUILD, VIGHNA_SCHEMA, VIGHNA_VERSION
ROOT=Path(__file__).resolve().parent
SOURCE=(ROOT/'tema.py').read_text(encoding='utf-8')
LAYER=tema.ESTILO_MODO_FOCO_INTEGRACAO_RESOLVEDOR
TOKENS=(
'focus_mode.session_bar_surface','focus_mode.session_bar_border','focus_mode.session_bar_status_text',
'focus_mode.session_bar_button_surface','focus_mode.session_bar_button_text','focus_mode.session_bar_button_border',
'focus_mode.session_bar_button_hover_surface','focus_mode.session_bar_button_hover_text','focus_mode.session_bar_button_hover_border')
EXPECTED={
'claro':('#F7F9FC','#E1E6ED','#536173','#FFFFFF','#334155','#CFD8E3','#F6FBFF','#235F98','#9FC7E7'),
'escuro':('#151E2A','#303D4E','#A7B4C3','#162333','#DCE6F0','#33475E','#1C3145','#9BD5FF','#4D89B8'),
'futurista':('#151D28','#354151','#B1BCC9','#232B36','#D1D9E2','#5A6472','#2C3643','#FFFFFF','#7A8594')}
BASE_TEMA='6ef8a246dd5746d6547dbc817bc438cda9cfd4bc63815481f2d6c49bafd95123'
PROTECTED={'main.py':'d2e4ebd54ae765ec8f11eabd5e6c6e086e3dfd7bb3d441def8c03705515da4fe','foco.py':'8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed','navegacao.py':'2cb3439a580cf867af9870750a82e06777718961dd84819e0705a96838c8b862','jogos.py':'498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286','checkpoint.py':'947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38','versao.py':'49e9d1b5c82bc10c70bd79ca5f494961e3cae3553cd4b70af1565bca661f9ac2'}
class FocusIntegrationTests(unittest.TestCase):
 def test_budget(self):
  self.assertEqual((SEMANTIC_TOKEN_COUNT,COMPONENT_TOKEN_COUNT,len(ALL_TOKENS)),(102,1148,1250)); self.assertEqual(sum(t.kind is TokenKind.COLOR for t in ALL_TOKENS),1165); self.assertEqual(sum(t.kind is TokenKind.GRADIENT for t in ALL_TOKENS),85)
  for p in TOKENS:self.assertEqual(token_spec(p).kind,TokenKind.COLOR)
 def test_values(self):
  for theme,vals in EXPECTED.items():
   for p,v in zip(TOKENS,vals):self.assertEqual(get_theme(theme).color(p).value,v)
 def test_exact_contract_consumption(self):
  self.assertEqual(tuple(re.findall(r'\{\{color:([^}]+)\}\}',LAYER)),TOKENS); self.assertNotIn('{{gradient:',LAYER)
 def test_scope(self):
  self.assertIn('QFrame#questionSessionFocusBar QPushButton#subtleButton {',LAYER); self.assertIn('QFrame#questionSessionFocusBar QPushButton#subtleButton:hover {',LAYER); self.assertNotIn('QDialog#questionSolverDialog QPushButton#subtleButton {',LAYER)
 def test_chromatic_only(self):
  self.assertIsNone(re.search(r'#[0-9A-Fa-f]{3,8}\b',LAYER));
  for x in ('border-radius','font-size','font-weight','padding','margin','min-width','max-width','min-height','max-height','letter-spacing'):self.assertNotIn(x,LAYER)
 def test_rendered_values(self):
  for theme,vals in EXPECTED.items():
   q=tema.render_qss(theme,LAYER); self.assertNotIn('{{color:',q); [self.assertIn(v,q) for v in vals]
 def test_final_qss_resolved(self):
  for q in (tema.stylesheet_claro(),tema.stylesheet_escuro(),tema.stylesheet_futurista()):self.assertNotIn('{{color:',q);self.assertNotIn('{{gradient:',q)
 def test_composition_order(self):
  for t in ('claro','escuro','futurista'):self.assertIn(f'render_qss("{t}", ESTILO_CARDS_GLOBAIS_BLOCO_C) + render_qss("{t}", ESTILO_MODO_FOCO_INTEGRACAO_RESOLVEDOR)',SOURCE)
 def test_no_runtime_patch(self):
  main=(ROOT/'main.py').read_text(encoding='utf-8'); foco=(ROOT/'foco.py').read_text(encoding='utf-8'); self.assertEqual(main.count('setObjectName("questionSessionFocusBar")'),1);self.assertEqual(main.count('setObjectName("questionSessionFocusState")'),1);self.assertEqual(main.count('setObjectName("subtleButton")'),66);self.assertEqual(len(re.findall(r'#[0-9A-Fa-f]{3,8}\b',foco)),0);self.assertNotIn('setStyleSheet(',foco)
 def test_rollback(self):self.assertEqual(hashlib.sha256(strip_focus_mode_resolver_integration_source(SOURCE).encode()).hexdigest(),BASE_TEMA)
 def test_protected_and_db(self):
  for f,h in PROTECTED.items():self.assertEqual(hashlib.sha256((ROOT/f).read_bytes()).hexdigest(),h,f)
  self.assertEqual((VIGHNA_VERSION,VIGHNA_BUILD,VIGHNA_SCHEMA),('0.29.59','statistics-my-evolution-tokens-v1',25)); c=sqlite3.connect(ROOT/'estudos.db');self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok');self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[]);c.close()
if __name__=='__main__':unittest.main()
