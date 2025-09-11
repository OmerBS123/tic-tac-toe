"""
Test script for the menu.py implementation with real scene functionality.

This script demonstrates the menu system with actual leaderboard and history scenes,
while keeping dummy callbacks for game logic to avoid side effects.
"""

import pygame

from src.tictactoe.menu import MenuCallbacks, create_main_menu, SceneManager
from src.tictactoe.infra.storage import Storage
from src.tictactoe.screens.leaderboard_scene import LeaderboardScene
from src.tictactoe.screens.history_scene import MatchHistoryScene
from src.tictactoe.screens.reset_scene import ResetScene


def add_sample_data(storage: Storage) -> None:
    """Add some sample data for testing."""
    # Add sample matches
    storage.record_match("Alice", "Bob", "X", "pvp")
    storage.record_match("Alice", "Bob", "O", "pvp")
    storage.record_match("Charlie", "AI", "X", "pvai", "easy")
    storage.record_match("Charlie", "AI", "Draw", "pvai", "medium")
    storage.record_match("Alice", "AI", "X", "pvai", "hard")
    storage.record_match("Bob", "Charlie", "O", "pvp")
    storage.record_match("Alice", "Charlie", "X", "pvp")
    storage.record_match("Bob", "AI", "O", "pvai", "easy")
    print("Sample data added!")


class MenuTestApp:
    """Test application that can show menu, leaderboard, and history scenes."""

    def __init__(self):
        pygame.init()

        # Use dynamic window sizing
        from src.tictactoe.layout import get_initial_window_size

        width, height = get_initial_window_size()

        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("Tic Tac Toe - Menu Test")

        # Initialize storage and scene manager
        self.storage = Storage()
        add_sample_data(self.storage)

        # Current scene state
        self.current_scene = "menu"
        self.scene_manager = None

        # Create scene manager with callbacks
        self._create_scene_manager()

    def _create_scene_manager(self):
        """Create the scene manager with callbacks."""
        callbacks = MenuCallbacks(
            play_pvp=self._dummy_play_pvp,
            play_vs_ai=self._dummy_play_vs_ai,
            show_leaderboard=self._show_leaderboard,
            show_history=self._show_history,
            reset_data=self._show_reset_scene,
            quit_game=self._dummy_quit_game,
        )

        self.scene_manager = create_main_menu(self.screen, callbacks)

    def _dummy_play_pvp(self, player_x: str, player_o: str) -> None:
        """Dummy callback for PvP game."""
        print(f"Starting PvP game: {player_x} vs {player_o}")

    def _dummy_play_vs_ai(self, player_name: str, difficulty: str) -> None:
        """Dummy callback for PvAI game."""
        print(f"Starting PvAI game: {player_name} vs AI ({difficulty})")

    def _show_leaderboard(self) -> None:
        """Real callback for showing leaderboard."""
        print("Showing leaderboard")
        self.scene_manager.set_scene("leaderboard")

    def _show_history(self) -> None:
        """Real callback for showing match history."""
        print("Showing match history")
        self.scene_manager.set_scene("history")

    def _show_reset_scene(self) -> None:
        """Real callback for showing reset scene."""
        print("Showing reset scene")
        self.scene_manager.set_scene("reset")

    def _dummy_quit_game(self) -> None:
        """Dummy callback for quit."""
        print("Quitting game")
        pygame.quit()
        exit()

    def run(self) -> None:
        """Run the menu test application."""
        print("Scene manager created successfully!")
        print("You can now interact with the menu.")
        print("Press ESC to return to menu from scenes.")

        # Run scene manager loop
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    exit()

                # Handle scene manager events
                result = self.scene_manager.handle_event(event)
                if result == "quit":
                    running = False
                    break

            # Draw current scene
            self.scene_manager.draw(self.screen)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


def test_menu() -> None:
    """Test the menu system with real scene functionality."""
    app = MenuTestApp()
    app.run()


if __name__ == "__main__":
    test_menu()
