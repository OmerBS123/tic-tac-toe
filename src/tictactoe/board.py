"""
Board class for tic-tac-toe game with all game logic methods.
"""

import numpy as np
from typing import Iterator, Tuple, Optional


class Board:
    """Represents a 3x3 tic-tac-toe board."""

    EMPTY = 0
    X_PLAYER = 1
    O_PLAYER = 2

    def __init__(self):
        """Initialize an empty 3x3 board."""
        self.board = np.zeros((3, 3), dtype=int)
        self.move_history = []  # Track moves for undo functionality

    def reset(self):
        """Reset the board to initial empty state."""
        self.board = np.zeros((3, 3), dtype=int)
        self.move_history = []

    def apply(self, move: Tuple[int, int], player: int) -> bool:
        """
        Apply a move to the board.

        Args:
            move: Tuple of (row, col) coordinates
            player: Player making the move (X_PLAYER or O_PLAYER)

        Returns:
            True if move was valid and applied, False otherwise
        """
        row, col = move
        if not self.is_valid_move(move):
            return False

        self.board[row, col] = player
        self.move_history.append((move, player))
        return True

    def undo(self, move: Tuple[int, int]):
        """
        Undo a move on the board.

        Args:
            move: Tuple of (row, col) coordinates to undo
        """
        row, col = move
        if not self.is_valid_move(move):
            return

        self.board[row, col] = self.EMPTY
        # Remove from history if it exists
        if self.move_history and self.move_history[-1][0] == move:
            self.move_history.pop()

    def is_valid_move(self, move: Tuple[int, int]) -> bool:
        """
        Check if a move is valid.

        Args:
            move: Tuple of (row, col) coordinates

        Returns:
            True if move is valid, False otherwise
        """
        row, col = move
        if not (0 <= row < 3 and 0 <= col < 3):
            return False

        return self.board[row, col] == self.EMPTY

    def legal_moves(self) -> Iterator[Tuple[int, int]]:
        """
        Return an iterator of all legal moves.

        Returns:
            Iterator of (row, col) tuples for all empty positions
        """
        for row in range(3):
            for col in range(3):
                if self.board[row, col] == self.EMPTY:
                    yield (row, col)

    def terminal(self) -> bool:
        """
        Check if the game is in a terminal state.

        Returns:
            True if game is over (win or draw), False otherwise
        """
        return self.check_winner() is not None or self.is_board_full()

    def check_winner(self) -> Optional[int]:
        """
        Check if there's a winner on the board.

        Returns:
            X_PLAYER, O_PLAYER if there's a winner, None otherwise
        """
        # Check rows
        for row in range(3):
            if self._check_line([(row, 0), (row, 1), (row, 2)]):
                return self.board[row, 0]

        # Check columns
        for col in range(3):
            if self._check_line([(0, col), (1, col), (2, col)]):
                return self.board[0, col]

        # Check diagonals
        if self._check_line([(0, 0), (1, 1), (2, 2)]):
            return self.board[0, 0]

        if self._check_line([(0, 2), (1, 1), (2, 0)]):
            return self.board[0, 2]

        return None

    def _check_line(self, positions: list) -> bool:
        """
        Check if all positions in a line have the same non-empty value.

        Args:
            positions: List of (row, col) tuples forming a line

        Returns:
            True if all positions have the same non-empty value
        """
        if len(positions) != 3:
            return False

        values = [self.board[row, col] for row, col in positions]
        return values[0] != self.EMPTY and values[0] == values[1] == values[2]

    def is_board_full(self) -> bool:
        """
        Check if the board is full.

        Returns:
            True if board is full, False otherwise
        """
        return np.all(self.board != self.EMPTY)

    def evaluate(self) -> int:
        """
        Evaluate the current board position.

        Returns:
            Positive score for O_PLAYER advantage, negative for X_PLAYER advantage, 0 for draw
        """
        winner = self.check_winner()

        match winner:
            case self.O_PLAYER:
                return 10
            case self.X_PLAYER:
                return -10
            case None:
                if self.is_board_full():
                    return 0

        # Evaluate based on potential winning lines
        score = 0

        # Check all possible lines (rows, columns, diagonals)
        lines = [
            # Rows
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            # Columns
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            # Diagonals
            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (1, 1), (2, 0)],
        ]

        for line in lines:
            line_score = self._evaluate_line(line)
            score += line_score

        return score

    def _evaluate_line(self, line: list) -> int:
        """
        Evaluate a specific line on the board.

        Args:
            line: List of (row, col) positions forming a line

        Returns:
            Score for this line
        """
        o_count = 0
        x_count = 0

        for row, col in line:
            if self.board[row, col] == self.O_PLAYER:
                o_count += 1
            elif self.board[row, col] == self.X_PLAYER:
                x_count += 1

        # If both players have pieces in this line, it's not useful
        if o_count > 0 and x_count > 0:
            return 0

        # Score based on how many pieces are in the line
        if o_count > 0:
            return o_count * o_count  # Exponential scoring
        elif x_count > 0:
            return -x_count * x_count

        return 0

    def get_board_copy(self) -> np.ndarray:
        """
        Get a deep copy of the current board state.

        Returns:
            Deep copy of the board
        """
        return self.board.copy()

    def __str__(self) -> str:
        """String representation of the board for debugging."""
        symbols = {self.EMPTY: " ", self.X_PLAYER: "X", self.O_PLAYER: "O"}
        lines = []
        for row in self.board:
            lines.append(" | ".join(symbols[cell] for cell in row))
        return "\n".join(lines)
