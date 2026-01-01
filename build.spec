# -*- mode: python ; coding: utf-8 -*-
"""
PDF Sentinel - PyInstaller Build Specification
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# ...

block_cipher = None

# Source directory
src_path = Path('.') / 'src'

# Collect qtawesome fonts and icons
qtawesome_datas = collect_data_files('qtawesome')

# Collect all PyQt6 modules to prevent missing imports
pyqt6_hidden_imports = collect_submodules('PyQt6')

a = Analysis(
    [str(src_path / 'main.py')],
    pathex=[str(src_path)],
    binaries=[],
    datas=[
        (str(src_path / 'assets'), 'assets'),
    ] + qtawesome_datas,
    hiddenimports=[
        'fitz',
        'watchdog.observers',
        'watchdog.events',
        'reportlab.platypus',
        'reportlab.lib',
        'qtawesome',
        'qtpy',
    ] + pyqt6_hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PDFSentinel',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/assets/icon.ico',
)
