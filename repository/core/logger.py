import logging
import os
from datetime import datetime


LOG_DIR = os.path.join(
    os.path.expanduser("~"),
    "Desktop",
    "JY Sysprep Logs"
)


def _setup_logger():
    log = logging.getLogger("JY Sysprep")
    log.setLevel(logging.DEBUG)

    if log.handlers:
        return log

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )
    console_handler.setFormatter(console_fmt)
    log.addHandler(console_handler)

    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(
            os.path.join(LOG_DIR, f"jy_sysprep_{timestamp}.log"),
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(module)s:%(lineno)d] %(message)s"
        )
        file_handler.setFormatter(file_fmt)
        log.addHandler(file_handler)
    except Exception:
        log.warning("无法创建文件日志处理器，仅使用控制台输出。")

    return log


logger = _setup_logger()
