from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parent
SPEC = (ROOT / "VighnaStudy.spec").read_text(encoding="utf-8")
UPDATE = (ROOT / "atualizar_exe.bat").read_text(encoding="utf-8")


class PyInstallerBuildConfigTests(unittest.TestCase):
    def test_required_qt_modules_are_not_excluded(self):
        for module in ("PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets"):
            self.assertNotRegex(
                SPEC,
                rf'^[ \t]*["\']{re.escape(module)}["\'],?[ \t]*$',
                msg=f"{module} nao pode ser excluido do build",
            )

    def test_excluded_qt_modules_are_not_imported_by_production_sources(self):
        excluded = set(re.findall(r'"(PySide6\.Qt[A-Za-z0-9_]+)"', SPEC))
        self.assertTrue(excluded)

        production_files = [
            p for p in ROOT.glob("*.py")
            if not p.name.startswith("test_")
            and "backup" not in p.name
            and "antes" not in p.name
        ]
        production_files += list((ROOT / "statistics_core").glob("*.py"))

        imports = []
        for path in production_files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for module in excluded:
                if re.search(rf"(?:from|import)\s+{re.escape(module)}\b", text):
                    imports.append((path.name, module))

        self.assertEqual([], imports, f"Modulo excluido passou a ser usado: {imports}")

    def test_default_update_build_does_not_force_clean(self):
        self.assertIn('if /I "%VIGHNA_CLEAN_BUILD%"=="1"', UPDATE)
        self.assertIn("Build INCREMENTAL", UPDATE)
        self.assertIn("--clean", UPDATE)
        self.assertIn("VighnaStudy.spec", UPDATE)

    def test_pyinstaller_is_not_upgraded_on_every_build(self):
        self.assertNotIn("pip install --upgrade pyinstaller", UPDATE.lower())
        self.assertIn("PyInstaller==%PYINSTALLER_ESPERADO%", UPDATE)


if __name__ == "__main__":
    unittest.main()
