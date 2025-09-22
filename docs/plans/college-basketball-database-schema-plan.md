# College Basketball Database Schema Design Plan

## Overview

This document outlines a comprehensive plan for structuring a PostgreSQL/Supabase database to handle college basketball teams and conferences. The design builds upon the existing sports platform architecture while optimizing for the unique characteristics of college basketball data.

## Current State Analysis

### Existing Architecture
The platform currently has a multi-league sports architecture with:
- **Sports Table**: Top-level sport categorization (College Basketball already exists)
- **Leagues Table**: Conference-level organization (10 college basketball conferences exist)
- **Teams Table**: Individual team records with market/name structure
- **TeamLeagueMembership**: Junction table for team-conference relationships

### College Basketball Data Requirements
Based on `teams/college_basketball_teams.md`, we need to support:
- **10 Major Conferences**: SEC, Big Ten, Big 12, ACC, MWC, WCC, CUSA, MAC, AAC, Sun Belt
- **167 Teams** total across all conferences
- **Hierarchical Structure**: Sport → Conference → Division/Region → Teams
- **Conference Realignment**: Teams changing conferences over time

## Database Schema Design

### 1. Core Entity Relationships

```
Sport (College Basketball)
  └── Conference (League)
      ├── Division/Region (Optional sub-grouping)
      └── Teams
          ├── Historical Conference Memberships
          ├── Season Records
          ├── Tournament Appearances
          └── Rankings/Ratings
```

### 2. Enhanced Table Structures

#### A. Sports Table (Existing - No Changes Needed)
```sql
-- Already exists and properly configured
-- sport_id for 'college-basketball' already seeded
```

#### B. Enhanced Leagues Table (Conference Structure)
```sql
-- Existing table with college basketball conferences
-- Additional fields needed for college-specific metadata:

ALTER TABLE leagues ADD COLUMN IF NOT EXISTS:
  - tournament_autobid BOOLEAN DEFAULT true  -- Automatic tournament bid
  - power_conference BOOLEAN DEFAULT false   -- Power 5/6 designation
  - founding_year INTEGER                    -- Conference founding year
  - headquarters_city VARCHAR(100)           -- Conference HQ location
  - commissioner_name VARCHAR(100)           -- Current commissioner
  - conference_website VARCHAR(255)          -- Official website
  - media_rights_partner VARCHAR(100)       -- TV/streaming partner
```

#### C. Conference Divisions Table (New)
```sql
CREATE TABLE conference_divisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conference_id UUID NOT NULL REFERENCES leagues(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,              -- "East", "West", "Atlantic", etc.
    slug VARCHAR(100) NOT NULL,              -- URL-friendly identifier
    abbreviation VARCHAR(10),                -- Short form
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(conference_id, slug),
    UNIQUE(conference_id, name)
);
```

#### D. Enhanced Teams Table
```sql
-- Existing table enhanced with college-specific fields:

ALTER TABLE teams ADD COLUMN IF NOT EXISTS:
  - school_name VARCHAR(150)                -- "University of Alabama"
  - mascot VARCHAR(50)                      -- "Crimson Tide"
  - arena_name VARCHAR(150)                 -- Home venue
  - arena_capacity INTEGER                  -- Seating capacity
  - enrollment INTEGER                      -- Student enrollment
  - academic_conference VARCHAR(100)        -- Academic affiliation
  - athletic_director VARCHAR(100)          -- Current AD
  - head_coach VARCHAR(100)                 -- Current head coach
  - conference_titles INTEGER DEFAULT 0     -- Conference championships
  - ncaa_appearances INTEGER DEFAULT 0      -- Tournament appearances
  - final_four_appearances INTEGER DEFAULT 0
  - national_championships INTEGER DEFAULT 0
  - school_colors VARCHAR(100)              -- "Crimson and White"
  - nickname VARCHAR(50)                    -- Alternative team name
```

#### E. Enhanced TeamLeagueMembership Table
```sql
-- Existing table enhanced for conference realignment tracking:

ALTER TABLE team_league_memberships ADD COLUMN IF NOT EXISTS:
  - division_id UUID REFERENCES conference_divisions(id)
  - membership_type VARCHAR(20) DEFAULT 'full'  -- full, associate, transitional
  - exit_reason VARCHAR(100)                    -- Why team left conference
  - entry_date DATE                             -- Specific join date
  - exit_date DATE                              -- Specific exit date
  - conference_record VARCHAR(20)              -- Best season record in conference
  - tournament_wins INTEGER DEFAULT 0          -- Conference tournament wins
```

