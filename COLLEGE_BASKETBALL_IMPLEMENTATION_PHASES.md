# College Basketball Database Schema Implementation Phases

## Executive Summary

This document outlines a strategic 6-phase approach for implementing a comprehensive college basketball database schema within the existing Corner League Media platform. The implementation builds upon the current sports data infrastructure while introducing college-specific entities and relationships.

## Current Infrastructure Analysis

**Existing Foundation:**
- PostgreSQL with async SQLAlchemy models
- Alembic migration system with proper versioning
- Core sports entities: Sport, League, Team with multi-league support
- Content ingestion pipeline with deduplication
- User preferences and Firebase authentication
- Full-text search capabilities

**Database Extensions Already Available:**
- `uuid-ossp`, `pg_trgm`, `unaccent`, `pgcrypto`
- Existing enums and indexes optimized for performance

---

## Phase 1: College Basketball Foundation
**Timeline: 1-2 weeks**
**Objective: Establish college-specific core entities**

### Database Changes

**New Tables:**
- `college_divisions` - NCAA divisions (D1, D2, D3, NAIA, NJCAA)
- `conferences` - College conferences (ACC, SEC, Big Ten, etc.)
- `colleges` - Educational institutions
- `college_teams` - College-specific team data

**New Enums:**
```sql
CREATE TYPE division_level AS ENUM ('D1', 'D2', 'D3', 'NAIA', 'NJCAA', 'JC');
CREATE TYPE conference_type AS ENUM ('major', 'mid_major', 'low_major', 'independent');
CREATE TYPE academic_season AS ENUM ('fall', 'spring', 'summer');
```

### Migration Scripts
1. **001_college_foundation.py** - Create divisions and conferences
2. **002_colleges_and_teams.py** - Add colleges and college teams
3. **003_college_indexes.py** - Performance indexes for college queries

### Data Population
- Seed 32 major conferences with metadata
- Load 350+ Division 1 colleges
- Create team records for major programs
- Establish conference memberships

### Testing Criteria
- ✓ All foreign key relationships validated
- ✓ Conference-college relationships properly mapped
- ✓ Team-college linkage functional
- ✓ Query performance <100ms for conference listings
- ✓ Migration rollback successful

### Dependencies
- None (builds on existing sports infrastructure)

### Deliverables
- SQLAlchemy models: `CollegeDivision`, `Conference`, `College`, `CollegeTeam`
- Migration files with proper rollback procedures
- Seed data for major conferences and colleges
- Basic API endpoints for college team lookup

---

## Phase 2: Academic and Season Framework
**Timeline: 2-3 weeks**
**Objective: Implement academic calendar and season management**

### Database Changes

**New Tables:**
- `academic_years` - Academic year periods (2023-24, 2024-25)
- `college_seasons` - Basketball seasons within academic years
- `conference_memberships` - Historical conference changes
- `season_conferences` - Conference lineups per season

**Schema Extensions:**
- Add `academic_year_id` to relevant tables
- Include `season_type` (regular, conference_tournament, ncaa_tournament)
- Academic calendar integration fields

### Migration Scripts
1. **004_academic_framework.py** - Academic years and seasons
2. **005_conference_memberships.py** - Historical conference tracking
3. **006_academic_indexes.py** - Academic query optimization

### Data Population
- Historical academic years (2010-present)
- Conference membership changes over time
- Season type classifications
- Academic calendar alignment

### Testing Criteria
- ✓ Academic year calculations accurate
- ✓ Conference history preserved correctly
- ✓ Season queries perform <150ms
- ✓ Historical data integrity maintained
- ✓ Academic calendar edge cases handled

### Dependencies
- Phase 1 completion (conferences and colleges)

### Deliverables
- Models: `AcademicYear`, `CollegeSeason`, `ConferenceMembership`
- Historical conference change tracking
- Academic calendar utilities
- Season-aware team queries

---

## Phase 3: Games and Competition Structure
**Timeline: 2-3 weeks**
**Objective: Implement college basketball game and tournament structure**

### Database Changes

**New Tables:**
- `college_games` - Individual basketball games
- `game_participants` - Team participation in games
- `tournaments` - Tournament definitions (March Madness, conference tournaments)
- `tournament_brackets` - Tournament structure and advancement
- `game_venues` - Playing locations and arena information

