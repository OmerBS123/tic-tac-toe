"""
Scene transition constants for tic-tac-toe game.

This module defines all the possible scene transition strings used throughout
the application, ensuring consistency and preventing typos.
"""


# Scene transition constants
class SceneTransition:
    """Constants for scene transitions returned by handle_event methods."""

    # Main menu transitions
    MENU = "menu"
    GAME = "game"
    QUIT = "quit"

    # Data management transitions
    RESET_CONFIRMED = "reset_confirmed"

    # Navigation transitions
    LEADERBOARD = "leaderboard"
    HISTORY = "history"
    RESET = "reset"
