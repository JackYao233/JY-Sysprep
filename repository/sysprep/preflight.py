import os
from pathlib import Path

from core.logger import logger


ACTION_FILES = ["Generalize.xml", "Specialize.xml", "Cleanup.xml", "Respecialize.xml"]


def run_preflight(unattend_path=None):
    windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
    sysprep_dir = windir / "System32" / "Sysprep"
    panther_dir = windir / "Panther"

    checks = []

    sysprep_exe = sysprep_dir / "sysprep.exe"
    checks.append({
        "name": "sysprep.exe",
        "ok": sysprep_exe.is_file(),
        "critical": True,
        "path": str(sysprep_exe),
    })

    checks.append({
        "name": "Panther 目录",
        "ok": panther_dir.is_dir(),
        "critical": True,
        "path": str(panther_dir),
    })

    action_files_dir = sysprep_dir / "ActionFiles"
    if action_files_dir.is_dir():
        checks.append({
            "name": "Sysprep ActionFiles 目录",
            "ok": True,
            "critical": False,
            "path": str(action_files_dir),
        })
        for af in ACTION_FILES:
            af_path = action_files_dir / af
            checks.append({
                "name": f"ActionFile: {af}",
                "ok": af_path.is_file(),
                "critical": True,
                "path": str(af_path),
            })
    else:
        checks.append({
            "name": "Sysprep ActionFiles 目录",
            "ok": True,
            "critical": False,
            "path": str(action_files_dir),
        })

    if unattend_path:
        checks.append({
            "name": "应答文件",
            "ok": Path(unattend_path).is_file(),
            "critical": True,
            "path": unattend_path,
        })

    failed = [c for c in checks if not c["ok"]]
    critical_failed = [c for c in failed if c["critical"]]

    return {
        "passed": len(critical_failed) == 0,
        "checks": checks,
        "failed": failed,
        "critical_failed": critical_failed,
    }


def format_preflight_report(result):
    lines = ["===== Sysprep 预检结果 ====="]
    for c in result["checks"]:
        status = "✓" if c["ok"] else "✗"
        tag = "[关键]" if c["critical"] else "[信息]"
        lines.append(f"  {status} {tag} {c['name']}")
        if not c["ok"]:
            lines.append(f"       路径: {c['path']}")
    if result["passed"]:
        lines.append("预检通过，可以执行 Sysprep。")
    else:
        lines.append(f"预检失败！{len(result['critical_failed'])} 项关键检查未通过。")
    return "\n".join(lines)