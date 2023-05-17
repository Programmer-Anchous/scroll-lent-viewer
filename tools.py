from pygame import image


def load_image(file_path):
    return image.load(file_path).convert()


def load_alpha_image(file_path):
    return image.load(file_path).convert_alpha()
