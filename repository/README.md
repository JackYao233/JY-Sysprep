# JY Sysprep

Windows 系统封装与镜像部署自动化框架。

A modular Windows Sysprep automation and image deployment framework.

## Alpha 0.3

当前开发版本采用 **TUI 文本配置向导**，使用逐项输入与分步骤提示，无需 Tkinter。Alpha 0.3 尚未完成实际部署验收；最新已核对的公开版本为 [Alpha 0.2](https://github.com/JackYao233/JY-Sysprep/releases/tag/Alpha_0.2)（核对日期：2026-10-14）。

主要功能：

- Windows 版本、架构、管理员权限与审核模式检测。
- Sysprep 文件和目录预检。
- 五步向导：基本设置 → 语言区域 → OOBE → 账户 → 确认。
- Audit/OOBE、关机/重启/退出、计算机名、时区、语言区域配置。
- 按系统能力提供 OOBE 选项、本地管理员账户与自动登录配置。
- 动态生成 x86/amd64 应答文件。
- 默认测试模式、执行前配置摘要与最终确认；默认不确认执行。
- 配置阶段 Ctrl+C 或输入结束取消。
- 程序日志与失败日志收集。

Current source uses a five-step console wizard. Test mode is enabled by default, and final confirmation defaults to cancellation. Configuration and XML logic have been checked on Python 3.7.9; actual deployment validation remains pending.

## 开发与运行

环境：Windows、Python 3.7.9（已测试）。运行代码只依赖 Python 标准库。

```powershell
git clone https://github.com/JackYao233/JY-Sysprep.git
cd JY-Sysprep
py -3.7 -m venv .venv37
.\.venv37\Scripts\python.exe main.py
```

本上传目录采用仓库根目录直接放置 `main.py` 的布局。上述命令适用于这套布局同步到 GitHub 后；原线上源码位于 `JY Sysprep/` 子目录。

在 PyCharm 中打开仓库根目录，选择 `.venv37/Scripts/python.exe`，设置 `main.py` 为入口、仓库根目录为工作目录。密码输入建议在 Terminal 中进行；部分 IDE 输出控制台不能隐藏 `getpass` 输入。

当前入口在启动向导前要求审核模式和预检通过，测试模式也受此限制。正式封装需要管理员权限。创建账户时，应答文件包含明文密码，请妥善保管。

## 检查与打包

```powershell
.\.venv37\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv37\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv37\Scripts\python.exe -m PyInstaller --noconfirm --distpath dist --workpath build "JY Sysprep Alpha 0.3.spec"
```

构建使用 Python 3.7.9 x64 和 PyInstaller 5.13.2。生成的 exe 放在 `dist/`，可作为 GitHub Release 附件；构建输出不提交到源码仓库。

已完成九项 Python 3.7 自动检查，包括源码及 spec 编译、TUI 配置与取消、XML 特殊字符处理与 UTF-8 文件读写。已生成独立 exe，并检查包内包含 Python 3.7 运行库和 TUI 模块、排除 GUI/Tkinter。尚未启动该 exe 或执行真实 Sysprep。

## 目录

```text
main.py                         TUI 入口
core/                           上下文、日志与任务基础
osdetect/                       Windows 检测
sysprep/                        配置、预检、应答文件与执行器
gui/                            暂保留的 GUI 实现，入口不加载
utils/                          工具模块
tests/                          TUI 与 Python 3.7 兼容性检查
docs/                           计划、兼容性与发布草稿
JY Sysprep Alpha 0.3.spec        当前打包配置
requirements-build.txt          构建依赖
.python-version                 Python 版本记录
.gitignore                      本地环境与构建输出排除规则
LICENSE                         MIT 许可
```

当前生成器使用 ElementTree 动态构建 XML；`sysprep/unattend/templates/` 保留模板文件，但生成流程不读取它。

## 当前限制与路线

优先验证 Windows 10/11。旧 Windows 与 Server 的代码映射不代表已验证部署兼容性。应答文件默认命名空间、环境策略、非默认系统目录与 ARM64 处理仍需完善，详见 [开发计划](docs/ALPHA-0.3-PLAN.md)。

| 版本 | 范围 |
| --- | --- |
| Alpha 0.1 | 基础封装与配置 |
| Alpha 0.2 | 审核模式与 Sysprep 文件检测 |
| Alpha 0.3 | TUI 配置向导完善，开发中 |
| Alpha 0.4 | 个性化配置 |
| Alpha 0.5 | 部署体验 |
| Beta | DISM/WIM 与镜像管理 |

[兼容性记录](docs/PYTHON-3.7-COMPATIBILITY.md) · [发布说明草稿](docs/ALPHA-0.3-RELEASE-NOTES.md) · [构建记录](docs/ALPHA-0.3-BUILD.json)

## License

[MIT](LICENSE)。
