# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['takeoff_converter.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('zztakeoff-logo.png', '.'),
    ],
    hiddenimports=[
        'anthropic',
        'openai',
        'google.generativeai',
        'PIL',
        'PIL._tkinter_finder',
        'openpyxl',
        'pandas',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='zzTakeoff Items Import Converter',
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
)

app = BUNDLE(
    exe,
    name='zzTakeoff Items Import Converter.app',
    icon=None,
    bundle_identifier='com.zztakeoff.converter',
)
