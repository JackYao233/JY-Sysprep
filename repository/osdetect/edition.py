def detect_windows_family(
        build,
        product,
        is_server=False
):

    try:
        build = int(build)

    except:
        build = 0


    # =====================
    # Server系统
    # =====================

    if is_server:


        if 6000 <= build < 7600:

            return "Windows Server 2008"


        if 7600 <= build < 9200:

            return "Windows Server 2008 R2"


        if 9200 <= build < 9600:

            return "Windows Server 2012"


        if 9600 <= build < 10240:

            return "Windows Server 2012 R2"


        if 14393 <= build < 17763:

            return "Windows Server 2016"


        if 17763 <= build < 20348:

            return "Windows Server 2019"


        if 20348 <= build < 26100:

            return "Windows Server 2022"


        if build >= 26100:

            return "Windows Server 2025"


        return "Windows Server"



    # =====================
    # Client系统
    # =====================

    else:


        if 6000 <= build < 7600:

            return "Windows Vista"


        if 7600 <= build < 9200:

            return "Windows 7"


        if 9200 <= build < 9600:

            return "Windows 8"


        if 9600 <= build < 10240:

            return "Windows 8.1"


        if 10240 <= build < 22000:

            return "Windows 10"


        if build >= 22000:

            return "Windows 11"


    return "Unknown"

def detect_nt_version(reg):

    major = reg.get(
        "CurrentMajorVersionNumber"
    )

    minor = reg.get(
        "CurrentMinorVersionNumber"
    )


    if major is not None and minor is not None:

        return f"{major}.{minor}"


    version = reg.get(
        "CurrentVersion"
    )


    if version:

        return version


    return None
def detect_server(reg):

    product = str(
        reg.get(
            "ProductName",
            ""
        )
    ).lower()


    installation = str(
        reg.get(
            "InstallationType",
            ""
        )
    ).lower()


    edition = str(
        reg.get(
            "EditionID",
            ""
        )
    ).lower()



    if "server" in product:

        return True


    if installation == "server":

        return True


    if "server" in edition:

        return True


    if "datacenter" in edition:

        return True


    return False