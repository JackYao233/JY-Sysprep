import os


def find_sysprep():


    paths = [

        r"C:\Windows\System32\Sysprep",

        r"C:\Windows\SysWOW64\Sysprep"

    ]


    for path in paths:


        exe = os.path.join(
            path,
            "sysprep.exe"
        )


        if os.path.exists(exe):

            return {

                "exist": True,

                "path": path,

                "exe": exe

            }



    return {

        "exist": False,

        "path": None,

        "exe": None

    }



# 兼容旧接口

def check_sysprep():

    return find_sysprep()