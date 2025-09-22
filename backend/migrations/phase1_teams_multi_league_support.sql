-- Phase 1: Non-Breaking Schema Enhancement for Multi-League Team Support
-- Date: 2025-01-21
-- Description: Add support for teams in multiple leagues with enhanced metadata
-- Breaking Change: NO - All existing functionality preserved

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Begin transaction for atomic migration
BEGIN TRANSACTION;

-- ============================================================================
-- 1. ADD ENHANCED METADATA COLUMNS TO EXISTING TABLES
-- ============================================================================

-- Add enhanced metadata columns to teams table
ALTER TABLE teams ADD COLUMN official_name TEXT;
ALTER TABLE teams ADD COLUMN short_name TEXT;
ALTER TABLE teams ADD COLUMN country_code TEXT;
ALTER TABLE teams ADD COLUMN founding_year INTEGER;

-- Add enhanced metadata columns to leagues table
ALTER TABLE leagues ADD COLUMN country_code TEXT;
ALTER TABLE leagues ADD COLUMN league_level INTEGER DEFAULT 1;
ALTER TABLE leagues ADD COLUMN competition_type TEXT DEFAULT 'league';

-- ============================================================================
-- 2. CREATE TEAM_LEAGUE_MEMBERSHIPS JUNCTION TABLE
-- ============================================================================

CREATE TABLE team_league_memberships (
    id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL,
    league_id TEXT NOT NULL,
    season_start_year INTEGER NOT NULL,
    season_end_year INTEGER, -- NULL for ongoing memberships
    is_active BOOLEAN NOT NULL DEFAULT 1,
    position_last_season INTEGER, -- Final league position if applicable
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraints
    FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE,
    FOREIGN KEY (league_id) REFERENCES leagues (id) ON DELETE CASCADE,

    -- Unique constraint to prevent duplicate active memberships
    UNIQUE (team_id, league_id, season_start_year),

    -- Check constraints for data integrity
    CHECK (season_end_year IS NULL OR season_end_year >= season_start_year),
    CHECK (season_start_year > 1800 AND season_start_year <= 2100),
    CHECK (season_end_year IS NULL OR (season_end_year > 1800 AND season_end_year <= 2100)),
    CHECK (position_last_season IS NULL OR position_last_season > 0)
);

-- ============================================================================
-- 3. CREATE PERFORMANCE INDEXES
-- ============================================================================

-- Index for team-league membership lookups
CREATE INDEX idx_team_league_memberships_team_id ON team_league_memberships(team_id);
CREATE INDEX idx_team_league_memberships_league_id ON team_league_memberships(league_id);
CREATE INDEX idx_team_league_memberships_active ON team_league_memberships(is_active);
CREATE INDEX idx_team_league_memberships_season ON team_league_memberships(season_start_year, season_end_year);

-- Composite index for active team-league relationships
CREATE INDEX idx_team_league_active_membership ON team_league_memberships(team_id, league_id, is_active);

-- Enhanced indexes for existing tables
CREATE INDEX idx_teams_country_code ON teams(country_code);
CREATE INDEX idx_teams_founding_year ON teams(founding_year);
CREATE INDEX idx_leagues_country_code ON leagues(country_code);
CREATE INDEX idx_leagues_level_type ON leagues(league_level, competition_type);

-- Sport-league-team query optimization
CREATE INDEX idx_teams_sport_league ON teams(sport_id, league_id);

-- ============================================================================
-- 4. UPDATE EXISTING DATA WITH ENHANCED METADATA
-- ============================================================================

-- Update existing soccer leagues with enhanced metadata
UPDATE leagues
SET
    country_code = 'GB',
    league_level = 1,
    competition_type = 'league'
WHERE id = '7cde8b74-858c-43d6-b91a-15ebe7a741bf'; -- Premier League

UPDATE leagues
SET
    country_code = 'US',
    league_level = 1,
    competition_type = 'league'
WHERE id = '896d4884-3e77-4357-aae3-98d3b614e26c'; -- Major League Soccer

-- ============================================================================
-- 5. CREATE VALIDATION VIEWS FOR TESTING
-- ============================================================================

-- View to check team multi-league memberships
CREATE VIEW v_team_multi_league_check AS
SELECT
    t.id as team_id,
    t.name as team_name,
    COUNT(tlm.league_id) as league_count,
    GROUP_CONCAT(l.name, ', ') as leagues
FROM teams t
LEFT JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
LEFT JOIN leagues l ON tlm.league_id = l.id
GROUP BY t.id, t.name;

-- View to check league team counts
CREATE VIEW v_league_team_counts AS
SELECT
    l.id as league_id,
    l.name as league_name,
    l.country_code,
    l.league_level,
    COUNT(DISTINCT tlm.team_id) as active_teams,
    COUNT(DISTINCT CASE WHEN tlm.season_end_year IS NULL THEN tlm.team_id END) as current_teams
FROM leagues l
LEFT JOIN team_league_memberships tlm ON l.id = tlm.league_id AND tlm.is_active = 1
GROUP BY l.id, l.name, l.country_code, l.league_level;

-- ============================================================================
-- 6. CREATE HELPER FUNCTIONS (AS VIEWS FOR SQLITE)
-- ============================================================================

-- View to get current team leagues
CREATE VIEW v_current_team_leagues AS
SELECT
    t.id as team_id,
    t.name as team_name,
    l.id as league_id,
    l.name as league_name,
    tlm.season_start_year,
    tlm.position_last_season
FROM teams t
JOIN team_league_memberships tlm ON t.id = tlm.team_id
JOIN leagues l ON tlm.league_id = l.id
WHERE tlm.is_active = 1 AND tlm.season_end_year IS NULL;

-- ============================================================================
-- 7. CREATE TRIGGER FOR AUTOMATIC UPDATED_AT
-- ============================================================================

-- Trigger to update updated_at on team_league_memberships changes
CREATE TRIGGER tr_team_league_memberships_updated_at
    AFTER UPDATE ON team_league_memberships
    FOR EACH ROW
BEGIN
    UPDATE team_league_memberships
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- Commit the transaction
COMMIT;

-- ============================================================================
-- MIGRATION VALIDATION QUERIES
-- ============================================================================

-- These queries should be run after migration to validate success

-- Check that all new columns exist
SELECT name FROM pragma_table_info('teams') WHERE name IN ('official_name', 'short_name', 'country_code', 'founding_year');
SELECT name FROM pragma_table_info('leagues') WHERE name IN ('country_code', 'league_level', 'competition_type');

-- Check that new table exists with correct structure
SELECT name FROM sqlite_master WHERE type='table' AND name='team_league_memberships';

-- Check that indexes were created
SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%memberships%';

-- Verify foreign key constraints work
PRAGMA foreign_key_check;

-- Check that views were created
SELECT name FROM sqlite_master WHERE type='view' AND name LIKE 'v_%';

-- Verify data integrity
SELECT 'All leagues have metadata' as check_name, COUNT(*) as pass_count FROM leagues WHERE country_code IS NOT NULL;