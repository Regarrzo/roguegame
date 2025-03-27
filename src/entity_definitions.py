'''
Finished component collections to add to the game world.
'''
from typing import *
import os
import pygame
from . import configuration
from . import ecs
from . import components

def player() -> Iterable[ecs.Component]:
    return (components.PlayerControlComponent(), 
            components.SpriteComponent(os.path.join("res", "imgs", "player.png")),
            components.CollisionComponent(),
            components.HealthComponent(10),
            components.MeleeAttackComponent(2),
            components.FleeVulnerabilityComponent()
            )

def rat() -> Iterable[Any]:
    return (components.DumbPeacefulBehaviourComponent(), 
            components.SpriteComponent(os.path.join("res", "imgs", "rat.png")),
            components.CollisionComponent(),
            components.HealthComponent(1)
            )

def goblin() -> Iterable[ecs.Component]:
    return (components.SpriteComponent(os.path.join("res", "imgs", "goblin.png")),
            components.CollisionComponent(),
            components.SimpleHostileBehaviourComponent(sight_range=10),
            components.PathfindTargetComponent(),
            components.HealthComponent(3),
            components.MeleeAttackComponent(1)
        )

def corpse() -> Iterable[ecs.Component]:
    return (components.SpriteComponent(os.path.join("res", "imgs", "dead.png"), z_index=-1),
        )
        

def hitmarker(damage) -> Iterable[ecs.Component]:
    return (components.FloatingTextComponent(str(damage), (255, 0, 0, 100)),
            components.RealtimeLifetimeComponent(pygame.time.get_ticks(), 500))
