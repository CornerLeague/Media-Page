#!/usr/bin/env python3
"""
Seed data for College Football Phase 2: Play-by-Play and Advanced Statistics

This script generates realistic football statistics data to demonstrate
the advanced analytics capabilities of the College Football Phase 2 system.
"""

import os
import sys
import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Dict, List, Tuple

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from models.base import Base
from models.college_football_phase1 import FootballTeam, FootballPlayer, FootballGame
from models.college_football_phase2 import (
    DriveData, PlayByPlay, FootballPlayerStatistics, FootballTeamStatistics,
    FootballAdvancedMetrics, FootballGameStatistics
)
from models.enums import (
    # Existing enums
    FootballPlayType, FootballPositionGroup, StatisticType, GameStatus,
    # Phase 2 enums
    PlayResult, DriveResult, FieldPosition, DownType, PlayDirection,
    PassLength, RushType, DefensivePlayType, PenaltyType, StatisticCategory,
    AdvancedMetricType, GameSituation
)


class FootballPhase2DataSeeder:
    """Generates realistic football statistics seed data"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Game data cache
        self.teams = []
        self.players = []
        self.games = []
        self.seasons = []

        # Statistics tracking
        self.drives_created = 0
        self.plays_created = 0
        self.player_stats_created = 0
        self.team_stats_created = 0
        self.advanced_metrics_created = 0
        self.game_stats_created = 0

    def load_existing_data(self):
        """Load existing football teams, players, and games"""
        print("Loading existing football data...")

        # Load teams
        self.teams = self.session.query(FootballTeam).all()
        print(f"Loaded {len(self.teams)} football teams")

        # Load players
        self.players = self.session.query(FootballPlayer).all()
        print(f"Loaded {len(self.players)} football players")

        # Load completed games from current season
        self.games = self.session.query(FootballGame).filter(
            FootballGame.status == GameStatus.FINAL
        ).all()
        print(f"Loaded {len(self.games)} completed games")

        # Load seasons (assuming we have current season data)
        from models.college import Season
        self.seasons = self.session.query(Season).all()
        print(f"Loaded {len(self.seasons)} seasons")

    def generate_game_drives_and_plays(self, game: FootballGame, num_drives_per_team: Tuple[int, int] = (8, 12)):
        """Generate realistic drives and play-by-play data for a game"""
        if not game.home_team_score or not game.away_team_score:
            # Generate random realistic scores
            game.home_team_score = random.randint(7, 42)
            game.away_team_score = random.randint(7, 42)

        drives = []
        all_plays = []

        # Determine total drives for each team
        home_drives = random.randint(*num_drives_per_team)
        away_drives = random.randint(*num_drives_per_team)

        # Alternate possessions starting with away team (common in football)
        drive_number = 1
        current_quarter = 1
        game_clock = 15 * 60  # 15 minutes per quarter in seconds

        for possession in range(home_drives + away_drives):
            if possession % 2 == 0:
                offense_team = game.away_team
                defense_team = game.home_team
                team_drive_num = (possession // 2) + 1
            else:
                offense_team = game.home_team
                defense_team = game.away_team
                team_drive_num = ((possession - 1) // 2) + 1

            # Generate drive
            drive, plays = self._generate_single_drive(
                game, offense_team, defense_team, drive_number,
                current_quarter, game_clock, team_drive_num
            )

            drives.append(drive)
            all_plays.extend(plays)

            drive_number += 1

            # Update game clock (approximate)
            drive_duration = drive.drive_duration_seconds or random.randint(120, 300)
            game_clock -= drive_duration

            # Handle quarter transitions
            if game_clock <= 0:
                current_quarter += 1
                game_clock = 15 * 60
                if current_quarter > 4:
                    break

        self.session.add_all(drives)
        self.session.add_all(all_plays)
        self.session.commit()

        self.drives_created += len(drives)
        self.plays_created += len(all_plays)

        return drives, all_plays

    def _generate_single_drive(self, game: FootballGame, offense_team: FootballTeam,
                             defense_team: FootballTeam, drive_number: int,
                             quarter: int, game_clock: int, team_drive_num: int):
        """Generate a single drive with realistic play sequence"""

        # Drive starting position
        start_yard_line = random.choices(
            [25, 30, 35, 40, 45, 50, 20, 15, 10],  # Field positions
            [25, 20, 15, 10, 8, 5, 10, 4, 3]       # Weights (touchbacks common)
        )[0]

        # Determine drive outcome based on field position and randomness
        drive_outcomes = [
            DriveResult.TOUCHDOWN, DriveResult.FIELD_GOAL, DriveResult.PUNT,
            DriveResult.TURNOVER_ON_DOWNS, DriveResult.INTERCEPTION, DriveResult.FUMBLE_LOST
        ]

        # Better field position = higher chance of scoring
        if start_yard_line >= 40:
            drive_result = random.choices(
                drive_outcomes,
                [30, 25, 25, 8, 7, 5]  # Higher scoring chance
            )[0]
        else:
            drive_result = random.choices(
                drive_outcomes,
                [15, 15, 40, 10, 10, 10]  # Lower scoring chance
            )[0]

        # Generate play sequence
        plays = []
        current_yard_line = start_yard_line
        current_down = 1
        yards_to_go = 10
        play_number = 1
        total_plays = 0
        total_yards = 0
        passing_yards = 0
        rushing_yards = 0
        first_downs = 0

        # Continue until drive ends
        while True:
            # Generate individual play
            play, play_yards, is_first_down, is_turnover, is_score = self._generate_single_play(
                game, offense_team, defense_team, drive_number, play_number,
                quarter, current_yard_line, current_down, yards_to_go
            )

            plays.append(play)
            total_plays += 1

            # Update drive statistics
            if play.is_pass:
                passing_yards += max(0, play_yards)
            elif play.is_rush:
                rushing_yards += max(0, play_yards)

            # Update field position
            current_yard_line = max(1, min(99, current_yard_line + play_yards))
            total_yards += max(0, play_yards)

            # Check for scoring or turnover
            if is_score or is_turnover:
                break

            # Check for first down
            if is_first_down or play_yards >= yards_to_go:
                current_down = 1
                yards_to_go = 10
                first_downs += 1
            else:
                current_down += 1
                yards_to_go -= play_yards

            # Check for turnover on downs
            if current_down > 4:
                drive_result = DriveResult.TURNOVER_ON_DOWNS
                break

            play_number += 1

        # Calculate drive duration (approximately 30-45 seconds per play)
        drive_duration = total_plays * random.randint(25, 50)

        # Determine points scored
        points_scored = 0
        if drive_result == DriveResult.TOUCHDOWN:
            points_scored = 7  # Assuming successful PAT
        elif drive_result == DriveResult.FIELD_GOAL:
            points_scored = 3

        # Create drive record
        drive = DriveData(
            game_id=game.id,
            drive_number=team_drive_num,
            offense_team_id=offense_team.id,
            defense_team_id=defense_team.id,
            start_quarter=quarter,
            end_quarter=quarter,
            drive_duration_seconds=drive_duration,
            start_yard_line=start_yard_line,
            end_yard_line=current_yard_line,
            start_field_position=self._get_field_position(start_yard_line),
            total_plays=total_plays,
            total_yards=total_yards,
            passing_plays=sum(1 for p in plays if p.is_pass),
            rushing_plays=sum(1 for p in plays if p.is_rush),
            passing_yards=passing_yards,
            rushing_yards=rushing_yards,
            drive_result=drive_result,
            points_scored=points_scored,
            first_downs_gained=first_downs,
            third_down_attempts=random.randint(0, 3),
            third_down_conversions=random.randint(0, 2),
            score_differential_start=random.randint(-14, 14),
            score_differential_end=random.randint(-14, 14),
            yards_per_play=Decimal(str(total_yards / total_plays)) if total_plays > 0 else Decimal('0'),
            explosive_play_count=sum(1 for p in plays if p.is_explosive_play),
            stuff_count=sum(1 for p in plays if p.is_stuff)
        )

        # Link plays to drive
        for play in plays:
            play.drive_id = drive.id

        return drive, plays

    def _generate_single_play(self, game: FootballGame, offense_team: FootballTeam,
                            defense_team: FootballTeam, drive_number: int, play_number: int,
                            quarter: int, yard_line: int, down: int, distance: int):
        """Generate a single play with realistic outcome"""

        # Determine play type based on down and distance
        if down <= 2:
            play_types = [FootballPlayType.RUSH, FootballPlayType.PASS]
            weights = [60, 40]  # Favor running on early downs
        elif distance <= 3:
            play_types = [FootballPlayType.RUSH, FootballPlayType.PASS]
            weights = [70, 30]  # Favor running in short yardage
        else:
            play_types = [FootballPlayType.RUSH, FootballPlayType.PASS]
            weights = [20, 80]  # Favor passing on long yardage

        play_type = random.choices(play_types, weights)[0]

        # Generate yards gained based on play type and situation
        if play_type == FootballPlayType.RUSH:
            # Rushing yards: typically 0-8 yards, occasional breakaway
            yards_gained = random.choices(
                [-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 18, 35, 60],
                [5, 8, 12, 15, 18, 16, 12, 8, 6, 4, 3, 2, 1, 0.3, 0.1]
            )[0]
            is_completion = None
            pass_length = None
            air_yards = None
            yards_after_catch = None
        else:  # Passing play
            # Determine if pass is complete (roughly 60% completion rate)
            is_completion = random.random() < 0.6

            if is_completion:
                # Completed pass yards
                yards_gained = random.choices(
                    [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 18, 22, 28, 40, 65],
                    [8, 10, 12, 14, 15, 12, 10, 8, 6, 5, 4, 3, 2, 1, 0.2]
                )[0]
                air_yards = int(yards_gained * 0.7)  # 70% air, 30% YAC
                yards_after_catch = yards_gained - air_yards
            else:
                # Incomplete pass
                yards_gained = 0
                air_yards = random.randint(5, 25)
                yards_after_catch = 0

            # Determine pass length
            if air_yards <= 0:
                pass_length = PassLength.SCREEN
            elif air_yards <= 9:
                pass_length = PassLength.SHORT
            elif air_yards <= 19:
                pass_length = PassLength.MEDIUM
            elif air_yards <= 39:
                pass_length = PassLength.DEEP
            else:
                pass_length = PassLength.BOMB

        # Determine play result
        play_result = PlayResult.GAIN
        is_turnover = False
        is_score = False
        points_scored = 0

        # Check for touchdowns
        if yard_line + yards_gained >= 100:
            play_result = PlayResult.TOUCHDOWN
            yards_gained = 100 - yard_line
            is_score = True
            points_scored = 6

        # Check for turnovers (low probability)
        elif random.random() < 0.02:  # 2% turnover rate
            if play_type == FootballPlayType.PASS:
                play_result = PlayResult.INTERCEPTION
            else:
                play_result = PlayResult.FUMBLE
            is_turnover = True

        # Check for sacks (if passing play)
        elif play_type == FootballPlayType.PASS and random.random() < 0.06:  # 6% sack rate
            play_result = PlayResult.SACK
            yards_gained = -random.randint(3, 10)

        # Check for negative plays
        elif yards_gained < 0:
            play_result = PlayResult.LOSS

        # Check for no gain
        elif yards_gained == 0:
            if play_type == FootballPlayType.PASS and not is_completion:
                play_result = PlayResult.INCOMPLETE
            else:
                play_result = PlayResult.NO_GAIN

        # Determine if first down achieved
        is_first_down = yards_gained >= distance

        # Create play record
        play = PlayByPlay(
            game_id=game.id,
            play_number=play_number,
            offense_team_id=offense_team.id,
            defense_team_id=defense_team.id,
            quarter=quarter,
            down=down,
            distance=distance,
            down_type=self._get_down_type(down, distance),
            yard_line=yard_line,
            yard_line_side="offense" if yard_line <= 50 else "defense",
            field_position=self._get_field_position(yard_line),
            play_type=play_type,
            play_description=self._generate_play_description(play_type, yards_gained, down, distance),
            play_result=play_result,
            yards_gained=yards_gained,
            yards_to_endzone_start=100 - yard_line,
            yards_to_endzone_end=max(0, 100 - yard_line - yards_gained),
            is_pass=(play_type == FootballPlayType.PASS),
            is_rush=(play_type == FootballPlayType.RUSH),
            is_special_teams=False,
            pass_length=pass_length,
            air_yards=air_yards,
            yards_after_catch=yards_after_catch,
            is_completion=is_completion,
            is_touchdown=is_score,
            points_scored=points_scored,
            is_turnover=is_turnover,
            is_red_zone=(yard_line >= 80),
            is_goal_line=(yard_line >= 95),
            is_explosive_play=(yards_gained >= 20 and play_type == FootballPlayType.PASS) or (yards_gained >= 10 and play_type == FootballPlayType.RUSH),
            is_stuff=(yards_gained < 0),
            score_differential=random.randint(-21, 21)
        )

        return play, yards_gained, is_first_down, is_turnover, is_score

    def _get_field_position(self, yard_line: int) -> FieldPosition:
        """Determine field position zone"""
        if yard_line <= 10:
            return FieldPosition.OWN_ENDZONE
        elif yard_line <= 50:
            return FieldPosition.OWN_TERRITORY
        elif yard_line <= 55:
            return FieldPosition.MIDFIELD
        elif yard_line <= 80:
            return FieldPosition.OPPONENT_TERRITORY
        elif yard_line <= 95:
            return FieldPosition.RED_ZONE
        else:
            return FieldPosition.GOAL_LINE

    def _get_down_type(self, down: int, distance: int) -> DownType:
        """Determine down and distance type"""
        if down == 1:
            return DownType.FIRST_DOWN
        elif down == 2:
            if distance <= 3:
                return DownType.SECOND_SHORT
            elif distance <= 7:
                return DownType.SECOND_MEDIUM
            else:
                return DownType.SECOND_LONG
        elif down == 3:
            if distance <= 3:
                return DownType.THIRD_SHORT
            elif distance <= 7:
                return DownType.THIRD_MEDIUM
            else:
                return DownType.THIRD_LONG
        else:
            return DownType.FOURTH_DOWN

    def _generate_play_description(self, play_type: FootballPlayType, yards: int, down: int, distance: int) -> str:
        """Generate realistic play description"""
        if play_type == FootballPlayType.RUSH:
            if yards < 0:
                return f"{down} & {distance}: Rush for {yards} yards (loss)"
            elif yards == 0:
                return f"{down} & {distance}: Rush for no gain"
            else:
                return f"{down} & {distance}: Rush for {yards} yards"
        else:  # Pass
            if yards == 0:
                return f"{down} & {distance}: Pass incomplete"
            elif yards < 0:
                return f"{down} & {distance}: Sack for {abs(yards)} yard loss"
            else:
                return f"{down} & {distance}: Pass complete for {yards} yards"

    def generate_player_statistics(self):
        """Generate season and game statistics for players"""
        print("Generating player statistics...")

        current_season = self.seasons[0] if self.seasons else None
        if not current_season:
            print("No season found, skipping player statistics")
            return

        # Generate season statistics for all players
        for player in self.players:
            self._generate_player_season_stats(player, current_season)

        # Generate game statistics for recent games
        recent_games = self.games[:10] if len(self.games) >= 10 else self.games
        for game in recent_games:
            # Get players from both teams
            home_players = [p for p in self.players if p.team_id == game.home_team_id]
            away_players = [p for p in self.players if p.team_id == game.away_team_id]

            for player in home_players[:22]:  # Starting lineup approximation
                self._generate_player_game_stats(player, game, current_season)

            for player in away_players[:22]:  # Starting lineup approximation
                self._generate_player_game_stats(player, game, current_season)

        self.session.commit()

    def _generate_player_season_stats(self, player: FootballPlayer, season):
        """Generate season statistics for a player based on position"""
        position_group = player.position_group
        games_played = random.randint(8, 12)
        games_started = random.randint(0, games_played) if position_group != FootballPositionGroup.QUARTERBACK else games_played

        stats = FootballPlayerStatistics(
            player_id=player.id,
            team_id=player.team_id,
            season_id=season.id,
            statistic_type=StatisticType.SEASON_TOTAL,
            position_group=position_group,
            games_played=games_played,
            games_started=games_started
        )

        # Generate position-specific statistics
        if position_group == FootballPositionGroup.QUARTERBACK:
            stats.passing_attempts = random.randint(200, 450)
            stats.passing_completions = int(stats.passing_attempts * random.uniform(0.55, 0.75))
            stats.passing_yards = random.randint(1800, 4500)
            stats.passing_touchdowns = random.randint(12, 35)
            stats.passing_interceptions = random.randint(3, 18)
            stats.passing_sacks = random.randint(15, 45)
            stats.rushing_attempts = random.randint(40, 120)
            stats.rushing_yards = random.randint(-50, 800)
            stats.rushing_touchdowns = random.randint(0, 12)

        elif position_group == FootballPositionGroup.RUNNING_BACK:
            stats.rushing_attempts = random.randint(80, 250)
            stats.rushing_yards = random.randint(300, 1800)
            stats.rushing_touchdowns = random.randint(2, 20)
            stats.receiving_targets = random.randint(20, 80)
            stats.receiving_receptions = int(stats.receiving_targets * random.uniform(0.6, 0.85))
            stats.receiving_yards = random.randint(100, 800)
            stats.receiving_touchdowns = random.randint(0, 8)

        elif position_group == FootballPositionGroup.WIDE_RECEIVER:
            stats.receiving_targets = random.randint(40, 150)
            stats.receiving_receptions = int(stats.receiving_targets * random.uniform(0.55, 0.75))
            stats.receiving_yards = random.randint(300, 1500)
            stats.receiving_touchdowns = random.randint(2, 15)
            stats.yards_after_catch = int(stats.receiving_yards * random.uniform(0.3, 0.5))

        elif position_group == FootballPositionGroup.TIGHT_END:
            stats.receiving_targets = random.randint(25, 80)
            stats.receiving_receptions = int(stats.receiving_targets * random.uniform(0.65, 0.8))
            stats.receiving_yards = random.randint(200, 800)
            stats.receiving_touchdowns = random.randint(1, 10)

        elif position_group in [FootballPositionGroup.LINEBACKER, FootballPositionGroup.DEFENSIVE_BACK]:
            stats.tackles_total = random.randint(40, 120)
            stats.tackles_solo = int(stats.tackles_total * random.uniform(0.6, 0.8))
            stats.tackles_assisted = stats.tackles_total - stats.tackles_solo
            stats.tackles_for_loss = random.randint(2, 15)
            stats.sacks = Decimal(str(random.uniform(0, 12)))
            stats.interceptions = random.randint(0, 8)
            stats.passes_defended = random.randint(3, 20)

        elif position_group == FootballPositionGroup.DEFENSIVE_LINE:
            stats.tackles_total = random.randint(25, 80)
            stats.tackles_solo = int(stats.tackles_total * random.uniform(0.7, 0.9))
            stats.tackles_assisted = stats.tackles_total - stats.tackles_solo
            stats.tackles_for_loss = random.randint(5, 25)
            stats.sacks = Decimal(str(random.uniform(2, 15)))
            stats.quarterback_hits = random.randint(8, 35)
            stats.fumbles_forced = random.randint(0, 5)

        self.session.add(stats)
        self.player_stats_created += 1

    def _generate_player_game_stats(self, player: FootballPlayer, game: FootballGame, season):
        """Generate game statistics for a player"""
        position_group = player.position_group

        stats = FootballPlayerStatistics(
            player_id=player.id,
            game_id=game.id,
            team_id=player.team_id,
            season_id=season.id,
            statistic_type=StatisticType.GAME_STATS,
            position_group=position_group,
            games_played=1,
            games_started=1 if random.random() < 0.5 else 0
        )

        # Scale down season stats for single game
        if position_group == FootballPositionGroup.QUARTERBACK:
            stats.passing_attempts = random.randint(15, 45)
            stats.passing_completions = int(stats.passing_attempts * random.uniform(0.5, 0.8))
            stats.passing_yards = random.randint(150, 450)
            stats.passing_touchdowns = random.randint(0, 4)
            stats.passing_interceptions = random.randint(0, 3)
            stats.rushing_attempts = random.randint(3, 15)
            stats.rushing_yards = random.randint(-10, 80)

        elif position_group == FootballPositionGroup.RUNNING_BACK:
            stats.rushing_attempts = random.randint(8, 25)
            stats.rushing_yards = random.randint(20, 180)
            stats.rushing_touchdowns = random.randint(0, 3)
            stats.receiving_targets = random.randint(2, 8)
            stats.receiving_receptions = min(stats.receiving_targets, random.randint(1, 6))
            stats.receiving_yards = random.randint(0, 80)

        elif position_group == FootballPositionGroup.WIDE_RECEIVER:
            stats.receiving_targets = random.randint(3, 12)
            stats.receiving_receptions = min(stats.receiving_targets, random.randint(1, 8))
            stats.receiving_yards = random.randint(0, 150)
            stats.receiving_touchdowns = random.randint(0, 2)

        elif position_group in [FootballPositionGroup.LINEBACKER, FootballPositionGroup.DEFENSIVE_BACK]:
            stats.tackles_total = random.randint(3, 12)
            stats.tackles_solo = int(stats.tackles_total * random.uniform(0.6, 0.8))
            stats.tackles_assisted = stats.tackles_total - stats.tackles_solo
            stats.tackles_for_loss = random.randint(0, 3)
            stats.sacks = Decimal(str(random.uniform(0, 2)))
            stats.interceptions = random.randint(0, 2)
            stats.passes_defended = random.randint(0, 4)

        self.session.add(stats)
        self.player_stats_created += 1

    def generate_team_statistics(self):
        """Generate team-level statistics"""
        print("Generating team statistics...")

        current_season = self.seasons[0] if self.seasons else None
        if not current_season:
            print("No season found, skipping team statistics")
            return

        # Generate season statistics for all teams
        for team in self.teams:
            self._generate_team_season_stats(team, current_season)

        # Generate game statistics for recent games
        for game in self.games[:10]:
            self._generate_team_game_stats(game.home_team, game.away_team, game, current_season)

        self.session.commit()

    def _generate_team_season_stats(self, team: FootballTeam, season):
        """Generate season statistics for a team"""
        games_played = random.randint(10, 15)

        stats = FootballTeamStatistics(
            team_id=team.id,
            season_id=season.id,
            statistic_type=StatisticType.SEASON_TOTAL,
            games_played=games_played,
            points_for=random.randint(250, 450),
            points_against=random.randint(180, 380),
            total_plays=random.randint(800, 1100),
            total_yards=random.randint(3500, 6000),
            first_downs=random.randint(180, 280),
            passing_attempts=random.randint(300, 500),
            passing_completions=random.randint(180, 350),
            passing_yards=random.randint(2000, 4000),
            passing_touchdowns=random.randint(15, 40),
            passing_interceptions=random.randint(8, 25),
            rushing_attempts=random.randint(400, 600),
            rushing_yards=random.randint(1200, 3000),
            rushing_touchdowns=random.randint(10, 35),
            third_down_attempts=random.randint(120, 180),
            third_down_conversions=random.randint(45, 90),
            red_zone_attempts=random.randint(35, 60),
            red_zone_scores=random.randint(25, 50),
            turnovers_lost=random.randint(15, 35),
            turnovers_gained=random.randint(15, 35),
            penalties=random.randint(80, 130),
            penalty_yards=random.randint(600, 1100)
        )

        self.session.add(stats)
        self.team_stats_created += 1

    def _generate_team_game_stats(self, home_team: FootballTeam, away_team: FootballTeam,
                                game: FootballGame, season):
        """Generate game statistics for both teams"""
        # Home team stats
        home_stats = FootballTeamStatistics(
            team_id=home_team.id,
            opponent_id=away_team.id,
            game_id=game.id,
            season_id=season.id,
            statistic_type=StatisticType.GAME_STATS,
            is_home_team=True,
            games_played=1,
            points_for=game.home_team_score or random.randint(7, 42),
            points_against=game.away_team_score or random.randint(7, 42),
            total_plays=random.randint(60, 85),
            total_yards=random.randint(250, 550),
            first_downs=random.randint(12, 25),
            passing_attempts=random.randint(20, 45),
            passing_completions=random.randint(12, 30),
            passing_yards=random.randint(120, 350),
            passing_touchdowns=random.randint(0, 4),
            passing_interceptions=random.randint(0, 3),
            rushing_attempts=random.randint(25, 45),
            rushing_yards=random.randint(80, 250),
            rushing_touchdowns=random.randint(0, 3),
            third_down_attempts=random.randint(8, 15),
            third_down_conversions=random.randint(3, 10),
            turnovers_lost=random.randint(0, 4),
            penalties=random.randint(4, 12),
            penalty_yards=random.randint(30, 100)
        )

        # Away team stats
        away_stats = FootballTeamStatistics(
            team_id=away_team.id,
            opponent_id=home_team.id,
            game_id=game.id,
            season_id=season.id,
            statistic_type=StatisticType.GAME_STATS,
            is_home_team=False,
            games_played=1,
            points_for=game.away_team_score or random.randint(7, 42),
            points_against=game.home_team_score or random.randint(7, 42),
            total_plays=random.randint(60, 85),
            total_yards=random.randint(250, 550),
            first_downs=random.randint(12, 25),
            passing_attempts=random.randint(20, 45),
            passing_completions=random.randint(12, 30),
            passing_yards=random.randint(120, 350),
            passing_touchdowns=random.randint(0, 4),
            passing_interceptions=random.randint(0, 3),
            rushing_attempts=random.randint(25, 45),
            rushing_yards=random.randint(80, 250),
            rushing_touchdowns=random.randint(0, 3),
            third_down_attempts=random.randint(8, 15),
            third_down_conversions=random.randint(3, 10),
            turnovers_lost=random.randint(0, 4),
            penalties=random.randint(4, 12),
            penalty_yards=random.randint(30, 100)
        )

        self.session.add(home_stats)
        self.session.add(away_stats)
        self.team_stats_created += 2

    def generate_advanced_metrics(self):
        """Generate advanced football metrics"""
        print("Generating advanced metrics...")

        current_season = self.seasons[0] if self.seasons else None
        if not current_season:
            print("No season found, skipping advanced metrics")
            return

        # Generate team-level advanced metrics
        for team in self.teams[:10]:  # Limit for demo purposes
            self._generate_team_advanced_metrics(team, current_season)

        # Generate player-level advanced metrics for key positions
        qbs = [p for p in self.players if p.position_group == FootballPositionGroup.QUARTERBACK][:5]
        for qb in qbs:
            self._generate_player_advanced_metrics(qb, current_season)

        self.session.commit()

    def _generate_team_advanced_metrics(self, team: FootballTeam, season):
        """Generate advanced metrics for a team"""
        metrics_to_generate = [
            (AdvancedMetricType.EPA, StatisticCategory.EFFICIENCY),
            (AdvancedMetricType.SUCCESS_RATE, StatisticCategory.EFFICIENCY),
            (AdvancedMetricType.YARDS_PER_PLAY, StatisticCategory.EFFICIENCY),
            (AdvancedMetricType.THIRD_DOWN_CONVERSION, StatisticCategory.SITUATIONAL),
            (AdvancedMetricType.RED_ZONE_EFFICIENCY, StatisticCategory.SITUATIONAL),
            (AdvancedMetricType.PRESSURE_RATE, StatisticCategory.PASS_DEFENSE),
        ]

        for metric_type, category in metrics_to_generate:
            metric = FootballAdvancedMetrics(
                team_id=team.id,
                season_id=season.id,
                metric_type=metric_type,
                metric_category=category,
                metric_value=self._generate_metric_value(metric_type),
                sample_size=random.randint(50, 200),
                percentile_rank=Decimal(str(random.uniform(10, 90))),
                z_score=Decimal(str(random.uniform(-2.5, 2.5)))
            )

            self.session.add(metric)
            self.advanced_metrics_created += 1

    def _generate_player_advanced_metrics(self, player: FootballPlayer, season):
        """Generate advanced metrics for a player"""
        if player.position_group == FootballPositionGroup.QUARTERBACK:
            metrics_to_generate = [
                (AdvancedMetricType.EPA, StatisticCategory.PASSING),
                (AdvancedMetricType.SUCCESS_RATE, StatisticCategory.PASSING),
                (AdvancedMetricType.PRESSURE_RATE, StatisticCategory.PASSING),
            ]
        else:
            return  # Skip other positions for now

        for metric_type, category in metrics_to_generate:
            metric = FootballAdvancedMetrics(
                player_id=player.id,
                season_id=season.id,
                metric_type=metric_type,
                metric_category=category,
                position_group=player.position_group,
                metric_value=self._generate_metric_value(metric_type),
                sample_size=random.randint(100, 400),
                percentile_rank=Decimal(str(random.uniform(15, 85))),
                z_score=Decimal(str(random.uniform(-2.0, 2.0)))
            )

            self.session.add(metric)
            self.advanced_metrics_created += 1

    def _generate_metric_value(self, metric_type: AdvancedMetricType) -> Decimal:
        """Generate realistic metric value based on type"""
        if metric_type == AdvancedMetricType.EPA:
            return Decimal(str(random.uniform(-0.5, 0.5)))
        elif metric_type == AdvancedMetricType.SUCCESS_RATE:
            return Decimal(str(random.uniform(0.35, 0.65)))
        elif metric_type == AdvancedMetricType.YARDS_PER_PLAY:
            return Decimal(str(random.uniform(4.5, 7.5)))
        elif metric_type == AdvancedMetricType.THIRD_DOWN_CONVERSION:
            return Decimal(str(random.uniform(0.25, 0.55)))
        elif metric_type == AdvancedMetricType.RED_ZONE_EFFICIENCY:
            return Decimal(str(random.uniform(0.45, 0.85)))
        elif metric_type == AdvancedMetricType.PRESSURE_RATE:
            return Decimal(str(random.uniform(0.15, 0.35)))
        else:
            return Decimal(str(random.uniform(0, 1)))

    def generate_game_statistics(self):
        """Generate comprehensive game-level statistics"""
        print("Generating game statistics...")

        current_season = self.seasons[0] if self.seasons else None
        if not current_season:
            print("No season found, skipping game statistics")
            return

        for game in self.games[:10]:  # Limit for demo purposes
            self._generate_comprehensive_game_stats(game, current_season)

        self.session.commit()

    def _generate_comprehensive_game_stats(self, game: FootballGame, season):
        """Generate comprehensive statistics for a game"""
        home_score = game.home_team_score or random.randint(7, 42)
        away_score = game.away_team_score or random.randint(7, 42)

        winner_id = None
        if home_score > away_score:
            winner_id = game.home_team_id
        elif away_score > home_score:
            winner_id = game.away_team_id

        stats = FootballGameStatistics(
            game_id=game.id,
            home_team_id=game.home_team_id,
            away_team_id=game.away_team_id,
            season_id=season.id,
            home_score=home_score,
            away_score=away_score,
            winner_id=winner_id,
            margin_of_victory=abs(home_score - away_score),
            total_plays=random.randint(120, 170),
            home_total_yards=random.randint(250, 550),
            away_total_yards=random.randint(250, 550),
            home_passing_yards=random.randint(120, 350),
            away_passing_yards=random.randint(120, 350),
            home_rushing_yards=random.randint(80, 250),
            away_rushing_yards=random.randint(80, 250),
            home_first_downs=random.randint(12, 25),
            away_first_downs=random.randint(12, 25),
            home_third_down_attempts=random.randint(8, 15),
            home_third_down_conversions=random.randint(3, 10),
            away_third_down_attempts=random.randint(8, 15),
            away_third_down_conversions=random.randint(3, 10),
            home_turnovers=random.randint(0, 4),
            away_turnovers=random.randint(0, 4),
            home_penalties=random.randint(4, 12),
            home_penalty_yards=random.randint(30, 100),
            away_penalties=random.randint(4, 12),
            away_penalty_yards=random.randint(30, 100),
            home_time_of_possession_seconds=random.randint(1600, 2000),
            away_time_of_possession_seconds=random.randint(1600, 2000),
            conference_game=random.random() < 0.7,  # 70% are conference games
            rivalry_game=random.random() < 0.2,     # 20% are rivalry games
            play_by_play_complete=random.random() < 0.8  # 80% have complete PBP
        )

        self.session.add(stats)
        self.game_stats_created += 1

    def run_seeding(self):
        """Run the complete seeding process"""
        print("Starting College Football Phase 2 data seeding...")

        try:
            # Load existing data
            self.load_existing_data()

            if not self.teams or not self.players or not self.games:
                print("Missing required base data (teams, players, or games). Please run Phase 1 seeding first.")
                return

            # Generate play-by-play data for a sample of games
            print(f"Generating play-by-play data for {min(5, len(self.games))} games...")
            for game in self.games[:5]:  # Limit to 5 games for demo
                self.generate_game_drives_and_plays(game)

            # Generate statistics
            self.generate_player_statistics()
            self.generate_team_statistics()
            self.generate_advanced_metrics()
            self.generate_game_statistics()

            # Print summary
            print("\n" + "="*60)
            print("COLLEGE FOOTBALL PHASE 2 SEEDING COMPLETE")
            print("="*60)
            print(f"Drives created: {self.drives_created}")
            print(f"Plays created: {self.plays_created}")
            print(f"Player statistics created: {self.player_stats_created}")
            print(f"Team statistics created: {self.team_stats_created}")
            print(f"Advanced metrics created: {self.advanced_metrics_created}")
            print(f"Game statistics created: {self.game_stats_created}")
            print("="*60)

        except Exception as e:
            print(f"Error during seeding: {e}")
            self.session.rollback()
            raise
        finally:
            self.session.close()


def main():
    """Main seeding function"""
    # Database configuration
    database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/corner_league_media')

    # Create seeder and run
    seeder = FootballPhase2DataSeeder(database_url)
    seeder.run_seeding()


if __name__ == "__main__":
    main()