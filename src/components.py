from typing import *
from enum import Enum, auto
from dataclasses import dataclass, asdict

from . import tiles

@dataclass
class SpriteComponent:
    img_key: str
    z_index: int = 0

    def __iter__(self):
        return iter(asdict(self).values())
    
@dataclass
class PlayerControlComponent:
    pass


@dataclass
class MovementActionComponent:
    dy: int = 0
    dx: int = 0

    def __iter__(self):
        return iter(asdict(self).values())

@dataclass
class IdleActionComponent:
    pass

@dataclass
class RandomMoveBehaviourComponent:
    pass
