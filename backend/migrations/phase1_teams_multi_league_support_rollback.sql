-- Phase 1 Rollback: Remove Multi-League Team Support Schema Enhancements
-- Date: 2025-01-21
-- Description: Rollback all Phase 1 changes to original schema state
-- WARNING: This will remove all team-league membership data!

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Begin transaction for atomic rollback
BEGIN TRANSACTION;

-- ============================================================================
-- 1. DROP VIEWS FIRST (DEPEND ON TABLES)
-- ============================================================================

DROP VIEW IF EXISTS v_team_multi_league_check;
DROP VIEW IF EXISTS v_league_team_counts;
DROP VIEW IF EXISTS v_current_team_leagues;

-- ============================================================================
-- 2. DROP TRIGGERS
-- ============================================================================

DROP TRIGGER IF EXISTS tr_team_league_memberships_updated_at;

-- ============================================================================
-- 3. DROP INDEXES CREATED IN PHASE 1
-- ============================================================================

-- Drop new table indexes
DROP INDEX IF EXISTS idx_team_league_memberships_team_id;
DROP INDEX IF EXISTS idx_team_league_memberships_league_id;
DROP INDEX IF EXISTS idx_team_league_memberships_active;
DROP INDEX IF EXISTS idx_team_league_memberships_season;
DROP INDEX IF EXISTS idx_team_league_active_membership;

-- Drop enhanced indexes on existing tables
DROP INDEX IF EXISTS idx_teams_country_code;
DROP INDEX IF EXISTS idx_teams_founding_year;
DROP INDEX IF EXISTS idx_leagues_country_code;
DROP INDEX IF EXISTS idx_leagues_level_type;
DROP INDEX IF EXISTS idx_teams_sport_league;

-- ============================================================================
-- 4. DROP JUNCTION TABLE
-- ============================================================================

DROP TABLE IF EXISTS team_league_memberships;

-- ============================================================================
-- 5. REMOVE ENHANCED METADATA COLUMNS
-- ============================================================================

-- Note: SQLite doesn't support DROP COLUMN directly
-- We need to recreate tables without the new columns

-- Backup existing data
CREATE TEMP TABLE teams_backup AS
SELECT
    id, sport_id, league_id, name, market, slug, abbreviation,
    logo_url, primary_color, secondary_color, is_active,
    external_id, created_at, updated_at
FROM teams;

CREATE TEMP TABLE leagues_backup AS
SELECT
    id, sport_id, name, slug, abbreviation, is_active,
    season_start_month, season_end_month, created_at, updated_at
FROM leagues;

-- Drop and recreate teams table
DROP TABLE teams;
CREATE TABLE teams (
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
);

-- Drop and recreate leagues table
DROP TABLE leagues;
CREATE TABLE leagues (
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
);

-- Restore data from backup
INSERT INTO teams SELECT * FROM teams_backup;
INSERT INTO leagues SELECT * FROM leagues_backup;

-- Drop temp tables
DROP TABLE teams_backup;
DROP TABLE leagues_backup;

-- Commit the rollback transaction
COMMIT;

-- ============================================================================
-- ROLLBACK VALIDATION QUERIES
-- ============================================================================

-- Verify rollback success
SELECT 'teams table restored' as status, COUNT(*) as record_count FROM teams;
SELECT 'leagues table restored' as status, COUNT(*) as record_count FROM leagues;

-- Verify no new columns exist
SELECT COUNT(*) as should_be_zero FROM pragma_table_info('teams') WHERE name IN ('official_name', 'short_name', 'country_code', 'founding_year');
SELECT COUNT(*) as should_be_zero FROM pragma_table_info('leagues') WHERE name IN ('country_code', 'league_level', 'competition_type');

-- Verify junction table is gone
SELECT COUNT(*) as should_be_zero FROM sqlite_master WHERE type='table' AND name='team_league_memberships';

-- Verify views are gone
SELECT COUNT(*) as should_be_zero FROM sqlite_master WHERE type='view' AND name LIKE 'v_%';