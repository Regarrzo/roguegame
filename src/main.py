from enum import Enum, auto
import pygame
import os

from . import configuration
from . import ecs
from . import graphics
from . import resources
from . import tiles
from . import components
from . import events
from . import inputs
from . import physics
from . import entity_definitions


def main():
    # ECS initialization
    pygame.init()
    game = ecs.ECS()
    clock = pygame.time.Clock()
    
    # Load resources
    res = resources.load_res(configuration.RESOURCES_PATH, tile_scale=configuration.SCALE)
    # System initialization
    graphics_system = graphics.GraphicsSystem(res, tile_scale=configuration.SCALE, window_dimensions=configuration.WINDOW_DIMS)
    game.register_system(graphics_system, events.RenderTickEvent)

    user_input_system = inputs.UserInputSystem()
    game.register_system(user_input_system, events.UserInputEvent)

    physics_system = physics.PhysicsSystem()
    game.register_system(physics_system, events.LogicTickEvent)

    # Initialise game
    dungeon = game.create_entity(components.PositionComponent(0, 0), 
                                 components.TilemapComponent(tiles.generate_map(), tiles.TILE_TO_IMG))
    player = game.create_entity(*entity_definitions.make_player(1, 1))

    while True:
        pressed_keys = []

        for pygame_event in pygame.event.get():
            if pygame_event.type == pygame.QUIT: 
                return

            if pygame_event.type == pygame.KEYDOWN:
                pressed_keys.append(pygame_event.key)

        if pressed_keys:
            game.emit_event(events.UserInputEvent(pressed_keys))
            game.emit_event(events.LogicTickEvent())

        pygame.display.flip()
        dt = clock.tick(configuration.TARGET_FPS)
        game.emit_event(events.RenderTickEvent(dt))



        
    
main()