
import itertools
from typing import Callable, Iterable, Mapping

from logic.Logic import Entity, Sentence


class Function(Sentence):

    def __init__(self,
                 name: str,
                 variables: Iterable[str],
                 action: Callable):
        self._name = name
        self._variables = variables
        self._action = action


class UnaryFunction(Function):

    def __init__(self,
                 name: str,
                 variable: str,
                 action: Callable[[Entity], bool]):
        super().__init__(name, [variable], action)

    def evaluate(self, facts: Iterable[Entity], bindings: Mapping[str, Entity]=None) -> bool:
        entity = bindings[self._variables[0]] if bindings else facts[self._variables[0]]
        return self._action(entity)


class BinaryFunction(Function):

    def __init__(self,
                 name: str,
                 variables: Iterable[str],
                 action: Callable[[Entity, Entity], bool]):
        super().__init__(name, variables, action)

    def evaluate(self, facts: Iterable[Entity], bindings: Mapping[str, Entity]=None) -> bool:
        entity1 = bindings[self._variables[0]] if bindings else facts[self._variables[0]]
        entity2 = bindings[self._variables[1]] if bindings else facts[self._variables[1]]
        return self._action(entity1, entity2)


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

    def evaluate(self, facts: Iterable[Entity]) -> bool:
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

    def evaluate(self, facts: Iterable[Entity]) -> bool:
        # TODO: Do we need to normalize the variables so they don't overlap with atoms in the knowledgebase?
        permutations = itertools.permutations(facts, len(self._variables))
        for permutation in permutations:
            # create a mapping of variable to atom in knowledgebase
            bindings = Quantifier._create_bindings(self._variables, permutation)
            if not self._predicate.evaluate(facts, bindings):
                return False

        return True