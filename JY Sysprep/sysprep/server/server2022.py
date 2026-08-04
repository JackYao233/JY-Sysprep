from ..adapter import SysprepAdapter


class Server2022Adapter(
    SysprepAdapter
):


    name = "Windows Server 2022"

    version = "10.0"


    def check_support(self):

        return (
            self.context.family
            ==
            "Windows Server 2022"
        )


    def prepare(self):

        print(
            "执行 Windows Server 2022 封装准备"
        )


    def generate_unattend(self):

        print(
            "生成 Windows Server 2022 unattend.xml"
        )


    def cleanup(self):

        print(
            "执行 Windows Server 2022 清理任务"
        )