import hashlib
import re
import sqlite3
import unittest
from _design_system_test_helpers import strip_cards_global_block_a
from pathlib import Path

import tema
from ui.design import (
    ALL_TOKENS,
    COMPONENT_TOKEN_COUNT,
    SEMANTIC_TOKEN_COUNT,
    TokenKind,
    get_theme,
    render_qss,
    token_spec,
)

ROOT = Path(__file__).resolve().parent
TEMA_SOURCE = (ROOT / "tema.py").read_text(encoding="utf-8")
MAIN_SOURCE = (ROOT / "main.py").read_text(encoding="utf-8")

DASHBOARD_COLOR_TOKENS = (
    "dashboard.canvas",
    "dashboard.title_text",
    "dashboard.subtitle_text",
    "dashboard.topbar_surface",
    "dashboard.topbar_border",
    "dashboard.profile_bar_surface",
    "dashboard.profile_bar_border",
    "dashboard.profile_label_text",
    "dashboard.profile_input_surface",
    "dashboard.profile_input_text",
    "dashboard.profile_input_border",
    "dashboard.profile_input_hover_surface",
    "dashboard.profile_input_hover_border",
    "dashboard.search_surface",
    "dashboard.search_text",
    "dashboard.search_border",
    "dashboard.search_hover_surface",
    "dashboard.search_hover_text",
    "dashboard.search_hover_border",
    "dashboard.nav_surface",
    "dashboard.nav_text",
    "dashboard.nav_border",
    "dashboard.nav_hover_surface",
    "dashboard.nav_hover_text",
    "dashboard.nav_hover_border",
    "dashboard.nav_pressed_surface",
    "dashboard.nav_pressed_border",
    "dashboard.secondary_surface",
    "dashboard.secondary_text",
    "dashboard.secondary_border",
    "dashboard.secondary_hover_surface",
    "dashboard.secondary_hover_text",
    "dashboard.secondary_hover_border",
    "dashboard.accent_surface",
    "dashboard.accent_border",
    "dashboard.accent_hover_surface",
    "dashboard.accent_hover_border",
    "dashboard.accent_pressed_surface",
)
DASHBOARD_GRADIENT_TOKENS = (
    "dashboard.topbar_gradient",
    "dashboard.nav_gradient",
    "dashboard.nav_hover_gradient",
)

