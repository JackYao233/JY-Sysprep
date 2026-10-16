"""Initial Vista scope: SP2 x64, single-system installation only."""
import sys

from sysprep.configured_adapter import ConfiguredWindowsAdapter
from sysprep.executor import run_sysprep


class VistaAdapter(ConfiguredWindowsAdapter):
    def __init__(self, context):
        super().__init__(context, "Windows Vista")

    def prepare(self):
        super().prepare()
        version = sys.getwindowsversion()
        if (version.major, version.minor) != (6, 0) or version.service_pack_major < 2:
            raise RuntimeError("Vista 实验支持要求 Windows Vista SP2。")
        if str(self.context.arch).lower() not in ("amd64", "x86_64", "x64"):
            raise RuntimeError("当前 Vista 实验支持仅覆盖 x64；x86 尚未适配验收。")
        if self.context.family != "Windows Vista" or getattr(self.context, "is_server", False):
            raise RuntimeError("此适配器仅适用于 Windows Vista 客户端。")
        print("Vista SP2 x64 实验支持：仅限单系统；不同配置仍需分别验证。")
        print("通用化及重启配置可能等待十多分钟，请结合日志变化观察进度。")

    def cleanup(self):
        config = self.context.sysprep_config
        if config.test_only:
            print("Vista 测试文件已生成：未执行 Sysprep，也未修改 BCD。")
            return
        run_sysprep(config.mode, config.completion_action, self._unattend_path,
                    allow_multiboot=False)
