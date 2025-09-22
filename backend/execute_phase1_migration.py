#!/usr/bin/env python3
"""
Execute Phase 1 College Basketball Migration on SQLite Database
Since Alembic requires PostgreSQL, this script manually executes the migration on SQLite
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def create_backup(db_path):
    """Create a backup of the database before migration."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / f"sports_platform_phase1_backup_{timestamp}.db"

    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"📦 Database backup created: {backup_path}")
    return backup_path


def execute_phase1_schema(cursor):
    """Execute Phase 1 schema creation on SQLite."""
    print("🔧 Creating Phase 1 schema...")

    # SQLite doesn't support PostgreSQL enums, so we'll use CHECK constraints

    # Create divisions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS divisions (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE,
            level TEXT NOT NULL CHECK (level IN ('D1', 'D2', 'D3', 'NAIA', 'NJCAA')),
            description TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            display_order INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create indexes for divisions
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_divisions_level ON divisions(level)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_divisions_slug ON divisions(slug)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_divisions_display_order ON divisions(display_order)")

    # Create college_conferences table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS college_conferences (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            division_id TEXT NOT NULL,
            name TEXT NOT NULL,
            slug TEXT NOT NULL,
            abbreviation TEXT,
            conference_type TEXT NOT NULL CHECK (conference_type IN ('power_five', 'mid_major', 'low_major', 'independent')),
            region TEXT CHECK (region IN ('northeast', 'southeast', 'midwest', 'southwest', 'west', 'northwest')),
            founded_year INTEGER,
            headquarters_city TEXT,
            headquarters_state TEXT,
            website_url TEXT,
            logo_url TEXT,
            primary_color TEXT,
            secondary_color TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            tournament_format TEXT,
            auto_bid_tournament BOOLEAN NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE CASCADE,
            UNIQUE(division_id, slug)
        )
    """)

    # Create indexes for college_conferences
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_college_conferences_division_id ON college_conferences(division_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_college_conferences_slug ON college_conferences(slug)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_college_conferences_abbreviation ON college_conferences(abbreviation)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_college_conferences_type_region ON college_conferences(conference_type, region)")

    # Create colleges table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS colleges (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            conference_id TEXT NOT NULL,
            name TEXT NOT NULL,
            slug TEXT NOT NULL,
            short_name TEXT,
            abbreviation TEXT,
            college_type TEXT NOT NULL CHECK (college_type IN ('public', 'private', 'religious', 'military', 'community')),
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            country TEXT NOT NULL DEFAULT 'USA',
            zip_code TEXT,
            founded_year INTEGER,
            enrollment INTEGER,
            website_url TEXT,
            athletics_website_url TEXT,
            logo_url TEXT,
            primary_color TEXT,
            secondary_color TEXT,
            mascot TEXT,
            nickname TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            arena_name TEXT,
            arena_capacity INTEGER,
            head_coach TEXT,
            coach_since_year INTEGER,
            ncaa_championships INTEGER NOT NULL DEFAULT 0,
            final_four_appearances INTEGER NOT NULL DEFAULT 0,
            ncaa_tournament_appearances INTEGER NOT NULL DEFAULT 0,
            conference_championships INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conference_id) REFERENCES college_conferences(id) ON DELETE CASCADE,
            UNIQUE(conference_id, slug)
        )
    """)

    # Create indexes for colleges
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_colleges_conference_id ON colleges(conference_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_colleges_slug ON colleges(slug)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_colleges_state_city ON colleges(state, city)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_colleges_name_search ON colleges(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_colleges_nickname ON colleges(nickname)")

    # Create college_teams table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS college_teams (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            college_id TEXT NOT NULL,
            sport_id TEXT NOT NULL,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            abbreviation TEXT,
            external_id TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            current_record_wins INTEGER NOT NULL DEFAULT 0,
            current_record_losses INTEGER NOT NULL DEFAULT 0,
            conference_record_wins INTEGER NOT NULL DEFAULT 0,
            conference_record_losses INTEGER NOT NULL DEFAULT 0,
            ap_poll_rank INTEGER,
            coaches_poll_rank INTEGER,
            net_ranking INTEGER,
            kenpom_ranking INTEGER,
            rpi_ranking INTEGER,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE CASCADE,
            FOREIGN KEY (sport_id) REFERENCES sports(id) ON DELETE CASCADE,
            UNIQUE(college_id, sport_id)
        )
    """)

    # Create indexes for college_teams
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_college_teams_college_id ON college_teams(college_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_college_teams_sport_id ON college_teams(sport_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_college_teams_slug ON college_teams(slug)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_college_teams_external_id ON college_teams(external_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_college_teams_rankings ON college_teams(ap_poll_rank, coaches_poll_rank)")

    print("✅ Phase 1 schema created successfully!")


def execute_phase1_seed_data(cursor):
    """Execute Phase 1 seed data insertion."""
    print("🌱 Inserting Phase 1 seed data...")

    # Insert Division I
    cursor.execute("""
        INSERT OR IGNORE INTO divisions (name, slug, level, description, is_active, display_order)
        VALUES ('Division I', 'division-i', 'D1', 'NCAA Division I - highest level of college athletics', 1, 1)
    """)

    # Get Division I ID
    cursor.execute("SELECT id FROM divisions WHERE slug = 'division-i'")
    division_i_id = cursor.fetchone()[0]

    # Insert conferences
    conferences_data = [
        ('Atlantic Coast Conference', 'acc', 'ACC', 'power_five', 'southeast', 1953, 'Charlotte', 'North Carolina'),
        ('Big East Conference', 'big-east', 'Big East', 'mid_major', 'northeast', 1979, 'New York', 'New York'),
        ('Big Ten Conference', 'big-ten', 'B1G', 'power_five', 'midwest', 1896, 'Chicago', 'Illinois'),
        ('Big 12 Conference', 'big-12', 'Big 12', 'power_five', 'midwest', 1994, 'Irving', 'Texas'),
        ('Pacific-12 Conference', 'pac-12', 'Pac-12', 'power_five', 'west', 1915, 'San Francisco', 'California'),
        ('Southeastern Conference', 'sec', 'SEC', 'power_five', 'southeast', 1932, 'Birmingham', 'Alabama'),
        ('American Athletic Conference', 'aac', 'AAC', 'mid_major', 'southeast', 2013, 'Irving', 'Texas'),
        ('Atlantic 10 Conference', 'a10', 'A-10', 'mid_major', 'northeast', 1975, 'Newport News', 'Virginia'),
        ('Mountain West Conference', 'mountain-west', 'MWC', 'mid_major', 'west', 1998, 'Colorado Springs', 'Colorado'),
        ('West Coast Conference', 'wcc', 'WCC', 'mid_major', 'west', 1952, 'San Bruno', 'California')
    ]

    for conf_data in conferences_data:
        cursor.execute("""
            INSERT OR IGNORE INTO college_conferences (
                division_id, name, slug, abbreviation, conference_type, region,
                founded_year, headquarters_city, headquarters_state, is_active, auto_bid_tournament
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
        """, (division_i_id,) + conf_data)

    # Get college basketball sport ID
    cursor.execute("SELECT id FROM sports WHERE slug = 'college-basketball'")
    sport_result = cursor.fetchone()
    if not sport_result:
        print("⚠️  College Basketball sport not found, creating it...")
        cursor.execute("""
            INSERT INTO sports (name, slug, has_teams, is_active, display_order)
            VALUES ('College Basketball', 'college-basketball', 1, 1, 7)
        """)
        cursor.execute("SELECT id FROM sports WHERE slug = 'college-basketball'")
        sport_result = cursor.fetchone()

    college_basketball_sport_id = sport_result[0]

    # Sample teams for testing (reduced set for demonstration)
    sample_teams_data = [
        # ACC (5 teams)
        ('acc', 'Duke University', 'duke-university', 'Durham', 'North Carolina', 'Blue Devils'),
        ('acc', 'University of North Carolina', 'university-of-north-carolina', 'Chapel Hill', 'North Carolina', 'Tar Heels'),
        ('acc', 'Virginia Tech', 'virginia-tech', 'Blacksburg', 'Virginia', 'Hokies'),
        ('acc', 'University of Virginia', 'university-of-virginia', 'Charlottesville', 'Virginia', 'Cavaliers'),
        ('acc', 'Florida State University', 'florida-state-university', 'Tallahassee', 'Florida', 'Seminoles'),

        # SEC (5 teams)
        ('sec', 'University of Kentucky', 'university-of-kentucky', 'Lexington', 'Kentucky', 'Wildcats'),
        ('sec', 'University of Florida', 'university-of-florida', 'Gainesville', 'Florida', 'Gators'),
        ('sec', 'University of Alabama', 'university-of-alabama', 'Tuscaloosa', 'Alabama', 'Crimson Tide'),
        ('sec', 'Auburn University', 'auburn-university', 'Auburn', 'Alabama', 'Tigers'),
        ('sec', 'University of Georgia', 'university-of-georgia', 'Athens', 'Georgia', 'Bulldogs'),

        # Big Ten (5 teams)
        ('big-ten', 'University of Michigan', 'university-of-michigan', 'Ann Arbor', 'Michigan', 'Wolverines'),
        ('big-ten', 'Michigan State University', 'michigan-state-university', 'East Lansing', 'Michigan', 'Spartans'),
        ('big-ten', 'Ohio State University', 'ohio-state-university', 'Columbus', 'Ohio', 'Buckeyes'),
        ('big-ten', 'Indiana University', 'indiana-university', 'Bloomington', 'Indiana', 'Hoosiers'),
        ('big-ten', 'Purdue University', 'purdue-university', 'West Lafayette', 'Indiana', 'Boilermakers'),

        # Big 12 (5 teams)
        ('big-12', 'University of Kansas', 'university-of-kansas', 'Lawrence', 'Kansas', 'Jayhawks'),
        ('big-12', 'Baylor University', 'baylor-university', 'Waco', 'Texas', 'Bears'),
        ('big-12', 'Texas Tech University', 'texas-tech-university', 'Lubbock', 'Texas', 'Red Raiders'),
        ('big-12', 'Iowa State University', 'iowa-state-university', 'Ames', 'Iowa', 'Cyclones'),
        ('big-12', 'Kansas State University', 'kansas-state-university', 'Manhattan', 'Kansas', 'Wildcats'),

        # Big East (5 teams)
        ('big-east', 'Villanova University', 'villanova-university', 'Villanova', 'Pennsylvania', 'Wildcats'),
        ('big-east', 'Georgetown University', 'georgetown-university', 'Washington', 'District of Columbia', 'Hoyas'),
        ('big-east', 'University of Connecticut', 'university-of-connecticut', 'Storrs', 'Connecticut', 'Huskies'),
        ('big-east', 'Marquette University', 'marquette-university', 'Milwaukee', 'Wisconsin', 'Golden Eagles'),
        ('big-east', 'Butler University', 'butler-university', 'Indianapolis', 'Indiana', 'Bulldogs')
    ]

    for conf_slug, college_name, college_slug, city, state, nickname in sample_teams_data:
        # Get conference ID
        cursor.execute("SELECT id FROM college_conferences WHERE slug = ?", (conf_slug,))
        conference_id = cursor.fetchone()[0]

        # Insert college
        cursor.execute("""
            INSERT OR IGNORE INTO colleges (
                conference_id, name, slug, college_type, city, state, nickname, is_active
            ) VALUES (?, ?, ?, 'public', ?, ?, ?, 1)
        """, (conference_id, college_name, college_slug, city, state, nickname))

        # Get college ID
        cursor.execute("SELECT id FROM colleges WHERE slug = ?", (college_slug,))
        college_result = cursor.fetchone()
        if college_result:
            college_id = college_result[0]

            # Insert college team
            team_slug = f"{college_slug}-{nickname.lower().replace(' ', '-')}"
            cursor.execute("""
                INSERT OR IGNORE INTO college_teams (
                    college_id, sport_id, name, slug, is_active
                ) VALUES (?, ?, ?, ?, 1)
            """, (college_id, college_basketball_sport_id, nickname, team_slug))

    print("✅ Phase 1 seed data inserted successfully!")


def main():
    """Main execution function."""
    print("🚀 Executing Phase 1 College Basketball Migration")
    print("=" * 60)

    # Database path
    db_path = backend_path / "sports_platform.db"

    if not db_path.exists():
        print("❌ Database file not found. Please ensure the database exists.")
        return 1

    # Create backup
    backup_path = create_backup(db_path)

    try:
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")

        # Execute schema migration
        execute_phase1_schema(cursor)

        # Execute seed data
        execute_phase1_seed_data(cursor)

        # Commit changes
        conn.commit()

        print("\n🎉 Phase 1 migration executed successfully!")
        print(f"📦 Backup available at: {backup_path}")

        # Quick verification
        cursor.execute("SELECT COUNT(*) FROM divisions")
        divisions_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM college_conferences")
        conferences_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM colleges")
        colleges_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM college_teams")
        teams_count = cursor.fetchone()[0]

        print(f"\n📊 Migration Summary:")
        print(f"   - Divisions: {divisions_count}")
        print(f"   - Conferences: {conferences_count}")
        print(f"   - Colleges: {colleges_count}")
        print(f"   - Teams: {teams_count}")

        return 0

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return 1

    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    sys.exit(main())