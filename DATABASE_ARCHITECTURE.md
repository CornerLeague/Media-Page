# Corner League Media - Database Architecture & API Contracts

## Overview

This document outlines the complete database architecture and API contracts for the Corner League Media sports platform. The system is designed to support personalized team content, real-time sports information, and fan experiences with robust data integrity and performance optimization.

## Technology Stack

- **Database**: PostgreSQL 15+ with Supabase compatibility
- **ORM**: SQLAlchemy 2.0+ with async support
- **Migrations**: Alembic with safe rollback strategies
- **API Framework**: FastAPI with OpenAPI 3.0 specification
- **Authentication**: Clerk JWT authentication
- **Caching**: Redis for performance optimization
- **Search**: PostgreSQL full-text search with pg_trgm

## Database Schema

### Core Entity Relationships

```
Sports (1:N) Leagues (1:N) Teams
   |                           |
   |                           |
   +----- Articles (M:N) ------+
   |                           |
   |                           |
   +----- Users (M:N) ---------+
           |
           +--- Preferences
           +--- Interactions
           +--- Experiences
```

### Key Design Principles

1. **Data Integrity**: Comprehensive foreign key constraints and check constraints
2. **Performance**: Strategic indexing for query patterns
3. **Scalability**: Partitioning-ready design for large tables
4. **Auditability**: Timestamp tracking and soft deletes
5. **Flexibility**: JSONB fields for extensible metadata

## Entity Details

### 1. Sports & Leagues Hierarchy

**Sports Table**: Core sports (Basketball, Football, Baseball, Hockey)
- UUID primary keys for scalability
- Slug fields for URL-friendly identifiers
- Display ordering and active status

**Leagues Table**: Sport-specific leagues (NBA, NFL, MLB, NHL)
- Foreign key to sports with CASCADE delete
- Season metadata (start/end months)
- Unique constraints on sport-slug combinations

**Teams Table**: Individual teams within leagues
- References both sport and league for query optimization
- Team branding data (colors, logos)
- External API integration support

### 2. User Management & Authentication

**Users Table**: Extends Clerk authentication
- Clerk user ID as unique identifier
- Onboarding completion tracking
- Content frequency preferences

**User Preferences**: Granular preference control
- Sport rankings (1 = most preferred)
- Team affinity scores (0.0 to 1.0)
- News type preferences with priorities
- Notification settings

### 3. Content Management System

**Feed Sources**: RSS/Atom feed management
- Active monitoring with failure tracking
- Configurable fetch intervals
- Website metadata for attribution

**Feed Snapshots**: Deduplication layer
- URL hash for primary deduplication
- Content hash for exact duplicate detection
- MinHash signatures for near-duplicate detection
- Processing status tracking

**Articles**: Processed content with classification
- Full-text search vector for performance
- AI-powered categorization
- Sentiment analysis scores
- Sport/team relationship scoring

### 4. Games & Live Data

**Games Table**: Scheduled and completed games
- Real-time score tracking
- Game status progression
- Venue and season metadata

**Game Events**: Live play-by-play data
- Event-driven updates for real-time features
- Player and team attribution
- Point value tracking for scoring

### 5. Fan Engagement

**Fan Experiences**: Community events and meetups
- Multiple experience types (watch parties, tailgates)
- Attendance tracking and limits
- Geographic location support

**Ticket Deals**: Aggregated ticket pricing
- Provider relationships
- AI-powered deal scoring (0.0 to 1.0)
- Expiration tracking

### 6. Analytics & Performance

**User Interactions**: Behavioral tracking
- Interaction type categorization
- Entity references for flexible analytics
- JSONB metadata for extensible data

**Content Performance**: Metrics aggregation
- Time-series performance data
- Content scoring for recommendation algorithms
- Date-partitioned for historical analysis

## Deduplication Strategy

### Multi-Layer Approach

1. **URL Normalization**: Remove tracking parameters, canonicalize format
2. **Primary Deduplication**: SHA-256 hash of normalized URL
3. **Content Hashing**: SHA-256 hash of title + content
4. **Near-Duplicate Detection**: MinHash with Jaccard similarity (>85% threshold)

### Performance Targets

- **Duplicate Rate**: <1% false negatives
- **Processing Speed**: >1000 articles/minute
- **Storage Efficiency**: >90% unique content retention

