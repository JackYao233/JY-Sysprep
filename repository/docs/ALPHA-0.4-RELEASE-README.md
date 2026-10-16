# JY Sysprep Alpha 0.4 x64

完整解压后，以管理员身份运行 Start.cmd。无需安装 Python 或 VMware Tools。
默认 GUI，按 F8 可切换 TUI；Start GUI.cmd 和 Start TUI.cmd 可直接指定界面。

本包基于统一候选包 8，保留通过测试的程序文件，没有重新编译。
Vista SP2 x64 使用独立运行环境；Windows 7、8、8.1、10、11 x64 使用现代运行环境。
现代主程序及无控制台辅助程序必须保留在同一目录，不要单独移动 EXE。
主界面保留 candidate 7 标签，Vista 保留原实验版标签，属于复用二进制的原始标识。

2026-10-16 用户反馈跨版本虚拟机回归通过。Windows 11 已反馈自动重启、OOBE、
进入桌面成功，随后统一包的关机及 OOBE 通过。测试范围不覆盖所有补丁、系统版本
及账户选项组合。Vista 正式封装限单系统；x86、ARM64、Windows Server 不在验收范围。

请从封装前快照开始配置与测试；默认测试模式仅生成应答文件，正式模式需另行确认。
若正式封装中断，保留现场，运行 Diagnostics/Collect.cmd，提供桌面生成的诊断 ZIP。
不要重复封装。应答 XML 可能包含账户密码，不要公开整个后台作业目录。

Check modern runtime.cmd 检查现代系统运行环境；Check background.cmd 检查管理员
无控制台辅助进程。这两个诊断入口不执行 Sysprep、BCD 操作或电源动作。
Vista 使用自身目录内保留的诊断入口。

Extract the entire package and run Start.cmd as administrator. Python and VMware Tools
are not required. GUI is the default; press F8 to switch to the TUI.
See RELEASE-NOTES.en.md for the English release summary and validation scope.

SHA256SUMS.txt covers package files. SOURCE-BUILDS.json and RELEASE-PROVENANCE.json
identify the original tested archives. Packaging and file checks were performed on
the development host; deployment validation was reported by the user in VMs.
