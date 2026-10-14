# Python 3.7 兼容性记录

日期：2026-10-14。

## 环境

- CPython 3.7.9，Windows x64。
- 独立虚拟环境 `.venv37`；环境文件不随源码分发。
- 运行模块使用 Python 标准库，无第三方运行依赖。
- 构建依赖：PyInstaller 5.13.2，记录于 `requirements-build.txt`。

## 已通过检查

九项自动检查全部通过：

1. 全部 Python 源码及三个原始 spec 的 Python 3.7 编译检查；上传目录仅保留 Alpha 0.3 spec。
2. 测试模式适配器不调用 Sysprep。
3. x86/amd64 XML 生成、中文及特殊字符处理、UTF-8 临时文件读写。
4. 默认最终确认取消。
5. 最终摘要反映最新配置。
6. 摘要不包含账户密码。
7. 入口调用文本向导与适配器流程。
8. 配置取消、Ctrl+C、EOF 不进入生成与封装流程。
9. 入口无 GUI/Tkinter 导入。

```powershell
.\.venv37\Scripts\python.exe -B -m unittest discover -s tests -v
```

## 构建结果

Python 3.7.9 x64 与 PyInstaller 5.13.2 已成功生成单文件 exe。包内检查确认包含 `python37.dll`、TUI 向导及 XML 生成模块，未包含 GUI/Tkinter。`pip check` 通过。

原构建 exe 为 6,487,870 字节，SHA-256 见 [构建记录](ALPHA-0.3-BUILD.json)。exe 单独作为 Release 附件提供。

## 边界

源码语法、TUI 逻辑与 XML 处理通过检查；尚未启动 exe 或执行真实 Sysprep。GUI 窗口、PyCharm 调试器与各 Windows 版本部署兼容性未纳入这些检查。
