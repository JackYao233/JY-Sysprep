# JY Sysprep

**Windows Sysprep Automation and Image Deployment Framework**  
**Windows 系统封装与镜像部署自动化框架**

JY Sysprep is an open-source tool for configuring Windows system preparation through a step-by-step console wizard. The project aims to grow into a modular Windows image customization and deployment platform.

JY Sysprep 是一个开源 Windows 系统封装工具，通过分步骤文本向导配置并执行 Sysprep。项目计划逐步扩展为模块化的 Windows 镜像定制与部署平台。

[Download Alpha 0.3 / 下载](https://github.com/JackYao233/JY-Sysprep/releases/tag/Alpha_0.3) · [Source / 源码](https://github.com/JackYao233/JY-Sysprep/tree/main/repository) · [Issues / 问题反馈](https://github.com/JackYao233/JY-Sysprep/issues)

## Version Status | 版本状态

**Alpha 0.3 is available as a prerelease.** It starts directly in TUI mode and does not load GUI or Tkinter. Alpha 0.4 is under development, with a restored GUI and retained TUI access.

**Alpha 0.3 已发布为预发布版本。** 程序直接进入 TUI 文本向导，不加载 GUI 或 Tkinter。Alpha 0.4 正在开发，计划恢复 GUI，并保留 TUI 入口。

## Features | 当前功能

| Feature | 功能 |
| --- | --- |
| Windows version, architecture and administrator status detection | Windows 版本、架构及管理员权限检测 |
| Audit Mode detection and Sysprep file checks | 审核模式检测及 Sysprep 文件预检 |
| Five-step console configuration wizard | 五步文本配置向导 |
| Audit/OOBE and shutdown/reboot/quit options | Audit/OOBE 及关机、重启、退出选项 |
| Computer name, time zone, language and region settings | 计算机名、时区、语言及区域设置 |
| OOBE options offered according to system capabilities | 按系统能力提供 OOBE 选项 |
| Registered owner and organization settings | 注册所有者及组织信息设置 |
| Optional local administrator account and automatic sign-in | 可选本地管理员账户及自动登录 |
| Dynamic x86/x64 answer file generation | 动态生成 x86/x64 应答文件 |
| Configuration summary and final confirmation | 执行前配置摘要及最终确认 |
| Program logging and Sysprep failure log collection | 程序日志及 Sysprep 失败日志收集 |

The wizard follows **Basic settings → Language and region → OOBE → Account → Confirmation**. Test mode is enabled by default and only generates an answer file. Final confirmation defaults to cancellation; Ctrl+C cancels during configuration.

向导顺序为 **基本设置 → 语言区域 → OOBE → 账户 → 确认**。默认开启测试模式，仅生成应答文件；最终确认默认取消。配置过程中可按 Ctrl+C 取消。

Answer files are generated dynamically with ElementTree. Template files remain in the source tree, but the current generator does not read them.

应答文件由 ElementTree 动态生成。源码中保留 XML 模板，但当前生成流程不读取模板。

## Quick Start | 快速开始

### Packaged executable | 使用独立程序

1. Download `JY.Sysprep.Alpha.0.3.exe` from the [Alpha 0.3 release](https://github.com/JackYao233/JY-Sysprep/releases/tag/Alpha_0.3).
2. Run it as administrator in a Windows Audit Mode environment.
3. Follow the console wizard. Keep test mode enabled to review the generated answer file first.
4. To perform system preparation, run the wizard with test mode disabled and confirm the final configuration.

1. 从 [Alpha 0.3 发布页](https://github.com/JackYao233/JY-Sysprep/releases/tag/Alpha_0.3) 下载 `JY.Sysprep.Alpha.0.3.exe`。
2. 在 Windows 审核模式中以管理员身份运行。
3. 按文本向导完成配置，建议先保持测试模式，检查生成的应答文件。
4. 正式封装时关闭测试模式，并在最后确认配置。

The packaged executable includes the Python runtime; a separate Python installation is unnecessary. Both test and formal modes require Audit Mode and successful startup checks. Formal execution runs Sysprep with `/generalize` and the selected completion action.

独立程序包含 Python 运行库，无需另行安装 Python。测试与正式模式均要求处于审核模式并通过启动检查。正式执行会调用 Sysprep `/generalize`，随后按所选设置关机、重启或退出。

### Run from source | 从源码运行

The Alpha 0.3 source has been checked with **Python 3.7.9 x64** and uses only the Python standard library at runtime. The source currently resides in the repository's **`repository/` subdirectory**.

Alpha 0.3 源码已使用 **Python 3.7.9 x64** 检查，运行时仅使用 Python 标准库。当前 GitHub 源码位于 **`repository/` 子目录**。

```powershell
git clone https://github.com/JackYao233/JY-Sysprep.git
cd JY-Sysprep\repository
py -3.7 -m venv .venv37
.\.venv37\Scripts\python.exe main.py
```

In PyCharm, open `repository/`, select `.venv37/Scripts/python.exe`, and use that directory as the working directory. Run `main.py`. Use the Terminal for hidden password input.

在 PyCharm 中打开 `repository/`，选择 `.venv37/Scripts/python.exe`，将该目录设为工作目录，运行 `main.py`。密码隐藏输入建议使用 Terminal。

## Testing and Compatibility | 测试与兼容性

The developer reports VMware testing on Windows 7, 8, 8.1, 10 and 11. Single-system testing was reported as normal. Boot failures after Sysprep were observed in the multi-boot test environment, including Windows 8 and Windows 11. This does not establish universal compatibility or prove a Windows-version-specific defect.

开发者已在 VMware 中测试 Windows 7、8、8.1、10、11，并反馈单系统测试正常。多系统测试环境曾在 Sysprep 后出现启动异常，涉及 Windows 8 和 Windows 11。上述结果属于当前测试环境记录，不代表所有系统版本及配置均已通过兼容性验证，也不能据此判定为某一 Windows 版本的普遍问题。

Alpha 0.3 does not include automatic BCD backup or multi-boot repair. Multi-boot protection is being developed for Alpha 0.4. Windows Server mappings exist in the source but have not been deployment-validated. ARM64 is not validated.

Alpha 0.3 不包含自动 BCD 备份与多系统引导修复；相关保护正在 Alpha 0.4 中开发。源码包含 Windows Server 适配映射，但尚未完成部署验证；ARM64 未验证。

When creating an account, its password is written in plain text to the answer file, including test output. Keep these files private.

创建账户时，密码会以明文写入应答文件，测试文件也具有相同行为，请妥善保管。

## Development and Build | 开发与构建

Run these commands from `repository/` with the Python 3.7 environment created above:

在 `repository/` 中创建上述 Python 3.7 环境后执行：

```powershell
.\.venv37\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv37\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv37\Scripts\python.exe -m PyInstaller --noconfirm --distpath dist --workpath build "JY Sysprep Alpha 0.3.spec"
```

The build uses PyInstaller 5.13.2. Executables are generated in `dist/` and distributed as release assets.

构建使用 PyInstaller 5.13.2，生成的 exe 位于 `dist/`，通过 Release 附件分发。

## Project Structure | 项目结构

```text
JY-Sysprep/
├── README.md                    Project homepage / 项目首页
└── repository/                  Source and development files / 源码及开发文件
    ├── main.py                  TUI entry point / TUI 入口
    ├── core/                    Context and logging / 上下文与日志
    ├── osdetect/                Windows detection / 系统检测
    ├── sysprep/                 Configuration, XML and execution / 配置、XML 与执行
    ├── gui/                     Retained GUI source / 保留的 GUI 源码
    ├── utils/
    ├── tests/
    ├── docs/
    ├── requirements-build.txt
    ├── JY Sysprep Alpha 0.3.spec
    └── LICENSE
```

## Roadmap | 开发路线

| Version | Status / 状态 | Scope / 范围 |
| --- | --- | --- |
| Alpha 0.1 | Released / 已发布 | Basic Sysprep automation / 基础封装自动化 |
| Alpha 0.2 | Released / 已发布 | Audit Mode and Sysprep checks / 审核模式及 Sysprep 检查 |
| Alpha 0.3 | Prerelease available / 预发布已提供 | TUI wizard and Python 3.7 environment / 文本向导及 Python 3.7 环境 |
| Alpha 0.4 | In development / 开发中 | GUI with retained TUI, workflow and multi-boot protection / GUI 与 TUI 双模式、流程及多系统保护 |
| Later / 后续 | Planned / 计划中 | Personalization, deployment experience and DISM/WIM image management / 个性化、部署体验及 DISM/WIM 镜像管理 |

## Contributing and License | 贡献与许可

Suggestions, issue reports and contributions are welcome. For boot or deployment issues, include the Windows build, virtualization version if applicable, selected Sysprep options, single-system/multi-boot layout and relevant logs. Remove passwords and personal information before sharing.

欢迎提交建议、问题反馈及代码贡献。反馈启动或部署问题时，请提供 Windows Build、虚拟化软件版本（如适用）、Sysprep 选项、单系统或多系统布局及相关日志；分享前请移除密码和个人信息。

[MIT License / MIT 许可](https://github.com/JackYao233/JY-Sysprep/blob/main/repository/LICENSE)
