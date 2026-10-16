import queue
import threading
import sys
import tkinter as tk
from tkinter import ttk, messagebox

from core.version import APP_NAME, DISPLAY_VERSION as VERSION
from gui.styles import BG, CARD_BG, PRIMARY, TEXT, FONT_BUTTON, FONT_STRONG, setup_fonts
from gui.page_welcome import WelcomePage
from gui.page_basic import BasicPage
from gui.page_locale import LocalePage
from gui.page_oobe import OOBEPage
from gui.page_account import AccountPage
from gui.page_confirm import ConfirmPage


class SysprepWizardApp:
    LABELS = ("1. 环境检测", "2. 基本设置", "3. 区域设置", "4. OOBE", "5. 账户", "6. 确认")

    def __init__(self, context, preflight_result, config, on_finish=None, visible=True):
        self.context = context
        self.preflight = preflight_result
        self.config = config
        self.on_finish = on_finish
        self.current_index = 0
        self.request_tui = False
        self.busy = False
        self.execution_started = False
        self._results = queue.Queue()
        self._worker_thread = None
        self.root = tk.Tk()
        try:
            if not visible:
                self.root.withdraw()
            self.root.title(getattr(context, "interface_title", "{} {}".format(APP_NAME, VERSION)))
            self.font_family = setup_fonts(self.root)
            self.root.configure(bg=BG)
            self.root.minsize(680, 440)
            width = min(820, max(680, self.root.winfo_screenwidth() - 60))
            height = min(760, max(440, self.root.winfo_screenheight() - 100))
            x = max(0, (self.root.winfo_screenwidth() - width) // 2)
            y = max(0, (self.root.winfo_screenheight() - height) // 2)
            self.root.geometry("{}x{}+{}+{}".format(width, height, x, y))
            self._setup_styles()
            self._build_ui()
            self._show_page(0)
            self.root.bind("<F8>", self._switch_to_tui)
            self.root.bind("<MouseWheel>", self._scroll)
            self.root.protocol("WM_DELETE_WINDOW", self._close)
        except Exception:
            self.root.destroy()
            raise

    def _setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        for name in ("Page.TFrame", "Header.TFrame", "TFrame"):
            style.configure(name, background=CARD_BG)
        style.configure("TLabelFrame", background=CARD_BG, foreground=TEXT)
        style.configure("TLabelFrame.Label", background=CARD_BG, foreground=TEXT,
                        font=FONT_STRONG)
        for name in ("TCheckbutton", "TRadiobutton"):
            style.configure(name, background=CARD_BG)

    def _build_ui(self):
        nav = tk.Frame(self.root, bg=BG)
        nav.pack(fill="x", padx=12, pady=12)
        self.nav_buttons = []
        for index, label in enumerate(self.LABELS):
            button = tk.Button(nav, text=label, font=FONT_BUTTON, bg=BG, fg=TEXT,
                               relief="flat", cursor="hand2", padx=6, pady=4,
                               command=lambda i=index: self._go_to(i))
            button.pack(side="left", padx=1)
            self.nav_buttons.append(button)
        bottom = tk.Frame(self.root, bg=BG)
        bottom.pack(side="bottom", fill="x", padx=16, pady=12)
        self.btn_prev = tk.Button(bottom, text="← 上一步", font=FONT_BUTTON, command=self._prev)
        self.btn_prev.pack(side="left")
        self.btn_tui = tk.Button(bottom, text="F8 · 文本模式", font=FONT_BUTTON, command=self._switch_to_tui)
        self.btn_tui.pack(side="left", padx=12)
        self.btn_next = tk.Button(bottom, text="下一步 →", font=FONT_BUTTON,
                                  bg=PRIMARY, fg="white", command=self._next)
        self.btn_next.pack(side="right")
        viewport = tk.Frame(self.root, bg=CARD_BG)
        viewport.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(viewport, bg=CARD_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(viewport, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.page_container = tk.Frame(self.canvas, bg=CARD_BG)
        self._canvas_window = self.canvas.create_window((0, 0), window=self.page_container, anchor="nw")
        self.page_container.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda event: self.canvas.itemconfigure(self._canvas_window, width=event.width))
        self._pages_list = [
            WelcomePage(self.page_container, self.context, self.preflight),
            BasicPage(self.page_container, self.config),
            LocalePage(self.page_container, self.config),
            OOBEPage(self.page_container, self.config, self.context),
            AccountPage(self.page_container, self.config),
            ConfirmPage(self.page_container, self.config, self.context, on_execute=self._execute),
        ]

    def _scroll(self, event):
        if event.delta:
            self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def _show_page(self, index):
        for page in self._pages_list:
            page.pack_forget()
        self.current_index = index
        page = self._pages_list[index]
        page.refresh()
        page.pack(fill="both", expand=True)
        self.canvas.yview_moveto(0)
        for i, button in enumerate(self.nav_buttons):
            button.configure(bg=PRIMARY if i == index else BG, fg="white" if i == index else TEXT)
        self.btn_prev.configure(state="normal" if index > 0 else "disabled")
        if index == len(self._pages_list) - 1:
            self.btn_next.pack_forget()
        else:
            self.btn_next.pack(side="right")
        self.btn_next.configure(state="normal" if self.preflight["passed"] else "disabled")

    def _save_current(self):
        ok, error = self._pages_list[self.current_index].collect()
        if not ok:
            messagebox.showwarning("输入错误", error, parent=self.root)
        return ok

    def _go_to(self, index):
        if self.busy or self.execution_started:
            return
        if index <= self.current_index + 1 and index != self.current_index:
            if index > self.current_index and not self.preflight["passed"]:
                return
            if self._save_current():
                self._show_page(index)

    def _next(self):
        if self.current_index < len(self._pages_list) - 1:
            self._go_to(self.current_index + 1)

    def _prev(self):
        if self.current_index > 0:
            self._go_to(self.current_index - 1)

    def _switch_to_tui(self, event=None):
        if not self.busy and not self.execution_started and self._save_current():
            self.request_tui = True
            self.root.destroy()
        return "break"

    def _close(self):
        if self.busy:
            messagebox.showinfo("正在执行", "请等待执行完成。", parent=self.root)
        else:
            self.root.destroy()

    def _set_busy(self):
        for button in self.nav_buttons + [self.btn_prev, self.btn_next, self.btn_tui]:
            button.configure(state="disabled")
        self._pages_list[-1].btn_execute.configure(state="disabled")

    def _execute(self):
        if self.busy or self.execution_started or self.current_index != len(self._pages_list) - 1:
            return
        if not self._save_current():
            return
        if not self.preflight["passed"]:
            messagebox.showerror("环境未通过", "请修复预检问题后重新运行。", parent=self.root)
            return
        if not self.config.test_only:
            background_note = ("\nWin11 多系统封装由当前管理员的独立进程执行；请勿注销或手动重启。"
                               if self.context.family == "Windows 11" and getattr(sys, "_jy_worker_capable", False) else "")
            if not messagebox.askyesno(
                "确认正式封装", "将执行 Sysprep /generalize /{}，完成后{}。\n将备份 BCD；多系统环境会先核对当前引导再执行完成动作。{}\n是否继续？".format(
                    self.config.mode, {"shutdown": "关机", "reboot": "重启", "quit": "退出"}[self.config.completion_action], background_note),
                default="no", parent=self.root,
            ):
                return
        self.busy = True
        self.execution_started = True
        self._set_busy()
        self._pages_list[-1].set_status("正在执行，请稍候……")

        def worker():
            try:
                result = self.on_finish(self.config) if self.on_finish else None
                self._results.put((True, result))
            except Exception as error:
                self._results.put((False, str(error)))

        # A disappearing GUI must not abandon Sysprep's BCD/power continuation.
        self._worker_thread = threading.Thread(target=worker, daemon=False)
        self._worker_thread.start()
        self.root.after(100, self._poll_result)

    def _poll_result(self):
        try:
            success, result = self._results.get_nowait()
        except queue.Empty:
            self.root.after(100, self._poll_result)
            return
        self.busy = False
        if success:
            message = "测试应答文件已生成：\n{}".format(result or "请查看控制台输出") if self.config.test_only else "Sysprep 已返回，详细信息请查看日志。"
            self._pages_list[-1].set_status(message)
            messagebox.showinfo("执行完成", message, parent=self.root)
        else:
            message = "执行失败：{}\n请查看控制台或桌面的 JY Sysprep Logs。\n请排查后重新运行程序。".format(result)
            self._pages_list[-1].set_status(message)
            messagebox.showerror("执行失败", message, parent=self.root)

    def run(self):
        try:
            self.root.mainloop()
        finally:
            if self._worker_thread is not None:
                self._worker_thread.join()
