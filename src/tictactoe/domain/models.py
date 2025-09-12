"""
Domain models for tic-tac-toe game.
"""

from datetime import datetime
from typing import NamedTuple


class PlayerStats(NamedTuple):
    """Player statistics for leaderboard display."""

    name: str
    total_wins: int
    pvp_wins: int
    ai_easy_wins: int
    ai_medium_wins: int
    ai_hard_wins: int
    win_percentage: float
    total_games: int


class MatchRecord(NamedTuple):
    """Match record for history display."""

    played_at: str
    player_x_name: str
    player_o_name: str
    result: str
    mode: str
    ai_level: str | None


class LeaderboardRow(NamedTuple):
    """Single row in leaderboard display."""

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
    """Complete leaderboard data structure."""

    title: str
    headers: list[str]
    rows: list[LeaderboardRow]
    total_players: int


class HistoryRow(NamedTuple):
    """Single row in match history display."""

    played_at: datetime
    date_str: str
    time_str: str
    player_x_name: str
    player_o_name: str
    result: str
    mode: str
    ai_level: str | None
    ai_level_display: str


class HistoryData(NamedTuple):
    """Complete match history data structure."""

    title: str
    headers: list[str]
    rows: list[HistoryRow]
    total_matches: int
    filter_applied: str | None


class GameSettings(NamedTuple):
    """Game configuration settings."""

    player_x_name: str
    player_o_name: str
    ai_difficulty: str
    game_mode: str


class GameResult(NamedTuple):
    """Result of a completed game."""

    winner: int | None
    player_x_name: str
    player_o_name: str
    mode: str
    ai_level: str | None
    played_at: datetime
