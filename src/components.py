from typing import *
from enum import Enum, auto
from dataclasses import dataclass, asdict

from . import tiles

@dataclass
class PositionComponent:
    y: int
    x: int

    def __iter__(self):
        return iter(asdict(self).values())

@dataclass
class SpriteComponent:
    img_key: str
    z_index: int = 0

    def __iter__(self):
        return iter(asdict(self).values())
    
@dataclass
class TilemapComponent:
    data: List[List[tiles.Tile]]
    tile_resource_map: Dict[tiles.Tile, str]

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
class CollisionComponent:
    tile_colliders: Set[tiles.Tile]