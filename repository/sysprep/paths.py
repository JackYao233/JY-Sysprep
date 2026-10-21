import os
from pathlib import Path


def windows_directory():
    return Path(os.environ.get("WINDIR", r"C:\Windows"))


def sysprep_directory():
    return windows_directory() / "System32" / "Sysprep"


def system_executable(name):
    return windows_directory() / "System32" / name
