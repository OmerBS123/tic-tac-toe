"""
Reset confirmation scene for confirming data reset using pygame.
"""

import pygame

from ..infra.storage import Storage
from ..scene import Scene
from ..layout import compute_layout, make_fonts
from ..logger import get_logger

logger = get_logger()


class ResetScene(Scene):
    """Pygame scene for confirming data reset."""

    def __init__(self, storage: Storage, width: int = 1000, height: int = 1100) -> None:
        """
        Initialize reset scene.

        Args:
            storage: Storage instance for database operations
            width: Scene width
            height: Scene height
        """
        super().__init__(width, height)
        self.storage = storage

        # Initialize layout and fonts
        self._on_resize_impl(width, height)

        logger.info("ResetScene initialized")

    def _on_resize_impl(self, width: int, height: int) -> None:
        """Handle resize implementation."""
        self.layout = compute_layout(width, height)
        self.fonts = make_fonts(self.layout)

        # Colors
        self.bg_color = (18, 18, 18)
        self.title_color = (100, 200, 255)
        self.text_color = (255, 255, 255)
        self.header_color = (200, 200, 200)
        self.accent_color = (100, 200, 255)
        self.warning_color = (255, 200, 100)
        self.error_color = (255, 100, 100)

        # Layout calculations
        self.title_y = self.layout.safe_margin
        self.content_start_y = self.title_y + self.layout.font_title + 40
        self.button_width = 200
        self.button_height = 60
        self.button_spacing = 30

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events.

        Args:
            event: Pygame event
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                logger.info("ESC pressed - returning to menu")
                return "menu"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = event.pos
                if self._is_back_button_clicked(mouse_x, mouse_y):
                    logger.info("Back button clicked - returning to menu")
                    return "menu"
                elif self._is_yes_button_clicked(mouse_x, mouse_y):
                    logger.info("Yes button clicked - executing reset")
                    return "reset_confirmed"
                elif self._is_no_button_clicked(mouse_x, mouse_y):
                    logger.info("No button clicked - returning to menu")
                    return "menu"
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the reset confirmation scene.

        Args:
            surface: Pygame surface to draw on
        """
        surface.fill(self.bg_color)

        # Draw title - using same centering method as leaderboard
        title_text = self.fonts["title"].render("CONFIRM RESET", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.width // 2, self.title_y))
        surface.blit(title_text, title_rect)

        # Draw confirmation message
        self._draw_confirmation_message(surface)

        # Draw buttons
        self._draw_buttons(surface)

        # Draw back button
        self._draw_back_button(surface)

        # Draw instructions
        instructions = self.fonts["small"].render("Press ESC or click Back to return to menu", True, self.header_color)
        surface.blit(instructions, (self.width - instructions.get_width() - 20, self.height - 30))

    def _draw_confirmation_message(self, surface: pygame.Surface) -> None:
        """
        Draw the confirmation message.

        Args:
            surface: Pygame surface to draw on
        """
        # Main question
        question_text = self.fonts["ui"].render("Are you sure you want to reset all data?", True, self.text_color)
        question_rect = question_text.get_rect(center=(self.width // 2, self.content_start_y))
        surface.blit(question_text, question_rect)

        # Warning message
        warning_text = self.fonts["small"].render("This will delete all match history and leaderboard data.", True, self.warning_color)
        warning_rect = warning_text.get_rect(center=(self.width // 2, self.content_start_y + 50))
        surface.blit(warning_text, warning_rect)

        # Additional warning
        warning2_text = self.fonts["small"].render("This action cannot be undone!", True, self.error_color)
        warning2_rect = warning2_text.get_rect(center=(self.width // 2, self.content_start_y + 80))
        surface.blit(warning2_text, warning2_rect)

    def _draw_buttons(self, surface: pygame.Surface) -> None:
        """
        Draw the Yes/No confirmation buttons.

        Args:
            surface: Pygame surface to draw on
        """
        # Calculate button positions (centered)
        total_button_width = 2 * self.button_width + self.button_spacing
        start_x = (self.width - total_button_width) // 2
        button_y = self.content_start_y + 150

        # Yes button (red/destructive)
        yes_x = start_x
        self._draw_button(surface, "YES, RESET", yes_x, button_y, self.button_width, self.button_height, self.error_color, (255, 150, 150))

        # No button (gray/cancel)
        no_x = start_x + self.button_width + self.button_spacing
        self._draw_button(surface, "NO, CANCEL", no_x, button_y, self.button_width, self.button_height, (100, 100, 100), (150, 150, 150))

    def _draw_button(self, surface: pygame.Surface, text: str, x: int, y: int, width: int, height: int, bg_color: tuple, border_color: tuple) -> None:
        """
        Draw a button with text.

        Args:
            surface: Pygame surface to draw on
            text: Button text
            x: Button X position
            y: Button Y position
            width: Button width
            height: Button height
            bg_color: Background color
            border_color: Border color
        """
        # Draw button background with rounded corners
        pygame.draw.rect(surface, bg_color, (x, y, width, height), border_radius=8)
        pygame.draw.rect(surface, border_color, (x, y, width, height), width=2, border_radius=8)

        # Draw button text
        button_text = self.fonts["ui"].render(text, True, self.text_color)
        text_rect = button_text.get_rect(center=(x + width // 2, y + height // 2))
        surface.blit(button_text, text_rect)

    def _draw_back_button(self, surface: pygame.Surface) -> None:
        """
        Draw the back button.

        Args:
            surface: Pygame surface to draw on
        """
        button_width = 100
        button_height = 50
        button_x = 20
        button_y = self.height - 70

        # Draw button background with rounded corners
        pygame.draw.rect(surface, (80, 80, 80), (button_x, button_y, button_width, button_height), border_radius=8)
        pygame.draw.rect(surface, (120, 120, 120), (button_x, button_y, button_width, button_height), width=2, border_radius=8)

        # Draw button text
        back_text = self.fonts["ui"].render("Back", True, self.text_color)
        text_rect = back_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
        surface.blit(back_text, text_rect)

        # Store button rect for click detection
        self.back_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    def _is_back_button_clicked(self, mouse_x: int, mouse_y: int) -> bool:
        """
        Check if the back button was clicked.

        Args:
            mouse_x: Mouse X position
            mouse_y: Mouse Y position

        Returns:
            True if back button was clicked
        """
        return hasattr(self, "back_button_rect") and self.back_button_rect.collidepoint(mouse_x, mouse_y)

    def _is_yes_button_clicked(self, mouse_x: int, mouse_y: int) -> bool:
        """
        Check if the Yes button was clicked.

        Args:
            mouse_x: Mouse X position
            mouse_y: Mouse Y position

        Returns:
            True if Yes button was clicked
        """
        if not hasattr(self, "yes_button_rect"):
            # Calculate Yes button position
            total_button_width = 2 * self.button_width + self.button_spacing
            start_x = (self.width - total_button_width) // 2
            button_y = self.content_start_y + 150
            self.yes_button_rect = pygame.Rect(start_x, button_y, self.button_width, self.button_height)

        return self.yes_button_rect.collidepoint(mouse_x, mouse_y)

    def _is_no_button_clicked(self, mouse_x: int, mouse_y: int) -> bool:
        """
        Check if the No button was clicked.

        Args:
            mouse_x: Mouse X position
            mouse_y: Mouse Y position

        Returns:
            True if No button was clicked
        """
        if not hasattr(self, "no_button_rect"):
            # Calculate No button position
            total_button_width = 2 * self.button_width + self.button_spacing
            start_x = (self.width - total_button_width) // 2
            button_y = self.content_start_y + 150
            self.no_button_rect = pygame.Rect(start_x + self.button_width + self.button_spacing, button_y, self.button_width, self.button_height)

        return self.no_button_rect.collidepoint(mouse_x, mouse_y)
