"""桌宠配置常量"""
import pygame

# 屏幕大小（动态获取）
pygame.init()
INFO = pygame.display.Info()
SCREEN_W = INFO.current_w
SCREEN_H = INFO.current_h

# 字体（WSL 下使用 Windows 字体文件）
FONT_PATH = "/mnt/c/Windows/Fonts/msyh.ttc"
FONT_SIZE = 13
FONT_SIZE_SMALL = 12

FPS = 30

# 颜色
COLORKEY = (255, 0, 255)   # 品红色 = 透明通道
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 宠物
PET_RADIUS = 40
PET_COLOR = (100, 180, 255)

# 游走
WALK_SPEED = 1.5
IDLE_MIN = 60
IDLE_MAX = 180

# 呼吸
BREATHE_SPEED = 0.02
BREATHE_MIN = 0.95
BREATHE_MAX = 1.05
