"""Regressões da Etapa 3E-B2b1: escopo, cascata, timer e checkpoint recursivo."""
from __future__ import annotations

import ast
from datetime import datetime, timedelta
import hashlib
from pathlib import Path
import re
from types import SimpleNamespace
import tempfile
import unittest
from _design_system_test_helpers import strip_cards_global_block_a
from unittest.mock import Mock, patch
import zipfile

import checkpoint
import tema

# O baseline estrutural acompanha as migrações aprovadas; no Passo 4, a única
# mudança externa a este contrato é o desagrupamento pause/game, provado em teste próprio.
from ui.design import ALL_TOKENS, get_theme

ROOT = Path(__file__).resolve().parent
BASELINE = {
    'claro': '1bffe9a506a2e8ffaa3366621d12fb1ddafb8b2b7c50e9271582854d606837a2',
    'escuro': '8067e89e17ca82728a2a5369eb47fa6700bfb1b93442b60b9c6f8ddf9a4168f7',
    'futurista': '54bb52dbb8cb3f8d43b114ff1813e6886de28305ca3d32d8d5cba36c09cb7885',
}
NAV_RULE = re.compile(r'QDialog#questionSolverDialog QPushButton#subtleButton\[sessionNavigation="true"\](?::hover)?\s*\{[^{}]*\}', re.S)
QUEUE_DETAIL_RULE = re.compile(r'QDialog#questionSolverDialog QLabel#questionSessionSummaryDetail\s*\{[^{}]*\}', re.S)
SUMMARY_DIALOG_RULE = re.compile(r'QDialog#questionSessionSummaryDialog(?:\s+[^\{]+)?\s*\{[^{}]*\}', re.S)
KEYS = ('navigation_surface', 'navigation_text', 'navigation_border',
        'navigation_hover_surface', 'navigation_hover_text', 'navigation_hover_border',
        'timer_surface', 'timer_text', 'timer_border')
VALUES = {
    'claro': ('#FFFFFF', '#334155', '#CFD8E3', '#F6FBFF', '#235F98', '#9FC7E7', '#F5F3FF', '#6D28D9', '#C4B5FD'),
    'escuro': ('#162333', '#DCE6F0', '#33475E', '#1C3145', '#9BD5FF', '#4D89B8', '#2E1065', '#DDD6FE', '#7C3AED'),
    'futurista': ('#232B36', '#D1D9E2', '#5A6472', '#2C3643', '#FFFFFF', '#7A8594', '#152A46', '#9EEEFF', '#42CAE9'),
}



