# Windows 11 封装后启动故障调查

记录日期：2026-10-14。以下客体时间保留日志原值；客体日志与 VMware 日志存在约 8 小时时差。

## 已确认事实

- 用户报告：Windows 7、8、8.1、10 测试正常，Windows 11（用户报告为 25H2）选择 OOBE、不创建账户，封装重启后异常。
- VMware 日志：Workstation 17.6.4、i9-13980HX、4 vCPU、16 GB、EFI、硬件版本 21。
- 宿主机日志为 `VBS is set to 0`、`Monitor Mode: CPL0`；没有证据支持宿主机 VBS 冲突判断。
- 最近日志显示交给 Windows Boot Manager 后约 0.7 秒发生 Triple fault；前两份轮转日志没有 Triple fault，随后两份共记录三次。
- 客体 Sysprep 使用 GENERALIZE、OOBE、REBOOT、UNATTEND，读取系统 Sysprep 目录中的应答文件。
- 客体日志在 2026-10-15 04:35:39 记录以下错误：

```text
SYSPRP BCD: BiUpdateEfiEntry failed c000000d
SYSPRP BCD: BiExportBcdObjects failed c000000d
SYSPRP BCD: BiExportStoreAlterationsToEfi failed c000000d
SYSPRP BCD: Failed to export alterations to firmware. Status: c000000d
```

- 同一过程随后仍报告 BCD generalize 成功，04:35:41 写入 `Sysprep_succeeded.tag`，并请求重启。因此成功标记不能代表启动配置完全正常。
- 时间换算后约为 VMware 日志中的 20:35:39—20:35:41；20:35:50 发生客体请求的重启，20:35:55 首次记录 Triple fault，时间相关。
- 第二份 setupact 的近期内容截至重启前的 CBS 服务退出，没有看到这次重启后进入 specialize/OOBE 的新执行记录。
- 旧的 `sysprep dialog box returned FALSE` 与八月份的 setup 错误不作为此次故障原因。

## 当前判断

### 后续 BCD 检查

用户提供的 `1.txt` 确认共享 EFI BCD 中有五个 Windows 启动项：WinPE 下 C:/D:/E:/F:/G: 分别对应 Windows 7/8/8.1/10/11，K: 为当前检查的 EFI 分区。

Windows 11 的 loader 标识符为 `{776ebad7-9075-11f1-82d8-fa35afdfd850}`，device 为 `locate=custom:12000002`，osdevice 为 `locate=custom:22000002`，而其他四个系统均指向明确分区。Windows 11 的 resume 条目也使用 locate，另有 `custom:21000026 partition=G:`。

locate 本身可以是 generalize 产生的定位方式，不单独证明 BCD 损坏。但在多个分区包含相同 Windows 路径的环境中，需要优先验证 Windows 11 引导是否定位到预期分区。建议先备份 K: 中的实际 BCD，仅将上述 Windows 11 loader 的 device/osdevice 指向核实后的 G:，保持其他启动项、恢复项与固件配置不变，然后测试启动。

修复命令仅供故障虚拟机的 WinPE 使用；每次重进 PE 需重新核实盘符，G: 不是对宿主机或其他环境的固定假设。此项修复尚未由用户验证，未据此认定最终根因。

封装期间 BCD/EFI 导出失败是本次最高优先级的故障线索。它与后续启动失败相关，但尚未取得实际 EFI BCD 内容，不能证明它单独导致 Triple fault。

Broadcom 官方在 Cloud Director 场景记录过同样的错误组合与 generalize 后 BCD 配置异常。该案例支持排查方向，不直接证明本次 Workstation 故障根因，也不照搬其中脚本。

日志中的 26100 组件版本不能单独用于判断用户最终安装的 Windows 功能版本；后续应读取实际系统版本或离线注册表验证。

## 下一步

1. 保留故障虚拟机副本与日志，避免覆盖证据。
2. 在故障虚拟机的 WinPE/恢复环境确认磁盘分区与 Windows 所在卷，记录 `diskpart` 的 `list volume` 输出。
3. 确定 EFI 系统分区后，读取其中 `EFI\Microsoft\Boot\BCD` 的全部条目。
4. 核实 Windows Boot Loader 的 device、osdevice、path、systemroot，以及是否存在多个 Windows 引导项；结合实际分区决定修复方式。
5. 修复后验证启动和 OOBE，再从封装前快照复测，确认是否需要在程序中加入专门的预检或封装后处理。

不要在宿主机直接执行修复用 bcdedit/bcdboot，不在未知分区布局下硬编码 C: 或 HarddiskVolume1，不删除/格式化分区。

## 程序侧的独立问题

- 应答文件根节点默认命名空间缺失需要单独修复和验证；当前日志没有证明它导致此次 Triple fault。
- 当前日志收集器缺少 `System32\Sysprep\Panther` 中的 generalize 日志，且没有完整保留 setuperr，诊断覆盖不足。
- 当前自动检查覆盖 Python、向导与 XML 读写，不能验证 Windows 接受全部配置或重启成功。

本次调查尚未修改程序、虚拟机、启动配置或发布副本。

## 参考

- [Broadcom：generalize 后 BCD 异常案例](https://knowledge.broadcom.com/external/article/424296/guest-customization-is-not-applied-on-wi.html)
- [Microsoft：UEFI BCD 系统存储设置](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/bcd-system-store-settings-for-uefi?view=windows-11)
