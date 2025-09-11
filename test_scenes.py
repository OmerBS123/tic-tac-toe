"""
Test script for leaderboard and history scenes.
"""

import pygame

from src.tictactoe.screens.history_scene import MatchHistoryScene
from src.tictactoe.screens.leaderboard_scene import LeaderboardScene
from src.tictactoe.storage import Storage


def add_sample_data(storage: Storage) -> None:
    """Add some sample data for testing."""
    # Add sample matches
    storage.record_match("Alice", "Bob", "X", "pvp")
    storage.record_match("Alice", "Bob", "O", "pvp")
    storage.record_match("Charlie", "AI", "X", "pvai", "easy")
    storage.record_match("Charlie", "AI", "Draw", "pvai", "medium")
    storage.record_match("Alice", "AI", "X", "pvai", "hard")
    storage.record_match("Bob", "Charlie", "O", "pvp")
    storage.record_match("Alice", "Charlie", "X", "pvp")
    storage.record_match("Bob", "AI", "O", "pvai", "easy")
    print("Sample data added!")


def test_leaderboard_scene() -> None:
    """Test the leaderboard scene."""
    pygame.init()

    # Use dynamic window sizing
    from src.tictactoe.layout import get_initial_window_size

    width, height = get_initial_window_size()

    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("Leaderboard Test")

    storage = Storage()
    add_sample_data(storage)

    scene = LeaderboardScene(storage, width, height)
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            result = scene.handle_event(event)
            if result == "menu":
                running = False

        scene.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def test_history_scene() -> None:
    """Test the history scene."""
    pygame.init()

    # Use dynamic window sizing
    from src.tictactoe.layout import get_initial_window_size

    width, height = get_initial_window_size()

    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("History Test")

    storage = Storage()
    add_sample_data(storage)

    scene = MatchHistoryScene(storage, width, height)
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            result = scene.handle_event(event)
            if result == "menu":
                running = False

        scene.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    print("Testing Leaderboard Scene...")
    test_leaderboard_scene()

    print("\nTesting History Scene...")
    test_history_scene()

    print("Tests completed!")