### 3. Additional Tables for College Basketball

#### A. NCAA Tournament History
```sql
CREATE TABLE ncaa_tournament_appearances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    seed INTEGER,                           -- Tournament seed (1-16)
    region VARCHAR(20),                     -- "East", "West", "South", "Midwest"
    rounds_advanced INTEGER DEFAULT 0,      -- How far they went
    final_ranking INTEGER,                  -- Final AP/Coaches poll ranking
    conference_id UUID REFERENCES leagues(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(team_id, year),
    CHECK(seed BETWEEN 1 AND 16),
    CHECK(rounds_advanced BETWEEN 0 AND 6)
);
```

#### B. Season Records
```sql
CREATE TABLE team_season_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    season_year INTEGER NOT NULL,           -- 2024 for 2023-24 season
    conference_id UUID REFERENCES leagues(id),
    overall_wins INTEGER DEFAULT 0,
    overall_losses INTEGER DEFAULT 0,
    conference_wins INTEGER DEFAULT 0,
    conference_losses INTEGER DEFAULT 0,
    conference_rank INTEGER,                -- Final conference standing
    postseason_result VARCHAR(50),         -- "NCAA First Round", "NIT", etc.
    head_coach VARCHAR(100),                -- Coach that season
    final_ap_ranking INTEGER,               -- Final AP poll ranking
    kenpom_rating DECIMAL(5,2),            -- KenPom efficiency rating
    net_ranking INTEGER,                    -- NCAA NET ranking
    strength_of_schedule DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(team_id, season_year)
);
```

#### C. Conference Tournament Results
```sql
CREATE TABLE conference_tournament_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conference_id UUID NOT NULL REFERENCES leagues(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    champion_team_id UUID REFERENCES teams(id),
    runner_up_team_id UUID REFERENCES teams(id),
    tournament_mvp VARCHAR(100),
    venue_name VARCHAR(150),
    venue_city VARCHAR(100),
    automatic_bid_received BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(conference_id, year)
);
```

## Data Types and Constraints

### Primary Data Types
- **UUIDs**: All primary keys for scalability and distributed systems
- **VARCHAR with appropriate lengths**: Optimized for typical content lengths
- **INTEGER**: Numeric values (years, counts, rankings)
- **DECIMAL(5,2)**: Ratings and percentages requiring precision
- **BOOLEAN**: Binary flags and status indicators
- **TIMESTAMP WITH TIME ZONE**: All temporal data for global consistency

### Key Constraints
1. **Referential Integrity**: All foreign keys with appropriate CASCADE rules
2. **Unique Constraints**: Prevent duplicate conference/team combinations per season
3. **Check Constraints**: Validate ranges (seeds 1-16, years > 1900)
4. **NOT NULL**: Required fields for data quality
5. **Default Values**: Sensible defaults for optional fields

## Indexing Strategy

### Performance-Critical Indexes

#### Primary Indexes (Automatic)
```sql
-- Primary key indexes created automatically on all UUID fields
```

#### Search and Filter Indexes
```sql
-- Conference and sport queries
CREATE INDEX idx_teams_sport_conference ON teams(sport_id, conference_id);
CREATE INDEX idx_leagues_sport_active ON leagues(sport_id, is_active);

-- Team lookups
CREATE INDEX idx_teams_slug ON teams(slug);
CREATE INDEX idx_teams_market_name ON teams(market, name);
CREATE INDEX idx_teams_abbreviation ON teams(abbreviation);

-- Season and historical data
CREATE INDEX idx_season_records_team_year ON team_season_records(team_id, season_year);
CREATE INDEX idx_season_records_conference_year ON team_season_records(conference_id, season_year);
CREATE INDEX idx_ncaa_tournament_year ON ncaa_tournament_appearances(year);
CREATE INDEX idx_ncaa_tournament_team_year ON ncaa_tournament_appearances(team_id, year);

-- Conference membership tracking
CREATE INDEX idx_team_memberships_active ON team_league_memberships(team_id, is_active);
CREATE INDEX idx_team_memberships_timeline ON team_league_memberships(team_id, season_start_year, season_end_year);
```

#### Full-Text Search Indexes
```sql
-- Team search by name and location
CREATE INDEX idx_teams_search ON teams USING gin(
    to_tsvector('english',
        coalesce(school_name, '') || ' ' ||
        coalesce(market, '') || ' ' ||
        coalesce(name, '') || ' ' ||
        coalesce(mascot, '')
    )
);

-- Conference search
CREATE INDEX idx_conferences_search ON leagues USING gin(
    to_tsvector('english',
        coalesce(name, '') || ' ' ||
        coalesce(abbreviation, '')
    )
);
```

