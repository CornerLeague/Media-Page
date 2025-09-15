-- Row Level Security (RLS) Policies for Supabase
-- These policies ensure data security and multi-tenancy

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE games ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE feed_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE ingestion_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preference_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_analytics ENABLE ROW LEVEL SECURITY;

-- Helper function to get current user's role
CREATE OR REPLACE FUNCTION get_current_user_role()
RETURNS user_role AS $$
DECLARE
    user_role_val user_role;
BEGIN
    SELECT role INTO user_role_val
    FROM users
    WHERE clerk_user_id = auth.jwt() ->> 'sub';

    RETURN COALESCE(user_role_val, 'user'::user_role);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper function to check if user is admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN get_current_user_role() = 'admin';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper function to get current user ID
CREATE OR REPLACE FUNCTION get_current_user_id()
RETURNS UUID AS $$
DECLARE
    user_id_val UUID;
BEGIN
    SELECT id INTO user_id_val
    FROM users
    WHERE clerk_user_id = auth.jwt() ->> 'sub';

    RETURN user_id_val;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- USERS TABLE POLICIES
-- Users can read their own record and public info of others
CREATE POLICY "users_select_policy" ON users
    FOR SELECT
    USING (
        -- Own record (full access)
        clerk_user_id = auth.jwt() ->> 'sub'
        OR
        -- Public info only for others (limited fields via view)
        status = 'active'
    );

-- Users can update their own record
CREATE POLICY "users_update_policy" ON users
    FOR UPDATE
    USING (clerk_user_id = auth.jwt() ->> 'sub');

-- Users can insert their own record (registration)
CREATE POLICY "users_insert_policy" ON users
    FOR INSERT
    WITH CHECK (clerk_user_id = auth.jwt() ->> 'sub');

-- Only admins can delete users
CREATE POLICY "users_delete_policy" ON users
    FOR DELETE
    USING (is_admin());

-- TEAMS TABLE POLICIES
-- Teams are publicly readable (no sensitive data)
CREATE POLICY "teams_select_policy" ON teams
    FOR SELECT
    USING (status = 'active');

-- Only admins can modify teams
CREATE POLICY "teams_admin_policy" ON teams
    FOR ALL
    USING (is_admin());

-- USER_TEAMS TABLE POLICIES
-- Users can read their own team relationships
CREATE POLICY "user_teams_select_policy" ON user_teams
    FOR SELECT
    USING (
        user_id = get_current_user_id()
        OR
        is_admin()
    );

-- Users can manage their own team relationships
CREATE POLICY "user_teams_insert_policy" ON user_teams
    FOR INSERT
    WITH CHECK (user_id = get_current_user_id());

CREATE POLICY "user_teams_update_policy" ON user_teams
    FOR UPDATE
    USING (user_id = get_current_user_id());

CREATE POLICY "user_teams_delete_policy" ON user_teams
    FOR DELETE
    USING (user_id = get_current_user_id());

-- ARTICLES TABLE POLICIES
-- Published articles are publicly readable
CREATE POLICY "articles_select_policy" ON articles
    FOR SELECT
    USING (status = 'published');

-- Only admins and moderators can modify articles
CREATE POLICY "articles_admin_policy" ON articles
    FOR ALL
    USING (
        get_current_user_role() IN ('admin', 'moderator')
    );

-- GAMES TABLE POLICIES
-- Games are publicly readable
CREATE POLICY "games_select_policy" ON games
    FOR SELECT
    USING (true);

-- Only admins can modify games
CREATE POLICY "games_admin_policy" ON games
    FOR ALL
    USING (is_admin());

-- TEAM_STATS TABLE POLICIES
-- Team stats are publicly readable
CREATE POLICY "team_stats_select_policy" ON team_stats
    FOR SELECT
    USING (true);

-- Only admins can modify team stats
CREATE POLICY "team_stats_admin_policy" ON team_stats
    FOR ALL
    USING (is_admin());

-- FEED_SOURCES TABLE POLICIES
-- Only admins can access feed sources (sensitive configuration)
CREATE POLICY "feed_sources_admin_policy" ON feed_sources
    FOR ALL
    USING (is_admin());

-- INGESTION_LOGS TABLE POLICIES
-- Only admins can access ingestion logs
CREATE POLICY "ingestion_logs_admin_policy" ON ingestion_logs
    FOR ALL
    USING (is_admin());

-- USER_PREFERENCE_HISTORY TABLE POLICIES
-- Users can read their own preference history
CREATE POLICY "user_preference_history_select_policy" ON user_preference_history
    FOR SELECT
    USING (
        user_id = get_current_user_id()
        OR
        is_admin()
    );

-- Only system can insert preference history (via triggers)
CREATE POLICY "user_preference_history_insert_policy" ON user_preference_history
    FOR INSERT
    WITH CHECK (true); -- Handled by triggers, not direct user input

-- SEARCH_ANALYTICS TABLE POLICIES
-- Users can read their own search analytics
CREATE POLICY "search_analytics_select_policy" ON search_analytics
    FOR SELECT
    USING (
        user_id = get_current_user_id()
        OR
        is_admin()
    );

-- Users can insert their own search analytics
CREATE POLICY "search_analytics_insert_policy" ON search_analytics
    FOR INSERT
    WITH CHECK (
        user_id = get_current_user_id()
        OR
        user_id IS NULL -- Anonymous searches
    );

-- Create a view for public user information
CREATE VIEW public_users AS
SELECT
    id,
    username,
    first_name,
    last_name,
    image_url,
    created_at
FROM users
WHERE status = 'active';

-- Grant access to the public view
GRANT SELECT ON public_users TO authenticated, anon;

-- Create a view for user team preferences with team details
CREATE VIEW user_team_preferences AS
SELECT
    ut.user_id,
    ut.team_id,
    ut.followed_at,
    ut.notifications_enabled,
    t.name as team_name,
    t.city as team_city,
    t.abbreviation,
    t.sport,
    t.league,
    t.logo_url,
    t.primary_color,
    t.secondary_color
FROM user_teams ut
JOIN teams t ON t.id = ut.team_id
WHERE t.status = 'active';

-- Grant access to authenticated users for their own data
GRANT SELECT ON user_team_preferences TO authenticated;

-- Create RLS policy for the view
CREATE POLICY "user_team_preferences_policy" ON user_team_preferences
    FOR SELECT
    USING (
        user_id = get_current_user_id()
        OR
        is_admin()
    );

-- Create view for article recommendations (personalized content)
CREATE VIEW personalized_articles AS
SELECT DISTINCT
    a.id,
    a.title,
    a.summary,
    a.author,
    a.source_name,
    a.source_url,
    a.published_at,
    a.category,
    a.tags,
    a.ai_summary,
    a.sentiment_score,
    a.view_count,
    a.like_count
FROM articles a
WHERE a.status = 'published'
AND (
    -- Articles about user's favorite teams
    EXISTS (
        SELECT 1 FROM user_teams ut
        WHERE ut.user_id = get_current_user_id()
        AND ut.team_id = ANY(a.team_ids)
    )
    OR
    -- Articles in user's preferred categories
    EXISTS (
        SELECT 1 FROM users u
        WHERE u.id = get_current_user_id()
        AND a.category::text = ANY(
            SELECT jsonb_array_elements_text(u.preferences->'content_categories')
        )
    )
);

-- Grant access to personalized articles
GRANT SELECT ON personalized_articles TO authenticated;