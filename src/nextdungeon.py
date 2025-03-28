from typing import *

from . import ecs
from . import components
from . import tiles
from . import events
from . import util
from . import entity_definitions
import random

class NextDungeonSystem(ecs.System):
    def __init__(self):
        pass

    def process(self, em: ecs.TilemapEcs, event: events.LoadNextDungeonEvent):
        entities = []

        try:
            level_number: components.BarTextComponent = em.query_single_with_component(components.BarTextComponent).get_component(em, components.BarTextComponent)
            level_label, number = level_number.text.split()
            next_text = f"{level_label} {int(number) + 1}"
        except (KeyError, ValueError):
            next_text = "Level 1"
            

        for entity in em.entities:
            entities.append(entity)

        for entity in entities:
            em.remove_entity(entity)

        em.tilemap.generate_random_connected_rooms(iters=10000, max_room_size=7)
    
        em.create_entity(em.tilemap.get_random_empty_tile(), *entity_definitions.player())

        for _ in range(random.randint(0, 20)):
            em.create_entity(em.tilemap.get_random_empty_tile(), *entity_definitions.rat())

        for _ in range(random.randint(1, 10)):
            em.create_entity(em.tilemap.get_random_empty_tile(), *entity_definitions.goblin())

        for _ in range(random.randint(1, 10)):
            em.create_entity(em.tilemap.get_random_empty_tile(), *entity_definitions.water())
    
        em.create_entity(em.tilemap.get_random_empty_tile(), *entity_definitions.stairs())
        em.create_entity((0, 0), *entity_definitions.bar_text(next_text))
        em.emit_event(events.GamestepEvent())
