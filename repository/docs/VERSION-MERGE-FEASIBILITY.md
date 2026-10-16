# Vista 与 Alpha 0.4 主版本合并可行性

评估日期：2026-10-15。

## 结论

**共用源码可行，已实现并检查；共用单个发行程序在技术上值得试验，但目前不能宣布跨版本部署兼容。** 当前适合保持一套业务与 GUI 源码、独立的 Vista 和主版本构建。

## 实际证据

- Vista GUI 直接复用主版本六步向导、F8/TUI、配置、生成器和执行器，没有复制一套 Vista GUI。
- 完整源码及两个环境的回归检查在 Python 3.6.8 和 Python 3.7.9 下各通过 62 项；Python 3.6 通过 dataclasses 0.8 补齐运行依赖。
- Python 3.6/Tcl-Tk 8.6.6 在当前开发机只读识别 Windows 11 Build 26300、AMD64，并选择主版本 `ConfiguredWindowsAdapter`；共享六页 GUI 可创建。见 [只读评估结果](MERGE-FEASIBILITY-CHECK.json)。
- Vista TUI experimental 2 有用户反馈的一次 OOBE 封装成功；GUI experimental 3 于 2026-10-15 经用户确认通过 Vista SP2 x64 单系统自检、交互操作及一次正式 GUI 封装（OOBE、通用化、关机、不创建账户，完成首次设置）。
- 统一候选包 1 已获用户反馈：前述 Vista、Windows 7、8、8.1、10、11 的 GUI 均正常。具体 Build、补丁及各系统 F8/TUI、测试输出和正式封装尚未逐项确认，也未覆盖 Windows Server、x86 或多系统组合。
- 用户随后反馈统一候选包在 Vista、Windows 7、8、8.1、10 的正式封装测试通过（按前述 OOBE、通用化、关机、不创建账户及完成首次设置的步骤）；Windows 11 的统一包正式部署仍待反馈。

## 三种方案

| 方案 | 可行性及代价 | 当前判断 |
| --- | --- | --- |
| 一套源码、两个独立构建 | 主版本保持 Python 3.7 工具链；Vista 使用 Python 3.6、旧 Tcl/Tk 和指定 UCRT | 当前最容易保持已知运行环境；已实现共享源码 |
| 一个 ZIP、两个隔离程序目录 | 将两个运行环境分别放入子目录，由入口选择；避免不同版本的同名 DLL 混装 | 已交付统一候选包 1，开发机检查及六个目标系统 GUI 反馈通过；跨版本部署验收待完成 |
| 一个程序统一 Python 3.6 工具链 | 共享源码可运行，但主线也要采用旧运行时和旧打包链；所有系统都需要重新验收 | 当前 Windows 11 上的只读识别及 GUI 检查提供初步证据；尚未交付统一程序 |

如果选择双运行环境启动器，系统选择必须发生在加载不兼容的 Python 运行库之前；不能先加载某个运行时再依靠 Python 分支来修复启动失败。两个目录应隔离 Python、Tcl/Tk、UCRT，不能把所有 DLL 混到根目录。

## 合并前需要完成

1. 已完成新 GUI 包在 Vista 的显示、F8 保存、测试文件生成、退出及一次正式 OOBE 封装验收；后续候选统一包仍需独立复测。
2. 为候选统一运行包分别在 Vista SP2、Windows 7、8、8.1、10、11 的 x64 单系统快照验证启动、GUI/TUI、测试输出及正式流程，记录 OS Build、补丁、虚拟硬件和耗时。
3. Vista 继续保留 SP2/x64/单系统限制；不能把现代系统多系统 BCD 流程的测试结果直接套用到 Vista。
4. 保留所有原有确认及失败停止保护；不要为实现统一入口而绕过权限、审核模式或预检。
5. 审计冻结程序调用系统工具时的 DLL 搜索环境。PyInstaller 会修改该搜索路径；这是需要检查的通用运行环境问题，未证实与此前 Vista 等待现象有关。

当前没有更换主版本 exe 或自动发布 GitHub 版本。合并与发行应以新包的虚拟机验收结果为依据。

统一候选包 1 已按双运行环境方案交付，操作及验收顺序见 [统一发行候选包](UNIFIED-CANDIDATE.md)。CMD 入口在加载 Python 前分流；Vista 文件与已验收原包一致，现代环境从当前共享源码重新构建。

## 参考

- [Python 3.6 的 Windows 支持范围](https://docs.python.org/zh-cn/3.6/using/windows.html)
- [PyInstaller 3.6 平台要求](https://pyinstaller.org/en/v3.6/requirements.html)
- [微软 UCRT 本地部署说明](https://learn.microsoft.com/en-us/cpp/windows/universal-crt-deployment)
- [PyInstaller 外部程序调用说明](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html#launching-external-programs-from-the-frozen-application)
