"""Read-only current-host profile and GUI check using the Vista Python runtime."""
import json
import logging
from pathlib import Path
import sys
from types import ModuleType
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def check():
    # Import shared detection without the normal desktop log-file handler.
    logger = ModuleType("core.logger")
    logger.logger = logging.getLogger("merge-readonly-check")
    with patch.dict(sys.modules, {"core.logger": logger}):
        from main import detect_system
        from sysprep.factory import AdapterFactory
    from gui.app import SysprepWizardApp
    from sysprep.config import SysprepConfig

    context = detect_system()
    adapter = AdapterFactory.create(context)
    checks = [{"name": "只读合并评估，禁止封装", "ok": False, "critical": True, "path": "诊断"}]
    app = SysprepWizardApp(context, {"passed": False, "checks": checks, "critical_failed": checks},
                           SysprepConfig(), on_finish=None, visible=False)
    try:
        for index in range(6):
            app._show_page(index)
            app.root.update_idletasks()
        report = {
            "python": sys.version.split()[0], "detectedFamily": context.family,
            "detectedBuild": context.build, "architecture": context.arch,
            "selectedAdapter": type(adapter).__name__ if adapter else None,
            "sharedGuiPagesChecked": 6, "tkVersion": app.root.tk.call("package", "provide", "Tk"),
            "fontFamily": app.font_family, "sysprepExecuted": False,
            "bcdReadOrModified": False, "crossVersionDeploymentValidated": False,
        }
    finally:
        app.root.update_idletasks()
        app.root.destroy()
    (ROOT / "docs/MERGE-FEASIBILITY-CHECK.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    check()
