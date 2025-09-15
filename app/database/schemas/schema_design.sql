-- Corner League Media Database Schema Design
-- Optimized for Supabase with PostgreSQL
-- Includes RLS policies, indexes, and full-text search capabilities

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Custom types and enums
CREATE TYPE user_role AS ENUM ('user', 'admin', 'moderator');
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended');
CREATE TYPE team_status AS ENUM ('active', 'inactive', 'archived');
CREATE TYPE sport_type AS ENUM ('nfl', 'nba', 'mlb', 'nhl', 'mls', 'college_football', 'college_basketball');
CREATE TYPE league_type AS ENUM ('NFL', 'NBA', 'MLB', 'NHL', 'MLS', 'NCAA_FB', 'NCAA_BB');
CREATE TYPE article_status AS ENUM ('draft', 'published', 'archived', 'deleted');
CREATE TYPE content_category AS ENUM ('news', 'analysis', 'opinion', 'rumors', 'injury_report', 'trade', 'draft', 'game_recap');
CREATE TYPE game_status AS ENUM ('scheduled', 'live', 'completed', 'postponed', 'cancelled');

-- Core Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_user_id TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    username TEXT UNIQUE,
    first_name TEXT,
    last_name TEXT,
    image_url TEXT,
    role user_role NOT NULL DEFAULT 'user',
    status user_status NOT NULL DEFAULT 'active',

    -- User preferences stored as JSONB for flexibility
    preferences JSONB NOT NULL DEFAULT '{
        "theme": "light",
        "language": "en",
        "timezone": "UTC",
        "email_notifications": true,
        "push_notifications": true,
        "favorite_sports": [],
        "content_categories": [],
        "ai_summary_enabled": true
    }'::jsonb,

    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Teams Table
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id TEXT UNIQUE, -- For API integrations
    name TEXT NOT NULL,
    city TEXT,
    abbreviation TEXT NOT NULL,
    sport sport_type NOT NULL,
    league league_type NOT NULL,
    conference TEXT,
    division TEXT,
    logo_url TEXT,
    primary_color TEXT,
    secondary_color TEXT,
    status team_status NOT NULL DEFAULT 'active',
    follower_count INTEGER NOT NULL DEFAULT 0,

    -- Full-text search vector
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', COALESCE(name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(city, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(abbreviation, '')), 'A')
    ) STORED,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(name, league),
    UNIQUE(abbreviation, league)
);

-- User-Team Relationships (Many-to-Many)
CREATE TABLE user_teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    followed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notifications_enabled BOOLEAN NOT NULL DEFAULT true,

    UNIQUE(user_id, team_id)
);

-- Articles/Content Table
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url_hash TEXT NOT NULL UNIQUE, -- Primary deduplication key
    title TEXT NOT NULL,
    content TEXT,
    summary TEXT,
    author TEXT,
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    published_at TIMESTAMPTZ,

    -- Content classification
    category content_category,
    tags TEXT[] DEFAULT '{}',
    sentiment_score NUMERIC(3,2), -- -1.0 to 1.0
    readability_score INTEGER, -- 0-100

    -- Related teams (many-to-many via array for performance)
    team_ids UUID[] DEFAULT '{}',

    -- AI-generated fields
    ai_summary TEXT,
    ai_tags TEXT[] DEFAULT '{}',
    ai_category content_category,
    ai_confidence NUMERIC(3,2), -- 0.0 to 1.0

    -- Engagement metrics
    view_count INTEGER NOT NULL DEFAULT 0,
    share_count INTEGER NOT NULL DEFAULT 0,
    like_count INTEGER NOT NULL DEFAULT 0,

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(content, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(summary, '')), 'B') ||
        setweight(to_tsvector('english', array_to_string(COALESCE(tags, '{}'), ' ')), 'C')
    ) STORED,

    status article_status NOT NULL DEFAULT 'published',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Games/Matches Table
CREATE TABLE games (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id TEXT UNIQUE, -- For API integrations
    home_team_id UUID NOT NULL REFERENCES teams(id),
    away_team_id UUID NOT NULL REFERENCES teams(id),
    scheduled_at TIMESTAMPTZ NOT NULL,
    venue TEXT,
    season TEXT NOT NULL,
    week INTEGER, -- For sports with weeks

    -- Game state
    status game_status NOT NULL DEFAULT 'scheduled',
    quarter INTEGER,
    time_remaining TEXT,

    -- Scores
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    final_score JSONB, -- Store detailed scoring if needed

    -- Game statistics (flexible JSON structure)
    stats JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT different_teams CHECK (home_team_id != away_team_id)
);

