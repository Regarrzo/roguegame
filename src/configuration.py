import os
import pygame
from . import components

SCALE = 64
WINDOW_DIMS = 16 * SCALE, 16 * SCALE
TARGET_FPS = 60
RESOURCES_PATH = "res"
KEY_MAP = {
    pygame.K_SPACE: components.IdleActionComponent(),
    pygame.K_UP: components.MovementActionComponent(-1, 0),
    pygame.K_DOWN: components.MovementActionComponent(1, 0),
    pygame.K_RIGHT: components.MovementActionComponent(0, 1),
    pygame.K_LEFT: components.MovementActionComponent(0, -1)
}
