from cnfc.regex import *
from cnfc import *
from .util import SatTestCase, write_cnf_to_string

import itertools
import unittest

class TestRegex(unittest.TestCase, SatTestCase):
    def test_epsilon_closure(self):
        delta = new_nfa_delta()
        delta['a'][EPSILON] = {'b','c'}
        delta['b'][EPSILON] = {'a','c'}
        delta['c'][EPSILON] = {'d'}
        delta['d'][EPSILON] = {'b'}
        delta['b'][ONE] = {'e'}
        delta['e'][EPSILON] = {'a'}
        n = NFA('a', {'y','z'}, delta)
        self.assertEqual(epsilon_closure(n, {'a'}), {'a','b','c','d'})
        self.assertEqual(epsilon_closure(n, {'b'}), {'a','b','c','d'})
        self.assertEqual(epsilon_closure(n, {'c'}), {'a','b','c','d'})
        self.assertEqual(epsilon_closure(n, {'d'}), {'a','b','c','d'})
        self.assertEqual(epsilon_closure(n, {'e'}), {'a','b','c','d','e'})
        self.assertEqual(epsilon_closure(n, {'f'}), {'f'})

    def test_illegal_dfa_parse(self):
        with self.assertRaises(ValueError):
            regex_to_dfa('01a')

    def test_simple_dfa_parse(self):
        self.assertTrue(regex_to_dfa('').accepts(''))
        self.assertFalse(regex_to_dfa('').accepts('0'))
        self.assertTrue(regex_to_dfa('0').accepts('0'))
        self.assertFalse(regex_to_dfa('0').accepts('1'))
        self.assertTrue(regex_to_dfa('001').accepts('001'))
        self.assertFalse(regex_to_dfa('001').accepts('100'))
        self.assertFalse(regex_to_dfa('001').accepts('00'))
        self.assertFalse(regex_to_dfa('001').accepts('0011'))

    def test_subexpressions(self):
        self.assertTrue(regex_to_dfa('(0)').accepts('0'))
        self.assertTrue(regex_to_dfa('(010)').accepts('010'))
        self.assertTrue(regex_to_dfa('(0)1(1)').accepts('011'))

    def test_alternation(self):
        self.assertTrue(regex_to_dfa('0|1').accepts('0'))
        self.assertTrue(regex_to_dfa('0|1').accepts('1'))
        self.assertFalse(regex_to_dfa('0|1').accepts(''))
        self.assertFalse(regex_to_dfa('0|1').accepts('00'))
