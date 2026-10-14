import tkinter as tk
from tkinter import ttk

from gui.base_page import BasePage
from gui.styles import CARD_BG, TEXT, FONT_BODY


class OOBEPage(BasePage):
    def __init__(self, parent, config, context):
        super().__init__(parent, "OOBE 选项", "配置首次启动体验界面")
        self.config = config
        self.context = context
        self._build_content()

    def _build_content(self):
        container = tk.Frame(self, bg=CARD_BG)
        container.pack(fill="both", expand=True, padx=24, pady=16)

        section = self.create_section(container, "隐藏页面")

        self.var_hide_eula = tk.BooleanVar(value=self.config.hide_eula)
        ttk.Checkbutton(section, text="隐藏许可条款页面", variable=self.var_hide_eula).pack(anchor="w", pady=2)

        self.var_hide_wireless = tk.BooleanVar(value=getattr(self.config, "hide_wireless", True))
        self.cb_wireless = ttk.Checkbutton(section, text="隐藏无线网络设置页面", variable=self.var_hide_wireless)
        self.cb_wireless.pack(anchor="w", pady=2)
        if not self.context.supports_wireless_oobe:
            self.cb_wireless.configure(state="disabled")

        self.var_hide_online = tk.BooleanVar(value=getattr(self.config, "hide_online_accounts", False))
        self.cb_online = ttk.Checkbutton(section, text="隐藏在线账户页面", variable=self.var_hide_online)
        self.cb_online.pack(anchor="w", pady=2)
        if not self.context.supports_online_accounts:
            self.cb_online.configure(state="disabled")

        self.var_hide_local = tk.BooleanVar(value=getattr(self.config, "hide_local_account_screen", False))
        self.cb_local = ttk.Checkbutton(section, text="隐藏 Server 管理员账户页面", variable=self.var_hide_local)
        self.cb_local.pack(anchor="w", pady=2)
        if not self.context.supports_local_account_screen:
            self.cb_local.configure(state="disabled")

        protect_section = self.create_section(container, "保护设置")
        self.var_protect = tk.IntVar(value=1 if self.config.protect_your_pc == 1 else 3)
        ttk.Radiobutton(protect_section, text="启用推荐的保护设置", variable=self.var_protect, value=1).pack(anchor="w", pady=2)
        ttk.Radiobutton(protect_section, text="不启用推荐设置", variable=self.var_protect, value=3).pack(anchor="w", pady=2)

        owner_section = self.create_section(container, "注册信息（可选）")
        row1 = ttk.Frame(owner_section)
        row1.pack(fill="x", pady=3)
        tk.Label(row1, text="注册所有者：", font=FONT_BODY, bg=CARD_BG, fg=TEXT, width=12, anchor="w").pack(side="left")
        self.var_owner = tk.StringVar(value=self.config.owner)
        ttk.Entry(row1, textvariable=self.var_owner, width=30).pack(side="left", padx=(8, 0))

        row2 = ttk.Frame(owner_section)
        row2.pack(fill="x", pady=3)
        tk.Label(row2, text="组织名称：", font=FONT_BODY, bg=CARD_BG, fg=TEXT, width=12, anchor="w").pack(side="left")
        self.var_org = tk.StringVar(value=self.config.organization)
        ttk.Entry(row2, textvariable=self.var_org, width=30).pack(side="left", padx=(8, 0))

    def collect(self):
        self.config.hide_eula = self.var_hide_eula.get()
        if self.context.supports_wireless_oobe:
            self.config.hide_wireless = self.var_hide_wireless.get()
        if self.context.supports_online_accounts:
            self.config.hide_online_accounts = self.var_hide_online.get()
        if self.context.supports_local_account_screen:
            self.config.hide_local_account_screen = self.var_hide_local.get()
        self.config.protect_your_pc = self.var_protect.get()
        self.config.owner = self.var_owner.get().strip()
        self.config.organization = self.var_org.get().strip()
        return True, None