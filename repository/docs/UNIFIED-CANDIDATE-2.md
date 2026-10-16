# Alpha 0.4 统一候选包 2：异常退出提示

2026-10-15。交付 `JY Sysprep Alpha 0.4 Unified Candidate 2 x64.zip`。完整解压后以管理员身份运行 `Start.cmd`，GUI/F8/TUI 入口不变。

## 问题及行为

候选包 1 在用户的 Windows 11 25H2 多系统环境中，Sysprep 已写成功标记，但 JY 窗口自动消失，后续 BCD 核对和重启未留下执行记录。用户确认期间没有自动重启，随后解压诊断包时 Explorer 崩溃。后一次 Explorer 崩溃不能解释更早发生的 JY 退出，进程消失的底层原因仍未确认。

本版先补齐异常提示，不引入 SYSTEM 任务或后台自动恢复，也不将当前问题宣称为已修复。

- 多系统正式封装前创建 `%ProgramData%\JY Sysprep\ExecutionRecords\<编号>\execution.json`，记录开始时间、PID、所选完成动作及 BCD 备份路径。
- 原子写入并刷新执行阶段：Sysprep 运行/返回、BCD 核对/完成、电源命令提交/接受、正常退出或失败。记录不包含账户密码，不作为自动修复的授权来源。
- 程序返回统一 CMD 入口后，由独立进程检查未完成记录；下次正常启动时也检查。PID 仍存活时不报中断，PID 已被较新进程复用时按原进程已退出处理。
- 使用原生 Windows 对话框显示最后阶段、开始时间、所选动作、执行记录及 BCD 备份路径，不依赖 Explorer 或 Tcl/Tk。确认后保留原始记录，避免重复提示同一次事件。
- `--check-last-run` 仅检查/提示记录，不进入向导，不执行 Sysprep、BCD 修复或关机重启。帮助及只读分流不弹出提示。
- 无法创建执行记录时，在启动 Sysprep 前停止；记录或检查失败不会绕过现有成功标记、BCD 复查等保护。

若整个会话、启动器或系统本身也被终止，无法保证立刻显示；下次启动仍会检查。直接双击现代 exe 时也支持下次启动检查，但退出后的即时检查需通过 `Start.cmd`。本版不能为没有创建过记录的候选包 1 补报历史中断。若系统已关机而记录只写到电源命令提交，提示应视为待核实，不能据此断言电源命令失败。

## 范围和验证

Vista 子目录直接沿用已验收包，所有文件保持一致；新记录及通知由现代入口使用。原候选包 1 和其验收记录保留。候选包 1 的 Vista/7/8/8.1/10 正式封装成功不能自动算作候选包 2 的部署验收。

共享源码在 Python 3.7 和 3.6 中各通过 68 项检查，包括中断识别、正常完成不提示、进程存活和 PID 复用、原生通知调用及确认状态、创建记录失败停止执行、原有 BCD 及关机保护。测试中的通知调用使用替身，不显示真实对话框；目标系统的可见效果与退出后的实际提示仍待虚拟机验证。未在开发机运行真实 Sysprep、BCD 修改或关机。

构建和包校验结果见 [UNIFIED-CANDIDATE-2-BUILD.json](UNIFIED-CANDIDATE-2-BUILD.json)。更新后的诊断包也会采集执行记录 JSON。

## 虚拟机测试

先保留当前失败现场及诊断结果，恢复封装前快照，再测试本版。保持此前 OOBE、通用化、不创建账户的配置。若窗口再次自动消失，观察是否显示未完成提示；若启动器也消失，下次启动应检查记录。记录最后阶段并运行新版 `JY Win11 Diagnostics.zip`，返回桌面诊断 ZIP。不要在已通用化的同一次会话中直接重复封装来测试提示。

## 构建

构建脚本已推进至[候选包 3](UNIFIED-CANDIDATE-3.md)，本包及其构建记录保留为历史交付；以下命令现在生成最新版。

```powershell
.\.venv37\Scripts\python.exe -m PyInstaller --noconfirm --distpath dist --workpath build/unified-modern "JY Sysprep Alpha 0.4 Modern.spec"
.\.venv37\Scripts\python.exe -B tools/package_unified.py
.\.venv37\Scripts\python.exe -B tools/check_unified.py
```
