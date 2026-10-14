import tkinter as tk
from tkinter import ttk

from gui.base_page import BasePage
from gui.styles import CARD_BG, TEXT, TEXT_SECONDARY, FONT_BODY, PRIMARY, DANGER


class ConfirmPage(BasePage):
    def __init__(self, parent, config, context, on_execute=None):
        super().__init__(parent, "确认执行", "请检查以下配置摘要")
        self.config = config
        self.context = context
        self.on_execute = on_execute
        self._build_content()

    def _build_content(self):
        container = tk.Frame(self, bg=CARD_BG)
        container.pack(fill="both", expand=True, padx=24, pady=16)

        section = self.create_section(container, "配置摘要")

        mode_text = "审核模式" if self.config.mode == "audit" else "OOBE 模式"
        action_map = {"shutdown": "关机", "reboot": "重启", "quit": "退出"}
        action_text = action_map.get(self.config.completion_action, self.config.completion_action)

        lines = [
            ("运行模式", "测试模式" if self.config.test_only else f"正式执行 — {mode_text}"),
            ("完成后动作", action_text),
            ("计算机名", self.config.computer_name),
            ("时区", self.config.time_zone),
            ("语言", f"{self.config.input_locale} / {self.config.ui_language}"),
            ("隐藏 EULA", "是" if self.config.hide_eula else "否"),
            ("保护设置", "推荐" if self.config.protect_your_pc == 1 else "不启用"),
        ]
        if self.config.owner:
            lines.append(("注册所有者", self.config.owner))
        if self.config.organization:
            lines.append(("组织", self.config.organization))
        if self.config.admin_username:
            lines.append(("管理员账户", self.config.admin_username))
            lines.append(("自动登录", "是" if self.config.auto_logon else "否"))

        for label, value in lines:
            row = ttk.Frame(section)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{label}：", font=FONT_BODY, bg=CARD_BG,
                     fg=TEXT_SECONDARY, width=14, anchor="w").pack(side="left")
            tk.Label(row, text=str(value), font=FONT_BODY, bg=CARD_BG, fg=TEXT).pack(side="left")

        btn_frame = tk.Frame(self, bg=CARD_BG)
        btn_frame.pack(fill="x", padx=24, pady=(20, 16))

        if self.config.test_only:
            btn_text = "生成测试应答文件"
            btn_color = PRIMARY
        else:
            btn_text = "生成应答文件并执行 Sysprep"
            btn_color = DANGER

        self.btn_execute = tk.Button(
            btn_frame, text=btn_text, font=("Microsoft YaHei UI", 11, "bold"),
            bg=btn_color, fg="white", activebackground=btn_color,
            relief="flat", cursor="hand2", padx=24, pady=8,
            command=self._on_execute
        )
        self.btn_execute.pack(side="right")

    def _on_execute(self):
        if self.on_execute:
            self.on_execute()

    def collect(self):
        return True, None