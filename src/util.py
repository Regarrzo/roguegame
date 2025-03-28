from __future__ import annotations
import heapq
import operator
from dataclasses import dataclass, field, asdict
from typing import *
import itertools

CARDINAL_DELTAS = [(1,0), (0,1), (0,-1), (-1,0)]
DIAGONAL_DELTAS = [(1,1), (-1,-1), (1,-1), (-1, 1)]

CARDINAL_DELTAS_COST = {delta: 1 for delta in CARDINAL_DELTAS}
DIAGONAL_DELTAS_COST = {delta: 1.41 for delta in DIAGONAL_DELTAS}


def manhatten_distance(a, b):
    return sum(abs(a_i - b_i) for a_i, b_i in zip(a, b))

def chebyshev_distance(a, b):
    return max(abs(a_i - b_i) for a_i, b_i in zip(a, b))


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

def iterate_rect(a, b):
    y_start, y_end = a[0], b[0]
    x_start, x_end = a[1], b[1]

    for y in range(y_start, y_end + 1):
        for x in range(x_start, x_end + 1):
            yield y, x

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

    def pathfind(self, origin, dest=None, heuristic=lambda x, y: 0) -> Tuple[Dict, Dict]:
        '''
        Early exit if dest is set. Faster if a suitable heuristic is given.
        Returns: (distances dict, previous node dict)
        '''
        pq = []
        real_dist = {origin: 0}
        heuristic_dist = {origin: heuristic(origin, dest)}
        prev = {}
        heapq.heappush(pq, _DistEdge(0, heuristic_dist[origin], origin))

        while pq:
            _, total_dist, curr_vertex = heapq.heappop(pq)

            if heuristic_dist[curr_vertex] != total_dist:
                continue

            if dest is not None and curr_vertex == dest:
                break

            for edge in self.edges[curr_vertex]:
                child_weight, child_vertex = edge

                if child_vertex not in real_dist:
                    real_dist[child_vertex] = float("inf")
                
                alt = real_dist[curr_vertex] + child_weight

                if alt < real_dist[child_vertex]:
                    prev[child_vertex] = curr_vertex
                    real_dist[child_vertex] = alt 
                    h_dist = alt + heuristic(child_vertex, dest)
                    heuristic_dist[child_vertex] = h_dist
                    heapq.heappush(pq, _DistEdge.from_edge(edge, h_dist))


        return real_dist, prev
    
    def trace_path(self, prev: Dict, dest: Hashable) -> Iterable[Hashable]:
        '''
        After pathfinding, this can convert the returned prev dict and a destination into an actual path, i.e. a list of nodes.
        '''
        path = [dest]

        while path[-1] in prev:
            path.append(prev[path[-1]])

        path.reverse()
        return path

    @staticmethod
    def from_2dgrid(grid: List[List[Hashable]], weights: Dict = None, deltas_cost: Dict[Tuple[int, int] : float] = ((1,0), (0,1), (-1,0), (0,-1))) -> Graph:
        '''
        Generate a graph from a 2 dimensional grid.
        '''
        
        height, width =  len(grid), len(grid[0])
        r = Graph()

        for i, j in itertools.product(range(height), range(width)):
            r.add((i, j))

            for (di, dj), cost in deltas_cost.items():
                ci, cj = (i + di, j + dj)

                if is_in_2dgrid_bounds(grid, (ci, cj)):
                    r.add((ci, cj))
                    w = weights[grid[ci][cj]] if weights else 1
                    r.connect((i, j), (ci, cj), w * cost)

        return r
                    
def grid2d_to_string(grid: List[List[Hashable]]) -> str:
    return "\n".join(" ".join(str(cell) for cell in row) for row in grid)

def distance(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    y_a, x_a = a
    y_b, x_b = b

    return ((y_a - y_b) ** 2 + (x_a - x_b) ** 2) ** 0.5

def _iterate_line_low(y0, x0, y1, x1) -> Generator[Tuple[int, int], None, None]:
    dy = y1 - y0
    dx = x1 - x0

    yi = 1

    if dy < 0:
        yi = -1
        dy = -dy
    
    D = 2 * dy - dx
    y = y0

    for x in get_integers_between(x0, x1):
        yield y, x

        if D > 0:
            y = y + yi
            D = D + (2 * (dy - dx))
        else:
            D = D + 2 * dy


def _iterate_line_high(y0, x0, y1, x1) -> Generator[Tuple[int, int], None, None]:
    dy = y1 - y0
    dx = x1 - x0

    xi = 1

    if dx < 0:
        xi = -1
        dx = -dx

    D = (2 * dx) - dy
    x = x0

    for y in get_integers_between(y0, y1):
        yield y, x

        if D > 0:
            x = x + xi
            D = D + (2 * (dx - dy))
        else:
            D = D + 2 * dx

def iterate_line(start: Tuple[int, int], end: Tuple[int, int]) -> Generator[Tuple[int, int], None, None]:
    y0, x0 = start
    y1, x1 = end

    if abs(y1 - y0) < abs(x1 - x0):
        if x0 > x1:
            return reversed(list(_iterate_line_low(y1, x1, y0, x0)))
        else:
            return _iterate_line_low(y0, x0, y1, x1)
    else:
        if y0 > y1:
            return reversed(list(_iterate_line_high(y1, x1, y0, x0)))
        else:
            return _iterate_line_high(y0, x0, y1, x1)



def reverse_tuple(a: Tuple):
    return tuple(reversed(a))

def top2(ta: Tuple, tb: Tuple, op):
    '''
    Performs op element wise between ta and tb
    '''
    return tuple((op(a, b) for a, b in zip(ta, tb)))

def top(t: Tuple, op):
    '''
    Performs op on every element of the tuple.
    '''
    return tuple((op(x) for x in t))

def tops(t: Tuple, s: float, op):
    '''
    Performs an elementwise scalar operation
    '''
    return tuple((op(x, s) for x in t))

def get_integers_between(a: int, b: int):
    '''
    Similar to range() but inclusive and does not care which one is bigger.
    '''
    direction = 1 if b >= a else -1
    return range(a, b + direction, direction)

def linint(a: Tuple, b: tuple, x: float):
    '''
    x is in [0, 1], will interpolate between tuples a and b.
    '''
    a_b = top2(b, a, operator.sub)
    
    return top2(a, tops(a_b, x, operator.mul), operator.add)

def are_adjacent(a: Tuple[int, int], b: Tuple[int, int]) -> bool:
    return all(-1 <= x <= 1 for x in top2(a, b, operator.sub))