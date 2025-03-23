import os
import pygame
from dataclasses import dataclass, asdict

from . import tiles
from . import ecs
from . import components

TILE_TO_IMG = {
    tiles.Tile.EMPTY: os.path.join("res", "imgs", "empty.png"),
    tiles.Tile.WALL: os.path.join("res", "imgs", "wall.png"),
}

class GraphicsSystem(ecs.System):
    SPRITE_QUERY_COMPONENTS = {components.SpriteComponent, components.PositionComponent}
    MAP_QUERY_COMPONENTS = {components.TilemapComponent}

    def __init__(self, resources, window_dimensions=(800, 600), tile_scale=16):
        self.resources = resources
        self.scr = pygame.display.set_mode(window_dimensions)
        self.tile_scale = tile_scale

    @staticmethod
    def _entity_sort(entity: ecs.Entity) -> int:
        return entity[components.SpriteComponent].z_index
    
    def draw_entity(self, entity: ecs.Entity):
        y_pos, x_pos = entity[components.PositionComponent]
        img = self.resources[entity[components.SpriteComponent].img_key]
        self.scr.blit(img, (x_pos * self.tile_scale, y_pos * self.tile_scale))

    def draw_tilemap(self, tilemap: tiles.Tilemap):
    
        height, width = tilemap.dims

        for y in range(height):
            for x in range(width):
                tile = tilemap[y, x]
                screen_pos = x * self.tile_scale, y * self.tile_scale
                img = self.resources[tile.get_image_key()]
                self.scr.blit(img, screen_pos)


    def process(self, entity_manager: ecs.ECS, event: ecs.Event):
        # this cound theoretically draw multiple tilemaps but this might never be necessary (maybe for chunked maps?)
        # generally the tilemap will be a singleton
        
        if isinstance(entity_manager, ecs.TilemapEcs):
            # then we can draw a tilemap
            self.draw_tilemap(entity_manager.tilemap)

        drawable_entities = list(entity_manager.query_all_with_components(*GraphicsSystem.SPRITE_QUERY_COMPONENTS)) # get all drawable entities
        drawable_entities.sort(key=GraphicsSystem._entity_sort) # sort according to z index

        for entity in drawable_entities:
            self.draw_entity(entity)

