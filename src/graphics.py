from typing import *

import os
import pygame
import functools
from dataclasses import dataclass, asdict

from . import tiles
from . import ecs
from . import components
from . import util

TILE_TO_IMG = {
    tiles.Tile.EMPTY: os.path.join("res", "imgs", "empty.png"),
    tiles.Tile.WALL: os.path.join("res", "imgs", "wall.png"),
}

class GraphicsSystem(ecs.System):
    SPRITE_QUERY_COMPONENTS = {components.SpriteComponent}

    def __init__(self, resources, window_dimensions=(800, 600), tile_scale=16):
        self.resources = resources
        self.scr = pygame.display.set_mode(window_dimensions)
        self.tile_scale = tile_scale

    @staticmethod
    def _entity_sort(entity_manager: ecs.Ecs, entity: ecs.Entity) -> int:
        return entity_manager.get_components(entity)[components.SpriteComponent].z_index
    
    def draw_entity(self, em: ecs.TilemapEcs, entity: ecs.Entity):
        y_pos, x_pos = em.get_pos(entity)
        img = self.resources[em.get_components(entity)[components.SpriteComponent].img_key]
        self.scr.blit(img, (x_pos * self.tile_scale, y_pos * self.tile_scale))

    def draw_tilemap(self, tilemap: tiles.Tilemap):
        height, width = tilemap.dims

        for y in range(height):
            for x in range(width):
                tile = tilemap[y, x]
                screen_pos = x * self.tile_scale, y * self.tile_scale
                img = self.resources[tile.get_image_key()]
                self.scr.blit(img, screen_pos)

    def draw_path_preview(self, em: ecs.Ecs, path: List[Tuple[int, int]]):
        img = self.resources[os.path.join("res", "imgs", "path_tile.png")]
        for y, x in path:
            screen_pos = x * self.tile_scale, y * self.tile_scale
            self.scr.blit(img, screen_pos)

    def draw_debug_square(self, em: ecs.TilemapEcs, pos: Tuple[int, int]):
        img = self.resources[os.path.join("res", "imgs", "debug.png")]
        y, x = pos
        screen_pos = x * self.tile_scale, y * self.tile_scale
        self.scr.blit(img, screen_pos)


    def process(self, em: ecs.Ecs, event: ecs.Event):
        # this cound theoretically draw multiple tilemaps but this might never be necessary (maybe for chunked maps?)
        # generally the tilemap will be a singleton
        
        if isinstance(em, ecs.TilemapEcs):
            # then we can draw a tilemap
            self.draw_tilemap(em.tilemap)

        drawable_entities = list(em.query_all_with_components(*GraphicsSystem.SPRITE_QUERY_COMPONENTS)) # get all drawable entities
        sorting_function = functools.partial(self._entity_sort, em)
        drawable_entities.sort(key=sorting_function) # sort according to z index

        for entity in drawable_entities:
            self.draw_entity(em, entity)

        try:
            player = em.query_single_with_component(components.PlayerControlComponent)
            player_pos = em.get_pos(player)
            pc: components.PlayerControlComponent = player.get_component(em, components.PlayerControlComponent)

            if pc.autowalk_plan:
                self.draw_path_preview(em, pc.autowalk_plan)
        except KeyError:
            pass
