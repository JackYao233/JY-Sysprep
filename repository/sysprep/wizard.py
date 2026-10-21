import getpass
import re
from copy import deepcopy
from core.version import DISPLAY_VERSION as VERSION

from sysprep.config import SysprepConfig


def _choose(prompt, choices, default):
    while True:
        value = input(f"{prompt} ({'/'.join(choices)}) [{default}]: ").strip().lower()
        if not value:
            return default
        if value in choices:
            return value
        print("请输入列出的选项。")


def _yes_no(prompt, default=False):
    return _choose(prompt, ("y", "n"), "y" if default else "n") == "y"


def _text(prompt, default=""):
    value = input(f"{prompt}" + (f" [{default}]" if default else "") + ": ").strip()
    return value or default


def _computer_name(value):
    if value == "*":
        return value
    if not re.fullmatch(r"[A-Za-z0-9-]{1,15}", value) or value.isdigit():
        raise ValueError("计算机名必须为 1–15 个字节，只能包含字母、数字和连字符，且不能全为数字。")
    return value


def _locale_preset(config):
    values = (config.input_locale, config.system_locale, config.ui_language, config.user_locale)
    default = "zh" if values == ("zh-CN",) * 4 else "en" if values == ("en-US",) * 4 else "custom"
    choice = _choose("语言和区域", ("zh", "en", "custom"), default)
    if choice == "zh":
        return "zh-CN", "zh-CN", "zh-CN", "zh-CN"
    if choice == "en":
        return "en-US", "en-US", "en-US", "en-US"
    return _text("输入法区域", config.input_locale), _text("系统区域", config.system_locale), _text("显示语言", config.ui_language), _text("用户区域", config.user_locale)


def collect_configuration(context, config=None):
    title = getattr(context, "interface_title", "JY Sysprep {}".format(VERSION))
    print("\n===== {} 文本配置向导 =====".format(title))
    print(f"检测到系统：{context.family}")
    print("回车使用默认值；Ctrl+C 取消配置。")
    config = deepcopy(config) if config is not None else SysprepConfig()
    print("\n--- 1/5 基本设置 ---")
    config.test_only = _yes_no("测试模式？仅生成应答文件，不执行 Sysprep", config.test_only)
    config.mode = _choose("封装后的启动模式", ("audit", "oobe"), config.mode)
    config.completion_action = _choose("Sysprep 完成后的动作", ("shutdown", "reboot", "quit"), config.completion_action)
    while True:
        try:
            config.computer_name = _computer_name(_text("计算机名（* 表示自动生成）", config.computer_name))
            break
        except ValueError as error:
            print(error)
    config.time_zone = _text("时区", config.time_zone)
    print("\n--- 2/5 语言和区域 ---")
    config.input_locale, config.system_locale, config.ui_language, config.user_locale = _locale_preset(config)
    print("\n--- 3/5 OOBE 选项 ---")
    config.hide_eula = _yes_no("隐藏许可条款页面？", config.hide_eula)
    if context.supports_wireless_oobe:
        config.hide_wireless = _yes_no("隐藏无线网络设置页面？", config.hide_wireless)
    if context.supports_online_accounts:
        config.hide_online_accounts = _yes_no("隐藏在线账户页面？", config.hide_online_accounts)
    if context.supports_local_account_screen:
        config.hide_local_account_screen = _yes_no("隐藏 Server 管理员账户页面？", config.hide_local_account_screen)
    config.protect_your_pc = 1 if _yes_no("启用推荐的保护设置？", config.protect_your_pc == 1) else 3
    config.owner = _text("注册所有者（可留空）", config.owner)
    config.organization = _text("组织名称（可留空）", config.organization)
    print("\n--- 4/5 账户设置 ---")
    if _yes_no("创建本地管理员账户？", bool(config.admin_username)):
        config.admin_username = _text("管理员账户名", config.admin_username or "")
        while not config.admin_username:
            print("账户名不能为空。")
            config.admin_username = _text("管理员账户名")
        print("账户密码将以明文写入应答文件，请妥善保管生成的文件。")
        config.admin_password = getpass.getpass("管理员密码（终端中隐藏输入）： ")
        while not config.admin_password:
            print("密码不能为空。")
            config.admin_password = getpass.getpass("管理员密码： ")
        config.auto_logon = _yes_no("首次启动时自动登录该账户？", config.auto_logon)
        if config.auto_logon:
            while True:
                raw = _text("自动登录次数", str(config.auto_logon_count))
                if raw.isdigit() and int(raw) > 0:
                    config.auto_logon_count = int(raw)
                    break
                print("请输入大于 0 的整数。")
    else:
        config.admin_username = None
        config.admin_password = None
        config.auto_logon = False
    print("\n--- 5/5 确认配置 ---")
    print(format_configuration_summary(config, context))
    action = "生成测试应答文件" if config.test_only else "生成应答文件并执行 Sysprep"
    return config if _yes_no(f"确认{action}？", False) else None


def format_configuration_summary(config, context):
    actions = {"shutdown": "关机", "reboot": "重启", "quit": "退出"}
    def yes_no(value):
        return "是" if value else "否"

    lines = [
        f"运行方式：{'测试模式（仅生成应答文件）' if config.test_only else '正式执行 Sysprep /generalize'}",
        f"封装后启动模式：{config.mode}",
        f"完成后动作：{actions.get(config.completion_action, config.completion_action)}",
        "引导保护：正式封装前备份 BCD；多系统环境先核对当前引导再关机/重启",
        f"计算机名：{config.computer_name}",
        f"时区：{config.time_zone}",
        f"输入法区域：{config.input_locale}",
        f"系统区域：{config.system_locale}",
        f"显示语言：{config.ui_language}",
        f"用户区域：{config.user_locale}",
        f"隐藏许可条款：{yes_no(config.hide_eula)}",
        f"保护设置：{config.protect_your_pc}",
        f"注册所有者：{config.owner or '未设置'}",
        f"组织：{config.organization or '未设置'}",
        f"本地管理员账户：{config.admin_username or '不创建'}",
        f"自动登录：{yes_no(config.auto_logon)}",
    ]
    for capability, label, value in (
        ("supports_wireless_oobe", "隐藏无线网络设置", config.hide_wireless),
        ("supports_online_accounts", "隐藏在线账户页面", config.hide_online_accounts),
        ("supports_local_account_screen", "隐藏 Server 管理员账户页面", config.hide_local_account_screen),
    ):
        if getattr(context, capability, False):
            lines.append(f"{label}：{yes_no(value)}")
    if config.auto_logon:
        lines.append(f"自动登录次数：{config.auto_logon_count}")
    return "\n".join(lines)
