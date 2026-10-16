"""Pure checks only: no worker, process launch, registry or power execution."""
import unittest
from sysprep import admin_job


class AdministratorJobPureTests(unittest.TestCase):
    def test_worker_requires_explicit_power_capability(self):
        with self.assertRaises(TypeError):
            admin_job.worker_main()
        with self.assertRaises(TypeError):
            admin_job.worker_main(power_action=None)

    def test_independent_environment_drops_frozen_parent_state(self):
        original = {"PATH": r"C:\bundle;C:\Windows\System32",
                    "_MEIPASS2": r"C:\bundle", "_PYI_APPLICATION_HOME_DIR": r"C:\bundle"}
        result = admin_job.independent_environment(original, r"C:\bundle")
        self.assertNotIn("_MEIPASS2", result)
        self.assertNotIn("_PYI_APPLICATION_HOME_DIR", result)
        self.assertEqual(result["PATH"], r"C:\Windows\System32")
        self.assertEqual(result["PYINSTALLER_RESET_ENVIRONMENT"], "1")
        self.assertIn("_MEIPASS2", original)

    def test_probe_power_request_rejected_before_any_system_access(self):
        with self.assertRaises(ValueError):
            admin_job.stage_job(action="reboot", probe=True)
