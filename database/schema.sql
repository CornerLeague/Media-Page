-- Corner League Media - Database Schema
-- PostgreSQL/Supabase Compatible Schema
-- Version: 1.0.0

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types and enums
CREATE TYPE content_frequency AS ENUM ('minimal', 'standard', 'comprehensive');
CREATE TYPE news_type AS ENUM ('injuries', 'trades', 'roster', 'general', 'scores', 'analysis');
CREATE TYPE game_status AS ENUM ('SCHEDULED', 'LIVE', 'FINAL', 'POSTPONED', 'CANCELLED');
CREATE TYPE game_result AS ENUM ('W', 'L', 'T');
CREATE TYPE experience_type AS ENUM ('watch_party', 'tailgate', 'viewing', 'meetup');
CREATE TYPE content_category AS ENUM ('injuries', 'trades', 'roster', 'general', 'scores', 'analysis');
CREATE TYPE ingestion_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'duplicate');

-- Base audit fields for all tables
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 1. SPORTS & LEAGUES ENTITIES
-- Sports (e.g., Basketball, Football, Baseball)
CREATE TABLE sports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    has_teams BOOLEAN NOT NULL DEFAULT true,
    icon VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Leagues (e.g., NFL, NBA, MLB)
CREATE TABLE leagues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sport_id UUID NOT NULL REFERENCES sports(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    abbreviation VARCHAR(10),
    is_active BOOLEAN NOT NULL DEFAULT true,
    season_start_month INTEGER, -- 1-12 for seasonality
    season_end_month INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(sport_id, slug)
);

-- Teams
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sport_id UUID NOT NULL REFERENCES sports(id) ON DELETE CASCADE,
    league_id UUID NOT NULL REFERENCES leagues(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    market VARCHAR(100) NOT NULL, -- City/region
    slug VARCHAR(100) NOT NULL,
    abbreviation VARCHAR(10),
    logo_url VARCHAR(500),
    primary_color VARCHAR(7), -- Hex color
    secondary_color VARCHAR(7), -- Hex color
    is_active BOOLEAN NOT NULL DEFAULT true,
    external_id VARCHAR(100), -- For API integrations
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(league_id, slug)
);

-- 2. USER MANAGEMENT
-- Users (extends Clerk authentication)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_user_id VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255),
    display_name VARCHAR(100),
    avatar_url VARCHAR(500),
    content_frequency content_frequency DEFAULT 'standard',
    is_active BOOLEAN NOT NULL DEFAULT true,
    onboarding_completed_at TIMESTAMP WITH TIME ZONE,
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Sport Preferences
CREATE TABLE user_sport_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sport_id UUID NOT NULL REFERENCES sports(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL, -- User's ranking of this sport (1 = most preferred)
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, sport_id)
);

-- User Team Preferences
CREATE TABLE user_team_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    affinity_score DECIMAL(3,2) NOT NULL DEFAULT 0.5 CHECK (affinity_score >= 0 AND affinity_score <= 1),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, team_id)
);

-- User News Type Preferences
CREATE TABLE user_news_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    news_type news_type NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT true,
    priority INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, news_type)
);

-- User Notification Settings
CREATE TABLE user_notification_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    push_enabled BOOLEAN NOT NULL DEFAULT false,
    email_enabled BOOLEAN NOT NULL DEFAULT false,
    game_reminders BOOLEAN NOT NULL DEFAULT false,
    news_alerts BOOLEAN NOT NULL DEFAULT false,
    score_updates BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- 3. GAMES & SCORES
-- Games
CREATE TABLE games (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sport_id UUID NOT NULL REFERENCES sports(id) ON DELETE CASCADE,
    league_id UUID NOT NULL REFERENCES leagues(id) ON DELETE CASCADE,
    home_team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    away_team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    status game_status NOT NULL DEFAULT 'SCHEDULED',
    period VARCHAR(20), -- Quarter, Half, Inning, etc.
    time_remaining VARCHAR(20),
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    external_id VARCHAR(100), -- For API integrations
    venue VARCHAR(255),
    season INTEGER,
    week INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Game Events (for live scoring updates)
CREATE TABLE game_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_id UUID NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- 'score', 'penalty', 'substitution', etc.
    event_time VARCHAR(20), -- Game time when event occurred
    description TEXT NOT NULL,
    team_id UUID REFERENCES teams(id), -- Team involved in event (nullable for neutral events)
    player_name VARCHAR(100),
    points_value INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. CONTENT MANAGEMENT
-- RSS Feed Sources
CREATE TABLE feed_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    url VARCHAR(1000) NOT NULL UNIQUE,
    website VARCHAR(500),
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    fetch_interval_minutes INTEGER DEFAULT 30,
    last_fetched_at TIMESTAMP WITH TIME ZONE,
    last_success_at TIMESTAMP WITH TIME ZONE,
    failure_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Feed Source to Sports/Teams mapping
CREATE TABLE feed_source_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feed_source_id UUID NOT NULL REFERENCES feed_sources(id) ON DELETE CASCADE,
    sport_id UUID REFERENCES sports(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CHECK (sport_id IS NOT NULL OR team_id IS NOT NULL)
);

-- Raw Feed Snapshots (for deduplication and parsing)
CREATE TABLE feed_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feed_source_id UUID NOT NULL REFERENCES feed_sources(id) ON DELETE CASCADE,
    url_hash VARCHAR(64) NOT NULL, -- SHA-256 hash of the article URL
    content_hash VARCHAR(64) NOT NULL, -- SHA-256 hash of content for duplicate detection
    minhash_signature BYTEA, -- MinHash signature for near-duplicate detection
    raw_content JSONB NOT NULL, -- Raw RSS/feed item data
    processed_at TIMESTAMP WITH TIME ZONE,
    status ingestion_status NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(feed_source_id, url_hash)
);

