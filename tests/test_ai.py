"""
Unit tests for the AI class.
"""

from unittest.mock import patch

from tictactoe.ai import AI
from tictactoe.board import Board
from tictactoe.consts.ai_consts import INFINITY, NEGATIVE_INFINITY, Depth, Difficulty
from tictactoe.consts.board_consts import Player


class TestAI:
    """Test cases for the AI class."""

    def test_init_default_difficulty(self) -> None:
        """Test AI initialization with default difficulty."""
        ai = AI()
        assert ai.difficulty == Difficulty.MEDIUM
        assert ai.MAX_PLAYER == Player.O_PLAYER.value
        assert ai.MIN_PLAYER == Player.X_PLAYER.value

    def test_init_custom_difficulty(self) -> None:
        """Test AI initialization with custom difficulty."""
        ai = AI(Difficulty.HARD)
        assert ai.difficulty == Difficulty.HARD

    def test_get_move_easy(self) -> None:
        """Test get_move for easy difficulty."""
        ai = AI(Difficulty.EASY)
        board = Board()
        board.apply((0, 0), Player.X_PLAYER.value)

        with patch("random.choice") as mock_choice:
            mock_choice.return_value = (1, 1)
            move = ai.get_move(board)
            assert move == (1, 1)
            mock_choice.assert_called_once()

    def test_get_move_medium(self) -> None:
        """Test get_move for medium difficulty."""
        ai = AI(Difficulty.MEDIUM)
        board = Board()

        with patch.object(ai, "_get_minimax_move") as mock_minimax:
            mock_minimax.return_value = (1, 1)
            move = ai.get_move(board)
            assert move == (1, 1)
            mock_minimax.assert_called_once_with(board, depth=Depth.MEDIUM.value)

    def test_get_move_hard(self) -> None:
        """Test get_move for hard difficulty."""
        ai = AI(Difficulty.HARD)
        board = Board()

        with patch.object(ai, "_get_minimax_move") as mock_minimax:
            mock_minimax.return_value = (2, 2)
            move = ai.get_move(board)
            assert move == (2, 2)
            mock_minimax.assert_called_once_with(board, depth=Depth.HARD.value)

    def test_get_easy_move(self) -> None:
        """Test _get_easy_move method."""
        board = Board()
        board.apply((0, 0), Player.X_PLAYER.value)

        with patch("random.choice") as mock_choice:
            mock_choice.return_value = (1, 1)
            move = AI._get_easy_move(board)
            assert move == (1, 1)
            mock_choice.assert_called_once()

    def test_get_minimax_move(self) -> None:
        """Test __get_minimax_move method."""
        ai = AI()
        board = Board()

        with patch.object(ai, "minimax") as mock_minimax:
            mock_minimax.return_value = 5
            move = ai._get_minimax_move(board, depth=3)
            assert move == (0, 0)
            mock_minimax.assert_called()

    def test_minimax_terminal_state(self) -> None:
        """Test minimax with terminal board state."""
        ai = AI()
        board = Board()
        board.apply((0, 0), Player.O_PLAYER.value)
        board.apply((0, 1), Player.O_PLAYER.value)
        board.apply((0, 2), Player.O_PLAYER.value)

        score = ai.minimax(
            board, depth=5, is_max=True, alpha=NEGATIVE_INFINITY, beta=INFINITY
        )
        assert score == 10

    def test_minimax_depth_zero(self) -> None:
        """Test minimax with depth zero."""
        ai = AI()
        board = Board()

        with patch.object(board, "evaluate") as mock_evaluate:
            mock_evaluate.return_value = 3
            score = ai.minimax(
                board, depth=0, is_max=True, alpha=NEGATIVE_INFINITY, beta=INFINITY
            )
            assert score == 3
            mock_evaluate.assert_called_once()

    def test_minimax_maximizing_player(self) -> None:
        """Test minimax for maximizing player."""
        ai = AI()
        board = Board()

        with patch.object(board, "legal_moves") as mock_moves:
            mock_moves.return_value = [(0, 0), (1, 1)]

            with patch.object(board, "apply") as mock_apply:
                with patch.object(board, "undo") as mock_undo:
                    with patch.object(board, "evaluate") as mock_evaluate:
                        mock_evaluate.return_value = 5

                        score = ai.minimax(
                            board,
                            depth=1,
                            is_max=True,
                            alpha=NEGATIVE_INFINITY,
                            beta=INFINITY,
                        )

                        assert score == 5
                        mock_apply.assert_called()
                        mock_undo.assert_called()

    def test_minimax_minimizing_player(self) -> None:
        """Test minimax for minimizing player."""
        ai = AI()
        board = Board()

        with patch.object(board, "legal_moves") as mock_moves:
            mock_moves.return_value = [(0, 0), (1, 1)]

            with patch.object(board, "apply") as mock_apply:
                with patch.object(board, "undo") as mock_undo:
                    with patch.object(board, "evaluate") as mock_evaluate:
                        mock_evaluate.return_value = -3

                        score = ai.minimax(
                            board,
                            depth=1,
                            is_max=False,
                            alpha=NEGATIVE_INFINITY,
                            beta=INFINITY,
                        )

                        assert score == -3
                        mock_apply.assert_called()
                        mock_undo.assert_called()

    def test_minimax_alpha_beta_pruning(self) -> None:
        """Test alpha-beta pruning in minimax."""
        ai = AI()
        board = Board()

        with patch.object(board, "legal_moves") as mock_moves:
            mock_moves.return_value = [(0, 0), (1, 1)]

            with patch.object(board, "apply"):
                with patch.object(board, "undo"):
                    with patch.object(ai, "minimax") as mock_minimax:
                        mock_minimax.side_effect = [10, 5]

                        score = ai.minimax(
                            board, depth=2, is_max=True, alpha=10, beta=INFINITY
                        )

                        assert score == 10
                        assert mock_minimax.call_count == 1

    def test_minimax_real_game_scenario(self) -> None:
        """Test minimax with a real game scenario."""
        ai = AI(Difficulty.HARD)
        board = Board()

        board.apply((0, 0), Player.X_PLAYER.value)
        board.apply((1, 1), Player.O_PLAYER.value)

        move = ai.get_move(board)
        assert isinstance(move, tuple)
        assert len(move) == 2
        assert 0 <= move[0] < 3
        assert 0 <= move[1] < 3

    def test_minimax_winning_move(self) -> None:
        """Test that AI finds winning move."""
        ai = AI(Difficulty.HARD)
        board = Board()

        board.apply((0, 0), Player.O_PLAYER.value)
        board.apply((0, 1), Player.O_PLAYER.value)
        board.apply((1, 0), Player.X_PLAYER.value)
        board.apply((1, 1), Player.X_PLAYER.value)

        move = ai.get_move(board)
        assert move == (0, 2)

    def test_minimax_blocking_move(self) -> None:
        """Test that AI blocks opponent's winning move."""
        ai = AI(Difficulty.HARD)
        board = Board()

        board.apply((0, 0), Player.X_PLAYER.value)
        board.apply((0, 1), Player.X_PLAYER.value)
        board.apply((1, 0), Player.O_PLAYER.value)

        move = ai.get_move(board)
        assert move == (0, 2)

    def test_difficulty_comparison(self) -> None:
        """Test difficulty level comparisons."""
        easy_ai = AI(Difficulty.EASY)
        medium_ai = AI(Difficulty.MEDIUM)
        hard_ai = AI(Difficulty.HARD)

        assert easy_ai.difficulty == Difficulty.EASY
        assert medium_ai.difficulty == Difficulty.MEDIUM
        assert hard_ai.difficulty == Difficulty.HARD
