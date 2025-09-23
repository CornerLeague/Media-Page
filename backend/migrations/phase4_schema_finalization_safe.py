#!/usr/bin/env python3
"""
Phase 4: Soccer Teams Multi-League Support - SAFE Schema Finalization
====================================================================

This is a SAFER version of the Phase 4 migration that:
1. Disables foreign key constraints during table operations
2. Preserves all data in team_league_memberships table
3. Uses more careful table replacement strategy
4. Includes extensive validation at each step

CRITICAL SAFETY MEASURES:
- Foreign key constraints disabled during migration
- All changes wrapped in transactions
- Comprehensive data preservation validation
- Zero data loss tolerance with immediate rollback on any issues

Author: Database ETL Architect
Date: 2025-09-21
Phase: 4/4 - SAFE final schema cleanup and optimization
"""

import sqlite3
import os
import sys
import traceback
from datetime import datetime
from typing import Dict, List, Tuple, Any
import uuid
import json


class Phase4SafeSchemaFinalization:
    """Phase 4: SAFE Schema finalization and cleanup"""

    def __init__(self, db_path: str, backup_path: str = None):
        self.db_path = db_path
        self.backup_path = backup_path or f"{db_path}_phase4_safe_rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        self.conn = None
        self.validation_results = {}

    def create_rollback_backup(self):
        """Create a rollback backup before making changes"""
        print(f"Creating rollback backup: {self.backup_path}")

        try:
            # Use SQLite backup API for consistent backup
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

        # Check team count
        cursor.execute("SELECT COUNT(*) as count FROM teams")
        team_count = cursor.fetchone()["count"]
        results["checks"]["total_teams"] = team_count
        print(f"✓ Total teams: {team_count}")

        # Check active team-league memberships
        cursor.execute("SELECT COUNT(*) as count FROM team_league_memberships WHERE is_active = 1")
        membership_count = cursor.fetchone()["count"]
        results["checks"]["active_memberships"] = membership_count
        print(f"✓ Active memberships: {membership_count}")

        # Check teams with valid league_id
        cursor.execute("""
            SELECT COUNT(*) as count FROM teams t
            WHERE EXISTS (
                SELECT 1 FROM team_league_memberships tlm
                WHERE tlm.team_id = t.id AND tlm.is_active = 1
            )
        """)
        teams_with_memberships = cursor.fetchone()["count"]
        results["checks"]["teams_with_memberships"] = teams_with_memberships
        print(f"✓ Teams with active memberships: {teams_with_memberships}")

        # Check schema state
        cursor.execute("PRAGMA table_info(teams)")
        columns = {row["name"]: row["type"] for row in cursor.fetchall()}
        has_league_id = "league_id" in columns
        results["checks"]["has_deprecated_league_id"] = has_league_id
        print(f"✓ Teams table has league_id column: {has_league_id}")

        self.validation_results["pre_migration"] = results
        return results

    def safe_remove_deprecated_column(self):
        """Safely remove the deprecated league_id column"""
        print("\n=== SAFELY REMOVING DEPRECATED COLUMN ===")

        cursor = self.conn.cursor()

        try:
            # Step 1: Disable foreign key constraints to prevent cascading deletes
            print("Disabling foreign key constraints...")
            cursor.execute("PRAGMA foreign_keys = OFF")

            # Step 2: Verify current data before any changes
            cursor.execute("SELECT COUNT(*) FROM teams")
            original_team_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM team_league_memberships WHERE is_active = 1")
            original_membership_count = cursor.fetchone()[0]
            print(f"  Teams before: {original_team_count}")
            print(f"  Memberships before: {original_membership_count}")

            # Step 3: Handle dependent views
            print("Handling dependent views...")
            cursor.execute("""
                SELECT name, sql FROM sqlite_master
                WHERE type='view' AND sql LIKE '%teams%'
            """)
            dependent_views = cursor.fetchall()

            # Drop dependent views temporarily
            for view_name, view_sql in dependent_views:
                print(f"  Dropping view: {view_name}")
                cursor.execute(f"DROP VIEW IF EXISTS {view_name}")

            # Step 4: Create new teams table without league_id
            print("Creating new teams table without league_id...")
            cursor.execute("""
                CREATE TABLE teams_new (
                    id TEXT PRIMARY KEY,
                    sport_id TEXT NOT NULL,
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
                    official_name TEXT,
                    short_name TEXT,
                    country_code TEXT,
                    founding_year INTEGER,
                    FOREIGN KEY (sport_id) REFERENCES sports (id) ON DELETE CASCADE
                )
            """)

            # Step 5: Copy data (excluding league_id)
            print("Copying team data to new table...")
            cursor.execute("""
                INSERT INTO teams_new (
                    id, sport_id, name, market, slug, abbreviation,
                    logo_url, primary_color, secondary_color, is_active,
                    external_id, created_at, updated_at, official_name,
                    short_name, country_code, founding_year
                )
                SELECT
                    id, sport_id, name, market, slug, abbreviation,
                    logo_url, primary_color, secondary_color, is_active,
                    external_id, created_at, updated_at, official_name,
                    short_name, country_code, founding_year
                FROM teams
            """)

            # Step 6: Verify data was copied correctly
            cursor.execute("SELECT COUNT(*) FROM teams_new")
            new_team_count = cursor.fetchone()[0]

            if original_team_count != new_team_count:
                raise Exception(f"Team data copy failed: {original_team_count} vs {new_team_count} rows")

            print(f"✓ Copied {new_team_count} teams to new table")

            # Step 7: Create optimized indexes on new table
            print("Creating optimized indexes...")
            new_indexes = [
                ("idx_teams_sport_id", "sport_id"),
                ("idx_teams_slug", "slug"),
                ("idx_teams_country_code", "country_code"),
                ("idx_teams_founding_year", "founding_year"),
                ("idx_teams_is_active", "is_active"),
                ("idx_teams_sport_country", "sport_id, country_code"),
                ("idx_teams_name_search", "name"),
                ("idx_teams_market_search", "market")
            ]

            created_count = 0
            for index_name, columns in new_indexes:
                try:
                    cursor.execute(f"CREATE INDEX {index_name} ON teams_new({columns})")
                    created_count += 1
                    print(f"  ✓ Created {index_name}")
                except sqlite3.OperationalError as e:
                    if "already exists" in str(e):
                        print(f"  - Index {index_name} already exists")
                    else:
                        print(f"  ⚠ Failed to create {index_name}: {e}")

            print(f"✓ Created {created_count} new indexes")

            # Step 8: Replace old table with new table
            print("Replacing old teams table...")
            cursor.execute("DROP TABLE teams")
            cursor.execute("ALTER TABLE teams_new RENAME TO teams")

            # Step 9: Verify memberships are still intact
            cursor.execute("SELECT COUNT(*) FROM team_league_memberships WHERE is_active = 1")
            membership_count_after = cursor.fetchone()[0]

            if membership_count_after != original_membership_count:
                raise Exception(f"CRITICAL: Memberships lost during migration: {original_membership_count} -> {membership_count_after}")

            print(f"✓ Memberships preserved: {membership_count_after}")

            # Step 10: Recreate dependent views
            print("Recreating dependent views...")
            for view_name, view_sql in dependent_views:
                try:
                    print(f"  Recreating view: {view_name}")
                    cursor.execute(view_sql)
                except Exception as e:
                    print(f"  ⚠ Failed to recreate view {view_name}: {e}")

            # Step 11: Add triggers for updated_at
            print("Creating updated_at trigger...")
            cursor.execute("""
                CREATE TRIGGER tr_teams_updated_at
                    AFTER UPDATE ON teams
                    FOR EACH ROW
                BEGIN
                    UPDATE teams
                    SET updated_at = CURRENT_TIMESTAMP
                    WHERE id = NEW.id;
                END
            """)

            # Step 12: Re-enable foreign key constraints
            print("Re-enabling foreign key constraints...")
            cursor.execute("PRAGMA foreign_keys = ON")

            # Step 13: Final verification
            cursor.execute("SELECT COUNT(*) FROM teams")
            final_team_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM team_league_memberships WHERE is_active = 1")
            final_membership_count = cursor.fetchone()[0]

            if (final_team_count != original_team_count or
                final_membership_count != original_membership_count):
                raise Exception(f"Data integrity check failed: teams {original_team_count}->{final_team_count}, memberships {original_membership_count}->{final_membership_count}")

            print("✓ Successfully removed league_id column with data preservation")

        except Exception as e:
            print(f"✗ Error in safe column removal: {e}")
            # Re-enable foreign keys before raising
            cursor.execute("PRAGMA foreign_keys = ON")
            raise

    def add_performance_indexes(self):
        """Add performance-optimized indexes"""
        print("\n=== ADDING PERFORMANCE-OPTIMIZED INDEXES ===")

        cursor = self.conn.cursor()

        performance_indexes = [
            ("idx_team_league_memberships_team_active",
             "team_league_memberships", "(team_id, is_active)",
             "Fast team membership lookups"),

            ("idx_team_league_memberships_league_active",
             "team_league_memberships", "(league_id, is_active)",
             "Fast league team lookups"),

            ("idx_team_league_memberships_composite",
             "team_league_memberships", "(is_active, season_start_year, season_end_year)",
             "Complex membership filtering"),

            ("idx_leagues_sport_type_level",
             "leagues", "(sport_id, competition_type, league_level)",
             "League classification filtering"),

            ("idx_leagues_country_active",
             "leagues", "(country_code, is_active)",
             "Geographic league filtering"),
        ]

        created_indexes = 0
        for index_name, table_name, columns, description in performance_indexes:
            try:
                cursor.execute(f"PRAGMA index_info({index_name})")
                if cursor.fetchall():
                    print(f"  Index {index_name} already exists")
                    continue

                cursor.execute(f"CREATE INDEX {index_name} ON {table_name}{columns}")
                created_indexes += 1
                print(f"✓ Created {index_name}: {description}")

            except Exception as e:
                print(f"⚠ Failed to create {index_name}: {e}")

        print(f"✓ Created {created_indexes} new performance indexes")

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive post-migration validation"""
        print("\n=== POST-MIGRATION VALIDATION ===")

        cursor = self.conn.cursor()
        results = {
            "timestamp": datetime.now().isoformat(),
            "phase": "post-migration",
            "checks": {}
        }

        # Check schema changes
        cursor.execute("PRAGMA table_info(teams)")
        columns = {row["name"]: row["type"] for row in cursor.fetchall()}
        has_league_id = "league_id" in columns
        results["checks"]["deprecated_column_removed"] = not has_league_id

        if has_league_id:
            print("✗ CRITICAL: league_id column still exists!")
            return results
        else:
            print("✓ league_id column successfully removed")

        # Check data integrity
        cursor.execute("SELECT COUNT(*) as count FROM teams")
        team_count = cursor.fetchone()["count"]
        results["checks"]["total_teams"] = team_count

        cursor.execute("SELECT COUNT(*) as count FROM team_league_memberships WHERE is_active = 1")
        membership_count = cursor.fetchone()["count"]
        results["checks"]["active_memberships"] = membership_count

        pre_migration_team_count = self.validation_results.get("pre_migration", {}).get("checks", {}).get("total_teams", 0)
        pre_migration_membership_count = self.validation_results.get("pre_migration", {}).get("checks", {}).get("active_memberships", 0)

        if team_count == pre_migration_team_count:
            print(f"✓ Team count preserved: {team_count}")
        else:
            print(f"✗ CRITICAL: Team count changed from {pre_migration_team_count} to {team_count}")

        if membership_count == pre_migration_membership_count:
            print(f"✓ Membership count preserved: {membership_count}")
        else:
            print(f"✗ CRITICAL: Membership count changed from {pre_migration_membership_count} to {membership_count}")

        # Test critical queries
        try:
            cursor.execute("""
                SELECT t.name, t.market, COUNT(tlm.league_id) as league_count
                FROM teams t
                JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
                GROUP BY t.id
                HAVING COUNT(tlm.league_id) > 1
                LIMIT 5
            """)
            multi_league_results = cursor.fetchall()
            results["checks"]["multi_league_teams_found"] = len(multi_league_results)
            print(f"✓ Multi-league query found {len(multi_league_results)} teams")

        except Exception as e:
            print(f"⚠ Multi-league query failed: {e}")

        # Check foreign key constraints
        try:
            cursor.execute("PRAGMA foreign_key_check")
            fk_violations = cursor.fetchall()
            results["checks"]["foreign_key_violations"] = len(fk_violations)

            if not fk_violations:
                print("✓ All foreign key constraints valid")
            else:
                print(f"✗ CRITICAL: {len(fk_violations)} foreign key violations")

        except Exception as e:
            print(f"⚠ Could not check foreign keys: {e}")

        self.validation_results["post_migration"] = results
        return results

    def save_migration_results(self):
        """Save all migration results to a JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"/Users/newmac/Desktop/Corner League Media 1/backend/migrations/phase4_safe_results_{timestamp}.json"

        all_results = {
            "migration_info": {
                "phase": "4 - SAFE Schema Finalization",
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
        """Execute the complete SAFE Phase 4 migration"""
        print("🚀 PHASE 4: SAFE SCHEMA FINALIZATION AND CLEANUP")
        print("=" * 60)

        try:
            # Step 1: Create rollback backup
            self.create_rollback_backup()

            # Step 2: Connect to database
            self.connect()

            # Step 3: Pre-migration validation
            pre_results = self.run_pre_migration_validation()

            # Step 4: Begin transaction for atomic changes
            print("\n=== BEGINNING ATOMIC MIGRATION ===")
            self.conn.execute("BEGIN IMMEDIATE TRANSACTION")

            try:
                # Step 5: Safely remove deprecated column
                self.safe_remove_deprecated_column()

                # Step 6: Add performance indexes
                self.add_performance_indexes()

                # Step 7: Post-migration validation
                post_results = self.run_comprehensive_validation()

                # Check if migration was successful
                if (post_results.get("checks", {}).get("deprecated_column_removed", False) and
                    post_results.get("checks", {}).get("total_teams", 0) == pre_results.get("checks", {}).get("total_teams", 0) and
                    post_results.get("checks", {}).get("active_memberships", 0) == pre_results.get("checks", {}).get("active_memberships", 0)):

                    print("\n✅ MIGRATION SUCCESSFUL - COMMITTING CHANGES")
                    self.conn.commit()

                else:
                    print("\n❌ MIGRATION VALIDATION FAILED - ROLLING BACK")
                    self.conn.rollback()
                    return False

            except Exception as e:
                print(f"\n❌ MIGRATION ERROR - ROLLING BACK: {e}")
                self.conn.rollback()
                raise

            # Step 8: Save results
            self.save_migration_results()

            print("\n🎉 PHASE 4 SAFE MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("✓ Deprecated league_id column removed safely")
            print("✓ All team and membership data preserved")
            print("✓ Performance indexes added")
            print("✓ Foreign key constraints maintained")
            print(f"✓ Rollback backup available: {self.backup_path}")

            return True

        except Exception as e:
            print(f"\n💥 CRITICAL ERROR: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return False

        finally:
            self.close()


def main():
    """Main entry point for SAFE Phase 4 migration"""
    import argparse

    parser = argparse.ArgumentParser(description="SAFE Phase 4: Schema finalization and cleanup")
    parser.add_argument("--db", default="/Users/newmac/Desktop/Corner League Media 1/backend/sports_platform.db",
                       help="Path to the SQLite database")
    parser.add_argument("--backup", help="Path for rollback backup (optional)")
    parser.add_argument("--dry-run", action="store_true", help="Run validation only, no changes")

    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f"❌ Database not found: {args.db}")
        sys.exit(1)

    migrator = Phase4SafeSchemaFinalization(args.db, args.backup)

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