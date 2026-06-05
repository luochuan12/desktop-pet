"""桌宠配置常量"""
import pygame

pygame.init()
INFO = pygame.display.Info()
SCREEN_W = INFO.current_w
SCREEN_H = INFO.current_h

# 窗口大小（本地坐标，宠物在这个范围内活动）
WIN_W = 300
WIN_H = 300

# 字体
FONT_PATH = "/mnt/c/Windows/Fonts/msyh.ttc"
FONT_SIZE = 13
FONT_SIZE_SMALL = 12

FPS = 30

# 颜色
COLORKEY = (255, 0, 255)
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
