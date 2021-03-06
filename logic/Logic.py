
from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, Mapping, Tuple, Union


"""
Any evaluatable expression
"""
class Sentence(ABC):

    def __init__(self):
        self._name = ''

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name

    def __hash__(self):
        return hash(self._name)

    def __str__(self):
        return self._name

    @property
    def name(self):
        return self._name

    @abstractmethod
    def evaluate(self,
                 entities: Mapping[str, 'Entity'],
                 functions: Iterable['Function'],
                 bindings: Mapping[str, 'Entity']=None) -> bool:
        pass

    def to_predicate(self) -> 'Predicate':
        return Predicate(Entity('True'), self)


"""
An atomic boolean variable
"""
class Entity(Sentence):

    # Attributes are tuples of attribute name and attribute value (None if not applicable)
    def __init__(self, name: str, attributes: Mapping[str, Iterable]=None):
        self._name = name
        self._attributes = attributes if attributes else dict()

    def udpate_attribute(self, attribute: str, value: Iterable[Any]):
        self._attributes.setdefault(attribute, []).append(value)

    def evaluate(self,
                 entities: Mapping[str, 'Entity'],
                 functions: Iterable['Function'],
                 bindings: Mapping[str, 'Entity']=None) -> bool:
        if bindings and self.name in bindings.keys():
            return self.substitute(bindings[self.name]) in entities

        return self.name == 'True' or self in entities

    def substitute(self, new_name: str) -> 'Entity':
        return Entity(new_name, self.attributes)


class Clause(Sentence):

    def __init__(self, clause_type: str, clauses: Iterable[Sentence]):
        self.clause_type = clause_type
        self.sub_clauses = clauses

        if clause_type == 'not':
            self._name = f'not ({clauses[0].name})'
        else:
            self._name = f' {clause_type} '.join([f'({clause.name})' for clause in clauses])


"""
A clause is a group of atoms or smaller subclauses.
"""
class AndClause(Clause):

    def __init__(self, clauses: Iterable[Sentence]):
        super().__init__('and', clauses)

    def evaluate(self,
                 entities: Mapping[str, Entity],
                 functions: Iterable['Function'],
                 bindings: Mapping[str, Entity]=None) -> bool:
        return all([clause.evaluate(entities, functions, bindings) for clause in self.sub_clauses])


class NotClause(Clause):

    def __init__(self, clause: Sentence):
        super().__init__('not', [clause])

    def evaluate(self,
                 entities: Mapping[str, Entity],
                 functions: Iterable['Function'],
                 bindings: Mapping[str, Entity]=None) -> bool:
        return not self.sub_clauses[0].evaluate(entities, functions, bindings)


class OrClause(Clause):

    def __init__(self, clauses: Iterable[Sentence]):
        super().__init__('or', clauses)

    def evaluate(self,
                 entities: Mapping[str, Entity],
                 functions: Iterable['Function'],
                 bindings: Mapping[str, Entity]=None) -> bool:
        return any([clause.evaluate(entities, functions, bindings) for clause in self.sub_clauses])


"""
A predicate has left hand side (lhs) and right hand side (rhs) sentences. A predicate evaluates to
true if lhs implies (->) rhs.
"""
class Predicate(Sentence):

    def __init__(self, left: Union[Entity, Clause], right: Union[Entity, Clause]):
        self._name = f'({left.name}) -> ({right.name})'

        self.lhs = left
        self.rhs = right

    def evaluate(self,
                 entities: Mapping[str, Entity],
                 functions: Iterable['Function'],
                 bindings: Mapping[str, Entity]=None) -> bool:
        return not self.lhs.evaluate(entities, functions, bindings) \
            or self.rhs.evaluate(entities, functions, bindings)

    def to_predicate(self):
        return self