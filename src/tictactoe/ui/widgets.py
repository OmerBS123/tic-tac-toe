"""
UI widgets for tic-tac-toe game.
"""

from collections.abc import Callable

import pygame

from ..consts.board_consts import Player
from ..consts.theme_consts import Colors
from ..domain.board import Board
from ..infra.logger import get_logger

logger = get_logger()


class GameUI:
    """Game UI widget for pygame-based tic-tac-toe board."""

    def __init__(self, board: Board, layout, fonts) -> None:
        """
        Initialize the game UI.

        Args:
            board: Board instance
            layout: Layout instance for responsive sizing
            fonts: Font dictionary
        """
        self.board = board
        self.layout = layout
        self.fonts = fonts

        self.board_size = 3
        self.board_width = min(self.layout.width, self.layout.height) * 0.6
        self.board_height = self.board_width
        self.cell_size = self.board_width // self.board_size

        self.board_x = (self.layout.width - self.board_width) // 2
        self.board_y = (self.layout.height - self.board_height) // 2

        self.back_button_width = 100
        self.back_button_height = 50
        self.back_button_x = 20
        self.back_button_y = 50

        self.screen = None
        self.running = True
        self.current_player = Player.X_PLAYER.value
        self.game_over = False
        self.winner = None
        self.hovered_cell = None

        self.player_x_name = "Player X"
        self.player_o_name = "Player O"

        self.width = layout.width
        self.height = layout.height

        self.font = fonts.get("ui", pygame.font.Font(None, 24))
        self.status_font = fonts.get("small", pygame.font.Font(None, 18))

        self.clock = pygame.time.Clock()

        logger.info("GameUI initialized")
        self.on_move_callback: Callable[[tuple[int, int], int], None] | None = None
        self.on_game_over_callback: Callable[[int | None], None] | None = None

    def set_move_callback(
        self, callback: Callable[[tuple[int, int], int], None]
    ) -> None:
        """
        Set callback for when a move is made.

        Args:
            callback: Function called with (row, col, player) when move is made
        """
        self.on_move_callback = callback

    def set_game_over_callback(self, callback: Callable[[int | None], None]) -> None:
        """
        Set callback for when game is over.

        Args:
            callback: Function called with winner (or None for draw) when game ends
        """
        self.on_game_over_callback = callback

    def handle_mouse_click(self, pos: tuple[int, int]) -> bool:
        """
        Handle mouse click for making moves.

        Args:
            pos: Mouse position (x, y)

        Returns:
            True if a move was made, False otherwise
        """
        if self.game_over:
            return False

        x, y = pos
        col = int((x - self.board_x) // self.cell_size)
        row = int((y - self.board_y) // self.cell_size)

        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            if self.board.is_valid_move((row, col)):
                self._make_move((row, col))
                return True
        return False

    def handle_mouse_motion(self, pos: tuple[int, int]) -> None:
        """
        Handle mouse motion for hover effects.

        Args:
            pos: Mouse position (x, y)
        """
        if self.game_over:
            self.hovered_cell = None
            return

        cell = self._get_cell_from_pos(pos)
        self.hovered_cell = cell

    def _get_cell_from_pos(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        """
        Get cell coordinates from mouse position.

        Args:
            pos: Mouse position (x, y)

        Returns:
            (row, col) if position is valid, None otherwise
        """
        x, y = pos
        col = int((x - self.board_x) // self.cell_size)
        row = int((y - self.board_y) // self.cell_size)

        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return row, col
        return None

    def get_cell_from_mouse(self, mouse_x: int, mouse_y: int) -> tuple[int, int] | None:
        """
        Get cell coordinates from mouse position.

        Args:
            mouse_x: Mouse X position
            mouse_y: Mouse Y position

        Returns:
            (row, col) if position is valid, None otherwise
        """
        return self._get_cell_from_pos((mouse_x, mouse_y))

    def _make_move(self, move: tuple[int, int]) -> None:
        """
        Make a move on the board.

        Args:
            move: (row, col) position to play
        """
        if self.board.apply(move, self.current_player):
            logger.info(f"Move made: {self.current_player} at {move}")

            if self.on_move_callback:
                self.on_move_callback(move, self.current_player)

            if self.board.terminal():
                self.game_over = True
                self.winner = self.board.check_winner()
                logger.info(f"Game over. Winner: {self.winner}")

                if self.on_game_over_callback:
                    self.on_game_over_callback(self.winner)
            else:
                self.current_player = (
                    Player.O_PLAYER.value
                    if self.current_player == Player.X_PLAYER.value
                    else Player.X_PLAYER.value
                )

    def _reset_game(self) -> None:
        """Reset the game to initial state."""
        self.board.reset()
        self.current_player = Player.X_PLAYER.value
        self.game_over = False
        self.winner = None
        self.hovered_cell = None
        logger.info("Game reset")

    def update_game_state(
        self,
        board,
        current_player: int,
        game_over: bool = False,
        winner: str = None,
        player_x_name: str = "Player X",
        player_o_name: str = "Player O",
    ) -> None:
        """
        Update game state from external source.

        Args:
            board: Board instance
            current_player: Current player value
            game_over: Whether game is over
            winner: Winner name if game is over
            player_x_name: Name of Player X
            player_o_name: Name of Player O
        """
        self.board = board
        self.current_player = current_player
        self.game_over = game_over
        self.winner = winner
        self.player_x_name = player_x_name
        self.player_o_name = player_o_name

    def update(self) -> None:
        """Update game state."""
        pass

    def render(self, surface: pygame.Surface) -> None:
        """
        Render the game to a surface.

        Args:
            surface: Pygame surface to render to
        """
        logger.debug(f"GameUI.render START - surface size: {surface.get_size()}")
        logger.debug(
            f"GameUI.render - game_over: {self.game_over}, current_player: {self.current_player}"
        )

        self.screen = surface

        surface.fill(Colors.BACKGROUND)
        logger.debug("GameUI.render - surface filled with background")

        logger.debug("GameUI.render - calling _draw_back_button")
        self._draw_back_button(surface)

        logger.debug("GameUI.render - calling _draw_player_turn_top")
        self._draw_player_turn_top(surface)

        logger.debug("GameUI.render - calling _draw_board")
        self._draw_board(surface)

        logger.debug("GameUI.render - calling _draw_game_status")
        self._draw_game_status(surface)

        logger.debug("GameUI.render END")

    def _draw_player_turn_top(self, surface: pygame.Surface) -> None:
        """
        Draw player turn display at the top of the screen.

        Args:
            surface: Pygame surface to draw on
        """
        logger.debug(f"_draw_player_turn_top START - game_over: {self.game_over}")

        if self.game_over:
            logger.debug("_draw_player_turn_top - game is over, skipping turn display")
            return

        current_player_name = self._get_current_player_name()
        turn_text = f"{current_player_name}'s Turn"

        logger.debug(
            f"_draw_player_turn_top - turn_text: '{turn_text}', current_player: {self.current_player}"
        )

        turn_surface = self.fonts["title"].render(turn_text, True, Colors.TEXT)
        turn_rect = turn_surface.get_rect(center=(surface.get_width() // 2, 60))

        padding = 8
        border_rect = pygame.Rect(
            turn_rect.left - padding,
            turn_rect.top - padding,
            turn_rect.width + 2 * padding,
            turn_rect.height + 2 * padding,
        )

        pygame.draw.rect(
            surface, Colors.BOARD_LINE, border_rect, width=2, border_radius=8
        )

        logger.debug(
            f"_draw_player_turn_top - text position: {turn_rect.center}, text size: {turn_surface.get_size()}"
        )

        surface.blit(turn_surface, turn_rect)
        logger.debug("_draw_player_turn_top - text blitted to surface")

        logger.debug("_draw_player_turn_top END")

    def _draw_board(self, surface: pygame.Surface) -> None:
        """
        Draw the tic-tac-toe board.

        Args:
            surface: Pygame surface to draw on
        """
        logger.debug(
            f"_draw_board START - board position: ({self.board_x}, {self.board_y}), size: {self.board_width}x{self.board_height}"
        )

        for row in range(self.board_size):
            for col in range(self.board_size):
                cell_x = self.board_x + col * self.cell_size
                cell_y = self.board_y + row * self.cell_size
                cell_value = self.board.get_cell(row, col)

                if cell_value != Player.EMPTY.value:
                    pygame.draw.rect(
                        surface,
                        Colors.BACKGROUND,
                        (cell_x, cell_y, self.cell_size, self.cell_size),
                    )
                else:
                    pygame.draw.rect(
                        surface,
                        Colors.BOARD,
                        (cell_x, cell_y, self.cell_size, self.cell_size),
                    )

                pygame.draw.rect(
                    surface,
                    Colors.BOARD_LINE,
                    (cell_x, cell_y, self.cell_size, self.cell_size),
                    width=2,
                )

        logger.debug("_draw_board - cells and borders drawn")

        pieces_drawn = 0
        for row in range(self.board_size):
            for col in range(self.board_size):
                cell_value = self.board.get_cell(row, col)
                if cell_value != Player.EMPTY.value:
                    self._draw_piece(surface, row, col, cell_value)
                    pieces_drawn += 1

        logger.debug(f"_draw_board - {pieces_drawn} pieces drawn")

        self._draw_hover(surface)

        self._draw_win_line(surface)

        logger.debug("_draw_board END")

    def _draw_piece(
        self, surface: pygame.Surface, row: int, col: int, player: int
    ) -> None:
        """
        Draw a single piece (X or O).

        Args:
            surface: Pygame surface to draw on
            row: Row position
            col: Column position
            player: Player value (X_PLAYER or O_PLAYER)
        """
        logger.debug(f"_draw_piece START - row: {row}, col: {col}, player: {player}")

        center_x = self.board_x + col * self.cell_size + self.cell_size // 2
        center_y = self.board_y + row * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 3

        logger.debug(
            f"_draw_piece - center: ({center_x}, {center_y}), radius: {radius}"
        )

        match player:
            case Player.X_PLAYER.value:
                color = Colors.X_COLOR
                logger.debug(f"_draw_piece - drawing X with color: {color}")
                pygame.draw.line(
                    surface,
                    color,
                    (center_x - radius, center_y - radius),
                    (center_x + radius, center_y + radius),
                    5,
                )
                pygame.draw.line(
                    surface,
                    color,
                    (center_x + radius, center_y - radius),
                    (center_x - radius, center_y + radius),
                    5,
                )

            case Player.O_PLAYER.value:
                color = Colors.O_COLOR
                logger.debug(f"_draw_piece - drawing O with color: {color}")
                pygame.draw.circle(surface, color, (center_x, center_y), radius, 5)

        logger.debug("_draw_piece END")

    def _draw_hover(self, surface: pygame.Surface) -> None:
        """Draw hover effect on valid moves."""
        if self.hovered_cell and not self.game_over:
            row, col = self.hovered_cell
            cell_x = self.board_x + col * self.cell_size
            cell_y = self.board_y + row * self.cell_size

            pygame.draw.rect(
                surface,
                Colors.TEXT,
                (cell_x, cell_y, self.cell_size, self.cell_size),
                width=4,
                border_radius=4,
            )

    def _draw_win_line(self, surface: pygame.Surface) -> None:
        """Draw line through winning combination."""
        if self.winner is None:
            return

        win_line = self._get_win_line()
        if win_line:
            start_pos = (
                self.board_x + win_line[0][1] * self.cell_size + self.cell_size // 2,
                self.board_y + win_line[0][0] * self.cell_size + self.cell_size // 2,
            )
            end_pos = (
                self.board_x + win_line[2][1] * self.cell_size + self.cell_size // 2,
                self.board_y + win_line[2][0] * self.cell_size + self.cell_size // 2,
            )

            pygame.draw.line(surface, Colors.WIN_LINE, start_pos, end_pos, 8)

    def _get_win_line(self) -> list[tuple[int, int]] | None:
        """
        Get the winning line coordinates.

        Returns:
            List of (row, col) tuples for winning line, or None
        """
        for row in range(self.board_size):
            if (
                self.board.board[row, 0]
                == self.board.board[row, 1]
                == self.board.board[row, 2]
                != Player.EMPTY.value
            ):
                return [(row, 0), (row, 1), (row, 2)]

        for col in range(self.board_size):
            if (
                self.board.board[0, col]
                == self.board.board[1, col]
                == self.board.board[2, col]
                != Player.EMPTY.value
            ):
                return [(0, col), (1, col), (2, col)]

        if (
            self.board.board[0, 0]
            == self.board.board[1, 1]
            == self.board.board[2, 2]
            != Player.EMPTY.value
        ):
            return [(0, 0), (1, 1), (2, 2)]

        if (
            self.board.board[0, 2]
            == self.board.board[1, 1]
            == self.board.board[2, 0]
            != Player.EMPTY.value
        ):
            return [(0, 2), (1, 1), (2, 0)]

        return None

    def _draw_status(self, surface: pygame.Surface) -> None:
        """Draw game status text."""
        status_text = ""
        if self.game_over:
            if self.winner is None:
                status_text = "Draw! Press R to restart"
            else:
                winner_name = "X" if self.winner == Player.X_PLAYER.value else "O"
                status_text = f"{winner_name} wins! Press R to restart"
        else:
            current_name = "X" if self.current_player == Player.X_PLAYER.value else "O"
            status_text = f"{current_name}'s turn"

        board_height = self.board_size * self.cell_size
        line_y = board_height + 20
        text_y = board_height + 70

        pygame.draw.line(surface, Colors.BOARD, (0, line_y), (self.width, line_y), 2)
        text_surface = self.status_font.render(status_text, True, Colors.BOARD)
        text_rect = text_surface.get_rect(center=(self.width // 2, text_y))
        surface.blit(text_surface, text_rect)

    def run(self) -> None:
        """Main game loop."""
        logger.info("Starting game loop")

        while self.running:
            self.update()
            self.render()
            self.clock.tick(60)

        logger.info("Game loop ended")
        pygame.quit()

    def quit(self) -> None:
        """Quit the game."""
        self.running = False

    def get_board(self) -> Board:
        """
        Get the current board state.

        Returns:
            Board instance
        """
        return self.board

    def set_board(self, board: Board) -> None:
        """
        Set the board state.

        Args:
            board: Board instance to use
        """
        self.board = board
        logger.debug("Board state updated")

    def is_game_over(self) -> bool:
        """
        Check if game is over.

        Returns:
            True if game is over
        """
        return self.game_over

    def get_current_player(self) -> int:
        """
        Get current player.

        Returns:
            Current player value
        """
        return self.current_player

    def set_current_player(self, player: int) -> None:
        """
        Set current player.

        Args:
            player: Player value to set
        """
        self.current_player = player
        logger.debug(f"Current player set to: {player}")

    def on_resize(self, width: int, height: int) -> None:
        """
        Handle window resize.

        Args:
            width: New window width
            height: New window height
        """
        self.width = width
        self.height = height
        self.cell_size = min(width, height) // 3
        self.font = pygame.font.Font(None, self.cell_size // 2)
        self.status_font = pygame.font.Font(None, self.cell_size // 3)

        logger.info(f"GameUI resized to {width}x{height}")

    def is_back_button_clicked(self, mouse_x: int, mouse_y: int) -> bool:
        """
        Check if the back button was clicked.

        Args:
            mouse_x: Mouse X position
            mouse_y: Mouse Y position

        Returns:
            True if back button was clicked
        """
        return (
            self.back_button_x <= mouse_x <= self.back_button_x + self.back_button_width
            and self.back_button_y
            <= mouse_y
            <= self.back_button_y + self.back_button_height
        )

    def _draw_back_button(self, surface: pygame.Surface) -> None:
        """
        Draw the back button.

        Args:
            surface: Pygame surface to draw on
        """
        logger.debug(
            f"_draw_back_button START - position: ({self.back_button_x}, {self.back_button_y}), size: {self.back_button_width}x{self.back_button_height}"
        )

        pygame.draw.rect(
            surface,
            Colors.BUTTON_BACKGROUND,
            (
                self.back_button_x,
                self.back_button_y,
                self.back_button_width,
                self.back_button_height,
            ),
            border_radius=8,
        )
        logger.debug("_draw_back_button - background drawn")

        pygame.draw.rect(
            surface,
            Colors.BUTTON_BORDER,
            (
                self.back_button_x,
                self.back_button_y,
                self.back_button_width,
                self.back_button_height,
            ),
            width=2,
            border_radius=8,
        )
        logger.debug("_draw_back_button - border drawn")

        back_text = self.fonts["ui"].render("Back", True, Colors.TEXT)
        text_rect = back_text.get_rect(
            center=(
                self.back_button_x + self.back_button_width // 2,
                self.back_button_y + self.back_button_height // 2,
            )
        )
        surface.blit(back_text, text_rect)
        logger.debug(f"_draw_back_button - text drawn at position: {text_rect.center}")

        logger.debug("_draw_back_button END")

    def _draw_game_status(self, surface: pygame.Surface) -> None:
        """
        Draw game status (game over message only).

        Args:
            surface: Pygame surface to draw on
        """
        logger.debug(f"_draw_game_status START - game_over: {self.game_over}")

        if not self.game_over:
            logger.debug("_draw_game_status - game not over, skipping status display")
            return

        status_y = min(self.board_y + self.board_height + 20, surface.get_height() - 30)
        logger.debug(f"_draw_game_status - status_y: {status_y}")

        if self.winner:
            status_text = f"Game Over! {self.winner} wins!"
            color = Colors.TEXT
            logger.debug(f"_draw_game_status - winner status: '{status_text}'")
        else:
            status_text = "Game Over! It's a draw!"
            color = Colors.TEXT
            logger.debug(f"_draw_game_status - draw status: '{status_text}'")

        status_surface = self.fonts["ui"].render(status_text, True, color)
        status_rect = status_surface.get_rect(
            center=(surface.get_width() // 2, status_y)
        )
        surface.blit(status_surface, status_rect)
        logger.debug(
            f"_draw_game_status - status text drawn at position: {status_rect.center}"
        )

        logger.debug("_draw_game_status END")

    def _get_current_player_name(self) -> str:
        """
        Get the name of the current player.

        Returns:
            Current player name
        """
        match self.current_player:
            case Player.X_PLAYER.value:
                return self.player_x_name
            case Player.O_PLAYER.value:
                return self.player_o_name
            case _:
                return "Unknown"
