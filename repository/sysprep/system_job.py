"""One-shot, SYSTEM-owned execution independent of the interactive desktop."""
from contextlib import contextmanager
import ctypes
from ctypes import wintypes
from datetime import datetime
import hashlib
import json
import logging
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from types import ModuleType
import uuid
from xml.etree import ElementTree as ET

from sysprep.execution_record import write_record, process_alive
from sysprep.paths import system_executable
from utils.system_process import run_system_command

PREFIX = "JY-Sysprep-Job-"
TERMINAL = {"completed", "power_command_accepted", "failed"}


def common_appdata():
    shell = ctypes.WinDLL("shell32", use_last_error=True)
    shell.SHGetFolderPathW.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR]
    shell.SHGetFolderPathW.restype = ctypes.c_long
    buffer = ctypes.create_unicode_buffer(260)
    if shell.SHGetFolderPathW(None, 0x23, None, 0, buffer) < 0:
        raise RuntimeError("无法确定系统 ProgramData 目录。")
    return Path(buffer.value)


def private_job_directory():
    """Create with the restrictive ACL atomically, before staging an executable."""
    class SECURITY_ATTRIBUTES(ctypes.Structure):
        _fields_ = [("nLength", wintypes.DWORD), ("lpSecurityDescriptor", wintypes.LPVOID),
                    ("bInheritHandle", wintypes.BOOL)]
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    security = ctypes.WinDLL("advapi32", use_last_error=True)
    security.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD,
                                                                            ctypes.POINTER(wintypes.LPVOID), wintypes.LPVOID]
    security.ConvertStringSecurityDescriptorToSecurityDescriptorW.restype = wintypes.BOOL
    kernel.CreateDirectoryW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(SECURITY_ATTRIBUTES)]
    kernel.CreateDirectoryW.restype = wintypes.BOOL
    kernel.LocalFree.argtypes = [wintypes.HLOCAL]
    kernel.LocalFree.restype = wintypes.HLOCAL
    descriptor = wintypes.LPVOID()
    sddl = "O:BAG:SYD:P(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)"
    if not security.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl, 1, ctypes.byref(descriptor), None):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        attributes = SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES), descriptor, False)
        folder = common_appdata() / (PREFIX + uuid.uuid4().hex)
        if not kernel.CreateDirectoryW(str(folder), ctypes.byref(attributes)):
            raise ctypes.WinError(ctypes.get_last_error())
        return folder
    finally:
        kernel.LocalFree(descriptor)


def task_name(folder):
    if not re.fullmatch(PREFIX + r"[0-9a-f]{32}", folder.name):
        raise ValueError("Invalid private job directory")
    return folder.name


def task_xml(folder):
    namespace = "http://schemas.microsoft.com/windows/2004/02/mit/task"
    root = ET.Element("Task", {"version": "1.2", "xmlns": namespace})
    ET.SubElement(root, "Triggers")  # Demand-only: no time, logon or boot trigger.
    principal = ET.SubElement(ET.SubElement(root, "Principals"), "Principal", {"id": "System"})
    # ServiceAccount is an API enum, not a valid XML LogonType value.
    # Built-in SYSTEM is specified by SID without a LogonType element.
    for key, value in (("UserId", "S-1-5-18"), ("RunLevel", "HighestAvailable")):
        ET.SubElement(principal, key).text = value
    settings = ET.SubElement(root, "Settings")
    for key, value in (("MultipleInstancesPolicy", "IgnoreNew"), ("DisallowStartIfOnBatteries", "false"),
                       ("StopIfGoingOnBatteries", "false"), ("AllowStartOnDemand", "true"),
                       ("ExecutionTimeLimit", "PT0S"), ("Enabled", "true")):
        ET.SubElement(settings, key).text = value
    action = ET.SubElement(ET.SubElement(root, "Actions", {"Context": "System"}), "Exec")
    ET.SubElement(action, "Command").text = str(folder / "worker.exe")
    ET.SubElement(action, "Arguments").text = "--deployment-worker"
    ET.SubElement(action, "WorkingDirectory").text = str(folder)
    return ET.tostring(root, encoding="unicode")


