from . import ecs
from . import components
from . import tiles
from . import events

class PhysicsSystem(ecs.System):
    def __init__(self):
        pass

    def process(self, entity_manager: ecs.ECS, event: events.LogicTickEvent):
        moving = entity_manager.query_all_with_components(components.MovementActionComponent, components.PositionComponent)

        for entity in moving:
            dy, dx = entity[components.MovementActionComponent]
            entity[components.PositionComponent].y += dy
            entity[components.PositionComponent].x += dx

            del entity[components.MovementActionComponent]