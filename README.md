# JY Sysprep

**Windows Sysprep Automation and Image Deployment Framework**  
**Windows 系统封装与镜像部署自动化框架**

JY Sysprep configures Windows system preparation through a graphical wizard or a text-based interface. Alpha 0.4 restores the GUI, retains the TUI, adds an isolated Vista runtime, and improves Windows 11 multiboot deployment.

JY Sysprep 通过图形或文本向导配置并执行 Windows 系统封装。Alpha 0.4 恢复 GUI、保留 TUI，加入 Vista 独立运行环境，并改进 Windows 11 多系统封装流程。

[Download Alpha 0.4 / 下载](https://github.com/JackYao233/JY-Sysprep/releases/tag/Alpha_0.4) · [Source / 源码](repository/) · [Issues / 问题反馈](https://github.com/JackYao233/JY-Sysprep/issues)

## Version Status | 版本状态

**Alpha 0.4 is available as a prerelease.** The unified x64 ZIP includes separate runtimes for Windows Vista SP2 and Windows 7–11. Python and VMware Tools are not required on the target system.

**Alpha 0.4 已发布为预发布版本。** 统一 x64 ZIP 按系统选择 Vista SP2 或 Windows 7–11 运行环境，目标机无需安装 Python 或 VMware Tools。

The package preserves the tested executables without recompilation, so the modern interface retains its candidate 7 label and the Vista runtime retains its original experimental label. Alpha 0.3 remains available as an older TUI release.

发行包原样保留已测试程序，因此现代界面仍显示 candidate 7，Vista 保留原实验版标识。Alpha 0.3 作为历史 TUI 版本保留。

## Features | 当前功能

| Feature | 功能 |
| --- | --- |
| Six-step GUI with F8 switching to TUI | 六步 GUI，按 F8 切换 TUI |
| Windows version, architecture, permissions and Audit Mode checks | 系统版本、架构、权限及审核模式检测 |
| Audit/OOBE and shutdown/reboot/quit options | Audit/OOBE 及关机、重启、退出选项 |
| Computer name, time zone, language and region settings | 计算机名、时区、语言及区域设置 |
| OOBE options adapted to system capabilities | 按系统能力提供 OOBE 选项 |
| Optional local administrator account and automatic sign-in | 可选本地管理员账户及自动登录 |
| Test mode enabled by default; final confirmation before deployment | 默认测试模式，正式封装前再次确认 |
| BCD backup and verification for the multiboot workflow | 多系统流程的 BCD 备份及核对 |
| Elevated, windowless helper for Windows 11 multiboot deployment | Win11 多系统封装使用管理员无控制台辅助进程 |
| Execution records, interrupted-run notifications and diagnostics | 执行记录、中断提醒及诊断采集 |

## Quick Start | 快速开始

1. Download [`JY.Sysprep.Alpha.0.4.x64.zip`](https://github.com/JackYao233/JY-Sysprep/releases/download/Alpha_0.4/JY.Sysprep.Alpha.0.4.x64.zip) and extract the entire archive.
2. Run `Start.cmd` as administrator in the Windows Audit Mode environment.
3. Use the GUI, press **F8** to switch to the TUI, or use `Start GUI.cmd` / `Start TUI.cmd` directly.
4. Keep test mode enabled first to review the generated answer file. Disable it and confirm the configuration when ready for formal system preparation.

一、 下载并完整解压 Alpha 0.4 ZIP。  
二、 在 Windows 审核模式中以管理员身份运行 `Start.cmd`。  
三、 默认进入 GUI；按 **F8** 切换 TUI，或使用对应启动脚本。  
四、 先通过测试模式检查应答文件，正式封装时关闭测试模式并确认配置。

Keep the full directory structure. Both executables under `runtimes/modern/` must remain together. Use the ZIP package for Alpha 0.4; the historical build 3 single EXE is an older artifact.

请保留完整目录结构，现代主程序与辅助程序必须位于同一目录。Alpha 0.4 请使用 ZIP 发行包；历史 build 3 单文件 EXE 属于旧构建。

Published ZIP SHA256:

```text
0B51BE3C43F8DB415A70AF234BA1899806E26FB4AD8FC4CF67EB902CCCCC69C2
```

## Testing and Compatibility | 测试与兼容性

On 2026-10-16, the developer reported successful VM regression testing within the following scope:

2026-10-16，开发者反馈以下虚拟机测试范围通过：

| System | Reported scope / 已反馈范围 |
| --- | --- |
| Windows Vista SP2 x64 | Original GUI deployment/OOBE and unified launcher regression; single-system only / 原 GUI 封装、OOBE 及统一入口回归，限单系统 |
| Windows 7 / 8 / 8.1 / 10 x64 | Unified-package regression / 统一包回归 |
| Windows 11 x64, multiboot | No-Tools deployment, automatic restart, OOBE and desktop; subsequent unified-package shutdown/OOBE / 无 Tools 封装、自动重启、OOBE、桌面及统一包关机/OOBE |

These results cover the tested VMs and configurations, not every Windows build or option combination. Windows Server, x86 and ARM64 are outside this release's validation scope. Vista multiboot deployment is not supported by this package.

上述结果适用于已测试虚拟机及配置，不代表所有 Windows Build 或选项组合均已验证。Windows Server、x86、ARM64 不在本次验收范围；本包不支持 Vista 多系统正式封装。

The windowless helper resolved the reported Windows 11 interruption in the tested environment. The evidence supports a terminal-lifecycle-related explanation, but does not establish that Windows Terminal was uninstalled or prove a single root cause.

无控制台辅助程序使本次 Win11 测试环境中的中断问题得到解决。结果支持终端生命周期相关的判断，但尚不能证明 Windows Terminal 被卸载或认定唯一根因。

[Validation details / 验收记录](repository/docs/UNIFIED-CANDIDATE-8.md) · [Release notes / 发布说明](repository/docs/RELEASE-NOTES-Alpha-0.4.en.md)

## Development and Build | 开发与构建

Source files live in **`repository/`**. The modern runtime uses **Python 3.7.9 x64**; Vista uses a separate **Python 3.6.8 x64** environment. In PyCharm, open `repository/` and use it as the working directory.

源码位于 **`repository/`**。现代环境使用 Python 3.7.9 x64，Vista 使用独立 Python 3.6.8 x64 环境。在 PyCharm 中打开该目录并将其设为工作目录。

Modern distribution entry: `modern_main.py`. Windowless helper entry: `admin_worker_main.py`. Vista entry: `vista_main.py`. Source mode is suitable for UI/configuration development; the independent deployment flow requires the packaged main executable and helper.

现代发行入口为 `modern_main.py`，无控制台辅助入口为 `admin_worker_main.py`，Vista 入口为 `vista_main.py`。源码模式适合界面和配置开发；独立封装流程需要配套打包程序。

Run these build commands from `repository/`, using an isolated build environment with Python 3.7 x64:

```powershell
python -m pip install -r requirements-build.txt
python -m PyInstaller --noconfirm --distpath dist/modern --workpath build/modern "JY Sysprep Alpha 0.4 Modern.spec"
python -m PyInstaller --noconfirm --distpath dist/modern --workpath build/worker "JY Sysprep Alpha 0.4 Worker.spec"
```

Keep `JY Sysprep Modern.exe` and `JY Sysprep Worker.exe` together. Unified packaging renames the main executable to `JY Sysprep.exe` while preserving its contents.

自动化测试源文件保留。涉及执行流程的测试、正式封装、引导修改和电源操作应在可恢复的隔离虚拟机中进行；测试替身不是唯一隔离措施。请先阅读 [测试执行限制](repository/TESTING.md)。

Tests and deployment flows can invoke real system operations. Review [TESTING.md](repository/TESTING.md) before execution and use a disposable, isolated VM for runtime validation.

## Diagnostics and Contributions | 诊断与反馈

If deployment is interrupted, preserve the current state and run `Diagnostics/Collect.cmd` from the release package. Include the Windows build, selected options, single-system/multiboot layout, last recorded stage and relevant diagnostics in an issue. Do not repeat Sysprep on the interrupted image.

若封装中断，请保留现场并运行发行包内的 `Diagnostics/Collect.cmd`。反馈时提供系统 Build、选项、启动布局、最后阶段及诊断记录。不要在已中断的镜像上重复封装。

Generated answer files may contain plaintext account passwords, including test output. Remove passwords and personal information before sharing files; do not publish an entire job directory.

生成的应答文件可能包含明文账户密码，测试输出也可能如此。分享前移除密码和个人信息，不要公开整个作业目录。

Suggestions, issue reports and contributions are welcome. Personalization and broader image-management features remain future work.

欢迎提交建议、问题反馈及贡献。个性化配置与更广泛的镜像管理功能仍为后续计划。
