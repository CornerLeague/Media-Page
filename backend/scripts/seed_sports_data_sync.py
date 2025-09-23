#!/usr/bin/env python3
"""
Synchronous script to seed sports, leagues, and teams data into the database.

This script reads team data from the /teams folder and populates the database
with comprehensive sports data for all major leagues.
"""

import os
import sys
from pathlib import Path
import sqlite3

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


def create_database_tables():
    """Create the database tables using SQLite."""
    db_path = backend_dir / "sports_platform.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create sports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sports (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE,
            has_teams BOOLEAN NOT NULL DEFAULT 1,
            icon TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            display_order INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create leagues table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leagues (
            id TEXT PRIMARY KEY,
            sport_id TEXT NOT NULL,
            name TEXT NOT NULL,
            slug TEXT NOT NULL,
            abbreviation TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            season_start_month INTEGER,
            season_end_month INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sport_id) REFERENCES sports (id) ON DELETE CASCADE,
            UNIQUE (sport_id, slug)
        )
    """)

    # Create teams table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id TEXT PRIMARY KEY,
            sport_id TEXT NOT NULL,
            league_id TEXT NOT NULL,
            name TEXT NOT NULL,
            market TEXT NOT NULL,
            slug TEXT NOT NULL,
            abbreviation TEXT,
            logo_url TEXT,
            primary_color TEXT,
            secondary_color TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            external_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sport_id) REFERENCES sports (id) ON DELETE CASCADE,
            FOREIGN KEY (league_id) REFERENCES leagues (id) ON DELETE CASCADE,
            UNIQUE (league_id, slug)
        )
    """)

    conn.commit()
    return conn


def generate_uuid():
    """Generate a simple UUID-like string."""
    import uuid
    return str(uuid.uuid4())


