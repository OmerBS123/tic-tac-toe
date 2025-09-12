"""
Scene manager for coordinating all game scenes.
"""

from collections.abc import Callable

import pygame

from tictactoe.consts.scene_consts import SceneTransition
from tictactoe.infra.logger import get_logger
from tictactoe.infra.storage import Storage
from tictactoe.screens.game_scene import GameScene
from tictactoe.screens.history_scene import MatchHistoryScene
from tictactoe.screens.leaderboard_scene import LeaderboardScene
from tictactoe.screens.main_menu_scene import MainMenuScene
from tictactoe.screens.reset_scene import ResetScene

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

        self.main_menu_scene = MainMenuScene(storage, width, height)
        self.leaderboard_scene = LeaderboardScene(storage, width, height)
        self.history_scene = MatchHistoryScene(storage, width, height)
        self.reset_scene = ResetScene(storage, width, height)
        self.game_scene = GameScene(storage, width, height)

        self.current_scene = "main_menu"

        logger.info("SceneManager initialized")

    def set_callbacks(self, callbacks: MenuCallbacks) -> None:
        """Set callbacks for all scenes."""
        self.main_menu_scene.set_callbacks(
            play_pvp=callbacks.play_pvp,
            play_vs_ai=callbacks.play_vs_ai,
            show_leaderboard=callbacks.show_leaderboard,
            show_history=callbacks.show_history,
            reset_data=callbacks.reset_data,
            quit_game=callbacks.quit_game,
        )

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """
        Handle pygame events for the current scene.

        Args:
            event: Pygame event

        Returns:
            Optional string indicating scene transition
        """
        match self.current_scene:
            case "main_menu":
                result = self.main_menu_scene.handle_event(event)
            case "leaderboard":
                result = self.leaderboard_scene.handle_event(event)
            case "history":
                result = self.history_scene.handle_event(event)
            case "reset":
                result = self.reset_scene.handle_event(event)
            case "game":
                result = self.game_scene.handle_event(event)
            case _:
                result = None

        if result:
            match result:
                case SceneTransition.MENU:
                    self.current_scene = "main_menu"
                case SceneTransition.LEADERBOARD:
                    self.current_scene = "leaderboard"
                case SceneTransition.HISTORY:
                    self.current_scene = "history"
                case SceneTransition.RESET:
                    self.current_scene = "reset"
                case SceneTransition.GAME:
                    return SceneTransition.GAME
                case SceneTransition.QUIT:
                    return SceneTransition.QUIT
                case SceneTransition.RESET_CONFIRMED:
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
        logger.debug(f"SceneManager.draw START - current_scene: {self.current_scene}")

        match self.current_scene:
            case "main_menu":
                logger.debug("SceneManager.draw - drawing main menu")
                self.main_menu_scene.draw(surface)
            case "leaderboard":
                logger.debug("SceneManager.draw - drawing leaderboard")
                self.leaderboard_scene.draw(surface)
            case "history":
                logger.debug("SceneManager.draw - drawing history")
                self.history_scene.draw(surface)
            case "reset":
                logger.debug("SceneManager.draw - drawing reset")
                self.reset_scene.draw(surface)
            case "game":
                logger.debug("SceneManager.draw - drawing game")
                self.game_scene.draw(surface)

        logger.debug("SceneManager.draw END")

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

            self.main_menu_scene.on_resize(width, height)
            self.leaderboard_scene.on_resize(width, height)
            self.history_scene.on_resize(width, height)
            self.reset_scene.on_resize(width, height)
            self.game_scene.on_resize(width, height)

            logger.info(f"SceneManager resized to {width}x{height}")

    def get_current_scene(self) -> str:
        """Get the current scene name."""
        return self.current_scene

    def set_scene(self, scene_name: str) -> None:
        """Set the current scene."""
        self.current_scene = scene_name
        logger.info(f"Switched to scene: {scene_name}")

    def start_pvp_game(self, player_x_name: str, player_o_name: str) -> None:
        """
        Start a Player vs Player game.

        Args:
            player_x_name: Name of player X
            player_o_name: Name of player O
        """
        self.game_scene.setup_game("pvp", player_x_name, player_o_name)
        self.current_scene = "game"
        logger.info(f"Started PvP game: {player_x_name} vs {player_o_name}")

    def start_pvai_game(self, player_name: str, ai_difficulty) -> None:
        """
        Start a Player vs AI game.

        Args:
            player_name: Name of human player
            ai_difficulty: AI difficulty level
        """
        self.game_scene.setup_game("pvai", player_name, ai_difficulty=ai_difficulty)
        self.current_scene = "game"
        logger.info(f"Started PvAI game: {player_name} vs AI ({ai_difficulty.value})")
