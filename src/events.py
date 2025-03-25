from typing import *

from enum import Enum, auto
from dataclasses import dataclass

from . import ecs

@dataclass
class RenderTickEvent(ecs.Event):
    dt: int
    mouse_pos: Tuple[int, int]
    left_click: bool

@dataclass
class PhysicsTickEvent(ecs.Event):
    pass

@dataclass
class AfterPhysicsTickEvent(ecs.Event):
    pass


@dataclass
class BehaviourTickEvent(ecs.Event):
    pass

@dataclass
class UserInputEvent(ecs.Event):
    keys: List[int]

@dataclass
class UserHoversTileWithMouseEvent(ecs.Event):
    pos: Tuple[int, int]

@dataclass
class UserClicksTileWithMouseEvent(ecs.Event):
    pos: Tuple[int, int]

@dataclass
class GamestepEvent(ecs.Event):
    pass