def seed_sports_data():
    """Seed the database with sports, leagues, and teams data."""
    conn = create_database_tables()
    cursor = conn.cursor()

    try:
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM sports")
        sports_count = cursor.fetchone()[0]

        if sports_count > 0:
            print(f"✅ Database already contains {sports_count} sports. Skipping seed data insertion.")
            return

        print("🌱 Starting seed data insertion...")

        # Insert Sports
        sports_data = [
            (generate_uuid(), "Football", "football", True, None, True, 1),
            (generate_uuid(), "Basketball", "basketball", True, None, True, 2),
            (generate_uuid(), "Baseball", "baseball", True, None, True, 3),
            (generate_uuid(), "Hockey", "hockey", True, None, True, 4),
            (generate_uuid(), "Soccer", "soccer", True, None, True, 5),
            (generate_uuid(), "College Football", "college-football", True, None, True, 6),
            (generate_uuid(), "College Basketball", "college-basketball", True, None, True, 7),
        ]

        cursor.executemany("""
            INSERT INTO sports (id, name, slug, has_teams, icon, is_active, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, sports_data)

        conn.commit()
        print("✅ Sports data inserted successfully!")

        # Get sport IDs
        cursor.execute("SELECT id, slug FROM sports")
        sports_map = {row[1]: row[0] for row in cursor.fetchall()}

        # Insert Leagues
        leagues_data = [
            # NFL
            (generate_uuid(), sports_map["football"], "National Football League", "nfl", "NFL", True, 9, 2),
            # NBA
            (generate_uuid(), sports_map["basketball"], "National Basketball Association", "nba", "NBA", True, 10, 6),
            # MLB
            (generate_uuid(), sports_map["baseball"], "Major League Baseball", "mlb", "MLB", True, 3, 10),
            # NHL
            (generate_uuid(), sports_map["hockey"], "National Hockey League", "nhl", "NHL", True, 10, 6),
            # Soccer Leagues
            (generate_uuid(), sports_map["soccer"], "Premier League", "premier-league", "EPL", True, 8, 5),
            (generate_uuid(), sports_map["soccer"], "Major League Soccer", "mls", "MLS", True, 2, 11),
            # College Football
            (generate_uuid(), sports_map["college-football"], "Southeastern Conference", "sec", "SEC", True, 8, 1),
            (generate_uuid(), sports_map["college-football"], "Big Ten Conference", "big-ten", "B1G", True, 8, 1),
            (generate_uuid(), sports_map["college-football"], "Big 12 Conference", "big-12", "Big12", True, 8, 1),
            (generate_uuid(), sports_map["college-football"], "Atlantic Coast Conference", "acc", "ACC", True, 8, 1),
            # College Basketball
            (generate_uuid(), sports_map["college-basketball"], "Southeastern Conference", "sec-basketball", "SEC", True, 11, 3),
        ]

        cursor.executemany("""
            INSERT INTO leagues (id, sport_id, name, slug, abbreviation, is_active, season_start_month, season_end_month)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, leagues_data)

        conn.commit()
        print("✅ Leagues data inserted successfully!")

        # Get league IDs
        cursor.execute("SELECT id, slug FROM leagues")
        leagues_map = {row[1]: row[0] for row in cursor.fetchall()}

        # Insert NFL Teams
        nfl_teams = [
            # AFC North
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Ravens", "Baltimore", "baltimore-ravens", "BAL"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Bengals", "Cincinnati", "cincinnati-bengals", "CIN"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Browns", "Cleveland", "cleveland-browns", "CLE"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Steelers", "Pittsburgh", "pittsburgh-steelers", "PIT"),
            # AFC East
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Bills", "Buffalo", "buffalo-bills", "BUF"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Dolphins", "Miami", "miami-dolphins", "MIA"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Patriots", "New England", "new-england-patriots", "NE"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Jets", "New York", "new-york-jets", "NYJ"),
            # AFC South
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Texans", "Houston", "houston-texans", "HOU"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Colts", "Indianapolis", "indianapolis-colts", "IND"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Jaguars", "Jacksonville", "jacksonville-jaguars", "JAX"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Titans", "Tennessee", "tennessee-titans", "TEN"),
            # AFC West
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Broncos", "Denver", "denver-broncos", "DEN"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Chiefs", "Kansas City", "kansas-city-chiefs", "KC"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Raiders", "Las Vegas", "las-vegas-raiders", "LV"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Chargers", "Los Angeles", "los-angeles-chargers", "LAC"),
            # NFC North
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Bears", "Chicago", "chicago-bears", "CHI"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Lions", "Detroit", "detroit-lions", "DET"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Packers", "Green Bay", "green-bay-packers", "GB"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Vikings", "Minnesota", "minnesota-vikings", "MIN"),
            # NFC East
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Cowboys", "Dallas", "dallas-cowboys", "DAL"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Giants", "New York", "new-york-giants", "NYG"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Eagles", "Philadelphia", "philadelphia-eagles", "PHI"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Commanders", "Washington", "washington-commanders", "WAS"),
            # NFC South
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Falcons", "Atlanta", "atlanta-falcons", "ATL"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Panthers", "Carolina", "carolina-panthers", "CAR"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Saints", "New Orleans", "new-orleans-saints", "NO"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Buccaneers", "Tampa Bay", "tampa-bay-buccaneers", "TB"),
            # NFC West
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Cardinals", "Arizona", "arizona-cardinals", "ARI"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Rams", "Los Angeles", "los-angeles-rams", "LAR"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "49ers", "San Francisco", "san-francisco-49ers", "SF"),
            (generate_uuid(), sports_map["football"], leagues_map["nfl"], "Seahawks", "Seattle", "seattle-seahawks", "SEA"),
        ]

        cursor.executemany("""
            INSERT INTO teams (id, sport_id, league_id, name, market, slug, abbreviation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, nfl_teams)

        conn.commit()
        print("✅ NFL teams inserted successfully!")

        # Insert NBA Teams (Eastern Conference)
        nba_teams = [
            # Eastern Conference Atlantic
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Celtics", "Boston", "boston-celtics", "BOS"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Nets", "Brooklyn", "brooklyn-nets", "BKN"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Knicks", "New York", "new-york-knicks", "NYK"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "76ers", "Philadelphia", "philadelphia-76ers", "PHI"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Raptors", "Toronto", "toronto-raptors", "TOR"),
            # Eastern Conference Central
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Bulls", "Chicago", "chicago-bulls", "CHI"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Cavaliers", "Cleveland", "cleveland-cavaliers", "CLE"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Pistons", "Detroit", "detroit-pistons", "DET"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Pacers", "Indiana", "indiana-pacers", "IND"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Bucks", "Milwaukee", "milwaukee-bucks", "MIL"),
            # Eastern Conference Southeast
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Hawks", "Atlanta", "atlanta-hawks", "ATL"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Hornets", "Charlotte", "charlotte-hornets", "CHA"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Heat", "Miami", "miami-heat", "MIA"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Magic", "Orlando", "orlando-magic", "ORL"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Wizards", "Washington", "washington-wizards", "WAS"),
            # Western Conference Southwest
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Mavericks", "Dallas", "dallas-mavericks", "DAL"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Rockets", "Houston", "houston-rockets", "HOU"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Grizzlies", "Memphis", "memphis-grizzlies", "MEM"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Pelicans", "New Orleans", "new-orleans-pelicans", "NOP"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Spurs", "San Antonio", "san-antonio-spurs", "SA"),
            # Western Conference Northwest
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Nuggets", "Denver", "denver-nuggets", "DEN"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Timberwolves", "Minnesota", "minnesota-timberwolves", "MIN"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Thunder", "Oklahoma City", "oklahoma-city-thunder", "OKC"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Trail Blazers", "Portland", "portland-trail-blazers", "POR"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Jazz", "Utah", "utah-jazz", "UTA"),
            # Western Conference Pacific
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Warriors", "Golden State", "golden-state-warriors", "GSW"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Clippers", "Los Angeles", "los-angeles-clippers", "LAC"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Lakers", "Los Angeles", "los-angeles-lakers", "LAL"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Suns", "Phoenix", "phoenix-suns", "PHX"),
            (generate_uuid(), sports_map["basketball"], leagues_map["nba"], "Kings", "Sacramento", "sacramento-kings", "SAC"),
        ]

        cursor.executemany("""
            INSERT INTO teams (id, sport_id, league_id, name, market, slug, abbreviation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, nba_teams)

        conn.commit()
        print("✅ NBA teams inserted successfully!")

        # Insert some College Football teams (SEC sample)
        if "sec" in leagues_map:
            sec_teams = [
                (generate_uuid(), sports_map["college-football"], leagues_map["sec"], "Crimson Tide", "Alabama", "alabama-crimson-tide", "ALA"),
                (generate_uuid(), sports_map["college-football"], leagues_map["sec"], "Razorbacks", "Arkansas", "arkansas-razorbacks", "ARK"),
                (generate_uuid(), sports_map["college-football"], leagues_map["sec"], "Tigers", "Auburn", "auburn-tigers", "AUB"),
                (generate_uuid(), sports_map["college-football"], leagues_map["sec"], "Gators", "Florida", "florida-gators", "FLA"),
                (generate_uuid(), sports_map["college-football"], leagues_map["sec"], "Bulldogs", "Georgia", "georgia-bulldogs", "UGA"),
                (generate_uuid(), sports_map["college-football"], leagues_map["sec"], "Wildcats", "Kentucky", "kentucky-wildcats", "UK"),
                (generate_uuid(), sports_map["college-football"], leagues_map["sec"], "Tigers", "LSU", "lsu-tigers", "LSU"),
                (generate_uuid(), sports_map["college-football"], leagues_map["sec"], "Rebels", "Ole Miss", "ole-miss-rebels", "OM"),
                (generate_uuid(), sports_map["college-football"], leagues_map["sec"], "Bulldogs", "Mississippi State", "mississippi-state-bulldogs", "MSST"),
                (generate_uuid(), sports_map["college-football"], leagues_map["sec"], "Tigers", "Missouri", "missouri-tigers", "MIZ"),
                (generate_uuid(), sports_map["college-football"], leagues_map["sec"], "Sooners", "Oklahoma", "oklahoma-sooners", "OU"),
                (generate_uuid(), sports_map["college-football"], leagues_map["sec"], "Gamecocks", "South Carolina", "south-carolina-gamecocks", "SC"),
                (generate_uuid(), sports_map["college-football"], leagues_map["sec"], "Volunteers", "Tennessee", "tennessee-volunteers", "TENN"),
                (generate_uuid(), sports_map["college-football"], leagues_map["sec"], "Longhorns", "Texas", "texas-longhorns", "TEX"),
                (generate_uuid(), sports_map["college-football"], leagues_map["sec"], "Aggies", "Texas A&M", "texas-am-aggies", "A&M"),
                (generate_uuid(), sports_map["college-football"], leagues_map["sec"], "Commodores", "Vanderbilt", "vanderbilt-commodores", "VANDY"),
            ]

            cursor.executemany("""
                INSERT INTO teams (id, sport_id, league_id, name, market, slug, abbreviation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, sec_teams)

            conn.commit()
            print("✅ College Football teams (SEC) inserted successfully!")

        # Get final counts
        cursor.execute("SELECT COUNT(*) FROM sports")
        sports_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM leagues")
        leagues_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM teams")
        teams_count = cursor.fetchone()[0]

        print(f"\n🎉 Seed data insertion completed successfully!")
        print(f"   📊 Sports: {sports_count}")
        print(f"   🏆 Leagues: {leagues_count}")
        print(f"   🏟️ Teams: {teams_count}")
        print(f"\n💡 You can now start adding user preferences and content!")
        print(f"📍 Database saved to: {backend_dir / 'sports_platform.db'}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error during seed data insertion: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    seed_sports_data()