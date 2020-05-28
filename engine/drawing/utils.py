from ..rt.image import Image

def clear(image: Image, color=(0,0,0)):
    for y in range(image.height):
        for x in range(image.width):
            image[x, y] = color