-- Articles (processed content)
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feed_snapshot_id UUID REFERENCES feed_snapshots(id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    content TEXT,
    author VARCHAR(255),
    source VARCHAR(255) NOT NULL,
    category content_category NOT NULL DEFAULT 'general',
    priority INTEGER DEFAULT 1,
    published_at TIMESTAMP WITH TIME ZONE NOT NULL,
    url VARCHAR(1000),
    image_url VARCHAR(1000),
    external_id VARCHAR(255),

    -- Content analysis fields
    word_count INTEGER,
    reading_time_minutes INTEGER,
    sentiment_score DECIMAL(3,2), -- -1 to 1

    -- Search and indexing
    search_vector TSVECTOR,

    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Article to Sports/Teams relationships
CREATE TABLE article_sports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    sport_id UUID NOT NULL REFERENCES sports(id) ON DELETE CASCADE,
    relevance_score DECIMAL(3,2) DEFAULT 0.5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(article_id, sport_id)
);

CREATE TABLE article_teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    relevance_score DECIMAL(3,2) DEFAULT 0.5,
    mentioned_players TEXT[], -- Array of player names mentioned
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(article_id, team_id)
);

-- 5. AI SUMMARIES
CREATE TABLE ai_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    sport_id UUID REFERENCES sports(id) ON DELETE CASCADE,
    summary_text TEXT NOT NULL,
    summary_type VARCHAR(50) DEFAULT 'daily', -- 'daily', 'weekly', 'game', 'team'
    source_article_ids UUID[] DEFAULT '{}', -- Array of article IDs used for summary
    confidence_score DECIMAL(3,2),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. DEPTH CHARTS & PLAYER DATA
CREATE TABLE players (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    jersey_number INTEGER,
    position VARCHAR(50),
    experience_years INTEGER,
    height VARCHAR(10), -- e.g., "6-2"
    weight INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT true,
    external_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE depth_chart_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    position VARCHAR(50) NOT NULL,
    depth_order INTEGER NOT NULL DEFAULT 1,
    week INTEGER, -- For weekly depth charts
    season INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(team_id, player_id, position, week, season)
);

-- 7. TICKETS & DEALS
CREATE TABLE ticket_providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    website VARCHAR(500),
    api_endpoint VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE ticket_deals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_id UUID NOT NULL REFERENCES ticket_providers(id) ON DELETE CASCADE,
    game_id UUID REFERENCES games(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    section VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity INTEGER,
    deal_score DECIMAL(3,2) NOT NULL DEFAULT 0.5 CHECK (deal_score >= 0 AND deal_score <= 1),
    external_url VARCHAR(1000),
    external_id VARCHAR(255),
    valid_until TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. FAN EXPERIENCES
CREATE TABLE fan_experiences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    game_id UUID REFERENCES games(id) ON DELETE CASCADE,
    sport_id UUID REFERENCES sports(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    experience_type experience_type NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    location VARCHAR(500),
    organizer VARCHAR(255),
    max_attendees INTEGER,
    current_attendees INTEGER DEFAULT 0,
    price DECIMAL(10,2),
    external_url VARCHAR(1000),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Experience Registrations
CREATE TABLE user_experience_registrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    experience_id UUID NOT NULL REFERENCES fan_experiences(id) ON DELETE CASCADE,
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'registered', -- 'registered', 'attended', 'cancelled'
    UNIQUE(user_id, experience_id)
);

-- 9. ANALYTICS & METRICS
CREATE TABLE user_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL, -- 'article_view', 'team_follow', 'game_view', etc.
    entity_type VARCHAR(50) NOT NULL, -- 'article', 'team', 'game', etc.
    entity_id UUID NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE content_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_type VARCHAR(50) NOT NULL, -- 'article', 'summary', etc.
    content_id UUID NOT NULL,
    metric_name VARCHAR(100) NOT NULL, -- 'views', 'shares', 'time_spent', etc.
    metric_value DECIMAL(15,4) NOT NULL,
    date_recorded DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(content_type, content_id, metric_name, date_recorded)
);