EXPECTED_COLORS = {
    "claro": {
        "dashboard.canvas": "#EBF2FA",
        "dashboard.title_text": "#10233F",
        "dashboard.subtitle_text": "#738196",
        "dashboard.topbar_surface": "#FFFFFF",
        "dashboard.topbar_border": "#E2E8F0",
        "dashboard.profile_bar_surface": "#FFFFFF",
        "dashboard.profile_bar_border": "#DCE3EE",
        "dashboard.profile_label_text": "#315C8A",
        "dashboard.profile_input_surface": "#FFFFFF",
        "dashboard.profile_input_text": "#153453",
        "dashboard.profile_input_border": "#B8CEE5",
        "dashboard.profile_input_hover_surface": "#FBFDFF",
        "dashboard.profile_input_hover_border": "#6EA5DD",
        "dashboard.search_surface": "#F7F9FC",
        "dashboard.search_text": "#607086",
        "dashboard.search_border": "#D8E2EE",
        "dashboard.search_hover_surface": "#EEF5FF",
        "dashboard.search_hover_text": "#285F9D",
        "dashboard.search_hover_border": "#B9D1EC",
        "dashboard.nav_surface": "#FFFFFF",
        "dashboard.nav_text": "#2D3748",
        "dashboard.nav_border": "#A0AEC0",
        "dashboard.nav_hover_surface": "#EDF2F7",
        "dashboard.nav_hover_text": "#1A202C",
        "dashboard.nav_hover_border": "#A0AEC0",
        "dashboard.nav_pressed_surface": "#FFFFFF",
        "dashboard.nav_pressed_border": "#A0AEC0",
        "dashboard.secondary_surface": "#FFFFFF",
        "dashboard.secondary_text": "#2D3748",
        "dashboard.secondary_border": "#A0AEC0",
        "dashboard.secondary_hover_surface": "#EDF2F7",
        "dashboard.secondary_hover_text": "#1A202C",
        "dashboard.secondary_hover_border": "#A0AEC0",
        "dashboard.accent_surface": "transparent",
        "dashboard.accent_border": "#A0AEC0",
        "dashboard.accent_hover_surface": "#EDF2F7",
        "dashboard.accent_hover_border": "#A0AEC0",
        "dashboard.accent_pressed_surface": "transparent",
    },
    "escuro": {
        "dashboard.canvas": "#0E1623",
        "dashboard.title_text": "#F1F6FB",
        "dashboard.subtitle_text": "#8FA1B5",
        "dashboard.topbar_surface": "#151F2D",
        "dashboard.topbar_border": "#2D4054",
        "dashboard.profile_bar_surface": "#111B28",
        "dashboard.profile_bar_border": "#30445A",
        "dashboard.profile_label_text": "#F8FAFC",
        "dashboard.profile_input_surface": "#172434",
        "dashboard.profile_input_text": "#EDF1F7",
        "dashboard.profile_input_border": "#40536A",
        "dashboard.profile_input_hover_surface": "#172434",
        "dashboard.profile_input_hover_border": "#8879F3",
        "dashboard.search_surface": "#111B28",
        "dashboard.search_text": "#9EB0C3",
        "dashboard.search_border": "#30445A",
        "dashboard.search_hover_surface": "#17263A",
        "dashboard.search_hover_text": "#CCE3FB",
        "dashboard.search_hover_border": "#486887",
        "dashboard.nav_surface": "#176B82",
        "dashboard.nav_text": "#EEFCFF",
        "dashboard.nav_border": "#2D91A7",
        "dashboard.nav_hover_surface": "#1B7C95",
        "dashboard.nav_hover_text": "#FFFFFF",
        "dashboard.nav_hover_border": "#43ABC0",
        "dashboard.nav_pressed_surface": "#14596D",
        "dashboard.nav_pressed_border": "#287B90",
        "dashboard.secondary_surface": "#162333",
        "dashboard.secondary_text": "#DCE6F0",
        "dashboard.secondary_border": "#33475E",
        "dashboard.secondary_hover_surface": "#1C3145",
        "dashboard.secondary_hover_text": "#9BD5FF",
        "dashboard.secondary_hover_border": "#4D89B8",
        "dashboard.accent_surface": "#416AB7",
        "dashboard.accent_border": "#4C7BCF",
        "dashboard.accent_hover_surface": "#355BA3",
        "dashboard.accent_hover_border": "#426EC4",
        "dashboard.accent_pressed_surface": "#416AB7",
    },
    "futurista": {
        "dashboard.canvas": "#0B111D",
        "dashboard.title_text": "#F5F7FB",
        "dashboard.subtitle_text": "#B4BECA",
        "dashboard.topbar_surface": "#0F1622",
        "dashboard.topbar_border": "#1E2634",
        "dashboard.profile_bar_surface": "#111925",
        "dashboard.profile_bar_border": "#313948",
        "dashboard.profile_label_text": "#BDC6D1",
        "dashboard.profile_input_surface": "#202935",
        "dashboard.profile_input_text": "#F2F5F9",
        "dashboard.profile_input_border": "#4A5362",
        "dashboard.profile_input_hover_surface": "#293341",
        "dashboard.profile_input_hover_border": "#6D7888",
        "dashboard.search_surface": "#212A35",
        "dashboard.search_text": "#C2CAD4",
        "dashboard.search_border": "#48515F",
        "dashboard.search_hover_surface": "#293342",
        "dashboard.search_hover_text": "#F3F7FB",
        "dashboard.search_hover_border": "#636E7D",
        "dashboard.nav_surface": "#212A35",
        "dashboard.nav_text": "#F7FAFC",
        "dashboard.nav_border": "#666F7C",
        "dashboard.nav_hover_surface": "#283241",
        "dashboard.nav_hover_text": "#F7FAFC",
        "dashboard.nav_hover_border": "#8892A0",
        "dashboard.nav_pressed_surface": "#1A212C",
        "dashboard.nav_pressed_border": "#596371",
        "dashboard.secondary_surface": "#232B36",
        "dashboard.secondary_text": "#D1D9E2",
        "dashboard.secondary_border": "#5A6472",
        "dashboard.secondary_hover_surface": "#2C3643",
        "dashboard.secondary_hover_text": "#FFFFFF",
        "dashboard.secondary_hover_border": "#7A8594",
        "dashboard.accent_surface": "#232C38",
        "dashboard.accent_border": "#5E6876",
        "dashboard.accent_hover_surface": "#2B3542",
        "dashboard.accent_hover_border": "#7B8695",
        "dashboard.accent_pressed_surface": "#1C2430",
    },
}

