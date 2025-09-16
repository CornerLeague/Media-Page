"""Add missing tables from INITIAL.md specification

Revision ID: 002
Revises: 001
Create Date: 2025-09-15 00:00:00.000000

This migration adds the missing tables required by the INITIAL.md specification:
- user_sport_prefs: User sports preferences with ranking
- sport: Sports reference table
- score: Game scoring data
- article_classification: AI classification of articles
- article_entities: Named entities extracted from articles
- depth_chart: Team depth chart information
- ticket_deal: Ticket deals and pricing
- experience: Fan experiences and events
- agent_run: Pipeline execution tracking
- scrape_job: Scheduled scraping jobs

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply missing tables migration."""

    # Create additional enum types for missing tables
    article_classification_category_enum = sa.Enum(
        'injury', 'roster', 'trade', 'general', 'depth_chart', 'game_recap',
        'analysis', 'rumors', name='article_classification_category'
    )
    agent_type_enum = sa.Enum(
        'scores', 'news', 'depth_chart', 'tickets', 'experiences', 'planner',
        'content_classification', name='agent_type'
    )
    run_status_enum = sa.Enum(
        'pending', 'running', 'completed', 'failed', 'cancelled', name='run_status'
    )
    job_type_enum = sa.Enum(
        'scrape_news', 'scrape_scores', 'scrape_depth_chart', 'scrape_tickets',
        'scrape_experiences', 'classify_content', name='job_type'
    )
    experience_type_enum = sa.Enum(
        'watch_party', 'meetup', 'bar_event', 'community_event', 'fan_fest',
        'tailgate', name='experience_type'
    )
    seat_quality_enum = sa.Enum(
        'premium', 'good', 'average', 'poor', name='seat_quality'
    )

    # Create enum types
    article_classification_category_enum.create(op.get_bind())
    agent_type_enum.create(op.get_bind())
    run_status_enum.create(op.get_bind())
    job_type_enum.create(op.get_bind())
    experience_type_enum.create(op.get_bind())
    seat_quality_enum.create(op.get_bind())

    # Create sport table
    op.create_table('sport',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('display_name', sa.Text(), nullable=False),
        sa.Column('has_teams', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('season_structure', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create user_sport_prefs table
    op.create_table('user_sport_prefs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sport_id', sa.Text(), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sport_id'], ['sport.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'rank', name='uq_user_sport_rank'),
        sa.UniqueConstraint('user_id', 'sport_id', name='uq_user_sport')
    )

    # Create score table
    op.create_table('score',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('period', sa.Integer(), nullable=True),
        sa.Column('period_pts', sa.Integer(), nullable=True),
        sa.Column('is_final', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('game_id', 'team_id', name='uq_game_team_score')
    )

    # Create article_classification table
    op.create_table('article_classification',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category', article_classification_category_enum, nullable=False),
        sa.Column('confidence', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('rationale_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('model_version', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('article_id', 'category', name='uq_article_category')
    )

    # Create article_entities table
    op.create_table('article_entities',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entity_type', sa.Text(), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('start_pos', sa.Integer(), nullable=True),
        sa.Column('end_pos', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create depth_chart table
    op.create_table('depth_chart',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('position', sa.Text(), nullable=False),
        sa.Column('player_name', sa.Text(), nullable=False),
        sa.Column('player_number', sa.Text(), nullable=True),
        sa.Column('depth_order', sa.Integer(), nullable=False),
        sa.Column('source', sa.Text(), nullable=False),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('captured_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('season_year', sa.Integer(), nullable=True),
        sa.Column('week', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', 'position', 'depth_order', 'season_year', 'week', name='uq_depth_chart_position')
    )

    # Create ticket_deal table
    op.create_table('ticket_deal',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.Text(), nullable=False),
        sa.Column('section', sa.Text(), nullable=True),
        sa.Column('row', sa.Text(), nullable=True),
        sa.Column('seat_numbers', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column('fees_est', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('total_price', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('seat_quality', seat_quality_enum, nullable=True),
        sa.Column('availability', sa.Integer(), nullable=True),
        sa.Column('deal_score', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('provider_url', sa.Text(), nullable=True),
        sa.Column('captured_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create experience table
    op.create_table('experience',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('type', experience_type_enum, nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('url', sa.Text(), nullable=True),
        sa.Column('venue', sa.Text(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('start_time', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('end_time', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('location_geo', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('quality_score', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('price_range', sa.Text(), nullable=True),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('captured_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('source', sa.Text(), nullable=False),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create agent_run table
    op.create_table('agent_run',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('agent_type', agent_type_enum, nullable=False),
        sa.Column('subject_key', sa.Text(), nullable=False),
        sa.Column('status', run_status_enum, nullable=False, server_default='pending'),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('finished_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('meta_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_text', sa.Text(), nullable=True),
        sa.Column('items_processed', sa.Integer(), nullable=True),
        sa.Column('items_created', sa.Integer(), nullable=True),
        sa.Column('items_updated', sa.Integer(), nullable=True),
        sa.Column('items_failed', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create scrape_job table
    op.create_table('scrape_job',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('subject_type', sa.Text(), nullable=False),
        sa.Column('subject_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('job_type', job_type_enum, nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('scheduled_for', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('status', run_status_enum, nullable=False, server_default='pending'),
        sa.Column('last_run_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('last_run_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('config_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['last_run_id'], ['agent_run.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance

    # User sport preferences indexes
    op.create_index('idx_user_sport_prefs_user_id', 'user_sport_prefs', ['user_id'])
    op.create_index('idx_user_sport_prefs_sport_id', 'user_sport_prefs', ['sport_id'])
    op.create_index('idx_user_sport_prefs_rank', 'user_sport_prefs', ['user_id', 'rank'])

    # Score indexes for fast game lookup
    op.create_index('idx_score_game_id', 'score', ['game_id'])
    op.create_index('idx_score_team_id', 'score', ['team_id'])
    op.create_index('idx_score_updated_at', 'score', ['updated_at'])
    op.create_index('idx_score_is_final', 'score', ['is_final'])

    # Article classification indexes
    op.create_index('idx_article_classification_article_id', 'article_classification', ['article_id'])
    op.create_index('idx_article_classification_category', 'article_classification', ['category'])
    op.create_index('idx_article_classification_confidence', 'article_classification', ['confidence'])

    # Article entities indexes
    op.create_index('idx_article_entities_article_id', 'article_entities', ['article_id'])
    op.create_index('idx_article_entities_type', 'article_entities', ['entity_type'])
    op.create_index('idx_article_entities_value', 'article_entities', ['value'])

    # Depth chart indexes
    op.create_index('idx_depth_chart_team_id', 'depth_chart', ['team_id'])
    op.create_index('idx_depth_chart_position', 'depth_chart', ['team_id', 'position'])
    op.create_index('idx_depth_chart_captured_at', 'depth_chart', ['captured_at'])

    # Ticket deal indexes
    op.create_index('idx_ticket_deal_game_id', 'ticket_deal', ['game_id'])
    op.create_index('idx_ticket_deal_price', 'ticket_deal', ['price'])
    op.create_index('idx_ticket_deal_deal_score', 'ticket_deal', ['deal_score'])
    op.create_index('idx_ticket_deal_captured_at', 'ticket_deal', ['captured_at'])

    # Experience indexes
    op.create_index('idx_experience_team_id', 'experience', ['team_id'])
    op.create_index('idx_experience_game_id', 'experience', ['game_id'])
    op.create_index('idx_experience_type', 'experience', ['type'])
    op.create_index('idx_experience_start_time', 'experience', ['start_time'])
    op.create_index('idx_experience_quality_score', 'experience', ['quality_score'])

    # Agent run indexes
    op.create_index('idx_agent_run_type_subject', 'agent_run', ['agent_type', 'subject_key'])
    op.create_index('idx_agent_run_status', 'agent_run', ['status'])
    op.create_index('idx_agent_run_started_at', 'agent_run', ['started_at'])

    # Scrape job indexes
    op.create_index('idx_scrape_job_subject', 'scrape_job', ['subject_type', 'subject_id'])
    op.create_index('idx_scrape_job_type_status', 'scrape_job', ['job_type', 'status'])
    op.create_index('idx_scrape_job_scheduled_for', 'scrape_job', ['scheduled_for'])
    op.create_index('idx_scrape_job_priority_scheduled', 'scrape_job', ['priority', 'scheduled_for'])

    # GIN indexes for full-text search and JSON operations
    op.create_index('idx_experience_location_geo', 'experience', ['location_geo'], postgresql_using='gin')


def downgrade() -> None:
    """Remove missing tables migration."""

    # Drop indexes first
    op.drop_index('idx_experience_location_geo')
    op.drop_index('idx_scrape_job_priority_scheduled')
    op.drop_index('idx_scrape_job_scheduled_for')
    op.drop_index('idx_scrape_job_type_status')
    op.drop_index('idx_scrape_job_subject')
    op.drop_index('idx_agent_run_started_at')
    op.drop_index('idx_agent_run_status')
    op.drop_index('idx_agent_run_type_subject')
    op.drop_index('idx_experience_quality_score')
    op.drop_index('idx_experience_start_time')
    op.drop_index('idx_experience_type')
    op.drop_index('idx_experience_game_id')
    op.drop_index('idx_experience_team_id')
    op.drop_index('idx_ticket_deal_captured_at')
    op.drop_index('idx_ticket_deal_deal_score')
    op.drop_index('idx_ticket_deal_price')
    op.drop_index('idx_ticket_deal_game_id')
    op.drop_index('idx_depth_chart_captured_at')
    op.drop_index('idx_depth_chart_position')
    op.drop_index('idx_depth_chart_team_id')
    op.drop_index('idx_article_entities_value')
    op.drop_index('idx_article_entities_type')
    op.drop_index('idx_article_entities_article_id')
    op.drop_index('idx_article_classification_confidence')
    op.drop_index('idx_article_classification_category')
    op.drop_index('idx_article_classification_article_id')
    op.drop_index('idx_score_is_final')
    op.drop_index('idx_score_updated_at')
    op.drop_index('idx_score_team_id')
    op.drop_index('idx_score_game_id')
    op.drop_index('idx_user_sport_prefs_rank')
    op.drop_index('idx_user_sport_prefs_sport_id')
    op.drop_index('idx_user_sport_prefs_user_id')

    # Drop tables in reverse order of dependencies
    op.drop_table('scrape_job')
    op.drop_table('agent_run')
    op.drop_table('experience')
    op.drop_table('ticket_deal')
    op.drop_table('depth_chart')
    op.drop_table('article_entities')
    op.drop_table('article_classification')
    op.drop_table('score')
    op.drop_table('user_sport_prefs')
    op.drop_table('sport')

    # Drop enum types
    sa.Enum(name='seat_quality').drop(op.get_bind())
    sa.Enum(name='experience_type').drop(op.get_bind())
    sa.Enum(name='job_type').drop(op.get_bind())
    sa.Enum(name='run_status').drop(op.get_bind())
    sa.Enum(name='agent_type').drop(op.get_bind())
    sa.Enum(name='article_classification_category').drop(op.get_bind())