def task_command(arguments):
    try:
        return run_system_command([str(system_executable("schtasks.exe"))] + arguments,
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
    except subprocess.CalledProcessError as error:
        def readable(value):
            if isinstance(value, bytes):
                return value.decode("oem" if sys.platform == "win32" else "utf-8", errors="replace").strip()
            return str(value or "").strip()
        details = "\n".join(value for value in (readable(error.stdout), readable(error.stderr)) if value)
        raise RuntimeError("计划任务操作 {} 失败（退出码 {}）：\n{}".format(
            arguments[0], error.returncode, details or "系统未返回错误文字")) from error


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stage_job(mode="oobe", action="quit", answer=None, identifier=None, probe=False):
    if not probe:
        raise RuntimeError("已停用 SYSTEM 封装方案：Microsoft 不支持在 SYSTEM 身份下运行 Sysprep。请勿使用候选包 4/R1 正式封装。")
    if mode not in ("oobe", "audit") or action not in ("quit", "reboot", "shutdown"):
        raise ValueError("Invalid execution options")
    if not getattr(sys, "frozen", False) or not ctypes.windll.shell32.IsUserAnAdmin():
        raise RuntimeError("独立后台任务需要以管理员身份运行打包程序。")
    folder = private_job_directory()
    shutil.copyfile(sys.executable, str(folder / "worker.exe"))
    job = {"schema": 1, "kind": "probe" if probe else "deployment", "mode": mode,
           "completionAction": action, "identifier": identifier,
           "createdUtc": datetime.utcnow().isoformat(timespec="microseconds") + "Z",
           "workerHash": file_hash(folder / "worker.exe")}
    if not probe:
        if not re.fullmatch(r"\{[0-9a-fA-F-]{36}\}", identifier or ""):
            raise ValueError("Missing expected loader identifier")
        shutil.copyfile(str(answer), str(folder / "unattend.xml"))
        job["answerHash"] = file_hash(folder / "unattend.xml")
    write_record(folder / "job.json", job)
    write_record(folder / "status.json", {"stage": "queued", "startedUtc": job["createdUtc"],
                                         "pid": 0, "completionAction": action, "jobKind": job["kind"]})
    (folder / "task.xml").write_text(task_xml(folder), encoding="utf-16")
    name = task_name(folder)
    created = False
    try:
        task_command(["/create", "/tn", name, "/xml", str(folder / "task.xml")])
        created = True
        task_command(["/run", "/tn", name])
    except Exception as error:
        if created:
            try:
                task_command(["/delete", "/tn", name, "/f"])
            except Exception:
                logging.getLogger("JY Sysprep").exception("任务清理失败：%s", name)
        raise RuntimeError("{}\n任务记录目录：{}".format(error, folder)) from error
    return folder


def wait_job(folder, startup_timeout=90):
    started = time.monotonic()
    while True:
        status = json.loads((folder / "status.json").read_text(encoding="utf-8"))
        if status["stage"] == "failed":
            raise RuntimeError("后台任务失败：{}；日志：{}".format(status.get("error"), folder / "worker.log"))
        if status["stage"] in TERMINAL:
            return status
        if status["stage"] != "queued" and not process_alive(status["pid"], status["startedUtc"]):
            raise RuntimeError("SYSTEM 后台进程异常退出，未确认完成；请保留日志：{}".format(folder))
        if status["stage"] == "queued" and time.monotonic() - started > startup_timeout:
            raise RuntimeError("后台任务启动状态未确认，请勿重试封装。任务记录：{}".format(folder))
        time.sleep(0.5)


def dispatch_and_wait(mode, action, answer, identifier):
    folder = stage_job(mode, action, answer, identifier)
    logging.getLogger("JY Sysprep").info("SYSTEM 后台任务：%s；桌面窗口退出不取消任务。", folder)
    return wait_job(folder)


def system_identity():
    import csv
    import os
    output = run_system_command([str(system_executable("whoami.exe")), "/user", "/fo", "csv", "/nh"],
                                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sid = list(csv.reader(output.stdout.decode("oem").splitlines()))[0][-1]
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.ProcessIdToSessionId.argtypes = [wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    kernel.ProcessIdToSessionId.restype = wintypes.BOOL
    session = wintypes.DWORD()
    if not kernel.ProcessIdToSessionId(os.getpid(), ctypes.byref(session)):
        raise ctypes.WinError(ctypes.get_last_error())
    if sid != "S-1-5-18" or session.value != 0:
        raise RuntimeError("Worker must run as SYSTEM in session 0")
    return {"workerSid": sid, "workerSession": session.value}


@contextmanager
def execution_mutex():
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    kernel.CreateMutexW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    kernel.ReleaseMutex.argtypes = [wintypes.HANDLE]
    kernel.ReleaseMutex.restype = wintypes.BOOL
    ctypes.set_last_error(0)
    handle = kernel.CreateMutexW(None, True, "Global\\JYSysprepFormalExecution")
    error = ctypes.get_last_error()
    if not handle:
        raise ctypes.WinError(error)
    try:
        if error == 183:
            raise RuntimeError("另一个后台执行任务已存在，停止重复封装。")
        yield
    finally:
        if error != 183:
            kernel.ReleaseMutex(handle)
        kernel.CloseHandle(handle)


def validate_job(folder):
    task_name(folder)
    if folder.parent != common_appdata():
        raise RuntimeError("Invalid private job location")
    job = json.loads((folder / "job.json").read_text(encoding="utf-8"))
    if job.get("schema") != 1 or job.get("kind") not in ("probe", "deployment"):
        raise ValueError("Invalid job schema")
    created = datetime.strptime(job["createdUtc"].rstrip("Z"), "%Y-%m-%dT%H:%M:%S.%f")
    if not 0 <= (datetime.utcnow() - created).total_seconds() <= 300:
        raise RuntimeError("Job expired; automatic retry is forbidden")
    if job["mode"] not in ("audit", "oobe") or job["completionAction"] not in ("quit", "reboot", "shutdown"):
        raise ValueError("Invalid execution options")
    if file_hash(folder / "worker.exe") != job["workerHash"]:
        raise RuntimeError("Worker hash mismatch")
    if job["kind"] == "deployment" and file_hash(folder / "unattend.xml") != job["answerHash"]:
        raise RuntimeError("Answer file hash mismatch")
    return job


def deployment_body(folder, job, progress):
    raise RuntimeError("SYSTEM 封装路径已停用，需改为管理员用户身份执行。")


def worker_main(*, power_action):
    """Run a worker with an explicit power capability supplied by its caller.

    There is deliberately no default or dynamic fallback to the real power
    function. Tests must pass their own callable, independent of module-cache
    state and patching of imported executor modules.
    """
    if not callable(power_action):
        raise TypeError("An explicit power_action callable is required")
    import os
    folder = Path(sys.executable).parent
    task_name(folder)  # Never use an arbitrary CLI directory or task name.
    if folder.parent != common_appdata():
        raise RuntimeError("Invalid worker directory")
    logger = logging.getLogger("JY Sysprep")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(str(folder / "worker.log"), encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger_module = ModuleType("core.logger")
    logger_module.logger = logger
    sys.modules["core.logger"] = logger_module
    status = {"pid": os.getpid(), "stage": "worker_started",
              "startedUtc": datetime.utcnow().isoformat(timespec="microseconds") + "Z"}
    def update(stage, **extra):
        status.update(extra)
        status["stage"] = stage
        status["updatedUtc"] = datetime.utcnow().isoformat(timespec="microseconds") + "Z"
        write_record(folder / "status.json", status)
        logger.info("后台执行阶段：%s", stage)
        handler.flush()
    deleted = False
    try:
        update("worker_started")
        job = validate_job(folder)
        status["jobKind"] = job["kind"]
        status.update(system_identity())
        status["completionAction"] = job["completionAction"]
        with (folder / "claimed").open("x"):
            pass  # One-shot even if somebody manually runs the task again.
        with execution_mutex():
            # Deleting a task does not terminate its running process.
            task_command(["/delete", "/tn", task_name(folder), "/f"])
            deleted = True
            if job["kind"] == "probe":
                time.sleep(2)  # Allows a detached probe launcher to exit first.
                update("completed", sysprepExecuted=False, bcdReadOrModified=False)
            else:
                update("preflight_running")
                result = deployment_body(folder, job, update)
                if (not isinstance(result, dict) or result.get("sysprepSucceeded") is not True
                        or result.get("bcdVerified") is not True):
                    raise RuntimeError("未取得本次封装成功及引导核对通过的结果，取消电源操作。")
                update("bcd_verified", backupDirectory=result.get("backupDirectory"))
                if job["completionAction"] == "quit":
                    update("completed")
                else:
                    update("power_requested")
                    power_action(job["completionAction"])
                    update("power_command_accepted")
        return 0
    except Exception as error:
        logger.exception("独立执行任务失败")
        update("failed", failedStage=status.get("stage"), error=str(error))
        return 1
    finally:
        if not deleted:
            try:
                task_command(["/delete", "/tn", task_name(folder), "/f"])
            except Exception:
                logger.exception("任务条目清理失败；该任务没有自动触发器。")
        handler.flush()
        logger.removeHandler(handler)
        handler.close()
