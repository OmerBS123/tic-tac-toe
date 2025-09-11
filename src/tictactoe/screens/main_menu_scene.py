"""
Main menu scene for the tic-tac-toe game using pygame.
"""

import pygame
from typing import Optional, Callable

from ..infra.storage import Storage
from ..scene import Scene
from ..layout import compute_layout, make_fonts
from ..consts.ai_consts import Difficulty
from ..logger import get_logger

logger = get_logger()


class MainMenuScene(Scene):
    """Pygame scene for the main menu with input fields and buttons."""

    def __init__(self, storage: Storage, width: int = 1000, height: int = 1100) -> None:
        """
        Initialize main menu scene.

        Args:
            storage: Storage instance for database operations
            width: Scene width
            height: Scene height
        """
        super().__init__(width, height)
        self.storage = storage

        # Callbacks for scene transitions
        self.play_pvp_callback: Optional[Callable[[str, str], None]] = None
        self.play_vs_ai_callback: Optional[Callable[[str, str], None]] = None
        self.show_leaderboard_callback: Optional[Callable[[], None]] = None
        self.show_history_callback: Optional[Callable[[], None]] = None
        self.reset_data_callback: Optional[Callable[[], None]] = None
        self.quit_game_callback: Optional[Callable[[], None]] = None

        # Input state
        self.player_x_name = "Player X"
        self.player_o_name = "Player O"
        self.ai_difficulty = Difficulty.MEDIUM
        self.selected_difficulty_index = 1  # Medium by default

        # UI state
        self.active_input = None  # "player_x", "player_o", or None
        self.cursor_blink_time = 0
        self.cursor_visible = True

        # Initialize layout and fonts
        self._on_resize_impl(width, height)

        logger.info("MainMenuScene initialized")

    def set_callbacks(
        self,
        play_pvp: Callable[[str, str], None],
        play_vs_ai: Callable[[str, str], None],
        show_leaderboard: Callable[[], None],
        show_history: Callable[[], None],
        reset_data: Callable[[], None],
        quit_game: Callable[[], None],
    ) -> None:
        """Set callback functions for scene transitions."""
        self.play_pvp_callback = play_pvp
        self.play_vs_ai_callback = play_vs_ai
        self.show_leaderboard_callback = show_leaderboard
        self.show_history_callback = show_history
        self.reset_data_callback = reset_data
        self.quit_game_callback = quit_game

    def _on_resize_impl(self, width: int, height: int) -> None:
        """Handle resize implementation."""
        self.layout = compute_layout(width, height)
        self.fonts = make_fonts(self.layout)

        # Colors
        self.bg_color = (18, 18, 18)
        self.title_color = (100, 200, 255)
        self.text_color = (255, 255, 255)
        self.input_color = (60, 60, 70)
        self.input_border_color = (100, 200, 255)
        self.input_active_color = (100, 200, 255)
        self.button_color = (50, 50, 50)
        self.button_hover_color = (70, 70, 70)
        self.button_text_color = (255, 255, 255)
        self.accent_color = (100, 200, 255)

        # Layout calculations
        self.title_y = self.layout.safe_margin
        self.content_start_y = self.title_y + self.layout.font_title + 40

        # Input field dimensions
        self.input_width = 300
        self.input_height = 40
        self.input_spacing = 60

        # Button dimensions
        self.button_width = 200
        self.button_height = 50
        self.button_spacing = 20

        # Calculate positions
        self.input_x = (self.width - self.input_width) // 2
        self.button_x = (self.width - self.button_width) // 2

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        Handle pygame events.

        Args:
            event: Pygame event

        Returns:
            Optional string indicating scene transition
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                logger.info("ESC pressed - quitting game")
                if self.quit_game_callback:
                    self.quit_game_callback()
                return "quit"
            elif event.key == pygame.K_TAB:
                # Switch between input fields
                if self.active_input == "player_x":
                    self.active_input = "player_o"
                elif self.active_input == "player_o":
                    self.active_input = None
                else:
                    self.active_input = "player_x"
            elif event.key == pygame.K_RETURN:
                # Start game with current settings
                return self._start_pvp_game()
            elif self.active_input:
                # Handle text input
                if event.key == pygame.K_BACKSPACE:
                    if self.active_input == "player_x":
                        self.player_x_name = self.player_x_name[:-1]
                    elif self.active_input == "player_o":
                        self.player_o_name = self.player_o_name[:-1]
                elif event.unicode.isprintable() and len(event.unicode) == 1:
                    if self.active_input == "player_x" and len(self.player_x_name) < 20:
                        self.player_x_name += event.unicode
                    elif self.active_input == "player_o" and len(self.player_o_name) < 20:
                        self.player_o_name += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = event.pos
                return self._handle_mouse_click(mouse_x, mouse_y)

        elif event.type == pygame.MOUSEWHEEL:
            # Handle difficulty selection with mouse wheel
            if self._is_difficulty_area_clicked(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                if event.y > 0:  # Scroll up
                    self.selected_difficulty_index = (self.selected_difficulty_index - 1) % 3
                else:  # Scroll down
                    self.selected_difficulty_index = (self.selected_difficulty_index + 1) % 3
                self.ai_difficulty = list(Difficulty)[self.selected_difficulty_index]

        return None

    def _handle_mouse_click(self, mouse_x: int, mouse_y: int) -> Optional[str]:
        """Handle mouse click events."""
        # Check input field clicks
        if self._is_player_x_input_clicked(mouse_x, mouse_y):
            self.active_input = "player_x"
        elif self._is_player_o_input_clicked(mouse_x, mouse_y):
            self.active_input = "player_o"
        elif self._is_difficulty_area_clicked(mouse_x, mouse_y):
            self.active_input = None
            # Cycle through difficulties
            self.selected_difficulty_index = (self.selected_difficulty_index + 1) % 3
            self.ai_difficulty = list(Difficulty)[self.selected_difficulty_index]
        else:
            self.active_input = None

        # Check button clicks
        if self._is_play_pvp_button_clicked(mouse_x, mouse_y):
            return self._start_pvp_game()
        elif self._is_play_vs_ai_button_clicked(mouse_x, mouse_y):
            return self._start_pvai_game()
        elif self._is_leaderboard_button_clicked(mouse_x, mouse_y):
            if self.show_leaderboard_callback:
                self.show_leaderboard_callback()
            return "leaderboard"
        elif self._is_history_button_clicked(mouse_x, mouse_y):
            if self.show_history_callback:
                self.show_history_callback()
            return "history"
        elif self._is_reset_button_clicked(mouse_x, mouse_y):
            if self.reset_data_callback:
                self.reset_data_callback()
            return "reset"
        elif self._is_quit_button_clicked(mouse_x, mouse_y):
            if self.quit_game_callback:
                self.quit_game_callback()
            return "quit"

        return None

    def _start_pvp_game(self) -> Optional[str]:
        """Start PvP game with current input values."""
        # Validate inputs
        if not self.player_x_name.strip() or not self.player_o_name.strip():
            logger.warning("Player names cannot be empty")
            return None

        if self.player_x_name.strip() == self.player_o_name.strip():
            logger.warning("Player names must be different")
            return None

        logger.info(f"Starting PvP game: {self.player_x_name} vs {self.player_o_name}")
        if self.play_pvp_callback:
            self.play_pvp_callback(self.player_x_name.strip(), self.player_o_name.strip())
        return "game"

    def _start_pvai_game(self) -> Optional[str]:
        """Start PvAI game with current input values."""
        # Validate input
        if not self.player_x_name.strip():
            logger.warning("Player name cannot be empty")
            return None

        logger.info(f"Starting PvAI game: {self.player_x_name} vs AI ({self.ai_difficulty.value})")
        if self.play_vs_ai_callback:
            self.play_vs_ai_callback(self.player_x_name.strip(), self.ai_difficulty.value)
        return "game"

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the main menu scene.

        Args:
            surface: Pygame surface to draw on
        """
        surface.fill(self.bg_color)

        # Update cursor blink
        self.cursor_blink_time += 1
        if self.cursor_blink_time >= 30:  # Blink every 30 frames
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink_time = 0

        # Draw title - using same centering method as other scenes
        title_text = self.fonts["title"].render("TIC TAC TOE", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.width // 2, self.title_y))
        surface.blit(title_text, title_rect)

        # Draw input fields
        self._draw_input_fields(surface)

        # Draw buttons
        self._draw_buttons(surface)

        # Draw instructions
        instructions = self.fonts["small"].render("TAB to switch fields • ENTER to start PvP • ESC to quit", True, self.text_color)
        surface.blit(instructions, (self.width - instructions.get_width() - 20, self.height - 30))

    def _draw_input_fields(self, surface: pygame.Surface) -> None:
        """Draw input fields for player names and AI difficulty."""
        y = self.content_start_y

        # Player X input
        self._draw_input_field(surface, "Player X Name:", self.player_x_name, self.input_x, y, self.active_input == "player_x")
        y += self.input_spacing

        # Player O input
        self._draw_input_field(surface, "Player O Name:", self.player_o_name, self.input_x, y, self.active_input == "player_o")
        y += self.input_spacing

        # AI Difficulty selector
        self._draw_difficulty_selector(surface, "AI Difficulty:", y)

    def _draw_input_field(self, surface: pygame.Surface, label: str, value: str, x: int, y: int, active: bool) -> None:
        """Draw a single input field."""
        # Draw label
        label_text = self.fonts["ui"].render(label, True, self.text_color)
        surface.blit(label_text, (x - label_text.get_width() - 20, y + 10))

        # Draw input field background
        border_color = self.input_active_color if active else self.input_border_color
        pygame.draw.rect(surface, self.input_color, (x, y, self.input_width, self.input_height))
        pygame.draw.rect(surface, border_color, (x, y, self.input_width, self.input_height), width=2)

        # Draw text
        text_surface = self.fonts["ui"].render(value, True, self.text_color)
        surface.blit(text_surface, (x + 10, y + 10))

        # Draw cursor if active
        if active and self.cursor_visible:
            cursor_x = x + 10 + text_surface.get_width()
            pygame.draw.line(surface, self.text_color, (cursor_x, y + 5), (cursor_x, y + self.input_height - 5), 2)

    def _draw_difficulty_selector(self, surface: pygame.Surface, label: str, y: int) -> None:
        """Draw AI difficulty selector."""
        # Draw label
        label_text = self.fonts["ui"].render(label, True, self.text_color)
        surface.blit(label_text, (self.input_x - label_text.get_width() - 20, y + 10))

        # Draw selector background
        pygame.draw.rect(surface, self.input_color, (self.input_x, y, self.input_width, self.input_height))
        pygame.draw.rect(surface, self.input_border_color, (self.input_x, y, self.input_width, self.input_height), width=2)

        # Draw difficulty text
        difficulty_text = f"{self.ai_difficulty.value.title()} - {'Random moves' if self.ai_difficulty == Difficulty.EASY else 'Smart moves' if self.ai_difficulty == Difficulty.MEDIUM else 'Optimal play'}"
        text_surface = self.fonts["ui"].render(difficulty_text, True, self.text_color)
        surface.blit(text_surface, (self.input_x + 10, y + 10))

    def _draw_buttons(self, surface: pygame.Surface) -> None:
        """Draw action buttons."""
        y = self.content_start_y + 200

        # Play 1 vs 1 button
        self._draw_button(surface, "Play 1 vs 1", self.button_x, y, (0, 150, 0), (0, 200, 0))
        y += self.button_height + self.button_spacing

        # Play vs AI button
        self._draw_button(surface, "Play vs AI", self.button_x, y, (0, 100, 200), (0, 150, 255))
        y += self.button_height + self.button_spacing

        # Secondary buttons (smaller)
        secondary_width = 150
        secondary_x = (self.width - secondary_width) // 2

        # Leaderboard button
        self._draw_button(surface, "Leaderboard", secondary_x, y, (200, 150, 0), (255, 200, 0), secondary_width)
        y += self.button_height + self.button_spacing

        # History button
        self._draw_button(surface, "Match History", secondary_x, y, (200, 150, 0), (255, 200, 0), secondary_width)
        y += self.button_height + self.button_spacing

        # Reset button
        self._draw_button(surface, "Reset Data", secondary_x, y, (200, 50, 50), (255, 100, 100), secondary_width)
        y += self.button_height + self.button_spacing

        # Quit button
        self._draw_button(surface, "Quit", secondary_x, y, (100, 100, 100), (150, 150, 150), secondary_width)

    def _draw_button(self, surface: pygame.Surface, text: str, x: int, y: int, bg_color: tuple, border_color: tuple, width: int = None) -> None:
        """Draw a button."""
        if width is None:
            width = self.button_width

        # Draw button background
        pygame.draw.rect(surface, bg_color, (x, y, width, self.button_height), border_radius=8)
        pygame.draw.rect(surface, border_color, (x, y, width, self.button_height), width=2, border_radius=8)

        # Draw button text
        button_text = self.fonts["ui"].render(text, True, self.button_text_color)
        text_rect = button_text.get_rect(center=(x + width // 2, y + self.button_height // 2))
        surface.blit(button_text, text_rect)

    # Mouse click detection methods
    def _is_player_x_input_clicked(self, mouse_x: int, mouse_y: int) -> bool:
        y = self.content_start_y
        return self.input_x <= mouse_x <= self.input_x + self.input_width and y <= mouse_y <= y + self.input_height

    def _is_player_o_input_clicked(self, mouse_x: int, mouse_y: int) -> bool:
        y = self.content_start_y + self.input_spacing
        return self.input_x <= mouse_x <= self.input_x + self.input_width and y <= mouse_y <= y + self.input_height

    def _is_difficulty_area_clicked(self, mouse_x: int, mouse_y: int) -> bool:
        y = self.content_start_y + 2 * self.input_spacing
        return self.input_x <= mouse_x <= self.input_x + self.input_width and y <= mouse_y <= y + self.input_height

    def _is_play_pvp_button_clicked(self, mouse_x: int, mouse_y: int) -> bool:
        y = self.content_start_y + 200
        return self.button_x <= mouse_x <= self.button_x + self.button_width and y <= mouse_y <= y + self.button_height

    def _is_play_vs_ai_button_clicked(self, mouse_x: int, mouse_y: int) -> bool:
        y = self.content_start_y + 200 + self.button_height + self.button_spacing
        return self.button_x <= mouse_x <= self.button_x + self.button_width and y <= mouse_y <= y + self.button_height

    def _is_leaderboard_button_clicked(self, mouse_x: int, mouse_y: int) -> bool:
        y = self.content_start_y + 200 + 2 * (self.button_height + self.button_spacing)
        secondary_x = (self.width - 150) // 2
        return secondary_x <= mouse_x <= secondary_x + 150 and y <= mouse_y <= y + self.button_height

    def _is_history_button_clicked(self, mouse_x: int, mouse_y: int) -> bool:
        y = self.content_start_y + 200 + 3 * (self.button_height + self.button_spacing)
        secondary_x = (self.width - 150) // 2
        return secondary_x <= mouse_x <= secondary_x + 150 and y <= mouse_y <= y + self.button_height

    def _is_reset_button_clicked(self, mouse_x: int, mouse_y: int) -> bool:
        y = self.content_start_y + 200 + 4 * (self.button_height + self.button_spacing)
        secondary_x = (self.width - 150) // 2
        return secondary_x <= mouse_x <= secondary_x + 150 and y <= mouse_y <= y + self.button_height

    def _is_quit_button_clicked(self, mouse_x: int, mouse_y: int) -> bool:
        y = self.content_start_y + 200 + 5 * (self.button_height + self.button_spacing)
        secondary_x = (self.width - 150) // 2
        return secondary_x <= mouse_x <= secondary_x + 150 and y <= mouse_y <= y + self.button_height
