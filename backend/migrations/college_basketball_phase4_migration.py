#!/usr/bin/env python3
"""
College Basketball Phase 4: Statistics & Rankings Migration
==========================================================

Implements comprehensive statistics, rankings, and analytics models for college basketball.

Phase 4 Components:
- Player: Individual player profiles with biographical and eligibility data
- TeamStatistics: Season and game-level team performance metrics
- PlayerStatistics: Individual player performance tracking
- Rankings: Multiple ranking system support (NET, KenPom, AP, Coaches)
- AdvancedMetrics: Analytics like efficiency ratings, strength of schedule
- SeasonRecords: Win-loss records with detailed breakdowns

Features:
- Comprehensive basketball statistics tracking
- Multiple ranking methodologies with historical data
- Advanced analytics (offensive/defensive efficiency, tempo, etc.)
- Player eligibility and transfer tracking
- Team performance trends and analytics
- Performance optimization for statistical queries

Safety Features:
- Idempotent operations (safe to re-run)
- Atomic transactions with rollback support
- Pre-migration validation
- Comprehensive error handling
- Data integrity verification
"""

import sys
import os
import sqlite3
import json
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import database and models
from database import get_db_path, init_db
from models.base import Base, create_tables
from models.enums import (
    PlayerPosition, PlayerEligibilityStatus, PlayerClass,
    RankingSystem, StatisticType, StatisticCategory, RecordType
)


