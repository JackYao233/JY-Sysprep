import ast
import importlib.util
import io
import logging
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from sysprep.config import SysprepConfig
from sysprep.wizard import collect_configuration, format_configuration_summary


ROOT = Path(__file__).resolve().parents[1]


class TuiTests(unittest.TestCase):
    def setUp(self):
        self.context = SimpleNamespace(
            family="Windows 11", supports_wireless_oobe=True,
            supports_online_accounts=True, supports_local_account_screen=False,
        )

    def test_default_confirmation_cancels(self):
        self.context.interface_title = "JY Sysprep Vista GUI experimental"
        with patch("builtins.input", return_value=""), patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertIsNone(collect_configuration(self.context))
        self.assertIn(self.context.interface_title, output.getvalue())

    def test_latest_choices_are_shown_before_confirmation(self):
        answers = iter([
            "n", "oobe", "quit", "JY-PC", "UTC", "en",
            "n", "n", "y", "y", "Owner", "Company", "n", "y",
        ])
        def answer(prompt):
            if prompt.startswith("确认"):
                output = captured.getvalue()
                self.assertIn("正式执行 Sysprep /generalize", output)
                self.assertIn("封装后启动模式：oobe", output)
                self.assertIn("计算机名：JY-PC", output)
                self.assertIn("隐藏在线账户页面：是", output)
                self.assertIn("显示语言：en-US", output)
            return next(answers)

        with patch("sys.stdout", new_callable=io.StringIO) as captured, patch("builtins.input", side_effect=answer):
            config = collect_configuration(self.context)
        self.assertFalse(config.test_only)
        self.assertEqual(config.completion_action, "quit")
        self.assertEqual(config.computer_name, "JY-PC")

    def test_password_is_not_in_summary(self):
        config = SysprepConfig(admin_username="Admin", admin_password="secret-value", auto_logon=True)
        summary = format_configuration_summary(config, self.context)
        self.assertIn("Admin", summary)
        self.assertIn("自动登录次数：1", summary)
        self.assertNotIn("secret-value", summary)

    def load_main(self):
        # Replace logger before importing so checks do not create desktop logs.
        logger_module = ModuleType("core.logger")
        logger_module.logger = logging.getLogger("tui-tests")
        spec = importlib.util.spec_from_file_location("tui_main_under_test", ROOT / "main.py")
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"core.logger": logger_module}):
            spec.loader.exec_module(module)
        return module

    def run_main(self, result=None, error=None, interface="tui", gui=None, gui_error=None, audit=True):
        module = self.load_main()
        adapter = Mock()
        with patch.object(module, "run_preflight", return_value={"passed": True}), \
                patch.object(module, "select_interface", return_value=interface), \
                patch.object(module, "create_gui", return_value=gui, side_effect=gui_error), \
                patch.object(module, "format_preflight_report", return_value="OK"), \
                patch.object(module, "check_audit_mode", return_value=audit), \
                patch.object(module, "detect_system", return_value=self.context), \
                patch.object(module.AdapterFactory, "create", return_value=adapter), \
                patch.object(module, "collect_configuration", return_value=result, side_effect=error) as collect, \
                patch("sys.stdout", new_callable=io.StringIO):
            module.main()
        if not audit or (interface == "gui" and gui_error is None and not gui.request_tui):
            collect.assert_not_called()
        else:
            collect.assert_called_once()
            self.assertIs(collect.call_args[0][0], self.context)
            if interface == "gui" and gui_error is None:
                self.assertIs(collect.call_args[0][1], gui.config)
        return adapter

    def test_gui_close_does_not_start_tui_or_execute(self):
        gui = Mock(request_tui=False)
        adapter = self.run_main(interface="gui", gui=gui)
        gui.run.assert_called_once()
        self.assertEqual(adapter.mock_calls, [])

    def test_gui_handoff_preserves_configuration(self):
        config = SysprepConfig(computer_name="GUI-PC")
        gui = Mock(request_tui=True, config=config)
        adapter = self.run_main(interface="gui", gui=gui, result=config)
        self.assertIs(self.context.sysprep_config, config)
        adapter.generate_unattend.assert_called_once()

    def test_missing_gui_falls_back_to_tui(self):
        adapter = self.run_main(interface="gui", gui_error=ImportError("No Tk"))
        self.assertEqual(adapter.mock_calls, [])

    def test_invalid_environment_gui_does_not_execute(self):
        gui = Mock(request_tui=False)
        adapter = self.run_main(interface="gui", gui=gui, audit=False)
        gui.run.assert_called_once()
        self.assertEqual(adapter.mock_calls, [])

    def test_entry_calls_text_wizard_and_adapter(self):
        config = SysprepConfig()
        adapter = self.run_main(result=config)
        self.assertIs(self.context.sysprep_config, config)
        self.assertEqual([call[0] for call in adapter.mock_calls], ["prepare", "generate_unattend", "cleanup"])

    def test_cancel_and_interrupted_input_do_not_execute(self):
        for error in (None, KeyboardInterrupt(), EOFError()):
            with self.subTest(error=type(error).__name__):
                adapter = self.run_main(error=error)
                self.assertEqual(adapter.mock_calls, [])

    def test_entry_has_no_gui_imports(self):
        tree = ast.parse((ROOT / "main.py").read_text(encoding="utf-8"))
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
        self.assertFalse(any(name.startswith(("gui", "tkinter")) for name in imports))

    def test_gui_exit_does_not_pause_console(self):
        module = self.load_main()
        with patch.object(module, "main", return_value="gui"), \
                patch("sys.stdin.isatty", return_value=True), patch("builtins.input") as prompt:
            module.run_application()
        prompt.assert_not_called()

    def test_tui_exit_keeps_console_pause(self):
        module = self.load_main()
        with patch.object(module, "main", return_value="tui"), \
                patch("sys.stdin.isatty", return_value=True), patch("builtins.input") as prompt:
            module.run_application()
        prompt.assert_called_once()

    def test_redirected_tui_exit_does_not_wait_for_input(self):
        module = self.load_main()
        with patch.object(module, "main", return_value="tui"), \
                patch("sys.stdin.isatty", return_value=False), patch("builtins.input") as prompt:
            module.run_application()
        prompt.assert_not_called()

    def test_interrupted_exit_prompt_is_handled(self):
        module = self.load_main()
        for error in (KeyboardInterrupt(), EOFError()):
            with self.subTest(error=type(error).__name__), \
                    patch.object(module, "main", return_value="tui"), \
                    patch("sys.stdin.isatty", return_value=True), patch("builtins.input", side_effect=error):
                module.run_application()


if __name__ == "__main__":
    unittest.main()
