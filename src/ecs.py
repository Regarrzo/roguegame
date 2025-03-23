'''
Main ECS engine file. No game specific logic goes here. This file is also heavily type hinted.
'''
from __future__ import annotations
from typing import *
from dataclasses import field, dataclass
from abc import ABC, abstractmethod

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
        self.entities: Dict[Hashable, Entity] = {}
        self.systems: Dict[Hashable, List[System]] = {}
        self._id_counter = 0

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

    def create_entity(self, *components, identifier: Hashable=None) -> Entity:
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

        self.entities[identifier] = entity
        return entity
    
    def remove_entity(self, identifier: Hashable):
        del self.entities[identifier]

    def query_entities(self, query: Callable[[Entity], bool]) -> Generator[Entity, None, None]:
        '''
        O(n) query over all entities. 
        '''
        return (entity for entity in self.entities.values() if query(entity))
    
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
    
    def __getitem__(self, identifier):
        return self.entities[identifier]