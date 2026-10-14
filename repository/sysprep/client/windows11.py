from ..adapter import SysprepAdapter
from sysprep.unattend.generator import generate
from sysprep.executor import run_sysprep
from sysprep.cleaner.windows import clean_temp

class Windows11Adapter(
    SysprepAdapter
):


    name = "Windows 11"

    version = "11"



    def check_support(self):


        return (
            self.context.os_profile.family
            ==
            "Windows 11"
        )

    def prepare(self):
        print(
            "执行 Windows 11 封装准备"
        )

        print(
            "清理临时文件"
        )


        print(
            "准备完成"
        )

    def generate_unattend(self):
        print(
            "进入 Windows11 unattend生成"
        )

        print(
            "加载generator成功"
        )

        path = generate(
            self.context
        )

        print(
            "生成:",
            path
        )

    def cleanup(self):
        print(
            "执行 Windows 11 Sysprep"
        )

        run_sysprep(
            "audit"
        )