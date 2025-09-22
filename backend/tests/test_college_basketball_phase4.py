#!/usr/bin/env python3
"""
Test Suite for College Basketball Phase 4: Statistics & Rankings
=============================================================

Comprehensive tests for Phase 4 implementation including:
- Schema validation and table creation
- Model relationships and constraints
- Statistics calculations and analytics
- Ranking system functionality
- Performance and indexing verification
- Data integrity and foreign key constraints

Test Categories:
1. Schema and Table Tests
2. Model Relationship Tests
3. Statistics and Analytics Tests
4. Ranking System Tests
5. Performance and Index Tests
6. Data Integrity Tests
7. Migration and Rollback Tests
"""

import pytest
import sqlite3
import tempfile
import os
from decimal import Decimal
from datetime import date, datetime, timedelta
from pathlib import Path
import sys

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from models.college_phase4 import (
    Player, TeamStatistics, PlayerStatistics,
    Rankings, AdvancedMetrics, SeasonRecords
)
from models.enums import (
    PlayerPosition, PlayerEligibilityStatus, PlayerClass,
    RankingSystem, StatisticType, RecordType
)


class TestCollegeBasketballPhase4:
    """Test suite for Phase 4 implementation"""

    @pytest.fixture
    def test_db_path(self):
        """Create a temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)

    @pytest.fixture
    def populated_db(self, test_db_path):
        """Create a database with Phase 1-3 data for testing Phase 4"""
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()

        # Create minimal Phase 1-3 tables for testing
        cursor.execute("""
            CREATE TABLE divisions (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                level TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE college_conferences (
                id TEXT PRIMARY KEY,
                division_id TEXT NOT NULL REFERENCES divisions(id),
                name TEXT NOT NULL,
                slug TEXT NOT NULL,
                conference_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE colleges (
                id TEXT PRIMARY KEY,
                conference_id TEXT NOT NULL REFERENCES college_conferences(id),
                name TEXT NOT NULL,
                slug TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE college_teams (
                id TEXT PRIMARY KEY,
                college_id TEXT NOT NULL REFERENCES colleges(id),
                sport_id TEXT NOT NULL,
                name TEXT NOT NULL,
                slug TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE academic_years (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                start_year INTEGER NOT NULL,
                end_year INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE seasons (
                id TEXT PRIMARY KEY,
                academic_year_id TEXT NOT NULL REFERENCES academic_years(id),
                name TEXT NOT NULL,
                season_type TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE college_games (
                id TEXT PRIMARY KEY,
                academic_year_id TEXT NOT NULL REFERENCES academic_years(id),
                season_id TEXT NOT NULL REFERENCES seasons(id),
                home_team_id TEXT NOT NULL REFERENCES college_teams(id),
                away_team_id TEXT NOT NULL REFERENCES college_teams(id),
                scheduled_at TIMESTAMP NOT NULL,
                status TEXT NOT NULL DEFAULT 'SCHEDULED',
                home_score INTEGER DEFAULT 0,
                away_score INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert test data
        test_data = [
            # Division
            ("div1", "Division I", "division-i", "D1"),
            # Conference
            ("conf1", "div1", "Test Conference", "test-conference", "power_five"),
            # College
            ("college1", "conf1", "Test University", "test-university", "Test City", "Test State"),
            # Team
            ("team1", "college1", "sport1", "Test Team", "test-team"),
            # Academic Year
            ("year1", "2024-25", 2024, 2025, "current"),
            # Season
            ("season1", "year1", "Regular Season 2024-25", "regular_season", "2024-11-01", "2025-03-01"),
        ]

        cursor.execute("INSERT INTO divisions VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)", test_data[0])
        cursor.execute("INSERT INTO college_conferences VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)", test_data[1])
        cursor.execute("INSERT INTO colleges VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)", test_data[2])
        cursor.execute("INSERT INTO college_teams VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)", test_data[3])
        cursor.execute("INSERT INTO academic_years VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)", test_data[4])
        cursor.execute("INSERT INTO seasons VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)", test_data[5])

        conn.commit()
        conn.close()
        return test_db_path

    def test_phase4_table_creation(self, test_db_path):
        """Test Phase 4 table creation"""
        from migrations.college_basketball_phase4_migration import CollegeBasketballPhase4Migration

        # Run migration
        migration = CollegeBasketballPhase4Migration(test_db_path, dry_run=False)

        # Create minimal prerequisites
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()

        # Create required tables for prerequisites check
        cursor.execute("CREATE TABLE IF NOT EXISTS college_teams (id TEXT PRIMARY KEY)")
        cursor.execute("CREATE TABLE IF NOT EXISTS academic_years (id TEXT PRIMARY KEY)")
        cursor.execute("INSERT OR IGNORE INTO college_teams VALUES ('team1')")
        cursor.execute("INSERT OR IGNORE INTO academic_years VALUES ('year1')")
        conn.commit()
        conn.close()

        # Run table creation
        assert migration.create_phase4_tables() == True

        # Verify tables exist
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        expected_tables = ['players', 'team_statistics', 'player_statistics',
                          'rankings', 'advanced_metrics', 'season_records']

        for table in expected_tables:
            assert table in tables, f"Table {table} was not created"

        conn.close()

    def test_phase4_indexes_creation(self, test_db_path):
        """Test Phase 4 index creation for performance"""
        from migrations.college_basketball_phase4_migration import CollegeBasketballPhase4Migration

        migration = CollegeBasketballPhase4Migration(test_db_path, dry_run=False)

        # Create tables first
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS college_teams (id TEXT PRIMARY KEY)")
        cursor.execute("CREATE TABLE IF NOT EXISTS academic_years (id TEXT PRIMARY KEY)")
        cursor.execute("INSERT OR IGNORE INTO college_teams VALUES ('team1')")
        cursor.execute("INSERT OR IGNORE INTO academic_years VALUES ('year1')")
        conn.commit()
        conn.close()

        migration.create_phase4_tables()
        assert migration.create_phase4_indexes() == True

        # Verify key indexes exist
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        indexes = [row[0] for row in cursor.fetchall()]

        # Check for critical performance indexes
        critical_indexes = [
            'idx_players_team_id',
            'idx_team_statistics_team_id',
            'idx_player_statistics_player_id',
            'idx_rankings_team_system',
            'idx_advanced_metrics_net_efficiency'
        ]

        for index in critical_indexes:
            assert index in indexes, f"Critical index {index} was not created"

        conn.close()

    def test_player_model_validation(self, populated_db):
        """Test Player model with validation"""
        conn = sqlite3.connect(populated_db)
        cursor = conn.cursor()

        # Create players table
        cursor.execute("""
            CREATE TABLE players (
                id TEXT PRIMARY KEY,
                team_id TEXT NOT NULL REFERENCES college_teams(id),
                academic_year_id TEXT NOT NULL REFERENCES academic_years(id),
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                full_name TEXT NOT NULL,
                jersey_number INTEGER,
                primary_position TEXT NOT NULL,
                player_class TEXT NOT NULL,
                eligibility_status TEXT NOT NULL DEFAULT 'eligible',
                height_inches INTEGER,
                weight_pounds INTEGER,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(team_id, jersey_number, academic_year_id)
            )
        """)

        # Test valid player insertion
        player_data = (
            "player1", "team1", "year1", "John", "Doe", "John Doe", 23,
            "point_guard", "sophomore", "eligible", 72, 180, True
        )

        cursor.execute("""
            INSERT INTO players (
                id, team_id, academic_year_id, first_name, last_name, full_name,
                jersey_number, primary_position, player_class, eligibility_status,
                height_inches, weight_pounds, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, player_data)

        # Test duplicate jersey number constraint
        with pytest.raises(sqlite3.IntegrityError):
            duplicate_data = (
                "player2", "team1", "year1", "Jane", "Smith", "Jane Smith", 23,
                "shooting_guard", "freshman", "eligible", 68, 160, True
            )
            cursor.execute("""
                INSERT INTO players (
                    id, team_id, academic_year_id, first_name, last_name, full_name,
                    jersey_number, primary_position, player_class, eligibility_status,
                    height_inches, weight_pounds, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, duplicate_data)

        # Verify player was inserted correctly
        cursor.execute("SELECT full_name, jersey_number, primary_position FROM players WHERE id = 'player1'")
        result = cursor.fetchone()
        assert result == ("John Doe", 23, "point_guard")

        conn.close()

    def test_statistics_relationships(self, populated_db):
        """Test statistics models and their relationships"""
        conn = sqlite3.connect(populated_db)
        cursor = conn.cursor()

        # Create required tables
        cursor.execute("""
            CREATE TABLE players (
                id TEXT PRIMARY KEY,
                team_id TEXT NOT NULL,
                academic_year_id TEXT NOT NULL,
                full_name TEXT NOT NULL,
                primary_position TEXT NOT NULL,
                player_class TEXT NOT NULL,
                eligibility_status TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE team_statistics (
                id TEXT PRIMARY KEY,
                team_id TEXT NOT NULL REFERENCES college_teams(id),
                academic_year_id TEXT NOT NULL REFERENCES academic_years(id),
                statistic_type TEXT NOT NULL,
                games_played INTEGER DEFAULT 0,
                points DECIMAL(8,2) DEFAULT 0,
                field_goal_percentage DECIMAL(5,3),
                three_point_percentage DECIMAL(5,3),
                total_rebounds DECIMAL(8,2),
                assists DECIMAL(8,2)
            )
        """)

        cursor.execute("""
            CREATE TABLE player_statistics (
                id TEXT PRIMARY KEY,
                player_id TEXT NOT NULL REFERENCES players(id),
                team_id TEXT NOT NULL REFERENCES college_teams(id),
                academic_year_id TEXT NOT NULL REFERENCES academic_years(id),
                statistic_type TEXT NOT NULL,
                games_played INTEGER DEFAULT 0,
                points DECIMAL(8,2) DEFAULT 0,
                minutes_played DECIMAL(6,2)
            )
        """)

        # Insert test player
        cursor.execute("""
            INSERT INTO players VALUES (
                'player1', 'team1', 'year1', 'Test Player', 'point_guard', 'sophomore', 'eligible'
            )
        """)

        # Insert team statistics
        cursor.execute("""
            INSERT INTO team_statistics VALUES (
                'team_stat1', 'team1', 'year1', 'season_total', 25, 1875.5, 0.467, 0.352, 875.3, 456.7
            )
        """)

        # Insert player statistics
        cursor.execute("""
            INSERT INTO player_statistics VALUES (
                'player_stat1', 'player1', 'team1', 'year1', 'season_total', 25, 387.5, 687.2
            )
        """)

        # Verify relationships
        cursor.execute("""
            SELECT p.full_name, ps.points, ts.points as team_points
            FROM players p
            JOIN player_statistics ps ON p.id = ps.player_id
            JOIN team_statistics ts ON p.team_id = ts.team_id
            WHERE p.id = 'player1'
        """)

        result = cursor.fetchone()
        assert result[0] == "Test Player"
        assert float(result[1]) == 387.5
        assert float(result[2]) == 1875.5

        conn.close()

    def test_ranking_systems(self, populated_db):
        """Test ranking system functionality"""
        conn = sqlite3.connect(populated_db)
        cursor = conn.cursor()

        # Create rankings table
        cursor.execute("""
            CREATE TABLE rankings (
                id TEXT PRIMARY KEY,
                team_id TEXT NOT NULL REFERENCES college_teams(id),
                academic_year_id TEXT NOT NULL REFERENCES academic_years(id),
                ranking_system TEXT NOT NULL,
                rank INTEGER NOT NULL,
                rating DECIMAL(10,4),
                ranking_date DATE NOT NULL,
                is_current BOOLEAN DEFAULT TRUE,
                is_ranked BOOLEAN DEFAULT TRUE,
                first_place_votes INTEGER,
                total_points INTEGER
            )
        """)

        # Test different ranking systems
        ranking_systems = ['ap_poll', 'coaches_poll', 'net_ranking', 'kenpom']

        for i, system in enumerate(ranking_systems):
            cursor.execute("""
                INSERT INTO rankings VALUES (
                    ?, 'team1', 'year1', ?, ?, ?, ?, TRUE, TRUE, ?, ?
                )
            """, (
                f"rank_{i+1}", system, i+1, 0.95 - (i * 0.05) if system == 'kenpom' else None,
                date.today().isoformat(), 10 - i if system in ['ap_poll', 'coaches_poll'] else 0,
                1500 - (i * 100) if system in ['ap_poll', 'coaches_poll'] else 0
            ))

        # Verify rankings
        cursor.execute("""
            SELECT ranking_system, rank, rating, first_place_votes
            FROM rankings
            WHERE team_id = 'team1'
            ORDER BY rank
        """)

        results = cursor.fetchall()
        assert len(results) == 4

        # Check AP Poll ranking
        ap_ranking = next(r for r in results if r[0] == 'ap_poll')
        assert ap_ranking[1] == 1
        assert ap_ranking[3] == 10  # First place votes

        # Check KenPom rating
        kenpom_ranking = next(r for r in results if r[0] == 'kenpom')
        assert kenpom_ranking[2] is not None  # Should have rating

        conn.close()

    def test_advanced_metrics_calculations(self, populated_db):
        """Test advanced metrics and analytics"""
        conn = sqlite3.connect(populated_db)
        cursor = conn.cursor()

        # Create advanced metrics table
        cursor.execute("""
            CREATE TABLE advanced_metrics (
                id TEXT PRIMARY KEY,
                team_id TEXT NOT NULL REFERENCES college_teams(id),
                academic_year_id TEXT NOT NULL REFERENCES academic_years(id),
                calculation_date DATE NOT NULL,
                offensive_efficiency DECIMAL(8,4),
                defensive_efficiency DECIMAL(8,4),
                net_efficiency DECIMAL(8,4),
                tempo DECIMAL(8,4),
                effective_field_goal_percentage DECIMAL(5,3),
                pythagorean_wins DECIMAL(6,2),
                strength_of_schedule DECIMAL(8,4)
            )
        """)

        # Insert realistic metrics
        cursor.execute("""
            INSERT INTO advanced_metrics VALUES (
                'metrics1', 'team1', 'year1', ?, 118.5, 95.2, 23.3, 68.7, 0.525, 22.3, 2.15
            )
        """, (date.today().isoformat(),))

        # Test efficiency calculations
        cursor.execute("""
            SELECT offensive_efficiency, defensive_efficiency, net_efficiency,
                   (offensive_efficiency - defensive_efficiency) as calculated_net
            FROM advanced_metrics
            WHERE id = 'metrics1'
        """)

        result = cursor.fetchone()
        offensive_eff = float(result[0])
        defensive_eff = float(result[1])
        net_eff = float(result[2])
        calculated_net = float(result[3])

        # Verify net efficiency calculation
        assert abs(net_eff - calculated_net) < 0.01, "Net efficiency calculation mismatch"
        assert offensive_eff > 100, "Offensive efficiency should be reasonable"
        assert defensive_eff < 110, "Defensive efficiency should be reasonable"

        conn.close()

    def test_season_records_tracking(self, populated_db):
        """Test season records and win-loss tracking"""
        conn = sqlite3.connect(populated_db)
        cursor = conn.cursor()

        # Create season records table
        cursor.execute("""
            CREATE TABLE season_records (
                id TEXT PRIMARY KEY,
                team_id TEXT NOT NULL REFERENCES college_teams(id),
                academic_year_id TEXT NOT NULL REFERENCES academic_years(id),
                record_type TEXT NOT NULL,
                wins INTEGER NOT NULL DEFAULT 0,
                losses INTEGER NOT NULL DEFAULT 0,
                current_streak TEXT,
                record_date DATE NOT NULL,
                is_current BOOLEAN DEFAULT TRUE
            )
        """)

        # Insert different record types
        record_types = [
            ('overall', 20, 5, 'W3'),
            ('conference', 12, 6, 'W3'),
            ('home', 12, 1, 'W8'),
            ('away', 6, 7, 'L1'),
            ('neutral', 2, 1, 'W1')
        ]

        for i, (record_type, wins, losses, streak) in enumerate(record_types):
            cursor.execute("""
                INSERT INTO season_records VALUES (
                    ?, 'team1', 'year1', ?, ?, ?, ?, ?, TRUE
                )
            """, (f"record_{i+1}", record_type, wins, losses, streak, date.today().isoformat()))

        # Test record calculations
        cursor.execute("""
            SELECT record_type, wins, losses,
                   CAST(wins AS FLOAT) / (wins + losses) as win_percentage,
                   (wins + losses) as total_games
            FROM season_records
            WHERE team_id = 'team1'
            ORDER BY record_type
        """)

        results = cursor.fetchall()

        # Verify overall record
        overall = next(r for r in results if r[0] == 'overall')
        assert overall[1] == 20  # wins
        assert overall[2] == 5   # losses
        assert abs(overall[3] - 0.8) < 0.01  # win percentage

        # Verify home advantage
        home = next(r for r in results if r[0] == 'home')
        away = next(r for r in results if r[0] == 'away')

        home_win_pct = home[1] / (home[1] + home[2])
        away_win_pct = away[1] / (away[1] + away[2])

        assert home_win_pct > away_win_pct, "Home win percentage should be higher than away"

        conn.close()

    def test_query_performance_indexes(self, populated_db):
        """Test that indexes improve query performance"""
        conn = sqlite3.connect(populated_db)
        cursor = conn.cursor()

        # Create tables with indexes
        cursor.execute("""
            CREATE TABLE test_players (
                id TEXT PRIMARY KEY,
                team_id TEXT NOT NULL,
                academic_year_id TEXT NOT NULL,
                full_name TEXT NOT NULL,
                primary_position TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE test_player_statistics (
                id TEXT PRIMARY KEY,
                player_id TEXT NOT NULL,
                team_id TEXT NOT NULL,
                points DECIMAL(8,2) DEFAULT 0
            )
        """)

        # Create performance indexes
        cursor.execute("CREATE INDEX idx_test_players_team_id ON test_players(team_id)")
        cursor.execute("CREATE INDEX idx_test_player_statistics_player_id ON test_player_statistics(player_id)")

        # Insert test data
        for i in range(1000):
            cursor.execute("""
                INSERT INTO test_players VALUES (?, 'team1', 'year1', ?, 'guard')
            """, (f"player_{i}", f"Player {i}"))

            cursor.execute("""
                INSERT INTO test_player_statistics VALUES (?, ?, 'team1', ?)
            """, (f"stat_{i}", f"player_{i}", i * 15.5))

        # Test query with index usage
        cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM test_players WHERE team_id = 'team1'")
        plan = cursor.fetchall()

        # Should use index (not scanning table)
        plan_text = ' '.join([str(row) for row in plan])
        assert "USING INDEX" in plan_text.upper() or "SEARCH" in plan_text.upper()

        # Test join performance
        cursor.execute("""
            EXPLAIN QUERY PLAN
            SELECT p.full_name, ps.points
            FROM test_players p
            JOIN test_player_statistics ps ON p.id = ps.player_id
            WHERE p.team_id = 'team1'
        """)

        join_plan = cursor.fetchall()
        join_text = ' '.join([str(row) for row in join_plan])

        # Should use indexes for join
        assert "USING INDEX" in join_text.upper() or "SEARCH" in join_text.upper()

        conn.close()

    def test_data_integrity_constraints(self, populated_db):
        """Test foreign key constraints and data integrity"""
        conn = sqlite3.connect(populated_db)
        cursor = conn.cursor()

        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")

        # Create tables with foreign key constraints
        cursor.execute("""
            CREATE TABLE test_players (
                id TEXT PRIMARY KEY,
                team_id TEXT NOT NULL REFERENCES college_teams(id) ON DELETE CASCADE,
                full_name TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE test_player_stats (
                id TEXT PRIMARY KEY,
                player_id TEXT NOT NULL REFERENCES test_players(id) ON DELETE CASCADE,
                points DECIMAL(8,2)
            )
        """)

        # Insert valid data
        cursor.execute("INSERT INTO test_players VALUES ('player1', 'team1', 'Test Player')")
        cursor.execute("INSERT INTO test_player_stats VALUES ('stat1', 'player1', 15.5)")

        # Test foreign key constraint violation
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO test_players VALUES ('player2', 'nonexistent_team', 'Invalid Player')")

        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO test_player_stats VALUES ('stat2', 'nonexistent_player', 20.0)")

        # Test cascade delete
        cursor.execute("DELETE FROM test_players WHERE id = 'player1'")

        # Statistics should be deleted too
        cursor.execute("SELECT COUNT(*) FROM test_player_stats")
        count = cursor.fetchone()[0]
        assert count == 0, "Statistics should be deleted when player is deleted"

        conn.close()

    def test_analytics_query_patterns(self, populated_db):
        """Test common analytics query patterns"""
        conn = sqlite3.connect(populated_db)
        cursor = conn.cursor()

        # Create comprehensive test data
        cursor.execute("""
            CREATE TABLE analytics_teams (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE analytics_players (
                id TEXT PRIMARY KEY,
                team_id TEXT NOT NULL,
                full_name TEXT NOT NULL,
                primary_position TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE analytics_stats (
                id TEXT PRIMARY KEY,
                player_id TEXT NOT NULL,
                team_id TEXT NOT NULL,
                points DECIMAL(8,2),
                rebounds DECIMAL(8,2),
                assists DECIMAL(8,2),
                minutes_played DECIMAL(6,2)
            )
        """)

        cursor.execute("""
            CREATE TABLE analytics_team_stats (
                id TEXT PRIMARY KEY,
                team_id TEXT NOT NULL,
                offensive_efficiency DECIMAL(8,4),
                defensive_efficiency DECIMAL(8,4)
            )
        """)

        # Insert test data
        teams = [('team1', 'Team A'), ('team2', 'Team B')]
        for team_id, name in teams:
            cursor.execute("INSERT INTO analytics_teams VALUES (?, ?)", (team_id, name))
            cursor.execute("INSERT INTO analytics_team_stats VALUES (?, ?, ?, ?)",
                         (f"team_stat_{team_id}", team_id, 115.5, 95.2))

        # Insert players and stats
        positions = ['point_guard', 'shooting_guard', 'center']
        for team_id, _ in teams:
            for i, position in enumerate(positions):
                player_id = f"player_{team_id}_{i}"
                cursor.execute("INSERT INTO analytics_players VALUES (?, ?, ?, ?)",
                             (player_id, team_id, f"Player {i}", position))
                cursor.execute("INSERT INTO analytics_stats VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (f"stat_{player_id}", player_id, team_id,
                              15.0 + i * 3, 8.0 + i * 2, 5.0 + i, 25.0 + i * 2))

        # Test 1: Team efficiency comparison
        cursor.execute("""
            SELECT t.name, ts.offensive_efficiency, ts.defensive_efficiency,
                   (ts.offensive_efficiency - ts.defensive_efficiency) as net_efficiency
            FROM analytics_teams t
            JOIN analytics_team_stats ts ON t.id = ts.team_id
            ORDER BY net_efficiency DESC
        """)

        results = cursor.fetchall()
        assert len(results) == 2
        assert results[0][3] > 0  # Net efficiency should be positive

        # Test 2: Player performance per minute
        cursor.execute("""
            SELECT p.full_name, p.primary_position,
                   (s.points / s.minutes_played) as points_per_minute,
                   (s.rebounds + s.assists) / s.minutes_played as productivity
            FROM analytics_players p
            JOIN analytics_stats s ON p.id = s.player_id
            ORDER BY points_per_minute DESC
        """)

        player_results = cursor.fetchall()
        assert len(player_results) == 6  # 3 players per team, 2 teams

        # Test 3: Team aggregation
        cursor.execute("""
            SELECT p.team_id,
                   AVG(s.points) as avg_points,
                   SUM(s.rebounds) as total_rebounds,
                   COUNT(*) as player_count
            FROM analytics_players p
            JOIN analytics_stats s ON p.id = s.player_id
            GROUP BY p.team_id
        """)

        team_agg = cursor.fetchall()
        assert len(team_agg) == 2
        assert team_agg[0][3] == 3  # Player count per team

        conn.close()

    def test_migration_rollback_capability(self, test_db_path):
        """Test migration rollback functionality"""
        from migrations.college_basketball_phase4_migration import CollegeBasketballPhase4Migration

        # Create backup scenario
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()

        # Create minimal data
        cursor.execute("CREATE TABLE test_data (id TEXT PRIMARY KEY, value TEXT)")
        cursor.execute("INSERT INTO test_data VALUES ('1', 'original')")
        conn.commit()
        conn.close()

        # Create migration instance
        migration = CollegeBasketballPhase4Migration(test_db_path, dry_run=False)

        # Create backup
        backup_path = migration.create_backup()
        assert os.path.exists(backup_path), "Backup file should be created"

        # Modify database
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE test_data SET value = 'modified' WHERE id = '1'")
        cursor.execute("CREATE TABLE college_teams (id TEXT PRIMARY KEY)")
        cursor.execute("CREATE TABLE academic_years (id TEXT PRIMARY KEY)")
        cursor.execute("INSERT INTO college_teams VALUES ('team1')")
        cursor.execute("INSERT INTO academic_years VALUES ('year1')")
        conn.commit()
        conn.close()

        # Verify modification
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM test_data WHERE id = '1'")
        assert cursor.fetchone()[0] == 'modified'
        conn.close()

        # Test backup restore (simulated rollback)
        import shutil
        shutil.copy2(backup_path, test_db_path)

        # Verify rollback
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM test_data WHERE id = '1'")
        assert cursor.fetchone()[0] == 'original'
        conn.close()

        # Cleanup
        os.unlink(backup_path)

    def test_enum_validation(self):
        """Test enum validation for Phase 4 models"""
        # Test PlayerPosition enum
        assert PlayerPosition.POINT_GUARD == "point_guard"
        assert PlayerPosition.CENTER == "center"

        # Test PlayerEligibilityStatus enum
        assert PlayerEligibilityStatus.ELIGIBLE == "eligible"
        assert PlayerEligibilityStatus.TRANSFER_PORTAL == "transfer_portal"

        # Test RankingSystem enum
        assert RankingSystem.AP_POLL == "ap_poll"
        assert RankingSystem.NET_RANKING == "net_ranking"
        assert RankingSystem.KENPOM == "kenpom"

        # Test StatisticType enum
        assert StatisticType.SEASON_TOTAL == "season_total"
        assert StatisticType.SEASON_AVERAGE == "season_average"

        # Test RecordType enum
        assert RecordType.OVERALL == "overall"
        assert RecordType.QUAD_1 == "quad_1"

    def test_comprehensive_integration(self, populated_db):
        """Test complete integration across all Phase 4 models"""
        conn = sqlite3.connect(populated_db)
        cursor = conn.cursor()

        # Create all Phase 4 tables
        from migrations.college_basketball_phase4_migration import CollegeBasketballPhase4Migration
        migration = CollegeBasketballPhase4Migration(populated_db, dry_run=False)

        assert migration.create_phase4_tables() == True
        assert migration.create_phase4_indexes() == True

        # Insert comprehensive test data
        # Player
        cursor.execute("""
            INSERT INTO players VALUES (
                'player1', 'team1', 'year1', 'John', 'Smith', 'John Smith', 23,
                'point_guard', NULL, 72, 180, ?, 'Test City', 'CA', 'USA',
                'Test High School', NULL, 'sophomore', 'eligible', 3, FALSE,
                NULL, NULL, 2023, 4, 150, 25, FALSE, NULL,
                'ext_1', 'espn_1', 'ncaa_1', 'photo_url', 'Bio text', TRUE, NULL,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
        """, (date(2002, 5, 15).isoformat(),))

        # Team Statistics
        cursor.execute("""
            INSERT INTO team_statistics VALUES (
                'team_stat1', 'team1', 'year1', NULL, NULL, 'season_total', 25,
                1875.5, 680.2, 1456.8, 0.467, 210.4, 598.3, 0.352,
                485.6, 678.9, 0.715, 240.3, 635.0, 875.3,
                456.7, 178.9, 98.4, 345.2, 456.8, 1650.2, ?,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
        """, (date.today().isoformat(),))

        # Player Statistics
        cursor.execute("""
            INSERT INTO player_statistics VALUES (
                'player_stat1', 'player1', 'team1', 'year1', NULL, NULL, 'season_total',
                687.5, 25, 22, 387.5, 140.2, 298.7, 0.469, 62.4, 156.8, 0.398,
                84.7, 108.9, 0.778, 35.6, 98.4, 134.0, 125.3, 42.7, 8.9, 89.6, 67.2, ?,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
        """, (date.today().isoformat(),))

        # Rankings
        cursor.execute("""
            INSERT INTO rankings VALUES (
                'ranking1', 'team1', 'year1', 'ap_poll', 5, NULL, 10, ?, 7, -2,
                3, 1420, TRUE, TRUE, NULL,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
        """, (date.today().isoformat(),))

        # Advanced Metrics
        cursor.execute("""
            INSERT INTO advanced_metrics VALUES (
                'metrics1', 'team1', 'year1', ?, 118.5, 95.2, 23.3, 68.7, 70.2,
                0.525, 0.568, 0.520, 0.185, 0.325, 0.285, 0.485, 0.205, 0.745, 0.295,
                2.15, 1.85, 22.3, 0.125, 4.2, 12.8, '5-2', 3, 8.45, TRUE,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
        """, (date.today().isoformat(),))

        # Season Records
        cursor.execute("""
            INSERT INTO season_records VALUES (
                'record1', 'team1', 'year1', 'overall', 20, 5, 'W3', 8, 2,
                NULL, NULL, NULL, NULL, NULL, ?, TRUE,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
        """, (date.today().isoformat(),))

        conn.commit()

        # Test comprehensive query across all models
        cursor.execute("""
            SELECT
                p.full_name,
                p.primary_position,
                ps.points / ps.games_played as ppg,
                ts.points / ts.games_played as team_ppg,
                r.rank as ap_rank,
                am.net_efficiency,
                sr.wins,
                sr.losses
            FROM players p
            JOIN player_statistics ps ON p.id = ps.player_id
            JOIN team_statistics ts ON p.team_id = ts.team_id AND ts.statistic_type = 'season_total'
            JOIN rankings r ON p.team_id = r.team_id AND r.ranking_system = 'ap_poll'
            JOIN advanced_metrics am ON p.team_id = am.team_id
            JOIN season_records sr ON p.team_id = sr.team_id AND sr.record_type = 'overall'
            WHERE p.id = 'player1'
        """)

        result = cursor.fetchone()
        assert result is not None, "Integration query should return results"

        # Verify data consistency
        assert result[0] == "John Smith"  # Player name
        assert result[1] == "point_guard"  # Position
        assert float(result[2]) > 0  # PPG should be positive
        assert result[4] == 5  # AP ranking
        assert float(result[5]) > 0  # Net efficiency should be positive
        assert result[6] == 20  # Wins
        assert result[7] == 5   # Losses

        conn.close()


def run_phase4_tests():
    """Run all Phase 4 tests"""
    import subprocess

    try:
        # Run pytest with verbose output
        result = subprocess.run([
            'python', '-m', 'pytest',
            __file__,
            '-v',
            '--tb=short'
        ], capture_output=True, text=True, cwd=str(backend_dir))

        print("Phase 4 Test Results:")
        print("=" * 50)
        print(result.stdout)

        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"Error running tests: {e}")
        return False


if __name__ == "__main__":
    # Run tests if called directly
    success = run_phase4_tests()
    exit(0 if success else 1)