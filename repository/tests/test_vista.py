import io
import json
import logging
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from xml.etree import ElementTree as ET

import vista_main
from sysprep.config import SysprepConfig
from sysprep.unattend.generator import create_xml


def vista_version(sp=2, major=6, minor=0):
    return SimpleNamespace(major=major, minor=minor, service_pack_major=sp)


class VistaTests(unittest.TestCase):
    def setUp(self):
        logger_module = ModuleType("core.logger")
        logger_module.logger = logging.getLogger("vista-tests")
        with patch.dict(sys.modules, {"core.logger": logger_module}):
            from sysprep.client.vista import VistaAdapter
            from sysprep.factory import AdapterFactory
            import sysprep.executor as executor
        self.adapter_class = VistaAdapter
        self.factory = AdapterFactory
        self.executor = executor
        self.context = SimpleNamespace(
            family="Windows Vista", arch="AMD64", is_admin=True, is_server=False,
            sysprep_config=SysprepConfig(), supports_wireless_oobe=False,
            supports_online_accounts=False, supports_local_account_screen=False,
        )

    def test_factory_selects_dedicated_vista_adapter(self):
        self.assertIsInstance(self.factory.create(self.context), self.adapter_class)
        self.context.family = "Windows 11"
        self.assertNotIsInstance(self.factory.create(self.context), self.adapter_class)

    def test_vista_sp2_x64_prepare(self):
        with patch("sys.getwindowsversion", return_value=vista_version()), \
                patch("sys.stdout", new_callable=io.StringIO):
            self.adapter_class(self.context).prepare()

    def test_vista_sp1_x86_and_other_hosts_rejected(self):
        for version, arch in ((vista_version(1), "AMD64"), (vista_version(), "x86"),
                              (vista_version(major=10), "AMD64")):
            with self.subTest(version=version, arch=arch), \
                    patch("sys.getwindowsversion", return_value=version), \
                    patch("sys.stdout", new_callable=io.StringIO):
                self.context.arch = arch
                with self.assertRaises(RuntimeError):
                    self.adapter_class(self.context).prepare()

    def test_test_mode_never_executes_sysprep(self):
        with patch("sysprep.client.vista.run_sysprep") as run, \
                patch("sys.stdout", new_callable=io.StringIO):
            self.adapter_class(self.context).cleanup()
        run.assert_not_called()

    def test_formal_vista_execution_forbids_multiboot(self):
        self.context.sysprep_config.test_only = False
        adapter = self.adapter_class(self.context)
        adapter._unattend_path = "test-answer.xml"
        with patch("sysprep.client.vista.run_sysprep") as run:
            adapter.cleanup()
        run.assert_called_once_with("audit", "shutdown", "test-answer.xml", allow_multiboot=False)

    def test_multiboot_guard_stops_before_sysprep_repair_and_power_action(self):
        from sysprep.boot import BootCompatibilityError
        plan = SimpleNamespace(multiboot=True, backup_directory=Path("test-backup"))
        with patch.object(self.executor.Path, "is_file", return_value=True), \
                patch.object(self.executor, "prepare_boot_plan", return_value=plan), \
                patch.object(self.executor, "repair_boot_plan") as repair, \
                patch.object(self.executor, "complete_power_action") as power, \
                patch.object(self.executor.subprocess, "run") as run, \
                patch.object(self.executor, "collect_sysprep_logs", return_value=None):
            with self.assertRaises(BootCompatibilityError):
                self.executor.run_sysprep(allow_multiboot=False)
        run.assert_not_called()
        repair.assert_not_called()
        power.assert_not_called()

    def test_vista_xml_has_namespace_account_and_no_modern_oobe_options(self):
        config = SysprepConfig(admin_username="TestAdmin", admin_password="test<&>",
                               auto_logon=True, auto_logon_count=2)
        root = ET.fromstring(create_xml(self.context, config))
        ns = "{urn:schemas-microsoft-com:unattend}"
        self.assertEqual(root.tag, ns + "unattend")
        for tag in ("HideOnlineAccountScreens", "HideWirelessSetupInOOBE", "HideLocalAccountScreen"):
            self.assertIsNone(root.find(".//" + ns + tag))
        for component in root.findall(".//" + ns + "component"):
            self.assertEqual(component.get("processorArchitecture"), "amd64")
        self.assertEqual(root.find(".//" + ns + "AutoLogon/" + ns + "LogonCount").text, "2")

    def test_read_only_self_test_does_not_load_app_or_write_files(self):
        with patch("pathlib.Path.write_text") as write, \
                patch("subprocess.run") as command, \
                patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(vista_main.run(["--self-test"]), 0)
        report = json.loads(output.getvalue())
        self.assertTrue(report["xmlCheckPassed"])
        self.assertFalse(report["sysprepExecuted"])
        self.assertFalse(report["bcdModified"])
        write.assert_not_called()
        command.assert_not_called()

    def test_entry_rejects_other_hosts_before_importing_main(self):
        fake_main = ModuleType("main")
        with patch.dict(sys.modules, {"main": fake_main}), \
                patch("sys.getwindowsversion", return_value=vista_version(major=10)), \
                patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(vista_main.run([]), 2)

    def test_entry_routes_default_gui_and_explicit_modes_to_shared_app(self):
        for args, expected in (([], []), (["--gui"], ["--gui"]), (["--tui"], ["--tui"])):
            fake_main = ModuleType("main")
            fake_main.run_application = Mock()
            with self.subTest(args=args), patch.dict(sys.modules, {"main": fake_main}), \
                    patch("sys.getwindowsversion", return_value=vista_version()), \
                    patch("sys.maxsize", 2 ** 63 - 1), patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(vista_main.run(args), 0)
            fake_main.run_application.assert_called_once_with(expected, display_version=vista_main.VISTA_BUILD)

    def test_gui_self_test_error_is_reported_without_running_workflow(self):
        with patch("gui.diagnostics.check_gui", side_effect=RuntimeError("Tk unavailable")), \
                patch("subprocess.run") as run, patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(vista_main.run(["--gui-self-test"]), 1)
        report = json.loads(output.getvalue())
        self.assertFalse(report["guiSmokeCheckPassed"])
        self.assertEqual(report["guiError"], "Tk unavailable")
        self.assertFalse(report["sysprepExecuted"])
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
