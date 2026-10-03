import unittest

from cnfc import *
from cnfc.funcs import Min, Max
from .util import SatTestCase


class TestSignedIntegers(unittest.TestCase, SatTestCase):
    def test_twos_complement_bits(self):
        f = Formula()
        sign, high, low = f.AddVars('sign high low')
        x = Integer(sign, high, low)
        f.Add(sign)
        f.Add(~high)
        f.Add(low)  # 101 represents -3.
        f.Add(x == -3)
        self.assertSat(f)

        f.Add(x == 5)
        self.assertUnsat(f)

    def test_tuple_view_of_integer_bits(self):
        f = Formula()
        bits = f.AddVars('x', 3)
        signed = Integer(bits)
        unsigned = Tuple(*bits)
        f.Add(unsigned == 7)
        f.Add(signed + 1 == 0)
        f.Add(unsigned + 1 == 8)
        self.assertSat(f)

        f.Add(signed == unsigned)
        self.assertUnsat(f)

    def test_signed_range(self):
        f = Formula()
        x = Integer(f.AddVars('x', 3))
        f.Add(x < -4)
        self.assertUnsat(f)

        f = Formula()
        x = Integer(f.AddVars('x', 3))
        f.Add(x >= 4)
        self.assertUnsat(f)

    def test_sign_extension(self):
        f = Formula()
        narrow = Integer(f.AddVars('narrow', 2))
        wide = Integer(f.AddVars('wide', 5))
        f.Add(narrow == -1)
        f.Add(wide == narrow)
        f.Add(wide == -1)
        self.assertSat(f)

        f.Add(wide == 3)
        self.assertUnsat(f)

    def test_tuple_compared_to_integer(self):
        f = Formula()
        x = Tuple(*f.AddVars('x', 3))
        f.Add(x == 7)
        f.Add(x > Integer(-1))
        f.Add(x >= Integer(7))
        f.Add(x != -1)
        self.assertSat(f)

        f.Add(x <= Integer(-1))
        self.assertUnsat(f)

    def test_negative_ordering(self):
        f = Formula()
        x = Integer(f.AddVars('x', 4))
        f.Add(x == -3)
        f.Add(x > -4)
        f.Add(x >= -3)
        f.Add(x < -2)
        f.Add(x <= -3)
        self.assertSat(f)

        f.Add(x != -3)
        self.assertUnsat(f)

    def test_chained_signed_comparison(self):
        f = Formula()
        x = Integer(f.AddVars('x', 3))
        f.Add(-3 <= x < -1)
        f.Add(x == -2)
        self.assertSat(f)

        f.Add(x == 0)
        self.assertUnsat(f)

    def test_negated_signed_comparisons(self):
        f = Formula()
        x = Integer(f.AddVars('x', 3))
        f.Add(x == -2)
        f.Add(Not(x < -3))
        f.Add(Not(x >= 0))
        f.Add(Not(x == 2))
        f.Add(Not(x != -2))
        self.assertSat(f)

        f.Add(Not(x <= -2))
        self.assertUnsat(f)

    def test_addition_grows_past_signed_range(self):
        f = Formula()
        x = Integer(f.AddVars('x', 3))
        f.Add(x == 3)
        f.Add(x + x == 6)
        self.assertSat(f)

        f.Add(x + x == -2)
        self.assertUnsat(f)

    def test_negative_addition(self):
        f = Formula()
        x = Integer(f.AddVars('x', 3))
        f.Add(x == -4)
        f.Add(x + x == -8)
        f.Add(x + 7 == 3)
        f.Add(7 + x == 3)
        f.Add(sum([x, x, Integer(10)]) == 2)
        self.assertSat(f)

        f.Add(x + x == 0)
        self.assertUnsat(f)

    def test_signed_subtraction(self):
        f = Formula()
        x = Integer(f.AddVars('x', 3))
        f.Add(x == 3)
        f.Add(x - 7 == -4)
        f.Add(-2 - x == -5)
        f.Add(Integer(-4) - x == -7)
        self.assertSat(f)

        f.Add(x - 7 == 4)
        self.assertUnsat(f)

    def test_subtraction_can_produce_negative_results(self):
        f = Formula()
        f.Add(Integer(1) - Integer(2) == -1)
        self.assertSat(f)

        f.Add(Integer(1) - Integer(2) == 1)
        self.assertUnsat(f)

    def test_negating_smallest_signed_value(self):
        f = Formula()
        x = Integer(f.AddVars('x', 3))
        f.Add(x == -4)
        f.Add(-x == 4)
        f.Add(-(-x) == x)
        f.Add(-Integer(7) == -7)
        self.assertSat(f)

        f.Add(-x == -4)
        self.assertUnsat(f)

    def test_signed_multiplication(self):
        f = Formula()
        x = Integer(f.AddVars('x', 3))
        y = Integer(f.AddVars('y', 3))
        f.Add(x == -4)
        f.Add(y == -3)
        f.Add(x * y == 12)
        f.Add(x * 7 == -28)
        f.Add(7 * x == -28)
        f.Add(x * 0 == 0)
        self.assertSat(f)

        f.Add(x * y == -12)
        self.assertUnsat(f)

    def test_one_bit_signed_multiplication(self):
        f = Formula()
        x = Integer(f.AddVars('x', 1))
        f.Add(x == -1)
        f.Add(x * x == 1)
        self.assertSat(f)

        f.Add(x * x == -1)
        self.assertUnsat(f)

    def test_negative_dividend(self):
        f = Formula()
        x = Integer(f.AddVars('x', 4))
        f.Add(x == -7)
        f.Add(x // 3 == -3)
        f.Add(x % 3 == 2)
        self.assertSat(f)

        f.Add(x // 3 == -2)
        self.assertUnsat(f)

    def test_negative_divisor(self):
        f = Formula()
        divisor = Integer(f.AddVars('divisor', 3))
        f.Add(divisor == -3)
        f.Add(7 // divisor == -3)
        f.Add(7 % divisor == -2)
        self.assertSat(f)

        f.Add(7 % divisor == 1)
        self.assertUnsat(f)

    def test_both_division_operands_negative(self):
        f = Formula()
        x = Integer(f.AddVars('x', 4))
        f.Add(x == -7)
        f.Add(x // -3 == 2)
        f.Add(x % -3 == -1)
        self.assertSat(f)

        f.Add(x // -3 == 3)
        self.assertUnsat(f)

    def test_exact_signed_division(self):
        f = Formula()
        f.Add(Integer(-6) // 3 == -2)
        f.Add(Integer(-6) % 3 == 0)
        f.Add(Integer(6) // -3 == -2)
        f.Add(Integer(6) % -3 == 0)
        self.assertSat(f)

    def test_division_grows_for_smallest_signed_value(self):
        f = Formula()
        x = Integer(f.AddVars('x', 3))
        f.Add(x == -4)
        f.Add(x // -1 == 4)
        f.Add(x % -1 == 0)
        self.assertSat(f)

        f.Add(x // -1 == -4)
        self.assertUnsat(f)

    def test_signed_division_and_modulo_by_zero(self):
        f = Formula()
        f.Add(Integer(-1) // 0 == 0)
        self.assertUnsat(f)

        f = Formula()
        f.Add(Integer(-1) % 0 == 0)
        self.assertUnsat(f)

    def test_signed_powers(self):
        f = Formula()
        x = Integer(f.AddVars('x', 3))
        f.Add(x == -2)
        f.Add(x ** 0 == 1)
        f.Add(x ** 2 == 4)
        f.Add(x ** 3 == -8)
        self.assertSat(f)

        f.Add(x ** 3 == 8)
        self.assertUnsat(f)

    def test_signed_modular_powers(self):
        f = Formula()
        f.Add(Integer(-2) ** 3 % 5 == 2)
        f.Add(pow(Integer(-2), 3, -5) == -3)
        f.Add(pow(Integer(2), 3, -5) == -2)
        self.assertSat(f)

        f.Add(Integer(-2) ** 3 % 5 == -3)
        self.assertUnsat(f)

    def test_signed_exponent_must_be_nonnegative(self):
        f = Formula()
        exponent = Integer(f.AddVars('exponent', 3))
        f.Add(exponent == 2)
        f.Add(Integer(-2) ** exponent == 4)
        self.assertSat(f)

        f = Formula()
        exponent = Integer(f.AddVars('exponent', 3))
        f.Add(exponent == -1)
        f.Add(Integer(-2) ** exponent == 1)
        self.assertUnsat(f)

    def test_signed_power_used_in_division(self):
        f = Formula()
        f.Add((Integer(-2) ** 3) // 2 == -4)
        f.Add((Integer(-2) ** 3) % 3 == 1)
        self.assertSat(f)

    def test_signed_zero_exponent(self):
        f = Formula()
        zero = Integer(0)
        f.Add(Integer(-2) ** zero == 1)
        f.Add(pow(Integer(-2), zero, Integer(1)) == 0)
        f.Add(pow(Integer(-2), zero, Integer(-1)) == 0)
        self.assertSat(f)

        f.Add(Integer(-2) ** zero == -1)
        self.assertUnsat(f)

    def test_signed_conditional(self):
        f = Formula()
        choose_negative = f.AddVar()
        result = If(choose_negative, Integer(-1), Integer(7))
        f.Add(choose_negative)
        f.Add(result == -1)
        self.assertSat(f)

        f.Add(result == 7)
        self.assertUnsat(f)

        f = Formula()
        choose_negative = f.AddVar()
        result = If(choose_negative, Integer(-1), Integer(7))
        f.Add(~choose_negative)
        f.Add(result == 7)
        self.assertSat(f)

        f.Add(result == -1)
        self.assertUnsat(f)

    def test_signed_min_and_max(self):
        f = Formula()
        x = Integer(f.AddVars('x', 3))
        f.Add(x == -2)
        f.Add(Min(Integer(-4), x, Integer(7)) == -4)
        f.Add(Max(Integer(-4), x, Integer(7)) == 7)
        f.Add(Max(Integer(-4), x) == -2)
        self.assertSat(f)

        f.Add(Min(x, Integer(7)) == 7)
        self.assertUnsat(f)

    def test_counts_compared_to_negative_bounds(self):
        f = Formula()
        a, b = f.AddVars('a b')
        f.Add(NumTrue(a, b) >= -1)
        f.Add(NumFalse(a, b) != Integer(-1))
        f.Add(NumTrue(a, b) > Integer(-2))
        self.assertSat(f)

        f.Add(NumFalse(a, b) == Integer(-1))
        self.assertUnsat(f)

    def test_empty_counts_in_arithmetic(self):
        f = Formula()
        f.Add(NumTrue() + Integer(1) == 1)
        f.Add(NumFalse() + Integer(1) == 1)
        self.assertSat(f)

    def test_empty_counts_compared_to_negative_bounds(self):
        f = Formula()
        f.Add(NumTrue() > -1)
        f.Add(NumFalse() >= Integer(-1))
        self.assertSat(f)

        f.Add(NumTrue() == -1)
        self.assertUnsat(f)

    def test_signed_solution_decoding(self):
        f = Formula()
        x = Integer(f.AddVars('x', 4))
        f.Add(x == -3)
        sol = f.Solve()
        self.assertIsNotNone(sol)
        self.assertEqual(sol.integer('x', 4), -3)
        self.assertEqual(sol.integer('x:0', 'x:1', 'x:2', 'x:3'), -3)
        self.assertEqual(sol.integer('x'), -3)

    def test_positive_signed_constant(self):
        f = Formula()
        f.Add(Integer(7) == 7)
        f.Add(Integer(7) > -1)
        f.Add(Integer(0) == 0)
        self.assertSat(f)

    def test_empty_integer_is_zero(self):
        f = Formula()
        f.Add(Integer() == 0)
        self.assertSat(f)

    def test_bits_needed_for_range(self):
        self.assertEqual(Integer.bits_needed_for_range(-10, 10), 5)
        self.assertEqual(Integer.bits_needed_for_range(-8, 7), 4)
        self.assertEqual(Integer.bits_needed_for_range(0, 8), 5)
        self.assertEqual(Integer.bits_needed_for_range(-9, -1), 5)
        self.assertEqual(Integer.bits_needed_for_range(0, 0), 1)
        self.assertEqual(Integer.bits_needed_for_range(-1, -1), 1)

    def test_range_helper_with_variables_and_constraints(self):
        f = Formula()
        bits = Integer.bits_needed_for_range(-10, 10)
        x = Integer(f.AddVars('x', bits))
        f.Add(-10 <= x <= 10)
        f.PushCheckpoint()
        f.Add(x == -10)
        self.assertSat(f)
        f.PopCheckpoint()

        f.Add(x == 10)
        self.assertSat(f)

    def test_range_helper_only_calculates_capacity(self):
        f = Formula()
        x = Integer(f.AddVars('x', Integer.bits_needed_for_range(-10, 10)))
        f.Add(x == 15)
        self.assertSat(f)

        f.Add(-10 <= x <= 10)
        self.assertUnsat(f)

    def test_reversed_range_is_rejected(self):
        with self.assertRaises(ValueError):
            Integer.bits_needed_for_range(5, -3)

    def test_non_integer_range_is_rejected(self):
        with self.assertRaises(TypeError):
            Integer.bits_needed_for_range(-1.5, 3)
