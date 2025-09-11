"""
Window management utilities for persistent window size preferences.

This module handles saving and loading window dimensions to provide
a consistent user experience across application sessions.
"""

import json
from contextlib import suppress
from pathlib import Path
from typing import TextIO

import pygame

from ..ui.layout import clamp


def get_initial_window_size() -> tuple[int, int]:
    """
    Get initial window size based on saved preferences or desktop percentage.

    Returns:
        Tuple of (width, height) for initial window
    """
    with suppress(Exception):
        window_file = Path(__file__).parent / "window.json"
        if window_file.exists():
            with open(window_file) as f:
                data = json.load(f)
                width = int(clamp(data["w"], 900, 1600))
                height = int(clamp(data["h"], 900, 1600))
                return width, height

    with suppress(Exception):
        pygame.init()
        desktop_info = pygame.display.Info()
        width = int(clamp(desktop_info.current_w * 0.8, 900, 1600))
        height = int(clamp(desktop_info.current_h * 0.8, 900, 1600))
        return width, height

    # Ultimate fallback
    return 1000, 1100


def save_window_size(width: int, height: int) -> None:
    """
    Save current window size for next launch.

    Args:
        width: Window width
        height: Window height
    """
    with suppress(Exception):
        window_file = Path(__file__).parent / "window.json"
        with open(window_file, "w") as f:
            f: TextIO
            json.dump({"w": width, "h": height}, f)
