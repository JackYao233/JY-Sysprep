# Vista SP2 x64 实验构建

当前阶段：开发机检查通过；**用户已反馈 Vista SP2 x64 单系统虚拟机中便携启动、TUI 测试应答生成及一次正式封装/OOBE 进入桌面成功**。这是特定配置的一次通过记录，不代表所有 Vista 配置均已验证。确认日期：2026-10-15。

本页记录的是已测试的 TUI experimental 2。后续新增的 [GUI experimental 3](VISTA-GUI.md) 默认 GUI 并保留 F8/TUI，单独打包且验收状态独立；源码 `vista_main.py` 现已扩展为双模式入口。

## 已确认的测试结果

- 用户提供的自检结果显示 Windows 6.0.6002 SP2、64 位，Python 3.6.8；Python、UCRT、VCRUNTIME 均从便携目录加载。未独立核查目标机是否原已安装 UCRT 更新。
- 用户反馈 TUI 测试应答文件生成正常；文件 XML 结构、命名空间、架构和配置内容已核对，未执行 Windows SIM 目录验证。
- 初期被认为卡住的流程中，设备重新安装用时约十分钟。用户随后确认原生 `/generalize /oobe /shutdown` 在等待十多分钟后继续重启、进入 OOBE 并成功进入桌面。
- 用户按同一封装前快照、OOBE、关机、不创建账户的步骤复测 JY 便携版，反馈“这次没问题”。据此记录该配置一次通过；账户创建、自动登录、Audit、多系统等不包含在本次通过范围内。
- 最初“原生正常”的测试未勾选 Generalize，因此早期据此优先怀疑应答文件的推断不成立。安装日志最后记录 MSDTC 调用不等于证明 MSDTC 故障；没有证据要求删除 ComputerName 或修改 MSDTC。

后续观察应结合日志增长、CPU/磁盘活动和完整重启结果，不能只凭配置画面停留十多分钟判定卡死。当前 ZIP 未因本次文档更新而重构建，原校验值仍适用。

## 范围

- Windows Vista SP2 x64 客户端，单系统安装。
- 默认进入 TUI；此构建不包含 GUI/Tkinter。
- 默认测试模式，仅生成应答文件。正式封装需要管理员权限和审核模式。
- Vista x86、RTM/SP1、多系统和 Windows Server 2008 不在本次验收范围内。
- 正式执行仍会识别并备份 BCD。检测到多系统时停止，不执行 Sysprep、引导修复或电源动作。
- 当前预检、审核模式判定和单系统 BCD 流程已被这次用户反馈的正式测试覆盖；其他配置仍需独立验证，不能因一次通过就宣称完整支持。

## 交付文件与前置条件

当前交付为根目录的 **`JY Sysprep Alpha 0.4 Vista Portable x64.zip`**（experimental 2），完整解压后运行文件夹中的 `JY Sysprep Vista.exe`。不要单独复制 exe 或删除旁边的 DLL。

便携包包含 Python 3.6.8 x64、dataclasses 0.8、VC 2015 的 VCRUNTIME140.dll，以及微软 SDK 10.0.14393.795 中的 **41 个 x64 UCRT/API-set 可再发行 DLL**，全部与 exe 放在同一目录。目标是无需在 Vista 中安装 Python、VC 运行库或 UCRT 补丁；在未安装 UCRT 更新的 Vista SP2 上是否可用仍待验收。

运行库直接从微软原版 SDK 组件中提取，没有安装 SDK，也没有从开发机系统目录或其他软件目录复制 DLL。下载组件核对固定哈希，提取时核对架构和文件版本，打包前再次核对每个 DLL 的哈希。来源及文件清单随包保存为 `runtime-manifest.json`，许可在 `licenses/`。

优先在**尚未安装 UCRT 更新**的干净 Vista SP2 x64 快照测试本包。若启动仍提示缺少 DLL 或入口点，先检查是否完整解压，并记录完整报错，不要通过安装补丁掩盖本次免安装验证的结果。

之前的 `JY Sysprep Alpha 0.4 Vista Experimental x64.exe` 是 experimental 1 单文件构建，仍要求目标系统已有 UCRT。此次免安装测试请使用新的 ZIP。

此包在现代 Windows 开发机上构建，静态依赖检查与开发机启动检查不能替代 Vista 验证。

## 虚拟机测试顺序

1. 使用 Vista SP2 x64 单系统虚拟机，记录版本、架构、补丁及 VMware 版本，创建测试快照。
2. 将整个 ZIP 复制到虚拟机并完整解压，双击 `Check runtime.cmd`；或者在解压目录的命令提示符中执行：

   ```bat
   "JY Sysprep Vista.exe" --self-test > Vista-self-test.txt 2>&1
   ```

   自检只检查运行库及内存中的 XML；不创建应答文件、不读取或修改 BCD、不执行 Sysprep。命令提示符将输出保存为 txt。`xmlCheckPassed: true` 仅表示内部 XML 检查通过。`loadedLibraries` 显示实际加载的 DLL 路径；未安装 UCRT 的 Vista 中，重点核对 `ucrtbase.dll` 是否来自解压目录。Windows 10/11 固定优先使用系统 UCRT，开发机上的结果不能代替此项 Vista 验证。

