"""宠物实体 — Tkinter Canvas 绘制 + 状态机"""
import random
import math
from config import PET_SIZE, PET_COLOR, WALK_SPEED, IDLE_MIN_MS, IDLE_MAX_MS


class Pet:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = PET_SIZE
        self.r = self.size // 2

        # 状态机
        self.state = "idle"
        self.idle_until = 0
        self.breathe_phase = 0.0
        self.scale = 1.0

        # 表情
        self.expression = "normal"
        self.idle_start_time = 0

        # 游走
        self.target_x = x
        self.target_y = y

        # 点击
        self.click_until = 0

        # 画布元素 ID
        self.body_id = None
        self.left_eye_id = None
        self.right_eye_id = None

        self._draw()

    def _draw(self):
        """在 Canvas 上绘制宠物"""
        r = int(self.r * self.scale)
        cx, cy = int(self.x), int(self.y)

        # 身体
        if self.body_id:
            self.canvas.coords(self.body_id, cx - r, cy - r, cx + r, cy + r)
        else:
            self.body_id = self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=PET_COLOR, outline="", tags="pet"
            )

        # 眼睛
        eye_y = int(cy - r * 0.15)
        self._draw_eyes(cx, eye_y, r)

    def _draw_eyes(self, cx, eye_y, r):
        offset = r // 3
        er = max(1, r // 5)

        if self.expression == "happy":
            # 倒 U 弧线
            arc_r = r // 4
            for ex, tag in [(cx - offset, "lefteye"), (cx + offset, "righteye")]:
                eid = getattr(self, f"{tag}_id", None)
                coords = (ex - arc_r, eye_y - arc_r, ex + arc_r, eye_y + arc_r)
                if eid:
                    self.canvas.coords(eid, *coords)
                else:
                    eid = self.canvas.create_arc(
                        *coords, start=0, extent=180,
                        style="arc", outline="black", width=max(1, r // 7),
                        tags="pet"
                    )
                    setattr(self, f"{tag}_id", eid)
        else:
            # 实心圆
            for ex, tag in [(cx - offset, "lefteye"), (cx + offset, "righteye")]:
                eid = getattr(self, f"{tag}_id", None)
                coords = (ex - er, eye_y - er, ex + er, eye_y + er)
                if eid:
                    self.canvas.coords(eid, *coords)
                    self.canvas.itemconfig(eid, fill="black", outline="")
                else:
                    eid = self.canvas.create_oval(
                        *coords, fill="black", outline="", tags="pet"
                    )
                    setattr(self, f"{tag}_id", eid)

    def update(self, now):
        """根据时间戳更新状态"""
        if self.state == "clicked":
            self._update_clicked(now)
        elif self.state == "walking":
            self._update_walking()
        elif self.state == "idle":
            self._update_idle(now)

        self._update_expression(now)
        self._draw()

    def _update_idle(self, now):
        self.breathe_phase += 0.02
        self.scale = 0.95 + 0.05 * (0.5 + 0.5 * math.sin(self.breathe_phase))
        if now >= self.idle_until:
            self._start_walking()

    def _start_walking(self):
        screen_w = self.canvas.winfo_screenwidth()
        screen_h = self.canvas.winfo_screenheight()
        margin = self.r + 20
        self.target_x = random.uniform(margin, screen_w - margin)
        self.target_y = random.uniform(margin, screen_h - margin)
        self.state = "walking"
        self.scale = 1.0

    def _update_walking(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        if dist < 2:
            self.x = self.target_x
            self.y = self.target_y
            self.state = "idle"
            self.idle_start_time = 0  # 重置累计 idle
            self.idle_until = self._now() + random.randint(IDLE_MIN_MS, IDLE_MAX_MS)
        else:
            self.x += (dx / dist) * WALK_SPEED
            self.y += (dy / dist) * WALK_SPEED

    def _update_clicked(self, now):
        elapsed = self.click_until - now
        progress = max(0, elapsed / 300)
        self.scale = 1.0 + 0.3 * progress
        if now >= self.click_until:
            self.state = "idle"
            self.scale = 1.0
            self.idle_until = now + random.randint(IDLE_MIN_MS, IDLE_MAX_MS)

    def _update_expression(self, now):
        if self.state == "clicked":
            self.expression = "happy"
        elif self.state == "idle":
            if self.idle_start_time == 0:
                self.idle_start_time = now
            if now - self.idle_start_time > 5000:
                self.expression = "bored"
            else:
                self.expression = "normal"
        else:
            self.expression = "normal"

    def _now(self):
        """获取当前时间戳（毫秒），由外部传入 now 参数更好"""
        import time
        return int(time.time() * 1000)

    def handle_click(self):
        now = self._now()
        self.state = "clicked"
        self.click_until = now + 300
        self.scale = 1.3

    def start_drag(self, mouse_x, mouse_y):
        self.drag_offset_x = self.x - mouse_x
        self.drag_offset_y = self.y - mouse_y

    def update_drag(self, mouse_x, mouse_y):
        self.x = mouse_x + self.drag_offset_x
        self.y = mouse_y + self.drag_offset_y
        screen_w = self.canvas.winfo_screenwidth()
        screen_h = self.canvas.winfo_screenheight()
        self.x = max(self.r, min(screen_w - self.r, self.x))
        self.y = max(self.r, min(screen_h - self.r, self.y))
        self._draw()

    def end_drag(self):
        self.state = "idle"
        self.idle_start_time = 0
        self.idle_until = self._now() + random.randint(IDLE_MIN_MS, IDLE_MAX_MS)

    def contains(self, mx, my):
        """检查点是否在宠物范围内"""
        return math.hypot(mx - self.x, my - self.y) <= self.r + 5
