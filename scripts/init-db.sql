-- =================================================================
-- Corner League Media - Database Initialization Script
-- =================================================================
-- This script sets up the initial database schema for development
-- and creates necessary extensions and configurations
-- =================================================================

-- Enable necessary PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create test database for running tests
SELECT 'CREATE DATABASE sportsdb_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'sportsdb_test')\gexec

-- Connect to main database
\c sportsdb;

-- Enable extensions in main database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- =================================================================
-- USERS AND AUTHENTICATION TABLES
-- =================================================================

-- Users table with Clerk integration
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    profile_image_url TEXT,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- User preferences and settings
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    favorite_teams TEXT[] DEFAULT '{}',
    favorite_sports TEXT[] DEFAULT '{}',
    notification_settings JSONB DEFAULT '{}',
    theme_preference VARCHAR(20) DEFAULT 'light',
    language_preference VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- =================================================================
-- SPORTS AND TEAMS TABLES
-- =================================================================

-- Sports/Leagues table
CREATE TABLE IF NOT EXISTS sports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    sport_type VARCHAR(50) NOT NULL, -- 'professional', 'college', 'international'
    is_active BOOLEAN DEFAULT true,
    logo_url TEXT,
    color_primary VARCHAR(7), -- hex color
    color_secondary VARCHAR(7), -- hex color
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sport_id UUID NOT NULL REFERENCES sports(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(100) DEFAULT 'United States',
    abbreviation VARCHAR(10),
    logo_url TEXT,
    color_primary VARCHAR(7), -- hex color
    color_secondary VARCHAR(7), -- hex color
    home_venue VARCHAR(200),
    conference VARCHAR(100),
    division VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sport_id, name)
);

-- =================================================================
-- CONTENT AND MEDIA TABLES
-- =================================================================

-- Content sources (ESPN, NBC Sports, etc.)
CREATE TABLE IF NOT EXISTS content_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    base_url TEXT NOT NULL,
    logo_url TEXT,
    reliability_score INTEGER DEFAULT 50 CHECK (reliability_score >= 0 AND reliability_score <= 100),
    is_active BOOLEAN DEFAULT true,
    api_config JSONB DEFAULT '{}',
    scraping_config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Content articles and posts
CREATE TABLE IF NOT EXISTS content_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID NOT NULL REFERENCES content_sources(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    content TEXT,
    url TEXT UNIQUE NOT NULL,
    author VARCHAR(200),
    published_at TIMESTAMP WITH TIME ZONE,
    content_type VARCHAR(50) NOT NULL DEFAULT 'article', -- 'article', 'video', 'podcast', 'social'
    category VARCHAR(100), -- 'news', 'analysis', 'highlights', 'injury_report'
    tags TEXT[] DEFAULT '{}',
    team_ids UUID[] DEFAULT '{}',
    sport_ids UUID[] DEFAULT '{}',
    image_url TEXT,
    video_url TEXT,
    reading_time_minutes INTEGER,
    engagement_score INTEGER DEFAULT 0,
    ai_summary TEXT,
    ai_sentiment VARCHAR(20), -- 'positive', 'negative', 'neutral'
    ai_topics TEXT[] DEFAULT '{}',
    is_featured BOOLEAN DEFAULT false,
    is_trending BOOLEAN DEFAULT false,
    is_published BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =================================================================
-- GAMES AND SCORES TABLES
-- =================================================================

-- Games and matchups
CREATE TABLE IF NOT EXISTS games (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sport_id UUID NOT NULL REFERENCES sports(id) ON DELETE CASCADE,
    home_team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    away_team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    actual_start_time TIMESTAMP WITH TIME ZONE,
    actual_end_time TIMESTAMP WITH TIME ZONE,
    season INTEGER NOT NULL,
    week INTEGER,
    game_type VARCHAR(50) DEFAULT 'regular', -- 'preseason', 'regular', 'playoff', 'championship'
    status VARCHAR(50) DEFAULT 'scheduled', -- 'scheduled', 'live', 'completed', 'postponed', 'cancelled'
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    venue VARCHAR(200),
    weather_conditions TEXT,
    attendance INTEGER,
    broadcast_networks TEXT[] DEFAULT '{}',
    odds JSONB DEFAULT '{}', -- betting odds and lines
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =================================================================
-- USER ENGAGEMENT TABLES
-- =================================================================

-- User reading history
CREATE TABLE IF NOT EXISTS user_article_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    article_id UUID NOT NULL REFERENCES content_articles(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL, -- 'view', 'like', 'share', 'bookmark', 'comment'
    interaction_value INTEGER DEFAULT 1, -- for tracking intensity (time spent, etc.)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, article_id, interaction_type)
);

-- User team following
CREATE TABLE IF NOT EXISTS user_team_follows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    notification_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, team_id)
);

