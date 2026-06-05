# 桌宠（Desktop Pet）实施计划

> **For Hermes:** 分阶段实施，当前先做阶段一（核心框架），后续再扩展。

**目标：** 用 Pygame 实现一个桌面宠物程序，支持透明窗口、拖拽、点击反应、动画和 Hermes 联动。

**架构：** 单进程 Pygame 应用，状态机驱动行为，占位图形先跑通流程，后续替换美术资源。

**技术栈：** Python 3.10 + Pygame 2.1 + WSLg（窗口显示）

---

## 阶段一：核心框架（本次目标）

完成一个可拖拽、可点击、有简单动画占位的桌宠 MVP。

### 文件结构（阶段一）

```
desktop-pet/
├── main.py          # 入口：初始化、主循环
├── pet.py           # 宠物实体：位置、状态、绘制
├── config.py        # 配置常量
└── docs/
    └── plan.md      # 本计划
```

---

### Task 1: 透明无边框窗口 + 主循环

**目标：** 创建一个置顶、透明背景、无边框的窗口，运行基础事件循环。

**创建文件：** `config.py`、`main.py`

**需要掌握的知识：**
- `pygame.NOFRAME` — 无边框窗口
- `pygame.SRCALPHA` — 支持透明通道
- `WS_EX_LAYERED` + `WS_EX_TOPMOST` — Windows 上实现透明和置顶（需要 ctypes 调用 Windows API）
- 注意：Pygame 原生的透明窗口支持有限，阶段一只做无边框+品红色透明（colorkey 方式）

**品红色透明原理：** 把背景涂成品红（255,0,255），然后设置 colorkey，让这个颜色变透明。这是老式游戏常用的技巧，简单可靠。

**Step 1: 创建 config.py**

```python
"""桌宠配置常量"""

# 窗口
WIN_WIDTH = 200
WIN_HEIGHT = 200
FPS = 30

# 颜色
COLORKEY = (255, 0, 255)  # 品红色 = 透明通道
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 宠物（阶段一用圆形占位）
PET_RADIUS = 40
PET_COLOR = (100, 180, 255)  # 浅蓝色
```

**Step 2: 创建 main.py**

```python
"""桌宠入口 — 透明窗口 + 主循环"""
import pygame
import sys
from config import WIN_WIDTH, WIN_HEIGHT, FPS, COLORKEY

def main():
    pygame.init()
    
    # 创建无边框窗口
    screen = pygame.display.set_mode(
        (WIN_WIDTH, WIN_HEIGHT),
        pygame.NOFRAME  # 无边框
    )
    pygame.display.set_caption("桌宠")
    
    # 设置品红色透明（colorkey 方式）
    screen.set_colorkey(COLORKEY)
    
    clock = pygame.time.Clock()
    
    # 将窗口置顶（Windows API）
    try:
        import ctypes
        hwnd = pygame.display.get_wm_info()["window"]
        # WS_EX_TOPMOST = 0x8, WS_EX_LAYERED = 0x80000
        ctypes.windll.user32.SetWindowLongW(
            hwnd, -20,  # GWL_EXSTYLE
            0x80008     # WS_EX_LAYERED | WS_EX_TOPMOST
        )
    except Exception:
        pass  # 非 Windows 环境跳过
    
    # 主循环
    while True:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # 绘制
        screen.fill(COLORKEY)  # 品红色 = 透明
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
```

**Step 3: 运行测试**

```bash
cd /mnt/c/Users/luochuan/projects/desktop-pet
python3 main.py
```

**预期效果：** 桌面上出现一个小窗口，背景透明（品红变透明），显示品红色以外的内容。按 Ctrl+C 或关闭窗口退出。

**验证标准：** 
- 窗口无边框
- 品红色区域透明（能看到后面的桌面）
- 窗口置顶
- 程序正常退出不报错

---

### Task 2: 宠物占位图形 + 拖动

**目标：** 画一个圆形占位符代表宠物，能用鼠标拖拽移动。

**创建文件：** `pet.py`

**Step 1: 创建 pet.py**

```python
"""宠物实体 — 位置、状态、绘制"""
import pygame
from config import PET_RADIUS, PET_COLOR

class Pet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = PET_RADIUS
        self.color = PET_COLOR
        
        # 拖动状态
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
    
    def draw(self, screen):
        """绘制宠物（阶段一用圆形占位）"""
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        # 画两个小圆当眼睛
        eye_offset = self.radius // 3
        eye_radius = self.radius // 5
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
        """开始拖拽"""
        self.dragging = True
        self.drag_offset_x = self.x - mouse_x
        self.drag_offset_y = self.y - mouse_y
    
    def update_drag(self, mouse_x, mouse_y):
        """拖拽中更新位置"""
        if self.dragging:
            self.x = mouse_x + self.drag_offset_x
            self.y = mouse_y + self.drag_offset_y
    
    def end_drag(self):
        """结束拖拽"""
        self.dragging = False
```

**Step 2: 修改 main.py，加入 Pet 和拖动逻辑**

在 main.py 中添加：

