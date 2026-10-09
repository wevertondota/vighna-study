import hashlib
import json
import re
import unittest
from pathlib import Path

import tema
from ui.design import ALL_TOKENS, COMPONENT_TOKEN_COUNT, SEMANTIC_TOKEN_COUNT, TokenKind, get_theme, token_spec

ROOT = Path(__file__).resolve().parent
TEMA_SOURCE = (ROOT / "tema.py").read_text(encoding="utf-8")
JOGOS_SOURCE = (ROOT / "jogos.py").read_text(encoding="utf-8")
MAIN_SOURCE = (ROOT / "main.py").read_text(encoding="utf-8")

PAUSE_COLOR_TOKENS = (
    "pause.hub_title_text",
    "pause.hub_subtitle_text",
    "pause.timer_panel_surface",
    "pause.timer_panel_border",
    "pause.records_panel_surface",
    "pause.records_panel_border",
    "pause.record_card_surface",
    "pause.record_card_border",
    "pause.section_title_text",
    "pause.record_title_text",
    "pause.record_value_text",
    "pause.timer_status_text",
    "pause.timer_value_surface",
    "pause.timer_value_text",
    "pause.timer_value_border",
    "pause.primary_surface",
    "pause.primary_border",
    "pause.primary_hover_surface",
    "pause.primary_hover_border",
    "pause.secondary_surface",
    "pause.secondary_text",
    "pause.secondary_border",
    "pause.secondary_hover_surface",
    "pause.secondary_hover_text",
    "pause.secondary_hover_border",
)

EXPECTED = {
    "claro": {
        "pause.hub_title_text": "#182433",
        "pause.hub_subtitle_text": "#64748B",
        "pause.timer_panel_surface": "#F3FAFA",
        "pause.timer_panel_border": "#C7E1E1",
        "pause.records_panel_surface": "#FFFFFF",
        "pause.records_panel_border": "#D9E2EC",
        "pause.record_card_surface": "#F8FAFC",
        "pause.record_card_border": "#E1E8F0",
        "pause.section_title_text": "#243449",
        "pause.record_title_text": "#64748B",
        "pause.record_value_text": "#214F70",
        "pause.timer_status_text": "#64748B",
        "pause.timer_value_surface": "#FFFFFF",
        "pause.timer_value_text": "#286D70",
        "pause.timer_value_border": "#B9DCDD",
        "pause.primary_surface": "#2D8B8D",
        "pause.primary_border": "#2D8B8D",
        "pause.primary_hover_surface": "#247678",
        "pause.primary_hover_border": "#247678",
        "pause.secondary_surface": "#FFFFFF",
        "pause.secondary_text": "#326FD3",
        "pause.secondary_border": "#A9C4EE",
        "pause.secondary_hover_surface": "#EEF5FF",
        "pause.secondary_hover_text": "#285FB5",
        "pause.secondary_hover_border": "#7FA8E8",
    },
    "escuro": {
        "pause.hub_title_text": "#EEF5FB",
        "pause.hub_subtitle_text": "#8FA2B5",
        "pause.timer_panel_surface": "#142A31",
        "pause.timer_panel_border": "#31565F",
        "pause.records_panel_surface": "#151F2D",
        "pause.records_panel_border": "#33465A",
        "pause.record_card_surface": "#192636",
        "pause.record_card_border": "#33475D",
        "pause.section_title_text": "#E8EEF5",
        "pause.record_title_text": "#8799AD",
        "pause.record_value_text": "#9DD9E1",
        "pause.timer_status_text": "#8FA2B5",
        "pause.timer_value_surface": "#162333",
        "pause.timer_value_text": "#A5E6E2",
        "pause.timer_value_border": "#3F7478",
        "pause.primary_surface": "#287779",
        "pause.primary_border": "#3B9798",
        "pause.primary_hover_surface": "#328A8C",
        "pause.primary_hover_border": "#50A8A9",
        "pause.secondary_surface": "#162333",
        "pause.secondary_text": "#A9C9FF",
        "pause.secondary_border": "#4E6F9E",
        "pause.secondary_hover_surface": "#1B3048",
        "pause.secondary_hover_text": "#D7E7FF",
        "pause.secondary_hover_border": "#6B92CA",
    },
    "futurista": {
        "pause.hub_title_text": "#E1F7FF",
        "pause.hub_subtitle_text": "#8EAFC3",
        "pause.timer_panel_surface": "#102B35",
        "pause.timer_panel_border": "#2F7180",
        "pause.records_panel_surface": "#101F30",
        "pause.records_panel_border": "#315D79",
        "pause.record_card_surface": "#13283A",
        "pause.record_card_border": "#315D79",
        "pause.section_title_text": "#E1F7FF",
        "pause.record_title_text": "#8799AD",
        "pause.record_value_text": "#8DE7E5",
        "pause.timer_status_text": "#8EAFC3",
        "pause.timer_value_surface": "#102033",
        "pause.timer_value_text": "#8DE7E5",
        "pause.timer_value_border": "#49AEB9",
        "pause.primary_surface": "transparent",
        "pause.primary_border": "#62D6D5",
        "pause.primary_hover_surface": "#328A8C",
        "pause.primary_hover_border": "#50A8A9",
        "pause.secondary_surface": "#102033",
        "pause.secondary_text": "#B6D9FF",
        "pause.secondary_border": "#4F7EB7",
        "pause.secondary_hover_surface": "#1B3048",
        "pause.secondary_hover_text": "#D7E7FF",
        "pause.secondary_hover_border": "#6B92CA",
    },
}

