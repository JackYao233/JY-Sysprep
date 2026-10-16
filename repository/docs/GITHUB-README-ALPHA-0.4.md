# JY Sysprep

Windows 系统封装与镜像部署工具。Alpha 0.4 提供 GUI/TUI 双模式、Vista 独立运行环境和 Windows 11 多系统封装改进。

Windows Sysprep automation with a graphical wizard, a retained TUI, isolated Vista support, and an improved Windows 11 multiboot workflow.

## Alpha 0.4

- 默认启动六步 GUI；启动提示或 GUI 中按 **F8** 切换 TUI。
- 通过 `--gui` / `--tui` 指定界面。
- 统一 x64 便携发行包按系统选择 Vista 或现代运行环境，目标机无需安装 Python 或 VMware Tools。
- Windows 11 多系统正式封装使用当前管理员用户的独立无控制台辅助程序。
- 多系统流程先备份 BCD，以 Sysprep `/quit` 完成封装，再核对当前系统引导项，最后提交所选电源动作。
- 保留阶段记录、失败日志、未完成提醒及诊断采集入口。

Alpha 0.4 restores the GUI while retaining F8/TUI operation. The Windows 11 multiboot flow uses a separate elevated, windowless helper. The package includes its runtimes, BCD backup/verification, execution records, and diagnostics.

## 下载与启动 / Download and run

在 [GitHub Releases](https://github.com/JackYao233/JY-Sysprep/releases) 下载对应发行资产。待 Alpha 0.4 发布后，使用 `JY Sysprep Alpha 0.4 x64.zip`，完整解压并以管理员身份运行 `Start.cmd`。

Use the ZIP release asset, extract it completely, and run `Start.cmd` as administrator. Use `Start GUI.cmd` or `Start TUI.cmd` to choose an interface directly. Keep the entire directory structure, including both modern executables.

现代程序显示 candidate 7、Vista 显示原实验版标识，是因为发布包保留了经过测试的二进制文件，没有为更换标签重新编译。历史根目录 build 3 单文件程序属于旧构建。

The original candidate labels remain visible because the release package preserves the tested binaries without recompilation.

## 验证范围 / Validation scope

2026-10-16 用户反馈 Alpha 0.4 统一候选包 8 的虚拟机回归通过。

| 系统 / System | 用户反馈 / User-reported result |
| --- | --- |
| Windows Vista SP2 x64，单系统 | 原 Vista GUI 正式封装及 OOBE 通过；统一包入口回归通过 |
| Windows 7 / 8 / 8.1 / 10 x64 | 统一包回归通过 |
| Windows 11 x64，多系统 | 无 Tools 环境：候选 7 正式封装、自动重启、OOBE、桌面通过；统一包关机及 OOBE 通过 |

These are user-reported VM results within the tested configurations, not certification of every Windows build or option combination. Vista deployment is limited to single-system x64 installations. Windows Server, x86, and ARM64 are outside the release validation scope.

测试详情：[统一包验收记录](docs/UNIFIED-CANDIDATE-8.md)、[英文 Release 简介](docs/RELEASE-NOTES-Alpha-0.4.en.md)。

## 配置与输出 / Configuration and output

可配置 Audit/OOBE、关机/重启/退出、计算机名、语言区域、时区、OOBE 选项、账户及自动登录。部分选项按系统能力启用。

默认测试模式只生成应答文件；正式模式要求管理员权限、审核模式、预检及用户确认。
创建账户时，应答文件可能包含明文密码，不要上传生成的 XML 或整个作业目录。

| 内容 | 位置 |
| --- | --- |
| 测试应答文件 | 桌面 `JY-Sysprep-<系统名称>-unattend.xml` |
| 普通程序日志 | 桌面 `JY Sysprep Logs` |
| BCD 备份 | `%ProgramData%\JY Sysprep\BootBackups` |
| Win11 独立作业记录 | `%ProgramData%\JY-Sysprep-Job-*` |

默认测试模式用于查看配置和生成结果，不代表正式封装一定成功。封装前保存快照；正式流程中请勿注销或手动重启。

## 源码开发 / Development

现代环境使用 **Python 3.7.9 x64**；Vista 环境使用独立的 **Python 3.6.8 x64**。
主程序运行代码主要使用标准库；构建依赖在 `requirements-build.txt` 中固定。
Vista 的依赖与兼容性说明见 [Vista GUI 文档](docs/VISTA-GUI.md) 和 [Python 3.7 兼容性记录](docs/PYTHON-3.7-COMPATIBILITY.md)。

在 PyCharm 中使用仓库根目录作为工作目录。当前现代发行入口为 `modern_main.py`，
无控制台辅助入口为 `admin_worker_main.py`，Vista 入口为 `vista_main.py`。
`main.py` 保留共用流程及历史入口。源码模式适合界面与配置开发；新版独立封装路径需要打包程序和辅助 EXE。

在构建环境中分别打包，保持两个输出 EXE 在同一目录：

```powershell
python -m pip install -r requirements-build.txt
python -m PyInstaller --noconfirm --distpath dist/modern --workpath build/modern "JY Sysprep Alpha 0.4 Modern.spec"
python -m PyInstaller --noconfirm --distpath dist/modern --workpath build/worker "JY Sysprep Alpha 0.4 Worker.spec"
```

Build the modern entry and the windowless helper separately, then keep `JY Sysprep Modern.exe` and `JY Sysprep Worker.exe` together. Renaming the main executable to `JY Sysprep.exe` is used only in the unified package layout.

## 检查与问题反馈 / Checks and issue reports

自动化测试源文件保留，但不应在日常宿主机直接运行涉及执行流程的测试。
正式封装、引导修改、电源操作及运行验证均应放在可恢复的隔离虚拟机中。
测试替身不能作为唯一隔离措施，详见 [测试执行限制](TESTING.md)。

发行包的 `Check modern runtime.cmd` 和 `Check background.cmd` 用于目标虚拟机诊断。
若正式封装中断，保留现场，运行 `Diagnostics/Collect.cmd`，并提供系统 Build、启动布局、选项、最后阶段及去除敏感信息后的日志。

Packaging tools preserve specific historical source-archive hashes. Reproducing an archived candidate requires the matching source release ZIPs; those binaries belong in Releases and are not part of this source tree. Historical documents remain under `docs/` for traceability.
