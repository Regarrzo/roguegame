from typing import *

import pygame

from . import ecs
from . import configuration
from . import events
from . import components


class UserInputSystem(ecs.System):
    def __init__(self):
        self.last_hovered_pos = (-1, -1)
        self.click_event_already_sent = False

    def process(self, entity_manager, event: Union[events.UserInputEvent, events.RenderTickEvent]):
        match type(event):
            case events.UserInputEvent:
                pressed_keys = event.keys
                # TODO: Support multiple inputs (maybe?)
                action = configuration.KEY_MAP.get(pressed_keys[0], None)

                if not action: return

                targets = entity_manager.query_all_with_components(components.PlayerControlComponent)

                if not list(targets) and pygame.K_SPACE in pressed_keys:
                    entity_manager.emit_event(events.LoadNextDungeonEvent())
                    return
            
                for target in targets:
                    entity_manager.add_components(target, action)

                entity_manager.emit_event(events.GamestepEvent())
            case events.RenderTickEvent:
                y, x = event.mouse_pos
                pos = int(y / configuration.SCALE), int(x / configuration.SCALE)

                if pos != self.last_hovered_pos:

                    self.last_hovered_pos = pos
                    entity_manager.emit_event(events.UserHoversTileWithMouseEvent(pos))

                if event.left_click:
                    if not self.click_event_already_sent:
                        self.click_event_already_sent = True
                        entity_manager.emit_event(events.UserClicksTileWithMouseEvent(pos))
                else:
                    self.click_event_already_sent = False