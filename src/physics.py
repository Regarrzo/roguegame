from . import ecs
from . import components
from . import tiles
from . import events
from . import util

class PhysicsSystem(ecs.System):
    def __init__(self):
        pass

    def process(self, em: ecs.TilemapEcs, event: events.PhysicsTickEvent):
        moving = em.query_all_with_components(components.MovementActionComponent, components.PositionComponent)
        
        for entity in moving:
            dy, dx = entity[components.MovementActionComponent]
            old_y, old_x =  entity[components.PositionComponent]
            new_y, new_x = old_y + dy, old_x + dx

            if em.tilemap.pos_is_in_bounds((new_y, new_x)) and not em.tilemap[new_y, new_x].is_collider():
                # valid move
                entity[components.PositionComponent].y = new_y
                entity[components.PositionComponent].x = new_x

            del entity[components.MovementActionComponent]