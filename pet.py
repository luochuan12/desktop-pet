"""宠物实体 — 位置、绘制、拖拽、动画状态"""
import pygame
from config import PET_RADIUS, PET_COLOR


class Pet:
    """桌宠角色（阶段一用圆形占位）"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = PET_RADIUS
        self.color = PET_COLOR

        # 状态
        self.state = "idle"       # idle | clicked
        self.click_timer = 0      # 弹跳效果剩余帧数
        self.scale = 1.0          # 当前缩放比例

        # 拖拽状态
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def handle_click(self):
        """被点击时的反应：弹跳变大"""
        self.state = "clicked"
        self.click_timer = 10     # 10 帧后恢复
        self.scale = 1.3          # 瞬间放大到 130%

    def update(self):
        """每帧更新状态"""
        if self.state == "clicked":
            self.click_timer -= 1
            # 缩放逐渐回缩：1.3 → 1.0
            self.scale = 1.0 + 0.3 * (self.click_timer / 10)
            if self.click_timer <= 0:
                self.state = "idle"
                self.scale = 1.0

    def draw(self, screen):
        """绘制宠物（带缩放效果）"""
        r = int(self.radius * self.scale)
        # 身体
        pygame.draw.circle(screen, self.color, (self.x, self.y), r)

        # 眼睛（跟随缩放）
        eye_offset = int(r // 3)
        eye_radius = max(1, int(r // 5))
        pygame.draw.circle(
            screen, (0, 0, 0),
            (self.x - eye_offset, self.y - eye_offset // 2),
            eye_radius
        )
        pygame.draw.circle(
            screen, (0, 0, 0),
            (self.x + eye_offset, self.y - eye_offset // 2),
            eye_radius
        )

    def start_drag(self, mouse_x, mouse_y):
        self.dragging = True
        self.drag_start_x = self.x
        self.drag_start_y = self.y
        self.drag_offset_x = self.x - mouse_x
        self.drag_offset_y = self.y - mouse_y

    def update_drag(self, mouse_x, mouse_y):
        if self.dragging:
            self.x = mouse_x + self.drag_offset_x
            self.y = mouse_y + self.drag_offset_y

    def end_drag(self):
        """结束拖拽，判断是拖拽还是点击"""
        if not self.dragging:
            return
        # 位移 < 5 像素 → 算点击
        moved = abs(self.x - self.drag_start_x) + abs(self.y - self.drag_start_y)
        if moved < 5:
            self.handle_click()
        self.dragging = False
