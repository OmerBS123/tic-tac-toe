"""
AI implementation using minimax algorithm with alpha-beta pruning.

Difficulty Levels:
- EASY: Purely random moves for beginners
- MEDIUM: Minimax with limited depth (3 levels) for intermediate players
- HARD: Full minimax with alpha-beta pruning for advanced players
"""

import random

from .board import Board
from .consts.ai_consts import INFINITY, NEGATIVE_INFINITY, Depth, Difficulty
from .consts.board_consts import Player


class AI:
    """AI opponent for tic-tac-toe using minimax algorithm."""

    def __init__(self, difficulty: Difficulty = Difficulty.MEDIUM) -> None:
        """
        Initialize the AI with specified difficulty.

        Args:
            difficulty: AI difficulty level
        """
        self.difficulty = difficulty
        self.MAX_PLAYER = Player.O_PLAYER.value
        self.MIN_PLAYER = Player.X_PLAYER.value

    def get_move(self, board: Board) -> tuple[int, int]:
        """
        Get the best move for the AI based on current board state.

        Args:
            board: Current game board

        Returns:
            Tuple of (row, col) for the best move
        """
        if self.difficulty == Difficulty.EASY:
            return self._get_easy_move(board)
        elif self.difficulty == Difficulty.MEDIUM:
            return self._get_medium_move(board)
        else:
            return self._get_hard_move(board)

    @staticmethod
    def _get_easy_move(board: Board) -> tuple[int, int]:
        """Get a move for easy difficulty (purely random)."""
        legal_moves = list(board.legal_moves())
        return random.choice(legal_moves)

    def _get_medium_move(self, board: Board) -> tuple[int, int]:
        """Get a move for medium difficulty (minimax with limited depth)."""
        return self._get_minimax_move(board, depth=Depth.MEDIUM.value)

    def _get_hard_move(self, board: Board) -> tuple[int, int]:
        """Get a move for hard difficulty (full minimax with alpha-beta pruning)."""
        return self._get_minimax_move(board, depth=Depth.HARD.value)

    def _get_minimax_move(self, board: Board, depth: int) -> tuple[int, int]:
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
        best_score = NEGATIVE_INFINITY

        for move in legal_moves:
            board.apply(move, self.MAX_PLAYER)
            score = self.minimax(board, depth, False, NEGATIVE_INFINITY, INFINITY)
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
            best = NEGATIVE_INFINITY
            for move in board.legal_moves():
                board.apply(move, self.MAX_PLAYER)
                val = self.minimax(board, depth - 1, False, alpha, beta)
                board.undo(move)
                best = max(best, val)
                alpha = max(alpha, best)
                if alpha >= beta:
                    break
            return best
        else:
            best = INFINITY
            for move in board.legal_moves():
                board.apply(move, self.MIN_PLAYER)
                val = self.minimax(board, depth - 1, True, alpha, beta)
                board.undo(move)
                best = min(best, val)
                beta = min(beta, best)
                if alpha >= beta:
                    break
            return best
