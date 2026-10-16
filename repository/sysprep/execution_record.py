"""Durable diagnostic records. Records never authorize repair or power actions."""
import ctypes
from datetime import datetime
import json
import os
from pathlib import Path
import uuid

TERMINAL = {"completed", "power_command_accepted"}


def record_root():
    return Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "JY Sysprep" / "ExecutionRecords"


def write_record(path, data):
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(str(temporary), str(path))


class ExecutionRecord:
    def __init__(self, mode, action, backup_directory, root=None):
        folder = (record_root() if root is None else Path(root)) / uuid.uuid4().hex
        folder.mkdir(parents=True)
        self.path = folder / "execution.json"
        self.data = {"pid": os.getpid(), "startedUtc": datetime.utcnow().isoformat(timespec="microseconds") + "Z",
                     "mode": mode, "completionAction": action,
                     "backupDirectory": str(backup_directory), "stage": "sysprep_running"}
        write_record(self.path, self.data)

    def update(self, stage, **details):
        self.data.update(details)
        self.data.update(stage=stage, updatedUtc=datetime.utcnow().isoformat() + "Z")
        write_record(self.path, self.data)


def process_alive(pid, started_utc=None):
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.GetExitCodeProcess.restype = wintypes.BOOL
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    kernel.GetProcessTimes.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.OpenProcess(0x1000, False, int(pid))
    if not handle:
        # Access denied is not proof of process termination.
        return ctypes.get_last_error() != 87
    try:
        if started_utc:
            times = [wintypes.FILETIME() for _ in range(4)]
            if kernel.GetProcessTimes(handle, *(ctypes.byref(value) for value in times)):
                created = (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
                recorded = datetime.strptime(started_utc.rstrip("Z"), "%Y-%m-%dT%H:%M:%S.%f")
                record_ticks = int((recorded - datetime(1601, 1, 1)).total_seconds() * 10000000)
                if created > record_ticks:
                    return False  # PID belongs to a newer process, possibly after reboot.
        code = wintypes.DWORD()
        return not kernel.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value == 259
    finally:
        kernel.CloseHandle(handle)


def background_record_paths():
    try:
        from sysprep.system_job import common_appdata
        return list(common_appdata().glob("JY-Sysprep-Job-*/status.json"))
    except OSError:
        return []


def interrupted_records():
    root = record_root()
    found = []
    paths = list(root.glob("*/execution.json")) if root.is_dir() else []
    paths += background_record_paths()
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("jobKind") == "probe":
                continue
            if data.get("stage") == "queued":
                started = datetime.strptime(data["startedUtc"].rstrip("Z"), "%Y-%m-%dT%H:%M:%S.%f")
                if (datetime.utcnow() - started).total_seconds() < 300:
                    continue
            if (data.get("stage") not in TERMINAL and not data.get("notified")
                    and not process_alive(data["pid"], data.get("startedUtc"))):
                found.append((path, data))
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return sorted(found, key=lambda item: item[1].get("startedUtc", ""))


def notify_interrupted():
    """Native dialog also works without Explorer or Tcl/Tk."""
    pending = interrupted_records()
    if not pending:
        return False
    path, data = pending[-1]
    stages = {"sysprep_running": "已启动 Sysprep，尚未记录返回",
              "queued": "后台任务尚未确认启动", "worker_started": "后台进程已启动，正在检查",
              "preflight_running": "后台进程正在重新检查封装条件",
              "identity_verified": "执行账户已确认，正在检查进程独立性",
              "sysprep_returned": "Sysprep 已返回，正在核对成功标记",
              "bcd_verifying": "正在核对或修复当前系统引导项",
              "bcd_verified": "引导项已核对，尚未提交完成动作",
              "power_requested": "正在提交关机或重启命令", "failed": "执行失败"}
    stage = data.get("failedStage", data.get("stage"))
    message = ("上次多系统封装流程未记录完成，请勿直接重试封装或强制重启。\n\n"
               "最后阶段：{}\n选择的完成动作：{}\n开始时间（UTC）：{}\n"
               "记录：{}\nBCD 备份：{}\n\n"
               "Sysprep 可能已完成，但后续 BCD 核对或关机/重启尚未完成。"
               "请保留现场并采集诊断日志。此提示不会执行修复或电源操作。"
               ).format(stages.get(stage, stage), data.get("completionAction"),
                        data.get("startedUtc"), path, data.get("backupDirectory"))
    if data.get("error"):
        message += "\n错误：" + str(data["error"])
    user = ctypes.WinDLL("user32", use_last_error=True)
    from ctypes import wintypes
    user.MessageBoxW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT]
    user.MessageBoxW.restype = ctypes.c_int
    acknowledged = user.MessageBoxW(None, message, "JY Sysprep：上次流程未完成", 0x10 | 0x10000)
    if acknowledged:
        data["notified"] = True
        try:
            write_record(path, data)
        except OSError:
            print("无法保存提示确认状态；请保留执行记录：{}".format(path))
    return True
