# Alpha 0.5 单文件源码构建

发行基线是已通过用户回归的 Single Candidate 3，SHA256 见验收元数据。
上传准备只原样复制该程序，不重新构建。以下步骤仅供开发者在独立构建环境使用。

## 源码与环境

在 PyCharm 打开源码目录 repository/，工作目录设为这一层。
single_main.py 是统一入口，admin_worker_main.py 是无控制台辅助入口。
构建使用 Python 3.6.8 x64、PyInstaller 3.6 和 dataclasses 0.8，依赖锁定在
requirements-build-vista.txt / requirements-vista.txt。
requirements-build.txt 和 modern_main.py 属于保留的旧 Python 3.7 构建路径，不是本次单文件发行入口。

构建依赖不放入 Git：

- .runtime-vista/Python36/：官方 Python 3.6.8 x64 完整运行目录，包括 Tcl/Tk 8.6.6。
- .venv36-vista/：基于上述 Python 建立的独立 venv，安装 requirements-build-vista.txt。
- build/vista-runtime/x64/：Windows SDK 10.0.14393.795 的 41 个 x64 可再发行 DLL 和 runtime-manifest.json。

可从官方 Python 3.6.8 x64 安装程序准备隔离运行目录，在独立开发 VM 中安装或提取，
不要把虚拟环境、安装程序或 DLL 提交到源码库。
tools/prepare_vista_runtime.py 从微软 SDK 下载并校验固定载荷，使用 7-Zip 提取所需运行库；
它需要构建机已安装 7-Zip，且使用 Python 3.6 的 msilib。脚本不会安装 SDK。
tools/prepare_vista_tk.py 用于已有隔离 Python 目录的 Tcl/Tk 组件提取，
需要 build/vista-downloads/python-3.6.8-amd64.exe（官方安装包，脚本校验 SHA256）。
若隔离目录已经包含官方 Tcl/Tk 组件，无需重复运行该提取步骤。

工具验证运行库的来源、版本、架构及 SHA256。预期运行库清单另保存在
docs/build-inputs/runtime-manifest.json，便于与本地生成清单比较。
第三方许可放在 licenses/third-party/；此目录不表示项目源码已另行声明某种开源许可证。

## 构建顺序

仅在构建环境中执行，所有命令从 repository/ 运行。以下命令不启动生成程序。

```powershell
& .\.runtime-vista\Python36\python.exe -m venv .venv36-vista
& .\.venv36-vista\Scripts\python.exe -m pip install -r requirements-build-vista.txt
& .\.venv36-vista\Scripts\python.exe -B tools/prepare_vista_runtime.py
& .\.venv36-vista\Scripts\python.exe -B -m PyInstaller --noconfirm --distpath build/alpha05-single-c3/worker --workpath build/alpha05-single-c3/worker-work "JY Sysprep Alpha 0.5 Single Worker.spec"
& .\.venv36-vista\Scripts\python.exe -B -m PyInstaller --noconfirm --distpath build/alpha05-single-c3/main --workpath build/alpha05-single-c3/main-work "JY Sysprep Alpha 0.5 Single.spec"
& .\.venv36-vista\Scripts\python.exe -B tools/verify_single_exe_static.py
```

静态校验脚本只读取源码、PE 和内置归档，不运行 EXE。若根目录已有同名交付文件，
脚本会拒绝覆盖，请在新的构建工作目录操作，不要删除或覆盖已验收发行程序。
校验脚本生成构建记录不代表新构建已通过虚拟机回归。

## 验证边界

完整测试套件和正式封装仅在可恢复快照的隔离 VM 中执行，详见 ../TESTING.md。
源码运行与冻结 EXE 在 DLL 搜索路径、子进程和临时目录上存在差别，源码测试不能替代成品验收。
不要添加自动执行封装或重启的构建后步骤。