#### Performance Optimization Indexes
```sql
-- Common filter combinations
CREATE INDEX idx_teams_active_sport ON teams(is_active, sport_id) WHERE is_active = true;
CREATE INDEX idx_current_memberships ON team_league_memberships(team_id, league_id)
    WHERE is_active = true AND season_end_year IS NULL;

-- Rankings and records queries
CREATE INDEX idx_season_records_rankings ON team_season_records(season_year, final_ap_ranking)
    WHERE final_ap_ranking IS NOT NULL;
CREATE INDEX idx_season_records_wins ON team_season_records(season_year, overall_wins)
    WHERE overall_wins > 20;
```

## Migration Planning

### Phase 1: Core Schema Enhancement (Week 1)
```sql
-- 001_enhance_college_basketball_schema.sql
1. Add college-specific columns to existing leagues table
2. Add college-specific columns to existing teams table
3. Create conference_divisions table
4. Update TeamLeagueMembership with division support
5. Create appropriate indexes for new columns
```

### Phase 2: Historical Data Tables (Week 2)
```sql
-- 002_college_basketball_historical_data.sql
1. Create ncaa_tournament_appearances table
2. Create team_season_records table
3. Create conference_tournament_results table
4. Add performance indexes
5. Add full-text search capability
```

### Phase 3: Data Population (Week 3)
```sql
-- 003_populate_college_basketball_data.sql
1. Populate enhanced conference metadata
2. Insert all 167 teams from college_basketball_teams.md
3. Create team-conference membership records
4. Add historical NCAA tournament data (last 10 years)
5. Populate recent season records
```

### Phase 4: Advanced Features (Week 4)
```sql
-- 004_college_basketball_advanced_features.sql
1. Add conference realignment history
2. Create conference championship tracking
3. Add coaching change history
4. Implement ranking systems integration
5. Create tournament bracket generation views
```

### Migration Safety Measures

#### Rollback Strategy
Each migration includes comprehensive DOWN operations:
```sql
-- Example rollback structure
CREATE OR REPLACE FUNCTION rollback_college_basketball_migration()
RETURNS VOID AS $$
BEGIN
    -- Remove new tables in reverse dependency order
    DROP TABLE IF EXISTS conference_tournament_results CASCADE;
    DROP TABLE IF EXISTS team_season_records CASCADE;
    DROP TABLE IF EXISTS ncaa_tournament_appearances CASCADE;
    DROP TABLE IF EXISTS conference_divisions CASCADE;

    -- Remove added columns
    ALTER TABLE leagues DROP COLUMN IF EXISTS tournament_autobid;
    ALTER TABLE teams DROP COLUMN IF EXISTS school_name;
    -- ... additional column removals

    -- Drop added indexes
    DROP INDEX IF EXISTS idx_teams_sport_conference;
    -- ... additional index removals
END;
$$ LANGUAGE plpgsql;
```

#### Testing Strategy
1. **Schema Validation**: Verify all constraints and relationships
2. **Data Integrity**: Ensure no orphaned records or constraint violations
3. **Performance Testing**: Validate index effectiveness with realistic queries
4. **Rollback Testing**: Verify all migrations can be safely reversed

## Query Performance Optimization

### Common Query Patterns

#### Conference Standings Query
```sql
-- Optimized for frequent conference standings requests
SELECT
    t.market, t.name, t.mascot,
    sr.conference_wins, sr.conference_losses,
    sr.overall_wins, sr.overall_losses,
    sr.conference_rank
FROM teams t
JOIN team_season_records sr ON t.id = sr.team_id
JOIN team_league_memberships tlm ON t.id = tlm.team_id
WHERE tlm.league_id = ?
    AND sr.season_year = ?
    AND tlm.is_active = true
ORDER BY sr.conference_rank ASC;
```

#### Tournament Selection Query
```sql
-- Teams eligible for NCAA tournament by criteria
SELECT
    t.market, t.name,
    sr.overall_wins, sr.overall_losses,
    sr.net_ranking, sr.strength_of_schedule,
    l.tournament_autobid
FROM teams t
JOIN team_season_records sr ON t.id = sr.team_id
JOIN team_league_memberships tlm ON t.id = tlm.team_id
JOIN leagues l ON tlm.league_id = l.id
WHERE sr.season_year = ?
    AND (sr.net_ranking <= 68 OR l.tournament_autobid = true)
ORDER BY sr.net_ranking ASC;
```

