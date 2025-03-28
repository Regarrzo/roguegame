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
    
    def draw_entity(self, em: ecs.TilemapEcs, entity: ecs.Entity, visibility: Set[Tuple[int, int]] = None):
        y_pos, x_pos = em.get_pos(entity)
        img = self.resources[em.get_components(entity)[components.SpriteComponent].img_key]
        self.scr.blit(img, (x_pos * self.tile_scale, y_pos * self.tile_scale))

    def draw_tile(self, tile: tiles.Tile, pos: Tuple[int, int], fog_of_war_filter=False):
        y, x = pos
        screen_pos = x * self.tile_scale, y * self.tile_scale
        img = self.resources[tile.get_image_key()]

        if not fog_of_war_filter:
            self.scr.blit(img, screen_pos)
        else:
            self.scr.blit(pygame.transform.grayscale(img), screen_pos)



    def draw_tilemap(self, tilemap: tiles.Tilemap, visiblity: Set[Tuple[int, int]] = None, discovered: Set[Tuple[int, int]] = None):
        height, width = tilemap.dims

        for y in range(height):
            for x in range(width):
                tile = tilemap[y, x]
                self.draw_tile(tile, (y, x))
    
    def draw_tilemap_with_visibility(self, tilemap: tiles.Tilemap, visiblity: Set[Tuple[int, int]], discovered: Set[Tuple[int, int]]):
        height, width = tilemap.dims
        hidden_img = self.resources[os.path.join("res", "imgs", "hidden.png")]

        for y in range(height):
            for x in range(width):
                if (y, x) in visiblity:
                    tile = tilemap[y, x]
                    self.draw_tile(tile, (y, x))
                elif (y, x) in discovered:
                    tile = tilemap[y, x]
                    self.draw_tile(tile, (y, x), fog_of_war_filter=True)
                else:
                    screen_pos = x * self.tile_scale, y * self.tile_scale
                    self.scr.blit(hidden_img, screen_pos)

                
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



    def draw_hp_bar(self, em: ecs.TilemapEcs, entity: ecs.Entity):
        y, x = em.get_pos(entity)
        hc: components.HealthComponent = entity.get_component(em, components.HealthComponent)
        color = util.linint((255, 0, 0), (0, 255, 0), hc.health / hc.max_health)
        
        start_pos = x * self.tile_scale, (y + 1) * self.tile_scale
        end_pos = x * self.tile_scale, y * self.tile_scale
        pygame.draw.line(self.scr, color, start_pos, util.linint(start_pos, end_pos, hc.health / hc.max_health), int(hc.max_health ** 0.5))


    def draw_text(self, em: ecs.TilemapEcs, pos: Tuple[int, int], comp: components.FloatingTextComponent):
        font: pygame.font.Font = self.resources[comp.font]
        img = font.render(comp.text, False, comp.color)
        y, x = pos
        screen_pos = self.tile_scale * x, self.tile_scale * y
        self.scr.blit(img, screen_pos)

    def draw_bartext(self, em: ecs.TilemapEcs, bartext: components.BarTextComponent):
        height, width = em.tilemap.dims
        screen_pos = 0, self.tile_scale * (height)
        font: pygame.font.Font = self.resources[bartext.font]
    
        img = font.render(bartext.text, False, bartext.color)
        self.scr.blit(img, screen_pos)

    def process(self, em: ecs.Ecs, event: ecs.Event):
        # this cound theoretically draw multiple tilemaps but this might never be necessary (maybe for chunked maps?)
        # generally the tilemap will be a singleton
        self.scr.fill((0, 0, 0))

        player = None
        try:
            player = em.query_single_with_component(components.PlayerControlComponent)
            pc: components.PlayerControlComponent = player.get_component(em, components.PlayerControlComponent)
        except KeyError:
            pass

        
        if isinstance(em, ecs.TilemapEcs):
            # then we can draw a tilemap
            if player is not None:
                self.draw_tilemap_with_visibility(em.tilemap, pc.visible, pc.discovered)
            else:
                self.draw_tilemap(em.tilemap)


        drawable_entities = list(em.query_all_with_components(*GraphicsSystem.SPRITE_QUERY_COMPONENTS)) # get all drawable entities
        sorting_function = functools.partial(self._entity_sort, em)
        drawable_entities.sort(key=sorting_function) # sort according to z index

        for entity in drawable_entities:
            y_pos, x_pos = em.get_pos(entity)

            if player is not None and pc.visible is not None and (y_pos, x_pos) not in pc.visible:
                continue
            
            self.draw_entity(em, entity)

            if entity.has_component(em, components.HealthComponent):
                self.draw_hp_bar(em, entity)

        font_entities = em.query_all_with_components(components.FloatingTextComponent)

        for entity in font_entities:
            comp = entity.get_component(em, components.FloatingTextComponent)
            pos = em.get_pos(entity)
            self.draw_text(em, pos, comp)


        if player is not None and pc.autowalk_plan:
            self.draw_path_preview(em, pc.autowalk_plan)

        try:
            bartext = em.query_single_with_component(components.BarTextComponent).get_component(em, components.BarTextComponent)
            self.draw_bartext(em, bartext)

        except KeyError:
            pass