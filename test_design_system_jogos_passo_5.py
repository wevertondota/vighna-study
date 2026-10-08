import hashlib
import json
import re
import unittest
from _design_system_test_helpers import strip_cards_global_block_a
from pathlib import Path

import tema
from ui.design import ALL_TOKENS, COMPONENT_TOKEN_COUNT, SEMANTIC_TOKEN_COUNT, TokenKind, get_theme, token_spec

ROOT = Path(__file__).resolve().parent
TEMA_SOURCE = (ROOT / "tema.py").read_text(encoding="utf-8")
JOGOS_SOURCE = (ROOT / "jogos.py").read_text(encoding="utf-8")

GAME_COLOR_TOKENS = (
    "game.hint_text",
    "game.board_surface",
    "game.board_border",
    "game.title_text",
    "game.metric_text",
    "game.status_text",
    "game.primary_surface",
    "game.primary_border",
    "game.primary_hover_surface",
    "game.primary_hover_border",
    "game.cell_surface",
    "game.cell_text",
    "game.cell_border",
    "game.chimp_number_surface",
    "game.chimp_number_text",
    "game.chimp_number_border",
    "game.chimp_correct_surface",
    "game.chimp_correct_text",
    "game.chimp_correct_border",
    "game.memory_hidden_surface",
    "game.memory_hidden_text",
    "game.memory_hidden_border",
    "game.memory_open_surface",
    "game.memory_open_text",
    "game.memory_open_border",
    "game.memory_matched_surface",
    "game.memory_matched_text",
    "game.memory_matched_border",
    "game.sequence_surface",
    "game.sequence_border",
    "game.sequence_lit_surface",
    "game.sequence_lit_border",
    "game.puzzle_movable_surface",
    "game.puzzle_movable_text",
    "game.puzzle_movable_border",
    "game.puzzle_blank_surface",
    "game.puzzle_blank_border",
    "game.puzzle_blank_text",
    "game.rotation_correct_surface",
    "game.rotation_correct_border",
    "game.rotation_wrong_surface",
    "game.rotation_wrong_border",
)

