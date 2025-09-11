"""
Main application orchestrator for tic-tac-toe game.
"""

import pygame

from tictactoe.app.scene_manager import SceneManager, MenuCallbacks
from tictactoe.infra.storage import Storage
from tictactoe.ui.layout import get_initial_window_size
from tictactoe.infra.logger import get_logger

logger = get_logger()


class TicTacToeApp:
    """Main application class with state machine."""

    def __init__(self, width: int = None, height: int = None) -> None:
        """
        Initialize the application.

        Args:
            width: Window width (defaults to computed size)
            height: Window height (defaults to computed size)
        """
        if width is None or height is None:
            width, height = get_initial_window_size()

        self.width = width
        self.height = height

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("Tic Tac Toe")

        # Initialize components
        self.storage = Storage()
        self.scene_manager = None

        # Create scene manager with callbacks
        self._create_scene_manager()

        logger.info("TicTacToeApp initialized")

    def _create_scene_manager(self) -> None:
        """Create the scene manager with callbacks."""
        callbacks = MenuCallbacks(
            play_pvp=self._start_pvp_game,
            play_vs_ai=self._start_pvai_game,
            show_leaderboard=self._show_leaderboard,
            show_history=self._show_history,
            reset_data=self._reset_data,
            quit_game=self._quit_game,
        )

        self.scene_manager = SceneManager(self.storage, self.width, self.height)
        self.scene_manager.set_callbacks(callbacks)
        logger.info("Scene manager created")

    def _start_pvp_game(self, player_x: str, player_o: str) -> None:
        """
        Start a PvP game.

        Args:
            player_x: Player X name
            player_o: Player O name
        """
        logger.info(f"Starting PvP game: {player_x} vs {player_o}")
        # TODO: Implement game logic
        # For now, just log the game start

    def _start_pvai_game(self, player_name: str, difficulty: str) -> None:
        """
        Start a PvAI game.

        Args:
            player_name: Human player name
            difficulty: AI difficulty level
        """
        logger.info(f"Starting PvAI game: {player_name} vs AI ({difficulty})")
        # TODO: Implement game logic
        # For now, just log the game start

    def _show_leaderboard(self) -> None:
        """Show leaderboard screen."""
        logger.info("Showing leaderboard")
        # Scene manager will handle the transition

    def _show_history(self) -> None:
        """Show match history screen."""
        logger.info("Showing match history")
        # Scene manager will handle the transition

    def _reset_data(self) -> None:
        """Show reset confirmation screen."""
        logger.info("Showing reset confirmation")
        # Scene manager will handle the transition

    def _quit_game(self) -> None:
        """Quit the application."""
        logger.info("Quitting game")
        # Don't call pygame.quit() here - let the main loop handle it

    def run(self) -> None:
        """Main application loop."""
        logger.info("Starting application loop")
        clock = pygame.time.Clock()
        running = True

        while running:
            events = pygame.event.get()

            # Handle events
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.VIDEORESIZE:
                    self._handle_resize(event.w, event.h)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self._toggle_fullscreen()

            if not running:
                break

            # Handle scene manager events
            for event in events:
                result = self.scene_manager.handle_event(event)
                if result == "quit":
                    running = False
                    break

            # Draw current scene
            self.scene_manager.draw(self.screen)

            pygame.display.flip()
            clock.tick(60)  # 60 FPS

        logger.info("Application loop ended")
        pygame.quit()

    def _handle_resize(self, width: int, height: int) -> None:
        """Handle window resize."""
        if (width, height) != (self.width, self.height):
            self.width = width
            self.height = height
            self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

            # Update scene manager
            if self.scene_manager:
                self.scene_manager.on_resize(width, height)

            logger.info(f"Window resized to {width}x{height}")

    def _toggle_fullscreen(self) -> None:
        """Toggle between fullscreen and windowed mode."""
        flags = self.screen.get_flags()
        is_fullscreen = bool(flags & pygame.FULLSCREEN)

        if is_fullscreen:
            # Exit fullscreen mode
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        else:
            # Enter fullscreen mode
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.width, self.height = self.screen.get_size()

        # Update scene manager
        if self.scene_manager:
            self.scene_manager.on_resize(self.width, self.height)

        logger.info(f"Toggled fullscreen: {not is_fullscreen}, size: {self.width}x{self.height}")


def main() -> None:
    """Main entry point."""
    app = TicTacToeApp()
    app.run()


if __name__ == "__main__":
    main()
