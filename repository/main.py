import sys

from core.context import Context
from core.logger import logger
from core.interface import select_interface, create_gui
from core.version import APP_NAME, DISPLAY_VERSION as VERSION

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
from sysprep.config import SysprepConfig


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


def main(argv=None, display_version=VERSION):
    interface = select_interface(argv)
    logger.info("Starting %s %s", APP_NAME, display_version)

    logger.info("正在执行 Sysprep 环境预检...")
    preflight = run_preflight()
    context = detect_system()
    context.interface_title = "{} {}".format(APP_NAME, display_version)
    adapter = AdapterFactory.create(context)
    preflight["checks"] = list(preflight.get("checks", [])) + [
        {"name": "审核模式 (Audit Mode)", "ok": check_audit_mode(), "critical": True,
         "path": "请先在目标 Windows 中进入审核模式"},
        {"name": "系统封装模块", "ok": adapter is not None, "critical": True,
         "path": str(context.family)},
    ]
    preflight["failed"] = [check for check in preflight["checks"] if not check["ok"]]
    preflight["critical_failed"] = [check for check in preflight["failed"] if check["critical"]]
    preflight["passed"] = preflight["passed"] and not preflight["critical_failed"]
    report = format_preflight_report(preflight)
    print(report)
    logger.info("\n%s", report)

    config = SysprepConfig()
    if interface == "gui":
        try:
            app = create_gui(
                context, preflight, config,
                on_finish=lambda selected: execute_configuration(context, adapter, selected),
            )
        except (ImportError, RuntimeError) as error:
            logger.warning("图形界面不可用，转入 TUI：%s", error)
        else:
            app.run()
            if not app.request_tui:
                return "gui"
            config = app.config

    if not preflight["passed"]:
        print("环境检查未通过，请修复以上问题后重新运行。")
        return "tui"
    logger.info("使用 TUI 文本配置向导。")
    try:
        config = collect_configuration(context, config)
    except (KeyboardInterrupt, EOFError):
        config = None
    if config is None:
        print("已取消，未生成应答文件，也不会执行 Sysprep。")
        return "tui"
    execute_configuration(context, adapter, config)
    return "tui"


def execute_configuration(context, adapter, config):
    if not config.test_only:
        if not context.is_admin:
            raise PermissionError("正式封装需要管理员权限。")
        latest = run_preflight()
        if not latest["passed"] or not check_audit_mode():
            raise RuntimeError("正式封装前检查未通过，请确认审核模式与系统文件。")
    context.sysprep_config = config
    logger.info("向导配置完成，开始执行。")
    try:
        adapter.prepare()
        adapter.generate_unattend()
        adapter.cleanup()
    except Exception:
        logger.exception("封装流程执行失败")
        raise
    return getattr(adapter, "_unattend_path", None)


def run_application(argv=None, display_version=None):
    pause_on_exit = True
    try:
        result = main(argv) if display_version is None else main(argv, display_version=display_version)
        pause_on_exit = result != "gui"
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

    if pause_on_exit and sys.stdin.isatty():
        try:
            input("\nPress Enter to exit...")
        except (KeyboardInterrupt, EOFError):
            pass


if __name__ == "__main__":
    run_application()