EXPECTED_PRIMARY_GRADIENTS = {
    "claro": ((0.0, "#2D8B8D"), (1.0, "#2D8B8D")),
    "escuro": ((0.0, "#287779"), (1.0, "#287779")),
    "futurista": ((0.0, "#1D7476"), (1.0, "#307F91")),
}

# Hash do mapa final de declarações específicas de TODOS os seletores #pause* e #game*
# na base do Passo 3. Isso permite separar seletores agrupados sem aceitar mudança visual.
BASELINE_TARGET_CASCADE_HASHES = {
    "claro": "3b7f51aba3528e1f7cccdca4b573618a29e849b0fbf131371bff73cf739bb54a",
    "escuro": "6478a3af576bce78c119ea553983059a0910d6e1178aa7af0d4b96c7c0688309",
    "futurista": "6184f89d50dfc37d6c0714891cd687b2185b7adb78fc388c5f2c6d28e669fcc8",
}

PROTECTED_HASHES = {
    "main.py": "d2e4ebd54ae765ec8f11eabd5e6c6e086e3dfd7bb3d441def8c03705515da4fe",
    "foco.py": "8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed",
    "jogos.py": "498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286",
    "versao.py": "49e9d1b5c82bc10c70bd79ca5f494961e3cae3553cd4b70af1565bca661f9ac2",
    "checkpoint.py": "947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38",
}

PAUSE_HUB_IDS = {
    "pauseHubTitle", "pauseHubSubtitle", "pauseBackButton", "pauseTimerPanel",
    "pauseSectionTitle", "pausePrimaryButton", "pauseSecondaryButton",
    "pauseTimerStatus", "pauseTimerValue", "pauseRecordsPanel", "pauseRecordCard",
    "pauseRecordTitle", "pauseRecordValue",
}


