# Corner League Media Database

A comprehensive PostgreSQL/Supabase database solution for the Corner League Media sports platform with advanced content ingestion, deduplication, and full-text search capabilities.

## 🏗️ Architecture Overview

### Core Components
- **PostgreSQL Schema**: Optimized for Supabase with RLS policies
- **SQLAlchemy Models**: Type-safe ORM models matching Pydantic schemas
- **Alembic Migrations**: Reversible database migrations with safe rollback
- **Content Ingestion**: High-performance pipeline with <1% duplicate rate
- **Full-Text Search**: PostgreSQL FTS with pg_trgm and tsvector optimization
- **Performance Monitoring**: Built-in analytics and maintenance utilities

### Database Tables

#### Core Entities
- **Users**: Authentication via Clerk, preferences, team relationships
- **Teams**: Sports teams (NFL, NBA, MLB, NHL) with full metadata
- **Articles**: Sports content with AI classification and team associations
- **Games**: Match/game data with real-time scoring
- **Team Stats**: Season statistics with computed metrics

#### Ingestion Pipeline
- **Feed Sources**: Content source configurations
- **Ingestion Logs**: Duplicate detection and error tracking
- **Search Analytics**: User search behavior and optimization data

#### User Engagement
- **User Teams**: Many-to-many team following relationships
- **User Preference History**: Audit trail for preference changes

## 🚀 Quick Start

### 1. Environment Configuration

Configure your database connection in `.env`:

```bash
# For local development
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sportsdb

# For Supabase (production)
SUPABASE_DATABASE_URL=postgresql://postgres:[password]@[host]:5432/postgres
SUPABASE_DB_HOST=your-project-ref.supabase.co
SUPABASE_DB_PASSWORD=your-database-password
SUPABASE_DB_NAME=postgres

# Performance settings
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
```

### 2. Database Setup

```bash
# Run complete setup with seed data
python app/database/setup.py

# Reset database (caution: drops all data)
python app/database/setup.py --reset

# Health check only
python app/database/setup.py --check-only
```

### 3. Migrations

```bash
# Create new migration
cd app/database && alembic revision --autogenerate -m "description"

# Apply migrations
cd app/database && alembic upgrade head

# Rollback migration
cd app/database && alembic downgrade -1
```

## 📊 Database Schema

### Users & Authentication
```sql
-- Users with Clerk integration
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_user_id TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    preferences JSONB NOT NULL DEFAULT '{}',
    role user_role NOT NULL DEFAULT 'user',
    status user_status NOT NULL DEFAULT 'active'
);

-- User-Team relationships
CREATE TABLE user_teams (
    user_id UUID REFERENCES users(id),
    team_id UUID REFERENCES teams(id),
    followed_at TIMESTAMPTZ DEFAULT NOW(),
    notifications_enabled BOOLEAN DEFAULT TRUE
);
```

### Content Management
```sql
-- Articles with full-text search
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url_hash TEXT NOT NULL UNIQUE, -- Primary deduplication
    title TEXT NOT NULL,
    content TEXT,
    team_ids UUID[], -- Related teams
    search_vector TSVECTOR, -- Full-text search
    ai_summary TEXT,
    ai_category content_category,
    ai_confidence NUMERIC(3,2)
);

-- Teams with comprehensive metadata
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    abbreviation TEXT NOT NULL,
    sport sport_type NOT NULL,
    league league_type NOT NULL,
    primary_color TEXT,
    search_vector TSVECTOR
);
```

### Ingestion Pipeline
```sql
-- Feed source configurations
CREATE TABLE feed_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL,
    feed_type TEXT NOT NULL,
    config JSONB DEFAULT '{}',
    fetch_interval_minutes INTEGER DEFAULT 30
);

-- Ingestion tracking with duplicate detection
CREATE TABLE ingestion_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url_hash TEXT NOT NULL,
    ingestion_status TEXT NOT NULL, -- 'success', 'duplicate', 'error'
    duplicate_of UUID REFERENCES articles(id),
    similarity_score NUMERIC(3,2)
);
```

