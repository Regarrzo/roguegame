'''
Finished component collections to add to the game world.
'''
from typing import *

from . import configuration
from . import ecs
from . import components

def make_player(y: int, x: int) -> Iterable[Any]:
    return (components.PositionComponent(y, x), 
            components.PlayerControlComponent(), 
            components.SpriteComponent(configuration.PLAYER_IMAGE_KEY),
            )