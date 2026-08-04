from ..adapter import SysprepAdapter


class Windows81Adapter(
    SysprepAdapter
):


    name = "Windows 8.1"

    version = "6.3"


    def check_support(self):

        return (
            self.context.family
            ==
            "Windows 8.1"
        )


    def prepare(self):

        print(
            "执行 Windows 8.1 封装准备"
        )


    def generate_unattend(self):

        print(
            "生成 Windows 8.1 unattend.xml"
        )


    def cleanup(self):

        print(
            "执行 Windows 8.1 清理任务"
        )