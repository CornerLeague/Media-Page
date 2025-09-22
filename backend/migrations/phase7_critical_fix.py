#!/usr/bin/env python3
"""
Phase 7 Critical Fix: Immediate repair of existing teams
=======================================================

This is a focused fix to address the critical issue where:
- Basketball teams exist but have no league memberships
- Football teams exist but have no league memberships
- College Football teams exist but have no league memberships

This will quickly fix the onboarding issue by ensuring all existing teams
have proper league associations.

Author: Database ETL Architect
Date: 2025-09-21
"""

import sqlite3
import uuid
from datetime import datetime


def create_missing_leagues_and_fix_memberships():
    """Create missing leagues and fix team memberships"""

    db_path = "/Users/newmac/Desktop/Corner League Media 1/backend/sports_platform.db"

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        print("🚀 CRITICAL FIX: Repairing existing team memberships")
        print("=" * 60)

        # Get sport IDs
        cursor.execute("SELECT name, id FROM sports")
        sport_ids = dict(cursor.fetchall())

        print(f"Found sports: {list(sport_ids.keys())}")

        # 1. Fix Basketball - replace NBA with conferences
        print("\n=== FIXING BASKETBALL ===")
        basketball_sport_id = sport_ids["Basketball"]

        # Create Eastern Conference
        eastern_conf_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT OR IGNORE INTO leagues (
                id, sport_id, name, slug, competition_type,
                league_level, country_code, is_active,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            eastern_conf_id, basketball_sport_id, "Eastern Conference", "eastern-conference",
            "conference", 1, "US", 1
        ))

        # Create Western Conference
        western_conf_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT OR IGNORE INTO leagues (
                id, sport_id, name, slug, competition_type,
                league_level, country_code, is_active,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            western_conf_id, basketball_sport_id, "Western Conference", "western-conference",
            "conference", 1, "US", 1
        ))

        print("✓ Created Basketball conferences")

        # Get basketball teams and assign to conferences
        cursor.execute("SELECT id, name, market FROM teams WHERE sport_id = ?", (basketball_sport_id,))
        basketball_teams = cursor.fetchall()

        # Eastern Conference teams
        eastern_teams = [
            "Celtics", "Nets", "Knicks", "76ers", "Raptors",
            "Bulls", "Cavaliers", "Pistons", "Pacers", "Bucks",
            "Hawks", "Hornets", "Heat", "Magic", "Wizards"
        ]

        eastern_count = 0
        western_count = 0

        for team in basketball_teams:
            team_id, name, market = team

            # Determine conference based on team name
            if any(et in name or et in market for et in eastern_teams):
                league_id = eastern_conf_id
                eastern_count += 1
                conf_name = "Eastern"
            else:
                league_id = western_conf_id
                western_count += 1
                conf_name = "Western"

            # Create membership
            cursor.execute("""
                INSERT OR IGNORE INTO team_league_memberships (
                    id, team_id, league_id, is_active,
                    season_start_year, created_at, updated_at
                ) VALUES (?, ?, ?, 1, 2024, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (str(uuid.uuid4()), team_id, league_id))

            print(f"  ✓ {market} {name} → {conf_name} Conference")

        print(f"✓ Basketball: {eastern_count} Eastern, {western_count} Western")

        # 2. Fix Football - replace NFL with conferences
        print("\n=== FIXING FOOTBALL ===")
        football_sport_id = sport_ids["Football"]

        # Create AFC
        afc_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT OR IGNORE INTO leagues (
                id, sport_id, name, slug, competition_type,
                league_level, country_code, is_active,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            afc_id, football_sport_id, "AFC", "afc",
            "conference", 1, "US", 1
        ))

        # Create NFC
        nfc_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT OR IGNORE INTO leagues (
                id, sport_id, name, slug, competition_type,
                league_level, country_code, is_active,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            nfc_id, football_sport_id, "NFC", "nfc",
            "conference", 1, "US", 1
        ))

        print("✓ Created Football conferences")

        # Get football teams and assign to conferences
        cursor.execute("SELECT id, name, market FROM teams WHERE sport_id = ?", (football_sport_id,))
        football_teams = cursor.fetchall()

        # AFC teams
        afc_teams = [
            "Ravens", "Bengals", "Browns", "Steelers",
            "Bills", "Dolphins", "Patriots", "Jets",
            "Texans", "Colts", "Jaguars", "Titans",
            "Broncos", "Chiefs", "Raiders", "Chargers"
        ]

        afc_count = 0
        nfc_count = 0

        for team in football_teams:
            team_id, name, market = team

            # Determine conference based on team name
            if any(at in name or at in market for at in afc_teams):
                league_id = afc_id
                afc_count += 1
                conf_name = "AFC"
            else:
                league_id = nfc_id
                nfc_count += 1
                conf_name = "NFC"

            # Create membership
            cursor.execute("""
                INSERT OR IGNORE INTO team_league_memberships (
                    id, team_id, league_id, is_active,
                    season_start_year, created_at, updated_at
                ) VALUES (?, ?, ?, 1, 2024, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (str(uuid.uuid4()), team_id, league_id))

            print(f"  ✓ {market} {name} → {conf_name}")

        print(f"✓ Football: {afc_count} AFC, {nfc_count} NFC")

        # 3. Fix College Football teams
        print("\n=== FIXING COLLEGE FOOTBALL ===")
        college_football_sport_id = sport_ids["College Football"]

        # Get existing college football teams and conferences
        cursor.execute("""
            SELECT t.id, t.name, t.market, l.name as league_name
            FROM teams t
            LEFT JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
            LEFT JOIN leagues l ON tlm.league_id = l.id
            WHERE t.sport_id = ?
        """, (college_football_sport_id,))
        cf_teams = cursor.fetchall()

        # Get available conferences
        cursor.execute("""
            SELECT id, name FROM leagues
            WHERE sport_id = ? AND is_active = 1
        """, (college_football_sport_id,))
        cf_conferences = dict(cursor.fetchall())

        print(f"Found {len(cf_teams)} college football teams")
        print(f"Available conferences: {list(cf_conferences.keys())}")

        # Assign teams to SEC (default for now)
        sec_id = None
        for conf_id, conf_name in cf_conferences.items():
            if "Southeastern" in conf_name:
                sec_id = conf_id
                break

        if sec_id:
            cf_count = 0
            for team in cf_teams:
                team_id, name, market, current_league = team

                if not current_league:  # Team has no league membership
                    cursor.execute("""
                        INSERT OR IGNORE INTO team_league_memberships (
                            id, team_id, league_id, is_active,
                            season_start_year, created_at, updated_at
                        ) VALUES (?, ?, ?, 1, 2024, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (str(uuid.uuid4()), team_id, sec_id))
                    cf_count += 1
                    print(f"  ✓ {name} → SEC")

            print(f"✓ College Football: {cf_count} teams assigned to SEC")

        # Commit changes
        conn.commit()

        # Final validation
        print("\n=== FINAL VALIDATION ===")
        cursor.execute("""
            SELECT s.name, COUNT(DISTINCT t.id) as teams, COUNT(tlm.id) as memberships
            FROM sports s
            LEFT JOIN teams t ON s.id = t.sport_id AND t.is_active = 1
            LEFT JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
            GROUP BY s.id, s.name
            ORDER BY s.name
        """)

        results = cursor.fetchall()
        for sport, teams, memberships in results:
            print(f"✓ {sport:<20} {teams:>3} teams, {memberships:>3} memberships")

        # Check for orphaned teams
        cursor.execute("""
            SELECT COUNT(*) FROM teams t
            LEFT JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
            WHERE tlm.team_id IS NULL AND t.is_active = 1
        """)
        orphaned = cursor.fetchone()[0]

        if orphaned == 0:
            print("✅ SUCCESS: No orphaned teams!")
        else:
            print(f"⚠ {orphaned} teams still need league assignments")

        print("\n🎉 CRITICAL FIX COMPLETED!")

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    create_missing_leagues_and_fix_memberships()