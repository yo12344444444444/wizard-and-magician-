# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['fixedHomeScreen.py'],
    pathex=[],
    binaries=[],
    datas=[('graphic', 'graphic'), ('screens', 'screens'), ('inventory', 'inventory'), ('server/clientTest.py', '.'), ('items.json', '.'), ('chatCervice1.py', '.'), ('ChatClient.py', '.'), ('items.json', '.'), ('inventory.json', '.'), ('FloatingText.py', '.'), ('buttons.py', '.'), ('lb', 'lb')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='fixedHomeScreen',
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
)
