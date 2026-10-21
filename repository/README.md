# JY Sysprep

Windows Sysprep automation with a graphical wizard and a text interface.

Windows 系统封装工具，提供图形向导及文本模式。

[Releases / 下载](https://github.com/JackYao233/JY-Sysprep/releases) · [Source / 源码](.) · [Issues](https://github.com/JackYao233/JY-Sysprep/issues)

## Alpha 0.5

Alpha 0.5 adds Windows Server support and combines the runtimes into one **x64 EXE**, approximately **16.2 MB**. Python and VMware Tools do not need to be installed on the target system. The executable automatically extracts its embedded resources at startup.

Alpha 0.5 新增 Windows Server 支持，整合为约 **16.2 MB 的单个 x64 EXE**。目标系统无需安装 Python 或 VMware Tools，程序启动时自动释放内置资源。

- Six-step GUI; press **F8** to switch to TUI. / 六步图形向导，F8 切换文本模式。
- Configure Audit/OOBE, shutdown/restart/quit, computer name, language, region, accounts and automatic sign-in. / 配置启动模式、完成动作、计算机名、区域、账户及自动登录。
- Test mode generates an answer file without running Sysprep. / 测试模式仅生成应答文件。
- BCD backup and verification for multiboot deployment. / 多系统引导备份及核对。
- Independent elevated, windowless helper for Windows 11 and Server 2025 multiboot deployment. / Win11、Server 2025 多系统封装使用管理员无控制台辅助进程。
- Execution records and interrupted-run notifications. / 执行记录及中断提示。

## Quick start / 使用方法

1. Download `JY Sysprep Alpha 0.5 x64.exe` from Releases and compare its SHA256 with the accompanying checksum file.
2. Run it as administrator in the target Windows **Audit Mode** environment.
3. Keep test mode enabled first and review the generated answer file.
4. Disable test mode, review the configuration and confirm when ready to execute Sysprep.

从 Releases 下载 EXE 和校验文件；在目标系统的审核模式中以管理员身份运行。
先用默认测试模式检查应答文件，再取消测试模式执行正式封装。
`--gui` / `--tui` 可直接指定界面。首次启动需要自动释放内置资源，无需手动解压。

The tested Candidate 3 executable is distributed unchanged under the release filename. Its window title still says `single EXE candidate 3`; it has not been recompiled just to change the label.

发行文件由已测试的候选版 3 原样复制，窗口仍显示 `single EXE candidate 3`，未为更换标题重新编译。

SHA256:

```text
D23689BD766B09EC5C32F2D746F7742085EB64DCE2D1FD6AD1015DB39CC61ACF
```

## Reported VM validation / 虚拟机验收

On 2026-10-19, the maintainer confirmed the following x64 regression scope passed for the single-EXE Candidate 3:

2026-10-19，维护者确认单 EXE 候选版 3 的以下 x64 回归范围通过：

| Client / 客户端 | Server / 服务器 |
| --- | --- |
| Vista SP2; Windows 7, 8, 8.1, 10, 11 | Server 2008 SP2, 2008 R2, 2012, 2012 R2, 2016, 2019, 2022, 2025 |

Validation is based on maintainer VM feedback for the tested configurations; successful deployment logs were not independently reviewed for every system. Vista formal deployment remains single-system only. Server Core, domain environments, configured server roles, x86 and ARM64 are outside the validated scope. Results do not cover every build or option combination.

验收基于维护者的虚拟机反馈，未逐系统独立核验成功日志。Vista 正式封装限单系统；Server Core、域环境、已配置服务器角色、x86 和 ARM64 不在已验收范围，不代表所有 Build 和选项组合均已验证。

[Validation / 验收记录](docs/ALPHA-0.5-SINGLE-EXE.md) · [Release notes / 发布说明](docs/RELEASE-NOTES-Alpha-0.5.en.md)

## Development / 开发

Open **`repository/`** in PyCharm. The single-file build uses an isolated **Python 3.6.8 x64** environment with pinned PyInstaller 3.6 dependencies and verified app-local runtime files. Normal usage of the release does not require this build environment.

在 PyCharm 中打开 `repository/`。单文件构建使用独立 Python 3.6.8 x64 环境；使用发行 EXE 无需配置开发环境。

[Build instructions / 构建说明](docs/ALPHA-0.5-BUILD.md) · [Test execution boundaries / 测试执行边界](TESTING.md)

Do not run deployment flows or the full test suite on an everyday host. Use an isolated, disposable VM with a recoverable snapshot. Answer files can contain account passwords; keep generated files and diagnostic logs out of Git.

正式封装及完整测试套件仅在可恢复快照的隔离虚拟机中执行。应答文件可能包含密码，请勿上传生成的应答文件或真实诊断日志。
