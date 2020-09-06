
from unittest import TestCase
from typing import Iterable, Mapping

from logic.FirstOrderLogic import *


def entity_list_to_dictionary(entities: Iterable[Entity]) -> Mapping[str, Entity]:
        return {e.name: e for e in entities}


class EvaluationTests(TestCase):

    def test_existentialquantifier_evaluation(self):
        alice = Entity('Alice')
        bob = Entity('Bob')
        carol = Entity('Carol')

        are_friends = Function('areFriends', ['p1', 'p2'])
        quantifier = ExistentialQuantifier(['p1', 'p2'], are_friends)

        entities = entity_list_to_dictionary([alice, bob, carol])

        self.assertFalse(quantifier.evaluate(entities, functions=[]))

        functions = [Function('areFriends', ['Alice', 'Bob'])]
        self.assertTrue(quantifier.evaluate(entities, functions))

    def test_function_evaluation(self):
        alice = Entity('Alice')
        bob = Entity('Bob')

        func = Function('isAlice', ['p1, p2'])

        func1 = Function('isAlice', ['p1', 'p3'])
        func2 = Function('isBob', ['p1, p2'])
        # Identical function but different instance
        func3 = Function('isAlice', ['p1, p2'])

        self.assertFalse(func.evaluate(entities=dict(), functions=[func1]))
        self.assertFalse(func.evaluate(entities=dict(), functions=[func2]))
        self.assertTrue(func.evaluate(entities=dict(), functions=[func3]))

    def test_universalquantifier_evaluation(self):
        alice = Entity('Alice')
        bob = Entity('Bob')
        carol = Entity('Carol')

        are_friends = Function('areFriends', ['p1', 'p2'])
        quantifier = UniversalQuantifier(['p1', 'p2'], are_friends)

        entities = entity_list_to_dictionary([alice, bob, carol])
        functions = []
        self.assertFalse(quantifier.evaluate(entities, functions))

        functions.extend(
            [Function('areFriends', ['Alice', 'Bob']),
            Function('areFriends', ['Bob', 'Carol']),
            Function('areFriends', ['Carol', 'Alice'])])
        self.assertFalse(quantifier.evaluate(entities, functions))

        functions.extend(
            [Function('areFriends', ['Alice', 'Carol']),
            Function('areFriends', ['Bob', 'Alice']),
            Function('areFriends', ['Carol', 'Bob'])])
        self.assertTrue(quantifier.evaluate(entities, functions))


class NestedQuantifierTests(TestCase):

    def test_nested_existentialquantifier(self):
        alice = Entity('Alice')
        bob = Entity('Bob')
        carol = Entity('Carol')

        # Construct something along the lines of: ExEy.AreFriends(x, y)
        are_friends = Function('areFriends', ['p1', 'p2'])
        inner_quantifier = ExistentialQuantifier(['p2'], are_friends)
        outer_quantifier = ExistentialQuantifier(['p1'], inner_quantifier)

        entities = entity_list_to_dictionary([alice, bob, carol])

        self.assertFalse(outer_quantifier.evaluate(entities, functions=[]))

        functions = [Function('areFriends', ['Alice', 'Bob'])]
        self.assertTrue(outer_quantifier.evaluate(entities, functions))

    def test_nested_mixed_quantifiers(self):
        pass

    def test_nested_universalquantifier(self):
        pass