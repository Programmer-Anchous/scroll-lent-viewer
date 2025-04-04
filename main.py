import pygame
import sys

from pathlib import Path
from tools import *
from finger import Finger
from math import hypot


ORANGE = (200, 140, 40)
WHITE = (200,) * 3
GREY = (25,) * 3
MEDIUM_GREY = (100,) * 3
LIGHT_GREY = (160,) * 3
BLACK = (15,) * 3

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

bottom_offset = 80
panel_width = 250

# font = pygame.font.Font(None, 36)
font_path = "data/fonts/font.otf"
font_small = pygame.font.Font(font_path, 24)
font = pygame.font.Font(font_path, 32)
font_big = pygame.font.Font(font_path, 48)

background_image = load_image("data/wallpaper.jpg")
# background_image.set_alpha(200)
module_net = load_image("data/module_net.png")
module_net.set_alpha(170)

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


class Label:
    def __init__(
        self,
        text: str,
        coords: tuple | list,
        center: bool = False,
        font_: pygame.font.Font = font,
    ):
        self.image = font_.render(text, True, WHITE)
        if center:
            self.rect = self.image.get_rect(center=coords)
        else:
            self.rect = self.image.get_rect(topleft=coords)

    def update(self):
        display.blit(self.image, self.rect)


class Button:
    def __init__(
        self,
        image: pygame.Surface,
        image_pressed: pygame.Surface,
        coords: tuple | list,
        center: bool = False,
    ):
        self.image = image
        self.image_pressed = image_pressed
        if center:
            self.rect = self.image.get_rect(center=coords)
        else:
            self.rect = self.image.get_rect(topleft=coords)
        self.coords = self.rect.topleft

        self.clicked = False

    def update(self, finger_pos: tuple, click: bool, scroll: tuple = 0):
        self.rect = self.rect.move(0, -scroll)

        if self.rect.y > self.coords[1]:
            self.rect.y = self.coords[1]
        elif self.rect.y < self.coords[1] - sliding_size:
            self.rect.y = self.coords[1] - sliding_size

        self.clicked = False
        if self.rect.collidepoint(finger_pos):
            current_image = self.image_pressed
            if click:
                self.clicked = True
        else:
            current_image = self.image
        display.blit(current_image, self.rect)

    def triggered(self) -> bool:
        return self.clicked

    def set_pos(self, x, y):
        self.rect.topleft = (x, y)
        self.coords = self.rect.topleft

    def reset(self):
        self.clicked = False


class TextButton(Button):
    def __init__(
        self,
        text: str,
        coords: tuple | list,
        center: bool = False,
        font_: pygame.font.Font = font,
    ):
        image = font_.render(text, True, WHITE)
        image_pressed = font_.render(text, True, WHITE)
        super().__init__(image, image_pressed, coords, center)


