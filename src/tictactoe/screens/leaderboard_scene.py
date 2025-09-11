"""
Leaderboard scene for displaying player statistics using pygame.
"""

import pygame

from ..app.scene import Scene
from ..consts.scene_consts import SceneTransition
from ..domain.services.leaderboard_service import LeaderboardService
from ..infra.logger import get_logger
from ..infra.storage import Storage
from ..ui.layout import compute_layout, make_fonts

logger = get_logger()


class LeaderboardScene(Scene):
    """Pygame scene for displaying the leaderboard."""

    def __init__(self, storage: Storage, width: int = 1000, height: int = 1100) -> None:
        """
        Initialize leaderboard scene.

        Args:
            storage: Storage instance for database operations
            width: Scene width
            height: Scene height
        """
        super().__init__(width, height)
        self.storage = storage
        self.manager = LeaderboardService(storage)

        # Initialize layout and fonts
        self._on_resize_impl(width, height)

        logger.info("LeaderboardScene initialized")

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

        # Layout calculations
        self.title_y = self.layout.safe_margin
        self.table_start_y = self.title_y + self.layout.font_title + 20
        self.row_height = max(30, int(self.layout.font_ui * 1.5))
        self.header_height = max(40, int(self.layout.font_ui * 1.8))
        self.margin_x = self.layout.safe_margin

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """
        Handle pygame events.

        Args:
            event: Pygame event

        Returns:
            String indicating scene transition (SceneTransition.MENU) or None if no action needed
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                logger.info("ESC pressed - returning to menu")
                return SceneTransition.MENU
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = event.pos
                if self._is_back_button_clicked(mouse_x, mouse_y):
                    logger.info("Back button clicked - returning to menu")
                    return SceneTransition.MENU
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the leaderboard scene.

        Args:
            surface: Pygame surface to draw on
        """
        surface.fill(self.bg_color)

        # Draw title
        title_text = self.fonts["title"].render("LEADERBOARD", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.width // 2, self.title_y))
        surface.blit(title_text, title_rect)

        # Get leaderboard data
        try:
            leaderboard_data = self.manager.get_leaderboard_data(limit=20)
            self._draw_leaderboard_table(surface, leaderboard_data)
        except Exception as e:
            logger.error(f"Error drawing leaderboard: {e}")
            self._draw_error_message(surface, "Error loading leaderboard")

        # Draw back button
        self._draw_back_button(surface)

        # Draw instructions
        instructions = self.fonts["small"].render("Press ESC or click Back to return to menu", True, self.header_color)
        surface.blit(instructions, (self.width - instructions.get_width() - 20, self.height - 30))

    def _draw_leaderboard_table(self, surface: pygame.Surface, data) -> None:
        """
        Draw the leaderboard table.

        Args:
            surface: Pygame surface to draw on
            data: LeaderboardData from manager
        """
        if not data.rows:
            self._draw_no_data_message(surface)
            return

        # Calculate column widths
        col_widths = [60, 150, 80, 60, 60, 60, 80, 80, 80]  # Rank, Name, Total, PvP, AI-E, AI-M, AI-H, Win%, Games
        col_x_positions = [self.margin_x]
        for width in col_widths[:-1]:
            col_x_positions.append(col_x_positions[-1] + width)

        # Draw headers
        y = self.table_start_y
        for i, header in enumerate(data.headers):
            header_text = self.fonts["ui"].render(header, True, self.header_color)
            surface.blit(header_text, (col_x_positions[i], y))

        # Draw separator line
        pygame.draw.line(surface, self.header_color, (self.margin_x, y + self.header_height), (self.width - self.margin_x, y + self.header_height), 2)

        y += self.header_height + 10

        # Draw rows
        for row in data.rows:
            self._draw_leaderboard_row(surface, row, col_x_positions, y)
            y += self.row_height

    def _draw_leaderboard_row(self, surface: pygame.Surface, row, col_x_positions: list, y: int) -> None:
        """
        Draw a single leaderboard row.

        Args:
            surface: Pygame surface to draw on
            row: LeaderboardRow data
            col_x_positions: X positions for each column
            y: Y position for the row
        """
        # Rank with medal - only show medal text, not rank number
        rank_text = row.medal if row.medal else str(row.rank)
        rank_surface = self.fonts["ui"].render(rank_text, True, self.text_color)
        surface.blit(rank_surface, (col_x_positions[0], y))

        # Player name
        name_surface = self.fonts["ui"].render(row.name, True, self.text_color)
        surface.blit(name_surface, (col_x_positions[1], y))

        # Statistics
        stats = [str(row.total_wins), str(row.pvp_wins), str(row.ai_easy_wins), str(row.ai_medium_wins), str(row.ai_hard_wins), f"{row.win_percentage:.1f}%", str(row.total_games)]  # win_percentage is now already multiplied by 100

        for i, stat in enumerate(stats):
            stat_surface = self.fonts["ui"].render(stat, True, self.text_color)
            surface.blit(stat_surface, (col_x_positions[i + 2], y))

    def _draw_no_data_message(self, surface: pygame.Surface) -> None:
        """
        Draw message when no leaderboard data is available.

        Args:
            surface: Pygame surface to draw on
        """
        message = self.fonts["ui"].render("No games played yet!", True, self.header_color)
        message_rect = message.get_rect(center=(self.width // 2, self.height // 2))
        surface.blit(message, message_rect)

    def _draw_error_message(self, surface: pygame.Surface, message: str) -> None:
        """
        Draw error message.

        Args:
            surface: Pygame surface to draw on
            message: Error message to display
        """
        error_text = self.fonts["ui"].render(message, True, (255, 100, 100))
        error_rect = error_text.get_rect(center=(self.width // 2, self.height // 2))
        surface.blit(error_text, error_rect)

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

        # Draw button text with larger font
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