```python
from pet import Pet

# 在 main() 中 screen 创建之后添加：
pet = Pet(WIN_WIDTH // 2, WIN_HEIGHT // 2)

# 在事件循环中添加：
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                mx, my = pygame.mouse.get_pos()
                pet.start_drag(mx, my)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                pet.end_drag()
        
        elif event.type == pygame.MOUSEMOTION:
            mx, my = pygame.mouse.get_pos()
            pet.update_drag(mx, my)

# 在 screen.fill(COLORKEY) 后添加：
        pet.draw(screen)
```

**Step 3: 运行测试**

```bash
python3 main.py
```

**预期效果：** 桌面出现一个蓝色圆形（有眼睛），可以用鼠标拖拽移动。

**验证标准：**
- 能看到蓝色圆形 + 眼睛
- 鼠标按住能拖拽
- 松手停止拖拽
- 窗口背景透明
- 程序正常退出

---

### Task 3: 点击反应 + 简单动画状态

**目标：** 点击宠物时有反馈效果（弹跳/变大再变小），引入状态概念。

**Step 1: 修改 pet.py，加入点击反应**

```python
class Pet:
    def __init__(self, x, y):
        # ... 原有代码 ...
        
        # 状态
        self.state = "idle"        # idle, clicked, walking
        self.click_timer = 0       # 点击效果计时器
        self.scale = 1.0           # 缩放比例（点击时变大）
    
    def handle_click(self):
        """被点击时的反应"""
        self.state = "clicked"
        self.click_timer = 10      # 10帧后恢复
        self.scale = 1.3           # 放大到130%
    
    def update(self):
        """每帧更新"""
        if self.state == "clicked":
            self.click_timer -= 1
            self.scale = 1.0 + 0.3 * (self.click_timer / 10)
            if self.click_timer <= 0:
                self.state = "idle"
                self.scale = 1.0
    
    def draw(self, screen):
        """绘制（加入缩放效果）"""
        r = int(self.radius * self.scale)
        pygame.draw.circle(screen, self.color, (self.x, self.y), r)
        # 眼睛也等比缩放
        eye_offset = int(r // 3 * self.scale)
        eye_radius = max(1, int(r // 5 * self.scale))
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
```

**Step 2: 修改 main.py，区分点击和拖拽**

在 MOUSEBUTTONDOWN 事件中：

```python
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mx, my = pygame.mouse.get_pos()
                # 如果鼠标在宠物范围内 → 拖拽；否则忽略
                dist = ((mx - pet.x)**2 + (my - pet.y)**2) ** 0.5
                if dist <= pet.radius:
                    pet.start_drag(mx, my)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if pet.dragging:
                    # 如果没怎么移动（短拖 = 点击）
                    pet.end_drag()
                    pet.handle_click()  # 点击反馈
```

实际上更简单的实现：区分"点击"和"拖拽"靠位移判断。按钮抬起时，如果位移小于 5 像素，算点击。

更简单的方式：MOUSEBUTTONUP 时如果 dragging=True，判断位置是否几乎没变：

```python
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and pet.dragging:
                old_x, old_y = pet.x, pet.y  # 需要保存按下时的位置
                pet.end_drag()
                # 位移小于阈值 = 点击
                if abs(pet.x - old_x) < 5 and abs(pet.y - old_y) < 5:
                    pet.handle_click()
```

需要在 Pet.start_drag 中记录起始位置：

```python
    def start_drag(self, mouse_x, mouse_y):
        self.dragging = True
        self.drag_start_x = self.x  # 新增：记录起始位置
        self.drag_start_y = self.y
        self.drag_offset_x = self.x - mouse_x
        self.drag_offset_y = self.y - mouse_y
```

**Step 3: 在主循环中每帧调用 pet.update()**

```python
        pet.update()  # 放在 screen.fill 之后、pet.draw 之前
```

**Step 4: 运行测试**

```bash
python3 main.py
```

**预期效果：**
- 快速点一下宠物 → 宠物弹跳变大再缩回
- 按住拖拽 → 正常拖动，松手不弹跳
- 轻点（拖很短距离）→ 弹跳

**验证标准：**
- 点击弹跳动画正常
- 拖拽不触发弹跳
- 动画流畅

---

### Task 4: 最终集成 + Git 提交

**目标：** 确认所有代码正确，整理并提交。

**Step 1: 完整运行验证**

```bash
cd /mnt/c/Users/luochuan/projects/desktop-pet
python3 main.py
```

测试清单：
- [ ] 窗口透明无边框
- [ ] 宠物可见
- [ ] 拖拽流畅
- [ ] 点击弹跳
- [ ] Ctrl+C 正常退出

**Step 2: 提交**

```bash
git add -A
git commit -m "feat: 桌宠核心框架 - 透明窗口/拖拽/点击反应"
```

---

## 阶段一完成标准

- [x] 透明无边框置顶窗口
- [x] 宠物占位图形（圆形 + 眼睛）
- [x] 鼠标拖拽移动
- [x] 点击弹跳反馈
- [x] Git 仓库已提交

## 下一阶段（阶段二）预览

- 随机游走（自动移动）
- 空闲动画（呼吸效果）
- 状态表情（多套表情切换）
- 右键菜单框架
- 更丰富的状态机

---

> **实施顺序：** Task 1 → Task 2 → Task 3 → Task 4（严格按顺序）
