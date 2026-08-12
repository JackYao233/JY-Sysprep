import os
import shutil
import glob
from datetime import datetime

from core.logger import logger


PANTHER_DIR = os.path.join(
    os.environ.get("WINDIR", r"C:\Windows"),
    "Panther"
)

SYSPREP_LOG_FILES = [
    os.path.join(PANTHER_DIR, "setupact.log"),
    os.path.join(PANTHER_DIR, "setupapi.dev.log"),
    os.path.join(PANTHER_DIR, "setupapi.app.log"),
    os.path.join(PANTHER_DIR, " PantherGC", "*.log"),
]


def collect_sysprep_logs():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_dir = os.path.join(desktop, f"SysprepLogs_{timestamp}")

    try:
        os.makedirs(dest_dir, exist_ok=True)
    except Exception as e:
        logger.error(f"无法创建日志保存目录: {e}")
        return None

    collected = 0

    for pattern in SYSPREP_LOG_FILES:
        for src in glob.glob(pattern):
            if os.path.isfile(src):
                dest = os.path.join(dest_dir, os.path.basename(src))
                try:
                    shutil.copy2(src, dest)
                    collected += 1
                    logger.info(f"已复制日志: {src} -> {dest}")
                except Exception as e:
                    logger.warning(f"复制日志失败 {src}: {e}")

    unattend_gc = os.path.join(PANTHER_DIR, "UnattendGC")
    if os.path.isdir(unattend_gc):
        for src in glob.glob(os.path.join(unattend_gc, "*")):
            if os.path.isfile(src):
                dest = os.path.join(dest_dir, f"UnattendGC_{os.path.basename(src)}")
                try:
                    shutil.copy2(src, dest)
                    collected += 1
                    logger.info(f"已复制日志: {src} -> {dest}")
                except Exception as e:
                    logger.warning(f"复制日志失败 {src}: {e}")

    if collected == 0:
        logger.warning("未找到任何 Sysprep 日志文件。")
        try:
            os.rmdir(dest_dir)
        except Exception:
            pass
        return None

    logger.info(f"共收集 {collected} 个日志文件到: {dest_dir}")
    return dest_dir