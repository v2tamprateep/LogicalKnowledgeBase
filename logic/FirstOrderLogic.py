
import itertools
from typing import Callable, Iterable, Mapping

from logic.Logic import Entity, Sentence


class Function(Sentence):

    def __init__(self,
                 name: str,
                 variables: Iterable[str]):
        self._name = f'{name}({",".join(variables)})'
        self._variables = variables

    def evaluate(self,
                 entities: Mapping[str, Entity],
                 functions: Iterable['Function'],
                 bindings: Mapping[str, Entity]=None) -> bool:
        if bindings:
            sub_names = [bindings[variable].name for variable in self._variables]
            return Function(self._name.split('(')[0], sub_names) in functions

        return self in functions


class Quantifier(Sentence):

    @staticmethod
    def _create_bindings(variables: Iterable[str],
                         entities: Iterable[Entity]) -> Mapping[str, Entity]:
        tuples = zip(variables, entities)
        return {v: e for v, e in tuples}


class ExistentialQuantifier(Quantifier):

    def __init__(self, variables: Iterable[str], sentence: Sentence):
        self._name = f'Exists {",".join(variables)}: {sentence.name}'

        self._variables = variables
        self._predicate = sentence.to_predicate()

    def evaluate(self,
                 entities: Mapping[str, Entity],
                 functions: Iterable['Function'],
                 bindings: Mapping[str, Entity]=None) -> bool:
        # TODO: Do we need to normalize the variables so they don't overlap with atoms in the knowledgebase?
        permutations = itertools.permutations(entities.values(), len(self._variables))
        for permutation in permutations:
            # create a mapping of variable to atom in knowledgebase
            bindings = Quantifier._create_bindings(self._variables, permutation)
            if self._predicate.evaluate(entities, functions, bindings):
                return True

        return False


class UniversalQuantifier(Quantifier):

    def __init__(self, variables: Iterable[str], sentence: Sentence):
        self._name = f'ForAll {",".join(variables)}: {sentence.name}'

        self._variables = variables
        self._predicate = sentence.to_predicate()

    def evaluate(self,
                 entities: Mapping[str, Entity],
                 functions: Iterable['Function'],
                 bindings: Mapping[str, Entity]=None) -> bool:
        # TODO: Do we need to normalize the variables so they don't overlap with atoms in the knowledgebase?
        permutations = itertools.permutations(entities.values(), len(self._variables))
        for permutation in permutations:
            # create a mapping of variable to atom in knowledgebase
            bindings = Quantifier._create_bindings(self._variables, permutation)
            if not self._predicate.evaluate(entities, functions, bindings):
                return False

        return True