-- Team Statistics Table
CREATE TABLE team_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    season TEXT NOT NULL,
    games_played INTEGER NOT NULL DEFAULT 0,
    wins INTEGER NOT NULL DEFAULT 0,
    losses INTEGER NOT NULL DEFAULT 0,
    ties INTEGER NOT NULL DEFAULT 0,
    points_for NUMERIC(8,2) DEFAULT 0,
    points_against NUMERIC(8,2) DEFAULT 0,
    win_percentage NUMERIC(4,3) GENERATED ALWAYS AS (
        CASE
            WHEN (wins + losses + ties) > 0
            THEN ROUND((wins + ties * 0.5) / (wins + losses + ties), 3)
            ELSE 0
        END
    ) STORED,

    -- Additional stats as JSONB for flexibility
    extended_stats JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(team_id, season)
);

-- Feed Sources Table (for content ingestion)
CREATE TABLE feed_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL,
    feed_type TEXT NOT NULL, -- 'rss', 'json', 'api'
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_fetched_at TIMESTAMPTZ,
    last_successful_fetch_at TIMESTAMPTZ,
    fetch_interval_minutes INTEGER NOT NULL DEFAULT 30,

    -- Configuration for the feed
    config JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Content Ingestion Log (for tracking duplicate detection)
CREATE TABLE ingestion_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES feed_sources(id),
    url_hash TEXT NOT NULL,
    source_url TEXT NOT NULL,
    ingestion_status TEXT NOT NULL, -- 'success', 'duplicate', 'error'
    error_message TEXT,
    duplicate_of UUID REFERENCES articles(id),
    similarity_score NUMERIC(3,2), -- For near-duplicate detection

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- User Preferences History (for analytics and rollback)
CREATE TABLE user_preference_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    old_preferences JSONB,
    new_preferences JSONB NOT NULL,
    changed_fields TEXT[] NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Search Analytics
CREATE TABLE search_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    query TEXT NOT NULL,
    results_count INTEGER NOT NULL,
    clicked_results UUID[], -- Array of article IDs clicked
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', query)
    ) STORED,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
-- Users table indexes
CREATE INDEX idx_users_clerk_user_id ON users(clerk_user_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status) WHERE status = 'active';
CREATE INDEX idx_users_preferences_gin ON users USING gin(preferences);

-- Teams table indexes
CREATE INDEX idx_teams_sport_league ON teams(sport, league);
CREATE INDEX idx_teams_search_vector ON teams USING gin(search_vector);
CREATE INDEX idx_teams_abbreviation ON teams(abbreviation);
CREATE INDEX idx_teams_status ON teams(status) WHERE status = 'active';

-- User-teams relationship indexes
CREATE INDEX idx_user_teams_user_id ON user_teams(user_id);
CREATE INDEX idx_user_teams_team_id ON user_teams(team_id);
CREATE INDEX idx_user_teams_followed_at ON user_teams(followed_at DESC);

-- Articles table indexes
CREATE INDEX idx_articles_url_hash ON articles(url_hash);
CREATE INDEX idx_articles_source_url ON articles(source_url);
CREATE INDEX idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX idx_articles_category ON articles(category);
CREATE INDEX idx_articles_status ON articles(status) WHERE status = 'published';
CREATE INDEX idx_articles_team_ids ON articles USING gin(team_ids);
CREATE INDEX idx_articles_tags ON articles USING gin(tags);
CREATE INDEX idx_articles_search_vector ON articles USING gin(search_vector);
CREATE INDEX idx_articles_ai_confidence ON articles(ai_confidence DESC) WHERE ai_confidence IS NOT NULL;

-- Games table indexes
CREATE INDEX idx_games_scheduled_at ON games(scheduled_at);
CREATE INDEX idx_games_teams ON games(home_team_id, away_team_id);
CREATE INDEX idx_games_season_week ON games(season, week);
CREATE INDEX idx_games_status ON games(status);

-- Team stats indexes
CREATE INDEX idx_team_stats_team_season ON team_stats(team_id, season);
CREATE INDEX idx_team_stats_win_percentage ON team_stats(win_percentage DESC);

-- Feed sources indexes
CREATE INDEX idx_feed_sources_active ON feed_sources(is_active) WHERE is_active = true;
CREATE INDEX idx_feed_sources_last_fetched ON feed_sources(last_fetched_at);

-- Ingestion logs indexes
CREATE INDEX idx_ingestion_logs_url_hash ON ingestion_logs(url_hash);
CREATE INDEX idx_ingestion_logs_status ON ingestion_logs(ingestion_status);
CREATE INDEX idx_ingestion_logs_created_at ON ingestion_logs(created_at DESC);

-- Search analytics indexes
CREATE INDEX idx_search_analytics_user_id ON search_analytics(user_id);
CREATE INDEX idx_search_analytics_created_at ON search_analytics(created_at DESC);