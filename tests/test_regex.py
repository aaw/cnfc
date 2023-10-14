from cnfc.regex import *
from cnfc import *
from .util import SatTestCase, write_cnf_to_string

import itertools
import unittest

def dfa_accepts(dfa, s):
    state = dfa.initial
    m = {'0': ZERO, '1': ONE}
    for ch in s:
        xch = m.get(ch)
        if xch is None: return False
        state = dfa.delta[state].get(xch)
        if state is None: return False
    return state in dfa.accepting

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
        self.assertTrue(dfa_accepts(regex_to_dfa(''), ''))
        self.assertFalse(dfa_accepts(regex_to_dfa(''), '0'))
        self.assertTrue(dfa_accepts(regex_to_dfa('0'), '0'))
        self.assertFalse(dfa_accepts(regex_to_dfa('0'), '1'))
        self.assertTrue(dfa_accepts(regex_to_dfa('001'), '001'))
        self.assertFalse(dfa_accepts(regex_to_dfa('001'), '100'))
        self.assertFalse(dfa_accepts(regex_to_dfa('001'), '00'))
        self.assertFalse(dfa_accepts(regex_to_dfa('001'), '0011'))

    def test_subexpressions(self):
        self.assertTrue(dfa_accepts(regex_to_dfa('(0)'), '0'))
        self.assertTrue(dfa_accepts(regex_to_dfa('(010)'), '010'))
        self.assertTrue(dfa_accepts(regex_to_dfa('(0)1(1)'), '011'))

    def test_alternation(self):
        self.assertTrue(dfa_accepts(regex_to_dfa('0|1'), '0'))
        self.assertTrue(dfa_accepts(regex_to_dfa('0|1'), '1'))
        self.assertFalse(dfa_accepts(regex_to_dfa('0|1'), ''))
        self.assertFalse(dfa_accepts(regex_to_dfa('0|1'), '00'))

    def test_question(self):
        self.assertTrue(dfa_accepts(regex_to_dfa('0?'), '0'))
        self.assertTrue(dfa_accepts(regex_to_dfa('0?'), ''))
        self.assertFalse(dfa_accepts(regex_to_dfa('0?'), '00'))

    def test_plus(self):
        self.assertTrue(dfa_accepts(regex_to_dfa('0+'), '0'))
        self.assertTrue(dfa_accepts(regex_to_dfa('0+'), '00'))
        self.assertTrue(dfa_accepts(regex_to_dfa('0+'), '00000000000'))
        self.assertFalse(dfa_accepts(regex_to_dfa('0+'), ''))
        self.assertFalse(dfa_accepts(regex_to_dfa('0+'), '1'))

    def test_kleene_star(self):
        self.assertTrue(dfa_accepts(regex_to_dfa('1*'), ''))
        self.assertTrue(dfa_accepts(regex_to_dfa('1*'), '1'))
        self.assertTrue(dfa_accepts(regex_to_dfa('1*'), '11'))
        self.assertTrue(dfa_accepts(regex_to_dfa('1*'), '1111111'))
        self.assertFalse(dfa_accepts(regex_to_dfa('1*'), '1101111'))
        self.assertFalse(dfa_accepts(regex_to_dfa('1*'), '00000'))
        self.assertFalse(dfa_accepts(regex_to_dfa('1*'), '0'))

    def test_fixed_repetitions(self):
        self.assertFalse(dfa_accepts(regex_to_dfa('1{4}'), ''))
        self.assertFalse(dfa_accepts(regex_to_dfa('1{4}'), '1'))
        self.assertFalse(dfa_accepts(regex_to_dfa('1{4}'), '11'))
        self.assertFalse(dfa_accepts(regex_to_dfa('1{4}'), '111'))
        self.assertTrue(dfa_accepts(regex_to_dfa('1{4}'), '1111'))
        self.assertFalse(dfa_accepts(regex_to_dfa('1{4}'), '11111'))
        self.assertFalse(dfa_accepts(regex_to_dfa('1{4}'), '0000'))

    def test_fixed_bounds(self):
        self.assertFalse(dfa_accepts(regex_to_dfa('1{2,4}'), ''))
        self.assertFalse(dfa_accepts(regex_to_dfa('1{2,4}'), '1'))
        self.assertTrue(dfa_accepts(regex_to_dfa('1{2,4}'), '11'))
        self.assertTrue(dfa_accepts(regex_to_dfa('1{2,4}'), '111'))
        self.assertTrue(dfa_accepts(regex_to_dfa('1{2,4}'), '1111'))
        self.assertFalse(dfa_accepts(regex_to_dfa('1{2,4}'), '11111'))
        self.assertFalse(dfa_accepts(regex_to_dfa('1{2,4}'), '0000'))

    def test_branch(self):
        regex = '((01)|(100))'
        self.assertTrue(dfa_accepts(regex_to_dfa(regex), '01'))
        self.assertTrue(dfa_accepts(regex_to_dfa(regex), '100'))
        self.assertFalse(dfa_accepts(regex_to_dfa(regex), '1000'))
        self.assertFalse(dfa_accepts(regex_to_dfa(regex), '0100'))
        self.assertFalse(dfa_accepts(regex_to_dfa(regex), '11'))
        self.assertFalse(dfa_accepts(regex_to_dfa(regex), '10'))
        self.assertFalse(dfa_accepts(regex_to_dfa(regex), ''))

    def test_composition(self):
        regex = '0(1|(00))+1?'
        self.assertTrue(dfa_accepts(regex_to_dfa(regex), '01'))
        self.assertTrue(dfa_accepts(regex_to_dfa(regex), '011'))
        self.assertTrue(dfa_accepts(regex_to_dfa(regex), '0001'))
        self.assertTrue(dfa_accepts(regex_to_dfa(regex), '000'))
        self.assertTrue(dfa_accepts(regex_to_dfa(regex), '000000000'))

    def test_accept_none(self):
        self.assertTrue(dfa_accepts(regex_to_dfa(''), ''))
        self.assertFalse(dfa_accepts(regex_to_dfa(''), '0'))
        self.assertFalse(dfa_accepts(regex_to_dfa(''), '1'))
        self.assertFalse(dfa_accepts(regex_to_dfa(''), '011010101'))
        self.assertFalse(dfa_accepts(regex_to_dfa(''), '101010110'))

    def test_accept_all(self):
        self.assertTrue(dfa_accepts(regex_to_dfa('(0|1)*'), ''))
        self.assertTrue(dfa_accepts(regex_to_dfa('(0|1)*'), '0'))
        self.assertTrue(dfa_accepts(regex_to_dfa('(0|1)*'), '1'))
        self.assertTrue(dfa_accepts(regex_to_dfa('(0|1)*'), '111111111'))
        self.assertTrue(dfa_accepts(regex_to_dfa('(0|1)*'), '1100101011010'))
        self.assertTrue(dfa_accepts(regex_to_dfa('(0|1)*'), '0001110001111'))
        self.assertFalse(dfa_accepts(regex_to_dfa('(0|1)*'), '2'))
