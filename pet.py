"""宠物实体 — 状态机、呼吸、游走、拖拽、点击"""
import random
import math
import pygame
from config import (
    PET_RADIUS, PET_COLOR,
    SCREEN_W, SCREEN_H, FPS,
    WALK_SPEED, IDLE_MIN, IDLE_MAX,
    BREATHE_SPEED, BREATHE_MIN, BREATHE_MAX,
)


class Pet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = PET_RADIUS
        self.color = PET_COLOR

        # 状态机
        self.state = "idle"          # idle | walking | clicked
        self.idle_timer = random.randint(IDLE_MIN, IDLE_MAX)
        self.breathe_phase = 0.0     # 呼吸相位（正弦波）
        self.scale = 1.0

        # 表情
        self.expression = "normal"    # normal | happy | bored
        self.total_idle = 0           # 累计 idle 帧数（用于判断无聊）

        # 游走
        self.target_x = x
        self.target_y = y

        # 点击弹跳
        self.click_timer = 0

        # 拖拽
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    # ── 公开方法 ──────────────────────────────

    def update(self):
        """每帧更新"""
        # 拖拽中不自动更新
        if self.dragging:
            return

        # 累计 idle 时间
        if self.state == "idle":
            self.total_idle += 1
        else:
            self.total_idle = 0

        if self.state == "clicked":
            self._update_clicked()
        elif self.state == "walking":
            self._update_walking()
        elif self.state == "idle":
            self._update_idle()

        self._update_expression()

    def draw(self, screen):
        """绘制"""
        r = int(self.radius * self.scale)
        cx, cy = int(self.x), int(self.y)
        pygame.draw.circle(screen, self.color, (cx, cy), r)

        # 根据表情画眼睛
        eye_y = int(cy - r * 0.15)
        if self.expression == "normal":
            self._draw_normal_eyes(screen, cx, eye_y, r)
        elif self.expression == "happy":
            self._draw_happy_eyes(screen, cx, eye_y, r)
        elif self.expression == "bored":
            self._draw_bored_eyes(screen, cx, eye_y, r)

    def _draw_normal_eyes(self, screen, cx, eye_y, r):
        """正常圆眼"""
        offset = r // 3
        radius = max(1, r // 5)
        pygame.draw.circle(screen, (0, 0, 0), (cx - offset, eye_y), radius)
        pygame.draw.circle(screen, (0, 0, 0), (cx + offset, eye_y), radius)

    def _draw_happy_eyes(self, screen, cx, eye_y, r):
        """开心眼 — 倒U弧线"""
        offset = r // 3
        arc_r = r // 4
        # 左眼：画上半圆弧（从 180° 到 360° = 倒 U）
        rect1 = pygame.Rect(cx - offset - arc_r, eye_y - arc_r, arc_r * 2, arc_r * 2)
        pygame.draw.arc(screen, (0, 0, 0), rect1, math.pi, 2 * math.pi, max(1, r // 8))
        rect2 = pygame.Rect(cx + offset - arc_r, eye_y - arc_r, arc_r * 2, arc_r * 2)
        pygame.draw.arc(screen, (0, 0, 0), rect2, math.pi, 2 * math.pi, max(1, r // 8))

    def _draw_bored_eyes(self, screen, cx, eye_y, r):
        """无聊眼 — 半圆（上半实心 = 眼睛半闭）"""
        offset = r // 3
        radius = max(1, r // 4)
        # 画上半部分的半圆
        for ex in [cx - offset, cx + offset]:
            rect = pygame.Rect(ex - radius, eye_y - radius, radius * 2, radius * 2)
            pygame.draw.arc(screen, (0, 0, 0), rect, math.pi, 2 * math.pi, max(1, r // 7))

    def _update_expression(self):
        """根据状态更新表情"""
        if self.state == "clicked":
            self.expression = "happy"
        elif self.state == "idle" and self.total_idle > FPS * 5:  # 发呆超过5秒
            self.expression = "bored"
        else:
            self.expression = "normal"

    def handle_click(self):
        self.state = "clicked"
        self.click_timer = 10
        self.scale = 1.3

    def start_drag(self, mouse_x, mouse_y):
        self.dragging = True
        self.drag_start_x = self.x
        self.drag_start_y = self.y
        self.drag_offset_x = self.x - mouse_x
        self.drag_offset_y = self.y - mouse_y
        # 打断自动行为
        self.state = "idle"
        self.idle_timer = random.randint(IDLE_MIN, IDLE_MAX)

    def update_drag(self, mouse_x, mouse_y):
        if self.dragging:
            self.x = mouse_x + self.drag_offset_x
            self.y = mouse_y + self.drag_offset_y

    def end_drag(self):
        if not self.dragging:
            return
        moved = abs(self.x - self.drag_start_x) + abs(self.y - self.drag_start_y)
        if moved < 5:
            self.handle_click()
        self.dragging = False

    # ── 内部状态更新 ──────────────────────────

    def _update_idle(self):
        # 呼吸效果
        self.breathe_phase += BREATHE_SPEED
        self.scale = BREATHE_MIN + (BREATHE_MAX - BREATHE_MIN) * (
            0.5 + 0.5 * math.sin(self.breathe_phase)
        )
        # 倒计时，到时 → 游走
        self.idle_timer -= 1
        if self.idle_timer <= 0:
            self._start_walking()

    def _start_walking(self):
        """随机选一个目标位置开始走"""
        # 确保目标离当前位置有一定距离
        margin = self.radius + 10
        self.target_x = random.uniform(margin, SCREEN_W - margin)
        self.target_y = random.uniform(margin, SCREEN_H - margin)
        self.state = "walking"

    def _update_walking(self):
        # 向目标移动
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        if dist < 1:
            # 到达 → 回到待机
            self.x = self.target_x
            self.y = self.target_y
            self.state = "idle"
            self.idle_timer = random.randint(IDLE_MIN, IDLE_MAX)
        else:
            speed = WALK_SPEED
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed
            # 游走时微微缩放（无呼吸）
            self.scale = 1.0

    def _update_clicked(self):
        self.click_timer -= 1
        self.scale = 1.0 + 0.3 * (self.click_timer / 10)
        if self.click_timer <= 0:
            self.state = "idle"
            self.scale = 1.0
            self.idle_timer = random.randint(IDLE_MIN, IDLE_MAX)