## 🔍 Content Ingestion Pipeline

### Deduplication Strategy
The system implements a multi-layered deduplication approach:

1. **URL Hash**: Primary deduplication using normalized URL hashing
2. **Content Similarity**: Jaccard similarity on title/content features
3. **MinHash**: Near-duplicate detection for performance at scale

```python
from app.database.utils.ingestion import IngestionPipeline, ContentItem

# Create content item
content = ContentItem(
    url="https://example.com/article",
    title="Team News Update",
    content="Article content...",
    team_names=["Lakers", "Warriors"]
)

# Ingest with automatic deduplication
pipeline = IngestionPipeline()
results = pipeline.process_content_batch([content])
print(f"Duplicate rate: {results['duplicate_rate']:.1%}")
```

### Feed Source Management
```python
from app.database.utils.ingestion import FeedSourceManager

# Create RSS feed source
source_id = FeedSourceManager.create_feed_source(
    name="ESPN NBA News",
    url="https://www.espn.com/espn/rss/nba/news",
    feed_type="rss",
    fetch_interval_minutes=30
)

# Process all due sources
sources = FeedSourceManager.get_sources_due_for_fetch()
for source in sources:
    results = pipeline.process_feed_source(source.id)
```

## 🔎 Full-Text Search

### Search Implementation
PostgreSQL full-text search with optimized ranking:

```python
from app.database.utils.search import FullTextSearchManager

# Search articles with team filtering
results = FullTextSearchManager.search_articles(
    query="trade rumors",
    team_ids=[team_id],
    limit=20
)

# Search teams
teams = FullTextSearchManager.search_teams(
    query="Los Angeles",
    sport="nba"
)

# Get search suggestions
suggestions = FullTextSearchManager.search_suggestions("laker")
```

### Search Analytics
```python
# Track search performance
analytics = FullTextSearchManager.search_analytics_summary(days=30)
print(f"Click-through rate: {analytics['click_through_rate']:.1%}")

# Get trending searches
trending = FullTextSearchManager.get_trending_searches(days=7)
```

## 🛡️ Row Level Security (RLS)

### Supabase RLS Policies
The database includes comprehensive RLS policies for multi-tenant security:

```sql
-- Users can only access their own data
CREATE POLICY "users_select_policy" ON users
    FOR SELECT USING (clerk_user_id = auth.jwt() ->> 'sub');

-- Articles are publicly readable when published
CREATE POLICY "articles_select_policy" ON articles
    FOR SELECT USING (status = 'published');

-- User-team relationships are private
CREATE POLICY "user_teams_select_policy" ON user_teams
    FOR SELECT USING (user_id = get_current_user_id());
```

### Helper Functions
```sql
-- Get current user role for authorization
CREATE FUNCTION get_current_user_role() RETURNS user_role;

-- Check admin privileges
CREATE FUNCTION is_admin() RETURNS BOOLEAN;

-- Get current user ID from JWT
CREATE FUNCTION get_current_user_id() RETURNS UUID;
```

## 📈 Performance Optimization

### Indexing Strategy
```sql
-- Full-text search indexes
CREATE INDEX idx_articles_search_vector ON articles USING gin(search_vector);
CREATE INDEX idx_teams_search_vector ON teams USING gin(search_vector);

-- Query optimization indexes
CREATE INDEX idx_articles_team_ids ON articles USING gin(team_ids);
CREATE INDEX idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX idx_user_teams_user_id ON user_teams(user_id);

-- Partial indexes for active records
CREATE INDEX idx_teams_status ON teams(status) WHERE status = 'active';
```

