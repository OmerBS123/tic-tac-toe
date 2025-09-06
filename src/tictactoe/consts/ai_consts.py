"""
Constants for the AI class.
"""

from enum import Enum


class Difficulty(Enum):
    """AI difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Depth(Enum):
    """Search depths for different difficulties."""

    EASY = 0
    MEDIUM = 3
    HARD = 9


INFINITY = float("inf")
NEGATIVE_INFINITY = float("-inf")
