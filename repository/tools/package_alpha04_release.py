"""Promote validated candidate files; no application imports or execution."""
import json
import zipfile

from package_unified_candidate8 import ROOT, digest, source_files


def package():
    source_record = json.loads((ROOT / "docs/UNIFIED-CANDIDATE-8-BUILD.json").read_text(encoding="utf-8-sig"))
    if not source_record.get("crossVersionDeploymentValidated"):
        raise RuntimeError("Candidate regression acceptance is missing")
    source = source_files(source_record)
    files = dict(source)
    files["README.txt"] = (ROOT / "docs/ALPHA-0.4-RELEASE-README.md").read_bytes()
    files["RELEASE-NOTES.en.md"] = (ROOT / "docs/RELEASE-NOTES-Alpha-0.4.en.md").read_bytes()
    files["RELEASE-PROVENANCE.json"] = json.dumps({
        "source": source_record["file"], "sourceSha256": source_record["sha256"],
        "programFilesRecompiled": False, "acceptanceBasis": "User-reported VM regression",
        "acceptanceDate": "2026-10-16 Europe/London",
        "platforms": ["Vista SP2 x64", "Windows 7 x64", "Windows 8 x64", "Windows 8.1 x64", "Windows 10 x64", "Windows 11 x64"],
        "githubPublished": False}, indent=2).encode("utf-8")
    del files["SHA256SUMS.txt"]
    files["SHA256SUMS.txt"] = "".join(digest(data) + "  " + name + "\n" for name, data in sorted(files.items())).encode("utf-8")
    name = "JY Sysprep Alpha 0.4 x64"
    archive = ROOT / (name + ".zip")
    with zipfile.ZipFile(str(archive), "x", zipfile.ZIP_DEFLATED) as output:
        for path, data in sorted(files.items()):
            output.writestr(name + "/" + path, data)
    with zipfile.ZipFile(str(archive)) as check:
        if check.testzip() is not None:
            raise RuntimeError("Release archive CRC mismatch")
        for path, data in files.items():
            if check.read(name + "/" + path) != data:
                raise RuntimeError("Release archive file mismatch")
    # Verify all non-documentation source files, including every runtime file.
    changed = {"README.txt", "SHA256SUMS.txt"}
    if any(files[path] != data for path, data in source.items() if path not in changed):
        raise RuntimeError("Tested candidate payload changed")
    record = {"file": archive.name, "sha256": digest(archive.read_bytes()), "bytes": archive.stat().st_size,
              "files": len(files), "sourceSha256": source_record["sha256"], "sourceCandidate": 8,
              "allCandidateRuntimeFilesUnchanged": True, "archiveFilesVerified": True,
              "crossVersionDeploymentValidated": True, "validationBasis": "User report, tested VM configurations only",
              "hostRuntimeExecuted": False, "programFilesRecompiled": False, "githubPublished": False}
    (ROOT / "docs/ALPHA-0.4-RELEASE-BUILD.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    package()
