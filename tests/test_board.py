"""
Unit tests for the Board class.
"""

import numpy as np

from tictactoe.board import Board
from tictactoe.consts.board_consts import BOARD_SIZE, Player, Score


class TestBoard:
    """Test cases for the Board class."""

    def test_init(self) -> None:
        """Test board initialization."""
        board = Board()
        assert board.board.shape == (BOARD_SIZE, BOARD_SIZE)
        assert np.all(board.board == Player.EMPTY.value)
        assert board.move_history == []

    def test_reset(self) -> None:
        """Test board reset functionality."""
        board = Board()
        board.apply((0, 0), Player.X_PLAYER.value)
        board.reset()
        assert np.all(board.board == Player.EMPTY.value)
        assert board.move_history == []

    def test_apply_valid_move(self) -> None:
        """Test applying a valid move."""
        board = Board()
        result = board.apply((1, 1), Player.X_PLAYER.value)
        assert result is True
        assert board.board[1, 1] == Player.X_PLAYER.value
        assert board.move_history == [((1, 1), Player.X_PLAYER.value)]

    def test_apply_invalid_move_out_of_bounds(self) -> None:
        """Test applying move out of bounds."""
        board = Board()
        result = board.apply((3, 3), Player.X_PLAYER.value)
        assert result is False
        assert np.all(board.board == Player.EMPTY.value)

    def test_apply_invalid_move_occupied(self) -> None:
        """Test applying move to occupied cell."""
        board = Board()
        board.apply((0, 0), Player.X_PLAYER.value)
        result = board.apply((0, 0), Player.O_PLAYER.value)
        assert result is False
        assert board.board[0, 0] == Player.X_PLAYER.value

    def test_undo_valid_move(self) -> None:
        """Test undoing a valid move."""
        board = Board()
        board.apply((1, 1), Player.X_PLAYER.value)
        board.undo((1, 1))
        assert board.board[1, 1] == Player.EMPTY.value

    def test_undo_invalid_move(self) -> None:
        """Test undoing an invalid move."""
        board = Board()
        board.undo((3, 3))
        assert np.all(board.board == Player.EMPTY.value)

    def test_is_valid_move(self) -> None:
        """Test move validation."""
        board = Board()
        assert board.is_valid_move((0, 0)) is True
        assert board.is_valid_move((2, 2)) is True
        assert board.is_valid_move((3, 0)) is False
        assert board.is_valid_move((0, 3)) is False

        board.apply((1, 1), Player.X_PLAYER.value)
        assert board.is_valid_move((1, 1)) is False

    def test_legal_moves(self) -> None:
        """Test legal moves iterator."""
        board = Board()
        moves = list(board.legal_moves())
        assert len(moves) == 9
        assert (0, 0) in moves
        assert (2, 2) in moves

        board.apply((0, 0), Player.X_PLAYER.value)
        moves = list(board.legal_moves())
        assert len(moves) == 8
        assert (0, 0) not in moves

    def test_terminal_empty_board(self) -> None:
        """Test terminal check on empty board."""
        board = Board()
        assert board.terminal() is False

    def test_terminal_full_board(self) -> None:
        """Test terminal check on full board."""
        board = Board()
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                player = (
                    Player.X_PLAYER.value if (i + j) % 2 == 0 else Player.O_PLAYER.value
                )
                board.apply((i, j), player)
        assert board.terminal() is True

    def test_check_winner_row(self) -> None:
        """Test winner detection in rows."""
        board = Board()
        board.apply((0, 0), Player.X_PLAYER.value)
        board.apply((0, 1), Player.X_PLAYER.value)
        board.apply((0, 2), Player.X_PLAYER.value)
        assert board.check_winner() == Player.X_PLAYER.value

    def test_check_winner_column(self) -> None:
        """Test winner detection in columns."""
        board = Board()
        board.apply((0, 1), Player.O_PLAYER.value)
        board.apply((1, 1), Player.O_PLAYER.value)
        board.apply((2, 1), Player.O_PLAYER.value)
        assert board.check_winner() == Player.O_PLAYER.value

    def test_check_winner_diagonal_main(self) -> None:
        """Test winner detection in main diagonal."""
        board = Board()
        board.apply((0, 0), Player.X_PLAYER.value)
        board.apply((1, 1), Player.X_PLAYER.value)
        board.apply((2, 2), Player.X_PLAYER.value)
        assert board.check_winner() == Player.X_PLAYER.value

    def test_check_winner_diagonal_anti(self) -> None:
        """Test winner detection in anti-diagonal."""
        board = Board()
        board.apply((0, 2), Player.O_PLAYER.value)
        board.apply((1, 1), Player.O_PLAYER.value)
        board.apply((2, 0), Player.O_PLAYER.value)
        assert board.check_winner() == Player.O_PLAYER.value

    def test_check_winner_no_winner(self) -> None:
        """Test no winner detection."""
        board = Board()
        board.apply((0, 0), Player.X_PLAYER.value)
        board.apply((0, 1), Player.O_PLAYER.value)
        board.apply((1, 0), Player.O_PLAYER.value)
        assert board.check_winner() is None

    def test_is_board_full_empty(self) -> None:
        """Test board full check on empty board."""
        board = Board()
        assert board.is_board_full() is False

    def test_is_board_full_partial(self) -> None:
        """Test board full check on partially filled board."""
        board = Board()
        board.apply((0, 0), Player.X_PLAYER.value)
        assert board.is_board_full() is False

    def test_is_board_full_complete(self) -> None:
        """Test board full check on full board."""
        board = Board()
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                board.apply((i, j), Player.X_PLAYER.value)
        assert board.is_board_full() is True

    def test_evaluate_x_wins(self) -> None:
        """Test evaluation when X wins."""
        board = Board()
        board.apply((0, 0), Player.X_PLAYER.value)
        board.apply((0, 1), Player.X_PLAYER.value)
        board.apply((0, 2), Player.X_PLAYER.value)
        assert board.evaluate() == Score.LOSE.value

    def test_evaluate_o_wins(self) -> None:
        """Test evaluation when O wins."""
        board = Board()
        board.apply((0, 0), Player.O_PLAYER.value)
        board.apply((0, 1), Player.O_PLAYER.value)
        board.apply((0, 2), Player.O_PLAYER.value)
        assert board.evaluate() == Score.WIN.value

    def test_evaluate_draw(self) -> None:
        """Test evaluation when game is a draw."""
        board = Board()
        board.apply((0, 0), Player.X_PLAYER.value)
        board.apply((0, 1), Player.O_PLAYER.value)
        board.apply((0, 2), Player.X_PLAYER.value)
        board.apply((1, 0), Player.O_PLAYER.value)
        board.apply((1, 1), Player.X_PLAYER.value)
        board.apply((1, 2), Player.O_PLAYER.value)
        board.apply((2, 0), Player.O_PLAYER.value)
        board.apply((2, 1), Player.X_PLAYER.value)
        board.apply((2, 2), Player.O_PLAYER.value)
        assert board.evaluate() == Score.DRAW.value

    def test_evaluate_partial_game(self) -> None:
        """Test evaluation during ongoing game."""
        board = Board()
        board.apply((0, 0), Player.O_PLAYER.value)
        board.apply((0, 1), Player.O_PLAYER.value)
        score = board.evaluate()
        assert score > 0

    def test_get_board_copy(self) -> None:
        """Test board copy functionality."""
        board = Board()
        board.apply((1, 1), Player.X_PLAYER.value)
        copy = board.get_board_copy()
        assert np.array_equal(board.board, copy)
        assert copy is not board.board

    def test_str_representation(self) -> None:
        """Test string representation of board."""
        board = Board()
        board.apply((0, 0), Player.X_PLAYER.value)
        board.apply((1, 1), Player.O_PLAYER.value)
        result = str(board)
        assert "X" in result
        assert "O" in result
        assert "|" in result
