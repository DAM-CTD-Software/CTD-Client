# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata
from pathlib import Path
import customtkinter

customtkinter_path = Path(customtkinter.__file__).parent.absolute()

datas=[
        (customtkinter_path, 'customtkinter/'),
        ('resources', '.')
]

datas += copy_metadata("ctd-processing")

a = Analysis(
    ['src/ctdclient/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['scipy._cyutility'],
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
    name='ctdclient',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources/icon.ico'],
)
