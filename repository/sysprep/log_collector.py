from pathlib import Path
import shutil
import tempfile

from core.logger import logger
from sysprep.paths import windows_directory


def collect_sysprep_logs(windir=None, destination_root=None):
    windows = Path(windir) if windir is not None else windows_directory()
    root = Path(destination_root) if destination_root is not None else Path.home() / "Desktop"
    try:
        root.mkdir(parents=True, exist_ok=True)
        destination = Path(tempfile.mkdtemp(prefix="SysprepLogs_", dir=str(root)))
    except OSError as error:
        logger.warning("无法创建日志目录：%s", error)
        return None
    locations = [
        (windows / "System32" / "Sysprep" / "Panther", Path("Sysprep") / "Panther"),
        (windows / "Panther", Path("Panther")),
        (windows / "Panther" / "UnattendGC", Path("Panther") / "UnattendGC"),
    ]
    collected = 0
    for source_directory, relative in locations:
        if not source_directory.is_dir():
            continue
        for source in source_directory.glob("*.log"):
            if not source.is_file():
                continue
            target = destination / relative / source.name
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(source), str(target))
                collected += 1
            except OSError as error:
                logger.warning("日志复制失败 %s：%s", source, error)
    if not collected:
        logger.warning("未找到可收集的 Sysprep/Windows Setup 日志。")
        try:
            destination.rmdir()
        except OSError:
            pass
        return None
    logger.info("已收集 %s 个日志文件：%s", collected, destination)
    return str(destination)
