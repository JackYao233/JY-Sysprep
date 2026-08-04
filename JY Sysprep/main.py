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

from sysprep.detector import check_sysprep
from sysprep.factory import AdapterFactory
from sysprep.status import check_environment
from sysprep.wizard import collect_configuration


def main():

    logger.info(
        "Starting JY Sysprep"
    )


    # 创建系统上下文
    context = Context()


    # =========================
    # 获取基础系统信息
    # =========================

    info = get_windows_info()






    # =========================
    # 获取注册表Windows信息
    # =========================

    reg = read_windows_registry()
    print(reg)

    profile = create_os_profile(

        reg,

        info

    )
    context.os_profile = profile

    context.family = profile.family

    context.product_name = profile.product_name

    context.display_version = profile.display_version

    context.build = profile.build

    context.edition = profile.edition

    context.arch = profile.architecture

    context.is_admin = profile.is_admin

    context.nt_version = detect_nt_version(reg)

    context.installation_type = reg.get(
        "InstallationType"
    )

    context.is_server = detect_server(reg)


    # =========================
    # 判断Windows系列
    # =========================

    context.family = detect_windows_family(

        context.build,

        context.product_name,

        context.is_server

    )

    # =========================
    # Sysprep检测
    # =========================
    status = check_environment()
    from sysprep.detector import find_sysprep
    sysprep_info = find_sysprep()

    print(
        "Sysprep:"
    )

    print(
        sysprep_info
    )

    print(
        "Sysprep状态:",
        sysprep_info["exist"]
    )

    print(
        "Sysprep路径:",
        sysprep_info["path"]
    )


    # =========================
    # 输出结果
    # =========================

    print("==============================")

    print(
        "系统类型:",
        context.family
    )


    print(
        "产品名称:",
        context.product_name
    )


    print(
        "版本:",
        context.display_version
    )

    print(
        "NT版本:",
        context.nt_version
    )

    print(
        "安装类型:",
        context.installation_type
    )

    print(
        "Build:",
        context.build
    )


    print(
        "Edition:",
        context.edition
    )

    print(
        "安装类型:",
        context.installation_type
    )

    print(
        "是否Server:",
        context.is_server
    )

    print(
        "架构:",
        context.arch
    )


    print(
        "管理员权限:",
        context.is_admin
    )


    print("==============================")



    logger.info(
        "done"
    )

    adapter = AdapterFactory.create(
        context
    )

    if adapter is None:
        print(
            "当前系统没有对应封装模块"
        )

        return

    context.sysprep_config = collect_configuration(context)
    if context.sysprep_config is None:
        print("已取消，未生成应答文件，也不会执行 Sysprep。")
        return

    print(
        "当前封装模块:",
        adapter.name
    )

    print(
        "支持状态:",
        adapter.check_support()
    )

    adapter.prepare()

    adapter.generate_unattend()

    adapter.cleanup()



    print("==============================")

    print(
        "Sysprep目录:",
        status["sysprep_dir"]
    )

    print(
        "Panther日志:",
        status["panther"]
    )

    print(
        "Generalize:",
        status["generalize"]
    )

    print(
        "OOBE:",
        status["oobe"]
    )

    print(
        "Audit:",
        status["audit"]
    )

    print("==============================")

    print(
        "Profile测试:"
    )

    print(
        context.os_profile.family
    )

if __name__ == "__main__":

    try:

        main()

    except Exception as e:

        print(
            "程序异常:"
        )

        print(
            repr(e)
        )


    if sys.stdin.isatty():
        input("\nPress Enter to exit...")
