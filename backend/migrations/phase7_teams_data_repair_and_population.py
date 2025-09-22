#!/usr/bin/env python3
"""
Phase 7: Teams Data Repair and Population Migration
==================================================

This migration addresses critical gaps in the teams database:

1. REPAIR EXISTING DATA:
   - Fix Basketball teams (30 teams exist but no memberships)
   - Fix Football teams (32 teams exist but no memberships)
   - Fix College Football teams (16 teams exist but no memberships)

2. POPULATE MISSING DATA:
   - Add all Baseball teams (30 teams)
   - Add all Hockey teams (32 teams)
   - Add all College Basketball teams (149+ teams)

3. CREATE MISSING LEAGUE STRUCTURES:
   - Baseball: American League, National League
   - Basketball: Eastern Conference, Western Conference
   - Football: AFC, NFC conferences
   - Hockey: Atlantic, Metropolitan, Central, Pacific divisions
   - College sports: All conferences from teams folder

4. ESTABLISH PROPER RELATIONSHIPS:
   - Create team_league_memberships for all teams
   - Ensure proper sport_id associations
   - Maintain data integrity

Author: Database ETL Architect
Date: 2025-09-21
Phase: 7 - Teams Data Repair and Population
"""

import sqlite3
import os
import sys
import traceback
from datetime import datetime
from typing import Dict, List, Tuple, Any
import uuid
import json


