#!/usr/bin/env python3
"""
College Basketball Phase 4: Comprehensive Seed Data Generator
===========================================================

Generates realistic sample data for the Phase 4 Statistics & Rankings implementation.

Includes:
- Diverse player rosters with realistic attributes
- Season and game-level team statistics
- Individual player performance data
- Multiple ranking systems (AP, Coaches, NET, KenPom)
- Advanced analytics and efficiency metrics
- Detailed season records with various breakdowns

Features:
- Position-appropriate statistics
- Conference-realistic performance levels
- Transfer portal and eligibility tracking
- Recruiting information and NBA prospects
- Historical ranking trends
- Advanced analytics calculations
"""

import sqlite3
import json
import random
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Tuple, Any
import uuid


class Phase4SeedDataGenerator:
    """Generates comprehensive seed data for Phase 4 models"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.seed_data = {
            "players": [],
            "team_statistics": [],
            "player_statistics": [],
            "rankings": [],
            "advanced_metrics": [],
            "season_records": []
        }

        # Realistic player names and attributes
        self.player_templates = {
            "point_guard": {
                "names": [
                    ("Marcus", "Johnson"), ("Tyler", "Williams"), ("Chris", "Davis"), ("Kevin", "Brown"),
                    ("Jordan", "Wilson"), ("Isaiah", "Miller"), ("DeShawn", "Garcia"), ("Malik", "Rodriguez"),
                    ("Ja'Marcus", "Martinez"), ("Tyrese", "Anderson"), ("Jalen", "Taylor"), ("Zion", "Thomas")
                ],
                "height_range": (69, 75),  # 5'9" to 6'3"
                "weight_range": (160, 200),
                "stat_tendencies": {
                    "points": (8, 18), "assists": (4, 9), "rebounds": (2, 6),
                    "steals": (1, 3), "turnovers": (2, 5), "fg_pct": (0.42, 0.52),
                    "three_pct": (0.32, 0.42), "ft_pct": (0.75, 0.88)
                }
            },
            "shooting_guard": {
                "names": [
                    ("Anthony", "Jackson"), ("Michael", "White"), ("Jamal", "Harris"), ("Donovan", "Martin"),
                    ("Klay", "Thompson"), ("Devin", "Walker"), ("Bradley", "Hill"), ("CJ", "Allen"),
                    ("Jaylen", "King"), ("Terrence", "Wright"), ("Xavier", "Lopez"), ("Damian", "Lee")
                ],
                "height_range": (71, 78),  # 5'11" to 6'6"
                "weight_range": (175, 220),
                "stat_tendencies": {
                    "points": (12, 22), "assists": (2, 6), "rebounds": (3, 7),
                    "steals": (1, 2), "turnovers": (1, 4), "fg_pct": (0.44, 0.54),
                    "three_pct": (0.35, 0.45), "ft_pct": (0.78, 0.90)
                }
            },
            "small_forward": {
                "names": [
                    ("LeBron", "James"), ("Kevin", "Durant"), ("Jimmy", "Butler"), ("Jayson", "Tatum"),
                    ("Paul", "George"), ("Kawhi", "Leonard"), ("Brandon", "Ingram"), ("Jaylen", "Brown"),
                    ("DeMar", "DeRozan"), ("Khris", "Middleton"), ("Gordon", "Hayward"), ("Otto", "Porter")
                ],
                "height_range": (75, 80),  # 6'3" to 6'8"
                "weight_range": (200, 240),
                "stat_tendencies": {
                    "points": (10, 20), "assists": (2, 5), "rebounds": (4, 8),
                    "steals": (1, 2), "turnovers": (1, 3), "fg_pct": (0.45, 0.55),
                    "three_pct": (0.32, 0.42), "ft_pct": (0.75, 0.85)
                }
            },
            "power_forward": {
                "names": [
                    ("Anthony", "Davis"), ("Giannis", "Antetokounmpo"), ("Blake", "Griffin"), ("Julius", "Randle"),
                    ("Tobias", "Harris"), ("Aaron", "Gordon"), ("John", "Collins"), ("Kristaps", "Porzingis"),
                    ("Pascal", "Siakam"), ("Jayson", "Tatum"), ("Zion", "Williamson"), ("Paolo", "Banchero")
                ],
                "height_range": (78, 83),  # 6'6" to 6'11"
                "weight_range": (220, 270),
                "stat_tendencies": {
                    "points": (8, 18), "assists": (1, 4), "rebounds": (6, 12),
                    "steals": (0, 2), "turnovers": (1, 3), "fg_pct": (0.47, 0.57),
                    "three_pct": (0.28, 0.38), "ft_pct": (0.70, 0.82)
                }
            },
            "center": {
                "names": [
                    ("Joel", "Embiid"), ("Nikola", "Jokic"), ("Rudy", "Gobert"), ("Karl-Anthony", "Towns"),
                    ("Bam", "Adebayo"), ("Deandre", "Ayton"), ("Jaren", "Jackson"), ("Myles", "Turner"),
                    ("Brook", "Lopez"), ("Clint", "Capela"), ("Robert", "Williams"), ("Alperen", "Sengun")
                ],
                "height_range": (80, 86),  # 6'8" to 7'2"
                "weight_range": (240, 300),
                "stat_tendencies": {
                    "points": (6, 16), "assists": (0, 3), "rebounds": (8, 15),
                    "steals": (0, 1), "turnovers": (1, 3), "blocks": (1, 4),
                    "fg_pct": (0.50, 0.65), "three_pct": (0.20, 0.35), "ft_pct": (0.65, 0.80)
                }
            }
        }

        # Conference performance tiers for realistic variation
        self.conference_tiers = {
            "power_five": {
                "efficiency_range": (110, 125),
                "ranking_range": (1, 68),
                "record_quality": "high"
            },
            "mid_major": {
                "efficiency_range": (100, 115),
                "ranking_range": (50, 200),
                "record_quality": "medium"
            },
            "low_major": {
                "efficiency_range": (90, 105),
                "ranking_range": (150, 350),
                "record_quality": "low"
            }
        }

    def generate_player_id(self) -> str:
        """Generate unique player ID"""
        return f"player_{uuid.uuid4().hex[:8]}"

    def generate_statistic_id(self, prefix: str) -> str:
        """Generate unique statistic ID"""
        return f"{prefix}_{uuid.uuid4().hex[:8]}"

    def get_teams_and_context(self) -> List[Tuple[str, str, str, str]]:
        """Get teams with their conference context for realistic seeding"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ct.id, ct.name, c.name as college_name, cc.conference_type
            FROM college_teams ct
            JOIN colleges c ON ct.college_id = c.id
            JOIN college_conferences cc ON c.conference_id = cc.id
            ORDER BY cc.conference_type, c.name
            LIMIT 50
        """)

        teams = cursor.fetchall()
        conn.close()
        return teams

    def get_current_academic_year(self) -> Tuple[str, str]:
        """Get current academic year"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, name FROM academic_years WHERE status = 'current' LIMIT 1")
        result = cursor.fetchone()
        conn.close()

        if result:
            return result
        else:
            # Create a current academic year if none exists
            year_id = f"academic_year_{uuid.uuid4().hex[:8]}"
            return year_id, "2024-25"

    def generate_players_for_team(self, team_id: str, team_name: str, academic_year_id: str,
                                  conference_type: str) -> List[Dict[str, Any]]:
        """Generate realistic player roster for a team"""
        players = []
        roster_size = random.randint(12, 15)  # Typical roster size

        # Position distribution (roughly realistic)
        positions = (
            ["point_guard"] * 2 +
            ["shooting_guard"] * 3 +
            ["small_forward"] * 3 +
            ["power_forward"] * 3 +
            ["center"] * 2 +
            ["guard"] * 1 +  # Combo guard
            ["forward"] * 1   # Combo forward
        )

        for i in range(roster_size):
            # Select position and template
            position = positions[i] if i < len(positions) else random.choice(list(self.player_templates.keys()))
            if position in ["guard", "forward"]:
                # Combo positions - pick randomly from appropriate positions
                if position == "guard":
                    template_pos = random.choice(["point_guard", "shooting_guard"])
                else:
                    template_pos = random.choice(["small_forward", "power_forward"])
            else:
                template_pos = position

            template = self.player_templates[template_pos]

            # Generate player attributes
            first_name, last_name = random.choice(template["names"])
            full_name = f"{first_name} {last_name}"

            # Add some unique variation to names
            if random.random() < 0.3:
                suffixes = ["Jr.", "II", "III"]
                full_name += f" {random.choice(suffixes)}"

            # Physical attributes
            height = random.randint(*template["height_range"])
            weight = random.randint(*template["weight_range"])

            # Academic attributes
            player_classes = ["freshman", "sophomore", "junior", "senior", "graduate"]
            class_weights = [0.3, 0.25, 0.25, 0.15, 0.05]  # More underclassmen
            player_class = random.choices(player_classes, weights=class_weights)[0]

            # Eligibility and transfer status
            eligibility_status = "eligible"
            is_transfer = False
            if random.random() < 0.15:  # 15% transfer rate
                is_transfer = True
                if random.random() < 0.3:
                    eligibility_status = "graduate_transfer"

            # Recruiting information
            recruiting_stars = None
            recruiting_rank = None
            if player_class in ["freshman", "sophomore"]:
                if conference_type == "power_five":
                    recruiting_stars = random.choices([3, 4, 5], weights=[0.4, 0.5, 0.1])[0]
                    if recruiting_stars == 5:
                        recruiting_rank = random.randint(1, 30)
                    elif recruiting_stars == 4:
                        recruiting_rank = random.randint(31, 150)
                else:
                    recruiting_stars = random.choices([2, 3, 4], weights=[0.3, 0.6, 0.1])[0]

            # NBA prospects
            nba_draft_eligible = False
            if player_class in ["junior", "senior", "graduate"] and recruiting_stars in [4, 5]:
                nba_draft_eligible = random.random() < 0.4

            player_data = {
                "id": self.generate_player_id(),
                "team_id": team_id,
                "academic_year_id": academic_year_id,
                "first_name": first_name,
                "last_name": last_name,
                "full_name": full_name,
                "jersey_number": i + 1,
                "primary_position": position,
                "secondary_position": None,
                "height_inches": height,
                "weight_pounds": weight,
                "birth_date": (date.today() - timedelta(days=random.randint(6570, 8030))).isoformat(),  # 18-22 years old
                "hometown": f"City {random.randint(1, 100)}",
                "home_state": random.choice(["CA", "TX", "FL", "NY", "IL", "PA", "OH", "GA", "NC", "MI"]),
                "home_country": "USA",
                "high_school": f"{first_name} {last_name} High School",
                "previous_college": f"Previous University {i}" if is_transfer else None,
                "player_class": player_class,
                "eligibility_status": eligibility_status,
                "years_of_eligibility_remaining": max(0, 4 - player_classes.index(player_class)),
                "is_transfer": is_transfer,
                "transfer_from_college_id": None,
                "transfer_year": 2024 if is_transfer else None,
                "recruiting_class_year": 2024 - player_classes.index(player_class) if player_class != "graduate" else None,
                "recruiting_stars": recruiting_stars,
                "recruiting_rank_national": recruiting_rank,
                "recruiting_rank_position": recruiting_rank // 5 if recruiting_rank else None,
                "nba_draft_eligible": nba_draft_eligible,
                "nba_draft_year": 2025 if nba_draft_eligible else None,
                "external_id": f"ext_{team_id}_{i+1}",
                "espn_player_id": f"espn_{team_id}_{i+1}",
                "ncaa_player_id": f"ncaa_{team_id}_{i+1}",
                "photo_url": f"https://example.com/players/{team_id}_{i+1}.jpg",
                "bio": f"{full_name} is a talented {position.replace('_', ' ')} from {player_data.get('hometown', 'Unknown')}.",
                "is_active": True,
                "injury_status": "Day-to-Day" if random.random() < 0.05 else None
            }

            players.append(player_data)

        return players

    def generate_team_statistics(self, team_id: str, team_name: str, academic_year_id: str,
                                conference_type: str) -> List[Dict[str, Any]]:
        """Generate realistic team statistics"""
        statistics = []

        # Get tier-appropriate performance levels
        tier = self.conference_tiers.get(conference_type, self.conference_tiers["mid_major"])

        # Season totals
        games_played = random.randint(28, 32)

        # Base stats adjusted for conference level
        base_efficiency = random.uniform(*tier["efficiency_range"])

        # Points per game (based on efficiency and pace)
        pace = random.uniform(65, 75)
        points_per_game = (base_efficiency * pace) / 100
        total_points = points_per_game * games_played

        # Field goal statistics
        fga_per_game = random.uniform(55, 70)
        fg_pct = random.uniform(0.42, 0.52)
        fgm_per_game = fga_per_game * fg_pct

        # Three-point statistics
        three_rate = random.uniform(0.35, 0.45)  # Percentage of shots that are 3s
        three_attempts_per_game = fga_per_game * three_rate
        three_pct = random.uniform(0.30, 0.40)
        three_makes_per_game = three_attempts_per_game * three_pct

        # Free throw statistics
        ft_rate = random.uniform(0.25, 0.35)  # FTA/FGA
        fta_per_game = fga_per_game * ft_rate
        ft_pct = random.uniform(0.65, 0.80)
        ftm_per_game = fta_per_game * ft_pct

        # Rebounding
        total_rebounds_per_game = random.uniform(32, 42)
        offensive_reb_rate = random.uniform(0.25, 0.35)
        offensive_rebounds_per_game = total_rebounds_per_game * offensive_reb_rate
        defensive_rebounds_per_game = total_rebounds_per_game - offensive_rebounds_per_game

        # Other statistics
        assists_per_game = random.uniform(10, 18)
        steals_per_game = random.uniform(5, 10)
        blocks_per_game = random.uniform(2, 6)
        turnovers_per_game = random.uniform(10, 16)
        fouls_per_game = random.uniform(16, 22)

        # Season totals
        season_stats = {
            "id": self.generate_statistic_id("team_season"),
            "team_id": team_id,
            "academic_year_id": academic_year_id,
            "season_id": None,
            "game_id": None,
            "statistic_type": "season_total",
            "games_played": games_played,
            "points": round(total_points, 2),
            "field_goals_made": round(fgm_per_game * games_played, 2),
            "field_goals_attempted": round(fga_per_game * games_played, 2),
            "field_goal_percentage": round(fg_pct, 3),
            "three_pointers_made": round(three_makes_per_game * games_played, 2),
            "three_pointers_attempted": round(three_attempts_per_game * games_played, 2),
            "three_point_percentage": round(three_pct, 3),
            "free_throws_made": round(ftm_per_game * games_played, 2),
            "free_throws_attempted": round(fta_per_game * games_played, 2),
            "free_throw_percentage": round(ft_pct, 3),
            "offensive_rebounds": round(offensive_rebounds_per_game * games_played, 2),
            "defensive_rebounds": round(defensive_rebounds_per_game * games_played, 2),
            "total_rebounds": round(total_rebounds_per_game * games_played, 2),
            "assists": round(assists_per_game * games_played, 2),
            "steals": round(steals_per_game * games_played, 2),
            "blocks": round(blocks_per_game * games_played, 2),
            "turnovers": round(turnovers_per_game * games_played, 2),
            "personal_fouls": round(fouls_per_game * games_played, 2),
            "points_allowed": round(random.uniform(65, 80) * games_played, 2),
            "stats_date": date.today().isoformat()
        }

        # Season averages
        season_averages = {
            "id": self.generate_statistic_id("team_avg"),
            "team_id": team_id,
            "academic_year_id": academic_year_id,
            "season_id": None,
            "game_id": None,
            "statistic_type": "season_average",
            "games_played": games_played,
            "points": round(points_per_game, 2),
            "field_goals_made": round(fgm_per_game, 2),
            "field_goals_attempted": round(fga_per_game, 2),
            "field_goal_percentage": round(fg_pct, 3),
            "three_pointers_made": round(three_makes_per_game, 2),
            "three_pointers_attempted": round(three_attempts_per_game, 2),
            "three_point_percentage": round(three_pct, 3),
            "free_throws_made": round(ftm_per_game, 2),
            "free_throws_attempted": round(fta_per_game, 2),
            "free_throw_percentage": round(ft_pct, 3),
            "offensive_rebounds": round(offensive_rebounds_per_game, 2),
            "defensive_rebounds": round(defensive_rebounds_per_game, 2),
            "total_rebounds": round(total_rebounds_per_game, 2),
            "assists": round(assists_per_game, 2),
            "steals": round(steals_per_game, 2),
            "blocks": round(blocks_per_game, 2),
            "turnovers": round(turnovers_per_game, 2),
            "personal_fouls": round(fouls_per_game, 2),
            "points_allowed": round(random.uniform(65, 80), 2),
            "stats_date": date.today().isoformat()
        }

        statistics.extend([season_stats, season_averages])
        return statistics

    def generate_player_statistics(self, players: List[Dict[str, Any]], academic_year_id: str) -> List[Dict[str, Any]]:
        """Generate realistic player statistics"""
        statistics = []

        for player in players:
            position = player["primary_position"]
            # Handle combo positions
            if position in ["guard", "forward"]:
                if position == "guard":
                    template_pos = random.choice(["point_guard", "shooting_guard"])
                else:
                    template_pos = random.choice(["small_forward", "power_forward"])
            else:
                template_pos = position

            if template_pos not in self.player_templates:
                template_pos = "small_forward"  # Default

            tendencies = self.player_templates[template_pos]["stat_tendencies"]

            # Games played (starters play more)
            is_starter = player["jersey_number"] <= 8  # Assume first 8 are main rotation
            games_played = random.randint(25, 30) if is_starter else random.randint(15, 28)
            games_started = random.randint(20, games_played) if is_starter else random.randint(0, 5)

            # Minutes played
            if is_starter:
                minutes_per_game = random.uniform(25, 35)
            else:
                minutes_per_game = random.uniform(10, 25)

            # Generate statistics based on position tendencies
            points_per_game = random.uniform(*tendencies["points"])
            assists_per_game = random.uniform(*tendencies["assists"])
            rebounds_per_game = random.uniform(*tendencies["rebounds"])
            steals_per_game = random.uniform(*tendencies["steals"])
            turnovers_per_game = random.uniform(*tendencies["turnovers"])

            # Shooting percentages
            fg_pct = random.uniform(*tendencies["fg_pct"])
            three_pct = random.uniform(*tendencies["three_pct"])
            ft_pct = random.uniform(*tendencies["ft_pct"])

            # Calculate makes and attempts based on points and percentages
            # Simplified calculation - real calculation would be more complex
            total_points = points_per_game * games_played
            estimated_fg_attempts = points_per_game / (fg_pct * 2.2)  # Rough estimate
            fg_attempts_total = estimated_fg_attempts * games_played
            fg_makes_total = fg_attempts_total * fg_pct

            # Three pointers (varying by position)
            if position in ["point_guard", "shooting_guard", "small_forward"]:
                three_attempt_rate = random.uniform(0.3, 0.5)
            else:
                three_attempt_rate = random.uniform(0.1, 0.3)

            three_attempts_total = fg_attempts_total * three_attempt_rate
            three_makes_total = three_attempts_total * three_pct

            # Free throws
            ft_rate = random.uniform(0.2, 0.4)
            ft_attempts_total = fg_attempts_total * ft_rate
            ft_makes_total = ft_attempts_total * ft_pct

            # Season totals
            season_stats = {
                "id": self.generate_statistic_id("player_season"),
                "player_id": player["id"],
                "team_id": player["team_id"],
                "academic_year_id": academic_year_id,
                "season_id": None,
                "game_id": None,
                "statistic_type": "season_total",
                "minutes_played": round(minutes_per_game * games_played, 2),
                "games_played": games_played,
                "games_started": games_started,
                "points": round(total_points, 2),
                "field_goals_made": round(fg_makes_total, 2),
                "field_goals_attempted": round(fg_attempts_total, 2),
                "field_goal_percentage": round(fg_pct, 3),
                "three_pointers_made": round(three_makes_total, 2),
                "three_pointers_attempted": round(three_attempts_total, 2),
                "three_point_percentage": round(three_pct, 3),
                "free_throws_made": round(ft_makes_total, 2),
                "free_throws_attempted": round(ft_attempts_total, 2),
                "free_throw_percentage": round(ft_pct, 3),
                "offensive_rebounds": round(rebounds_per_game * games_played * 0.3, 2),
                "defensive_rebounds": round(rebounds_per_game * games_played * 0.7, 2),
                "total_rebounds": round(rebounds_per_game * games_played, 2),
                "assists": round(assists_per_game * games_played, 2),
                "steals": round(steals_per_game * games_played, 2),
                "blocks": round(random.uniform(0, 2) * games_played, 2),
                "turnovers": round(turnovers_per_game * games_played, 2),
                "personal_fouls": round(random.uniform(1, 4) * games_played, 2),
                "stats_date": date.today().isoformat()
            }

            # Season averages
            season_averages = {
                "id": self.generate_statistic_id("player_avg"),
                "player_id": player["id"],
                "team_id": player["team_id"],
                "academic_year_id": academic_year_id,
                "season_id": None,
                "game_id": None,
                "statistic_type": "season_average",
                "minutes_played": round(minutes_per_game, 2),
                "games_played": games_played,
                "games_started": games_started,
                "points": round(points_per_game, 2),
                "field_goals_made": round(fg_makes_total / games_played, 2),
                "field_goals_attempted": round(fg_attempts_total / games_played, 2),
                "field_goal_percentage": round(fg_pct, 3),
                "three_pointers_made": round(three_makes_total / games_played, 2),
                "three_pointers_attempted": round(three_attempts_total / games_played, 2),
                "three_point_percentage": round(three_pct, 3),
                "free_throws_made": round(ft_makes_total / games_played, 2),
                "free_throws_attempted": round(ft_attempts_total / games_played, 2),
                "free_throw_percentage": round(ft_pct, 3),
                "offensive_rebounds": round(rebounds_per_game * 0.3, 2),
                "defensive_rebounds": round(rebounds_per_game * 0.7, 2),
                "total_rebounds": round(rebounds_per_game, 2),
                "assists": round(assists_per_game, 2),
                "steals": round(steals_per_game, 2),
                "blocks": round(random.uniform(0, 2), 2),
                "turnovers": round(turnovers_per_game, 2),
                "personal_fouls": round(random.uniform(1, 4), 2),
                "stats_date": date.today().isoformat()
            }

            statistics.extend([season_stats, season_averages])

        return statistics

    def generate_rankings(self, teams: List[Tuple[str, str, str, str]], academic_year_id: str) -> List[Dict[str, Any]]:
        """Generate realistic rankings for multiple systems"""
        rankings = []
        ranking_systems = ["ap_poll", "coaches_poll", "net_ranking", "kenpom"]

        # Sort teams by conference type for realistic ranking distribution
        power_five_teams = [t for t in teams if t[3] == "power_five"]
        mid_major_teams = [t for t in teams if t[3] == "mid_major"]
        low_major_teams = [t for t in teams if t[3] == "low_major"]

        # Simulate rankings for each system
        for system in ranking_systems:
            current_rank = 1

            # Top 25 mostly from power conferences
            top_teams = random.sample(power_five_teams, min(20, len(power_five_teams)))
            if len(mid_major_teams) > 0:
                top_teams.extend(random.sample(mid_major_teams, min(5, len(mid_major_teams))))

            for i, (team_id, team_name, college_name, conference_type) in enumerate(top_teams[:25]):
                # Generate ranking with some variation between systems
                base_rank = current_rank
                if system in ["net_ranking", "kenpom"]:
                    # Analytics systems might rank teams differently
                    rank_variation = random.randint(-3, 3)
                    actual_rank = max(1, min(25, base_rank + rank_variation))
                else:
                    actual_rank = base_rank

                # Poll-specific data
                first_place_votes = 0
                total_points = 0
                if system in ["ap_poll", "coaches_poll"] and actual_rank <= 5:
                    first_place_votes = random.randint(0, 15) if actual_rank == 1 else random.randint(0, 3)
                    total_points = random.randint(1500 - (actual_rank * 60), 1500)

                ranking_data = {
                    "id": self.generate_statistic_id("ranking"),
                    "team_id": team_id,
                    "academic_year_id": academic_year_id,
                    "ranking_system": system,
                    "rank": actual_rank,
                    "rating": round(random.uniform(0.8, 1.0), 4) if system == "kenpom" else None,
                    "ranking_week": 10,  # Mid-season
                    "ranking_date": date.today().isoformat(),
                    "previous_rank": max(1, actual_rank + random.randint(-2, 2)),
                    "rank_change": random.randint(-3, 3),
                    "first_place_votes": first_place_votes,
                    "total_points": total_points,
                    "is_current": True,
                    "is_ranked": True,
                    "notes": None
                }

                rankings.append(ranking_data)
                current_rank += 1

            # Add some "receiving votes" teams
            if system in ["ap_poll", "coaches_poll"]:
                receiving_votes_teams = [t for t in teams if t not in top_teams][:10]
                for team_id, team_name, college_name, conference_type in receiving_votes_teams:
                    ranking_data = {
                        "id": self.generate_statistic_id("ranking"),
                        "team_id": team_id,
                        "academic_year_id": academic_year_id,
                        "ranking_system": system,
                        "rank": random.randint(26, 40),
                        "rating": None,
                        "ranking_week": 10,
                        "ranking_date": date.today().isoformat(),
                        "previous_rank": None,
                        "rank_change": None,
                        "first_place_votes": 0,
                        "total_points": random.randint(10, 100),
                        "is_current": True,
                        "is_ranked": False,
                        "notes": "Receiving votes"
                    }
                    rankings.append(ranking_data)

        return rankings

    def generate_advanced_metrics(self, teams: List[Tuple[str, str, str, str]], academic_year_id: str) -> List[Dict[str, Any]]:
        """Generate realistic advanced metrics"""
        metrics = []

        for team_id, team_name, college_name, conference_type in teams:
            tier = self.conference_tiers.get(conference_type, self.conference_tiers["mid_major"])

            # Base efficiency within tier range
            offensive_eff = random.uniform(*tier["efficiency_range"])
            defensive_eff = random.uniform(95, 110)  # Defense varies less by conference
            net_eff = offensive_eff - defensive_eff

            # Tempo and pace
            tempo = random.uniform(66, 74)
            pace = tempo + random.uniform(-2, 2)

            # Four Factors
            offensive_efg = random.uniform(0.48, 0.58)
            offensive_tov = random.uniform(0.15, 0.25)
            offensive_orb = random.uniform(0.25, 0.40)
            offensive_ft_rate = random.uniform(0.25, 0.40)

            defensive_efg = random.uniform(0.45, 0.55)
            defensive_tov = random.uniform(0.15, 0.25)
            defensive_drb = random.uniform(0.65, 0.80)
            defensive_ft_rate = random.uniform(0.25, 0.40)

            # Strength metrics
            sos = random.uniform(-3, 3)
            sor = random.uniform(-2, 2)

            metrics_data = {
                "id": self.generate_statistic_id("metrics"),
                "team_id": team_id,
                "academic_year_id": academic_year_id,
                "calculation_date": date.today().isoformat(),
                "offensive_efficiency": round(offensive_eff, 4),
                "defensive_efficiency": round(defensive_eff, 4),
                "net_efficiency": round(net_eff, 4),
                "tempo": round(tempo, 4),
                "pace": round(pace, 4),
                "effective_field_goal_percentage": round(offensive_efg, 3),
                "true_shooting_percentage": round(offensive_efg + 0.02, 3),
                "offensive_four_factor_efg": round(offensive_efg, 3),
                "offensive_four_factor_tov": round(offensive_tov, 3),
                "offensive_four_factor_orb": round(offensive_orb, 3),
                "offensive_four_factor_ft": round(offensive_ft_rate, 3),
                "defensive_four_factor_efg": round(defensive_efg, 3),
                "defensive_four_factor_tov": round(defensive_tov, 3),
                "defensive_four_factor_drb": round(defensive_drb, 3),
                "defensive_four_factor_ft": round(defensive_ft_rate, 3),
                "strength_of_schedule": round(sos, 4),
                "strength_of_record": round(sor, 4),
                "pythagorean_wins": round(random.uniform(15, 25), 2),
                "luck_factor": round(random.uniform(-3, 3), 3),
                "average_lead": round(random.uniform(-5, 10), 2),
                "lead_changes_per_game": round(random.uniform(8, 15), 2),
                "close_game_record": f"{random.randint(3, 8)}-{random.randint(2, 5)}",
                "comeback_wins": random.randint(0, 5),
                "performance_variance": round(random.uniform(5, 15), 4),
                "is_current": True
            }

            metrics.append(metrics_data)

        return metrics

    def generate_season_records(self, teams: List[Tuple[str, str, str, str]], academic_year_id: str) -> List[Dict[str, Any]]:
        """Generate realistic season records"""
        records = []
        record_types = ["overall", "conference", "home", "away", "neutral", "quad_1", "quad_2"]

        for team_id, team_name, college_name, conference_type in teams:
            tier = self.conference_tiers.get(conference_type, self.conference_tiers["mid_major"])

            # Base overall record (conference tier affects strength)
            if conference_type == "power_five":
                base_wins = random.randint(15, 25)
                base_losses = random.randint(5, 15)
            elif conference_type == "mid_major":
                base_wins = random.randint(18, 28)
                base_losses = random.randint(3, 10)
            else:
                base_wins = random.randint(20, 30)
                base_losses = random.randint(2, 8)

            for record_type in record_types:
                if record_type == "overall":
                    wins, losses = base_wins, base_losses
                elif record_type == "conference":
                    conf_games = random.randint(16, 20)
                    wins = random.randint(6, conf_games - 2)
                    losses = conf_games - wins
                elif record_type == "home":
                    home_games = random.randint(12, 16)
                    wins = random.randint(int(home_games * 0.6), home_games)  # Home advantage
                    losses = home_games - wins
                elif record_type == "away":
                    away_games = random.randint(10, 14)
                    wins = random.randint(2, int(away_games * 0.6))  # Away disadvantage
                    losses = away_games - wins
                elif record_type == "neutral":
                    neutral_games = random.randint(2, 6)
                    wins = random.randint(0, neutral_games)
                    losses = neutral_games - wins
                elif record_type == "quad_1":
                    q1_games = random.randint(5, 12)
                    wins = random.randint(1, max(1, q1_games // 2))
                    losses = q1_games - wins
                elif record_type == "quad_2":
                    q2_games = random.randint(4, 8)
                    wins = random.randint(2, q2_games)
                    losses = q2_games - wins

                # Generate streak
                streak_type = random.choice(["W", "L"])
                streak_length = random.randint(1, 5)
                current_streak = f"{streak_type}{streak_length}"

                record_data = {
                    "id": self.generate_statistic_id("record"),
                    "team_id": team_id,
                    "academic_year_id": academic_year_id,
                    "record_type": record_type,
                    "wins": wins,
                    "losses": losses,
                    "current_streak": current_streak,
                    "longest_win_streak": random.randint(3, 8),
                    "longest_loss_streak": random.randint(1, 4),
                    "opponent_rank_range": None,
                    "quad_1_wins": wins if record_type == "quad_1" else None,
                    "quad_1_losses": losses if record_type == "quad_1" else None,
                    "quad_2_wins": wins if record_type == "quad_2" else None,
                    "quad_2_losses": losses if record_type == "quad_2" else None,
                    "record_date": date.today().isoformat(),
                    "is_current": True
                }

                records.append(record_data)

        return records

    def insert_data_to_database(self):
        """Insert all generated data into the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Insert players
            for player in self.seed_data["players"]:
                cursor.execute("""
                    INSERT OR IGNORE INTO players (
                        id, team_id, academic_year_id, first_name, last_name, full_name,
                        jersey_number, primary_position, secondary_position, height_inches, weight_pounds,
                        birth_date, hometown, home_state, home_country, high_school, previous_college,
                        player_class, eligibility_status, years_of_eligibility_remaining, is_transfer,
                        transfer_from_college_id, transfer_year, recruiting_class_year, recruiting_stars,
                        recruiting_rank_national, recruiting_rank_position, nba_draft_eligible, nba_draft_year,
                        external_id, espn_player_id, ncaa_player_id, photo_url, bio, is_active, injury_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    player["id"], player["team_id"], player["academic_year_id"],
                    player["first_name"], player["last_name"], player["full_name"],
                    player["jersey_number"], player["primary_position"], player["secondary_position"],
                    player["height_inches"], player["weight_pounds"], player["birth_date"],
                    player["hometown"], player["home_state"], player["home_country"],
                    player["high_school"], player["previous_college"], player["player_class"],
                    player["eligibility_status"], player["years_of_eligibility_remaining"],
                    player["is_transfer"], player["transfer_from_college_id"], player["transfer_year"],
                    player["recruiting_class_year"], player["recruiting_stars"],
                    player["recruiting_rank_national"], player["recruiting_rank_position"],
                    player["nba_draft_eligible"], player["nba_draft_year"],
                    player["external_id"], player["espn_player_id"], player["ncaa_player_id"],
                    player["photo_url"], player["bio"], player["is_active"], player["injury_status"]
                ))

            # Insert team statistics
            for stat in self.seed_data["team_statistics"]:
                cursor.execute("""
                    INSERT OR IGNORE INTO team_statistics (
                        id, team_id, academic_year_id, season_id, game_id, statistic_type,
                        games_played, points, field_goals_made, field_goals_attempted, field_goal_percentage,
                        three_pointers_made, three_pointers_attempted, three_point_percentage,
                        free_throws_made, free_throws_attempted, free_throw_percentage,
                        offensive_rebounds, defensive_rebounds, total_rebounds, assists, steals, blocks,
                        turnovers, personal_fouls, points_allowed, stats_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    stat["id"], stat["team_id"], stat["academic_year_id"], stat["season_id"], stat["game_id"],
                    stat["statistic_type"], stat["games_played"], stat["points"],
                    stat["field_goals_made"], stat["field_goals_attempted"], stat["field_goal_percentage"],
                    stat["three_pointers_made"], stat["three_pointers_attempted"], stat["three_point_percentage"],
                    stat["free_throws_made"], stat["free_throws_attempted"], stat["free_throw_percentage"],
                    stat["offensive_rebounds"], stat["defensive_rebounds"], stat["total_rebounds"],
                    stat["assists"], stat["steals"], stat["blocks"], stat["turnovers"],
                    stat["personal_fouls"], stat["points_allowed"], stat["stats_date"]
                ))

            # Insert player statistics
            for stat in self.seed_data["player_statistics"]:
                cursor.execute("""
                    INSERT OR IGNORE INTO player_statistics (
                        id, player_id, team_id, academic_year_id, season_id, game_id, statistic_type,
                        minutes_played, games_played, games_started, points,
                        field_goals_made, field_goals_attempted, field_goal_percentage,
                        three_pointers_made, three_pointers_attempted, three_point_percentage,
                        free_throws_made, free_throws_attempted, free_throw_percentage,
                        offensive_rebounds, defensive_rebounds, total_rebounds, assists, steals, blocks,
                        turnovers, personal_fouls, stats_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    stat["id"], stat["player_id"], stat["team_id"], stat["academic_year_id"],
                    stat["season_id"], stat["game_id"], stat["statistic_type"],
                    stat["minutes_played"], stat["games_played"], stat["games_started"], stat["points"],
                    stat["field_goals_made"], stat["field_goals_attempted"], stat["field_goal_percentage"],
                    stat["three_pointers_made"], stat["three_pointers_attempted"], stat["three_point_percentage"],
                    stat["free_throws_made"], stat["free_throws_attempted"], stat["free_throw_percentage"],
                    stat["offensive_rebounds"], stat["defensive_rebounds"], stat["total_rebounds"],
                    stat["assists"], stat["steals"], stat["blocks"], stat["turnovers"],
                    stat["personal_fouls"], stat["stats_date"]
                ))

            # Insert rankings
            for ranking in self.seed_data["rankings"]:
                cursor.execute("""
                    INSERT OR IGNORE INTO rankings (
                        id, team_id, academic_year_id, ranking_system, rank, rating, ranking_week,
                        ranking_date, previous_rank, rank_change, first_place_votes, total_points,
                        is_current, is_ranked, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ranking["id"], ranking["team_id"], ranking["academic_year_id"],
                    ranking["ranking_system"], ranking["rank"], ranking["rating"], ranking["ranking_week"],
                    ranking["ranking_date"], ranking["previous_rank"], ranking["rank_change"],
                    ranking["first_place_votes"], ranking["total_points"],
                    ranking["is_current"], ranking["is_ranked"], ranking["notes"]
                ))

            # Insert advanced metrics
            for metric in self.seed_data["advanced_metrics"]:
                cursor.execute("""
                    INSERT OR IGNORE INTO advanced_metrics (
                        id, team_id, academic_year_id, calculation_date,
                        offensive_efficiency, defensive_efficiency, net_efficiency, tempo, pace,
                        effective_field_goal_percentage, true_shooting_percentage,
                        offensive_four_factor_efg, offensive_four_factor_tov, offensive_four_factor_orb, offensive_four_factor_ft,
                        defensive_four_factor_efg, defensive_four_factor_tov, defensive_four_factor_drb, defensive_four_factor_ft,
                        strength_of_schedule, strength_of_record, pythagorean_wins, luck_factor,
                        average_lead, lead_changes_per_game, close_game_record, comeback_wins,
                        performance_variance, is_current
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metric["id"], metric["team_id"], metric["academic_year_id"], metric["calculation_date"],
                    metric["offensive_efficiency"], metric["defensive_efficiency"], metric["net_efficiency"],
                    metric["tempo"], metric["pace"], metric["effective_field_goal_percentage"], metric["true_shooting_percentage"],
                    metric["offensive_four_factor_efg"], metric["offensive_four_factor_tov"], metric["offensive_four_factor_orb"], metric["offensive_four_factor_ft"],
                    metric["defensive_four_factor_efg"], metric["defensive_four_factor_tov"], metric["defensive_four_factor_drb"], metric["defensive_four_factor_ft"],
                    metric["strength_of_schedule"], metric["strength_of_record"], metric["pythagorean_wins"], metric["luck_factor"],
                    metric["average_lead"], metric["lead_changes_per_game"], metric["close_game_record"], metric["comeback_wins"],
                    metric["performance_variance"], metric["is_current"]
                ))

            # Insert season records
            for record in self.seed_data["season_records"]:
                cursor.execute("""
                    INSERT OR IGNORE INTO season_records (
                        id, team_id, academic_year_id, record_type, wins, losses,
                        current_streak, longest_win_streak, longest_loss_streak,
                        opponent_rank_range, quad_1_wins, quad_1_losses, quad_2_wins, quad_2_losses,
                        record_date, is_current
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record["id"], record["team_id"], record["academic_year_id"], record["record_type"],
                    record["wins"], record["losses"], record["current_streak"],
                    record["longest_win_streak"], record["longest_loss_streak"], record["opponent_rank_range"],
                    record["quad_1_wins"], record["quad_1_losses"], record["quad_2_wins"], record["quad_2_losses"],
                    record["record_date"], record["is_current"]
                ))

            conn.commit()
            print("Successfully inserted all seed data!")

        except Exception as e:
            conn.rollback()
            print(f"Error inserting data: {e}")
            raise
        finally:
            conn.close()

    def generate_all_seed_data(self) -> Dict[str, int]:
        """Generate comprehensive seed data for all Phase 4 models"""
        print("Generating comprehensive Phase 4 seed data...")

        # Get teams and academic year
        teams = self.get_teams_and_context()
        academic_year_id, academic_year_name = self.get_current_academic_year()

        print(f"Generating data for {len(teams)} teams in {academic_year_name}")

        # Generate data for each category
        all_players = []
        all_team_stats = []
        all_player_stats = []

        for i, (team_id, team_name, college_name, conference_type) in enumerate(teams):
            print(f"Processing team {i+1}/{len(teams)}: {college_name} {team_name}")

            # Generate players for this team
            team_players = self.generate_players_for_team(team_id, team_name, academic_year_id, conference_type)
            all_players.extend(team_players)

            # Generate team statistics
            team_stats = self.generate_team_statistics(team_id, team_name, academic_year_id, conference_type)
            all_team_stats.extend(team_stats)

            # Generate player statistics for this team
            player_stats = self.generate_player_statistics(team_players, academic_year_id)
            all_player_stats.extend(player_stats)

        # Generate rankings for all teams
        print("Generating rankings...")
        rankings = self.generate_rankings(teams, academic_year_id)

        # Generate advanced metrics
        print("Generating advanced metrics...")
        advanced_metrics = self.generate_advanced_metrics(teams, academic_year_id)

        # Generate season records
        print("Generating season records...")
        season_records = self.generate_season_records(teams, academic_year_id)

        # Store all data
        self.seed_data = {
            "players": all_players,
            "team_statistics": all_team_stats,
            "player_statistics": all_player_stats,
            "rankings": rankings,
            "advanced_metrics": advanced_metrics,
            "season_records": season_records
        }

        # Insert into database
        print("Inserting data into database...")
        self.insert_data_to_database()

        # Return counts
        counts = {category: len(data) for category, data in self.seed_data.items()}
        print(f"Generated seed data: {counts}")
        return counts


def main():
    """Main function to generate seed data"""
    import argparse
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Generate Phase 4 seed data")
    parser.add_argument("--db", help="Database path", default="sports_platform.db")
    parser.add_argument("--output", help="Output JSON file for data review", default=None)

    args = parser.parse_args()

    # Verify database exists
    if not Path(args.db).exists():
        print(f"Error: Database not found at {args.db}")
        sys.exit(1)

    # Generate seed data
    generator = Phase4SeedDataGenerator(args.db)
    counts = generator.generate_all_seed_data()

    # Optionally save data to JSON for review
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(generator.seed_data, f, indent=2, default=str)
        print(f"Seed data saved to {args.output}")

    print("Phase 4 seed data generation completed successfully!")
    return counts


if __name__ == "__main__":
    main()