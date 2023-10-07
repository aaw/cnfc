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
        delta['e'][EPSILON] = {'a','e'}
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

    def test_question(self):
        self.assertTrue(regex_to_dfa('0?').accepts('0'))
        self.assertTrue(regex_to_dfa('0?').accepts(''))
        self.assertFalse(regex_to_dfa('0?').accepts('00'))

    def test_plus(self):
        self.assertTrue(regex_to_dfa('0+').accepts('0'))
        self.assertTrue(regex_to_dfa('0+').accepts('00'))
        self.assertTrue(regex_to_dfa('0+').accepts('00000000000'))
        self.assertFalse(regex_to_dfa('0+').accepts(''))
        self.assertFalse(regex_to_dfa('0+').accepts('1'))

    def test_kleene_star(self):
        self.assertTrue(regex_to_dfa('1*').accepts(''))
        self.assertTrue(regex_to_dfa('1*').accepts('1'))
        self.assertTrue(regex_to_dfa('1*').accepts('11'))
        self.assertTrue(regex_to_dfa('1*').accepts('1111111'))
        self.assertFalse(regex_to_dfa('1*').accepts('1101111'))
        self.assertFalse(regex_to_dfa('1*').accepts('00000'))
        self.assertFalse(regex_to_dfa('1*').accepts('0'))

    def test_fixed_repetitions(self):
        self.assertFalse(regex_to_dfa('1{4}').accepts(''))
        self.assertFalse(regex_to_dfa('1{4}').accepts('1'))
        self.assertFalse(regex_to_dfa('1{4}').accepts('11'))
        self.assertFalse(regex_to_dfa('1{4}').accepts('111'))
        self.assertTrue(regex_to_dfa('1{4}').accepts('1111'))
        self.assertFalse(regex_to_dfa('1{4}').accepts('11111'))
        self.assertFalse(regex_to_dfa('1{4}').accepts('0000'))

    def test_fixed_bounds(self):
        self.assertFalse(regex_to_dfa('1{2,4}').accepts(''))
        self.assertFalse(regex_to_dfa('1{2,4}').accepts('1'))
        self.assertTrue(regex_to_dfa('1{2,4}').accepts('11'))
        self.assertTrue(regex_to_dfa('1{2,4}').accepts('111'))
        self.assertTrue(regex_to_dfa('1{2,4}').accepts('1111'))
        self.assertFalse(regex_to_dfa('1{2,4}').accepts('11111'))
        self.assertFalse(regex_to_dfa('1{2,4}').accepts('0000'))

    def test_branch(self):
        regex = '((01)|(100))'
        self.assertTrue(regex_to_dfa(regex).accepts('01'))
        self.assertTrue(regex_to_dfa(regex).accepts('100'))
        self.assertFalse(regex_to_dfa(regex).accepts('1000'))
        self.assertFalse(regex_to_dfa(regex).accepts('0100'))
        self.assertFalse(regex_to_dfa(regex).accepts('11'))
        self.assertFalse(regex_to_dfa(regex).accepts('10'))
        self.assertFalse(regex_to_dfa(regex).accepts(''))

    def test_composition(self):
        regex = '0(1|(00))+1?'
        self.assertTrue(regex_to_dfa(regex).accepts('01'))
        self.assertTrue(regex_to_dfa(regex).accepts('011'))
        self.assertTrue(regex_to_dfa(regex).accepts('0001'))
        self.assertTrue(regex_to_dfa(regex).accepts('000'))
        self.assertTrue(regex_to_dfa(regex).accepts('000000000'))
