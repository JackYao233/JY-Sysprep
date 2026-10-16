"""Verify and package the onedir build. Does not run Sysprep."""
import hashlib
import json
from pathlib import Path
import shutil
import stat
import zipfile


ROOT = Path(__file__).resolve().parents[1]
NAME = "JY Sysprep Alpha 0.4 Vista Portable x64"
FOLDER = ROOT / "dist" / NAME


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def package(gui=False):
    import pefile

    name = "JY Sysprep Alpha 0.4 Vista GUI Portable x64" if gui else NAME
    folder = ROOT / "dist" / name
    # MSI-extracted Tcl files may be read-only; make generated output rebuildable.
    for generated in folder.rglob("*"):
        if generated.is_file():
            generated.chmod(generated.stat().st_mode | stat.S_IWRITE)
    runtime_path = ROOT / "build" / "vista-runtime" / "x64" / "runtime-manifest.json"
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    if any((folder / file).exists() for file in ("Vista-self-test.txt", "Vista-gui-self-test.txt")):
        raise RuntimeError("Rebuild the distribution first; do not package a generated test report")
    for item in runtime["files"]:
        if digest(folder / item["file"]) != item["sha256"]:
            raise RuntimeError("Packaged runtime hash mismatch: " + item["file"])
    for path in list(folder.glob("*.dll")) + list(folder.glob("*.pyd")) + list(folder.glob("*.exe")):
        image = pefile.PE(str(path))
        if image.FILE_HEADER.Machine != 0x8664:
            raise RuntimeError("Wrong architecture in portable package: " + path.name)
        for entry in getattr(image, "DIRECTORY_ENTRY_IMPORT", []):
            dependency = entry.dll.decode("ascii").lower()
            if dependency.startswith(("api-ms-", "ext-ms-")) and not (folder / dependency).exists():
                raise RuntimeError("Missing app-local API-set dependency: " + dependency)
        image.close()

    licenses = folder / "licenses"
    licenses.mkdir(exist_ok=True)
    copies = [
        (ROOT / ".runtime-vista/Python36/LICENSE.txt", licenses / "Python-and-Microsoft-Runtime.txt"),
        (ROOT / ".venv36-vista/Lib/site-packages/dataclasses-0.8.dist-info/LICENSE.txt", licenses / "dataclasses.txt"),
        (ROOT / ".venv36-vista/Lib/site-packages/PyInstaller-3.6.dist-info/COPYING.txt", licenses / "PyInstaller-bootloader.txt"),
        (ROOT / "build/vista-downloads/sdk-manifest/u2", licenses / "Windows-SDK-License.rtf"),
        (runtime_path, folder / "runtime-manifest.json"),
    ]
    if gui:
        copies += [
            (ROOT / ".runtime-vista/Python36/tcl/tk8.6/license.terms", licenses / "Tcl-Tk-license.terms"),
            (ROOT / "build/vista-runtime/tk-manifest.json", folder / "tk-manifest.json"),
        ]
    for source, target in copies:
        shutil.copy2(str(source), str(target))
    (folder / "README.txt").write_text(
        "JY Sysprep Alpha 0.4 Vista Portable x64 - experimental 2\n\n"
        "目标：Windows Vista SP2 x64、单系统。默认使用 TUI 文本向导。\n"
        "本包随附 Python、VC 运行库和 UCRT，无需另行安装。\n"
        "请解压整个文件夹，保留全部文件；不要只复制 exe。\n\n"
        "1. 先双击 Check runtime.cmd，只读自检结果保存到 Vista-self-test.txt。\n"
        "2. 确认 xmlCheckPassed 为 true。loadedLibraries 显示实际加载的 DLL 路径。\n"
        "3. 在 Vista 审核模式中，以管理员身份运行 JY Sysprep Vista.exe。\n"
        "4. 先保持测试模式，检查生成的应答文件，再测试正式封装。\n\n"
        "自检不执行 Sysprep、不生成应答文件、不读写 BCD。\n"
        "正式封装会写入应答文件、备份 BCD，并按选择关机、重启或退出。\n"
        "账户密码会以明文写入应答文件，请妥善保管。\n\n"
        "已通过开发机检查；尚未在无 UCRT 更新的 Vista 中完成验收。\n"
        "Windows 10/11 会优先使用系统 UCRT，开发机测试不能证明 Vista 免安装兼容。\n"
        "如启动失败，请保留完整错误文字和 Vista-self-test.txt。\n\n"
        "本包使用微软 Windows SDK 10.0.14393.795 的 x64 可再发行运行库。\n"
        "第三方许可见 licenses；运行库来源及校验值见 runtime-manifest.json。\n",
        encoding="utf-8-sig")
    (folder / "Check runtime.cmd").write_bytes(
        b'@echo off\r\nsetlocal\r\npushd "%~dp0"\r\n'
        b'"JY Sysprep Vista.exe" --self-test > "Vista-self-test.txt" 2>&1\r\n'
        b'set "jy_test_result=%errorlevel%"\r\ntype "Vista-self-test.txt"\r\n'
        b'echo.\r\necho Read-only test exit code: %jy_test_result%\r\n'
        b'echo Report saved to Vista-self-test.txt\r\npause\r\npopd\r\nexit /b %jy_test_result%\r\n')
    if gui:
        readme = (folder / "README.txt").read_text(encoding="utf-8-sig")
        readme = readme.replace("Vista Portable x64 - experimental 2", "Vista GUI Portable x64 - experimental 3")
        readme = readme.replace("默认使用 TUI 文本向导。", "默认进入 GUI；启动提示或 GUI 中按 F8 可进入 TUI。")
        readme += ("\nGUI 验收：先双击 Check GUI.cmd，检查 guiSmokeCheckPassed 为 true。\n"
                   "该项使用诊断数据检查六个页面与 F8，不执行真实封装。\n"
                   "之后在审核模式中运行程序，通过 GUI 生成测试文件，并尝试 F8。\n"
                   "若需要直接进入文本向导，运行 Start TUI.cmd。\n"
                   "GUI 关闭后应直接退出；实际启动及封装仍待本 GUI 包的 Vista 验证。\n"
                   "此前 TUI 包已反馈封装成功，配置阶段可能等待十多分钟，应结合日志观察进度。\n")
        (folder / "README.txt").write_text(readme, encoding="utf-8-sig")
        (folder / "Check GUI.cmd").write_bytes(
            b'@echo off\r\nsetlocal\r\npushd "%~dp0"\r\n'
            b'"JY Sysprep Vista.exe" --gui-self-test > "Vista-gui-self-test.txt" 2>&1\r\n'
            b'set "jy_test_result=%errorlevel%"\r\ntype "Vista-gui-self-test.txt"\r\n'
            b'echo.\r\necho GUI self-test exit code: %jy_test_result%\r\npause\r\n'
            b'popd\r\nexit /b %jy_test_result%\r\n')
        (folder / "Start TUI.cmd").write_bytes(
            b'@echo off\r\n"%~dp0JY Sysprep Vista.exe" --tui\r\n')
    files = sorted(path for path in folder.rglob("*") if path.is_file() and path.name != "SHA256SUMS.txt")
    (folder / "SHA256SUMS.txt").write_text(
        "".join("{}  {}\n".format(digest(path), path.relative_to(folder).as_posix()) for path in files),
        encoding="utf-8")
    archive = ROOT / (name + ".zip")
    with zipfile.ZipFile(str(archive), "w", zipfile.ZIP_DEFLATED) as output:
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                output.write(str(path), str(Path(name) / path.relative_to(folder)))
    with zipfile.ZipFile(str(archive)) as output:
        if output.testzip() is not None:
            raise RuntimeError("ZIP verification failed")
    record = {
        "file": archive.name, "version": "Alpha 0.4 Vista GUI experimental 3" if gui else "Alpha 0.4 Vista experimental 2",
        "target": "Vista SP2 x64 client, single-system", "format": "portable onedir ZIP",
        "bytes": archive.stat().st_size, "sha256": digest(archive),
        "python": "3.6.8 x64", "pyinstaller": "3.6", "ucrtSdk": runtime["sdk"],
        "appLocalUcrtDlls": len(runtime["files"]), "allNativeFilesX64": True,
        "apiSetImportsPresent": True, "zipIntegrityVerified": True,
        "launchedOnVistaWithoutUcrtUpdate": None, "realSysprepTested": False,
        "guiIncluded": gui,
    }
    record_name = "VISTA-GUI-BUILD.json" if gui else "VISTA-PORTABLE-BUILD.json"
    (ROOT / "docs" / record_name).write_text(json.dumps(record, indent=2), encoding="utf-8")
    print("Created {} ({} bytes)".format(archive, archive.stat().st_size))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--gui", action="store_true")
    package(gui=parser.parse_args().gui)
