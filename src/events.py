from typing import *

from enum import Enum, auto
from dataclasses import dataclass

from . import ecs

@dataclass
class RenderTickEvent(ecs.Event):
    dt: int

@dataclass
class PhysicsTickEvent(ecs.Event):
    pass

@dataclass
class BehaviourTickEvent(ecs.Event):
    pass

@dataclass
class UserInputEvent(ecs.Event):
    def __init__(self, keys: List[int]):
        self.keys = keys