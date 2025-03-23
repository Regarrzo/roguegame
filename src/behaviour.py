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

    def process(self, em: ecs.Ecs, event: events.BehaviourTickEvent):
        random_movers = em.query_all_with_components(components.RandomMoveBehaviourComponent)
        
        for mover in random_movers:
            em.add_components(mover, random.choice(BehaviourSystem.MOVES))