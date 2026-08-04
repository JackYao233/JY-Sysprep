from ..adapter import SysprepAdapter


class Windows8Adapter(
    SysprepAdapter
):


    name = "Windows 8"

    version = "6.2"


    def check_support(self):

        return (
            self.context.family
            ==
            "Windows 8"
        )


    def prepare(self):

        print(
            "执行 Windows 8 封装准备"
        )


    def generate_unattend(self):

        print(
            "生成 Windows 8 unattend.xml"
        )


    def cleanup(self):

        print(
            "执行 Windows 8 清理任务"
        )