### Maintenance Operations
```python
from app.database.utils.maintenance import DatabaseMaintenance

# Regular maintenance
DatabaseMaintenance.vacuum_analyze()
DatabaseMaintenance.update_table_statistics()

# Performance monitoring
health = DatabaseMaintenance.health_check()
recommendations = DatabaseMaintenance.optimize_queries()

# Cleanup old data
cleaned = DatabaseMaintenance.cleanup_old_data(days=90)
```

## 🗃️ Seed Data

### Sports Teams
The system includes comprehensive seed data for major sports leagues:

- **NFL**: 32 teams with conferences, divisions, colors
- **NBA**: 30 teams with conferences, divisions, colors
- **MLB**: 30 teams with leagues, divisions, colors
- **NHL**: 32 teams with conferences, divisions, colors

```python
from app.database.seed_data.load_teams import load_all_teams

# Load all team data
results = load_all_teams()
print(f"Loaded: {results}")
# Output: {'nfl': 32, 'nba': 30, 'mlb': 30, 'nhl': 32}
```

## 🔧 Database Utilities

### Connection Management
```python
from app.database.database import get_session, check_database_connection

# Session management with automatic cleanup
with get_session() as session:
    user = session.execute(select(User).where(User.id == user_id)).scalar_one()

# Health checks
is_healthy = check_database_connection()
db_info = get_database_info()
```

### Migration Management
```bash
# Generate migration from model changes
cd app/database
alembic revision --autogenerate -m "add new feature"

# Apply migrations
alembic upgrade head

# Rollback specific migration
alembic downgrade <revision_id>

# Show migration history
alembic history --verbose
```

## 📊 Monitoring & Analytics

### Ingestion Metrics
```python
# Get ingestion performance
pipeline = IngestionPipeline()
stats = pipeline.get_ingestion_stats(days=7)

# Example output:
{
    'total_attempts': 1500,
    'successful': 1350,
    'duplicates': 120,
    'errors': 30,
    'duplicate_rate': 0.08,  # 8% duplicate rate
    'success_rate': 0.90,
    'error_rate': 0.02
}
```

### Search Analytics
```python
# Search performance metrics
search_manager = FullTextSearchManager()
analytics = search_manager.search_analytics_summary(days=30)

# Example output:
{
    'total_searches': 5000,
    'unique_users': 1200,
    'avg_results_per_search': 15.3,
    'zero_result_rate': 0.05,
    'click_through_rate': 0.12
}
```

## 🚀 Production Deployment

### Supabase Configuration
1. Create Supabase project
2. Configure environment variables
3. Run migrations: `alembic upgrade head`
4. Apply RLS policies from `schemas/rls_policies.sql`
5. Load seed data: `python setup.py`

### Performance Recommendations
- Enable connection pooling (default: 10 connections)
- Set up automated backups with 7-day retention
- Monitor query performance with pg_stat_statements
- Configure autovacuum for high-write tables
- Use read replicas for analytics queries

### Security Checklist
- ✅ RLS policies enabled on all tables
- ✅ Clerk authentication integration
- ✅ Environment variables secured
- ✅ Database credentials rotated
- ✅ Audit logging enabled

## 🐛 Troubleshooting

### Common Issues
1. **Migration conflicts**: Use `alembic merge` to resolve
2. **Connection pool exhaustion**: Increase `DATABASE_POOL_SIZE`
3. **Slow queries**: Run `DatabaseMaintenance.optimize_queries()`
4. **High duplicate rate**: Adjust similarity thresholds in deduplication
5. **Search relevance**: Update search vectors with `reindex_search_vectors()`

### Debug Commands
```bash
# Check database health
python app/database/setup.py --check-only

# Analyze query performance
EXPLAIN ANALYZE SELECT * FROM articles WHERE search_vector @@ plainto_tsquery('basketball');

# Monitor active connections
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

## 📝 API Integration

The database integrates seamlessly with the FastAPI backend through SQLAlchemy models that match Pydantic schemas, providing type-safe database operations with automatic validation.

For more details on API integration, see the main [FastAPI documentation](../README.md).