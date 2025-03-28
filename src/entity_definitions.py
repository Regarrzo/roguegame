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
            components.SimpleHostileBehaviourComponent(sight_range=5),
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

def healmarker(healing) -> Iterable[ecs.Component]:
    return (components.FloatingTextComponent(str(healing), (0, 255, 0, 100)),
            components.RealtimeLifetimeComponent(pygame.time.get_ticks(), 500))



def water(player_only=True, heal_amount=2) -> Iterable[ecs.Component]:
    return (components.SpriteComponent(os.path.join("res", "imgs", "water.png")),
            components.PickupComponent(player_only, heal_amount))

def stairs(player_only=True, heal_amount=100, nextlevel_switch=True) -> Iterable[ecs.Component]:
    return (components.SpriteComponent(os.path.join("res", "imgs", "stairs.png")),
            components.PickupComponent(player_only, heal_amount, nextlevel_switch=True))


def bar_text(text="Not set.", color=(255, 255, 255)):
    return (components.BarTextComponent(text, color),)