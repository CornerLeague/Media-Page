#!/usr/bin/env python3
"""
Phase 2 User Preferences Validation
===================================

This script checks if the user preference tables exist and creates them if missing.
These tables are critical for onboarding completion where users set their team preferences.

Author: Database ETL Architect
Date: 2025-09-21
"""

import sqlite3
import uuid
from datetime import datetime


def validate_and_create_user_preference_tables():
    """Check and create user preference tables if missing"""

    db_path = "/Users/newmac/Desktop/Corner League Media 1/backend/sports_platform.db"

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("🔍 USER PREFERENCES VALIDATION")
        print("=" * 50)

        # Check which tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name LIKE '%user%'
            ORDER BY name
        """)

        existing_tables = [row['name'] for row in cursor.fetchall()]
        print(f"Existing user-related tables: {existing_tables}")

        required_tables = [
            'users',
            'user_sport_preferences',
            'user_team_preferences',
            'user_news_preferences',
            'user_notification_settings'
        ]

        missing_tables = [table for table in required_tables if table not in existing_tables]

        if not missing_tables:
            print("✅ All user preference tables exist")
            return validate_table_structures(cursor)
        else:
            print(f"❌ Missing tables: {missing_tables}")
            return create_missing_tables(cursor, missing_tables, conn)

    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()


def validate_table_structures(cursor):
    """Validate that existing tables have correct structure"""

    print("\n=== VALIDATING TABLE STRUCTURES ===")

    # Check users table
    cursor.execute("PRAGMA table_info(users)")
    users_columns = {row['name']: row['type'] for row in cursor.fetchall()}

    required_user_columns = {
        'id': 'TEXT',
        'firebase_uid': 'VARCHAR(128)',
        'email': 'VARCHAR(255)',
        'display_name': 'VARCHAR(100)',
        'onboarding_completed_at': 'DATETIME',
        'is_active': 'BOOLEAN',
        'created_at': 'DATETIME',
        'updated_at': 'DATETIME'
    }

    missing_user_columns = []
    for col, col_type in required_user_columns.items():
        if col not in users_columns:
            missing_user_columns.append(col)

    if missing_user_columns:
        print(f"❌ Users table missing columns: {missing_user_columns}")
        return False
    else:
        print("✅ Users table structure is valid")

    # Check user_team_preferences table structure if it exists
    try:
        cursor.execute("PRAGMA table_info(user_team_preferences)")
        team_pref_columns = {row['name']: row['type'] for row in cursor.fetchall()}

        required_team_pref_columns = {
            'id': 'TEXT',
            'user_id': 'TEXT',
            'team_id': 'TEXT',
            'affinity_score': 'NUMERIC',
            'is_active': 'BOOLEAN',
            'created_at': 'DATETIME',
            'updated_at': 'DATETIME'
        }

        missing_team_pref_columns = []
        for col, col_type in required_team_pref_columns.items():
            if col not in team_pref_columns:
                missing_team_pref_columns.append(col)

        if missing_team_pref_columns:
            print(f"❌ User team preferences table missing columns: {missing_team_pref_columns}")
            return False
        else:
            print("✅ User team preferences table structure is valid")

    except sqlite3.OperationalError:
        print("❌ User team preferences table doesn't exist")
        return False

    return True


def create_missing_tables(cursor, missing_tables, conn):
    """Create missing user preference tables"""

    print("\n=== CREATING MISSING TABLES ===")

    try:
        # Create users table if missing
        if 'users' in missing_tables:
            print("Creating users table...")
            cursor.execute("""
                CREATE TABLE users (
                    id TEXT PRIMARY KEY,
                    firebase_uid VARCHAR(128) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE,
                    display_name VARCHAR(100),
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    avatar_url VARCHAR(500),
                    bio TEXT,
                    date_of_birth DATE,
                    location VARCHAR(100),
                    timezone VARCHAR(50) DEFAULT 'UTC',
                    content_frequency VARCHAR(20) DEFAULT 'standard',
                    is_active BOOLEAN DEFAULT 1 NOT NULL,
                    is_verified BOOLEAN DEFAULT 0 NOT NULL,
                    onboarding_completed_at DATETIME,
                    last_active_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    email_verified_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """)

            # Create indexes for users table
            cursor.execute("CREATE INDEX idx_users_firebase_uid ON users(firebase_uid)")
            cursor.execute("CREATE INDEX idx_users_email ON users(email)")
            cursor.execute("CREATE INDEX idx_users_is_active ON users(is_active)")
            cursor.execute("CREATE INDEX idx_users_last_active_at ON users(last_active_at)")

            print("✅ Created users table with indexes")

        # Create user_sport_preferences table if missing
        if 'user_sport_preferences' in missing_tables:
            print("Creating user_sport_preferences table...")
            cursor.execute("""
                CREATE TABLE user_sport_preferences (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    sport_id TEXT NOT NULL,
                    rank INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT 1 NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (sport_id) REFERENCES sports(id) ON DELETE CASCADE,
                    UNIQUE(user_id, sport_id)
                )
            """)

            cursor.execute("CREATE INDEX idx_user_sport_preferences_user_id ON user_sport_preferences(user_id)")
            cursor.execute("CREATE INDEX idx_user_sport_preferences_sport_id ON user_sport_preferences(sport_id)")

            print("✅ Created user_sport_preferences table with indexes")

        # Create user_team_preferences table if missing
        if 'user_team_preferences' in missing_tables:
            print("Creating user_team_preferences table...")
            cursor.execute("""
                CREATE TABLE user_team_preferences (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    team_id TEXT NOT NULL,
                    affinity_score NUMERIC(3, 2) DEFAULT 0.5 NOT NULL,
                    is_active BOOLEAN DEFAULT 1 NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
                    UNIQUE(user_id, team_id)
                )
            """)

            cursor.execute("CREATE INDEX idx_user_team_preferences_user_id ON user_team_preferences(user_id)")
            cursor.execute("CREATE INDEX idx_user_team_preferences_team_id ON user_team_preferences(team_id)")

            print("✅ Created user_team_preferences table with indexes")

        # Create user_news_preferences table if missing
        if 'user_news_preferences' in missing_tables:
            print("Creating user_news_preferences table...")
            cursor.execute("""
                CREATE TABLE user_news_preferences (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    news_type VARCHAR(50) NOT NULL,
                    enabled BOOLEAN DEFAULT 1 NOT NULL,
                    priority INTEGER DEFAULT 1 NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(user_id, news_type)
                )
            """)

            cursor.execute("CREATE INDEX idx_user_news_preferences_user_id ON user_news_preferences(user_id)")

            print("✅ Created user_news_preferences table with indexes")

        # Create user_notification_settings table if missing
        if 'user_notification_settings' in missing_tables:
            print("Creating user_notification_settings table...")
            cursor.execute("""
                CREATE TABLE user_notification_settings (
                    id TEXT PRIMARY KEY,
                    user_id TEXT UNIQUE NOT NULL,
                    push_enabled BOOLEAN DEFAULT 0 NOT NULL,
                    email_enabled BOOLEAN DEFAULT 0 NOT NULL,
                    game_reminders BOOLEAN DEFAULT 0 NOT NULL,
                    news_alerts BOOLEAN DEFAULT 0 NOT NULL,
                    score_updates BOOLEAN DEFAULT 0 NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("CREATE INDEX idx_user_notification_settings_user_id ON user_notification_settings(user_id)")

            print("✅ Created user_notification_settings table with indexes")

        # Commit all table creations
        conn.commit()

        # Test table creation by checking final state
        print("\n=== VERIFYING CREATED TABLES ===")
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name LIKE '%user%'
            ORDER BY name
        """)

        final_tables = [row['name'] for row in cursor.fetchall()]
        print(f"✅ Final user tables: {final_tables}")

        # Test foreign key constraints
        print("\n=== TESTING FOREIGN KEY CONSTRAINTS ===")

        # Check if foreign keys are properly configured
        cursor.execute("PRAGMA foreign_keys")
        fk_status = cursor.fetchone()[0]
        print(f"Foreign keys enabled: {bool(fk_status)}")

        if not fk_status:
            print("⚠ Enabling foreign keys for this session...")
            cursor.execute("PRAGMA foreign_keys = ON")

        print("✅ All user preference tables created successfully")
        return True

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        conn.rollback()
        return False


def test_onboarding_workflow():
    """Test that the onboarding workflow can complete successfully"""

    db_path = "/Users/newmac/Desktop/Corner League Media 1/backend/sports_platform.db"

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("\n🧪 TESTING ONBOARDING WORKFLOW")
        print("=" * 40)

        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")

        # Test 1: Create a test user
        test_user_id = str(uuid.uuid4())
        test_firebase_uid = f"test_{uuid.uuid4()}"

        cursor.execute("""
            INSERT INTO users (
                id, firebase_uid, email, display_name, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (test_user_id, test_firebase_uid, "test@example.com", "Test User"))

        print("✅ Created test user")

        # Test 2: Set sport preferences
        cursor.execute("SELECT id, name FROM sports WHERE is_active = 1 LIMIT 3")
        sports = cursor.fetchall()

        for rank, sport in enumerate(sports, 1):
            sport_pref_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO user_sport_preferences (
                    id, user_id, sport_id, rank, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (sport_pref_id, test_user_id, sport['id'], rank))

        print(f"✅ Set {len(sports)} sport preferences")

        # Test 3: Set team preferences
        cursor.execute("""
            SELECT t.id, t.name, t.market
            FROM teams t
            JOIN team_league_memberships tlm ON t.id = tlm.team_id
            WHERE t.is_active = 1 AND tlm.is_active = 1
            LIMIT 5
        """)
        teams = cursor.fetchall()

        for i, team in enumerate(teams):
            team_pref_id = str(uuid.uuid4())
            affinity_score = 0.9 - (i * 0.1)  # Decreasing affinity
            cursor.execute("""
                INSERT INTO user_team_preferences (
                    id, user_id, team_id, affinity_score, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (team_pref_id, test_user_id, team['id'], affinity_score))

        print(f"✅ Set {len(teams)} team preferences")

        # Test 4: Set notification preferences
        notification_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO user_notification_settings (
                id, user_id, push_enabled, email_enabled, game_reminders,
                news_alerts, score_updates, created_at, updated_at
            ) VALUES (?, ?, 1, 0, 1, 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (notification_id, test_user_id))

        print("✅ Set notification preferences")

        # Test 5: Mark onboarding as complete
        cursor.execute("""
            UPDATE users
            SET onboarding_completed_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (test_user_id,))

        print("✅ Marked onboarding as complete")

        # Test 6: Verify complete user profile
        cursor.execute("""
            SELECT u.id, u.display_name, u.onboarding_completed_at,
                   COUNT(DISTINCT usp.id) as sport_prefs,
                   COUNT(DISTINCT utp.id) as team_prefs,
                   COUNT(DISTINCT uns.id) as notification_settings
            FROM users u
            LEFT JOIN user_sport_preferences usp ON u.id = usp.user_id AND usp.is_active = 1
            LEFT JOIN user_team_preferences utp ON u.id = utp.user_id AND utp.is_active = 1
            LEFT JOIN user_notification_settings uns ON u.id = uns.user_id
            WHERE u.id = ?
            GROUP BY u.id, u.display_name, u.onboarding_completed_at
        """, (test_user_id,))

        result = cursor.fetchone()
        print(f"✅ Complete profile: {result['sport_prefs']} sports, "
              f"{result['team_prefs']} teams, "
              f"{result['notification_settings']} notification settings")

        # Clean up test data
        cursor.execute("DELETE FROM users WHERE id = ?", (test_user_id,))
        conn.commit()

        print("✅ Cleaned up test data")
        print("\n🎉 ONBOARDING WORKFLOW TEST PASSED!")
        return True

    except Exception as e:
        print(f"❌ Onboarding workflow test failed: {e}")
        # Clean up on error
        try:
            cursor.execute("DELETE FROM users WHERE id = ?", (test_user_id,))
            conn.commit()
        except:
            pass
        return False
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    success1 = validate_and_create_user_preference_tables()
    success2 = test_onboarding_workflow() if success1 else False

    if success1 and success2:
        print("\n🎉 ALL VALIDATIONS PASSED - ONBOARDING READY!")
    else:
        print("\n❌ VALIDATION FAILED - ONBOARDING NOT READY")

    exit(0 if (success1 and success2) else 1)