-- =================================================================
-- SEARCH AND RECOMMENDATIONS TABLES
-- =================================================================

-- Content search index (for full-text search)
CREATE TABLE IF NOT EXISTS content_search_index (
    article_id UUID PRIMARY KEY REFERENCES content_articles(id) ON DELETE CASCADE,
    search_vector tsvector,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User recommendation scores
CREATE TABLE IF NOT EXISTS user_content_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    article_id UUID NOT NULL REFERENCES content_articles(id) ON DELETE CASCADE,
    recommendation_score FLOAT NOT NULL,
    recommendation_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, article_id)
);

-- =================================================================
-- INDEXES FOR PERFORMANCE
-- =================================================================

-- User indexes
CREATE INDEX IF NOT EXISTS idx_users_clerk_user_id ON users(clerk_user_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Content indexes
CREATE INDEX IF NOT EXISTS idx_content_articles_source_id ON content_articles(source_id);
CREATE INDEX IF NOT EXISTS idx_content_articles_published_at ON content_articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_content_articles_content_type ON content_articles(content_type);
CREATE INDEX IF NOT EXISTS idx_content_articles_is_featured ON content_articles(is_featured) WHERE is_featured = true;
CREATE INDEX IF NOT EXISTS idx_content_articles_is_trending ON content_articles(is_trending) WHERE is_trending = true;
CREATE INDEX IF NOT EXISTS idx_content_articles_team_ids ON content_articles USING GIN(team_ids);
CREATE INDEX IF NOT EXISTS idx_content_articles_sport_ids ON content_articles USING GIN(sport_ids);
CREATE INDEX IF NOT EXISTS idx_content_articles_tags ON content_articles USING GIN(tags);

-- Search indexes
CREATE INDEX IF NOT EXISTS idx_content_search_vector ON content_search_index USING GIN(search_vector);

-- Games indexes
CREATE INDEX IF NOT EXISTS idx_games_sport_id ON games(sport_id);
CREATE INDEX IF NOT EXISTS idx_games_home_team_id ON games(home_team_id);
CREATE INDEX IF NOT EXISTS idx_games_away_team_id ON games(away_team_id);
CREATE INDEX IF NOT EXISTS idx_games_scheduled_at ON games(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_games_status ON games(status);
CREATE INDEX IF NOT EXISTS idx_games_season ON games(season);

-- User interaction indexes
CREATE INDEX IF NOT EXISTS idx_user_article_interactions_user_id ON user_article_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_article_interactions_article_id ON user_article_interactions(article_id);
CREATE INDEX IF NOT EXISTS idx_user_article_interactions_created_at ON user_article_interactions(created_at);
CREATE INDEX IF NOT EXISTS idx_user_team_follows_user_id ON user_team_follows(user_id);
CREATE INDEX IF NOT EXISTS idx_user_team_follows_team_id ON user_team_follows(team_id);

-- =================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sports_updated_at BEFORE UPDATE ON sports FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_content_sources_updated_at BEFORE UPDATE ON content_sources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_content_articles_updated_at BEFORE UPDATE ON content_articles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_games_updated_at BEFORE UPDATE ON games FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update search index when article is updated
CREATE OR REPLACE FUNCTION update_content_search_index()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO content_search_index (article_id, search_vector)
    VALUES (
        NEW.id,
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'C') ||
        setweight(to_tsvector('english', array_to_string(NEW.tags, ' ')), 'D')
    )
    ON CONFLICT (article_id)
    DO UPDATE SET
        search_vector = setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                       setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B') ||
                       setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'C') ||
                       setweight(to_tsvector('english', array_to_string(NEW.tags, ' ')), 'D'),
        updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for search index updates
CREATE TRIGGER update_content_search_index_trigger
    AFTER INSERT OR UPDATE OF title, summary, content, tags ON content_articles
    FOR EACH ROW EXECUTE FUNCTION update_content_search_index();

-- =================================================================
-- GRANT PERMISSIONS
-- =================================================================

-- Grant all necessary permissions to the postgres user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO postgres;