# Alpha 0.4 统一候选包 3：执行生命周期与系统工具环境

2026-10-15。用户反馈重装 Windows 11 后，候选包 2 在多系统引导环境仍异常，且没有未完成提示。应将程序路径作为重点排查对象，不能继续以系统残留为主要解释。

根目录交付 `JY Sysprep Alpha 0.4 Unified Candidate 3 x64.zip`。本包修复已确认的程序薄弱点，Windows 11 故障是否因此解决仍须目标虚拟机验证。

## 修改

1. 原 GUI 执行任务使用 `daemon=True`，GUI 主循环一旦提前结束，进程可能在多系统 Sysprep /quit 返回、BCD 核对及电源动作完成前退出。改为非守护线程，并在 GUI 主循环退出时等待执行线程结束。回归测试模拟 GUI 提前退出，断言任务执行完成且线程退出后入口才返回。
2. 打包程序启动 Windows 系统工具时，之前直接继承冻结程序的 DLL 搜索覆盖。新增统一系统命令封装：冻结环境临时清除 DLL 搜索目录，剔除子进程 PATH 中的包路径，调用后恢复原目录；异常路径也恢复。用于 Sysprep、bcdedit 和 shutdown。此兼容处理遵循 [PyInstaller 官方说明](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html#launching-external-programs-from-the-frozen-application)，尚无证据证明它就是用户此次故障根因。
3. 执行记录更新失败时保留原始异常及日志收集机会，不让记录写入错误覆盖最初失败。沿用候选包 2 的执行阶段记录和原生提示。

非守护线程不能阻止 Windows 强制终止整个进程或会话；此版尚未加入 SYSTEM 后台任务。若启动器同时被终止，无法保证立即弹窗。不能把候选包 2 缺少即时提示直接解释为此次修复已经完成。

Vista 文件仍直接取自原已验收包，不重新构建；现代程序从当前共享源码新建。候选包 1、2 及其记录保留，部署结果不自动继承。

## 先做只读自检

在 Windows 7～11 中，完整解压，运行 `Check modern runtime.cmd`。结果写入同目录 `Modern-runtime-self-test.txt`。它使用隐藏 GUI、诊断用上下文和假任务验证 GUI 退出后的线程等待；系统程序仅运行 `cmd /d /c ver`。不会执行 Sysprep、读写 BCD、生成应答文件、关机或重启。

重点字段：

- `systemCommandPassed: true`
- `dllSearchRestored: true`
- `guiExitWaitsForExecution: true`
- `executionThreadDaemon: false`
- `sysprepExecuted: false`
- `bcdReadOrModified: false`

此自检可在现有问题环境运行。正式封装则需恢复封装前快照，以管理员身份通过 `Start.cmd` 进入，并沿用 OOBE、通用化、不创建账户的单次对照配置。若仍退出，返回新版诊断包采集结果和此自检文本；不要在同一次已通用化会话反复执行封装。

## 检查

用户随后正式测试仍失败，并确认现象完全相同：程序窗口自动消失、没有电源动作、没有未完成提示。因此候选包 3 未解决实际故障；只读自检通过不能替代正式部署结果。下一步读取本次执行记录及诊断包，区分线程正常返回、进程被终止与 BCD/电源处理失败，不继续无证据修改或继承验收状态。

2026-10-15，用户截图确认候选包 3 在 Windows 10.0.26300.9457 上的运行时自检通过：系统命令、DLL 搜索路径恢复、六页 GUI、切换逻辑、假任务退出等待均通过；执行线程为非守护线程，Python 3.7.9、Tcl/Tk 8.6.9。此次未执行 Sysprep、未读写 BCD；不标记正式封装通过。截图中的 Build 与此前故障包的 26200.7462 不同，后续对照需记录实际系统版本。

Python 3.6、3.7 各 73 项回归检查通过，涵盖 GUI 主循环退出、DLL 搜索路径恢复及原有失败停止保护。开发机未执行真实封装或电源操作。实际 ZIP 和冻结 exe 检查见 [构建记录](UNIFIED-CANDIDATE-3-BUILD.json)。

构建脚本 `tools/package_unified.py` 和 `tools/check_unified.py` 现以候选包 3 为目标。
