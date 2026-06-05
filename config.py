"""桌宠配置常量"""
import os
import sys
import pygame

pygame.init()
INFO = pygame.display.Info()
SCREEN_W = INFO.current_w
SCREEN_H = INFO.current_h

WIN_W = 280
WIN_H = 280
FPS = 30

# ── 平台检测 ──
IS_WINDOWS = sys.platform == "win32"

# 字体路径
if IS_WINDOWS:
    FONT_PATH = "C:/Windows/Fonts/msyh.ttc"
else:
    FONT_PATH = "/mnt/c/Windows/Fonts/msyh.ttc"

# 如果默认字体不存在，尝试替代
if not os.path.exists(FONT_PATH):
    if IS_WINDOWS:
        FONT_PATH = "C:/Windows/Fonts/simhei.ttf"
    else:
        FONT_PATH = "/mnt/c/Windows/Fonts/simhei.ttf"

FONT_SIZE = 13
FONT_SIZE_SMALL = 12

# 颜色
COLORKEY = (255, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PET_RADIUS = 40
PET_COLOR = (100, 180, 255)

WALK_SPEED = 1.5
IDLE_MIN = 60
IDLE_MAX = 180

BREATHE_SPEED = 0.02
BREATHE_MIN = 0.95
BREATHE_MAX = 1.05
