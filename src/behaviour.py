
from typing import *
import random
import operator

from . import ecs
from . import components
from . import tiles
from . import events
from . import util

class BehaviourSystem(ecs.System):
    MOVES = (components.MovementActionComponent(1, 0), 
             components.MovementActionComponent(-1, 0), 
             components.MovementActionComponent(0, 1), 
             components.MovementActionComponent(0, -1),
             components.MovementActionComponent(0, 0))
    
    DELTAS_COST = util.CARDINAL_DELTAS_COST | util.DIAGONAL_DELTAS_COST

    def __init__(self):
        pass

    def find_best_flee_move(self, em: ecs.TilemapEcs, fleer: ecs.Entity, threat: ecs.Entity):
        y, x = em.get_pos(fleer)
        threat_pos = em.get_pos(threat)
        
        valid_moves = []

        for move in BehaviourSystem.MOVES:
            dy, dx = move
            new_y, new_x = y + dy, x + dx

            if em.tilemap.pos_is_in_bounds((new_y, new_x)) and not em.tilemap[new_y, new_x].is_collider():
                valid_moves.append(move)

        def distance_to_threat(move: components.MovementActionComponent) -> float:
            dy, dx = move
            new_pos = y + dy, x + dx
            return util.distance(new_pos, threat_pos)
        
        valid_moves.sort(key=distance_to_threat)
        return valid_moves[-1]
    
    
    
    def go_toward(self, em: ecs.TilemapEcs, entity: ecs.Entity, pos: Tuple[int, int]):
        pathfind_data: components.PathfindTargetComponent = entity.get_component(em, components.PathfindTargetComponent)
        entity_pos = em.get_pos(entity)

        if entity_pos == pos:
            return

        if not pathfind_data.plan or pathfind_data.plan[-1] != pos:
            if pathfind_data.graph is None:
                pathfind_data.graph = em.tilemap.get_graph(tiles.DEFAULT_TILE_WEIGHTS, BehaviourSystem.DELTAS_COST)

            dist, prev = pathfind_data.graph.pathfind(entity_pos, pos)
            pathfind_data.plan = pathfind_data.graph.trace_path(prev, pos)

        if len(pathfind_data.plan) < 2:
            return

        target = pathfind_data.plan[1]
        relative_target = util.top2(target, entity_pos, operator.sub)
        assert((abs(x) <= 1 for x in relative_target))

        em.add_components(entity, components.MovementActionComponent(*relative_target))
        del pathfind_data.plan[0]

        
    def process_peaceful(self, em: ecs.TilemapEcs, peaceful: Iterable[ecs.Entity], player: ecs.Entity):
        for mover in peaceful:
            mover_pos = em.get_pos(mover)

            if player:
                player_pos = em.get_pos(player)

            if player and util.distance(player_pos, mover_pos) < 5:
                em.add_components(mover, self.find_best_flee_move(em, mover, player))
            else:
                em.add_components(mover, random.choice(BehaviourSystem.MOVES))

    def process_hostile(self, hostiles: Iterable[ecs.Entity], em: ecs.Ecs, player: ecs.Entity):
        if not player:
            return
        
        player_pos = em.get_pos(player)
        
        for hostile in hostiles:
            hostile_pos = em.get_pos(hostile)
            hostile_behaviour: components.SimpleHostileBehaviourComponent = hostile.get_component(em, components.SimpleHostileBehaviourComponent)
            pathfind_data: components.PathfindTargetComponent = hostile.get_component(em, components.PathfindTargetComponent)
        
            if util.distance(player_pos, hostile_pos) <= hostile_behaviour.sight_range and em.tilemap.in_los(hostile_pos, player_pos):
                hostile_behaviour.last_seen_player_position = player_pos

            if hostile_behaviour.last_seen_player_position is not None and hostile_pos != hostile_behaviour.last_seen_player_position:
                self.go_toward(em, hostile, player_pos)                
    

    def process(self, em: ecs.Ecs, event: events.BehaviourTickEvent):
        try:
            player = em.query_single_with_component(components.PlayerControlComponent)
            player_pos = em.get_pos(player)
        except KeyError:
            player = None

        dumb_peaceful = em.query_all_with_components(components.DumbPeacefulBehaviourComponent)
        self.process_peaceful(em, dumb_peaceful, player)

        simple_hostile = em.query_all_with_components(components.SimpleHostileBehaviourComponent, components.PathfindTargetComponent)
        self.process_hostile(simple_hostile, em, player)