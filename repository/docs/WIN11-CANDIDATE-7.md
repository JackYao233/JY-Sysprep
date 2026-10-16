# Windows 11 修复候选 7

## 用户验收结果

2026-10-16（Europe/London 对话日期），用户确认候选 7 在恢复无 VMware Tools
封装前快照后的 Windows 11 多系统虚拟机中，后台诊断通过，正式封装自动重启，
随后完成 OOBE 并进入桌面。本次为用户反馈的一次完整流程通过。

后台诊断截图显示管理员会话 1、workerElevated=true、processInJob=false、
hasConsole=false。对比候选 6 的中断，无控制台辅助程序及系统工具的无窗口启动
与本次结果改善一致，支持终端生命周期相关的判断，但没有直接捕获终止调用，
不能证明 Windows Terminal 被卸载或将其认定为唯一根因。

尚未取得本次成功作业的逐阶段日志及 BCD 核对输出；此结论不扩展到其他系统、
关机动作或其他配置的回归验收。下方“待验证”内容保留为构建时设计与步骤。

候选 6 的正式测试未完成。新增原始事件未找到 JY 崩溃、Defender 拦截或代码完整性
拦截的直接证据。原先 Application/AppX 2562 的正文实际涉及 WidgetsPlatformRuntime
目录删除，不是 JY 的进程退出记录。

AppModel 原始事件中，Windows Terminal 容器在虚拟机时间 04:48:13.972 出现事件 217，
随后 04:48:14.376 出现该应用容器事件 41；Sysprep 在 04:48:26 完成。
这些事件提供终端生命周期线索，但没有直接指出终止 JY 的进程或调用。

本版进行针对性的无控制台隔离，不能称为已确认修复。

## 修改

- 新增 JY Sysprep Worker.exe，以 PyInstaller console=False 单独构建。
  主程序仍保留 GUI/F8/TUI；后台辅助程序不初始化 GUI 或控制台向导。
- 从同目录的辅助程序复制受保护的执行文件，不再复制主控制台 EXE。
- 后台核对 hasConsole=false、processInJob=false、管理员用户和非零会话；
  不满足时在封装前停止。
- 后台调用 whoami、BCD 工具、Sysprep 等系统程序时使用 CREATE_NO_WINDOW，
  防止子工具再分配新控制台。Sysprep 仍使用 /quiet /quit。
- 继续保留本次成功标记、BCD 备份与核对、失败日志及电源动作约束。

依据：[PyInstaller 控制台行为](https://pyinstaller.org/en/v5.13.2/feature-notes.html)、
[Microsoft 进程创建标志](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags)。

## 验证

1. 本次事件诊断包已保留后，恢复无 Tools 的封装前快照。
2. 完整解压本包到新目录，保留主程序与 JY Sysprep Worker.exe 在同一目录。
   辅助程序不能单独双击启动。
3. 以管理员身份运行 Check background.cmd，先提供结果。
   应为 stage=completed、hasConsole=false、processInJob=false、workerElevated=true、
   workerSession 大于 0，三个封装/BCD/电源动作标记均为 false。
4. 诊断通过后再验证正式封装；如果仍中断，保留现场，使用包内的 Collect.cmd
   采集，不要重复封装。该采集只读系统并在桌面生成新的报告目录及 ZIP。

需要提供作业目录文件时，选择 status.json、worker.log、bootstrap.log、launch.json。
不公开可能含密码的 unattend.xml。windowless 程序 bootstrap.log 可能为空，
应结合 worker.log 和状态记录分析。

本包自带运行环境，无需在虚拟机安装 Python 或 VMware Tools。
宿主机只进行构建与文件校验，未运行程序、单元测试、封装或电源操作。
