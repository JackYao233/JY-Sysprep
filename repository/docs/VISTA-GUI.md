# Vista GUI 便携实验版

2026-10-15，Alpha 0.4 Vista GUI experimental 3。

用户截图已确认 Vista SP2 x64（6.0.6002）上的只读 GUI 自检通过：六页、GUI→TUI 切换逻辑、Tcl/Tk 8.6.6 及 Python/UCRT/VC/Tcl/Tk 本地加载均正常，字体选择为 Segoe UI。2026-10-15，用户进一步确认交互验收通过：中文及布局、物理 F8 切换并保留配置、测试模式生成应答文件、关闭 GUI 时控制台退出。随后用户反馈 GUI 正式封装成功；本次测试按前述步骤采用单系统虚拟机、OOBE、通用化、关机、不创建账户，并完成首次设置进入桌面。

根目录交付：`JY Sysprep Alpha 0.4 Vista GUI Portable x64.zip`。完整解压后运行 `JY Sysprep Vista.exe`。此次构建使用独立 Python 3.6.8、Tcl/Tk 8.6.6、PyInstaller 3.6，携带原版 SDK 中的 41 个 UCRT/API-set DLL。目标机无需另行安装 Python、Tcl/Tk 或 VC/UCRT 运行库；本 GUI 包已通过 Vista 自检、交互验收及一次正式封装。

## 已整合的功能

- 默认启动六步 GUI，支持窗口调整和页面滚动。
- 启动控制台提示期间或 GUI 内按 F8 切换 TUI；`Start TUI.cmd` 直接进入文本向导。
- `--gui` / `--tui` 指定界面；GUI 初始化失败仍回退到 TUI。
- F8 前保存并校验当前页，沿用主版本的配置模型及执行流程。
- Vista 不支持的 OOBE 控件保持禁用，正式封装仍受 SP2 x64、审核模式、管理员权限和单系统限制。
- 中文字体优先使用 Microsoft YaHei UI；Vista 没有该字体时回退到 Microsoft YaHei，再考虑系统字体。
- GUI 关闭沿用主版本的直接退出逻辑；执行中禁止关闭及重复执行。
- 正式执行前显示 Vista 通用化可能等待十多分钟的提示，不添加虚假的进度百分比。

## 只读 GUI 自检

1. 将 ZIP 复制到 Vista SP2 x64，完整解压。
2. 先双击 `Check GUI.cmd`，它将结果保存为 `Vista-gui-self-test.txt`。
3. 核对 `guiSmokeCheckPassed: true`、`guiPagesChecked: 6`、`guiToTuiHandoffChecked: true`；`loadedLibraries` 给出实际运行库位置。

GUI 自检使用诊断用 Vista 数据和阻止执行的预检状态，在隐藏窗口中创建六个页面并检查 F8 切换逻辑。它不读取真实 Sysprep 预检、不生成应答文件、不执行封装、不读写 BCD。它不能代替真实系统预检、物理按键、显示效果及封装验收。

## Vista 实际界面验收

1. 在原来的 Vista SP2 x64 单系统审核模式快照中，以管理员身份运行 exe。
2. 检查六页内容是否完整、中文是否正常、禁用选项是否正确。
3. 在基本设置中输入测试计算机名，按 F8，确认 TUI 保留该值；随后取消，不执行封装。
4. 重新打开 GUI，使用测试模式生成应答文件，检查路径和配置内容。
5. 关闭 GUI，确认其控制台窗口也随程序退出。
6. 上述项目通过后，从封装前快照再测 GUI 正式 OOBE、关机、不开启账户创建；参考先前实际等待时间及日志判断进度。

TUI experimental 2 和 GUI experimental 3 均有用户反馈的一次 Vista 封装成功。GUI 包的验收来自本包实际测试；当前结论仅覆盖已测的 Vista SP2 x64 单系统配置，其他系统、账户组合及多系统不在此次验收范围内。

## 构建及检查

```powershell
.\.venv36-vista\Scripts\python.exe -B tools/prepare_vista_runtime.py
.\.venv36-vista\Scripts\python.exe -B tools/prepare_vista_tk.py
.\.venv36-vista\Scripts\python.exe -m PyInstaller --noconfirm --distpath dist --workpath build/vista-gui "JY Sysprep Alpha 0.4 Vista GUI Portable.spec"
.\.venv36-vista\Scripts\python.exe -B tools/package_vista_portable.py --gui
.\.venv36-vista\Scripts\python.exe -B tools/check_vista_portable.py --gui
```

构建机需要 7-Zip 和已下载的官方 Python 3.6.8 x64 安装包，目标机不需要。`prepare_vista_tk.py` 核对固定安装包 SHA-256 和内部组件哈希后提取文件，不运行安装程序；Tcl/Tk 来源清单随包保存为 `tk-manifest.json`。许可位于 `licenses/`。

开发机已通过 Python 3.6 和 Python 3.7 各 62 项检查，其中 GUI 检查 12 项。交付包验证包括 ZIP 全部文件哈希、x64 架构、API-set 依赖、清除 Tcl/Tk 环境变量及隔离 PATH 后的帮助和 GUI 自检、包内 Tcl/Tk 加载路径。构建记录见 [VISTA-GUI-BUILD.json](VISTA-GUI-BUILD.json)。

## 与主版本的关系

使用同一套 `gui/`、`main.py`、配置模型、生成器及执行器。Vista 入口仅保留目标版本检查、界面参数、自检和构建标识；Vista 差异在专用适配器中处理。旧 TUI ZIP 和现有主版本 exe 保留，没有因本次源码整合被替换。

合并评估见 [版本合并可行性](VERSION-MERGE-FEASIBILITY.md)。
