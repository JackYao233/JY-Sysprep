import subprocess
from pathlib import Path

from core.logger import logger
from sysprep.log_collector import collect_sysprep_logs


class SysprepPreflightError(RuntimeError):
    def __init__(self, message, preflight_result):
        super().__init__(message)
        self.preflight_result = preflight_result


def run_sysprep(mode="audit", completion_action="shutdown", unattend_path=None):
    executable = Path(r"C:\Windows\System32\Sysprep\sysprep.exe")
    answer_file = Path(unattend_path or r"C:\Windows\System32\Sysprep\unattend.xml")
    if not executable.is_file():
        raise FileNotFoundError(f"找不到 Sysprep：{executable}")
    if not answer_file.is_file():
        raise FileNotFoundError(f"找不到应答文件：{answer_file}")

    cmd = [str(executable), "/generalize", "/audit" if mode == "audit" else "/oobe"]
    if completion_action == "shutdown":
        cmd.append("/shutdown")
    elif completion_action == "reboot":
        cmd.append("/reboot")
    elif completion_action == "quit":
        cmd.append("/quit")
    else:
        raise ValueError("完成后的动作必须是 shutdown、reboot 或 quit。")
    cmd.append(f"/unattend:{answer_file}")

    logger.info(f"正在执行 Sysprep: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        logger.info("Sysprep 执行完成。")
    except subprocess.CalledProcessError as e:
        logger.error(f"Sysprep 执行失败，返回码: {e.returncode}")
        logger.info("正在收集 Sysprep 日志到桌面...")
        log_dir = collect_sysprep_logs()
        if log_dir:
            logger.info(f"日志已保存到: {log_dir}")
        else:
            logger.warning("未能收集到 Sysprep 日志。")
        raise
