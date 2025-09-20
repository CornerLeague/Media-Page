"""Initial database schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-01-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""

    # Create extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "unaccent"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # Create enums
    op.execute("""
        CREATE TYPE content_frequency AS ENUM ('minimal', 'standard', 'comprehensive')
    """)
    op.execute("""
        CREATE TYPE news_type AS ENUM ('injuries', 'trades', 'roster', 'general', 'scores', 'analysis')
    """)
    op.execute("""
        CREATE TYPE game_status AS ENUM ('SCHEDULED', 'LIVE', 'FINAL', 'POSTPONED', 'CANCELLED')
    """)
    op.execute("""
        CREATE TYPE game_result AS ENUM ('W', 'L', 'T')
    """)
    op.execute("""
        CREATE TYPE experience_type AS ENUM ('watch_party', 'tailgate', 'viewing', 'meetup')
    """)
    op.execute("""
        CREATE TYPE content_category AS ENUM ('injuries', 'trades', 'roster', 'general', 'scores', 'analysis')
    """)
    op.execute("""
        CREATE TYPE ingestion_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'duplicate')
    """)

    # Create update trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create sports table
    op.create_table('sports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('has_teams', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('icon', sa.String(255)),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create leagues table
    op.create_table('leagues',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('sport_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sports.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('abbreviation', sa.String(10)),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('season_start_month', sa.Integer()),
        sa.Column('season_end_month', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('sport_id', 'slug', name='uq_league_sport_slug'),
    )

    # Create teams table
    op.create_table('teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('sport_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sports.id', ondelete='CASCADE'), nullable=False),
        sa.Column('league_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('leagues.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('market', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('abbreviation', sa.String(10)),
        sa.Column('logo_url', sa.String(500)),
        sa.Column('primary_color', sa.String(7)),
        sa.Column('secondary_color', sa.String(7)),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('external_id', sa.String(100)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('league_id', 'slug', name='uq_team_league_slug'),
    )

    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('clerk_user_id', sa.String(255), nullable=False, unique=True),
        sa.Column('email', sa.String(255)),
        sa.Column('display_name', sa.String(100)),
        sa.Column('avatar_url', sa.String(500)),
        sa.Column('content_frequency', postgresql.ENUM(name='content_frequency'), server_default='standard'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('onboarding_completed_at', sa.DateTime(timezone=True)),
        sa.Column('last_active_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create user preference tables
    op.create_table('user_sport_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sport_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sports.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'sport_id', name='uq_user_sport'),
        sa.CheckConstraint('rank > 0', name='check_valid_rank'),
    )

    op.create_table('user_team_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('affinity_score', sa.Numeric(3, 2), nullable=False, server_default='0.5'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'team_id', name='uq_user_team'),
        sa.CheckConstraint('affinity_score >= 0 AND affinity_score <= 1', name='check_valid_affinity'),
    )

    op.create_table('user_news_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('news_type', postgresql.ENUM(name='news_type'), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'news_type', name='uq_user_news_type'),
        sa.CheckConstraint('priority > 0', name='check_valid_priority'),
    )

    op.create_table('user_notification_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('push_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('email_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('game_reminders', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('news_alerts', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('score_updates', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create games table
    op.create_table('games',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('sport_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sports.id', ondelete='CASCADE'), nullable=False),
        sa.Column('league_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('leagues.id', ondelete='CASCADE'), nullable=False),
        sa.Column('home_team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('away_team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', postgresql.ENUM(name='game_status'), server_default='SCHEDULED'),
        sa.Column('period', sa.String(20)),
        sa.Column('time_remaining', sa.String(20)),
        sa.Column('home_score', sa.Integer(), server_default='0'),
        sa.Column('away_score', sa.Integer(), server_default='0'),
        sa.Column('external_id', sa.String(100)),
        sa.Column('venue', sa.String(255)),
        sa.Column('season', sa.Integer()),
        sa.Column('week', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table('game_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('games.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('event_time', sa.String(20)),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE')),
        sa.Column('player_name', sa.String(100)),
        sa.Column('points_value', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create content management tables
    op.create_table('feed_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('url', sa.String(1000), nullable=False, unique=True),
        sa.Column('website', sa.String(500)),
        sa.Column('description', sa.Text()),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('fetch_interval_minutes', sa.Integer(), server_default='30'),
        sa.Column('last_fetched_at', sa.DateTime(timezone=True)),
        sa.Column('last_success_at', sa.DateTime(timezone=True)),
        sa.Column('failure_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table('feed_source_mappings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('feed_source_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('feed_sources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sport_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sports.id', ondelete='CASCADE')),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE')),
        sa.Column('priority', sa.Integer(), server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint('sport_id IS NOT NULL OR team_id IS NOT NULL', name='check_sport_or_team_required'),
    )

    op.create_table('feed_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('feed_source_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('feed_sources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('url_hash', sa.String(64), nullable=False),
        sa.Column('content_hash', sa.String(64), nullable=False),
        sa.Column('minhash_signature', sa.LargeBinary()),
        sa.Column('raw_content', postgresql.JSONB(), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True)),
        sa.Column('status', postgresql.ENUM(name='ingestion_status'), server_default='pending'),
        sa.Column('error_message', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('feed_source_id', 'url_hash', name='uq_feed_url_hash'),
    )

    op.create_table('articles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('feed_snapshot_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('feed_snapshots.id', ondelete='SET NULL')),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('summary', sa.Text()),
        sa.Column('content', sa.Text()),
        sa.Column('author', sa.String(255)),
        sa.Column('source', sa.String(255), nullable=False),
        sa.Column('category', postgresql.ENUM(name='content_category'), server_default='general'),
        sa.Column('priority', sa.Integer(), server_default='1'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('url', sa.String(1000)),
        sa.Column('image_url', sa.String(1000)),
        sa.Column('external_id', sa.String(255)),
        sa.Column('word_count', sa.Integer()),
        sa.Column('reading_time_minutes', sa.Integer()),
        sa.Column('sentiment_score', sa.Numeric(3, 2)),
        sa.Column('search_vector', postgresql.TSVECTOR()),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint('word_count >= 0', name='check_valid_word_count'),
        sa.CheckConstraint('reading_time_minutes >= 0', name='check_valid_reading_time'),
        sa.CheckConstraint('sentiment_score >= -1 AND sentiment_score <= 1', name='check_valid_sentiment'),
    )

    op.create_table('article_sports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sport_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sports.id', ondelete='CASCADE'), nullable=False),
        sa.Column('relevance_score', sa.Numeric(3, 2), server_default='0.5'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('article_id', 'sport_id', name='uq_article_sport'),
    )

    op.create_table('article_teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('relevance_score', sa.Numeric(3, 2), server_default='0.5'),
        sa.Column('mentioned_players', postgresql.ARRAY(sa.String()), server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('article_id', 'team_id', name='uq_article_team'),
    )

    # Continue with remaining tables...
    # (This is getting long, so I'll create separate migration files for better organization)


def downgrade() -> None:
    """Downgrade database schema."""

    # Drop tables in reverse order
    op.drop_table('article_teams')
    op.drop_table('article_sports')
    op.drop_table('articles')
    op.drop_table('feed_snapshots')
    op.drop_table('feed_source_mappings')
    op.drop_table('feed_sources')
    op.drop_table('game_events')
    op.drop_table('games')
    op.drop_table('user_notification_settings')
    op.drop_table('user_news_preferences')
    op.drop_table('user_team_preferences')
    op.drop_table('user_sport_preferences')
    op.drop_table('users')
    op.drop_table('teams')
    op.drop_table('leagues')
    op.drop_table('sports')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS ingestion_status')
    op.execute('DROP TYPE IF EXISTS content_category')
    op.execute('DROP TYPE IF EXISTS experience_type')
    op.execute('DROP TYPE IF EXISTS game_result')
    op.execute('DROP TYPE IF EXISTS game_status')
    op.execute('DROP TYPE IF EXISTS news_type')
    op.execute('DROP TYPE IF EXISTS content_frequency')

    # Drop function
    op.execute('DROP FUNCTION IF EXISTS set_updated_at()')

    # Note: Extensions are typically not dropped in migrations as they might be used by other applications