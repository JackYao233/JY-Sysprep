# Alpha 0.4 开发与验收记录

日期：2026-10-14。当前为 Alpha 0.4 build 3 开发测试版，新增多系统引导保护；尚未完成新流程的 Windows 虚拟机封装验收。

## 本版范围

根据用户决定：恢复 GUI 作为默认入口，保留 TUI，支持特殊按键进入文本模式。使用 F8，不新增第三方界面依赖，继续使用 Python 3.7.9。

## 使用方式

build 3 修复 GUI 关闭后的控制台等待问题：GUI 正常关闭后直接退出，不再显示“Press Enter to exit”。TUI（含 F8 转入和 GUI 不可用回退）保留退出提示；重定向输入时不等待。此前 build 2 exe 已归档到 `dist/archive/JY Sysprep Alpha 0.4-build2.exe`。

- 默认启动：控制台提示 2 秒内按 F8 进入 TUI，否则进入 GUI。
- 在 GUI 的任意配置页按 F8，或点击底部“F8 · 文本模式”，校验并保存当前页后切换到 TUI。
- 输入不合法时先纠正当前页；切换不会静默丢弃无效输入。
- TUI 使用已经保存的配置作为默认值；账户密码需重新输入。
- `--tui` 直接进入 TUI，适合 IDE、远程终端或错过启动按键的情况。
- `--gui` 直接进入 GUI，跳过启动按键等待；GUI 内 F8 仍有效。
- 缺少 Tkinter 或 Tk 无法初始化时回退到 TUI。
- 打包保留控制台用于 F8 与 TUI，GUI 模式下也会存在控制台窗口。

```powershell
.\.venv37\Scripts\python.exe main.py
.\.venv37\Scripts\python.exe main.py --gui
.\.venv37\Scripts\python.exe main.py --tui
```

## 已完成

- [x] 统一版本标识 Alpha 0.4。
- [x] GUI 默认入口、启动 F8、窗口 F8、显式模式参数。
- [x] 修复环境页没有 `collect()` 导致无法继续的问题。
- [x] 确认页每次进入时刷新配置摘要及按钮文案，复用 TUI 摘要格式。
- [x] 返回页面和顶部向后导航统一保存、校验；禁止跳过未经过的页面。
- [x] 基本配置与账户输入校验通过后再提交，避免部分写入。
- [x] 已有语言配置在 GUI 初始化时保持，不被固定中文预设覆盖。
- [x] 可调整窗口大小、滚动页面，底部导航固定显示。
- [x] 正式封装额外确认，默认“否”。
- [x] 后台线程执行，结果通过队列由 Tk 主线程显示。
- [x] 执行开始后禁止重复执行、导航及切换 TUI；失败后提示重新运行，避免对部分封装状态重试。
- [x] 测试成功显示输出路径，失败显示原因；执行异常写入程序日志。
- [x] 非审核模式或关键预检失败时，GUI 可查看原因但不能继续；TUI 退出。
- [x] 正式执行前重新检查文件环境、审核模式与管理员权限。
- [x] 统一生成器、执行器、预检的 Windows 目录来源；无效执行模式/动作拒绝。
- [x] 应答文件补齐默认命名空间；明确拒绝未实现的 ARM64 架构。
- [x] ActionFiles 缺失显示未通过的信息项，不再绿色通过；是否作为关键项仍保留原策略。
- [x] 新增 Alpha 0.4 spec、两个 PyCharm GUI/TUI 运行配置。

## 检查结果

Python 3.7.9 x64 下 **48 项检查通过**，包括九项实际 Tk 隐藏窗口测试和多系统 BCD/执行顺序/日志收集检查。

- GUI 页面导航、摘要刷新、输入校验、账户校验、F8 保存与切换。
- 正式确认取消、预检失败阻止继续、后台任务成功/失败与防重复执行。
- 控制台 F8 扫描码、显式模式参数、无控制台默认 GUI。
- 主入口关闭 GUI、转 TUI、GUI 不可用回退、环境失败展示。
- 原有 TUI、XML 生成与读写、Python 3.7 全源码及 spec 编译。
- 多系统检测、动态目标分区、备份成功校验、仅修改已识别的当前引导项并复查。
- 备份/封装/成功标记/引导修复失败时不提交自动关机或重启。
- 三阶段同名日志保持独立，不收集账户应答文件。

测试中的执行器均被替换为模拟对象，没有运行真实 Sysprep。

```powershell
.\.venv37\Scripts\python.exe -B -m unittest discover -s tests -v
```

## 构建

Python 3.7.9 x64 / PyInstaller 5.13.2。根目录 `JY Sysprep Alpha 0.4.exe` 已生成。归档检查确认包含 GUI、TUI、Python 3.7、Tkinter 扩展与 Tcl/Tk 资源；exe `--help` 启动检查通过。

