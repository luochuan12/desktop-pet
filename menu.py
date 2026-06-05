"""右键菜单 — 显示、选择、回调"""
import pygame
from config import WHITE, BLACK, FONT_PATH


class Menu:
    """手绘右键菜单"""

    def __init__(self, items, font=None):
        """
        items: [(文字, 回调函数), ...]
        font: pygame.font.Font 实例（需支持中文）
        """
        self.items = items
        self.visible = False
        self.x = 0
        self.y = 0
        self.width = 140
        self.item_height = 28
        self.padding = 8
        self.hover_index = -1

        # 使用传入的字体，否则尝试微软雅黑
        if font:
            self.font = font
        else:
            try:
                self.font = pygame.font.Font(FONT_PATH, 13)
            except Exception:
                self.font = pygame.font.SysFont("arial", 13)

    def show(self, x, y):
        self.visible = True
        self.x = x
        self.y = y
        self.hover_index = -1

    def hide(self):
        self.visible = False
        self.hover_index = -1

    def handle_mouse_move(self, mx, my):
        if not self.visible:
            return
        rel_y = my - self.y
        if 0 <= mx - self.x <= self.width:
            idx = rel_y // self.item_height
            if 0 <= idx < len(self.items):
                self.hover_index = idx
            else:
                self.hover_index = -1
        else:
            self.hover_index = -1

    def handle_click(self, mx, my):
        if not self.visible:
            return False
        rel_x = mx - self.x
        rel_y = my - self.y
        if 0 <= rel_x <= self.width:
            idx = rel_y // self.item_height
            if 0 <= idx < len(self.items):
                self.hide()
                self.items[idx][1]()
                return True
        self.hide()
        return False

    def draw(self, screen):
        if not self.visible:
            return
        h = len(self.items) * self.item_height
        bg = pygame.Surface((self.width, h))
        bg.fill(WHITE)
        bg.set_alpha(230)
        screen.blit(bg, (self.x, self.y))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, h), 1)

        for i, (text, _) in enumerate(self.items):
            if i == self.hover_index:
                highlight = pygame.Surface((self.width - 2, self.item_height - 2))
                highlight.fill((200, 220, 255))
                screen.blit(highlight, (self.x + 1, self.y + i * self.item_height + 1))
            txt = self.font.render(text, True, BLACK)
            screen.blit(txt, (self.x + self.padding,
                              self.y + i * self.item_height + 5))
