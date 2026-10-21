import os
import subprocess
import unittest
from unittest.mock import patch, Mock, call

from utils import system_process


class SystemProcessTests(unittest.TestCase):
    def test_path_cleanup_preserves_system_entries_and_input(self):
        environment = {"Path": r'C:\Windows\System32;"C:\bundle";C:\bundle\bin;C:\bundle-other', "OTHER": "keep"}
        result = system_process.clean_child_environment(environment, r"C:\bundle")
        self.assertEqual(result["Path"], r"C:\Windows\System32;C:\bundle-other")
        self.assertEqual(result["OTHER"], "keep")
        self.assertIn(r'C:\bundle\bin', environment["Path"])

    def test_dll_search_restored_after_child_failure(self):
        kernel = Mock()
        def get_directory(size, buffer):
            buffer.value = r"C:\bundle"
            return len(buffer.value)
        kernel.GetDllDirectoryW.side_effect = get_directory
        kernel.SetDllDirectoryW.return_value = True
        with patch.object(system_process.ctypes, "WinDLL", return_value=kernel):
            with self.assertRaises(RuntimeError):
                with system_process.system_dll_search():
                    raise RuntimeError("child failed")
        self.assertEqual(kernel.SetDllDirectoryW.call_args_list, [call(None), call(r"C:\bundle")])

    def test_frozen_system_command_receives_clean_environment(self):
        kernel = Mock()
        kernel.GetDllDirectoryW.return_value = 0
        kernel.SetDllDirectoryW.return_value = True
        with patch.object(system_process.sys, "frozen", True, create=True), \
                patch.object(system_process.sys, "_MEIPASS", r"C:\bundle", create=True), \
                patch.object(system_process.ctypes, "WinDLL", return_value=kernel), \
                patch.object(system_process.subprocess, "run") as run:
            system_process.run_system_command(["test-system.exe"], check=True,
                env={"PATH": r"C:\bundle;C:\Windows\System32"})
        self.assertEqual(run.call_args[1]["env"]["PATH"], r"C:\Windows\System32")
        self.assertTrue(run.call_args[1]["check"])

    def test_reset_failure_does_not_run_child(self):
        kernel = Mock()
        kernel.GetDllDirectoryW.return_value = 0
        kernel.SetDllDirectoryW.return_value = False
        with patch.object(system_process.sys, "frozen", True, create=True), \
                patch.object(system_process.sys, "_MEIPASS", r"C:\bundle", create=True), \
                patch.object(system_process.ctypes, "WinDLL", return_value=kernel), \
                patch.object(system_process.subprocess, "run") as run:
            with self.assertRaises(OSError):
                system_process.run_system_command(["test-system.exe"])
        run.assert_not_called()
