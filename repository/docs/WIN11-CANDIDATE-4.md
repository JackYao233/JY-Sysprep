# Windows 11 修复候选 4：虚拟机验证

> 已撤回正式封装测试：用户反馈 R1 的任务长期处于 Queued，后台日志未创建。
> 这尚不能证明排队的具体原因。进一步核对微软官方文档发现 SYSTEM 身份运行
> Sysprep 不受支持，因此停止此执行方案。候选 4/R1 不应继续正式封装。
> 源码已阻止创建正式 SYSTEM 作业；已交付的 EXE 不包含这一后续保护。
> 下方保留原测试设计作为历史记录，不再作为操作指引。
>
> 依据：https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/sysprep--system-preparation--overview?view=windows-11

## 修订版 1

用户截图确认原候选 4 的运行环境检查通过，但后台任务在 `/create` 阶段失败。
源码中错误地将 API 枚举 `ServiceAccount` 写入任务 XML 的 `LogonType`。
修订版移除不合法字段，保留 SYSTEM SID，并显示计划任务工具的完整错误输出。
构建完成后仍需在虚拟机重新运行 `Check background.cmd`，通过前不要正式封装。
此修订未在宿主机运行程序、测试或注册任务。

这是未完成运行验收的 Windows 11 x64 专用候选程序，不是已验证的正式版。
目标机无需安装 Python。此次仅构建，不在宿主机启动程序、运行测试或创建后台任务。

## 修改依据

候选 3 的诊断包显示：2026-10-16 04:50:25 启动 Sysprep 后，JY 的记录
停在 `sysprep_running`；04:51:20 Sysprep 日志已写入成功标记。
后续引导核对及电源操作没有记录。尚不能确定前台进程消失的具体原因。

本版尝试由独立 SYSTEM 后台任务接管 Windows 11 多系统正式封装。
它先重新检查环境及当前引导项，再以 `/quiet /quit` 执行 Sysprep，
检查本次成功标记，核对当前系统引导项，最后提交用户选择的电源动作。
后台任务注册失败时停止，不退回前台执行。任务没有定时、登录或开机触发器。

新增阶段记录包含时间、失败前阶段和备份位置。后台执行必须明确收到
封装成功及引导核对通过的结果，才可提交关机/重启。此方案仍需实测。

## 测试顺序（仅在隔离虚拟机内）

1. 保留可恢复的封装前快照。将压缩包完整解压到虚拟机的本地磁盘；
   不要从宿主机共享目录运行。关闭可写宿主机共享和宿主机磁盘直通。
2. 运行 `Check runtime.cmd`。它检查系统命令及 GUI，输出
   `Runtime-check.txt`，不执行封装、引导修改或电源操作。
3. 右键 `Check background.cmd`，选择“以管理员身份运行”。
   此项会实际创建并启动一次 SYSTEM 诊断任务，生成受保护的诊断目录，
   因此不是只读检查。它不执行 Sysprep、读取/修改 BCD 或执行电源操作。
   输出 `Background-check.txt` 应包含：`stage: completed`、
   `workerSid: S-1-5-18`、`workerSession: 0`、`sysprepExecuted: false`。
   若出现错误或没有完成记录，停止，不继续正式封装。
4. 两项检查通过后，从封装前快照准备正式测试；以管理员身份运行
   `JY Sysprep Modern.exe`，确认显示 candidate 4，先验证 GUI 和测试文件生成。
5. 在审核模式下选择正式封装、OOBE、原定的关机或重启动作，记录选项。
   正式模式会实际执行 Sysprep，并在多系统环境核对/修改当前系统引导项。
6. 若桌面窗口消失，观察虚拟机是否自动完成所选动作。不要仅凭窗口消失
   判定失败，也不要重复运行封装。若没有完成，保留现场和最新后台记录。

后台记录位置：`C:\ProgramData\JY-Sysprep-Job-*`（系统盘不是 C: 时相应变化）。
请提供最新目录中的 `status.json`、`worker.log`，以及嵌套的
`ExecutionRecords` 和 `BootBackups` 诊断记录。应答 XML 可能含账户密码，
不要直接公开整个后台目录。

## 范围与限制

- 本包只包含现代运行环境，先验证 Windows 11；不替换既有 Vista 包。
- 后台方案只接管 Windows 11 多系统正式封装。
- 单系统及其他 Windows 版本仍使用原执行路径；本次没有回归验证。
- 后台记录可供前端或下次启动读取；不能保证桌面会话消失后立即弹窗。
- 可执行文件构建完成不等于实际封装验证通过。

命令参数依据：[Microsoft Sysprep 命令行文档](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/sysprep-command-line-options?view=windows-11)。
