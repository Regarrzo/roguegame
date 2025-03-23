from __future__ import annotations
import heapq
from dataclasses import dataclass, field, asdict
from typing import Any, List, Dict, Tuple, Set, Hashable
import itertools

def is_in_2dgrid_bounds(grid: List[List], tup: Tuple[int, int]) -> bool:
    height, width = len(grid), len(grid[0])
    y, x = tup
    return 0 <= y < height and 0 <= x < width

def intervals_intersect(a, b):
    a_start, a_end = a
    b_start, b_end = b
    return a_end >= b_start and b_end >= a_start

def rects_intersect(a0, b0, a1, b1):
    y_interval_0 = (a0[0], b0[0])
    y_interval_1 = (a1[0], b1[0])
    x_interval_0 = (a0[1], b0[1])
    x_interval_1 = (a1[1], b1[1])

    return intervals_intersect(y_interval_0, y_interval_1) and intervals_intersect(x_interval_0, x_interval_1)

def grow_rect(a, b, x):
    y_a, x_a = a
    y_b, x_b = b
    return (y_a - x, x_a - x), (y_b + x, x_b + x)

def get_rect_center(a, b):
    y_a, x_a = a
    y_b, x_b = b

    return (y_a + y_b) // 2, (x_a + x_b) // 2

# There are a lot of these grid2d functions. Maybe it would make sense to make a class that handles the map.
def grid2d_fill_rect(grid: List[List], a, b, tile):
    y_start, y_end = a[0], b[0]
    x_start, x_end = a[1], b[1]

    for y in range(y_start, y_end + 1):
        for x in range(x_start, x_end + 1):
            grid[y][x] = tile

def grid2d_trace_path(grid: List[List], path: List[(int, int)], tile):
    for y, x in path:
        grid[y][x] = tile


def grid2d_iterate_with_tile(grid: List[List], tile):
    height, width =  len(grid), len(grid[0])

    for i, j in itertools.product(range(height), range(width)):
        if grid[i][j] == tile: yield i, j

@dataclass(order=True)
class _Edge:
    weight: float
    to: Any=field(compare=False)

    def __iter__(self):
        return iter(asdict(self).values())

@dataclass(order=True)
class _DistEdge:
    weight: float
    total_dist: float=field(compare=True)
    to: Any=field(compare=False)

    def __iter__(self):
        return iter(asdict(self).values())
    
    @staticmethod
    def from_edge(edge: _Edge, total_dist: float):
        return _DistEdge(edge.weight, total_dist, edge.to)


class Graph:
    def __init__(self):
        self.nodes: Set[Any] = set()
        self.edges: Dict[Any, List[_Edge]] = {}

    def add(self, node):
        self.nodes.add(node)

        if node not in self.edges:
            self.edges[node] = []

    def connect(self, a, b, weight=1):
        '''
        Directed edge connection between a and b with given weight
        '''
        if b not in self.nodes or a not in self.nodes:
            raise ValueError("Tried connecting to node not in graph.")

        self.edges[a].append(_Edge(weight, b))

    def biconnect(self, a, b, weight=1):
        '''
        Undirected (actually: doubly directed) edge connection between a and b with given weight
        '''
        self.connect(a, b, weight)
        self.connect(b, a, weight)

    def pathfind(self, origin, dest=None) -> Tuple[Dict, Dict]:
        '''
        Early exit if dest is set.
        Returns: (distances dict, previous node dict)
        '''
        pq = []
        dist = {origin: 0}
        prev = {}
        heapq.heappush(pq, _DistEdge(0, 0, origin))

        while pq:
            _, total_dist, curr_vertex = heapq.heappop(pq)

            if dist[curr_vertex] != total_dist:
                continue

            if dest is not None and curr_vertex == dest:
                break

            for edge in self.edges[curr_vertex]:
                child_weight, child_vertex = edge

                if child_vertex not in dist:
                    dist[child_vertex] = float("inf")
                
                alt = dist[curr_vertex] + child_weight

                if alt < dist[child_vertex]:
                    prev[child_vertex] = curr_vertex
                    dist[child_vertex] = alt
                    heapq.heappush(pq, _DistEdge.from_edge(edge, alt))

        return dist, prev
    
    def trace_path(self, prev: Dict, dest: Hashable) -> List[Hashable]:
        '''
        After pathfinding, this can convert the returned prev dict and a destination into an actual path, i.e. a list of nodes.
        '''
        path = [dest]

        while path[-1] in prev:
            path.append(prev[path[-1]])

        path.reverse()
        return path

    @staticmethod
    def from_2dgrid(grid: List[List[Hashable]], weights: Dict = None, deltas: Tuple[Tuple] = ((1,0), (0,1), (-1,0), (0,-1))) -> Graph:
        '''
        Generate a graph from a 2 dimensional grid.
        '''
        
        height, width =  len(grid), len(grid[0])
        r = Graph()

        for i, j in itertools.product(range(height), range(width)):
            r.add((i, j))

            for di, dj in deltas:
                ci, cj = (i + di, j + dj)

                if is_in_2dgrid_bounds(grid, (ci, cj)):
                    r.add((ci, cj))
                    w = weights[grid[ci][cj]] if weights else 1
                    r.connect((i, j), (ci, cj), w)

        return r
                    
def grid2d_to_string(grid: List[List[Hashable]]) -> str:
    return "\n".join(" ".join(str(cell) for cell in row) for row in grid)


