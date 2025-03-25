from typing import *
import operator

from . import ecs
from . import components
from . import tiles
from . import events
from . import util

class PlayerSystem(ecs.System):
    IDLE_ACTION = components.MovementActionComponent(0, 0)
    PLAYER_DELTAS_COST = util.DIAGONAL_DELTAS_COST | util.CARDINAL_DELTAS_COST
    AUTOWALK_FREQUENCY = 100# in milliseconds
    SIGHT_RADIUS = 12

    def recompute_path(self, em: ecs.TilemapEcs, pos, dest, pc: components.PlayerControlComponent):
        graph = em.tilemap.get_graph(tiles.DEFAULT_TILE_WEIGHTS, deltas_cost=PlayerSystem.PLAYER_DELTAS_COST)

        for node in graph.nodes:
            if node not in pc.discovered:
                for edge in graph.edges[node]:
                    edge.weight = float("inf")

        dist, prev = graph.pathfind(pos, dest)
        return list(graph.trace_path(prev, dest))

    def autowalk_step(self, em: ecs.TilemapEcs, player: ecs.Entity, pc: components.PlayerControlComponent) -> bool:
        '''
        Perform one step of the planned autowalk.

        Returns: whether the step was successful or whether the autowalk should be aborted.
        '''
        
        player_pos = em.get_pos(player)
        next_pos = pc.autowalk_plan[0]

        if pc.autowalk_plan[0] != player_pos or len(pc.autowalk_plan) == 1:
            return False
        
        target_pos = pc.autowalk_plan[1]
        relative = util.top2(target_pos, player_pos, operator.sub)

        assert((abs(x) <= 1 for x in relative)) # make sure we are not teleporting
        em.add_components(player, components.MovementActionComponent(*relative))

        del pc.autowalk_plan[0]
        return pc.autowalk_plan[-1] != player_pos
    
    def update_visibility(self, em: ecs.TilemapEcs, player: ecs.Entity):
        player_pos = em.get_pos(player)
        pc: components.PlayerControlComponent = player.get_component(em, components.PlayerControlComponent)
        pc.visible = set()
        
        for pos in em.tilemap.iterate_radius(player_pos, PlayerSystem.SIGHT_RADIUS):
            if em.tilemap.in_los(player_pos, pos):
                pc.visible.add(pos)

        pc.discovered = pc.discovered.union(pc.visible)
            
        

    def process(self, em: ecs.TilemapEcs, event):
        try:
            player = em.query_single_with_component(components.PlayerControlComponent)
        except KeyError:
            return
        
        pos = em.get_pos(player)
        pc: components.PlayerControlComponent = player.get_component(em, components.PlayerControlComponent)
        
        match type(event):
            case events.UserHoversTileWithMouseEvent:
                if not pc.do_autowalk:
                    if event.pos not in pc.discovered:
                        pc.autowalk_plan = None
                    else:
                        pc.autowalk_plan = self.recompute_path(em, pos, event.pos, pc)

            case events.UserClicksTileWithMouseEvent:
                if event.pos != pos:
                    if event.pos in pc.discovered:
                        pc.autowalk_plan = self.recompute_path(em, pos, event.pos, pc)
                        pc.autowalk_timer = PlayerSystem.AUTOWALK_FREQUENCY
                        pc.do_autowalk = True
                else:
                    em.add_components(player, PlayerSystem.IDLE_ACTION)
                    em.emit_event(events.GamestepEvent())
            case events.RenderTickEvent:
                if pc.do_autowalk:
                    pc.autowalk_timer += event.dt
                    if pc.autowalk_timer >= PlayerSystem.AUTOWALK_FREQUENCY:
                        pc.autowalk_timer = 0
                        pc.do_autowalk = self.autowalk_step(em, player, pc)

                        if pc.do_autowalk: 
                            em.emit_event(events.GamestepEvent())
            case events.AfterPhysicsTickEvent:
                self.update_visibility(em, player)
            