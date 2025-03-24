import os
import pygame
from . import components

WINDOW_DIMS = 32 * 32, 32 * 32
TARGET_FPS = 60
RESOURCES_PATH = "res"
SCALE = 32
KEY_MAP = {
    pygame.K_SPACE: components.IdleActionComponent(),
    pygame.K_UP: components.MovementActionComponent(-1, 0),
    pygame.K_DOWN: components.MovementActionComponent(1, 0),
    pygame.K_RIGHT: components.MovementActionComponent(0, 1),
    pygame.K_LEFT: components.MovementActionComponent(0, -1)
}
