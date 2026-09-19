# -*- mode: python ; coding: utf-8 -*-

"""Build otimizado do VighnaStudy.

O aplicativo utiliza apenas QtCore, QtGui e QtWidgets. Componentes Qt que nao
fazem parte do Vighna sao excluidos explicitamente para evitar analise/coleta
acidental pelo PyInstaller. O build padrao reutiliza o workpath; use
atualizar_exe_limpo.bat quando for necessario descartar o cache.
"""

from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

ROOT = Path.cwd()

# O Vighna nao importa nem usa estes componentes. Manter a lista aqui deixa o
# contrato do executavel auditavel e evita hooks/bibliotecas desnecessarios.
QT_EXCLUDES = [
    "PySide6.QtNetwork",
    "PySide6.QtQml",
    "PySide6.QtQuick",
    "PySide6.QtQuickWidgets",
    "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineWidgets",
    "PySide6.QtWebChannel",
    "PySide6.QtMultimedia",
    "PySide6.QtMultimediaWidgets",
    "PySide6.QtBluetooth",
    "PySide6.QtNfc",
    "PySide6.QtPositioning",
    "PySide6.QtLocation",
    "PySide6.QtSql",
    "PySide6.QtTest",
    "PySide6.QtOpenGL",
    "PySide6.QtOpenGLWidgets",
    "PySide6.QtPrintSupport",
    "PySide6.QtSvg",
    "PySide6.QtSvgWidgets",
    "PySide6.QtPdf",
    "PySide6.QtPdfWidgets",
]


# QtAwesome usa fontes Font Awesome distribuídas como dados do pacote.
# A coleta explícita evita depender do comportamento de hooks externos.
QTA_DATAS = collect_data_files("qtawesome")
GENERAL_EXCLUDES = [
    "tkinter",
    "matplotlib",
    "numpy",
    "pandas",
]


a = Analysis(
    ["main.py"],
    pathex=[str(ROOT)],
    binaries=[],
    datas=QTA_DATAS,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=QT_EXCLUDES + GENERAL_EXCLUDES,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VighnaStudy",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # Velocidade de build e previsibilidade sao mais importantes que alguns
    # MB de compressao em um aplicativo --onedir. Qt6 ja domina o tamanho.
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[str(ROOT / "vighnastudy.ico")],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="VighnaStudy",
)
