-- =================================================================
-- Corner League Media - Development Seed Data
-- =================================================================
-- This script populates the database with sample data for development
-- Only run in development environments - NOT in production!
-- =================================================================

-- Check if we're in development environment
DO $$
BEGIN
    IF current_setting('application_name', true) = 'production' THEN
        RAISE EXCEPTION 'This seed script should not be run in production!';
    END IF;
END
$$;

-- =================================================================
-- SPORTS AND LEAGUES SEED DATA
-- =================================================================

-- Insert major sports leagues
INSERT INTO sports (id, name, display_name, description, sport_type, color_primary, color_secondary) VALUES
    ('11111111-1111-1111-1111-111111111111', 'nfl', 'NFL', 'National Football League', 'professional', '#013369', '#D50A0A'),
    ('22222222-2222-2222-2222-222222222222', 'nba', 'NBA', 'National Basketball Association', 'professional', '#C8102E', '#1D428A'),
    ('33333333-3333-3333-3333-333333333333', 'mlb', 'MLB', 'Major League Baseball', 'professional', '#132448', '#C4CED4'),
    ('44444444-4444-4444-4444-444444444444', 'nhl', 'NHL', 'National Hockey League', 'professional', '#000000', '#C8102E'),
    ('55555555-5555-5555-5555-555555555555', 'college_football', 'College Football', 'NCAA Division I Football', 'college', '#FF6B35', '#004225'),
    ('66666666-6666-6666-6666-666666666666', 'college_basketball', 'College Basketball', 'NCAA Division I Basketball', 'college', '#FF6B35', '#004225')
ON CONFLICT (name) DO NOTHING;

-- =================================================================
-- NFL TEAMS SEED DATA
-- =================================================================

INSERT INTO teams (id, sport_id, name, display_name, city, state, abbreviation, conference, division, color_primary, color_secondary) VALUES
    -- AFC East
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', 'buffalo_bills', 'Buffalo Bills', 'Buffalo', 'New York', 'BUF', 'AFC', 'East', '#00338D', '#C60C30'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaab', '11111111-1111-1111-1111-111111111111', 'miami_dolphins', 'Miami Dolphins', 'Miami', 'Florida', 'MIA', 'AFC', 'East', '#008E97', '#FC4C02'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaac', '11111111-1111-1111-1111-111111111111', 'new_england_patriots', 'New England Patriots', 'Foxborough', 'Massachusetts', 'NE', 'AFC', 'East', '#002244', '#C60C30'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaad', '11111111-1111-1111-1111-111111111111', 'new_york_jets', 'New York Jets', 'East Rutherford', 'New Jersey', 'NYJ', 'AFC', 'East', '#125740', '#000000'),

    -- AFC North
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaae', '11111111-1111-1111-1111-111111111111', 'baltimore_ravens', 'Baltimore Ravens', 'Baltimore', 'Maryland', 'BAL', 'AFC', 'North', '#241773', '#000000'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaf', '11111111-1111-1111-1111-111111111111', 'cincinnati_bengals', 'Cincinnati Bengals', 'Cincinnati', 'Ohio', 'CIN', 'AFC', 'North', '#FB4F14', '#000000'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaag0', '11111111-1111-1111-1111-111111111111', 'cleveland_browns', 'Cleveland Browns', 'Cleveland', 'Ohio', 'CLE', 'AFC', 'North', '#311D00', '#FF3C00'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaag1', '11111111-1111-1111-1111-111111111111', 'pittsburgh_steelers', 'Pittsburgh Steelers', 'Pittsburgh', 'Pennsylvania', 'PIT', 'AFC', 'North', '#FFB612', '#101820'),

    -- NFC East
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbba', '11111111-1111-1111-1111-111111111111', 'dallas_cowboys', 'Dallas Cowboys', 'Arlington', 'Texas', 'DAL', 'NFC', 'East', '#003594', '#869397'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '11111111-1111-1111-1111-111111111111', 'new_york_giants', 'New York Giants', 'East Rutherford', 'New Jersey', 'NYG', 'NFC', 'East', '#0B2265', '#A71930'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbc', '11111111-1111-1111-1111-111111111111', 'philadelphia_eagles', 'Philadelphia Eagles', 'Philadelphia', 'Pennsylvania', 'PHI', 'NFC', 'East', '#004C54', '#A5ACAF'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbd', '11111111-1111-1111-1111-111111111111', 'washington_commanders', 'Washington Commanders', 'Landover', 'Maryland', 'WAS', 'NFC', 'East', '#5A1414', '#FFB612')
ON CONFLICT (sport_id, name) DO NOTHING;

