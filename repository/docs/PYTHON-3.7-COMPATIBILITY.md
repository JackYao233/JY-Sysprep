# Python 3.7 环境迁移与兼容性

日期：2026-10-14。

## 当前环境

- 基础解释器：`C:\Program Files\Python37\python.exe`。
- 版本：CPython 3.7.9，64 位。
- 项目环境：`G:\JY Sysprep\.venv37\Scripts\python.exe`。
- pip：20.1.1（Python 3.7 安装自带版本）；运行项目无需额外安装依赖。
- `.python-version`：3.7.9。该文件记录版本意图，不会自动改变系统默认 `python`。
- 新增 PyCharm 运行配置：`Alpha 0.3 TUI (Python 3.7)`，显式使用 `.venv37`。
- 已登记 PyCharm Python 3.7 SDK，并修改项目、模块及原 `main` 运行配置的解释器设置。登记前的用户 SDK 配置备份在 `.idea/jdk.table.before-python37.xml`，现有 SDK 保留。
- 旧环境保留；未修改系统 Python 的默认选择。

## 检查范围

结果：**9 项检查全部通过，全部源码及 spec 编译通过**。无需为 Python 3.7 修改业务代码。

使用真实 Python 3.7 执行检查，而非仅在较新 Python 上解析语法。

- 原六项 TUI 检查：默认取消、最新配置摘要、密码不进入摘要、入口调用文本向导与适配器、中断取消、入口无 GUI 导入。
- 对 `main.py`、全部源码目录、测试与三个 spec 逐文件编译，不写入字节码缓存。
- x86/amd64 XML 生成与解析：计算机名、中文所有者、特殊字符、账户及自动登录次数。
- UTF-8 应答文件写入与读取：仅使用临时目录。
- 测试模式适配器跳过 Sysprep：执行器使用模拟对象。

项目采用的 `dataclasses`、`typing.Optional`、ElementTree、pathlib、unittest.mock 均可在本次 Python 3.7 运行中使用；未发现需要修改的 Python 3.8+ 语法或当前执行路径 API。

```powershell
.\.venv37\Scripts\python.exe -B -m unittest discover -s tests -v
```

沙箱内首次运行受到 Python 3.7 的 Windows 路径解析访问限制；经允许在沙箱外运行原测试后通过。这属于本次执行环境限制，未据此更改项目路径逻辑。

## PyCharm

运行使用 `Alpha 0.3 TUI (Python 3.7)` 配置。若已打开的 PyCharm 未刷新磁盘上的解释器设置，重新打开项目，并确认状态栏解释器路径为 `.venv37/Scripts/python.exe`。

## 构建边界

`requirements-build.txt` 固定 `PyInstaller==5.13.2`；其 [发布元数据](https://pypi.org/project/pyinstaller/5.13.2/) 明确声明 Python 3.7 支持。现有 spec 的 Python 3.7 语法已纳入编译检查。

后续已安装 PyInstaller 5.13.2，在 `.venv37` 中成功打包为根目录 `JY Sysprep Alpha 0.3.exe`。归档检查确认包含 `python37.dll`、TUI 向导与 XML 生成器，排除 GUI/Tkinter；`pip check` 通过。exe 大小为 6,487,870 字节，SHA-256 见 [构建记录](ALPHA-0.3-BUILD.json)。尚未启动 exe，不声称已验证实际运行与部署。

## 结论边界

这些检查验证 Python 3.7 的源码语法、TUI 逻辑和 XML 处理兼容性；没有执行真实 Sysprep，也没有验证 Windows 版本部署兼容性、GUI 窗口或 PyCharm 调试器。
