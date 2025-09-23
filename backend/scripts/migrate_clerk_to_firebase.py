#!/usr/bin/env python3
"""
Data migration script for Clerk to Firebase user authentication.

This script should be run AFTER the schema migration but BEFORE making firebase_uid NOT NULL.

Usage:
    python scripts/migrate_clerk_to_firebase.py --dry-run  # Test without changes
    python scripts/migrate_clerk_to_firebase.py           # Execute migration

Requirements:
- Database connection configured
- Mapping file or service to convert clerk_user_id to firebase_uid
- Adequate backup of users table before running
"""

import asyncio
import logging
import argparse
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update, text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClerkToFirebaseMigrator:
    """Handles migration of user authentication from Clerk to Firebase."""

    def __init__(self, database_url: str, dry_run: bool = False):
        self.database_url = database_url
        self.dry_run = dry_run
        self.engine = create_async_engine(database_url)
        self.async_session = sessionmaker(self.engine, class_=AsyncSession)

    async def get_clerk_to_firebase_mapping(self) -> Dict[str, str]:
        """
        Get mapping from clerk_user_id to firebase_uid.

        In production, this would:
        1. Query your authentication service API
        2. Read from a prepared mapping file
        3. Use existing database relationships

        Returns:
            Dict mapping clerk_user_id -> firebase_uid
        """
        # PLACEHOLDER: Implement your mapping logic here
        # This is just an example structure
        mapping = {}

        # Example: Read from mapping file
        # with open('clerk_firebase_mapping.json', 'r') as f:
        #     mapping = json.load(f)

        # Example: Query authentication service
        # for clerk_id in clerk_ids:
        #     firebase_uid = await auth_service.get_firebase_uid(clerk_id)
        #     mapping[clerk_id] = firebase_uid

        logger.warning("PLACEHOLDER: Implement get_clerk_to_firebase_mapping() with actual mapping logic")
        return mapping

    async def validate_mapping(self, mapping: Dict[str, str]) -> bool:
        """Validate the clerk->firebase mapping."""
        async with self.async_session() as session:
            # Get all current clerk_user_ids
            result = await session.execute(
                text("SELECT clerk_user_id FROM users WHERE clerk_user_id IS NOT NULL")
            )
            clerk_ids = {row[0] for row in result.fetchall()}

            # Check mapping coverage
            mapped_ids = set(mapping.keys())
            missing_mappings = clerk_ids - mapped_ids
            extra_mappings = mapped_ids - clerk_ids

            if missing_mappings:
                logger.error(f"Missing mappings for clerk_user_ids: {missing_mappings}")
                return False

            if extra_mappings:
                logger.warning(f"Extra mappings (users may have been deleted): {extra_mappings}")

            # Check for duplicate firebase_uids
            firebase_uids = list(mapping.values())
            if len(firebase_uids) != len(set(firebase_uids)):
                logger.error("Duplicate firebase_uids found in mapping")
                return False

            logger.info(f"Mapping validation successful: {len(mapping)} users to migrate")
            return True

    async def migrate_users(self, mapping: Dict[str, str]) -> bool:
        """Migrate users from clerk_user_id to firebase_uid."""
        async with self.async_session() as session:
            try:
                migrated_count = 0

                for clerk_id, firebase_uid in mapping.items():
                    if self.dry_run:
                        logger.info(f"DRY RUN: Would migrate {clerk_id} -> {firebase_uid}")
                    else:
                        # Update user record
                        result = await session.execute(
                            update(text("users"))
                            .where(text("clerk_user_id = :clerk_id"))
                            .values(firebase_uid=firebase_uid)
                            .values({"clerk_id": clerk_id})
                        )

                        if result.rowcount == 1:
                            migrated_count += 1
                            logger.debug(f"Migrated user {clerk_id} -> {firebase_uid}")
                        else:
                            logger.error(f"Failed to migrate user {clerk_id}")

                if not self.dry_run:
                    await session.commit()
                    logger.info(f"Successfully migrated {migrated_count} users")
                else:
                    logger.info(f"DRY RUN: Would migrate {len(mapping)} users")

                return True

            except Exception as e:
                if not self.dry_run:
                    await session.rollback()
                logger.error(f"Migration failed: {e}")
                return False

    async def verify_migration(self) -> bool:
        """Verify that migration completed successfully."""
        async with self.async_session() as session:
            # Check that all users have firebase_uid
            result = await session.execute(
                text("SELECT COUNT(*) FROM users WHERE firebase_uid IS NULL")
            )
            null_count = result.scalar()

            if null_count > 0:
                logger.error(f"{null_count} users still have NULL firebase_uid")
                return False

            # Check for duplicate firebase_uids
            result = await session.execute(
                text("""
                    SELECT firebase_uid, COUNT(*) as count
                    FROM users
                    GROUP BY firebase_uid
                    HAVING COUNT(*) > 1
                """)
            )
            duplicates = result.fetchall()

            if duplicates:
                logger.error(f"Found duplicate firebase_uids: {duplicates}")
                return False

            # Get total user count
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            total_users = result.scalar()

            logger.info(f"Migration verification successful: {total_users} users with unique firebase_uids")
            return True

    async def run(self) -> bool:
        """Execute the complete migration process."""
        try:
            logger.info("Starting Clerk to Firebase migration")

            # Step 1: Get mapping
            mapping = await self.get_clerk_to_firebase_mapping()
            if not mapping:
                logger.error("No mapping data available")
                return False

            # Step 2: Validate mapping
            if not await self.validate_mapping(mapping):
                logger.error("Mapping validation failed")
                return False

            # Step 3: Migrate users
            if not await self.migrate_users(mapping):
                logger.error("User migration failed")
                return False

            # Step 4: Verify migration (skip for dry run)
            if not self.dry_run:
                if not await self.verify_migration():
                    logger.error("Migration verification failed")
                    return False

            logger.info("Migration completed successfully")
            return True

        except Exception as e:
            logger.error(f"Migration process failed: {e}")
            return False
        finally:
            await self.engine.dispose()


async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Migrate users from Clerk to Firebase authentication")
    parser.add_argument("--dry-run", action="store_true", help="Run without making changes")
    parser.add_argument("--database-url", help="Database connection URL (defaults to DATABASE_URL env var)")

    args = parser.parse_args()

    # Get database URL
    database_url = args.database_url
    if not database_url:
        import os
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("No database URL provided. Use --database-url or set DATABASE_URL environment variable")
            return False

    # Run migration
    migrator = ClerkToFirebaseMigrator(database_url, dry_run=args.dry_run)
    success = await migrator.run()

    if success:
        if args.dry_run:
            logger.info("Dry run completed successfully")
        else:
            logger.info("Migration completed successfully")
        return True
    else:
        logger.error("Migration failed")
        return False


if __name__ == "__main__":
    import sys
    success = asyncio.run(main())
    sys.exit(0 if success else 1)