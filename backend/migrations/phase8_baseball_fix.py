#!/usr/bin/env python3
"""
Phase 8 Baseball Fix: Complete the baseball teams population
==========================================================

This script specifically fixes the baseball issue where the
American League and National League weren't created properly.

Author: Database ETL Architect
Date: 2025-09-21
"""

import sqlite3
import uuid
from datetime import datetime


def fix_baseball_teams():
    """Fix baseball teams population"""

    db_path = "/Users/newmac/Desktop/Corner League Media 1/backend/sports_platform.db"

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        print("🚀 BASEBALL FIX: Creating leagues and teams")
        print("=" * 60)

        # Get Baseball sport ID
        cursor.execute("SELECT id FROM sports WHERE name = 'Baseball'")
        result = cursor.fetchone()
        if not result:
            print("❌ Baseball sport not found")
            return

        baseball_sport_id = result[0]
        print(f"✓ Found Baseball sport ID: {baseball_sport_id}")

        # Create American League
        al_id = str(uuid.uuid4())
        print(f"Creating American League with ID: {al_id}")

        cursor.execute("""
            INSERT INTO leagues (
                id, sport_id, name, slug, competition_type,
                league_level, country_code, is_active,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (al_id, baseball_sport_id, "American League", "american-league", "league", 1, "US", 1))

        # Create National League
        nl_id = str(uuid.uuid4())
        print(f"Creating National League with ID: {nl_id}")

        cursor.execute("""
            INSERT INTO leagues (
                id, sport_id, name, slug, competition_type,
                league_level, country_code, is_active,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (nl_id, baseball_sport_id, "National League", "national-league", "league", 1, "US", 1))

        print("✓ Created both baseball leagues")

        # Baseball teams data
        american_league_teams = [
            ("Baltimore", "Orioles"), ("Boston", "Red Sox"), ("New York", "Yankees"),
            ("Tampa Bay", "Rays"), ("Toronto", "Blue Jays"), ("Chicago", "White Sox"),
            ("Cleveland", "Guardians"), ("Detroit", "Tigers"), ("Kansas City", "Royals"),
            ("Minnesota", "Twins"), ("Oakland", "Athletics"), ("Houston", "Astros"),
            ("Los Angeles", "Angels"), ("Seattle", "Mariners"), ("Texas", "Rangers")
        ]

        national_league_teams = [
            ("Atlanta", "Braves"), ("Miami", "Marlins"), ("New York", "Mets"),
            ("Philadelphia", "Phillies"), ("Washington", "Nationals"), ("Chicago", "Cubs"),
            ("Cincinnati", "Reds"), ("Milwaukee", "Brewers"), ("Pittsburgh", "Pirates"),
            ("St. Louis", "Cardinals"), ("Arizona", "Diamondbacks"), ("Colorado", "Rockies"),
            ("Los Angeles", "Dodgers"), ("San Diego", "Padres"), ("San Francisco", "Giants")
        ]

        al_count = 0
        nl_count = 0

        # Create American League teams
        print("\nCreating American League teams...")
        for market, name in american_league_teams:
            team_id = str(uuid.uuid4())
            slug = f"{market.lower().replace(' ', '-')}-{name.lower()}"

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

            al_count += 1
            print(f"  ✓ {market} {name}")

        # Create National League teams
        print("\nCreating National League teams...")
        for market, name in national_league_teams:
            team_id = str(uuid.uuid4())
            slug = f"{market.lower().replace(' ', '-')}-{name.lower()}"

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

            nl_count += 1
            print(f"  ✓ {market} {name}")

        # Commit changes
        conn.commit()

        print(f"\n✅ SUCCESS!")
        print(f"✓ American League: {al_count} teams")
        print(f"✓ National League: {nl_count} teams")
        print(f"✓ Total Baseball teams: {al_count + nl_count}")

        # Final check
        cursor.execute("""
            SELECT COUNT(*) FROM teams WHERE sport_id = ?
        """, (baseball_sport_id,))
        total_teams = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM team_league_memberships tlm
            JOIN teams t ON tlm.team_id = t.id
            WHERE t.sport_id = ? AND tlm.is_active = 1
        """, (baseball_sport_id,))
        total_memberships = cursor.fetchone()[0]

        print(f"✓ Verification: {total_teams} teams, {total_memberships} memberships")

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    fix_baseball_teams()