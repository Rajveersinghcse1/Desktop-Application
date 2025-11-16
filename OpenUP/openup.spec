# -*- mode: python ; coding: utf-8 -*-

"""PyInstaller specification file for OpenUP."""

import sys
from pathlib import Path

block_cipher = None

# Collect all source files
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('resources', 'resources'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'pandas',
        'numpy',
        'PIL',
        'openpyxl',
        'src.core.config',
        'src.core.logger',
        'src.core.plugin_base',
        'src.core.plugin_manager',
        'src.core.worker_pool',
        'src.core.cache_manager',
        'src.ui.main_window',
        'src.ui.file_browser',
        'src.ui.domain_filter',
        'src.ui.preview_area',
        'src.ui.dialogs',
        'src.ui.themes',
        'src.plugins.text_plugin',
        'src.plugins.image_plugin',
        'src.plugins.data_plugin',
        'src.utils.helpers',
    ],
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
    [],
    exclude_binaries=True,
    name='OpenUP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OpenUP',
)

# macOS app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='OpenUP.app',
        icon=None,
        bundle_identifier='com.openup.viewer',
    )
