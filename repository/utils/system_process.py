"""Launch Windows system tools without inheriting frozen-app DLL overrides."""
from contextlib import contextmanager
import ctypes
import os
import subprocess
import sys
import threading

_DLL_LOCK = threading.RLock()


def clean_child_environment(environment, bundle):
    result = dict(environment)
    key = next((key for key in result if key.upper() == "PATH"), "PATH")
    root = os.path.normcase(os.path.abspath(bundle))
    def bundled(value):
        path = os.path.normcase(os.path.abspath(value.strip('"')))
        return path == root or path.startswith(root + os.sep)
    result[key] = os.pathsep.join(value for value in result.get(key, "").split(os.pathsep)
                                  if value and not bundled(value))
    return result


@contextmanager
def system_dll_search():
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetDllDirectoryW.argtypes = [wintypes.DWORD, wintypes.LPWSTR]
    kernel.GetDllDirectoryW.restype = wintypes.DWORD
    kernel.SetDllDirectoryW.argtypes = [wintypes.LPCWSTR]
    kernel.SetDllDirectoryW.restype = wintypes.BOOL
    with _DLL_LOCK:
        buffer = ctypes.create_unicode_buffer(32768)
        ctypes.set_last_error(0)
        length = kernel.GetDllDirectoryW(len(buffer), buffer)
        if length >= len(buffer) or (length == 0 and ctypes.get_last_error()):
            raise RuntimeError("无法读取 DLL 搜索路径，已停止调用系统程序。")
        previous = buffer.value or None
        if not kernel.SetDllDirectoryW(None):
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            yield
        finally:
            if not kernel.SetDllDirectoryW(previous):
                raise ctypes.WinError(ctypes.get_last_error())


def run_system_command(command, **kwargs):
    if sys.platform == "win32" and getattr(sys, "_jy_windowless_worker", False):
        # System tools launched by a windowless worker must not allocate a new
        # console (which may be delegated to the packaged Windows Terminal).
        kwargs["creationflags"] = kwargs.get("creationflags", 0) | subprocess.CREATE_NO_WINDOW
    if sys.platform != "win32" or not getattr(sys, "frozen", False):
        return subprocess.run(command, **kwargs)
    environment = kwargs.get("env")
    kwargs["env"] = clean_child_environment(os.environ if environment is None else environment,
                                             sys._MEIPASS)
    with system_dll_search():
        return subprocess.run(command, **kwargs)
