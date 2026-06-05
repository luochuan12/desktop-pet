"""桌宠配置"""
import sys

IS_WINDOWS = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"

FPS = 30
FRAME_MS = 1000 // FPS

# 宠物
PET_SIZE = 80

# 游走
WALK_SPEED = 3
IDLE_MIN_MS = 2000
IDLE_MAX_MS = 6000

# 颜色
WHITE = "#FFFFFF"
BLACK = "#000000"
PET_COLOR = "#64B4FF"
BG_COLOR = "black"
HIGHLIGHT_COLOR = "#C8DCFF"

# 字体
if IS_WINDOWS:
    FONT = ("Microsoft YaHei", 10)
    FONT_SMALL = ("Microsoft YaHei", 9)
else:
    FONT = ("sans-serif", 10)
    FONT_SMALL = ("sans-serif", 9)
