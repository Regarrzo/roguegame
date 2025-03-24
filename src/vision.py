
from . import ecs
from . import components
from . import tiles
from . import events
from . import util

class VisionSystem(ecs.System):
    def __init__(self):
        pass

    def process(self, em: ecs.TilemapEcs, event: events.PhysicsTickEvent):
        moving = em.query_all_with_components(components.MovementActionComponent)
        
        for entity in moving:
            dy, dx = em.get_components(entity)[components.MovementActionComponent]
            old_y, old_x =  em.get_pos(entity)
            new_pos = old_y + dy, old_x + dx

            if em.tilemap.pos_is_in_bounds((new_pos)) and not em.tilemap[new_pos].is_collider():
                # valid move
                em.move_entity(entity, new_pos)

            em.remove_components(entity, components.MovementActionComponent)