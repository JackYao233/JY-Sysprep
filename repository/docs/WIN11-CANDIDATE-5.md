# Windows 11 修复候选 5

后续完整诊断已确认：Sysprep 在虚拟机时间 06:36:02 创建本次成功标记；
06:39:52 相关进程已不存在，BCD 仍未固定，正式流程未完成。
调查记录及下一步见 [候选 6](WIN11-CANDIDATE-6.md)。下方“待采集”描述保留历史顺序。

本包自带 Python 3.7.9 运行环境，目标虚拟机不需要安装 Python 或 VMware Tools。
这是尚待虚拟机验收的修复候选，不表示 Windows 11 封装问题已经解决。

用户反馈：已恢复到无 Tools 快照后，候选 5 管理员后台诊断通过。
截图显示 queued → worker_started → completed，executionContext=administrator，
workerSession=1，workerElevated=true，账户 SID 为用户 SID（非 SYSTEM）。
sysprepExecuted、bcdReadOrModified、powerActionExecuted 均为 false。
此结果只确认诊断进程启动和结束，正式封装及自动电源动作仍待验证。

随后的正式测试未确认完成：用户提供 status.json 和 worker.log，bootstrap.log 为空。
记录显示管理员会话 1，worker PID 4404，预检和 BCD 备份通过，随后停在
`sysprep_running`，没有返回、引导复查或电源命令记录。本次 Sysprep 成功与否、
进程是否仍存活尚待采集；不得认定管理员独立进程方案已解决原问题。

## 本次修改

- 撤销候选 4/R1 的 SYSTEM 计划任务入口，不创建或运行计划任务。
- Windows 11 多系统正式封装改由当前已提升权限的管理员用户启动独立进程。
  子进程核对相同账户、会话及 Windows 目录，拒绝 SYSTEM、服务账户、会话 0。
- 复制执行文件到受限的 ProgramData 作业目录，使用单独的临时运行目录，
  不沿用 GUI 的 PyInstaller 解压目录。
- 保留本次 Sysprep 成功标记、当前引导项核对、BCD 备份及阶段落盘。
  只有本次封装和 BCD 核对都通过，才提交用户选择的电源动作。
- 新增 `bootstrap.log`，捕获 Python 主流程启动前后的标准输出及错误。
  进程退出或启动超时会显示诊断目录，不会自动重新运行 Sysprep。

独立进程用于减少对 GUI/控制台生命周期的依赖，不保证在用户注销、
系统终止会话或其他强制结束进程的情况下存活。原始进程消失的根因仍未确认。

## 在虚拟机内依次验证

1. 使用你恢复后的无 Tools 封装前快照；完整解压到虚拟机本地磁盘的新目录。
2. 运行 `Check runtime.cmd`。应报告 candidate 5，检查系统命令、GUI、界面切换。
3. 右键 `Check background.cmd`，以管理员身份运行。它创建管理员独立诊断进程，
   不运行 Sysprep、不读取或修改 BCD、不执行电源动作。
   窗口显示进度并生成 `Background-check.txt`。
4. 诊断结果应为 `stage: completed`、`executionContext: administrator`、
   `workerElevated: true`、`workerSession` 大于 0，且 `workerSid` 不为
   `S-1-5-18`，`sysprepExecuted`、`bcdReadOrModified`、`powerActionExecuted` 均为 false。
5. 将 `Background-check.txt` 发回确认，再进行正式封装。

如检查失败，请提供显示的 ProgramData 作业目录中的 `status.json`、
`bootstrap.log`、`worker.log`（若有）。不要手动双击 worker.exe 或修改作业文件。
不要发送整个作业目录；正式作业的应答 XML 可能含账户密码。

## 正式封装的后续验收

通过诊断后，从封装前快照开始：管理员运行 `JY Sysprep Modern.exe`，
确认 GUI 的测试模式生成正常，再以原配置测试正式 OOBE 和关机/重启。
正式封装会修改当前系统状态和多系统 BCD；此时不要注销或手动重启。
记录实际动作是否完成、下次启动是否进入 OOBE 并正常到达桌面。

本次包只提供现代环境，先验证 Windows 11。Vista 及旧候选包均保留；
未验证的新构建不能代替这些历史验收结果。

## 已知证据与方案纠正

候选 3：JY 记录止于 `sysprep_running`，随后 Sysprep 日志创建成功标记，
后续 BCD 核对及电源操作未记录。候选 4/R1：诊断任务在 Windows 任务计划
程序中一直为 Queued，没有 worker.log，不能确认排队的具体原因。

SYSTEM 封装方案已撤回，依据
[Microsoft Sysprep 限制说明](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/sysprep--system-preparation--overview?view=windows-11)。
独立进程的创建标志依据
[Microsoft 进程创建标志](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags)。

本包仅构建及文件校验；未在宿主机运行可执行文件、单元测试、封装或电源操作。
