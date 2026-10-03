import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / "main.py").read_text(encoding="utf-8")
FOCO = (ROOT / "foco.py").read_text(encoding="utf-8")
TEMA = (ROOT / "tema.py").read_text(encoding="utf-8")
VERSAO = (ROOT / "versao.py").read_text(encoding="utf-8")
TREE_MAIN = ast.parse(MAIN)
TREE_FOCO = ast.parse(FOCO)


def metodo(tree, classe, nome):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == classe:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == nome:
                    return item
    raise AssertionError(f"Método {classe}.{nome} não encontrado")


class TransparentTextBackgrounds049Tests(unittest.TestCase):
    def test_versao_e_schema(self):
        self.assertIn('VIGHNA_VERSION = "0.29.49"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "transparent-text-backgrounds-v1"', VERSAO)
        self.assertIn('VIGHNA_SCHEMA = 25', VERSAO)

    def test_tres_temas_tornam_textos_e_seletores_transparentes(self):
        regra = (
            "QLabel,\n"
            "    QCheckBox,\n"
            "    QRadioButton {\n"
            "        background-color: transparent;\n"
            "    }"
        )
        self.assertEqual(TEMA.count(regra), 3)

    def test_futurista_documenta_correcao_do_quadrante(self):
        self.assertIn("Correção visual global do Futurista", TEMA)
        self.assertIn("não devem repintar o fundo-base dentro dos cards", TEMA)

    def test_badges_com_fundo_proprio_continuam_definidos(self):
        for seletor in [
            "QLabel#questionCorrectBadge",
            "QLabel#dashboardTodayDate",
            "QLabel#questionSnapshotNotice",
        ]:
            self.assertIn(seletor, TEMA)

    def test_telas_afetadas_usam_labels_sobre_cards(self):
        visualizador = ast.unparse(metodo(TREE_MAIN, "JanelaVisualizarQuestao", "__init__"))
        resumo = ast.unparse(metodo(TREE_MAIN, "JanelaResumoResolucaoQuestoes", "__init__"))
        foco = ast.unparse(metodo(TREE_FOCO, "JanelaModoFoco", "montar_interface"))
        pos_foco = ast.unparse(metodo(TREE_FOCO, "JanelaPosFoco", "__init__"))
        self.assertIn("questionViewerCard", visualizador)
        self.assertIn("questionExplanationCard", visualizador)
        self.assertIn("questionSessionSummaryCard", resumo)
        self.assertIn("questionReviewIntegrationCard", resumo)
        self.assertIn("effectivenessImpactCard", resumo)
        self.assertIn("focusHeroPanel", foco)
        self.assertIn("focusConfigPanel", foco)
        self.assertIn("postFocusHero", pos_foco)


if __name__ == "__main__":
    unittest.main()
