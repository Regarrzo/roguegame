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
    MAP_QUERY_COMPONENTS = {components.TilemapComponent, components.PositionComponent}

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

    def draw_tilemap(self, tilemap: ecs.Entity):
        
        tm = tilemap[components.TilemapComponent].data
        y_offset, x_offset = tilemap[components.PositionComponent]
        resource_map = tilemap[components.TilemapComponent].tile_resource_map
        height, width = len(tm), len(tm[0])

        for y in range(height):
            for x in range(width):
                tile = tm[y][x]
                screen_pos = (x + x_offset) * self.tile_scale, (y + y_offset) * self.tile_scale
                img = self.resources[resource_map[tile]]
                self.scr.blit(img, screen_pos)


    def process(self, entity_manager: ecs.ECS, event: ecs.Event):
        # this cound theoretically draw multiple tilemaps but this might never be necessary (maybe for chunked maps?)
        # generally the tilemap will be a singleton
        drawable_tilemaps = list(entity_manager.query_all_with_components(*GraphicsSystem.MAP_QUERY_COMPONENTS))
        
        for tilemap in drawable_tilemaps:
            self.draw_tilemap(tilemap)

        
        drawable_entities = list(entity_manager.query_all_with_components(*GraphicsSystem.SPRITE_QUERY_COMPONENTS)) # get all drawable entities
        drawable_entities.sort(key=GraphicsSystem._entity_sort) # sort according to z index

        for entity in drawable_entities:
            self.draw_entity(entity)

