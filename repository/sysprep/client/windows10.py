from ..adapter import SysprepAdapter


class Windows10Adapter(
    SysprepAdapter
):


    name = "Windows 10"

    version = "10"


    def check_support(self):

        return (
            self.context.os_profile.family
            ==
            "Windows 10"
        )


    def prepare(self):

        print(
            "执行 Windows 10 封装准备"
        )


    def generate_unattend(self):

        print(
            "生成 Windows 10 unattend.xml"
        )


    def cleanup(self):

        print(
            "执行 Windows 10 清理任务"
        )