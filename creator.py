import pygame
import sys

from pathlib import Path
from tools import load_image, load_alpha_image


W_SIZE = WIDTH, HEIGHT = (1920, 1080)

pygame.init()

infoObject = pygame.display.Info()
screen = pygame.display.set_mode(
    (infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN
)
display = pygame.Surface(W_SIZE)
screen_offset_x = screen.get_width() // 2 - WIDTH // 2
screen_offset_y = screen.get_height() // 2 - HEIGHT // 2

clock = pygame.time.Clock()
FPS = 60

background_image = load_image("data/wallpaper.jpg")
module_net = load_image("data/module_net.png")
module_net.set_alpha(100)

scr_w, scr_h = display.get_size()
bg_w, bg_h = background_image.get_size()

if scr_w != bg_w:
    scale_coeff_x = scr_w / bg_w

    background_image = pygame.transform.scale(
        background_image, (scale_coeff_x * bg_w, scale_coeff_x * bg_h)
    )
    bg_w, bg_h = background_image.get_size()

if scr_h > bg_h:
    scale_coeff_y = scr_h / bg_h

    background_image = pygame.transform.scale(
        background_image, (scale_coeff_y * bg_w, scale_coeff_y * bg_h)
    )


icon_width = 282
area_between_icons_x = 32
area_between_icons_y = 32
left_offset = 191
top_offset = 95

buttons_and_dirs = []
directories = [str(path) for path in Path("data/lents").glob("**/lent.png")]
for i, path in enumerate(directories):
    try:
        lent_image = load_image(f"data/lents/lent_{i + 1}/lent.png")
        logo_image = load_alpha_image(f"data/lents/lent_{i + 1}/logo.png")
    except Exception as exception:
        print(f"{exception.__class__.__name__}: {str(exception)}")
        continue

    with open(f'data/lents/lent_{i + 1}/pos.txt', 'r') as file:
        x, y = map(int, file.read().split(','))
    
    pos_path = path[:-8] + 'pos.txt'
    buttons_and_dirs.append([logo_image, pygame.Rect(x, y, *logo_image.get_size()), pos_path])

logo_image = load_alpha_image("data/chronicle/logo.png")
pos_path = 'data/chronicle/pos.txt'
with open(pos_path, 'r') as file:
    x, y = map(int, file.read().split(','))
buttons_and_dirs.append([logo_image, pygame.Rect(x, y, *logo_image.get_size()), pos_path])


magnets_x = [
    left_offset,
    left_offset + (area_between_icons_x + icon_width),
    left_offset + (area_between_icons_x + icon_width) * 2,
    left_offset + (area_between_icons_x + icon_width) * 3,
    left_offset + (area_between_icons_x + icon_width) * 4,
]
magnets_y = [
    top_offset
]


def save_positions(buttons_and_dirs, offset):
    for i in range(len(buttons_and_dirs)):
        with open(buttons_and_dirs[i][2], 'w') as file:
            x, y = buttons_and_dirs[i][1].topleft
            file.write('{},{}'.format(x, y - offset))


def main_menu():
    drag = False
    drag_idx = None
    drag_start = None
    drag_rect = None

    offset = 0
    while True:
        display.fill((0, 0, 0))

        display.blit(background_image, (0, 0))
        display.blit(module_net, (0, 0))

        mx, my = mouse_pos = pygame.mouse.get_pos()

        clicked = False
        offset_dx = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEWHEEL:
                offset_dx = event.y * 65
                offset += offset_dx

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = True
                    drag_start = mouse_pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if drag_idx is not None:
                        buttons_and_dirs[drag_idx][1] = drag_rect

                    drag = False
                    drag_idx = None
                    drag_start = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    save_positions(buttons_and_dirs, offset)

        for i, (image, rect, _) in enumerate(buttons_and_dirs):
            rect.move_ip(0, offset_dx)
            if drag_idx == i:
                rect = rect.move(mx - drag_start[0], my - drag_start[1])
                for x in magnets_x:
                    if abs(x - rect.x) < 20:
                        rect.x = x
                for y in magnets_y:
                    if abs(y - rect.y) < 15:
                        rect.y = y
                for k in range(len(buttons_and_dirs)):
                    if k == i:
                        continue
                    another = buttons_and_dirs[k][1]
                    if another.left < rect.right and another.right > rect.left:
                        if abs(rect.top - another.bottom - area_between_icons_y) < 15:
                            rect.top = another.bottom + area_between_icons_y
                            break
                drag_rect = rect.copy()
            else:
                display.blit(image, rect)

            if clicked and not drag:
                if rect.collidepoint(mx, my):
                    drag = True
                    drag_idx = i
                    drag_rect = rect.copy()

        if drag_idx is not None:
            display.blit(buttons_and_dirs[drag_idx][0], drag_rect)

        screen.blit(display, (screen_offset_x, screen_offset_y))
        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main_menu()