EXPECTED_GRADIENTS = {
    "claro": {
        "dashboard.topbar_gradient": ((0.0, "#FFFFFF"), (1.0, "#FFFFFF")),
        "dashboard.nav_gradient": ((0.0, "#FFFFFF"), (1.0, "#FFFFFF")),
        "dashboard.nav_hover_gradient": ((0.0, "#EDF2F7"), (1.0, "#EDF2F7")),
    },
    "escuro": {
        "dashboard.topbar_gradient": ((0.0, "#151F2D"), (1.0, "#151F2D")),
        "dashboard.nav_gradient": ((0.0, "#176B82"), (1.0, "#176B82")),
        "dashboard.nav_hover_gradient": ((0.0, "#1B7C95"), (1.0, "#1B7C95")),
    },
    "futurista": {
        "dashboard.topbar_gradient": ((0.0, "#0D1420"), (0.52, "#0F1622"), (1.0, "#0C1320")),
        "dashboard.nav_gradient": ((0.0, "#212A35"), (1.0, "#1F2732")),
        "dashboard.nav_hover_gradient": ((0.0, "#283241"), (1.0, "#252E3B")),
    },
}

OLD_QSS_BASELINE = {
    "claro": "ae984441b7a8eed69fcc9427003d28c96f631a2e7ed8c2b60504469af7441ab4",
    "escuro": "1a5a8ed63656acff1afdd27ce501a7cde18a157b1cb95e01dd305129f18847fd",
    "futurista": "4b118824e007ab2d02141e87fd994c58df0bd6fb07eff64ed5ad0ecfce090e4c",
}
NEW_QSS_BASELINE = {
    "claro": "257d65d1427b26067616ee97408571e5354bd618bd512cfabd4b887d314bdb9b",
    "escuro": "777e1ffb22578576303bc7123a936eeb264ac712faed3efef3fbd9f6cebdcba5",
    "futurista": "53f523143c157af9cfa8f22619dcb23fed38f230d6d299fd7e119570ff042e14",
}

PROTECTED_HASHES = {
    "main.py": "bdb0815e71387bd87d40498bf535ef839d19a1a9086d55e0582ea50946713b45",
    "foco.py": "8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed",
    "jogos.py": "498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286",
    "estudos.db": "034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef",
    "versao.py": "c201d237e622dd2269838e54914458fd775c7ec1a91f07b518775ee833caa439",
    "checkpoint.py": "947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38",
}


def canonical_qss(qss: str) -> str:
    qss = re.sub(r"#[0-9A-Fa-f]{3,8}\b", lambda m: m.group(0).upper(), qss)
    return re.sub(r"\s+", " ", qss).strip()


def qss_hash(qss: str) -> str:
    return hashlib.sha256(canonical_qss(qss).encode("utf-8")).hexdigest()


def constant_source(name: str) -> str:
    match = re.search(rf'{name}\s*=\s*r"""(.*?)"""', TEMA_SOURCE, re.S)
    if not match:
        raise AssertionError(f"Constante não encontrada: {name}")
    return match.group(1)


