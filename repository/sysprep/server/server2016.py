from ..adapter import SysprepAdapter


class Server2016Adapter(
    SysprepAdapter
):


    name = "Windows Server 2016"

    version = "10.0"


    def check_support(self):

        return (
            self.context.family
            ==
            "Windows Server 2016"
        )


    def prepare(self):

        print(
            "执行 Windows Server 2016 封装准备"
        )


    def generate_unattend(self):

        print(
            "生成 Windows Server 2016 unattend.xml"
        )


    def cleanup(self):

        print(
            "执行 Windows Server 2016 清理任务"
        )