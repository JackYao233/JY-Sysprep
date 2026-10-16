"""Preserve the running Windows loader when generalizing a multiboot PC."""
import ctypes
from dataclasses import dataclass
import json
import logging
import ntpath
import os
from pathlib import Path
import re
import subprocess
import tempfile

from sysprep.paths import system_executable
from utils.system_process import run_system_command


logger = logging.getLogger("JY Sysprep")
GUID = r"\{[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\}"


class BootCompatibilityError(RuntimeError):
    pass


@dataclass
class Loader:
    identifier: str
    values: dict


@dataclass
class BootPlan:
    identifier: str
    drive: str
    system_root: str
    loader_path: str
    multiboot: bool
    backup_directory: Path


def parse_loaders(text):
    """Use stable BCD property names; do not depend on translated headings."""
    loaders = []
    for block in re.split(r"\n[ \t]*\n", text.replace("\r\n", "\n")):
        identifier = None
        values = {}
        for line in block.splitlines():
            if identifier is None:
                match = re.match(r"^\S.*?\s+(" + GUID + r")\s*$", line)
                if match:
                    identifier = match.group(1).lower()
                continue
            if not line or line[0].isspace():
                continue
            fields = line.split(None, 1)
            if len(fields) == 2:
                values[fields[0].lower()] = fields[1].strip()
        path = values.get("path", "").lower()
        if identifier and path.endswith(("\\winload.efi", "\\winload.exe")):
            if identifier in [entry.identifier for entry in loaders]:
                raise BootCompatibilityError("BCD 中出现重复的系统引导标识符，已停止封装。")
            loaders.append(Loader(identifier, values))
    return loaders


def run_bcd(arguments):
    command = [str(system_executable("bcdedit.exe"))] + list(arguments)
    logger.info("BCD: %s", " ".join(command))
    result = run_system_command(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=30)
    def decode(value):
        if isinstance(value, str):
            return value
        if value.startswith((b"\xff\xfe", b"\xfe\xff")):
            return value.decode("utf-16")
        return value.decode("oem", errors="replace")
    output = decode(result.stdout)
    if result.returncode:
        raise BootCompatibilityError("BCD 命令失败：{}".format(decode(result.stderr).strip() or output.strip()))
    return output


def running_windows_directory():
    # Read from Windows itself, not a PE drive letter or a configurable default.
    buffer = ctypes.create_unicode_buffer(32768)
    length = ctypes.windll.kernel32.GetWindowsDirectoryW(buffer, len(buffer))
    if not length or length >= len(buffer):
        raise BootCompatibilityError("无法确定当前运行 Windows 的目录，已停止封装。")
    return buffer.value


def _find_current(text, identifier=None):
    entries = parse_loaders(text)
    if len(entries) != 1 or (identifier and entries[0].identifier != identifier):
        raise BootCompatibilityError("无法唯一识别当前 Windows 引导项，已停止自动处理。")
    return entries[0]


def _check_target(entry, root, loader_path):
    if entry.values.get("systemroot", "").lower() != root.lower():
        raise BootCompatibilityError("BCD 的系统目录与当前 Windows 不匹配，已停止自动处理。")
    if entry.values.get("path", "").lower() != loader_path.lower():
        raise BootCompatibilityError("封装前后引导文件路径变化，已停止自动处理。")


