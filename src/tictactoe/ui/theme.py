"""
UI theme constants for tic-tac-toe game.
"""


# Color palette
class Colors:
    """Color constants for the game UI."""

    # Background colors
    BACKGROUND = (255, 255, 255)  # White
    DARK_BACKGROUND = (18, 18, 18)  # Dark gray

    # Board colors
    BOARD = (0, 0, 0)  # Black
    BOARD_LINE = (100, 100, 100)  # Gray

    # Player colors
    X_COLOR = (255, 0, 0)  # Red
    O_COLOR = (0, 0, 255)  # Blue

    # Interactive colors
    HOVER = (200, 200, 200)  # Light gray
    HOVER_DARK = (60, 60, 70)  # Dark gray

    # Status colors
    WIN_LINE = (0, 255, 0)  # Green
    WIN_TEXT = (0, 150, 0)  # Dark green
    DRAW_TEXT = (150, 150, 150)  # Gray

    # UI colors
    TEXT = (0, 0, 0)  # Black
    TEXT_DARK = (0, 0, 0)  # Black
    TITLE = (100, 200, 255)  # Light blue
    ACCENT = (100, 200, 255)  # Light blue

    # Button colors
    BUTTON_PRIMARY = (0, 150, 0)  # Green
    BUTTON_PRIMARY_HOVER = (0, 200, 0)  # Light green
    BUTTON_SECONDARY = (0, 100, 200)  # Blue
    BUTTON_SECONDARY_HOVER = (0, 150, 255)  # Light blue
    BUTTON_WARNING = (200, 50, 50)  # Red
    BUTTON_WARNING_HOVER = (255, 100, 100)  # Light red
    BUTTON_NEUTRAL = (100, 100, 100)  # Gray
    BUTTON_NEUTRAL_HOVER = (150, 150, 150)  # Light gray

    # Additional button colors for widgets
    BUTTON_BACKGROUND = (100, 100, 100)  # Gray background
    BUTTON_BORDER = (150, 150, 150)  # Light gray border

    # Input field colors
    INPUT_BACKGROUND = (60, 60, 70)  # Dark gray
    INPUT_BORDER = (100, 200, 255)  # Light blue
    INPUT_ACTIVE = (100, 200, 255)  # Light blue


# Font sizes
class FontSizes:
    """Font size constants."""

    TITLE = 54
    LARGE = 42
    MEDIUM = 36
    SMALL = 24
    TINY = 18


# Layout constants
class Layout:
    """Layout and spacing constants."""

    # Button dimensions
    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 50
    BUTTON_SPACING = 20

    # Input field dimensions
    INPUT_WIDTH = 300
    INPUT_HEIGHT = 40
    INPUT_SPACING = 60

    # Margins and padding
    SAFE_MARGIN = 50
    CONTENT_PADDING = 20
    SECTION_SPACING = 40