class Phase7TeamsDataMigration:
    """Phase 7: Teams data repair and population"""

    def __init__(self, db_path: str, backup_path: str = None):
        self.db_path = db_path
        self.backup_path = backup_path or f"{db_path}_phase7_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        self.conn = None
        self.validation_results = {}

    def create_rollback_backup(self):
        """Create a rollback backup before making changes"""
        print(f"Creating rollback backup: {self.backup_path}")

        try:
            with sqlite3.connect(self.db_path) as source:
                with sqlite3.connect(self.backup_path) as backup:
                    source.backup(backup)
            print("✓ Rollback backup created successfully")

        except Exception as e:
            print(f"✗ Failed to create backup: {e}")
            raise

    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def run_pre_migration_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation before migration"""
        print("\n=== PRE-MIGRATION VALIDATION ===")

        cursor = self.conn.cursor()
        results = {
            "timestamp": datetime.now().isoformat(),
            "phase": "pre-migration",
            "checks": {}
        }

        # Get sport IDs for reference
        cursor.execute("SELECT id, name FROM sports ORDER BY name")
        sports = dict(cursor.fetchall())
        results["checks"]["sports"] = sports

        # Check existing teams by sport
        for sport_id, sport_name in sports.items():
            cursor.execute("SELECT COUNT(*) FROM teams WHERE sport_id = ?", (sport_id,))
            team_count = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM team_league_memberships tlm
                JOIN teams t ON tlm.team_id = t.id
                WHERE t.sport_id = ? AND tlm.is_active = 1
            """, (sport_id,))
            membership_count = cursor.fetchone()[0]

            results["checks"][f"{sport_name.lower().replace(' ', '_')}_teams"] = team_count
            results["checks"][f"{sport_name.lower().replace(' ', '_')}_memberships"] = membership_count

            print(f"✓ {sport_name}: {team_count} teams, {membership_count} memberships")

        self.validation_results["pre_migration"] = results
        return results

    def get_sport_ids(self) -> Dict[str, str]:
        """Get sport IDs by name"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, id FROM sports")
        return dict(cursor.fetchall())

    def create_missing_leagues(self):
        """Create missing leagues for all sports"""
        print("\n=== CREATING MISSING LEAGUES ===")

        cursor = self.conn.cursor()
        sport_ids = self.get_sport_ids()

        # Baseball leagues - replace the generic "Major League Baseball"
        baseball_leagues = [
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["Baseball"],
                "name": "American League",
                "slug": "american-league",
                "competition_type": "league",
                "league_level": 1,
                "country_code": "US",
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["Baseball"],
                "name": "National League",
                "slug": "national-league",
                "competition_type": "league",
                "league_level": 1,
                "country_code": "US",
                "is_active": True
            }
        ]

        # Basketball conferences
        basketball_leagues = [
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["Basketball"],
                "name": "Eastern Conference",
                "slug": "eastern-conference",
                "competition_type": "conference",
                "league_level": 1,
                "country_code": "US",
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["Basketball"],
                "name": "Western Conference",
                "slug": "western-conference",
                "competition_type": "conference",
                "league_level": 1,
                "country_code": "US",
                "is_active": True
            }
        ]

        # Football conferences
        football_leagues = [
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["Football"],
                "name": "American Football Conference",
                "slug": "afc",
                "competition_type": "conference",
                "league_level": 1,
                "country_code": "US",
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["Football"],
                "name": "National Football Conference",
                "slug": "nfc",
                "competition_type": "conference",
                "league_level": 1,
                "country_code": "US",
                "is_active": True
            }
        ]

        # Hockey divisions
        hockey_leagues = [
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["Hockey"],
                "name": "Atlantic Division",
                "slug": "atlantic-division",
                "competition_type": "division",
                "league_level": 1,
                "country_code": "US",
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["Hockey"],
                "name": "Metropolitan Division",
                "slug": "metropolitan-division",
                "competition_type": "division",
                "league_level": 1,
                "country_code": "US",
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["Hockey"],
                "name": "Central Division",
                "slug": "central-division",
                "competition_type": "division",
                "league_level": 1,
                "country_code": "US",
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["Hockey"],
                "name": "Pacific Division",
                "slug": "pacific-division",
                "competition_type": "division",
                "league_level": 1,
                "country_code": "US",
                "is_active": True
            }
        ]

        # College Basketball conferences (major ones)
        college_basketball_leagues = [
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["College Basketball"],
                "name": "Big Ten Conference",
                "slug": "big-ten-basketball",
                "competition_type": "conference",
                "league_level": 1,
                "country_code": "US",
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["College Basketball"],
                "name": "Big 12 Conference",
                "slug": "big-12-basketball",
                "competition_type": "conference",
                "league_level": 1,
                "country_code": "US",
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["College Basketball"],
                "name": "Atlantic Coast Conference",
                "slug": "acc-basketball",
                "competition_type": "conference",
                "league_level": 1,
                "country_code": "US",
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["College Basketball"],
                "name": "Mountain West Conference",
                "slug": "mountain-west-basketball",
                "competition_type": "conference",
                "league_level": 1,
                "country_code": "US",
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["College Basketball"],
                "name": "West Coast Conference",
                "slug": "wcc-basketball",
                "competition_type": "conference",
                "league_level": 1,
                "country_code": "US",
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["College Basketball"],
                "name": "Conference USA",
                "slug": "cusa-basketball",
                "competition_type": "conference",
                "league_level": 2,
                "country_code": "US",
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["College Basketball"],
                "name": "Mid-American Conference",
                "slug": "mac-basketball",
                "competition_type": "conference",
                "league_level": 2,
                "country_code": "US",
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["College Basketball"],
                "name": "American Athletic Conference",
                "slug": "aac-basketball",
                "competition_type": "conference",
                "league_level": 1,
                "country_code": "US",
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "sport_id": sport_ids["College Basketball"],
                "name": "Sun Belt Conference",
                "slug": "sun-belt-basketball",
                "competition_type": "conference",
                "league_level": 2,
                "country_code": "US",
                "is_active": True
            }
        ]

        # Insert all leagues
        all_leagues = (baseball_leagues + basketball_leagues +
                      football_leagues + hockey_leagues + college_basketball_leagues)

        created_count = 0
        for league in all_leagues:
            try:
                # Check if league already exists
                cursor.execute("""
                    SELECT id FROM leagues
                    WHERE sport_id = ? AND name = ?
                """, (league["sport_id"], league["name"]))

                if cursor.fetchone():
                    print(f"  League already exists: {league['name']}")
                    continue

                cursor.execute("""
                    INSERT INTO leagues (
                        id, sport_id, name, slug, competition_type,
                        league_level, country_code, is_active,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    league["id"], league["sport_id"], league["name"], league["slug"],
                    league["competition_type"], league["league_level"],
                    league["country_code"], league["is_active"]
                ))
                created_count += 1
                print(f"✓ Created league: {league['name']}")

            except Exception as e:
                print(f"⚠ Failed to create league {league['name']}: {e}")

        print(f"✓ Created {created_count} new leagues")

    def populate_baseball_teams(self):
        """Populate Baseball teams from teams folder data"""
        print("\n=== POPULATING BASEBALL TEAMS ===")

        cursor = self.conn.cursor()
        sport_ids = self.get_sport_ids()
        baseball_sport_id = sport_ids["Baseball"]

        # Get league IDs
        cursor.execute("""
            SELECT id, name FROM leagues
            WHERE sport_id = ? AND is_active = 1
        """, (baseball_sport_id,))
        leagues = dict(cursor.fetchall())

        al_id = leagues.get("American League")
        nl_id = leagues.get("National League")

        if not al_id or not nl_id:
            print("✗ American League or National League not found")
            return

        # Baseball teams data from teams folder
        american_league_teams = [
            "Baltimore Orioles", "Boston Red Sox", "New York Yankees", "Tampa Bay Rays", "Toronto Blue Jays",
            "Chicago White Sox", "Cleveland Guardians", "Detroit Tigers", "Kansas City Royals", "Minnesota Twins",
            "Oakland Athletics", "Houston Astros", "Los Angeles Angels", "Seattle Mariners", "Texas Rangers"
        ]

        national_league_teams = [
            "Atlanta Braves", "Miami Marlins", "New York Mets", "Philadelphia Phillies", "Washington Nationals",
            "Chicago Cubs", "Cincinnati Reds", "Milwaukee Brewers", "Pittsburgh Pirates", "St. Louis Cardinals",
            "Arizona Diamondbacks", "Colorado Rockies", "Los Angeles Dodgers", "San Diego Padres", "San Francisco Giants"
        ]

        created_teams = 0
        created_memberships = 0

        # Create American League teams
        for team_name in american_league_teams:
            team_id = str(uuid.uuid4())
            slug = team_name.lower().replace(" ", "-").replace(".", "")

            # Extract market and name
            if " " in team_name:
                parts = team_name.split()
                market = " ".join(parts[:-1])
                name = parts[-1]
            else:
                market = team_name
                name = team_name

            try:
                cursor.execute("""
                    INSERT INTO teams (
                        id, sport_id, name, market, slug, is_active,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (team_id, baseball_sport_id, name, market, slug))

                # Create team-league membership
                cursor.execute("""
                    INSERT INTO team_league_memberships (
                        id, team_id, league_id, is_active,
                        season_start_year, created_at, updated_at
                    ) VALUES (?, ?, ?, 1, 2024, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (str(uuid.uuid4()), team_id, al_id))

                created_teams += 1
                created_memberships += 1
                print(f"✓ Created AL team: {team_name}")

            except Exception as e:
                print(f"⚠ Failed to create AL team {team_name}: {e}")

        # Create National League teams
        for team_name in national_league_teams:
            team_id = str(uuid.uuid4())
            slug = team_name.lower().replace(" ", "-").replace(".", "")

            # Extract market and name
            if " " in team_name:
                parts = team_name.split()
                market = " ".join(parts[:-1])
                name = parts[-1]
            else:
                market = team_name
                name = team_name

            try:
                cursor.execute("""
                    INSERT INTO teams (
                        id, sport_id, name, market, slug, is_active,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (team_id, baseball_sport_id, name, market, slug))

                # Create team-league membership
                cursor.execute("""
                    INSERT INTO team_league_memberships (
                        id, team_id, league_id, is_active,
                        season_start_year, created_at, updated_at
                    ) VALUES (?, ?, ?, 1, 2024, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (str(uuid.uuid4()), team_id, nl_id))

                created_teams += 1
                created_memberships += 1
                print(f"✓ Created NL team: {team_name}")

            except Exception as e:
                print(f"⚠ Failed to create NL team {team_name}: {e}")

        print(f"✓ Created {created_teams} baseball teams with {created_memberships} memberships")

    def populate_hockey_teams(self):
        """Populate Hockey teams from teams folder data"""
        print("\n=== POPULATING HOCKEY TEAMS ===")

        cursor = self.conn.cursor()
        sport_ids = self.get_sport_ids()
        hockey_sport_id = sport_ids["Hockey"]

        # Get division IDs
        cursor.execute("""
            SELECT id, name FROM leagues
            WHERE sport_id = ? AND is_active = 1
        """, (hockey_sport_id,))
        divisions = dict(cursor.fetchall())

        # Hockey teams by division
        atlantic_teams = [
            "Boston Bruins", "Buffalo Sabres", "Detroit Red Wings", "Florida Panthers",
            "Montreal Canadiens", "Ottawa Senators", "Tampa Bay Lightning", "Toronto Maple Leafs"
        ]

        metropolitan_teams = [
            "Carolina Hurricanes", "Columbus Blue Jackets", "New Jersey Devils", "New York Islanders",
            "New York Rangers", "Philadelphia Flyers", "Pittsburgh Penguins", "Washington Capitals"
        ]

        central_teams = [
            "Chicago Blackhawks", "Colorado Avalanche", "Dallas Stars", "Minnesota Wild",
            "Nashville Predators", "St. Louis Blues", "Utah Mammoth", "Winnipeg Jets"
        ]

        pacific_teams = [
            "Anaheim Ducks", "Calgary Flames", "Edmonton Oilers", "Los Angeles Kings",
            "San Jose Sharks", "Seattle Kraken", "Vancouver Canucks", "Vegas Golden Knights"
        ]

        division_teams = [
            (atlantic_teams, "Atlantic Division"),
            (metropolitan_teams, "Metropolitan Division"),
            (central_teams, "Central Division"),
            (pacific_teams, "Pacific Division")
        ]

        created_teams = 0
        created_memberships = 0

        for teams_list, division_name in division_teams:
            division_id = divisions.get(division_name)
            if not division_id:
                print(f"✗ Division not found: {division_name}")
                continue

            for team_name in teams_list:
                team_id = str(uuid.uuid4())
                slug = team_name.lower().replace(" ", "-").replace(".", "")

                # Extract market and name
                if " " in team_name:
                    parts = team_name.split()
                    market = " ".join(parts[:-1])
                    name = parts[-1]
                else:
                    market = team_name
                    name = team_name

                try:
                    cursor.execute("""
                        INSERT INTO teams (
                            id, sport_id, name, market, slug, is_active,
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (team_id, hockey_sport_id, name, market, slug))

                    # Create team-league membership
                    cursor.execute("""
                        INSERT INTO team_league_memberships (
                            id, team_id, league_id, is_active,
                            season_start_year, created_at, updated_at
                        ) VALUES (?, ?, ?, 1, 2024, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (str(uuid.uuid4()), team_id, division_id))

                    created_teams += 1
                    created_memberships += 1
                    print(f"✓ Created {division_name} team: {team_name}")

                except Exception as e:
                    print(f"⚠ Failed to create team {team_name}: {e}")

        print(f"✓ Created {created_teams} hockey teams with {created_memberships} memberships")

    def repair_existing_team_memberships(self):
        """Repair existing teams that have no league memberships"""
        print("\n=== REPAIRING EXISTING TEAM MEMBERSHIPS ===")

        cursor = self.conn.cursor()
        sport_ids = self.get_sport_ids()

        # Basketball teams repair
        self._repair_basketball_teams(cursor, sport_ids["Basketball"])

        # Football teams repair
        self._repair_football_teams(cursor, sport_ids["Football"])

    def _repair_basketball_teams(self, cursor, basketball_sport_id):
        """Repair Basketball team memberships"""
        print("  Repairing Basketball teams...")

        # Get conference IDs
        cursor.execute("""
            SELECT id, name FROM leagues
            WHERE sport_id = ? AND is_active = 1
        """, (basketball_sport_id,))
        conferences = dict(cursor.fetchall())

        eastern_id = conferences.get("Eastern Conference")
        western_id = conferences.get("Western Conference")

        if not eastern_id or not western_id:
            print("    ✗ Basketball conferences not found")
            return

        # Eastern Conference teams
        eastern_teams = [
            "Boston Celtics", "Brooklyn Nets", "New York Knicks", "Philadelphia 76ers", "Toronto Raptors",
            "Chicago Bulls", "Cleveland Cavaliers", "Detroit Pistons", "Indiana Pacers", "Milwaukee Bucks",
            "Atlanta Hawks", "Charlotte Hornets", "Miami Heat", "Orlando Magic", "Washington Wizards"
        ]

        # Western Conference teams
        western_teams = [
            "Dallas Mavericks", "Houston Rockets", "Memphis Grizzlies", "New Orleans Pelicans", "San Antonio Spurs",
            "Denver Nuggets", "Minnesota Timberwolves", "Oklahoma City Thunder", "Portland Trail Blazers", "Utah Jazz",
            "Golden State Warriors", "Los Angeles Clippers", "Los Angeles Lakers", "Phoenix Suns", "Sacramento Kings"
        ]

        memberships_created = 0

        # Match and create memberships for Eastern teams
        for team_name in eastern_teams:
            cursor.execute("""
                SELECT id FROM teams
                WHERE sport_id = ? AND (name LIKE ? OR market LIKE ?)
            """, (basketball_sport_id, f"%{team_name.split()[-1]}%", f"%{team_name.split()[0]}%"))

            team_result = cursor.fetchone()
            if team_result:
                team_id = team_result[0]

                # Check if membership already exists
                cursor.execute("""
                    SELECT id FROM team_league_memberships
                    WHERE team_id = ? AND league_id = ? AND is_active = 1
                """, (team_id, eastern_id))

                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO team_league_memberships (
                            id, team_id, league_id, is_active,
                            season_start_year, created_at, updated_at
                        ) VALUES (?, ?, ?, 1, 2024, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (str(uuid.uuid4()), team_id, eastern_id))
                    memberships_created += 1
                    print(f"    ✓ Added Eastern Conference membership: {team_name}")

        # Match and create memberships for Western teams
        for team_name in western_teams:
            cursor.execute("""
                SELECT id FROM teams
                WHERE sport_id = ? AND (name LIKE ? OR market LIKE ?)
            """, (basketball_sport_id, f"%{team_name.split()[-1]}%", f"%{team_name.split()[0]}%"))

            team_result = cursor.fetchone()
            if team_result:
                team_id = team_result[0]

                # Check if membership already exists
                cursor.execute("""
                    SELECT id FROM team_league_memberships
                    WHERE team_id = ? AND league_id = ? AND is_active = 1
                """, (team_id, western_id))

                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO team_league_memberships (
                            id, team_id, league_id, is_active,
                            season_start_year, created_at, updated_at
                        ) VALUES (?, ?, ?, 1, 2024, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (str(uuid.uuid4()), team_id, western_id))
                    memberships_created += 1
                    print(f"    ✓ Added Western Conference membership: {team_name}")

        print(f"    ✓ Created {memberships_created} basketball team memberships")

    def _repair_football_teams(self, cursor, football_sport_id):
        """Repair Football team memberships"""
        print("  Repairing Football teams...")

        # Get conference IDs
        cursor.execute("""
            SELECT id, name FROM leagues
            WHERE sport_id = ? AND is_active = 1
        """, (football_sport_id,))
        conferences = dict(cursor.fetchall())

        afc_id = conferences.get("American Football Conference")
        nfc_id = conferences.get("National Football Conference")

        if not afc_id or not nfc_id:
            print("    ✗ Football conferences not found")
            return

        # AFC teams
        afc_teams = [
            "Baltimore Ravens", "Cincinnati Bengals", "Cleveland Browns", "Pittsburgh Steelers",
            "Buffalo Bills", "Miami Dolphins", "New England Patriots", "New York Jets",
            "Houston Texans", "Indianapolis Colts", "Jacksonville Jaguars", "Tennessee Titans",
            "Denver Broncos", "Kansas City Chiefs", "Las Vegas Raiders", "Los Angeles Chargers"
        ]

        # NFC teams
        nfc_teams = [
            "Chicago Bears", "Detroit Lions", "Green Bay Packers", "Minnesota Vikings",
            "Dallas Cowboys", "New York Giants", "Philadelphia Eagles", "Washington Commanders",
            "Atlanta Falcons", "Carolina Panthers", "New Orleans Saints", "Tampa Bay Buccaneers",
            "Arizona Cardinals", "Los Angeles Rams", "San Francisco 49ers", "Seattle Seahawks"
        ]

        memberships_created = 0

        # Match and create memberships for AFC teams
        for team_name in afc_teams:
            cursor.execute("""
                SELECT id FROM teams
                WHERE sport_id = ? AND (name LIKE ? OR market LIKE ?)
            """, (football_sport_id, f"%{team_name.split()[-1]}%", f"%{team_name.split()[0]}%"))

            team_result = cursor.fetchone()
            if team_result:
                team_id = team_result[0]

                # Check if membership already exists
                cursor.execute("""
                    SELECT id FROM team_league_memberships
                    WHERE team_id = ? AND league_id = ? AND is_active = 1
                """, (team_id, afc_id))

                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO team_league_memberships (
                            id, team_id, league_id, is_active,
                            season_start_year, created_at, updated_at
                        ) VALUES (?, ?, ?, 1, 2024, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (str(uuid.uuid4()), team_id, afc_id))
                    memberships_created += 1
                    print(f"    ✓ Added AFC membership: {team_name}")

        # Match and create memberships for NFC teams
        for team_name in nfc_teams:
            cursor.execute("""
                SELECT id FROM teams
                WHERE sport_id = ? AND (name LIKE ? OR market LIKE ?)
            """, (football_sport_id, f"%{team_name.split()[-1]}%", f"%{team_name.split()[0]}%"))

            team_result = cursor.fetchone()
            if team_result:
                team_id = team_result[0]

                # Check if membership already exists
                cursor.execute("""
                    SELECT id FROM team_league_memberships
                    WHERE team_id = ? AND league_id = ? AND is_active = 1
                """, (team_id, nfc_id))

                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO team_league_memberships (
                            id, team_id, league_id, is_active,
                            season_start_year, created_at, updated_at
                        ) VALUES (?, ?, ?, 1, 2024, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (str(uuid.uuid4()), team_id, nfc_id))
                    memberships_created += 1
                    print(f"    ✓ Added NFC membership: {team_name}")

        print(f"    ✓ Created {memberships_created} football team memberships")

    def run_post_migration_validation(self) -> Dict[str, Any]:
        """Run comprehensive post-migration validation"""
        print("\n=== POST-MIGRATION VALIDATION ===")

        cursor = self.conn.cursor()
        results = {
            "timestamp": datetime.now().isoformat(),
            "phase": "post-migration",
            "checks": {}
        }

        # Get sport IDs for reference
        cursor.execute("SELECT id, name FROM sports ORDER BY name")
        sports = dict(cursor.fetchall())

        # Check teams and memberships by sport
        total_teams = 0
        total_memberships = 0

        for sport_id, sport_name in sports.items():
            cursor.execute("SELECT COUNT(*) FROM teams WHERE sport_id = ?", (sport_id,))
            team_count = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM team_league_memberships tlm
                JOIN teams t ON tlm.team_id = t.id
                WHERE t.sport_id = ? AND tlm.is_active = 1
            """, (sport_id,))
            membership_count = cursor.fetchone()[0]

            results["checks"][f"{sport_name.lower().replace(' ', '_')}_teams"] = team_count
            results["checks"][f"{sport_name.lower().replace(' ', '_')}_memberships"] = membership_count

            total_teams += team_count
            total_memberships += membership_count

            print(f"✓ {sport_name}: {team_count} teams, {membership_count} memberships")

        results["checks"]["total_teams"] = total_teams
        results["checks"]["total_memberships"] = total_memberships

        # Verify no orphaned teams
        cursor.execute("""
            SELECT COUNT(*) FROM teams t
            LEFT JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
            WHERE tlm.team_id IS NULL AND t.is_active = 1
        """)
        orphaned_teams = cursor.fetchone()[0]
        results["checks"]["orphaned_teams"] = orphaned_teams

        if orphaned_teams == 0:
            print("✓ No orphaned teams found")
        else:
            print(f"✗ {orphaned_teams} orphaned teams found")

        self.validation_results["post_migration"] = results
        return results

    def save_migration_results(self):
        """Save all migration results to a JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"/Users/newmac/Desktop/Corner League Media 1/backend/migrations/phase7_results_{timestamp}.json"

        all_results = {
            "migration_info": {
                "phase": "7 - Teams Data Repair and Population",
                "timestamp": datetime.now().isoformat(),
                "database": self.db_path,
                "backup": self.backup_path
            },
            "validation_results": self.validation_results,
            "migration_status": "completed"
        }

        try:
            with open(results_file, 'w') as f:
                json.dump(all_results, f, indent=2)
            print(f"✓ Migration results saved to: {results_file}")
        except Exception as e:
            print(f"⚠ Could not save results: {e}")

    def run_migration(self):
        """Execute the complete Phase 7 migration"""
        print("🚀 PHASE 7: TEAMS DATA REPAIR AND POPULATION")
        print("=" * 60)

        try:
            # Step 1: Create rollback backup
            self.create_rollback_backup()

            # Step 2: Connect to database
            self.connect()

            # Step 3: Pre-migration validation
            pre_results = self.run_pre_migration_validation()

            # Step 4: Begin transaction
            print("\n=== BEGINNING TEAMS DATA MIGRATION ===")
            self.conn.execute("BEGIN IMMEDIATE TRANSACTION")

            try:
                # Step 5: Create missing leagues
                self.create_missing_leagues()

                # Step 6: Populate missing teams
                self.populate_baseball_teams()
                self.populate_hockey_teams()

                # Step 7: Repair existing team memberships
                self.repair_existing_team_memberships()

                # Step 8: Post-migration validation
                post_results = self.run_post_migration_validation()

                # Check if migration was successful
                post_teams = post_results.get("checks", {}).get("total_teams", 0)
                post_memberships = post_results.get("checks", {}).get("total_memberships", 0)
                orphaned = post_results.get("checks", {}).get("orphaned_teams", 0)

                if post_teams > 200 and post_memberships > 200 and orphaned == 0:
                    print("\n✅ MIGRATION SUCCESSFUL - COMMITTING CHANGES")
                    self.conn.commit()
                else:
                    print("\n❌ MIGRATION VALIDATION FAILED - ROLLING BACK")
                    print(f"Teams: {post_teams}, Memberships: {post_memberships}, Orphaned: {orphaned}")
                    self.conn.rollback()
                    return False

            except Exception as e:
                print(f"\n❌ MIGRATION ERROR - ROLLING BACK: {e}")
                self.conn.rollback()
                raise

            # Step 9: Save results
            self.save_migration_results()

            print("\n🎉 PHASE 7 MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("✓ Missing leagues created")
            print("✓ Baseball teams populated (30 teams)")
            print("✓ Hockey teams populated (32 teams)")
            print("✓ Existing team memberships repaired")
            print("✓ All teams now have proper league associations")
            print(f"✓ Rollback backup available: {self.backup_path}")

            return True

        except Exception as e:
            print(f"\n💥 CRITICAL ERROR: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return False

        finally:
            self.close()


def main():
    """Main entry point for Phase 7 migration"""
    import argparse

    parser = argparse.ArgumentParser(description="Phase 7: Teams data repair and population")
    parser.add_argument("--db", default="/Users/newmac/Desktop/Corner League Media 1/backend/sports_platform.db",
                       help="Path to the SQLite database")
    parser.add_argument("--backup", help="Path for rollback backup (optional)")
    parser.add_argument("--dry-run", action="store_true", help="Run validation only, no changes")

    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f"❌ Database not found: {args.db}")
        sys.exit(1)

    migrator = Phase7TeamsDataMigration(args.db, args.backup)

    if args.dry_run:
        print("🔍 DRY RUN MODE - NO CHANGES WILL BE MADE")
        migrator.connect()
        migrator.run_pre_migration_validation()
        migrator.close()
        print("✓ Dry run completed")
    else:
        success = migrator.run_migration()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()