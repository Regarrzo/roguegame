'''
Finished component collections to add to the game world.
'''
from typing import *
import os

from . import configuration
from . import ecs
from . import components

def player() -> Iterable[ecs.Component]:
    return (components.PlayerControlComponent(), 
            components.SpriteComponent(os.path.join("res", "imgs", "player.png")),
            components.CollisionComponent()
            )

def rat() -> Iterable[Any]:
    return (components.DumbPeacefulBehaviourComponent(), 
            components.SpriteComponent(os.path.join("res", "imgs", "rat.png")),
            components.CollisionComponent()
            )

def goblin() -> Iterable[ecs.Component]:
    return (components.SpriteComponent(os.path.join("res", "imgs", "goblin.png")),
            components.CollisionComponent(),
            components.SimpleHostileBehaviourComponent(sight_range=10),
            components.PathfindTargetComponent()
        )