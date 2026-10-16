"""One-shot worker under the launching administrator, without Task Scheduler."""
import csv
import ctypes
from ctypes import wintypes
from datetime import datetime
import json
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from types import ModuleType

from sysprep.execution_record import write_record, process_alive
from sysprep.paths import system_executable, windows_directory
from sysprep.system_job import common_appdata, private_job_directory, file_hash, execution_mutex, task_name
from utils.system_process import run_system_command, system_dll_search, clean_child_environment

TERMINAL = {"completed", "power_command_accepted"}


def process_in_job():
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.argtypes = []
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.IsProcessInJob.argtypes = [wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)]
    kernel.IsProcessInJob.restype = wintypes.BOOL
    result = wintypes.BOOL()
    if not kernel.IsProcessInJob(kernel.GetCurrentProcess(), None, ctypes.byref(result)):
        raise ctypes.WinError(ctypes.get_last_error())
    return bool(result.value)


def has_console():
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetConsoleCP.argtypes = []
    kernel.GetConsoleCP.restype = wintypes.UINT
    return kernel.GetConsoleCP() != 0


def administrator_identity():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        raise RuntimeError("请以管理员身份运行程序。")
    output = run_system_command([str(system_executable("whoami.exe")), "/user", "/fo", "csv", "/nh"],
                                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sid = list(csv.reader(output.stdout.decode("oem").splitlines()))[0][-1]
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.ProcessIdToSessionId.argtypes = [wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    kernel.ProcessIdToSessionId.restype = wintypes.BOOL
    session = wintypes.DWORD()
    if not kernel.ProcessIdToSessionId(os.getpid(), ctypes.byref(session)):
        raise ctypes.WinError(ctypes.get_last_error())
    if sid in ("S-1-5-18", "S-1-5-19", "S-1-5-20") or session.value == 0:
        raise RuntimeError("不允许 SYSTEM、服务账户或会话 0 执行封装。")
    return {"workerSid": sid, "workerSession": session.value, "workerElevated": True,
            "processInJob": process_in_job()}


def independent_environment(environment, bundle):
    result = clean_child_environment(environment, bundle)
    # A separately unpacked one-file process must not reuse the GUI's _MEI dir.
    for key in list(result):
        if key.upper().startswith(("_MEIPASS", "_PYI_")):
            del result[key]
    result["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
    result["PYTHONIOENCODING"] = "utf-8"
    return result


def stage_job(mode="oobe", action="quit", answer=None, identifier=None, probe=False):
    if mode not in ("oobe", "audit") or action not in ("quit", "reboot", "shutdown"):
        raise ValueError("Invalid execution options")
    if probe and action != "quit":
        raise ValueError("A probe cannot request a power action")
    if not getattr(sys, "frozen", False):
        raise RuntimeError("独立进程需要使用打包程序。")
    identity = administrator_identity()
    if not probe and not re.fullmatch(r"\{[0-9a-fA-F-]{36}\}", identifier or ""):
        raise ValueError("Missing expected loader identifier")
    helper = Path(sys.executable).parent / "JY Sysprep Worker.exe"
    if not helper.is_file():
        raise RuntimeError("缺少 JY Sysprep Worker.exe，请完整解压候选包，不要单独移动主程序。")
    folder = private_job_directory()
    shutil.copyfile(str(helper), str(folder / "worker.exe"))
    job = {"schema": 2, "executionContext": "administrator", "kind": "probe" if probe else "deployment",
           "mode": mode, "completionAction": action, "identifier": identifier,
           "createdUtc": datetime.utcnow().isoformat(timespec="microseconds") + "Z",
           "workerHash": file_hash(folder / "worker.exe"), "windowsDirectory": str(windows_directory()),
           "issuerSid": identity["workerSid"], "issuerSession": identity["workerSession"],
           "launcherInJob": identity["processInJob"]}
    if not probe:
        shutil.copyfile(str(answer), str(folder / "unattend.xml"))
        job["answerHash"] = file_hash(folder / "unattend.xml")
    write_record(folder / "job.json", job)
    write_record(folder / "status.json", {"stage": "queued", "pid": 0, "jobKind": job["kind"],
                                         "startedUtc": job["createdUtc"], "completionAction": action,
                                         "executionContext": "administrator"})
    try:
        environment = independent_environment(os.environ, sys._MEIPASS)
        runtime_temp = folder / "RuntimeTemp"
        runtime_temp.mkdir()
        environment["TEMP"] = environment["TMP"] = str(runtime_temp)
        with (folder / "bootstrap.log").open("ab") as output, system_dll_search():
            process = subprocess.Popen([str(folder / "worker.exe"), "--admin-deployment-worker"],
                                       cwd=str(folder), env=environment, close_fds=True,
                                       stdin=subprocess.DEVNULL, stdout=output, stderr=output,
                                       creationflags=(subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                                                      | subprocess.CREATE_BREAKAWAY_FROM_JOB))
        write_record(folder / "launch.json", {"launcherPid": process.pid,
                                               "createdUtc": job["createdUtc"],
                                               "launcherInJob": identity["processInJob"],
                                               "breakawayRequested": True})
    except Exception as error:
        write_record(folder / "status.json", {"stage": "failed", "pid": 0, "jobKind": job["kind"],
                                              "startedUtc": job["createdUtc"], "error": str(error),
                                              "failedStage": "launch", "completionAction": action})
        raise RuntimeError("无法启动管理员执行进程；记录：{}；{}".format(folder, error)) from error
    return folder, process


def wait_job(folder, process, startup_timeout=60, show_progress=False):
    started = time.monotonic()
    last_stage = None
    while True:
        status = json.loads((folder / "status.json").read_text(encoding="utf-8"))
        stage = status.get("stage")
        if show_progress and stage != last_stage:
            print(json.dumps({"stage": stage, "jobDirectory": str(folder)}, ensure_ascii=True), flush=True)
            last_stage = stage
        if stage == "failed":
            raise RuntimeError("管理员执行进程失败：{}；记录：{}".format(status.get("error"), folder))
        if stage in TERMINAL:
            return status
        if process.poll() is not None:
            # The last atomic status write may have happened after our read.
            final = json.loads((folder / "status.json").read_text(encoding="utf-8"))
            if final.get("stage") in TERMINAL:
                return final
            raise RuntimeError("执行进程已退出（{}），未确认完成；请提供 status.json、bootstrap.log、worker.log：{}".format(
                process.returncode, folder))
        if stage == "queued" and time.monotonic() - started > startup_timeout:
            raise RuntimeError("执行进程未记录启动；请勿重试封装。记录：{}".format(folder))
        if stage != "queued" and not process_alive(status["pid"], status["startedUtc"]):
            raise RuntimeError("执行进程记录不再存活，请勿重试封装。记录：{}".format(folder))
        time.sleep(0.5)


def dispatch_and_wait(mode, action, answer, identifier):
    folder, process = stage_job(mode, action, answer, identifier)
    logging.getLogger("JY Sysprep").info("管理员独立执行进程：%s", folder)
    return wait_job(folder, process)


def validate_job(folder, identity):
    task_name(folder)  # Only validates the protected directory name; no task API.
    if folder.parent != common_appdata():
        raise RuntimeError("Invalid worker directory")
    job = json.loads((folder / "job.json").read_text(encoding="utf-8"))
    if job.get("schema") != 2 or job.get("executionContext") != "administrator":
        raise ValueError("Invalid administrator job schema")
    if job.get("kind") not in ("probe", "deployment"):
        raise ValueError("Invalid job kind")
    if job.get("mode") not in ("audit", "oobe") or job.get("completionAction") not in ("quit", "shutdown", "reboot"):
        raise ValueError("Invalid job options")
    if job["kind"] == "probe" and job["completionAction"] != "quit":
        raise ValueError("A probe cannot request a power action")
    if (identity["workerSid"] != job["issuerSid"] or identity["workerSession"] != job["issuerSession"]
            or os.path.normcase(str(windows_directory())) != os.path.normcase(job["windowsDirectory"])):
        raise RuntimeError("执行账户、会话或 Windows 目录与启动时不同。")
    created = datetime.strptime(job["createdUtc"].rstrip("Z"), "%Y-%m-%dT%H:%M:%S.%f")
    if not 0 <= (datetime.utcnow() - created).total_seconds() <= 300:
        raise RuntimeError("Job expired; retry is forbidden")
    if file_hash(folder / "worker.exe") != job["workerHash"]:
        raise RuntimeError("Worker hash mismatch")
    if job["kind"] == "deployment":
        if not re.fullmatch(r"\{[0-9a-fA-F-]{36}\}", job.get("identifier") or ""):
            raise ValueError("Invalid expected loader")
        if file_hash(folder / "unattend.xml") != job["answerHash"]:
            raise RuntimeError("Answer file hash mismatch")
    return job


def deployment_body(folder, job, progress):
    from sysprep.status import check_audit_mode
    from sysprep.preflight import run_preflight
    from sysprep.executor import run_sysprep
    if not check_audit_mode() or not run_preflight(str(folder / "unattend.xml"))["passed"]:
        raise RuntimeError("审核模式或封装预检未通过。")
    return run_sysprep(job["mode"], "quit", str(folder / "unattend.xml"), quiet=True,
                       backup_root=folder / "BootBackups", expected_identifier=job["identifier"],
                       record_directory=folder / "ExecutionRecords", require_multiboot=True, progress=progress)


def worker_main(*, power_action):
    if not callable(power_action):
        raise TypeError("Explicit power_action callable required")
    folder = Path(sys.executable).parent
    task_name(folder)
    if folder.parent != common_appdata():
        raise RuntimeError("Invalid worker location")
    logger = logging.getLogger("JY Sysprep")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(str(folder / "worker.log"), encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    shim = ModuleType("core.logger")
    shim.logger = logger
    sys.modules["core.logger"] = shim
    status = {"pid": os.getpid(), "stage": "worker_started", "executionContext": "administrator",
              "startedUtc": datetime.utcnow().isoformat(timespec="microseconds") + "Z"}
    def update(stage, **extra):
        status.update(extra, stage=stage, updatedUtc=datetime.utcnow().isoformat(timespec="microseconds") + "Z")
        write_record(folder / "status.json", status)
        logger.info("执行阶段：%s", stage)
        handler.flush()
    try:
        update("worker_started")
        identity = administrator_identity()
        status.update(identity)
        status["hasConsole"] = has_console()
        job = validate_job(folder, identity)
        status.update(jobKind=job["kind"], completionAction=job["completionAction"])
        update("identity_verified", launcherInJob=job.get("launcherInJob"))
        if identity["processInJob"]:
            raise RuntimeError("执行进程仍受 Job Object 统一进程管理，停止本次检查或封装。")
        if status["hasConsole"]:
            raise RuntimeError("后台进程仍关联控制台，停止本次检查或封装。")
        with (folder / "claimed").open("x"):
            pass
        with execution_mutex():
            if job["kind"] == "probe":
                time.sleep(2)
                update("completed", sysprepExecuted=False, bcdReadOrModified=False, powerActionExecuted=False)
                return 0
            update("preflight_running")
            result = deployment_body(folder, job, update)
            if (not isinstance(result, dict) or result.get("sysprepSucceeded") is not True
                    or result.get("bcdVerified") is not True):
                raise RuntimeError("未取得本次封装及引导核对通过结果，取消电源动作。")
            update("bcd_verified", backupDirectory=result.get("backupDirectory"))
            if job["completionAction"] == "quit":
                update("completed")
            else:
                update("power_requested")
                power_action(job["completionAction"])
                update("power_command_accepted")
        return 0
    except Exception as error:
        logger.exception("管理员执行进程失败")
        update("failed", failedStage=status.get("stage"), error=str(error))
        return 1
    finally:
        handler.flush()
        logger.removeHandler(handler)
        handler.close()
