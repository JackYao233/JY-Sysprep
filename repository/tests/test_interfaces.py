import io
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from core.interface import select_interface
from sysprep.config import SysprepConfig
from sysprep.wizard import collect_configuration


class InterfaceTests(unittest.TestCase):
    def test_gui_import_failure_is_available_for_fallback(self):
        from core.interface import create_gui
        with patch.dict(sys.modules, {"gui.app": None}):
            with self.assertRaises(ImportError):
                create_gui(None, None, None, None)

    def test_explicit_modes_do_not_probe_console(self):
        with patch("sys.stdin.isatty", side_effect=AssertionError("console probed")):
            self.assertEqual(select_interface(["--tui"]), "tui")
            self.assertEqual(select_interface(["--gui"]), "gui")

    def test_non_console_defaults_to_gui(self):
        with patch("sys.stdin.isatty", return_value=False):
            self.assertEqual(select_interface([]), "gui")

    def test_startup_f8_selects_tui(self):
        console = Mock()
        console.kbhit.return_value = True
        console.getwch.side_effect = ["\xe0", "B"]
        with patch.dict(sys.modules, {"msvcrt": console}), \
                patch("sys.platform", "win32"), patch("sys.stdin.isatty", return_value=True), \
                patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(select_interface([], timeout=1), "tui")

    def test_tui_preserves_previous_defaults_without_mutating_source(self):
        context = SimpleNamespace(family="Windows 11", supports_wireless_oobe=True,
                                  supports_online_accounts=True, supports_local_account_screen=False)
        initial = SysprepConfig(computer_name="FROM-GUI", ui_language="en-US", user_locale="en-US",
                                system_locale="en-US", input_locale="en-US", owner="Owner")
        with patch("builtins.input", return_value=""), patch("sys.stdout", new_callable=io.StringIO) as output:
            result = collect_configuration(context, initial)
        self.assertIsNone(result)
        self.assertEqual(initial.computer_name, "FROM-GUI")
        self.assertIn("计算机名：FROM-GUI", output.getvalue())
        self.assertIn("显示语言：en-US", output.getvalue())


if __name__ == "__main__":
    unittest.main()
