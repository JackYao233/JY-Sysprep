import subprocess
from pathlib import Path


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
    subprocess.run(cmd, check=True)
