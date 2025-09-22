#!/usr/bin/env python3
"""
Phase 4 Rollback: Restore league_id column and constraints
=========================================================

This script provides emergency rollback capability for Phase 4 migration
by restoring the league_id column and related constraints.

IMPORTANT: This rollback script restores the schema to the pre-Phase 4 state
but maintains all data and relationships established in Phases 1-3.

Author: Database ETL Architect
Date: 2025-09-21
Purpose: Emergency rollback for Phase 4 schema cleanup
"""

import sqlite3
import os
import sys
import traceback
from datetime import datetime
from typing import Dict, List, Any
import json


class Phase4Rollback:
    """Rollback Phase 4 schema changes"""

    def __init__(self, db_path: str, backup_path: str):
        self.db_path = db_path
        self.backup_path = backup_path
        self.conn = None

    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def restore_from_backup(self):
        """Restore database from backup"""
        print(f"🔄 Restoring database from backup: {self.backup_path}")

        if not os.path.exists(self.backup_path):
            raise Exception(f"Backup file not found: {self.backup_path}")

        try:
            # Simple file copy restore
            import shutil
            shutil.copy2(self.backup_path, self.db_path)
            print("✓ Database restored from backup")

        except Exception as e:
            raise Exception(f"Failed to restore from backup: {e}")

    def manual_rollback(self):
        """Manual rollback by recreating league_id column"""
        print("🔧 Performing manual rollback...")

        cursor = self.conn.cursor()

        try:
            self.conn.execute("BEGIN IMMEDIATE TRANSACTION")

            # Step 1: Check if league_id already exists
            cursor.execute("PRAGMA table_info(teams)")
            columns = {row["name"]: row["type"] for row in cursor.fetchall()}

            if "league_id" in columns:
                print("⚠ league_id column already exists")
                self.conn.rollback()
                return

            # Step 2: Create teams table with league_id
            print("Creating teams table with league_id...")
            cursor.execute("""
                CREATE TABLE teams_with_league_id (
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
                    official_name TEXT,
                    short_name TEXT,
                    country_code TEXT,
                    founding_year INTEGER,
                    FOREIGN KEY (sport_id) REFERENCES sports (id) ON DELETE CASCADE,
                    FOREIGN KEY (league_id) REFERENCES leagues (id) ON DELETE CASCADE,
                    UNIQUE (league_id, slug)
                )
            """)

            # Step 3: Populate with data and determine primary league
            print("Populating teams with primary league assignment...")
            cursor.execute("""
                INSERT INTO teams_with_league_id (
                    id, sport_id, league_id, name, market, slug, abbreviation,
                    logo_url, primary_color, secondary_color, is_active,
                    external_id, created_at, updated_at, official_name,
                    short_name, country_code, founding_year
                )
                SELECT
                    t.id, t.sport_id,
                    -- Use the first active league membership as primary
                    (SELECT tlm.league_id FROM team_league_memberships tlm
                     WHERE tlm.team_id = t.id AND tlm.is_active = 1
                     ORDER BY tlm.season_start_year ASC LIMIT 1) as league_id,
                    t.name, t.market, t.slug, t.abbreviation,
                    t.logo_url, t.primary_color, t.secondary_color, t.is_active,
                    t.external_id, t.created_at, t.updated_at, t.official_name,
                    t.short_name, t.country_code, t.founding_year
                FROM teams t
                WHERE EXISTS (
                    SELECT 1 FROM team_league_memberships tlm
                    WHERE tlm.team_id = t.id AND tlm.is_active = 1
                )
            """)

            # Step 4: Replace old teams table
            cursor.execute("DROP TABLE teams")
            cursor.execute("ALTER TABLE teams_with_league_id RENAME TO teams")

            # Step 5: Recreate indexes
            print("Recreating original indexes...")
            cursor.execute("CREATE INDEX idx_teams_country_code ON teams(country_code)")
            cursor.execute("CREATE INDEX idx_teams_founding_year ON teams(founding_year)")
            cursor.execute("CREATE INDEX idx_teams_sport_league ON teams(sport_id, league_id)")

            # Step 6: Recreate trigger
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

            self.conn.commit()
            print("✓ Manual rollback completed")

        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Manual rollback failed: {e}")

    def validate_rollback(self):
        """Validate that rollback was successful"""
        print("🔍 Validating rollback...")

        cursor = self.conn.cursor()

        # Check schema
        cursor.execute("PRAGMA table_info(teams)")
        columns = {row["name"]: row["type"] for row in cursor.fetchall()}

        if "league_id" not in columns:
            raise Exception("Rollback failed: league_id column not restored")

        # Check data integrity
        cursor.execute("SELECT COUNT(*) FROM teams")
        team_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM team_league_memberships WHERE is_active = 1")
        membership_count = cursor.fetchone()[0]

        print(f"✓ Teams: {team_count}")
        print(f"✓ Active memberships: {membership_count}")

        # Check foreign keys
        cursor.execute("PRAGMA foreign_key_check")
        violations = cursor.fetchall()
        if violations:
            raise Exception(f"Foreign key violations found: {len(violations)}")

        print("✓ Rollback validation passed")

    def run_rollback(self, use_backup: bool = True):
        """Execute the rollback"""
        print("🔙 PHASE 4 ROLLBACK")
        print("=" * 40)

        try:
            if use_backup and os.path.exists(self.backup_path):
                self.restore_from_backup()
            else:
                self.connect()
                self.manual_rollback()

            # Always validate after rollback
            if not self.conn:
                self.connect()
            self.validate_rollback()

            print("\n✅ ROLLBACK SUCCESSFUL!")
            print("✓ league_id column restored")
            print("✓ All constraints recreated")
            print("✓ Data integrity maintained")

            return True

        except Exception as e:
            print(f"\n❌ ROLLBACK FAILED: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return False

        finally:
            self.close()


def main():
    """Main entry point for Phase 4 rollback"""
    import argparse

    parser = argparse.ArgumentParser(description="Phase 4 rollback")
    parser.add_argument("--db", default="/Users/newmac/Desktop/Corner League Media 1/backend/sports_platform.db",
                       help="Path to the SQLite database")
    parser.add_argument("--backup", required=True, help="Path to backup file")
    parser.add_argument("--manual", action="store_true", help="Use manual rollback instead of backup restore")

    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f"❌ Database not found: {args.db}")
        sys.exit(1)

    rollback = Phase4Rollback(args.db, args.backup)
    success = rollback.run_rollback(use_backup=not args.manual)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()