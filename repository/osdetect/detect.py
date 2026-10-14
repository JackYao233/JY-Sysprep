try:

    import ctypes

except ImportError:

    ctypes = None


import platform



def get_windows_info():

    info={}


    info["version"] = platform.version()

    info["system"] = platform.system()

    info["architecture"] = platform.machine()



    try:

        if ctypes:

            info["admin"] = (
                ctypes.windll.shell32.IsUserAnAdmin()
                !=0
            )

        else:

            info["admin"] = False


    except Exception:

        info["admin"]=False



    return info