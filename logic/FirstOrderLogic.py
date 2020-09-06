
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

    def __init__(self, quantifier_type: str, variables: Iterable[str], sentence: Sentence):
        self._name = f'{quantifier_type} {",".join(variables)}: {sentence.name}'

        self._variables = variables
        self._predicate = sentence.to_predicate()

    @staticmethod
    def _create_bindings(variables: Iterable[str],
                         entities: Iterable[Entity]) -> Mapping[str, Entity]:
        tuples = zip(variables, entities)
        return {v: e for v, e in tuples}

    def _normalize(self, existing_bindings: Mapping[str, Entity]) -> str:
        existing_variables = [existing_bindings.keys()]
        normalized_vars = []

        for variable in self._variables:
            if not variable in existing_variables:
                normalized_vars.append(variable)
                existing_variables.append(variable)

            count = 1
            while f'{variable}{count}' in existing_variables:
                count = count + 1

            normalized_var = f'{variable}{count}'
            normalized_vars.append(variable)
            existing_variables.append(variable)

        self._variables = normalized_vars

    def evaluate(self,
                 entities: Mapping[str, Entity],
                 functions: Iterable[Function],
                 bindings: Mapping[str, Entity]=dict()) -> bool:
        self._normalize(bindings)

        permutations = itertools.permutations(entities.values(), len(self._variables))
        return self.evaluate_permutations(permutations, entities, functions, bindings)


class ExistentialQuantifier(Quantifier):

    def __init__(self, variables: Iterable[str], sentence: Sentence):
        super().__init__('Exists', variables, sentence)

    def evaluate_permutations(self,
                              permutations: Iterable,
                              entities: Mapping[str, Entity],
                              functions: Iterable[Function],
                              bindings: Mapping[str, Entity]) -> bool:
        for permutation in permutations:
            # Update the mapping of variable to entity in knowledgebase
            new_bindings = \
                Quantifier._create_bindings(self._variables, permutation).update(bindings)
            if self._predicate.evaluate(entities, functions, new_bindings):
                return True

        return False


class UniversalQuantifier(Quantifier):

    def __init__(self, variables: Iterable[str], sentence: Sentence):
        super().__init__('ForAll', variables, sentence)

    def evaluate_permutations(self,
                              permutations: Iterable,
                              entities: Mapping[str, Entity],
                              functions: Iterable[Function],
                              bindings: Mapping[str, Entity]) -> bool:
        for permutation in permutations:
            # Update the mapping of variable to entity in knowledgebase
            new_bindings = \
                Quantifier._create_bindings(self._variables, permutation).update(bindings)
            if not self._predicate.evaluate(entities, functions, new_bindings):
                return False

        return True