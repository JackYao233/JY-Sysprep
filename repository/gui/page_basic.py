import re
import tkinter as tk
from tkinter import ttk, messagebox

from gui.base_page import BasePage
from gui.styles import CARD_BG, TEXT, FONT_BODY


class BasicPage(BasePage):
    def __init__(self, parent, config):
        super().__init__(parent, "基本设置", "配置 Sysprep 运行模式")
        self.config = config
        self._build_content()

    def _build_content(self):
        container = tk.Frame(self, bg=CARD_BG)
        container.pack(fill="both", expand=True, padx=24, pady=16)

        section = self.create_section(container, "运行模式")

        self.var_test_only = tk.BooleanVar(value=self.config.test_only)
        cb_test = ttk.Checkbutton(section, text="测试模式（仅生成应答文件，不执行 Sysprep）",
                                   variable=self.var_test_only)
        cb_test.pack(anchor="w", pady=4)

        mode_frame = ttk.Frame(section)
        mode_frame.pack(fill="x", pady=(8, 0))
        tk.Label(mode_frame, text="封装后启动模式：", font=FONT_BODY, bg=CARD_BG, fg=TEXT).pack(side="left")
        self.var_mode = tk.StringVar(value=self.config.mode)
        ttk.Radiobutton(mode_frame, text="审核模式 (Audit)", variable=self.var_mode, value="audit").pack(side="left", padx=(8, 0))
        ttk.Radiobutton(mode_frame, text="OOBE 模式", variable=self.var_mode, value="oobe").pack(side="left", padx=(12, 0))

        action_frame = ttk.Frame(section)
        action_frame.pack(fill="x", pady=(8, 0))
        tk.Label(action_frame, text="完成后动作：", font=FONT_BODY, bg=CARD_BG, fg=TEXT).pack(side="left")
        self.var_action = tk.StringVar(value=self.config.completion_action)
        ttk.Radiobutton(action_frame, text="关机", variable=self.var_action, value="shutdown").pack(side="left", padx=(8, 0))
        ttk.Radiobutton(action_frame, text="重启", variable=self.var_action, value="reboot").pack(side="left", padx=(12, 0))
        ttk.Radiobutton(action_frame, text="退出", variable=self.var_action, value="quit").pack(side="left", padx=(12, 0))

        name_section = self.create_section(container, "计算机名")
        name_frame = ttk.Frame(name_section)
        name_frame.pack(fill="x")
        tk.Label(name_frame, text="计算机名：", font=FONT_BODY, bg=CARD_BG, fg=TEXT).pack(side="left")
        self.var_computer_name = tk.StringVar(value=self.config.computer_name)
        self.entry_name = ttk.Entry(name_frame, textvariable=self.var_computer_name, width=30)
        self.entry_name.pack(side="left", padx=(8, 0))
        tk.Label(name_section, text="输入 * 表示自动生成", font=("Microsoft YaHei UI", 9),
                 bg=CARD_BG, fg="#999999").pack(anchor="w", pady=(4, 0))

        tz_section = self.create_section(container, "时区")
        tz_frame = ttk.Frame(tz_section)
        tz_frame.pack(fill="x")
        tk.Label(tz_frame, text="时区：", font=FONT_BODY, bg=CARD_BG, fg=TEXT).pack(side="left")
        self.var_timezone = tk.StringVar(value=self.config.time_zone)
        ttk.Entry(tz_frame, textvariable=self.var_timezone, width=30).pack(side="left", padx=(8, 0))

    def collect(self):
        self.config.test_only = self.var_test_only.get()
        self.config.mode = self.var_mode.get()
        self.config.completion_action = self.var_action.get()
        self.config.time_zone = self.var_timezone.get().strip() or "China Standard Time"

        name = self.var_computer_name.get().strip()
        if name and name != "*":
            if not re.fullmatch(r"[A-Za-z0-9-]{1,15}", name) or name.isdigit():
                return False, "计算机名必须为 1–15 个字符，只能包含字母、数字和连字符，且不能全为数字。"
        self.config.computer_name = name or "*"
        return True, None