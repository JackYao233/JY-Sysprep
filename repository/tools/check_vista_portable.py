"""Check the delivered ZIP from an extracted directory, without running Sysprep."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
NAME = "JY Sysprep Alpha 0.4 Vista Portable x64"


def check(gui=False):
    record_name = "VISTA-GUI-BUILD.json" if gui else "VISTA-PORTABLE-BUILD.json"
    record_path = ROOT / "docs" / record_name
    record = json.loads(record_path.read_text(encoding="utf-8"))
    archive = ROOT / record["file"]
    if hashlib.sha256(archive.read_bytes()).hexdigest().upper() != record["sha256"]:
        raise RuntimeError("ZIP build record mismatch")
    with tempfile.TemporaryDirectory(prefix="vista-portable-", dir=str(ROOT / "build")) as temporary:
        with zipfile.ZipFile(str(archive)) as packed:
            if any(Path(name).is_absolute() or ".." in Path(name).parts for name in packed.namelist()):
                raise RuntimeError("Unsafe ZIP member")
            packed.extractall(temporary)
        folder = Path(temporary) / ("JY Sysprep Alpha 0.4 Vista GUI Portable x64" if gui else NAME)
        for line in (folder / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
            expected, relative = line.split("  ", 1)
            if hashlib.sha256((folder / relative).read_bytes()).hexdigest().upper() != expected:
                raise RuntimeError("Extracted file hash mismatch: " + relative)
        environment = dict(os.environ)
        environment["PATH"] = os.path.join(os.environ["SYSTEMROOT"], "System32")
        environment.pop("TCL_LIBRARY", None)
        environment.pop("TK_LIBRARY", None)
        result = subprocess.run([str(folder / "JY Sysprep Vista.exe"), "--self-test"],
                                cwd=str(ROOT / "build"), env=environment, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        if result.returncode:
            raise RuntimeError("Extracted EXE self-test failed: " + repr(result.stderr))
        report = json.loads(result.stdout.decode("utf-8"))
        if not report["xmlCheckPassed"] or report["sysprepExecuted"] or report["bcdModified"]:
            raise RuntimeError("Unexpected self-test result")
        for library in ("python36.dll", "vcruntime140.dll"):
            path = report["loadedLibraries"][library]
            if not path or Path(path).parent != folder:
                raise RuntimeError("Library not loaded from portable folder: " + library)
        result = subprocess.run([str(folder / "JY Sysprep Vista.exe"), "--help"], cwd=str(folder),
                                env=environment, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=30)
        if result.returncode or b"--self-test" not in result.stdout:
            raise RuntimeError("Portable help check failed")
        result = subprocess.run([os.path.join(os.environ["SYSTEMROOT"], "System32", "cmd.exe"),
                                 "/d", "/c", "Check runtime.cmd"], cwd=str(folder), env=environment,
                                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=30)
        if result.returncode:
            raise RuntimeError("Self-test CMD failed: " + repr(result.stderr))
        saved = json.loads((folder / "Vista-self-test.txt").read_text(encoding="utf-8"))
        if not saved["xmlCheckPassed"]:
            raise RuntimeError("CMD did not save a successful self-test report")
        if gui:
            result = subprocess.run([str(folder / "JY Sysprep Vista.exe"), "--gui-self-test"],
                                    cwd=str(ROOT / "build"), env=environment, stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            if result.returncode:
                raise RuntimeError("Packaged GUI self-test failed: " + repr(result.stdout + result.stderr))
            gui_report = json.loads(result.stdout.decode("utf-8"))
            if not gui_report.get("guiSmokeCheckPassed") or not gui_report.get("guiToTuiHandoffChecked"):
                raise RuntimeError("Packaged GUI page or F8 check failed")
            for library in ("tcl86t.dll", "tk86t.dll"):
                if Path(gui_report["loadedLibraries"][library]).parent != folder:
                    raise RuntimeError("Tcl/Tk loaded from outside portable folder")
            result = subprocess.run([os.path.join(os.environ["SYSTEMROOT"], "System32", "cmd.exe"),
                                     "/d", "/c", "Check GUI.cmd"], cwd=str(folder), env=environment,
                                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, timeout=30)
            saved_gui = json.loads((folder / "Vista-gui-self-test.txt").read_text(encoding="utf-8"))
            if result.returncode or not saved_gui.get("guiSmokeCheckPassed"):
                raise RuntimeError("GUI self-test CMD failed")
            record.update({"packagedGuiSelfTestPassedOnDevelopmentHost": True,
                           "guiSelfTestCmdPassedOnDevelopmentHost": True,
                           "guiPagesChecked": gui_report["guiPagesChecked"],
                           "tclVersion": gui_report["tclVersion"], "tkVersion": gui_report["tkVersion"],
                           "appLocalTclTkVerifiedOnDevelopmentHost": True})
    record.update({"extractedZipFilesVerified": True, "extractedExeSelfTestPassedOnDevelopmentHost": True,
                   "extractedExeHelpPassedOnDevelopmentHost": True, "selfTestCmdPassedOnDevelopmentHost": True,
                   "isolatedPathVerifiedOnDevelopmentHost": True})
    record_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print("ZIP file hashes, extracted EXE, help and self-test CMD verified with isolated PATH")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--gui", action="store_true")
    check(gui=parser.parse_args().gui)
