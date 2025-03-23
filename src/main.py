from enum import Enum, auto
import pygame
import os

from . import util
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
from . import behaviour


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
    game.register_system(physics_system, events.PhysicsTickEvent)

    behaviour_system = behaviour.BehaviourSystem()
    game.register_system(behaviour_system, events.BehaviourTickEvent)

    # Initialise game
    dungeon = game.create_entity(components.PositionComponent(0, 0), 
                                 components.TilemapComponent(tiles.generate_map(), tiles.TILE_TO_IMG, tiles.TILE_COLLDIERS))
    
    
    player = game.create_entity(*entity_definitions.player(*tiles.get_valid_player_spawnpoint(dungeon[components.TilemapComponent].data)))

    for _ in range(10):
        rat = game.create_entity(*entity_definitions.rat(*tiles.get_valid_player_spawnpoint(dungeon[components.TilemapComponent].data)))

    while True:
        pressed_keys = []

        for pygame_event in pygame.event.get():
            if pygame_event.type == pygame.QUIT: 
                return

            if pygame_event.type == pygame.KEYDOWN:
                pressed_keys.append(pygame_event.key)

        if pressed_keys:
            game.emit_event(events.UserInputEvent(pressed_keys))
            game.emit_event(events.BehaviourTickEvent())
            game.emit_event(events.PhysicsTickEvent())

        pygame.display.flip()
        dt = clock.tick(configuration.TARGET_FPS)
        game.emit_event(events.RenderTickEvent(dt))



main() #cmmit this line to run the game with menu
        
# uncommit this line to run the game with menu    
# def run_game():
#     main()  

# if __name__ == "__main__":
#     run_game()  
