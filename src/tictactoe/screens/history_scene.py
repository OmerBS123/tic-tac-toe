"""
Match history scene for displaying recent games using pygame.
"""

import pygame

from ..infra.storage import Storage
from ..app.scene import Scene
from ..ui.layout import Layout, compute_layout, make_fonts
from ..domain.services.history_service import HistoryService
from ..infra.logger import get_logger

logger = get_logger()


class MatchHistoryScene(Scene):
    """Pygame scene for displaying match history with scrolling."""

    def __init__(self, storage: Storage, width: int = 1000, height: int = 1100) -> None:
        """
        Initialize match history scene.

        Args:
            storage: Storage instance for database operations
            width: Scene width
            height: Scene height
        """
        super().__init__(width, height)
        self.storage = storage
        self.manager = HistoryService(storage)

        # Scrolling
        self.scroll_offset = 0
        self.max_scroll = 0
        self.rows_per_page = 15

        # Initialize layout and fonts
        self._on_resize_impl(width, height)

        logger.info("MatchHistoryScene initialized")

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
        self.row_height = max(25, int(self.layout.font_ui * 1.2))
        self.header_height = max(35, int(self.layout.font_ui * 1.5))
        self.margin_x = self.layout.safe_margin

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
            elif event.key in (pygame.K_DOWN, pygame.K_PAGEDOWN):
                self._scroll_down()
            elif event.key in (pygame.K_UP, pygame.K_PAGEUP):
                self._scroll_up()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = event.pos
                if self._is_back_button_clicked(mouse_x, mouse_y):
                    logger.info("Back button clicked - returning to menu")
                    return "menu"
        return None

    def _scroll_down(self) -> None:
        """Scroll down in the history."""
        if self.scroll_offset < self.max_scroll:
            self.scroll_offset += 1
            logger.debug(f"Scrolled down to offset {self.scroll_offset}")

    def _scroll_up(self) -> None:
        """Scroll up in the history."""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
            logger.debug(f"Scrolled up to offset {self.scroll_offset}")

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the match history scene.

        Args:
            surface: Pygame surface to draw on
        """
        surface.fill(self.bg_color)

        # Draw title
        title_text = self.fonts["title"].render("MATCH HISTORY", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.width // 2, self.title_y))
        surface.blit(title_text, title_rect)

        # Get history data
        try:
            history_data = self.manager.get_history_data(limit=100)
            self.max_scroll = max(0, len(history_data.rows) - self.rows_per_page)
            self._draw_history_table(surface, history_data)
        except Exception as e:
            logger.error(f"Error drawing match history: {e}")
            self._draw_error_message(surface, "Error loading match history")

        # Draw back button
        self._draw_back_button(surface)

        # Draw instructions
        instructions = self.fonts["small"].render("↑/↓ to scroll • ESC or click Back to return", True, self.header_color)
        surface.blit(instructions, (self.width - instructions.get_width() - 20, self.height - 30))

    def _draw_history_table(self, surface: pygame.Surface, data) -> None:
        """
        Draw the match history table.

        Args:
            surface: Pygame surface to draw on
            data: HistoryData from manager
        """
        if not data.rows:
            self._draw_no_data_message(surface)
            return

        # Calculate column widths
        col_widths = [100, 80, 120, 40, 120, 80, 80, 80]  # Date, Time, Player X, vs, Player O, Result, Mode, AI Level
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

        # Draw visible rows (with scrolling)
        visible_rows = data.rows[self.scroll_offset : self.scroll_offset + self.rows_per_page]
        for row in visible_rows:
            self._draw_history_row(surface, row, col_x_positions, y)
            y += self.row_height

        # Draw scroll indicator
        if len(data.rows) > self.rows_per_page:
            self._draw_scroll_indicator(surface, len(data.rows))

    def _draw_history_row(self, surface: pygame.Surface, row, col_x_positions: list, y: int) -> None:
        """
        Draw a single history row.

        Args:
            surface: Pygame surface to draw on
            row: HistoryRow data
            col_x_positions: X positions for each column
            y: Y position for the row
        """
        # Date
        date_surface = self.fonts["ui"].render(row.date_str, True, self.text_color)
        surface.blit(date_surface, (col_x_positions[0], y))

        # Time
        time_surface = self.fonts["ui"].render(row.time_str, True, self.text_color)
        surface.blit(time_surface, (col_x_positions[1], y))

        # Player X
        player_x_surface = self.fonts["ui"].render(row.player_x_name, True, self.text_color)
        surface.blit(player_x_surface, (col_x_positions[2], y))

        # VS
        vs_surface = self.fonts["ui"].render("vs", True, self.accent_color)
        surface.blit(vs_surface, (col_x_positions[3], y))

        # Player O
        player_o_surface = self.fonts["ui"].render(row.player_o_name, True, self.text_color)
        surface.blit(player_o_surface, (col_x_positions[4], y))

        # Result
        result_color = self._get_result_color(row.result)
        result_surface = self.fonts["ui"].render(row.result, True, result_color)
        surface.blit(result_surface, (col_x_positions[5], y))

        # Mode
        mode_surface = self.fonts["ui"].render(row.mode, True, self.text_color)
        surface.blit(mode_surface, (col_x_positions[6], y))

        # AI Level
        ai_level_surface = self.fonts["ui"].render(row.ai_level_display, True, self.text_color)
        surface.blit(ai_level_surface, (col_x_positions[7], y))

    def _get_result_color(self, result: str) -> tuple[int, int, int]:
        """
        Get color for result text.

        Args:
            result: Game result (player name or 'Draw')

        Returns:
            RGB color tuple
        """
        if result == "Draw":
            return (200, 200, 200)  # Gray for draw
        else:
            return (100, 200, 255)  # Blue for winner

    def _draw_scroll_indicator(self, surface: pygame.Surface, total_rows: int) -> None:
        """
        Draw scroll indicator.

        Args:
            surface: Pygame surface to draw on
            total_rows: Total number of rows
        """
        # Calculate scroll bar position
        scroll_height = 200
        scroll_y = self.height - scroll_height - 50
        scroll_width = 20

        # Background
        pygame.draw.rect(surface, (50, 50, 50), (self.width - scroll_width - 20, scroll_y, scroll_width, scroll_height))

        # Scroll thumb
        thumb_height = max(20, int(scroll_height * self.rows_per_page / total_rows))
        thumb_y = scroll_y + int((scroll_height - thumb_height) * self.scroll_offset / self.max_scroll)

        pygame.draw.rect(surface, self.accent_color, (self.width - scroll_width - 20, thumb_y, scroll_width, thumb_height))

    def _draw_no_data_message(self, surface: pygame.Surface) -> None:
        """
        Draw message when no history data is available.

        Args:
            surface: Pygame surface to draw on
        """
        message = self.fonts["ui"].render("No matches played yet!", True, self.header_color)
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
