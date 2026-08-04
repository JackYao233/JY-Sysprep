import os


def check_environment():


    result = {}


    windows = os.environ.get(
        "WINDIR",
        r"C:\Windows"
    )


    sysprep_dir = os.path.join(
        windows,
        "System32",
        "Sysprep"
    )


    panther = os.path.join(
        windows,
        "Panther"
    )


    result["sysprep_dir"] = (
        os.path.exists(sysprep_dir)
    )


    result["panther"] = (
        os.path.exists(panther)
    )


    # Sysprep相关日志

    generalize_log = os.path.join(
        panther,
        "setupact.log"
    )


    result["generalize"] = (
        os.path.exists(generalize_log)
    )


    # OOBE状态

    oobe = os.path.join(
        windows,
        "System32",
        "oobe"
    )


    result["oobe"] = (
        os.path.exists(oobe)
    )


    # Audit模式相关

    audit = os.path.join(
        windows,
        "Panther",
        "UnattendGC"
    )


    result["audit"] = (
        os.path.exists(audit)
    )


    return result