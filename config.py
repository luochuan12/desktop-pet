"""桌宠配置常量"""
import os
import sys
import pygame

pygame.init()
INFO = pygame.display.Info()
SCREEN_W = INFO.current_w
SCREEN_H = INFO.current_h

FPS = 30

# ── 平台检测 ──
IS_WINDOWS = sys.platform == "win32"

# 透明色（Windows 用黑色 = pywin32 真透明, Linux/WSL 用品红 = colorkey）
TRANS_COLOR = (0, 0, 0) if IS_WINDOWS else (255, 0, 255)

# 字体
if IS_WINDOWS:
    FONT_PATH = "C:/Windows/Fonts/msyh.ttc"
else:
    FONT_PATH = "/mnt/c/Windows/Fonts/msyh.ttc"
if not os.path.exists(FONT_PATH):
    FONT_PATH = None

FONT_SIZE = 13
FONT_SIZE_SMALL = 12

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PET_RADIUS = 40
PET_COLOR = (100, 180, 255)

WALK_SPEED = 2.0
IDLE_MIN = 60
IDLE_MAX = 180

BREATHE_SPEED = 0.02
BREATHE_MIN = 0.95
BREATHE_MAX = 1.05
