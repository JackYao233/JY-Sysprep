"""Static ZIP verification only: no application imports or process creation."""
import json
from pathlib import PurePosixPath
import struct
import zipfile

from package_unified_candidate8 import ROOT, NAME, RECORD, digest, source_files


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def check():
    record = json.loads(RECORD.read_text(encoding="utf-8-sig"))
    archive = ROOT / record["file"]
    require(digest(archive.read_bytes()) == record["sha256"], "Archive hash mismatch")
    files = {}
    with zipfile.ZipFile(str(archive)) as source:
        require(source.testzip() is None, "Archive CRC mismatch")
        for item in source.infolist():
            path = PurePosixPath(item.filename)
            require(not path.is_absolute() and ".." not in path.parts and ":" not in item.filename,
                    "Unsafe archive path")
            require(path.parts[0] == NAME and len(path.parts) >= 2, "Wrong archive root")
            name = PurePosixPath(*path.parts[1:]).as_posix()
            require(name not in files, "Duplicate archive entry")
            files[name] = source.read(item)
    manifest = {}
    for line in files["SHA256SUMS.txt"].decode("utf-8").splitlines():
        expected, name = line.split("  ", 1)
        require(name not in manifest, "Duplicate manifest entry")
        manifest[name] = expected
        require(digest(files[name]) == expected, "File hash mismatch: " + name)
    require(set(manifest) == set(files) - {"SHA256SUMS.txt"}, "Manifest coverage mismatch")
    vista = source_files(json.loads((ROOT / "docs/VISTA-GUI-BUILD.json").read_text(encoding="utf-8-sig")))
    modern = source_files(json.loads((ROOT / "docs/WIN11-CANDIDATE-7-BUILD.json").read_text(encoding="utf-8-sig")))
    require({name[len("runtimes/vista/"):]: data for name, data in files.items()
             if name.startswith("runtimes/vista/")} == vista, "Vista payload changed")
    require(files["runtimes/modern/JY Sysprep.exe"] == modern["JY Sysprep Modern.exe"], "Modern EXE changed")
    worker = files["runtimes/modern/JY Sysprep Worker.exe"]
    require(worker == modern["JY Sysprep Worker.exe"], "Worker EXE changed")
    offset = struct.unpack_from("<I", worker, 60)[0]
    require(struct.unpack_from("<H", worker, offset + 92)[0] == 2, "Worker is a console executable")
    launcher = files["Start.cmd"].decode("ascii")
    for value in ('jy_runtime=vista', 'jy_runtime=modern', 'JY Sysprep Worker.exe', '--route-only', '--check-last-run'):
        require(value in launcher, "Missing launcher behavior: " + value)
    for script in ("Check background.cmd", "Check modern runtime.cmd"):
        text = files[script].decode("ascii")
        require('.\\runtimes\\modern\\JY Sysprep.exe' in text, "Wrong check path")
        require('Use the Vista runtime self-check instead.' in text, "Missing Vista guard")
    require('--admin-worker-self-test' in files["Check background.cmd"].decode("ascii"), "Wrong worker check")
    require(set(files) >= {"Start GUI.cmd", "Start TUI.cmd", "Diagnostics/Collect.cmd", "Diagnostics/Collect.ps1"},
            "Missing entry or diagnostic files")
    record.update(archiveVerified=True, allFileHashesVerified=True, vistaPayloadUnchanged=True,
                  modernPayloadMatchesCandidate7=True, workerGuiSubsystemVerified=True,
                  launcherStaticallyChecked=True, archiveFilesChecked=len(files),
                  runtimeExecuted=False)
    RECORD.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    check()
