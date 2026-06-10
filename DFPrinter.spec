# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\Rostek\\printer\\printer_pyside6_qml\\src\\main.py'],
    pathex=['D:\\Rostek\\printer\\printer_pyside6_qml'],
    binaries=[],
    datas=[('D:\\Rostek\\printer\\printer_pyside6_qml\\src\\views', 'src\\views'), ('D:\\Rostek\\printer\\printer_pyside6_qml\\src\\assets', 'src\\assets')],
    hiddenimports=['uvicorn.logging', 'uvicorn.loops.auto', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.websockets.auto', 'uvicorn.lifespan.on'],
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
    name='DFPrinter',
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
    icon=['D:\\Rostek\\printer\\printer_pyside6_qml\\src\\assets\\icon\\icon.ico'],
)
