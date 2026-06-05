"""桌宠配置常量"""

# 窗口
WIN_WIDTH = 200
WIN_HEIGHT = 200
FPS = 30

# 颜色
COLORKEY = (255, 0, 255)   # 品红色 = 透明通道
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 宠物（阶段一用圆形占位）
PET_RADIUS = 40
PET_COLOR = (100, 180, 255)  # 浅蓝色

# 游走
WALK_SPEED = 1.5            # 每帧移动像素
IDLE_MIN = 60               # 最短待机帧数（约2秒）
IDLE_MAX = 180              # 最长待机帧数（约6秒）

# 呼吸动画
BREATHE_SPEED = 0.02        # 呼吸变化速度
BREATHE_MIN = 0.95          # 最小缩放
BREATHE_MAX = 1.05          # 最大缩放
