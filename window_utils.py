"""窗口操作 — Windows(ctypes) / Linux(wmctrl) 双平台兼容"""
import sys
import subprocess

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import ctypes

    def get_hwnd(pygame_display):
        """从 pygame 窗口获取 Windows 句柄"""
        return pygame_display.get_wm_info()["window"]

    def set_topmost(hwnd):
        """窗口置顶"""
        ctypes.windll.user32.SetWindowPos(
            hwnd, -1, 0, 0, 0, 0,
            0x0001 | 0x0002  # SWP_NOSIZE | SWP_NOMOVE
        )

    def move_to(hwnd, x, y):
        """移动窗口到绝对位置"""
        ctypes.windll.user32.SetWindowPos(
            hwnd, 0, x, y, 0, 0,
            0x0001 | 0x0004  # SWP_NOSIZE | SWP_NOZORDER
        )

    def set_round_clip(hwnd, cx, cy, r):
        """裁剪窗口为圆形"""
        hrgn = ctypes.windll.gdi32.CreateEllipticRgn(
            int(cx - r), int(cy - r),
            int(cx + r), int(cy + r)
        )
        ctypes.windll.user32.SetWindowRgn(hwnd, hrgn, True)

    def set_rect_clip(hwnd, x, y, w, h):
        """裁剪窗口为矩形"""
        hrgn = ctypes.windll.gdi32.CreateRectRgn(x, y, x + w, y + h)
        ctypes.windll.user32.SetWindowRgn(hwnd, hrgn, True)

else:
    # Linux / WSL

    def get_hwnd(pygame_display):
        return None  # Linux 下不需要句柄

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
        pass  # Linux 不支持，依靠 colorkey 透明

    def set_rect_clip(hwnd, x, y, w, h):
        pass  # Linux 不支持
