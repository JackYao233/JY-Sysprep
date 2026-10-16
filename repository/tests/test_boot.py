import logging
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

from sysprep.boot import (BootCompatibilityError, BootPlan, parse_loaders,
                          prepare_boot_plan, repair_boot_plan, run_bcd)


CURRENT = "{11111111-1111-1111-1111-111111111111}"
OTHER = "{22222222-2222-2222-2222-222222222222}"
RECOVERY = "{33333333-3333-3333-3333-333333333333}"


def entry(identifier=CURRENT, drive="D:", locate=False, winpe=False):
    device = "locate=custom:12000002" if locate else "partition=" + drive
    osdevice = "locate=custom:22000002" if locate else "partition=" + drive
    if winpe:
        device = osdevice = "ramdisk=[D:]\\Recovery\\winre.wim,{44444444-4444-4444-4444-444444444444}"
    return ("Windows 启动加载器\n----------------\n标识符                  " + identifier +
            "\ndevice                  " + device +
            "\npath                    \\Windows\\system32\\winload.efi" +
            "\ndescription             Windows test" +
            "\nosdevice                " + osdevice +
            "\nsystemroot              \\Windows" + ("\nwinpe                   Yes" if winpe else "") + "\n")


class BootTests(unittest.TestCase):
    def test_localized_headings_and_recovery_parse(self):
        parsed = parse_loaders(entry() + "\n" + entry(OTHER, "F:") + "\n" + entry(RECOVERY, winpe=True))
        self.assertEqual([loader.identifier for loader in parsed], [CURRENT, OTHER, RECOVERY])

    def test_duplicate_identifier_rejected(self):
        with self.assertRaises(BootCompatibilityError):
            parse_loaders(entry() + "\n" + entry())

    def prepare(self, folder, loaders):
        def bcd(args):
            if args[0] == "/export":
                Path(args[1]).write_bytes(b"test BCD backup")
                return ""
            return entry() if args[1] == "{current}" else loaders
        with patch("sysprep.boot.running_windows_directory", return_value="D:\\Windows"), \
                patch("sysprep.boot.run_bcd", side_effect=bcd):
            return prepare_boot_plan(folder)

    def test_backup_and_multiboot_detection_use_actual_drive(self):
        with tempfile.TemporaryDirectory() as folder:
            plan = self.prepare(folder, entry() + "\n" + entry(OTHER, "F:"))
            self.assertTrue(plan.multiboot)
            self.assertEqual(plan.drive, "D:")
            self.assertEqual(plan.identifier, CURRENT)
            self.assertTrue((plan.backup_directory / "BCD.backup").is_file())
            self.assertTrue((plan.backup_directory / "plan.json").is_file())

    def test_recovery_loader_does_not_make_single_system_multiboot(self):
        with tempfile.TemporaryDirectory() as folder:
            plan = self.prepare(folder, entry() + "\n" + entry(RECOVERY, winpe=True))
            self.assertFalse(plan.multiboot)

    def test_backup_not_created_stops_before_sysprep(self):
        def bcd(args):
            return "" if args[0] == "/export" else entry()
        with tempfile.TemporaryDirectory() as folder, \
                patch("sysprep.boot.running_windows_directory", return_value="D:\\Windows"), \
                patch("sysprep.boot.run_bcd", side_effect=bcd):
            with self.assertRaises(BootCompatibilityError):
                prepare_boot_plan(folder)

    def test_different_fixed_partition_is_rejected(self):
        with patch("sysprep.boot.running_windows_directory", return_value="D:\\Windows"), \
                patch("sysprep.boot.run_bcd", return_value=entry(drive="C:")) as command:
            with self.assertRaises(BootCompatibilityError):
                prepare_boot_plan()
        command.assert_called_once()

    def test_unsupported_vhd_or_missing_current_is_rejected(self):
        for text in ("", entry().replace("partition=D:", "vhd=[C:]\\test.vhdx")):
            with self.subTest(text=text), \
                    patch("sysprep.boot.running_windows_directory", return_value="D:\\Windows"), \
                    patch("sysprep.boot.run_bcd", return_value=text):
                with self.assertRaises(BootCompatibilityError):
                    prepare_boot_plan()

    def test_repair_only_changes_selected_loader_and_verifies(self):
        with tempfile.TemporaryDirectory() as folder:
            plan = BootPlan(CURRENT, "D:", "\\Windows", "\\Windows\\system32\\winload.efi", True, Path(folder))
            values = {"device": "locate=custom:12000002", "osdevice": "locate=custom:22000002"}
            commands = []
            def render():
                return entry(locate=True).replace("locate=custom:12000002", values["device"]).replace("locate=custom:22000002", values["osdevice"])
            def bcd(args):
                commands.append(args)
                if args[0] == "/set":
                    self.assertEqual(args[1], CURRENT)
                    values[args[2]] = args[3]
                    return ""
                return render() + ("\n" + entry(OTHER, "F:") if args[1] == "osloader" else "")
            with patch("sysprep.boot.run_bcd", side_effect=bcd):
                repair_boot_plan(plan)
            self.assertEqual([command for command in commands if command[0] == "/set"], [
                ["/set", CURRENT, "device", "partition=D:"],
                ["/set", CURRENT, "osdevice", "partition=D:"],
            ])
            self.assertTrue((Path(folder) / "loaders-verified.txt").is_file())

    def test_repair_wrong_identifier_or_failed_readback_stops(self):
        with tempfile.TemporaryDirectory() as folder:
            plan = BootPlan(CURRENT, "D:", "\\Windows", "\\Windows\\system32\\winload.efi", True, Path(folder))
            for text in (entry(OTHER), entry(locate=True)):
                with patch("sysprep.boot.run_bcd", return_value=text), self.subTest(text=text):
                    with self.assertRaises(BootCompatibilityError):
                        repair_boot_plan(plan)

    def test_bcd_command_failure_propagates(self):
        result = SimpleNamespace(returncode=1, stdout=b"BCD failed", stderr=b"")
        with patch("sysprep.boot.subprocess.run", return_value=result):
            with self.assertRaises(BootCompatibilityError):
                run_bcd(["/enum", "{current}", "/v"])


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        logger_module = ModuleType("core.logger")
        logger_module.logger = logging.getLogger("execution-tests")
        logger_module.logger.addHandler(logging.NullHandler())
        with patch.dict(sys.modules, {"core.logger": logger_module}):
            from sysprep import executor
        self.executor = executor
        record_patch = patch.object(executor, "ExecutionRecord")
        self.record_factory = record_patch.start()
        self.addCleanup(record_patch.stop)

    def run_flow(self, multiboot=True, action="reboot", repair_error=None, sysprep_error=None, stamps=None):
        plan = SimpleNamespace(multiboot=multiboot, backup_directory=Path("test-backup"))
        events = []
        def run(args, **kwargs):
            events.append(("run", args))
            if sysprep_error:
                raise sysprep_error
        def repair(selected):
            self.assertIs(selected, plan)
            events.append(("repair", None))
            if repair_error:
                raise repair_error
        with patch.object(self.executor.Path, "is_file", return_value=True), \
                patch.object(self.executor, "prepare_boot_plan", return_value=plan), \
                patch.object(self.executor, "_success_stamp", side_effect=stamps or [(1, 1), (2, 2)]), \
                patch.object(self.executor, "repair_boot_plan", side_effect=repair), \
                patch.object(self.executor.subprocess, "run", side_effect=run), \
                patch.object(self.executor, "collect_sysprep_logs", return_value=None):
            self.executor.run_sysprep("oobe", action, "test-answer.xml")
        return events

    def test_multiboot_quit_then_repair_then_reboot(self):
        events = self.run_flow()
        self.assertEqual([event[0] for event in events], ["run", "repair", "run"])
        self.assertIn("/quit", events[0][1])
        self.assertNotIn("/reboot", events[0][1])
        self.assertEqual(events[2][1][-3:], ["/r", "/t", "0"])

    def test_multiboot_shutdown_and_quit_choices(self):
        events = self.run_flow(action="shutdown")
        self.assertEqual(events[-1][1][-3:], ["/s", "/t", "0"])
        events = self.run_flow(action="quit")
        self.assertEqual([event[0] for event in events], ["run", "repair"])

    def test_single_system_keeps_original_sysprep_action(self):
        events = self.run_flow(multiboot=False)
        self.assertEqual(len(events), 1)
        self.assertIn("/reboot", events[0][1])
        self.record_factory.assert_not_called()

    def test_record_creation_failure_prevents_sysprep(self):
        with patch.object(self.executor.Path, "is_file", return_value=True), \
                patch.object(self.executor, "prepare_boot_plan", return_value=SimpleNamespace(multiboot=True, backup_directory=Path("backup"))), \
                patch.object(self.executor, "_success_stamp", return_value=None), \
                patch.object(self.executor, "ExecutionRecord", side_effect=OSError("record unavailable")), \
                patch.object(self.executor.subprocess, "run") as command, \
                patch.object(self.executor, "collect_sysprep_logs", return_value=None):
            with self.assertRaises(OSError):
                self.executor.run_sysprep()
            command.assert_not_called()

    def test_isolated_dispatch_failure_never_falls_back_to_desktop_sysprep(self):
        plan = SimpleNamespace(multiboot=True, backup_directory=Path("backup"), identifier=CURRENT)
        with patch.object(self.executor.Path, "is_file", return_value=True), \
                patch.object(self.executor, "prepare_boot_plan", return_value=plan), \
                patch("sysprep.admin_job.dispatch_and_wait", side_effect=RuntimeError("worker launch failed")), \
                patch.object(self.executor, "run_system_command") as command, \
                patch.object(self.executor, "collect_sysprep_logs", return_value=None):
            with self.assertRaises(RuntimeError):
                self.executor.run_sysprep(isolate=True)
            command.assert_not_called()

    def test_changed_current_loader_stops_before_sysprep(self):
        plan = SimpleNamespace(identifier=OTHER)
        with patch.object(self.executor.Path, "is_file", return_value=True), \
                patch.object(self.executor, "prepare_boot_plan", return_value=plan), \
                patch.object(self.executor, "run_system_command") as command, \
                patch.object(self.executor, "collect_sysprep_logs", return_value=None):
            with self.assertRaises(BootCompatibilityError):
                self.executor.run_sysprep(expected_identifier=CURRENT)
            command.assert_not_called()

    def test_failure_never_schedules_power_action(self):
        for error in ("repair", "sysprep", "stale", "missing"):
            events = []
            def repair(plan):
                if error == "repair":
                    raise BootCompatibilityError("repair failed")
            def run(args, **kwargs):
                events.append(args)
                if error == "sysprep":
                    raise subprocess.CalledProcessError(1, args)
            plan = SimpleNamespace(multiboot=True, backup_directory=Path("test-backup"))
            stamps = [(1, 1), (1, 1)] if error == "stale" else [(1, 1), None] if error == "missing" else [(1, 1), (2, 2)]
            with self.subTest(error=error), \
                    patch.object(self.executor.Path, "is_file", return_value=True), \
                    patch.object(self.executor, "prepare_boot_plan", return_value=plan), \
                    patch.object(self.executor, "_success_stamp", side_effect=stamps), \
                    patch.object(self.executor, "repair_boot_plan", side_effect=repair), \
                    patch.object(self.executor.subprocess, "run", side_effect=run), \
                    patch.object(self.executor, "collect_sysprep_logs", return_value=None):
                with self.assertRaises((BootCompatibilityError, subprocess.CalledProcessError)):
                    self.executor.run_sysprep()
            self.assertEqual(len(events), 1)
            self.assertIn("/quit", events[0])

    def test_invalid_parameters_do_not_read_or_write_bcd(self):
        for mode, action in (("bad", "quit"), ("oobe", "bad")):
            with patch.object(self.executor, "prepare_boot_plan") as prepare:
                with self.assertRaises(ValueError):
                    self.executor.run_sysprep(mode, action)
                prepare.assert_not_called()

    def test_prepare_failure_prevents_sysprep_and_shutdown(self):
        with patch.object(self.executor.Path, "is_file", return_value=True), \
                patch.object(self.executor, "prepare_boot_plan", side_effect=BootCompatibilityError("backup failed")), \
                patch.object(self.executor.subprocess, "run") as run, \
                patch.object(self.executor, "collect_sysprep_logs", return_value=None):
            with self.assertRaises(BootCompatibilityError):
                self.executor.run_sysprep()
        run.assert_not_called()


