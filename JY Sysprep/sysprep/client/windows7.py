from ..adapter import SysprepAdapter


class Windows7Adapter(
    SysprepAdapter
):


    name = "Windows 7"

    version = "6.1"


    def check_support(self):

        return (
            self.context.family
            ==
            "Windows 7"
        )


    def prepare(self):

        print(
            "执行 Windows 7 封装准备"
        )


    def generate_unattend(self):

        print(
            "生成 Windows 7 unattend.xml"
        )


    def cleanup(self):

        print(
            "执行 Windows 7 清理任务"
        )