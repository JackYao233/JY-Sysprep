"""Vista SP2 x64 GUI/TUI entry; reuses the main application's workflow."""
import argparse
import json
import sys


VISTA_BUILD = "Alpha 0.4 Vista GUI experimental 3"


def loaded_libraries():
    """Report actual DLL locations for the Vista VM's read-only smoke test."""
    import ctypes
    from ctypes import wintypes

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
    kernel.GetModuleHandleW.restype = wintypes.HMODULE
    kernel.GetModuleFileNameW.argtypes = [wintypes.HMODULE, wintypes.LPWSTR, wintypes.DWORD]
    kernel.GetModuleFileNameW.restype = wintypes.DWORD
    result = {}
    for name in ("python36.dll", "ucrtbase.dll", "vcruntime140.dll", "tcl86t.dll", "tk86t.dll"):
        handle = kernel.GetModuleHandleW(name)
        buffer = ctypes.create_unicode_buffer(32768)
        size = kernel.GetModuleFileNameW(handle, buffer, len(buffer)) if handle else 0
        result[name] = buffer.value if 0 < size < len(buffer) else None
    return result


def self_test(check_gui=False):
    # No logger import, file writes, BCD access or Sysprep execution.
    from types import SimpleNamespace
    from xml.etree import ElementTree as ET
    from sysprep.config import SysprepConfig
    from sysprep.unattend.generator import create_xml

    context = SimpleNamespace(arch="AMD64", supports_wireless_oobe=False,
                              supports_online_accounts=False,
                              supports_local_account_screen=False)
    root = ET.fromstring(create_xml(context, SysprepConfig(mode="oobe")))
    namespace = "{urn:schemas-microsoft-com:unattend}"
    if root.tag != namespace + "unattend":
        raise RuntimeError("Invalid answer file namespace")
    forbidden = ("HideWirelessSetupInOOBE", "HideOnlineAccountScreens", "HideLocalAccountScreen")
    if any(root.find(".//" + namespace + tag) is not None for tag in forbidden):
        raise RuntimeError("Unsupported Vista answer file option")
    version = sys.getwindowsversion()
    report = {
        "build": VISTA_BUILD,
        "python": sys.version.split()[0],
        "windows": list(version[:3]),
        "servicePackMajor": version.service_pack_major,
        "pointerBits": 64 if sys.maxsize > 2 ** 32 else 32,
        "xmlCheckPassed": True,
        "sysprepExecuted": False,
        "bcdModified": False,
        "vistaDeploymentValidated": False,
    }
    exit_code = 0
    if check_gui:
        try:
            from gui.diagnostics import check_gui as run_gui_check
            report.update(run_gui_check())
        except Exception as error:
            report.update({"guiSmokeCheckPassed": False, "guiError": str(error)})
            exit_code = 1
    report["loadedLibraries"] = loaded_libraries()
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return exit_code


def run(argv=None):
    parser = argparse.ArgumentParser(description="JY Sysprep Alpha 0.4 - Vista SP2 x64 GUI / TUI")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--tui", action="store_true", help="Start the console wizard")
    modes.add_argument("--gui", action="store_true", help="Start the graphical wizard")
    checks = parser.add_mutually_exclusive_group()
    checks.add_argument("--self-test", action="store_true", help="Read-only runtime and XML check; never runs Sysprep")
    checks.add_argument("--gui-self-test", action="store_true", help="Read-only six-page GUI and F8 handoff check")
    args = parser.parse_args(argv)
    if args.self_test or args.gui_self_test:
        return self_test(check_gui=args.gui_self_test)

    version = sys.getwindowsversion()
    if (version.major, version.minor) != (6, 0) or version.service_pack_major < 2:
        print("This experimental build targets Windows Vista SP2 x64 only.")
        print("Use --self-test for a read-only runtime check on this computer.")
        return 2
    if sys.maxsize <= 2 ** 32:
        print("This build requires a 64-bit Python runtime.")
        return 2
    print("JY Sysprep " + VISTA_BUILD)
    print("Target: Vista SP2 x64, single-system installation. Deployment validation pending.")
    from main import run_application
    selected = ["--tui"] if args.tui else ["--gui"] if args.gui else []
    run_application(selected, display_version=VISTA_BUILD)
    return 0


if __name__ == "__main__":
    sys.exit(run())
