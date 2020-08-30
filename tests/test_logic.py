
from unittest import TestCase

from logic.Logic import *


class EvaluationTests(TestCase):

    def test_andclause_evaluation(self):
        entityA = Entity('A')
        entityB = Entity('B')

        # Components are all true
        clause = AndClause([entityA, entityB])
        self.assertTrue(clause.evaluate(facts=set([entityA, entityB])))

        # Components are all false
        clause = AndClause([entityA, entityB])
        self.assertFalse(clause.evaluate(set()))

        # Some components are false
        clause = AndClause([entityA, entityB])
        self.assertFalse(clause.evaluate(facts=set([entityA])))
        self.assertFalse(clause.evaluate(facts=set([entityB])))

    def test_entity_evaluation(self):
        entityA = Entity('A')

        # Entity is true
        self.assertTrue(entityA.evaluate(facts=set([entityA])))

        # Entity is false
        self.assertFalse(entityA.evaluate(facts=set()))

    def test_notclause_evaluation(self):
        entityA = Entity('A')

        # Component is true
        clause = NotClause(entityA)
        self.assertFalse(clause.evaluate(facts=set([entityA])))

        # Components is false
        clause = NotClause(entityA)
        self.assertTrue(clause.evaluate(facts=set()))

    def test_orclause_evaluation(self):
        entityA = Entity('A')
        entityB = Entity('B')

        # Components are all true
        clause = OrClause([entityA, entityB])
        self.assertTrue(clause.evaluate(facts=set([entityA, entityB])))

        # Components are all false
        clause = OrClause([entityA, entityB])
        self.assertFalse(clause.evaluate(facts=set()))

        # Some components are false
        clause = OrClause([entityA, entityB])
        self.assertTrue(clause.evaluate(facts=set([entityA])))
        self.assertTrue(clause.evaluate(facts=set([entityB])))

    def test_predicate_evaluation(self):
        entityA = Entity('A')
        entityB = Entity('B')
        predicate = Predicate(entityA, entityB)

        # If the LHS is false, always evaluate to true
        self.assertTrue(predicate.evaluate(facts=set()))
        self.assertTrue(predicate.evaluate(facts=set([entityB])))

        # if the LHS is true, evaluate to the boolean value of the RHS
        self.assertFalse(predicate.evaluate(facts=set([entityA])))
        self.assertTrue(predicate.evaluate(facts=set([entityA, entityB])))


class PredicateConversionTests(TestCase):

    def assert_predicate_conversion(self, sentence: Sentence):
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
            self.assert_predicate_conversion(clause)

    def test_entity_to_predicate(self):
        entity = Entity('A')
        self.assert_predicate_conversion(entity)