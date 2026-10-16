# Windows 11 修复候选 6

## 用户实测及完整诊断

后台诊断截图通过：管理员会话 1，processInJob=false、launcherInJob=false，未执行封装、BCD 或电源操作。
随后正式作业 68beb3653239485ca8d0a26495458d7b 的 launch.json 显示 launcherInJob=true，
breakawayRequested=true，实际 worker 的 processInJob=false，说明本次脱离已生效。
但 worker 记录再次停于 sysprep_running，未记录后续阶段。

诊断包 JY-Win11-Diagnostics-20261016-044836-f8e4da.zip 显示：
虚拟机 04:48:26 Sysprep 创建本次成功标记；04:48:37 已无目标进程，
BCD 仍为 locate=custom，bootstrap.log 为空。正式流程未完成。
不能将这次中断归因于“没有脱离父进程 Job Object”；其他终止原因尚未查明。
同期 AppX 事件 2562 的格式化 Message 为空，继续采集原始事件 XML，避免根据事件编号猜测原因。

下方保留构建时的设计与步骤，新的封装验证应等待退出证据明确后再进行。

目标机无需安装 Python 或 VMware Tools。本包是待验证候选，尚未确认解决 Win11 问题。

## 候选 5 的诊断结论

用户提供的 JY-Win11-Diagnostics-20261016-063951-e36a39.zip 显示：

- 虚拟机时间 06:34:57，管理员子进程记录启动 Sysprep，完成动作保存为 reboot。
- 06:36:02，Sysprep 创建本次成功标记，系统状态为 GENERALIZE_RESEAL_TO_OOBE。
- 06:39:52，采集到的相关进程列表为空，未发现 worker.exe、JY 或 sysprep.exe。
- JY 记录仍止于 sysprep_running，没有返回记录，bootstrap.log 为空。
- 当前 BCD 的 device/osdevice 仍为 locate=custom，未完成 JY 的后续分区固定。

因此这是 Sysprep 已报告成功、JY 后续处理未完成的现场，不能继续等待或重复封装。
采集时进程不存在不等于已证明进程在何时、被谁终止。

## 本次源码修正与假设

候选 5 使用 DETACHED_PROCESS 和新进程组，但这并不等于脱离 Job Object。
Windows 默认可以让子进程继承父进程的 Job Object，而后者允许统一结束进程。
这是独立进程实现中需要补足的边界，尚未证实是本次异常的根因。

候选 6 启动执行进程时明确请求 CREATE_BREAKAWAY_FROM_JOB，记录启动方和
实际执行进程是否属于 Job Object。如果不允许脱离，启动失败后停止；如果
实际执行进程仍属于 Job Object，在调用 Sysprep 前停止，不使用原路径重试。
它仍以当前已提升的管理员身份运行，不创建 SYSTEM 任务，不使用服务账户。

依据：[Microsoft Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)、
[进程创建标志](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags)。

## 下一次虚拟机验证

1. 当前诊断包已保留后，恢复无 Tools 的封装前快照，不在已 generalize 的现场重跑。
2. 解压本包到新目录。以管理员身份运行 Check background.cmd，提供 Background-check.txt。
3. 应包含 stage=completed、executionContext=administrator、workerElevated=true、
   processInJob=false、workerSession 大于 0；封装、BCD、电源操作标记均为 false。
4. 如果启动被拒绝或 processInJob 仍为 true，请保留报告，不执行正式封装。
5. 诊断通过后再确认正式封装测试。即使检查通过，也不证明原始进程消失问题已修复。

失败时提供显示的作业目录中的 status.json、worker.log、bootstrap.log 和 launch.json。
不要提供可能包含账户密码的 unattend.xml。不要手动运行 worker.exe。

本包仅在宿主机构建并校验文件，未运行 EXE、测试套件、封装、引导修改或电源操作。
