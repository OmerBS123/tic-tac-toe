"""
Match history screen logic for displaying recent games.
"""

from datetime import datetime
from typing import Any, NamedTuple

from ..models import MatchRecord, HistoryRow, HistoryData
from ...infra.storage import Storage
from ...logger import get_logger

logger = get_logger()


class HistoryService:
    """Manager for match history functionality."""

    def __init__(self, storage: Storage) -> None:
        """
        Initialize history manager.

        Args:
            storage: Storage instance for database operations
        """
        self.storage = storage
        logger.debug("HistoryManager initialized")

    def get_recent_matches(self, limit: int = 50, filter_mode: str | None = None) -> list[MatchRecord]:
        """
        Get recent matches with optional filtering.

        Args:
            limit: Maximum number of matches to return
            filter_mode: Filter by mode ('pvp', 'easy', 'medium', 'hard') or None for all

        Returns:
            List of MatchRecord sorted by played_at (desc)
        """
        matches = self.storage.recent_matches(limit, filter_mode)
        logger.info(f"Retrieved {len(matches)} recent matches (filter: {filter_mode})")
        return matches

    def get_history_data(self, limit: int = 50, filter_mode: str | None = None) -> HistoryData:
        """
        Get match history data structured for pygame rendering.

        Args:
            limit: Maximum number of matches to return
            filter_mode: Filter by mode ('pvp', 'easy', 'medium', 'hard') or None for all

        Returns:
            HistoryData with structured data for pygame
        """
        matches = self.storage.recent_matches(limit, filter_mode)

        rows = []
        for match in matches:
            played_at = datetime.fromisoformat(match.played_at.replace("Z", "+00:00"))
            date_str = played_at.strftime("%Y-%m-%d")
            time_str = played_at.strftime("%H:%M")

            # Convert result character to player name
            if match.result == "X":
                result_display = match.player_x_name
            elif match.result == "O":
                result_display = match.player_o_name
            else:  # Draw
                result_display = "Draw"

            # Use dash instead of N/A for AI level
            ai_level_display = match.ai_level or "-"

            row = HistoryRow(
                played_at=played_at,
                date_str=date_str,
                time_str=time_str,
                player_x_name=match.player_x_name,
                player_o_name=match.player_o_name,
                result=result_display,  # Use player name instead of character
                mode=match.mode.upper(),
                ai_level=match.ai_level,
                ai_level_display=ai_level_display,
            )
            rows.append(row)

        headers = ["Date", "Time", "Player X", "vs", "Player O", "Result", "Mode", "AI Level"]

        filter_display = None
        if filter_mode == "pvp":
            filter_display = "PvP Only"
        elif filter_mode in ("easy", "medium", "hard"):
            filter_display = f"AI-{filter_mode.title()} Only"

        return HistoryData(title="MATCH HISTORY", headers=headers, rows=rows, total_matches=len(rows), filter_applied=filter_display)

    def get_matches_for_player(self, player_name: str, limit: int = 20) -> list[MatchRecord]:
        """
        Get matches for a specific player.

        Args:
            player_name: Name of the player
            limit: Maximum number of matches to return

        Returns:
            List of MatchRecord for the player
        """
        all_matches = self.get_recent_matches(limit * 2)
        player_matches = [match for match in all_matches if match.player_x_name.lower() == player_name.lower() or match.player_o_name.lower() == player_name.lower()]

        logger.debug(f"Found {len(player_matches)} matches for player: {player_name}")
        return player_matches[:limit]

    def get_player_stats(self, player_name: str) -> dict[str, Any]:
        """
        Get statistics for a specific player.

        Args:
            player_name: Name of the player

        Returns:
            Dictionary with player statistics
        """
        matches = self.get_matches_for_player(player_name, 1000)

        if not matches:
            return {"name": player_name, "total_matches": 0, "wins": 0, "losses": 0, "draws": 0, "win_percentage": 0.0, "pvp_matches": 0, "pvai_matches": 0}

        wins = 0
        losses = 0
        draws = 0
        pvp_matches = 0
        pvai_matches = 0

        for match in matches:
            if match.mode == "pvp":
                pvp_matches += 1
            else:
                pvai_matches += 1

            if match.result == "Draw":
                draws += 1
            elif (match.result == "X" and match.player_x_name.lower() == player_name.lower()) or (match.result == "O" and match.player_o_name.lower() == player_name.lower()):
                wins += 1
            else:
                losses += 1

        total_matches = len(matches)
        win_percentage = (wins / total_matches * 100) if total_matches > 0 else 0.0

        return {"name": player_name, "total_matches": total_matches, "wins": wins, "losses": losses, "draws": draws, "win_percentage": round(win_percentage, 1), "pvp_matches": pvp_matches, "pvai_matches": pvai_matches}

    @staticmethod
    def get_filter_options() -> list[str]:
        """
        Get available filter options for match history.

        Returns:
            List of filter option strings
        """
        return ["All", "PvP", "AI-Easy", "AI-Medium", "AI-Hard"]

    @staticmethod
    def apply_filter(filter_option: str) -> str | None:
        """
        Convert filter option to storage filter mode.

        Args:
            filter_option: User-friendly filter option

        Returns:
            Storage filter mode or None for "All"
        """
        filter_mapping = {"All": None, "PvP": "pvp", "AI-Easy": "easy", "AI-Medium": "medium", "AI-Hard": "hard"}

        return filter_mapping.get(filter_option, None)
