from pygame import image


def load_image(file_path):
    return image.load(file_path).convert()


def load_alpha_image(file_path):
    return image.load(file_path).convert_alpha()


def sign(num: int | float):
    if num < 0:
        return -1
    if num == 0:
        return 0
    return 1
