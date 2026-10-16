# -*- mode: python ; coding: utf-8 -*-
import hashlib
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(SPEC))
RUNTIME = os.path.join(BASE_DIR, 'build', 'vista-runtime', 'x64')
with open(os.path.join(RUNTIME, 'runtime-manifest.json'), encoding='utf-8') as handle:
    runtime = json.load(handle)
if runtime['sdk'] != '10.0.14393.795' or runtime['architecture'] != 'x64':
    raise RuntimeError('Wrong Vista runtime source')
runtime_files = []
for item in runtime['files']:
    if os.path.basename(item['file']) != item['file']:
        raise RuntimeError('Invalid runtime filename')
    source = os.path.join(RUNTIME, item['file'])
    with open(source, 'rb') as handle:
        digest = hashlib.sha256(handle.read()).hexdigest().upper()
    if digest != item['sha256'] or not item['version'].startswith('10.0.14393.'):
        raise RuntimeError('Vista runtime verification failed: ' + source)
    runtime_files.append((item['file'], source, 'BINARY'))
if len(runtime_files) != 41 or not any(item[0] == 'ucrtbase.dll' for item in runtime_files):
    raise RuntimeError('Incomplete Vista runtime')

a = Analysis(
    [os.path.join(BASE_DIR, 'vista_main.py')], pathex=[BASE_DIR],
    binaries=[], datas=[], hiddenimports=['dataclasses', 'gui.app', 'gui.diagnostics', 'tkinter'],
    hookspath=[], runtime_hooks=[], excludes=[],
    win_no_prefer_redirects=False, win_private_assemblies=False,
    cipher=None, noarchive=False,
)
# Drop host-discovered system DLLs, then add only the verified SDK set.
a.binaries = [item for item in a.binaries
              if item[0].lower() != 'ucrtbase.dll'
              and not item[0].lower().startswith(('api-ms-', 'ext-ms-'))]
runtime_roots = [os.path.normcase(os.path.join(BASE_DIR, name)) + os.sep
                 for name in ('.runtime-vista', '.venv36-vista')]
for name, source, kind in a.binaries:
    if not any(os.path.normcase(os.path.abspath(source)).startswith(root) for root in runtime_roots):
        raise RuntimeError('Unexpected binary source: ' + source)
a.binaries += runtime_files
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True,
    name='JY Sysprep Vista', debug=False, bootloader_ignore_signals=False,
    strip=False, upx=False, console=True,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=False,
    name='JY Sysprep Alpha 0.4 Vista GUI Portable x64',
)
