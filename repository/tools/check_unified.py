"""Read-only archive and CMD routing checks. Never executes a deployment flow."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def run_cmd(path, args, env=None):
    # List arguments are quoted by subprocess; no user-supplied command text.
    return subprocess.run([os.environ["COMSPEC"], "/d", "/c", str(path)] + args,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          stdin=subprocess.DEVNULL, env=env, timeout=90)


def check():
    record_path = ROOT / "docs/UNIFIED-CANDIDATE-3-BUILD.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    archive = ROOT / record["file"]
    assert hashlib.sha256(archive.read_bytes()).hexdigest().upper() == record["sha256"]
    with tempfile.TemporaryDirectory(prefix="unified check 中文 ", dir=str(ROOT / "build")) as temporary:
        target = Path(temporary)
        with zipfile.ZipFile(str(archive)) as source:
            assert source.testzip() is None
            for item in source.infolist():
                path = Path(item.filename)
                assert not path.is_absolute() and ".." not in path.parts
            source.extractall(str(target))
        folder = target / archive.stem
        hashes = (folder / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
        for line in hashes:
            expected, relative = line.split("  ", 1)
            assert hashlib.sha256((folder / relative).read_bytes()).hexdigest().upper() == expected
        # Confirm every Vista file is identical to the accepted source archive.
        vista = json.loads((ROOT / "docs/VISTA-GUI-BUILD.json").read_text(encoding="utf-8"))
        with zipfile.ZipFile(str(ROOT / vista["file"])) as source:
            for item in source.infolist():
                if not item.is_dir():
                    relative = Path(*Path(item.filename).parts[1:])
                    assert (folder / "runtimes/vista" / relative).read_bytes() == source.read(item)
        env = {key.upper(): value for key, value in os.environ.items()}
        env["PATH"] = os.path.join(env["SYSTEMROOT"], "System32")
        for key in ("TCL_LIBRARY", "TK_LIBRARY", "PYTHONHOME", "PYTHONPATH"):
            env.pop(key, None)
        # Isolate execution-record lookup from the developer's real ProgramData.
        env["PROGRAMDATA"] = str(target / "ProgramData")
        actual = run_cmd(folder / "Start.cmd", ["--route-only"], env)
        assert actual.returncode == 0 and actual.stdout.strip() == b"modern", actual.stdout
        help_result = run_cmd(folder / "Start.cmd", ["--help"], env)
        assert help_result.returncode == 0 and b"--tui" in help_result.stdout, help_result.stdout
        check_result = run_cmd(folder / "Start.cmd", ["--check-last-run"], env)
        assert check_result.returncode == 0, check_result.stdout
        runtime = subprocess.run([str(folder / "runtimes/modern/JY Sysprep.exe"), "--runtime-self-test"],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 stdin=subprocess.DEVNULL, env=env, timeout=90)
        assert runtime.returncode == 0, runtime.stdout
        runtime_report = json.loads(runtime.stdout.decode("ascii"))
        for flag in ("systemCommandPassed", "dllSearchRestored", "guiExitWaitsForExecution"):
            assert runtime_report[flag], runtime_report
        assert not runtime_report["sysprepExecuted"] and not runtime_report["bcdReadOrModified"]
        runtime_script = run_cmd(folder / "Check modern runtime.cmd", [], env)
        assert runtime_script.returncode == 0, runtime_script.stdout
        script_report = json.loads((folder / "Modern-runtime-self-test.txt").read_text(encoding="ascii"))
        assert script_report["guiExitWaitsForExecution"] and script_report["dllSearchRestored"]
        for script in ("Start GUI.cmd", "Start TUI.cmd"):
            # --help cannot be appended to the UI shortcuts; inspect their fixed forwarding.
            assert b'call "%~dp0Start.cmd" --' in (folder / script).read_bytes()
        vista_check = subprocess.run([str(folder / "runtimes/vista/JY Sysprep Vista.exe"), "--gui-self-test"],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    stdin=subprocess.DEVNULL, env=env, timeout=90)
        assert vista_check.returncode == 0, vista_check.stdout
        assert json.loads(vista_check.stdout.decode("ascii"))["guiSmokeCheckPassed"]
        original = (folder / "Start.cmd").read_text(encoding="ascii")
        cases = [("6.0.6002", "AMD64", None, 0, b"vista"),
                 ("6.1.7601", "AMD64", None, 0, b"modern"),
                 ("6.2.9200", "AMD64", None, 0, b"modern"),
                 ("6.3.9600", "x86", "AMD64", 0, b"modern"),
                 ("10.0.19045", "AMD64", None, 0, b"modern"),
                 ("10.0.26100", "AMD64", None, 0, b"modern"),
                 ("5.1.2600", "AMD64", None, 2, None),
                 ("10.0.26100", "x86", None, 2, None),
                 ("10.0.26100", "ARM64", None, 2, None)]
        # Substitute only the OS-version producer in a disposable launcher copy.
        # This checks branch logic, not real compatibility on simulated systems.
        assert original.count("ver |") == 2
        for version, architecture, wow64, code, output in cases:
            script = folder / "route-test.cmd"
            script.write_bytes(original.replace("ver |", "echo Microsoft Windows [Version {}] |".format(version)).replace("\n", "\r\n").encode("ascii"))
            simulated = env.copy()
            simulated["PROCESSOR_ARCHITECTURE"] = architecture
            simulated.pop("PROCESSOR_ARCHITEW6432", None)
            if wow64:
                simulated["PROCESSOR_ARCHITEW6432"] = wow64
            result = run_cmd(script, ["--route-only"], simulated)
            assert result.returncode == code, (version, architecture, result.stdout)
            if output:
                assert result.stdout.strip() == output, result.stdout
        # Missing runtime must fail rather than launch another environment.
        modern = folder / "runtimes/modern/JY Sysprep.exe"
        modern.rename(modern.with_suffix(".disabled"))
        result = run_cmd(folder / "Start.cmd", ["--route-only"], env)
        assert result.returncode == 3, result.stdout
    record.update({"archiveVerified": True, "allFileHashesVerified": True,
                   "vistaPayloadUnchanged": True, "routingCasesPassed": len(cases),
                   "missingRuntimeRejected": True, "developmentHostRoute": "modern",
                   "modernHelpPassed": True, "vistaGuiSelfTestPassedOnDevelopmentHost": True,
                   "modernCheckLastRunPassed": True,
                   "packagedGuiLifetimeCheckPassed": True, "packagedSystemCommandCheckPassed": True,
                   "modernRuntimeCmdPassed": True,
                   "pathWithSpacesAndChineseChecked": True,
                   "crossVersionDeploymentValidated": False})
    record_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    # Runtime checks are intentionally disabled after the host restart incident.
    # The default entry now verifies files only; it never launches bundled EXEs.
    from check_unified_static import check as check_static
    check_static()
