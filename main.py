import pygame
import sys


ORANGE = (200, 140, 40)
WHITE = (200,) * 3
GREY = (25,) * 3
MEDIUM_GREY = (100,) * 3
LIGHT_GREY = (160,) * 3
BLACK = (15,) * 3


pygame.init()

infoObject = pygame.display.Info()
screen = pygame.display.set_mode(
    (infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN
)

clock = pygame.time.Clock()
FPS = 80


font = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

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
    def __init__(self, text, coords, center=False):
        image = font.render(text, True, LIGHT_GREY)
        image_pressed = font.render(text, True, WHITE)
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
            elif self.scroll > (self.image_height - screen_h):
                self.scroll = self.image_height - screen_h
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

        cropped = self.image.subsurface((0, self.scroll, self.image_width, screen_h))
        screen.blit(
            cropped, (screen.get_width() // 2 - cropped.get_width() // 2, self.coord_x)
        )


class Pannel:
    def __init__(self):
        self.width = 200
        self.image = pygame.Surface((self.width, screen.get_height()))
        self.image.fill(GREY)
        pygame.draw.line(
            self.image,
            MEDIUM_GREY,
            (self.image.get_width() - 1, 0),
            (self.image.get_width() - 1, self.image.get_height()),
            3,
        )
        pygame.draw.line(
            self.image,
            MEDIUM_GREY,
            (self.image.get_width() - 40, 0),
            (self.image.get_width() - 40, self.image.get_height()),
            2,
        )
        self.image.set_alpha(220)

        arrow = pygame.image.load("data/arrow.png").convert()
        arrow_pressed = pygame.image.load("data/arrow_pressed.png").convert()

        surf = pygame.Surface((40, screen.get_height()))
        surf.fill((255, 255, 255))
        surf.set_colorkey((255, 255, 255))
        surf_pressed = surf.copy()

        surf.blit(
            arrow,
            (
                surf.get_width() // 2 - arrow.get_width() // 2,
                surf.get_height() // 2 - arrow.get_height() // 2,
            ),
        )

        surf_pressed.blit(
            arrow_pressed,
            (
                surf_pressed.get_width() // 2 - arrow_pressed.get_width() // 2,
                surf_pressed.get_height() // 2 - arrow_pressed.get_height() // 2,
            ),
        )
        self.open_button = Button(surf, surf_pressed, (0, 0))
        self.close_button = Button(
            pygame.transform.flip(surf, True, False),
            pygame.transform.flip(surf_pressed, True, False),
            (160, 0),
        )

        self.opened_rect = self.image.get_rect(topleft=(0, 0))

        self.auto_scroll_button = TextButton("auto", (80, screen.get_height() // 2 - 50), True)

        self.button_exit = TextButton("back", (80, screen.get_height() - 40), True)

        self.is_opened = False
        self.close = False

    def update(self, mouse_pos, click):
        if not pygame.mouse.get_visible() or (mouse_pos[0] > 400 and not self.is_opened):
            return
        
        self.close = False
        if self.is_opened:
            screen.blit(self.image, (0, 0))
            self.close_button.update(mouse_pos, click)
            self.button_exit.update(mouse_pos, click)
            self.auto_scroll_button.update(mouse_pos, click)
        else:
            screen.blit(self.image, (-160, 0))
            self.open_button.update(mouse_pos, click)

        if self.close_button.triggered():
            self.close_button.update(mouse_pos, click)
            self.is_opened = False

        if self.open_button.triggered():
            self.open_button.update(mouse_pos, click)
            self.is_opened = True

        if self.button_exit.triggered():
            self.close = True

    def is_closing(self):
        close = self.close
        self.close = False
        return close
    
    def is_mouse_in_pannel(self, mx, my):
        return (pannel.is_opened and pannel.opened_rect.collidepoint(mx, my) or pannel.close_button.triggered() or pannel.open_button.triggered())


button_lents = [
    (
        TextButton("lent 1", (screen.get_width() // 2 - 60, screen.get_height() - 600)),
        Lent("data/lent.png"),
    ),
    (
        TextButton("lent 2", (screen.get_width() // 2 - 60, screen.get_height() - 550)),
        Lent("data/lent1.png"),
    ),
    (
        TextButton("lent 3", (screen.get_width() // 2 - 60, screen.get_height() - 500)),
        Lent("data/lent2.bmp"),
    ),
]

button_exit = TextButton(
    "exit", (screen.get_width() // 2, screen.get_height() - 300), True
)

author_label = font_small.render("Made by Anchous Production", True, WHITE)

speed = 100

pannel = Pannel()


def lent_menu(lent):
    auto_scroll = 0
    auto_scroll_speed = 1
    background_image.set_alpha(50)
    mouse_counter = 0
    mouse_limit = FPS * 1.5  # time after which the mouse won't be visible(1.5 seconds)

    is_drag = False
    scroll = 0

    prev_mouse_pos = [0, 0]
    while True:
        screen.fill(BLACK)

        # decrease the scroll value by 1 toward zero
        scroll = (abs(scroll) - 1) * sign(scroll)
        flag = False

        mx, my = pygame.mouse.get_pos()
        if (mx, my) != prev_mouse_pos:
            mouse_counter = 0
            pygame.mouse.set_visible(True)
        else:
            mouse_counter += 1
            if mouse_counter > mouse_limit:
                pygame.mouse.set_visible(False)
                mouse_counter = mouse_limit
        
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

        if pannel.auto_scroll_button.triggered():
            auto_scroll = auto_scroll_speed - auto_scroll
            flag = False

        if pannel.is_closing():
            break
        
        lent.update(scroll + auto_scroll)
        pannel.update((mx, my), clicked)

        if flag and clicked and not pannel.is_mouse_in_pannel(mx, my):
            is_drag = True
            auto_scroll = 0

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
            pygame.draw.line(
                screen,
                LIGHT_GREY,
                (screen.get_width() // 2 - 200, button.rect.y + 30),
                (screen.get_width() // 2 + 200, button.rect.y + 30),
                1,
            )
            if button.triggered():
                lent_menu(lent)
                background_image.set_alpha(100)

        button_exit.update((mx, my), clicked)

        if button_exit.triggered():
            break

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main_menu()