-- =================================================================
-- NBA TEAMS SEED DATA (Sample)
-- =================================================================

INSERT INTO teams (id, sport_id, name, display_name, city, state, abbreviation, conference, division, color_primary, color_secondary) VALUES
    ('cccccccc-cccc-cccc-cccc-ccccccccccca', '22222222-2222-2222-2222-222222222222', 'los_angeles_lakers', 'Los Angeles Lakers', 'Los Angeles', 'California', 'LAL', 'Western', 'Pacific', '#552583', '#FDB927'),
    ('cccccccc-cccc-cccc-cccc-ccccccccccbb', '22222222-2222-2222-2222-222222222222', 'boston_celtics', 'Boston Celtics', 'Boston', 'Massachusetts', 'BOS', 'Eastern', 'Atlantic', '#007A33', '#BA9653'),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', '22222222-2222-2222-2222-222222222222', 'golden_state_warriors', 'Golden State Warriors', 'San Francisco', 'California', 'GSW', 'Western', 'Pacific', '#1D428A', '#FFC72C'),
    ('cccccccc-cccc-cccc-cccc-cccccccccccd', '22222222-2222-2222-2222-222222222222', 'miami_heat', 'Miami Heat', 'Miami', 'Florida', 'MIA', 'Eastern', 'Southeast', '#98002E', '#F9A01B')
ON CONFLICT (sport_id, name) DO NOTHING;

-- =================================================================
-- CONTENT SOURCES SEED DATA
-- =================================================================

INSERT INTO content_sources (id, name, display_name, base_url, reliability_score) VALUES
    ('dddddddd-dddd-dddd-dddd-ddddddddddda', 'espn', 'ESPN', 'https://espn.com', 95),
    ('dddddddd-dddd-dddd-dddd-dddddddddddb', 'nbc_sports', 'NBC Sports', 'https://nbcsports.com', 90),
    ('dddddddd-dddd-dddd-dddd-dddddddddddc', 'fox_sports', 'FOX Sports', 'https://foxsports.com', 88),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'cbs_sports', 'CBS Sports', 'https://cbssports.com', 87),
    ('dddddddd-dddd-dddd-dddd-ddddddddddde', 'bleacher_report', 'Bleacher Report', 'https://bleacherreport.com', 75),
    ('dddddddd-dddd-dddd-dddd-dddddddddddf', 'the_athletic', 'The Athletic', 'https://theathletic.com', 92)
ON CONFLICT (name) DO NOTHING;

-- =================================================================
-- SAMPLE CONTENT ARTICLES
-- =================================================================

INSERT INTO content_articles (
    id, source_id, title, summary, content, url, author, published_at,
    content_type, category, tags, team_ids, sport_ids, ai_summary, ai_sentiment
) VALUES
    (
        'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeea',
        'dddddddd-dddd-dddd-dddd-ddddddddddda',
        'Cowboys Prepare for Crucial Division Matchup',
        'Dallas Cowboys gear up for an important NFC East showdown this weekend.',
        'The Dallas Cowboys are making final preparations for what could be a season-defining game against their division rivals. With playoff implications on the line, both teams are expected to bring their best effort to the field.',
        'https://espn.com/nfl/story/_/id/12345/cowboys-prepare-crucial-division-matchup',
        'John Smith',
        CURRENT_TIMESTAMP - INTERVAL '2 hours',
        'article',
        'news',
        ARRAY['NFL', 'Cowboys', 'NFC East', 'playoffs'],
        ARRAY['bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbba'],
        ARRAY['11111111-1111-1111-1111-111111111111'],
        'Cowboys preparing for important division game with playoff implications.',
        'neutral'
    ),
    (
        'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeeb',
        'dddddddd-dddd-dddd-dddd-dddddddddddb',
        'Lakers Trade Rumors Heat Up Before Deadline',
        'Los Angeles Lakers reportedly exploring multiple trade options.',
        'As the trade deadline approaches, the Los Angeles Lakers front office is actively pursuing several deals that could reshape their roster for a playoff push. Sources close to the team indicate multiple scenarios are being evaluated.',
        'https://nbcsports.com/nba/news/lakers-trade-rumors-heat-up-before-deadline',
        'Sarah Johnson',
        CURRENT_TIMESTAMP - INTERVAL '5 hours',
        'article',
        'analysis',
        ARRAY['NBA', 'Lakers', 'trades', 'deadline'],
        ARRAY['cccccccc-cccc-cccc-cccc-ccccccccccca'],
        ARRAY['22222222-2222-2222-2222-222222222222'],
        'Lakers exploring trade options before deadline for playoff push.',
        'neutral'
    ),
    (
        'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeec',
        'dddddddd-dddd-dddd-dddd-dddddddddddc',
        'Top 10 Plays of the Week: NFL Edition',
        'Countdown of the most spectacular plays from this week in the NFL.',
        'From incredible touchdown catches to game-saving defensive plays, this week delivered some truly memorable moments. Our analysts break down the top 10 plays that had fans on their feet.',
        'https://foxsports.com/nfl/gallery/top-10-plays-week-nfl-edition',
        'Mike Rodriguez',
        CURRENT_TIMESTAMP - INTERVAL '1 day',
        'video',
        'highlights',
        ARRAY['NFL', 'highlights', 'top plays', 'weekly'],
        ARRAY[],
        ARRAY['11111111-1111-1111-1111-111111111111'],
        'Weekly countdown of spectacular NFL plays and highlights.',
        'positive'
    )
