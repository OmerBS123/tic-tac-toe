"""
Leaderboard screen logic for displaying player statistics.
"""

from typing import Any, NamedTuple

from ..storage import Storage, PlayerStats
from ..logger import get_logger

logger = get_logger()


class LeaderboardRow(NamedTuple):
    """Single leaderboard row data for pygame rendering."""

    rank: int
    medal: str
    name: str
    total_wins: int
    pvp_wins: int
    ai_easy_wins: int
    ai_medium_wins: int
    ai_hard_wins: int
    win_percentage: float
    total_games: int


class LeaderboardData(NamedTuple):
    """Complete leaderboard data for pygame rendering."""

    title: str
    headers: list[str]
    rows: list[LeaderboardRow]
    total_players: int


class LeaderboardManager:
    """Manager for leaderboard functionality."""

    def __init__(self, storage: Storage) -> None:
        """
        Initialize leaderboard manager.

        Args:
            storage: Storage instance for database operations
        """
        self.storage = storage
        logger.debug("LeaderboardManager initialized")

    def get_leaderboard(self, limit: int = 50) -> list[PlayerStats]:
        """
        Get leaderboard data.

        Args:
            limit: Maximum number of players to return

        Returns:
            List of PlayerStats sorted by total wins
        """
        leaderboard = self.storage.leaderboard(limit)
        logger.info(f"Retrieved leaderboard with {len(leaderboard)} players")
        return leaderboard

    def get_leaderboard_data(self, limit: int = 50) -> LeaderboardData:
        """
        Get leaderboard data structured for pygame rendering.

        Args:
            limit: Maximum number of players to return

        Returns:
            LeaderboardData with structured data for pygame
        """
        leaderboard = self.storage.leaderboard(limit)

        medals = ["🥇", "🥈", "🥉"]
        rows = []

        for i, player in enumerate(leaderboard):
            rank = i + 1
            medal = medals[i] if i < 3 else ""

            row = LeaderboardRow(
                rank=rank,
                medal=medal,
                name=player.name,
                total_wins=player.total_wins,
                pvp_wins=player.pvp_wins,
                ai_easy_wins=player.ai_easy_wins,
                ai_medium_wins=player.ai_medium_wins,
                ai_hard_wins=player.ai_hard_wins,
                win_percentage=player.win_percentage,
                total_games=player.total_games,
            )
            rows.append(row)

        headers = ["Rank", "Player", "Total", "PvP", "AI-E", "AI-M", "AI-H", "Win%", "Games"]

        return LeaderboardData(title="LEADERBOARD", headers=headers, rows=rows, total_players=len(rows))

    def get_player_rank(self, player_name: str) -> int | None:
        """
        Get the rank of a specific player.

        Args:
            player_name: Name of the player

        Returns:
            Rank (1-based) or None if player not found
        """
        leaderboard = self.get_leaderboard()

        for i, player in enumerate(leaderboard):
            if player.name.lower() == player_name.lower():
                return i + 1

        return None

    def get_top_players(self, count: int = 3) -> list[PlayerStats]:
        """
        Get top N players.

        Args:
            count: Number of top players to return

        Returns:
            List of top PlayerStats
        """
        leaderboard = self.get_leaderboard(count)
        logger.debug(f"Retrieved top {len(leaderboard)} players")
        return leaderboard