def strip_dashboard_block_a(theme_name, qss):
    # Bloco F é posterior a este contrato histórico; retire-o primeiro.
    if theme_name == "futurista":
        qss = qss.replace(tema.render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_H), "", 1)
        qss = qss.replace(tema.render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_H), "", 1)
    else:
        qss = qss.replace(tema.render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_H), "", 1)
    if theme_name == "futurista":
        qss = qss.replace(tema.render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_G), "", 1)
        qss = qss.replace(tema.render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_G), "", 1)
    else:
        qss = qss.replace(tema.render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_G), "", 1)
    if theme_name == "futurista":
        qss = qss.replace(tema.render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_F), "", 1)
        qss = qss.replace(tema.render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_F), "", 1)
    else:
        qss = qss.replace(tema.render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_F), "", 1)
    # Bloco E é posterior a este contrato histórico; retire-o em seguida.
    if theme_name == "futurista":
        qss = qss.replace(tema.render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_E), "", 1)
        qss = qss.replace(tema.render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_E), "", 1)
    else:
        qss = qss.replace(tema.render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_E), "", 1)
    # Bloco D é posterior a este contrato histórico; retire-o em seguida.
    if theme_name == "futurista":
        qss = qss.replace(tema.render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_D), "", 1)
        qss = qss.replace(tema.render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_D), "", 1)
    else:
        qss = qss.replace(tema.render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_D), "", 1)
    # Bloco C é posterior a este contrato histórico; retire-o antes dos blocos B/A.
    if theme_name == "futurista":
        qss = qss.replace(tema.render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_C), "", 1)
        qss = qss.replace(tema.render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_C), "", 1)
    else:
        qss = qss.replace(tema.render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_C), "", 1)
    # Bloco B é posterior a este contrato histórico; retire-o antes do Bloco A.
    if theme_name == "futurista":
        qss = qss.replace(
            tema.render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_B_ESCURO), "", 1
        )
        qss = qss.replace(
            tema.render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_B_FUTURISTA), "", 1
        )
    else:
        bloco_b = (
            tema.ESTILO_DASHBOARD_BLOCO_B_CLARO
            if theme_name == "claro"
            else tema.ESTILO_DASHBOARD_BLOCO_B_ESCURO
        )
        qss = qss.replace(tema.render_qss(theme_name, bloco_b), "", 1)
    if theme_name == "futurista":
        qss = qss.replace(
            tema.render_qss("escuro", tema.ESTILO_DASHBOARD_SHELL_ESCURO), "", 1
        )
        qss = qss.replace(
            tema.render_qss("futurista", tema.ESTILO_DASHBOARD_SHELL_FUTURISTA), "", 1
        )
        return qss
    constant = (
        tema.ESTILO_DASHBOARD_SHELL_CLARO
        if theme_name == "claro"
        else tema.ESTILO_DASHBOARD_SHELL_ESCURO
    )
    return qss.replace(tema.render_qss(theme_name, constant), "", 1)

def canonical(qss):
    return re.sub(r'\s+', ' ', re.sub(r'#[0-9A-Fa-f]{3,8}\b', lambda m: m[0].upper(), qss)).strip()



