"""窗口操作 — Windows(pywin32 真透明) / Linux(wmctrl colorkey)"""
import sys
import subprocess

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import ctypes

    def get_hwnd(pygame_display):
        return pygame_display.get_wm_info()["window"]

    def make_transparent(hwnd, color=(0, 0, 0)):
        """设置分层窗口 + 指定颜色透明（真透明）"""
        # 添加 WS_EX_LAYERED (0x80000)
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000)
        # 黑色 → 透明
        color_key = (color[2] << 16) | (color[1] << 8) | color[0]
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, color_key, 0, 0x00000001)

    def set_topmost(hwnd):
        ctypes.windll.user32.SetWindowPos(
            hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002
        )

    def move_to(hwnd, x, y):
        # 全屏窗口不需要移动
        pass

    def set_round_clip(hwnd, cx, cy, r):
        # pywin32 方案不需要裁剪
        pass

    def set_rect_clip(hwnd, x, y, w, h):
        pass

else:
    # Linux / WSL
    def get_hwnd(pygame_display):
        return None

    def make_transparent(hwnd, color=None):
        pass

    def set_topmost(hwnd):
        try:
            subprocess.run(
                ["wmctrl", "-r", "桌宠", "-b", "add,above"],
                capture_output=True, timeout=1
            )
        except Exception:
            pass

    def move_to(hwnd, x, y):
        try:
            subprocess.run(
                ["wmctrl", "-r", "桌宠", "-e", f"0,{x},{y},-1,-1"],
                capture_output=True, timeout=1
            )
        except Exception:
            pass

    def set_round_clip(hwnd, cx, cy, r):
        pass

    def set_rect_clip(hwnd, x, y, w, h):
        pass
