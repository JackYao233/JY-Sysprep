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
        with patch("builtins.input", return_value=""), patch("sys.stdout", new_callable=io.StringIO):
            self.assertIsNone(collect_configuration(self.context))

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

    def run_main(self, result=None, error=None):
        module = self.load_main()
        adapter = Mock()
        with patch.object(module, "run_preflight", return_value={"passed": True}), \
                patch.object(module, "format_preflight_report", return_value="OK"), \
                patch.object(module, "check_audit_mode", return_value=True), \
                patch.object(module, "detect_system", return_value=self.context), \
                patch.object(module.AdapterFactory, "create", return_value=adapter), \
                patch.object(module, "collect_configuration", return_value=result, side_effect=error) as collect, \
                patch("sys.stdout", new_callable=io.StringIO):
            module.main()
        collect.assert_called_once_with(self.context)
        return adapter

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


if __name__ == "__main__":
    unittest.main()
