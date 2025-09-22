"""
Database migration for onboarding enhancements
Adds current_onboarding_step to users table and onboarding fields to sports table
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def get_database_path() -> str:
    """Get the path to the SQLite database"""
    backend_dir = Path(__file__).parent.parent
    return str(backend_dir / "sports_platform.db")


def migrate_users_table(conn: sqlite3.Connection) -> None:
    """Add current_onboarding_step column to users table"""
    try:
        # Check if column already exists
        cursor = conn.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'current_onboarding_step' not in columns:
            logger.info("Adding current_onboarding_step column to users table")
            conn.execute("""
                ALTER TABLE users
                ADD COLUMN current_onboarding_step INTEGER
            """)
            logger.info("Successfully added current_onboarding_step column")
        else:
            logger.info("current_onboarding_step column already exists in users table")

    except Exception as e:
        logger.error(f"Error migrating users table: {str(e)}")
        raise


def migrate_sports_table(conn: sqlite3.Connection) -> None:
    """Add onboarding-related columns to sports table"""
    try:
        # Check existing columns
        cursor = conn.execute("PRAGMA table_info(sports)")
        columns = [row[1] for row in cursor.fetchall()]

        # Add icon_url column
        if 'icon_url' not in columns:
            logger.info("Adding icon_url column to sports table")
            conn.execute("""
                ALTER TABLE sports
                ADD COLUMN icon_url TEXT
            """)
            logger.info("Successfully added icon_url column")
        else:
            logger.info("icon_url column already exists in sports table")

        # Add description column
        if 'description' not in columns:
            logger.info("Adding description column to sports table")
            conn.execute("""
                ALTER TABLE sports
                ADD COLUMN description TEXT
            """)
            logger.info("Successfully added description column")
        else:
            logger.info("description column already exists in sports table")

        # Add popularity_rank column
        if 'popularity_rank' not in columns:
            logger.info("Adding popularity_rank column to sports table")
            conn.execute("""
                ALTER TABLE sports
                ADD COLUMN popularity_rank INTEGER DEFAULT 999
            """)
            logger.info("Successfully added popularity_rank column")
        else:
            logger.info("popularity_rank column already exists in sports table")

    except Exception as e:
        logger.error(f"Error migrating sports table: {str(e)}")
        raise


def seed_sports_onboarding_data(conn: sqlite3.Connection) -> None:
    """Seed initial onboarding data for sports"""
    try:
        logger.info("Seeding sports onboarding data")

        # Update sports with onboarding data
        sports_data = [
            ("basketball", "Fast-paced indoor sport with two teams shooting hoops", 1),
            ("football", "American football with strategic gameplay and tackles", 2),
            ("baseball", "Classic American pastime with batting and pitching", 3),
            ("hockey", "High-speed ice sport with sticks and pucks", 4),
            ("soccer", "Global sport played with feet and a ball", 5),
            ("college-basketball", "Collegiate basketball with March Madness excitement", 6),
            ("college-football", "University-level football with passionate fan bases", 7),
        ]

        for slug, description, rank in sports_data:
            conn.execute("""
                UPDATE sports
                SET description = ?, popularity_rank = ?
                WHERE slug = ?
            """, (description, rank, slug))

        logger.info("Successfully seeded sports onboarding data")

    except Exception as e:
        logger.error(f"Error seeding sports onboarding data: {str(e)}")
        raise


def run_migration() -> None:
    """Run the complete onboarding enhancements migration"""
    db_path = get_database_path()

    if not Path(db_path).exists():
        logger.error(f"Database file not found: {db_path}")
        raise FileNotFoundError(f"Database file not found: {db_path}")

    logger.info(f"Starting onboarding enhancements migration on {db_path}")

    try:
        with sqlite3.connect(db_path) as conn:
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")

            # Run migrations
            migrate_users_table(conn)
            migrate_sports_table(conn)
            seed_sports_onboarding_data(conn)

            # Commit changes
            conn.commit()

        logger.info("Onboarding enhancements migration completed successfully")

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise


def rollback_migration() -> None:
    """Rollback the onboarding enhancements migration"""
    db_path = get_database_path()

    logger.info(f"Rolling back onboarding enhancements migration on {db_path}")

    try:
        with sqlite3.connect(db_path) as conn:
            # Note: SQLite doesn't support DROP COLUMN, so we can't easily rollback
            # In a production environment, you'd want to recreate the table without these columns

            # Reset sports data
            conn.execute("""
                UPDATE sports
                SET description = NULL, popularity_rank = 999
            """)

            # Reset user onboarding steps
            conn.execute("""
                UPDATE users
                SET current_onboarding_step = NULL
            """)

            conn.commit()

        logger.info("Onboarding enhancements migration rolled back successfully")

    except Exception as e:
        logger.error(f"Rollback failed: {str(e)}")
        raise


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        run_migration()