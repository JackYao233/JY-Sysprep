"""Modern-runtime entry for the isolated unified distribution candidate."""
import sys


def runtime_self_test():
    import ctypes
    from ctypes import wintypes
    import json
    import os
    import subprocess
    from gui.diagnostics import check_gui, check_execution_lifetime
    from utils.system_process import run_system_command
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetDllDirectoryW.argtypes = [wintypes.DWORD, wintypes.LPWSTR]
    kernel.GetDllDirectoryW.restype = wintypes.DWORD
    def dll_directory():
        buffer = ctypes.create_unicode_buffer(32768)
        length = kernel.GetDllDirectoryW(len(buffer), buffer)
        if length >= len(buffer):
            raise RuntimeError("DLL directory exceeded buffer")
        return buffer.value
    before = dll_directory()
    command = os.path.join(os.environ["SystemRoot"], "System32", "cmd.exe")
    result = run_system_command([command, "/d", "/c", "ver"], check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if dll_directory() != before:
        raise RuntimeError("DLL search path was not restored")
    report = {"build": "Alpha 0.4 Win11 candidate 7", "python": sys.version.split()[0],
              "systemCommandPassed": result.returncode == 0, "dllSearchRestored": True,
              "windowsVersionOutput": result.stdout.decode("oem", errors="replace").strip(),
              "sysprepExecuted": False, "bcdReadOrModified": False}
    report.update(check_gui())
    report.update(check_execution_lifetime())
    print(json.dumps(report, indent=2, ensure_ascii=True))


def worker_power_action(action):
    # Import only after the worker has initialized its private logger.
    from sysprep.executor import complete_power_action
    complete_power_action(action)


def run():
    if sys.argv[1:] == ["--admin-deployment-worker"]:
        raise RuntimeError("请由独立无控制台辅助程序执行后台作业。")
    if sys.argv[1:] == ["--deployment-worker"]:
        raise RuntimeError("旧 SYSTEM 执行入口已停用。")
    if sys.argv[1:] in (["--system-worker-self-test"], ["--system-worker-probe-detach"]):
        raise RuntimeError("旧 SYSTEM 诊断入口已停用，请使用 Check background.cmd。")
    if sys.argv[1:] in (["--admin-worker-self-test"], ["--admin-worker-probe-detach"]):
        import json
        from sysprep.admin_job import stage_job, wait_job
        folder, process = stage_job(probe=True)
        if sys.argv[1:] == ["--admin-worker-probe-detach"]:
            print(json.dumps({"jobDirectory": str(folder), "probeOnly": True}))
        else:
            print(json.dumps({"jobDirectory": str(folder), "probeOnly": True}), flush=True)
            report = wait_job(folder, process, show_progress=True)
            report["jobDirectory"] = str(folder)
            print(json.dumps(report, indent=2, ensure_ascii=True))
        return 0
    if sys.argv[1:] == ["--runtime-self-test"]:
        return runtime_self_test()
    # Help remains noninteractive, including package smoke checks.
    if "--help" not in sys.argv[1:] and "-h" not in sys.argv[1:]:
        from sysprep.execution_record import notify_interrupted
        notify_interrupted()
    if sys.argv[1:] == ["--check-last-run"]:
        return
    from main import run_application
    sys._jy_worker_capable = True
    run_application(display_version="Alpha 0.4 Win11 candidate 7")


if __name__ == "__main__":
    sys.exit(run())