-- 10. INDEXES FOR PERFORMANCE

-- User-related indexes
CREATE INDEX idx_users_clerk_id ON users(clerk_user_id);
CREATE INDEX idx_users_active ON users(is_active, last_active_at);
CREATE INDEX idx_user_sport_prefs_user_rank ON user_sport_preferences(user_id, rank);
CREATE INDEX idx_user_team_prefs_user_affinity ON user_team_preferences(user_id, affinity_score DESC);

-- Sports/Teams indexes
CREATE INDEX idx_teams_sport_league ON teams(sport_id, league_id);
CREATE INDEX idx_teams_active ON teams(is_active);
CREATE INDEX idx_leagues_sport ON leagues(sport_id);

-- Games indexes
CREATE INDEX idx_games_teams ON games(home_team_id, away_team_id);
CREATE INDEX idx_games_scheduled ON games(scheduled_at);
CREATE INDEX idx_games_status ON games(status);
CREATE INDEX idx_games_sport_league ON games(sport_id, league_id);
CREATE INDEX idx_game_events_game_time ON game_events(game_id, event_time);

-- Content indexes
CREATE INDEX idx_articles_published ON articles(published_at DESC);
CREATE INDEX idx_articles_category ON articles(category);
CREATE INDEX idx_articles_active ON articles(is_active);
CREATE INDEX idx_articles_source ON articles(source);
CREATE INDEX idx_article_sports_relevance ON article_sports(sport_id, relevance_score DESC);
CREATE INDEX idx_article_teams_relevance ON article_teams(team_id, relevance_score DESC);

-- Feed processing indexes
CREATE INDEX idx_feed_snapshots_url_hash ON feed_snapshots(url_hash);
CREATE INDEX idx_feed_snapshots_content_hash ON feed_snapshots(content_hash);
CREATE INDEX idx_feed_snapshots_status ON feed_snapshots(status);
CREATE INDEX idx_feed_sources_active ON feed_sources(is_active, last_fetched_at);

-- Full-text search indexes
CREATE INDEX idx_articles_search_vector ON articles USING GIN(search_vector);
CREATE INDEX idx_articles_title_trgm ON articles USING GIN(title gin_trgm_ops);

-- Analytics indexes
CREATE INDEX idx_user_interactions_user_type ON user_interactions(user_id, interaction_type);
CREATE INDEX idx_user_interactions_entity ON user_interactions(entity_type, entity_id);
CREATE INDEX idx_content_performance_date ON content_performance(date_recorded, content_type);

-- Ticket and experience indexes
CREATE INDEX idx_ticket_deals_team_game ON ticket_deals(team_id, game_id);
CREATE INDEX idx_ticket_deals_score ON ticket_deals(deal_score DESC);
CREATE INDEX idx_fan_experiences_team_time ON fan_experiences(team_id, start_time);
CREATE INDEX idx_fan_experiences_type ON fan_experiences(experience_type);

-- 11. TRIGGERS FOR AUTOMATED UPDATES

-- Update timestamps
CREATE TRIGGER set_updated_at_sports BEFORE UPDATE ON sports FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER set_updated_at_leagues BEFORE UPDATE ON leagues FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER set_updated_at_teams BEFORE UPDATE ON teams FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER set_updated_at_users BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER set_updated_at_user_sport_preferences BEFORE UPDATE ON user_sport_preferences FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER set_updated_at_user_team_preferences BEFORE UPDATE ON user_team_preferences FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER set_updated_at_user_news_preferences BEFORE UPDATE ON user_news_preferences FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER set_updated_at_user_notification_settings BEFORE UPDATE ON user_notification_settings FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER set_updated_at_games BEFORE UPDATE ON games FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER set_updated_at_articles BEFORE UPDATE ON articles FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER set_updated_at_players BEFORE UPDATE ON players FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER set_updated_at_depth_chart_entries BEFORE UPDATE ON depth_chart_entries FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER set_updated_at_ticket_deals BEFORE UPDATE ON ticket_deals FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER set_updated_at_fan_experiences BEFORE UPDATE ON fan_experiences FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Update search vectors for articles
CREATE OR REPLACE FUNCTION update_article_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                        setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B') ||
                        setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_article_search_vector_trigger
    BEFORE INSERT OR UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_article_search_vector();

-- 12. ROW LEVEL SECURITY (RLS) POLICIES

