-- Phase 1 Migration Validation Queries
-- Date: 2025-01-21
-- Description: Comprehensive validation queries to confirm Phase 1 implementation

-- ============================================================================
-- 1. SCHEMA VALIDATION
-- ============================================================================

-- Check all new columns exist in teams table
SELECT
    'Teams Table New Columns' as validation_name,
    COUNT(*) as columns_added,
    GROUP_CONCAT(name, ', ') as column_names
FROM pragma_table_info('teams')
WHERE name IN ('official_name', 'short_name', 'country_code', 'founding_year');

-- Check all new columns exist in leagues table
SELECT
    'Leagues Table New Columns' as validation_name,
    COUNT(*) as columns_added,
    GROUP_CONCAT(name, ', ') as column_names
FROM pragma_table_info('leagues')
WHERE name IN ('country_code', 'league_level', 'competition_type');

-- Verify junction table exists with correct structure
SELECT
    'Junction Table Structure' as validation_name,
    COUNT(*) as column_count,
    GROUP_CONCAT(name, ', ') as columns
FROM pragma_table_info('team_league_memberships');

-- ============================================================================
-- 2. INDEX VALIDATION
-- ============================================================================

-- Check all new indexes were created
SELECT
    'New Indexes Created' as validation_name,
    COUNT(*) as index_count,
    GROUP_CONCAT(name, ', ') as index_names
FROM sqlite_master
WHERE type='index'
AND name LIKE 'idx_%'
AND name NOT IN (
    -- Exclude any existing indexes that might have been there before
    SELECT name FROM sqlite_master WHERE type='index' AND sql IS NULL
);

-- Check specific junction table indexes
SELECT
    'Junction Table Indexes' as validation_name,
    COUNT(*) as index_count,
    GROUP_CONCAT(name, ', ') as index_names
FROM sqlite_master
WHERE type='index'
AND name LIKE 'idx_%memberships%';

-- ============================================================================
-- 3. CONSTRAINT VALIDATION
-- ============================================================================

-- Verify foreign key constraints are working
PRAGMA foreign_key_check;

-- Check unique constraints on junction table
SELECT
    'Junction Table Constraints' as validation_name,
    sql
FROM sqlite_master
WHERE type='table'
AND name='team_league_memberships';

-- ============================================================================
-- 4. DATA INTEGRITY VALIDATION
-- ============================================================================

-- Check that enhanced metadata was populated for existing leagues
SELECT
    'Leagues with Enhanced Metadata' as validation_name,
    COUNT(*) as leagues_with_metadata,
    (SELECT COUNT(*) FROM leagues) as total_leagues,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM leagues), 2) || '%' as percentage
FROM leagues
WHERE country_code IS NOT NULL;

-- Verify soccer leagues have correct metadata
SELECT
    'Soccer League Metadata' as validation_name,
    l.name,
    l.country_code,
    l.league_level,
    l.competition_type
FROM leagues l
JOIN sports s ON l.sport_id = s.id
WHERE s.name = 'Soccer';

-- ============================================================================
-- 5. VIEW VALIDATION
-- ============================================================================

-- Check all validation views were created
SELECT
    'Validation Views Created' as validation_name,
    COUNT(*) as view_count,
    GROUP_CONCAT(name, ', ') as view_names
FROM sqlite_master
WHERE type='view'
AND name LIKE 'v_%';

-- Test league team counts view
SELECT
    'League Team Counts View Test' as validation_name,
    league_name,
    country_code,
    league_level,
    active_teams,
    current_teams
FROM v_league_team_counts
WHERE league_name IN ('Premier League', 'Major League Soccer');

-- Test multi-league check view (should be empty since no teams in multiple leagues yet)
SELECT
    'Multi-League Check View Test' as validation_name,
    COUNT(*) as teams_in_multiple_leagues
FROM v_team_multi_league_check
WHERE league_count > 1;

-- ============================================================================
-- 6. BACKWARD COMPATIBILITY VALIDATION
-- ============================================================================

-- Test that existing queries still work
SELECT
    'Backward Compatibility - Sport League Count' as validation_name,
    s.name as sport,
    COUNT(l.id) as league_count
FROM sports s
LEFT JOIN leagues l ON s.id = l.sport_id
GROUP BY s.id, s.name
ORDER BY s.name;

-- Test existing team queries work
SELECT
    'Backward Compatibility - Team Count by Sport' as validation_name,
    s.name as sport,
    COUNT(t.id) as team_count
FROM sports s
LEFT JOIN teams t ON s.id = t.sport_id
GROUP BY s.id, s.name
ORDER BY s.name;

-- Verify existing team-league relationships are intact
SELECT
    'Backward Compatibility - Team-League Relationships' as validation_name,
    l.name as league,
    COUNT(t.id) as team_count
FROM leagues l
LEFT JOIN teams t ON l.id = t.league_id
WHERE l.sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'  -- Soccer
GROUP BY l.id, l.name;

-- ============================================================================
-- 7. PERFORMANCE VALIDATION
-- ============================================================================

-- Check query plans for common queries use indexes
EXPLAIN QUERY PLAN
SELECT * FROM team_league_memberships WHERE team_id = 'test-id';

EXPLAIN QUERY PLAN
SELECT * FROM team_league_memberships WHERE league_id = 'test-id';

EXPLAIN QUERY PLAN
SELECT * FROM team_league_memberships WHERE is_active = 1;

-- ============================================================================
-- 8. TRIGGER VALIDATION
-- ============================================================================

-- Check that triggers were created
SELECT
    'Triggers Created' as validation_name,
    COUNT(*) as trigger_count,
    GROUP_CONCAT(name, ', ') as trigger_names
FROM sqlite_master
WHERE type='trigger'
AND name LIKE 'tr_%';

-- ============================================================================
-- 9. OVERALL MIGRATION SUCCESS SUMMARY
-- ============================================================================

-- Summary validation query
SELECT
    'Phase 1 Migration Summary' as summary,
    (SELECT COUNT(*) FROM pragma_table_info('teams') WHERE name IN ('official_name', 'short_name', 'country_code', 'founding_year')) as team_columns_added,
    (SELECT COUNT(*) FROM pragma_table_info('leagues') WHERE name IN ('country_code', 'league_level', 'competition_type')) as league_columns_added,
    (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='team_league_memberships') as junction_table_created,
    (SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%memberships%') as junction_indexes_created,
    (SELECT COUNT(*) FROM sqlite_master WHERE type='view' AND name LIKE 'v_%') as validation_views_created,
    (SELECT COUNT(*) FROM sqlite_master WHERE type='trigger' AND name LIKE 'tr_%') as triggers_created,
    (SELECT COUNT(*) FROM leagues WHERE country_code IS NOT NULL) as leagues_with_metadata;

-- Check for any foreign key violations
SELECT
    'Foreign Key Violations' as check_name,
    COUNT(*) as violation_count
FROM (
    SELECT * FROM pragma_foreign_key_check() LIMIT 1
);