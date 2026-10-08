from __future__ import annotations

import re


def strip_focus_mode_resolver_integration(tema, theme_name: str, qss: str) -> str:
    """Remove a camada aditiva Foco/Resolvedor de snapshots históricos."""
    if not hasattr(tema, "ESTILO_MODO_FOCO_INTEGRACAO_RESOLVEDOR"):
        return qss
    if theme_name == "futurista":
        final = tema.render_qss("futurista", tema.ESTILO_MODO_FOCO_INTEGRACAO_RESOLVEDOR)
        inherited = tema.render_qss("escuro", tema.ESTILO_MODO_FOCO_INTEGRACAO_RESOLVEDOR)
        if qss.endswith(final):
            qss = qss[:-len(final)]
        elif final in qss:
            qss = qss.replace(final, "", 1)
        if inherited in qss:
            qss = qss.replace(inherited, "", 1)
        return qss
    layer = tema.render_qss(theme_name, tema.ESTILO_MODO_FOCO_INTEGRACAO_RESOLVEDOR)
    if qss.endswith(layer):
        return qss[:-len(layer)]
    return qss.replace(layer, "", 1)


def strip_focus_mode_resolver_integration_source(source: str) -> str:
    """Remove constante e composições da integração Foco/Resolvedor."""
    source = re.sub(
        r'# ============================================================\n'
        r'# Design System — Modo Foco — Integração no Resolvedor\n'
        r'# Camada cromática aditiva da faixa contextual de Foco\.\n'
        r'# Não altera geometria, tipografia, callbacks ou objectNames\.\n'
        r'# ============================================================\n'
        r'ESTILO_MODO_FOCO_INTEGRACAO_RESOLVEDOR = r"""\n.*?\n"""\n\n',
        '', source, count=1, flags=re.S,
    )
    for theme_name in ('claro', 'escuro', 'futurista'):
        source = source.replace(
            f' + render_qss("{theme_name}", ESTILO_MODO_FOCO_INTEGRACAO_RESOLVEDOR)', '', 1
        )
    return source


def strip_cards_global_block_c(tema, theme_name: str, qss: str) -> str:
    """Remove integrações posteriores e a camada Cards globais C de snapshots históricos."""
    qss = strip_focus_mode_resolver_integration(tema, theme_name, qss)
    if not hasattr(tema, "ESTILO_CARDS_GLOBAIS_BLOCO_C"):
        return qss
    if theme_name == "futurista":
        final = tema.render_qss("futurista", tema.ESTILO_CARDS_GLOBAIS_BLOCO_C)
        inherited = tema.render_qss("escuro", tema.ESTILO_CARDS_GLOBAIS_BLOCO_C)
        if qss.endswith(final):
            qss = qss[:-len(final)]
        elif final in qss:
            qss = qss.replace(final, "", 1)
        if inherited in qss:
            qss = qss.replace(inherited, "", 1)
        return qss
    layer = tema.render_qss(theme_name, tema.ESTILO_CARDS_GLOBAIS_BLOCO_C)
    if qss.endswith(layer):
        return qss[:-len(layer)]
    return qss.replace(layer, "", 1)


def strip_cards_global_block_c_source(source: str) -> str:
    """Remove integrações posteriores e a constante/composições do Bloco C."""
    source = strip_focus_mode_resolver_integration_source(source)
    source = re.sub(
        r'# ============================================================\n'
        r'# Design System — Cards globais — Bloco C\n'
        r'# myEvolutionStatCard compartilhado\. Somente shell e cores dos\n'
        r'# textos descendentes; a família myEvolution restante fica intacta\.\n'
        r'# ============================================================\n'
        r'ESTILO_CARDS_GLOBAIS_BLOCO_C = r"""\n.*?\n"""\n\n',
        '', source, count=1, flags=re.S,
    )
    for theme_name in ('claro','escuro','futurista'):
        source = source.replace(
            f' + render_qss("{theme_name}", ESTILO_CARDS_GLOBAIS_BLOCO_C)', '', 1
        )
    return source


