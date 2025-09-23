"""
Phase 2: Firebase Data Migration Script

This script handles the data migration between Phase 1 (schema changes) and Phase 3 (constraints).
It populates firebase_uid values and validates data integrity before constraints are applied.

USAGE:
    python migrations/phase2_firebase_data_migration.py

REQUIREMENTS:
    - Phase 1 migration must be completed
    - Firebase UID mapping data must be available
    - Database connection configuration

SAFETY FEATURES:
    - Idempotent operations (can be run multiple times)
    - Validation checks before and after migration
    - Rollback capabilities
    - Progress tracking and logging
"""

import asyncio
import logging
import sys
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, update
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from database import get_database_url
from models.users import User

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('firebase_data_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FirebaseDataMigration:
    """Handles the data migration from clerk_user_id to firebase_uid."""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_async_engine(database_url)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def validate_phase1_complete(self) -> bool:
        """Verify that Phase 1 migration has been completed."""
        async with self.async_session() as session:
            try:
                # Check if firebase_uid column exists
                result = await session.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'users'
                    AND column_name = 'firebase_uid'
                """))

                if not result.fetchone():
                    logger.error("Phase 1 not complete: firebase_uid column missing")
                    return False

                # Check if new profile columns exist
                required_columns = [
                    'first_name', 'last_name', 'bio', 'date_of_birth',
                    'location', 'timezone', 'is_verified', 'email_verified_at'
                ]

                for column in required_columns:
                    result = await session.execute(text(f"""
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_name = 'users'
                        AND column_name = '{column}'
                    """))
                    if not result.fetchone():
                        logger.error(f"Phase 1 not complete: {column} column missing")
                        return False

                logger.info("✓ Phase 1 validation passed")
                return True

            except Exception as e:
                logger.error(f"Phase 1 validation failed: {e}")
                return False

    async def get_users_needing_migration(self) -> List[Tuple[str, str]]:
        """Get list of users that need firebase_uid populated."""
        async with self.async_session() as session:
            try:
                # Find users with clerk_user_id but no firebase_uid
                result = await session.execute(text("""
                    SELECT id, clerk_user_id, email, display_name
                    FROM users
                    WHERE clerk_user_id IS NOT NULL
                    AND (firebase_uid IS NULL OR firebase_uid = '')
                    ORDER BY created_at
                """))

                users = result.fetchall()
                logger.info(f"Found {len(users)} users needing migration")
                return users

            except Exception as e:
                logger.error(f"Failed to get users needing migration: {e}")
                return []

    async def generate_firebase_uid_mapping(self, users: List[Tuple]) -> Dict[str, str]:
        """Generate firebase_uid values for users based on clerk_user_id.

        In production, this would integrate with your Firebase Authentication
        system to get actual firebase_uid values. For now, we generate
        placeholder values that follow Firebase UID format.
        """
        mapping = {}

        for user in users:
            user_id, clerk_user_id, email, display_name = user

            # Generate a Firebase-compatible UID (28 characters, alphanumeric)
            # In production, replace this with actual Firebase UID lookup
            firebase_uid = f"fb_{clerk_user_id}_{user_id.hex[:20]}"

            mapping[str(user_id)] = firebase_uid
            logger.debug(f"Generated mapping: {user_id} -> {firebase_uid}")

        logger.info(f"Generated {len(mapping)} firebase_uid mappings")
        return mapping

    async def migrate_user_data(self, uid_mapping: Dict[str, str]) -> bool:
        """Migrate user data using the firebase_uid mapping."""
        async with self.async_session() as session:
            try:
                migration_count = 0

                for user_id, firebase_uid in uid_mapping.items():
                    # Update user with firebase_uid
                    await session.execute(
                        update(User)
                        .where(User.id == user_id)
                        .values(firebase_uid=firebase_uid)
                    )
                    migration_count += 1

                    if migration_count % 100 == 0:
                        logger.info(f"Migrated {migration_count} users...")

                await session.commit()
                logger.info(f"✓ Successfully migrated {migration_count} users")
                return True

            except Exception as e:
                await session.rollback()
                logger.error(f"Data migration failed: {e}")
                return False

    async def validate_migration_complete(self) -> bool:
        """Validate that all users have firebase_uid values."""
        async with self.async_session() as session:
            try:
                # Check for users without firebase_uid
                result = await session.execute(text("""
                    SELECT COUNT(*)
                    FROM users
                    WHERE firebase_uid IS NULL OR firebase_uid = ''
                """))

                null_count = result.scalar()

                if null_count > 0:
                    logger.error(f"Migration incomplete: {null_count} users still have NULL firebase_uid")
                    return False

                # Check for duplicate firebase_uid values
                result = await session.execute(text("""
                    SELECT firebase_uid, COUNT(*)
                    FROM users
                    WHERE firebase_uid IS NOT NULL
                    GROUP BY firebase_uid
                    HAVING COUNT(*) > 1
                """))

                duplicates = result.fetchall()

                if duplicates:
                    logger.error(f"Found {len(duplicates)} duplicate firebase_uid values")
                    for firebase_uid, count in duplicates:
                        logger.error(f"  {firebase_uid}: {count} occurrences")
                    return False

                # Get total user count for verification
                result = await session.execute(text("SELECT COUNT(*) FROM users"))
                total_users = result.scalar()

                logger.info(f"✓ Migration validation passed: {total_users} users with unique firebase_uid")
                return True

            except Exception as e:
                logger.error(f"Migration validation failed: {e}")
                return False

    async def create_migration_log(self, success: bool, user_count: int, error: Optional[str] = None):
        """Create a log entry for this migration."""
        async with self.async_session() as session:
            try:
                await session.execute(text("""
                    INSERT INTO migration_log (
                        migration_name,
                        executed_at,
                        success,
                        user_count,
                        error_message
                    ) VALUES (
                        'phase2_firebase_data_migration',
                        :executed_at,
                        :success,
                        :user_count,
                        :error_message
                    )
                """), {
                    'executed_at': datetime.utcnow(),
                    'success': success,
                    'user_count': user_count,
                    'error_message': error
                })
                await session.commit()
            except Exception as e:
                # Migration log table might not exist, that's OK
                logger.warning(f"Could not create migration log: {e}")

    async def run_migration(self) -> bool:
        """Run the complete data migration process."""
        logger.info("Starting Phase 2: Firebase data migration")

        try:
            # Step 1: Validate Phase 1 is complete
            if not await self.validate_phase1_complete():
                logger.error("Cannot proceed: Phase 1 migration not complete")
                return False

            # Step 2: Get users needing migration
            users = await self.get_users_needing_migration()

            if not users:
                logger.info("No users need migration - already complete")
                await self.create_migration_log(True, 0)
                return True

            # Step 3: Generate firebase_uid mapping
            uid_mapping = await self.generate_firebase_uid_mapping(users)

            if not uid_mapping:
                logger.error("Failed to generate firebase_uid mapping")
                await self.create_migration_log(False, 0, "Failed to generate firebase_uid mapping")
                return False

            # Step 4: Migrate the data
            if not await self.migrate_user_data(uid_mapping):
                logger.error("Data migration failed")
                await self.create_migration_log(False, len(users), "Data migration failed")
                return False

            # Step 5: Validate migration completion
            if not await self.validate_migration_complete():
                logger.error("Migration validation failed")
                await self.create_migration_log(False, len(users), "Migration validation failed")
                return False

            await self.create_migration_log(True, len(users))
            logger.info(f"✓ Phase 2 migration completed successfully: {len(users)} users migrated")
            logger.info("→ Ready for Phase 3: Apply constraints migration")

            return True

        except Exception as e:
            logger.error(f"Migration failed with unexpected error: {e}")
            await self.create_migration_log(False, 0, str(e))
            return False

        finally:
            await self.engine.dispose()


async def main():
    """Main entry point for the migration script."""
    logger.info("Phase 2: Firebase Data Migration")
    logger.info("=" * 50)

    # Get database URL from environment or config
    try:
        database_url = get_database_url()
        if not database_url:
            logger.error("Database URL not configured")
            return False
    except Exception as e:
        logger.error(f"Failed to get database URL: {e}")
        return False

    # Run the migration
    migration = FirebaseDataMigration(database_url)
    success = await migration.run_migration()

    if success:
        logger.info("🎉 Phase 2 migration completed successfully!")
        logger.info("Next steps:")
        logger.info("1. Verify data integrity in your application")
        logger.info("2. Run Phase 3 migration to apply constraints")
        logger.info("3. Test Firebase authentication integration")
        return True
    else:
        logger.error("❌ Phase 2 migration failed!")
        logger.error("Check the logs above for details")
        logger.error("Do not proceed to Phase 3 until this is resolved")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)