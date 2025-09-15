"""Initial database schema for Corner League Media

Revision ID: 001
Revises:
Create Date: 2025-09-14 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply initial schema migration."""

    # Enable required extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"pg_trgm\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"unaccent\"")

    # Create custom enum types
    user_role_enum = sa.Enum('user', 'admin', 'moderator', name='user_role')
    user_status_enum = sa.Enum('active', 'inactive', 'suspended', name='user_status')
    team_status_enum = sa.Enum('active', 'inactive', 'archived', name='team_status')
    sport_type_enum = sa.Enum('nfl', 'nba', 'mlb', 'nhl', 'mls', 'college_football', 'college_basketball', name='sport_type')
    league_type_enum = sa.Enum('NFL', 'NBA', 'MLB', 'NHL', 'MLS', 'NCAA_FB', 'NCAA_BB', name='league_type')
    article_status_enum = sa.Enum('draft', 'published', 'archived', 'deleted', name='article_status')
    content_category_enum = sa.Enum('news', 'analysis', 'opinion', 'rumors', 'injury_report', 'trade', 'draft', 'game_recap', name='content_category')
    game_status_enum = sa.Enum('scheduled', 'live', 'completed', 'postponed', 'cancelled', name='game_status')

    # Create enum types
    user_role_enum.create(op.get_bind())
    user_status_enum.create(op.get_bind())
    team_status_enum.create(op.get_bind())
    sport_type_enum.create(op.get_bind())
    league_type_enum.create(op.get_bind())
    article_status_enum.create(op.get_bind())
    content_category_enum.create(op.get_bind())
    game_status_enum.create(op.get_bind())

    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('clerk_user_id', sa.Text(), nullable=False),
        sa.Column('email', sa.Text(), nullable=False),
        sa.Column('username', sa.Text(), nullable=True),
        sa.Column('first_name', sa.Text(), nullable=True),
        sa.Column('last_name', sa.Text(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('role', user_role_enum, nullable=False, server_default='user'),
        sa.Column('status', user_status_enum, nullable=False, server_default='active'),
        sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=False,
                 server_default=sa.text("'{\"theme\": \"light\", \"language\": \"en\", \"timezone\": \"UTC\", \"email_notifications\": true, \"push_notifications\": true, \"favorite_sports\": [], \"content_categories\": [], \"ai_summary_enabled\": true}'::jsonb")),
        sa.Column('last_login', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('clerk_user_id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    # Create teams table
    op.create_table('teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('external_id', sa.Text(), nullable=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('city', sa.Text(), nullable=True),
        sa.Column('abbreviation', sa.Text(), nullable=False),
        sa.Column('sport', sport_type_enum, nullable=False),
        sa.Column('league', league_type_enum, nullable=False),
        sa.Column('conference', sa.Text(), nullable=True),
        sa.Column('division', sa.Text(), nullable=True),
        sa.Column('logo_url', sa.Text(), nullable=True),
        sa.Column('primary_color', sa.Text(), nullable=True),
        sa.Column('secondary_color', sa.Text(), nullable=True),
        sa.Column('status', team_status_enum, nullable=False, server_default='active'),
        sa.Column('follower_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id'),
        sa.UniqueConstraint('name', 'league'),
        sa.UniqueConstraint('abbreviation', 'league')
    )

    # Add search vector to teams (computed column)
    op.execute("""
        ALTER TABLE teams ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            setweight(to_tsvector('english', COALESCE(name, '')), 'A') ||
            setweight(to_tsvector('english', COALESCE(city, '')), 'B') ||
            setweight(to_tsvector('english', COALESCE(abbreviation, '')), 'A')
        ) STORED
    """)

    # Create user_teams junction table
    op.create_table('user_teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('followed_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'team_id')
    )

    # Create articles table
    op.create_table('articles',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('url_hash', sa.Text(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('author', sa.Text(), nullable=True),
        sa.Column('source_name', sa.Text(), nullable=False),
        sa.Column('source_url', sa.Text(), nullable=False),
        sa.Column('published_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('category', content_category_enum, nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.Text()), nullable=True, server_default="'{}'"),
        sa.Column('sentiment_score', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('readability_score', sa.Integer(), nullable=True),
        sa.Column('team_ids', postgresql.ARRAY(postgresql.UUID()), nullable=True, server_default="'{}'"),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('ai_tags', postgresql.ARRAY(sa.Text()), nullable=True, server_default="'{}'"),
        sa.Column('ai_category', content_category_enum, nullable=True),
        sa.Column('ai_confidence', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('share_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('like_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', article_status_enum, nullable=False, server_default='published'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url_hash'),
        sa.UniqueConstraint('source_url')
    )

    # Add search vector to articles (computed column)
    op.execute("""
        ALTER TABLE articles ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
            setweight(to_tsvector('english', COALESCE(content, '')), 'B') ||
            setweight(to_tsvector('english', COALESCE(summary, '')), 'B') ||
            setweight(to_tsvector('english', array_to_string(COALESCE(tags, '{}'), ' ')), 'C')
        ) STORED
    """)

    # Create games table
    op.create_table('games',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('external_id', sa.Text(), nullable=True),
        sa.Column('home_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('away_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scheduled_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('venue', sa.Text(), nullable=True),
        sa.Column('season', sa.Text(), nullable=False),
        sa.Column('week', sa.Integer(), nullable=True),
        sa.Column('status', game_status_enum, nullable=False, server_default='scheduled'),
        sa.Column('quarter', sa.Integer(), nullable=True),
        sa.Column('time_remaining', sa.Text(), nullable=True),
        sa.Column('home_score', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('away_score', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('final_score', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('stats', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default="'{}'"),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['away_team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['home_team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id'),
        sa.CheckConstraint('home_team_id != away_team_id', name='different_teams')
    )

    # Create team_stats table
    op.create_table('team_stats',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('season', sa.Text(), nullable=False),
        sa.Column('games_played', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('wins', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('losses', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ties', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('points_for', sa.Numeric(precision=8, scale=2), nullable=True, server_default='0'),
        sa.Column('points_against', sa.Numeric(precision=8, scale=2), nullable=True, server_default='0'),
        sa.Column('extended_stats', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default="'{}'"),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', 'season')
    )

    # Add computed win_percentage column
    op.execute("""
        ALTER TABLE team_stats ADD COLUMN win_percentage numeric(4,3)
        GENERATED ALWAYS AS (
            CASE
                WHEN (wins + losses + ties) > 0
                THEN ROUND((wins + ties * 0.5) / (wins + losses + ties), 3)
                ELSE 0
            END
        ) STORED
    """)

    # Create feed_sources table
    op.create_table('feed_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('feed_type', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_fetched_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('last_successful_fetch_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('fetch_interval_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default="'{}'"),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create ingestion_logs table
    op.create_table('ingestion_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('url_hash', sa.Text(), nullable=False),
        sa.Column('source_url', sa.Text(), nullable=False),
        sa.Column('ingestion_status', sa.Text(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('duplicate_of', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('similarity_score', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['duplicate_of'], ['articles.id'], ),
        sa.ForeignKeyConstraint(['source_id'], ['feed_sources.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_preference_history table
    op.create_table('user_preference_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('old_preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('changed_fields', postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create search_analytics table
    op.create_table('search_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('results_count', sa.Integer(), nullable=False),
        sa.Column('clicked_results', postgresql.ARRAY(postgresql.UUID()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Add search vector to search_analytics (computed column)
    op.execute("""
        ALTER TABLE search_analytics ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            to_tsvector('english', query)
        ) STORED
    """)

    # Create all indexes for performance
    create_indexes()


def create_indexes():
    """Create all performance indexes."""

    # Users table indexes
    op.create_index('idx_users_clerk_user_id', 'users', ['clerk_user_id'])
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_status', 'users', ['status'],
                   postgresql_where=sa.text("status = 'active'"))
    op.create_index('idx_users_preferences_gin', 'users', ['preferences'],
                   postgresql_using='gin')

    # Teams table indexes
    op.create_index('idx_teams_sport_league', 'teams', ['sport', 'league'])
    op.create_index('idx_teams_search_vector', 'teams', ['search_vector'],
                   postgresql_using='gin')
    op.create_index('idx_teams_abbreviation', 'teams', ['abbreviation'])
    op.create_index('idx_teams_status', 'teams', ['status'],
                   postgresql_where=sa.text("status = 'active'"))

    # User-teams relationship indexes
    op.create_index('idx_user_teams_user_id', 'user_teams', ['user_id'])
    op.create_index('idx_user_teams_team_id', 'user_teams', ['team_id'])
    op.create_index('idx_user_teams_followed_at', 'user_teams', [sa.text('followed_at DESC')])

    # Articles table indexes
    op.create_index('idx_articles_url_hash', 'articles', ['url_hash'])
    op.create_index('idx_articles_source_url', 'articles', ['source_url'])
    op.create_index('idx_articles_published_at', 'articles', [sa.text('published_at DESC')])
    op.create_index('idx_articles_category', 'articles', ['category'])
    op.create_index('idx_articles_status', 'articles', ['status'],
                   postgresql_where=sa.text("status = 'published'"))
    op.create_index('idx_articles_team_ids', 'articles', ['team_ids'],
                   postgresql_using='gin')
    op.create_index('idx_articles_tags', 'articles', ['tags'],
                   postgresql_using='gin')
    op.create_index('idx_articles_search_vector', 'articles', ['search_vector'],
                   postgresql_using='gin')
    op.create_index('idx_articles_ai_confidence', 'articles', [sa.text('ai_confidence DESC')],
                   postgresql_where=sa.text("ai_confidence IS NOT NULL"))

    # Games table indexes
    op.create_index('idx_games_scheduled_at', 'games', ['scheduled_at'])
    op.create_index('idx_games_teams', 'games', ['home_team_id', 'away_team_id'])
    op.create_index('idx_games_season_week', 'games', ['season', 'week'])
    op.create_index('idx_games_status', 'games', ['status'])

    # Team stats indexes
    op.create_index('idx_team_stats_team_season', 'team_stats', ['team_id', 'season'])
    op.create_index('idx_team_stats_win_percentage', 'team_stats', [sa.text('win_percentage DESC')])

    # Feed sources indexes
    op.create_index('idx_feed_sources_active', 'feed_sources', ['is_active'],
                   postgresql_where=sa.text("is_active = true"))
    op.create_index('idx_feed_sources_last_fetched', 'feed_sources', ['last_fetched_at'])

    # Ingestion logs indexes
    op.create_index('idx_ingestion_logs_url_hash', 'ingestion_logs', ['url_hash'])
    op.create_index('idx_ingestion_logs_status', 'ingestion_logs', ['ingestion_status'])
    op.create_index('idx_ingestion_logs_created_at', 'ingestion_logs', [sa.text('created_at DESC')])

    # Search analytics indexes
    op.create_index('idx_search_analytics_user_id', 'search_analytics', ['user_id'])
    op.create_index('idx_search_analytics_created_at', 'search_analytics', [sa.text('created_at DESC')])


def downgrade() -> None:
    """Rollback initial schema migration."""

    # Drop all indexes first
    drop_indexes()

    # Drop tables in reverse dependency order
    op.drop_table('search_analytics')
    op.drop_table('user_preference_history')
    op.drop_table('ingestion_logs')
    op.drop_table('feed_sources')
    op.drop_table('team_stats')
    op.drop_table('games')
    op.drop_table('articles')
    op.drop_table('user_teams')
    op.drop_table('teams')
    op.drop_table('users')

    # Drop enum types
    sa.Enum(name='game_status').drop(op.get_bind())
    sa.Enum(name='content_category').drop(op.get_bind())
    sa.Enum(name='article_status').drop(op.get_bind())
    sa.Enum(name='league_type').drop(op.get_bind())
    sa.Enum(name='sport_type').drop(op.get_bind())
    sa.Enum(name='team_status').drop(op.get_bind())
    sa.Enum(name='user_status').drop(op.get_bind())
    sa.Enum(name='user_role').drop(op.get_bind())


def drop_indexes():
    """Drop all indexes."""
    # Users indexes
    op.drop_index('idx_users_preferences_gin')
    op.drop_index('idx_users_status')
    op.drop_index('idx_users_email')
    op.drop_index('idx_users_clerk_user_id')

    # Teams indexes
    op.drop_index('idx_teams_status')
    op.drop_index('idx_teams_abbreviation')
    op.drop_index('idx_teams_search_vector')
    op.drop_index('idx_teams_sport_league')

    # User-teams indexes
    op.drop_index('idx_user_teams_followed_at')
    op.drop_index('idx_user_teams_team_id')
    op.drop_index('idx_user_teams_user_id')

    # Articles indexes
    op.drop_index('idx_articles_ai_confidence')
    op.drop_index('idx_articles_search_vector')
    op.drop_index('idx_articles_tags')
    op.drop_index('idx_articles_team_ids')
    op.drop_index('idx_articles_status')
    op.drop_index('idx_articles_category')
    op.drop_index('idx_articles_published_at')
    op.drop_index('idx_articles_source_url')
    op.drop_index('idx_articles_url_hash')

    # Games indexes
    op.drop_index('idx_games_status')
    op.drop_index('idx_games_season_week')
    op.drop_index('idx_games_teams')
    op.drop_index('idx_games_scheduled_at')

    # Team stats indexes
    op.drop_index('idx_team_stats_win_percentage')
    op.drop_index('idx_team_stats_team_season')

    # Feed sources indexes
    op.drop_index('idx_feed_sources_last_fetched')
    op.drop_index('idx_feed_sources_active')

    # Ingestion logs indexes
    op.drop_index('idx_ingestion_logs_created_at')
    op.drop_index('idx_ingestion_logs_status')
    op.drop_index('idx_ingestion_logs_url_hash')

    # Search analytics indexes
    op.drop_index('idx_search_analytics_created_at')
    op.drop_index('idx_search_analytics_user_id')