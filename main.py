"""桌宠入口 — Tkinter 原生透明窗口 + 右键菜单 + Hermes 联动"""
import sys
import random
import subprocess
import threading
import tkinter as tk
from tkinter import Menu as TkMenu
from config import (
    IS_WINDOWS, IS_MAC,
    FRAME_MS, FONT, FONT_SMALL, WHITE,
)
from pet import Pet


class DesktopPet:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("桌宠")

        # 屏幕尺寸
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        # 透明全屏窗口
        self.root.overrideredirect(True)
        self.root.geometry(f"{self.screen_w}x{self.screen_h}+0+0")
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')

        # Windows: 用 transparentcolor 让黑色透明
        if IS_WINDOWS:
            self.root.wm_attributes('-transparentcolor', 'black')
        elif IS_MAC:
            self.root.attributes('-transparent', True)

        # 隐藏窗口到任务栏（可选）
        self.root.withdraw()  # 先隐藏
        self.root.after(100, self.root.deiconify)

        # Canvas
        self.canvas = tk.Canvas(
            self.root, bg='black', highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)

        # 宠物
        self.pet = Pet(self.canvas, self.screen_w // 2, self.screen_h // 2)

        # 对话气泡
        self.bubble_items = []
        self.bubble_timer = None

        # 右键菜单
        self.context_menu = TkMenu(self.root, tearoff=0, font=FONT_SMALL)
        self.context_menu.add_command(label="讲个笑话", command=self._tell_joke)
        self.context_menu.add_command(label="你在干嘛？", command=self._what_doing)
        self.context_menu.add_command(
            label="问 AI：今天学什么？", command=self._ask_ai_study
        )
        self.context_menu.add_command(
            label="问 AI：随机小知识", command=self._ask_ai_fact
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(label="退出", command=self._quit)

        # 拖拽状态
        self.dragging = False
        self.drag_start_time = 0
        self.drag_start_x = 0
        self.drag_start_y = 0

        # 绑定事件
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<ButtonPress-3>", self._on_right_click)

        # 键盘退出
        self.root.bind("<Escape>", lambda e: self._quit())

        # 游戏循环
        self._last_time = 0
        self._game_loop()

    # ── 事件处理 ──

    def _on_press(self, event):
        if self.pet.contains(event.x, event.y):
            self.dragging = True
            self.drag_start_time = event.time
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.pet.start_drag(event.x, event.y)

    def _on_drag(self, event):
        if self.dragging:
            self.pet.update_drag(event.x, event.y)

    def _on_release(self, event):
        if self.dragging:
            self.dragging = False
            moved = abs(event.x - self.drag_start_x) + abs(event.y - self.drag_start_y)
            if moved < 5 and event.time - self.drag_start_time < 300:
                self.pet.handle_click()
            self.pet.end_drag()

    def _on_right_click(self, event):
        if self.pet.contains(event.x, event.y):
            self.context_menu.tk_popup(event.x_root, event.y_root)

    # ── 菜单动作 ──

    def _tell_joke(self):
        jokes = [
            "为什么 Oct 31 == Dec 25？\n程序员懂的...",
            "SQL 走进酒吧：我能 JOIN 吗？",
            "bug 不叫 bug，叫特性。",
        ]
        self._show_bubble(random.choice(jokes), 3000)

    def _what_doing(self):
        msgs = {
            "walking": "溜达溜达~ 🚶",
            "idle": "发呆中 💤",
        }
        if self.pet.expression == "bored":
            msg = "好无聊…… 😑"
        else:
            msg = msgs.get(self.pet.state, "发呆中 💤")
        self._show_bubble(msg, 3000)

    def _ask_ai_study(self):
        self._ask_hermes("我是Java初学者，今天应该学什么？给简短建议")

    def _ask_ai_fact(self):
        self._ask_hermes("有趣的编程冷知识，简短")

    def _ask_hermes(self, question):
        self._show_bubble("🤔 思考中...", 30000)
        def _run():
            try:
                result = subprocess.run(
                    ["hermes", "chat", "-q", question, "-Q"],
                    capture_output=True, text=True, timeout=30,
                    cwd="/home/luochuan" if not IS_WINDOWS else None,
                )
                answer = result.stdout.strip()
                if "session_id:" in answer:
                    answer = answer.split("\n", 1)[-1].strip()
                self.root.after(0, lambda: self._show_bubble(
                    answer if answer else "😅 没回答上来...", 10000
                ))
            except Exception:
                self.root.after(0, lambda: self._show_bubble("❌ 调用失败", 3000))
        threading.Thread(target=_run, daemon=True).start()

    def _show_bubble(self, text, duration_ms):
        """显示对话气泡"""
        self._clear_bubble()
        x = self.pet.x
        y = self.pet.y - self.pet.r - 10

        # 文字
        lines = text.split("\n")
        font = FONT
        # 创建文字
        text_ids = []
        max_w = 0
        total_h = 0
        for line in lines:
            tid = self.canvas.create_text(
                0, 0, text=line, font=font, fill="black", anchor="nw"
            )
            bbox = self.canvas.bbox(tid)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            max_w = max(max_w, w)
            total_h += h
            text_ids.append((tid, w, h))

        pad = 8
        bw = max_w + pad * 2
        bh = total_h + pad * 2
        bx = x - bw // 2
        by = y - bh

        # 气泡背景
        bg_id = self.canvas.create_rectangle(
            bx, by, bx + bw, by + bh,
            fill=WHITE, outline="black", width=1
        )
        self.bubble_items.append(bg_id)

        # 小三角
        tri = self.canvas.create_polygon(
            x, y + 3, x - 6, by + bh, x + 6, by + bh,
            fill=WHITE, outline="black"
        )
        self.bubble_items.append(tri)

        # 文字
        cy = by + pad
        for tid, w, h in text_ids:
            self.canvas.coords(tid, bx + pad, cy)
            self.bubble_items.append(tid)
            cy += h

        # 定时清除
        if self.bubble_timer:
            self.root.after_cancel(self.bubble_timer)
        self.bubble_timer = self.root.after(duration_ms, self._clear_bubble)

    def _clear_bubble(self):
        for item_id in self.bubble_items:
            self.canvas.delete(item_id)
        self.bubble_items.clear()
        self.bubble_timer = None

    def _quit(self):
        self.root.destroy()
        sys.exit(0)

    # ── 游戏循环 ──

    def _game_loop(self):
        now = self._now_ms()
        if not self.dragging:
            self.pet.update(now)
        self.root.after(FRAME_MS, self._game_loop)

    def _now_ms(self):
        import time
        return int(time.time() * 1000)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = DesktopPet()
    app.run()