def strip_cards_global_block_b(tema, theme_name: str, qss: str) -> str:
    """Remove C e depois apenas a camada Cards globais B de snapshots históricos."""
    qss = strip_cards_global_block_c(tema, theme_name, qss)
    if not hasattr(tema, "ESTILO_CARDS_GLOBAIS_BLOCO_B"):
        return qss
    if theme_name == "futurista":
        final = tema.render_qss("futurista", tema.ESTILO_CARDS_GLOBAIS_BLOCO_B)
        inherited = tema.render_qss("escuro", tema.ESTILO_CARDS_GLOBAIS_BLOCO_B)
        if qss.endswith(final):
            qss = qss[:-len(final)]
        elif final in qss:
            qss = qss.replace(final, "", 1)
        if inherited in qss:
            qss = qss.replace(inherited, "", 1)
        return qss
    layer = tema.render_qss(theme_name, tema.ESTILO_CARDS_GLOBAIS_BLOCO_B)
    if qss.endswith(layer):
        return qss[:-len(layer)]
    return qss.replace(layer, "", 1)


def strip_cards_global_block_a(tema, theme_name: str, qss: str) -> str:
    """Remove as camadas Cards globais posteriores antes do Bloco A em snapshots históricos."""
    qss = strip_cards_global_block_b(tema, theme_name, qss)
    if not hasattr(tema, "ESTILO_CARDS_GLOBAIS_BLOCO_A"):
        return qss
    if theme_name == "futurista":
        final = tema.render_qss("futurista", tema.ESTILO_CARDS_GLOBAIS_BLOCO_A)
        inherited = tema.render_qss("escuro", tema.ESTILO_CARDS_GLOBAIS_BLOCO_A)
        if qss.endswith(final):
            qss = qss[:-len(final)]
        elif final in qss:
            qss = qss.replace(final, "", 1)
        if inherited in qss:
            qss = qss.replace(inherited, "", 1)
        return qss
    layer = tema.render_qss(theme_name, tema.ESTILO_CARDS_GLOBAIS_BLOCO_A)
    if qss.endswith(layer):
        return qss[:-len(layer)]
    return qss.replace(layer, "", 1)


def strip_cards_global_block_b_source(source: str) -> str:
    """Remove C e depois a constante/composições do Bloco B."""
    source = strip_cards_global_block_c_source(source)
    source = re.sub(
        r'# ============================================================\n'
        r'# Design System — Cards globais — Bloco B\n'
        r'# Shell compartilhado studyActionCard\. Somente superfície e borda;\n'
        r'# textos, geometria e comportamento permanecem na cascata histórica\.\n'
        r'# ============================================================\n'
        r'ESTILO_CARDS_GLOBAIS_BLOCO_B = r"""\n.*?\n"""\n\n',
        '', source, count=1, flags=re.S,
    )
    for theme_name in ('claro','escuro','futurista'):
        source = source.replace(
            f' + render_qss("{theme_name}", ESTILO_CARDS_GLOBAIS_BLOCO_B)', '', 1
        )
    return source


def strip_cards_global_block_a_source(source: str) -> str:
    """Remove B e depois a constante/composições do Bloco A para rollbacks históricos."""
    source = strip_cards_global_block_b_source(source)
    source = re.sub(
        r'# ============================================================\n'
        r'# Design System — Cards globais — Bloco A\n'
        r'# Superfícies básicas e métricas\. Camada cromática aditiva,\n'
        r'# escopada aos shells genéricos e aos textos internos dos cards\.\n'
        r'# ============================================================\n'
        r'ESTILO_CARDS_GLOBAIS_BLOCO_A = r"""\n.*?\n"""\n\n',
        '', source, count=1, flags=re.S,
    )
    for theme_name in ('claro','escuro','futurista'):
        source = source.replace(
            f' + render_qss("{theme_name}", ESTILO_CARDS_GLOBAIS_BLOCO_A)', '', 1
        )
    return source
