from ..adapter import SysprepAdapter


class Server2019Adapter(
    SysprepAdapter
):


    name = "Windows Server 2019"

    version = "10.0"


    def check_support(self):

        return (
            self.context.family
            ==
            "Windows Server 2019"
        )


    def prepare(self):

        print(
            "执行 Windows Server 2019 封装准备"
        )


    def generate_unattend(self):

        print(
            "生成 Windows Server 2019 unattend.xml"
        )


    def cleanup(self):

        print(
            "执行 Windows Server 2019 清理任务"
        )