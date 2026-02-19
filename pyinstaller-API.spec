# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

ROOT = Path().resolve()

ENTRY_POINT = ROOT / "cocktailberry" / "api.py"
LOG_CONFIG = ROOT / "log_config.yaml"
ICON = ROOT / "scripts" / "assets" / "berry.ico"
artifact_name = os.getenv("PYI_NAME", "pyi_name_not_set")


a = Analysis(
    [str(ENTRY_POINT.relative_to(ROOT))],
    pathex=[],
    binaries=[],
    datas=[
        (str(LOG_CONFIG), "."),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=artifact_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[ICON],
)
