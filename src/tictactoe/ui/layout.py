"""
Centralized layout calculations for responsive UI.

This module provides the single source of truth for all responsive geometry,
ensuring consistent layout across all scenes regardless of window size.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

import pygame


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max bounds."""
    return max(min_val, min(max_val, value))


@dataclass
class Layout:
    """Layout configuration for a given window size."""

    # Window dimensions
    width: int
    height: int

    # Safe margins (4% of smallest dimension)
    safe_margin: int

    # Header area
    header_height: int

    # Grid positioning (centered square for 3x3 board)
    grid_x: int
    grid_y: int
    grid_size: int
    cell_size: int

    # Font sizes (scaled with window size)
    font_title: int
    font_ui: int
    font_mark: int
    font_small: int

    # Menu sizing
    menu_width: int
    menu_height: int


def compute_layout(width: int, height: int) -> Layout:
    """
    Compute responsive layout for given window dimensions.

    Args:
        width: Window width in pixels
        height: Window height in pixels

    Returns:
        Layout object with all calculated dimensions
    """
    # Safe margin: 4% of smallest dimension
    safe_margin = int(min(width, height) * 0.04)

    # Header height: 12% of height, clamped between 80-180px
    header_height = int(clamp(height * 0.12, 80, 180))

    # Grid size: largest square that fits with safe margins
    available_width = width - 2 * safe_margin
    available_height = height - header_height - 2 * safe_margin
    grid_size = min(available_width, available_height)

    # Ensure grid size is multiple of 3 for exact cell division
    grid_size -= grid_size % 3
    cell_size = grid_size // 3

    # Center the grid
    grid_x = (width - grid_size) // 2
    grid_y = header_height + ((height - header_height - grid_size) // 2)

    # Font sizes scale with minimum dimension
    base_size = min(width, height)
    font_title = int(clamp(base_size * 0.050, 28, 64))
    font_ui = int(clamp(base_size * 0.028, 18, 36))
    font_mark = int(clamp(cell_size * 0.60, 28, 120))
    font_small = int(clamp(base_size * 0.020, 14, 24))

    # Menu sizing (slightly smaller than window for padding)
    menu_width = int(width * 0.9)
    menu_height = int(height * 0.9)

    return Layout(
        width=width,
        height=height,
        safe_margin=safe_margin,
        header_height=header_height,
        grid_x=grid_x,
        grid_y=grid_y,
        grid_size=grid_size,
        cell_size=cell_size,
        font_title=font_title,
        font_ui=font_ui,
        font_mark=font_mark,
        font_small=font_small,
        menu_width=menu_width,
        menu_height=menu_height,
    )


def get_initial_window_size() -> tuple[int, int]:
    """
    Get initial window size based on desktop percentage.

    Returns:
        Tuple of (width, height) for initial window
    """
    try:
        # Try to restore last window size
        window_file = Path("window.json")
        if window_file.exists():
            with open(window_file) as f:
                data = json.load(f)
                width = int(clamp(data["w"], 900, 1600))
                height = int(clamp(data["h"], 900, 1600))
                return width, height
    except Exception:
        pass

    # Fallback: 80% of desktop size
    try:
        pygame.init()
        desktop_info = pygame.display.Info()
        width = int(clamp(desktop_info.current_w * 0.8, 900, 1600))
        height = int(clamp(desktop_info.current_h * 0.8, 900, 1600))
        return width, height
    except Exception:
        # Ultimate fallback
        return 1000, 1100


def save_window_size(width: int, height: int) -> None:
    """
    Save current window size for next launch.

    Args:
        width: Window width
        height: Window height
    """
    try:
        with open("window.json", "w") as f:
            f: TextIO
            json.dump({"w": width, "h": height}, f)
    except Exception:
        pass  # Ignore save errors


def make_fonts(layout: Layout) -> dict[str, pygame.font.Font]:
    """
    Create font objects based on layout configuration.

    Args:
        layout: Layout object with font sizes

    Returns:
        Dictionary of font objects
    """
    return {
        "title": pygame.font.Font(None, layout.font_title),
        "ui": pygame.font.Font(None, layout.font_ui),
        "mark": pygame.font.Font(None, layout.font_mark),
        "small": pygame.font.Font(None, layout.font_small),
    }


def get_cell_from_mouse(mouse_x: int, mouse_y: int, layout: Layout) -> tuple[int, int]:
    """
    Convert mouse coordinates to grid cell coordinates.

    Args:
        mouse_x: Mouse X position
        mouse_y: Mouse Y position
        layout: Layout object with grid positioning

    Returns:
        Tuple of (col, row) or (-1, -1) if outside grid
    """
    col = (mouse_x - layout.grid_x) // layout.cell_size
    row = (mouse_y - layout.grid_y) // layout.cell_size

    if 0 <= col < 3 and 0 <= row < 3:
        return col, row
    else:
        return -1, -1


def get_cell_rect(col: int, row: int, layout: Layout) -> pygame.Rect:
    """
    Get the rectangle for a specific grid cell.

    Args:
        col: Column (0-2)
        row: Row (0-2)
        layout: Layout object with grid positioning

    Returns:
        pygame.Rect for the cell
    """
    x = layout.grid_x + col * layout.cell_size
    y = layout.grid_y + row * layout.cell_size
    return pygame.Rect(x, y, layout.cell_size, layout.cell_size)