def strip_navigation_layer(theme_name: str, qss: str) -> str:
    qss = strip_cards_global_block_a(tema, theme_name, qss)
    if theme_name == "futurista":
        final_back = render_qss("futurista", tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
        inherited_back = render_qss("escuro", tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
        if qss.endswith(final_back):
            qss = qss[:-len(final_back)]
        elif final_back in qss:
            qss = qss.replace(final_back, "", 1)
        if inherited_back in qss:
            qss = qss.replace(inherited_back, "", 1)
    else:
        back_layer = render_qss(theme_name, tema.ESTILO_NAVEGACAO_RETORNOS_DASHBOARD)
        if qss.endswith(back_layer):
            qss = qss[:-len(back_layer)]
        elif back_layer in qss:
            qss = qss.replace(back_layer, "", 1)
    if theme_name == "futurista":
        final = render_qss("futurista", tema.ESTILO_NAVEGACAO_BUSCA_GLOBAL)
        inherited = render_qss("escuro", tema.ESTILO_NAVEGACAO_BUSCA_GLOBAL)
        if qss.endswith(final):
            qss = qss[:-len(final)]
        if inherited in qss:
            qss = qss.replace(inherited, "", 1)
        return qss
    layer = render_qss(theme_name, tema.ESTILO_NAVEGACAO_BUSCA_GLOBAL)
    if qss.endswith(layer):
        return qss[:-len(layer)]
    return qss.replace(layer, "", 1)


def strip_dashboard_block_c(theme_name: str, qss: str) -> str:
    qss = strip_navigation_layer(theme_name, qss)
    # Bloco G é posterior; retire-o antes. Bloco F é posterior aos contratos A/B/C/D/E; retire-o primeiro.
    if theme_name == "futurista":
        qss = qss.replace(render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_H), "", 1)
        qss = qss.replace(render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_H), "", 1)
    else:
        qss = qss.replace(render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_H), "", 1)
    if theme_name == "futurista":
        qss = qss.replace(render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_G), "", 1)
        qss = qss.replace(render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_G), "", 1)
    else:
        qss = qss.replace(render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_G), "", 1)
    if theme_name == "futurista":
        qss = qss.replace(render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_F), "", 1)
        qss = qss.replace(render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_F), "", 1)
    else:
        qss = qss.replace(render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_F), "", 1)
    # Bloco E é posterior aos contratos A/B/C/D; retire-o em seguida.
    if theme_name == "futurista":
        qss = qss.replace(render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_E), "", 1)
        qss = qss.replace(render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_E), "", 1)
    else:
        qss = qss.replace(render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_E), "", 1)
    # Bloco D é posterior aos contratos A/B/C; retire-o em seguida.
    if theme_name == "futurista":
        qss = qss.replace(render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_D), "", 1)
        qss = qss.replace(render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_D), "", 1)
    else:
        qss = qss.replace(render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_D), "", 1)
    if theme_name == "futurista":
        qss = qss.replace(render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_C), "", 1)
        qss = qss.replace(render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_C), "", 1)
        return qss
    return qss.replace(render_qss(theme_name, tema.ESTILO_DASHBOARD_BLOCO_C), "", 1)


def strip_dashboard_block_b(theme_name: str, qss: str) -> str:
    qss = strip_dashboard_block_c(theme_name, qss)
    if theme_name == "futurista":
        qss = qss.replace(render_qss("escuro", tema.ESTILO_DASHBOARD_BLOCO_B_ESCURO), "", 1)
        qss = qss.replace(render_qss("futurista", tema.ESTILO_DASHBOARD_BLOCO_B_FUTURISTA), "", 1)
        return qss
    constant = (
        tema.ESTILO_DASHBOARD_BLOCO_B_CLARO
        if theme_name == "claro"
        else tema.ESTILO_DASHBOARD_BLOCO_B_ESCURO
    )
    return qss.replace(render_qss(theme_name, constant), "", 1)


