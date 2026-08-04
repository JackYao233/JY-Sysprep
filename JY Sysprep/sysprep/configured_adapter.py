from sysprep.adapter import SysprepAdapter
from sysprep.executor import run_sysprep
from sysprep.unattend.generator import generate


class ConfiguredWindowsAdapter(SysprepAdapter):
    def __init__(self, context, name):
        super().__init__(context)
        self.name = name
        self._unattend_path = None

    def check_support(self):
        return self.context.family == self.name

    def prepare(self):
        config = getattr(self.context, "sysprep_config", None)
        if not config:
            raise RuntimeError("未确认封装配置，已取消执行。")
        if not config.test_only and not self.context.is_admin:
            raise PermissionError("请以管理员身份运行 JY Sysprep。")
        print(f"正在为 {self.name} 准备封装配置。")

    def generate_unattend(self):
        self._unattend_path = generate(self.context, self.context.sysprep_config)
        print(f"已生成应答文件：{self._unattend_path}")

    def cleanup(self):
        if self.context.sysprep_config.test_only:
            print("测试模式已完成：未执行 Sysprep。")
            return
        run_sysprep(
            self.context.sysprep_config.mode,
            self.context.sysprep_config.completion_action,
            self._unattend_path,
        )
