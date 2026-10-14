import tkinter as tk
from tkinter import ttk, messagebox

from gui.styles import BG, CARD_BG, PRIMARY, TEXT, FONT_BUTTON
from gui.page_welcome import WelcomePage
from gui.page_basic import BasicPage
from gui.page_locale import LocalePage
from gui.page_oobe import OOBEPage
from gui.page_account import AccountPage
from gui.page_confirm import ConfirmPage


class SysprepWizardApp:
    PAGE_CLASSES = [
        "welcome",
        "basic",
        "locale",
        "oobe",
        "account",
        "confirm",
    ]

    def __init__(self, context, preflight_result, config, on_finish=None):
        self.context = context
        self.preflight = preflight_result
        self.config = config
        self.on_finish = on_finish
        self.current_index = 0

        self.root = tk.Tk()
        self.root.title("JY Sysprep")
        self.root.geometry("680x600")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self._center_window(680, 600)

        self._setup_styles()
        self._build_ui()
        self._show_page(0)

    def _center_window(self, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Page.TFrame", background=CARD_BG)
        style.configure("Header.TFrame", background=CARD_BG)
        style.configure("Nav.TFrame", background=BG)
        style.configure("TLabelFrame", background=CARD_BG, foreground=TEXT)
        style.configure("TLabelFrame.Label", background=CARD_BG, foreground=TEXT,
                         font=("Microsoft YaHei UI", 10, "bold"))
        style.configure("TFrame", background=CARD_BG)
        style.configure("TCheckbutton", background=CARD_BG)
        style.configure("TRadiobutton", background=CARD_BG)

    def _build_ui(self):
        self.nav_frame = tk.Frame(self.root, bg=BG)
        self.nav_frame.pack(fill="x", padx=16, pady=(12, 0))

        self.nav_buttons = []
        for i, name in enumerate(self.PAGE_CLASSES):
            labels = {
                "welcome": "1. 环境检测",
                "basic": "2. 基本设置",
                "locale": "3. 区域设置",
                "oobe": "4. OOBE",
                "account": "5. 账户",
                "confirm": "6. 确认",
            }
            btn = tk.Button(
                self.nav_frame, text=labels[name],
                font=FONT_BUTTON, bg=BG, fg=TEXT,
                relief="flat", cursor="hand2",
                padx=8, pady=4,
                command=lambda idx=i: self._go_to(idx)
            )
            btn.pack(side="left", padx=2)
            self.nav_buttons.append(btn)

        sep = ttk.Separator(self.root, orient="horizontal")
        sep.pack(fill="x", padx=16, pady=(4, 0))

        self.page_container = tk.Frame(self.root, bg=CARD_BG)
        self.page_container.pack(fill="both", expand=True)

        bottom = tk.Frame(self.root, bg=BG)
        bottom.pack(fill="x", padx=16, pady=(0, 12))

        self.btn_prev = tk.Button(
            bottom, text="← 上一步", font=FONT_BUTTON,
            bg=BG, fg=TEXT, relief="flat", cursor="hand2",
            command=self._prev
        )
        self.btn_prev.pack(side="left")

        self.btn_next = tk.Button(
            bottom, text="下一步 →", font=FONT_BUTTON,
            bg=PRIMARY, fg="white", relief="flat", cursor="hand2",
            command=self._next
        )
        self.btn_next.pack(side="right")

        self.pages = {}
        self._pages_list = []

    def _build_pages(self):
        self._pages_list = [
            WelcomePage(self.page_container, self.context, self.preflight),
            BasicPage(self.page_container, self.config),
            LocalePage(self.page_container, self.config),
            OOBEPage(self.page_container, self.config, self.context),
            AccountPage(self.page_container, self.config),
            ConfirmPage(self.page_container, self.config, self.context, on_execute=self._execute),
        ]

    def _show_page(self, index):
        if not self._pages_list:
            self._build_pages()

        for page in self._pages_list:
            page.pack_forget()

        self.current_index = index
        page = self._pages_list[index]
        page.pack(fill="both", expand=True)

        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.configure(bg=PRIMARY, fg="white")
            else:
                btn.configure(bg=BG, fg=TEXT)

        self.btn_prev.configure(state="normal" if index > 0 else "disabled")

        if index == len(self._pages_list) - 1:
            self.btn_next.pack_forget()
        else:
            self.btn_next.pack(side="right")

        can_proceed = self.preflight["passed"]
        if not can_proceed and index == 0:
            self.btn_next.configure(state="disabled")
        else:
            self.btn_next.configure(state="normal")

    def _go_to(self, index):
        if index < self.current_index:
            self._show_page(index)
        elif index == self.current_index + 1:
            self._next()

    def _next(self):
        page = self._pages_list[self.current_index]
        ok, error = page.collect()
        if not ok:
            messagebox.showwarning("输入错误", error, parent=self.root)
            return
        if self.current_index < len(self._pages_list) - 1:
            self._show_page(self.current_index + 1)

    def _prev(self):
        if self.current_index > 0:
            self._show_page(self.current_index - 1)

    def _execute(self):
        page = self._pages_list[-1]
        ok, error = page.collect()
        if not ok:
            messagebox.showwarning("配置错误", error, parent=self.root)
            return
        if self.on_finish:
            self.on_finish(self.config)
        self.root.destroy()

    def run(self):
        self.root.mainloop()