EXPECTED = {
    "claro": {
        "game.hint_text": "#64748B", "game.board_surface": "#FFFFFF", "game.board_border": "#D9E2EC",
        "game.title_text": "#243449", "game.metric_text": "#214F70", "game.status_text": "#526276",
        "game.primary_surface": "#2D8B8D", "game.primary_border": "#2D8B8D",
        "game.primary_hover_surface": "#247678", "game.primary_hover_border": "#247678",
        "game.cell_surface": "#F7FAFC", "game.cell_text": "#243449", "game.cell_border": "#CFD9E5",
        "game.chimp_number_surface": "#EDF5FF", "game.chimp_number_text": "#275F9F", "game.chimp_number_border": "#9FC3EC",
        "game.chimp_correct_surface": "#E6F7F3", "game.chimp_correct_text": "#257565", "game.chimp_correct_border": "#8BD2C3",
        "game.memory_hidden_surface": "#EEF3F8", "game.memory_hidden_text": "#60758A", "game.memory_hidden_border": "#C9D5E1",
        "game.memory_open_surface": "#E9F2FF", "game.memory_open_text": "#255F9E", "game.memory_open_border": "#8FB8E8",
        "game.memory_matched_surface": "#E4F6F0", "game.memory_matched_text": "#247060", "game.memory_matched_border": "#8CCBBB",
        "game.sequence_surface": "#EDF2F7", "game.sequence_border": "#CBD6E2",
        "game.sequence_lit_surface": "#E6B85A", "game.sequence_lit_border": "#C9922C",
        "game.puzzle_movable_surface": "#EDF5FF", "game.puzzle_movable_text": "#275F9F", "game.puzzle_movable_border": "#98BEE9",
        "game.puzzle_blank_surface": "#EDF1F5", "game.puzzle_blank_border": "#E0E6ED", "game.puzzle_blank_text": "transparent",
        "game.rotation_correct_surface": "#E4F6F0", "game.rotation_correct_border": "#60B89E",
        "game.rotation_wrong_surface": "#FFF0F1", "game.rotation_wrong_border": "#D88B96",
    },
    "escuro": {
        "game.hint_text": "#8FA2B5", "game.board_surface": "#151F2D", "game.board_border": "#33465A",
        "game.title_text": "#E8EEF5", "game.metric_text": "#9DD9E1", "game.status_text": "#A5B2C1",
        "game.primary_surface": "#287779", "game.primary_border": "#3B9798",
        "game.primary_hover_surface": "#328A8C", "game.primary_hover_border": "#50A8A9",
        "game.cell_surface": "#1B2939", "game.cell_text": "#DFE8F2", "game.cell_border": "#3A4E64",
        "game.chimp_number_surface": "#1D3550", "game.chimp_number_text": "#A8CFF7", "game.chimp_number_border": "#4F79A5",
        "game.chimp_correct_surface": "#173B35", "game.chimp_correct_text": "#9AE0CE", "game.chimp_correct_border": "#3F8173",
        "game.memory_hidden_surface": "#202D3D", "game.memory_hidden_text": "#8DA0B4", "game.memory_hidden_border": "#3B4F65",
        "game.memory_open_surface": "#1D3855", "game.memory_open_text": "#B2D5FB", "game.memory_open_border": "#557FAE",
        "game.memory_matched_surface": "#183A34", "game.memory_matched_text": "#9EE0D0", "game.memory_matched_border": "#477F73",
        "game.sequence_surface": "#202E3E", "game.sequence_border": "#3C5065",
        "game.sequence_lit_surface": "#A97625", "game.sequence_lit_border": "#D2A049",
        "game.puzzle_movable_surface": "#1C3855", "game.puzzle_movable_text": "#ACD2FA", "game.puzzle_movable_border": "#527BA8",
        "game.puzzle_blank_surface": "#121C29", "game.puzzle_blank_border": "#26384B", "game.puzzle_blank_text": "transparent",
        "game.rotation_correct_surface": "#183A34", "game.rotation_correct_border": "#477F73",
        "game.rotation_wrong_surface": "#45232B", "game.rotation_wrong_border": "#A45F6E",
    },
    "futurista": {
        "game.hint_text": "#8EAFC3", "game.board_surface": "#101F30", "game.board_border": "#315D79",
        "game.title_text": "#E1F7FF", "game.metric_text": "#8DE7E5", "game.status_text": "#8EAFC3",
        "game.primary_surface": "transparent", "game.primary_border": "#62D6D5",
        "game.primary_hover_surface": "#328A8C", "game.primary_hover_border": "#50A8A9",
        "game.cell_surface": "#14283B", "game.cell_text": "#E5F5FF", "game.cell_border": "#386681",
        "game.chimp_number_surface": "#173B5C", "game.chimp_number_text": "#B7E3FF", "game.chimp_number_border": "#5AA9DC",
        "game.chimp_correct_surface": "#17413D", "game.chimp_correct_text": "#AAF6E4", "game.chimp_correct_border": "#53BAA7",
        "game.memory_hidden_surface": "#202D3D", "game.memory_hidden_text": "#8DA0B4", "game.memory_hidden_border": "#3B4F65",
        "game.memory_open_surface": "#173B5C", "game.memory_open_text": "#B7E3FF", "game.memory_open_border": "#5AA9DC",
        "game.memory_matched_surface": "#17413D", "game.memory_matched_text": "#AAF6E4", "game.memory_matched_border": "#53BAA7",
        "game.sequence_surface": "#14283B", "game.sequence_border": "#386681",
        "game.sequence_lit_surface": "#B17F2B", "game.sequence_lit_border": "#F0C15D",
        "game.puzzle_movable_surface": "#173B5C", "game.puzzle_movable_text": "#B7E3FF", "game.puzzle_movable_border": "#5AA9DC",
        "game.puzzle_blank_surface": "#0D1825", "game.puzzle_blank_border": "#203D52", "game.puzzle_blank_text": "transparent",
        "game.rotation_correct_surface": "#17413D", "game.rotation_correct_border": "#53BAA7",
        "game.rotation_wrong_surface": "#48212F", "game.rotation_wrong_border": "#C25978",
    },
}

