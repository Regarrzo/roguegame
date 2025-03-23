from . import ecs
from . import components
from . import tiles
from . import events
from . import util

class PhysicsSystem(ecs.System):
    def __init__(self):
        pass

    def process(self, entity_manager: ecs.ECS, event: events.PhysicsTickEvent):
        moving = entity_manager.query_all_with_components(components.MovementActionComponent, components.PositionComponent)
        tm_comp = entity_manager.query_single_with_component(components.TilemapComponent)[components.TilemapComponent]

        for entity in moving:
            dy, dx = entity[components.MovementActionComponent]
            old_y, old_x =  entity[components.PositionComponent]
            new_y, new_x = old_y + dy, old_x + dx

            if util.is_in_2dgrid_bounds(tm_comp.data, (new_y, new_x)) and tm_comp.data[new_y][new_x] not in tm_comp.tile_colliders:
                # valid move
                entity[components.PositionComponent].y = new_y
                entity[components.PositionComponent].x = new_x

            del entity[components.MovementActionComponent]