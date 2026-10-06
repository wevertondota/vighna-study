"""Caracterização da primeira integração real do Design System: ícones."""

from __future__ import annotations

from pathlib import Path
import re
import unittest
from unittest.mock import Mock, patch

from PySide6.QtWidgets import QApplication

import icones
from ui.design import qtawesome_color


ROOT = Path(__file__).resolve().parent
FALLBACK = ROOT / "assets" / "config_gear.png"

LEGACY_COLORS = {
    "claro": {
        "acao": "#355874",
        "destaque": "#FFFFFF",
        "configuracao": "#0F3989",
    },
    "escuro": {
        "acao": "#BED0E1",
        "destaque": "#FFFFFF",
        "configuracao": "#BED0E1",
    },
    "futurista": {
        "acao": "#B6D9E8",
        "destaque": "#FFFFFF",
        "configuracao": "#B6D9E8",
    },
}

ROLE_TOKENS = {
    "acao": "icon.action",
    "destaque": "icon.highlight",
    "configuracao": "icon.configuration",
}


class IconDesignSystemMigrationTests(unittest.TestCase):
    def test_tres_temas_preservam_exatamente_as_cores_legadas(self) -> None:
        for theme, roles in LEGACY_COLORS.items():
            for role, expected in roles.items():
                with self.subTest(theme=theme, role=role):
                    self.assertEqual(icones.cor_icone(theme, role), expected)
                    self.assertEqual(qtawesome_color(theme, ROLE_TOKENS[role]), expected)

    def test_tabela_de_icones_contem_tokens_e_nenhum_hexadecimal(self) -> None:
        self.assertNotRegex(repr(icones.CORES_ICONES), re.compile(r"#[0-9A-Fa-f]{3,8}"))
        for theme in LEGACY_COLORS:
            self.assertEqual(icones.CORES_ICONES[theme], ROLE_TOKENS)

    def test_icones_usa_api_publica_e_preserva_fallback_de_papel(self) -> None:
        with patch.object(icones, "qtawesome_color", wraps=qtawesome_color) as adapter:
            self.assertEqual(icones.cor_icone("claro", "papel_desconhecido"), "#355874")
            adapter.assert_called_once_with("claro", "icon.action")

    def test_criar_icone_continua_passando_nome_e_cor_ao_qtawesome(self) -> None:
        expected_icon = object()
        fake_qta = Mock()
        fake_qta.icon.return_value = expected_icon

        with patch.object(icones, "qta", fake_qta):
            result = icones.criar_icone(
                "fa6s.gear",
                tema="futurista",
                papel="configuracao",
                fallback_path=FALLBACK,
            )

        self.assertIs(result, expected_icon)
        fake_qta.icon.assert_called_once_with("fa6s.gear", color="#B6D9E8")

    def test_fallback_por_arquivo_permanece_quando_qtawesome_esta_ausente(self) -> None:
        self.assertTrue(FALLBACK.exists())
        expected_icon = object()
        with (
            patch.object(icones, "qta", None),
            patch.object(icones, "QIcon", return_value=expected_icon) as qicon,
        ):
            result = icones.criar_icone("fa6s.gear", fallback_path=FALLBACK)
        self.assertIs(result, expected_icon)
        qicon.assert_called_once_with(str(FALLBACK))

    def test_fallback_por_arquivo_permanece_quando_qtawesome_falha(self) -> None:
        fake_qta = Mock()
        fake_qta.icon.side_effect = RuntimeError("glifo indisponível")
        expected_icon = object()
        with (
            patch.object(icones, "qta", fake_qta),
            patch.object(icones, "QIcon", return_value=expected_icon) as qicon,
        ):
            result = icones.criar_icone("inexistente", fallback_path=FALLBACK)
        self.assertIs(result, expected_icon)
        qicon.assert_called_once_with(str(FALLBACK))

    def test_sem_qtawesome_e_sem_arquivo_retorna_qicon_vazio(self) -> None:
        expected_icon = object()
        with (
            patch.object(icones, "qta", None),
            patch.object(icones, "QIcon", return_value=expected_icon) as qicon,
        ):
            result = icones.criar_icone("inexistente", fallback_path=ROOT / "nao_existe.png")
        self.assertIs(result, expected_icon)
        qicon.assert_called_once_with()

    def test_importacao_e_resolucao_nao_exigem_qapplication(self) -> None:
        self.assertIsNone(QApplication.instance())
        self.assertEqual(icones.cor_icone("escuro", "acao"), "#BED0E1")
        self.assertIsNone(QApplication.instance())


if __name__ == "__main__":
    unittest.main()
