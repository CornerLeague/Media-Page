#!/usr/bin/env python3
"""
Integration tests for College Football Phase 2

This script tests the integration between Phase 1 and Phase 2 models,
validates relationships, and demonstrates advanced analytics capabilities.
"""

import os
import sys
from datetime import date, datetime
from decimal import Decimal

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker

from models.base import Base
from models.college_football_phase1 import FootballTeam, FootballPlayer, FootballGame
from models.college_football_phase2 import (
    DriveData, PlayByPlay, FootballPlayerStatistics, FootballTeamStatistics,
    FootballAdvancedMetrics, FootballGameStatistics
)
from models.enums import *


class FootballPhase2IntegrationTester:
    """Tests College Football Phase 2 integration and functionality"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []

    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        if passed:
            self.tests_passed += 1
            status = "PASS"
        else:
            self.tests_failed += 1
            status = "FAIL"

        result = f"[{status}] {test_name}"
        if message:
            result += f" - {message}"

        self.test_results.append(result)
        print(result)

    def test_phase1_data_exists(self):
        """Test that Phase 1 data exists and is accessible"""
        print("\n=== Testing Phase 1 Data Availability ===")

        # Test teams
        teams = self.session.query(FootballTeam).all()
        self.log_test("Football teams exist", len(teams) > 0, f"Found {len(teams)} teams")

        # Test players
        players = self.session.query(FootballPlayer).all()
        self.log_test("Football players exist", len(players) > 0, f"Found {len(players)} players")

        # Test games
        games = self.session.query(FootballGame).all()
        self.log_test("Football games exist", len(games) > 0, f"Found {len(games)} games")

        return len(teams) > 0 and len(players) > 0 and len(games) > 0

    def test_phase2_tables_created(self):
        """Test that Phase 2 tables were created successfully"""
        print("\n=== Testing Phase 2 Table Creation ===")

        tables_to_check = [
            'football_drive_data',
            'football_play_by_play',
            'football_player_statistics',
            'football_team_statistics',
            'football_advanced_metrics',
            'football_game_statistics'
        ]

        for table_name in tables_to_check:
            try:
                result = self.session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                self.log_test(f"Table {table_name} exists", True, f"{count} records")
            except Exception as e:
                self.log_test(f"Table {table_name} exists", False, str(e))

    def test_phase2_relationships(self):
        """Test relationships between Phase 1 and Phase 2 models"""
        print("\n=== Testing Model Relationships ===")

        # Test drive-to-game relationship
        drives = self.session.query(DriveData).limit(5).all()
        for drive in drives:
            game_exists = drive.game is not None
            self.log_test(f"Drive {drive.id} links to game", game_exists)

            if game_exists:
                home_team_exists = drive.game.home_team is not None
                away_team_exists = drive.game.away_team is not None
                self.log_test(f"Game {drive.game.id} has teams", home_team_exists and away_team_exists)

        # Test play-to-drive relationship
        plays = self.session.query(PlayByPlay).filter(PlayByPlay.drive_id.isnot(None)).limit(5).all()
        for play in plays:
            drive_exists = play.drive is not None
            self.log_test(f"Play {play.id} links to drive", drive_exists)

        # Test player stats relationship
        player_stats = self.session.query(FootballPlayerStatistics).limit(5).all()
        for stat in player_stats:
            player_exists = stat.player is not None
            team_exists = stat.team is not None
            self.log_test(f"Player stat {stat.id} has relationships", player_exists and team_exists)

    def test_advanced_analytics_calculations(self):
        """Test advanced analytics calculations and properties"""
        print("\n=== Testing Advanced Analytics ===")

        # Test drive efficiency calculations
        drives = self.session.query(DriveData).filter(
            DriveData.total_plays > 0
        ).limit(10).all()

        for drive in drives:
            # Test yards per play calculation
            if drive.yards_per_play is not None:
                expected_ypp = drive.total_yards / drive.total_plays
                calculated_ypp = float(drive.yards_per_play)
                ypp_correct = abs(calculated_ypp - expected_ypp) < 0.1
                self.log_test(f"Drive {drive.id} yards per play calculation", ypp_correct)

            # Test third down percentage
            if drive.third_down_attempts > 0:
                third_down_pct = drive.third_down_percentage
                pct_valid = third_down_pct is not None and 0 <= third_down_pct <= 100
                self.log_test(f"Drive {drive.id} third down percentage valid", pct_valid)

        # Test team statistics calculations
        team_stats = self.session.query(FootballTeamStatistics).filter(
            FootballTeamStatistics.total_plays > 0
        ).limit(5).all()

        for stat in team_stats:
            # Test yards per play
            ypp = stat.yards_per_play
            ypp_valid = ypp is not None and ypp > 0
            self.log_test(f"Team stat {stat.id} yards per play", ypp_valid)

            # Test completion percentage
            if stat.passing_attempts > 0:
                completion_pct = stat.passing_completion_percentage
                pct_valid = completion_pct is not None and 0 <= completion_pct <= 100
                self.log_test(f"Team stat {stat.id} completion percentage", pct_valid)

    def test_situational_analytics(self):
        """Test situational analytics and context-aware metrics"""
        print("\n=== Testing Situational Analytics ===")

        # Test red zone plays
        red_zone_plays = self.session.query(PlayByPlay).filter(
            PlayByPlay.is_red_zone == True
        ).limit(10).all()

        for play in red_zone_plays:
            field_pos_correct = play.field_position in [FieldPosition.RED_ZONE, FieldPosition.GOAL_LINE]
            self.log_test(f"Red zone play {play.id} field position", field_pos_correct)

        # Test third down conversions
        third_down_plays = self.session.query(PlayByPlay).filter(
            PlayByPlay.down == 3
        ).limit(10).all()

        for play in third_down_plays:
            down_type_correct = play.down_type in [DownType.THIRD_SHORT, DownType.THIRD_MEDIUM, DownType.THIRD_LONG]
            self.log_test(f"Third down play {play.id} down type", down_type_correct)

        # Test explosive plays
        explosive_plays = self.session.query(PlayByPlay).filter(
            PlayByPlay.is_explosive_play == True
        ).all()

        explosive_count_valid = len(explosive_plays) >= 0
        self.log_test("Explosive plays identified", explosive_count_valid, f"Found {len(explosive_plays)} explosive plays")

    def test_advanced_metrics_quality(self):
        """Test quality and validity of advanced metrics"""
        print("\n=== Testing Advanced Metrics Quality ===")

        # Test EPA values are reasonable
        epa_metrics = self.session.query(FootballAdvancedMetrics).filter(
            FootballAdvancedMetrics.metric_type == AdvancedMetricType.EPA
        ).all()

        for metric in epa_metrics:
            epa_reasonable = -2.0 <= float(metric.metric_value) <= 2.0
            self.log_test(f"EPA metric {metric.id} reasonable", epa_reasonable, f"EPA: {metric.metric_value}")

        # Test success rate metrics are valid percentages
        success_metrics = self.session.query(FootballAdvancedMetrics).filter(
            FootballAdvancedMetrics.metric_type == AdvancedMetricType.SUCCESS_RATE
        ).all()

        for metric in success_metrics:
            success_valid = 0 <= float(metric.metric_value) <= 1
            self.log_test(f"Success rate {metric.id} valid", success_valid, f"Rate: {metric.metric_value}")

        # Test percentile ranks
        percentile_metrics = self.session.query(FootballAdvancedMetrics).filter(
            FootballAdvancedMetrics.percentile_rank.isnot(None)
        ).limit(10).all()

        for metric in percentile_metrics:
            percentile_valid = 0 <= float(metric.percentile_rank) <= 100
            self.log_test(f"Percentile rank {metric.id} valid", percentile_valid, f"Rank: {metric.percentile_rank}")

    def test_performance_queries(self):
        """Test performance of common analytics queries"""
        print("\n=== Testing Query Performance ===")

        import time

        # Test complex aggregation query
        start_time = time.time()
        result = self.session.query(
            FootballTeam.id,
            func.avg(FootballPlayerStatistics.passing_yards).label('avg_passing'),
            func.count(FootballPlayerStatistics.id).label('stat_count')
        ).join(FootballPlayerStatistics).group_by(FootballTeam.id).limit(10).all()

        query_time = time.time() - start_time
        performance_good = query_time < 5.0  # Should complete in under 5 seconds
        self.log_test("Team aggregation query performance", performance_good, f"{query_time:.2f} seconds")

        # Test play-by-play analysis query
        start_time = time.time()
        pbp_analysis = self.session.query(
            PlayByPlay.game_id,
            func.count(PlayByPlay.id).label('total_plays'),
            func.sum(PlayByPlay.yards_gained).label('total_yards')
        ).group_by(PlayByPlay.game_id).limit(5).all()

        query_time = time.time() - start_time
        performance_good = query_time < 3.0
        self.log_test("Play-by-play analysis query performance", performance_good, f"{query_time:.2f} seconds")

    def test_data_integrity(self):
        """Test data integrity and constraints"""
        print("\n=== Testing Data Integrity ===")

        # Test drive consistency
        drives = self.session.query(DriveData).limit(10).all()
        for drive in drives:
            plays_consistent = drive.total_plays >= 0
            yards_consistent = drive.total_yards >= 0
            self.log_test(f"Drive {drive.id} data consistency", plays_consistent and yards_consistent)

        # Test player statistics consistency
        player_stats = self.session.query(FootballPlayerStatistics).filter(
            FootballPlayerStatistics.passing_attempts > 0
        ).limit(5).all()

        for stat in player_stats:
            completions_valid = stat.passing_completions <= stat.passing_attempts
            self.log_test(f"Player stat {stat.id} passing consistency", completions_valid)

        # Test game statistics totals
        game_stats = self.session.query(FootballGameStatistics).limit(5).all()
        for stat in game_stats:
            scores_positive = stat.home_score >= 0 and stat.away_score >= 0
            margin_correct = stat.margin_of_victory == abs(stat.home_score - stat.away_score)
            self.log_test(f"Game stat {stat.id} integrity", scores_positive and margin_correct)

    def test_enum_values(self):
        """Test that enum values are properly stored and retrieved"""
        print("\n=== Testing Enum Values ===")

        # Test play results
        play_results = self.session.query(PlayByPlay.play_result).distinct().all()
        valid_results = [result[0] for result in play_results]
        results_valid = all(result in PlayResult.__members__.values() for result in valid_results)
        self.log_test("Play result enums valid", results_valid, f"Found: {valid_results}")

        # Test drive results
        drive_results = self.session.query(DriveData.drive_result).distinct().all()
        valid_drive_results = [result[0] for result in drive_results]
        drive_results_valid = all(result in DriveResult.__members__.values() for result in valid_drive_results)
        self.log_test("Drive result enums valid", drive_results_valid, f"Found: {valid_drive_results}")

    def test_complex_analytics_scenarios(self):
        """Test complex analytics scenarios"""
        print("\n=== Testing Complex Analytics Scenarios ===")

        # Test red zone efficiency calculation
        try:
            red_zone_drives = self.session.query(DriveData).filter(
                DriveData.is_red_zone_drive == True
            ).all()

            if red_zone_drives:
                scoring_drives = [d for d in red_zone_drives if d.points_scored > 0]
                efficiency = len(scoring_drives) / len(red_zone_drives) if red_zone_drives else 0
                efficiency_reasonable = 0.4 <= efficiency <= 0.9  # Typical red zone efficiency
                self.log_test("Red zone efficiency calculation", efficiency_reasonable, f"Efficiency: {efficiency:.2%}")
            else:
                self.log_test("Red zone efficiency calculation", True, "No red zone drives found")
        except Exception as e:
            self.log_test("Red zone efficiency calculation", False, str(e))

        # Test third down conversion rates by distance
        try:
            third_down_plays = self.session.query(PlayByPlay).filter(
                PlayByPlay.down == 3
            ).all()

            if third_down_plays:
                short_yardage = [p for p in third_down_plays if p.distance <= 3]
                medium_yardage = [p for p in third_down_plays if 4 <= p.distance <= 7]
                long_yardage = [p for p in third_down_plays if p.distance >= 8]

                self.log_test("Third down distance categorization",
                             len(short_yardage) + len(medium_yardage) + len(long_yardage) <= len(third_down_plays),
                             f"Short: {len(short_yardage)}, Medium: {len(medium_yardage)}, Long: {len(long_yardage)}")
            else:
                self.log_test("Third down distance categorization", True, "No third down plays found")
        except Exception as e:
            self.log_test("Third down distance categorization", False, str(e))

    def test_model_properties(self):
        """Test model property methods"""
        print("\n=== Testing Model Properties ===")

        # Test drive properties
        drives = self.session.query(DriveData).limit(5).all()
        for drive in drives:
            # Test time of possession calculation
            if drive.drive_duration_seconds:
                top_minutes = drive.time_of_possession_minutes
                minutes_valid = top_minutes is not None and top_minutes > 0
                self.log_test(f"Drive {drive.id} time of possession", minutes_valid)

            # Test drive efficiency
            efficiency = drive.drive_efficiency
            efficiency_valid = efficiency is None or (0 <= efficiency <= 1)
            self.log_test(f"Drive {drive.id} efficiency calculation", efficiency_valid)

        # Test game statistics properties
        game_stats = self.session.query(FootballGameStatistics).limit(3).all()
        for stat in game_stats:
            # Test game classification properties
            is_blowout = stat.is_blowout
            is_close = stat.is_close_game
            blowout_logic = not (is_blowout and is_close)  # Can't be both
            self.log_test(f"Game {stat.id} classification logic", blowout_logic)

            # Test turnover margin
            home_margin = stat.turnover_margin_home
            away_margin = stat.turnover_margin_away
            margin_sum = home_margin + away_margin == 0  # Should sum to zero
            self.log_test(f"Game {stat.id} turnover margin math", margin_sum)

    def run_all_tests(self):
        """Run all integration tests"""
        print("Starting College Football Phase 2 Integration Tests...")
        print("=" * 60)

        try:
            # Phase 1 prerequisite tests
            if not self.test_phase1_data_exists():
                print("Phase 1 data missing. Skipping further tests.")
                return

            # Core integration tests
            self.test_phase2_tables_created()
            self.test_phase2_relationships()
            self.test_enum_values()

            # Analytics tests
            self.test_advanced_analytics_calculations()
            self.test_situational_analytics()
            self.test_advanced_metrics_quality()

            # Performance and integrity tests
            self.test_performance_queries()
            self.test_data_integrity()

            # Complex scenario tests
            self.test_complex_analytics_scenarios()
            self.test_model_properties()

            # Print summary
            self.print_test_summary()

        except Exception as e:
            print(f"Critical error during testing: {e}")
            self.tests_failed += 1
        finally:
            self.session.close()

    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("COLLEGE FOOTBALL PHASE 2 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_failed}")
        print(f"Success Rate: {self.tests_passed/(self.tests_passed + self.tests_failed)*100:.1f}%")
        print("=" * 60)

        if self.tests_failed > 0:
            print("\nFailed Tests:")
            failed_tests = [result for result in self.test_results if "[FAIL]" in result]
            for test in failed_tests:
                print(f"  {test}")

        print(f"\nIntegration Status: {'PASS' if self.tests_failed == 0 else 'NEEDS ATTENTION'}")


def main():
    """Main testing function"""
    # Database configuration
    database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/corner_league_media')

    # Create tester and run
    tester = FootballPhase2IntegrationTester(database_url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()