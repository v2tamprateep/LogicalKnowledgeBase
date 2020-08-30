
import itertools
from typing import Callable, Iterable, Mapping, Set

from Logic import Entity, Sentence


class Function(Sentence):

    def __init__(self,
                 name: str,
                 entities: Iterable[Entity],
                 action: Callable[[Iterable[Entity]], bool]):
        self._name = name
        self._entities = entities
        self._action = action

    def evaluate(self, facts: Set, bindings: Mapping[str, Entity]=None) -> bool:
        if bindings:
            substitutes = [e.substitute(bindings[e.name]) if e.name in bindings.keys() else e
                           for e in self._entities]
            return self._action(substitutes)

        return self._action(self._entities)


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

    def evaluate(self, facts: Set) -> bool:
        # TODO: Do we need to normalize the variables so they don't overlap with atoms in the knowledgebase?
        permutations = itertools.permutations(facts, len(self._variables))
        for permutation in permutations:
            # create a mapping of variable to atom in knowledgebase
            bindings = Quantifier._create_bindings(self._variables, permutation)
            if self._predicate.evaluate(facts, bindings):
                return True

        return False


class UniversalQuantifier(Quantifier):

    def __init__(self, variables: Iterable[str], sentence: Sentence):
        self._name = f'ForAll {",".join(variables)}: {predicate.name}'

        self._variables = variables
        self._predicate = sentence.to_predicate()

    def evaluate(self, facts: Set) -> bool:
        # TODO: Do we need to normalize the variables so they don't overlap with atoms in the knowledgebase?
        permutations = itertools.permutations(facts, len(self._variables))
        for permutation in permutations:
            # create a mapping of variable to atom in knowledgebase
            bindings = Quantifier._create_bindings(self._variables, permutation)
            if not self._predicate.evaluate(facts, bindings):
                return False

        return True