**Enhanced Enums:**
```sql
CREATE TYPE tournament_type AS ENUM ('ncaa', 'nit', 'cbi', 'conference', 'regular');
CREATE TYPE game_type AS ENUM ('regular_season', 'conference_tournament', 'ncaa_tournament', 'exhibition');
CREATE TYPE bracket_round AS ENUM ('first_four', 'round_64', 'round_32', 'sweet_16', 'elite_8', 'final_4', 'championship');
```

### Migration Scripts
1. **007_college_games.py** - Game structure and participants
2. **008_tournaments_and_brackets.py** - Tournament framework
3. **009_game_venues.py** - Venue and location data
4. **010_competition_indexes.py** - Game query optimization

### Data Population
- Historical March Madness brackets (2010-present)
- Major conference tournament structures
- Venue data for major arenas
- Regular season game templates

### Testing Criteria
- ✓ Tournament bracket integrity maintained
- ✓ Game-team relationships accurate
- ✓ Venue assignments correct
- ✓ Performance <200ms for tournament queries
- ✓ Bracket advancement logic functional

### Dependencies
- Phase 2 completion (academic seasons)

### Deliverables
- Models: `CollegeGame`, `Tournament`, `TournamentBracket`, `GameVenue`
- March Madness bracket management
- Conference tournament support
- Game scheduling framework

---

## Phase 4: Advanced Statistics and Rankings
**Timeline: 3-4 weeks**
**Objective: Implement comprehensive statistics and ranking systems**

### Database Changes

**New Tables:**
- `team_statistics` - Seasonal team performance metrics
- `player_statistics` - Individual player stats
- `ranking_systems` - Various ranking methodologies (AP, Coaches, NET, KenPom)
- `team_rankings` - Historical ranking data
- `advanced_metrics` - Analytics like efficiency ratings

**Statistical Framework:**
- Offensive/defensive efficiency calculations
- Strength of schedule metrics
- Historical ranking preservation
- Real-time stat updates

### Migration Scripts
1. **011_team_statistics.py** - Core team statistical framework
2. **012_player_statistics.py** - Individual player metrics
3. **013_ranking_systems.py** - Ranking methodology support
4. **014_advanced_metrics.py** - Analytics and efficiency ratings
5. **015_statistics_indexes.py** - Performance optimization

### Data Population
- Historical AP and Coaches Poll data
- NET ranking integration
- Advanced metrics for major programs
- Player statistical leaders

### Testing Criteria
- ✓ Statistical calculations accurate
- ✓ Ranking historical integrity preserved
- ✓ Advanced metrics computed correctly
- ✓ Query performance <250ms for complex stats
- ✓ Real-time update mechanisms functional

### Dependencies
- Phase 3 completion (games and tournaments)

### Deliverables
- Models: `TeamStatistics`, `PlayerStatistics`, `RankingSystem`, `AdvancedMetrics`
- Statistical calculation utilities
- Ranking historical preservation
- Performance analytics dashboard support

---

## Phase 5: Content Integration and Media
**Timeline: 2-3 weeks**
**Objective: Integrate college basketball content with existing content pipeline**

### Database Changes

**Table Extensions:**
- Extend `content_articles` with college-specific fields
- Add `college_content_classification` for academic context
- Create `recruiting_content` for recruiting news
- Implement `coach_content` for coaching changes

**Content Enhancement:**
- College-specific content categorization
- Recruiting news classification
- Academic achievement integration
- Coach and staff change tracking

### Migration Scripts
1. **016_college_content_extension.py** - Extend content framework
2. **017_recruiting_content.py** - Recruiting news support
3. **018_coaching_content.py** - Coaching change tracking
4. **019_content_classification.py** - College content categorization

### Data Population
- Historical recruiting content
- Coaching change archives
- Academic achievement records
- Conference content categorization

### Testing Criteria
- ✓ Content pipeline integration successful
- ✓ College-specific categorization accurate
- ✓ Deduplication <1% rate maintained
- ✓ Full-text search relevance optimized
- ✓ Content ingestion performance maintained

### Dependencies
- Phase 4 completion (statistics framework)
- Existing content ingestion pipeline

### Deliverables
- Enhanced content models with college specificity
- Recruiting news pipeline
- Coaching change tracking
- College content classification system

