from contextlib import contextmanager
from datetime import datetime, timedelta
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock
from xml.etree import ElementTree as ET

from sysprep import system_job as jobs


@contextmanager
def unlocked():
    yield


class SystemJobTests(unittest.TestCase):
    def test_task_is_demand_only_system_and_uses_separate_executable(self):
        folder = Path(r"C:\ProgramData") / (jobs.PREFIX + "a" * 32)
        tree = ET.fromstring(jobs.task_xml(folder))
        ns = {"t": "http://schemas.microsoft.com/windows/2004/02/mit/task"}
        self.assertEqual(len(tree.find("t:Triggers", ns)), 0)
        self.assertEqual(tree.find(".//t:UserId", ns).text, "S-1-5-18")
        self.assertIsNone(tree.find(".//t:LogonType", ns))
        self.assertEqual(tree.find(".//t:Command", ns).text, str(folder / "worker.exe"))
        self.assertEqual(tree.find(".//t:Arguments", ns).text, "--deployment-worker")
        self.assertIsNone(tree.find(".//t:RestartOnFailure", ns))

    def test_manifest_rejects_tampering_and_expired_jobs(self):
        with tempfile.TemporaryDirectory() as base:
            folder = Path(base) / (jobs.PREFIX + "a" * 32)
            folder.mkdir()
            (folder / "worker.exe").write_bytes(b"test-worker")
            job = {"schema": 1, "kind": "probe", "mode": "oobe", "completionAction": "quit",
                   "createdUtc": datetime.utcnow().isoformat(timespec="microseconds") + "Z",
                   "workerHash": jobs.file_hash(folder / "worker.exe")}
            with patch.object(jobs, "common_appdata", return_value=Path(base)):
                (folder / "job.json").write_text(json.dumps(job))
                self.assertEqual(jobs.validate_job(folder)["kind"], "probe")
                (folder / "worker.exe").write_bytes(b"tampered")
                with self.assertRaises(RuntimeError):
                    jobs.validate_job(folder)
                job["workerHash"] = jobs.file_hash(folder / "worker.exe")
                job["createdUtc"] = (datetime.utcnow() - timedelta(minutes=6)).isoformat(timespec="microseconds") + "Z"
                (folder / "job.json").write_text(json.dumps(job))
                with self.assertRaises(RuntimeError):
                    jobs.validate_job(folder)

    def run_worker(self, probe=False, fail=False, unverified=False):
        base = tempfile.TemporaryDirectory()
        self.addCleanup(base.cleanup)
        folder = Path(base.name) / (jobs.PREFIX + "b" * 32)
        folder.mkdir()
        job = {"kind": "probe" if probe else "deployment", "completionAction": "reboot"}
        # Pass the fake directly; never rely on patching an executor module
        # that a later dynamic import may replace with another module object.
        power = Mock(name="fake_power_action")
        original_handlers = jobs.logging.getLogger("JY Sysprep").handlers[:]
        def restore_loggers():
            logger = jobs.logging.getLogger("JY Sysprep")
            for handler in logger.handlers[:]:
                if handler not in original_handlers:
                    logger.removeHandler(handler)
                    handler.close()
        self.addCleanup(restore_loggers)
        # Restore the logger shim installed by the worker in this test process.
        with patch.dict(jobs.sys.modules), \
                patch.object(jobs.sys, "executable", str(folder / "worker.exe")), \
                patch.object(jobs, "common_appdata", return_value=Path(base.name)), \
                patch.object(jobs, "validate_job", return_value=job), \
                patch.object(jobs, "system_identity", return_value={"workerSid": "S-1-5-18", "workerSession": 0}), \
                patch.object(jobs, "execution_mutex", side_effect=unlocked), \
                patch.object(jobs, "task_command") as task, \
                patch.object(jobs.time, "sleep"), \
                patch.object(jobs, "deployment_body", side_effect=RuntimeError("BCD verify failed") if fail else None,
                             return_value=None if unverified else {"sysprepSucceeded": True, "bcdVerified": True}) as deploy:
            code = jobs.worker_main(power_action=power)
        status = json.loads((folder / "status.json").read_text(encoding="utf-8"))
        return code, status, deploy, power, task

    def test_probe_never_runs_deployment_or_power(self):
        code, status, deploy, power, task = self.run_worker(probe=True)
        self.assertEqual(code, 0)
        self.assertEqual(status["workerSession"], 0)
        self.assertFalse(status["sysprepExecuted"])
        deploy.assert_not_called()
        power.assert_not_called()
        self.assertEqual(task.call_args[0][0][0], "/delete")

    def test_missing_power_capability_fails_before_worker_initialization(self):
        with patch.object(jobs, "common_appdata") as appdata:
            with self.assertRaises(TypeError):
                jobs.worker_main()
            with self.assertRaises(TypeError):
                jobs.worker_main(power_action=None)
        appdata.assert_not_called()

    def test_unverified_return_never_runs_power(self):
        code, status, deploy, power, task = self.run_worker(unverified=True)
        self.assertEqual(code, 1)
        self.assertEqual(status["stage"], "failed")
        self.assertEqual(status["failedStage"], "preflight_running")
        power.assert_not_called()

    def test_failure_never_runs_power_and_success_does(self):
        code, status, deploy, power, task = self.run_worker(fail=True)
        self.assertEqual(code, 1)
        self.assertEqual(status["stage"], "failed")
        power.assert_not_called()
        code, status, deploy, power, task = self.run_worker()
        self.assertEqual(code, 0)
        self.assertEqual(status["stage"], "power_command_accepted")
        power.assert_called_once_with("reboot")
