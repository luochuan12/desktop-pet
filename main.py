"""桌宠入口 — 全屏透明窗口 + 菜单 + Hermes 联动"""
import pygame
import sys
import random
import subprocess
import threading
from config import SCREEN_W, SCREEN_H, FPS, COLORKEY, WHITE, BLACK, FONT_PATH, FONT_SIZE_SMALL
from pet import Pet
from menu import Menu


def main():
    pygame.init()

    # 全屏无边框窗口（品红色 = 透明）
    screen = pygame.display.set_mode(
        (SCREEN_W, SCREEN_H),
        pygame.NOFRAME
    )
    pygame.display.set_caption("桌宠")
    screen.set_colorkey(COLORKEY)

    clock = pygame.time.Clock()

    # 窗口置顶
    try:
        import ctypes
        hwnd = pygame.display.get_wm_info()["window"]
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, 0x80008)
    except Exception:
        pass

    # 宠物初始在屏幕中央
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

    # ── Hermes 后台调用 ──
    def ask_hermes(question):
        nonlocal bubble_text, bubble_timer
        say("🤔 思考中...", 9999)
        try:
            result = subprocess.run(
                ["hermes", "chat", "-q", question, "-Q"],
                capture_output=True, text=True, timeout=30,
                cwd="/home/luochuan",
            )
            answer = result.stdout.strip()
            if "session_id:" in answer:
                answer = answer.split("\n", 1)[-1].strip()
            if answer:
                say(answer, 360)
            else:
                say("😅 没回答上来...", 120)
        except subprocess.TimeoutExpired:
            say("⏰ 思考超时了~", 120)
        except Exception:
            say("❌ Hermes 调用失败...", 120)

    def ask_hermes_async(question):
        t = threading.Thread(target=ask_hermes, args=(question,), daemon=True)
        t.start()

    # ── 笑话 ──
    jokes = [
        "为什么程序员分不清万圣节和圣诞节？\n因为 Oct 31 == Dec 25！",
        "SQL 走进酒吧，看到两张桌子，\n问：我能 JOIN 你们吗？",
        "bug 不叫 bug，叫：\n未被文档记录的特性。",
        "Java 和 C 去吃饭，C 说：\n我指针忘带了。Java：没事，我不需要。",
    ]

    # ── 菜单 ──
    menu = Menu([
        ("讲个笑话", lambda: say(random.choice(jokes), 180)),
        ("你在干嘛？", lambda: say(_status_msg(pet), 120)),
        ("问 AI：今天学什么？",
         lambda: ask_hermes_async("我是一名Java初学者，今天应该学什么？给一个简短的学习建议")),
        ("问 AI：随机小知识",
         lambda: ask_hermes_async("给我一个有趣的编程小知识，简短一点")),
        ("退出", lambda: _quit()),
    ], font_menu)

    def _status_msg(p):
        if p.state == "walking":
            return "溜达溜达~ 🚶"
        elif p.expression == "bored":
            return "好无聊啊…… 😑"
        else:
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
                    if dist <= pet.radius:
                        pet.start_drag(mx, my)

                elif event.button == 3:
                    dist = ((mx - pet.x) ** 2 + (my - pet.y) ** 2) ** 0.5
                    if dist <= pet.radius:
                        menu.show(int(pet.x) + 30, int(pet.y) - 120)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    pet.end_drag()

            elif event.type == pygame.MOUSEMOTION:
                mx, my = pygame.mouse.get_pos()
                pet.update_drag(mx, my)
                menu.handle_mouse_move(mx, my)

        # ── 更新 ──
        pet.update()
        if bubble_timer > 0:
            bubble_timer -= 1
        else:
            bubble_text = ""

        # ── 绘制 ──
        screen.fill(COLORKEY)

        if bubble_text:
            _draw_bubble(screen, pet, bubble_text, font_small)

        pet.draw(screen)
        menu.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)


def _draw_bubble(screen, pet, text, font):
    """在宠物上方绘制对话气泡"""
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
