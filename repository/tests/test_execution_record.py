import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sysprep import execution_record as records


class ExecutionRecordTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.object(records, "background_record_paths", return_value=[])
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_process_check_distinguishes_current_dead_and_reused_pid(self):
        self.assertTrue(records.process_alive(os.getpid()))
        self.assertFalse(records.process_alive(2147483646))
        self.assertFalse(records.process_alive(os.getpid(), "2000-01-01T00:00:00.000000Z"))

    def test_interrupted_child_is_detected_but_live_and_terminal_are_ignored(self):
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(records, "record_root", return_value=Path(folder)):
            interrupted = records.ExecutionRecord("oobe", "reboot", "backup")
            successful = records.ExecutionRecord("oobe", "shutdown", "backup")
            successful.update("power_command_accepted")
            live = records.ExecutionRecord("oobe", "quit", "backup")
            live.data["pid"] = 42
            live.update("bcd_verifying")
            with patch.object(records, "process_alive", side_effect=lambda pid, started: pid == 42):
                pending = records.interrupted_records()
            self.assertEqual([item[0] for item in pending], [interrupted.path])
            self.assertEqual(json.loads(interrupted.path.read_text())["stage"], "sysprep_running")
            self.assertFalse(interrupted.path.with_suffix(".tmp").exists())

    def test_failure_keeps_failed_stage_and_error(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(records, "record_root", return_value=Path(folder)):
            record = records.ExecutionRecord("oobe", "quit", "backup")
            record.update("failed", failedStage="bcd_verifying", error="readback failed")
            with patch.object(records, "process_alive", return_value=False):
                data = records.interrupted_records()[0][1]
            self.assertEqual(data["failedStage"], "bcd_verifying")
            self.assertEqual(data["error"], "readback failed")

    def test_notification_is_native_read_only_and_acknowledged_once(self):
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(records, "record_root", return_value=Path(folder)), \
                patch.object(records, "process_alive", return_value=False), \
                patch.object(records.ctypes, "WinDLL") as win_dll:
            user = win_dll.return_value
            user.MessageBoxW.return_value = 1
            record = records.ExecutionRecord("oobe", "reboot", "backup")
            self.assertTrue(records.notify_interrupted())
            self.assertIn(str(record.path), user.MessageBoxW.call_args[0][1])
            self.assertFalse(records.notify_interrupted())
            user.MessageBoxW.assert_called_once()
            win_dll.assert_called_once_with("user32", use_last_error=True)

    def test_modern_check_only_does_not_start_application(self):
        import modern_main
        with patch.object(modern_main.sys, "argv", ["app", "--check-last-run"]), \
                patch.object(records, "notify_interrupted") as notify:
            modern_main.run()
            notify.assert_called_once()
