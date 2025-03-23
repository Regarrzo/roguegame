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

TILE_TO_IMG = {
    Tile.EMPTY: os.path.join("res", "imgs", "empty.png"),
    Tile.WALL: os.path.join("res", "imgs", "wall.png"),
}

TILE_COLLDIERS = {Tile.WALL}

def generate_map(dims=(32, 32), iters=1000, min_room_size=2, max_room_size=5, wall_weight=10):
    map_height, map_width = dims
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
        graph = util.Graph.from_2dgrid(r, weights={Tile.EMPTY: 1, Tile.WALL: wall_weight})
        _, prev = graph.pathfind(pathfind_origin, pathfind_dest)
        path = graph.trace_path(prev, pathfind_dest)
        util.grid2d_trace_path(r, path, Tile.EMPTY)

    return r

def get_valid_player_spawnpoint(tiles: List[List[Tile]]):
    return random.choice(list(util.grid2d_iterate_with_tile(tiles, Tile.EMPTY)))