import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FOCO = (ROOT / "foco.py").read_text(encoding="utf-8")
TEMA = (ROOT / "tema.py").read_text(encoding="utf-8")
VERSAO = (ROOT / "versao.py").read_text(encoding="utf-8")
TREE = ast.parse(FOCO)


def metodo(classe, nome):
    for node in TREE.body:
        if isinstance(node, ast.ClassDef) and node.name == classe:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == nome:
                    return item
    raise AssertionError(f"Método {classe}.{nome} não encontrado")


class FocusVisual047Tests(unittest.TestCase):
    def test_versao_e_build(self):
        self.assertIn('VIGHNA_VERSION = "0.29.47"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "focus-ui-polish-v1"', VERSAO)
        self.assertIn('VIGHNA_SCHEMA = 25', VERSAO)

    def test_modo_foco_ganhou_hero_e_layout_em_duas_colunas(self):
        montar = ast.unparse(metodo("JanelaModoFoco", "montar_interface"))
        self.assertIn("focusHeroPanel", montar)
        self.assertIn("self.hero_hoje", montar)
        self.assertIn("self.hero_estado", montar)
        self.assertIn("self.hero_nota", montar)
        self.assertIn("coluna_esquerda", montar)
        self.assertIn("coluna_direita", montar)
        self.assertIn("Pausas & Desafios", montar)
        self.assertIn("Sessões recentes", montar)

    def test_estado_visual_do_hero_acompanha_inicio_pausa_e_reset(self):
        iniciar = ast.unparse(metodo("JanelaModoFoco", "iniciar"))
        pausar = ast.unparse(metodo("JanelaModoFoco", "alternar_pausa"))
        finalizar = ast.unparse(metodo("JanelaModoFoco", "finalizar"))
        self.assertIn("self.hero_estado.setText('Sessão ativa')", iniciar)
        self.assertIn("self.hero_nota.setText", iniciar)
        self.assertIn("self.hero_estado.setText('Sessão pausada')", pausar)
        self.assertIn("self.hero_estado.setText('Pronto para iniciar')", finalizar)

    def test_pos_foco_ficou_mais_organizado(self):
        init = ast.unparse(metodo("JanelaPosFoco", "__init__"))
        self.assertIn("postFocusDialogTitle", init)
        self.assertIn("postFocusDialogSubtitle", init)
        self.assertIn("postFocusMiniCard", init)
        self.assertIn("Qual é o próximo passo?", init)
        self.assertIn("Continuar estudando", init)
        self.assertIn("postFocusContinue", init)

    def test_tema_cobre_novos_componentes(self):
        for token in [
            "focusHeroPanel",
            "focusHeroMiniCard",
            "focusConfigHint",
            "postFocusDialogTitle",
            "postFocusMiniCard",
        ]:
            self.assertIn(token, TEMA)


if __name__ == "__main__":
    unittest.main()
