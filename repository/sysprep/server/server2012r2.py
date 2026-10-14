from ..adapter import SysprepAdapter


class Server2012R2Adapter(
    SysprepAdapter
):


    name = "Windows Server 2012 R2"

    version = "6.3"


    def check_support(self):

        return (
            self.context.family
            ==
            "Windows Server 2012 R2"
        )


    def prepare(self):

        print(
            "执行 Windows Server 2012 R2 封装准备"
        )


    def generate_unattend(self):

        print(
            "生成 Windows Server 2012 R2 unattend.xml"
        )


    def cleanup(self):

        print(
            "执行 Windows Server 2012 R2 清理任务"
        )