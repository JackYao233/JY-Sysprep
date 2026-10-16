# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 3.6 / Python 3.6.8 x64; intentionally separate from the main build.
import os

BASE_DIR = os.path.dirname(os.path.abspath(SPEC))
a = Analysis(
    [os.path.join(BASE_DIR, 'vista_main.py')], pathex=[BASE_DIR],
    binaries=[], datas=[], hiddenimports=['dataclasses'],
    hookspath=[], runtime_hooks=[], excludes=['gui', 'tkinter', '_tkinter'],
    win_no_prefer_redirects=False, win_private_assemblies=False,
    cipher=None, noarchive=False,
)
# Use the target OS's UCRT update (KB2999226 or its replacement).
# Never redistribute API-set/UCRT DLLs discovered in this computer's PATH.
a.binaries = [item for item in a.binaries
              if item[0].lower() != 'ucrtbase.dll'
              and not item[0].lower().startswith(('api-ms-', 'ext-ms-'))]
runtime_roots = [os.path.normcase(os.path.join(BASE_DIR, name)) + os.sep
                 for name in ('.runtime-vista', '.venv36-vista')]
for name, source, kind in a.binaries:
    if not any(os.path.normcase(os.path.abspath(source)).startswith(root)
               for root in runtime_roots):
        raise RuntimeError('Unexpected Vista binary source: ' + source)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='JY Sysprep Alpha 0.4 Vista Experimental x64',
    debug=False, bootloader_ignore_signals=False, strip=False,
    upx=False, runtime_tmpdir=None, console=True,
)
