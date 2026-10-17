# -*- mode: python ; coding: utf-8 -*-
# Build SOMENTE EM LABORATORIO; nao instalar nem aprovar G7.
# Executar na pasta deste arquivo com PyInstaller instalado em venv descartavel:
# python -m PyInstaller --clean --noconfirm VighnaLab_QA_V3153_R1.spec
from pathlib import Path
BASE = Path(SPECPATH)
resources = [(str(BASE / name), ".") for name in (
    "PAINEL_VERSAO.json", "estado_planejamento_v3.json", "estado_planejamento_v2a.json"
)]
a = Analysis([str(BASE / "painel_homologacao.py")], pathex=[str(BASE)],
             binaries=[], datas=resources, hiddenimports=[], hookspath=[], hooksconfig={},
             runtime_hooks=[], excludes=[], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True,
          name="VighnaLab_QA_V3153_R1", debug=False, bootloader_ignore_signals=False,
          strip=False, upx=False, console=True, disable_windowed_traceback=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False,
               name="VighnaLab_QA_V3153_R1")
