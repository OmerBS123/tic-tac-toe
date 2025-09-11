"""
Game UI implementation using pygame for the tic-tac-toe board.
"""

from collections.abc import Callable

import pygame

from .board import Board
from .consts.board_consts import Player
from .logger import get_logger

logger = get_logger()


class GameUI:
    """Game UI manager for pygame-based tic-tac-toe board."""

    def __init__(self, width: int = 600, height: int = 700) -> None:
        """
        Initialize the game UI.

        Args:
            width: Window width in pixels
            height: Window height in pixels
        """
        self.width = width
        self.height = height
        self.board_size = 3
        self.cell_size = min(width, height) // 3

        # Colors
        self.BACKGROUND_COLOR = (255, 255, 255)  # White
        self.BOARD_COLOR = (0, 0, 0)  # Black
        self.X_COLOR = (255, 0, 0)  # Red
        self.O_COLOR = (0, 0, 255)  # Blue
        self.HOVER_COLOR = (200, 200, 200)  # Light gray
        self.WIN_LINE_COLOR = (0, 255, 0)  # Green

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Tic Tac Toe")
        self.clock = pygame.time.Clock()

        # Font for X and O
        self.font = pygame.font.Font(None, self.cell_size // 2)

        # Game state
        self.board = Board()
        self.running = True
        self.current_player = Player.X_PLAYER.value
        self.game_over = False
        self.winner = None
        self.hovered_cell: tuple[int, int] | None = None

        # Callbacks
        self.on_move_callback: Callable[[tuple[int, int], int], None] | None = None
        self.on_game_over_callback: Callable[[int | None], None] | None = None

        logger.info("GameUI initialized")

    def set_move_callback(self, callback: Callable[[tuple[int, int], int], None]) -> None:
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

    def handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                logger.info("Game quit requested")

            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_mouse_click(event.pos)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self._reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def _handle_mouse_motion(self, pos: tuple[int, int]) -> None:
        """
        Handle mouse motion for hover effects.

        Args:
            pos: Mouse position (x, y)
        """
        if self.game_over:
            self.hovered_cell = None
            return

        x, y = pos
        col = x // self.cell_size
        row = y // self.cell_size

        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            if self.board.is_valid_move((row, col)):
                self.hovered_cell = (row, col)
            else:
                self.hovered_cell = None
        else:
            self.hovered_cell = None

    def _handle_mouse_click(self, pos: tuple[int, int]) -> None:
        """
        Handle mouse click for making moves.

        Args:
            pos: Mouse position (x, y)
        """
        if self.game_over:
            return

        x, y = pos
        col = x // self.cell_size
        row = y // self.cell_size

        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            if self.board.is_valid_move((row, col)):
                self._make_move((row, col))

    def _make_move(self, move: tuple[int, int]) -> None:
        """
        Make a move on the board.

        Args:
            move: (row, col) position to play
        """
        if self.board.apply(move, self.current_player):
            logger.info(f"Move made: {self.current_player} at {move}")

            # Call move callback if set
            if self.on_move_callback:
                self.on_move_callback(move, self.current_player)

            # Check for game over
            if self.board.terminal():
                self.game_over = True
                self.winner = self.board.check_winner()
                logger.info(f"Game over. Winner: {self.winner}")

                # Call game over callback if set
                if self.on_game_over_callback:
                    self.on_game_over_callback(self.winner)
            else:
                # Switch players
                self.current_player = Player.O_PLAYER.value if self.current_player == Player.X_PLAYER.value else Player.X_PLAYER.value

    def _reset_game(self) -> None:
        """Reset the game to initial state."""
        self.board.reset()
        self.current_player = Player.X_PLAYER.value
        self.game_over = False
        self.winner = None
        self.hovered_cell = None
        logger.info("Game reset")

    def update(self) -> None:
        """Update game state."""
        self.handle_events()

    def render(self) -> None:
        """Render the game to the screen."""
        # Clear screen
        self.screen.fill(self.BACKGROUND_COLOR)

        # Draw board
        self._draw_board()

        # Draw X's and O's
        self._draw_pieces()

        # Draw hover effect
        self._draw_hover()

        # Draw win line if game is over
        if self.game_over and self.winner is not None:
            self._draw_win_line()

        # Draw game status
        self._draw_status()

        # Update display
        pygame.display.flip()

    def _draw_board(self) -> None:
        """Draw the game board grid."""
        board_height = self.board_size * self.cell_size
        line_y = board_height + 20

        # Draw vertical lines (extend to separation line)
        for i in range(1, self.board_size):
            x = i * self.cell_size
            pygame.draw.line(self.screen, self.BOARD_COLOR, (x, 0), (x, line_y), 3)

        # Draw horizontal lines (only within the board area)
        for i in range(1, self.board_size):
            y = i * self.cell_size
            pygame.draw.line(self.screen, self.BOARD_COLOR, (0, y), (self.width, y), 3)

    def _draw_pieces(self) -> None:
        """Draw X's and O's on the board."""
        for row in range(self.board_size):
            for col in range(self.board_size):
                player = self.board.board[row, col]
                if player != Player.EMPTY.value:
                    self._draw_piece(row, col, player)

    def _draw_piece(self, row: int, col: int, player: int) -> None:
        """
        Draw a single piece (X or O).

        Args:
            row: Row position
            col: Column position
            player: Player value (X_PLAYER or O_PLAYER)
        """
        center_x = col * self.cell_size + self.cell_size // 2
        center_y = row * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 3

        if player == Player.X_PLAYER.value:
            # Draw X
            color = self.X_COLOR
            # Draw two diagonal lines
            pygame.draw.line(self.screen, color, (center_x - radius, center_y - radius), (center_x + radius, center_y + radius), 5)
            pygame.draw.line(self.screen, color, (center_x + radius, center_y - radius), (center_x - radius, center_y + radius), 5)

        elif player == Player.O_PLAYER.value:
            # Draw O
            color = self.O_COLOR
            pygame.draw.circle(self.screen, color, (center_x, center_y), radius, 5)

    def _draw_hover(self) -> None:
        """Draw hover effect on valid moves."""
        if self.hovered_cell and not self.game_over:
            row, col = self.hovered_cell
            x = col * self.cell_size
            y = row * self.cell_size

            # Draw semi-transparent overlay
            hover_surface = pygame.Surface((self.cell_size, self.cell_size))
            hover_surface.set_alpha(50)
            hover_surface.fill(self.HOVER_COLOR)
            self.screen.blit(hover_surface, (x, y))

    def _draw_win_line(self) -> None:
        """Draw line through winning combination."""
        if self.winner is None:
            return

        # Find winning line
        win_line = self._get_win_line()
        if win_line:
            start_pos = (win_line[0][1] * self.cell_size + self.cell_size // 2, win_line[0][0] * self.cell_size + self.cell_size // 2)
            end_pos = (win_line[2][1] * self.cell_size + self.cell_size // 2, win_line[2][0] * self.cell_size + self.cell_size // 2)

            pygame.draw.line(self.screen, self.WIN_LINE_COLOR, start_pos, end_pos, 8)

    def _get_win_line(self) -> list[tuple[int, int]] | None:
        """
        Get the winning line coordinates.

        Returns:
            List of (row, col) tuples for winning line, or None
        """
        # Check rows
        for row in range(self.board_size):
            if self.board.board[row, 0] == self.board.board[row, 1] == self.board.board[row, 2] != Player.EMPTY.value:
                return [(row, 0), (row, 1), (row, 2)]

        # Check columns
        for col in range(self.board_size):
            if self.board.board[0, col] == self.board.board[1, col] == self.board.board[2, col] != Player.EMPTY.value:
                return [(0, col), (1, col), (2, col)]

        # Check main diagonal
        if self.board.board[0, 0] == self.board.board[1, 1] == self.board.board[2, 2] != Player.EMPTY.value:
            return [(0, 0), (1, 1), (2, 2)]

        # Check anti-diagonal
        if self.board.board[0, 2] == self.board.board[1, 1] == self.board.board[2, 0] != Player.EMPTY.value:
            return [(0, 2), (1, 1), (2, 0)]

        return None

    def _draw_status(self) -> None:
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

        # Position text below the board area
        board_height = self.board_size * self.cell_size
        line_y = board_height + 20
        text_y = board_height + 70  # Moved further down for more breathing room

        pygame.draw.line(self.screen, self.BOARD_COLOR, (0, line_y), (self.width, line_y), 2)

        # Render text
        text_surface = self.font.render(status_text, True, self.BOARD_COLOR)
        text_rect = text_surface.get_rect(center=(self.width // 2, text_y))
        self.screen.blit(text_surface, text_rect)

    def run(self) -> None:
        """Main game loop."""
        logger.info("Starting game loop")

        while self.running:
            self.update()
            self.render()
            self.clock.tick(60)  # 60 FPS

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
