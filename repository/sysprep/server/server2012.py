from ..adapter import SysprepAdapter


class Server2012Adapter(
    SysprepAdapter
):


    name = "Windows Server 2012"

    version = "6.2"


    def check_support(self):

        return (
            self.context.family
            ==
            "Windows Server 2012"
        )


    def prepare(self):

        print(
            "执行 Windows Server 2012 封装准备"
        )


    def generate_unattend(self):

        print(
            "生成 Windows Server 2012 unattend.xml"
        )


    def cleanup(self):

        print(
            "执行 Windows Server 2012 清理任务"
        )