def strip_navigation_search_layer(theme_name: str, qss: str) -> str:
    qss = strip_cards_global_block_a(tema, theme_name, qss)
    """Remove apenas a camada aditiva da Busca global para snapshots históricos."""
    # Remove primeiro a camada posterior de Retornos ao Dashboard, quando presente.
    if hasattr(tema, "ESTILO_NAVEGACAO_RETORNOS_DASHBOARD"):
        if theme_name == "futurista":
            final_back = tema.render_qss("futurista", tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
            inherited_back = tema.render_qss("escuro", tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
            if qss.endswith(final_back):
                qss = qss[:-len(final_back)]
            if inherited_back in qss:
                qss = qss.replace(inherited_back, "", 1)
        else:
            back_layer = tema.render_qss(theme_name, tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
            if qss.endswith(back_layer):
                qss = qss[:-len(back_layer)]
            else:
                qss = qss.replace(back_layer, "", 1)
    if theme_name == "futurista":
        final = tema.render_qss("futurista", tema.ESTILO_NAVEGACAO_BUSCA_GLOBAL)
        inherited = tema.render_qss("escuro", tema.ESTILO_NAVEGACAO_BUSCA_GLOBAL)
        if qss.endswith(final):
            qss = qss[:-len(final)]
        if inherited in qss:
            qss = qss.replace(inherited, "", 1)
        return qss
    layer = tema.render_qss(theme_name, tema.ESTILO_NAVEGACAO_BUSCA_GLOBAL)
    if qss.endswith(layer):
        return qss[:-len(layer)]
    return qss.replace(layer, "", 1)

class SessionNavigationTimerTests(unittest.TestCase):
    def test_exact_nine_tokens_and_values(self):
        self.assertEqual(len(ALL_TOKENS), 1250)
        for name, values in VALUES.items():
            for key, value in zip(KEYS, values):
                self.assertEqual(get_theme(name).color('session.' + key).value, value)

    def test_all_unrelated_rules_and_cascade_match_original_hash(self):
        for name, original_hash in BASELINE.items():
            qss = getattr(tema, 'stylesheet_' + name)()
            qss = strip_navigation_search_layer(name, qss)
            qss = strip_dashboard_block_a(name, qss)
            rules = NAV_RULE.findall(qss)
            self.assertEqual(len(rules), 4 if name == 'futurista' else 2)
            original = NAV_RULE.sub('', qss)
            original = QUEUE_DETAIL_RULE.sub('', original)
            original = SUMMARY_DIALOG_RULE.sub('', original)
            self.assertEqual(hashlib.sha256(canonical(original).encode()).hexdigest(), original_hash)
        self.assertTrue(tema.stylesheet_futurista().startswith(tema.stylesheet_escuro()))

    def test_navigation_property_is_assigned_only_to_dashboard(self):
        source = (ROOT / 'main.py').read_text(encoding='utf-8')
        self.assertEqual(source.count('setProperty("sessionNavigation", True)'), 1)
        self.assertIn('self.botao_dashboard.setProperty("sessionNavigation", True)', source)
        self.assertNotIn('sessionNavigation', (ROOT / 'foco.py').read_text(encoding='utf-8'))

    def test_checkpoint_includes_current_design_and_future_nested_ui(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in checkpoint.FONTES_NUCLEO_ATUAL:
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text('# fixture\n')
            expected = []
            for source in (ROOT / 'ui').rglob('*.py'):
                if '__pycache__' in source.parts:
                    continue
                relative = source.relative_to(ROOT)
                dest = root / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(source.read_bytes())
                expected.append(relative.as_posix())
            future = root / 'ui/future/nested/widget.py'
            future.parent.mkdir(parents=True)
            future.write_text('# future\n')
            expected.append('ui/future/nested/widget.py')
            for name in ('layout.ui', 'resources.qrc', 'config.toml'):
                resource = future.parent / name
                resource.write_text('# future resource\n')
                expected.append(resource.relative_to(root).as_posix())
            with patch.object(checkpoint, 'localizar_pasta_projeto', return_value=root):
                result = checkpoint.gerar_checkpoint('teste-recursivo')
            with zipfile.ZipFile(result['caminho']) as archive:
                self.assertTrue(set(expected) <= set(archive.namelist()))
            self.assertTrue(checkpoint.inspecionar_checkpoint(result['caminho'])['valido'])

    def test_timer_elapsed_countdown_and_expiration(self):
        tree = ast.parse((ROOT / 'main.py').read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'JanelaResolverQuestoes')
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'atualizar_relogio_simulado')
        now = datetime(2026, 10, 6, 12, 0, 0)
        clock = Mock()
        clock.now.return_value = now
        ns = {'datetime': clock}
        exec(compile(ast.Module(body=[method], type_ignores=[]), '<timer>', 'exec'), ns)
        for mode, start, limit, done, text, expired in (
            (False, now, 1, False, None, False),
            (True, None, 1, False, None, False),
            (True, now - timedelta(seconds=3661), 0, False, '⏱ 01:01:01', False),
            (True, now - timedelta(seconds=10), 1, False, '⏱ 00:00:50', False),
            (True, now - timedelta(seconds=61), 1, False, '⏱ 00:00:00', True),
            (True, now - timedelta(seconds=61), 1, True, '⏱ 00:00:00', False),
        ):
            state = SimpleNamespace(modo_simulado=mode, inicio_simulado=start,
                                    tempo_limite_minutos=limit, finalizada=done,
                                    simulado_relogio=Mock(), timer_simulado=Mock(), finalizar=Mock())
            ns[method.name](state)
            if text is None:
                state.simulado_relogio.setText.assert_not_called()
            else:
                state.simulado_relogio.setText.assert_called_once_with(text)
            if expired:
                state.timer_simulado.stop.assert_called_once()
                state.finalizar.assert_called_once_with(True, 'Tempo esgotado')
            else:
                state.finalizar.assert_not_called()


if __name__ == '__main__':
    unittest.main()