EXPECTED_PRIMARY_GRADIENTS = {
    "claro": ((0.0, "#2D8B8D"), (1.0, "#2D8B8D")),
    "escuro": ((0.0, "#287779"), (1.0, "#287779")),
    "futurista": ((0.0, "#1D7476"), (1.0, "#307F91")),
}

BASELINE_GAME_CASCADE_HASHES = {
    "claro": "4a160f6d3c58f24fed7ded7a531dc9eb1156da04e80c636ccd2189a9c9b734f0",
    "escuro": "eba34a0788dbb3e9cba5027f989b672c0886fbd8651f3a6ff18ff2e71930e2c1",
    "futurista": "12fd6fecf5ffdf9557977af5d170c96e0a042674fe3b53c1c63b120ddc22a235",
}

EXPECTED_QSS_NORMALIZED = {
    "claro": "eeba3c038c38703e8da3c59a81fdccee74e8f8dfd3e3cb29735f10544391e946",
    "escuro": "4dcd474191f214dda638db3414c8834a2888c9b988b6cf45be06505af92ab738",
    # Difere estruturalmente do Passo 4 somente pela separação dos grupos de
    # estados coincidentes; a cascata game.* acima permanece idêntica.
    "futurista": "0e80f4d9f6705261e8aa01db0b5e7d057d81a0ed4a37d3a04ab7b10eac997ca7",
}

PROTECTED_HASHES = {
    "main.py": "bdb0815e71387bd87d40498bf535ef839d19a1a9086d55e0582ea50946713b45",
    "foco.py": "8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed",
    "jogos.py": "498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286",
    "estudos.db": "034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef",
    "versao.py": "c201d237e622dd2269838e54914458fd775c7ec1a91f07b518775ee833caa439",
    "checkpoint.py": "947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38",
}