class Lent:
    def __init__(self, image: pygame.Surface):
        self.image = image
        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()
        self.cropped = None

        self.scroll = 0

        self.is_start = True
        self.is_end = False

        self.end_scroll_value = self.image_height - HEIGHT + bottom_offset

        self.links = []

        self.is_animation = False
        self.speed = 0
        self.end_scroll = None

    def update(self, movement: int):
        if self.is_animation:
            if abs(self.scroll - self.end_scroll) / abs(self.speed) < 15:
                if abs(self.speed) > 3:
                    self.speed = abs(abs(self.speed) * 0.8) * sign(self.speed)

            scroll = self.scroll + self.speed
            self.set_scroll(scroll)

            if abs(self.scroll - self.end_scroll) <= abs(self.speed):
                self.scroll = self.end_scroll

                self.is_animation = False
                self.speed = 0
                self.end_scroll = None
        else:
            if self.is_start:
                if movement > 0:
                    self.is_start = False

            elif self.is_end:
                if movement < 0:
                    self.is_end = False

            if not (self.is_start or self.is_end):
                self.scroll += movement
                if self.scroll < 0:
                    self.scroll = 0
                    self.is_start = True
                elif self.scroll > self.end_scroll_value:
                    self.scroll = self.end_scroll_value
                    self.is_end = True

        self.cropped = self.image.subsurface(
            (0, self.scroll, self.image_width, HEIGHT - bottom_offset)
        )

        display.blit(self.cropped, (display.get_width() //
                     2 - self.cropped.get_width() // 2, 0))

    def set_scroll(self, scroll_num: int):
        self.scroll = scroll_num
        if self.scroll <= 0:
            self.scroll = 0
            self.is_start = True
            self.is_end = False
        elif self.scroll >= self.end_scroll_value:
            self.scroll = self.end_scroll_value
            self.is_start = False
            self.is_end = True
        else:
            self.is_start = False
            self.is_end = False

    def add_links(self, *links):
        for i, link in enumerate(links):
            button = TextButton(link[0], (30, i * 60 + 160))
            self.links.append((button, link[1]))

    def animation(self, end_scroll):
        if end_scroll != self.scroll:
            self.speed = (end_scroll - self.scroll) / 30
            self.end_scroll = end_scroll
            self.is_animation = True

    def reset(self):
        self.speed = 0
        self.is_animation = False
        self.scroll = 0


class Chronicle:
    def __init__(self, blocks):
        self.blocks = blocks

        self.scroll = 0

        self.is_start = True
        self.is_end = False

        self.image_height = blocks[-1]["rect"].bottom

        self.end_scroll_value = self.image_height - HEIGHT + bottom_offset * 2

        self.links = []
        self.cropped = pygame.Surface(W_SIZE)

        self.is_animation = False
        self.speed = 0
        self.end_scroll = None

    def update(self, movement: int):
        if self.is_animation:
            if abs(self.scroll - self.end_scroll) / abs(self.speed) < 15:
                if abs(self.speed) > 3:
                    self.speed = abs(abs(self.speed) * 0.8) * sign(self.speed)

            scroll = self.scroll + self.speed
            self.set_scroll(scroll)

            if abs(self.scroll - self.end_scroll) <= abs(self.speed):
                self.scroll = self.end_scroll

                self.is_animation = False
                self.speed = 0
                self.end_scroll = None
        else:
            if self.is_start:
                if movement > 0:
                    self.is_start = False

            elif self.is_end:
                if movement < 0:
                    self.is_end = False

            if not (self.is_start or self.is_end):
                self.scroll += movement
                if self.scroll < 0:
                    self.scroll = 0
                    self.is_start = True
                elif self.scroll > self.end_scroll_value:
                    self.scroll = self.end_scroll_value
                    self.is_end = True

        for block in self.blocks:
            display.blit(block["image"], block["rect"].move(0, -self.scroll))
        

    def set_scroll(self, scroll_num: int):
        self.scroll = scroll_num
        if self.scroll <= 0:
            self.scroll = 0
            self.is_start = True
            self.is_end = False
        elif self.scroll >= self.end_scroll_value:
            self.scroll = self.end_scroll_value
            self.is_start = False
            self.is_end = True
        else:
            self.is_start = False
            self.is_end = False

    def add_links(self, *links):
        for i, link in enumerate(links):
            button = TextButton(link[0], (30, i * 60 + 160))
            self.links.append((button, link[1]))

    def animation(self, end_scroll):
        if end_scroll != self.scroll:
            self.speed = (end_scroll - self.scroll) / 30
            self.end_scroll = end_scroll
            self.is_animation = True

    def reset(self):
        self.speed = 0
        self.is_animation = False
        self.scroll = 0


class Panel:
    def __init__(self):
        self.width = panel_width
        self.surf = pygame.Surface((self.width, HEIGHT - bottom_offset))
        self.surf.set_alpha(210)
        self.is_opened = False

        dark_label = font.render("автопрокрутка", True, WHITE)
        light_label = font.render("автопрокрутка", True, WHITE)
        button_width, button_height = (
            dark_label.get_width() + 20,
            dark_label.get_height() + 26,
        )

        auto_scroll_image = pygame.Surface((button_width, button_height))
        auto_scroll_image.blit(
            dark_label,
            (
                button_width // 2 - dark_label.get_width() // 2,
                button_height // 2 - dark_label.get_height() // 2 - 2,
            ),
        )
        pygame.draw.rect(
            auto_scroll_image, WHITE, (0, 0, button_width, button_height), 4, 2
        )
        auto_scroll_image.set_colorkey((0, 0, 0))

        auto_scroll_image_pressed = pygame.Surface(
            (button_width, button_height))
        auto_scroll_image_pressed.blit(
            light_label,
            (
                button_width // 2 - dark_label.get_width() // 2,
                button_height // 2 - dark_label.get_height() // 2 - 2,
            ),
        )
        pygame.draw.rect(
            auto_scroll_image_pressed, WHITE, (0,
                                               0, button_width, button_height), 4, 2
        )
        auto_scroll_image_pressed.set_colorkey((0, 0, 0))

        self.auto_scroll_button = Button(
            auto_scroll_image, auto_scroll_image_pressed, (
                panel_width // 2 - 1, 80), True
        )

    def update(self, mouse_pos: tuple | list, click: bool, bg):
        if self.is_opened:
            display.blit(bg, (0, 0))
            display.blit(self.surf, (0, 0))
            self.auto_scroll_button.update(mouse_pos, click)

    def is_mouse_in_panel(self, mouse_pos: tuple):
        return mouse_pos[0] < self.width

    def open(self):
        self.is_opened = True

    def close(self):
        self.is_opened = False
        self.auto_scroll_button.reset()


def create_lent_button_images(button_surf: pygame.Surface) -> tuple:
    button_surf_pressed = button_surf.copy()
    return button_surf, button_surf_pressed


buttons_and_lents = []
directories = [path for path in Path("data/lents").iterdir() if path.is_dir()]
for i in range(len(directories)):
    try:
        lent_image = load_image(f"data/lents/lent_{i + 1}/lent.png")
        logo_image = load_alpha_image(f"data/lents/lent_{i + 1}/logo.png")
    except Exception as exception:
        print(f"{exception.__class__.__name__}: {str(exception)}")
        continue

    lent = Lent(lent_image)
    button = Button(
        *create_lent_button_images(logo_image),
        ((area_between_icons_x + icon_width) * i + left_offset, top_offset),
    )

    with open(f'data/lents/lent_{i + 1}/pos.txt', 'r') as file:
        button.set_pos(*map(int, file.read().split(',')))

    buttons_and_lents.append((lent, button))

buttons_and_lents[1][0].add_links(
    ("Начало", 0), ("Заводы", 7217), ("Инвестиции", 11689))
buttons_and_lents[0][0].add_links(
    ("Данные", 2610), ("История", 3838), ("Особенности", 8215))

chronicle_blocks = []
blocks_paths = [str(path) for path in Path("data/chronicle/blocks").iterdir()]
for path in blocks_paths:
    image = load_image(path, (255, 255, 255))
    rect = pygame.Rect(0, top_offset, image.get_width(), image.get_height())
    rect.centerx = WIDTH // 2
    if chronicle_blocks:
        rect.y = chronicle_blocks[-1]["rect"].bottom + area_between_icons_y
    chronicle_blocks.append({
        "image": image,
        "rect": rect
    })

logo_image = load_alpha_image(f"data/chronicle/logo.png")

button = Button(
    *create_lent_button_images(logo_image),
    (0, 0),
)

with open(f'data/chronicle/pos.txt', 'r') as file:
    button.set_pos(*map(int, file.read().split(',')))

buttons_and_lents.append((Chronicle(chronicle_blocks), button))

sliding_size = max([button.rect.bottom for _, button in buttons_and_lents]) - 1080 + top_offset
sliding_size = max(sliding_size, 0)

button_exit = TextButton(" ", (WIDTH - 28, 10))

# creating menu button sign
menu_sign = pygame.Surface((panel_width, bottom_offset))
menu_sign.fill((20, 20, 20))

menu_sign_pressed = pygame.Surface((panel_width, bottom_offset))
menu_sign_pressed.fill((30, 30, 30))

three_line_menu_offset = 20
three_line_menu_width = 45
for surf in (menu_sign, menu_sign_pressed):
    pygame.draw.line(
        surf,
        LIGHT_GREY,
        (
            panel_width // 2 - three_line_menu_width,
            bottom_offset // 2 - three_line_menu_offset,
        ),
        (
            panel_width // 2 + three_line_menu_width,
            bottom_offset // 2 - three_line_menu_offset,
        ),
        5,
    )
    pygame.draw.line(
        surf,
        LIGHT_GREY,
        (panel_width // 2 - three_line_menu_width, bottom_offset // 2),
        (panel_width // 2 + three_line_menu_width, bottom_offset // 2),
        5,
    )
    pygame.draw.line(
        surf,
        LIGHT_GREY,
        (
            panel_width // 2 - three_line_menu_width,
            bottom_offset // 2 + three_line_menu_offset,
        ),
        (
            panel_width // 2 + three_line_menu_width,
            bottom_offset // 2 + three_line_menu_offset,
        ),
        5,
    )

button_open_panel = Button(
    menu_sign, menu_sign_pressed, (0, HEIGHT - bottom_offset))

# creating back button sign
back_sign_width = 30

back_sign = pygame.Surface((panel_width, bottom_offset))
back_sign.fill((20, 20, 20))

back_sign_pressed = pygame.Surface((panel_width, bottom_offset))
back_sign_pressed.fill((30, 30, 30))

for sign_surf in (back_sign, back_sign_pressed):
    width = 70
    thickness = 3
    surf = pygame.Surface((width, width))
    surf.set_colorkey((0, 0, 0))
    pygame.draw.rect(surf, LIGHT_GREY, (width // 2 - thickness,
                     0, thickness * 2, width // 2 + thickness))
    pygame.draw.rect(surf, LIGHT_GREY, (width // 2 - thickness,
                     width // 2 - thickness, width // 2 + thickness, thickness * 2))
    surf = pygame.transform.rotate(surf, -45)

    hypot_offset = hypot(width, width) // 8
    sign_surf.blit(surf, (panel_width // 2 - surf.get_width() //
                   2 - hypot_offset, bottom_offset // 2 - surf.get_height() // 2))

button_close_lent = Button(
    back_sign, back_sign_pressed, (WIDTH - panel_width, HEIGHT - bottom_offset)
)

speed = 100

panel = Panel()

finger = Finger(FPS)


def lent_menu(lent: Lent):
    auto_scroll = 0
    auto_scroll_speed = 2

    while True:
        display.fill(BLACK)

        finger_pos = pygame.mouse.get_pos()

        finger_motion = (0, 0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # finger_down_pos = (event.x * WIDTH, event.y * HEIGHT)
                finger_down_pos = event.pos
                finger.down(finger_down_pos)

            if event.type == pygame.MOUSEBUTTONUP:
                # finger_pos = (event.x * WIDTH, event.y * HEIGHT)
                finger_pos = event.pos
                finger.up(finger_pos)

            if event.type == pygame.MOUSEMOTION:
                # finger_motion = (event.dx * WIDTH, event.dy * HEIGHT)
                finger_motion = event.rel
        finger.motion(finger_motion)

        if panel.is_opened:
            frame_rect = pygame.Rect(
                panel_width + 1, 0,
                WIDTH - panel_width,
                HEIGHT - bottom_offset
            )
        else:
            frame_rect = pygame.Rect(0, 0, WIDTH, HEIGHT - bottom_offset)

        finger.update(frame_rect)
        clicked = finger.is_clicked()

        scroll = 0
        if finger.is_press_in_frame():
            scroll = -finger.get_scroll()
        scroll -= finger.get_inertion_scroll()

        lent.update(scroll + auto_scroll)
        button_open_panel.update(finger_pos, clicked)
        panel_bg = lent.cropped.subsurface(
            0, 0, panel_width, HEIGHT - bottom_offset)

        panel.update(finger_pos, clicked, panel_bg)
        button_close_lent.update(finger_pos, clicked)

        if button_open_panel.triggered():
            panel.is_opened = not panel.is_opened

        if button_close_lent.triggered():
            lent.reset()
            panel.close()
            finger.reset()
            break

        if panel.is_opened:
            if panel.auto_scroll_button.triggered():
                auto_scroll = auto_scroll_speed - auto_scroll
                panel.close()
                # panel.auto_scroll_button.clicked = False

            for link_button, scroll_num in lent.links:
                link_button.update(finger_pos, clicked)
                if link_button.triggered():
                    lent.animation(scroll_num)
                    scroll = 0
                    panel.is_opened = False
                    auto_scroll = 0

        if (auto_scroll and lent.is_end) or \
                (finger.finger_down and finger.is_press_in_frame()):
            auto_scroll = 0

        # pygame.draw.rect(display, (255, 255, 255), frame_rect, 5)

        screen.blit(display, (screen_offset_x, screen_offset_y))
        pygame.display.update()
        clock.tick(FPS)


def main_menu():
    while True:
        display.fill((0, 0, 0))

        display.blit(
            background_image,
            (0, 0)
        )
        # screen.blit(module_net, (0, 0))

        finger_pos = pygame.mouse.get_pos()

        finger_motion = (0, 0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # finger_down_pos = (event.x * WIDTH, event.y * HEIGHT)
                finger_down_pos = event.pos
                finger.down(finger_down_pos)

            if event.type == pygame.MOUSEBUTTONUP:
                # finger_pos = (event.x * WIDTH, event.y * HEIGHT)
                finger_pos = event.pos
                finger.up(finger_pos)

            if event.type == pygame.MOUSEMOTION:
                # finger_motion = (event.dx * WIDTH, event.dy * HEIGHT)
                finger_motion = event.rel
        finger.motion(finger_motion)

        frame_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        finger.update(frame_rect)
        clicked = finger.is_clicked()

        scroll = 0
        if finger.is_press_in_frame():
            scroll = -finger.get_scroll()
        scroll -= finger.get_inertion_scroll()

        for lent, button in buttons_and_lents:
            button.update(finger_pos, clicked, scroll)
            if button.triggered():
                finger.reset()
                lent_menu(lent)

        button_exit.update(finger_pos, clicked)

        if button_exit.triggered():
            break

        screen.blit(display, (screen_offset_x, screen_offset_y))
        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main_menu()
