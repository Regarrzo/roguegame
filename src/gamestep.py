from typing import *

from . import ecs
from . import components
from . import tiles
from . import events
from . import util

class GamestepSystem(ecs.System):
    '''
    This is a system for managing each turn. It responds to a gamestep event and calls other events necessary.
    '''
    def __init__(self):
        pass

    def pos_is_free(self, em: ecs.TilemapEcs, pos: Tuple[int, int]):
        return em.tilemap.pos_is_in_bounds((pos)) and not em.tilemap[pos].is_collider() and not any(e.has_component(em, components.CollisionComponent) for e in em.get_entities_at(pos))

    def process(self, em: ecs.TilemapEcs, event: events.GamestepEvent):
        assert(type(event) == events.GamestepEvent)

        em.emit_event(events.BehaviourTickEvent())
        em.emit_event(events.PhysicsTickEvent())
        