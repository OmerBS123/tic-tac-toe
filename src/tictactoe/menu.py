"""
Scene manager for coordinating all game scenes.
"""

from collections.abc import Callable
from typing import Any, Dict, Optional

import pygame

from .infra.storage import Storage
from .screens.main_menu_scene import MainMenuScene
from .screens.leaderboard_scene import LeaderboardScene
from .screens.history_scene import MatchHistoryScene
from .screens.reset_scene import ResetScene
from .logger import get_logger

logger = get_logger()


class MenuCallbacks:
    """Container for menu callback functions."""

    def __init__(
        self,
        play_pvp: Callable[[str, str], None],
        play_vs_ai: Callable[[str, str], None],
        show_leaderboard: Callable[[], None],
        show_history: Callable[[], None],
        reset_data: Callable[[], None],
        quit_game: Callable[[], None],
    ) -> None:
        """
        Initialize menu callbacks.

        Args:
            play_pvp: Callback for starting PvP game (player_x, player_o)
            play_vs_ai: Callback for starting PvAI game (player_name, difficulty)
            show_leaderboard: Callback for showing leaderboard
            show_history: Callback for showing match history
            reset_data: Callback for resetting all data
            quit_game: Callback for quitting the game
        """
        self.play_pvp = play_pvp
        self.play_vs_ai = play_vs_ai
        self.show_leaderboard = show_leaderboard
        self.show_history = show_history
        self.reset_data = reset_data
        self.quit_game = quit_game


class SceneManager:
    """Manages all game scenes and coordinates transitions."""

    def __init__(self, storage: Storage, width: int, height: int) -> None:
        """
        Initialize scene manager.

        Args:
            storage: Storage instance for database operations
            width: Initial window width
            height: Initial window height
        """
        self.storage = storage
        self.width = width
        self.height = height

        # Initialize all scenes
        self.main_menu_scene = MainMenuScene(storage, width, height)
        self.leaderboard_scene = LeaderboardScene(storage, width, height)
        self.history_scene = MatchHistoryScene(storage, width, height)
        self.reset_scene = ResetScene(storage, width, height)

        # Current scene
        self.current_scene = "main_menu"

        logger.info("SceneManager initialized")

    def set_callbacks(self, callbacks: MenuCallbacks) -> None:
        """Set callbacks for all scenes."""
        # Set main menu callbacks
        self.main_menu_scene.set_callbacks(
            play_pvp=callbacks.play_pvp,
            play_vs_ai=callbacks.play_vs_ai,
            show_leaderboard=callbacks.show_leaderboard,
            show_history=callbacks.show_history,
            reset_data=callbacks.reset_data,
            quit_game=callbacks.quit_game,
        )

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        Handle pygame events for the current scene.

        Args:
            event: Pygame event

        Returns:
            Optional string indicating scene transition
        """
        if self.current_scene == "main_menu":
            result = self.main_menu_scene.handle_event(event)
        elif self.current_scene == "leaderboard":
            result = self.leaderboard_scene.handle_event(event)
        elif self.current_scene == "history":
            result = self.history_scene.handle_event(event)
        elif self.current_scene == "reset":
            result = self.reset_scene.handle_event(event)
        else:
            result = None

        # Handle scene transitions
        if result:
            if result == "menu":
                self.current_scene = "main_menu"
            elif result == "leaderboard":
                self.current_scene = "leaderboard"
            elif result == "history":
                self.current_scene = "history"
            elif result == "reset":
                self.current_scene = "reset"
            elif result == "game":
                return "game"
            elif result == "quit":
                return "quit"
            elif result == "reset_confirmed":
                logger.info("Reset confirmed - executing reset")
                self.storage.reset_data()
                self.current_scene = "main_menu"

        return None

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the current scene.

        Args:
            surface: Pygame surface to draw on
        """
        if self.current_scene == "main_menu":
            self.main_menu_scene.draw(surface)
        elif self.current_scene == "leaderboard":
            self.leaderboard_scene.draw(surface)
        elif self.current_scene == "history":
            self.history_scene.draw(surface)
        elif self.current_scene == "reset":
            self.reset_scene.draw(surface)

    def on_resize(self, width: int, height: int) -> None:
        """
        Handle window resize for all scenes.

        Args:
            width: New window width
            height: New window height
        """
        if (width, height) != (self.width, self.height):
            self.width = width
            self.height = height

            # Update all scenes
            self.main_menu_scene.on_resize(width, height)
            self.leaderboard_scene.on_resize(width, height)
            self.history_scene.on_resize(width, height)
            self.reset_scene.on_resize(width, height)

            logger.info(f"SceneManager resized to {width}x{height}")

    def get_current_scene(self) -> str:
        """Get the current scene name."""
        return self.current_scene

    def set_scene(self, scene_name: str) -> None:
        """Set the current scene."""
        self.current_scene = scene_name
        logger.info(f"Switched to scene: {scene_name}")


# Legacy compatibility functions
def create_main_menu(screen: pygame.Surface, callbacks: MenuCallbacks) -> SceneManager:
    """
    Create the scene manager (legacy compatibility).

    Args:
        screen: Pygame surface for the menu
        callbacks: Menu callback functions

    Returns:
        SceneManager instance
    """
    width, height = screen.get_size()
    scene_manager = SceneManager(Storage(), width, height)
    scene_manager.set_callbacks(callbacks)

    logger.info("Scene manager created successfully")
    return scene_manager


def get_menu_data(scene_manager: SceneManager) -> Dict[str, Any]:
    """
    Get current menu data for debugging or state management.

    Args:
        scene_manager: Scene manager instance

    Returns:
        Dictionary with current menu values
    """
    data = {}

    if hasattr(scene_manager, "main_menu_scene"):
        main_menu = scene_manager.main_menu_scene
        data["player_x"] = main_menu.player_x_name
        data["player_o"] = main_menu.player_o_name
        data["ai_difficulty"] = main_menu.ai_difficulty.value

    return data


def set_menu_data(scene_manager: SceneManager, data: Dict[str, Any]) -> None:
    """
    Set menu data from a dictionary.

    Args:
        scene_manager: Scene manager instance
        data: Dictionary with menu values
    """
    if hasattr(scene_manager, "main_menu_scene"):
        main_menu = scene_manager.main_menu_scene

        if "player_x" in data:
            main_menu.player_x_name = data["player_x"]
        if "player_o" in data:
            main_menu.player_o_name = data["player_o"]
        if "ai_difficulty" in data:
            # Find the difficulty enum value
            from .consts.ai_consts import Difficulty

            for diff in Difficulty:
                if diff.value == data["ai_difficulty"]:
                    main_menu.ai_difficulty = diff
                    main_menu.selected_difficulty_index = list(Difficulty).index(diff)
                    break
