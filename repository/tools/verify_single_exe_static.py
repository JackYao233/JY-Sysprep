"""Read PE/CArchive data only; never import application modules or launch EXEs."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import pefile
from PyInstaller.archive.readers import CArchiveReader

ROOT = Path(__file__).absolute().parents[1]
NAME = "JY Sysprep Alpha 0.5 Single Candidate 3 x64.exe"


def sha(data):
    return hashlib.sha256(data).hexdigest().upper()


def check_archive(path, expected_subsystem):
    raw = path.read_bytes()
    image = pefile.PE(data=raw)
    try:
        if image.FILE_HEADER.Machine != 0x8664 or image.OPTIONAL_HEADER.Subsystem != expected_subsystem:
            raise RuntimeError("Wrong PE architecture/subsystem: " + path.name)
    finally:
        image.close()
    archive = CArchiveReader(str(path))
    names = archive.contents()
    runtime = json.loads((ROOT / "build/vista-runtime/x64/runtime-manifest.json").read_text(encoding="utf-8"))
    for item in runtime["files"]:
        if sha(archive.extract(item["file"])[1]) != item["sha256"]:
            raise RuntimeError("Embedded runtime mismatch: " + item["file"])
    native_count = 0
    for name in names:
        if not name.lower().endswith((".exe", ".dll", ".pyd")):
            continue
        native_count += 1
        binary = pefile.PE(data=archive.extract(name)[1])
        try:
            if binary.FILE_HEADER.Machine != 0x8664:
                raise RuntimeError("Non-x64 embedded file: " + name)
            for entry in getattr(binary, "DIRECTORY_ENTRY_IMPORT", []):
                dependency = entry.dll.decode("ascii").lower()
                if dependency.startswith(("api-ms-", "ext-ms-")) and dependency not in names:
                    raise RuntimeError("Missing API set: " + dependency)
        finally:
            binary.close()
    return archive, native_count


def verify():
    for directory in ("core", "gui", "osdetect", "sysprep", "utils"):
        for source in (ROOT / directory).rglob("*.py"):
            ast.parse(source.read_text(encoding="utf-8-sig"), filename=str(source))
    ast.parse((ROOT / "single_main.py").read_text(encoding="utf-8"))
    main = ROOT / "build/alpha05-single-c3/main" / NAME
    worker = ROOT / "build/alpha05-single-c3/worker/JY Sysprep Worker.exe"
    main_archive, main_count = check_archive(main, 3)
    worker_archive, worker_count = check_archive(worker, 2)
    if main_archive.extract("JY Sysprep Worker.exe")[1] != worker.read_bytes():
        raise RuntimeError("Embedded worker differs from verified worker")
    names = main_archive.contents()
    for required in ("python36.dll", "tcl86t.dll", "tk86t.dll", "ALPHA-0.5-SINGLE-EXE.md"):
        if required not in names:
            raise RuntimeError("Missing resource: " + required)
    if not any(name.replace("\\", "/").startswith("licenses/") for name in names):
        raise RuntimeError("Missing licenses")
    target = ROOT / NAME
    if target.exists():
        raise RuntimeError("Refusing to overwrite a delivered candidate")
    shutil.copyfile(str(main), str(target))
    if target.read_bytes() != main.read_bytes():
        raise RuntimeError("Delivery copy mismatch")
    previous = 50728822
    record = dict(file=NAME, bytes=target.stat().st_size, sha256=sha(target.read_bytes()),
                  previousZipBytes=previous,
                  reductionPercent=round(100 * (1 - target.stat().st_size / previous), 2),
                  python="3.6.8 x64", singleFileDistribution=True, extractsResourcesAtStartup=True,
                  embeddedWorkerSha256=sha(worker.read_bytes()), embeddedWorkerMatches=True,
                  nativeFilesChecked=main_count + worker_count, appLocalRuntimeDllsPerArchive=41,
                  workerWindowless=True, python36SyntaxParsed=True, hostRuntimeExecuted=False,
                  runtimeVmRegressionPassed=False, githubPublished=False)
    (ROOT / "docs/ALPHA-0.5-SINGLE-EXE-CANDIDATE-3-BUILD.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    (ROOT / (NAME + ".sha256")).write_text(record["sha256"] + "  " + NAME + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    verify()