### Implementation Details

```python
# URL normalization removes tracking parameters
# Content fingerprinting using MinHash (128 permutations)
# Sliding window comparison (30-day lookback)
# Configurable similarity thresholds per content type
```

## API Architecture

### Authentication & Authorization

- **JWT Bearer Tokens**: Clerk-issued tokens for all authenticated endpoints
- **Row Level Security**: Supabase RLS policies for data isolation
- **Rate Limiting**: Tiered limits by authentication status
- **CORS**: Configured for frontend domain whitelist

### API Design Patterns

1. **RESTful Resources**: Standard HTTP methods and status codes
2. **Consistent Responses**: Standardized `APIResponse<T>` wrapper
3. **Pagination**: Cursor-based pagination for large datasets
4. **Error Handling**: Structured error responses with codes
5. **Versioning**: URL path versioning (`/api/v1/`)

### Key Endpoints

```yaml
# User Management
GET    /api/v1/users/me
PUT    /api/v1/users/me
PATCH  /api/v1/users/me/preferences

# Content & Feeds
GET    /api/v1/sports/feed
GET    /api/v1/sports/personalized

# Team Data
GET    /api/v1/teams/{id}/dashboard

# Games & Scores
GET    /api/v1/games
GET    /api/v1/games/{id}

# Real-time Updates
WS     /ws (WebSocket for live updates)
```

### Response Formats

```typescript
// Standard API Response
interface APIResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
  timestamp: string;
}

// Paginated Response
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
}
```

## Migration Strategy

### Alembic Configuration

- **Safe Migrations**: All migrations include explicit downgrade functions
- **Rollback Testing**: Automated testing of migration rollbacks
- **Zero-Downtime**: Migrations designed for live system updates
- **Linear History**: No branching or merging of migration files

### Migration Phases

1. **Phase 1**: Core schema (sports, users, basic content)
2. **Phase 2**: Advanced features (experiences, analytics)
3. **Phase 3**: Performance optimizations (indexes, functions)

### Rollback Strategy

```sql
-- Each migration includes comprehensive rollback
-- Drop in reverse dependency order
-- Preserve data integrity during rollbacks
-- Test rollbacks in staging environment
```

## Performance Optimization

### Indexing Strategy

```sql
-- User query patterns
CREATE INDEX idx_users_clerk_id ON users(clerk_user_id);
CREATE INDEX idx_user_team_prefs_affinity ON user_team_preferences(user_id, affinity_score DESC);

-- Content discovery
CREATE INDEX idx_articles_published ON articles(published_at DESC);
CREATE INDEX idx_articles_search_vector ON articles USING GIN(search_vector);

-- Real-time updates
CREATE INDEX idx_games_status ON games(status);
CREATE INDEX idx_game_events_game_time ON game_events(game_id, event_time);
```

### Query Optimization

- **Eager Loading**: SQLAlchemy selectinload for relationships
- **Query Batching**: Bulk operations for data processing
- **Connection Pooling**: Async connection management
- **Prepared Statements**: Parameterized queries for security

### Full-Text Search

```sql
-- Weighted search vectors
CREATE TRIGGER update_article_search_vector_trigger
  BEFORE INSERT OR UPDATE ON articles
  FOR EACH ROW EXECUTE FUNCTION update_article_search_vector();

-- Search function with ranking
SELECT ts_rank(search_vector, query) as rank, *
FROM articles, plainto_tsquery('english', $1) query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

## Data Integrity & Constraints

### Referential Integrity

- **Cascade Deletes**: Parent-child relationships with appropriate cascade behavior
- **Check Constraints**: Data validation at database level
- **Unique Constraints**: Prevent duplicate data entry
- **NOT NULL Constraints**: Required field enforcement

### Business Logic Constraints

```sql
-- Affinity scores must be between 0 and 1
ALTER TABLE user_team_preferences
ADD CONSTRAINT check_valid_affinity
CHECK (affinity_score >= 0 AND affinity_score <= 1);

-- Deal scores must be between 0 and 1
ALTER TABLE ticket_deals
ADD CONSTRAINT check_valid_deal_score
CHECK (deal_score >= 0 AND deal_score <= 1);

