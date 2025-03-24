from typing import *

from . import ecs
from . import components
from . import tiles
from . import events
from . import util

class PhysicsSystem(ecs.System):
    def __init__(self):
        pass

    def pos_is_free(self, em: ecs.TilemapEcs, pos: Tuple[int, int]):
        return em.tilemap.pos_is_in_bounds((pos)) and not em.tilemap[pos].is_collider() and not any(e.has_component(em, components.CollisionComponent) for e in em.get_entities_at(pos))

    def process(self, em: ecs.TilemapEcs, event: events.PhysicsTickEvent):
        moving = em.query_all_with_components(components.MovementActionComponent)
        
        for entity in moving:
            dy, dx = em.get_components(entity)[components.MovementActionComponent]
            old_y, old_x =  em.get_pos(entity)
            new_pos = old_y + dy, old_x + dx

            if self.pos_is_free(em, new_pos):
                em.move_entity(entity, new_pos)

            em.remove_components(entity, components.MovementActionComponent)