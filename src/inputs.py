import pygame

from . import ecs
from . import configuration
from . import events
from . import components


class UserInputSystem(ecs.System):
    def __init__(self):
        pass

    def process(self, entity_manager, event: events.UserInputEvent):
        pressed_keys = event.keys
         # TODO: Support multiple inputs (maybe?)
        action = configuration.KEY_MAP.get(pressed_keys[0], None)

        if not action: return

        targets = entity_manager.query_all_with_components(components.PlayerControlComponent)
    
        for target in targets:
            entity_manager.add_components(target, action)

        entity_manager.emit_event(events.BehaviourTickEvent())
        entity_manager.emit_event(events.PhysicsTickEvent())