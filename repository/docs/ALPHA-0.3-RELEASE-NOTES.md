# JY Sysprep Alpha 0.3 — 发布说明草稿

> 尚未发布。发布前应完成开发计划中的必需修复与验收，删除未通过验证的功能描述，并填写测试环境。建议继续作为预发布版本。

## 中文

Alpha 0.3 聚焦 TUI 文本配置向导。当前入口直接启动控制台向导，无需 Tkinter。

- 环境预检后进入基本设置、语言区域、OOBE、账户、确认五个步骤。
- 文本交互配置运行模式、完成动作、计算机名、时区、语言与区域。
- 根据系统能力启用相关 OOBE 配置项。
- 配置本地管理员账户及可选自动登录。
- 默认测试模式仅生成应答文件；正式模式执行 Sysprep。
- 确认前显示最新配置摘要，默认取消；配置过程中 Ctrl+C 或输入结束可取消。

模式、语言区域、OOBE、账户与 XML 生成属于已有功能；本版本重点是完善文本向导的步骤、摘要与取消体验。GUI 开发暂缓。

当前限制：

- 当前启动入口要求审核模式并通过预检，测试模式也适用。
- 正式封装需要管理员权限。
- 账户应答文件包含明文密码。
- 旧 Windows 与 Server 映射不代表已通过部署验证。
- 应答文件验证与终端实测仍列为发布前待办；exe 已构建并检查包内模块，本草稿不能作为已完成公告。

## English

Alpha 0.3 focuses on a console text wizard. The entry point starts the TUI directly without Tkinter; GUI development is deferred.

- Environment checks followed by five configuration steps: basic settings, locale, OOBE, accounts, and confirmation.
- Text prompts for existing mode, completion action, computer name, time zone, locale, OOBE, and account settings.
- Test mode enabled by default to generate an answer file without executing Sysprep.
- A current configuration summary before confirmation; confirmation defaults to cancel. Ctrl+C or EOF during configuration cancels the workflow.

This is an unpublished release draft. An executable has been built and its archive contents checked; terminal interaction, answer-file validation, and deployment checks remain release prerequisites. Existing Windows-family mappings do not establish tested compatibility.

## 发布前填写 / Complete before publishing

- 源码提交 / Source commit：待填写
- Python 与 PyInstaller 版本 / Build versions：Python 3.7.9 x64、PyInstaller 5.13.2；根目录 exe 已生成，包内模块检查通过
- 已验证 Windows 版本、Build、架构 / Tested systems：待填写
- TUI 验收结果 / Wizard validation：Python 3.7 下九项逻辑与兼容性检查通过；真实终端交互待验证
- Audit/OOBE 部署结果 / Deployment validation：待填写
- exe SHA-256：见 [构建记录](ALPHA-0.3-BUILD.json)

建议 Tag：`Alpha_0.3`，与现有 `Alpha_0.2` 风格一致；当前尚未创建。
