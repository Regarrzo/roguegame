from typing import *
import pygame
from . import ecs
from . import components
from . import tiles
from . import events
from . import util
from . import entity_definitions

class CleanupDeadSystem(ecs.System):
    def __init__(self):
        pass
        
    def process(self, em: ecs.TilemapEcs, event: events.AfterPhysicsTickEvent):
        can_die = em.query_all_with_components(components.HealthComponent)
        died = []

        for entity in can_die:
            health: int = entity.get_component(em, components.HealthComponent).health

            if health < 1:
                died.append(entity)

        for dead in died:
            dead_pos = em.get_pos(dead)
            em.create_entity(dead_pos, *entity_definitions.corpse())
            em.remove_entity(dead)
            
        can_expire = em.query_all_with_components(components.RealtimeLifetimeComponent)
        expired = []
        for entity in can_expire:
            lifetime: components.RealtimeLifetimeComponent = entity.get_component(em, components.RealtimeLifetimeComponent)
            
            if lifetime.created + lifetime.lifetime < pygame.time.get_ticks():
                expired.append(entity)

        for entity in expired:
            em.remove_entity(entity)