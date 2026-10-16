"""Read-only GUI smoke check; uses fixture data, never detects or prepares the OS."""
from types import SimpleNamespace


def diagnostic_context():
    return SimpleNamespace(
        family="Windows Vista", product_name="Vista GUI diagnostic context",
        display_version="SP2", build="6002", edition="Diagnostic", arch="AMD64",
        nt_version="6.0", installation_type="Client", is_admin=False,
        supports_wireless_oobe=False, supports_online_accounts=False,
        supports_local_account_screen=False, interface_title="JY Sysprep GUI self-test",
    )


def check_gui():
    from tkinter import TclError
    from gui.app import SysprepWizardApp
    from sysprep.config import SysprepConfig

    context = diagnostic_context()
    checks = [{"name": "只读 GUI 自检，禁止封装", "ok": False, "critical": True, "path": "诊断数据"}]
    preflight = {"passed": False, "checks": checks, "critical_failed": checks}

    def forbidden_execution(config):
        raise RuntimeError("GUI self-test must never execute a workflow")

    app = SysprepWizardApp(context, preflight, SysprepConfig(),
                           on_finish=forbidden_execution, visible=False)
    try:
        for index in range(len(app._pages_list)):
            app._show_page(index)
            app.root.update_idletasks()
        oobe = app._pages_list[3]
        if not all(str(widget.cget("state")) == "disabled"
                   for widget in (oobe.cb_wireless, oobe.cb_online, oobe.cb_local)):
            raise RuntimeError("Unsupported Vista OOBE controls were enabled")
        report = {"guiSmokeCheckPassed": True, "guiUsesDiagnosticContext": True,
                  "guiPagesChecked": len(app._pages_list), "fontFamily": app.font_family,
                  "tclVersion": app.root.tk.call("info", "patchlevel"),
                  "tkVersion": app.root.tk.call("package", "provide", "Tk")}
        app._switch_to_tui()
        if not app.request_tui:
            raise RuntimeError("GUI to TUI handoff check failed")
        report["guiToTuiHandoffChecked"] = True
        return report
    finally:
        try:
            app.root.destroy()
        except TclError:
            pass


def check_execution_lifetime():
    """Leave the hidden GUI loop during a fake task; never executes an adapter."""
    import threading
    from tkinter import TclError
    from gui.app import SysprepWizardApp
    from sysprep.config import SysprepConfig
    release = threading.Event()
    finished = threading.Event()
    def fake_execution(config):
        if not release.wait(5):
            raise RuntimeError("Diagnostic task release timed out")
        finished.set()
        return "diagnostic-no-output"
    app = SysprepWizardApp(diagnostic_context(), {"passed": True, "checks": []},
                           SysprepConfig(test_only=True), on_finish=fake_execution, visible=False)
    try:
        app._show_page(5)
        app._execute()
        def leave_loop():
            app.root.quit()
            release.set()
        app.root.after(0, leave_loop)
        app.run()
        passed = (not app._worker_thread.daemon and finished.is_set()
                  and not app._worker_thread.is_alive())
        if not passed:
            raise RuntimeError("GUI exit abandoned the diagnostic task")
        return {"guiExitWaitsForExecution": True, "executionThreadDaemon": False,
                "diagnosticTaskOnly": True}
    finally:
        release.set()
        if app._worker_thread is not None:
            app._worker_thread.join()
        try:
            app.root.destroy()
        except TclError:
            pass
