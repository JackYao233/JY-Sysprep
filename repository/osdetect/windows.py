import winreg


REG_PATH = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"



def read_windows_registry():

    result={}


    try:

        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            REG_PATH
        )

        values = [

            "ProductName",

            "DisplayVersion",

            "CurrentBuild",

            "CurrentVersion",

            "CurrentMajorVersionNumber",

            "CurrentMinorVersionNumber",

            "EditionID",

            "InstallationType",

            "ProductId"

        ]

        for value in values:

            try:

                data,_ = winreg.QueryValueEx(
                    key,
                    value
                )

                result[value]=data



            except FileNotFoundError:

                result[value] = None


    except Exception as e:

        result["error"]=str(e)


    return result