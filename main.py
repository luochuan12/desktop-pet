"""桌宠入口 — 透明窗口 + 主循环"""
import pygame
import sys
from config import WIN_WIDTH, WIN_HEIGHT, FPS, COLORKEY
from pet import Pet


def main():
    pygame.init()

    # 创建无边框窗口
    screen = pygame.display.set_mode(
        (WIN_WIDTH, WIN_HEIGHT),
        pygame.NOFRAME
    )
    pygame.display.set_caption("桌宠")

    # 设置品红色透明（colorkey 方式）
    screen.set_colorkey(COLORKEY)

    clock = pygame.time.Clock()

    # 把窗口置顶（调用 Windows API）
    try:
        import ctypes
        hwnd = pygame.display.get_wm_info()["window"]
        # GWL_EXSTYLE = -20
        # WS_EX_LAYERED = 0x80000, WS_EX_TOPMOST = 0x8
        ctypes.windll.user32.SetWindowLongW(
            hwnd, -20,
            0x80008  # WS_EX_LAYERED | WS_EX_TOPMOST
        )
    except Exception:
        pass  # 非 Windows 环境跳过

    # 创建宠物（初始位置在窗口中央）
    pet = Pet(WIN_WIDTH // 2, WIN_HEIGHT // 2)

    # 主循环
    while True:
        # ① 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    mx, my = pygame.mouse.get_pos()
                    # 只有点在宠物上才开始拖拽
                    dist = ((mx - pet.x) ** 2 + (my - pet.y) ** 2) ** 0.5
                    if dist <= pet.radius:
                        pet.start_drag(mx, my)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    pet.end_drag()

            elif event.type == pygame.MOUSEMOTION:
                mx, my = pygame.mouse.get_pos()
                pet.update_drag(mx, my)

        # ② 绘制
        screen.fill(COLORKEY)   # 品红色 = 透明
        pet.update()
        pet.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
