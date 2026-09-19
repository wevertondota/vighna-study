from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / "main.py").read_text(encoding="utf-8")
ICONS = (ROOT / "icones.py").read_text(encoding="utf-8")
REQ = (ROOT / "requirements.txt").read_text(encoding="utf-8")
SPEC = (ROOT / "VighnaStudy.spec").read_text(encoding="utf-8")
UPDATE = (ROOT / "atualizar_exe.bat").read_text(encoding="utf-8")


class QtAwesomeIntegrationTests(unittest.TestCase):
    def test_project_remains_pyside6_only(self):
        production = MAIN + "\n" + ICONS
        self.assertNotIn("PyQt6", production)
        self.assertIn("PySide6", ICONS)

    def test_qtawesome_is_pinned_and_prepared_by_updater(self):
        self.assertIn("QtAwesome==1.4.2", REQ)
        self.assertIn('QTA_ESPERADO=1.4.2', UPDATE)
        self.assertIn('pip install "QtAwesome==%QTA_ESPERADO%"', UPDATE)

    def test_pyinstaller_collects_qtawesome_font_data(self):
        self.assertIn('collect_data_files("qtawesome")', SPEC)
        self.assertIn("datas=QTA_DATAS", SPEC)

    def test_icon_layer_has_safe_fallback(self):
        self.assertIn("except ImportError", ICONS)
        self.assertIn("fallback_path", ICONS)
        self.assertIn('"fa6s.gear"', MAIN)
        self.assertIn('"fa6s.chart-pie"', MAIN)
        self.assertIn('"fa6s.file-lines"', MAIN)
        self.assertIn('"fa6s.calendar-days"', MAIN)


if __name__ == "__main__":
    unittest.main()