---

## Phase 6: User Experience and Personalization
**Timeline: 2-3 weeks**
**Objective: Enable college basketball user preferences and personalized experiences**

### Database Changes

**New Tables:**
- `user_college_preferences` - College team following
- `user_conference_interests` - Conference-level preferences
- `bracket_predictions` - March Madness bracket picks
- `college_notifications` - College-specific notification preferences

**Personalization Framework:**
- College team preference management
- Conference-level interest tracking
- Tournament bracket prediction system
- Academic calendar integration

### Migration Scripts
1. **020_user_college_preferences.py** - College team preferences
2. **021_conference_interests.py** - Conference-level preferences
3. **022_bracket_predictions.py** - Tournament prediction system
4. **023_college_notifications.py** - Notification preferences

### Data Population
- Default preference templates
- Conference interest categories
- Bracket prediction frameworks
- Notification preference defaults

### Testing Criteria
- ✓ User preference storage accurate
- ✓ Bracket prediction logic functional
- ✓ Notification delivery targeted
- ✓ Personalization queries <100ms
- ✓ User data privacy maintained

### Dependencies
- Phase 5 completion (content integration)
- Existing user preference framework

### Deliverables
- Models: `UserCollegePreferences`, `BracketPrediction`, `CollegeNotifications`
- Personalized content delivery
- March Madness bracket system
- College-specific notification framework

---

## Implementation Guidelines

### Migration Strategy
**Idempotent Design:**
- All migrations include proper rollback procedures
- Safe defaults for new NOT NULL constraints
- Indexes created within migration files
- Foreign key constraints with appropriate cascading

**Performance Considerations:**
- Create indexes during low-traffic periods
- Use `CONCURRENTLY` for index creation in production
- Batch data population to avoid lock contention
- Monitor query performance after each phase

### Quality Assurance Standards

**Data Integrity:**
- All foreign key relationships properly defined
- No orphaned records possible
- Enum constraints enforced at database level
- Unique constraints prevent duplicates

**Performance Benchmarks:**
- Conference listings: <100ms
- Team rosters: <150ms
- Game schedules: <200ms
- Statistical queries: <250ms
- Complex tournament brackets: <300ms

**Testing Requirements:**
- Unit tests for all model relationships
- Integration tests for data population
- Performance tests for complex queries
- Migration rollback verification
- End-to-end user preference testing

### Data Population Strategy

**Seed Data Priorities:**
1. **Phase 1:** Major conferences and D1 colleges
2. **Phase 2:** Recent academic years (2020-present)
3. **Phase 3:** March Madness brackets (2015-present)
4. **Phase 4:** Current season statistics
5. **Phase 5:** Recent recruiting and coaching content
6. **Phase 6:** Default user preference templates

**External Data Sources:**
- NCAA official APIs for authoritative data
- ESPN and Sports Reference for historical information
- Conference websites for membership changes
- Academic calendars from institutional sources

### Monitoring and Maintenance

**Health Metrics:**
- Ingestion pipeline duplicate rates (<1%)
- Query performance degradation alerts
- Data consistency validation routines
- User preference update frequencies

**Maintenance Procedures:**
- Weekly VACUUM and ANALYZE on large tables
- Monthly index usage analysis
- Quarterly data archival for old seasons
- Annual academic year rollover procedures

---

## Estimated Timeline Summary

| Phase | Duration | Deliverables | Critical Path |
|-------|----------|--------------|---------------|
| 1 | 1-2 weeks | College foundation entities | Independent |
| 2 | 2-3 weeks | Academic framework | Depends on Phase 1 |
| 3 | 2-3 weeks | Games and tournaments | Depends on Phase 2 |
| 4 | 3-4 weeks | Statistics and rankings | Depends on Phase 3 |
| 5 | 2-3 weeks | Content integration | Depends on Phase 4 |
| 6 | 2-3 weeks | User personalization | Depends on Phase 5 |

**Total Estimated Duration: 12-18 weeks**

**Parallel Development Opportunities:**
- Content ingestion adaptation (Phase 5) can begin during Phase 4
- User interface updates can proceed alongside Phase 6
- Testing infrastructure can be developed during any phase

This phased approach ensures systematic, testable implementation of college basketball functionality while maintaining the existing platform's stability and performance standards.