"""
AI implementation using minimax algorithm with alpha-beta pruning.
"""

import random
from typing import Tuple
from .board import Board


class AI:
    """AI opponent for tic-tac-toe using minimax algorithm."""

    def __init__(self, difficulty: str = "medium"):
        """
        Initialize the AI with specified difficulty.

        Args:
            difficulty: AI difficulty level ("easy", "medium", "hard")
        """
        self.difficulty = difficulty
        self.MAX_PLAYER = Board.O_PLAYER  # AI always plays as O
        self.MIN_PLAYER = Board.X_PLAYER  # Human plays as X

    def get_move(self, board: Board) -> Tuple[int, int]:
        """
        Get the best move for the AI based on current board state.

        Args:
            board: Current game board

        Returns:
            Tuple of (row, col) for the best move
        """
        if self.difficulty == "easy":
            return self._get_easy_move(board)
        elif self.difficulty == "medium":
            return self._get_medium_move(board)
        else:  # hard
            return self._get_hard_move(board)

    def _get_easy_move(self, board: Board) -> Tuple[int, int]:
        """Get a move for easy difficulty (purely random)."""
        legal_moves = list(board.legal_moves())
        return random.choice(legal_moves)

    def _get_medium_move(self, board: Board) -> Tuple[int, int]:
        """Get a move for medium difficulty (minimax with limited depth)."""
        return self.__get_minimax_move(board, depth=3)

    def _get_hard_move(self, board: Board) -> Tuple[int, int]:
        """Get a move for hard difficulty (full minimax with alpha-beta pruning)."""
        return self.__get_minimax_move(board, depth=9)

    def __get_minimax_move(self, board: Board, depth: int) -> Tuple[int, int]:
        """
        Get the best move using minimax algorithm with specified depth.

        Args:
            board: Current game board
            depth: Search depth for minimax

        Returns:
            Tuple of (row, col) for the best move
        """
        legal_moves = list(board.legal_moves())
        best_move = legal_moves[0]
        best_score = float("-inf")

        for move in legal_moves:
            board.apply(move, self.MAX_PLAYER)
            score = self.minimax(board, depth, False, float("-inf"), float("inf"))
            board.undo(move)

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def minimax(self, board: Board, depth: int, is_max: bool, alpha: float, beta: float) -> float:
        """
        Minimax algorithm with alpha-beta pruning.

        Args:
            board: Current board state
            depth: Remaining search depth
            is_max: True if maximizing player (AI), False if minimizing (human)
            alpha: Alpha value for pruning
            beta: Beta value for pruning

        Returns:
            Score of the position
        """
        if board.terminal() or depth == 0:
            return board.evaluate()

        if is_max:
            best = float("-inf")
            for move in board.legal_moves():
                board.apply(move, self.MAX_PLAYER)
                val = self.minimax(board, depth - 1, False, alpha, beta)
                board.undo(move)
                best = max(best, val)
                alpha = max(alpha, best)
                if alpha >= beta:  # prune
                    break
            return best
        else:
            best = float("inf")
            for move in board.legal_moves():
                board.apply(move, self.MIN_PLAYER)
                val = self.minimax(board, depth - 1, True, alpha, beta)
                board.undo(move)
                best = min(best, val)
                beta = min(beta, best)
                if alpha >= beta:  # prune
                    break
            return best
