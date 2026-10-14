import sys

from core.context import Context
from core.logger import logger

from osdetect.detect import get_windows_info
from osdetect.windows import read_windows_registry
from osdetect.edition import (
    detect_windows_family,
    detect_nt_version,
    detect_server
)
from osdetect.profile import create_os_profile

from sysprep.factory import AdapterFactory
from sysprep.preflight import run_preflight, format_preflight_report
from sysprep.status import check_audit_mode
from sysprep.wizard import collect_configuration


def detect_system():
    context = Context()

    info = get_windows_info()
    reg = read_windows_registry()
    profile = create_os_profile(reg, info)

    context.os_profile = profile
    context.family = profile.family
    context.product_name = profile.product_name
    context.display_version = profile.display_version
    context.build = profile.build
    context.edition = profile.edition
    context.arch = profile.architecture
    context.is_admin = profile.is_admin
    context.nt_version = detect_nt_version(reg)
    context.installation_type = reg.get("InstallationType")
    context.is_server = detect_server(reg)

    context.family = detect_windows_family(
        context.build, context.product_name, context.is_server
    )

    if context.family in ("Windows 8", "Windows 8.1", "Windows 10", "Windows 11"):
        context.supports_wireless_oobe = True
    if not context.is_server and context.family in ("Windows 8", "Windows 8.1", "Windows 10", "Windows 11"):
        context.supports_online_accounts = True
    if context.is_server and context.family in (
        "Windows Server 2012", "Windows Server 2012 R2",
        "Windows Server 2016", "Windows Server 2019",
        "Windows Server 2022", "Windows Server 2025"
    ):
        context.supports_local_account_screen = True

    return context


def main():
    logger.info("Starting JY Sysprep")

    logger.info("正在执行 Sysprep 环境预检...")
    preflight = run_preflight()
    report = format_preflight_report(preflight)
    print(report)
    logger.info(f"\n{report}")

    if not preflight["passed"]:
        failed_names = [c["name"] for c in preflight["critical_failed"]]
        msg = f"Sysprep 预检失败，缺少关键文件：{', '.join(failed_names)}"
        logger.error(msg)
        print(f"\n{msg}")
        print("请修复上述问题后重新运行。")
        return

    if not check_audit_mode():
        print("当前系统不在审核模式 (Audit Mode) 下运行。")
        print("请先通过 sysprep /audit 进入审核模式后再运行本程序。")
        return

    context = detect_system()

    adapter = AdapterFactory.create(context)
    if adapter is None:
        print("当前系统没有对应封装模块。")
        return

    logger.info("使用 TUI 文本配置向导。")
    try:
        config = collect_configuration(context)
    except (KeyboardInterrupt, EOFError):
        config = None
    if config is None:
        print("已取消，未生成应答文件，也不会执行 Sysprep。")
        return
    context.sysprep_config = config
    logger.info("向导配置完成，开始执行。")
    adapter.prepare()
    adapter.generate_unattend()
    adapter.cleanup()


if __name__ == "__main__":

    try:

        main()

    except Exception as e:

        print("程序异常:")
        print(repr(e))
        logger.error(f"程序异常: {repr(e)}", exc_info=True)

        from sysprep.log_collector import collect_sysprep_logs
        log_dir = collect_sysprep_logs()
        if log_dir:
            print(f"Sysprep 日志已保存到桌面: {log_dir}")
        else:
            print("未能收集 Sysprep 日志。")

    if sys.stdin.isatty():
        input("\nPress Enter to exit...")
