import io
import logging
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET


class CompatibilityTests(unittest.TestCase):
    def test_all_source_and_specs_compile(self):
        root = Path(__file__).absolute().parents[1]
        files = list(root.glob("*.py")) + list(root.glob("*.spec"))
        for folder in ("core", "osdetect", "sysprep", "utils", "gui", "tests"):
            files.extend((root / folder).rglob("*.py"))
        for source in files:
            with self.subTest(source=str(source)):
                compile(source.read_text(encoding="utf-8"), str(source), "exec")

    def test_xml_generation_and_utf8_write(self):
        from sysprep.config import SysprepConfig
        from sysprep.unattend.generator import create_xml
        from sysprep.unattend.writer import write_unattend

        config = SysprepConfig(
            computer_name="JY-PC", owner="中文 & Owner",
            admin_username="TestAdmin", admin_password="test-only<&>",
            auto_logon=True, auto_logon_count=2,
        )
        for architecture, expected in (("AMD64", "amd64"), ("x86", "x86")):
            context = SimpleNamespace(
                arch=architecture, supports_wireless_oobe=True,
                supports_online_accounts=True, supports_local_account_screen=False,
            )
            xml = create_xml(context, config)
            root = ET.fromstring(xml)
            self.assertTrue(all(node.get("processorArchitecture") == expected for node in root.iter("component")))
            self.assertEqual(root.find(".//ComputerName").text, "JY-PC")
            self.assertEqual(root.find(".//RegisteredOwner").text, "中文 & Owner")
            self.assertEqual(root.find(".//LocalAccount/Password/Value").text, "test-only<&>")
            self.assertEqual(root.find(".//AutoLogon/LogonCount").text, "2")
            with tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "nested" / "unattend.xml"
                write_unattend(xml, output)
                self.assertEqual(output.read_text(encoding="utf-8"), xml)

    def test_test_only_adapter_does_not_run_sysprep(self):
        logger_module = ModuleType("core.logger")
        logger_module.logger = logging.getLogger("compatibility-tests")
        with patch.dict(sys.modules, {"core.logger": logger_module}):
            from sysprep.configured_adapter import ConfiguredWindowsAdapter
        from sysprep.config import SysprepConfig

        context = SimpleNamespace(family="Windows 11", is_admin=False, sysprep_config=SysprepConfig())
        adapter = ConfiguredWindowsAdapter(context, "Windows 11")
        with patch("sysprep.configured_adapter.run_sysprep") as execute, \
                patch("sys.stdout", new_callable=io.StringIO):
            adapter.prepare()
            adapter.cleanup()
        execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
