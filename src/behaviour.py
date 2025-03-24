import random

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

        


    def process(self, em: ecs.Ecs, event: events.BehaviourTickEvent):
        dumb_peaceful = em.query_all_with_components(components.DumbPeacefulBehaviourComponent)

        try:
            player = em.query_single_with_component(components.PlayerControlComponent)
            player_pos = em.get_pos(player)
        except KeyError:
            player = None

        for mover in dumb_peaceful:
            mover_pos = em.get_pos(mover)
            if player and util.distance(player_pos, mover_pos) < 5:
                em.add_components(mover, self.find_best_flee_move(em, mover, player))
            else:
                em.add_components(mover, random.choice(BehaviourSystem.MOVES))