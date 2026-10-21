import os
WORKER = False
with open(os.path.join(os.path.dirname(os.path.abspath(SPEC)), 'tools', 'single_exe_spec.py'), encoding='utf-8') as stream:
    exec(compile(stream.read(), 'single_exe_spec.py', 'exec'))
