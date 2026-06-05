"""桌宠入口 — pywin32 真透明全屏方案 (参考 DesktopPet-Ducky)"""
import pygame
import sys
import random
import subprocess
import threading
from config import (
    SCREEN_W, SCREEN_H,
    FPS, TRANS_COLOR, WHITE, BLACK,
    FONT_PATH, FONT_SIZE_SMALL,
    PET_RADIUS, IS_WINDOWS,
)
from pet import Pet
from menu import Menu
import window_utils as wu


def main():
    pygame.init()

    # 全屏无边框窗口
    screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
    pygame.display.set_caption("桌宠")

    hwnd = wu.get_hwnd(pygame.display)
    wu.make_transparent(hwnd)  # 真透明（Windows 上）
    wu.set_topmost(hwnd)

    clock = pygame.time.Clock()

    # 黑色 = 透明的 surface
    transparent_surface = pygame.Surface(screen.get_size())
    transparent_surface.fill(TRANS_COLOR)

    # 宠物在屏幕中央
    pet = Pet(SCREEN_W // 2, SCREEN_H // 2)

    # ── 字体 ──
    try:
        font_small = pygame.font.Font(FONT_PATH, FONT_SIZE_SMALL)
        font_menu = pygame.font.Font(FONT_PATH, 13)
    except Exception:
        font_small = pygame.font.SysFont("arial", 12)
        font_menu = pygame.font.SysFont("arial", 13)

    # ── 对话气泡 ──
    bubble_text = ""
    bubble_timer = 0

    def say(text, duration=120):
        nonlocal bubble_text, bubble_timer
        bubble_text = text
        bubble_timer = duration

    # ── Hermes ──
    def ask_hermes(question):
        say("🤔 思考中...", 9999)
        try:
            result = subprocess.run(
                ["hermes", "chat", "-q", question, "-Q"],
                capture_output=True, text=True, timeout=30,
                cwd="/home/luochuan" if not IS_WINDOWS else None,
            )
            answer = result.stdout.strip()
            if "session_id:" in answer:
                answer = answer.split("\n", 1)[-1].strip()
            say(answer if answer else "😅 没回答上来...", 360)
        except subprocess.TimeoutExpired:
            say("⏰ 超时了~", 120)
        except Exception:
            say("❌ 调用失败", 120)

    def ask_hermes_async(question):
        threading.Thread(target=ask_hermes, args=(question,), daemon=True).start()

    jokes = [
        "为什么 Oct 31 == Dec 25？\n因为程序员用八进制算...",
        "SQL 走进酒吧：我能 JOIN 你们吗？",
        "bug 不叫 bug，叫未被文档记录的特性。",
    ]

    menu = Menu([
        ("讲个笑话", lambda: say(random.choice(jokes), 180)),
        ("你在干嘛？", lambda: say(_status_msg(pet), 120)),
        ("问 AI：今天学什么？",
         lambda: ask_hermes_async("我是Java初学者，今天学什么？给简短建议")),
        ("问 AI：随机小知识",
         lambda: ask_hermes_async("有趣的编程冷知识，简短")),
        ("退出", lambda: _quit()),
    ], font_menu)

    def _status_msg(p):
        if p.state == "walking":
            return "溜达溜达~ 🚶"
        elif p.expression == "bored":
            return "好无聊…… 😑"
        return "发呆中 💤"

    def _quit():
        pygame.quit()
        sys.exit()

    # ── 主循环 ──
    dragging = False
    frame = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _quit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                if menu.visible:
                    if menu.handle_click(mx, my):
                        continue

                if event.button == 1:
                    # 检查是否点在宠物上
                    dist = ((mx - pet.x) ** 2 + (my - pet.y) ** 2) ** 0.5
                    if dist <= pet.radius + 15:
                        dragging = True
                        pet.start_drag(mx, my)

                elif event.button == 3:
                    dist = ((mx - pet.x) ** 2 + (my - pet.y) ** 2) ** 0.5
                    if dist <= pet.radius + 15:
                        menu.show(
                            int(pet.x) + 30,
                            int(pet.y) - 100
                        )

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging:
                    dragging = False
                    pet.end_drag()

            elif event.type == pygame.MOUSEMOTION:
                mx, my = pygame.mouse.get_pos()
                if dragging:
                    # 拖拽：宠物直接跟随鼠标
                    pet.update_drag(mx, my)
                menu.handle_mouse_move(mx, my)

        # ── 更新 ──
        if not dragging:
            pet.update()

        if bubble_timer > 0:
            bubble_timer -= 1
        else:
            bubble_text = ""

        frame += 1
        if frame % 30 == 0:
            wu.set_topmost(hwnd)

        # ── 绘制 ──
        screen.blit(transparent_surface, (0, 0))

        if bubble_text:
            _draw_bubble(screen, pet, bubble_text, font_small)

        pet.draw(screen)
        menu.draw(screen)

        pygame.display.update()
        clock.tick(FPS)


def _draw_bubble(screen, pet, text, font):
    lines = text.split("\n")
    line_surfs = [font.render(line, True, BLACK) for line in lines]
    max_w = max(s.get_width() for s in line_surfs) + 16
    h = sum(s.get_height() for s in line_surfs) + 12
    bx = int(pet.x - max_w // 2)
    by = int(pet.y - pet.radius - h - 10)

    bubble = pygame.Surface((max_w, h))
    bubble.fill(WHITE)
    bubble.set_alpha(230)
    screen.blit(bubble, (bx, by))
    pygame.draw.rect(screen, BLACK, (bx, by, max_w, h), 1)

    tri_points = [
        (int(pet.x), int(pet.y - pet.radius - 3)),
        (int(pet.x - 6), by + h),
        (int(pet.x + 6), by + h),
    ]
    pygame.draw.polygon(screen, WHITE, tri_points)

    y_off = by + 6
    for s in line_surfs:
        screen.blit(s, (bx + 8, y_off))
        y_off += s.get_height()


if __name__ == "__main__":
    main()
