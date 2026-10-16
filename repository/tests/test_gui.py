import time
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from sysprep.config import SysprepConfig

try:
    import tkinter as tk
    from gui.app import SysprepWizardApp
except ImportError:
    tk = None


@unittest.skipIf(tk is None, "Tkinter unavailable")
class GuiTests(unittest.TestCase):
    def setUp(self):
        real_tk = tk.Tk

        def hidden_root():
            root = real_tk()
            root.withdraw()
            return root

        self.context = SimpleNamespace(
            family="Windows 11", product_name="Windows 11 Pro", display_version="25H2",
            build="26200", edition="Professional", arch="AMD64", nt_version="10.0",
            installation_type="Client", is_admin=True,
            supports_wireless_oobe=True, supports_online_accounts=True,
            supports_local_account_screen=False,
        )
        self.config = SysprepConfig()
        self.callback = Mock(return_value="test-output.xml")
        with patch("gui.app.tk.Tk", side_effect=hidden_root):
            self.app = SysprepWizardApp(self.context, {"passed": True, "checks": []},
                                        self.config, self.callback)
        self.app.root.update_idletasks()
        self.addCleanup(self.destroy_root)

    def destroy_root(self):
        try:
            self.app.root.update_idletasks()
            self.app.root.destroy()
        except tk.TclError:
            pass

    def test_summary_refreshes_after_navigation_and_edits(self):
        self.app._next()
        basic = self.app._pages_list[1]
        basic.var_computer_name.set("NEW-PC")
        basic.var_test_only.set(False)
        basic.var_mode.set("oobe")
        for unused in range(4):
            self.app._next()
        confirm = self.app._pages_list[-1]
        self.assertIn("计算机名：NEW-PC", confirm.summary.get())
        self.assertIn("正式执行", confirm.summary.get())
        self.assertEqual(confirm.btn_execute.cget("text"), "生成应答文件并执行 Sysprep")
        self.app._go_to(1)
        basic.var_computer_name.set("EDITED-PC")
        for unused in range(4):
            self.app._next()
        self.assertIn("计算机名：EDITED-PC", confirm.summary.get())

    def test_backward_navigation_saves_input(self):
        self.app._next()
        self.app._pages_list[1].var_computer_name.set("SAVED-PC")
        self.app._prev()
        self.assertEqual(self.config.computer_name, "SAVED-PC")

    def test_invalid_input_does_not_partly_update_config(self):
        self.app._next()
        basic = self.app._pages_list[1]
        basic.var_computer_name.set("invalid name")
        basic.var_test_only.set(False)
        with patch("gui.app.messagebox.showwarning"):
            self.app._next()
        self.assertEqual(self.app.current_index, 1)
        self.assertTrue(self.config.test_only)
        self.assertEqual(self.config.computer_name, "*")

    def test_invalid_account_count_does_not_change_config(self):
        account = self.app._pages_list[4]
        account.var_create_admin.set(True)
        account.var_username.set("Admin")
        account.var_password.set("example-only")
        account.var_auto_logon.set(True)
        account.var_logon_count.set("0")
        self.assertFalse(account.collect()[0])
        self.assertIsNone(self.config.admin_username)
        self.assertIsNone(self.config.admin_password)

    def test_f8_switch_saves_current_page_and_does_not_execute(self):
        self.assertTrue(self.app.root.bind("<F8>"))
        self.app._next()
        self.app._pages_list[1].var_computer_name.set("TUI-PC")
        self.app._switch_to_tui()
        self.assertTrue(self.app.request_tui)
        self.assertEqual(self.config.computer_name, "TUI-PC")
        self.callback.assert_not_called()

    def test_formal_confirmation_cancel_does_not_execute(self):
        self.app._show_page(5)
        self.config.test_only = False
        with patch("gui.app.messagebox.askyesno", return_value=False):
            self.app._execute()
        self.callback.assert_not_called()
        self.assertFalse(self.app.busy)

    def test_failed_preflight_cannot_advance_or_execute(self):
        self.app.preflight["passed"] = False
        self.app._next()
        self.assertEqual(self.app.current_index, 0)
        self.app._show_page(5)
        with patch("gui.app.messagebox.showerror"):
            self.app._execute()
        self.callback.assert_not_called()

    def test_background_success_or_failure_cannot_execute_twice(self):
        for failure in (False, True):
            with self.subTest(failure=failure):
                self.app.execution_started = False
                self.callback.reset_mock()
                self.callback.side_effect = RuntimeError("test failure") if failure else None
                self.app._show_page(5)
                with patch("gui.app.messagebox.showinfo"), patch("gui.app.messagebox.showerror"):
                    self.app._execute()
                    self.app._execute()
                    self.app._switch_to_tui()
                    deadline = time.monotonic() + 3
                    while self.app.busy and time.monotonic() < deadline:
                        self.app.root.update()
                        time.sleep(0.01)
                self.assertFalse(self.app.busy)
                self.assertFalse(self.app.request_tui)
                self.callback.assert_called_once()
                status = self.app._pages_list[-1].status.get()
                self.assertIn("test failure" if failure else "test-output.xml", status)

    def test_all_pages_have_scrollable_content(self):
        for index in range(6):
            self.app._show_page(index)
            self.app.root.update_idletasks()
            self.assertIsNotNone(self.app.canvas.bbox("all"))

    def test_gui_loop_exit_waits_for_execution_to_finish(self):
        release = threading.Event()
        finished = threading.Event()
        def execute(config):
            if not release.wait(3):
                raise RuntimeError("Test execution was not released")
            finished.set()
            return "test-output.xml"
        self.app.on_finish = execute
        self.app._show_page(5)
        self.app._execute()
        self.assertFalse(self.app._worker_thread.daemon)
        # Reproduce a Tk event-loop exit while the execution is still in flight.
        with patch.object(self.app.root, "mainloop", side_effect=release.set):
            self.app.run()
        self.assertTrue(finished.is_set())
        self.assertFalse(self.app._worker_thread.is_alive())
        self.assertEqual(self.app._results.get_nowait(), (True, "test-output.xml"))

    def test_vista_pages_disable_unsupported_options_and_preserve_f8_config(self):
        self.destroy_root()
        self.context.family = "Windows Vista"
        self.context.interface_title = "Vista GUI test"
        self.context.supports_wireless_oobe = False
        self.context.supports_online_accounts = False
        self.app = SysprepWizardApp(self.context, {"passed": True, "checks": []},
                                    self.config, self.callback, visible=False)
        self.assertEqual(self.app.root.title(), "Vista GUI test")
        for index in range(6):
            self.app._show_page(index)
            self.app.root.update_idletasks()
        oobe = self.app._pages_list[3]
        for widget in (oobe.cb_wireless, oobe.cb_online, oobe.cb_local):
            self.assertEqual(str(widget.cget("state")), "disabled")
        self.app._show_page(1)
        self.app._pages_list[1].var_computer_name.set("VISTA-PC")
        self.app._switch_to_tui()
        self.assertEqual(self.config.computer_name, "VISTA-PC")
        self.assertTrue(self.app.request_tui)
        self.callback.assert_not_called()

    def test_font_fallback_accepts_vista_chinese_font(self):
        from gui.styles import setup_fonts, FONT_BODY
        with patch("tkinter.font.families", return_value=("Microsoft YaHei",)):
            self.assertEqual(setup_fonts(self.app.root), "Microsoft YaHei")
        self.assertEqual(FONT_BODY[0], "Microsoft YaHei")

    def test_readonly_gui_diagnostic_checks_pages_and_tui_handoff(self):
        from gui.diagnostics import check_gui
        with patch("subprocess.run") as run, patch("pathlib.Path.write_text") as write:
            report = check_gui()
        self.assertTrue(report["guiSmokeCheckPassed"])
        self.assertEqual(report["guiPagesChecked"], 6)
        self.assertTrue(report["guiToTuiHandoffChecked"])
        run.assert_not_called()
        write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
