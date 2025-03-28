import os
import pygame
from . import components

DUNGEON_DIMS = 32, 32
SCALE = 32
WINDOW_DIMS = DUNGEON_DIMS[1] * SCALE, DUNGEON_DIMS[0] * SCALE + 40
TARGET_FPS = 60
RESOURCES_PATH = "res"
KEY_MAP = {
    pygame.K_SPACE: components.IdleActionComponent(),
    pygame.K_UP: components.MovementActionComponent(-1, 0),
    pygame.K_DOWN: components.MovementActionComponent(1, 0),
    pygame.K_RIGHT: components.MovementActionComponent(0, 1),
    pygame.K_LEFT: components.MovementActionComponent(0, -1)
}
