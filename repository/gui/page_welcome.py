import tkinter as tk
from tkinter import ttk

from gui.base_page import BasePage
from gui.styles import CARD_BG, TEXT, TEXT_SECONDARY, SUCCESS, DANGER, WARNING, FONT_BODY


class WelcomePage(BasePage):
    def __init__(self, parent, context, preflight_result):
        super().__init__(parent, "JY Sysprep", "环境检测与系统信息")
        self.context = context
        self.preflight = preflight_result
        self._build_content()

    def _build_content(self):
        container = tk.Frame(self, bg=CARD_BG)
        container.pack(fill="both", expand=True, padx=24, pady=16)

        preflight_section = self.create_section(container, "环境预检")
        for check in self.preflight["checks"]:
            row = ttk.Frame(preflight_section)
            row.pack(fill="x", pady=1)
            icon = "✓" if check["ok"] else "✗"
            color = SUCCESS if check["ok"] else DANGER
            tk.Label(row, text=f" {icon} ", font=FONT_BODY, bg=CARD_BG, fg=color, width=3).pack(side="left")
            tk.Label(row, text=check["name"], font=FONT_BODY, bg=CARD_BG, fg=TEXT).pack(side="left")
            if not check["ok"]:
                tk.Label(row, text=f"  ({check['path']})", font=("Microsoft YaHei UI", 9),
                         bg=CARD_BG, fg=DANGER).pack(side="left")

        if self.preflight["passed"]:
            tk.Label(preflight_section, text="预检通过",
                     font=("Microsoft YaHei UI", 10, "bold"),
                     bg=CARD_BG, fg=SUCCESS).pack(anchor="w", pady=(6, 0))
        else:
            failed_names = [c["name"] for c in self.preflight["critical_failed"]]
            tk.Label(preflight_section, text=f"预检失败：缺少 {', '.join(failed_names)}",
                     font=FONT_BODY, bg=CARD_BG, fg=DANGER).pack(anchor="w", pady=(6, 0))

        info_section = self.create_section(container, "系统信息")
        info_items = [
            ("系统类型", self.context.family),
            ("产品名称", self.context.product_name),
            ("版本", self.context.display_version),
            ("Build", self.context.build),
            ("Edition", self.context.edition),
            ("架构", self.context.arch),
            ("NT 版本", self.context.nt_version),
            ("安装类型", self.context.installation_type),
            ("管理员权限", "是" if self.context.is_admin else "否"),
        ]
        for label, value in info_items:
            row = ttk.Frame(info_section)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"{label}：", font=FONT_BODY, bg=CARD_BG,
                     fg=TEXT_SECONDARY, width=12, anchor="w").pack(side="left")
            tk.Label(row, text=str(value or "—"), font=FONT_BODY,
                     bg=CARD_BG, fg=TEXT).pack(side="left")