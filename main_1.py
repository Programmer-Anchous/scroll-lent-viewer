import pygame
import sys

from random import randrange
from tools import *


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

clock = pygame.time.Clock()
FPS = 80

bottom_offset = 100
panel_width = 300

font = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)
font_big = pygame.font.Font(None, 48)

background_image = pygame.image.load("data/bg.png").convert()

scr_w, scr_h = screen.get_size()
bg_w, bg_h = background_image.get_size()

if scr_w > bg_w:
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


def sign(num):
    if num < 0:
        return -1
    if num == 0:
        return 0
    return 1


class Button:
    def __init__(self, image, image_pressed, coords, center=False):
        self.image = image
        self.image_pressed = image_pressed
        if center:
            self.rect = image.get_rect(center=coords)
        else:
            self.rect = image.get_rect(topleft=coords)

        self.clicked = False

    def update(self, mouse_pos, click):
        self.clicked = False
        if self.rect.collidepoint(mouse_pos):
            current_image = self.image_pressed
            if click:
                self.clicked = True
        else:
            current_image = self.image
        screen.blit(current_image, self.rect)

    def triggered(self) -> bool:
        return self.clicked


class TextButton(Button):
    def __init__(self, text, coords, center=False, font_=font):
        image = font_.render(text, True, LIGHT_GREY)
        image_pressed = font_.render(text, True, WHITE)
        super().__init__(image, image_pressed, coords, center)


