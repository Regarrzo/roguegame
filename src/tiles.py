from __future__ import annotations

from typing import *
from enum import Enum, auto


import random
import os
import itertools

from . import util
from . import ecs

class Tile(Enum):
    EMPTY = auto()
    WALL = auto()

    def get_image_key(self) -> str:
        return TILE_TO_IMG[self]
    
    def is_collider(self) -> bool:
        return self in TILE_COLLDIERS
    
    def blocks_los(self) -> bool:
        return self in LOS_BLOCKERS

TILE_TO_IMG = {
    Tile.EMPTY: os.path.join("res", "imgs", "empty.png"),
    Tile.WALL: os.path.join("res", "imgs", "wall.png"),
}

TILE_COLLDIERS = {Tile.WALL}
LOS_BLOCKERS = {Tile.WALL}

DEFAULT_TILE_WEIGHTS = {tile: float("inf") if tile.is_collider() else 1 for tile in Tile}

class Tilemap:
    def __init__(self, dims: Tuple[int, int]=(16, 16), init_tile=Tile.EMPTY):
        self.dims = dims
        height, width = dims
        self._data: List[List[Tile]] = [[init_tile] * width for _ in range(height)]

    def __getitem__(self, pos: Tuple[int, int]) -> Tile:
        y, x = pos
        return self._data[y][x]
    
    def __setitem__(self, pos: Tuple[int, int], to: Tile):
        self._graph = None
        y, x = pos
        self._data[y][x] = to


    def pos_is_in_bounds(self, pos: Tuple[int, int]) -> bool:
        y, x = pos
        height, width = self.dims
        return 0 <= y < height and 0 <= x < width

    def fill_rect(self, a: Tuple[int, int], b: Tuple[int, int], tile: Tile):
        y_start, y_end = a[0], b[0]
        x_start, x_end = a[1], b[1]

        for y, x in itertools.product(range(y_start, y_end + 1), 
                                      range(x_start, x_end + 1)):
            self._data[y][x] = tile

    def trace_path(self, path: List[Tuple[int, int]], tile: Tile):
        for y, x in path:
            self._data[y][x] = tile
    
    def iterate_with_tile(self, tile: Tile) -> Generator[Tuple[int, int], None, None]:
        height, width = self.dims

        for y, x in itertools.product(range(height), 
                                      range(width)):
            if self._data[y][x] == tile: 
                yield y, x

    def get_graph(self, weights: Dict[Tile, float] = None, deltas_cost: Dict[Tuple[int, int] : float] = ((1,0), (0,1), (-1,0), (0,-1))):
        '''
        Get a graph view for pathfinding. Will recompute the graph. deltas_cost is a doct mapping deltas to their weight multiplier.
        '''
        return util.Graph.from_2dgrid(self._data, weights, deltas_cost)
    
    def generate_random_connected_rooms(self, iters=1000, min_room_size=2, max_room_size=5, wall_weight=10):
        map_height, map_width = self.dims
        r = [[Tile.WALL] * map_width for _ in range(map_height)]
        rooms = []

        for i in range(iters):
            height = random.randint(min_room_size, max_room_size)
            width = random.randint(min_room_size, max_room_size)
            
            y_pos = random.randint(1, map_height - 2 - height)
            x_pos = random.randint(1, map_width - 2 - width)

            a0, b0 = (y_pos, x_pos), (y_pos + height, x_pos + width)

            if not any((util.rects_intersect(a0, b0, *util.grow_rect(a1, b1, 1)) for a1, b1 in rooms)):
                rooms.append((a0, b0))

        for a, b in rooms:
            util.grid2d_fill_rect(r, a, b, Tile.EMPTY)

        for room, next_room in zip(rooms, rooms[1:]):
            pathfind_origin = util.get_rect_center(*room)
            pathfind_dest = util.get_rect_center(*next_room)
            graph = util.Graph.from_2dgrid(r, weights={Tile.EMPTY: 1, Tile.WALL: wall_weight}, deltas_cost=util.CARDINAL_DELTAS_COST)
            _, prev = graph.pathfind(pathfind_origin, pathfind_dest)
            path = graph.trace_path(prev, pathfind_dest)
            util.grid2d_trace_path(r, path, Tile.EMPTY)

        self._data = r

    def get_random_empty_tile(self):
        return random.choice(list(self.iterate_with_tile(Tile.EMPTY)))
    
    def in_los(self, origin: Tuple[int, int], destination: Tuple[int, int]) -> bool:
        '''
        Returns true if destination can be seen from origin.
        '''
        for pos in list(util.iterate_line(origin, destination))[:-1]:
            if self[pos].blocks_los():
                return False

        return True

    def iterate_radius(self, origin: Tuple[int, int], radius: float, deltas: Tuple[Tuple[int, int]] = ((1,0), (0,1), (-1,0), (0,-1))) -> Generator[Tuple[int, int], None, None]:
        '''
        Iterate through all tiles whose center lies in the specified radius from the position.
        '''

        visited = set()
        to_visit = [origin]

        while to_visit:
            curr = to_visit.pop()
            visited.add(curr)
            dist_to_origin = util.distance(curr, origin)

            if dist_to_origin <= radius:
                yield curr
            else:
                continue
            
            for dy, dx in deltas:
                curr_y, curr_x = curr
                new = curr_y + dy, curr_x + dx
                
                if self.pos_is_in_bounds(new) and new not in visited and new not in to_visit:
                    to_visit.append(new)
        

    