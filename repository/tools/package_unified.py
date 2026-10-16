"""Assemble isolated runtimes; preserve the accepted Vista archive byte-for-byte."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = "JY Sysprep Alpha 0.4 Unified Candidate 3 x64"


def digest(data):
    return hashlib.sha256(data).hexdigest().upper()


def package():
    if sys.version_info[:2] != (3, 7) or sys.maxsize <= 2 ** 32:
        raise RuntimeError("Use the Python 3.7 x64 build environment")
    vista = json.loads((ROOT / "docs/VISTA-GUI-BUILD.json").read_text(encoding="utf-8"))
    vista_archive = ROOT / vista["file"]
    if digest(vista_archive.read_bytes()) != vista["sha256"]:
        raise RuntimeError("Accepted Vista archive hash mismatch")
    modern = ROOT / "dist/JY Sysprep Modern.exe"
    files = {}
    with zipfile.ZipFile(str(vista_archive)) as source:
        for item in source.infolist():
            if item.is_dir():
                continue
            path = Path(item.filename)
            if path.is_absolute() or ".." in path.parts or len(path.parts) < 2:
                raise RuntimeError("Invalid Vista archive path")
            relative = Path(*path.parts[1:]).as_posix()
            files["runtimes/vista/" + relative] = source.read(item)
    files["runtimes/modern/JY Sysprep.exe"] = modern.read_bytes()
    files["Start.cmd"] = (ROOT / "tools/unified/Start.cmd").read_text().replace("\n", "\r\n").encode("ascii")
    files["Start TUI.cmd"] = b'@echo off\r\ncall "%~dp0Start.cmd" --tui\r\nexit /b %errorlevel%\r\n'
    files["Start GUI.cmd"] = b'@echo off\r\ncall "%~dp0Start.cmd" --gui\r\nexit /b %errorlevel%\r\n'
    files["Check modern runtime.cmd"] = (b'@echo off\r\nsetlocal\r\npushd "%~dp0"\r\n'
        b'"runtimes\\modern\\JY Sysprep.exe" --runtime-self-test > "Modern-runtime-self-test.txt" 2>&1\r\n'
        b'set "jy_result=%errorlevel%"\r\ntype "Modern-runtime-self-test.txt"\r\npause\r\npopd\r\nexit /b %jy_result%\r\n')
    files["README.txt"] = ("JY Sysprep Alpha 0.4 Unified Candidate 3 x64\n\n"
        "完整解压，以管理员身份运行 Start.cmd；默认 GUI，按 F8 可切换 TUI。\n"
        "Start GUI.cmd / Start TUI.cmd 可直接选择界面。\n"
        "入口仅识别系统并启动对应程序，不执行封装操作；程序内仍需配置和确认。\n"
        "本版新增现代系统多系统封装执行记录及异常退出提示。\n"
        "候选包 3 修复 GUI 退出导致守护执行线程被截断的风险，并隔离系统工具的 DLL 搜索路径。\n"
        "Windows 7～11 可先运行 Check modern runtime.cmd，只读检查会生成 Modern-runtime-self-test.txt。\n"
        "若前端退出且流程未完成，启动器返回后或下次启动时提示失败阶段与记录路径。\n"
        "若整个会话或启动器被终止，无法保证立即弹窗；下次启动仍会检测。\n"
        "提示不会自动修复或重启，也不表示窗口消失的根因已解决。\n"
        "Vista SP2 x64 使用 runtimes/vista，Windows 7～11 x64 使用 runtimes/modern。\n"
        "无需在目标机安装 Python。请保留目录结构，不要移动或混合 DLL。\n"
        "Vista 子包已通过一次单系统 GUI 封装；统一入口及新的现代系统构建仍需虚拟机验收。\n"
        "本包不承诺 Windows Server、x86 或 ARM64 支持。Vista 不支持多系统封装。\n"
        "先在封装前快照中验证启动、中文界面、F8、测试输出及关闭，再验证正式 OOBE。\n"
        "Start.cmd --route-only 只输出所选运行环境，不启动程序。\n"
        "Vista 原包中的 README 和校验表保留作为来源记录；统一包文件以根目录 SHA256SUMS.txt 为准。\n"
        "第三方许可见 runtimes/vista/licenses 和 runtimes/modern/licenses。\n").encode("utf-8-sig")
    licenses = ROOT / ".venv37/Lib/site-packages/PyInstaller-5.13.2.dist-info/COPYING.txt"
    files["runtimes/modern/licenses/PyInstaller-bootloader.txt"] = licenses.read_bytes()
    files["runtimes/modern/licenses/Python.txt"] = (Path(sys.base_prefix) / "LICENSE.txt").read_bytes()
    files["runtimes/modern/licenses/Tcl-Tk.terms"] = (Path(sys.base_prefix) / "tcl/tk8.6/license.terms").read_bytes()
    manifest = {name: digest(data) for name, data in sorted(files.items())}
    files["SHA256SUMS.txt"] = "".join("{}  {}\n".format(value, key) for key, value in manifest.items()).encode("utf-8")
    archive = ROOT / (NAME + ".zip")
    with zipfile.ZipFile(str(archive), "w", zipfile.ZIP_DEFLATED) as output:
        for name, data in sorted(files.items()):
            output.writestr(NAME + "/" + name, data)
    record = {"file": archive.name, "sha256": digest(archive.read_bytes()),
              "bytes": archive.stat().st_size, "version": "Alpha 0.4 unified candidate 3",
              "vistaSourceSha256": vista["sha256"], "modernPython": "3.7.9 x64",
              "vistaPython": "3.6.8 x64", "files": len(files),
              "crossVersionDeploymentValidated": False}
    (ROOT / "docs/UNIFIED-CANDIDATE-3-BUILD.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    # Preserve historical code above; the command-line entry assembles the
    # current candidate from verified source archives without rebuilding EXEs.
    from package_unified_candidate8 import package as package_current
    package_current()
