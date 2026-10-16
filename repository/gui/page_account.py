import tkinter as tk
from tkinter import ttk

from gui.base_page import BasePage
from gui.styles import CARD_BG, TEXT, FONT_BODY


class AccountPage(BasePage):
    def __init__(self, parent, config):
        super().__init__(parent, "账户设置", "配置本地管理员账户")
        self.config = config
        self._build_content()

    def _build_content(self):
        container = tk.Frame(self, bg=CARD_BG)
        container.pack(fill="both", expand=True, padx=24, pady=16)

        section = self.create_section(container, "本地管理员账户")

        self.var_create_admin = tk.BooleanVar(value=bool(self.config.admin_username))
        self.cb_create = ttk.Checkbutton(section, text="创建本地管理员账户",
                                          variable=self.var_create_admin,
                                          command=self._toggle_fields)
        self.cb_create.pack(anchor="w", pady=(0, 8))

        self.account_frame = ttk.Frame(section)
        self.account_frame.pack(fill="x")

        row1 = ttk.Frame(self.account_frame)
        row1.pack(fill="x", pady=3)
        tk.Label(row1, text="管理员账户名：", font=FONT_BODY, bg=CARD_BG, fg=TEXT, width=14, anchor="w").pack(side="left")
        self.var_username = tk.StringVar(value=self.config.admin_username or "")
        self.entry_username = ttk.Entry(row1, textvariable=self.var_username, width=24)
        self.entry_username.pack(side="left", padx=(8, 0))

        row2 = ttk.Frame(self.account_frame)
        row2.pack(fill="x", pady=3)
        tk.Label(row2, text="密码：", font=FONT_BODY, bg=CARD_BG, fg=TEXT, width=14, anchor="w").pack(side="left")
        self.var_password = tk.StringVar(value=self.config.admin_password or "")
        self.entry_password = ttk.Entry(row2, textvariable=self.var_password, width=24, show="*")
        self.entry_password.pack(side="left", padx=(8, 0))
        tk.Label(section, text="创建账户时，密码会以明文写入应答文件。", font=FONT_BODY,
                 bg=CARD_BG, fg=TEXT).pack(anchor="w", pady=(8, 0))

        auto_section = self.create_section(container, "自动登录")
        self.var_auto_logon = tk.BooleanVar(value=self.config.auto_logon)
        self.cb_auto = ttk.Checkbutton(auto_section, text="首次启动时自动登录管理员账户",
                                        variable=self.var_auto_logon,
                                        command=self._toggle_auto_logon)
        self.cb_auto.pack(anchor="w", pady=(0, 4))

        count_frame = ttk.Frame(auto_section)
        count_frame.pack(fill="x")
        tk.Label(count_frame, text="自动登录次数：", font=FONT_BODY, bg=CARD_BG, fg=TEXT, width=14, anchor="w").pack(side="left")
        self.var_logon_count = tk.StringVar(value=str(self.config.auto_logon_count))
        self.entry_count = ttk.Entry(count_frame, textvariable=self.var_logon_count, width=8)
        self.entry_count.pack(side="left", padx=(8, 0))

        self._toggle_fields()
        self._toggle_auto_logon()

    def _toggle_fields(self):
        state = "normal" if self.var_create_admin.get() else "disabled"
        self.entry_username.configure(state=state)
        self.entry_password.configure(state=state)
        self.cb_auto.configure(state=state)
        if not self.var_create_admin.get():
            self.var_auto_logon.set(False)
            self._toggle_auto_logon()

    def _toggle_auto_logon(self):
        state = "normal" if (self.var_create_admin.get() and self.var_auto_logon.get()) else "disabled"
        self.entry_count.configure(state=state)

    def collect(self):
        if self.var_create_admin.get():
            username = self.var_username.get().strip()
            password = self.var_password.get()
            if not username:
                return False, "管理员账户名不能为空。"
            if not password:
                return False, "管理员密码不能为空。"
            count = self.config.auto_logon_count
            if self.var_auto_logon.get():
                try:
                    count = int(self.var_logon_count.get())
                    if count <= 0:
                        raise ValueError
                except ValueError:
                    return False, "自动登录次数必须为大于 0 的整数。"
            self.config.admin_username = username
            self.config.admin_password = password
            self.config.auto_logon = self.var_auto_logon.get()
            self.config.auto_logon_count = count
        else:
            self.config.admin_username = None
            self.config.admin_password = None
            self.config.auto_logon = False
        return True, None
