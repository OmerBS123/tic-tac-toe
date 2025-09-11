"""
Unit tests for the storage module.
"""

import tempfile
from pathlib import Path

import pytest

from tictactoe.storage import MatchRecord, PlayerStats, Storage


class TestStorage:
    """Test cases for the Storage class."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.storage = Storage(self.temp_db.name)

    def teardown_method(self) -> None:
        """Clean up after each test method."""
        Path(self.temp_db.name).unlink(missing_ok=True)

    def test_init_creates_tables(self) -> None:
        """Test that initialization creates the required tables."""
        import sqlite3

        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()

            # noinspection SqlResolve
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            assert "players" in tables
            assert "matches" in tables

    def test_get_or_create_player_id_new_player(self) -> None:
        """Test creating a new player."""
        player_id = self.storage.get_or_create_player_id("Alice")

        assert player_id == 1

        import sqlite3

        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            # noinspection SqlResolve
            cursor.execute("SELECT name FROM players WHERE id = ?", (player_id,))
            result = cursor.fetchone()

            assert result is not None
            assert result[0] == "Alice"

    def test_get_or_create_player_id_existing_player(self) -> None:
        """Test getting existing player ID."""
        player_id1 = self.storage.get_or_create_player_id("Alice")
        player_id2 = self.storage.get_or_create_player_id("Alice")

        assert player_id1 == player_id2
        assert player_id1 == 1

    def test_get_or_create_player_id_case_insensitive(self) -> None:
        """Test that player lookup is case insensitive."""
        player_id1 = self.storage.get_or_create_player_id("Alice")
        player_id2 = self.storage.get_or_create_player_id("alice")
        player_id3 = self.storage.get_or_create_player_id("ALICE")

        assert player_id1 == player_id2 == player_id3

    def test_get_or_create_player_id_normalizes_name(self) -> None:
        """Test that player names are normalized (trimmed)."""
        player_id1 = self.storage.get_or_create_player_id("Alice")
        player_id2 = self.storage.get_or_create_player_id("  Alice  ")

        assert player_id1 == player_id2

    def test_get_or_create_player_id_empty_name_raises_error(self) -> None:
        """Test that empty player name raises ValueError."""
        with pytest.raises(ValueError, match="Player name cannot be empty"):
            self.storage.get_or_create_player_id("")

        with pytest.raises(ValueError, match="Player name cannot be empty"):
            self.storage.get_or_create_player_id("   ")

    def test_record_match_pvp_valid(self) -> None:
        """Test recording a valid PvP match."""
        self.storage.record_match("Alice", "Bob", "X", "pvp")

        import sqlite3

        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            # noinspection SqlResolve
            cursor.execute("SELECT COUNT(*) FROM matches")
            count = cursor.fetchone()[0]

            assert count == 1

            # noinspection SqlResolve
            cursor.execute(
                "SELECT player_x_id, player_o_id, result, mode, ai_level FROM matches"
            )
            result = cursor.fetchone()

            assert result[2] == "X"
            assert result[3] == "pvp"
            assert result[4] is None

    def test_record_match_pvai_valid(self) -> None:
        """Test recording a valid PvAI match."""
        self.storage.record_match("Alice", "AI", "O", "pvai", "hard")

        import sqlite3

        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            # noinspection SqlResolve
            cursor.execute("SELECT COUNT(*) FROM matches")
            count = cursor.fetchone()[0]

            assert count == 1

            # noinspection SqlResolve
            cursor.execute(
                "SELECT player_x_id, player_o_id, result, mode, ai_level FROM matches"
            )
            result = cursor.fetchone()

            assert result[2] == "O"
            assert result[3] == "pvai"
            assert result[4] == "hard"

    def test_record_match_invalid_result_raises_error(self) -> None:
        """Test that invalid result raises ValueError."""
        with pytest.raises(ValueError, match="Invalid result"):
            self.storage.record_match("Alice", "Bob", "Invalid", "pvp")

    def test_record_match_invalid_mode_raises_error(self) -> None:
        """Test that invalid mode raises ValueError."""
        with pytest.raises(ValueError, match="Invalid mode"):
            self.storage.record_match("Alice", "Bob", "X", "invalid")

    def test_record_match_pvai_invalid_ai_level_raises_error(self) -> None:
        """Test that invalid AI level for PvAI raises ValueError."""
        with pytest.raises(ValueError, match="Invalid AI level for PvAI mode"):
            self.storage.record_match("Alice", "AI", "X", "pvai", "invalid")

    def test_record_match_pvp_with_ai_level_raises_error(self) -> None:
        """Test that PvP mode with AI level raises ValueError."""
        with pytest.raises(ValueError, match="AI level should be None for PvP mode"):
            self.storage.record_match("Alice", "Bob", "X", "pvp", "easy")

    def test_leaderboard_empty_database(self) -> None:
        """Test leaderboard with empty database."""
        leaderboard = self.storage.leaderboard()

        assert leaderboard == []

    def test_leaderboard_single_player(self) -> None:
        """Test leaderboard with single player."""
        self.storage.record_match("Alice", "Bob", "X", "pvp")

        leaderboard = self.storage.leaderboard()

        assert len(leaderboard) == 2
        assert leaderboard[0].name == "Alice"
        assert leaderboard[0].total_wins == 1
        assert leaderboard[0].pvp_wins == 1
        assert leaderboard[0].ai_easy_wins == 0
        assert leaderboard[0].ai_medium_wins == 0
        assert leaderboard[0].ai_hard_wins == 0
        assert leaderboard[0].win_percentage == 1.0
        assert leaderboard[0].total_games == 1

    def test_leaderboard_multiple_players_sorted(self) -> None:
        """Test leaderboard with multiple players sorted correctly."""
        self.storage.record_match("Alice", "Bob", "X", "pvp")
        self.storage.record_match("Bob", "Alice", "O", "pvp")
        self.storage.record_match("Charlie", "Alice", "X", "pvp")
        self.storage.record_match("Charlie", "Bob", "X", "pvp")

        leaderboard = self.storage.leaderboard()

        assert len(leaderboard) == 3
        # Alice has 2 wins (1 as X, 1 as O), Charlie has 2 wins (both as X), Bob has 0 wins
        assert leaderboard[0].name == "Alice"
        assert leaderboard[0].total_wins == 2
        assert leaderboard[1].name == "Charlie"
        assert leaderboard[1].total_wins == 2
        assert leaderboard[2].name == "Bob"
        assert leaderboard[2].total_wins == 0

    def test_leaderboard_tie_breaking(self) -> None:
        """Test leaderboard tie-breaking rules."""
        self.storage.record_match("Alice", "Bob", "X", "pvp")
        self.storage.record_match("Bob", "Alice", "O", "pvp")
        self.storage.record_match("Alice", "AI", "X", "pvai", "easy")
        self.storage.record_match("Bob", "AI", "O", "pvai", "easy")

        leaderboard = self.storage.leaderboard()

        assert len(leaderboard) == 3
        # Alice has 3 wins (1 PvP as X, 1 PvP as O, 1 PvAI as X)
        # AI has 1 win (1 PvAI as O)
        # Bob has 0 wins
        assert leaderboard[0].name == "Alice"
        assert leaderboard[0].total_wins == 3
        assert leaderboard[0].pvp_wins == 2
        assert leaderboard[0].ai_easy_wins == 1
        assert leaderboard[1].name == "AI"
        assert leaderboard[1].total_wins == 1
        assert leaderboard[1].pvp_wins == 0
        assert leaderboard[1].ai_easy_wins == 1

    def test_leaderboard_win_percentage_calculation(self) -> None:
        """Test win percentage calculation."""
        self.storage.record_match("Alice", "Bob", "X", "pvp")
        self.storage.record_match("Bob", "Alice", "O", "pvp")
        self.storage.record_match("Alice", "Bob", "Draw", "pvp")

        leaderboard = self.storage.leaderboard()

        alice_stats = next(p for p in leaderboard if p.name == "Alice")
        # Alice has 2 wins out of 3 games (1 as X, 1 as O, 1 draw)
        assert alice_stats.total_wins == 2
        assert alice_stats.total_games == 3
        assert alice_stats.win_percentage == 0.67

    def test_recent_matches_empty_database(self) -> None:
        """Test recent matches with empty database."""
        matches = self.storage.recent_matches()

        assert matches == []

    def test_recent_matches_chronological_order(self) -> None:
        """Test that recent matches are in chronological order."""
        self.storage.record_match("Alice", "Bob", "X", "pvp")
        self.storage.record_match("Bob", "Alice", "O", "pvp")
        self.storage.record_match("Charlie", "Alice", "X", "pvp")

        matches = self.storage.recent_matches()

        assert len(matches) == 3
        # Matches are returned in insertion order (not reverse chronological)
        assert matches[0].player_x_name == "Alice"
        assert matches[1].player_x_name == "Bob"
        assert matches[2].player_x_name == "Charlie"

    def test_recent_matches_filter_pvp(self) -> None:
        """Test filtering recent matches by PvP mode."""
        self.storage.record_match("Alice", "Bob", "X", "pvp")
        self.storage.record_match("Alice", "AI", "O", "pvai", "easy")
        self.storage.record_match("Bob", "Alice", "O", "pvp")

        matches = self.storage.recent_matches(filter_mode="pvp")

        assert len(matches) == 2
        assert all(match.mode == "pvp" for match in matches)

    def test_recent_matches_filter_ai_level(self) -> None:
        """Test filtering recent matches by AI level."""
        self.storage.record_match("Alice", "AI", "X", "pvai", "easy")
        self.storage.record_match("Alice", "AI", "O", "pvai", "medium")
        self.storage.record_match("Alice", "AI", "X", "pvai", "hard")

        matches = self.storage.recent_matches(filter_mode="hard")

        assert len(matches) == 1
        assert matches[0].ai_level == "hard"

    def test_recent_matches_limit(self) -> None:
        """Test limiting the number of recent matches."""
        for i in range(5):
            self.storage.record_match(f"Player{i}", "Bob", "X", "pvp")

        matches = self.storage.recent_matches(limit=3)

        assert len(matches) == 3

    def test_reset_data(self) -> None:
        """Test resetting all data."""
        self.storage.record_match("Alice", "Bob", "X", "pvp")
        self.storage.record_match("Alice", "AI", "O", "pvai", "easy")

        import sqlite3

        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            # noinspection SqlResolve
            cursor.execute("SELECT COUNT(*) FROM players")
            players_before = cursor.fetchone()[0]
            # noinspection SqlResolve
            cursor.execute("SELECT COUNT(*) FROM matches")
            matches_before = cursor.fetchone()[0]

        assert players_before > 0
        assert matches_before > 0

        self.storage.reset_data()

        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            # noinspection SqlResolve
            cursor.execute("SELECT COUNT(*) FROM players")
            players_after = cursor.fetchone()[0]
            # noinspection SqlResolve
            cursor.execute("SELECT COUNT(*) FROM matches")
            matches_after = cursor.fetchone()[0]

        assert players_after == 0
        assert matches_after == 0

    def test_get_stats_summary(self) -> None:
        """Test getting statistics summary."""
        self.storage.record_match("Alice", "Bob", "X", "pvp")
        self.storage.record_match("Alice", "AI", "O", "pvai", "easy")
        self.storage.record_match("Bob", "Alice", "Draw", "pvp")

        summary = self.storage.get_stats_summary()

        assert summary["total_players"] == 3
        assert summary["total_matches"] == 3
        assert summary["pvp_matches"] == 2
        assert summary["pvai_matches"] == 1
        assert summary["draws"] == 1

    def test_get_stats_summary_empty_database(self) -> None:
        """Test getting statistics summary from empty database."""
        summary = self.storage.get_stats_summary()

        assert summary["total_players"] == 0
        assert summary["total_matches"] == 0
        assert summary["pvp_matches"] == 0
        assert summary["pvai_matches"] == 0
        assert summary["draws"] == 0

    def test_player_stats_namedtuple(self) -> None:
        """Test PlayerStats NamedTuple structure."""
        stats = PlayerStats(
            name="Alice",
            total_wins=5,
            pvp_wins=3,
            ai_easy_wins=1,
            ai_medium_wins=1,
            ai_hard_wins=0,
            win_percentage=0.83,
            total_games=6,
        )

        assert stats.name == "Alice"
        assert stats.total_wins == 5
        assert stats.pvp_wins == 3
        assert stats.ai_easy_wins == 1
        assert stats.ai_medium_wins == 1
        assert stats.ai_hard_wins == 0
        assert stats.win_percentage == 0.83
        assert stats.total_games == 6

    def test_match_record_namedtuple(self) -> None:
        """Test MatchRecord NamedTuple structure."""
        match = MatchRecord(
            played_at="2025-09-06T15:30:00",
            player_x_name="Alice",
            player_o_name="Bob",
            result="X",
            mode="pvp",
            ai_level=None,
        )

        assert match.played_at == "2025-09-06T15:30:00"
        assert match.player_x_name == "Alice"
        assert match.player_o_name == "Bob"
        assert match.result == "X"
        assert match.mode == "pvp"
        assert match.ai_level is None

    def test_leaderboard_limit(self) -> None:
        """Test leaderboard limit parameter."""
        for i in range(10):
            self.storage.record_match(f"Player{i}", "Bob", "X", "pvp")

        leaderboard = self.storage.leaderboard(limit=5)

        assert len(leaderboard) == 5

    def test_complex_scenario(self) -> None:
        """Test a complex scenario with multiple players and game types."""
        # PvP matches
        self.storage.record_match("Alice", "Bob", "X", "pvp")
        self.storage.record_match("Alice", "Bob", "O", "pvp")
        self.storage.record_match("Alice", "Bob", "Draw", "pvp")
        self.storage.record_match("Charlie", "Alice", "X", "pvp")
        self.storage.record_match("Charlie", "Bob", "O", "pvp")

        # PvAI matches
        self.storage.record_match("Alice", "AI", "X", "pvai", "easy")
        self.storage.record_match("Alice", "AI", "O", "pvai", "easy")
        self.storage.record_match("Alice", "AI", "X", "pvai", "medium")
        self.storage.record_match("Bob", "AI", "O", "pvai", "medium")
        self.storage.record_match("Bob", "AI", "Draw", "pvai", "hard")
        self.storage.record_match("Charlie", "AI", "X", "pvai", "hard")
        self.storage.record_match("Charlie", "AI", "X", "pvai", "hard")

        # Test leaderboard
        leaderboard = self.storage.leaderboard()
        assert len(leaderboard) == 4

        # Alice should be first (3 wins)
        alice = next(p for p in leaderboard if p.name == "Alice")
        assert alice.total_wins == 3
        assert alice.pvp_wins == 1
        assert alice.ai_easy_wins == 1
        assert alice.ai_medium_wins == 1
        assert alice.ai_hard_wins == 0

        # Charlie should be second (3 wins, but more PvAI wins)
        charlie = next(p for p in leaderboard if p.name == "Charlie")
        assert charlie.total_wins == 3
        assert charlie.pvp_wins == 1
        assert charlie.ai_easy_wins == 0
        assert charlie.ai_medium_wins == 0
        assert charlie.ai_hard_wins == 2

        # Test recent matches
        recent = self.storage.recent_matches()
        assert len(recent) == 12

        # Test filtering
        pvp_matches = self.storage.recent_matches(filter_mode="pvp")
        assert len(pvp_matches) == 5

        hard_ai_matches = self.storage.recent_matches(filter_mode="hard")
        assert len(hard_ai_matches) == 3

        # Test summary
        summary = self.storage.get_stats_summary()
        assert summary["total_players"] == 4
        assert summary["total_matches"] == 12
        assert summary["pvp_matches"] == 5
        assert summary["pvai_matches"] == 7
        assert summary["draws"] == 2
