"""宠物实体 — 状态机、呼吸、游走、拖拽"""
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
        self.state = "idle"
        self.idle_timer = random.randint(IDLE_MIN, IDLE_MAX)
        self.breathe_phase = 0.0
        self.scale = 1.0

        # 表情
        self.expression = "normal"
        self.total_idle = 0

        # 游走目标（屏幕坐标）
        self.target_x = x
        self.target_y = y

        # 点击弹跳
        self.click_timer = 0

        # 拖拽
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def update(self):
        if self.dragging:
            return

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
        r = int(self.radius * self.scale)
        cx, cy = int(self.x), int(self.y)
        pygame.draw.circle(screen, self.color, (cx, cy), r)

        eye_y = int(cy - r * 0.15)
        if self.expression == "normal":
            self._draw_normal_eyes(screen, cx, eye_y, r)
        elif self.expression == "happy":
            self._draw_happy_eyes(screen, cx, eye_y, r)
        elif self.expression == "bored":
            self._draw_bored_eyes(screen, cx, eye_y, r)

    def _draw_normal_eyes(self, screen, cx, eye_y, r):
        offset = r // 3
        radius = max(1, r // 5)
        pygame.draw.circle(screen, (0, 0, 0), (cx - offset, eye_y), radius)
        pygame.draw.circle(screen, (0, 0, 0), (cx + offset, eye_y), radius)

    def _draw_happy_eyes(self, screen, cx, eye_y, r):
        offset = r // 3
        arc_r = r // 4
        rect1 = pygame.Rect(cx - offset - arc_r, eye_y - arc_r, arc_r * 2, arc_r * 2)
        pygame.draw.arc(screen, (0, 0, 0), rect1, math.pi, 2 * math.pi, max(1, r // 8))
        rect2 = pygame.Rect(cx + offset - arc_r, eye_y - arc_r, arc_r * 2, arc_r * 2)
        pygame.draw.arc(screen, (0, 0, 0), rect2, math.pi, 2 * math.pi, max(1, r // 8))

    def _draw_bored_eyes(self, screen, cx, eye_y, r):
        offset = r // 3
        radius = max(1, r // 4)
        for ex in [cx - offset, cx + offset]:
            rect = pygame.Rect(ex - radius, eye_y - radius, radius * 2, radius * 2)
            pygame.draw.arc(screen, (0, 0, 0), rect, math.pi, 2 * math.pi, max(1, r // 7))

    def _update_expression(self):
        if self.state == "clicked":
            self.expression = "happy"
        elif self.state == "idle" and self.total_idle > FPS * 5:
            self.expression = "bored"
        else:
            self.expression = "normal"

    def handle_click(self):
        self.state = "clicked"
        self.click_timer = 10
        self.scale = 1.3

    def start_drag(self, mouse_x, mouse_y):
        self.dragging = True
        self.drag_offset_x = self.x - mouse_x
        self.drag_offset_y = self.y - mouse_y

    def update_drag(self, mouse_x, mouse_y):
        """拖拽：宠物直接跟随鼠标"""
        if self.dragging:
            self.x = mouse_x + self.drag_offset_x
            self.y = mouse_y + self.drag_offset_y
            # 边界检测
            self.x = max(self.radius, min(SCREEN_W - self.radius, self.x))
            self.y = max(self.radius, min(SCREEN_H - self.radius, self.y))

    def end_drag(self):
        """结束拖拽，判断是否算点击"""
        self.dragging = False
        self.state = "idle"
        self.idle_timer = random.randint(IDLE_MIN, IDLE_MAX)

    def _update_idle(self):
        self.breathe_phase += BREATHE_SPEED
        self.scale = BREATHE_MIN + (BREATHE_MAX - BREATHE_MIN) * (
            0.5 + 0.5 * math.sin(self.breathe_phase)
        )
        self.idle_timer -= 1
        if self.idle_timer <= 0:
            self._start_walking()

    def _start_walking(self):
        margin = self.radius + 20
        self.target_x = random.uniform(margin, SCREEN_W - margin)
        self.target_y = random.uniform(margin, SCREEN_H - margin)
        self.state = "walking"

    def _update_walking(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        if dist < 1:
            self.x = self.target_x
            self.y = self.target_y
            self.state = "idle"
            self.idle_timer = random.randint(IDLE_MIN, IDLE_MAX)
        else:
            speed = WALK_SPEED
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed
            self.scale = 1.0

    def _update_clicked(self):
        self.click_timer -= 1
        self.scale = 1.0 + 0.3 * (self.click_timer / 10)
        if self.click_timer <= 0:
            self.state = "idle"
            self.scale = 1.0
            self.idle_timer = random.randint(IDLE_MIN, IDLE_MAX)