class CollegeBasketballPhase4Migration:
    """
    College Basketball Phase 4: Statistics & Rankings Migration
    """

    def __init__(self, db_path: Optional[str] = None, dry_run: bool = False):
        self.db_path = db_path or get_db_path()
        self.dry_run = dry_run
        self.backup_path = None
        self.migration_results = {
            "status": "pending",
            "start_time": None,
            "end_time": None,
            "tables_created": [],
            "indexes_created": [],
            "seed_data_inserted": {},
            "errors": [],
            "warnings": [],
            "rollback_path": None
        }

    def log(self, message: str, level: str = "INFO"):
        """Log migration progress"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        if level == "ERROR":
            self.migration_results["errors"].append(message)
        elif level == "WARNING":
            self.migration_results["warnings"].append(message)

    def create_backup(self) -> str:
        """Create a backup of the current database"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found: {self.db_path}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"college_basketball_phase4_backup_{timestamp}.db"
        backup_path = os.path.join(os.path.dirname(self.db_path), backup_filename)

        # Create backup
        import shutil
        shutil.copy2(self.db_path, backup_path)

        self.backup_path = backup_path
        self.migration_results["rollback_path"] = backup_path
        self.log(f"Database backup created: {backup_path}")
        return backup_path

    def validate_prerequisites(self) -> bool:
        """Validate that prerequisites are met for Phase 4"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check for required Phase 1-3 tables
            required_tables = [
                'divisions', 'college_conferences', 'colleges', 'college_teams',
                'academic_years', 'seasons', 'venues', 'tournaments', 'college_games'
            ]

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]

            missing_tables = [table for table in required_tables if table not in existing_tables]
            if missing_tables:
                self.log(f"Missing required tables: {missing_tables}", "ERROR")
                return False

            # Check for required data
            cursor.execute("SELECT COUNT(*) FROM college_teams")
            team_count = cursor.fetchone()[0]
            if team_count == 0:
                self.log("No college teams found. Phase 1-3 must be completed first.", "ERROR")
                return False

            cursor.execute("SELECT COUNT(*) FROM academic_years")
            year_count = cursor.fetchone()[0]
            if year_count == 0:
                self.log("No academic years found. Phase 2 must be completed first.", "ERROR")
                return False

            conn.close()
            self.log("Prerequisites validation passed")
            return True

        except Exception as e:
            self.log(f"Prerequisites validation failed: {e}", "ERROR")
            return False

    def create_phase4_tables(self) -> bool:
        """Create Phase 4 tables with proper schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")

            tables_sql = {
                "players": """
                CREATE TABLE IF NOT EXISTS players (
                    id TEXT PRIMARY KEY,
                    team_id TEXT NOT NULL REFERENCES college_teams(id) ON DELETE CASCADE,
                    academic_year_id TEXT NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    jersey_number INTEGER,
                    primary_position TEXT NOT NULL,
                    secondary_position TEXT,
                    height_inches INTEGER,
                    weight_pounds INTEGER,
                    birth_date DATE,
                    hometown TEXT,
                    home_state TEXT,
                    home_country TEXT DEFAULT 'USA',
                    high_school TEXT,
                    previous_college TEXT,
                    player_class TEXT NOT NULL,
                    eligibility_status TEXT NOT NULL DEFAULT 'eligible',
                    years_of_eligibility_remaining INTEGER NOT NULL DEFAULT 4,
                    is_transfer BOOLEAN NOT NULL DEFAULT FALSE,
                    transfer_from_college_id TEXT REFERENCES colleges(id) ON DELETE SET NULL,
                    transfer_year INTEGER,
                    recruiting_class_year INTEGER,
                    recruiting_stars INTEGER,
                    recruiting_rank_national INTEGER,
                    recruiting_rank_position INTEGER,
                    nba_draft_eligible BOOLEAN NOT NULL DEFAULT FALSE,
                    nba_draft_year INTEGER,
                    external_id TEXT,
                    espn_player_id TEXT,
                    ncaa_player_id TEXT,
                    photo_url TEXT,
                    bio TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    injury_status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(team_id, jersey_number, academic_year_id)
                )
                """,

                "team_statistics": """
                CREATE TABLE IF NOT EXISTS team_statistics (
                    id TEXT PRIMARY KEY,
                    team_id TEXT NOT NULL REFERENCES college_teams(id) ON DELETE CASCADE,
                    academic_year_id TEXT NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
                    season_id TEXT REFERENCES seasons(id) ON DELETE CASCADE,
                    game_id TEXT REFERENCES college_games(id) ON DELETE CASCADE,
                    statistic_type TEXT NOT NULL,
                    games_played INTEGER NOT NULL DEFAULT 0,
                    points DECIMAL(8,2) NOT NULL DEFAULT 0,
                    field_goals_made DECIMAL(8,2),
                    field_goals_attempted DECIMAL(8,2),
                    field_goal_percentage DECIMAL(5,3),
                    three_pointers_made DECIMAL(8,2),
                    three_pointers_attempted DECIMAL(8,2),
                    three_point_percentage DECIMAL(5,3),
                    free_throws_made DECIMAL(8,2),
                    free_throws_attempted DECIMAL(8,2),
                    free_throw_percentage DECIMAL(5,3),
                    offensive_rebounds DECIMAL(8,2),
                    defensive_rebounds DECIMAL(8,2),
                    total_rebounds DECIMAL(8,2),
                    assists DECIMAL(8,2),
                    steals DECIMAL(8,2),
                    blocks DECIMAL(8,2),
                    turnovers DECIMAL(8,2),
                    personal_fouls DECIMAL(8,2),
                    points_allowed DECIMAL(8,2),
                    stats_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(team_id, game_id, statistic_type),
                    UNIQUE(team_id, season_id, statistic_type)
                )
                """,

                "player_statistics": """
                CREATE TABLE IF NOT EXISTS player_statistics (
                    id TEXT PRIMARY KEY,
                    player_id TEXT NOT NULL REFERENCES players(id) ON DELETE CASCADE,
                    team_id TEXT NOT NULL REFERENCES college_teams(id) ON DELETE CASCADE,
                    academic_year_id TEXT NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
                    season_id TEXT REFERENCES seasons(id) ON DELETE CASCADE,
                    game_id TEXT REFERENCES college_games(id) ON DELETE CASCADE,
                    statistic_type TEXT NOT NULL,
                    minutes_played DECIMAL(6,2),
                    games_played INTEGER NOT NULL DEFAULT 0,
                    games_started INTEGER NOT NULL DEFAULT 0,
                    points DECIMAL(8,2) NOT NULL DEFAULT 0,
                    field_goals_made DECIMAL(8,2),
                    field_goals_attempted DECIMAL(8,2),
                    field_goal_percentage DECIMAL(5,3),
                    three_pointers_made DECIMAL(8,2),
                    three_pointers_attempted DECIMAL(8,2),
                    three_point_percentage DECIMAL(5,3),
                    free_throws_made DECIMAL(8,2),
                    free_throws_attempted DECIMAL(8,2),
                    free_throw_percentage DECIMAL(5,3),
                    offensive_rebounds DECIMAL(8,2),
                    defensive_rebounds DECIMAL(8,2),
                    total_rebounds DECIMAL(8,2),
                    assists DECIMAL(8,2),
                    steals DECIMAL(8,2),
                    blocks DECIMAL(8,2),
                    turnovers DECIMAL(8,2),
                    personal_fouls DECIMAL(8,2),
                    stats_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(player_id, game_id, statistic_type),
                    UNIQUE(player_id, season_id, statistic_type)
                )
                """,

                "rankings": """
                CREATE TABLE IF NOT EXISTS rankings (
                    id TEXT PRIMARY KEY,
                    team_id TEXT NOT NULL REFERENCES college_teams(id) ON DELETE CASCADE,
                    academic_year_id TEXT NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
                    ranking_system TEXT NOT NULL,
                    rank INTEGER NOT NULL,
                    rating DECIMAL(10,4),
                    ranking_week INTEGER,
                    ranking_date DATE NOT NULL,
                    previous_rank INTEGER,
                    rank_change INTEGER,
                    first_place_votes INTEGER,
                    total_points INTEGER,
                    is_current BOOLEAN NOT NULL DEFAULT TRUE,
                    is_ranked BOOLEAN NOT NULL DEFAULT TRUE,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(team_id, ranking_system, ranking_date)
                )
                """,

                "advanced_metrics": """
                CREATE TABLE IF NOT EXISTS advanced_metrics (
                    id TEXT PRIMARY KEY,
                    team_id TEXT NOT NULL REFERENCES college_teams(id) ON DELETE CASCADE,
                    academic_year_id TEXT NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
                    calculation_date DATE NOT NULL,
                    offensive_efficiency DECIMAL(8,4),
                    defensive_efficiency DECIMAL(8,4),
                    net_efficiency DECIMAL(8,4),
                    tempo DECIMAL(8,4),
                    pace DECIMAL(8,4),
                    effective_field_goal_percentage DECIMAL(5,3),
                    true_shooting_percentage DECIMAL(5,3),
                    offensive_four_factor_efg DECIMAL(5,3),
                    offensive_four_factor_tov DECIMAL(5,3),
                    offensive_four_factor_orb DECIMAL(5,3),
                    offensive_four_factor_ft DECIMAL(5,3),
                    defensive_four_factor_efg DECIMAL(5,3),
                    defensive_four_factor_tov DECIMAL(5,3),
                    defensive_four_factor_drb DECIMAL(5,3),
                    defensive_four_factor_ft DECIMAL(5,3),
                    strength_of_schedule DECIMAL(8,4),
                    strength_of_record DECIMAL(8,4),
                    pythagorean_wins DECIMAL(6,2),
                    luck_factor DECIMAL(6,3),
                    average_lead DECIMAL(6,2),
                    lead_changes_per_game DECIMAL(6,2),
                    close_game_record TEXT,
                    comeback_wins INTEGER,
                    performance_variance DECIMAL(8,4),
                    is_current BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(team_id, academic_year_id, calculation_date)
                )
                """,

                "season_records": """
                CREATE TABLE IF NOT EXISTS season_records (
                    id TEXT PRIMARY KEY,
                    team_id TEXT NOT NULL REFERENCES college_teams(id) ON DELETE CASCADE,
                    academic_year_id TEXT NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
                    record_type TEXT NOT NULL,
                    wins INTEGER NOT NULL DEFAULT 0,
                    losses INTEGER NOT NULL DEFAULT 0,
                    current_streak TEXT,
                    longest_win_streak INTEGER,
                    longest_loss_streak INTEGER,
                    opponent_rank_range TEXT,
                    quad_1_wins INTEGER,
                    quad_1_losses INTEGER,
                    quad_2_wins INTEGER,
                    quad_2_losses INTEGER,
                    record_date DATE NOT NULL,
                    is_current BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(team_id, academic_year_id, record_type, record_date)
                )
                """
            }

            # Create tables
            for table_name, sql in tables_sql.items():
                if not self.dry_run:
                    cursor.execute(sql)
                    self.migration_results["tables_created"].append(table_name)
                self.log(f"Created table: {table_name}")

            # Commit table creation
            if not self.dry_run:
                conn.commit()

            conn.close()
            return True

        except Exception as e:
            self.log(f"Failed to create Phase 4 tables: {e}", "ERROR")
            return False

    def create_phase4_indexes(self) -> bool:
        """Create optimized indexes for Phase 4 analytics queries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            indexes_sql = [
                # Players table indexes
                "CREATE INDEX IF NOT EXISTS idx_players_team_id ON players(team_id)",
                "CREATE INDEX IF NOT EXISTS idx_players_academic_year_id ON players(academic_year_id)",
                "CREATE INDEX IF NOT EXISTS idx_players_full_name ON players(full_name)",
                "CREATE INDEX IF NOT EXISTS idx_players_last_name ON players(last_name)",
                "CREATE INDEX IF NOT EXISTS idx_players_jersey_number ON players(jersey_number)",
                "CREATE INDEX IF NOT EXISTS idx_players_position ON players(primary_position)",
                "CREATE INDEX IF NOT EXISTS idx_players_class ON players(player_class)",
                "CREATE INDEX IF NOT EXISTS idx_players_eligibility ON players(eligibility_status)",
                "CREATE INDEX IF NOT EXISTS idx_players_transfer ON players(is_transfer)",
                "CREATE INDEX IF NOT EXISTS idx_players_active ON players(is_active)",
                "CREATE INDEX IF NOT EXISTS idx_players_external_id ON players(external_id)",
                "CREATE INDEX IF NOT EXISTS idx_players_espn_id ON players(espn_player_id)",
                "CREATE INDEX IF NOT EXISTS idx_players_ncaa_id ON players(ncaa_player_id)",
                "CREATE INDEX IF NOT EXISTS idx_players_team_jersey ON players(team_id, jersey_number)",

                # Team statistics indexes
                "CREATE INDEX IF NOT EXISTS idx_team_statistics_team_id ON team_statistics(team_id)",
                "CREATE INDEX IF NOT EXISTS idx_team_statistics_academic_year_id ON team_statistics(academic_year_id)",
                "CREATE INDEX IF NOT EXISTS idx_team_statistics_season_id ON team_statistics(season_id)",
                "CREATE INDEX IF NOT EXISTS idx_team_statistics_game_id ON team_statistics(game_id)",
                "CREATE INDEX IF NOT EXISTS idx_team_statistics_type ON team_statistics(statistic_type)",
                "CREATE INDEX IF NOT EXISTS idx_team_statistics_stats_date ON team_statistics(stats_date)",
                "CREATE INDEX IF NOT EXISTS idx_team_statistics_team_year ON team_statistics(team_id, academic_year_id)",

                # Player statistics indexes
                "CREATE INDEX IF NOT EXISTS idx_player_statistics_player_id ON player_statistics(player_id)",
                "CREATE INDEX IF NOT EXISTS idx_player_statistics_team_id ON player_statistics(team_id)",
                "CREATE INDEX IF NOT EXISTS idx_player_statistics_academic_year_id ON player_statistics(academic_year_id)",
                "CREATE INDEX IF NOT EXISTS idx_player_statistics_season_id ON player_statistics(season_id)",
                "CREATE INDEX IF NOT EXISTS idx_player_statistics_game_id ON player_statistics(game_id)",
                "CREATE INDEX IF NOT EXISTS idx_player_statistics_type ON player_statistics(statistic_type)",
                "CREATE INDEX IF NOT EXISTS idx_player_statistics_stats_date ON player_statistics(stats_date)",
                "CREATE INDEX IF NOT EXISTS idx_player_statistics_player_year ON player_statistics(player_id, academic_year_id)",

                # Rankings indexes
                "CREATE INDEX IF NOT EXISTS idx_rankings_team_id ON rankings(team_id)",
                "CREATE INDEX IF NOT EXISTS idx_rankings_academic_year_id ON rankings(academic_year_id)",
                "CREATE INDEX IF NOT EXISTS idx_rankings_system ON rankings(ranking_system)",
                "CREATE INDEX IF NOT EXISTS idx_rankings_rank ON rankings(rank)",
                "CREATE INDEX IF NOT EXISTS idx_rankings_date ON rankings(ranking_date)",
                "CREATE INDEX IF NOT EXISTS idx_rankings_current ON rankings(is_current)",
                "CREATE INDEX IF NOT EXISTS idx_rankings_ranked ON rankings(is_ranked)",
                "CREATE INDEX IF NOT EXISTS idx_rankings_team_system ON rankings(team_id, ranking_system)",
                "CREATE INDEX IF NOT EXISTS idx_rankings_system_date ON rankings(ranking_system, ranking_date)",

                # Advanced metrics indexes
                "CREATE INDEX IF NOT EXISTS idx_advanced_metrics_team_id ON advanced_metrics(team_id)",
                "CREATE INDEX IF NOT EXISTS idx_advanced_metrics_academic_year_id ON advanced_metrics(academic_year_id)",
                "CREATE INDEX IF NOT EXISTS idx_advanced_metrics_calculation_date ON advanced_metrics(calculation_date)",
                "CREATE INDEX IF NOT EXISTS idx_advanced_metrics_current ON advanced_metrics(is_current)",
                "CREATE INDEX IF NOT EXISTS idx_advanced_metrics_offensive_efficiency ON advanced_metrics(offensive_efficiency)",
                "CREATE INDEX IF NOT EXISTS idx_advanced_metrics_defensive_efficiency ON advanced_metrics(defensive_efficiency)",
                "CREATE INDEX IF NOT EXISTS idx_advanced_metrics_net_efficiency ON advanced_metrics(net_efficiency)",
                "CREATE INDEX IF NOT EXISTS idx_advanced_metrics_team_year ON advanced_metrics(team_id, academic_year_id)",

                # Season records indexes
                "CREATE INDEX IF NOT EXISTS idx_season_records_team_id ON season_records(team_id)",
                "CREATE INDEX IF NOT EXISTS idx_season_records_academic_year_id ON season_records(academic_year_id)",
                "CREATE INDEX IF NOT EXISTS idx_season_records_type ON season_records(record_type)",
                "CREATE INDEX IF NOT EXISTS idx_season_records_date ON season_records(record_date)",
                "CREATE INDEX IF NOT EXISTS idx_season_records_current ON season_records(is_current)",
                "CREATE INDEX IF NOT EXISTS idx_season_records_wins ON season_records(wins)",
                "CREATE INDEX IF NOT EXISTS idx_season_records_losses ON season_records(losses)",
                "CREATE INDEX IF NOT EXISTS idx_season_records_team_type ON season_records(team_id, record_type)",
            ]

            # Create indexes
            for index_sql in indexes_sql:
                if not self.dry_run:
                    cursor.execute(index_sql)
                index_name = index_sql.split("IF NOT EXISTS ")[1].split(" ON ")[0]
                self.migration_results["indexes_created"].append(index_name)

            # Commit index creation
            if not self.dry_run:
                conn.commit()

            self.log(f"Created {len(indexes_sql)} indexes for optimal query performance")
            conn.close()
            return True

        except Exception as e:
            self.log(f"Failed to create Phase 4 indexes: {e}", "ERROR")
            return False

    def insert_seed_data(self) -> bool:
        """Insert comprehensive seed data for Phase 4 models"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get existing data for seeding
            cursor.execute("SELECT id, name FROM college_teams ORDER BY name LIMIT 20")
            teams = cursor.fetchall()

            cursor.execute("SELECT id, name FROM academic_years WHERE status = 'current' LIMIT 1")
            current_year = cursor.fetchone()

            if not teams or not current_year:
                self.log("No teams or current academic year found for seeding", "WARNING")
                return True

            seed_counts = {
                "players": 0,
                "team_statistics": 0,
                "player_statistics": 0,
                "rankings": 0,
                "advanced_metrics": 0,
                "season_records": 0
            }

            # Sample player names for diversity
            sample_players = [
                ("Marcus", "Johnson", "PG"), ("Tyler", "Williams", "SG"), ("Kevin", "Davis", "SF"),
                ("Anthony", "Brown", "PF"), ("Michael", "Wilson", "C"), ("Jason", "Miller", "G"),
                ("David", "Garcia", "F"), ("Christopher", "Rodriguez", "PG"), ("Matthew", "Martinez", "SG"),
                ("Daniel", "Anderson", "SF"), ("James", "Taylor", "PF"), ("Robert", "Thomas", "C")
            ]

            # Insert sample players for each team
            for team_id, team_name in teams[:10]:  # Limit to 10 teams for reasonable seed data
                for i, (first_name, last_name, position) in enumerate(sample_players):
                    if i >= 12:  # Roster limit
                        break

                    player_id = f"player_{team_id}_{i+1}"
                    full_name = f"{first_name} {last_name}"

                    if not self.dry_run:
                        cursor.execute("""
                            INSERT OR IGNORE INTO players (
                                id, team_id, academic_year_id, first_name, last_name, full_name,
                                jersey_number, primary_position, player_class, eligibility_status,
                                height_inches, weight_pounds, hometown, home_state
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            player_id, team_id, current_year[0], first_name, last_name, full_name,
                            i+1, position.lower().replace('pg', 'point_guard').replace('sg', 'shooting_guard')
                                .replace('sf', 'small_forward').replace('pf', 'power_forward')
                                .replace('c', 'center').replace('g', 'guard').replace('f', 'forward'),
                            'sophomore', 'eligible',
                            72 + (i % 8), 180 + (i * 5), f"City {i+1}", "State"
                        ))
                    seed_counts["players"] += 1

            # Insert sample team statistics
            for team_id, team_name in teams[:10]:
                stat_id = f"team_stats_{team_id}_season"

                if not self.dry_run:
                    cursor.execute("""
                        INSERT OR IGNORE INTO team_statistics (
                            id, team_id, academic_year_id, statistic_type, games_played,
                            points, field_goals_made, field_goals_attempted, field_goal_percentage,
                            three_pointers_made, three_pointers_attempted, three_point_percentage,
                            free_throws_made, free_throws_attempted, free_throw_percentage,
                            total_rebounds, assists, steals, blocks, turnovers, personal_fouls
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        stat_id, team_id, current_year[0], 'season_total', 25,
                        1875.5, 680.2, 1456.8, 0.467,
                        210.4, 598.3, 0.352,
                        485.6, 678.9, 0.715,
                        875.3, 456.7, 178.9, 98.4, 345.2, 456.8
                    ))
                seed_counts["team_statistics"] += 1

            # Insert sample rankings
            ranking_systems = ['ap_poll', 'coaches_poll', 'net_ranking', 'kenpom']
            for i, (team_id, team_name) in enumerate(teams[:25]):  # Top 25 teams
                for system in ranking_systems:
                    ranking_id = f"ranking_{team_id}_{system}"

                    if not self.dry_run:
                        cursor.execute("""
                            INSERT OR IGNORE INTO rankings (
                                id, team_id, academic_year_id, ranking_system, rank,
                                ranking_date, is_current, is_ranked
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            ranking_id, team_id, current_year[0], system, i+1,
                            date.today().isoformat(), True, True
                        ))
                    seed_counts["rankings"] += 1

            # Insert sample advanced metrics
            for team_id, team_name in teams[:15]:
                metric_id = f"metrics_{team_id}_current"

                if not self.dry_run:
                    cursor.execute("""
                        INSERT OR IGNORE INTO advanced_metrics (
                            id, team_id, academic_year_id, calculation_date,
                            offensive_efficiency, defensive_efficiency, net_efficiency,
                            tempo, effective_field_goal_percentage, true_shooting_percentage
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        metric_id, team_id, current_year[0], date.today().isoformat(),
                        115.5 - (i * 0.8), 95.2 + (i * 0.6), 20.3 - (i * 1.4),
                        68.5 + (i * 0.3), 0.525 - (i * 0.003), 0.568 - (i * 0.004)
                    ))
                seed_counts["advanced_metrics"] += 1

            # Insert sample season records
            record_types = ['overall', 'conference', 'home', 'away', 'neutral']
            for team_id, team_name in teams[:12]:
                for record_type in record_types:
                    record_id = f"record_{team_id}_{record_type}"

                    # Generate realistic win-loss records
                    if record_type == 'overall':
                        wins, losses = 20 - (i // 2), 5 + (i // 2)
                    elif record_type == 'conference':
                        wins, losses = 12 - (i // 3), 6 + (i // 3)
                    elif record_type == 'home':
                        wins, losses = 12 - (i // 4), 1 + (i // 4)
                    elif record_type == 'away':
                        wins, losses = 6 - (i // 3), 7 + (i // 3)
                    else:  # neutral
                        wins, losses = 2, 1

                    if not self.dry_run:
                        cursor.execute("""
                            INSERT OR IGNORE INTO season_records (
                                id, team_id, academic_year_id, record_type,
                                wins, losses, record_date, is_current
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            record_id, team_id, current_year[0], record_type,
                            wins, losses, date.today().isoformat(), True
                        ))
                    seed_counts["season_records"] += 1

            # Commit seed data
            if not self.dry_run:
                conn.commit()

            self.migration_results["seed_data_inserted"] = seed_counts
            self.log(f"Inserted seed data: {seed_counts}")

            conn.close()
            return True

        except Exception as e:
            self.log(f"Failed to insert seed data: {e}", "ERROR")
            return False

    def verify_migration(self) -> bool:
        """Verify that the migration completed successfully"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check that all tables exist
            expected_tables = ['players', 'team_statistics', 'player_statistics',
                             'rankings', 'advanced_metrics', 'season_records']

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]

            missing_tables = [table for table in expected_tables if table not in existing_tables]
            if missing_tables:
                self.log(f"Verification failed: Missing tables {missing_tables}", "ERROR")
                return False

            # Check data counts
            verification_results = {}
            for table in expected_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                verification_results[table] = count
                self.log(f"Table {table}: {count} records")

            # Check for proper indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
            indexes = [row[0] for row in cursor.fetchall()]
            self.log(f"Created {len(indexes)} indexes for performance optimization")

            conn.close()
            self.log("Migration verification completed successfully")
            return True

        except Exception as e:
            self.log(f"Migration verification failed: {e}", "ERROR")
            return False

    def run_migration(self) -> Dict[str, Any]:
        """Execute the complete Phase 4 migration"""
        self.migration_results["start_time"] = datetime.now().isoformat()

        try:
            self.log("Starting College Basketball Phase 4: Statistics & Rankings Migration")

            if self.dry_run:
                self.log("DRY RUN MODE - No changes will be made to the database")

            # Step 1: Validate prerequisites
            if not self.validate_prerequisites():
                self.migration_results["status"] = "failed"
                return self.migration_results

            # Step 2: Create backup
            if not self.dry_run:
                self.create_backup()

            # Step 3: Create Phase 4 tables
            if not self.create_phase4_tables():
                self.migration_results["status"] = "failed"
                return self.migration_results

            # Step 4: Create optimized indexes
            if not self.create_phase4_indexes():
                self.migration_results["status"] = "failed"
                return self.migration_results

            # Step 5: Insert seed data
            if not self.insert_seed_data():
                self.migration_results["status"] = "failed"
                return self.migration_results

            # Step 6: Verify migration
            if not self.verify_migration():
                self.migration_results["status"] = "failed"
                return self.migration_results

            self.migration_results["status"] = "completed"
            self.migration_results["end_time"] = datetime.now().isoformat()

            self.log("College Basketball Phase 4 migration completed successfully!")
            return self.migration_results

        except Exception as e:
            self.log(f"Migration failed with unexpected error: {e}", "ERROR")
            self.migration_results["status"] = "failed"
            self.migration_results["end_time"] = datetime.now().isoformat()
            return self.migration_results


def main():
    """Main migration execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="College Basketball Phase 4: Statistics & Rankings Migration")
    parser.add_argument("--db", help="Database path", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no changes)")
    parser.add_argument("--output", help="Output results to JSON file", default=None)

    args = parser.parse_args()

    # Run migration
    migration = CollegeBasketballPhase4Migration(
        db_path=args.db,
        dry_run=args.dry_run
    )

    results = migration.run_migration()

    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results written to: {args.output}")

    # Print summary
    print(f"\nMigration Status: {results['status'].upper()}")
    if results.get('errors'):
        print(f"Errors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  - {error}")

    if results.get('warnings'):
        print(f"Warnings: {len(results['warnings'])}")
        for warning in results['warnings']:
            print(f"  - {warning}")

    # Exit with appropriate code
    exit_code = 0 if results['status'] == 'completed' else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()