class LogCollectionTests(unittest.TestCase):
    def test_logs_from_all_phases_keep_separate_names(self):
        logger_module = ModuleType("core.logger")
        logger_module.logger = logging.getLogger("log-tests")
        with patch.dict(sys.modules, {"core.logger": logger_module}):
            from sysprep.log_collector import collect_sysprep_logs
        with tempfile.TemporaryDirectory() as folder:
            windows = Path(folder) / "Windows"
            files = {
                "System32/Sysprep/Panther/setupact.log": "generalize",
                "System32/Sysprep/Panther/setuperr.log": "BCD error",
                "Panther/setupact.log": "specialize",
                "Panther/setuperr.log": "setup error",
                "Panther/UnattendGC/setupact.log": "oobe",
                "Panther/unattend.xml": "private answer file",
            }
            for name, content in files.items():
                path = windows / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            output = Path(collect_sysprep_logs(windows, Path(folder) / "output"))
            self.assertEqual((output / "Sysprep/Panther/setupact.log").read_text(), "generalize")
            self.assertEqual((output / "Panther/setupact.log").read_text(), "specialize")
            self.assertEqual((output / "Panther/UnattendGC/setupact.log").read_text(), "oobe")
            self.assertEqual(len(list(output.rglob("*.log"))), 5)
            self.assertEqual(list(output.rglob("*.xml")), [])


if __name__ == "__main__":
    unittest.main()