```powershell
.\.venv37\Scripts\python.exe -m PyInstaller --noconfirm --distpath . --workpath build/python37-alpha04 "JY Sysprep Alpha 0.4.spec"
```

具体文件大小与 SHA-256 记录在 `ALPHA-0.4-BUILD.json`。

## 尚未完成

- [ ] 虚拟机中的实际 GUI 显示、键盘 F8 与高 DPI/低分辨率体验验收。
- [ ] Win7/8/8.1/10/11 上 Alpha 0.4 测试输出与正式封装回归。
- [ ] Windows 接受应答文件及实际 specialize/OOBE 验证；XML 可解析不等同于完整 schema 校验。
- [x] 多系统 BCD 检测、备份与当前系统兼容处理已实现；真实多系统回归仍待用户验证。
- [x] 补齐 generalize/specialize/OOBE 日志和 setuperr 收集，避免同名日志覆盖。
- [ ] 个性化引擎。
- [ ] 单独整理 Alpha 0.4 GitHub 上传目录与发布说明。

build 3 自动处理多系统当前引导项，行为详见 [多系统兼容说明](ALPHA-0.4-MULTIBOOT.md)。当前 Windows 目录由系统 API 获取，不使用此前 PE 中的 G:。旧 0.4 exe 已归档，Alpha 0.3 exe 和 GitHub 上传副本保持原样。

## 2026-10-15：Vista GUI 整合及合并评估

Vista TUI experimental 2 已有用户反馈的一次单系统 OOBE 封装成功。新 experimental 3 接入本项目同一套 GUI、F8/TUI 和执行流程，加入 Vista 字体回退、只读 GUI 自检和较长等待提示；打包为独立 GUI 便携 ZIP，旧包与主版本 exe 保留。

当前共享源码在 Python 3.6.8 和 Python 3.7.9 下各通过 62 项检查（含 12 项 GUI 检查）。GUI 包已完成开发机上的文件哈希、x64/运行库依赖、隔离环境下解压启动及六页 GUI/F8 自检。2026-10-15，用户确认 Vista SP2 x64 单系统虚拟机上的自检、交互及一次正式 GUI 封装/OOBE 成功。早先的 48 项记录对应 build 3 当时的检查范围。

同一套源码的合并已实现；单一运行包覆盖所有系统仍需跨版本验收。操作及结论见 [Vista GUI 说明](VISTA-GUI.md) 和 [合并可行性评估](VERSION-MERGE-FEASIBILITY.md)。

## 2026-10-15：统一发行候选包 1

采用单个 ZIP、Vista/modern 两个隔离运行环境和 CMD 系统分流入口。Vista 文件取自已验收 GUI experimental 3 原包；现代环境通过独立 spec 从当前共享源码构建，不替换原有 exe。9 个分流分支、缺失文件停止、ZIP 全文件哈希、Vista 原文件一致性、中文/空格路径、隔离环境下帮助及 Vista 只读 GUI 自检通过。Python 3.7 现有 62 项回归检查通过。实际跨版本部署仍待虚拟机验收，详见 [候选包说明](UNIFIED-CANDIDATE.md)。

用户随后反馈前述六个目标系统（Vista、7、8、8.1、10、11）的 GUI 均正常，已记录为 GUI 运行验收通过；F8/TUI、测试输出及正式封装不据此自动标记通过。

随后用户按正式封装测试步骤反馈 Windows 7 成功，已单独记录统一候选包的 Windows 7 正式封装/OOBE 通过；尚不标记整个系统范围的正式部署验收完成。

用户进一步反馈“vista通过”，统一候选包的 Vista 正式封装/OOBE 也已通过。剩余 Windows 8、8.1、10、11 的正式流程待反馈。

用户随后反馈“8 8.1 10测试完成”，按当前正式封装验收范围记录 Windows 8、8.1、10 通过；统一候选包目前仅剩 Windows 11 的正式流程待反馈。

## 2026-10-15：候选包 2 异常退出提示

Windows 11 多系统测试日志显示 Sysprep 已创建成功标记，JY 窗口自动消失，后续 BCD 和电源处理缺少执行证据。按用户要求加入多系统执行阶段持久记录、启动器返回后的独立原生提示、下次启动检查；不引入自动恢复，不修改 Vista 已验收包。共享源码在两套 Python 环境中各通过 68 项检查。详见 [候选包 2](UNIFIED-CANDIDATE-2.md)。

## 2026-10-15：候选包 3 程序侧修复

重装 Windows 11 后，用户确认候选包 2 在多系统引导环境仍异常且无未完成提示。改为非守护执行线程并在 GUI 主循环结束后等待任务，增加系统工具 DLL 搜索环境清理与恢复，保留最初异常，加入冻结 exe 的只读生命周期/系统工具自检。Python 3.6、3.7 各 73 项检查通过；真实 Windows 11 故障是否解决待验收。详见 [候选包 3](UNIFIED-CANDIDATE-3.md)。
