import tkinter as tk
from tkinter import ttk

from gui.base_page import BasePage
from gui.styles import CARD_BG, TEXT, FONT_BODY


LOCALE_PRESETS = {
    "中文（简体）": ("zh-CN", "zh-CN", "zh-CN", "zh-CN"),
    "English (US)": ("en-US", "en-US", "en-US", "en-US"),
    "自定义": None,
}


class LocalePage(BasePage):
    def __init__(self, parent, config):
        super().__init__(parent, "区域设置", "配置语言和区域")
        self.config = config
        self._build_content()

    def _build_content(self):
        container = tk.Frame(self, bg=CARD_BG)
        container.pack(fill="both", expand=True, padx=24, pady=16)

        preset_section = self.create_section(container, "语言预设")
        self.var_preset = tk.StringVar(value="中文（简体）")
        for name in LOCALE_PRESETS:
            ttk.Radiobutton(preset_section, text=name, variable=self.var_preset,
                            value=name, command=self._on_preset_change).pack(anchor="w", pady=2)

        detail_section = self.create_section(container, "详细设置")
        self.var_input = tk.StringVar(value=self.config.input_locale)
        self.var_system = tk.StringVar(value=self.config.system_locale)
        self.var_ui = tk.StringVar(value=self.config.ui_language)
        self.var_user = tk.StringVar(value=self.config.user_locale)

        self.entry_input = self._add_locale_row(detail_section, "输入法区域：", self.var_input)
        self.entry_system = self._add_locale_row(detail_section, "系统区域：", self.var_system)
        self.entry_ui = self._add_locale_row(detail_section, "显示语言：", self.var_ui)
        self.entry_user = self._add_locale_row(detail_section, "用户区域：", self.var_user)

        self._on_preset_change()

    def _add_locale_row(self, parent, label, var):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label, font=FONT_BODY, bg=CARD_BG, fg=TEXT, width=12, anchor="w").pack(side="left")
        entry = ttk.Entry(row, textvariable=var, width=20)
        entry.pack(side="left", padx=(8, 0))
        return entry

    def _on_preset_change(self):
        preset = LOCALE_PRESETS.get(self.var_preset.get())
        state = "normal" if preset is None else "disabled"
        for entry in (self.entry_input, self.entry_system, self.entry_ui, self.entry_user):
            entry.configure(state=state)
        if preset:
            self.var_input.set(preset[0])
            self.var_system.set(preset[1])
            self.var_ui.set(preset[2])
            self.var_user.set(preset[3])

    def collect(self):
        self.config.input_locale = self.var_input.get().strip() or "zh-CN"
        self.config.system_locale = self.var_system.get().strip() or "zh-CN"
        self.config.ui_language = self.var_ui.get().strip() or "zh-CN"
        self.config.user_locale = self.var_user.get().strip() or "zh-CN"
        return True, None