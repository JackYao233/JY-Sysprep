import subprocess
from pathlib import Path

from core.logger import logger
from sysprep.log_collector import collect_sysprep_logs
from sysprep.paths import sysprep_directory
from sysprep.paths import system_executable
from sysprep.boot import prepare_boot_plan, repair_boot_plan, BootCompatibilityError
from sysprep.execution_record import ExecutionRecord
from utils.system_process import run_system_command


class SysprepPreflightError(RuntimeError):
    def __init__(self, message, preflight_result):
        super().__init__(message)
        self.preflight_result = preflight_result


def _success_stamp(directory):
    marker = directory / "Sysprep_succeeded.tag"
    if not marker.is_file():
        return None
    stat = marker.stat()
    return stat.st_mtime_ns, stat.st_ino


def complete_power_action(action):
    if action == "quit":
        return
    switch = {"shutdown": "/s", "reboot": "/r"}[action]
    run_system_command([str(system_executable("shutdown.exe")), switch, "/t", "0"], check=True)


def run_sysprep(mode="audit", completion_action="shutdown", unattend_path=None, allow_multiboot=True,
                isolate=False, quiet=False, backup_root=None, expected_identifier=None, record_directory=None,
                require_multiboot=False, progress=None):
    if mode not in ("audit", "oobe"):
        raise ValueError("启动模式必须是 audit 或 oobe。")
    if completion_action not in ("shutdown", "reboot", "quit"):
        raise ValueError("完成后的动作必须是 shutdown、reboot 或 quit。")
    executable = sysprep_directory() / "sysprep.exe"
    answer_file = Path(unattend_path) if unattend_path else sysprep_directory() / "unattend.xml"
    if not executable.is_file():
        raise FileNotFoundError(f"找不到 Sysprep：{executable}")
    if not answer_file.is_file():
        raise FileNotFoundError(f"找不到应答文件：{answer_file}")

    record = None
    def report(stage, **details):
        if record is not None:
            record.update(stage, **details)
        if progress is not None:
            progress(stage, **details)

    try:
        plan = prepare_boot_plan() if backup_root is None else prepare_boot_plan(backup_root)
        if expected_identifier is not None and plan.identifier != expected_identifier:
            raise BootCompatibilityError("后台任务识别到的当前引导项与确认时不同，停止封装。")
        if require_multiboot and not plan.multiboot:
            raise BootCompatibilityError("后台任务的多系统引导条件已变化，停止封装。")
        if plan.multiboot and not allow_multiboot:
            raise BootCompatibilityError("Vista 实验支持仅限单系统，已停止封装；未修改引导项。BCD 备份：{}".format(plan.backup_directory))
        if isolate and plan.multiboot:
            from sysprep.admin_job import dispatch_and_wait
            return dispatch_and_wait(mode, completion_action, answer_file, plan.identifier)
        original_stamp = _success_stamp(sysprep_directory()) if plan.multiboot else None
        action = "quit" if plan.multiboot else completion_action
        if plan.multiboot:
            logger.info("检测到多个系统引导项：先封装并退出，完成当前系统 BCD 核对后再%s。", completion_action)
        cmd = [str(executable), "/generalize", "/audit" if mode == "audit" else "/oobe",
               "/" + action, "/unattend:{}".format(answer_file)]
        if quiet:
            cmd.append("/quiet")
        logger.info("正在执行 Sysprep: %s", " ".join(cmd))
        if plan.multiboot:
            record = (ExecutionRecord(mode, completion_action, plan.backup_directory)
                      if record_directory is None else ExecutionRecord(mode, completion_action, plan.backup_directory,
                                                                       root=record_directory))
            logger.info("独立执行记录：%s", record.path)
        if progress is not None:
            progress("sysprep_running", backupDirectory=str(plan.backup_directory))
        result = run_system_command(cmd, check=True)
        if plan.multiboot:
            report("sysprep_returned", returncode=getattr(result, "returncode", 0))
            new_stamp = _success_stamp(sysprep_directory())
            if new_stamp is None or new_stamp == original_stamp:
                raise BootCompatibilityError("未发现本次 Sysprep 的新成功标记；已取消自动关机/重启。备份：{}".format(plan.backup_directory))
            report("bcd_verifying")
            repair_boot_plan(plan)
            report("bcd_verified")
            logger.info("引导核对完成，备份位于：%s", plan.backup_directory)
            record.update("power_requested" if completion_action != "quit" else "completed")
            complete_power_action(completion_action)
            if completion_action != "quit":
                record.update("power_command_accepted")
        logger.info("Sysprep 执行完成。")
        return {"sysprepSucceeded": True, "bcdVerified": bool(plan.multiboot),
                "backupDirectory": str(plan.backup_directory)}
    except Exception as error:
        if record is not None:
            failed_stage = record.data.get("stage")
            try:
                record.update("failed", failedStage=failed_stage, error=str(error))
            except OSError:
                logger.exception("无法更新执行记录，保留此前阶段。")
        logger.exception("封装或引导处理失败，未继续提交完成动作。")
        logger.info("正在收集 Sysprep 日志到桌面...")
        try:
            log_dir = collect_sysprep_logs()
            if log_dir:
                logger.info("日志已保存到: %s", log_dir)
        except Exception:
            logger.warning("日志收集失败，请手工提取 Panther 日志。", exc_info=True)
        raise
