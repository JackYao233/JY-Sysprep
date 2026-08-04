from sysprep.models.osprofile import OSProfile

from osdetect.edition import (
    detect_windows_family,
    detect_nt_version,
    detect_server
)



def create_os_profile(reg, windows_info):


    profile = OSProfile()



    # ======================
    # 注册表信息
    # ======================

    profile.product_name = reg.get(
        "ProductName"
    )


    profile.display_version = reg.get(
        "DisplayVersion"
    )


    profile.build = reg.get(
        "CurrentBuild"
    )


    profile.edition = reg.get(
        "EditionID"
    )


    profile.installation_type = reg.get(
        "InstallationType"
    )



    # ======================
    # NT版本
    # ======================

    profile.nt_version = detect_nt_version(
        reg
    )



    # ======================
    # Server判断
    # ======================

    profile.is_server = detect_server(
        reg
    )



    # ======================
    # 系统类型判断
    # ======================

    profile.family = detect_windows_family(

        profile.build,

        profile.product_name,

        profile.is_server

    )



    # ======================
    # 硬件信息
    # ======================

    profile.architecture = windows_info.get(
        "architecture"
    )


    profile.is_admin = windows_info.get(
        "admin"
    )


    return profile