-- Enable RLS on user-specific tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sport_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_team_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_news_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_notification_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_experience_registrations ENABLE ROW LEVEL SECURITY;

-- RLS policies for users table
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid()::text = clerk_user_id);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid()::text = clerk_user_id);

-- Similar policies for other user tables
CREATE POLICY "Users can manage own sport preferences" ON user_sport_preferences
    FOR ALL USING (user_id IN (SELECT id FROM users WHERE clerk_user_id = auth.uid()::text));

CREATE POLICY "Users can manage own team preferences" ON user_team_preferences
    FOR ALL USING (user_id IN (SELECT id FROM users WHERE clerk_user_id = auth.uid()::text));

CREATE POLICY "Users can manage own news preferences" ON user_news_preferences
    FOR ALL USING (user_id IN (SELECT id FROM users WHERE clerk_user_id = auth.uid()::text));

CREATE POLICY "Users can manage own notification settings" ON user_notification_settings
    FOR ALL USING (user_id IN (SELECT id FROM users WHERE clerk_user_id = auth.uid()::text));

-- Read-only access for public content
CREATE POLICY "Public content readable" ON sports FOR SELECT USING (is_active = true);
CREATE POLICY "Public content readable" ON leagues FOR SELECT USING (is_active = true);
CREATE POLICY "Public content readable" ON teams FOR SELECT USING (is_active = true);
CREATE POLICY "Public content readable" ON articles FOR SELECT USING (is_active = true);
CREATE POLICY "Public content readable" ON games FOR SELECT USING (true);

-- 13. UTILITY FUNCTIONS

-- Function to calculate deal scores based on price and market data
CREATE OR REPLACE FUNCTION calculate_deal_score(
    price DECIMAL,
    average_price DECIMAL,
    market_demand DECIMAL DEFAULT 0.5
) RETURNS DECIMAL AS $$
BEGIN
    -- Simple deal score calculation: lower price = higher score
    -- With market demand adjustment
    RETURN GREATEST(0, LEAST(1, (1 - (price / NULLIF(average_price, 0))) * (1 + market_demand)));
END;
$$ LANGUAGE plpgsql;

-- Function to get user's most preferred team
CREATE OR REPLACE FUNCTION get_user_primary_team(user_uuid UUID)
RETURNS UUID AS $$
DECLARE
    primary_team_id UUID;
BEGIN
    SELECT team_id INTO primary_team_id
    FROM user_team_preferences
    WHERE user_id = user_uuid
    ORDER BY affinity_score DESC
    LIMIT 1;

    RETURN primary_team_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get personalized content for user
CREATE OR REPLACE FUNCTION get_personalized_articles(
    user_uuid UUID,
    limit_count INTEGER DEFAULT 20
) RETURNS TABLE (
    article_id UUID,
    title VARCHAR,
    summary TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    relevance_score DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        a.id,
        a.title,
        a.summary,
        a.published_at,
        GREATEST(
            COALESCE(ast.relevance_score, 0) * usp.rank::DECIMAL / 10,
            COALESCE(at.relevance_score, 0) * utp.affinity_score
        ) as relevance_score
    FROM articles a
    LEFT JOIN article_sports ast ON a.id = ast.article_id
    LEFT JOIN user_sport_preferences usp ON ast.sport_id = usp.sport_id AND usp.user_id = user_uuid
    LEFT JOIN article_teams at ON a.id = at.article_id
    LEFT JOIN user_team_preferences utp ON at.team_id = utp.team_id AND utp.user_id = user_uuid
    WHERE a.is_active = true
    AND (usp.user_id IS NOT NULL OR utp.user_id IS NOT NULL)
    ORDER BY relevance_score DESC, a.published_at DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- 14. INITIAL DATA CONSTRAINTS

-- Ensure we have logical constraints
ALTER TABLE user_sport_preferences ADD CONSTRAINT valid_rank CHECK (rank > 0);
ALTER TABLE user_news_preferences ADD CONSTRAINT valid_priority CHECK (priority > 0);
ALTER TABLE articles ADD CONSTRAINT valid_word_count CHECK (word_count >= 0);
ALTER TABLE articles ADD CONSTRAINT valid_reading_time CHECK (reading_time_minutes >= 0);
ALTER TABLE depth_chart_entries ADD CONSTRAINT valid_depth_order CHECK (depth_order > 0);
ALTER TABLE fan_experiences ADD CONSTRAINT valid_attendee_count CHECK (current_attendees <= max_attendees);
ALTER TABLE ticket_deals ADD CONSTRAINT valid_price CHECK (price >= 0);
ALTER TABLE ticket_deals ADD CONSTRAINT valid_quantity CHECK (quantity > 0);

-- Performance hint: Analyze tables after initial data load
-- ANALYZE;

COMMENT ON DATABASE current_database() IS 'Corner League Media - Sports Platform Database';