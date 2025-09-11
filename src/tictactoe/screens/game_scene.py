"""
Game scene for playing tic-tac-toe matches.
"""

import pygame

from ..app.scene import Scene
from ..consts.ai_consts import Difficulty
from ..consts.board_consts import Player
from ..consts.scene_consts import SceneTransition
from ..domain.ai import AI
from ..domain.board import Board
from ..infra.logger import get_logger
from ..ui.layout import compute_layout, make_fonts
from ..ui.widgets import GameUI

logger = get_logger()


class GameScene(Scene):
    """Scene for playing tic-tac-toe matches."""

    def __init__(self, width: int = 1000, height: int = 1000) -> None:
        """
        Initialize game scene.

        Args:
            width: Scene width
            height: Scene height
        """
        super().__init__(width, height)

        # Game state
        self.board = Board()
        self.current_player = Player.X_PLAYER
        self.game_mode = "pvp"  # "pvp" or "pvai"
        self.player_x_name = "Player X"
        self.player_o_name = "Player O"
        self.ai_difficulty = Difficulty.MEDIUM
        self.ai = None
        self.game_over = False
        self.winner = None

        # Initialize UI
        self.game_ui = None
        self._on_resize_impl(width, height)

        logger.info("GameScene initialized")

    def setup_game(self, mode: str, player_x_name: str, player_o_name: str = None, ai_difficulty: Difficulty = None) -> None:
        """
        Setup game parameters.

        Args:
            mode: Game mode ("pvp" or "pvai")
            player_x_name: Name of player X
            player_o_name: Name of player O (for PvP)
            ai_difficulty: AI difficulty (for PvAI)
        """
        self.game_mode = mode
        self.player_x_name = player_x_name

        match mode:
            case "pvp":
                self.player_o_name = player_o_name or "Player O"
                self.ai = None
            case "pvai":
                self.player_o_name = "AI"
                self.ai_difficulty = ai_difficulty or Difficulty.MEDIUM
                self.ai = AI(self.ai_difficulty)

        # Reset game state
        self.board = Board()
        self.current_player = Player.X_PLAYER
        self.game_over = False
        self.winner = None

        logger.info(f"Game setup: {mode}, X: {self.player_x_name}, O: {self.player_o_name}")

    def _on_resize_impl(self, width: int, height: int) -> None:
        """Handle resize implementation."""
        self.layout = compute_layout(width, height)
        self.fonts = make_fonts(self.layout)

        # Initialize game UI
        if self.game_ui is None:
            self.game_ui = GameUI(self.board, self.layout, self.fonts)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """
        Handle pygame events.

        Args:
            event: Pygame event

        Returns:
            String indicating scene transition or None if no action needed
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                logger.info("ESC pressed - returning to menu")
                return SceneTransition.MENU
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = event.pos
                if not self.game_over:
                    self._handle_board_click(mouse_x, mouse_y)
                elif self._is_back_button_clicked(mouse_x, mouse_y):
                    logger.info("Back button clicked - returning to menu")
                    return SceneTransition.MENU
        return None

    def _handle_board_click(self, mouse_x: int, mouse_y: int) -> None:
        """
        Handle click on the game board.

        Args:
            mouse_x: Mouse X position
            mouse_y: Mouse Y position
        """
        if self.game_ui is None:
            return

        # Get clicked cell
        cell = self.game_ui.get_cell_from_mouse(mouse_x, mouse_y)
        if cell is None:
            return

        row, col = cell

        # Check if cell is empty
        if self.board.get_cell(row, col) != Player.EMPTY.value:
            logger.debug(f"Cell ({row}, {col}) is already occupied")
            return

        # Make move
        self.board.make_move(row, col, self.current_player.value)
        logger.info(f"{self._get_player_name(self.current_player.value)} played at ({row}, {col})")

        # Check for game over
        if self.board.is_game_over():
            self._handle_game_over()
            return

        # Switch players
        self.current_player = Player.O_PLAYER if self.current_player == Player.X_PLAYER else Player.X_PLAYER

        # Handle AI move (if PvAI and it's AI's turn)
        if self.game_mode == "pvai" and self.current_player == Player.O_PLAYER and not self.game_over:
            self._make_ai_move()

    def _make_ai_move(self) -> None:
        """Make AI move."""
        if self.ai is None:
            return

        try:
            row, col = self.ai.get_move(self.board)
            self.board.make_move(row, col, self.current_player.value)
            logger.info(f"AI played at ({row}, {col})")

            # Check for game over
            if self.board.is_game_over():
                self._handle_game_over()
                return

            # Switch back to human player
            self.current_player = Player.X_PLAYER
        except Exception as e:
            logger.error(f"AI move failed: {e}")

    def _handle_game_over(self) -> None:
        """Handle game over state."""
        self.game_over = True

        if self.board.is_draw():
            self.winner = None
            logger.info("Game ended in a draw")
        else:
            # Get the winner
            winner_player = self.board.get_winner()
            if winner_player is not None:
                self.winner = self._get_player_name(winner_player)
                logger.info(f"Game won by: {self.winner}")
            else:
                self.winner = None
                logger.info("Game ended with no winner")

    def _get_player_name(self, player: int) -> str:
        """
        Get player name from player value.

        Args:
            player: Player value (int)

        Returns:
            Player name string
        """
        match player:
            case Player.X_PLAYER.value:
                return self.player_x_name
            case Player.O_PLAYER.value:
                return self.player_o_name
            case _:
                return "Unknown"

    def _is_back_button_clicked(self, mouse_x: int, mouse_y: int) -> bool:
        """
        Check if the back button was clicked.

        Args:
            mouse_x: Mouse X position
            mouse_y: Mouse Y position

        Returns:
            True if back button was clicked
        """
        if self.game_ui is None:
            return False
        return self.game_ui.is_back_button_clicked(mouse_x, mouse_y)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the game scene.

        Args:
            surface: Pygame surface to draw on
        """
        if self.game_ui is None:
            return

        # Draw game UI
        self.game_ui.render(surface)

        # Draw game over overlay if needed
        if self.game_over:
            self._draw_game_over_overlay(surface)

    def _draw_game_over_overlay(self, surface: pygame.Surface) -> None:
        """
        Draw game over overlay.

        Args:
            surface: Pygame surface to draw on
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # Game over message
        if self.winner:
            message = f"{self.winner} wins!"
            color = (100, 200, 255)  # Blue
        else:
            message = "It's a draw!"
            color = (200, 200, 200)  # Gray

        game_over_text = self.fonts["title"].render(message, True, color)
        game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        surface.blit(game_over_text, game_over_rect)

        # Instructions
        instructions = self.fonts["ui"].render("Click Back to return to menu", True, (255, 255, 255))
        instructions_rect = instructions.get_rect(center=(self.width // 2, self.height // 2 + 50))
        surface.blit(instructions, instructions_rect)