def prepare_boot_plan(backup_root=None):
    directory = ntpath.normpath(running_windows_directory())
    drive, root = ntpath.splitdrive(directory)
    if not re.fullmatch(r"[A-Za-z]:", drive) or not root.startswith("\\"):
        raise BootCompatibilityError("当前 Windows 不是可识别的本地分区安装。")
    drive = drive.upper()
    current_text = run_bcd(["/enum", "{current}", "/v"])
    current = _find_current(current_text)
    loader_path = current.values.get("path", "")
    expected_paths = [ntpath.join(root, "system32", name).lower() for name in ("winload.efi", "winload.exe")]
    if loader_path.lower() not in expected_paths:
        raise BootCompatibilityError("当前引导文件不属于正在运行的 Windows。")
    _check_target(current, root, loader_path)
    # Avoid VHD, ramdisk and other non-partition boot modes.
    for key in ("device", "osdevice"):
        value = current.values.get(key, "").lower()
        if not value.startswith(("partition=", "locate=")):
            raise BootCompatibilityError("当前系统使用不支持的引导设备类型：{}".format(value))
        if re.match(r"partition=[a-z]:$", value) and value != "partition=" + drive.lower():
            raise BootCompatibilityError("当前引导项的分区与运行系统不一致，需手工检查。")
    all_text = run_bcd(["/enum", "osloader", "/v"])
    entries = parse_loaders(all_text)
    if current.identifier not in [entry.identifier for entry in entries]:
        raise BootCompatibilityError("当前 Windows 引导项未出现在系统 BCD 中。")
    installed = [entry for entry in entries if "winpe" not in entry.values
                 and entry.values.get("osdevice", "").lower().startswith(("partition=", "locate="))]
    if backup_root is None:
        backup_root = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "JY Sysprep" / "BootBackups"
    backup_root = Path(backup_root)
    backup_root.mkdir(parents=True, exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix="before-sysprep-", dir=str(backup_root)))
    backup_file = backup / "BCD.backup"
    run_bcd(["/export", str(backup_file)])
    if not backup_file.is_file() or backup_file.stat().st_size == 0:
        raise BootCompatibilityError("BCD 备份文件未生成，已停止封装。")
    plan = BootPlan(current.identifier, drive, root, loader_path, len(installed) > 1, backup)
    (backup / "current-before.txt").write_text(current_text, encoding="utf-8")
    (backup / "loaders-before.txt").write_text(all_text, encoding="utf-8")
    (backup / "plan.json").write_text(json.dumps({
        "identifier": plan.identifier, "drive": drive, "system_root": root,
        "loader_path": loader_path, "multiboot": plan.multiboot,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("BCD 已备份：%s；多系统引导项：%s", backup, plan.multiboot)
    return plan


def repair_boot_plan(plan):
    """Called only after Sysprep /quit; touch two fields in one known loader."""
    try:
        current_text = run_bcd(["/enum", plan.identifier, "/v"])
        current = _find_current(current_text, plan.identifier)
        _check_target(current, plan.system_root, plan.loader_path)
        before_text = run_bcd(["/enum", "osloader", "/v"])
        before = {entry.identifier: entry.values for entry in parse_loaders(before_text)}
        if plan.identifier not in before:
            raise BootCompatibilityError("封装后目标引导项不存在。")
        (plan.backup_directory / "current-after-sysprep.txt").write_text(current_text, encoding="utf-8")
        (plan.backup_directory / "loaders-after-sysprep.txt").write_text(before_text, encoding="utf-8")
        expected = "partition=" + plan.drive
        for key in ("device", "osdevice"):
            if current.values.get(key, "").lower() != expected.lower():
                run_bcd(["/set", plan.identifier, key, expected])
        verified_text = run_bcd(["/enum", plan.identifier, "/v"])
        verified = _find_current(verified_text, plan.identifier)
        _check_target(verified, plan.system_root, plan.loader_path)
        if any(verified.values.get(key, "").lower() != expected.lower() for key in ("device", "osdevice")):
            raise BootCompatibilityError("修复后的分区指向未通过复查。")
        after_text = run_bcd(["/enum", "osloader", "/v"])
        after = {entry.identifier: entry.values for entry in parse_loaders(after_text)}
        expected_values = dict(before[plan.identifier], device=expected, osdevice=expected)
        if set(after) != set(before):
            raise BootCompatibilityError("处理期间引导项列表发生变化。")
        for identifier in before:
            expected_entry = expected_values if identifier == plan.identifier else before[identifier]
            actual_entry = dict(after[identifier])
            expected_entry = dict(expected_entry)
            for key in ("device", "osdevice"):
                if key in actual_entry:
                    actual_entry[key] = actual_entry[key].lower()
                if key in expected_entry:
                    expected_entry[key] = expected_entry[key].lower()
            if actual_entry != expected_entry:
                raise BootCompatibilityError("处理后的引导项出现预期之外的变化。")
        (plan.backup_directory / "loaders-verified.txt").write_text(after_text, encoding="utf-8")
        logger.info("当前系统引导已核对并固定到 %s：%s", plan.drive, plan.identifier)
    except Exception as error:
        raise BootCompatibilityError(
            "多系统引导处理未完成，已取消自动关机/重启。备份：{}。原因：{}".format(plan.backup_directory, error)
        ) from error
