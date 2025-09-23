-- Phase 2 Soccer Teams Migration - Verification Queries
-- ===================================================

-- 1. Overview: Total counts across soccer entities
SELECT
    'Soccer Sport' as entity,
    COUNT(*) as count
FROM sports
WHERE id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'

UNION ALL

SELECT
    'Soccer Leagues' as entity,
    COUNT(*) as count
FROM leagues
WHERE sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'

UNION ALL

SELECT
    'Soccer Teams' as entity,
    COUNT(*) as count
FROM teams
WHERE sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'

UNION ALL

SELECT
    'Soccer Team-League Memberships' as entity,
    COUNT(*) as count
FROM team_league_memberships tlm
JOIN teams t ON tlm.team_id = t.id
WHERE t.sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab';

-- 2. League Details: All soccer leagues with metadata
SELECT
    l.name as league_name,
    l.country_code,
    l.league_level,
    l.competition_type,
    l.is_active,
    COUNT(tlm.team_id) as active_teams
FROM leagues l
LEFT JOIN team_league_memberships tlm ON l.id = tlm.league_id AND tlm.is_active = 1
WHERE l.sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'
GROUP BY l.id, l.name, l.country_code, l.league_level, l.competition_type, l.is_active
ORDER BY l.name;

-- 3. Teams in Multiple Leagues: Key validation for international competitions
SELECT
    t.short_name,
    t.official_name,
    t.country_code,
    COUNT(tlm.league_id) as league_count,
    GROUP_CONCAT(l.name, ' | ') as leagues
FROM teams t
JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
JOIN leagues l ON tlm.league_id = l.id
WHERE t.sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'
GROUP BY t.id, t.short_name, t.official_name, t.country_code
HAVING league_count > 1
ORDER BY league_count DESC, t.short_name;

-- 4. Sample Teams by League: Verify proper distribution
SELECT
    l.name as league_name,
    t.short_name as team_short_name,
    t.official_name as team_official_name,
    t.country_code as team_country,
    tlm.season_start_year
FROM leagues l
JOIN team_league_memberships tlm ON l.id = tlm.league_id AND tlm.is_active = 1
JOIN teams t ON tlm.team_id = t.id
WHERE l.sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'
ORDER BY l.name, t.short_name
LIMIT 50;

-- 5. Country Distribution: Teams by country code
SELECT
    t.country_code,
    COUNT(*) as team_count,
    GROUP_CONCAT(DISTINCT l.name, ' | ') as leagues_represented
FROM teams t
JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
JOIN leagues l ON tlm.league_id = l.id
WHERE t.sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'
GROUP BY t.country_code
ORDER BY team_count DESC;

-- 6. Data Quality Check: Teams with missing or invalid data
SELECT
    'Teams with missing short_name' as check_type,
    COUNT(*) as count
FROM teams
WHERE sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'
AND (short_name IS NULL OR short_name = '')

UNION ALL

SELECT
    'Teams with missing official_name' as check_type,
    COUNT(*) as count
FROM teams
WHERE sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'
AND (official_name IS NULL OR official_name = '')

UNION ALL

SELECT
    'Teams with missing country_code' as check_type,
    COUNT(*) as count
FROM teams
WHERE sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'
AND (country_code IS NULL OR country_code = '')

UNION ALL

SELECT
    'Inactive team memberships' as check_type,
    COUNT(*) as count
FROM team_league_memberships tlm
JOIN teams t ON tlm.team_id = t.id
WHERE t.sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'
AND tlm.is_active = 0;

-- 7. Premier League Teams: Detailed verification
SELECT
    'Premier League Verification' as section,
    t.short_name,
    t.official_name,
    t.country_code,
    t.slug
FROM teams t
JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
JOIN leagues l ON tlm.league_id = l.id
WHERE l.name = 'Premier League' AND l.sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'
ORDER BY t.short_name;

-- 8. UEFA Champions League Teams: International competition verification
SELECT
    'UEFA Champions League Verification' as section,
    t.short_name,
    t.country_code,
    COUNT(tlm2.league_id) as total_leagues
FROM teams t
JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
JOIN leagues l ON tlm.league_id = l.id
LEFT JOIN team_league_memberships tlm2 ON t.id = tlm2.team_id AND tlm2.is_active = 1
WHERE l.name = 'UEFA Champions League' AND l.sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'
GROUP BY t.id, t.short_name, t.country_code
ORDER BY total_leagues DESC, t.short_name;

-- 9. Schema Validation: Verify foreign key integrity
SELECT
    'Teams without valid sport reference' as integrity_check,
    COUNT(*) as violations
FROM teams t
LEFT JOIN sports s ON t.sport_id = s.id
WHERE t.sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'
AND s.id IS NULL

UNION ALL

SELECT
    'Memberships without valid team reference' as integrity_check,
    COUNT(*) as violations
FROM team_league_memberships tlm
LEFT JOIN teams t ON tlm.team_id = t.id
WHERE t.sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'
AND t.id IS NULL

UNION ALL

SELECT
    'Memberships without valid league reference' as integrity_check,
    COUNT(*) as violations
FROM team_league_memberships tlm
JOIN teams t ON tlm.team_id = t.id
LEFT JOIN leagues l ON tlm.league_id = l.id
WHERE t.sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'
AND l.id IS NULL;

-- 10. Final Summary: Migration success metrics
SELECT
    'PHASE 2 MIGRATION SUMMARY' as summary,
    'Expected: 6 leagues, 125 unique teams, 142 memberships, 17 multi-league teams' as expected_results,
    CAST(
        (SELECT COUNT(*) FROM leagues WHERE sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab') || ' leagues, ' ||
        (SELECT COUNT(*) FROM teams WHERE sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab') || ' unique teams, ' ||
        (SELECT COUNT(*) FROM team_league_memberships tlm JOIN teams t ON tlm.team_id = t.id WHERE t.sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab') || ' memberships, ' ||
        (SELECT COUNT(*) FROM (
            SELECT t.id FROM teams t
            JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = 1
            WHERE t.sport_id = '61a964ee-563b-4ccd-b277-b429ec1c57ab'
            GROUP BY t.id HAVING COUNT(tlm.league_id) > 1
        )) || ' multi-league teams'
    AS TEXT) as actual_results;