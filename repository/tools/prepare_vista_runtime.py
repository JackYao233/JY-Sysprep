"""Extract SDK redistributables without installing the SDK. Run with Python 3.6."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "build" / "vista-downloads" / "ucrt-sdk14393"
OUTPUT = ROOT / "build" / "vista-runtime" / "x64"
BASE_URL = "https://download.microsoft.com/download/C/D/8/CD8533F8-5324-4D30-824C-B834C5AD51F9/standalonesdk/Installers/"
# Original SDK payloads verified against the signed SDK bootstrapper manifest.
PAYLOADS = {
    "Universal CRT Redistributable-x86_en-us.msi": "6D76C3F206059D0A85A550317C0192F079147C1970335EB79DEABA9B2AAC9556",
    "9126f6ff98d955951fe9323f4444c119.cab": "3988B3D36C1B4343B0A7D3237A30A3DB726AF2D17A27DC748A2EE47C7628FD0E",
    "948a611cd2aca64b1e5113ffb7b95d5f.cab": "13719323A05589C3EE7F600794C5D385D692BA1A30D87CE86987B23D511DE976",
    "fef2cfedd6135e0ed85290b83f3682c3.cab": "408B2C176FDC7EEE8AE5AB4BBD1B65F284D4900448B6C014C8DC90294A98C31D",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def rows(database, table):
    view = database.OpenView("SELECT * FROM " + table)
    view.Execute(None)
    record = view.Fetch()
    while record:
        yield [record.GetString(index) for index in range(1, record.GetFieldCount() + 1)]
        record = view.Fetch()
    view.Close()


def prepare():
    import msilib
    import pefile

    seven_zip = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "7-Zip" / "7z.exe"
    if not seven_zip.is_file():
        raise RuntimeError("Build machine requires 7-Zip at " + str(seven_zip))
    SOURCE.mkdir(parents=True, exist_ok=True)
    bootstrapper = SOURCE.parent / "sdksetup-14393.exe"
    if not bootstrapper.exists():
        urllib.request.urlretrieve("https://go.microsoft.com/fwlink/p/?LinkId=838916", str(bootstrapper))
    if sha256(bootstrapper) != "0D3A5C94143FE14A45BB9608A951DEA04CB01BF1FF90003E8C3D80DACFCA05BE":
        raise RuntimeError("SDK bootstrapper hash mismatch")
    subprocess.run([str(seven_zip), "x", "-y", "-o" + str(SOURCE.parent / "sdk-manifest"),
                    str(bootstrapper), "u2"], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for name, expected in PAYLOADS.items():
        path = SOURCE / name
        if not path.exists():
            urllib.request.urlretrieve(BASE_URL + urllib.parse.quote(name), str(path))
        if sha256(path) != expected:
            raise RuntimeError("SDK payload hash mismatch: " + name)

    database = msilib.OpenDatabase(str(SOURCE / "Universal CRT Redistributable-x86_en-us.msi"),
                                  msilib.MSIDBOPEN_READONLY)
    directories = {row[0]: row[2].split("|")[-1] for row in rows(database, "Directory")}
    components = {row[0]: row[2] for row in rows(database, "Component")}
    wanted = {row[0]: row[2].split("|")[-1] for row in rows(database, "File")
              if directories.get(components[row[1]]) == "x64" and row[2].lower().endswith(".dll")}
    if "ucrtbase.dll" not in wanted.values() or len(wanted) < 30:
        raise RuntimeError("Incomplete x64 UCRT file table")

    extracted = SOURCE / "extracted"
    for cab in sorted(SOURCE.glob("*.cab")):
        target = extracted / cab.stem
        subprocess.run([str(seven_zip), "x", "-y", "-o" + str(target), str(cab)],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    files = []
    for identifier, name in sorted(wanted.items(), key=lambda pair: pair[1]):
        matches = list(extracted.glob("*/" + identifier))
        if len(matches) != 1:
            raise RuntimeError("Cannot uniquely locate SDK file: " + name)
        source = matches[0]
        image = pefile.PE(str(source))
        if image.FILE_HEADER.Machine != 0x8664:
            raise RuntimeError("Wrong runtime architecture: " + name)
        info = image.VS_FIXEDFILEINFO[0]
        version = [info.FileVersionMS >> 16, info.FileVersionMS & 65535,
                   info.FileVersionLS >> 16, info.FileVersionLS & 65535]
        if version[:3] != [10, 0, 14393]:
            raise RuntimeError("Unexpected UCRT version: " + str(version))
        image.close()
        shutil.copy2(str(source), str(OUTPUT / name))
        files.append({"file": name, "version": ".".join(map(str, version)), "sha256": sha256(source)})
    extra = set(path.name for path in OUTPUT.glob("*.dll")) - set(wanted.values())
    if extra:
        raise RuntimeError("Unexpected DLLs in runtime directory: " + repr(extra))
    manifest = {"sdk": "10.0.14393.795", "architecture": "x64", "source": BASE_URL,
                "payloadSha256": PAYLOADS, "files": files}
    (OUTPUT / "runtime-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("Verified and extracted {} x64 UCRT DLLs into {}".format(len(files), OUTPUT))


if __name__ == "__main__":
    prepare()
