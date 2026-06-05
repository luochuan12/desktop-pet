"""桌宠入口 — 跨平台透明窗口 + 菜单 + Hermes 联动"""
import pygame
import sys
import random
import subprocess
import threading
from config import (
    WIN_W, WIN_H, SCREEN_W, SCREEN_H,
    FPS, COLORKEY, WHITE, BLACK,
    FONT_PATH, FONT_SIZE_SMALL,
    PET_RADIUS, IS_WINDOWS,
)
from pet import Pet
from menu import Menu
import window_utils as wu


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.NOFRAME)
    pygame.display.set_caption("桌宠")
    screen.set_colorkey(COLORKEY)
    clock = pygame.time.Clock()

    hwnd = wu.get_hwnd(pygame.display)

    # 初始窗口位置（屏幕中央）
    win_x = (SCREEN_W - WIN_W) // 2
    win_y = (SCREEN_H - WIN_H) // 2
    wu.move_to(hwnd, win_x, win_y)
    wu.set_topmost(hwnd)

    pet = Pet(WIN_W // 2, WIN_H // 2)

    # ── 字体 ──
    try:
        font_small = pygame.font.Font(FONT_PATH, FONT_SIZE_SMALL)
        font_menu = pygame.font.Font(FONT_PATH, 13)
    except Exception:
        font_small = pygame.font.SysFont("arial", 12)
        font_menu = pygame.font.SysFont("arial", 13)

    # ── 裁剪状态 ──
    clip_expanded = False

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
            say("⏰ 思考超时了~", 120)
        except Exception:
            say("❌ 调用失败", 120)

    def ask_hermes_async(question):
        threading.Thread(target=ask_hermes, args=(question,), daemon=True).start()

    jokes = [
        "为什么程序员分不清万圣节和圣诞节？\n因为 Oct 31 == Dec 25！",
        "SQL 走进酒吧：我能 JOIN 你们吗？",
        "bug 不叫 bug，叫未被文档记录的特性。",
    ]

    menu = Menu([
        ("讲个笑话", lambda: say(random.choice(jokes), 180)),
        ("你在干嘛？", lambda: say(_status_msg(pet), 120)),
        ("问 AI：今天学什么？",
         lambda: ask_hermes_async("我是一名Java初学者，今天应该学什么？给简短建议")),
        ("问 AI：随机小知识",
         lambda: ask_hermes_async("给我一个有趣的编程小知识，简短")),
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
                    dist = ((mx - pet.x) ** 2 + (my - pet.y) ** 2) ** 0.5
                    if dist <= pet.radius + 10:
                        pet.start_drag(mx, my)

                elif event.button == 3:
                    dist = ((mx - pet.x) ** 2 + (my - pet.y) ** 2) ** 0.5
                    if dist <= pet.radius + 10:
                        menu.show(int(pet.x) + 20, int(pet.y) - 100)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    pet.end_drag()

            elif event.type == pygame.MOUSEMOTION:
                mx, my = pygame.mouse.get_pos()
                pet.update_drag(mx, my)
                menu.handle_mouse_move(mx, my)

        # ── 更新 ──
        pet.update()

        # 拖拽中移动窗口
        if pet.dragging:
            mx, my = pygame.mouse.get_pos()
            if pet.x < 60 and win_x > 0:
                win_x = max(0, win_x - 4)
                wu.move_to(hwnd, win_x, win_y)
            elif pet.x > WIN_W - 60 and win_x < SCREEN_W - WIN_W:
                win_x = min(SCREEN_W - WIN_W, win_x + 4)
                wu.move_to(hwnd, win_x, win_y)
            if pet.y < 60 and win_y > 0:
                win_y = max(0, win_y - 4)
                wu.move_to(hwnd, win_x, win_y)
            elif pet.y > WIN_H - 60 and win_y < SCREEN_H - WIN_H:
                win_y = min(SCREEN_H - WIN_H, win_y + 4)
                wu.move_to(hwnd, win_x, win_y)
        else:
            # 游走中接近边缘 → 移动窗口
            margin = 90
            moved = False
            if pet.x < margin and win_x > 0:
                win_x = max(0, win_x - 3); moved = True
            elif pet.x > WIN_W - margin and win_x < SCREEN_W - WIN_W:
                win_x = min(SCREEN_W - WIN_W, win_x + 3); moved = True
            if pet.y < margin and win_y > 0:
                win_y = max(0, win_y - 3); moved = True
            elif pet.y > WIN_H - margin and win_y < SCREEN_H - WIN_H:
                win_y = min(SCREEN_H - WIN_H, win_y + 3); moved = True
            if moved:
                wu.move_to(hwnd, win_x, win_y)

        wu.set_topmost(hwnd)

        if bubble_timer > 0:
            bubble_timer -= 1
        else:
            bubble_text = ""

        # ── 裁剪 ──
        need_expand = menu.visible or (bubble_text and bubble_timer > 0)
        if need_expand and not clip_expanded:
            wu.set_rect_clip(hwnd, 0, 0, WIN_W, WIN_H)
            clip_expanded = True
        elif not need_expand and clip_expanded:
            r = PET_RADIUS + 15
            wu.set_round_clip(hwnd, pet.x, pet.y, r)
            clip_expanded = False
        elif not clip_expanded:
            r = PET_RADIUS + 15
            wu.set_round_clip(hwnd, pet.x, pet.y, r)

        # ── 绘制 ──
        screen.fill(COLORKEY)

        if bubble_text:
            _draw_bubble(screen, pet, bubble_text, font_small)

        pet.draw(screen)
        menu.draw(screen)

        pygame.display.flip()
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