class Lent:
    def __init__(self, filename: str):
        self.image = pygame.image.load(filename).convert()
        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()

        # coeff = 1080 / self.image_width
        # self.image = pygame.transform.scale(self.image, (self.image_width * coeff, self.image_height * coeff))
        # self.image_width = self.image.get_width()
        # self.image_height = self.image.get_height()

        self.coord_x = 100
        self.scroll = 0
        self.offset = 0

        self.is_start = True
        self.is_end = False

    def update(self, movement):
        screen_h = screen.get_height()

        if not (self.is_start or self.is_end):
            self.scroll += movement
            if self.scroll < 0:
                self.scroll = 0
                self.is_start = True
            elif self.scroll > (self.image_height - screen_h + bottom_offset):
                self.scroll = self.image_height - screen_h + bottom_offset
                self.is_end = True

        elif self.is_start:
            self.coord_x -= movement

            if self.coord_x > self.offset:
                self.coord_x = self.offset

            elif self.coord_x < 0:
                self.coord_x = 0
                self.is_start = False

        elif self.is_end:
            self.coord_x -= movement

            if self.coord_x < -self.offset:
                self.coord_x = -self.offset

            elif self.coord_x > 0:
                self.coord_x = 0
                self.is_end = False

        cropped = self.image.subsurface(
            (0, self.scroll, self.image_width, screen_h - bottom_offset)
        )
        screen.blit(
            cropped, (screen.get_width() // 2 - cropped.get_width() // 2, self.coord_x)
        )


class Panel:
    def __init__(self):
        self.width = panel_width
        self.surf = pygame.Surface((self.width, HEIGHT - bottom_offset))
        self.surf.set_alpha(200)
        self.is_opened = False

        self.auto_scroll_button = TextButton(
            "auto", (panel_width // 2, screen.get_height() // 2 - 50), True, font_big
        )
        self.button_exit = TextButton(
            "back", (panel_width // 2, screen.get_height() - 40), True, font_big
        )

    def update(self, mouse_pos, click):
        if self.is_opened:
            screen.blit(self.surf, (0, 0))
            self.auto_scroll_button.update(mouse_pos, click)
            # self.button_exit.update(mouse_pos, click)

    def is_mouse_in_panel(self, mx, my):
        return mx < self.width

    def open(self):
        self.is_opened = True

    def close(self):
        self.is_opened = False


icon_width = 400
area_between_icons = 60


def create_lent_button_images(logo_path):
    b_surf = pygame.image.load(logo_path).convert()
    frame_color = get_frame_color(b_surf)
    pygame.draw.rect(b_surf, frame_color, (0, 0, 400, 400), 5)
    b_surf_pressed = b_surf.copy()

    average_c = sum(frame_color) // 3
    dark_surf = pygame.Surface((400, 400))
    dark_surf.set_alpha(average_c // 10)
    b_surf.blit(dark_surf, (0, 0))

    return b_surf, b_surf_pressed


r, g, b = randrange(100, 170), randrange(100, 170), randrange(100, 170)
b2_surf = pygame.Surface((icon_width, icon_width))
b2_surf.fill((r, g, b))

b2_surf_pressed = pygame.Surface((icon_width, icon_width))
b2_surf_pressed.fill((r + 15, g + 15, b + 15))


r, g, b = randrange(100, 170), randrange(100, 170), randrange(100, 170)
b3_surf = pygame.Surface((icon_width, icon_width))
b3_surf.fill((r, g, b))

b3_surf_pressed = pygame.Surface((icon_width, icon_width))
b3_surf_pressed.fill((r + 15, g + 15, b + 15))


r, g, b = randrange(100, 170), randrange(100, 170), randrange(100, 170)
b4_surf = pygame.Surface((icon_width, icon_width))
b4_surf.fill((r, g, b))

b4_surf_pressed = pygame.Surface((icon_width, icon_width))
b4_surf_pressed.fill((r + 15, g + 15, b + 15))
del r, g, b

button_lents = [
    (
        Button(*create_lent_button_images("data/industry_logo.png"), (area_between_icons, 60)),
        Lent("data/lent2.png"),
    ),
    (
        Button(b2_surf, b2_surf_pressed, (area_between_icons * 2 + icon_width, 60)),
        Lent("data/lent1.png"),
    ),
    (
        Button(b3_surf, b3_surf_pressed, (area_between_icons * 3 + icon_width * 2, 60)),
        Lent("data/lent.png"),
    ),
    (
        Button(b4_surf, b4_surf_pressed, (area_between_icons * 4 + icon_width * 3, 60)),
        Lent("data/lent2.png"),
    ),
]

button_exit = TextButton("exit", (10, screen.get_height() - 30))

menu_sign = pygame.Surface((panel_width, 100))
menu_sign.fill((20, 20, 20))

menu_sign_pressed = pygame.Surface((panel_width, 100))
menu_sign_pressed.fill((30, 30, 30))

three_line_menu_offset = 25
three_line_menu_width = 45
for surf in (menu_sign, menu_sign_pressed):
    pygame.draw.line(
        surf,
        LIGHT_GREY,
        (panel_width // 2 - three_line_menu_width, bottom_offset // 2 - three_line_menu_offset),
        (panel_width // 2 + three_line_menu_width, bottom_offset // 2 - three_line_menu_offset),
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
        (panel_width // 2 - three_line_menu_width, bottom_offset // 2 + three_line_menu_offset),
        (panel_width // 2 + three_line_menu_width, bottom_offset // 2 + three_line_menu_offset),
        5,
    )

button_open_panel = Button(menu_sign, menu_sign_pressed, (0, HEIGHT - 100))

back_sign = pygame.Surface((panel_width, 100))
back_sign.fill((20, 20, 20))

back_sign_pressed = pygame.Surface((panel_width, 100))
back_sign_pressed.fill((30, 30, 30))

for surf in (back_sign, back_sign_pressed):
    pygame.draw.line(
        surf,
        LIGHT_GREY,
        (panel_width // 2 - three_line_menu_width, bottom_offset // 2),
        (panel_width // 2 + three_line_menu_width, bottom_offset // 2),
        5
    )
    pygame.draw.line(
        surf,
        LIGHT_GREY,
        (panel_width // 2 - three_line_menu_width, bottom_offset // 2),
        (panel_width // 2, bottom_offset // 2 - 25),
        6
    )
    pygame.draw.line(
        surf,
        LIGHT_GREY,
        (panel_width // 2 - three_line_menu_width, bottom_offset // 2),
        (panel_width // 2, bottom_offset // 2 + 25),
        6
    )

button_close_lent = Button(back_sign, back_sign_pressed, (WIDTH - panel_width, HEIGHT - 100))

author_label = font_small.render("Made by Anchous Production", True, WHITE)

speed = 100

panel = Panel()

pygame.mouse.set_visible(False)

def draw_mouse(mx, my):
    pygame.draw.circle(screen, (0, 0, 240), (mx, my), 20)
    pygame.draw.circle(screen, (240, 240, 0), (mx, my), 20, 3)


def lent_menu(lent):
    auto_scroll = 0
    auto_scroll_speed = 1
    background_image.set_alpha(50)

    is_drag = False
    scroll = 0

    prev_mouse_pos = [0, 0]
    while True:
        screen.fill(BLACK)

        # decrease the scroll value by 1 toward zero
        scroll = (abs(scroll) - 1) * sign(scroll)
        flag = False

        mx, my = pygame.mouse.get_pos()

        if is_drag:
            y_movement = prev_mouse_pos[1] - my
            if y_movement != 0:
                scroll = y_movement

        prev_mouse_pos = mx, my

        clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = True
                    flag = True
                if event.button == 4:
                    scroll = -speed
                if event.button == 5:
                    scroll = speed

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_drag = False

        lent.update(scroll + auto_scroll)
        button_open_panel.update((mx, my), clicked)
        panel.update((mx, my), clicked)

        # check if opening panel or pressing button on it
        if my < (HEIGHT - bottom_offset):
            if panel.auto_scroll_button.triggered():
                auto_scroll = auto_scroll_speed - auto_scroll
                flag = False

            if (
                flag
                and clicked
                and not (panel.is_mouse_in_panel(mx, my) and panel.is_opened)
            ):
                is_drag = True
                auto_scroll = 0
        else:
            if button_open_panel.triggered():
                panel.is_opened = not panel.is_opened
        
        # check if closing lent
        button_close_lent.update((mx, my), clicked)
        if button_close_lent.triggered():
            break

        draw_mouse(mx, my)

        pygame.display.update()
        clock.tick(FPS)


def main_menu():
    background_image.set_alpha(100)
    while True:
        screen.fill((0, 0, 0))

        screen.blit(
            background_image,
            (
                screen.get_width() // 2 - background_image.get_width() // 2,
                screen.get_height() // 2 - background_image.get_height() // 2,
            ),
        )

        screen.blit(author_label, (screen.get_width() - 260, screen.get_height() - 30))

        mx, my = pygame.mouse.get_pos()

        clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = True

        for button, lent in button_lents:
            button.update((mx, my), clicked)
            if button.triggered():
                lent_menu(lent)
                background_image.set_alpha(100)

        button_exit.update((mx, my), clicked)

        if button_exit.triggered():
            break

        draw_mouse(mx, my)

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main_menu()
