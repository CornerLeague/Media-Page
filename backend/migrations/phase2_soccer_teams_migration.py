#!/usr/bin/env python3
"""
Phase 2 Soccer Teams Migration
===============================

Imports all soccer teams and creates league-team relationships from soccer_teams.md

PHASE 2 REQUIREMENTS:
- Create 4 new leagues: UEFA Champions League, La Liga, Bundesliga, Serie A
- Import 144 total teams across 6 leagues
- Handle teams in multiple leagues (domestic + international)
- Ensure data integrity and no duplicates
- Populate enhanced metadata
"""

import sqlite3
import uuid
import re
import sys
import os
from typing import Dict, List, Tuple, Set
from datetime import datetime

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SoccerTeamsMigration:
    def __init__(self, db_path: str, teams_file_path: str):
        self.db_path = db_path
        self.teams_file_path = teams_file_path
        self.soccer_sport_id = "61a964ee-563b-4ccd-b277-b429ec1c57ab"

        # Will be populated from database
        self.existing_leagues = {}

        # New leagues to create
        self.new_leagues = {
            "UEFA Champions League": {
                "country_code": "EU",
                "league_level": 1,
                "competition_type": "international",
                "is_active": True
            },
            "La Liga": {
                "country_code": "ES",
                "league_level": 1,
                "competition_type": "domestic",
                "is_active": True
            },
            "Bundesliga": {
                "country_code": "DE",
                "league_level": 1,
                "competition_type": "domestic",
                "is_active": True
            },
            "Serie A": {
                "country_code": "IT",
                "league_level": 1,
                "competition_type": "domestic",
                "is_active": True
            }
        }

        # Country mappings for teams
        self.league_country_map = {
            "Premier League": "GB",
            "UEFA Champions League": None,  # International - teams keep their own countries
            "Major League Soccer": "US",
            "La Liga": "ES",
            "Bundesliga": "DE",
            "Serie A": "IT"
        }

        # Team country overrides for international teams
        self.team_country_overrides = {
            # UEFA Champions League specific mappings
            "FC Barcelona": "ES",
            "FC Bayern Munich": "DE",
            "Benfica": "PT",
            "Borussia Dortmund": "DE",
            "Celtic": "GB",
            "Club Brugge": "BE",
            "Dinamo Zagreb": "HR",
            "Atlético Madrid": "ES",
            "Atalanta": "IT",
            "Paris Saint-Germain": "FR",
            "Red Star Belgrade": "RS",
            "Feyenoord": "NL",
            "Galatasaray": "TR",
            "Inter Milan": "IT",
            "Juventus": "IT",
            "Lille": "FR",
            "PSV Eindhoven": "NL",
            "Rangers": "GB",
            "RB Leipzig": "DE",
            "Real Madrid": "ES",
            "Real Sociedad": "ES",
            "Milan": "IT",
            "Bayer Leverkusen": "DE",
            "Borussia Mönchengladbach": "DE",
            "Sevilla": "ES",
            "Shakhtar Donetsk": "UA",
            "Sporting CP": "PT",
            "Sturm Graz": "AT",
            "Red Bull Salzburg": "AT",
            "Union Saint-Gilloise": "BE",
            "Young Boys": "CH",
            "FC Copenhagen": "DK"
        }

        self.parsed_data = {}
        self.created_leagues = {}
        self.imported_teams = {}
        self.team_memberships = []

    def generate_slug(self, name: str) -> str:
        """Generate URL-friendly slug from team/league name"""
        # Remove special characters and convert to lowercase
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        # Replace spaces and multiple hyphens with single hyphen
        slug = re.sub(r'[-\s]+', '-', slug)
        # Remove leading/trailing hyphens
        return slug.strip('-')

    def extract_team_names(self, team_line: str) -> Tuple[str, str]:
        """Extract short name and official name from team line"""
        # Pattern: "Short Name (Official Name)"
        match = re.match(r'•\s*([^(]+?)\s*\(([^)]+)\)', team_line.strip())
        if match:
            short_name = match.group(1).strip()
            official_name = match.group(2).strip()
            return short_name, official_name
        else:
            # Fallback: use the text after bullet point
            name = team_line.replace('•', '').strip()
            return name, name

    def parse_teams_file(self) -> Dict:
        """Parse the soccer_teams.md file and extract league-team data"""
        print("Parsing soccer_teams.md file...")

        with open(self.teams_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        leagues_data = {}
        current_league = None

        for line in content.split('\n'):
            line = line.strip()

            if line.startswith('League:'):
                current_league = line.replace('League:', '').strip()
                leagues_data[current_league] = []
                print(f"Found league: {current_league}")

            elif line.startswith('•') and current_league:
                short_name, official_name = self.extract_team_names(line)
                team_data = {
                    'short_name': short_name,
                    'official_name': official_name,
                    'slug': self.generate_slug(short_name)
                }
                leagues_data[current_league].append(team_data)

        # Validate parsed data
        total_teams = sum(len(teams) for teams in leagues_data.values())
        print(f"\nParsed {len(leagues_data)} leagues with {total_teams} total teams:")
        for league, teams in leagues_data.items():
            print(f"  {league}: {len(teams)} teams")

        self.parsed_data = leagues_data
        return leagues_data

    def load_existing_leagues(self, conn: sqlite3.Connection):
        """Load all existing leagues from database"""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name FROM leagues WHERE sport_id = ?
        """, (self.soccer_sport_id,))

        self.existing_leagues = {name: league_id for league_id, name in cursor.fetchall()}
        print(f"Loaded {len(self.existing_leagues)} existing leagues")

    def create_new_leagues(self, conn: sqlite3.Connection) -> Dict[str, str]:
        """Create the 4 new leagues and return their IDs"""
        print("\nChecking/creating new leagues...")
        created_league_ids = {}

        cursor = conn.cursor()

        # Use the loaded existing leagues
        existing_leagues_db = self.existing_leagues

        for league_name, league_info in self.new_leagues.items():
            if league_name in existing_leagues_db:
                league_id = existing_leagues_db[league_name]
                created_league_ids[league_name] = league_id
                print(f"  Found existing: {league_name} ({league_id})")
            else:
                league_id = str(uuid.uuid4())
                slug = self.generate_slug(league_name)

                cursor.execute("""
                    INSERT INTO leagues (
                        id, sport_id, name, slug, abbreviation, country_code,
                        league_level, competition_type, is_active, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    league_id, self.soccer_sport_id, league_name, slug,
                    league_name[:10].upper(),  # Simple abbreviation
                    league_info["country_code"], league_info["league_level"],
                    league_info["competition_type"], league_info["is_active"],
                    datetime.utcnow(), datetime.utcnow()
                ))

                created_league_ids[league_name] = league_id
                print(f"  Created: {league_name} ({league_id})")

        conn.commit()
        self.created_leagues = created_league_ids
        return created_league_ids

    def get_team_country_code(self, team_short_name: str, league_name: str) -> str:
        """Determine the appropriate country code for a team"""
        # Check for specific overrides first
        if team_short_name in self.team_country_overrides:
            return self.team_country_overrides[team_short_name]

        # Use league default for domestic leagues
        league_country = self.league_country_map.get(league_name)
        if league_country:
            return league_country

        # Default fallback
        return "US"

    def find_duplicate_team(self, cursor: sqlite3.Cursor, short_name: str, official_name: str) -> str:
        """Check if team already exists and return its ID"""
        # Check by short name first
        cursor.execute("""
            SELECT id FROM teams
            WHERE sport_id = ? AND (name = ? OR short_name = ? OR official_name = ?)
        """, (self.soccer_sport_id, short_name, short_name, official_name))

        result = cursor.fetchone()
        return result[0] if result else None

    def import_teams(self, conn: sqlite3.Connection) -> Dict[str, str]:
        """Import all unique teams and return team_id mappings"""
        print("\nImporting teams...")
        cursor = conn.cursor()
        imported_team_ids = {}
        duplicate_count = 0

        # All league IDs (existing + new)
        all_league_ids = {**self.existing_leagues, **self.created_leagues}

        for league_name, teams in self.parsed_data.items():
            print(f"\n  Processing {league_name} ({len(teams)} teams):")

            for team_data in teams:
                short_name = team_data['short_name']
                official_name = team_data['official_name']
                slug = team_data['slug']

                # Check if team already exists
                existing_team_id = self.find_duplicate_team(cursor, short_name, official_name)

                if existing_team_id:
                    print(f"    Found existing: {short_name} ({existing_team_id})")
                    imported_team_ids[f"{league_name}:{short_name}"] = existing_team_id
                    duplicate_count += 1
                else:
                    # Create new team
                    team_id = str(uuid.uuid4())
                    country_code = self.get_team_country_code(short_name, league_name)

                    cursor.execute("""
                        INSERT INTO teams (
                            id, sport_id, league_id, name, market, slug, short_name, official_name,
                            country_code, is_active, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        team_id, self.soccer_sport_id, all_league_ids[league_name],
                        short_name, short_name, slug, short_name, official_name,
                        country_code, True, datetime.utcnow(), datetime.utcnow()
                    ))

                    imported_team_ids[f"{league_name}:{short_name}"] = team_id
                    print(f"    Created: {short_name} ({team_id}) [{country_code}]")

        conn.commit()

        unique_teams = len(set(imported_team_ids.values()))
        total_entries = len(imported_team_ids)

        print(f"\nTeam import summary:")
        print(f"  Total team entries: {total_entries}")
        print(f"  Unique teams: {unique_teams}")
        print(f"  Duplicates found: {duplicate_count}")
        print(f"  Teams in multiple leagues: {total_entries - unique_teams}")

        self.imported_teams = imported_team_ids
        return imported_team_ids

    def create_team_league_memberships(self, conn: sqlite3.Connection):
        """Create team-league memberships in junction table"""
        print("\nCreating team-league memberships...")
        cursor = conn.cursor()

        # All league IDs (existing + new)
        all_league_ids = {**self.existing_leagues, **self.created_leagues}

        memberships_created = 0

        for league_name, teams in self.parsed_data.items():
            league_id = all_league_ids[league_name]
            print(f"\n  Processing memberships for {league_name}:")

            for team_data in teams:
                short_name = team_data['short_name']
                team_id = self.imported_teams[f"{league_name}:{short_name}"]

                # Check if membership already exists
                cursor.execute("""
                    SELECT id FROM team_league_memberships
                    WHERE team_id = ? AND league_id = ?
                """, (team_id, league_id))

                if cursor.fetchone():
                    print(f"    Membership exists: {short_name}")
                    continue

                # Create new membership
                membership_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO team_league_memberships (
                        id, team_id, league_id, season_start_year,
                        is_active, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    membership_id, team_id, league_id, 2024,
                    True, datetime.utcnow(), datetime.utcnow()
                ))

                memberships_created += 1
                print(f"    Created: {short_name} -> {league_name}")

        conn.commit()
        print(f"\nCreated {memberships_created} team-league memberships")

    def validate_migration(self, conn: sqlite3.Connection) -> bool:
        """Validate the migration results"""
        print("\nValidating migration results...")
        cursor = conn.cursor()

        # Check total teams imported
        cursor.execute("""
            SELECT COUNT(*) FROM teams WHERE sport_id = ?
        """, (self.soccer_sport_id,))
        total_teams = cursor.fetchone()[0]

        # Check total memberships
        cursor.execute("""
            SELECT COUNT(*) FROM team_league_memberships tlm
            JOIN teams t ON tlm.team_id = t.id
            WHERE t.sport_id = ?
        """, (self.soccer_sport_id,))
        total_memberships = cursor.fetchone()[0]

        # Check teams in multiple leagues
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT tlm.team_id, COUNT(*) as league_count
                FROM team_league_memberships tlm
                JOIN teams t ON tlm.team_id = t.id
                WHERE t.sport_id = ? AND tlm.is_active = 1
                GROUP BY tlm.team_id
                HAVING league_count > 1
            )
        """, (self.soccer_sport_id,))
        multi_league_teams = cursor.fetchone()[0]

        # Check league team counts
        cursor.execute("""
            SELECT l.name, COUNT(tlm.team_id) as team_count
            FROM leagues l
            LEFT JOIN team_league_memberships tlm ON l.id = tlm.league_id AND tlm.is_active = 1
            WHERE l.sport_id = ?
            GROUP BY l.id, l.name
            ORDER BY l.name
        """, (self.soccer_sport_id,))
        league_counts = cursor.fetchall()

        print(f"\nValidation Results:")
        print(f"  Total unique teams: {total_teams}")
        print(f"  Total memberships: {total_memberships}")
        print(f"  Teams in multiple leagues: {multi_league_teams}")
        print(f"\nLeague team counts:")

        expected_counts = {
            "Premier League": 20,
            "UEFA Champions League": 36,
            "Major League Soccer": 28,
            "La Liga": 20,
            "Bundesliga": 18,
            "Serie A": 20
        }

        all_valid = True
        for league_name, team_count in league_counts:
            expected = expected_counts.get(league_name, "Unknown")
            status = "✓" if team_count == expected else "✗"
            print(f"    {league_name}: {team_count} teams (expected: {expected}) {status}")
            if team_count != expected:
                all_valid = False

        return all_valid

    def run_migration(self) -> bool:
        """Execute the complete Phase 2 migration"""
        print("=== Phase 2 Soccer Teams Migration ===")
        print(f"Database: {self.db_path}")
        print(f"Teams file: {self.teams_file_path}")

        try:
            # Parse teams file
            self.parse_teams_file()

            # Connect to database
            conn = sqlite3.connect(self.db_path)
            conn.execute("BEGIN TRANSACTION")

            try:
                # Load existing leagues
                self.load_existing_leagues(conn)

                # Create new leagues
                self.create_new_leagues(conn)

                # Import teams
                self.import_teams(conn)

                # Create memberships
                self.create_team_league_memberships(conn)

                # Validate results
                is_valid = self.validate_migration(conn)

                if is_valid:
                    conn.commit()
                    print("\n✓ Phase 2 migration completed successfully!")
                    return True
                else:
                    conn.rollback()
                    print("\n✗ Migration validation failed - rolled back")
                    return False

            except Exception as e:
                conn.rollback()
                print(f"\n✗ Migration failed: {e}")
                raise
            finally:
                conn.close()

        except Exception as e:
            print(f"Error during migration: {e}")
            return False

def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='Phase 2 Soccer Teams Migration')
    parser.add_argument('--db-path', required=True, help='Path to SQLite database')
    parser.add_argument('--teams-file', required=True, help='Path to soccer_teams.md file')
    parser.add_argument('--dry-run', action='store_true', help='Validate only, do not execute')

    args = parser.parse_args()

    migration = SoccerTeamsMigration(args.db_path, args.teams_file)

    if args.dry_run:
        print("DRY RUN MODE - Parsing and validation only")
        migration.parse_teams_file()
        return

    success = migration.run_migration()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()