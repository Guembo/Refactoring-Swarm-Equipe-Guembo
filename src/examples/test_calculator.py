"""
Test suite for calculator module.
Tests basic arithmetic operations and edge cases.
"""

import pytest
from calculator import add, divide, calculate_average, Calculator


def test_add() -> None:
    """
    Tests that the `add` function correctly sums positive, negative, and zero integers.

    Asserts:
        - Correctly sums two positive integers (e.g., 2 + 3 = 5).
        - Correctly sums a negative and a positive integer resulting in zero (e.g., -1 + 1 = 0).
        - Correctly sums two zeros (e.g., 0 + 0 = 0).
    """
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0


def test_divide() -> None:
    """
    Tests that the `divide` function correctly performs division and raises
    ZeroDivisionError for division by zero.

    Asserts:
        - Correctly divides two positive integers (e.g., 10 / 2 = 5.0).
        - Correctly divides two positive integers (e.g., 9 / 3 = 3.0).
        - Raises ZeroDivisionError when the denominator is zero.
    """
    assert divide(10, 2) == 5.0
    assert divide(9, 3) == 3.0

    # Test division by zero
    with pytest.raises(ZeroDivisionError):
        divide(5, 0)


def test_calculate_average() -> None:
    """
    Tests that the `calculate_average` function correctly computes the average
    of a list of numbers and raises ZeroDivisionError for an empty list.

    Asserts:
        - Correctly computes the average of a list of positive integers (e.g., [1, 2, 3, 4, 5] -> 3.0).
        - Correctly computes the average of a list of positive integers (e.g., [10, 20] -> 15.0).
        - Raises ZeroDivisionError when the input list is empty.
    """
    assert calculate_average([1, 2, 3, 4, 5]) == 3.0
    assert calculate_average([10, 20]) == 15.0

    # Test with an empty list
    with pytest.raises(ZeroDivisionError):
        calculate_average([])


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (3, 4, 12),  # Product of two positive integers
        (-2, 5, -10),  # Product of a negative and a positive integer
        (0, 100, 0),  # Product of zero and a positive integer
        (2.5, 3.0, 7.5),  # Product of two floats
        (1000000, 2000000, 2000000000000),  # Product of two large integers
    ],
)
def test_calculator_multiply(a: float, b: float, expected: float) -> None:
    """
    Tests the `Calculator.multiply` method for various integer and float inputs
    using parameterized tests.

    Args:
        a: The first number for multiplication.
        b: The second number for multiplication.
        expected: The expected result of the multiplication.
    """
    calc = Calculator()
    assert calc.multiply(a, b) == expected


@pytest.mark.parametrize(
    "base, exponent, expected",
    [
        (2, 3, 8),  # Positive base, positive exponent
        (5, 2, 25),  # Positive base, positive exponent
        (10, 0, 1),  # Any base, zero exponent
        (2, -2, 0.25),  # Positive base, negative exponent
        (9, 0.5, 3.0),  # Positive base, fractional exponent
        (0, 0, 1),  # Zero base, zero exponent
        (-2, 3, -8),  # Negative base, odd integer exponent
        (-2, 2, 4),  # Negative base, even integer exponent
    ],
)
def test_calculator_power_valid(base: float, exponent: float, expected: float) -> None:
    """
    Tests the `Calculator.power` method for valid integer and float inputs
    using parameterized tests.

    Args:
        base: The base number.
        exponent: The exponent.
        expected: The expected result of the power calculation.
    """
    calc = Calculator()
    assert calc.power(base, exponent) == expected


def test_calculator_power_edge_cases() -> None:
    """
    Tests edge cases for the `Calculator.power` method, including expected exceptions.

    Asserts:
        - Raises ZeroDivisionError for zero base and negative exponent.
        - Raises ValueError for negative base and fractional exponent when the result is not a real number.
    """
    calc = Calculator()

    # Test zero base with negative exponent
    with pytest.raises(ZeroDivisionError):
        calc.power(0, -2)

    # Test negative base with fractional exponent (result is not a real number)
    with pytest.raises(ValueError):
        calc.power(-4, 0.5)
        
