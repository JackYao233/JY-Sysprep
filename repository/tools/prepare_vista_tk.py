"""Copy official Tcl/Tk components into the isolated Python 3.6 runtime."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
from xml.etree import ElementTree as ET

from prepare_vista_runtime import rows


ROOT = Path(__file__).resolve().parents[1]
INSTALLER_SHA256 = "96088A58B7C43BC83B84E6B67F15E8706C614023DD64F9A5A14E81FF824ADADC"


def prepare():
    import msilib
    import pefile

    installer = ROOT / "build/vista-downloads/python-3.6.8-amd64.exe"
    data = installer.read_bytes()
    if hashlib.sha256(data).hexdigest().upper() != INSTALLER_SHA256:
        raise RuntimeError("Official Python installer hash mismatch")
    seven_zip = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "7-Zip/7z.exe"
    work = ROOT / "build/vista-downloads/tk-components"
    work.mkdir(parents=True, exist_ok=True)
    start = 0
    containers = []
    while True:
        offset = data.find(b"MSCF", start)
        if offset < 0:
            break
        size = struct.unpack_from("<I", data, offset + 8)[0]
        if size > 36 and offset + size <= len(data):
            cab = work / ("container-%d.cab" % len(containers))
            cab.write_bytes(data[offset:offset + size])
            destination = work / ("container-%d" % len(containers))
            subprocess.run([str(seven_zip), "x", "-y", "-o" + str(destination), str(cab)],
                           check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            containers.append(destination)
            start = offset + size
        else:
            start = offset + 4
    if len(containers) != 2:
        raise RuntimeError("Unexpected Python installer container layout")
    manifest = ET.parse(str(containers[0] / "0"))
    ns = {"b": "http://schemas.microsoft.com/wix/2008/Burn"}
    payload = manifest.find("b:Payload[@Id='tcltk_JustForMe']", ns)
    if payload is None:
        raise RuntimeError("Tcl/Tk payload not found")
    msi = containers[1] / payload.get("SourcePath")
    if hashlib.sha1(msi.read_bytes()).hexdigest().upper() != payload.get("Hash"):
        raise RuntimeError("Tcl/Tk MSI payload hash mismatch")
    unpacked = work / "msi"
    subprocess.run([str(seven_zip), "x", "-y", "-o" + str(unpacked), str(msi), "cab1.cab"],
                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    files = work / "files"
    subprocess.run([str(seven_zip), "x", "-y", "-o" + str(files), str(unpacked / "cab1.cab")],
                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    db = msilib.OpenDatabase(str(msi), msilib.MSIDBOPEN_READONLY)
    directories = {row[0]: (row[1], row[2]) for row in rows(db, "Directory")}
    components = {row[0]: row[2] for row in rows(db, "Component")}

    def relative_directory(identifier):
        if identifier in ("TARGETDIR", "InstallDirectory"):
            return Path()
        parent, default = directories[identifier]
        name = default.split(":")[0].split("|")[-1]
        return relative_directory(parent) / (name if name != "." else "")

    target_root = ROOT / ".runtime-vista/Python36"
    copied = 0
    for row in rows(db, "File"):
        source = files / row[0]
        target = target_root / relative_directory(components[row[1]]) / row[2].split("|")[-1]
        if not str(target.resolve()).lower().startswith(str(target_root.resolve()).lower() + os.sep):
            raise RuntimeError("Component destination escaped runtime directory")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(source), str(target))
        copied += 1
    native = []
    for name in ("_tkinter.pyd", "tcl86t.dll", "tk86t.dll"):
        path = target_root / "DLLs" / name
        image = pefile.PE(str(path))
        if image.FILE_HEADER.Machine != 0x8664:
            raise RuntimeError("Wrong Tcl/Tk architecture")
        image.close()
        native.append({"file": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper()})
    record = {"pythonInstallerSha256": INSTALLER_SHA256, "payloadSha1": payload.get("Hash"),
              "source": "Official Python 3.6.8 amd64 installer", "copiedFiles": copied, "nativeFiles": native}
    (ROOT / "build/vista-runtime/tk-manifest.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print("Copied {} official Tcl/Tk component files into isolated Python 3.6".format(copied))


if __name__ == "__main__":
    prepare()
