
from abc import ABC, abstractmethod
from enum import Enum
import itertools
from typing import Any, Callable, Iterable, Mapping, Union


"""
In this context, a sentence is any evaluatable expression.
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
                 knowledge_base: 'KnowledgeBase',
                 bindings: Mapping[str, 'Entity']=None) -> bool:
        pass


"""
TODO: Rethink class hierarchy
"""
class Entity(Sentence):

    def __init__(self, name: str, attributes: Iterable[str]=None):
        self._name = name

        self.attributes = set(attributes) if attributes else set()

    def evaluate(self,
                 knowledge_base: 'KnowledgeBase',
                 bindings: Mapping[str, 'Entity']=None) -> bool:
        if bindings and self.name in bindings.keys():
            return self.substitute(bindings[self.name]) in knowledge_base.truths

        return self in knowledge_base.truths

    def substitute(self, new_name: str) -> 'Entity':
        return Entity(new_name, self.attributes)

    def to_predicate(self) -> 'Predicate':
        return Predicate(Entity('True'), self)


class Function(Sentence):

    def __init__(self,
                 name: str,
                 entities: Iterable[Entity],
                 action: Callable[[Iterable[Entity]], bool]):
        self._name = name
        self._entities = entities
        self._action = action

    def evaluate(self,
                 knowledge_base: 'KnowledgeBase',
                 bindings: Mapping[str, Entity]=None) -> bool:
        if bindings:
            substitutes = [e.substitute(bindings[e.name]) if e.name in bindings.keys() else e
                           for e in self._entities]
            return self._action(substitutes)

        return self._action(self._entities)


"""
A clause is a group of atoms or smaller subclauses.
"""
class Clause(Sentence):

    @abstractmethod
    def evaluate(self, knowledge_base: 'KnowledgeBase') -> bool:
        pass

    def get_components(self) -> Union[str, Iterable]:
        return self.clause_type, self.sub_clauses

    def to_predicate(self) -> 'Predicate':
        return Predicate(Entity('True'), self)


"""
A clause that evaluates to True if all subcomponents evaluate to True and False otherwise.
"""
class AndClause(Clause):

    def __init__(self, clauses: Iterable[Sentence]):
        self.clause_type = 'and'
        self._name = f' and '.join([f'({clause.name})' for clause in clauses])

        self.sub_clauses = clauses

    def evaluate(self,
                 knowledge_base: 'KnowledgeBase',
                 bindings: Mapping[str, Entity]=None) -> bool:
        return all([clause.evaluate(knowledge_base, bindings) for clause in self.sub_clauses])


"""
A single clause that evaluates to the negation of the clause's evaluation
"""
class NotClause(Clause):

    def __init__(self, clause: Sentence):
        self.clause_type = 'not'
        self._name = f'not ({clause.name})'

        self.sub_clauses = [clause]

    def evaluate(self,
                 knowledge_base: 'KnowledgeBase',
                 bindings: Mapping[str, Entity]=None) -> bool:
        return not self.sub_clauses[0].evaluate(knowledge_base, bindings)


"""
A clause that evaluates to True if any subcomponents evaluate to True and False otherwise.
"""
class OrClause(Clause):

    def __init__(self, clauses: Iterable[Sentence]):
        self.clause_type = 'or'
        self._name = f' or '.join([f'({clause.name})' for clause in clauses])

        self.sub_clauses = clauses

    def evaluate(self, knowledge_base: 'KnowledgeBase', bindings: Mapping[str, Entity]=None) -> bool:
        return any([clause.evaluate(knowledge_base, bindings) for clause in self.sub_clauses])


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
                 knowledge_base: 'KnowledgeBase',
                 bindings: Mapping[str, Entity]=None) -> bool:
        return not self.lhs.evaluate(knowledge_base, bindings) \
            or self.rhs.evaluate(knowledge_base, bindings)

    def to_predicate(self):
        return self


class Quantifier(Sentence):

    @staticmethod
    def _create_bindings(variables: Iterable[str],
                         entities: Iterable[Entity]) -> Mapping[str, Entity]:
        tuples = zip(variables, entities)
        return {v: e for v, e in tuples}

    def to_predicate(self) -> 'Predicate':
        return Predicate(Entity('True'), self)


class ExistentialQuantifier(Quantifier):

    def __init__(self, variables: Iterable[str], sentence: Sentence):
        self._name = f'Exists {",".join(variables)}: {predicate.name}'

        self._variables = variables
        self._predicate = sentence.to_predicate()

    def evaluate(self, knowledge_base: 'KnowledgeBase') -> bool:
        # TODO: Do we need to normalize the variables so they don't overlap with atoms in the knowledgebase?
        permutations = itertools.permutations(knowledge_base.truths, len(self._variables))
        for permutation in permutations:
            # create a mapping of variable to atom in knowledgebase
            bindings = Quantifier._create_bindings(self._variables, permutation)
            if self._predicate.evaluate(knowledge_base, bindings):
                return True

        return False


class UniversalQuantifier(Quantifier):

    def __init__(self, variables: Iterable[str], sentence: Sentence):
        self._name = f'ForAll {",".join(variables)}: {predicate.name}'

        self._variables = variables
        self._predicate = sentence.to_predicate()

    def evaluate(self, knowledge_base: 'KnowledgeBase') -> bool:
        # TODO: Do we need to normalize the variables so they don't overlap with atoms in the knowledgebase?
        permutations = itertools.permutations(knowledge_base.truths, len(self._variables))
        for permutation in permutations:
            # create a mapping of variable to atom in knowledgebase
            bindings = Quantifier._create_bindings(self._variables, permutation)
            if not self._predicate.evaluate(knowledge_base, bindings):
                return False

        return True


class KnowledgeBase():

    def __init__(self):
        self._entities = dict()
        self._facts = set()

        self._entities['True'] = Entity('True')

    # TODO: Is there a way to generalize this?
    def _entails_atom(self, atom: Entity) -> bool:
        if atom in self._entities.values():
            return True

        relevant_facts = [fact for fact in self._facts if fact.rhs == atom]
        for fact in relevant_facts:
            if self.entails(fact.lhs):
                return True

        return False

    def _entails_clause(self, clause: Clause) -> bool:
        clause_type, components = clause.get_components()

        results = [self.entails(component) for component in components]
        if clause_type == 'and':
            return all(results)
        elif clause_type == 'or':
            return any(results)
        else:
            return not results[0]

    def add_entity_attributes(self, entity_name: str, attributes: Union[str, Iterable[str]]):
        self.entities[entity_name].attributes.update(attributes)

    def entails(self, query: Union[Entity, Clause]) -> bool:
        if type(query) is Entity:
            return self._entails_atom(query)

        if issubclass(type(query), Clause):
            return self._entails_clause(query)

        return False

    @property
    def entities(self):
        return self._entities

    @property
    def facts(self):
        return self._facts

    def remove_entity_attributes(self, entity_name: str, attributes: Union[str, Iterable[str]]):
        entity = self.entities[entity_name]
        for attribute in attributes:
            entity.attributes.discard(attribute)

    def tell(self, sentence: Sentence):
        if type(sentence) is Entity:
            self._entities.add(sentence)
        else:
            self._facts.add(sentence.to_predicate())