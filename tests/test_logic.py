
from unittest import TestCase

from logic.Logic import *


class EvaluationTests(TestCase):

    def test_andclause_evaluation(self):
        entityA = Entity('A')
        entityB = Entity('B')

        # Components are all true
        clause = AndClause([entityA, entityB])
        self.assertTrue(clause.evaluate(entities=[entityA, entityB], functions=[]))

        # Components are all false
        clause = AndClause([entityA, entityB])
        self.assertFalse(clause.evaluate(entities=[], functions=[]))

        # Some components are false
        clause = AndClause([entityA, entityB])
        self.assertFalse(clause.evaluate(entities=[entityA], functions=[]))
        self.assertFalse(clause.evaluate(entities=[entityB], functions=[]))

    def test_entity_evaluation(self):
        entityA = Entity('A')

        # Entity is true
        self.assertTrue(entityA.evaluate(entities=[entityA], functions=[]))

        # Entity is false
        self.assertFalse(entityA.evaluate(entities=[], functions=[]))

    def test_notclause_evaluation(self):
        entityA = Entity('A')

        # Component is true
        clause = NotClause(entityA)
        self.assertFalse(clause.evaluate(entities=[entityA], functions=[]))

        # Components is false
        clause = NotClause(entityA)
        self.assertTrue(clause.evaluate(entities=[], functions=[]))

    def test_orclause_evaluation(self):
        entityA = Entity('A')
        entityB = Entity('B')

        # Components are all true
        clause = OrClause([entityA, entityB])
        self.assertTrue(clause.evaluate(entities=[entityA, entityB], functions=[]))

        # Components are all false
        clause = OrClause([entityA, entityB])
        self.assertFalse(clause.evaluate(entities=[], functions=[]))

        # Some components are false
        clause = OrClause([entityA, entityB])
        self.assertTrue(clause.evaluate(entities=[entityA], functions=[]))
        self.assertTrue(clause.evaluate(entities=[entityB], functions=[]))

    def test_predicate_evaluation(self):
        entityA = Entity('A')
        entityB = Entity('B')
        predicate = Predicate(entityA, entityB)

        # If the LHS is false, always evaluate to true
        self.assertTrue(predicate.evaluate(entities=[], functions=[]))
        self.assertTrue(predicate.evaluate(entities=[entityB], functions=[]))

        # if the LHS is true, evaluate to the boolean value of the RHS
        self.assertFalse(predicate.evaluate(entities=[entityA], functions=[]))
        self.assertTrue(predicate.evaluate(entities=[entityA, entityB], functions=[]))


class PredicateConversionTests(TestCase):

    def _assert_predicate_conversion(self, sentence: Sentence):
        predicate = sentence.to_predicate()

        self.assertEqual(predicate.lhs, Entity('True'))
        self.assertEqual(predicate.rhs, sentence)

    def test_clause_to_predicate(self):
        entityA = Entity('A')
        entityB = Entity('B')

        and_clause = AndClause([entityA, entityB])
        or_clause = OrClause([entityA, entityB])
        not_clause = NotClause(entityA)

        for clause in [and_clause, or_clause, not_clause]:
            self._assert_predicate_conversion(clause)

    def test_entity_to_predicate(self):
        entity = Entity('A')
        self._assert_predicate_conversion(entity)