### Materialized Views for Performance
```sql
-- Current conference standings materialized view
CREATE MATERIALIZED VIEW current_conference_standings AS
SELECT
    l.name as conference_name,
    t.id as team_id,
    t.market || ' ' || t.name as team_name,
    sr.conference_wins,
    sr.conference_losses,
    sr.overall_wins,
    sr.overall_losses,
    rank() OVER (PARTITION BY l.id ORDER BY sr.conference_wins DESC, sr.conference_losses ASC) as conference_rank
FROM teams t
JOIN team_season_records sr ON t.id = sr.team_id
JOIN team_league_memberships tlm ON t.id = tlm.team_id AND tlm.is_active = true
JOIN leagues l ON tlm.league_id = l.id
WHERE sr.season_year = EXTRACT(year FROM CURRENT_DATE)
    AND l.sport_id = (SELECT id FROM sports WHERE slug = 'college-basketball');

-- Refresh strategy
CREATE INDEX ON current_conference_standings(conference_name, conference_rank);
```

## Data Quality and Validation

### Constraint Strategy
1. **Conference Membership**: Teams can only be in one primary conference per season
2. **Season Integrity**: Season records must match team's conference during that period
3. **Tournament Logic**: Only teams from autobid conferences or at-large selections
4. **Historical Accuracy**: Conference changes must maintain timeline consistency

### Validation Functions
```sql
-- Validate conference membership timeline
CREATE OR REPLACE FUNCTION validate_conference_membership_timeline()
RETURNS TRIGGER AS $$
BEGIN
    -- Ensure no overlapping active memberships
    IF EXISTS (
        SELECT 1 FROM team_league_memberships
        WHERE team_id = NEW.team_id
            AND id != NEW.id
            AND is_active = true
            AND (season_end_year IS NULL OR season_end_year >= NEW.season_start_year)
            AND NEW.season_start_year <= COALESCE(season_end_year, 9999)
    ) THEN
        RAISE EXCEPTION 'Team cannot have overlapping active conference memberships';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

## Supabase-Specific Optimizations

### Row Level Security (RLS)
```sql
-- Public read access for team and conference data
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Teams are publicly readable" ON teams FOR SELECT USING (true);

ALTER TABLE leagues ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Conferences are publicly readable" ON leagues FOR SELECT USING (true);

-- Admin-only write access
CREATE POLICY "Admin can modify teams" ON teams FOR ALL USING (
    auth.jwt() ->> 'role' = 'admin'
);
```

### Real-time Subscriptions
```sql
-- Enable real-time for live scoring and rankings
ALTER publication supabase_realtime ADD TABLE team_season_records;
ALTER publication supabase_realtime ADD TABLE ncaa_tournament_appearances;
```

### Performance Monitoring
```sql
-- Track query performance
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Monitor slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
WHERE query ILIKE '%college%basketball%'
ORDER BY total_time DESC;
```

## Implementation Timeline

### Week 1: Foundation
- [ ] Create enhanced schema migrations
- [ ] Update existing college basketball conferences
- [ ] Add college-specific metadata fields
- [ ] Implement core indexes

### Week 2: Data Modeling
- [ ] Create historical data tables
- [ ] Implement tournament tracking
- [ ] Add season records capability
- [ ] Create performance optimization indexes

### Week 3: Data Population
- [ ] Import all 167 teams from college_basketball_teams.md
- [ ] Create team-conference relationships
- [ ] Populate historical tournament data
- [ ] Add recent season records

### Week 4: Advanced Features
- [ ] Implement conference realignment tracking
- [ ] Add ranking systems integration
- [ ] Create tournament bracket views
- [ ] Performance testing and optimization

## Success Metrics

### Performance Targets
- **Team Search Queries**: < 50ms response time
- **Conference Standings**: < 100ms for full conference
- **Tournament History**: < 200ms for multi-year data
- **Full-Text Search**: < 150ms across all teams/conferences

### Data Quality Goals
- **Duplicate Rate**: < 0.1% for team records
- **Referential Integrity**: 100% maintained
- **Historical Accuracy**: 99.9% for tournament data
- **Conference Membership**: 100% timeline consistency

### Scalability Requirements
- **Support Growth**: 500+ teams (future expansion)
- **Historical Data**: 50+ years of records
- **Concurrent Users**: 10,000+ simultaneous queries
- **Real-time Updates**: < 1 second latency for live data

This comprehensive plan provides a robust foundation for college basketball data management while maintaining compatibility with the existing sports platform architecture and ensuring optimal performance for both current and future requirements.