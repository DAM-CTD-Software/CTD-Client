# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata
from pathlib import Path
import customtkinter
import ctdam

customtkinter_path = Path(customtkinter.__file__).parent.absolute()
ctdam_path = Path(ctdam.__file__).parent.joinpath('conv', 'sensor_mapping.toml')

datas=[
        (customtkinter_path, 'customtkinter/'),
        ('src/ctdclient/resources', '.'),
        ('/htmls', 'htmls'),
        (ctdam_path, 'ctdam/conv/'),
]

datas += copy_metadata("ctdam")

a = Analysis(
    ['src/ctdclient/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['scipy._cyutility', 'numpy._core._exceptions'],
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
    icon=['src/ctdclient/resources/icon.ico'],
    version='version.txt',
)