def _game_cascade_hash(qss: str) -> str:
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
            if any(fragment in selector for fragment in ("#game", "#chimp", "#memory", "#sequence", "#rotation", "#puzzle")):
                out.setdefault(selector, {}).update(props)
    payload = json.dumps(out, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _normalized_qss_hash(qss: str) -> str:
    qss = re.sub(r"#[0-9A-Fa-f]{3,8}\b", lambda m: m.group(0).upper(), qss)
    qss = re.sub(r"\s+", " ", qss).strip()
    return hashlib.sha256(qss.encode("utf-8")).hexdigest()


def _source_rules(source: str):
    masked = re.sub(r"\{\{(?:color|gradient):[^}]+\}\}", "TOKEN", source)
    for match in re.finditer(r"([^{}]+)\{([^{}]*)\}", masked):
        yield match.group(1), match.group(2)


class DesignSystemJogosPasso5Tests(unittest.TestCase):
    def test_contagem_final_do_passo_5(self):
        self.assertEqual(SEMANTIC_TOKEN_COUNT, 102)
        self.assertEqual(COMPONENT_TOKEN_COUNT, 928)
        self.assertEqual(len(ALL_TOKENS), 1030)

    def test_exatamente_42_colors_e_um_gradiente_game(self):
        self.assertEqual(len(GAME_COLOR_TOKENS), 42)
        for path in GAME_COLOR_TOKENS:
            with self.subTest(path=path):
                self.assertEqual(token_spec(path).kind, TokenKind.COLOR)
        self.assertEqual(token_spec("game.primary_gradient").kind, TokenKind.GRADIENT)

    def test_valores_game_reproduzem_linha_de_base(self):
        for theme_name, values in EXPECTED.items():
            theme = get_theme(theme_name)
            for path, expected in values.items():
                with self.subTest(theme=theme_name, path=path):
                    self.assertEqual(theme.color(path).value, expected)

    def test_gradiente_primario_preserva_solidos_e_futurista(self):
        for theme_name, expected in EXPECTED_PRIMARY_GRADIENTS.items():
            spec = get_theme(theme_name).gradient("game.primary_gradient")
            actual = tuple((stop.position, stop.color.value) for stop in spec.stops)
            self.assertEqual(actual, expected)
            self.assertEqual(
                (spec.direction.x1, spec.direction.y1, spec.direction.x2, spec.direction.y2),
                (0.0, 0.0, 1.0, 0.0),
            )

    def test_cascata_dos_jogos_permanece_identica_ao_passo_4(self):
        styles = {
            "claro": tema.stylesheet_claro(),
            "escuro": tema.stylesheet_escuro(),
            "futurista": tema.stylesheet_futurista(),
        }
        for theme_name, qss in styles.items():
            with self.subTest(theme=theme_name):
                self.assertEqual(_game_cascade_hash(qss), BASELINE_GAME_CASCADE_HASHES[theme_name])
                self.assertNotIn("{{color:", qss)
                self.assertNotIn("{{gradient:", qss)

    def test_qss_global_muda_somente_na_estrutura_futurista_esperada(self):
        styles = {
            "claro": tema.stylesheet_claro(),
            "escuro": tema.stylesheet_escuro(),
            "futurista": tema.stylesheet_futurista(),
        }
        for theme_name, qss in styles.items():
            with self.subTest(theme=theme_name):
                qss = strip_cards_global_block_a(tema, theme_name, qss)
                self.assertEqual(_normalized_qss_hash(qss), EXPECTED_QSS_NORMALIZED[theme_name])

    def test_regras_de_jogo_nao_contem_hex_literal(self):
        found = 0
        for selector, body in _source_rules(TEMA_SOURCE):
            if any(fragment in selector for fragment in ("#game", "#chimp", "#memory", "#sequence", "#rotation", "#puzzle")):
                found += 1
                self.assertIsNone(re.search(r"#[0-9A-Fa-f]{6,8}\b", body), selector.strip())
        self.assertGreater(found, 40)

    def test_assimetrias_de_heranca_futurista_foram_preservadas(self):
        self.assertEqual(TEMA_SOURCE.count("{{gradient:game.primary_gradient}}"), 1)
        self.assertEqual(TEMA_SOURCE.count("{{color:game.primary_surface}}"), 2)
        self.assertEqual(TEMA_SOURCE.count("{{color:game.primary_hover_surface}}"), 2)
        self.assertEqual(TEMA_SOURCE.count("{{color:game.memory_hidden_surface}}"), 2)
        self.assertEqual(TEMA_SOURCE.count("{{color:game.sequence_surface}}"), 2)
        self.assertEqual(TEMA_SOURCE.count("{{color:game.cell_surface}}"), 3)
        self.assertEqual(get_theme("futurista").color("game.primary_surface").value, "transparent")

    def test_estados_dinamicos_continuam_exatamente_no_codigo(self):
        markers = (
            'setProperty("cellState", estado)',
            'setProperty("cardState", estado)',
            'setProperty("lit", bool(aceso))',
            'setProperty("answerState", "idle")',
            'setProperty("answerState", "correct")',
            'setProperty("answerState", "wrong")',
            'setProperty("tileState", "blank" if valor == 0 else ("movable" if i in vizinhos else "normal"))',
        )
        for marker in markers:
            self.assertIn(marker, JOGOS_SOURCE)

    def test_forma_matriz_permanece_orientada_pela_palette(self):
        self.assertIn("cor = self.palette().color(QPalette.Highlight)", JOGOS_SOURCE)
        self.assertIn("cor.setAlpha(155)", JOGOS_SOURCE)
        self.assertNotIn("setStyleSheet(", JOGOS_SOURCE)
        self.assertIsNone(re.search(r"#[0-9A-Fa-f]{6,8}\b", JOGOS_SOURCE))

    def test_codigo_de_fluxo_e_banco_permanecem_byte_a_byte(self):
        for name, expected in PROTECTED_HASHES.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected)


if __name__ == "__main__":
    unittest.main()
