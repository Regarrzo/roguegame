import pygame
import os

import pygame.freetype

def scale_image(img: pygame.surface.Surface, scale):
    width, height = img.get_size()
    return pygame.transform.scale(img, (scale, scale))

def _load_images(path: str, scale=2):
    imgs = {}
    for folder, subs, files in os.walk(path):
        for f in files:
            key = os.path.join(folder, f)
            imgs[key] = scale_image(pygame.image.load(key), scale)
    return imgs

def _load_fonts(path: str, text_size=24):
    imgs = {}
    for folder, subs, files in os.walk(path):
        for f in files:
            key = os.path.join(folder, f)
            imgs[key] = pygame.font.Font(key, text_size)
    return imgs


def load_res(path: str, tile_scale=16) -> dict:
    '''
    Load all resources necessary for the game to work and return them as a dictionary mapping resource paths to the actual resource.
    '''
    return _load_images(os.path.join(path, "imgs"), scale=tile_scale) | _load_fonts(os.path.join(path, "fonts"), text_size=50)
