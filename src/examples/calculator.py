"""
Sample buggy calculator module for testing the Refactoring Swarm.
This file intentionally contains bugs, style issues, and missing type hints.
"""

from typing import List, Union

def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Adds two numbers.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of a and b.
    """
    return a + b

def divide(a: Union[int, float], b: Union[int, float]) -> float:
    """Divides two numbers.

    Args:
        a: The numerator.
        b: The denominator.

    Returns:
        The result of a / b.

    Raises:
        ValueError: If the denominator is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

def calculate_average(numbers: List[Union[int, float]]) -> float:
    """Calculates the average of a list of numbers.

    Args:
        numbers: A list of numbers.

    Returns:
        The average of the numbers.

    Raises:
        ValueError: If the input list is empty.
    """
    if not numbers:
        raise ValueError("Cannot calculate average of an empty list.")
    return sum(numbers) / len(numbers)

class Calculator:
    """A simple calculator class."""

    def __init__(self) -> None:
        """Initializes the Calculator with a default value of 0."""
        self.value: Union[int, float] = 0
    
    def multiply(self, x: Union[int, float], y: Union[int, float]) -> Union[int, float]:
        """Multiplies two numbers.

        Args:
            x: The first number.
            y: The second number.

        Returns:
            The product of x and y.
        """
        return x * y
    
    def power(self, base: Union[int, float], exponent: int) -> Union[int, float]:
        """Calculates base raised to the power of exponent.

        Args:
            base: The base number.
            exponent: The exponent (must be a non-negative integer).

        Returns:
            The result of base^exponent.

        Raises:
            ValueError: If the exponent is negative.
        """
        if exponent < 0:
            raise ValueError("Exponent must be a non-negative integer.")
        result: Union[int, float] = 1
        for _ in range(exponent):
            result *= base
        return result