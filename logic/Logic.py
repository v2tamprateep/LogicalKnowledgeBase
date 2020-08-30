
from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, Mapping, Set, Union


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
    def evaluate(self, facts: Set, bindings: Mapping[str, 'Entity']=None) -> bool:
        pass

    def to_predicate(self) -> 'Predicate':
        return Predicate(Entity('True'), self)


"""
An atomic boolean variable
"""
class Entity(Sentence):

    def __init__(self, name: str, attributes: Iterable[str]=None):
        self._name = name

        self.attributes = set(attributes) if attributes else set()

    def evaluate(self, facts: Set, bindings: Mapping[str, 'Entity']=None) -> bool:
        if bindings and self.name in bindings.keys():
            return self.substitute(bindings[self.name]) in facts

        return self in facts

    def substitute(self, new_name: str) -> 'Entity':
        return Entity(new_name, self.attributes)


"""
A clause is a group of atoms or smaller subclauses.
"""
class AndClause(Sentence):

    def __init__(self, clauses: Iterable[Sentence]):
        self.clause_type = 'and'
        self._name = f' and '.join([f'({clause.name})' for clause in clauses])

        self.sub_clauses = clauses

    def evaluate(self, facts: Set, bindings: Mapping[str, Entity]=None) -> bool:
        return all([clause.evaluate(facts, bindings) for clause in self.sub_clauses])


class NotClause(Sentence):

    def __init__(self, clause: Sentence):
        self.clause_type = 'not'
        self._name = f'not ({clause.name})'

        self.sub_clauses = [clause]

    def evaluate(self, facts: Set, bindings: Mapping[str, Entity]=None) -> bool:
        return not self.sub_clauses[0].evaluate(facts, bindings)


class OrClause(Sentence):

    def __init__(self, clauses: Iterable[Sentence]):
        self.clause_type = 'or'
        self._name = f' or '.join([f'({clause.name})' for clause in clauses])

        self.sub_clauses = clauses

    def evaluate(self, facts: Set, bindings: Mapping[str, Entity]=None) -> bool:
        return any([clause.evaluate(facts, bindings) for clause in self.sub_clauses])


"""
A predicate has left hand side (lhs) and right hand side (rhs) sentences. A predicate evaluates to
true if lhs implies (->) rhs.
"""
class Predicate(Sentence):

    def __init__(self, left: Union[Entity, Clause], right: Union[Entity, Clause]):
        self._name = f'({left.name}) -> ({right.name})'

        self.lhs = left
        self.rhs = right

    def evaluate(self, facts: Set, bindings: Mapping[str, Entity]=None) -> bool:
        return not self.lhs.evaluate(facts, bindings) \
            or self.rhs.evaluate(facts, bindings)

    def to_predicate(self):
        return self