ON CONFLICT (url) DO NOTHING;

-- =================================================================
-- SAMPLE GAMES SCHEDULE
-- =================================================================

INSERT INTO games (
    id, sport_id, home_team_id, away_team_id, scheduled_at, season, week,
    game_type, status, venue
) VALUES
    (
        'ffffffff-ffff-ffff-ffff-fffffffffff1',
        '11111111-1111-1111-1111-111111111111',
        'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbba', -- Cowboys
        'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbc', -- Eagles
        CURRENT_TIMESTAMP + INTERVAL '3 days',
        2024,
        15,
        'regular',
        'scheduled',
        'AT&T Stadium'
    ),
    (
        'ffffffff-ffff-ffff-ffff-fffffffffff2',
        '22222222-2222-2222-2222-222222222222',
        'cccccccc-cccc-cccc-cccc-ccccccccccca', -- Lakers
        'cccccccc-cccc-cccc-cccc-ccccccccccbb', -- Celtics
        CURRENT_TIMESTAMP + INTERVAL '1 day',
        2024,
        NULL,
        'regular',
        'scheduled',
        'Crypto.com Arena'
    ),
    (
        'ffffffff-ffff-ffff-ffff-fffffffffff3',
        '11111111-1111-1111-1111-111111111111',
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', -- Bills
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaab', -- Dolphins
        CURRENT_TIMESTAMP - INTERVAL '2 days',
        2024,
        14,
        'regular',
        'completed',
        'Highmark Stadium'
    )
ON CONFLICT DO NOTHING;

-- Update the completed game with final scores
UPDATE games
SET home_score = 31, away_score = 17,
    actual_start_time = scheduled_at,
    actual_end_time = scheduled_at + INTERVAL '3 hours'
WHERE id = 'ffffffff-ffff-ffff-ffff-fffffffffff3';

-- =================================================================
-- SAMPLE USER DATA (for testing)
-- =================================================================

-- Insert a test user (use your Clerk user ID here if testing)
INSERT INTO users (
    id, clerk_user_id, email, username, first_name, last_name, is_verified
) VALUES (
    '99999999-9999-9999-9999-999999999999',
    'user_test123456789',
    'test@cornerleague.com',
    'testuser',
    'Test',
    'User',
    true
) ON CONFLICT (clerk_user_id) DO NOTHING;

-- Insert user preferences for test user
INSERT INTO user_preferences (
    user_id, favorite_teams, favorite_sports, theme_preference
) VALUES (
    '99999999-9999-9999-9999-999999999999',
    ARRAY['bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbba', 'cccccccc-cccc-cccc-cccc-ccccccccccca'], -- Cowboys, Lakers
    ARRAY['11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222'], -- NFL, NBA
    'dark'
) ON CONFLICT (user_id) DO NOTHING;

-- Insert some team follows for test user
INSERT INTO user_team_follows (user_id, team_id) VALUES
    ('99999999-9999-9999-9999-999999999999', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbba'), -- Cowboys
    ('99999999-9999-9999-9999-999999999999', 'cccccccc-cccc-cccc-cccc-ccccccccccca')  -- Lakers
ON CONFLICT (user_id, team_id) DO NOTHING;

-- =================================================================
-- UPDATE STATISTICS
-- =================================================================

-- Update table statistics for better query planning
ANALYZE users;
ANALYZE user_preferences;
ANALYZE sports;
ANALYZE teams;
ANALYZE content_sources;
ANALYZE content_articles;
ANALYZE games;
ANALYZE user_article_interactions;
ANALYZE user_team_follows;
ANALYZE content_search_index;