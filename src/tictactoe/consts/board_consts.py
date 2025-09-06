"""
Constants for the Board class.
"""

from enum import Enum

BOARD_SIZE = 3


class Player(Enum):
    """Player constants."""

    EMPTY = 0
    X_PLAYER = 1
    O_PLAYER = 2


class Score(Enum):
    """Evaluation scores."""

    WIN = 10
    LOSE = -10
    DRAW = 0
