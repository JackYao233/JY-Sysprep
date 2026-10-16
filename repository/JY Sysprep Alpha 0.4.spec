# -*- mode: python ; coding: utf-8 -*-
import os

BASE_DIR = os.path.dirname(os.path.abspath(SPEC))
a = Analysis(
    [os.path.join(BASE_DIR, 'main.py')],
    pathex=[BASE_DIR],
    binaries=[],
    datas=[(os.path.join(BASE_DIR, 'sysprep', 'unattend', 'templates'), 'sysprep/unattend/templates')],
    hiddenimports=['gui.app', 'tkinter'],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[],
    win_no_prefer_redirects=False, win_private_assemblies=False,
    cipher=None, noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='JY Sysprep Alpha 0.4',
    debug=False, bootloader_ignore_signals=False,
    strip=False, upx=True, upx_exclude=[], runtime_tmpdir=None,
    console=True, disable_windowed_traceback=False,
    argv_emulation=False, target_arch=None,
    codesign_identity=None, entitlements_file=None,
)
