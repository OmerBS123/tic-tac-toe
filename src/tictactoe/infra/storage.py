"""
SQLite storage for tic-tac-toe leaderboard and match history.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from ..domain.models import PlayerStats, MatchRecord
from ..logger import get_logger

logger = get_logger()


class Storage:
    """SQLite storage manager for tic-tac-toe data."""

    def __init__(self, db_path: str = "tictactoe.db") -> None:
        """
        Initialize storage with database path.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._init_schema()
        logger.info(f"Storage initialized with database: {self.db_path}")

    def _init_schema(self) -> None:
        """Initialize database schema with players and matches tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    player_x_id INTEGER NOT NULL,
                    player_o_id INTEGER NOT NULL,
                    result TEXT NOT NULL CHECK (result IN ('X', 'O', 'Draw')),
                    mode TEXT NOT NULL CHECK (mode IN ('pvp', 'pvai')),
                    ai_level TEXT CHECK (ai_level IN ('easy', 'medium', 'hard') OR ai_level IS NULL),
                    FOREIGN KEY (player_x_id) REFERENCES players (id),
                    FOREIGN KEY (player_o_id) REFERENCES players (id)
                )
            """
            )

            conn.commit()
            logger.debug("Database schema initialized")

    def get_or_create_player_id(self, name: str) -> int:
        """
        Get existing player ID or create new player.

        Args:
            name: Player name (will be normalized)

        Returns:
            Player ID
        """
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Player name cannot be empty")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM players WHERE LOWER(name) = LOWER(?)", (normalized_name,))
            result = cursor.fetchone()

            if result:
                player_id = result[0]
                logger.debug(f"Found existing player: {normalized_name} (ID: {player_id})")
                return player_id

            cursor.execute("INSERT INTO players (name) VALUES (?)", (normalized_name,))
            player_id = cursor.lastrowid
            conn.commit()

            logger.info(f"Created new player: {normalized_name} (ID: {player_id})")
            return player_id

    def record_match(self, player_x: str, player_o: str, result: str, mode: str, ai_level: str | None = None) -> None:
        """
        Record a completed match.

        Args:
            player_x: Name of player X
            player_o: Name of player O (or "AI" for AI matches)
            result: 'X', 'O', or 'Draw'
            mode: 'pvp' or 'pvai'
            ai_level: 'easy', 'medium', 'hard', or None for PvP
        """
        if result not in ("X", "O", "Draw"):
            raise ValueError(f"Invalid result: {result}")

        if mode not in ("pvp", "pvai"):
            raise ValueError(f"Invalid mode: {mode}")

        if mode == "pvai" and ai_level not in ("easy", "medium", "hard"):
            raise ValueError(f"Invalid AI level for PvAI mode: {ai_level}")

        if mode == "pvp" and ai_level is not None:
            raise ValueError("AI level should be None for PvP mode")

        player_x_id = self.get_or_create_player_id(player_x)
        player_o_id = self.get_or_create_player_id(player_o)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO matches (player_x_id, player_o_id, result, mode, ai_level)
                VALUES (?, ?, ?, ?, ?)
            """,
                (player_x_id, player_o_id, result, mode, ai_level),
            )

            conn.commit()

            logger.info(f"Recorded match: {player_x} vs {player_o} → {result} ({mode}/{ai_level or 'N/A'})")

    def leaderboard(self, limit: int = 50) -> list[PlayerStats]:
        """
        Get leaderboard data sorted by total wins.

        Args:
            limit: Maximum number of players to return

        Returns:
            List of PlayerStats sorted by total wins (desc), then tie-breakers
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = """
                WITH player_wins AS (
                    SELECT 
                        p.id,
                        p.name,
                        COUNT(CASE 
                            WHEN (m.result = 'X' AND m.player_x_id = p.id) OR 
                                 (m.result = 'O' AND m.player_o_id = p.id) 
                            THEN 1 
                        END) as total_wins,
                        COUNT(CASE 
                            WHEN ((m.result = 'X' AND m.player_x_id = p.id) OR 
                                  (m.result = 'O' AND m.player_o_id = p.id)) 
                                 AND m.mode = 'pvp' 
                            THEN 1 
                        END) as pvp_wins,
                        COUNT(CASE 
                            WHEN ((m.result = 'X' AND m.player_x_id = p.id) OR 
                                  (m.result = 'O' AND m.player_o_id = p.id)) 
                                 AND m.mode = 'pvai' AND m.ai_level = 'easy' 
                            THEN 1 
                        END) as ai_easy_wins,
                        COUNT(CASE 
                            WHEN ((m.result = 'X' AND m.player_x_id = p.id) OR 
                                  (m.result = 'O' AND m.player_o_id = p.id)) 
                                 AND m.mode = 'pvai' AND m.ai_level = 'medium' 
                            THEN 1 
                        END) as ai_medium_wins,
                        COUNT(CASE 
                            WHEN ((m.result = 'X' AND m.player_x_id = p.id) OR 
                                  (m.result = 'O' AND m.player_o_id = p.id)) 
                                 AND m.mode = 'pvai' AND m.ai_level = 'hard' 
                            THEN 1 
                        END) as ai_hard_wins,
                        COUNT(CASE 
                            WHEN m.player_x_id = p.id OR m.player_o_id = p.id 
                            THEN 1 
                        END) as total_games
                    FROM players p
                    LEFT JOIN matches m ON (m.player_x_id = p.id OR m.player_o_id = p.id)
                    GROUP BY p.id, p.name
                )
                SELECT 
                    name,
                    total_wins,
                    pvp_wins,
                    ai_easy_wins,
                    ai_medium_wins,
                    ai_hard_wins,
                    CASE 
                        WHEN total_games > 0 THEN ROUND(CAST(total_wins AS FLOAT) / total_games * 100, 1)
                        ELSE 0.0
                    END as win_percentage,
                    total_games
                FROM player_wins
                WHERE total_games > 0
                ORDER BY 
                    total_wins DESC,
                    pvp_wins DESC,
                    (ai_easy_wins + ai_medium_wins + ai_hard_wins) DESC,
                    name ASC
                LIMIT ?
            """

            cursor.execute(query, (limit,))
            results = cursor.fetchall()

            leaderboard_data = [PlayerStats(name=row[0], total_wins=row[1], pvp_wins=row[2], ai_easy_wins=row[3], ai_medium_wins=row[4], ai_hard_wins=row[5], win_percentage=row[6], total_games=row[7]) for row in results]

            logger.debug(f"Retrieved leaderboard with {len(leaderboard_data)} players")
            return leaderboard_data

    def recent_matches(self, limit: int = 50, filter_mode: str | None = None) -> list[MatchRecord]:
        """
        Get recent matches with optional filtering.

        Args:
            limit: Maximum number of matches to return
            filter_mode: Filter by mode ('pvp', 'easy', 'medium', 'hard') or None for all

        Returns:
            List of MatchRecord sorted by played_at (desc)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            base_query = """
                SELECT 
                    m.played_at,
                    px.name as player_x_name,
                    po.name as player_o_name,
                    m.result,
                    m.mode,
                    m.ai_level
                FROM matches m
                JOIN players px ON m.player_x_id = px.id
                JOIN players po ON m.player_o_id = po.id
            """

            where_clause = ""
            params = []

            if filter_mode == "pvp":
                where_clause = " WHERE m.mode = 'pvp'"
            elif filter_mode in ("easy", "medium", "hard"):
                where_clause = " WHERE m.mode = 'pvai' AND m.ai_level = ?"
                params.append(filter_mode)

            query = base_query + where_clause + " ORDER BY m.played_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            results = cursor.fetchall()

            match_data = [MatchRecord(played_at=row[0], player_x_name=row[1], player_o_name=row[2], result=row[3], mode=row[4], ai_level=row[5]) for row in results]

            logger.debug(f"Retrieved {len(match_data)} recent matches (filter: {filter_mode})")
            return match_data

    def reset_data(self) -> None:
        """Reset all data by deleting all matches and players."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM matches")
            cursor.execute("DELETE FROM players")

            conn.commit()

            logger.info("All data reset - matches and players deleted")

    def get_stats_summary(self) -> dict[str, Any]:
        """Get overall statistics summary."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM players")
            total_players = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM matches")
            total_matches = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM matches WHERE mode = 'pvp'")
            pvp_matches = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM matches WHERE mode = 'pvai'")
            pvai_matches = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM matches WHERE result = 'Draw'")
            draws = cursor.fetchone()[0]

            return {"total_players": total_players, "total_matches": total_matches, "pvp_matches": pvp_matches, "pvai_matches": pvai_matches, "draws": draws}
