# Alpha 0.4 统一发行候选包 1

2026-10-15。根目录交付 `JY Sysprep Alpha 0.4 Unified Candidate 1 x64.zip`，约 18 MiB。

## 运行

完整解压 ZIP，以管理员身份运行 `Start.cmd`。默认进入 GUI；启动提示期间或 GUI 中按 F8 可进入 TUI。`Start GUI.cmd`、`Start TUI.cmd` 可直接指定界面。关闭 GUI 后，启动器随子程序退出；从已有终端调用时返回原终端。

入口在加载 Python 前读取 Windows 版本和处理器环境：NT 6.0 选择 Vista，NT 6.1/6.2/6.3/10.0 选择现代环境。不满足 AMD64 条件、未知系统版本或缺失运行文件会停止；Vista SP2、审核模式、管理员和单系统限制仍由原程序检查。该分流不能识别所有受支持产品，系统适配及预检仍由程序负责。

`Start.cmd --route-only` 只输出 `vista` 或 `modern`，不启动程序、不执行 Sysprep、不读写 BCD。版本分流依据系统返回的版本号；第三方兼容模式或人为修改的环境不在本次检查范围内。

目录结构：

```text
Start.cmd
Start GUI.cmd
Start TUI.cmd
README.txt
SHA256SUMS.txt
runtimes/
  vista/       已验收的 Python 3.6.8 GUI experimental 3 便携包原文件
  modern/      当前共享源码构建的 Python 3.7.9 单文件程序
```

目标机无需安装 Python。完整保留两个目录，不将 DLL 混放到根目录。Vista 子目录中的旧说明与校验表作为原包记录保留，统一包以根目录 README 和 SHA256SUMS 为准。

## 验证状态

2026-10-15，用户反馈“我测试了它们的gui，都没问题”。按前述测试范围记录为 Vista、Windows 7、8、8.1、10、11 的 GUI 运行通过；未额外推定各系统 F8/TUI、测试 XML 或正式封装已通过。具体 Build、补丁及硬件配置尚未逐项记录。

随后用户反馈“7的没问题”“vista通过”及“8 8.1 10测试完成”，按上一轮正式封装测试步骤记录 Vista、Windows 7、8、8.1、10 的统一候选包正式流程通过：OOBE、通用化、关机、不创建账户，并完成首次设置进入桌面。本轮具体系统 Build 未单独提供。统一包的 Windows 11 正式流程仍待反馈；Vista 原独立包的成功记录单独保留。

- 统一 ZIP 全文件校验通过；Vista 每个文件与已验收的原 ZIP 字节一致。
- 开发机实际分流到 modern；隔离 PATH、清除 Python/Tcl/Tk 环境变量后，经中文及空格路径启动 `--help` 成功。
- 9 个分流分支检查通过，包括 Vista、7、8、8.1、10、11、32 位控制台运行于 AMD64 系统、拒绝 x86 和 ARM64/未知版本。这里模拟了版本输出，仅证明入口逻辑。
- 运行文件缺失时停止，未回退到另一个环境。
- 统一包中 Vista 程序的只读 GUI 自检在开发机通过。
- 共享源码在 Python 3.6 和 Python 3.7 中各通过 62 项回归检查；主版本程序从当前源码新建，旧根目录 exe 和 Vista ZIP 均保留。

Vista 原包已有用户反馈的一次 SP2 x64 单系统 GUI 正式封装成功；统一包的上述六个系统 GUI 已获用户反馈通过，正式部署仍未完成跨版本验收。目标范围为 Vista SP2 至 Windows 11 的 x64 客户端，尚不承诺整个范围的封装兼容，不包含 Server/x86/ARM64 验收。

## 虚拟机验收顺序

先在 Vista SP2 x64 检查统一入口：运行 `Start.cmd --route-only` 应为 `vista`；再检查默认 GUI、F8 保留配置、测试模式 XML、退出，随后从封装前快照完成正式 OOBE、通用化、关机和首次设置。

然后在 Windows 7、8、8.1、10、11 的 x64 单系统快照逐一重复，分流结果应为 `modern`。记录系统 Build、补丁状态、虚拟硬件、选择项及首次设置结果。每次正式测试前恢复快照；先沿用不创建账户的配置。账户及多系统组合单独验收。

## 重建

以下构建脚本现已推进到[候选包 2](UNIFIED-CANDIDATE-2.md)；本页及 UNIFIED-BUILD.json 保留候选包 1 的历史交付与验收，不会被新构建覆盖。

先按 [Vista GUI 说明](VISTA-GUI.md) 准备原包，确认其哈希符合验收记录。

```powershell
.\.venv37\Scripts\python.exe -m PyInstaller --noconfirm --distpath dist --workpath build/unified-modern "JY Sysprep Alpha 0.4 Modern.spec"
.\.venv37\Scripts\python.exe -B tools/package_unified.py
.\.venv37\Scripts\python.exe -B tools/check_unified.py
```

最后一条检查只执行入口、帮助、诊断，不执行实际封装。构建与校验结果见 [UNIFIED-BUILD.json](UNIFIED-BUILD.json)。