class DashboardBlockADesignSystemTests(unittest.TestCase):
    def test_orcamento_de_tokens_do_bloco_a(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 928)
        self.assertEqual(len(ALL_TOKENS), 1030)
        self.assertEqual(len(DASHBOARD_COLOR_TOKENS), 38)
        self.assertEqual(len(DASHBOARD_GRADIENT_TOKENS), 3)
        for path in DASHBOARD_COLOR_TOKENS:
            self.assertEqual(token_spec(path).kind, TokenKind.COLOR, path)
        for path in DASHBOARD_GRADIENT_TOKENS:
            self.assertEqual(token_spec(path).kind, TokenKind.GRADIENT, path)

    def test_tokens_reproduzem_baseline_visual_mapeado(self):
        for theme_name, expected in EXPECTED_COLORS.items():
            theme = get_theme(theme_name)
            for path, value in expected.items():
                with self.subTest(theme=theme_name, path=path):
                    self.assertEqual(theme.color(path).value, value)
        for theme_name, expected in EXPECTED_GRADIENTS.items():
            theme = get_theme(theme_name)
            for path, stops in expected.items():
                with self.subTest(theme=theme_name, path=path):
                    actual = tuple((stop.position, stop.color.value) for stop in theme.gradient(path).stops)
                    self.assertEqual(actual, stops)

    def test_camadas_shell_sao_tokenizadas_e_estritamente_escopadas(self):
        allowed_ids = {
            "dashboardPage", "dashboardScroll", "dashboardRoot", "pageTitle", "pageSubtitle",
            "dashboardTopBar", "topProfileBar", "topProfileLabel", "topProfileCombo",
            "globalSearchTrigger", "questionsNavButton", "subtleButton", "topAccentButton",
        }
        for name in (
            "ESTILO_DASHBOARD_SHELL_CLARO",
            "ESTILO_DASHBOARD_SHELL_ESCURO",
            "ESTILO_DASHBOARD_SHELL_FUTURISTA",
        ):
            source = constant_source(name)
            with self.subTest(name=name):
                self.assertIsNone(re.search(r"#[0-9A-Fa-f]{6,8}\b", source))
                ids = set(re.findall(r"#([A-Za-z_][A-Za-z0-9_]*)", source))
                self.assertTrue(ids <= allowed_ids, sorted(ids - allowed_ids))
                self.assertIn("#dashboardRoot", source)
                self.assertNotIn("dashboardFocusPanel", source)
                self.assertNotIn("planningPanel", source)
                self.assertNotIn("dashboardOverviewCard", source)
                self.assertNotIn("QPainter", source)
                for selector in re.findall(r"([^{}]+)\{", source):
                    if "#subtleButton" in selector or "#topAccentButton" in selector or "#questionsNavButton" in selector or "#globalSearchTrigger" in selector or "#topProfile" in selector:
                        self.assertIn("#dashboardTopBar", selector)

    def test_renderizacao_nao_deixa_marcadores_de_token(self):
        styles = {
            "claro": tema.stylesheet_claro(),
            "escuro": tema.stylesheet_escuro(),
            "futurista": tema.stylesheet_futurista(),
        }
        for theme_name, qss in styles.items():
            with self.subTest(theme=theme_name):
                self.assertNotIn("{{color:", qss)
                self.assertNotIn("{{gradient:", qss)
                qss_a = strip_dashboard_block_b(theme_name, qss)
                self.assertEqual(qss_hash(qss_a), NEW_QSS_BASELINE[theme_name])

    def test_qss_historico_so_recebeu_as_camadas_shell_previstas(self):
        light = strip_dashboard_block_b("claro", tema.stylesheet_claro())
        dark = strip_dashboard_block_b("escuro", tema.stylesheet_escuro())
        future = strip_dashboard_block_b("futurista", tema.stylesheet_futurista())
        light_shell = render_qss("claro", tema.ESTILO_DASHBOARD_SHELL_CLARO)
        dark_shell = render_qss("escuro", tema.ESTILO_DASHBOARD_SHELL_ESCURO)
        future_shell = render_qss("futurista", tema.ESTILO_DASHBOARD_SHELL_FUTURISTA)

        self.assertTrue(light.endswith(light_shell))
        self.assertTrue(dark.endswith(dark_shell))
        self.assertTrue(future.endswith(future_shell))
        self.assertEqual(qss_hash(light[:-len(light_shell)]), OLD_QSS_BASELINE["claro"])
        self.assertEqual(qss_hash(dark[:-len(dark_shell)]), OLD_QSS_BASELINE["escuro"])

        # Futurista historicamente deriva do stylesheet escuro; portanto recebe
        # a camada escura por herança e a camada futurista final a sobrescreve.
        future_without_final = future[:-len(future_shell)]
        inherited_dark = render_qss("escuro", tema.ESTILO_DASHBOARD_SHELL_ESCURO)
        self.assertIn(inherited_dark, future_without_final)
        future_without_block_a = future_without_final.replace(inherited_dark, "", 1)
        self.assertEqual(qss_hash(future_without_block_a), OLD_QSS_BASELINE["futurista"])

    def test_hierarquia_e_comportamento_do_dashboard_nao_foram_movidos(self):
        for marker in (
            'tela.setObjectName("dashboardPage")',
            'scroll.setObjectName("dashboardScroll")',
            'conteudo.setObjectName("dashboardRoot")',
            'topo_container.setObjectName("dashboardTopBar")',
            'self.botao_busca_global.setObjectName("globalSearchTrigger")',
            'botao_questoes.setObjectName("questionsNavButton")',
            'self.botao_retomar_questoes_topo.setObjectName("subtleButton")',
            'self.botao_configuracoes_topo.setObjectName("topAccentButton")',
            'perfil_central.setObjectName("topProfileBar")',
            'perfil_global_rotulo.setObjectName("topProfileLabel")',
            'self.combo_concurso.setObjectName("topProfileCombo")',
            'gerenciar_concursos.setObjectName("subtleButton")',
        ):
            self.assertIn(marker, MAIN_SOURCE)

    def test_codigo_banco_versao_e_modulos_concluidos_permanecem_byte_a_byte(self):
        for name, expected in PROTECTED_HASHES.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected)
        con = sqlite3.connect(ROOT / "estudos.db")
        try:
            self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(), [])
        finally:
            con.close()


if __name__ == "__main__":
    unittest.main()