def _target_cascade_hash(qss: str) -> str:
    qss = re.sub(r"/\*.*?\*/", "", qss, flags=re.S)
    out = {}
    for match in re.finditer(r"([^{}]+)\{([^{}]*)\}", qss):
        selectors = [item.strip() for item in match.group(1).split(",")]
        props = {}
        for declaration in match.group(2).split(";"):
            if ":" not in declaration:
                continue
            key, value = declaration.split(":", 1)
            value = re.sub(r"\s+", " ", value.strip())
            value = re.sub(r"#[0-9A-Fa-f]{3,8}\b", lambda m: m.group(0).upper(), value)
            props[key.strip()] = value
        for selector in selectors:
            # O Dashboard Bloco C acrescenta somente o acesso rápido externo
            # [embedded="false"]; ele não integra a cascata histórica do hub.
            if '#dashboardQuickAccess[embedded="false"]' in selector:
                continue
            if "#pause" in selector or "#game" in selector:
                out.setdefault(selector, {}).update(props)
    payload = json.dumps(out, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _source_rules(source: str):
    masked = re.sub(r"\{\{(?:color|gradient):[^}]+\}\}", "TOKEN", source)
    for match in re.finditer(r"([^{}]+)\{([^{}]*)\}", masked):
        yield match.group(1), match.group(2)


class DesignSystemPausaPasso4Tests(unittest.TestCase):
    def test_contagem_final_do_passo_4(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 1148)
        self.assertEqual(len(ALL_TOKENS), 1250)

    def test_exatamente_25_colors_e_um_gradiente_pause(self):
        self.assertEqual(len(PAUSE_COLOR_TOKENS), 25)
        for path in PAUSE_COLOR_TOKENS:
            with self.subTest(path=path):
                self.assertEqual(token_spec(path).kind, TokenKind.COLOR)
        self.assertEqual(token_spec("pause.primary_gradient").kind, TokenKind.GRADIENT)

    def test_valores_reproduzem_a_linha_de_base(self):
        for theme_name, values in EXPECTED.items():
            theme = get_theme(theme_name)
            for path, expected in values.items():
                with self.subTest(theme=theme_name, path=path):
                    self.assertEqual(theme.color(path).value, expected)

    def test_gradiente_primario_preserva_solidos_e_futurista(self):
        for theme_name, expected in EXPECTED_PRIMARY_GRADIENTS.items():
            spec = get_theme(theme_name).gradient("pause.primary_gradient")
            actual = tuple((stop.position, stop.color.value) for stop in spec.stops)
            self.assertEqual(actual, expected)
            self.assertEqual(
                (spec.direction.x1, spec.direction.y1, spec.direction.x2, spec.direction.y2),
                (0.0, 0.0, 1.0, 0.0),
            )

    def test_cascata_pause_e_game_permanece_idêntica_ao_passo_3(self):
        styles = {
            "claro": tema.stylesheet_claro(),
            "escuro": tema.stylesheet_escuro(),
            "futurista": tema.stylesheet_futurista(),
        }
        for theme_name, qss in styles.items():
            with self.subTest(theme=theme_name):
                self.assertEqual(_target_cascade_hash(qss), BASELINE_TARGET_CASCADE_HASHES[theme_name])
                self.assertNotIn("{{color:", qss)
                self.assertNotIn("{{gradient:", qss)

    def test_pause_hub_e_game_mantem_contratos_separados_apos_passo_5(self):
        found_pause = 0
        for selector, body in _source_rules(TEMA_SOURCE):
            selector_ids = set(re.findall(r"#([A-Za-z0-9_]+)", selector))
            if selector_ids & PAUSE_HUB_IDS:
                found_pause += 1
                self.assertIsNone(re.search(r"#[0-9A-Fa-f]{6}\b", body), selector.strip())
            if any(item.startswith("game") for item in selector_ids):
                self.assertNotIn("pause.", body, selector.strip())
        self.assertGreater(found_pause, 20)
        self.assertIn("{{color:game.board_surface}}", TEMA_SOURCE)
        self.assertIn("{{gradient:game.primary_gradient}}", TEMA_SOURCE)

    def test_assimetrias_futuristas_permanecem_explicitas(self):
        self.assertEqual(TEMA_SOURCE.count("{{gradient:pause.primary_gradient}}"), 1)
        self.assertEqual(TEMA_SOURCE.count("{{color:pause.primary_surface}}"), 2)
        self.assertEqual(TEMA_SOURCE.count("{{color:pause.primary_hover_surface}}"), 2)
        self.assertEqual(TEMA_SOURCE.count("{{color:pause.secondary_hover_surface}}"), 2)
        self.assertEqual(get_theme("futurista").color("pause.primary_surface").value, "transparent")
        self.assertEqual(
            get_theme("futurista").color("pause.primary_hover_surface").value,
            get_theme("escuro").color("pause.primary_hover_surface").value,
        )

    def test_tabs_globais_e_dashboard_pause_nav_ficam_fora(self):
        self.assertIn('tabs = QTabWidget()', JOGOS_SOURCE)
        self.assertIn('tabs.setObjectName("pauseGamesTabs")', JOGOS_SOURCE)
        self.assertNotIn("QTabWidget#pauseGamesTabs", TEMA_SOURCE)
        self.assertIn('setObjectName("pauseNavButton")', MAIN_SOURCE)
        nav_blocks = [body for selector, body in _source_rules(TEMA_SOURCE) if "#pauseNavButton" in selector]
        self.assertTrue(nav_blocks)
        self.assertTrue(all("pause." not in body for body in nav_blocks))

    def test_codigo_de_fluxo_e_banco_permanecem_byte_a_byte(self):
        for name, expected in PROTECTED_HASHES.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected)

    def test_fluxo_timer_recordes_e_jogos_continua_presente(self):
        for marker in (
            'self.iniciar_pausa_btn.setObjectName("pausePrimaryButton")',
            'self.parar_pausa_btn.setObjectName("pauseSecondaryButton")',
            'self.pausa_tempo.setObjectName("pauseTimerValue")',
            'recordes.setObjectName("pauseRecordsPanel")',
            'tabs.setObjectName("pauseGamesTabs")',
        ):
            self.assertIn(marker, JOGOS_SOURCE)


if __name__ == "__main__":
    unittest.main()
