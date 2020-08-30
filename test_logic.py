
from unittest import TestCase

from logic import *


class AtomTests(TestCase):

    def test_atom_to_predicate(self):
        atom = Atom('A')
        predicate = atom.to_predicate()

        self.assertEqual(predicate.lhs, True)
        self.assertEqual(predicate.rhs, atom)

