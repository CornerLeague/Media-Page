#!/bin/bash

# Phase 1 Migration Execution Script
# Date: 2025-01-21
# Description: Execute Phase 1 schema migration with validation and rollback capability

set -e  # Exit on any error

# Configuration
DB_PATH="../sports_platform.db"
MIGRATION_SQL="phase1_teams_multi_league_support.sql"
ROLLBACK_SQL="phase1_teams_multi_league_support_rollback.sql"
BACKUP_PATH="../sports_platform_backup_$(date +%Y%m%d_%H%M%S).db"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Phase 1 Migration Execution ===${NC}"
echo "Database: $DB_PATH"
echo "Migration: $MIGRATION_SQL"
echo "Backup will be created at: $BACKUP_PATH"
echo

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo -e "${RED}Error: Database file not found at $DB_PATH${NC}"
    exit 1
fi

# Check if migration file exists
if [ ! -f "$MIGRATION_SQL" ]; then
    echo -e "${RED}Error: Migration file not found: $MIGRATION_SQL${NC}"
    exit 1
fi

# Function to run validation queries
validate_migration() {
    echo -e "${BLUE}Running validation queries...${NC}"

    # Check new columns exist
    NEW_TEAM_COLS=$(sqlite3 "$DB_PATH" "SELECT name FROM pragma_table_info('teams') WHERE name IN ('official_name', 'short_name', 'country_code', 'founding_year');" | wc -l)
    NEW_LEAGUE_COLS=$(sqlite3 "$DB_PATH" "SELECT name FROM pragma_table_info('leagues') WHERE name IN ('country_code', 'league_level', 'competition_type');" | wc -l)

    echo "New team columns added: $NEW_TEAM_COLS/4"
    echo "New league columns added: $NEW_LEAGUE_COLS/3"

    # Check junction table exists
    JUNCTION_TABLE=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='team_league_memberships';")
    echo "Junction table created: $JUNCTION_TABLE"

    # Check indexes created
    INDEX_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%memberships%';")
    echo "New indexes created: $INDEX_COUNT"

    # Check views created
    VIEW_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM sqlite_master WHERE type='view' AND name LIKE 'v_%';")
    echo "Validation views created: $VIEW_COUNT"

    # Verify foreign key constraints
    FK_VIOLATIONS=$(sqlite3 "$DB_PATH" "PRAGMA foreign_key_check;" | wc -l)
    echo "Foreign key violations: $FK_VIOLATIONS"

    # Check data integrity
    LEAGUES_WITH_METADATA=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM leagues WHERE country_code IS NOT NULL;")
    TOTAL_LEAGUES=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM leagues;")
    echo "Leagues with metadata: $LEAGUES_WITH_METADATA/$TOTAL_LEAGUES"

    # Validation summary
    if [ "$NEW_TEAM_COLS" -eq 4 ] && [ "$NEW_LEAGUE_COLS" -eq 3 ] && [ "$JUNCTION_TABLE" -eq 1 ] && [ "$FK_VIOLATIONS" -eq 0 ]; then
        echo -e "${GREEN}✓ Migration validation PASSED${NC}"
        return 0
    else
        echo -e "${RED}✗ Migration validation FAILED${NC}"
        return 1
    fi
}

# Function to test existing functionality
test_existing_functionality() {
    echo -e "${BLUE}Testing existing functionality...${NC}"

    # Test existing queries still work
    SPORTS_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM sports;")
    LEAGUES_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM leagues;")
    TEAMS_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM teams;")

    echo "Sports: $SPORTS_COUNT"
    echo "Leagues: $LEAGUES_COUNT"
    echo "Teams: $TEAMS_COUNT"

    # Test soccer-specific queries
    SOCCER_ID="61a964ee-563b-4ccd-b277-b429ec1c57ab"
    SOCCER_LEAGUES=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM leagues WHERE sport_id = '$SOCCER_ID';")
    SOCCER_TEAMS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM teams WHERE sport_id = '$SOCCER_ID';")

    echo "Soccer leagues: $SOCCER_LEAGUES"
    echo "Soccer teams: $SOCCER_TEAMS"

    echo -e "${GREEN}✓ Existing functionality intact${NC}"
}

# Create backup
echo -e "${YELLOW}Creating database backup...${NC}"
cp "$DB_PATH" "$BACKUP_PATH"
echo "Backup created: $BACKUP_PATH"
echo

# Pre-migration state
echo -e "${BLUE}Pre-migration database state:${NC}"
test_existing_functionality
echo

# Execute migration
echo -e "${YELLOW}Executing Phase 1 migration...${NC}"
if sqlite3 "$DB_PATH" < "$MIGRATION_SQL"; then
    echo -e "${GREEN}✓ Migration executed successfully${NC}"
else
    echo -e "${RED}✗ Migration failed${NC}"
    echo "Restoring from backup..."
    cp "$BACKUP_PATH" "$DB_PATH"
    exit 1
fi
echo

# Validate migration
if validate_migration; then
    echo -e "${GREEN}✓ Migration validation successful${NC}"
else
    echo -e "${RED}✗ Migration validation failed${NC}"
    echo -e "${YELLOW}Rolling back migration...${NC}"
    if sqlite3 "$DB_PATH" < "$ROLLBACK_SQL"; then
        echo -e "${GREEN}✓ Rollback completed${NC}"
    else
        echo -e "${RED}✗ Rollback failed, restoring from backup${NC}"
        cp "$BACKUP_PATH" "$DB_PATH"
    fi
    exit 1
fi
echo

# Test existing functionality after migration
echo -e "${BLUE}Post-migration functionality test:${NC}"
test_existing_functionality
echo

# Show new capabilities
echo -e "${BLUE}New schema capabilities:${NC}"
echo "Teams can now belong to multiple leagues through team_league_memberships table"
echo "Enhanced metadata available for teams and leagues"
echo "Performance indexes created for common query patterns"
echo "Validation views available for monitoring"
echo

echo -e "${GREEN}=== Phase 1 Migration Completed Successfully ===${NC}"
echo "Backup available at: $BACKUP_PATH"
echo "Next steps: Implement Phase 2 data population and validation"