from PIL import Image
from pygame import image


def average_color(img):
    # convert pygame.Surfac -> PIL.Image
    strFormat = 'RGBA'
    raw_str = image.tostring(img, strFormat, False)
    pil_image = Image.frombytes(strFormat, img.get_size(), raw_str)

    r = g = b = 0
    pixels_im = pil_image.load()
    x, y = pil_image.size
    amount = x * y

    for i in range(x):
        for j in range(y):
            colors = list(pixels_im[i, j])
            r += colors[0]
            g += colors[1]
            b += colors[2]
    
    return (r // amount, g // amount, b // amount)


def negative_color(color):
    return tuple(map(lambda x: 255 - x, color))


def get_frame_color(img):
    return negative_color(average_color(img))

def load_image(file_path):
    return image.load(file_path).convert()