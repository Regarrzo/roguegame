from typing import *

from . import ecs
from . import components
from . import tiles
from . import events
from . import util
from . import entity_definitions

class PhysicsSystem(ecs.System):
    def __init__(self):
        pass
        
    def pos_is_free(self, em: ecs.TilemapEcs, pos: Tuple[int, int]):
        return em.tilemap.pos_is_in_bounds((pos)) and not em.tilemap[pos].is_collider() and not any(e.has_component(em, components.CollisionComponent) for e in em.get_entities_at(pos))

    def get_attackable_at(self, em: ecs.TilemapEcs, pos: Tuple[int, int]):
        flee_vulnerable = em.query_all_with_components(components.FleeVulnerabilityComponent)
        attackable_flee_vulnerable = set(list(e for e in flee_vulnerable if e.get_component(em, components.FleeVulnerabilityComponent).vulnerable_square == pos))
        attackable_default = (e for e in em.get_entities_at(pos) if e.has_component(em, components.HealthComponent))
        return attackable_flee_vulnerable.union(attackable_default)

    def process(self, em: ecs.TilemapEcs, event: events.PhysicsTickEvent):
        moving = list(em.query_all_with_components(components.MovementActionComponent))
        
        for entity in moving:
            dy, dx = em.get_components(entity)[components.MovementActionComponent]
            old_y, old_x =  em.get_pos(entity)
            new_pos = old_y + dy, old_x + dx

            if entity.has_component(em, components.MeleeAttackComponent):
                for target in self.get_attackable_at(em, new_pos):
                    if target == entity:
                        continue
                    
                    damage = entity.get_component(em, components.MeleeAttackComponent).damage
                    target.get_component(em, components.HealthComponent).health -= damage
                    em.create_entity(new_pos, *entity_definitions.hitmarker(damage))

            if self.pos_is_free(em, new_pos):
                if entity.has_component(em, components.FleeVulnerabilityComponent):
                    entity.get_component(em, components.FleeVulnerabilityComponent).vulnerable_square = old_y, old_x

                em.move_entity(entity, new_pos)

            
            em.remove_components(entity, components.MovementActionComponent)

