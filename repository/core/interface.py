import argparse
import sys
import time


def select_interface(argv=None, timeout=2.0):
    parser = argparse.ArgumentParser(description="JY Sysprep GUI / TUI")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--tui", action="store_true", help="直接进入文本向导")
    modes.add_argument("--gui", action="store_true", help="直接进入图形向导")
    args = parser.parse_args(argv)
    if args.tui:
        return "tui"
    if args.gui:
        return "gui"
    if sys.platform == "win32" and sys.stdin.isatty():
        import msvcrt
        print("默认启动图形向导，2 秒内按 F8 进入文本向导（GUI 中也可按 F8）。", flush=True)
        deadline = time.monotonic() + timeout
        extended = False
        while time.monotonic() < deadline:
            if msvcrt.kbhit():
                key = msvcrt.getwch()
                if extended:
                    if key == "B":  # Windows console F8 scan code
                        return "tui"
                    extended = False
                else:
                    extended = key in ("\x00", "\xe0")
            time.sleep(0.02)
    return "gui"


def create_gui(context, preflight, config, on_finish):
    # Keep TUI usable on Python installations without Tkinter.
    from gui.app import SysprepWizardApp
    from tkinter import TclError
    try:
        return SysprepWizardApp(context, preflight, config, on_finish=on_finish)
    except TclError as error:
        raise RuntimeError("无法初始化 Tk 图形界面：{}".format(error)) from error
