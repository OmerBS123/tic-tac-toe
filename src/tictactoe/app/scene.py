"""
Base Scene class for all game scenes.

This provides a common interface for scene management and dynamic resizing.
"""

from abc import ABC, abstractmethod

import pygame

from ..ui.layout import Layout


class Scene(ABC):
    """Base class for all game scenes."""

    def __init__(self, width: int, height: int):
        """
        Initialize the scene.

        Args:
            width: Initial window width
            height: Initial window height
        """
        self.width = width
        self.height = height
        self.layout: Layout | None = None
        self._last_size = (width, height)

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> str | None:
        """
        Handle pygame events.

        Args:
            event: Pygame event

        Returns:
            Optional string indicating scene transition (e.g., "menu", "game")
        """
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the scene.

        Args:
            surface: Pygame surface to draw on
        """
        pass

    def on_resize(self, width: int, height: int) -> None:
        """
        Handle window resize.

        Args:
            width: New window width
            height: New window height
        """
        if (width, height) != self._last_size:
            self._last_size = (width, height)
            self.width = width
            self.height = height
            self._on_resize_impl(width, height)

    @abstractmethod
    def _on_resize_impl(self, width: int, height: int) -> None:
        """
        Implementation-specific resize handling.

        Override this method in subclasses to handle resize events.

        Args:
            width: New window width
            height: New window height
        """
        pass
