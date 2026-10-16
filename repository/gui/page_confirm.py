import tkinter as tk

from gui.base_page import BasePage
from gui.styles import CARD_BG, TEXT, FONT_BODY, FONT_ACTION, PRIMARY, DANGER
from sysprep.wizard import format_configuration_summary


class ConfirmPage(BasePage):
    def __init__(self, parent, config, context, on_execute=None):
        super().__init__(parent, "确认执行", "核对配置后再执行；F8 可切换文本模式")
        self.config = config
        self.context = context
        self.on_execute = on_execute
        section = self.create_section(self, "配置摘要")
        self.summary = tk.StringVar()
        tk.Label(section, textvariable=self.summary, justify="left", anchor="w",
                 font=FONT_BODY, bg=CARD_BG, fg=TEXT, wraplength=600).pack(fill="x")
        if getattr(context, "family", None) == "Windows Vista":
            tk.Label(self, text="Vista 通用化及重启配置可能等待十多分钟，请结合日志变化观察进度。",
                     justify="left", anchor="w", font=FONT_BODY, bg=CARD_BG, fg=TEXT,
                     wraplength=600).pack(fill="x", padx=24, pady=(12, 0))
        self.status = tk.StringVar()
        tk.Label(self, textvariable=self.status, justify="left", anchor="w",
                 font=FONT_BODY, bg=CARD_BG, wraplength=600).pack(fill="x", padx=24, pady=12)
        self.btn_execute = tk.Button(
            self, font=FONT_ACTION, fg="white",
            relief="flat", cursor="hand2", padx=24, pady=8, command=self._on_execute,
        )
        self.btn_execute.pack(anchor="e", padx=24, pady=(8, 20))
        self.refresh()

    def refresh(self):
        self.summary.set(format_configuration_summary(self.config, self.context))
        color = PRIMARY if self.config.test_only else DANGER
        self.btn_execute.configure(
            text="生成测试应答文件" if self.config.test_only else "生成应答文件并执行 Sysprep",
            bg=color, activebackground=color,
        )

    def set_status(self, text):
        self.status.set(text)

    def _on_execute(self):
        if self.on_execute:
            self.on_execute()

    def collect(self):
        return True, None
