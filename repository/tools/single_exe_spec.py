"""Shared PyInstaller 3.6 configuration; executed by the two single-EXE specs."""
import hashlib
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(SPEC))
RUNTIME = os.path.join(BASE_DIR, 'build', 'vista-runtime', 'x64')
with open(os.path.join(RUNTIME, 'runtime-manifest.json'), encoding='utf-8') as stream:
    runtime = json.load(stream)
if runtime['sdk'] != '10.0.14393.795' or runtime['architecture'] != 'x64':
    raise RuntimeError('Wrong NT 6.0 runtime source')
runtime_files = []
for item in runtime['files']:
    if os.path.basename(item['file']) != item['file']:
        raise RuntimeError('Invalid runtime filename')
    source = os.path.join(RUNTIME, item['file'])
    with open(source, 'rb') as stream:
        actual = hashlib.sha256(stream.read()).hexdigest().upper()
    if actual != item['sha256'] or not item['version'].startswith('10.0.14393.'):
        raise RuntimeError('NT 6.0 runtime verification failed')
    runtime_files.append((item['file'], source, 'BINARY'))
if len(runtime_files) != 41:
    raise RuntimeError('Incomplete runtime')
datas = []
if not WORKER:
    helper = os.path.join(BASE_DIR, 'build', 'alpha05-single-c3', 'worker', 'JY Sysprep Worker.exe')
    if not os.path.isfile(helper):
        raise RuntimeError('Build the windowless worker first')
    datas = [(helper, '.'),
             (os.path.join(BASE_DIR, 'licenses', 'third-party'), 'licenses'),
             (os.path.join(RUNTIME, 'runtime-manifest.json'), '.'),
             (os.path.join(BASE_DIR, 'docs', 'ALPHA-0.5-SINGLE-EXE.md'), '.')]
a = Analysis(
    [os.path.join(BASE_DIR, 'admin_worker_main.py' if WORKER else 'single_main.py')],
    pathex=[BASE_DIR], binaries=[], datas=datas,
    hiddenimports=['dataclasses'] if WORKER else ['dataclasses', 'gui.app', 'gui.diagnostics', 'tkinter'],
    hookspath=[], runtime_hooks=[], excludes=['tkinter'] if WORKER else [],
    win_no_prefer_redirects=False, win_private_assemblies=False, cipher=None, noarchive=False,
)
a.binaries = [item for item in a.binaries if item[0].lower() != 'ucrtbase.dll'
              and not item[0].lower().startswith(('api-ms-', 'ext-ms-'))]
roots = [os.path.normcase(os.path.join(BASE_DIR, name)) + os.sep
         for name in ('.runtime-vista', '.venv36-vista')]
for name, source, kind in a.binaries:
    if not any(os.path.normcase(os.path.abspath(source)).startswith(root) for root in roots):
        raise RuntimeError('Unexpected binary source: ' + source)
a.binaries += runtime_files
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
          name='JY Sysprep Worker' if WORKER else 'JY Sysprep Alpha 0.5 Single Candidate 3 x64',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
          console=not WORKER)
