# Alpha 0.4 build 2 多系统兼容说明

## 改进依据

用户在多个 Windows 共用 EFI 引导的虚拟机上复现封装后启动失败；Win11 固定正确引导分区后恢复，Win8 也出现类似问题，单系统对照正常。本版针对这种多系统原机启动场景加入保护，不将问题归类为某个 Windows 版本的普遍缺陷。

## 正式封装流程

1. 从 Windows API 获取正在运行的 Windows 目录，提取实际系统盘符。
2. 使用 `bcdedit /enum {current} /v` 识别当前完整引导 GUID，并核对系统目录和 winload 路径。
3. 读取 `osloader` 引导项；排除 ramdisk/WinPE 恢复环境，以多个系统加载器判断需启用兼容流程。
4. 导出整个系统 BCD，并保存当前引导项和加载器列表。备份必须实际生成且非空。
5. 单系统：维持原有 Sysprep `/shutdown`、`/reboot` 或 `/quit`。
6. 多系统：使用 Sysprep `/generalize /audit或oobe /quit`，先不关机或重启。
7. 确认成功返回且本次生成了新的 `Sysprep_succeeded.tag`。
8. 按封装前识别的 GUID 读取当前加载器，将 device/osdevice 固定到实际系统分区；已经正确时不重复设置。
9. 读回复查分区、系统目录和引导路径，核对加载器列表及其他条目未发生预期之外的变化。
10. 核对成功后执行用户原本选择的关机、重启或退出。

测试模式不会执行 BCD、Sysprep 或关机命令，只生成测试应答文件。

## 备份与故障反馈

每次正式封装前建立独立目录：

```text
%ProgramData%\JY Sysprep\BootBackups\before-sysprep-随机编号\
    BCD.backup
    plan.json
    current-before.txt
    loaders-before.txt
    current-after-sysprep.txt      多系统封装成功后
    loaders-after-sysprep.txt      多系统封装成功后
    loaders-verified.txt          修复复查成功后
```

BCD 导出不是完整虚拟机快照，也不等同于固件 NVRAM 备份。

识别或备份失败时不启动 Sysprep。多系统封装、成功标记或 BCD 核对失败时不提交自动关机/重启动作；错误中提供备份位置。不会自动导入整个 BCD 覆盖共享引导。

错误发生后收集桌面日志目录，分别保留：

```text
Sysprep\Panther\*.log
Panther\*.log
Panther\UnattendGC\*.log
```

其中包括 setupact 与 setuperr。账户应答文件不进入此诊断收集目录。

## 适用边界

- 不针对 Win11 单独判断，适用于能准确识别的标准分区安装与系统 BCD。
- 当前实现只固定当前系统加载器的 device/osdevice，不修改其他系统条目、启动顺序、恢复条目或内存诊断条目。
- 未支持的 VHD/ramdisk 等特殊引导、目标不一致或无法唯一识别的情况会停止，要求人工检查。
- 固定的是运行环境中的实际分区，不是 PE 中的固定盘符。映像迁移到其他磁盘后仍需按部署目标配置引导。
- 系统 BCD 的读取/备份/修复要求管理员权限。

## 验证与复测

Python 3.7 下 44 项自动检查通过。BCD、Sysprep 与 shutdown.exe 均使用模拟对象，没有在宿主机上执行真实引导修改或封装。

建议从此前出问题的虚拟机封装前快照开始，先复测 Win8，再复测 Win11：

1. 确认窗口或 TUI 显示 `Alpha 0.4 build 2` 或更新构建；当前版本为 build 3。
2. 选择正式封装、OOBE 与重启。
3. 核对控制台提示检测到多个系统引导项、备份路径、使用 `/quit` 完成 Sysprep、引导核对成功后再重启。
4. 验证进入 OOBE；之后验证其他系统启动项仍能启动。
5. 如未自动重启，保留错误和备份，不反复执行 Sysprep；提供 `plan.json`、前后引导文本及收集日志继续排查。

自动检查和 exe 帮助启动不等同于真实多系统封装验收。本版尚待上述虚拟机实测。

## 官方参考

- [Sysprep 参数：/quit 完成处理后不重启](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/sysprep-command-line-options?view=windows-11)
- [BCDEdit：系统存储、导出、完整 GUID 和设置](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/bcdedit)
- [UEFI BCD 中的 device/osdevice 设置](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/bcd-system-store-settings-for-uefi?view=windows-11)
