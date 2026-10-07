# AquaClean.spec
# PyInstaller build spec - packages the game into a single standalone
# executable with all images and sounds bundled inside. No Python
# installation is needed to run the result.
#
# Built automatically by .github/workflows/build.yml on every version tag.
# To build locally instead: pyinstaller AquaClean.spec

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AquaClean',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AquaClean',
)

app = BUNDLE(
    coll,
    name='AquaClean.app',
    icon=None,
    bundle_identifier='com.rijitghosh.aquaclean',
)
