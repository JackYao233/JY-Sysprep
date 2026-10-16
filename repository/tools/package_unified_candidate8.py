"""Archive assembly only. Never imports or executes the application."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct
import zipfile

ROOT = Path(__file__).absolute().parents[1]
NAME = "JY Sysprep Alpha 0.4 Unified Candidate 8 x64"
RECORD = ROOT / "docs/UNIFIED-CANDIDATE-8-BUILD.json"


def digest(data):
    return hashlib.sha256(data).hexdigest().upper()


def source_files(metadata):
    archive = ROOT / metadata["file"]
    if digest(archive.read_bytes()) != metadata["sha256"]:
        raise RuntimeError("Source archive hash mismatch: " + archive.name)
    files = {}
    with zipfile.ZipFile(str(archive)) as source:
        if source.testzip() is not None:
            raise RuntimeError("Corrupt source archive")
        for item in source.infolist():
            if item.is_dir():
                continue
            path = PurePosixPath(item.filename.replace("\\", "/"))
            if path.is_absolute() or ".." in path.parts or len(path.parts) < 2 or ":" in item.filename:
                raise ValueError("Invalid source archive path")
            relative = PurePosixPath(*path.parts[1:]).as_posix()
            if relative in files:
                raise ValueError("Duplicate source file")
            files[relative] = source.read(item)
    return files


def package():
    vista = json.loads((ROOT / "docs/VISTA-GUI-BUILD.json").read_text(encoding="utf-8-sig"))
    modern = json.loads((ROOT / "docs/WIN11-CANDIDATE-7-BUILD.json").read_text(encoding="utf-8-sig"))
    vista_files, modern_files = source_files(vista), source_files(modern)
    worker = modern_files["JY Sysprep Worker.exe"]
    offset = struct.unpack_from("<I", worker, 60)[0]
    if struct.unpack_from("<H", worker, offset + 92)[0] != 2:
        raise RuntimeError("Worker must use the GUI PE subsystem")
    files = {"runtimes/vista/" + name: data for name, data in vista_files.items()}
    files["runtimes/modern/JY Sysprep.exe"] = modern_files["JY Sysprep Modern.exe"]
    files["runtimes/modern/JY Sysprep Worker.exe"] = worker
    for name, data in modern_files.items():
        if name.startswith("licenses/"):
            files["runtimes/modern/" + name] = data
    files["Start.cmd"] = (ROOT / "tools/unified/Start.cmd").read_bytes()
    for mode in ("GUI", "TUI"):
        files["Start " + mode + ".cmd"] = ('@echo off\r\ncall "%~dp0Start.cmd" --' + mode.lower() + '\r\nexit /b %errorlevel%\r\n').encode("ascii")
    for source, target in (("Check runtime.cmd", "Check modern runtime.cmd"),
                           ("Check background.cmd", "Check background.cmd")):
        text = modern_files[source].decode("ascii")
        text = text.replace("candidate 7", "unified candidate 8 (candidate 7 runtime)")
        text = text.replace(".\\JY Sysprep Modern.exe", ".\\runtimes\\modern\\JY Sysprep.exe")
        # Reject Vista before a modern EXE could be started.
        guard = ('ver | "%SystemRoot%\\System32\\findstr.exe" /r /c:" 6\\.0\\." >nul\r\n'
                 'if not errorlevel 1 (\r\n echo Use the Vista runtime self-check instead.\r\n pause\r\n exit /b 2\r\n)\r\n')
        text = text.replace('pushd "%~dp0"\r\n', guard + 'pushd "%~dp0"\r\n')
        files[target] = text.encode("ascii")
    for name in ("Collect.cmd", "Collect.ps1"):
        files["Diagnostics/" + name] = (ROOT / "tools/win11-diagnostics" / name).read_bytes()
    files["README.txt"] = (ROOT / "docs/UNIFIED-CANDIDATE-8.md").read_bytes()
    files["SOURCE-BUILDS.json"] = json.dumps({"vista": vista["file"], "vistaSha256": vista["sha256"],
                                             "modern": modern["file"], "modernSha256": modern["sha256"]}, indent=2).encode("utf-8")
    files["SHA256SUMS.txt"] = "".join(digest(data) + "  " + name + "\n" for name, data in sorted(files.items())).encode("utf-8")
    archive = ROOT / (NAME + ".zip")
    # Never overwrite an already delivered candidate.
    with zipfile.ZipFile(str(archive), "x", zipfile.ZIP_DEFLATED) as output:
        for name, data in sorted(files.items()):
            output.writestr(NAME + "/" + name, data)
    record = {"file": archive.name, "sha256": digest(archive.read_bytes()), "bytes": archive.stat().st_size,
              "version": "Alpha 0.4 unified candidate 8", "files": len(files),
              "vistaSourceSha256": vista["sha256"], "modernSourceSha256": modern["sha256"],
              "modernPython": "3.7.9 x64", "vistaPython": "3.6.8 x64",
              "sourceWin11UserDeploymentPassed": bool(modern["windows11DeploymentValidated"]),
              "crossVersionDeploymentValidated": False, "hostRuntimeExecuted": False,
              "runtimeRegressionPending": ["Vista launcher", "Windows 7", "Windows 8", "Windows 8.1", "Windows 10", "Windows 11 unified entry and shutdown"]}
    RECORD.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    package()