-- Attendee counts cannot exceed capacity
ALTER TABLE fan_experiences
ADD CONSTRAINT check_valid_attendee_count
CHECK (current_attendees <= max_attendees);
```

## Monitoring & Maintenance

### Health Checks

- **Connection Pool**: Monitor active/idle connections
- **Query Performance**: Track slow queries (>1s)
- **Replication Lag**: Monitor read replica synchronization
- **Storage Usage**: Track table sizes and growth

### Maintenance Procedures

```sql
-- Regular maintenance
VACUUM ANALYZE articles;
REINDEX INDEX idx_articles_search_vector;

-- Performance monitoring
SELECT * FROM pg_stat_statements
WHERE mean_time > 1000
ORDER BY total_time DESC;

-- Storage analysis
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Security Considerations

### Data Protection

- **Encryption at Rest**: Database-level encryption
- **Encryption in Transit**: TLS for all connections
- **PII Handling**: Minimal storage, secure deletion
- **Audit Logging**: Track data access and modifications

### Access Control

```sql
-- Row Level Security policies
CREATE POLICY "Users can view own data" ON users
  FOR SELECT USING (auth.uid()::text = clerk_user_id);

CREATE POLICY "Users can manage own preferences" ON user_team_preferences
  FOR ALL USING (user_id IN (SELECT id FROM users WHERE clerk_user_id = auth.uid()::text));
```

## Deployment Architecture

### Database Setup

1. **Primary Database**: PostgreSQL 15+ with required extensions
2. **Read Replicas**: For read-heavy workloads
3. **Connection Pooling**: PgBouncer for connection management
4. **Backup Strategy**: Continuous WAL archiving + daily snapshots

### Environment Configuration

```bash
# Required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

# Supabase compatibility
-- All schema compatible with Supabase postgres
-- RLS policies for multi-tenant security
-- Real-time subscriptions for live updates
```

## File Structure

```
/database/
├── schema.sql              # Complete schema definition
├── seeds/
│   └── 001_initial_data.py # Sample data for development
/backend/
├── models/                 # SQLAlchemy models
│   ├── __init__.py
│   ├── base.py
│   ├── sports.py
│   ├── users.py
│   ├── content.py
│   └── ...
├── alembic/               # Migration management
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── ingestion/             # Content pipeline
│   ├── pipeline.py
│   └── deduplication.py
└── api/
    ├── schemas/           # Pydantic schemas
    └── openapi_spec.yaml  # Complete API specification
/src/lib/types/
└── backend-types.ts       # TypeScript definitions
```

## Getting Started

### Development Setup

```bash
# 1. Initialize database
createdb corner_league_dev
psql corner_league_dev < database/schema.sql

# 2. Run migrations
alembic upgrade head

# 3. Seed development data
python database/seeds/001_initial_data.py

# 4. Start API server
uvicorn backend.main:app --reload
```

### Production Deployment

```bash
# 1. Set environment variables
export DATABASE_URL="postgresql://..."
export CLERK_SECRET_KEY="..."

# 2. Run migrations
alembic upgrade head

# 3. Start production server
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
```

## Testing Strategy

### Database Testing

- **Migration Testing**: Automated up/down migration testing
- **Constraint Testing**: Validate all check constraints
- **Performance Testing**: Query performance benchmarks
- **Data Integrity**: Foreign key relationship testing

### API Testing

- **Unit Tests**: Individual endpoint testing
- **Integration Tests**: End-to-end workflow testing
- **Load Testing**: Performance under concurrent load
- **Security Testing**: Authentication and authorization validation

## Future Enhancements

### Scalability Improvements

1. **Table Partitioning**: Time-based partitioning for large tables
2. **Sharding Strategy**: Geographic or team-based sharding
3. **Caching Layer**: Redis for frequently accessed data
4. **CDN Integration**: Static asset optimization

### Feature Extensions

1. **Real-time Notifications**: WebSocket push notifications
2. **Advanced Analytics**: ML-powered recommendation engine
3. **Mobile API**: Optimized endpoints for mobile apps
4. **Third-party Integrations**: ESPN, Twitter, etc.

---

This architecture provides a robust foundation for the Corner League Media platform, ensuring data integrity, performance, and scalability while maintaining flexibility for future enhancements.