BG = "#f0f0f0"
CARD_BG = "#ffffff"
PRIMARY = "#0078d4"
PRIMARY_HOVER = "#106ebe"
DANGER = "#d13438"
SUCCESS = "#107c10"
WARNING = "#ff8c00"
TEXT = "#333333"
TEXT_SECONDARY = "#666666"
BORDER = "#cccccc"

# Shared lists let pages imported before Tk starts use the detected font family.
FONT_TITLE = ["Microsoft YaHei UI", 16, "bold"]
FONT_SUBTITLE = ["Microsoft YaHei UI", 11]
FONT_BODY = ["Microsoft YaHei UI", 10]
FONT_SMALL = ["Microsoft YaHei UI", 9]
FONT_BUTTON = ["Microsoft YaHei UI", 10]
FONT_STRONG = ["Microsoft YaHei UI", 10, "bold"]
FONT_ACTION = ["Microsoft YaHei UI", 11, "bold"]


def setup_fonts(root):
    from tkinter import font
    available = set(font.families(root))
    family = next((name for name in ("Microsoft YaHei UI", "Microsoft YaHei", "Segoe UI")
                   if name in available), root.tk.call("font", "actual", "TkDefaultFont", "-family"))
    for spec in (FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_SMALL, FONT_BUTTON, FONT_STRONG, FONT_ACTION):
        spec[0] = family
    return family
