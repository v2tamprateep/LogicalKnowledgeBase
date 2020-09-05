
from unittest import TestCase

from logic.FirstOrderLogic import *


class EvaluationTests(TestCase):

    def test_existentialquantifier_evaluation(self):
        self.assertFalse(True)

    def test_binaryfunction_evaluation(self):
        alice = Entity('Alice')
        bob = Entity('Bob')

        func = BinaryFunction('areEqual', ['p1', 'p2'], lambda p, q: p == q)

        self.assertTrue(func.evaluate([], bindings={'p1': alice, 'p2': alice}))
        self.assertFalse(func.evaluate([], bindings={'p1': alice, 'p2': bob}))

    def test_unaryfunction_evaluation(self):
        alice = Entity('Alice')
        bob = Entity('Bob')

        func = UnaryFunction('isAlice', 'p1', lambda p: p.name == 'Alice')

        self.assertTrue(func.evaluate([], bindings={'p1': alice}))
        self.assertFalse(func.evaluate([], bindings={'p1': bob}))

    def test_universalquantifier_evaluation(self):
        self.assertFalse(True)