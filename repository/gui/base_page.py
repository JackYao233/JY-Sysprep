import tkinter as tk
from tkinter import ttk

from gui.styles import BG, CARD_BG, FONT_TITLE, FONT_SUBTITLE, TEXT, TEXT_SECONDARY, BORDER


class BasePage(ttk.Frame):
    def __init__(self, parent, title, subtitle=""):
        super().__init__(parent, style="Page.TFrame")
        self._title = title
        self._subtitle = subtitle
        self._build_header()

    def _build_header(self):
        header = ttk.Frame(self, style="Header.TFrame")
        header.pack(fill="x", padx=24, pady=(20, 0))

        title_lbl = tk.Label(
            header, text=self._title,
            font=FONT_TITLE, bg=CARD_BG, fg=TEXT, anchor="w"
        )
        title_lbl.pack(fill="x")

        if self._subtitle:
            sub_lbl = tk.Label(
                header, text=self._subtitle,
                font=FONT_SUBTITLE, bg=CARD_BG, fg=TEXT_SECONDARY, anchor="w"
            )
            sub_lbl.pack(fill="x", pady=(4, 0))

        sep = ttk.Separator(self, orient="horizontal")
        sep.pack(fill="x", padx=24, pady=(12, 0))

    def create_section(self, parent, label_text):
        frame = ttk.LabelFrame(parent, text=label_text, padding=12)
        frame.pack(fill="x", padx=24, pady=(12, 0))
        return frame

    def add_row(self, parent, label_text, widget, pady=4):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=pady)
        lbl = tk.Label(row, text=label_text, font=("Microsoft YaHei UI", 10),
                        bg=CARD_BG, fg=TEXT, width=22, anchor="w")
        lbl.pack(side="left")
        widget.pack(side="left", fill="x", expand=True)
        return row