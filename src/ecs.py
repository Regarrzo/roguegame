'''
Main ECS engine file. No game specific logic goes here. This file is also heavily type hinted.
'''
from __future__ import annotations


from typing import *
from dataclasses import field, dataclass
from abc import ABC, abstractmethod

from . import tiles

@dataclass
class Entity:
    identifier: Hashable
    components: Dict[Type, Any]

    def add(self, component: Any):
        self.components[type(component)] = component
    
    def __getitem__(self, component_type: Type) -> Any:
        return self.components[component_type]
    
    def __setitem__(self, component_type: Type, to: Any) -> Any:
        self.components[component_type] = to

    def __delitem__(self, component_type: Type):
        del self.components[component_type]
    
    def __hash__(self):
        return hash(self.identifier)

class Event(ABC):
    '''
    Events are how systems are called.
    '''

class System(ABC):
    '''
    Systems for handling game logic via events.
    '''
    @abstractmethod
    def process(self, entity_manager: ECS, event: Event):
        pass

class ECS:
    '''
    (Usually) singleton object central to the entity component system.
    It stores entities and components and calls systems via events. 
    '''
    def __init__(self):
        self.entities: Set[Entity] = set()
        self.systems: Dict[Entity, List[System]] = {}
        self._id_counter = 0
        self._position_to_entity: Dict[Tuple[int, int], Set[Entity]] = {}
        self._entity_to_position: Dict[Entity, Tuple[int, int]]= {}

    def _next_id(self) -> int:
        # If the id counter becomes very large then this might kill performance, but in practise this will
        # probably never happen because everything is turn based and relatively slow, so we can just keep
        # incrementing.
        self._id_counter += 1
        return self._id_counter

    def register_system(self, system: System, *event_types: Type):
        '''
        Registers system to be called for all of the event names passed.
        '''
        for identifier in event_types:
            if identifier not in self.systems:
                self.systems[identifier] = []

            self.systems[identifier].append(system)

    def unregister_system(self, system: System, *event_types: Type):
        '''
        Unregisters system from all passed event names.
        '''
        for identifier in event_types:
            self.systems[identifier].remove(system)

    def emit_event(self, event: Event):
        '''
        Emits the given event to all systems registered for it, calling the system.process method.
        '''
        recipients = self.systems.get(type(event), [])

        for system in recipients:
            system.process(self, event)

    def create_entity(self, pos: Tuple[int, int], *components, identifier: Hashable=None) -> Entity:
        '''
        Create a new entity containing the components specified. Identifier must be unique for each entity.
        If identifier is not specified, an identifier will be automatically chosen.

        Returns: the new entity
        '''
        if identifier is None:
            identifier = self._next_id()
        
        if identifier in self.entities:
            raise ValueError(f"Entity with identifier {identifier} already exists.")

        entity = Entity(identifier, {type(c) : c for c in components})

        if pos in self._position_to_entity:
            self._position_to_entity[pos].add(entity)
        else:
            self._position_to_entity[pos] = set([entity])

        self._entity_to_position[entity] = pos
        self.entities.add(entity)
        return entity
    
    def remove_entity(self, entity: Entity):
        pos = self._entity_to_position[entity]
        self._position_to_entity[pos].remove(entity)
        del self._entity_to_position[Entity]
        del self.entities[entity]

    def move_entity(self, entity: Entity, target: Tuple[int, int]):
        '''
        Use this function to change an entities position.
        '''
        old_pos = self.get_pos(entity)

        # entity removed from grid
        self._position_to_entity[old_pos].remove(entity)
        
        if target in self._position_to_entity:
            self._position_to_entity[target].add(entity)
        else:
            self._position_to_entity[target] = set([entity])

        self._entity_to_position[entity] = target


    def query_entities(self, query: Callable[[Entity], bool]) -> Generator[Entity, None, None]:
        '''
        O(n) query over all entities. 
        '''
        return (entity for entity in self.entities if query(entity))
    
    def query_all_with_components(self, *component_types) -> Generator[Entity, None, None]:
        '''
        Queries all entities that have all of the specified components.
        '''
        # TODO: Improve the performance of this query if the current implementation is not fast enough.
        return self.query_entities(lambda entity: set(component_types) <= entity.components.keys())
    
    def query_single_with_component(self, component_type) -> Entity:
        '''
        Meant for cases where only one entity that has the specified component exists.
        '''
        # TODO: Improve the performance of this query if the current implementation is not fast enough.
        result = list(self.query_all_with_components(component_type))
        
        if not result:
            raise KeyError(f"Failed query for {component_type}, no entity for this component type exists.")

        return result[0]    
    
    def get_entities_at(self, pos: Tuple[int, int]) -> Set[Entity]:
        '''
        Return a set of entities at a given position
        '''
        return self._position_to_entity[pos]

    def get_pos(self, entity: Entity) -> Tuple[int, int]:
        '''
        Use this to get the position of an entity.
        '''
        return self._entity_to_position[entity]
    
    def __getitem__(self, identifier):
        return self.entities[identifier]
    
class TilemapEcs(ECS):
    '''
    (Usually) singleton object central to the entity component system. This one comes with an included tilemap.
    It stores entities and components and calls systems via events. It also stores and manages the tilemap.
    '''
    def __init__(self, tilemap: tiles.Tilemap):
        super().__init__()
        self.tilemap: tiles.Tilemap = tilemap
    
    