3. 进入审核模式，以管理员身份运行 exe，保持测试模式，完成 TUI 五步配置。检查中文、密码隐藏输入、默认取消和 Ctrl+C 取消。
4. 检查桌面测试应答文件，使用适用于 Vista 的 Windows AIK/Windows SIM 和目标安装镜像目录验证组件及设置；不要用 Windows 11 的设置目录代替 Vista 的目录。
5. 首次正式测试选择 OOBE、不创建账户、完成后关机。重新启动后确认 OOBE 能正常完成并进入桌面。
6. 从快照分别测试 Audit、账户创建、自动登录、语言区域及关机/重启/退出选项。不要在同一已封装系统中反复叠加测试。
7. 若失败，收集 `Vista-self-test.txt`、控制台报错、桌面的 `JY Sysprep Logs`、目标系统的 Sysprep/Panther、Panther、Panther/UnattendGC 日志，并记录失败发生在启动、预检、封装还是重启阶段。

本阶段未开放多系统封装。确认单系统流程通过后，再单独设计多系统验收。

## 开发环境

- `.runtime-vista/Python36/`：项目内独立安装的官方 Python 3.6.8 x64，不加入 PATH、不安装启动器及快捷方式。
- `.venv36-vista/`：Vista 专用环境。
- `.venv37/`：现有主开发环境，保持原版本和依赖。
- `vista_main.py`：实验版入口；`main.py` 仍是主版本入口。
- `sysprep/client/vista.py`：专用适配器及 SP2/x64 限制。
- `requirements-vista.txt`：Python 3.6 的运行兼容包。
- `requirements-build-vista.txt`：独立打包工具版本。
- `JY Sysprep Alpha 0.4 Vista.spec`：独立构建配置。
- `JY Sysprep Alpha 0.4 Vista Portable.spec`：携带本地运行库的文件夹构建配置。
- `tools/prepare_vista_runtime.py`：下载、核对并提取微软 SDK 可再发行 DLL，不运行安装程序。
- `tools/package_vista_portable.py`：核对二进制文件、加入许可及自检入口，创建 ZIP。
- `tools/check_vista_portable.py`：检查 ZIP 文件校验值及解压后的只读启动。

PyCharm 可选择 `.venv36-vista/Scripts/python.exe`，入口设为 `vista_main.py`、参数 `--self-test`、工作目录设为项目根目录。普通开发机上不启动 Vista 封装向导。

复现依赖与构建：

```powershell
.\.runtime-vista\Python36\python.exe -m venv .venv36-vista
.\.venv36-vista\Scripts\python.exe -m pip install pip==21.3.1 setuptools==59.6.0 wheel==0.37.1
.\.venv36-vista\Scripts\python.exe -m pip install -r requirements-build-vista.txt
.\.venv36-vista\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv36-vista\Scripts\python.exe -B tools/prepare_vista_runtime.py
.\.venv36-vista\Scripts\python.exe -m PyInstaller --noconfirm --distpath dist --workpath build/vista-portable "JY Sysprep Alpha 0.4 Vista Portable.spec"
.\.venv36-vista\Scripts\python.exe -B tools/package_vista_portable.py
.\.venv36-vista\Scripts\python.exe -B tools/check_vista_portable.py
```

提取步骤需要开发机已安装 7-Zip（默认路径 `C:/Program Files/7-Zip/7z.exe`），Vista 测试机无需安装。SDK 组件来自微软 HTTPS 下载服务器，下载后核对固定 SHA-256。

构建会拒绝来自独立 Python 环境和已核对 SDK 清单以外的二进制文件。Python 3.6 环境没有安装 Tk，所以 GUI 测试跳过；GUI 回归在 Python 3.7 环境运行。新便携包记录见 `VISTA-PORTABLE-BUILD.json`；`VISTA-BUILD.json` 是之前 experimental 1 单文件构建的记录。

开发机结果：Python 3.6 检查通过 48 项、跳过 9 项 GUI 检查；Python 3.7 回归通过 57 项。已验证所有随包原生文件为 x64、UCRT 文件哈希及 API-set 导入依赖，并完成 ZIP 完整性、解压后 exe 帮助/自检及自检 CMD 的隔离 PATH 启动检查。真实 Vista 测试结果来自用户反馈，见上方记录；开发机上未执行 Sysprep。

## 参考资料

- [Python 3.6 的 Windows 支持范围](https://docs.python.org/zh-cn/3.6/using/windows.html)
- [官方 Python 3.6.8 下载](https://www.python.org/downloads/release/python-368/)
- [PyInstaller 3.6 平台要求](https://pyinstaller.org/en/v3.6/requirements.html)
- [Microsoft Universal C Runtime 更新说明](https://support.microsoft.com/help/2999226/update-for-universal-c-runtime-in-windows)

这些资料用于选择实验基线；兼容声明以虚拟机中的实际验收结果为准。
